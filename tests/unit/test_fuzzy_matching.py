#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模糊匹配功能测试
测试单一功能：模糊匹配算法
支持多种输入：文字查询、图片查询、不同匹配参数
"""

import os
import sys
import base64
import json

# 添加后端路径
sys.path.append('../crewaiBackend')

from utils.rag_retriever import MultimodalRAGRetriever

def test_fuzzy_matching():
    """测试模糊匹配功能"""
    print("=" * 80)
    print("模糊匹配功能测试")
    print("=" * 80)
    
    # 初始化RAG检索器
    rag_retriever = MultimodalRAGRetriever()
    
    # 测试用例：文字查询
    text_test_cases = [
        {
            "query": "祛疤膏",
            "description": "产品名称模糊匹配",
            "expected_type": "product",
            "min_relevance": 0.1
        },
        {
            "query": "疤痕",
            "description": "产品描述关键词匹配",
            "expected_type": "product", 
            "min_relevance": 0.1
        },
        {
            "query": "正品",
            "description": "客服文档匹配",
            "expected_type": "text",
            "min_relevance": 0.1
        },
        {
            "query": "发货时间",
            "description": "客服问答匹配",
            "expected_type": "text",
            "min_relevance": 0.1
        },
        {
            "query": "优惠活动",
            "description": "价格优惠类匹配",
            "expected_type": "text",
            "min_relevance": 0.1
        },
        {
            "query": "退换货",
            "description": "售后服务匹配",
            "expected_type": "text",
            "min_relevance": 0.1
        },
        {
            "query": "不相关查询",
            "description": "无匹配内容测试",
            "expected_type": "none",
            "min_relevance": 0.0
        }
    ]
    
    print("\n" + "="*60)
    print("文字查询模糊匹配测试")
    print("="*60)
    
    text_results = []
    for i, test_case in enumerate(text_test_cases, 1):
        print(f"\n测试 {i}/{len(text_test_cases)}: {test_case['description']}")
        print(f"查询: {test_case['query']}")
        print("-" * 40)
        
        try:
            # 测试产品查询
            results = rag_retriever.search(
                query=test_case['query'],
                max_results=3,
                route_decision="PRODUCT_QUERY"
            )
            
            print(f"找到 {len(results)} 个匹配结果:")
            for j, result in enumerate(results, 1):
                print(f"  {j}. 类型: {result.get('type', 'unknown')}")
                print(f"     相关性: {result.get('relevance', 0):.3f}")
                print(f"     来源: {result.get('source', 'unknown')}")
                print(f"     内容: {result.get('content', '')[:100]}...")
                print()
            
            # 验证结果
            if results:
                best_result = results[0]
                relevance = best_result.get('relevance', 0)
                result_type = best_result.get('type', 'unknown')
                
                if relevance >= test_case['min_relevance']:
                    print(f"✅ 匹配成功: 相关性 {relevance:.3f}")
                    text_results.append({
                        'query': test_case['query'],
                        'success': True,
                        'relevance': relevance,
                        'type': result_type,
                        'results_count': len(results)
                    })
                else:
                    print(f"❌ 相关性不足: {relevance:.3f} < {test_case['min_relevance']}")
                    text_results.append({
                        'query': test_case['query'],
                        'success': False,
                        'relevance': relevance,
                        'error': '相关性不足'
                    })
            else:
                print("❌ 无匹配结果")
                text_results.append({
                    'query': test_case['query'],
                    'success': False,
                    'relevance': 0,
                    'error': '无匹配结果'
                })
                
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            text_results.append({
                'query': test_case['query'],
                'success': False,
                'relevance': 0,
                'error': str(e)
            })
    
    # 测试图片查询
    print("\n" + "="*60)
    print("图片查询模糊匹配测试")
    print("="*60)
    
    image_test_cases = [
        {
            "file": "../crewaiBackend/rag_documents/images/extracted_1.png",
            "description": "产品图片匹配测试",
            "expected_similarity": 0.7
        }
    ]
    
    image_results = []
    for i, test_case in enumerate(image_test_cases, 1):
        print(f"\n测试 {i}/{len(image_test_cases)}: {test_case['description']}")
        print(f"图片文件: {test_case['file']}")
        print("-" * 40)
        
        if not os.path.exists(test_case['file']):
            print(f"❌ 图片文件不存在: {test_case['file']}")
            image_results.append({
                'file': test_case['file'],
                'success': False,
                'error': '文件不存在'
            })
            continue
        
        try:
            # 读取图片并转换为Base64
            with open(test_case['file'], 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            print(f"图片大小: {len(image_data)} bytes (Base64)")
            
            # 测试图片搜索
            results = rag_retriever.search(
                query="",
                max_results=3,
                input_image_data=image_data,
                route_decision="PRODUCT_QUERY"
            )
            
            print(f"找到 {len(results)} 个图片匹配结果:")
            for j, result in enumerate(results, 1):
                print(f"  {j}. 类型: {result.get('type', 'unknown')}")
                print(f"     相似度: {result.get('relevance', 0):.3f}")
                print(f"     来源: {result.get('source', 'unknown')}")
                if 'product_info' in result:
                    print(f"     产品: {result['product_info'].get('name', 'unknown')}")
                print()
            
            # 验证结果
            if results:
                best_result = results[0]
                similarity = best_result.get('relevance', 0)
                
                if similarity >= test_case['expected_similarity']:
                    print(f"✅ 图片匹配成功: 相似度 {similarity:.3f}")
                    image_results.append({
                        'file': test_case['file'],
                        'success': True,
                        'similarity': similarity,
                        'results_count': len(results)
                    })
                else:
                    print(f"❌ 相似度不足: {similarity:.3f} < {test_case['expected_similarity']}")
                    image_results.append({
                        'file': test_case['file'],
                        'success': False,
                        'similarity': similarity,
                        'error': '相似度不足'
                    })
            else:
                print("❌ 无图片匹配结果")
                image_results.append({
                    'file': test_case['file'],
                    'success': False,
                    'similarity': 0,
                    'error': '无匹配结果'
                })
                
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            image_results.append({
                'file': test_case['file'],
                'success': False,
                'similarity': 0,
                'error': str(e)
            })
    
    # 测试不同匹配参数
    print("\n" + "="*60)
    print("匹配参数测试")
    print("="*60)
    
    parameter_tests = [
        {
            "query": "祛疤",
            "max_results": 1,
            "description": "限制结果数量"
        },
        {
            "query": "祛疤",
            "max_results": 5,
            "description": "增加结果数量"
        }
    ]
    
    parameter_results = []
    for i, test_case in enumerate(parameter_tests, 1):
        print(f"\n测试 {i}/{len(parameter_tests)}: {test_case['description']}")
        print(f"查询: {test_case['query']}, 最大结果数: {test_case['max_results']}")
        print("-" * 40)
        
        try:
            results = rag_retriever.search(
                query=test_case['query'],
                max_results=test_case['max_results'],
                route_decision="PRODUCT_QUERY"
            )
            
            print(f"返回结果数: {len(results)} (期望: {test_case['max_results']})")
            
            if len(results) <= test_case['max_results']:
                print("✅ 参数设置正确")
                parameter_results.append({
                    'test': test_case['description'],
                    'success': True,
                    'returned_count': len(results),
                    'expected_count': test_case['max_results']
                })
            else:
                print("❌ 返回结果数超出限制")
                parameter_results.append({
                    'test': test_case['description'],
                    'success': False,
                    'returned_count': len(results),
                    'expected_count': test_case['max_results'],
                    'error': '结果数超出限制'
                })
                
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            parameter_results.append({
                'test': test_case['description'],
                'success': False,
                'error': str(e)
            })
    
    # 输出测试结果总结
    print(f"\n{'='*80}")
    print("模糊匹配测试结果总结")
    print(f"{'='*80}")
    
    # 文字查询结果
    print(f"\n📝 文字查询测试: {sum(1 for r in text_results if r['success'])}/{len(text_results)} 成功")
    for result in text_results:
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {result['query']}: 相关性 {result['relevance']:.3f}")
        if not result['success'] and 'error' in result:
            print(f"    错误: {result['error']}")
    
    # 图片查询结果
    print(f"\n🖼️ 图片查询测试: {sum(1 for r in image_results if r['success'])}/{len(image_results)} 成功")
    for result in image_results:
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {os.path.basename(result['file'])}: 相似度 {result.get('similarity', 0):.3f}")
        if not result['success'] and 'error' in result:
            print(f"    错误: {result['error']}")
    
    # 参数测试结果
    print(f"\n⚙️ 参数测试: {sum(1 for r in parameter_results if r['success'])}/{len(parameter_results)} 成功")
    for result in parameter_results:
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {result['test']}")
        if not result['success'] and 'error' in result:
            print(f"    错误: {result['error']}")
    
    # 总体结果
    total_tests = len(text_results) + len(image_results) + len(parameter_results)
    total_success = sum(1 for r in text_results if r['success']) + \
                   sum(1 for r in image_results if r['success']) + \
                   sum(1 for r in parameter_results if r['success'])
    
    print(f"\n🎯 总体结果: {total_success}/{total_tests} 个测试成功")
    
    if total_success == total_tests:
        print("🎉 所有模糊匹配测试通过!")
        return True
    else:
        print("⚠️ 部分模糊匹配测试失败")
        return False

def show_matching_parameters():
    """显示模糊匹配参数配置"""
    print("\n" + "="*80)
    print("模糊匹配参数配置说明")
    print("="*80)
    
    print("""
