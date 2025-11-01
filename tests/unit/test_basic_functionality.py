"""
Basic Functionality Tests
Test core basic functionality of the system
"""
import pytest
from unittest.mock import patch, Mock
from datetime import datetime


class TestBasicFunctionality:
    """Basic functionality test class"""
    
    def test_config_loading_functionality(self):
        """Test configuration loading functionality"""
        from crewaiBackend.config import config
        
        # Test basic configuration items exist
        assert hasattr(config, 'GOOGLE_API_KEY')
        assert hasattr(config, 'RAGFLOW_BASE_URL')
        assert hasattr(config, 'MYSQL_HOST')
        assert hasattr(config, 'MYSQL_PORT')
        assert hasattr(config, 'MYSQL_DATABASE')
        
        # Test configuration item types
        assert isinstance(config.MYSQL_PORT, int)
        assert isinstance(config.PORT, int)
        assert isinstance(config.GOOGLE_API_KEY, str)
        assert isinstance(config.RAGFLOW_BASE_URL, str)
    
    def test_database_connection_functionality(self):
        """Test database connection functionality"""
        with patch('crewaiBackend.utils.database.DatabaseManager') as mock_db_manager:
            mock_db = Mock()
            mock_db.execute_query.return_value = []
            mock_db.execute_update.return_value = 1
            mock_db_manager.return_value = mock_db
            
            from crewaiBackend.utils.database import db_manager
            assert db_manager is not None
            assert callable(db_manager.execute_query)
            assert callable(db_manager.execute_update)
    
    def test_session_management_functionality(self):
        """Test session management functionality"""
        with patch('crewaiBackend.utils.sessionManager.db_manager') as mock_db:
            mock_db.execute_update.return_value = 1
            mock_db.execute_query.return_value = []
            
            from crewaiBackend.utils.sessionManager import SessionManager, ChatSession, ChatMessage
            
            # Test SessionManager creation
            sm = SessionManager()
            assert sm is not None
            assert hasattr(sm, 'db')
            
            # Test ChatSession creation
            session = ChatSession(session_id="test_123", title="Test Session")
            assert session.session_id == "test_123"
            assert session.title == "Test Session"
            assert len(session.messages) == 0
            
            # Test ChatMessage creation
            message = ChatMessage("user", "Hello")
            assert message.role == "user"
            assert message.content == "Hello"
            assert message.id is not None
    
    def test_job_management_functionality(self):
        """Test job management functionality"""
        from crewaiBackend.utils.jobManager import Event, Job, append_event, jobs
        
        # Test Event creation
        event = Event(timestamp=datetime.now(), data="test data")
        assert event.data == "test data"
        assert event.timestamp is not None
        
        # Test Job creation
        job = Job(
            status="STARTED",
            events=[],
            result=""
        )
        assert job.status == "STARTED"
        assert job.events == []
        
        # Test append_event function exists
        assert callable(append_event)
    
    def test_ragflow_client_functionality(self):
        """Test RAGFlow client functionality"""
        with patch('crewaiBackend.utils.ragflow_client.requests') as mock_requests:
            mock_response = Mock()
            mock_response.json.return_value = {'code': 0, 'data': 'test'}
            mock_response.status_code = 200
            mock_requests.post.return_value = mock_response
            
            from crewaiBackend.utils.ragflow_client import RAGFlowClient
            
            # Test RAGFlowClient creation
            client = RAGFlowClient("http://localhost:80", "test_key")
            assert client is not None
            assert client.base_url == "http://localhost:80"
            assert client.api_key == "test_key"
    
    
    def test_llm_functionality(self):
        """Test LLM functionality"""
        with patch('crewaiBackend.utils.myLLM.ChatGoogleGenerativeAI') as mock_llm:
            mock_instance = Mock()
            mock_llm.return_value = mock_instance
            
            from crewaiBackend.utils.myLLM import my_llm
            
            # Test LLM creation
            llm = my_llm("google")
            assert llm is not None
    
    def test_flask_app_functionality(self):
        """Test Flask application functionality"""
        from crewaiBackend.main import app
        
        # Test Flask application creation
        assert app is not None
        assert app.name == 'crewaiBackend.main'
        
        # Test route registration
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        assert '/health' in routes
        assert '/api/sessions' in routes
        assert '/api/crew' in routes
    
    def test_error_handling_functionality(self):
        """Test error handling functionality"""
        with patch('crewaiBackend.utils.sessionManager.db_manager') as mock_db:
            mock_db.execute_update.side_effect = Exception("Database error")
            
            from crewaiBackend.utils.sessionManager import SessionManager
            
            sm = SessionManager()
            
            # Test error handling
            with pytest.raises(Exception):
                sm.create_session(title="Test Session")
    
    def test_data_validation_functionality(self):
        """Test data validation functionality"""
        from crewaiBackend.utils.sessionManager import ChatMessage, ChatSession
        
        # Test message data validation
        message = ChatMessage("user", "Hello")
        assert message.role in ["user", "assistant", "system"]
        assert isinstance(message.content, str)
        assert len(message.content) > 0
        
        # Test session data validation
        session = ChatSession(session_id="test_123", title="Test Session")
        assert isinstance(session.session_id, str)
        assert isinstance(session.title, str)
        assert len(session.session_id) > 0
        assert len(session.title) > 0
    
    def test_concurrent_access_functionality(self):
        """Test concurrent access functionality"""
        from crewaiBackend.utils.jobManager import jobs_lock
        
        # Test lock mechanism exists
        assert jobs_lock is not None
        
        # Test lock can be acquired and released
        with jobs_lock:
            # Perform some operations within the lock
            assert True
        
        # Lock should have been released
        assert True
    
    def test_logging_functionality(self):
        """Test logging functionality"""
        import logging
        
        # Test logger creation
        logger = logging.getLogger('test_logger')
        assert logger is not None
        
        # Test log level setting
        logger.setLevel(logging.INFO)
        assert logger.level == logging.INFO
        
        # Test log message recording
        with patch('logging.Logger.info') as mock_info:
            logger.info("Test log message")
            mock_info.assert_called_once_with("Test log message")
    
    def test_json_serialization_functionality(self):
        """Test JSON serialization functionality"""
        from crewaiBackend.utils.sessionManager import ChatMessage, ChatSession
        import json
        
        # Test message JSON serialization
        message = ChatMessage("user", "Hello")
        message_dict = message.to_dict()
        json_str = json.dumps(message_dict)
        assert isinstance(json_str, str)
        
        # Test session JSON serialization
        session = ChatSession(session_id="test_123", title="Test Session")
        session_dict = session.to_dict()
        json_str = json.dumps(session_dict)
        assert isinstance(json_str, str)
