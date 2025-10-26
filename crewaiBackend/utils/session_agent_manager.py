# -*- coding: utf-8 -*-
"""
会话Agent管理器

架构说明：
- RAGFlow和SQL在程序启动时拉起，全局共享
- Agent在session第一次对话时创建，session删除时释放
- session存在时复用Agent，避免重复创建

Session ID映射关系：
- 一个应用session_id对应一个RAGFlow session_id（一对一映射）
- RAGFlow session在第一次对话时由SessionAgent自动创建
- 删除应用session时，自动删除对应的RAGFlow session

生命周期管理：
1. 创建会话：只创建数据库记录，不创建RAGFlow会话
2. 第一次对话：创建SessionAgent，自动创建RAGFlow会话
3. 后续对话：复用已有的SessionAgent和RAGFlow会话
4. 删除会话：先释放Agent（删除RAGFlow会话），再删除数据库记录
5. 清理非活跃会话：自动释放Agent并删除RAGFlow会话
"""

import threading
from typing import Dict, Optional
from datetime import datetime
import logging

from crewai import Agent, Crew, Process
from .myLLM import my_llm
from .ragflow_session_manager import ragflow_session_manager

logger = logging.getLogger(__name__)

class SessionAgentManager:
    """会话Agent管理器"""
    
    def __init__(self):
        """初始化管理器"""
        self.session_agents: Dict[str, 'SessionAgent'] = {}
        self.lock = threading.Lock()
        
        # 全局共享资源（程序启动时创建）
        self.shared_llm = None
        self._init_shared_resources()
    
    def _init_shared_resources(self):
        """初始化全局共享资源"""
        try:
            # 创建共享LLM实例
            self.shared_llm = my_llm("google")
            logger.info("全局LLM实例创建成功")
            
        except Exception as e:
            logger.error(f"初始化全局资源失败: {e}")
            raise
    
    def get_or_create_agent(self, session_id: str) -> 'SessionAgent':
        """
        获取或创建会话Agent
        
        Args:
            session_id: 会话ID
            
        Returns:
            SessionAgent实例
        """
        with self.lock:
            # 检查是否已有该会话的Agent
            if session_id in self.session_agents:
                agent = self.session_agents[session_id]
                agent.update_last_used()
                logger.info(f"🔄 复用会话 {session_id} 的Agent")
                return agent
            
            # 创建新Agent
            agent = SessionAgent(
                session_id=session_id,
                llm=self.shared_llm
            )
            
            self.session_agents[session_id] = agent
            logger.info(f"🆕 为会话 {session_id} 创建新Agent，当前会话数: {len(self.session_agents)}")
            return agent
    
    def release_agent(self, session_id: str):
        """
        释放会话Agent，同时删除对应的RAGFlow会话
        
        Args:
            session_id: 会话ID
        """
        with self.lock:
            if session_id in self.session_agents:
                agent = self.session_agents[session_id]
                
                # 清理资源（包括删除RAGFlow会话）
                agent.cleanup()
                
                # 从字典中移除
                del self.session_agents[session_id]
                logger.info(f"释放会话 {session_id} 的Agent，当前会话数: {len(self.session_agents)}")
            else:
                logger.warning(f"尝试释放不存在的会话 {session_id}")
    
    def get_session_status(self) -> Dict:
        """获取所有会话状态"""
        with self.lock:
            return {
                'total_sessions': len(self.session_agents),
                'sessions': list(self.session_agents.keys()),
                'session_details': {
                    session_id: {
                        'created_at': agent.created_at.isoformat(),
                        'last_used': agent.last_used.isoformat(),
                        'age_seconds': (datetime.now() - agent.created_at).total_seconds()
                    }
                    for session_id, agent in self.session_agents.items()
                }
            }
    
    def cleanup_inactive_sessions(self, max_age_seconds: int = 1800):
        """
        清理非活跃会话，同时删除对应的RAGFlow会话
        
        Args:
            max_age_seconds: 最大非活跃时间（秒）
        """
        with self.lock:
            now = datetime.now()
            inactive_sessions = [
                (session_id, agent) for session_id, agent in self.session_agents.items()
                if (now - agent.last_used).total_seconds() > max_age_seconds
            ]
            
            for session_id, agent in inactive_sessions:
                # 清理资源（包括删除RAGFlow会话）
                agent.cleanup()
                
                # 从字典中移除
                del self.session_agents[session_id]
                logger.info(f"清理非活跃会话 {session_id}")
            
            if inactive_sessions:
                logger.info(f"清理完成，释放 {len(inactive_sessions)} 个非活跃会话")


