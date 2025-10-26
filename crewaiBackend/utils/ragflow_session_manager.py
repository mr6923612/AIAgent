# -*- coding: utf-8 -*-
"""
RAGFlow会话管理器

专门负责管理RAGFlow会话的创建、映射和删除
- 维护应用session_id到RAGFlow session_id的一对一映射
- 提供RAGFlow会话的创建、获取、删除接口
- 从数据库加载已有的映射关系，确保重启后映射不丢失
"""

import logging
from typing import Dict, Optional
from .ragflow_client import create_ragflow_client, DEFAULT_CHAT_ID

logger = logging.getLogger(__name__)


class RAGFlowSessionManager:
    """RAGFlow会话管理器（单例模式）"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """单例模式：确保全局只有一个实例"""
        if cls._instance is None:
            cls._instance = super(RAGFlowSessionManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化管理器"""
        # 避免重复初始化
        if self._initialized:
            logger.info("[RAGFlow] 使用已有的 RAGFlow 会话管理器实例")
            return
        
        # RAGFlow会话ID映射：{应用session_id: RAGFlow session_id}
        self.session_mapping: Dict[str, str] = {}
        
        # 全局共享的RAGFlow客户端
        self.ragflow_client = create_ragflow_client()
        
        # 从数据库加载已有的映射关系
        self._load_mappings_from_database()
        
        logger.info(f"RAGFlow会话管理器初始化完成，已加载 {len(self.session_mapping)} 个会话映射")
        
        # 启动时清理无效的RAGFlow会话
        self._cleanup_invalid_sessions()
        
        # 标记为已初始化
        self._initialized = True
    
    def _load_mappings_from_database(self):
        """从数据库加载已有的RAGFlow会话映射"""
        try:
            from .database import db_manager
            
            # 查询所有有RAGFlow session ID的会话
            query = """
                SELECT session_id, ragflow_session_id 
                FROM chat_sessions 
                WHERE ragflow_session_id IS NOT NULL
            """
            logger.info(f"[RAGFlow] 正在从数据库加载会话映射，查询SQL: {query}")
            results = db_manager.execute_query(query)
            
            logger.info(f"[RAGFlow] 数据库查询结果类型: {type(results)}, 长度: {len(results) if results else 'None'}")
            
            if results:
                for row in results:
                    app_session_id = row[0]
                    ragflow_session_id = row[1]
                    self.session_mapping[app_session_id] = ragflow_session_id
                    logger.info(f"[RAGFlow] 加载映射: {app_session_id[:8]} -> {ragflow_session_id[:8] if ragflow_session_id else 'None'}")
                
                logger.info(f"[RAGFlow] 从数据库加载了 {len(results)} 个会话映射")
            else:
                logger.info("[RAGFlow] 数据库中没有已有的会话映射")
                
        except Exception as e:
            logger.warning(f"[RAGFlow] 从数据库加载映射失败（可能数据库未连接）: {e}")
            import traceback
            logger.warning(f"[RAGFlow] 错误堆栈: {traceback.format_exc()}")
    
    def get_or_create_session(self, app_session_id: str, session_name: str = None) -> Optional[str]:
        """
        获取或创建RAGFlow会话ID
        
        Args:
            app_session_id: 应用会话ID
            session_name: 会话名称（可选）
            
        Returns:
            RAGFlow会话ID，失败时返回None
        """
        # 1. 先检查内存映射
        if app_session_id in self.session_mapping:
            ragflow_session_id = self.session_mapping[app_session_id]
            logger.info(f"[RAGFlow] 从内存复用已有会话: {app_session_id[:8]} -> {ragflow_session_id[:8]}")
            return ragflow_session_id
        
        # 2. 如果内存中没有，从数据库查询（处理进程重启后的情况）
        try:
            from .database import db_manager
            query = "SELECT ragflow_session_id FROM chat_sessions WHERE session_id = %s AND ragflow_session_id IS NOT NULL"
            results = db_manager.execute_query(query, (app_session_id,))
            
            if results and len(results) > 0:
                ragflow_session_id = results[0][0]
                # 将数据库中的映射加载到内存
                self.session_mapping[app_session_id] = ragflow_session_id
                logger.info(f"[RAGFlow] 从数据库恢复会话映射: {app_session_id[:8]} -> {ragflow_session_id[:8]}")
                return ragflow_session_id
        except Exception as e:
            logger.warning(f"[RAGFlow] 从数据库查询会话映射失败: {e}")
        
        # 3. 如果数据库中也没有，创建新的RAGFlow会话
        try:
            name = session_name or f"会话_{app_session_id[:8]}"
            logger.info(f"[RAGFlow] 创建新会话: {app_session_id[:8]}")
            
            session_data = self.ragflow_client.create_session(
                chat_id=DEFAULT_CHAT_ID,
                name=name,
                user_id=f"user_{app_session_id}"
            )
            
            ragflow_session_id = session_data.get('id', '')
            
            if ragflow_session_id:
                # 建立映射关系
                self.session_mapping[app_session_id] = ragflow_session_id
                logger.info(f"[RAGFlow] 会话创建成功: {app_session_id[:8]} -> {ragflow_session_id[:8]}")
                return ragflow_session_id
            else:
                logger.error(f"[RAGFlow] 会话创建失败：返回数据中没有id")
                return None
                
        except Exception as e:
            logger.error(f"[RAGFlow] 会话创建失败: {e}")
            return None
    
    def get_session_id(self, app_session_id: str) -> Optional[str]:
        """
        获取RAGFlow会话ID（不创建新的）
        
        Args:
            app_session_id: 应用会话ID
            
        Returns:
            RAGFlow会话ID，不存在时返回None
        """
        return self.session_mapping.get(app_session_id)
    
    def delete_session(self, app_session_id: str) -> bool:
        """
        删除RAGFlow会话
        
        Args:
            app_session_id: 应用会话ID
            
        Returns:
            删除是否成功
        """
        # 获取RAGFlow会话ID
        ragflow_session_id = self.session_mapping.get(app_session_id)
        
        if not ragflow_session_id:
            logger.warning(f"[RAGFlow] 会话不存在，无需删除: {app_session_id[:8]}")
            return True  # 不存在视为成功
        
        try:
            logger.info(f"[RAGFlow] 删除会话: {app_session_id[:8]} -> {ragflow_session_id[:8]}")
            
            self.ragflow_client.delete_session(
                chat_id=DEFAULT_CHAT_ID,
                session_id=ragflow_session_id
            )
            
            # 移除映射关系
            del self.session_mapping[app_session_id]
            
            logger.info(f"[RAGFlow] 会话删除成功: {app_session_id[:8]}")
            return True
            
        except Exception as e:
            logger.error(f"[RAGFlow] 会话删除失败: {e}")
            # 即使删除失败，也移除映射关系
            if app_session_id in self.session_mapping:
                del self.session_mapping[app_session_id]
            return False
    
    def cleanup_all_sessions(self) -> int:
        """
        清理所有RAGFlow会话
        
        Returns:
            清理的会话数量
        """
        count = 0
        session_ids = list(self.session_mapping.keys())
        
        for app_session_id in session_ids:
            if self.delete_session(app_session_id):
                count += 1
        
        logger.info(f"[RAGFlow] 清理完成，共删除 {count} 个会话")
        return count
    
    def get_mapping_count(self) -> int:
        """获取当前映射的会话数量"""
        return len(self.session_mapping)
    
    def get_mappings(self) -> Dict[str, str]:
        """获取所有映射关系"""
        return self.session_mapping.copy()
    
    def _cleanup_invalid_sessions(self):
        """
        启动时清理无效的RAGFlow会话
        
        清理策略（双向清理）：
        1. 获取RAGFlow中的所有session
        2. 获取数据库中的所有session映射
        3. 双向清理：
           a) 如果数据库中的ragflow_session_id在RAGFlow中不存在，清空数据库字段
           b) 如果RAGFlow中的session_id不在数据库映射中，删除RAGFlow会话
        """
        try:
            logger.info("[RAGFlow] 开始清理无效会话...")
            
            # 获取RAGFlow中所有的sessions
            ragflow_sessions = self._get_all_ragflow_sessions()
            if ragflow_sessions is None:
                logger.warning("[RAGFlow] 无法获取RAGFlow会话列表，跳过清理")
                return
            
            ragflow_session_ids = set(ragflow_sessions.keys())
            logger.info(f"[RAGFlow] RAGFlow中有 {len(ragflow_session_ids)} 个会话")
            
            from .database import db_manager
            
            # === 步骤 1：获取数据库中所有的 ragflow_session_id ===
            query = """
                SELECT session_id, ragflow_session_id 
                FROM chat_sessions 
                WHERE ragflow_session_id IS NOT NULL
            """
            db_results = db_manager.execute_query(query)
            
            # 构建数据库映射：{ragflow_session_id: app_session_id}
            db_mapping = {}
            if db_results:
                for row in db_results:
                    app_session_id = row[0]
                    db_ragflow_session_id = row[1]
                    db_mapping[db_ragflow_session_id] = app_session_id
            
            db_ragflow_session_ids = set(db_mapping.keys())
            logger.info(f"[RAGFlow] 数据库中有 {len(db_ragflow_session_ids)} 个会话映射")
            
            # === 步骤 2：清理数据库中的无效映射 ===
            # 如果数据库中的 ragflow_session_id 在 RAGFlow 中不存在，清空数据库字段
            db_invalid_count = 0
            for db_ragflow_session_id, app_session_id in list(db_mapping.items()):
                if db_ragflow_session_id not in ragflow_session_ids:
                    # 清空数据库中的ragflow_session_id
                    update_query = "UPDATE chat_sessions SET ragflow_session_id = NULL WHERE session_id = %s"
                    db_manager.execute_update(update_query, (app_session_id,))
                    
                    # 从内存映射中删除
                    if app_session_id in self.session_mapping:
                        del self.session_mapping[app_session_id]
                    
                    # 从 db_ragflow_session_ids 中移除，这样不会保护这个无效的 session
                    db_ragflow_session_ids.discard(db_ragflow_session_id)
                    
                    db_invalid_count += 1
                    logger.info(f"[RAGFlow] 清理数据库无效映射: {app_session_id[:8]} -> {db_ragflow_session_id[:8]}")
            
            # === 步骤 3：清理RAGFlow中的孤立会话 ===
            # 找出 RAGFlow 中存在但数据库中没有记录的会话（孤立会话）
            orphaned_sessions = ragflow_session_ids - db_ragflow_session_ids
            ragflow_deleted_count = 0
            
            if orphaned_sessions:
                logger.info(f"[RAGFlow] 发现 {len(orphaned_sessions)} 个孤立会话，准备删除...")
                for orphaned_session_id in orphaned_sessions:
                    try:
                        self.ragflow_client.delete_session(
                            chat_id=DEFAULT_CHAT_ID,
                            session_id=orphaned_session_id
                        )
                        ragflow_deleted_count += 1
                        logger.info(f"[RAGFlow] 删除孤立会话: {orphaned_session_id[:8]}")
                    except Exception as e:
                        logger.warning(f"[RAGFlow] 删除孤立会话失败 {orphaned_session_id[:8]}: {e}")
            
            # === 总结 ===
            total_cleaned = db_invalid_count + ragflow_deleted_count
            if total_cleaned > 0:
                logger.info(f"[RAGFlow] 清理完成，共清理 {total_cleaned} 个会话 (数据库无效映射:{db_invalid_count}, RAGFlow孤立会话:{ragflow_deleted_count})")
            else:
                logger.info(f"[RAGFlow] 所有会话都有效，无需清理 (数据库:{len(db_ragflow_session_ids)}, RAGFlow:{len(ragflow_session_ids)})")
                
        except Exception as e:
            logger.warning(f"[RAGFlow] 清理无效会话失败: {e}")
    
    def _get_all_ragflow_sessions(self) -> Optional[Dict[str, dict]]:
        """
        获取RAGFlow中所有的sessions
        
        Returns:
            {session_id: session_data} 的字典，失败时返回None
        """
        try:
            # 调用RAGFlow API获取sessions
            # 注意：RAGFlow的list_sessions API需要chat_id
            response = self.ragflow_client.list_sessions(chat_id=DEFAULT_CHAT_ID)
            
            if not response:
                return {}
            
            # 构建session_id到session_data的映射
            session_dict = {}
            for session in response:
                session_id = session.get('id')
                if session_id:
                    session_dict[session_id] = session
            
            return session_dict
            
        except Exception as e:
            logger.error(f"[RAGFlow] 获取RAGFlow会话列表失败: {e}")
            return None


# 全局RAGFlow会话管理器实例
ragflow_session_manager = RAGFlowSessionManager()
