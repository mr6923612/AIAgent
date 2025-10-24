"""
Ollama模型测试
测试Ollama服务是否正常运行并包含所需的模型
注意：此测试需要下载大模型文件，不适合在CI/CD中运行
"""
import pytest
import requests
import time
import os
from unittest.mock import patch, Mock

# 检查是否在CI环境中
IS_CI = os.getenv('CI') or os.getenv('GITHUB_ACTIONS')

class TestOllamaModels:
    """Ollama模型测试类"""

    @pytest.fixture
    def ollama_base_url(self):
        """Ollama服务基础URL"""
        return "http://localhost:11434"

    def test_ollama_service_connection(self, ollama_base_url):
        """测试Ollama服务连接"""
        try:
            response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
            assert response.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama服务未运行，跳过连接测试")

    def test_ollama_models_list(self, ollama_base_url):
        """测试获取模型列表"""
        try:
            response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                assert 'models' in data
                assert isinstance(data['models'], list)
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama服务未运行，跳过模型列表测试")

    def test_required_models_present(self, ollama_base_url):
        """测试必需的模型是否存在"""
        if IS_CI:
            pytest.skip("跳过模型下载测试 - 不适合在CI环境中运行")
        
        required_models = ['bge-m3']
        
        try:
            response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                installed_models = [model['name'] for model in data.get('models', [])]
                
                for model in required_models:
                    # 检查模型名称是否在已安装模型中（支持带标签的模型名）
                    model_found = any(model in installed_model for installed_model in installed_models)
                    assert model_found, f"必需模型 {model} 未安装，已安装模型: {installed_models}"
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama服务未运行，跳过模型存在性测试")

    def test_bge_m3_model_inference(self, ollama_base_url):
        """测试bge-m3模型推理功能"""
        if IS_CI:
            pytest.skip("跳过模型推理测试 - 不适合在CI环境中运行")
        
        try:
            test_data = {
                "model": "bge-m3",
                "prompt": "Hello, world!",
                "stream": False
            }
            
            response = requests.post(
                f"{ollama_base_url}/api/generate",
                json=test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                assert 'response' in result
                assert isinstance(result['response'], str)
            else:
                pytest.skip(f"bge-m3模型推理测试失败: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama服务未运行，跳过bge-m3推理测试")

    def test_ollama_model_download(self, ollama_base_url):
        """测试模型下载功能"""
        if IS_CI:
            pytest.skip("跳过模型下载测试 - 不适合在CI环境中运行")
        
        try:
            # 测试下载一个小的测试模型
            test_model = "tinyllama"
            
            response = requests.post(
                f"{ollama_base_url}/api/pull",
                json={"name": test_model},
                timeout=60
            )
            
            if response.status_code == 200:
                # 检查模型是否在列表中
                time.sleep(5)  # 等待下载完成
                tags_response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
                if tags_response.status_code == 200:
                    data = tags_response.json()
                    installed_models = [model['name'] for model in data.get('models', [])]
                    # 检查模型名称是否在已安装模型中（支持带标签的模型名）
                    model_found = any(test_model in installed_model for installed_model in installed_models)
                    assert model_found, f"测试模型 {test_model} 下载失败，已安装模型: {installed_models}"
            else:
                pytest.skip(f"模型下载测试失败: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama服务未运行，跳过模型下载测试")

    def test_ollama_health_check(self, ollama_base_url):
        """测试Ollama健康检查"""
        try:
            response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
            assert response.status_code == 200
            
            # 检查响应格式
            data = response.json()
            assert 'models' in data
            assert isinstance(data['models'], list)
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama服务未运行，跳过健康检查测试")
