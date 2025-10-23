"""
CrewAI API测试
"""
import pytest
import json
from unittest.mock import patch, Mock


class TestCrewAPI:
    """CrewAI API测试类"""
    
    def test_run_crew_success(self, test_client, mock_session_agent_manager, 
                             mock_ragflow_client, mock_crew):
        """测试成功运行CrewAI"""
        with patch('main.session_manager') as mock_sm:
            mock_session = Mock()
            mock_session.session_id = "test_session_123"
            mock_sm.get_session.return_value = mock_session
            
            response = test_client.post('/api/run_crew', 
                                      json={
                                          "session_id": "test_session_123",
                                          "message": "Hello, test message"
                                      })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert "task_id" in data
    
    def test_run_crew_invalid_session(self, test_client):
        """测试无效会话运行CrewAI"""
        with patch('main.session_manager') as mock_sm:
            mock_sm.get_session.return_value = None
            
            response = test_client.post('/api/run_crew', 
                                      json={
                                          "session_id": "invalid_session",
                                          "message": "Hello"
                                      })
            
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False
            assert "Session not found" in data["error"]
    
    def test_run_crew_missing_data(self, test_client):
        """测试缺少必要数据"""
        response = test_client.post('/api/run_crew', 
                                  json={"session_id": "test_session"})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Missing required data" in data["error"]
    
    def test_run_crew_with_file_upload(self, test_client, mock_session_agent_manager,
                                      mock_ragflow_client, mock_crew):
        """测试带文件上传的CrewAI运行"""
        with patch('main.session_manager') as mock_sm:
            mock_session = Mock()
            mock_session.session_id = "test_session_123"
            mock_sm.get_session.return_value = mock_session
            
            # 模拟文件上传
            data = {
                'session_id': 'test_session_123',
                'message': 'Process this file',
                'file': (io.BytesIO(b'file content'), 'test.txt')
            }
            
            response = test_client.post('/api/run_crew', 
                                      data=data,
                                      content_type='multipart/form-data')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
    
    def test_get_task_status(self, test_client):
        """测试获取任务状态"""
        with patch('main.task_status') as mock_status:
            mock_status.get.return_value = {
                "status": "completed",
                "result": "Test result"
            }
            
            response = test_client.get('/api/task_status/test_task_123')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["status"] == "completed"
    
    def test_get_task_status_not_found(self, test_client):
        """测试任务状态不存在"""
        with patch('main.task_status') as mock_status:
            mock_status.get.return_value = None
            
            response = test_client.get('/api/task_status/nonexistent_task')
            
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False
            assert "Task not found" in data["error"]
