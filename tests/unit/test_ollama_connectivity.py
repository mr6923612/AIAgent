"""
Ollama服务连通性测试
只测试Ollama服务是否正常运行，不下载模型
"""
import pytest
import requests
import time
from unittest.mock import patch, Mock

class TestOllamaConnectivity:
    """Ollama服务连通性测试类"""

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

    def test_ollama_api_endpoints(self, ollama_base_url):
        """测试Ollama API端点"""
        try:
            # 测试tags端点
            response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                assert 'models' in data
                assert isinstance(data['models'], list)
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama服务未运行，跳过API端点测试")

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

    def test_ollama_service_availability(self, ollama_base_url):
        """测试Ollama服务可用性"""
        try:
            # 测试服务是否响应
            response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
            assert response.status_code == 200
            
            # 测试响应时间
            start_time = time.time()
            response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response_time < 5.0, f"响应时间过长: {response_time:.2f}秒"
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama服务未运行，跳过可用性测试")

    def test_ollama_service_configuration(self, ollama_base_url):
        """测试Ollama服务配置"""
        try:
            response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                # 检查响应头
                assert 'application/json' in response.headers.get('content-type', '')
                
                # 检查响应内容
                data = response.json()
                assert isinstance(data, dict)
                assert 'models' in data
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama服务未运行，跳过配置测试")
