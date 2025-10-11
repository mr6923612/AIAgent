#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CrewAI内置RAG工具测试
测试单一功能：CrewAI内置RAG工具的使用
支持多种输入：文字查询、图片查询
"""

import os
import sys
import base64

# 添加后端路径
sys.path.append('../crewaiBackend')

from crewai_tools import RagTool
from utils.myLLM import my_llm

def test_crewai_rag_tool():
    """测试CrewAI内置RAG工具"""
    print("=" * 80)
    print("CrewAI内置RAG工具测试")
    print("=" * 80)
    
    try:
        # 创建RAG工具
        print("1. 创建CrewAI RAG工具...")
        rag_tool = RagTool()
        print("✅ RAG工具创建成功")
        
        # 添加知识库文档
        print("\n2. 添加知识库文档...")
        knowledge_base_path = "../crewaiBackend/rag_documents/taobao_customer_service.md"
        if os.path.exists(knowledge_base_path):
            rag_tool.add(data_type="file", path=knowledge_base_path)
            print(f"✅ 已添加知识库文档: {knowledge_base_path}")
        else:
            print(f"❌ 知识库文档不存在: {knowledge_base_path}")
        
        # 添加产品内容JSON文件
        print("\n3. 添加产品内容...")
        products_path = "../crewaiBackend/rag_documents/products_content.json"
        if os.path.exists(products_path):
            rag_tool.add(data_type="file", path=products_path)
            print(f"✅ 已添加产品内容: {products_path}")
        else:
            print(f"❌ 产品内容文件不存在: {products_path}")
        
        # 添加图片文件
        print("\n4. 添加图片文件...")
        images_path = "../crewaiBackend/rag_documents/images"
        if os.path.exists(images_path):
            image_count = 0
            for filename in os.listdir(images_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    image_path = os.path.join(images_path, filename)
                    try:
                        rag_tool.add(data_type="file", path=image_path)
                        print(f"✅ 已添加图片: {filename}")
                        image_count += 1
                    except Exception as e:
                        print(f"⚠️ 添加图片失败 {filename}: {str(e)}")
            
            if image_count == 0:
                print("⚠️ 未找到图片文件")
        else:
            print(f"❌ 图片目录不存在: {images_path}")
        
        # 测试RAG工具功能
        print("\n5. 测试RAG工具功能...")
        test_queries = [
            "祛疤膏产品信息",
            "正品保证",
            "发货时间",
            "优惠活动",
            "退换货政策"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n测试查询 {i}/{len(test_queries)}: {query}")
            print("-" * 40)
            
            try:
                # 使用RAG工具进行搜索
                result = rag_tool.run(query)
                print(f"✅ 搜索成功")
                print(f"结果: {result[:200]}..." if len(str(result)) > 200 else f"结果: {result}")
                
            except Exception as e:
                print(f"❌ 搜索失败: {str(e)}")
        
        print(f"\n{'='*80}")
        print("CrewAI RAG工具测试完成")
        print(f"{'='*80}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_crewai_rag_with_agent():
    """测试CrewAI RAG工具与Agent的集成"""
    print("\n" + "=" * 80)
    print("CrewAI RAG工具与Agent集成测试")
    print("=" * 80)
    
    try:
        from crewai import Agent
        
        # 创建RAG工具
        rag_tool = RagTool()
        
        # 添加知识库
        knowledge_base_path = "../crewaiBackend/rag_documents/taobao_customer_service.md"
        if os.path.exists(knowledge_base_path):
            rag_tool.add(data_type="file", path=knowledge_base_path)
        
        products_path = "../crewaiBackend/rag_documents/products_content.json"
        if os.path.exists(products_path):
            rag_tool.add(data_type="file", path=products_path)
        
        # 创建使用RAG工具的Agent
        print("1. 创建使用RAG工具的Agent...")
        knowledge_agent = Agent(
            role="知识检索助手",
            goal="从知识库中检索相关信息",
            backstory="你是一个高效的知识检索助手，能够使用RAG工具从知识库中检索相关信息。",
            verbose=True,
            llm=my_llm("google"),
            tools=[rag_tool]
        )
        print("✅ Agent创建成功")
        
        # 测试Agent使用RAG工具
        print("\n2. 测试Agent使用RAG工具...")
        test_query = "祛疤膏产品的功效和使用方法"
        
        try:
            # 创建任务
            from crewai import Task
            task = Task(
                description=f"请使用RAG工具搜索关于'{test_query}'的信息，并提供详细的回答。",
                expected_output="基于RAG工具检索结果的详细回答",
                agent=knowledge_agent
            )
            
            print(f"查询: {test_query}")
            print("正在执行任务...")
            
            # 执行任务
            result = task.execute()
            print("✅ 任务执行成功")
            print(f"结果: {result}")
            
        except Exception as e:
            print(f"❌ 任务执行失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ 集成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🧪 CrewAI内置RAG工具测试")
    print("=" * 80)
    
    # 测试1: 基础RAG工具功能
    success1 = test_crewai_rag_tool()
    
    # 测试2: RAG工具与Agent集成
    success2 = test_crewai_rag_with_agent()
    
    # 输出测试结果
    print(f"\n{'='*80}")
    print("测试结果总结")
    print(f"{'='*80}")
    
    print(f"基础RAG工具测试: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"RAG工具与Agent集成测试: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if success1 and success2:
        print("\n🎉 所有CrewAI RAG工具测试通过!")
        return True
    else:
        print("\n⚠️ 部分测试失败")
        return False

if __name__ == "__main__":
    main()
