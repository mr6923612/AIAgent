"""
MySQL数据库操作测试
"""
import pytest
from unittest.mock import patch, Mock, MagicMock


class TestMySQLOperations:
    """MySQL操作测试类"""
    
    @patch('utils.sessionManager.pymysql.connect')
    def test_database_connection(self, mock_connect):
        """测试数据库连接"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        from utils.sessionManager import SessionManager
        with patch.object(SessionManager, '_init_database'):
            sm = SessionManager()
            # 测试连接是否被调用
            mock_connect.assert_called()
    
    @patch('utils.sessionManager.pymysql.connect')
    def test_create_session_in_database(self, mock_connect):
        """测试在数据库中创建会话"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        from utils.sessionManager import SessionManager
        with patch.object(SessionManager, '_init_database'):
            sm = SessionManager()
            session_id = sm.create_session("Test Session")
            
            # 验证数据库操作被调用
            mock_cursor.execute.assert_called()
            mock_conn.commit.assert_called()
    
    @patch('utils.sessionManager.pymysql.connect')
    def test_add_message_to_database(self, mock_connect):
        """测试在数据库中添加消息"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        from utils.sessionManager import SessionManager
        with patch.object(SessionManager, '_init_database'):
            sm = SessionManager()
            session_id = sm.create_session("Test Session")
            message_id = sm.add_message_to_session(session_id, "user", "Hello")
            
            # 验证消息插入操作被调用
            assert mock_cursor.execute.call_count >= 2  # 至少调用两次execute
    
    @patch('utils.sessionManager.pymysql.connect')
    def test_get_session_from_database(self, mock_connect):
        """测试从数据库获取会话"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        
        # 模拟数据库查询结果
        mock_cursor.fetchall.return_value = [
            ("test_session_123", "Test Session", 5, "2024-01-01 12:00:00", "2024-01-01 12:30:00")
        ]
        mock_connect.return_value = mock_conn
        
        from utils.sessionManager import SessionManager
        with patch.object(SessionManager, '_init_database'):
            sm = SessionManager()
            session = sm.get_session("test_session_123")
            
            # 验证数据库查询被调用
            mock_cursor.execute.assert_called()
            assert session is not None
    
    @patch('utils.sessionManager.pymysql.connect')
    def test_delete_session_from_database(self, mock_connect):
        """测试从数据库删除会话"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        from utils.sessionManager import SessionManager
        with patch.object(SessionManager, '_init_database'):
            sm = SessionManager()
            session_id = sm.create_session("Test Session")
            sm.delete_session(session_id)
            
            # 验证删除操作被调用
            mock_cursor.execute.assert_called()
            mock_conn.commit.assert_called()
    
    @patch('utils.sessionManager.pymysql.connect')
    def test_database_error_handling(self, mock_connect):
        """测试数据库错误处理"""
        mock_connect.side_effect = Exception("Connection failed")
        
        from utils.sessionManager import SessionManager
        with pytest.raises(Exception):
            with patch.object(SessionManager, '_init_database'):
                sm = SessionManager()
                sm.create_session("Test Session")
    
    @patch('utils.sessionManager.pymysql.connect')
    def test_transaction_rollback(self, mock_connect):
        """测试事务回滚"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("SQL error")
        mock_connect.return_value = mock_conn
        
        from utils.sessionManager import SessionManager
        with patch.object(SessionManager, '_init_database'):
            sm = SessionManager()
            with pytest.raises(Exception):
                sm.create_session("Test Session")
            
            # 验证回滚被调用
            mock_conn.rollback.assert_called()
