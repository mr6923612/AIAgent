#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话管理测试用例
测试会话的创建、删除、RAGFlow集成等功能
"""

import sys
import os
import time
import requests
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.sessionManager import SessionManager
from utils.ragflow_client import create_ragflow_client, DEFAULT_CHAT_ID
from scripts.test_cleanup import register_test_session, cleanup_test_sessions

class SessionManagementTest:
    """会话管理测试类"""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.ragflow_client = None
        self.test_sessions = []
        self.base_url = "http://localhost:8012"
        
    def setup(self):
        """测试前准备"""
        print("🔧 测试前准备...")
        
        # 初始化RAGFlow客户端
        try:
            self.ragflow_client = create_ragflow_client()
            print("✅ RAGFlow客户端初始化成功")
        except Exception as e:
            print(f"⚠️ RAGFlow客户端初始化失败: {e}")
            self.ragflow_client = None
    
    def teardown(self):
        """测试后清理"""
        print("🧹 测试后清理...")
        cleanup_test_sessions()
        print("✅ 测试清理完成")
    
    def test_create_session(self):
        """测试创建会话"""
        print("\n🧪 测试创建会话...")
        
        try:
            # 创建会话
            session = self.session_manager.create_session(
                user_id="test_user",
                title="测试会话",
                ragflow_client=self.ragflow_client
            )
            
            # 注册测试会话
            register_test_session(session.session_id, session.ragflow_session_id)
            
            # 验证会话创建
            assert session.session_id is not None
            assert session.user_id == "test_user"
            assert session.title == "测试会话"
            
            print(f"✅ 会话创建成功: {session.session_id}")
            print(f"✅ RAGFlow会话ID: {session.ragflow_session_id}")
            
            return session
            
        except Exception as e:
            print(f"❌ 创建会话失败: {e}")
            raise
    
    def test_create_session_via_api(self):
        """测试通过API创建会话"""
        print("\n🧪 测试通过API创建会话...")
        
        try:
            # 通过API创建会话
            response = requests.post(
                f"{self.base_url}/api/sessions",
                json={
                    "user_id": "test_api_user",
                    "title": "API测试会话"
                },
                timeout=10
            )
            
            assert response.status_code == 201
            session_data = response.json()
            
            # 注册测试会话
            register_test_session(session_data['session_id'], session_data.get('ragflow_session_id'))
            
            # 验证响应数据
            assert 'session_id' in session_data
            assert 'title' in session_data
            assert 'created_at' in session_data
            
            print(f"✅ API会话创建成功: {session_data['session_id']}")
            print(f"✅ RAGFlow会话ID: {session_data.get('ragflow_session_id')}")
            
            return session_data
            
        except Exception as e:
            print(f"❌ API创建会话失败: {e}")
            raise
    
    def test_get_session(self):
        """测试获取会话"""
        print("\n🧪 测试获取会话...")
        
        try:
            # 先创建一个会话
            session = self.test_create_session()
            session_id = session.session_id
            
            # 获取会话
            retrieved_session = self.session_manager.get_session(session_id)
            
            # 验证会话数据
            assert retrieved_session is not None
            assert retrieved_session.session_id == session_id
            assert retrieved_session.user_id == "test_user"
            assert retrieved_session.title == "测试会话"
            
            print(f"✅ 会话获取成功: {session_id}")
            
        except Exception as e:
            print(f"❌ 获取会话失败: {e}")
            raise
    
    def test_add_message(self):
        """测试添加消息"""
        print("\n🧪 测试添加消息...")
        
        try:
            # 先创建一个会话
            session = self.test_create_session()
            session_id = session.session_id
            
            # 添加用户消息
            user_message = self.session_manager.add_message(
                session_id, "user", "你好，这是一个测试消息"
            )
            
            assert user_message is not None
            assert user_message.role == "user"
            assert user_message.content == "你好，这是一个测试消息"
            
            # 添加助手消息
            assistant_message = self.session_manager.add_message(
                session_id, "assistant", "你好！我是智能客服，很高兴为您服务。"
            )
            
            assert assistant_message is not None
            assert assistant_message.role == "assistant"
            
            # 验证会话中的消息
            updated_session = self.session_manager.get_session(session_id)
            assert len(updated_session.messages) == 2
            
            print(f"✅ 消息添加成功: 用户消息 + 助手消息")
            
        except Exception as e:
            print(f"❌ 添加消息失败: {e}")
            raise
    
    def test_delete_session(self):
        """测试删除会话"""
        print("\n🧪 测试删除会话...")
        
        try:
            # 先创建一个会话
            session = self.test_create_session()
            session_id = session.session_id
            
            # 删除会话
            success = self.session_manager.delete_session(session_id, self.ragflow_client)
            
            assert success is True
            
            # 验证会话已删除
            deleted_session = self.session_manager.get_session(session_id)
            assert deleted_session is None
            
            print(f"✅ 会话删除成功: {session_id}")
            
        except Exception as e:
            print(f"❌ 删除会话失败: {e}")
            raise
    
    def test_delete_session_via_api(self):
        """测试通过API删除会话"""
        print("\n🧪 测试通过API删除会话...")
        
        try:
            # 先通过API创建一个会话
            session_data = self.test_create_session_via_api()
            session_id = session_data['session_id']
            
            # 通过API删除会话
            response = requests.delete(f"{self.base_url}/api/sessions/{session_id}")
            
            assert response.status_code == 200
            
            # 验证会话已删除
            get_response = requests.get(f"{self.base_url}/api/sessions/{session_id}")
            assert get_response.status_code == 404
            
            print(f"✅ API会话删除成功: {session_id}")
            
        except Exception as e:
            print(f"❌ API删除会话失败: {e}")
            raise
    
    def test_ragflow_integration(self):
        """测试RAGFlow集成"""
        print("\n🧪 测试RAGFlow集成...")
        
        if not self.ragflow_client:
            print("⚠️ 跳过RAGFlow集成测试（客户端未初始化）")
            return
        
        try:
            # 创建会话（包含RAGFlow会话）
            session = self.session_manager.create_session(
                user_id="test_ragflow_user",
                title="RAGFlow测试会话",
                ragflow_client=self.ragflow_client
            )
            
            # 注册测试会话
            register_test_session(session.session_id, session.ragflow_session_id)
            
            # 验证RAGFlow会话ID存在
            assert session.ragflow_session_id is not None
            print(f"✅ RAGFlow会话创建成功: {session.ragflow_session_id}")
            
            # 测试RAGFlow对话
            try:
                answer_data = self.ragflow_client.converse(
                    chat_id=DEFAULT_CHAT_ID,
                    question="你好，请介绍一下你的功能",
                    session_id=session.ragflow_session_id
                )
                
                assert answer_data is not None
                print(f"✅ RAGFlow对话测试成功")
                
            except Exception as e:
                print(f"⚠️ RAGFlow对话测试失败: {e}")
            
        except Exception as e:
            print(f"❌ RAGFlow集成测试失败: {e}")
            raise
    
    def test_multiple_sessions(self):
        """测试多个会话管理"""
        print("\n🧪 测试多个会话管理...")
        
        try:
            # 创建多个会话
            sessions = []
            for i in range(3):
                session = self.session_manager.create_session(
                    user_id=f"test_multi_user_{i}",
                    title=f"多会话测试_{i}",
                    ragflow_client=self.ragflow_client
                )
                sessions.append(session)
                register_test_session(session.session_id, session.ragflow_session_id)
            
            # 验证会话创建
            assert len(sessions) == 3
            
            # 获取用户的所有会话
            user_sessions = self.session_manager.get_user_sessions("test_multi_user_0")
            assert len(user_sessions) >= 1
            
            print(f"✅ 多会话管理测试成功: 创建了 {len(sessions)} 个会话")
            
        except Exception as e:
            print(f"❌ 多会话管理测试失败: {e}")
            raise
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始会话管理测试...")
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            self.setup()
            
            # 运行测试用例
            self.test_create_session()
            self.test_create_session_via_api()
            self.test_get_session()
            self.test_add_message()
            self.test_delete_session()
            self.test_delete_session_via_api()
            self.test_ragflow_integration()
            self.test_multiple_sessions()
            
            print("\n🎉 所有测试用例通过！")
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            raise
            
        finally:
            self.teardown()

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='会话管理测试')
    parser.add_argument('--test', choices=[
        'create', 'get', 'add_message', 'delete', 'api_create', 'api_delete', 
        'ragflow', 'multiple', 'all'
    ], default='all', help='指定要运行的测试')
    
    args = parser.parse_args()
    
    tester = SessionManagementTest()
    
    try:
        tester.setup()
        
        if args.test == 'all':
            tester.run_all_tests()
        elif args.test == 'create':
            tester.test_create_session()
        elif args.test == 'get':
            tester.test_get_session()
        elif args.test == 'add_message':
            tester.test_add_message()
        elif args.test == 'delete':
            tester.test_delete_session()
        elif args.test == 'api_create':
            tester.test_create_session_via_api()
        elif args.test == 'api_delete':
            tester.test_delete_session_via_api()
        elif args.test == 'ragflow':
            tester.test_ragflow_integration()
        elif args.test == 'multiple':
            tester.test_multiple_sessions()
        
        print(f"\n✅ 测试 {args.test} 完成")
        
    except Exception as e:
        print(f"\n❌ 测试 {args.test} 失败: {e}")
        return 1
        
    finally:
        tester.teardown()
    
    return 0

if __name__ == "__main__":
    exit(main())
