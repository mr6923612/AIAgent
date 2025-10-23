"""
配置模块单元测试
"""
import pytest
import os
from unittest.mock import patch
from config import config


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
        assert config.MYSQL_PORT == 3307  # 实际配置是3307
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
        assert isinstance(config.PORT, int)  # 使用PORT而不是FLASK_PORT
        assert isinstance(config.GOOGLE_API_KEY, str)
        assert isinstance(config.RAGFLOW_BASE_URL, str)
        assert isinstance(config.MYSQL_HOST, str)
        assert isinstance(config.MYSQL_DATABASE, str)
