"""
RAGFlow API客户端
用于与RAGFlow服务进行交互，包括创建会话和对话功能
"""

import requests
import json
import os
import time
import logging
from typing import Dict, Any, Optional, Generator

# 导入配置
try:
    from config import config
    DEFAULT_CHAT_ID = config.RAGFLOW_CHAT_ID
    DEFAULT_BASE_URL = config.RAGFLOW_BASE_URL
    DEFAULT_API_KEY = config.RAGFLOW_API_KEY
except ImportError:
    DEFAULT_CHAT_ID = "63854abaabb511f0bf790ec84fa37cec"
    DEFAULT_BASE_URL = "http://localhost:9380"
    DEFAULT_API_KEY = "ragflow-ZkMzMwODc2YWM1YzExZjBhNGM1MGVjOD"

logger = logging.getLogger(__name__)


class RAGFlowClient:
    """RAGFlow API客户端"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        """
        初始化RAGFlow客户端
        
        Args:
            base_url: RAGFlow服务的基础URL，默认从配置获取
            api_key: API密钥，默认从配置获取
        """
        self.base_url = base_url or os.getenv('RAGFLOW_BASE_URL', DEFAULT_BASE_URL)
        self.api_key = api_key or os.getenv('RAGFLOW_API_KEY', DEFAULT_API_KEY)
        
        if not self.api_key:
            raise ValueError("RAGFlow API key is required. Set RAGFLOW_API_KEY environment variable.")
        
        # 确保base_url不以斜杠结尾
        self.base_url = self.base_url.rstrip('/')
        
        # 设置默认请求头
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        logger.info(f"RAGFlow客户端初始化完成: {self.base_url}")
    
    def _make_request(self, method: str, url: str, data: dict = None, max_retries: int = 3) -> Dict[str, Any]:
        """
        通用API请求方法
        
        Args:
            method: HTTP方法
            url: 请求URL
            data: 请求数据
            max_retries: 最大重试次数
            
        Returns:
            API响应数据
            
        Raises:
            requests.RequestException: 请求失败时抛出异常
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
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                response.raise_for_status()
                result = response.json()
                
                if result.get('code') != 0:
                    raise Exception(f"RAGFlow API error: {result.get('message', 'Unknown error')}")
                
                return result.get('data', {})
                
            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    logger.warning(f"API请求失败，第{attempt + 1}次重试: {str(e)}")
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                else:
                    raise Exception(f"API请求失败，已重试{max_retries}次: {str(e)}")
    
    def create_session(self, chat_id: str, name: str, user_id: str = None, max_retries: int = 3) -> Dict[str, Any]:
        """
        创建会话
        
        Args:
            chat_id: 聊天助手的ID
            name: 会话名称
            user_id: 可选的用户定义ID
            max_retries: 最大重试次数
            
        Returns:
            包含会话信息的字典
            
        Raises:
            requests.RequestException: 请求失败时抛出异常
        """
        url = f"{self.base_url}/api/v1/chats/{chat_id}/sessions"
        
        data = {"name": name}
        if user_id:
            data["user_id"] = user_id
        
        logger.info(f"创建RAGFlow会话: {name}")
        return self._make_request('POST', url, data, max_retries)
    
    def converse(self, chat_id: str, question: str, stream: bool = True, 
                 session_id: str = None, user_id: str = None) -> Dict[str, Any]:
        """
        与聊天助手对话（非流式）
        
        Args:
            chat_id: 聊天助手的ID
            question: 问题
            stream: 是否使用流式输出，默认为True但此方法返回完整响应
            session_id: 会话ID，如果不提供将创建新会话
            user_id: 可选的用户定义ID
            
        Returns:
            包含回答信息的字典
            
        Raises:
            requests.RequestException: 请求失败时抛出异常
        """
        url = f"{self.base_url}/api/v1/chats/{chat_id}/completions"
        
        data = {
            "question": question,
            "stream": False  # 非流式模式
        }
        
        if session_id:
            data["session_id"] = session_id
        if user_id:
            data["user_id"] = user_id
        
        logger.info(f"RAGFlow对话请求: {question[:50]}...")
        return self._make_request('POST', url, data)
    
    def converse_stream(self, chat_id: str, question: str, session_id: str = None, 
                       user_id: str = None) -> Generator[Dict[str, Any], None, None]:
        """
        与聊天助手对话（流式）
        
        Args:
            chat_id: 聊天助手的ID
            question: 问题
            session_id: 会话ID，如果不提供将创建新会话
            user_id: 可选的用户定义ID
            
        Yields:
            流式响应数据块
            
        Raises:
            requests.RequestException: 请求失败时抛出异常
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
                    
                    # 跳过SSE格式的data:前缀
                    if line_str.startswith('data:'):
                        line_str = line_str[5:].strip()
                    
                    if line_str:
                        try:
                            data_chunk = json.loads(line_str)
                            
                            if data_chunk.get('code') != 0:
                                raise Exception(f"RAGFlow API error: {data_chunk.get('message', 'Unknown error')}")
                            
                            yield data_chunk.get('data', {})
                            
                        except json.JSONDecodeError:
                            # 跳过无效的JSON行
                            continue
            
        except requests.RequestException as e:
            raise Exception(f"Failed to converse (stream): {str(e)}")
    
    def get_session_info(self, chat_id: str, session_id: str) -> Dict[str, Any]:
        """
        获取会话信息（如果RAGFlow提供此API）
        
        Args:
            chat_id: 聊天助手的ID
            session_id: 会话ID
            
        Returns:
            会话信息字典
        """
        # 注意：此方法假设RAGFlow提供获取会话信息的API
        # 如果实际API不同，需要相应调整
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
        删除RAGFlow会话
        
        Args:
            chat_id: 聊天助手的ID
            session_ids: 要删除的会话ID列表
            max_retries: 最大重试次数
            
        Returns:
            删除结果字典
            
        Raises:
            requests.RequestException: 请求失败时抛出异常
        """
        url = f"{self.base_url}/api/v1/chats/{chat_id}/sessions"
        data = {"ids": session_ids}
        
        logger.info(f"删除RAGFlow会话: {session_ids}")
        return self._make_request('DELETE', url, data, max_retries)
    
    def delete_session(self, chat_id: str, session_id: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        删除单个RAGFlow会话
        
        Args:
            chat_id: 聊天助手的ID
            session_id: 要删除的会话ID
            max_retries: 最大重试次数
            
        Returns:
            删除结果字典
        """
        return self.delete_sessions(chat_id, [session_id], max_retries)


# 便捷函数
def create_ragflow_client(base_url: str = None, api_key: str = None) -> RAGFlowClient:
    """
    创建RAGFlow客户端的便捷函数
    
    Args:
        base_url: RAGFlow服务的基础URL
        api_key: API密钥
        
    Returns:
        RAGFlowClient实例
    """
    return RAGFlowClient(base_url, api_key)


# 示例使用
if __name__ == "__main__":
    # 设置环境变量示例
    # os.environ['RAGFLOW_BASE_URL'] = 'http://localhost:9380'
    # os.environ['RAGFLOW_API_KEY'] = 'your_api_key_here'
    
    try:
        # 创建客户端
        client = create_ragflow_client()
        
        # 示例：创建会话
        chat_id = DEFAULT_CHAT_ID
        session_data = client.create_session(chat_id, "测试会话", "user123")
        print("创建会话成功:", session_data)
        
        # 示例：非流式对话
        answer = client.converse(chat_id, "你好，你是谁？", session_id=session_data.get('id'))
        print("对话回答:", answer)
        
        # 示例：流式对话
        print("流式对话:")
        for chunk in client.converse_stream(chat_id, "请介绍一下你的功能", session_id=session_data.get('id')):
            if isinstance(chunk, dict) and 'answer' in chunk:
                print(chunk['answer'], end='', flush=True)
            elif chunk is True:
                print("\n[对话结束]")
                break
        
    except Exception as e:
        print(f"错误: {e}")
