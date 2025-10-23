"""
简化的测试示例 - 展示测试框架的基本使用
"""
import pytest
from config import config


class TestSimple:
    """简单测试类"""
    
    def test_config_basic(self):
        """测试基本配置"""
        assert config.MYSQL_HOST == "localhost"
        assert config.MYSQL_PORT == 3307
        assert config.PORT == 8012
    
    def test_config_types(self):
        """测试配置类型"""
        assert isinstance(config.MYSQL_PORT, int)
        assert isinstance(config.PORT, int)
        assert isinstance(config.MYSQL_HOST, str)
        assert isinstance(config.MYSQL_DATABASE, str)
    
    def test_math_operations(self):
        """测试基本数学运算"""
        assert 2 + 2 == 4
        assert 3 * 3 == 9
        assert 10 / 2 == 5
    
    def test_string_operations(self):
        """测试字符串操作"""
        text = "Hello World"
        assert len(text) == 11
        assert text.upper() == "HELLO WORLD"
        assert text.lower() == "hello world"
    
    @pytest.mark.parametrize("input,expected", [
        (1, 1),
        (2, 4),
        (3, 9),
        (4, 16),
        (5, 25)
    ])
    def test_square(self, input, expected):
        """参数化测试示例"""
        assert input ** 2 == expected
