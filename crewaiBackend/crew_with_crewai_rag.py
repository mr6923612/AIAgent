# -*- coding: utf-8 -*-
# 客服机器人CrewAI配置
# 使用CrewAI内置的RagTool替换自定义RAG实现

from crewai import Agent, Crew, Process, Task
from utils.jobManager import append_event
from crewai_tools import RagTool
import json
import os
import re
from datetime import datetime

class CrewtestprojectCrew:
    """客服机器人CrewAI类 - 使用CrewAI内置RagTool"""
    
    def __init__(self, job_id, llm):
        self.job_id = job_id
        self.llm = llm
        # 初始化CrewAI的RAG工具
        self.rag_tool = self._initialize_crewai_rag_tool()

    def _initialize_crewai_rag_tool(self):
        """初始化CrewAI的RAG工具并添加数据源"""
        # 配置RAG工具参数
        config = {
            "chunker": {
                "chunk_size": 400,
                "chunk_overlap": 100,
                "length_function": "len",
                "min_chunk_size": 0
            }
        }
        
        rag_tool_instance = RagTool(config=config, summarize=True)
        
        # 添加知识库文档
        knowledge_base_path = "rag_documents/taobao_customer_service.md"
        if os.path.exists(knowledge_base_path):
            rag_tool_instance.add(data_type="file", path=knowledge_base_path)
            append_event(self.job_id, f"RAG工具已加载知识库: {knowledge_base_path}")
        else:
            append_event(self.job_id, f"警告: 知识库文件不存在: {knowledge_base_path}")

        # 添加产品内容 (将JSON转换为文本格式)
        products_content_path = "rag_documents/products_content.json"
        if os.path.exists(products_content_path):
            # 读取JSON并转换为文本格式
            try:
                with open(products_content_path, 'r', encoding='utf-8') as f:
                    products_data = json.load(f)
                
                # 将产品信息转换为文本格式
                products_text = self._convert_products_to_text(products_data)
                
                # 创建临时文本文件
                temp_products_path = "rag_documents/products_content.txt"
                with open(temp_products_path, 'w', encoding='utf-8') as f:
                    f.write(products_text)
                
                rag_tool_instance.add(data_type="file", path=temp_products_path)
                append_event(self.job_id, f"RAG工具已加载产品内容: {temp_products_path}")
            except Exception as e:
                append_event(self.job_id, f"加载产品内容失败: {str(e)}")
        else:
            append_event(self.job_id, f"警告: 产品内容文件不存在: {products_content_path}")

        # 注意：CrewAI RagTool主要处理文本内容，图片检索功能有限
        append_event(self.job_id, "注意: CrewAI RagTool主要用于文本检索，图片检索功能可能需要额外定制。")

        return rag_tool_instance

    def _convert_products_to_text(self, products_data):
        """将产品JSON数据转换为文本格式"""
        text_content = "产品信息库:\n\n"
        
        for i, product in enumerate(products_data, 1):
            if "product_info" in product:
                product_info = product["product_info"]
                text_content += f"产品{i}:\n"
                text_content += f"名称: {product_info.get('name', '未知')}\n"
                text_content += f"描述: {product_info.get('description', '无描述')}\n"
                
                # 添加图片信息（如果有）
                if "images" in product and product["images"]:
                    text_content += f"图片: {', '.join([img.get('filename', '') for img in product['images']])}\n"
                
                text_content += "\n"
        
        return text_content

    def append_event_callback(self, task_output):
        """任务完成回调函数"""
        print("Callback called: %s", task_output)
        append_event(self.job_id, task_output.raw)
    
    def _create_rag_search_tool(self):
        """创建RAG搜索工具 (使用CrewAI RagTool)"""
        def rag_search_function(query: str, route_decision: str = "PRODUCT_QUERY") -> str:
            """使用CrewAI RagTool进行搜索"""
            try:
                append_event(self.job_id, f"使用CrewAI RagTool搜索: {query[:50]}...")
                
                # 直接调用RagTool的run方法
                results = self.rag_tool.run(query)
                
                if not results:
                    append_event(self.job_id, "CrewAI RagTool未找到相关信息")
                    return "未找到相关信息"
                
                append_event(self.job_id, f"CrewAI RagTool搜索完成，找到相关信息")
                return results  # RagTool通常返回格式化好的文本
                
            except Exception as e:
                append_event(self.job_id, f"CrewAI RagTool搜索失败: {str(e)}")
                return f"搜索失败: {str(e)}"
        
        return rag_search_function

    def _perform_rag_search(self, query: str, image_data: str = None, route_decision: str = "PRODUCT_QUERY") -> str:
        """使用CrewAI RagTool执行搜索 (适配旧接口)"""
        # 对于CrewAI RagTool，route_decision和image_data通常在工具内部处理或通过LLM的提示词引导
        # 这里简化为直接调用RagTool
        return self._create_rag_search_tool()(query)

    def create_agents(self):
        """创建客服机器人相关的Agent"""
        
        # 1. 输入理解Agent
        input_analyzer = Agent(
            role="客户输入理解助手",
            goal="理解客户的输入内容，进行路由判断",
            backstory="""你是一个简洁高效的输入理解助手。
            你的职责：
            - 分析客户输入的文字内容
            - 判断问题是通用客服问题还是产品问题
            - 提取关键信息""",
            verbose=False,
            llm=self.llm,
        )

        # 2. 知识检索Agent (使用CrewAI RagTool)
        knowledge_retriever = Agent(
            role="知识检索助手",
            goal="从知识库中快速检索相关信息",
            backstory="""你是一个高效的知识检索助手。
            你的职责：
            - 根据客户问题从知识库检索相关信息
            - 整理和总结检索结果
            - 提供准确的知识支持""",
            verbose=False,
            llm=self.llm,
            tools=[self.rag_tool]  # 直接使用CrewAI的RagTool
        )

        # 3. 拟人客服Agent
        customer_service_agent = Agent(
            role="拟人客服机器人",
            goal="以拟人的方式回复客户，提供友好专业的客服体验",
            backstory="""你是一个拟人的客服机器人，像真人客服一样与客户交流。
            你的特点：
            - 语言自然、友好、有温度
            - 像真人一样理解和回应客户
            - 基于知识库信息提供准确回答
            - 保持客服的专业性和亲和力""",
            verbose=False,
            llm=self.llm,
        )

        return {
            "input_analyzer": input_analyzer,
            "knowledge_retriever": knowledge_retriever,
            "customer_service_agent": customer_service_agent
        }

    def create_input_analysis_task(self, agents, inputs):
        """创建输入分析任务"""
        return Task(
            description=f"""
            理解客户输入：
            
            客户输入：{inputs.get('customer_input', '')}
            {'图片数据：已上传图片文件' if inputs.get('image_data') else ''}
            
            请执行：
            1. 判断问题类型：通用客服问题 或 产品问题
            2. 提取关键信息
            
            输出格式：
            ROUTE: [GENERAL_SERVICE 或 PRODUCT_QUERY]
            问题分类：[具体问题类型]
            关键信息：[提取的关键信息]
            """,
            expected_output="路由决策和关键信息",
            agent=agents["input_analyzer"],
            callback=self.append_event_callback,
        )

    def create_tasks(self, agents, inputs, route_decision="PRODUCT_QUERY"):
        """创建客服机器人的任务流程"""
        
        # 任务1：输入理解 (已在kickoff中单独执行)
        
        # 任务2：知识检索
        knowledge_retrieval_task = Task(
            description=f"""
            从知识库检索相关信息：
            
            客户问题：{inputs.get('customer_input', '')}
            路由决策：{route_decision}
            
            请使用RAG检索器从知识库中搜索相关信息，然后整理检索结果，提供相关信息摘要。
            """,
            expected_output="检索到的相关信息摘要",
            agent=agents["knowledge_retriever"],
            callback=self.append_event_callback,
        )

        # 任务3：拟人客服回复
        customer_service_task = Task(
            description=f"""
            以拟人方式回复客户：
            
            客户问题：{inputs.get('customer_input', '')}
            检索信息：{knowledge_retrieval_task}
            
            请像真人客服一样回复客户，语言自然友好，基于检索信息提供准确回答。
            """,
            expected_output="拟人的客服回复",
            agent=agents["customer_service_agent"],
            callback=self.append_event_callback,
        )

        return [
            knowledge_retrieval_task,
            customer_service_task
        ]

    def create_crew(self, agents, tasks):
        """创建客服机器人Crew"""
        return Crew(
            agents=list(agents.values()),
            tasks=tasks,
            process=Process.sequential,  # 顺序执行
            verbose=False
        )

    def kickoff(self, inputs):
        """启动客服机器人分析流程"""
        try:
            # 创建Agent
            append_event(self.job_id, "正在初始化智能客服机器人...")
            agents = self.create_agents()
            append_event(self.job_id, "智能客服机器人初始化完成")
            
            # 执行输入理解和路由判断
            append_event(self.job_id, "input_analyzer 开始分析客户输入...")
            input_task = self.create_input_analysis_task(agents, inputs)
            try:
                input_result = input_task.execute()
                append_event(self.job_id, "input_analyzer 分析完成")
            except (StopIteration, Exception) as e:
                append_event(self.job_id, f"input_analyzer 执行异常，使用备用路由判断: {str(e)}")
                # 根据输入内容简单判断路由
                customer_input = inputs.get('customer_input', '').lower()
                if any(keyword in customer_input for keyword in ['退货', '换货', '物流', '支付', '会员', '优惠', '客服', '投诉', '退款', '发货', '快递']):
                    input_result = "ROUTE: GENERAL_SERVICE\n通用客服问题"
                else:
                    input_result = "ROUTE: PRODUCT_QUERY\n产品相关问题"
                append_event(self.job_id, f"备用路由判断完成: {input_result}")
            
            # 检查路由决策
            route_decision = self._extract_route_decision(input_result)
            append_event(self.job_id, f"路由决策确定: {route_decision}")
            
            # 执行知识检索和客服回复
            append_event(self.job_id, "knowledge_retriever 开始检索相关知识...")
            tasks = self.create_tasks(agents, inputs, route_decision)
            crew = self.create_crew(agents, tasks)
            try:
                results = crew.kickoff()
                append_event(self.job_id, "knowledge_retriever 和 customer_service_agent 工作完成")
            except (StopIteration, Exception) as e:
                append_event(self.job_id, f"knowledge_retriever 和 customer_service_agent 执行异常: {str(e)}")
                # 提供基于路由决策的简单回答
                if route_decision == "GENERAL_SERVICE":
                    results = "抱歉，系统暂时无法处理您的通用客服问题，请稍后重试或联系人工客服。"
                    append_event(self.job_id, "使用通用客服备用回复")
                else:
                    results = "抱歉，系统暂时无法处理您的产品咨询，请稍后重试或联系人工客服。"
                    append_event(self.job_id, "使用产品咨询备用回复")
            
            final_result = self.format_final_result(results, inputs)
            return final_result
                    
        except Exception as e:
            append_event(self.job_id, f"启动客服机器人分析流程失败: {str(e)}")
            return f"启动客服机器人分析流程失败: {str(e)}"

    def _extract_route_decision(self, input_result: str) -> str:
        """从输入分析结果中提取路由决策"""
        match = re.search(r"ROUTE:\s*(GENERAL_SERVICE|PRODUCT_QUERY)", input_result)
        if match:
            return match.group(1)
        return "PRODUCT_QUERY"  # 默认路由

    def format_final_result(self, results, inputs):
        """格式化最终结果"""
        # 假设results已经是最终回复文本
        return {
            "customer_input": inputs.get('customer_input', ''),
            "response": results,
            "timestamp": datetime.now().isoformat()
        }
