"""
Ollama Service Connectivity Tests
Only test if Ollama service is running normally, do not download models
"""
import pytest
import requests
import time
from unittest.mock import patch, Mock

class TestOllamaConnectivity:
    """Ollama service connectivity test class"""

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

    def test_ollama_api_endpoints(self, ollama_base_url):
        """Test Ollama API endpoints"""
        try:
            # Test tags endpoint
            response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                assert 'models' in data
                assert isinstance(data['models'], list)
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama service is not running, skipping API endpoint test")

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

    def test_ollama_service_availability(self, ollama_base_url):
        """Test Ollama service availability"""
        try:
            # Test if service responds
            response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
            assert response.status_code == 200
            
            # Test response time
            start_time = time.time()
            response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response_time < 5.0, f"Response time too long: {response_time:.2f} seconds"
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama service is not running, skipping availability test")

    def test_ollama_service_configuration(self, ollama_base_url):
        """Test Ollama service configuration"""
        try:
            response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                # Check response headers
                assert 'application/json' in response.headers.get('content-type', '')
                
                # Check response content
                data = response.json()
                assert isinstance(data, dict)
                assert 'models' in data
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama service is not running, skipping configuration test")
