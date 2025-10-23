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
        message = ChatMessage("user", "Hello")
        assert message.role == "user"
        assert message.content == "Hello"
        assert message.id is not None  # 使用 id 而不是 message_id
        assert message.timestamp is not None
    
    def test_message_to_dict(self):
        """测试消息转字典"""
        message = ChatMessage("user", "Hello")
        message_dict = message.to_dict()
        assert message_dict["role"] == "user"
        assert message_dict["content"] == "Hello"
        assert "id" in message_dict  # 使用 id 而不是 message_id


class TestChatSession:
    """聊天会话测试类"""
    
    def test_session_creation(self):
        """测试会话创建"""
        session = ChatSession(session_id="session_123", title="Test Session")
        assert session.session_id == "session_123"
        assert session.title == "Test Session"
        assert len(session.messages) == 0
    
    def test_add_message(self):
        """测试添加消息"""
        session = ChatSession(session_id="session_123", title="Test Session")
        session.add_message("user", "Hello")  # 直接传 role 和 content
        assert len(session.messages) == 1
        assert session.messages[0].content == "Hello"
    
    def test_session_to_dict(self):
        """测试会话转字典"""
        session = ChatSession(session_id="session_123", title="Test Session")
        session_dict = session.to_dict()
        assert session_dict["session_id"] == "session_123"
        assert session_dict["title"] == "Test Session"
        assert session_dict["message_count"] == 0


class TestSessionManager:
    """会话管理器测试类"""
    
    @pytest.fixture
    def session_manager(self):
        """会话管理器夹具"""
        with patch('utils.sessionManager.db_manager') as mock_db:
            mock_db.execute_update.return_value = 1
            mock_db.execute_query.return_value = []
            return SessionManager()
    
    def test_session_manager_creation(self, session_manager):
        """测试会话管理器创建"""
        assert session_manager is not None
        assert hasattr(session_manager, 'db')
    
    def test_create_session(self, session_manager):
        """测试创建会话"""
        session = session_manager.create_session(title="Test Session")
        assert session is not None
        assert session.title == "Test Session"
    
    def test_get_session(self, session_manager):
        """测试获取会话"""
        # Mock 数据库查询结果
        session_row = (
            "test_session_123", "user_1", "Test Session",
            __import__('datetime').datetime.now(), __import__('datetime').datetime.now(), "{}", None
        )
        session_manager.db.execute_query.return_value = [session_row]
        
        session = session_manager.get_session("test_session_123")
        assert session is not None
        assert session.session_id == "test_session_123"
    
    def test_add_message_to_session(self, session_manager):
        """测试向会话添加消息"""
        # Mock 数据库查询结果
        session_row = (
            "test_session_123", "user_1", "Test Session",
            __import__('datetime').datetime.now(), __import__('datetime').datetime.now(), "{}", None
        )
        session_manager.db.execute_query.return_value = [session_row]
        
        message = session_manager.add_message("test_session_123", "user", "Hello")
        assert message is not None
        assert message.content == "Hello"
    
    def test_get_all_sessions(self, session_manager):
        """测试获取所有会话"""
        # Mock 数据库查询结果 - 需要完整的会话行数据
        session_row1 = (
            "session1", "user_1", "Session 1",
            __import__('datetime').datetime.now(), __import__('datetime').datetime.now(), "{}", None
        )
        session_row2 = (
            "session2", "user_1", "Session 2", 
            __import__('datetime').datetime.now(), __import__('datetime').datetime.now(), "{}", None
        )
        
        # 第一次查询返回会话ID列表，后续查询返回会话详情
        session_manager.db.execute_query.side_effect = [
            [("session1",), ("session2",)],  # get_all_sessions 的查询
            [session_row1, []],  # get_session("session1") 的查询
            [session_row2, []]   # get_session("session2") 的查询
        ]
        
        sessions = session_manager.get_all_sessions()
        assert len(sessions) == 2
    
    def test_delete_session(self, session_manager):
        """测试删除会话"""
        # Mock 数据库查询结果
        session_row = (
            "test_session_123", "user_1", "Test Session",
            __import__('datetime').datetime.now(), __import__('datetime').datetime.now(), "{}", None
        )
        session_manager.db.execute_query.return_value = [session_row]
        session_manager.db.execute_update.return_value = 1
        
        result = session_manager.delete_session("test_session_123")
        assert result is True
