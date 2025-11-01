"""
RAGFlow API Client
For interacting with RAGFlow service, including session creation and conversation functions
"""

import requests
import json
import os
import time
import logging
from typing import Dict, Any, Optional, Generator

# Import configuration
try:
    from ..config import config
    DEFAULT_CHAT_ID = config.RAGFLOW_CHAT_ID
    DEFAULT_BASE_URL = config.RAGFLOW_BASE_URL
    DEFAULT_API_KEY = config.RAGFLOW_API_KEY
except ImportError:
    DEFAULT_CHAT_ID = "63854abaabb511f0bf790ec84fa37cec"
    DEFAULT_BASE_URL = "http://localhost:9380"
    DEFAULT_API_KEY = "ragflow-ZkMzMwODc2YWM1YzExZjBhNGM1MGVjOD"

logger = logging.getLogger(__name__)


class RAGFlowClient:
    """RAGFlow API Client"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        """
        Initialize RAGFlow client
        
        Args:
            base_url: RAGFlow service base URL, defaults to config value
            api_key: API key, defaults to config value
        """
        # Priority: environment variables, then parameters, finally default values
        self.base_url = base_url or os.getenv('RAGFLOW_BASE_URL') or DEFAULT_BASE_URL
        self.api_key = api_key or os.getenv('RAGFLOW_API_KEY') or DEFAULT_API_KEY
        
        if not self.api_key:
            raise ValueError("RAGFlow API key is required. Set RAGFLOW_API_KEY environment variable.")
        
        # Ensure base_url doesn't end with slash
        self.base_url = self.base_url.rstrip('/')
        
        # Set default request headers
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        logger.info(f"RAGFlow client initialized: {self.base_url}")
    
    def _make_request(self, method: str, url: str, data: dict = None, max_retries: int = 3) -> Dict[str, Any]:
        """
        Generic API request method
        
        Args:
            method: HTTP method
            url: Request URL
            data: Request data
            max_retries: Maximum retry count
            
        Returns:
            API response data
            
        Raises:
            requests.RequestException: Raises exception when request fails
        """
        for attempt in range(max_retries):
            try:
                if method.upper() == 'GET':
                    response = requests.get(url, headers=self.headers, timeout=30)
                elif method.upper() == 'POST':
                    response = requests.post(url, headers=self.headers, json=data, timeout=30)
                elif method.upper() == 'DELETE':
                    response = requests.delete(url, headers=self.headers, json=data, timeout=30)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                result = response.json()
                
                if result.get('code') != 0:
                    raise Exception(f"RAGFlow API error: {result.get('message', 'Unknown error')}")
                
                return result.get('data', {})
                
            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    logger.warning(f"API request failed, retry {attempt + 1}: {str(e)}")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    raise Exception(f"API request failed after {max_retries} retries: {str(e)}")
    
    def create_session(self, chat_id: str, name: str, user_id: str = None, max_retries: int = 3) -> Dict[str, Any]:
        """
        Create session
        
        Args:
            chat_id: Chat assistant ID
            name: Session name
            user_id: Optional user-defined ID
            max_retries: Maximum retry count
            
        Returns:
            Dictionary containing session information
            
        Raises:
            requests.RequestException: Raises exception when request fails
        """
        url = f"{self.base_url}/api/v1/chats/{chat_id}/sessions"
        
        data = {"name": name}
        if user_id:
            data["user_id"] = user_id
        
        logger.info(f"Creating RAGFlow session: {name}")
        return self._make_request('POST', url, data, max_retries)
    
    def converse(self, chat_id: str, question: str, stream: bool = True, 
                 session_id: str = None, user_id: str = None) -> Dict[str, Any]:
        """
        Converse with chat assistant (non-streaming)
        
        Args:
            chat_id: Chat assistant ID
            question: Question
            stream: Whether to use streaming output, default is True but this method returns complete response
            session_id: Session ID, will create new session if not provided
            user_id: Optional user-defined ID
            
        Returns:
            Dictionary containing answer information
            
        Raises:
            requests.RequestException: Raises exception when request fails
        """
        url = f"{self.base_url}/api/v1/chats/{chat_id}/completions"
        
        data = {
            "question": question,
            "stream": False  # Non-streaming mode
        }
        
        if session_id:
            data["session_id"] = session_id
        if user_id:
            data["user_id"] = user_id
        
        logger.info(f"RAGFlow conversation request: {question[:50]}...")
        return self._make_request('POST', url, data)
    
    def converse_stream(self, chat_id: str, question: str, session_id: str = None, 
                       user_id: str = None) -> Generator[Dict[str, Any], None, None]:
        """
        Converse with chat assistant (streaming)
        
        Args:
            chat_id: Chat assistant ID
            question: Question
            session_id: Session ID, will create new session if not provided
            user_id: Optional user-defined ID
            
        Yields:
            Streaming response data chunks
            
        Raises:
            requests.RequestException: Raises exception when request fails
        """
        url = f"{self.base_url}/api/v1/chats/{chat_id}/completions"
        
        data = {
            "question": question,
            "stream": True
        }
        
        if session_id:
            data["session_id"] = session_id
        if user_id:
            data["user_id"] = user_id
        
        try:
            response = requests.post(url, headers=self.headers, json=data, stream=True)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    
                    # Skip SSE format data: prefix
                    if line_str.startswith('data:'):
                        line_str = line_str[5:].strip()
                    
                    if line_str:
                        try:
                            data_chunk = json.loads(line_str)
                            
                            if data_chunk.get('code') != 0:
                                raise Exception(f"RAGFlow API error: {data_chunk.get('message', 'Unknown error')}")
                            
                            yield data_chunk.get('data', {})
                            
                        except json.JSONDecodeError:
                            # Skip invalid JSON lines
                            continue
            
        except requests.RequestException as e:
            raise Exception(f"Failed to converse (stream): {str(e)}")
    
    def get_session_info(self, chat_id: str, session_id: str) -> Dict[str, Any]:
        """
        Get session information (if RAGFlow provides this API)
        
        Args:
            chat_id: Chat assistant ID
            session_id: Session ID
            
        Returns:
            Session information dictionary
        """
        # Note: This method assumes RAGFlow provides an API to get session information
        # If the actual API differs, adjust accordingly
        url = f"{self.base_url}/api/v1/chats/{chat_id}/sessions/{session_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('code') != 0:
                raise Exception(f"RAGFlow API error: {result.get('message', 'Unknown error')}")
            
            return result.get('data', {})
            
        except requests.RequestException as e:
            raise Exception(f"Failed to get session info: {str(e)}")
    
    def delete_sessions(self, chat_id: str, session_ids: list, max_retries: int = 3) -> Dict[str, Any]:
        """
        Delete RAGFlow sessions
        
        Args:
            chat_id: Chat assistant ID
            session_ids: List of session IDs to delete
            max_retries: Maximum retry count
            
        Returns:
            Deletion result dictionary
            
        Raises:
            requests.RequestException: Raises exception when request fails
        """
        url = f"{self.base_url}/api/v1/chats/{chat_id}/sessions"
        data = {"ids": session_ids}
        
        logger.info(f"Deleting RAGFlow sessions: {session_ids}")
        return self._make_request('DELETE', url, data, max_retries)
    
    def delete_session(self, chat_id: str, session_id: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Delete a single RAGFlow session
        
        Args:
            chat_id: Chat assistant ID
            session_id: Session ID to delete
            max_retries: Maximum retry count
            
        Returns:
            Deletion result dictionary
        """
        return self.delete_sessions(chat_id, [session_id], max_retries)
    
    def list_sessions(self, chat_id: str, page: int = 1, page_size: int = 1000) -> list:
        """
        Get all sessions for specified chat
        
        Args:
            chat_id: Chat assistant ID
            page: Page number, starting from 1
            page_size: Number per page, default 1000 (get all)
            
        Returns:
            Session list or empty list
        """
        url = f"{self.base_url}/api/v1/chats/{chat_id}/sessions"
        params = {
            "page": page,
            "page_size": page_size
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 0:
                data = result.get('data', [])
                # RAGFlow API may return list or dict, handle uniformly
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return data.get('items', [])
                else:
                    return []
            else:
                logger.error(f"Failed to get session list: {result.get('message')}")
                return []
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to request session list: {e}")
            return []
    
    def list_chats(self, page: int = 1, page_size: int = 30, orderby: str = "create_time", desc: bool = True):
        """
        Get chat assistant list
        
        Args:
            page: Page number, starting from 1
            page_size: Number per page
            orderby: Sort field
            desc: Whether descending order
            
        Returns:
            Chat assistant list or empty list
        """
        url = f"{self.base_url}/api/v1/chats"
        params = {
            "page": page,
            "page_size": page_size,
            "orderby": orderby,
            "desc": desc
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 0:
                data = result.get('data', [])
                # RAGFlow API may return list or dict, handle uniformly
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return data.get('items', [])
                else:
                    return []
            else:
                logger.error(f"Failed to get chat assistant list: {result.get('message')}")
                return []
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to request chat assistant list: {e}")
            return []


# Convenience function
def create_ragflow_client(base_url: str = None, api_key: str = None) -> RAGFlowClient:
    """
    Convenience function to create RAGFlow client
    
    Args:
        base_url: RAGFlow service base URL
        api_key: API key
        
    Returns:
        RAGFlowClient instance
    """
    return RAGFlowClient(base_url, api_key)


# Example usage
if __name__ == "__main__":
    # Set environment variable example
    # os.environ['RAGFLOW_BASE_URL'] = 'http://localhost:9380'
    # os.environ['RAGFLOW_API_KEY'] = 'your_api_key_here'
    
    try:
        # Create client
        client = create_ragflow_client()
        
        # Example: Create session
        chat_id = DEFAULT_CHAT_ID
        session_data = client.create_session(chat_id, "Test Session", "user123")
        print("Session created successfully:", session_data)
        
        # Example: Non-streaming conversation
        answer = client.converse(chat_id, "Hello, who are you?", session_id=session_data.get('id'))
        print("Conversation answer:", answer)
        
        # Example: Streaming conversation
        print("Streaming conversation:")
        for chunk in client.converse_stream(chat_id, "Please introduce your features", session_id=session_data.get('id')):
            if isinstance(chunk, dict) and 'answer' in chunk:
                print(chunk['answer'], end='', flush=True)
            elif chunk is True:
                print("\n[Conversation ended]")
                break
        
    except Exception as e:
        print(f"Error: {e}")
