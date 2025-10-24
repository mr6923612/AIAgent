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
                        'age_seconds': (datetime.now() - agent.created_at).total_seconds(),
                        'ragflow_session_id': agent.ragflow_session_id or 'Not created yet'
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
    
    def __init__(self, session_id: str, llm, ragflow_client):
        self.session_id = session_id
        self.llm = llm
        self.ragflow_client = ragflow_client
        self.created_at = datetime.now()
        self.last_used = datetime.now()
        
        # RAGFlow会话ID（一个应用session对应一个RAGFlow session）
        self.ragflow_session_id = None
        
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

        return {
            'customer_service': customer_service_agent
        }
    
    def _create_crew(self):
        """创建Crew（只创建一次）"""
        return Crew(
            agents=[self.agents['customer_service']],
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
        
        # 1. 先通过RAGFlow获取知识
        ragflow_result = self._call_ragflow(customer_input, session_id)
        
        # 2. 创建客服回复任务（将RAGFlow结果注入到描述中）
        service_task = Task(
            description=f"""
            为客户提供专业、友好的回复。
            
            客户问题：{customer_input}
            会话ID：{session_id}
            知识库信息：{ragflow_result}
            
            请基于知识库信息提供：
            1. 自然、友好的回复
            2. 准确的答案
            3. 如果信息不足，提供合理的建议
            4. 保持专业和耐心的态度
            5. 像真人客服一样自然，不要提及"知识库"、"系统"等技术词汇
            """,
            agent=self.agents['customer_service'],
            expected_output="专业的客服回复"
        )
        
        return [service_task]
    
    def _call_ragflow(self, customer_input: str, session_id: str) -> str:
        """
        调用RAGFlow进行知识检索
        
        Args:
            customer_input: 客户输入
            session_id: 会话ID
            
        Returns:
            检索到的知识摘要
        """
        try:
            logger.info(f"[会话:{session_id[:8]}] 开始调用RAGFlow进行知识检索...")
            
            # 获取或创建RAGFlow会话
            ragflow_session_id = self._get_ragflow_session_id(session_id)
            logger.info(f"[会话:{session_id[:8]}] 使用RAGFlow会话: {ragflow_session_id}")
            
            # 调用RAGFlow API
            logger.info(f"[会话:{session_id[:8]}] 向RAGFlow发送问题: {customer_input}")
            answer_data = self.ragflow_client.converse(
                chat_id=DEFAULT_CHAT_ID,
                question=customer_input,
                session_id=ragflow_session_id
            )
            
            # 提取回答
            answer = answer_data.get('answer', '')
            reference = answer_data.get('reference', {})
            
            # 构建摘要
            summary_parts = []
            if answer:
                summary_parts.append(f"RAGFlow回答: {answer}")
                logger.info(f"[会话:{session_id[:8]}] RAGFlow返回答案，长度: {len(answer)}字符")
            
            if reference and reference.get('chunks'):
                chunks = reference['chunks']
                summary_parts.append(f"相关文档片段数: {len(chunks)}")
                logger.info(f"[会话:{session_id[:8]}] 找到{len(chunks)}个相关文档片段")
                for i, chunk in enumerate(chunks[:2]):  # 只显示前2个片段
                    content = chunk.get('content', '')[:150]
                    if content:
                        summary_parts.append(f"片段{i+1}: {content}...")
            
            result = "\n".join(summary_parts) if summary_parts else "未找到相关信息"
            logger.info(f"[会话:{session_id[:8]}] RAGFlow检索完成")
            return result
            
        except Exception as e:
            logger.error(f"[会话:{session_id[:8]}] 调用RAGFlow失败: {e}")
            import traceback
            logger.error(f"错误详情: {traceback.format_exc()}")
            return f"知识检索失败: {str(e)}"
    
    def _get_ragflow_session_id(self, session_id: str) -> str:
        """
        获取或创建RAGFlow会话ID（一个应用session对应一个RAGFlow session）
        
        Args:
            session_id: 应用会话ID
            
        Returns:
            RAGFlow会话ID
        """
        # 如果已有RAGFlow会话ID，直接返回
        if self.ragflow_session_id:
            logger.info(f"[会话:{session_id[:8]}] 复用已有RAGFlow会话: {self.ragflow_session_id}")
            return self.ragflow_session_id
        
        # 创建新的RAGFlow会话
        try:
            logger.info(f"[会话:{session_id[:8]}] 创建新的RAGFlow会话...")
            session_data = self.ragflow_client.create_session(
                chat_id=DEFAULT_CHAT_ID,
                name=f"会话_{session_id[:8]}",
                user_id=f"user_{session_id}"
            )
            self.ragflow_session_id = session_data.get('id', '')
            logger.info(f"[会话:{session_id[:8]}] RAGFlow会话创建成功: {self.ragflow_session_id}")
            return self.ragflow_session_id
        except Exception as e:
            logger.error(f"[会话:{session_id[:8]}] 创建RAGFlow会话失败: {e}")
            return ""
    
    def cleanup(self):
        """
        清理会话资源，包括删除对应的RAGFlow会话
        """
        if self.ragflow_session_id:
            try:
                logger.info(f"[会话:{self.session_id[:8]}] 删除RAGFlow会话: {self.ragflow_session_id}")
                self.ragflow_client.delete_session(
                    chat_id=DEFAULT_CHAT_ID,
                    session_ids=[self.ragflow_session_id]
                )
                logger.info(f"[会话:{self.session_id[:8]}] RAGFlow会话删除成功")
            except Exception as e:
                logger.error(f"[会话:{self.session_id[:8]}] 删除RAGFlow会话失败: {e}")


# 全局会话Agent管理器实例
session_agent_manager = SessionAgentManager()