📋 可调节的模糊匹配参数位置:

1. 相关性阈值 (crewaiBackend/utils/rag_retriever.py):
   - 第189行: if relevance > 0.1  # 文字匹配最低阈值
   - 第150行: if best_result["relevance"] < 0.9  # 询问确认阈值
   - 第274行: if similarity > 0.7  # 图片相似度阈值

2. 匹配算法参数 (第337-390行 _calculate_relevance方法):
   - 第346行: return 1.0  # 完全匹配分数
   - 第353行: return 0.8  # 部分匹配分数
   - 第368行: return max(0.2, min(relevance, 1.0))  # 词汇匹配分数范围
   - 第377行: return 0.3  # 相似词汇匹配分数
   - 第388行: return 0.2  # 字符级匹配分数

3. 搜索策略参数:
   - max_results: 最大返回结果数 (默认5)
   - route_decision: 路由决策 ("PRODUCT_QUERY" 或 "GENERAL_SERVICE")

🔧 如何调节参数:

1. 降低匹配阈值 (更宽松):
   - 将 0.1 改为 0.05 或更低
   - 将 0.7 改为 0.5 或更低

2. 提高匹配精度 (更严格):
   - 将 0.1 改为 0.3 或更高
   - 将 0.7 改为 0.8 或更高

3. 调整匹配分数权重:
   - 修改 _calculate_relevance 方法中的分数值
   - 调整不同匹配策略的优先级

4. 修改搜索范围:
   - 调整 max_results 参数
   - 修改 route_decision 策略
""")

if __name__ == "__main__":
    # 显示参数配置说明
    show_matching_parameters()
    
    # 运行模糊匹配测试
    test_fuzzy_matching()
