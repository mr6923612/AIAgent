#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的CrewAI RAG工具测试
测试CrewAI内置RagTool的基本功能
"""

import sys
import os
import unittest

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../crewaiBackend')))

def test_crewai_rag_import():
    """测试CrewAI RAG工具导入"""
    print("\n--- 测试CrewAI RAG工具导入 ---")
    
    try:
        from crewai_tools import RagTool
        print("SUCCESS: CrewAI RagTool导入成功")
        return True
    except ImportError as e:
        print(f"ERROR: CrewAI RagTool导入失败: {e}")
        print("请确保在正确的Python环境中运行（需要Python 3.10+）")
        return False

def test_rag_tool_creation():
    """测试RagTool创建"""
    print("\n--- 测试RagTool创建 ---")
    
    try:
        from crewai_tools import RagTool
        
        # 创建RagTool实例
        rag_tool = RagTool()
        print("SUCCESS: RagTool实例创建成功")
        
        # 测试基本配置
        config = {
            "chunker": {
                "chunk_size": 400,
                "chunk_overlap": 100,
                "length_function": "len",
                "min_chunk_size": 0
            }
        }
        
        rag_tool_with_config = RagTool(config=config, summarize=True)
        print("SUCCESS: 带配置的RagTool实例创建成功")
        
        return True
    except Exception as e:
        print(f"ERROR: RagTool创建失败: {e}")
        return False

def test_rag_tool_data_loading():
    """测试RagTool数据加载"""
    print("\n--- 测试RagTool数据加载 ---")
    
    try:
        from crewai_tools import RagTool
        
        rag_tool = RagTool()
        
        # 检查知识库文件是否存在
        knowledge_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../crewaiBackend/rag_documents/taobao_customer_service.md'))
        if os.path.exists(knowledge_base_path):
            rag_tool.add(data_type="file", path=knowledge_base_path)
            print(f"SUCCESS: 知识库文件加载成功: {knowledge_base_path}")
        else:
            print(f"WARNING: 知识库文件不存在: {knowledge_base_path}")
            # 创建测试文件
            with open(knowledge_base_path, 'w', encoding='utf-8') as f:
                f.write("这是一个测试知识库文档。产品A的特点是高性能。产品B的价格是100元。")
            rag_tool.add(data_type="file", path=knowledge_base_path)
            print(f"SUCCESS: 创建并加载测试知识库: {knowledge_base_path}")
        
        return True
    except Exception as e:
        print(f"ERROR: RagTool数据加载失败: {e}")
        return False

def test_rag_tool_search():
    """测试RagTool搜索功能"""
    print("\n--- 测试RagTool搜索功能 ---")
    
    try:
        from crewai_tools import RagTool
        
        rag_tool = RagTool()
        
        # 添加测试数据
        knowledge_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../crewaiBackend/rag_documents/taobao_customer_service.md'))
        if not os.path.exists(knowledge_base_path):
            with open(knowledge_base_path, 'w', encoding='utf-8') as f:
                f.write("这是一个测试知识库文档。产品A的特点是高性能。产品B的价格是100元。")
        
        rag_tool.add(data_type="file", path=knowledge_base_path)
        
        # 测试搜索
        query = "产品A的特点是什么？"
        print(f"查询: {query}")
        result = rag_tool.run(query)
        print(f"搜索结果: {result}")
        
        if result and "高性能" in result:
            print("SUCCESS: RagTool搜索功能正常")
            return True
        else:
            print("WARNING: RagTool搜索结果不符合预期")
            return False
            
    except Exception as e:
        print(f"ERROR: RagTool搜索测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("=" * 60)
    print("CrewAI RAG工具简单测试")
    print("=" * 60)
    
    tests = [
        ("导入测试", test_crewai_rag_import),
        ("创建测试", test_rag_tool_creation),
        ("数据加载测试", test_rag_tool_data_loading),
        ("搜索功能测试", test_rag_tool_search)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n运行测试: {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"ERROR: 测试 {test_name} 执行异常: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("测试结果总结:")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "SUCCESS: 通过" if result else "ERROR: 失败"
        print(f"- {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    print(f"总体结果: {'SUCCESS: 全部通过' if all_passed else 'ERROR: 有失败'}")
    print("=" * 60)
    
    if not all_passed:
        print("\n注意事项:")
        print("1. 确保在正确的Python环境中运行（需要Python 3.10+）")
        print("2. 确保已安装crewai-tools包")
        print("3. 确保有必要的依赖包")
    
    return all_passed

if __name__ == '__main__':
    main()
