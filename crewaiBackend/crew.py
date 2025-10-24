# -*- coding: utf-8 -*-
# 客服机器人CrewAI配置
# 使用RAGFlow替换CrewAI内置RagTool

from crewai import Agent, Crew, Process
from .utils.jobManager import append_event
from .utils.ragflow_client import create_ragflow_client, DEFAULT_CHAT_ID
import json
import os
import requests
from datetime import datetime

# 导入配置
try:
    from config import config
except ImportError:
    config = None


class CrewtestprojectCrew:
    """客服机器人CrewAI类 - 使用RAGFlow替换CrewAI RagTool"""
    
    def __init__(self, job_id, llm):
        self.job_id = job_id
        self.llm = llm
        # 初始化RAGFlow客户端
        self.ragflow_client = create_ragflow_client()
        self.session_id = None  # 存储会话ID

    def append_event_callback(self, task_output):
        """任务完成回调函数"""
        print("Callback called:", task_output)
        append_event(self.job_id, task_output.raw if hasattr(task_output, "raw") else str(task_output))

    def create_agents(self):
        """创建客服机器人相关的Agent"""

        # 1. 智能客服Agent
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
            - 即使没有相关信息，也会基于专业知识尽力帮助客户
            - 回复简洁明了，直接解决客户问题
            - 回答完全像真人客服一样自然，不会有任何技术痕迹
            - 如果没有相关信息 输出暂时不了解
            - 采用这样的问答方式：
            Can you do 500$?
            Sry mate, that's too low. Best I can do is $650.""",
            verbose=False,
            llm=self.llm,
        )

        return {
            "customer_service_agent": customer_service_agent
        }

    def call_ragflow(self, customer_input, route_decision="PRODUCT_QUERY", ragflow_session_id=None):
        """调用RAGFlow进行知识检索并返回摘要"""
        try:
            append_event(self.job_id, f"开始调用RAGFlow进行知识检索...")
            
            # 使用传入的RAGFlow会话ID
            session_id_to_use = ragflow_session_id
            
            if not session_id_to_use:
                append_event(self.job_id, "警告: 没有RAGFlow会话ID，将创建新会话")
                # 只有在没有会话ID时才创建新会话
                session_data = self.ragflow_client.create_session(
                    chat_id=DEFAULT_CHAT_ID,
                    name=f"客服会话_{self.job_id}",
                    user_id=f"user_{self.job_id}"
                )
                session_id_to_use = session_data.get('id')
                append_event(self.job_id, f"RAGFlow会话创建成功: {session_id_to_use}")
            else:
                append_event(self.job_id, f"使用现有RAGFlow会话: {session_id_to_use}")
            
            # 使用RAGFlow进行对话
            append_event(self.job_id, f"向RAGFlow发送问题: {customer_input}")
            answer_data = self.ragflow_client.converse(
                chat_id=DEFAULT_CHAT_ID,
                question=customer_input,
                session_id=session_id_to_use
            )
            
            # 提取回答和引用信息
            answer = answer_data.get('answer', '')
            reference = answer_data.get('reference', {})
            
            # 构建摘要信息
            summary_parts = []
            if answer:
                summary_parts.append(f"回答: {answer}")
            
            if reference and reference.get('chunks'):
                chunks = reference['chunks']
                summary_parts.append(f"相关文档片段数量: {len(chunks)}")
                for i, chunk in enumerate(chunks[:3]):  # 只显示前3个片段
                    content = chunk.get('content', '')[:200] + '...' if len(chunk.get('content', '')) > 200 else chunk.get('content', '')
                    summary_parts.append(f"片段{i+1}: {content}")
            
            summary = "\n".join(summary_parts) if summary_parts else "未找到相关信息"
            
            append_event(self.job_id, f"RAGFlow检索完成，获得{len(answer)}字符的回答")
            return summary
            
        except Exception as e:
            append_event(self.job_id, f"调用RAGFlow失败: {str(e)}")
            import traceback
            append_event(self.job_id, f"错误详情: {traceback.format_exc()}")
            # 出错时返回空摘要
            return ""

    def create_tasks(self, agents, inputs, route_decision="PRODUCT_QUERY"):
        """创建客服机器人的任务流程（不再使用CrewAI Task进行知识检索）"""
        from crewai import Task

        customer_input = inputs.get("customer_input", "")
        session_id = inputs.get("session_id")
        
        # 获取上下文信息和RAGFlow会话ID
        context_info = ""
        ragflow_session_id = None
        if session_id:
            try:
                from utils.sessionManager import SessionManager
                session_manager = SessionManager()
                session = session_manager.get_session(session_id)
                if session:
                    context_info = session.get_context_summary(max_messages=5)
                    ragflow_session_id = session.ragflow_session_id
                    append_event(self.job_id, f"获取到会话上下文，包含{len(session.messages)}条消息")
                    append_event(self.job_id, f"RAGFlow会话ID: {ragflow_session_id}")
            except Exception as e:
                append_event(self.job_id, f"获取上下文失败: {str(e)}")

        # 直接调用RAGFlow，传递会话ID
        retrieved_summary = self.call_ragflow(customer_input, route_decision, ragflow_session_id)

        # 智能客服回复任务（基于RAGFlow结果）
        customer_service_task = Task(
            description=f"""
                作为智能客服代表，请为客户提供专业、友好的服务。
                
                客户问题：{customer_input}
                
                知识库信息：{retrieved_summary}
                
                对话历史：{context_info}
                
                重要提醒：
                - 你的回答必须像真人客服一样自然，不要暴露任何技术细节
                - 绝对不要提及"知识库"、"数据库"、"系统"、"AI"等词汇
                - 不要说明信息来源或检索过程
                - 就像你本来就了解这些信息一样自然地回答
                - 不要主动建议客户去官网、门店或其他渠道获取信息
                - 不要添加"或者您可以在..."、"建议您..."等扩展性建议
                - 只回答客户直接问的问题，不要额外推荐其他渠道
                
                服务要求：
                1. 自动识别客户语言并使用相同语言回复（中文/英文/其他语言）
                2. 语言表达自然流畅，像朋友一样亲切交流
                3. 准确理解客户需求，提供专业回答
                4. 基于提供的知识库信息进行回答，确保信息准确性
                5. 如果客户问的是关于之前对话的问题，请结合对话历史来回答
                6. 即使没有相关信息，也要基于专业知识尽力帮助客户
                7. 始终保持耐心和专业态度
                8. 回复简洁明了，直接解决客户问题
                9. 回答要像真人客服一样自然，不要有任何技术痕迹
                10. 专注于回答客户的问题，不要主动推荐其他渠道或扩展建议
                11. 如果客户问"刚才你介绍了什么功能？"或类似问题，请结合对话历史中的相关信息来回答
                12. 如果没有相关信息 输出暂时不了解
                13. 采用这样的问答方式：
                Can you do 500$?
                Sry mate, that's too low. Best I can do is $650.
            """,
            expected_output="像真人客服一样的自然回复，使用客户相同的语言，结合对话历史和知识库信息",
            agent=agents["customer_service_agent"]
        )

        return [customer_service_task]

    def create_crew(self, agents, tasks):
        """创建客服机器人Crew（原Crew结构可保留）"""
        return Crew(
            agents=list(agents.values()),
            tasks=tasks,
            process=Process.sequential,
            verbose=False
        )

    def kickoff(self, inputs):
        """启动客服机器人分析流程"""
        try:
            append_event(self.job_id, "正在初始化智能客服机器人...")
            agents = self.create_agents()
            append_event(self.job_id, "智能客服机器人初始化完成")
            
            append_event(self.job_id, "开始执行客服机器人任务流程...")
            tasks = self.create_tasks(agents, inputs)
            crew = self.create_crew(agents, tasks)
            
            try:
                results = crew.kickoff()
                append_event(self.job_id, "客服机器人任务流程完成")
            except (StopIteration, Exception) as e:
                append_event(self.job_id, f"客服机器人任务执行异常: {str(e)}")
                results = "抱歉，系统暂时无法处理您的请求，请稍后重试或联系人工客服。"
                append_event(self.job_id, "使用备用回复")
            
            final_result = self.format_final_result(results, inputs)
            return final_result
        except Exception as e:
            append_event(self.job_id, f"启动客服机器人分析流程失败: {str(e)}")
            return f"启动客服机器人分析流程失败: {str(e)}"

    def format_final_result(self, results, inputs):
        """格式化最终结果，只返回简洁的自然回答"""
        # 提取CrewAI的原始回答
        if hasattr(results, 'raw'):
            response_text = results.raw
        elif hasattr(results, 'tasks_output') and results.tasks_output:
            # 从任务输出中提取回答
            response_text = results.tasks_output[0].raw
        else:
            response_text = str(results)
        
        # 只返回简洁的回答
        return response_text
