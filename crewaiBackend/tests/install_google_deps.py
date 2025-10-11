#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google API依赖安装脚本
自动安装所需的Google API相关依赖包
"""

import subprocess
import sys
import os

def install_package(package):
    """安装Python包"""
    try:
        print(f"📦 正在安装 {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package} 安装失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 Google API 依赖安装工具")
    print("=" * 50)
    
    # 需要安装的包
    packages = [
        "langchain-google-genai==1.0.0",
        "google-generativeai==0.3.2",
        "requests==2.31.0"
    ]
    
    print("📋 需要安装的包:")
    for package in packages:
        print(f"  - {package}")
    print()
    
    # 安装包
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
        print()
    
    print("=" * 50)
    print(f"📊 安装结果: {success_count}/{len(packages)} 个包安装成功")
    
    if success_count == len(packages):
        print("🎉 所有依赖安装完成！")
        print("💡 现在可以运行: python test_google_api.py")
    else:
        print("❌ 部分依赖安装失败，请手动安装")
        print("💡 手动安装命令:")
        for package in packages:
            print(f"   pip install {package}")

if __name__ == "__main__":
    main()
