"""
会话API测试
"""
import pytest
import json
from unittest.mock import patch, Mock


class TestSessionAPI:
    """会话API测试类"""
    
    def test_create_session(self, test_client, mock_ragflow_client):
        """测试创建会话API"""
        with patch('main.session_manager') as mock_sm:
            mock_sm.create_session.return_value = "test_session_123"
            
            response = test_client.post('/api/sessions', 
                                      json={"title": "Test Session"})
            
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert "session_id" in data
    
    def test_get_all_sessions(self, test_client):
        """测试获取所有会话API"""
        with patch('main.session_manager') as mock_sm:
            mock_sessions = [
                {"session_id": "session_1", "title": "Session 1", "message_count": 5},
                {"session_id": "session_2", "title": "Session 2", "message_count": 3}
            ]
            mock_sm.get_all_sessions.return_value = mock_sessions
            
            response = test_client.get('/api/sessions')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert len(data["sessions"]) == 2
    
    def test_get_session(self, test_client):
        """测试获取特定会话API"""
        with patch('main.session_manager') as mock_sm:
            mock_session = Mock()
            mock_session.to_dict.return_value = {
                "session_id": "test_session_123",
                "title": "Test Session",
                "message_count": 5
            }
            mock_sm.get_session.return_value = mock_session
            
            response = test_client.get('/api/sessions/test_session_123')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["session"]["session_id"] == "test_session_123"
    
    def test_delete_session(self, test_client, mock_ragflow_client):
        """测试删除会话API"""
        with patch('main.session_manager') as mock_sm:
            mock_sm.delete_session.return_value = True
            
            response = test_client.delete('/api/sessions/test_session_123')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
    
    def test_session_not_found(self, test_client):
        """测试会话不存在的情况"""
        with patch('main.session_manager') as mock_sm:
            mock_sm.get_session.return_value = None
            
            response = test_client.get('/api/sessions/nonexistent_session')
            
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False
            assert "Session not found" in data["error"]
    
    def test_invalid_session_data(self, test_client):
        """测试无效的会话数据"""
        response = test_client.post('/api/sessions', 
                                  json={"invalid": "data"})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
