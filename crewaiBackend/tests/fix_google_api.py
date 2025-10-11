#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google API快速修复脚本
解决API密钥和配置问题
"""

import os
import sys

def check_api_key():
    """检查API密钥配置"""
    print("🔍 检查API密钥配置...")
    
    # 检查环境变量
    env_key = os.getenv("GOOGLE_API_KEY")
    if env_key:
        print(f"✅ 环境变量 GOOGLE_API_KEY: {env_key[:20]}...")
        return env_key
    else:
        print("❌ 未找到环境变量 GOOGLE_API_KEY")
        return None

def update_config_file():
    """更新配置文件"""
    print("🔧 更新配置文件...")
    
    config_file = "utils/myLLM.py"
    if not os.path.exists(config_file):
        print(f"❌ 配置文件不存在: {config_file}")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经使用正确的Google API配置
        if "ChatGoogleGenerativeAI" in content:
            print("✅ 配置文件已使用正确的Google API配置")
            return True
        else:
            print("❌ 配置文件需要更新")
            return False
            
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return False

def test_import():
    """测试导入"""
    print("🧪 测试导入...")
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("✅ langchain_google_genai 导入成功")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("💡 请运行: pip install langchain-google-genai")
        return False

def main():
    """主函数"""
    print("🚀 Google API 快速修复工具")
    print("=" * 50)
    
    # 检查API密钥
    api_key = check_api_key()
    if not api_key:
        print("\n💡 解决方案:")
        print("1. 获取Google API密钥: https://makersuite.google.com/app/apikey")
        print("2. 设置环境变量:")
        print("   Windows: set GOOGLE_API_KEY=your-key")
        print("   Linux/Mac: export GOOGLE_API_KEY=your-key")
        return
    
    # 检查配置文件
    config_ok = update_config_file()
    if not config_ok:
        print("❌ 配置文件需要手动更新")
        return
    
    # 测试导入
    import_ok = test_import()
    if not import_ok:
        print("❌ 依赖包未安装")
        return
    
    print("\n🎉 所有检查通过！")
    print("💡 现在可以运行:")
    print("   python test_google_api.py")
    print("   python main.py")

if __name__ == "__main__":
    main()