class SessionAgent:
    """会话Agent实例"""
    
    def __init__(self, session_id: str, llm):
        self.session_id = session_id
        self.llm = llm
        self.created_at = datetime.now()
        self.last_used = datetime.now()
        
        # 创建一个共享的Crew工具实例（用于复用crew.py中的定义）
        from ..crew import CrewtestprojectCrew
        self._crew_helper = CrewtestprojectCrew(job_id="temp", llm=self.llm)
        
        # 创建Agent（只创建一次）
        self.agents = self._create_agents()
        self.crew = self._create_crew()
    
    def update_last_used(self):
        """更新最后使用时间"""
        self.last_used = datetime.now()
    
    def _create_agents(self):
        """创建Agent（从crew.py复用定义）"""
        # 使用共享的crew helper实例
        agents_dict = self._crew_helper.create_agents()
        return agents_dict
    
    def _create_crew(self):
        """创建Crew（复用crew.py中的定义）"""
        # 使用crew.py中的create_crew方法
        return self._crew_helper.create_crew(
            agents=self.agents,
            tasks=[]  # 任务在kickoff时动态创建
        )
    
    def kickoff(self, inputs):
        """执行任务"""
        # 更新使用时间
        self.update_last_used()
        
        # 动态创建任务
        tasks = self._create_tasks(inputs)
        
        # 更新Crew的任务
        self.crew.tasks = tasks
        
        # 执行任务
        return self.crew.kickoff()
    
    def _create_tasks(self, inputs):
        """根据输入动态创建任务（从crew.py复用定义）"""
        from crewai import Task
        
        # 导入crew.py中的类
        from ..crew import CrewtestprojectCrew
        
        # 确保RAGFlow session_id已创建并更新到数据库
        session_id = inputs.get('session_id', '')
        ragflow_session_id = None
        
        if session_id:
            # 使用ragflow_session_manager获取或创建RAGFlow session ID
            ragflow_session_id = ragflow_session_manager.get_or_create_session(session_id)
            
            # 更新数据库中的ragflow_session_id
            if ragflow_session_id:
                try:
                    from ..utils.sessionManager import SessionManager
                    session_manager = SessionManager()
                    session = session_manager.get_session(session_id)
                    
                    # 检查数据库中的ragflow_session_id是否与内存中的一致
                    db_ragflow_session_id = session.ragflow_session_id if session else None
                    
                    if db_ragflow_session_id != ragflow_session_id:
                        # 更新数据库记录（无论是新建还是不一致都更新）
                        from ..utils.database import db_manager
                        query = "UPDATE chat_sessions SET ragflow_session_id = %s WHERE session_id = %s"
                        db_manager.execute_update(query, (ragflow_session_id, session_id))
                        logger.info(f"[会话:{session_id[:8]}] 已将RAGFlow session_id更新到数据库: {ragflow_session_id[:8]}")
                    
                    # 将 ragflow_session_id 直接传入 inputs，避免 crew.py 中的导入问题
                    inputs = inputs.copy()  # 避免修改原始 inputs
                    inputs['ragflow_session_id'] = ragflow_session_id
                    logger.info(f"[会话:{session_id[:8]}] 传递RAGFlow session_id到任务: {ragflow_session_id[:8]}")
                    
                except Exception as e:
                    logger.warning(f"[会话:{session_id[:8]}] 更新RAGFlow session_id到数据库失败: {e}")
        
        # 使用共享的crew helper来创建tasks
        tasks = self._crew_helper.create_tasks(self.agents, inputs)
        
        return tasks
    
    def cleanup(self):
        """
        清理会话资源，包括删除对应的RAGFlow会话
        """
        try:
            # 使用ragflow_session_manager删除RAGFlow会话
            ragflow_session_manager.delete_session(self.session_id)
        except Exception as e:
            logger.error(f"[会话:{self.session_id[:8]}] 清理RAGFlow会话失败: {e}")


# 全局会话Agent管理器实例
session_agent_manager = SessionAgentManager()
