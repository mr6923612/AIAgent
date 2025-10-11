#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目状态检查脚本
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("Python版本检查:")
    version = sys.version_info
    print(f"  当前版本: Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 10:
        print("  [OK] Python版本符合要求 (3.10+)")
        return True
    else:
        print("  [ERROR] Python版本不符合要求，需要3.10+")
        return False

def check_dependencies():
    """检查依赖包"""
    print("\n依赖包检查:")
    required_packages = [
        "flask", "flask-cors", "crewai", "pydantic", 
        "Pillow", "langchain", "python-docx"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  [OK] {package}")
        except ImportError:
            print(f"  [ERROR] {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n  缺少依赖包: {', '.join(missing_packages)}")
        print("  请运行: pip install -r requirements.txt")
        return False
    else:
        print("  [OK] 所有依赖包已安装")
        return True

def check_project_structure():
    """检查项目结构"""
    print("\n项目结构检查:")
    
    required_files = [
        "main.py",
        "crew.py", 
        "requirements.txt",
        "utils/jobManager.py",
        "utils/myLLM.py",
        "utils/rag_retriever.py",
        "utils/word_processor.py"
    ]
    
    required_dirs = [
        "utils",
        "scripts", 
        "tests",
        "docs",
        "rag_documents",
        "rag_documents/images"
    ]
    
    missing_items = []
    
    # 检查文件
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  [OK] {file_path}")
        else:
            print(f"  [ERROR] {file_path} - 文件不存在")
            missing_items.append(file_path)
    
    # 检查目录
    for dir_path in required_dirs:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            print(f"  [OK] {dir_path}/")
        else:
            print(f"  [ERROR] {dir_path}/ - 目录不存在")
            missing_items.append(dir_path)
    
    if missing_items:
        print(f"\n  缺少项目文件/目录: {', '.join(missing_items)}")
        return False
    else:
        print("  [OK] 项目结构完整")
        return True

def check_rag_documents():
    """检查RAG文档状态"""
    print("\nRAG文档检查:")
    
    rag_docs_path = "rag_documents"
    if not os.path.exists(rag_docs_path):
        print("  [ERROR] rag_documents目录不存在")
        return False
    
    # 检查Word文档
    word_files = []
    for file in os.listdir(rag_docs_path):
        if file.lower().endswith(('.docx', '.doc')):
            word_files.append(file)
    
    print(f"  Word文档: {len(word_files)} 个")
    for file in word_files:
        print(f"    - {file}")
    
    # 检查处理后的内容
    content_files = []
    for file in os.listdir(rag_docs_path):
        if file.endswith('_content.json'):
            content_files.append(file)
    
    print(f"  处理后的内容: {len(content_files)} 个")
    for file in content_files:
        print(f"    - {file}")
    
    # 检查图片
    images_dir = os.path.join(rag_docs_path, "images")
    if os.path.exists(images_dir):
        image_files = [f for f in os.listdir(images_dir) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        print(f"  提取的图片: {len(image_files)} 张")
        for file in image_files[:5]:  # 只显示前5个
            print(f"    - {file}")
        if len(image_files) > 5:
            print(f"    ... 还有 {len(image_files) - 5} 张图片")
    else:
        print("  提取的图片: 0 张")
    
    return True

def check_configuration():
    """检查配置"""
    print("\n配置检查:")
    
    # 检查环境变量
    env_vars = ["SERPER_API_KEY", "GOOGLE_API_KEY"]
    for var in env_vars:
        if os.getenv(var):
            print(f"  [OK] {var} - 已设置")
        else:
            print(f"  [WARN] {var} - 未设置 (可选)")
    
    # 检查API配置
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()
            if "PORT = 8012" in content:
                print("  [OK] 服务器端口配置正确 (8012)")
            else:
                print("  [WARN] 服务器端口配置可能有问题")
    except Exception as e:
        print(f"  [ERROR] 无法读取main.py配置: {str(e)}")
    
    return True

def check_network():
    """检查网络连接"""
    print("\n网络连接检查:")
    
    # 检查本地端口
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8012))
        sock.close()
        
        if result == 0:
            print("  [WARN] 端口8012已被占用，服务器可能已在运行")
        else:
            print("  [OK] 端口8012可用")
    except Exception as e:
        print(f"  [ERROR] 网络检查失败: {str(e)}")
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("CrewAI Backend 项目状态检查")
    print("=" * 60)
    
    checks = [
        ("Python版本", check_python_version),
        ("依赖包", check_dependencies),
        ("项目结构", check_project_structure),
        ("RAG文档", check_rag_documents),
        ("配置", check_configuration),
        ("网络连接", check_network)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  [ERROR] {name}检查失败: {str(e)}")
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("检查结果总结:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "[OK] 通过" if result else "[ERROR] 失败"
        print(f"  {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体状态: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("[SUCCESS] 项目状态良好，可以正常运行！")
    else:
        print("[WARN] 项目存在问题，请根据上述检查结果进行修复")
    
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
    except Exception as e:
        print(f"\n\n发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
