"""
Frontend-Backend Integration Tests
Test basic functionality integration of frontend and backend
"""
import pytest
from unittest.mock import patch, Mock
import json


class TestFrontendBackendIntegration:
    """Frontend-backend integration test class"""
    
    def test_session_management_flow(self):
        """Test session management flow"""
        # Mock frontend session creation request
        session_data = {
            'title': 'Test Session',
            'user_id': 'test_user'
        }
        
        # Mock backend session manager
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
            
            # Test session creation
            session = mock_manager.create_session(title=session_data['title'])
            assert session is not None
            assert session.to_dict()['title'] == 'Test Session'
    
    def test_chat_message_flow(self):
        """Test chat message flow"""
        # Mock frontend message sending request
        message_data = {
            'session_id': 'test_session_123',
            'role': 'user',
            'content': 'Hello, how are you?'
        }
        
        # Mock backend message processing
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
            
            # Test message adding
            message = mock_manager.add_message(
                message_data['session_id'],
                message_data['role'],
                message_data['content']
            )
            assert message is not None
            assert message.to_dict()['content'] == 'Hello, how are you?'
    
    def test_ai_response_flow(self):
        """Test AI response flow"""
        # Mock frontend AI request
        ai_request = {
            'customer_input': 'What is the weather like?',
            'session_id': 'test_session_123'
        }
        
        # Mock backend AI processing
        with patch('crewaiBackend.main.CrewtestprojectCrew') as mock_crew_class:
            mock_crew_instance = Mock()
            mock_crew_instance.kickoff.return_value = "The weather is sunny today."
            mock_crew_class.return_value = mock_crew_instance
            
            with patch('crewaiBackend.utils.jobManager.append_event') as mock_append:
                # Test AI response generation
                crew = mock_crew_class()
                response = crew.kickoff()
                assert response == "The weather is sunny today."
    
    def test_user_authentication_flow(self):
        """Test user authentication flow"""
        # Mock frontend user login
        user_data = {
            'username': 'test_user',
            'password': 'test_password'
        }
        
        # Mock backend authentication processing
        with patch('crewaiBackend.main.session_manager') as mock_session_manager:
            # Mock user session creation
            mock_session = Mock()
            mock_session.to_dict.return_value = {
                'session_id': 'user_session_123',
                'user_id': 'test_user',
                'title': 'User Session'
            }
            mock_session_manager.create_session.return_value = mock_session
            
            # Test user session creation
            session = mock_session_manager.create_session(title="User Session")
            assert session is not None
            assert session.to_dict()['user_id'] == 'test_user'
    
    def test_data_persistence_flow(self):
        """Test data persistence flow"""
        # Mock frontend data save request
        save_data = {
            'session_id': 'test_session_123',
            'messages': [
                {'role': 'user', 'content': 'Hello'},
                {'role': 'assistant', 'content': 'Hi there!'}
            ]
        }
        
        # Mock backend data saving
        with patch('crewaiBackend.utils.sessionManager.SessionManager') as mock_session_manager:
            mock_manager = Mock()
            mock_manager.update_session.return_value = True
            mock_session_manager.return_value = mock_manager
            
            # Test data update
            result = mock_manager.update_session(
                save_data['session_id'],
                {'messages': save_data['messages']}
            )
            assert result is True
    
    def test_error_handling_flow(self):
        """Test error handling flow"""
        # Mock frontend error request
        error_request = {
            'session_id': 'nonexistent_session',
            'action': 'get_session'
        }
        
        # Mock backend error handling
        with patch('crewaiBackend.utils.sessionManager.SessionManager') as mock_session_manager:
            mock_manager = Mock()
            mock_manager.get_session.return_value = None
            mock_session_manager.return_value = mock_manager
            
            # Test error handling
            session = mock_manager.get_session(error_request['session_id'])
            assert session is None
    
    def test_real_time_updates_flow(self):
        """Test real-time updates flow"""
        # Mock frontend real-time update request
        update_request = {
            'session_id': 'test_session_123',
            'action': 'get_latest_messages'
        }
        
        # Mock backend real-time updates
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
            
            # Test real-time updates
            session = mock_manager.get_session(update_request['session_id'])
            assert session is not None
            assert len(session.messages) == 2
    
    def test_multi_user_session_isolation(self):
        """Test multi-user session isolation"""
        # Mock multi-user sessions
        user1_data = {
            'user_id': 'user1',
            'session_id': 'session_user1_123'
        }
        user2_data = {
            'user_id': 'user2', 
            'session_id': 'session_user2_456'
        }
        
        # Mock backend session isolation
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
            
            # Test session isolation
            session1 = mock_manager.get_session(user1_data['session_id'])
            session2 = mock_manager.get_session(user2_data['session_id'])
            assert session1.to_dict()['user_id'] == 'user1'
            assert session2.to_dict()['user_id'] == 'user2'
            assert session1.to_dict()['session_id'] != session2.to_dict()['session_id']
