"""
Session Manager Unit Tests
"""
import pytest
from unittest.mock import Mock, patch
from crewaiBackend.utils.sessionManager import SessionManager, ChatSession, ChatMessage


class TestChatMessage:
    """Chat message test class"""
    
    def test_message_creation(self):
        """Test message creation"""
        message = ChatMessage("user", "Hello")
        assert message.role == "user"
        assert message.content == "Hello"
        assert message.id is not None  # Use id instead of message_id
        assert message.timestamp is not None
    
    def test_message_to_dict(self):
        """Test message to dictionary conversion"""
        message = ChatMessage("user", "Hello")
        message_dict = message.to_dict()
        assert message_dict["role"] == "user"
        assert message_dict["content"] == "Hello"
        assert "id" in message_dict  # Use id instead of message_id


class TestChatSession:
    """Chat session test class"""
    
    def test_session_creation(self):
        """Test session creation"""
        session = ChatSession(session_id="session_123", title="Test Session")
        assert session.session_id == "session_123"
        assert session.title == "Test Session"
        assert len(session.messages) == 0
    
    def test_add_message(self):
        """Test adding message"""
        session = ChatSession(session_id="session_123", title="Test Session")
        session.add_message("user", "Hello")  # Pass role and content directly
        assert len(session.messages) == 1
        assert session.messages[0].content == "Hello"
    
    def test_session_to_dict(self):
        """Test session to dictionary conversion"""
        session = ChatSession(session_id="session_123", title="Test Session")
        session_dict = session.to_dict()
        assert session_dict["session_id"] == "session_123"
        assert session_dict["title"] == "Test Session"
        assert session_dict["message_count"] == 0


class TestSessionManager:
    """Session manager test class"""
    
    @pytest.fixture
    def session_manager(self):
        """Session manager fixture"""
        with patch('crewaiBackend.utils.sessionManager.db_manager') as mock_db:
            mock_db.execute_update.return_value = 1
            mock_db.execute_query.return_value = []
            return SessionManager()
    
    def test_session_manager_creation(self, session_manager):
        """Test session manager creation"""
        assert session_manager is not None
        assert hasattr(session_manager, 'db')
    
    def test_create_session(self, session_manager):
        """Test creating session"""
        session = session_manager.create_session(title="Test Session")
        assert session is not None
        assert session.title == "Test Session"
    
    def test_get_session(self, session_manager):
        """Test getting session"""
        # Mock database query result
        session_row = (
            "test_session_123", "user_1", "Test Session",
            __import__('datetime').datetime.now(), __import__('datetime').datetime.now(), "{}", None
        )
        session_manager.db.execute_query.return_value = [session_row]
        
        session = session_manager.get_session("test_session_123")
        assert session is not None
        assert session.session_id == "test_session_123"
    
    def test_add_message_to_session(self, session_manager):
        """Test adding message to session"""
        # Mock database query result
        session_row = (
            "test_session_123", "user_1", "Test Session",
            __import__('datetime').datetime.now(), __import__('datetime').datetime.now(), "{}", None
        )
        session_manager.db.execute_query.return_value = [session_row]
        
        message = session_manager.add_message("test_session_123", "user", "Hello")
        assert message is not None
        assert message.content == "Hello"
    
    def test_get_all_sessions(self, session_manager):
        """Test getting all sessions"""
        # Mock database query result - only return session ID list
        session_manager.db.execute_query.return_value = [("session1",), ("session2",)]
        
        # Mock get_session method
        with patch.object(session_manager, 'get_session') as mock_get_session:
            mock_session1 = Mock()
            mock_session2 = Mock()
            mock_get_session.side_effect = [mock_session1, mock_session2]
            
            sessions = session_manager.get_all_sessions()
            assert len(sessions) == 2
            assert mock_get_session.call_count == 2
    
    def test_delete_session(self, session_manager):
        """Test deleting session"""
        # Mock database query result
        session_row = (
            "test_session_123", "user_1", "Test Session",
            __import__('datetime').datetime.now(), __import__('datetime').datetime.now(), "{}", None
        )
        session_manager.db.execute_query.return_value = [session_row]
        session_manager.db.execute_update.return_value = 1
        
        result = session_manager.delete_session("test_session_123")
        assert result is True
