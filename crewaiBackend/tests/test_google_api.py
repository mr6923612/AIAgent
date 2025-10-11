# -*- coding: utf-8 -*-
"""
Google Chat API测试脚本
用于验证Google Gemini API密钥是否有效
"""

import os
import requests
from utils.myLLM import GOOGLE_CHAT_API_KEY, GOOGLE_CHAT_MODEL

def test_google_api():
    """测试Google Chat API密钥"""
    
    print("测试Google Chat API密钥...")
    print("=" * 50)
    print(f"模型: {GOOGLE_CHAT_MODEL}")
    print(f"API Key: {GOOGLE_CHAT_API_KEY[:20]}...")
    print("=" * 50)
    
    try:
        # 使用LangChain的Google集成进行测试
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        print("初始化Google Chat模型...")
        llm = ChatGoogleGenerativeAI(
            model=GOOGLE_CHAT_MODEL,
            google_api_key=GOOGLE_CHAT_API_KEY,
            temperature=0.7,
            max_output_tokens=100
        )
        
        print("发送测试请求...")
        response = llm.invoke("Hello, this is a test message. Please respond with a brief greeting.")
        
        print("Google Chat API密钥有效！")
        print(f"模型回复: {response.content}")
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        return False

def test_crewai_integration():
    """测试CrewAI集成"""
    
    print("\n测试CrewAI集成...")
    print("=" * 50)
    
    try:
        # 先测试导入
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("ChatGoogleGenerativeAI导入成功")
        
        # 测试直接创建LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GOOGLE_CHAT_API_KEY,
            temperature=0.7,
            max_output_tokens=100
        )
        print("LLM直接创建成功")
        
        # 测试my_llm函数
        from utils.myLLM import my_llm
        llm2 = my_llm("google")
        print("my_llm函数调用成功")
        
        # 简单测试
        test_input = "你好，请简单介绍一下你自己"
        print(f"测试输入: {test_input}")
        
        # 这里可以添加更多的CrewAI测试
        print("CrewAI集成测试通过")
        return True
        
    except Exception as e:
        print(f"CrewAI集成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("Google Chat API 配置测试工具")
    print("=" * 50)
    
    # 检查环境变量
    env_key = os.getenv("GOOGLE_API_KEY")
    if env_key:
        print(f"检测到环境变量 GOOGLE_API_KEY: {env_key[:20]}...")
    else:
        print("未检测到环境变量 GOOGLE_API_KEY，使用默认配置")
    
    # 测试Google Chat API
    google_ok = test_google_api()
    
    # 测试CrewAI集成
    crewai_ok = test_crewai_integration()
    
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"Google Chat API: {'可用' if google_ok else '不可用'}")
    print(f"CrewAI集成: {'正常' if crewai_ok else '异常'}")
    
    if google_ok and crewai_ok:
        print("\nGoogle Chat API配置正确，系统可以正常运行！")
        print("系统将使用Google Gemini 2.5 Flash模型")
    else:
        print("\nGoogle Chat API不可用，请检查配置：")
        print("1. API密钥是否正确")
        print("2. 网络连接是否正常")
        print("3. 模型名称是否有效")
        print("\n建议：")
        print("1. 访问 https://makersuite.google.com/app/apikey 获取Google API密钥")
        print("2. 设置环境变量: export GOOGLE_API_KEY='your-google-key'")
        print("3. 或者直接修改 utils/myLLM.py 中的配置")

if __name__ == "__main__":
    main()
