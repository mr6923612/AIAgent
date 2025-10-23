"""
会话流程集成测试
"""
import pytest
from unittest.mock import patch, Mock


class TestSessionFlow:
    """会话流程测试类"""
    
    def test_complete_session_flow(self, test_client, mock_ragflow_client, 
                                  mock_session_agent_manager, mock_crew):
        """测试完整的会话流程"""
        with patch('main.session_manager') as mock_sm:
            # 1. 创建会话
            mock_sm.create_session.return_value = "test_session_123"
            mock_session = Mock()
            mock_session.session_id = "test_session_123"
            mock_session.title = "Test Session"
            mock_sm.get_session.return_value = mock_session
            
            # 创建会话
            create_response = test_client.post('/api/sessions', 
                                             json={"title": "Test Session"})
            assert create_response.status_code == 200
            
            # 2. 运行CrewAI
            crew_response = test_client.post('/api/run_crew', 
                                           json={
                                               "session_id": "test_session_123",
                                               "message": "Hello, test message"
                                           })
            assert crew_response.status_code == 200
            
            # 3. 获取会话信息
            get_response = test_client.get('/api/sessions/test_session_123')
            assert get_response.status_code == 200
            
            # 4. 删除会话
            delete_response = test_client.delete('/api/sessions/test_session_123')
            assert delete_response.status_code == 200
    
    def test_multiple_sessions_management(self, test_client, mock_ragflow_client):
        """测试多会话管理"""
        with patch('main.session_manager') as mock_sm:
            # 创建多个会话
            mock_sessions = [
                {"session_id": "session_1", "title": "Session 1", "message_count": 5},
                {"session_id": "session_2", "title": "Session 2", "message_count": 3},
                {"session_id": "session_3", "title": "Session 3", "message_count": 8}
            ]
            mock_sm.get_all_sessions.return_value = mock_sessions
            
            # 获取所有会话
            response = test_client.get('/api/sessions')
            assert response.status_code == 200
            data = response.get_json()
            assert len(data["sessions"]) == 3
    
    def test_session_persistence(self, test_client, mock_ragflow_client):
        """测试会话持久化"""
        with patch('main.session_manager') as mock_sm:
            # 模拟会话持久化
            mock_sm.create_session.return_value = "persistent_session_123"
            mock_session = Mock()
            mock_session.session_id = "persistent_session_123"
            mock_session.to_dict.return_value = {
                "session_id": "persistent_session_123",
                "title": "Persistent Session",
                "message_count": 0
            }
            mock_sm.get_session.return_value = mock_session
            
            # 创建会话
            create_response = test_client.post('/api/sessions', 
                                             json={"title": "Persistent Session"})
            assert create_response.status_code == 200
            
            # 重新获取会话（模拟重启后）
            get_response = test_client.get('/api/sessions/persistent_session_123')
            assert get_response.status_code == 200
            data = get_response.get_json()
            assert data["session"]["session_id"] == "persistent_session_123"
    
    def test_error_handling_flow(self, test_client):
        """测试错误处理流程"""
        with patch('main.session_manager') as mock_sm:
            # 模拟数据库错误
            mock_sm.create_session.side_effect = Exception("Database error")
            
            # 创建会话应该失败
            response = test_client.post('/api/sessions', 
                                      json={"title": "Test Session"})
            assert response.status_code == 500
            data = response.get_json()
            assert data["success"] is False
            assert "Database error" in data["error"]
