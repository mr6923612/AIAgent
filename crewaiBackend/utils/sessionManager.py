"""
会话管理器
用于管理聊天会话和上下文记录
使用MySQL数据库进行持久化存储
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4
from .database import db_manager

logger = logging.getLogger(__name__)


class ChatMessage:
    """聊天消息类"""
    
    def __init__(self, role: str, content: str, timestamp: datetime = None):
        self.role = role  # 'user' 或 'assistant'
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.id = str(uuid4())
    
    def to_dict(self):
        return {
            'id': self.id,
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        message = cls(
            role=data['role'],
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )
        message.id = data['id']
        return message


class ChatSession:
    """聊天会话类"""
    
    def __init__(self, session_id: str = None, user_id: str = None, title: str = None, ragflow_session_id: str = None):
        self.session_id = session_id or str(uuid4())
        self.user_id = user_id or "anonymous"
        self.title = title or f"聊天会话 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.messages: List[ChatMessage] = []
        self.context = {}  # 存储上下文信息
        self.ragflow_session_id = ragflow_session_id  # RAGFlow会话ID
    
    def add_message(self, role: str, content: str):
        """添加消息到会话"""
        message = ChatMessage(role, content)
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def get_context_summary(self, max_messages: int = 10) -> str:
        """获取上下文摘要"""
        if not self.messages:
            return ""
        
        recent_messages = self.messages[-max_messages:]
        context_parts = []
        
        for msg in recent_messages:
            role_name = "用户" if msg.role == "user" else "客服"
            context_parts.append(f"{role_name}: {msg.content}")
        
        return "\n".join(context_parts)
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'messages': [msg.to_dict() for msg in self.messages],
            'message_count': len(self.messages),
            'context': self.context,
            'ragflow_session_id': self.ragflow_session_id
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        session = cls(
            session_id=data['session_id'],
            user_id=data['user_id'],
            title=data['title'],
            ragflow_session_id=data.get('ragflow_session_id')
        )
        session.created_at = datetime.fromisoformat(data['created_at'])
        session.updated_at = datetime.fromisoformat(data['updated_at'])
        session.messages = [ChatMessage.from_dict(msg) for msg in data['messages']]
        session.context = data.get('context', {})
        return session


class SessionManager:
    """会话管理器"""

    def __init__(self):
        self.db = db_manager
        logger.info("会话管理器初始化完成")

    def create_session(self, user_id: str = None, title: str = None) -> ChatSession:
        """
        创建新会话（只创建数据库记录）
        注意：RAGFlow会话的创建由session_agent_manager在第一次对话时自动创建
        """
        session_id = str(uuid4())
        user_id = user_id or "anonymous"
        title = title or f"聊天会话 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        try:
            # 插入会话到数据库（ragflow_session_id暂时为NULL，后续由agent管理）
            query = """
                INSERT INTO chat_sessions (session_id, user_id, title, context, ragflow_session_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (session_id, user_id, title, json.dumps({}), None)
            self.db.execute_update(query, params)
            
            # 创建会话对象
            session = ChatSession(session_id=session_id, user_id=user_id, title=title, ragflow_session_id=None)
            logger.info(f"创建新会话: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"创建会话失败: {e}")
            raise

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """获取会话"""
        try:
            # 查询会话信息
            session_query = "SELECT * FROM chat_sessions WHERE session_id = %s"
            session_data = self.db.execute_query(session_query, (session_id,))
            
            if not session_data:
                return None
            
            session_row = session_data[0]
            session = ChatSession(
                session_id=session_row[0],
                user_id=session_row[1],
                title=session_row[2],
                ragflow_session_id=session_row[6] if len(session_row) > 6 else None
            )
            session.created_at = session_row[3]
            session.updated_at = session_row[4]
            session.context = json.loads(session_row[5]) if session_row[5] else {}
            
            # 查询消息
            messages_query = """
                SELECT id, role, content, timestamp 
                FROM chat_messages 
                WHERE session_id = %s 
                ORDER BY timestamp ASC
            """
            messages_data = self.db.execute_query(messages_query, (session_id,))
            
            for msg_row in messages_data:
                message = ChatMessage(
                    role=msg_row[1],
                    content=msg_row[2],
                    timestamp=msg_row[3]
                )
                message.id = msg_row[0]
                session.messages.append(message)
            
            return session
            
        except Exception as e:
            logger.error(f"获取会话失败: {e}")
            return None

    def get_user_sessions(self, user_id: str) -> List[ChatSession]:
        """获取用户的所有会话"""
        try:
            query = """
                SELECT session_id FROM chat_sessions 
                WHERE user_id = %s 
                ORDER BY updated_at DESC
            """
            sessions_data = self.db.execute_query(query, (user_id,))
            
            sessions = []
            for row in sessions_data:
                session = self.get_session(row[0])
                if session:
                    sessions.append(session)
            
            return sessions
            
        except Exception as e:
            logger.error(f"获取用户会话失败: {e}")
            return []

    def add_message(self, session_id: str, role: str, content: str) -> Optional[ChatMessage]:
        """添加消息到会话"""
        try:
            message_id = str(uuid4())
            
            # 插入消息到数据库
            query = """
                INSERT INTO chat_messages (id, session_id, role, content)
                VALUES (%s, %s, %s, %s)
            """
            params = (message_id, session_id, role, content)
            self.db.execute_update(query, params)
            
            # 如果是第一条用户消息，自动更新会话标题
            if role == 'user':
                # 检查是否是第一条用户消息
                count_query = """
                    SELECT COUNT(*) FROM chat_messages 
                    WHERE session_id = %s AND role = 'user'
                """
                count_result = self.db.execute_query(count_query, (session_id,))
                if count_result and count_result[0][0] == 1:  # 第一条用户消息
                    # 生成基于内容的标题（截取前30个字符）
                    new_title = content[:30] + ('...' if len(content) > 30 else '')
                    title_update_query = "UPDATE chat_sessions SET title = %s WHERE session_id = %s"
                    self.db.execute_update(title_update_query, (new_title, session_id))
            
            # 更新会话的更新时间
            update_query = "UPDATE chat_sessions SET updated_at = NOW() WHERE session_id = %s"
            self.db.execute_update(update_query, (session_id,))
            
            # 创建消息对象
            message = ChatMessage(role, content)
            message.id = message_id
            
            logger.info(f"添加消息到会话 {session_id}: {role}")
            return message
            
        except Exception as e:
            logger.error(f"添加消息失败: {e}")
            return None

    def update_session_title(self, session_id: str, title: str):
        """更新会话标题"""
        try:
            query = "UPDATE chat_sessions SET title = %s, updated_at = NOW() WHERE session_id = %s"
            self.db.execute_update(query, (title, session_id))
            logger.info(f"更新会话标题: {session_id}")
            
        except Exception as e:
            logger.error(f"更新会话标题失败: {e}")

    def delete_session(self, session_id: str) -> bool:
        """
        删除会话（只删除数据库记录）
        注意：RAGFlow会话的删除由session_agent_manager负责
        """
        try:
            # 删除本地会话（由于外键约束，删除会话会自动删除相关消息）
            query = "DELETE FROM chat_sessions WHERE session_id = %s"
            affected_rows = self.db.execute_update(query, (session_id,))
            
            if affected_rows > 0:
                logger.info(f"删除本地会话: {session_id}")
                return True
            else:
                logger.warning(f"会话不存在: {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"删除会话失败: {e}")
            return False

    def get_all_sessions(self) -> List[ChatSession]:
        """获取所有会话"""
        try:
            query = "SELECT session_id FROM chat_sessions ORDER BY updated_at DESC"
            sessions_data = self.db.execute_query(query)
            
            sessions = []
            for row in sessions_data:
                session = self.get_session(row[0])
                if session:
                    sessions.append(session)
            
            return sessions
            
        except Exception as e:
            logger.error(f"获取所有会话失败: {e}")
            return []

    def cleanup_old_sessions(self, days: int = 30):
        """
        清理旧会话
        注意：这个方法只清理数据库记录，不清理Agent
        如需清理Agent，请调用session_agent_manager.cleanup_inactive_sessions()
        """
        try:
            # 先获取要删除的session IDs
            select_query = "SELECT session_id FROM chat_sessions WHERE updated_at < DATE_SUB(NOW(), INTERVAL %s DAY)"
            old_sessions = self.db.execute_query(select_query, (days,))
            
            if not old_sessions:
                logger.info("没有需要清理的旧会话")
                return
            
            # 删除数据库记录
            delete_query = "DELETE FROM chat_sessions WHERE updated_at < DATE_SUB(NOW(), INTERVAL %s DAY)"
            affected_rows = self.db.execute_update(delete_query, (days,))
            logger.info(f"清理了 {affected_rows} 个旧会话（数据库记录）")
            
        except Exception as e:
            logger.error(f"清理旧会话失败: {e}")
