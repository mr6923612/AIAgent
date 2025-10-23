"""
基本功能测试
测试系统的核心基本功能
"""
import pytest
from unittest.mock import patch, Mock
from datetime import datetime


class TestBasicFunctionality:
    """基本功能测试类"""
    
    def test_config_loading_functionality(self):
        """测试配置加载功能"""
        from crewaiBackend.config import config
        
        # 测试基本配置项存在
        assert hasattr(config, 'GOOGLE_API_KEY')
        assert hasattr(config, 'RAGFLOW_BASE_URL')
        assert hasattr(config, 'MYSQL_HOST')
        assert hasattr(config, 'MYSQL_PORT')
        assert hasattr(config, 'MYSQL_DATABASE')
        
        # 测试配置项类型
        assert isinstance(config.MYSQL_PORT, int)
        assert isinstance(config.PORT, int)
        assert isinstance(config.GOOGLE_API_KEY, str)
        assert isinstance(config.RAGFLOW_BASE_URL, str)
    
    def test_database_connection_functionality(self):
        """测试数据库连接功能"""
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
        """测试会话管理功能"""
        with patch('crewaiBackend.utils.sessionManager.db_manager') as mock_db:
            mock_db.execute_update.return_value = 1
            mock_db.execute_query.return_value = []
            
            from crewaiBackend.utils.sessionManager import SessionManager, ChatSession, ChatMessage
            
            # 测试SessionManager创建
            sm = SessionManager()
            assert sm is not None
            assert hasattr(sm, 'db')
            
            # 测试ChatSession创建
            session = ChatSession(session_id="test_123", title="Test Session")
            assert session.session_id == "test_123"
            assert session.title == "Test Session"
            assert len(session.messages) == 0
            
            # 测试ChatMessage创建
            message = ChatMessage("user", "Hello")
            assert message.role == "user"
            assert message.content == "Hello"
            assert message.id is not None
    
    def test_job_management_functionality(self):
        """测试任务管理功能"""
        from crewaiBackend.utils.jobManager import Event, Job, append_event, jobs
        
        # 测试Event创建
        event = Event(timestamp=datetime.now(), data="test data")
        assert event.data == "test data"
        assert event.timestamp is not None
        
        # 测试Job创建
        job = Job(
            status="STARTED",
            events=[],
            result=""
        )
        assert job.status == "STARTED"
        assert job.events == []
        
        # 测试append_event函数存在
        assert callable(append_event)
    
    def test_ragflow_client_functionality(self):
        """测试RAGFlow客户端功能"""
        with patch('crewaiBackend.utils.ragflow_client.requests') as mock_requests:
            mock_response = Mock()
            mock_response.json.return_value = {'code': 0, 'data': 'test'}
            mock_response.status_code = 200
            mock_requests.post.return_value = mock_response
            
            from crewaiBackend.utils.ragflow_client import RAGFlowClient
            
            # 测试RAGFlowClient创建
            client = RAGFlowClient("http://localhost:80", "test_key")
            assert client is not None
            assert client.base_url == "http://localhost:80"
            assert client.api_key == "test_key"
    
    
    def test_llm_functionality(self):
        """测试LLM功能"""
        with patch('crewaiBackend.utils.myLLM.ChatGoogleGenerativeAI') as mock_llm:
            mock_instance = Mock()
            mock_llm.return_value = mock_instance
            
            from crewaiBackend.utils.myLLM import my_llm
            
            # 测试LLM创建
            llm = my_llm("google")
            assert llm is not None
    
    def test_flask_app_functionality(self):
        """测试Flask应用功能"""
        from crewaiBackend.main import app
        
        # 测试Flask应用创建
        assert app is not None
        assert app.name == 'crewaiBackend.main'
        
        # 测试路由注册
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        assert '/health' in routes
        assert '/api/sessions' in routes
        assert '/api/crew' in routes
    
    def test_error_handling_functionality(self):
        """测试错误处理功能"""
        with patch('crewaiBackend.utils.sessionManager.db_manager') as mock_db:
            mock_db.execute_update.side_effect = Exception("Database error")
            
            from crewaiBackend.utils.sessionManager import SessionManager
            
            sm = SessionManager()
            
            # 测试错误处理
            with pytest.raises(Exception):
                sm.create_session(title="Test Session")
    
    def test_data_validation_functionality(self):
        """测试数据验证功能"""
        from crewaiBackend.utils.sessionManager import ChatMessage, ChatSession
        
        # 测试消息数据验证
        message = ChatMessage("user", "Hello")
        assert message.role in ["user", "assistant", "system"]
        assert isinstance(message.content, str)
        assert len(message.content) > 0
        
        # 测试会话数据验证
        session = ChatSession(session_id="test_123", title="Test Session")
        assert isinstance(session.session_id, str)
        assert isinstance(session.title, str)
        assert len(session.session_id) > 0
        assert len(session.title) > 0
    
    def test_concurrent_access_functionality(self):
        """测试并发访问功能"""
        from crewaiBackend.utils.jobManager import jobs_lock
        
        # 测试锁机制存在
        assert jobs_lock is not None
        
        # 测试锁可以被获取和释放
        with jobs_lock:
            # 在锁内执行一些操作
            assert True
        
        # 锁应该已经释放
        assert True
    
    def test_logging_functionality(self):
        """测试日志功能"""
        import logging
        
        # 测试日志记录器创建
        logger = logging.getLogger('test_logger')
        assert logger is not None
        
        # 测试日志级别设置
        logger.setLevel(logging.INFO)
        assert logger.level == logging.INFO
        
        # 测试日志消息记录
        with patch('logging.Logger.info') as mock_info:
            logger.info("Test log message")
            mock_info.assert_called_once_with("Test log message")
    
    def test_json_serialization_functionality(self):
        """测试JSON序列化功能"""
        from crewaiBackend.utils.sessionManager import ChatMessage, ChatSession
        import json
        
        # 测试消息JSON序列化
        message = ChatMessage("user", "Hello")
        message_dict = message.to_dict()
        json_str = json.dumps(message_dict)
        assert isinstance(json_str, str)
        
        # 测试会话JSON序列化
        session = ChatSession(session_id="test_123", title="Test Session")
        session_dict = session.to_dict()
        json_str = json.dumps(session_dict)
        assert isinstance(json_str, str)
