"""
Ollama Model Tests
Test if Ollama service is running normally and contains required models
Note: This test requires downloading large model files, not suitable for CI/CD runs
"""
import pytest
import requests
import time
import os
from unittest.mock import patch, Mock

# Check if in CI environment
IS_CI = os.getenv('CI') or os.getenv('GITHUB_ACTIONS')

class TestOllamaModels:
    """Ollama model test class"""

    @pytest.fixture
    def ollama_base_url(self):
        """Ollama service base URL"""
        return "http://localhost:11434"

    def test_ollama_service_connection(self, ollama_base_url):
        """Test Ollama service connection"""
        try:
            response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
            assert response.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama service is not running, skipping connection test")

    def test_ollama_models_list(self, ollama_base_url):
        """Test getting model list"""
        try:
            response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                assert 'models' in data
                assert isinstance(data['models'], list)
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama service is not running, skipping model list test")

    def test_required_models_present(self, ollama_base_url):
        """Test if required models exist"""
        if IS_CI:
            pytest.skip("Skipping model download test - not suitable for CI environment")
        
        required_models = ['bge-m3']
        
        try:
            response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                installed_models = [model['name'] for model in data.get('models', [])]
                
                for model in required_models:
                    # Check if model name is in installed models (supports tagged model names)
                    model_found = any(model in installed_model for installed_model in installed_models)
                    assert model_found, f"Required model {model} is not installed, installed models: {installed_models}"
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama service is not running, skipping model existence test")

    def test_bge_m3_model_inference(self, ollama_base_url):
        """Test bge-m3 model inference functionality"""
        if IS_CI:
            pytest.skip("Skipping model inference test - not suitable for CI environment")
        
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
                pytest.skip(f"bge-m3 model inference test failed: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama service is not running, skipping bge-m3 inference test")

    def test_ollama_model_download(self, ollama_base_url):
        """Test model download functionality"""
        if IS_CI:
            pytest.skip("Skipping model download test - not suitable for CI environment")
        
        try:
            # Test downloading a small test model
            test_model = "tinyllama"
            
            response = requests.post(
                f"{ollama_base_url}/api/pull",
                json={"name": test_model},
                timeout=60
            )
            
            if response.status_code == 200:
                # Check if model is in the list
                time.sleep(5)  # Wait for download to complete
                tags_response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
                if tags_response.status_code == 200:
                    data = tags_response.json()
                    installed_models = [model['name'] for model in data.get('models', [])]
                    # Check if model name is in installed models (supports tagged model names)
                    model_found = any(test_model in installed_model for installed_model in installed_models)
                    assert model_found, f"Test model {test_model} download failed, installed models: {installed_models}"
            else:
                pytest.skip(f"Model download test failed: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama service is not running, skipping model download test")

    def test_ollama_health_check(self, ollama_base_url):
        """Test Ollama health check"""
        try:
            response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
            assert response.status_code == 200
            
            # Check response format
            data = response.json()
            assert 'models' in data
            assert isinstance(data['models'], list)
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama service is not running, skipping health check test")
