"""
MySQL Database Operations Tests
"""
import pytest
from unittest.mock import patch, Mock


class TestMySQLOperations:
    """MySQL operations test class"""
    
    @patch('crewaiBackend.utils.sessionManager.db_manager')
    def test_database_connection(self, mock_db):
        """Test database connection"""
        mock_db.execute_query.return_value = []
        
        from crewaiBackend.utils.sessionManager import SessionManager
        sm = SessionManager()
        # Trigger a database call
        sm.get_all_sessions()
        mock_db.execute_query.assert_called()
    
    @patch('crewaiBackend.utils.sessionManager.db_manager')
    def test_create_session_in_database(self, mock_db):
        """Test creating session in database"""
        mock_db.execute_update.return_value = 1
        
        from crewaiBackend.utils.sessionManager import SessionManager
        sm = SessionManager()
        session = sm.create_session(title="Test Session")
        assert session is not None
        mock_db.execute_update.assert_called()
    
    @patch('crewaiBackend.utils.sessionManager.db_manager')
    def test_add_message_to_database(self, mock_db):
        """Test adding message to database"""
        # Insert message and update session update time
        mock_db.execute_update.return_value = 1
        # First query counts user messages, returns 1, triggers title update
        mock_db.execute_query.side_effect = [ [(1,)] ]
        
        from crewaiBackend.utils.sessionManager import SessionManager
        sm = SessionManager()
        session = sm.create_session(title="Test Session")
        msg = sm.add_message(session.session_id, "user", "Hello")
        assert msg is not None
        assert mock_db.execute_update.call_count >= 2
    
    @patch('crewaiBackend.utils.sessionManager.db_manager')
    def test_get_session_from_database(self, mock_db):
        """Test getting session from database"""
        # Mock chat_sessions row (at least 7 columns accessed up to index 6)
        session_row = (
            "test_session_123",  # session_id
            "user_1",            # user_id
            "Test Session",      # title
            __import__('datetime').datetime.now(),  # created_at
            __import__('datetime').datetime.now(),  # updated_at
            "{}",                # context JSON
            None                  # ragflow_session_id
        )
        messages_rows = [
            ("msg1", "user", "Hello", __import__('datetime').datetime.now()),
            ("msg2", "assistant", "Hi", __import__('datetime').datetime.now()),
        ]
        mock_db.execute_query.side_effect = [ [session_row], messages_rows ]
        
        from crewaiBackend.utils.sessionManager import SessionManager
        sm = SessionManager()
        session = sm.get_session("test_session_123")
        assert session is not None
        assert len(session.messages) == 2
    
    @patch('crewaiBackend.utils.sessionManager.db_manager')
    def test_delete_session_from_database(self, mock_db):
        """Test deleting session from database"""
        # get_session query + delete call
        session_row = (
            "test_session_123", "user_1", "Test Session",
            __import__('datetime').datetime.now(), __import__('datetime').datetime.now(), "{}", None
        )
        mock_db.execute_query.side_effect = [ [session_row], [] ]
        mock_db.execute_update.return_value = 1
        
        from crewaiBackend.utils.sessionManager import SessionManager
        sm = SessionManager()
        ok = sm.delete_session("test_session_123")
        assert ok is True
        mock_db.execute_update.assert_called()
    
    @patch('crewaiBackend.utils.sessionManager.db_manager')
    def test_database_error_handling(self, mock_db):
        """Test database error handling"""
        mock_db.execute_update.side_effect = Exception("Connection failed")
        
        from crewaiBackend.utils.sessionManager import SessionManager
        sm = SessionManager()
        with pytest.raises(Exception):
            sm.create_session(title="Test Session")
    
    @patch('crewaiBackend.utils.sessionManager.db_manager')
    def test_transaction_rollback(self, mock_db):
        """Test transaction rollback"""
        mock_db.execute_update.side_effect = Exception("SQL error")
        
        from crewaiBackend.utils.sessionManager import SessionManager
        sm = SessionManager()
        with pytest.raises(Exception):
            sm.create_session(title="Test Session")
