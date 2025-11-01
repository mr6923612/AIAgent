"""
Configuration Module Unit Tests
"""
import pytest
import os
from unittest.mock import patch
from crewaiBackend.config import config


class TestConfig:
    """Configuration test class"""
    
    def test_config_loading(self):
        """Test configuration loading"""
        assert config.GOOGLE_API_KEY is not None
        assert config.RAGFLOW_BASE_URL is not None
        assert config.MYSQL_HOST is not None
        assert config.MYSQL_PORT is not None
        assert config.MYSQL_DATABASE is not None
    
    def test_config_defaults(self):
        """Test configuration defaults"""
        # Test default port (adjust according to actual configuration)
        # May be 3306 in CI environment, 3307 in local development environment
        assert config.MYSQL_PORT in [3306, 3307]  # Support both port configurations
        assert config.PORT == 8012  # Actual configuration is 8012
    
    def test_environment_variable_loading(self):
        """Test environment variable loading"""
        # Test if environment variables are correctly read
        assert isinstance(config.GOOGLE_API_KEY, str)
        assert isinstance(config.RAGFLOW_BASE_URL, str)
        assert isinstance(config.MYSQL_HOST, str)
    
    def test_config_types(self):
        """Test configuration types"""
        assert isinstance(config.MYSQL_PORT, int)
        assert isinstance(config.PORT, int)
        assert isinstance(config.GOOGLE_API_KEY, str)
        assert isinstance(config.RAGFLOW_BASE_URL, str)
        assert isinstance(config.MYSQL_HOST, str)
        assert isinstance(config.MYSQL_DATABASE, str)
