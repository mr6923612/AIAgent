#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话清理工具
清理所有前端会话和RAGFlow会话
"""

import sys
import os
import json
import requests
import time
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from utils.sessionManager import SessionManager
from utils.ragflow_client import create_ragflow_client, DEFAULT_CHAT_ID

class SessionCleaner:
    """会话清理器"""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.ragflow_client = None
        self.cleaned_sessions = []
        self.failed_sessions = []
        
    def init_ragflow_client(self):
        """初始化RAGFlow客户端"""
        try:
            self.ragflow_client = create_ragflow_client()
            print("✅ RAGFlow客户端初始化成功")
            return True
        except Exception as e:
            print(f"❌ RAGFlow客户端初始化失败: {e}")
            return False
    
    def get_all_local_sessions(self):
        """获取所有本地会话"""
        try:
            sessions = self.session_manager.get_all_sessions()
            print(f"📊 找到 {len(sessions)} 个本地会话")
            return sessions
        except Exception as e:
            print(f"❌ 获取本地会话失败: {e}")
            return []
    
    def get_ragflow_sessions(self):
        """获取RAGFlow会话列表（如果API支持）"""
        if not self.ragflow_client:
            return []
        
        try:
            # 注意：这里假设RAGFlow有获取会话列表的API
            # 如果实际API不同，需要调整
            print("📊 获取RAGFlow会话列表...")
            # 由于RAGFlow可能没有直接的会话列表API，我们返回空列表
            # 实际实现可能需要通过其他方式获取
            return []
        except Exception as e:
            print(f"⚠️ 获取RAGFlow会话列表失败: {e}")
            return []
    
    def clean_local_sessions(self, sessions):
        """清理本地会话"""
        print("\n🧹 开始清理本地会话...")
        
        for session in sessions:
            try:
                session_id = session.session_id
                ragflow_session_id = getattr(session, 'ragflow_session_id', None)
                
                print(f"🗑️ 删除会话: {session_id}")
                
                # 删除本地会话（会自动删除RAGFlow会话）
                success = self.session_manager.delete_session(session_id, self.ragflow_client)
                
                if success:
                    self.cleaned_sessions.append({
                        'type': 'local',
                        'session_id': session_id,
                        'ragflow_session_id': ragflow_session_id,
                        'status': 'success'
                    })
                    print(f"✅ 会话删除成功: {session_id}")
                else:
                    self.failed_sessions.append({
                        'type': 'local',
                        'session_id': session_id,
                        'status': 'failed',
                        'error': '删除失败'
                    })
                    print(f"❌ 会话删除失败: {session_id}")
                    
            except Exception as e:
                error_msg = str(e)
                self.failed_sessions.append({
                    'type': 'local',
                    'session_id': getattr(session, 'session_id', 'unknown'),
                    'status': 'error',
                    'error': error_msg
                })
                print(f"❌ 删除会话异常: {error_msg}")
    
    def clean_ragflow_sessions_directly(self):
        """直接清理RAGFlow会话（通过API）"""
        if not self.ragflow_client:
            print("⚠️ RAGFlow客户端未初始化，跳过RAGFlow清理")
            return
        
        print("\n🧹 开始清理RAGFlow会话...")
        
        try:
            # 尝试获取所有RAGFlow会话
            # 注意：这需要RAGFlow提供相应的API
            print("📊 获取RAGFlow会话列表...")
            
            # 由于RAGFlow可能没有直接的会话列表API
            # 这里我们提供一个手动清理的示例
            print("⚠️ RAGFlow会话需要手动清理或通过其他API获取")
            
        except Exception as e:
            print(f"❌ 清理RAGFlow会话失败: {e}")
    
    def clean_database_tables(self):
        """清理数据库表"""
        print("\n🧹 清理数据库表...")
        
        try:
            from utils.database import db_manager
            
            # 清理消息表
            messages_query = "DELETE FROM chat_messages"
            messages_affected = db_manager.execute_update(messages_query)
            print(f"✅ 清理消息表: 删除了 {messages_affected} 条记录")
            
            # 清理会话表
            sessions_query = "DELETE FROM chat_sessions"
            sessions_affected = db_manager.execute_update(sessions_query)
            print(f"✅ 清理会话表: 删除了 {sessions_affected} 条记录")
            
        except Exception as e:
            print(f"❌ 清理数据库表失败: {e}")
    
    def generate_report(self):
        """生成清理报告"""
        print("\n" + "="*50)
        print("📊 清理报告")
        print("="*50)
        
        print(f"✅ 成功清理: {len(self.cleaned_sessions)} 个会话")
        print(f"❌ 清理失败: {len(self.failed_sessions)} 个会话")
        
        if self.cleaned_sessions:
            print("\n✅ 成功清理的会话:")
            for session in self.cleaned_sessions:
                print(f"  - {session['session_id']} (RAGFlow: {session.get('ragflow_session_id', 'N/A')})")
        
        if self.failed_sessions:
            print("\n❌ 清理失败的会话:")
            for session in self.failed_sessions:
                print(f"  - {session['session_id']}: {session.get('error', 'Unknown error')}")
        
        print(f"\n⏰ 清理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
    
    def run_cleanup(self, clean_database=False, clean_ragflow=True):
        """运行清理流程"""
        print("🚀 开始会话清理流程...")
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. 初始化RAGFlow客户端
        if clean_ragflow:
            self.init_ragflow_client()
        
        # 2. 获取所有本地会话
        sessions = self.get_all_local_sessions()
        
        if not sessions:
            print("ℹ️ 没有找到需要清理的会话")
            return
        
        # 3. 清理本地会话
        self.clean_local_sessions(sessions)
        
        # 4. 清理RAGFlow会话（如果启用）
        if clean_ragflow and self.ragflow_client:
            self.clean_ragflow_sessions_directly()
        
        # 5. 清理数据库表（如果启用）
        if clean_database:
            self.clean_database_tables()
        
        # 6. 生成报告
        self.generate_report()

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='清理所有会话')
    parser.add_argument('--database', action='store_true', help='清理数据库表')
    parser.add_argument('--no-ragflow', action='store_true', help='跳过RAGFlow清理')
    parser.add_argument('--confirm', action='store_true', help='确认清理（跳过确认提示）')
    
    args = parser.parse_args()
    
    # 确认提示
    if not args.confirm:
        print("⚠️ 警告：此操作将删除所有会话数据！")
        print("包括：")
        print("  - 所有本地会话和消息")
        print("  - 所有RAGFlow会话")
        if args.database:
            print("  - 数据库表数据")
        
        confirm = input("\n确认继续吗？(yes/no): ").lower().strip()
        if confirm not in ['yes', 'y']:
            print("❌ 操作已取消")
            return
    
    # 创建清理器并运行
    cleaner = SessionCleaner()
    cleaner.run_cleanup(
        clean_database=args.database,
        clean_ragflow=not args.no_ragflow
    )

if __name__ == "__main__":
    main()
