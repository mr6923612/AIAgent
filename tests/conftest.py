"""
测试配置和共享夹具
"""
import os
import sys
import pytest
import tempfile
from unittest.mock import Mock, patch
from flask import Flask

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 使用Mock避免真实的API调用
import unittest.mock as mock

# Mock所有外部依赖
with mock.patch.dict('os.environ', {
    'GOOGLE_API_KEY': 'test_key',
    'RAGFLOW_BASE_URL': 'http://localhost:80',
    'RAGFLOW_API_KEY': 'test_key',
    'RAGFLOW_CHAT_ID': 'test_chat_id'
}):
    from crewaiBackend.main import app
    from crewaiBackend.config import config
    from crewaiBackend.utils.sessionManager import SessionManager
    from crewaiBackend.utils.ragflow_client import RAGFlowClient
    from crewaiBackend.utils.session_agent_manager import SessionAgentManager


@pytest.fixture(scope="session")
def test_app():
    """测试Flask应用"""
    app.config['TESTING'] = True
    app.config['MYSQL_DATABASE'] = 'test_backend_db'
    return app


@pytest.fixture
def test_client(test_app):
    """测试客户端"""
    return test_app.test_client()


@pytest.fixture
def test_session_manager():
    """测试会话管理器"""
    return SessionManager()


@pytest.fixture
def mock_ragflow_client():
    """Mock RAGFlow客户端"""
    with patch('utils.ragflow_client.RAGFlowClient') as mock:
        mock_instance = Mock()
        mock_instance.create_session.return_value = {"session_id": "test_session_123"}
        mock_instance.converse.return_value = {"response": "Test response"}
        mock_instance.delete_session.return_value = {"success": True}
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_session_agent_manager():
    """Mock会话Agent管理器"""
    with patch('utils.session_agent_manager.SessionAgentManager') as mock:
        mock_instance = Mock()
        mock_instance.get_or_create_agent.return_value = Mock()
        mock_instance.cleanup_inactive_sessions.return_value = None
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_llm():
    """Mock LLM"""
    with patch('utils.myLLM.myLLM') as mock:
        mock_instance = Mock()
        mock_instance.invoke.return_value = "Test LLM response"
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_crew():
    """Mock CrewAI Crew"""
    with patch('crew.Crew') as mock:
        mock_instance = Mock()
        mock_instance.kickoff.return_value = "Test crew response"
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture(scope="function")
def temp_db():
    """临时数据库配置"""
    # 使用内存数据库或临时文件
    temp_db_path = tempfile.mktemp()
    original_db = config.MYSQL_DATABASE
    config.MYSQL_DATABASE = 'test_backend_db'
    yield temp_db_path
    config.MYSQL_DATABASE = original_db


@pytest.fixture
def sample_session_data():
    """示例会话数据"""
    return {
        "session_id": "test_session_123",
        "title": "Test Session",
        "message_count": 5,
        "created_at": "2024-01-01 12:00:00",
        "updated_at": "2024-01-01 12:30:00"
    }


@pytest.fixture
def sample_message_data():
    """示例消息数据"""
    return {
        "message_id": "msg_123",
        "session_id": "test_session_123",
        "role": "user",
        "content": "Hello, this is a test message",
        "timestamp": "2024-01-01 12:00:00"
    }


# 测试标记
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "api: API tests")
    config.addinivalue_line("markers", "database: Database tests")
    config.addinivalue_line("markers", "external: External service tests")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "smoke: Smoke tests")
