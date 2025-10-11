#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模糊匹配测试器启动脚本
提供GUI和CLI两种测试方式
"""

import sys
import os

def check_dependencies():
    """检查依赖"""
    print("🔍 检查依赖...")
    
    # 检查后端模块
    try:
        sys.path.append('../crewaiBackend')
        from utils.rag_retriever import MultimodalRAGRetriever
        print("✅ 后端模块检查通过")
    except ImportError as e:
        print(f"❌ 后端模块导入失败: {e}")
        return False
    
    # 检查GUI依赖
    try:
        import tkinter
        print("✅ GUI依赖检查通过")
        gui_available = True
    except ImportError:
        print("⚠️ GUI依赖不可用，将使用命令行模式")
        gui_available = False
    
    # 检查图片处理依赖
    try:
        from PIL import Image
        print("✅ 图片处理依赖检查通过")
    except ImportError:
        print("⚠️ 图片处理依赖不可用，图片测试功能可能受限")
    
    return gui_available

def show_menu():
    """显示启动菜单"""
    print("\n" + "="*60)
    print("🔍 模糊匹配测试器")
    print("="*60)
    print("请选择测试方式:")
    print("1. 图形界面测试器 (推荐)")
    print("2. 命令行测试器")
    print("3. 查看帮助")
    print("4. 退出")
    print("-"*60)

def show_help():
    """显示帮助信息"""
    print("\n📖 帮助信息")
    print("="*60)
    print("""
🔍 模糊匹配测试器功能:

1. 图形界面测试器:
   - 直观的参数调节界面
   - 实时图片预览
   - 拖拽式操作
   - 适合交互式测试

2. 命令行测试器:
   - 纯文本界面
   - 支持脚本化测试
   - 适合批量测试
   - 支持测试历史保存

📋 测试功能:
- 文字查询模糊匹配
- 图片相似度匹配
- 参数实时调整
- 测试结果分析
- 参数优化建议

⚙️ 可调节参数:
- 文字匹配阈值 (0.0-1.0)
- 图片相似度阈值 (0.0-1.0)
- 询问确认阈值 (0.0-1.0)
- 最大结果数 (1-20)
- 搜索策略 (产品查询/通用客服)

📁 测试数据:
- 文字查询: 支持中文和英文
- 图片文件: 支持 PNG, JPG, JPEG, GIF, BMP
- 测试结果: 可保存为JSON格式

🚀 快速开始:
1. 选择测试方式
2. 设置参数 (或使用预设)
3. 输入测试内容
4. 查看匹配结果
5. 调整参数优化效果
""")

def main():
    """主函数"""
    print("🚀 启动模糊匹配测试器...")
    
    # 检查依赖
    gui_available = check_dependencies()
    
    while True:
        show_menu()
        choice = input("请选择 (1-4): ").strip()
        
        if choice == "1":
            if gui_available:
                try:
                    print("🖥️ 启动图形界面测试器...")
                    from test_fuzzy_matching_interactive import main as gui_main
                    gui_main()
                except Exception as e:
                    print(f"❌ 图形界面启动失败: {e}")
                    print("🔄 切换到命令行模式...")
                    from test_fuzzy_matching_cli import main as cli_main
                    cli_main()
            else:
                print("❌ 图形界面不可用，请选择命令行模式")
        elif choice == "2":
            try:
                print("💻 启动命令行测试器...")
                from test_fuzzy_matching_cli import main as cli_main
                cli_main()
            except Exception as e:
                print(f"❌ 命令行测试器启动失败: {e}")
        elif choice == "3":
            show_help()
        elif choice == "4":
            print("👋 再见!")
            break
        else:
            print("❌ 无效选择，请重新输入")
        
        if choice in ["1", "2"]:
            break  # 测试器运行完成后退出启动脚本

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 程序出错: {str(e)}")
