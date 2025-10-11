#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分类测试运行器
支持按类别运行测试：单元测试、集成测试、LLM测试
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_unit_tests():
    """运行单元测试（不需要LLM）"""
    print("🧪 运行单元测试（不需要LLM）")
    print("=" * 60)
    
    unit_tests = [
        {
            'module': 'unit.test_speech_to_text',
            'name': '语音转文字功能测试'
        },
        {
            'module': 'unit.test_fuzzy_matching',
            'name': '模糊匹配功能测试'
        },
        {
            'module': 'unit.test_crewai_rag',
            'name': 'CrewAI内置RAG工具测试'
        },
        {
            'module': 'unit.test_rag_comparison',
            'name': 'RAG实现对比测试'
        }
    ]
    
    results = []
    
    for test in unit_tests:
        print(f"\n运行: {test['name']}")
        print("-" * 40)
        
        try:
            module = __import__(test['module'])
            if hasattr(module, 'test_speech_to_text'):
                result = module.test_speech_to_text()
            elif hasattr(module, 'test_fuzzy_matching'):
                result = module.test_fuzzy_matching()
            elif hasattr(module, 'test_crewai_rag'):
                result = module.test_crewai_rag()
            elif hasattr(module, 'test_rag_comparison'):
                result = module.test_rag_comparison()
            elif hasattr(module, 'main'):
                result = module.main()
            else:
                print(f"❌ 测试模块 {test['module']} 没有找到测试函数")
                result = False
            
            results.append({
                'name': test['name'],
                'success': result
            })
            
        except Exception as e:
            print(f"❌ 运行测试 {test['name']} 时出错: {str(e)}")
            results.append({
                'name': test['name'],
                'success': False
            })
    
    return results

def run_integration_tests():
    """运行集成测试（需要后端API但避免LLM）"""
    print("🔗 运行集成测试（需要后端API但避免LLM）")
    print("=" * 60)
    
    integration_tests = [
        {
            'module': 'integration.test_backend_api_optimized',
            'name': '优化的后端API测试'
        }
    ]
    
    results = []
    
    for test in integration_tests:
        print(f"\n运行: {test['name']}")
        print("-" * 40)
        
        try:
            module = __import__(test['module'])
            if hasattr(module, 'main'):
                result = module.main()
                results.append({
                    'name': test['name'],
                    'success': result
                })
            else:
                print(f"❌ 测试模块 {test['module']} 没有找到main函数")
                results.append({
                    'name': test['name'],
                    'success': False
                })
            
        except Exception as e:
            print(f"❌ 运行测试 {test['name']} 时出错: {str(e)}")
            results.append({
                'name': test['name'],
                'success': False
            })
    
    return results

def run_llm_tests():
    """运行LLM测试（需要调用LLM）"""
    print("🤖 运行LLM测试（需要调用LLM）")
    print("=" * 60)
    
    llm_tests = [
        {
            'module': 'llm_tests.test_integration',
            'name': '完整集成测试（包含LLM）'
        }
    ]
    
    results = []
    
    for test in llm_tests:
        print(f"\n运行: {test['name']}")
        print("-" * 40)
        
        try:
            module = __import__(test['module'])
            if hasattr(module, 'main'):
                result = module.main()
                results.append({
                    'name': test['name'],
                    'success': result
                })
            else:
                print(f"❌ 测试模块 {test['module']} 没有找到main函数")
                results.append({
                    'name': test['name'],
                    'success': False
                })
            
        except Exception as e:
            print(f"❌ 运行测试 {test['name']} 时出错: {str(e)}")
            results.append({
                'name': test['name'],
                'success': False
            })
    
    return results

def show_menu():
    """显示菜单"""
    print("\n" + "="*60)
    print("🧪 分类测试运行器")
    print("="*60)
    print("请选择要运行的测试类别:")
    print("1. 单元测试 (不需要LLM)")
    print("2. 集成测试 (需要后端API，避免LLM)")
    print("3. LLM测试 (需要调用LLM)")
    print("4. 运行所有测试")
    print("5. 交互式测试器")
    print("6. 退出")
    print("-"*60)

def show_test_summary():
    """显示测试分类说明"""
    print("\n📋 测试分类说明")
    print("="*60)
    print("""
🧪 单元测试 (不需要LLM):
   - 语音转文字功能测试
   - 模糊匹配功能测试
   - 交互式测试器
   - 特点: 快速、独立、不依赖外部服务

🔗 集成测试 (需要后端API，避免LLM):
   - 优化的后端API测试
   - 错误处理测试
   - 音频处理测试
   - 特点: 测试API接口，但避免长时间LLM调用

🤖 LLM测试 (需要调用LLM):
   - 完整集成测试
   - 端到端流程测试
   - 特点: 完整功能测试，但需要LLM调用

💡 建议测试顺序:
   1. 先运行单元测试，确保基础功能正常
   2. 再运行集成测试，确保API接口正常
   3. 最后运行LLM测试，验证完整流程
""")

def main():
    """主函数"""
    print("🚀 启动分类测试运行器...")
    
    while True:
        show_menu()
        choice = input("请选择 (1-6): ").strip()
        
        if choice == "1":
            results = run_unit_tests()
            print(f"\n📊 单元测试结果: {sum(1 for r in results if r['success'])}/{len(results)} 成功")
            
        elif choice == "2":
            results = run_integration_tests()
            print(f"\n📊 集成测试结果: {sum(1 for r in results if r['success'])}/{len(results)} 成功")
            
        elif choice == "3":
            confirm = input("⚠️ LLM测试会调用LLM，可能需要较长时间，确认继续？(y/N): ").strip().lower()
            if confirm == 'y':
                results = run_llm_tests()
                print(f"\n📊 LLM测试结果: {sum(1 for r in results if r['success'])}/{len(results)} 成功")
            else:
                print("已取消LLM测试")
                
        elif choice == "4":
            print("🔄 运行所有测试...")
            unit_results = run_unit_tests()
            integration_results = run_integration_tests()
            
            confirm = input("⚠️ 是否运行LLM测试？(y/N): ").strip().lower()
            llm_results = []
            if confirm == 'y':
                llm_results = run_llm_tests()
            
            # 汇总结果
            all_results = unit_results + integration_results + llm_results
            success_count = sum(1 for r in all_results if r['success'])
            print(f"\n📊 总体测试结果: {success_count}/{len(all_results)} 成功")
            
        elif choice == "5":
            try:
                print("🖥️ 启动交互式测试器...")
                from unit.start_fuzzy_matching_test import main as interactive_main
                interactive_main()
            except Exception as e:
                print(f"❌ 交互式测试器启动失败: {e}")
                
        elif choice == "6":
            print("👋 再见!")
            break
            
        else:
            print("❌ 无效选择，请重新输入")
        
        if choice in ["1", "2", "3", "4"]:
            show_test_summary()
        
        input("\n按回车键继续...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 程序出错: {str(e)}")
