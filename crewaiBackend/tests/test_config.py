"""
测试配置文件
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 测试环境配置
TEST_CONFIG = {
    'MYSQL_DATABASE': 'test_backend_db',
    'MYSQL_HOST': 'localhost',
    'MYSQL_PORT': 3306,
    'MYSQL_USER': 'root',
    'MYSQL_PASSWORD': '',
    'RAGFLOW_BASE_URL': 'http://localhost:9380',
    'RAGFLOW_API_KEY': 'test_key',
    'RAGFLOW_CHAT_ID': 'test_chat_id',
    'GOOGLE_API_KEY': 'test_google_key',
    'FLASK_ENV': 'testing',
    'FLASK_DEBUG': False
}

def setup_test_environment():
    """设置测试环境"""
    # 设置测试环境变量
    for key, value in TEST_CONFIG.items():
        os.environ[key] = str(value)
    
    # 确保测试目录存在
    test_dirs = [
        'reports',
        'htmlcov',
        'crewaiBackend/tests/unit',
        'crewaiBackend/tests/integration',
        'crewaiBackend/tests/api',
        'crewaiBackend/tests/database',
        'crewaiBackend/tests/external'
    ]
    
    for dir_path in test_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

def cleanup_test_environment():
    """清理测试环境"""
    # 清理测试环境变量
    for key in TEST_CONFIG.keys():
        if key in os.environ:
            del os.environ[key]

if __name__ == "__main__":
    setup_test_environment()
    print("Test environment configured successfully!")
