"""
配置模块单元测试
"""
import pytest
import os
from unittest.mock import patch
from crewaiBackend.config import config


class TestConfig:
    """配置测试类"""
    
    def test_config_loading(self):
        """测试配置加载"""
        assert config.GOOGLE_API_KEY is not None
        assert config.RAGFLOW_BASE_URL is not None
        assert config.MYSQL_HOST is not None
        assert config.MYSQL_PORT is not None
        assert config.MYSQL_DATABASE is not None
    
    def test_config_defaults(self):
        """测试配置默认值"""
        # 测试默认端口（根据实际配置调整）
        # 在CI环境中可能是3306，在本地开发环境中是3307
        assert config.MYSQL_PORT in [3306, 3307]  # 支持两种端口配置
        assert config.PORT == 8012  # 实际配置是8012
    
    def test_environment_variable_loading(self):
        """测试环境变量加载"""
        # 测试环境变量是否被正确读取
        assert isinstance(config.GOOGLE_API_KEY, str)
        assert isinstance(config.RAGFLOW_BASE_URL, str)
        assert isinstance(config.MYSQL_HOST, str)
    
    def test_config_types(self):
        """测试配置类型"""
        assert isinstance(config.MYSQL_PORT, int)
        assert isinstance(config.PORT, int)
        assert isinstance(config.GOOGLE_API_KEY, str)
        assert isinstance(config.RAGFLOW_BASE_URL, str)
        assert isinstance(config.MYSQL_HOST, str)
        assert isinstance(config.MYSQL_DATABASE, str)
