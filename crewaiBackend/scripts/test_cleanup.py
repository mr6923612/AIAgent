#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用例清理工具
确保测试用例在完成后清理所有会话
"""

import sys
import os
import time
from datetime import datetime

# 设置编码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.sessionManager import SessionManager
from utils.ragflow_client import create_ragflow_client, DEFAULT_CHAT_ID

class TestSessionCleaner:
    """测试会话清理器"""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.ragflow_client = None
        self.test_sessions = []
        
    def init_ragflow_client(self):
        """初始化RAGFlow客户端"""
        try:
            self.ragflow_client = create_ragflow_client()
            return True
        except Exception as e:
            print(f"⚠️ RAGFlow客户端初始化失败: {e}")
            return False
    
    def register_test_session(self, session_id, ragflow_session_id=None):
        """注册测试会话"""
        self.test_sessions.append({
            'session_id': session_id,
            'ragflow_session_id': ragflow_session_id,
            'created_at': datetime.now()
        })
    
    def cleanup_test_sessions(self):
        """清理所有测试会话"""
        if not self.test_sessions:
            print("ℹ️ 没有测试会话需要清理")
            return
        
        print(f"🧹 开始清理 {len(self.test_sessions)} 个测试会话...")
        
        # 初始化RAGFlow客户端
        if not self.ragflow_client:
            self.init_ragflow_client()
        
        cleaned_count = 0
        failed_count = 0
        
        for session_info in self.test_sessions:
            try:
                session_id = session_info['session_id']
                ragflow_session_id = session_info.get('ragflow_session_id')
                
                print(f"🗑️ 清理测试会话: {session_id}")
                
                # 删除会话
                success = self.session_manager.delete_session(session_id, self.ragflow_client)
                
                if success:
                    cleaned_count += 1
                    print(f"✅ 测试会话清理成功: {session_id}")
                else:
                    failed_count += 1
                    print(f"❌ 测试会话清理失败: {session_id}")
                    
            except Exception as e:
                failed_count += 1
                print(f"❌ 清理测试会话异常: {e}")
        
        print(f"📊 测试会话清理完成: 成功 {cleaned_count}, 失败 {failed_count}")
        
        # 清空测试会话列表
        self.test_sessions.clear()
    
    def cleanup_all_sessions(self):
        """清理所有会话（包括非测试会话）"""
        print("🧹 清理所有会话...")
        
        try:
            # 获取所有会话
            all_sessions = self.session_manager.get_all_sessions()
            print(f"📊 找到 {len(all_sessions)} 个会话")
            
            if not all_sessions:
                print("ℹ️ 没有会话需要清理")
                return
            
            # 初始化RAGFlow客户端
            if not self.ragflow_client:
                self.init_ragflow_client()
            
            cleaned_count = 0
            failed_count = 0
            
            for session in all_sessions:
                try:
                    session_id = session.session_id
                    print(f"🗑️ 清理会话: {session_id}")
                    
                    success = self.session_manager.delete_session(session_id, self.ragflow_client)
                    
                    if success:
                        cleaned_count += 1
                        print(f"✅ 会话清理成功: {session_id}")
                    else:
                        failed_count += 1
                        print(f"❌ 会话清理失败: {session_id}")
                        
                except Exception as e:
                    failed_count += 1
                    print(f"❌ 清理会话异常: {e}")
            
            print(f"📊 会话清理完成: 成功 {cleaned_count}, 失败 {failed_count}")
            
        except Exception as e:
            print(f"❌ 清理所有会话失败: {e}")

# 全局测试清理器实例
test_cleaner = TestSessionCleaner()

def register_test_session(session_id, ragflow_session_id=None):
    """注册测试会话（供测试用例使用）"""
    test_cleaner.register_test_session(session_id, ragflow_session_id)

def cleanup_test_sessions():
    """清理测试会话（供测试用例使用）"""
    test_cleaner.cleanup_test_sessions()

def cleanup_all_sessions():
    """清理所有会话（供测试用例使用）"""
    test_cleaner.cleanup_all_sessions()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='测试会话清理工具')
    parser.add_argument('--all', action='store_true', help='清理所有会话')
    parser.add_argument('--test-only', action='store_true', help='只清理测试会话')
    
    args = parser.parse_args()
    
    if args.all:
        cleanup_all_sessions()
    elif args.test_only:
        cleanup_test_sessions()
    else:
        print("请指定 --all 或 --test-only 参数")
        print("  --all: 清理所有会话")
        print("  --test-only: 只清理测试会话")
