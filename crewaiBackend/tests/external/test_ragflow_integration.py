"""
RAGFlow集成测试
"""
import pytest
from unittest.mock import patch, Mock
import requests


class TestRAGFlowIntegration:
    """RAGFlow集成测试类"""
    
    @patch('utils.ragflow_client.requests.post')
    def test_ragflow_create_session(self, mock_post):
        """测试RAGFlow创建会话"""
        mock_response = Mock()
        mock_response.json.return_value = {"session_id": "ragflow_session_123"}
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        from utils.ragflow_client import RAGFlowClient
        client = RAGFlowClient()
        result = client.create_session()
        
        assert result["session_id"] == "ragflow_session_123"
        mock_post.assert_called_once()
    
    @patch('utils.ragflow_client.requests.post')
    def test_ragflow_converse(self, mock_post):
        """测试RAGFlow对话"""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "RAGFlow response"}
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        from utils.ragflow_client import RAGFlowClient
        client = RAGFlowClient()
        result = client.converse("ragflow_session_123", "Hello")
        
        assert result["response"] == "RAGFlow response"
        mock_post.assert_called_once()
    
    @patch('utils.ragflow_client.requests.delete')
    def test_ragflow_delete_session(self, mock_delete):
        """测试RAGFlow删除会话"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_response.status_code = 200
        mock_delete.return_value = mock_response
        
        from utils.ragflow_client import RAGFlowClient
        client = RAGFlowClient()
        result = client.delete_session("ragflow_session_123")
        
        assert result["success"] is True
        mock_delete.assert_called_once()
    
    @patch('utils.ragflow_client.requests.post')
    def test_ragflow_api_error_handling(self, mock_post):
        """测试RAGFlow API错误处理"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        from utils.ragflow_client import RAGFlowClient
        client = RAGFlowClient()
        
        with pytest.raises(Exception):
            client.create_session()
    
    @patch('utils.ragflow_client.requests.post')
    def test_ragflow_network_timeout(self, mock_post):
        """测试RAGFlow网络超时"""
        mock_post.side_effect = requests.exceptions.Timeout("Request timeout")
        
        from utils.ragflow_client import RAGFlowClient
        client = RAGFlowClient()
        
        with pytest.raises(requests.exceptions.Timeout):
            client.create_session()
    
    @patch('utils.ragflow_client.requests.post')
    def test_ragflow_retry_mechanism(self, mock_post):
        """测试RAGFlow重试机制"""
        # 第一次调用失败，第二次成功
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        
        mock_response_success = Mock()
        mock_response_success.json.return_value = {"session_id": "ragflow_session_123"}
        mock_response_success.status_code = 200
        
        mock_post.side_effect = [mock_response_fail, mock_response_success]
        
        from utils.ragflow_client import RAGFlowClient
        client = RAGFlowClient()
        result = client.create_session()
        
        assert result["session_id"] == "ragflow_session_123"
        assert mock_post.call_count == 2  # 重试了一次
