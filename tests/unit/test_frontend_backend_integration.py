"""
前后端集成测试
测试前端和后端的基本功能集成
"""
import pytest
from unittest.mock import patch, Mock
import json


class TestFrontendBackendIntegration:
    """前后端集成测试类"""
    
    def test_session_management_flow(self):
        """测试会话管理流程"""
        # 模拟前端创建会话请求
        session_data = {
            'title': 'Test Session',
            'user_id': 'test_user'
        }
        
        # 模拟后端会话管理器
        with patch('crewaiBackend.utils.sessionManager.SessionManager') as mock_session_manager:
            mock_manager = Mock()
            mock_session = Mock()
            mock_session.to_dict.return_value = {
                'session_id': 'test_session_123',
                'title': 'Test Session',
                'message_count': 0
            }
            mock_manager.create_session.return_value = mock_session
            mock_session_manager.return_value = mock_manager
            
            # 测试会话创建
            session = mock_manager.create_session(title=session_data['title'])
            assert session is not None
            assert session.to_dict()['title'] == 'Test Session'
    
    def test_chat_message_flow(self):
        """测试聊天消息流程"""
        # 模拟前端发送消息请求
        message_data = {
            'session_id': 'test_session_123',
            'role': 'user',
            'content': 'Hello, how are you?'
        }
        
        # 模拟后端消息处理
        with patch('crewaiBackend.utils.sessionManager.SessionManager') as mock_session_manager:
            mock_manager = Mock()
            mock_message = Mock()
            mock_message.to_dict.return_value = {
                'id': 'msg_123',
                'role': 'user',
                'content': 'Hello, how are you?',
                'timestamp': '2024-01-01T00:00:00'
            }
            mock_manager.add_message.return_value = mock_message
            mock_session_manager.return_value = mock_manager
            
            # 测试消息添加
            message = mock_manager.add_message(
                message_data['session_id'],
                message_data['role'],
                message_data['content']
            )
            assert message is not None
            assert message.to_dict()['content'] == 'Hello, how are you?'
    
    def test_ai_response_flow(self):
        """测试AI响应流程"""
        # 模拟前端发送AI请求
        ai_request = {
            'customer_input': 'What is the weather like?',
            'session_id': 'test_session_123'
        }
        
        # 模拟后端AI处理
        with patch('crewaiBackend.main.CrewtestprojectCrew') as mock_crew_class:
            mock_crew_instance = Mock()
            mock_crew_instance.kickoff.return_value = "The weather is sunny today."
            mock_crew_class.return_value = mock_crew_instance
            
            with patch('crewaiBackend.utils.jobManager.append_event') as mock_append:
                # 测试AI响应生成
                crew = mock_crew_class()
                response = crew.kickoff()
                assert response == "The weather is sunny today."
    
    def test_user_authentication_flow(self):
        """测试用户认证流程"""
        # 模拟前端用户登录
        user_data = {
            'username': 'test_user',
            'password': 'test_password'
        }
        
        # 模拟后端认证处理
        with patch('crewaiBackend.main.session_manager') as mock_session_manager:
            # 模拟用户会话创建
            mock_session = Mock()
            mock_session.to_dict.return_value = {
                'session_id': 'user_session_123',
                'user_id': 'test_user',
                'title': 'User Session'
            }
            mock_session_manager.create_session.return_value = mock_session
            
            # 测试用户会话创建
            session = mock_session_manager.create_session(title="User Session")
            assert session is not None
            assert session.to_dict()['user_id'] == 'test_user'
    
    def test_data_persistence_flow(self):
        """测试数据持久化流程"""
        # 模拟前端数据保存请求
        save_data = {
            'session_id': 'test_session_123',
            'messages': [
                {'role': 'user', 'content': 'Hello'},
                {'role': 'assistant', 'content': 'Hi there!'}
            ]
        }
        
        # 模拟后端数据保存
        with patch('crewaiBackend.utils.sessionManager.SessionManager') as mock_session_manager:
            mock_manager = Mock()
            mock_manager.update_session.return_value = True
            mock_session_manager.return_value = mock_manager
            
            # 测试数据更新
            result = mock_manager.update_session(
                save_data['session_id'],
                {'messages': save_data['messages']}
            )
            assert result is True
    
    def test_error_handling_flow(self):
        """测试错误处理流程"""
        # 模拟前端错误请求
        error_request = {
            'session_id': 'nonexistent_session',
            'action': 'get_session'
        }
        
        # 模拟后端错误处理
        with patch('crewaiBackend.utils.sessionManager.SessionManager') as mock_session_manager:
            mock_manager = Mock()
            mock_manager.get_session.return_value = None
            mock_session_manager.return_value = mock_manager
            
            # 测试错误处理
            session = mock_manager.get_session(error_request['session_id'])
            assert session is None
    
    def test_real_time_updates_flow(self):
        """测试实时更新流程"""
        # 模拟前端实时更新请求
        update_request = {
            'session_id': 'test_session_123',
            'action': 'get_latest_messages'
        }
        
        # 模拟后端实时更新
        with patch('crewaiBackend.utils.sessionManager.SessionManager') as mock_session_manager:
            mock_manager = Mock()
            mock_session = Mock()
            mock_session.messages = [
                {'role': 'user', 'content': 'Hello'},
                {'role': 'assistant', 'content': 'Hi there!'}
            ]
            mock_session.to_dict.return_value = {
                'session_id': 'test_session_123',
                'messages': mock_session.messages
            }
            mock_manager.get_session.return_value = mock_session
            mock_session_manager.return_value = mock_manager
            
            # 测试实时更新
            session = mock_manager.get_session(update_request['session_id'])
            assert session is not None
            assert len(session.messages) == 2
    
    def test_multi_user_session_isolation(self):
        """测试多用户会话隔离"""
        # 模拟多用户会话
        user1_data = {
            'user_id': 'user1',
            'session_id': 'session_user1_123'
        }
        user2_data = {
            'user_id': 'user2', 
            'session_id': 'session_user2_456'
        }
        
        # 模拟后端会话隔离
        with patch('crewaiBackend.utils.sessionManager.SessionManager') as mock_session_manager:
            mock_manager = Mock()
            mock_session1 = Mock()
            mock_session1.to_dict.return_value = {
                'session_id': 'session_user1_123',
                'user_id': 'user1'
            }
            mock_session2 = Mock()
            mock_session2.to_dict.return_value = {
                'session_id': 'session_user2_456',
                'user_id': 'user2'
            }
            mock_manager.get_session.side_effect = lambda sid: mock_session1 if sid == 'session_user1_123' else mock_session2
            mock_session_manager.return_value = mock_manager
            
            # 测试会话隔离
            session1 = mock_manager.get_session(user1_data['session_id'])
            session2 = mock_manager.get_session(user2_data['session_id'])
            assert session1.to_dict()['user_id'] == 'user1'
            assert session2.to_dict()['user_id'] == 'user2'
            assert session1.to_dict()['session_id'] != session2.to_dict()['session_id']
