#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令行交互式模糊匹配测试模块
允许用户输入文字和图片，实时测试匹配效果并调整参数
"""

import os
import sys
import base64
import json

# 添加后端路径
sys.path.append('../crewaiBackend')

from utils.rag_retriever import MultimodalRAGRetriever

class FuzzyMatchingCLI:
    """命令行交互式模糊匹配测试器"""
    
    def __init__(self):
        self.rag_retriever = MultimodalRAGRetriever()
        self.current_params = {
            'relevance_threshold': 0.1,
            'image_similarity_threshold': 0.7,
            'inquiry_threshold': 0.9,
            'max_results': 5,
            'route_decision': 'PRODUCT_QUERY'
        }
        self.test_history = []
    
    def show_menu(self):
        """显示主菜单"""
        print("\n" + "="*60)
        print("🔍 模糊匹配参数测试器")
        print("="*60)
        print("1. 设置参数")
        print("2. 文字查询测试")
        print("3. 图片查询测试")
        print("4. 组合查询测试")
        print("5. 查看当前参数")
        print("6. 参数预设")
        print("7. 查看测试历史")
        print("8. 保存测试结果")
        print("9. 退出")
        print("-"*60)
    
    def show_current_params(self):
        """显示当前参数"""
        print("\n📋 当前参数设置:")
        print(f"  文字匹配阈值: {self.current_params['relevance_threshold']:.2f}")
        print(f"  图片相似度阈值: {self.current_params['image_similarity_threshold']:.2f}")
        print(f"  询问确认阈值: {self.current_params['inquiry_threshold']:.2f}")
        print(f"  最大结果数: {self.current_params['max_results']}")
        print(f"  搜索策略: {self.current_params['route_decision']}")
    
    def set_parameters(self):
        """设置参数"""
        print("\n⚙️ 参数设置")
        print("-"*30)
        
        # 文字匹配阈值
        while True:
            try:
                value = input(f"文字匹配阈值 (当前: {self.current_params['relevance_threshold']:.2f}, 0.0-1.0): ").strip()
                if not value:
                    break
                value = float(value)
                if 0.0 <= value <= 1.0:
                    self.current_params['relevance_threshold'] = value
                    break
                else:
                    print("请输入0.0到1.0之间的数值")
            except ValueError:
                print("请输入有效的数值")
        
        # 图片相似度阈值
        while True:
            try:
                value = input(f"图片相似度阈值 (当前: {self.current_params['image_similarity_threshold']:.2f}, 0.0-1.0): ").strip()
                if not value:
                    break
                value = float(value)
                if 0.0 <= value <= 1.0:
                    self.current_params['image_similarity_threshold'] = value
                    break
                else:
                    print("请输入0.0到1.0之间的数值")
            except ValueError:
                print("请输入有效的数值")
        
        # 询问确认阈值
        while True:
            try:
                value = input(f"询问确认阈值 (当前: {self.current_params['inquiry_threshold']:.2f}, 0.0-1.0): ").strip()
                if not value:
                    break
                value = float(value)
                if 0.0 <= value <= 1.0:
                    self.current_params['inquiry_threshold'] = value
                    break
                else:
                    print("请输入0.0到1.0之间的数值")
            except ValueError:
                print("请输入有效的数值")
        
        # 最大结果数
        while True:
            try:
                value = input(f"最大结果数 (当前: {self.current_params['max_results']}, 1-20): ").strip()
                if not value:
                    break
                value = int(value)
                if 1 <= value <= 20:
                    self.current_params['max_results'] = value
                    break
                else:
                    print("请输入1到20之间的整数")
            except ValueError:
                print("请输入有效的整数")
        
        # 搜索策略
        print(f"搜索策略 (当前: {self.current_params['route_decision']}):")
        print("1. PRODUCT_QUERY (产品查询)")
        print("2. GENERAL_SERVICE (通用客服)")
        choice = input("选择 (1-2, 回车跳过): ").strip()
        if choice == "1":
            self.current_params['route_decision'] = 'PRODUCT_QUERY'
        elif choice == "2":
            self.current_params['route_decision'] = 'GENERAL_SERVICE'
        
        print("✅ 参数设置完成")
        self.show_current_params()
    
    def text_query_test(self):
        """文字查询测试"""
        print("\n📝 文字查询测试")
        print("-"*30)
        
        query = input("请输入查询文字: ").strip()
        if not query:
            print("❌ 查询文字不能为空")
            return
        
        print(f"\n🔍 正在搜索: {query}")
        print("⏳ 请稍候...")
        
        try:
            results = self.rag_retriever.search(
                query=query,
                max_results=self.current_params['max_results'],
                route_decision=self.current_params['route_decision']
            )
            
            self.display_results(results, query=query)
            
            # 保存到历史
            self.test_history.append({
                'type': 'text',
                'query': query,
                'params': self.current_params.copy(),
                'results': results,
                'timestamp': self.get_timestamp()
            })
            
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
    
    def image_query_test(self):
        """图片查询测试"""
        print("\n🖼️ 图片查询测试")
        print("-"*30)
        
        image_path = input("请输入图片文件路径: ").strip()
        if not image_path:
            print("❌ 图片路径不能为空")
            return
        
        if not os.path.exists(image_path):
            print(f"❌ 图片文件不存在: {image_path}")
            return
        
        try:
            # 读取图片并转换为Base64
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            print(f"\n🔍 正在分析图片: {os.path.basename(image_path)}")
            print(f"📊 图片大小: {len(image_data)} bytes (Base64)")
            print("⏳ 请稍候...")
            
            results = self.rag_retriever.search(
                query="",
                max_results=self.current_params['max_results'],
                input_image_data=image_data,
                route_decision=self.current_params['route_decision']
            )
            
            self.display_results(results, image_path=image_path)
            
            # 保存到历史
            self.test_history.append({
                'type': 'image',
                'image_path': image_path,
                'params': self.current_params.copy(),
                'results': results,
                'timestamp': self.get_timestamp()
            })
            
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
    
    def combined_query_test(self):
        """组合查询测试"""
        print("\n🔗 组合查询测试 (文字+图片)")
        print("-"*30)
        
        query = input("请输入查询文字 (可选): ").strip()
        image_path = input("请输入图片文件路径 (可选): ").strip()
        
        if not query and not image_path:
            print("❌ 至少需要输入文字或图片")
            return
        
        if image_path and not os.path.exists(image_path):
            print(f"❌ 图片文件不存在: {image_path}")
            return
        
        try:
            image_data = None
            if image_path:
                with open(image_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
            
            print(f"\n🔍 正在搜索...")
            if query:
                print(f"  文字: {query}")
            if image_path:
                print(f"  图片: {os.path.basename(image_path)}")
            print("⏳ 请稍候...")
            
            results = self.rag_retriever.search(
                query=query,
                max_results=self.current_params['max_results'],
                input_image_data=image_data,
                route_decision=self.current_params['route_decision']
            )
            
            self.display_results(results, query=query, image_path=image_path)
            
            # 保存到历史
            self.test_history.append({
                'type': 'combined',
                'query': query,
                'image_path': image_path,
                'params': self.current_params.copy(),
                'results': results,
                'timestamp': self.get_timestamp()
            })
            
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
    
    def display_results(self, results, query=None, image_path=None):
        """显示测试结果"""
        print("\n" + "="*60)
        print("📊 测试结果")
        print("="*60)
        
        # 显示当前参数
        print("⚙️ 当前参数:")
        print(f"  文字匹配阈值: {self.current_params['relevance_threshold']:.2f}")
        print(f"  图片相似度阈值: {self.current_params['image_similarity_threshold']:.2f}")
        print(f"  询问确认阈值: {self.current_params['inquiry_threshold']:.2f}")
        print(f"  最大结果数: {self.current_params['max_results']}")
        print(f"  搜索策略: {self.current_params['route_decision']}")
        
        # 显示输入信息
        print("\n📥 输入信息:")
        if query:
            print(f"  文字查询: {query}")
        if image_path:
            print(f"  图片文件: {os.path.basename(image_path)}")
        
        # 显示匹配结果
        print(f"\n🎯 匹配结果:")
        if results:
            print(f"找到 {len(results)} 个匹配结果:\n")
            
            for i, result in enumerate(results, 1):
                print(f"结果 {i}:")
                print(f"  类型: {result.get('type', 'unknown')}")
                print(f"  相关性/相似度: {result.get('relevance', 0):.3f}")
                print(f"  来源: {result.get('source', 'unknown')}")
                print(f"  章节: {result.get('section', 'unknown')}")
                
                content = result.get('content', '')
                if len(content) > 150:
                    content = content[:150] + "..."
                print(f"  内容: {content}")
                
                if 'product_info' in result:
                    product_info = result['product_info']
                    print(f"  产品名称: {product_info.get('name', 'unknown')}")
                
                print()
        else:
            print("❌ 未找到匹配结果")
        
        # 显示参数建议
        print("💡 参数调整建议:")
        if results:
            best_relevance = results[0].get('relevance', 0)
            if best_relevance < 0.3:
                print("  - 建议降低文字匹配阈值以获得更多结果")
            elif best_relevance > 0.8:
                print("  - 当前匹配效果良好")
            
            if len(results) < 3:
                print("  - 建议增加最大结果数或降低阈值")
        else:
            print("  - 建议降低匹配阈值或检查输入内容")
    
    def parameter_presets(self):
        """参数预设"""
        print("\n🎛️ 参数预设")
        print("-"*30)
        print("1. 严格模式 (高精度，少结果)")
        print("2. 宽松模式 (低精度，多结果)")
        print("3. 默认模式 (平衡)")
        print("4. 自定义模式")
        
        choice = input("请选择预设 (1-4): ").strip()
        
        if choice == "1":
            self.current_params = {
                'relevance_threshold': 0.3,
                'image_similarity_threshold': 0.8,
                'inquiry_threshold': 0.8,
                'max_results': 3,
                'route_decision': 'PRODUCT_QUERY'
            }
            print("✅ 已设置为严格模式")
        elif choice == "2":
            self.current_params = {
                'relevance_threshold': 0.05,
                'image_similarity_threshold': 0.5,
                'inquiry_threshold': 0.95,
                'max_results': 10,
                'route_decision': 'PRODUCT_QUERY'
            }
            print("✅ 已设置为宽松模式")
        elif choice == "3":
            self.current_params = {
                'relevance_threshold': 0.1,
                'image_similarity_threshold': 0.7,
                'inquiry_threshold': 0.9,
                'max_results': 5,
                'route_decision': 'PRODUCT_QUERY'
            }
            print("✅ 已设置为默认模式")
        elif choice == "4":
            self.set_parameters()
            return
        else:
            print("❌ 无效选择")
            return
        
        self.show_current_params()
    
    def show_test_history(self):
        """显示测试历史"""
        print("\n📚 测试历史")
        print("-"*30)
        
        if not self.test_history:
            print("暂无测试历史")
            return
        
        for i, test in enumerate(self.test_history, 1):
            print(f"\n测试 {i} ({test['timestamp']}):")
            print(f"  类型: {test['type']}")
            if 'query' in test and test['query']:
                print(f"  文字: {test['query']}")
            if 'image_path' in test and test['image_path']:
                print(f"  图片: {os.path.basename(test['image_path'])}")
            print(f"  结果数: {len(test['results'])}")
            if test['results']:
                best_relevance = test['results'][0].get('relevance', 0)
                print(f"  最佳相关性: {best_relevance:.3f}")
    
    def save_test_results(self):
        """保存测试结果"""
        if not self.test_history:
            print("❌ 没有测试历史可保存")
            return
        
        filename = input("请输入保存文件名 (默认: fuzzy_matching_results.json): ").strip()
        if not filename:
            filename = "fuzzy_matching_results.json"
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_history, f, ensure_ascii=False, indent=2)
            print(f"✅ 测试结果已保存到: {filename}")
        except Exception as e:
            print(f"❌ 保存失败: {str(e)}")
    
    def get_timestamp(self):
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def run(self):
        """运行主程序"""
        print("🚀 启动模糊匹配参数测试器...")
        
        while True:
            self.show_menu()
            choice = input("请选择操作 (1-9): ").strip()
            
            if choice == "1":
                self.set_parameters()
            elif choice == "2":
                self.text_query_test()
            elif choice == "3":
                self.image_query_test()
            elif choice == "4":
                self.combined_query_test()
            elif choice == "5":
                self.show_current_params()
            elif choice == "6":
                self.parameter_presets()
            elif choice == "7":
                self.show_test_history()
            elif choice == "8":
                self.save_test_results()
            elif choice == "9":
                print("👋 再见!")
                break
            else:
                print("❌ 无效选择，请重新输入")
            
            input("\n按回车键继续...")

def main():
    """主函数"""
    try:
        app = FuzzyMatchingCLI()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 程序出错: {str(e)}")

if __name__ == "__main__":
    main()
