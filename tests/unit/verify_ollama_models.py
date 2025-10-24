#!/usr/bin/env python3
"""
Ollama模型验证脚本
验证Ollama服务是否正常运行并包含所需的模型
"""

import requests
import json
import time
import sys

def check_ollama_service():
    """检查Ollama服务是否运行"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Ollama服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Ollama服务 (http://localhost:11434)")
        return False
    except Exception as e:
        print(f"❌ 检查Ollama服务时出错: {str(e)}")
        return False

def get_installed_models():
    """获取已安装的模型列表"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            return models
        else:
            print(f"❌ 获取模型列表失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 获取模型列表时出错: {str(e)}")
        return []

def verify_required_models():
    """验证必需的模型是否已安装"""
    required_models = ['bge-m3', 'llama3.2:3b']
    
    print("Checking Ollama service status...")
    if not check_ollama_service():
        print("Ollama service is not running, please check service status")
        return False
    
    print("Getting installed models list...")
    installed_models = get_installed_models()
    
    if not installed_models:
        print("No installed models found")
        return False
    
    print(f"Installed models: {', '.join(installed_models)}")
    
    missing_models = []
    for model in required_models:
        if model not in installed_models:
            missing_models.append(model)
    
    if missing_models:
        print(f"Missing required models: {', '.join(missing_models)}")
        return False
    
    print("All required models are installed")
    return True

def test_model_inference():
    """测试模型推理功能"""
    print("Testing model inference...")
    
    try:
        # 测试bge-m3模型
        test_data = {
            "model": "bge-m3",
            "prompt": "Hello, world!",
            "stream": False
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("bge-m3 model inference test successful")
            return True
        else:
            print(f"Model inference test failed: {response.status_code}")
            return False
                
    except Exception as e:
        print(f"Error during model inference test: {str(e)}")
        return False

def main():
    """主函数"""
    print("Starting Ollama model verification...")
    print("=" * 50)
    
    # 等待服务启动
    print("Waiting for Ollama service to start...")
    time.sleep(5)
    
    # 验证模型
    if not verify_required_models():
        print("Model verification failed")
        sys.exit(1)
    
    # 测试推理
    if not test_model_inference():
        print("Model inference test failed")
        sys.exit(1)
    
    print("=" * 50)
    print("All verifications passed! Ollama model configuration is correct")
    sys.exit(0)

if __name__ == "__main__":
    main()
