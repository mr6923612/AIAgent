"""
会话管理器单元测试
"""
import pytest
from unittest.mock import Mock, patch
from utils.sessionManager import SessionManager, ChatSession, ChatMessage


class TestChatMessage:
    """聊天消息测试类"""
    
    def test_message_creation(self):
        """测试消息创建"""
        message = ChatMessage("user", "Hello", "msg_123")
        assert message.role == "user"
        assert message.content == "Hello"
        assert message.message_id == "msg_123"
        assert message.timestamp is not None
    
    def test_message_to_dict(self):
        """测试消息转字典"""
        message = ChatMessage("user", "Hello", "msg_123")
        message_dict = message.to_dict()
        assert message_dict["role"] == "user"
        assert message_dict["content"] == "Hello"
        assert message_dict["message_id"] == "msg_123"


class TestChatSession:
    """聊天会话测试类"""
    
    def test_session_creation(self):
        """测试会话创建"""
        session = ChatSession("session_123", "Test Session")
        assert session.session_id == "session_123"
        assert session.title == "Test Session"
        assert len(session.messages) == 0
        assert session.message_count == 0
    
    def test_add_message(self):
        """测试添加消息"""
        session = ChatSession("session_123", "Test Session")
        message = ChatMessage("user", "Hello", "msg_123")
        session.add_message(message)
        assert len(session.messages) == 1
        assert session.message_count == 1
    
    def test_session_to_dict(self):
        """测试会话转字典"""
        session = ChatSession("session_123", "Test Session")
        session_dict = session.to_dict()
        assert session_dict["session_id"] == "session_123"
        assert session_dict["title"] == "Test Session"
        assert session_dict["message_count"] == 0


class TestSessionManager:
    """会话管理器测试类"""
    
    @pytest.fixture
    def session_manager(self):
        """会话管理器夹具"""
        with patch('utils.sessionManager.SessionManager._init_database'):
            return SessionManager()
    
    def test_session_manager_creation(self, session_manager):
        """测试会话管理器创建"""
        assert session_manager is not None
        assert hasattr(session_manager, 'sessions')
    
    @patch('utils.sessionManager.SessionManager._init_database')
    def test_create_session(self, mock_init_db, session_manager):
        """测试创建会话"""
        session_id = session_manager.create_session("Test Session")
        assert session_id is not None
        assert session_id in session_manager.sessions
    
    @patch('utils.sessionManager.SessionManager._init_database')
    def test_get_session(self, mock_init_db, session_manager):
        """测试获取会话"""
        session_id = session_manager.create_session("Test Session")
        session = session_manager.get_session(session_id)
        assert session is not None
        assert session.session_id == session_id
    
    @patch('utils.sessionManager.SessionManager._init_database')
    def test_add_message_to_session(self, mock_init_db, session_manager):
        """测试向会话添加消息"""
        session_id = session_manager.create_session("Test Session")
        message_id = session_manager.add_message_to_session(session_id, "user", "Hello")
        assert message_id is not None
        
        session = session_manager.get_session(session_id)
        assert len(session.messages) == 1
        assert session.messages[0].content == "Hello"
    
    @patch('utils.sessionManager.SessionManager._init_database')
    def test_get_all_sessions(self, mock_init_db, session_manager):
        """测试获取所有会话"""
        session_manager.create_session("Session 1")
        session_manager.create_session("Session 2")
        
        sessions = session_manager.get_all_sessions()
        assert len(sessions) == 2
    
    @patch('utils.sessionManager.SessionManager._init_database')
    def test_delete_session(self, mock_init_db, session_manager):
        """测试删除会话"""
        session_id = session_manager.create_session("Test Session")
        assert session_id in session_manager.sessions
        
        session_manager.delete_session(session_id)
        assert session_id not in session_manager.sessions
