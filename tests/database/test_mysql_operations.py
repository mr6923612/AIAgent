"""
MySQL数据库操作测试
"""
import pytest
from unittest.mock import patch, Mock


class TestMySQLOperations:
    """MySQL操作测试类"""
    
    @patch('crewaiBackend.utils.sessionManager.db_manager')
    def test_database_connection(self, mock_db):
        """测试数据库连接"""
        mock_db.execute_query.return_value = []
        
        from crewaiBackend.utils.sessionManager import SessionManager
        sm = SessionManager()
        # 触发一次数据库调用
        sm.get_all_sessions()
        mock_db.execute_query.assert_called()
    
    @patch('crewaiBackend.utils.sessionManager.db_manager')
    def test_create_session_in_database(self, mock_db):
        """测试在数据库中创建会话"""
        mock_db.execute_update.return_value = 1
        
        from crewaiBackend.utils.sessionManager import SessionManager
        sm = SessionManager()
        session = sm.create_session(title="Test Session")
        assert session is not None
        mock_db.execute_update.assert_called()
    
    @patch('crewaiBackend.utils.sessionManager.db_manager')
    def test_add_message_to_database(self, mock_db):
        """测试在数据库中添加消息"""
        # 插入消息与更新会话更新时间
        mock_db.execute_update.return_value = 1
        # 第一次查询统计用户消息数返回1，触发标题更新
        mock_db.execute_query.side_effect = [ [(1,)] ]
        
        from crewaiBackend.utils.sessionManager import SessionManager
        sm = SessionManager()
        session = sm.create_session(title="Test Session")
        msg = sm.add_message(session.session_id, "user", "Hello")
        assert msg is not None
        assert mock_db.execute_update.call_count >= 2
    
    @patch('crewaiBackend.utils.sessionManager.db_manager')
    def test_get_session_from_database(self, mock_db):
        """测试从数据库获取会话"""
        # 模拟 chat_sessions 行(至少7列访问到 index 6)
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
        """测试从数据库删除会话"""
        # get_session 查询 + 删除调用
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
        """测试数据库错误处理"""
        mock_db.execute_update.side_effect = Exception("Connection failed")
        
        from crewaiBackend.utils.sessionManager import SessionManager
        sm = SessionManager()
        with pytest.raises(Exception):
            sm.create_session(title="Test Session")
    
    @patch('crewaiBackend.utils.sessionManager.db_manager')
    def test_transaction_rollback(self, mock_db):
        """测试事务回滚"""
        mock_db.execute_update.side_effect = Exception("SQL error")
        
        from crewaiBackend.utils.sessionManager import SessionManager
        sm = SessionManager()
        with pytest.raises(Exception):
            sm.create_session(title="Test Session")
