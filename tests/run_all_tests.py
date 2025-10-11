#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行器
运行所有测试用例
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_test(test_module, test_name):
    """运行单个测试模块"""
    print(f"\n{'='*80}")
    print(f"运行测试: {test_name}")
    print(f"{'='*80}")
    
    try:
        # 动态导入测试模块
        module = __import__(test_module)
        
        # 运行测试
        if hasattr(module, 'main'):
            result = module.main()
            return result
        elif hasattr(module, 'test_speech_to_text'):
            result = module.test_speech_to_text()
            return result
        elif hasattr(module, 'test_fuzzy_matching'):
            result = module.test_fuzzy_matching()
            return result
        else:
            print(f"❌ 测试模块 {test_module} 没有找到测试函数")
            return False
            
    except Exception as e:
        print(f"❌ 运行测试 {test_name} 时出错: {str(e)}")
        return False

def main():
    """运行所有测试"""
    print("🧪 运行所有测试用例")
    print("=" * 80)
    
    # 测试列表（按新的目录结构）
    tests = [
        {
            'module': 'unit.test_speech_to_text',
            'name': '语音转文字功能测试（单元测试）'
        },
        {
            'module': 'unit.test_fuzzy_matching',
            'name': '模糊匹配功能测试（单元测试）'
        },
        {
            'module': 'integration.test_backend_api_optimized', 
            'name': '优化的后端API测试（集成测试）'
        },
        {
            'module': 'llm_tests.test_integration',
            'name': '完整集成测试（LLM测试）'
        }
    ]
    
    results = []
    
    for test in tests:
        result = run_test(test['module'], test['name'])
        results.append({
            'name': test['name'],
            'success': result
        })
    
    # 输出最终结果
    print(f"\n{'='*80}")
    print("所有测试结果总结")
    print(f"{'='*80}")
    
    success_count = 0
    for result in results:
        status = "✅ 通过" if result['success'] else "❌ 失败"
        print(f"{result['name']}: {status}")
        if result['success']:
            success_count += 1
    
    print(f"\n总计: {success_count}/{len(results)} 个测试套件通过")
    
    if success_count == len(results):
        print("🎉 所有测试通过!")
        return True
    else:
        print("⚠️ 部分测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
