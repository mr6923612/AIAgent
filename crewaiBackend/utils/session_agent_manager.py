# -*- coding: utf-8 -*-
"""
会话Agent管理器
- RAGFlow和SQL在程序启动时拉起，全局共享
- Agent在session建立时拉起，session结束时释放
- session存在时复用Agent，避免重复创建
"""

import threading
from typing import Dict, Optional
from datetime import datetime
import logging

from crewai import Agent, Crew, Process
from .myLLM import my_llm
from .ragflow_client import create_ragflow_client, DEFAULT_CHAT_ID

logger = logging.getLogger(__name__)

class SessionAgentManager:
    """会话Agent管理器"""
    
    def __init__(self):
        """初始化管理器"""
        self.session_agents: Dict[str, 'SessionAgent'] = {}
        self.lock = threading.Lock()
        
        # 全局共享资源（程序启动时创建）
        self.shared_llm = None
        self.shared_ragflow_client = None
        self._init_shared_resources()
    
    def _init_shared_resources(self):
        """初始化全局共享资源"""
        try:
            # 创建共享LLM实例
            self.shared_llm = my_llm("google")
            logger.info("✅ 全局LLM实例创建成功")
            
            # 创建共享RAGFlow客户端
            self.shared_ragflow_client = create_ragflow_client()
            logger.info("✅ 全局RAGFlow客户端创建成功")
            
        except Exception as e:
            logger.error(f"❌ 初始化全局资源失败: {e}")
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
                llm=self.shared_llm,
                ragflow_client=self.shared_ragflow_client
            )
            
            self.session_agents[session_id] = agent
            logger.info(f"🆕 为会话 {session_id} 创建新Agent，当前会话数: {len(self.session_agents)}")
            return agent
    
    def release_agent(self, session_id: str):
        """
        释放会话Agent
        
        Args:
            session_id: 会话ID
        """
        with self.lock:
            if session_id in self.session_agents:
                del self.session_agents[session_id]
                logger.info(f"🗑️ 释放会话 {session_id} 的Agent，当前会话数: {len(self.session_agents)}")
            else:
                logger.warning(f"⚠️ 尝试释放不存在的会话 {session_id}")
    
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
        清理非活跃会话
        
        Args:
            max_age_seconds: 最大非活跃时间（秒）
        """
        with self.lock:
            now = datetime.now()
            inactive_sessions = [
                session_id for session_id, agent in self.session_agents.items()
                if (now - agent.last_used).total_seconds() > max_age_seconds
            ]
            
            for session_id in inactive_sessions:
                del self.session_agents[session_id]
                logger.info(f"🧹 清理非活跃会话 {session_id}")
            
            if inactive_sessions:
                logger.info(f"🧹 清理完成，释放 {len(inactive_sessions)} 个非活跃会话")


class SessionAgent:
    """会话Agent实例"""
    
    def __init__(self, session_id: str, llm, ragflow_client):
        self.session_id = session_id
        self.llm = llm
        self.ragflow_client = ragflow_client
        self.created_at = datetime.now()
        self.last_used = datetime.now()
        
        # 创建Agent（只创建一次）
        self.agents = self._create_agents()
        self.crew = self._create_crew()
    
    def update_last_used(self):
        """更新最后使用时间"""
        self.last_used = datetime.now()
    
    def _create_agents(self):
        """创建Agent（只创建一次）"""
        # 智能客服Agent
        customer_service_agent = Agent(
            role="智能客服代表",
            goal="为客户提供友好、专业的服务，像真人客服一样自然回复",
            backstory="""你是一位经验丰富的客服代表，具备强大的语言识别和回复能力。
            你的特点：
            - 能够自动识别客户使用的语言（中文、英文、其他语言）
            - 使用相同的语言进行自然、亲切的回复
            - 语言表达自然流畅，像朋友一样交流
            - 能够准确理解客户需求并提供专业回答
            - 基于公司信息提供准确回答
            - 始终保持耐心和专业的态度
            - 即使没有相关信息，也会基于专业知识尽力帮助客户""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # 知识检索Agent
        knowledge_agent = Agent(
            role="知识检索专家",
            goal="从知识库中检索相关信息，为客服提供准确答案",
            backstory="""你是一位专业的知识检索专家，擅长从大量信息中快速找到相关内容。
            你的职责：
            - 根据客户问题检索相关知识
            - 提供准确、相关的信息
            - 确保信息的时效性和准确性
            - 为客服代表提供决策支持""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        return {
            'customer_service': customer_service_agent,
            'knowledge': knowledge_agent
        }
    
    def _create_crew(self):
        """创建Crew（只创建一次）"""
        return Crew(
            agents=[self.agents['customer_service'], self.agents['knowledge']],
            tasks=[],  # 任务在kickoff时动态创建
            process=Process.sequential,
            verbose=True
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
        """根据输入动态创建任务"""
        from crewai import Task
        
        customer_input = inputs.get('customer_input', '')
        session_id = inputs.get('session_id', '')
        
        # 知识检索任务
        knowledge_task = Task(
            description=f"""
            请根据客户的问题检索相关知识：
            客户问题：{customer_input}
            
            请使用RAGFlow知识库检索相关信息，为客服代表提供准确的答案。
            """,
            agent=self.agents['knowledge'],
            expected_output="检索到的相关知识信息"
        )
        
        # 客服回复任务
        service_task = Task(
            description=f"""
            基于检索到的知识，为客户提供专业、友好的回复：
            客户问题：{customer_input}
            会话ID：{session_id}
            
            请提供：
            1. 自然、友好的回复
            2. 基于检索知识的准确答案
            3. 如果信息不足，提供合理的建议
            4. 保持专业和耐心的态度
            """,
            agent=self.agents['customer_service'],
            expected_output="专业的客服回复"
        )
        
        return [knowledge_task, service_task]


# 全局会话Agent管理器实例
session_agent_manager = SessionAgentManager()
