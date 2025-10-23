#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话持久化测试脚本
测试会话清理后SQL数据是否保留，以及重新登录是否能恢复会话
"""

import sys
import os
import time
import requests
import json
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_test_session():
    """创建测试会话"""
    try:
        session_data = {
            "user_id": "test_user_persistence",
            "title": "持久化测试会话"
        }
        
        response = requests.post('http://localhost:5000/api/sessions', 
                               json=session_data, timeout=5)
        
        if response.status_code == 201:
            session_info = response.json()
            print(f"✅ 测试会话创建成功: {session_info['session_id']}")
            return session_info['session_id']
        else:
            print(f"❌ 创建测试会话失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 创建测试会话失败: {e}")
        return None

def add_test_message(session_id):
    """添加测试消息"""
    try:
        message_data = {
            "role": "user",
            "content": "这是一条测试消息，用于验证会话持久化"
        }
        
        response = requests.post(f'http://localhost:5000/api/sessions/{session_id}/messages', 
                               json=message_data, timeout=5)
        
        if response.status_code == 201:
            print(f"✅ 测试消息添加成功")
            return True
        else:
            print(f"❌ 添加测试消息失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 添加测试消息失败: {e}")
        return False

def get_session_info(session_id):
    """获取会话信息"""
    try:
        response = requests.get(f'http://localhost:5000/api/sessions/{session_id}', timeout=5)
        
        if response.status_code == 200:
            session_info = response.json()
            print(f"✅ 会话信息获取成功:")
            print(f"  会话ID: {session_info['session_id']}")
            print(f"  用户ID: {session_info['user_id']}")
            print(f"  标题: {session_info['title']}")
            print(f"  消息数量: {len(session_info['messages'])}")
            print(f"  创建时间: {session_info['created_at']}")
            return session_info
        else:
            print(f"❌ 获取会话信息失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 获取会话信息失败: {e}")
        return None

def check_agent_status(session_id):
    """检查Agent状态"""
    try:
        response = requests.get('http://localhost:5000/api/sessions/status', timeout=5)
        
        if response.status_code == 200:
            status = response.json()
            if session_id in status['sessions']:
                print(f"✅ Agent存在，会话 {session_id} 在Agent池中")
                return True
            else:
                print(f"ℹ️  Agent不存在，会话 {session_id} 不在Agent池中")
                return False
        else:
            print(f"❌ 获取Agent状态失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 检查Agent状态失败: {e}")
        return False

def test_session_recovery(session_id):
    """测试会话恢复"""
    try:
        # 发送一个请求来触发Agent创建
        test_data = {
            "customer_input": "测试会话恢复",
            "session_id": session_id
        }
        
        print(f"🔄 发送测试请求，触发Agent创建...")
        response = requests.post('http://localhost:5000/api/crew', 
                               json=test_data, timeout=30)
        
        if response.status_code == 202:
            print(f"✅ 测试请求发送成功，Agent应该已重新创建")
            return True
        else:
            print(f"❌ 测试请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试会话恢复失败: {e}")
        return False

def cleanup_test_session(session_id):
    """清理测试会话"""
    try:
        response = requests.delete(f'http://localhost:5000/api/sessions/{session_id}', timeout=5)
        
        if response.status_code == 200:
            print(f"✅ 测试会话清理成功")
            return True
        else:
            print(f"❌ 清理测试会话失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 清理测试会话失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 开始会话持久化测试")
    print("=" * 50)
    
    # 1. 创建测试会话
    print("\n1️⃣ 创建测试会话...")
    session_id = create_test_session()
    if not session_id:
        print("❌ 测试失败：无法创建会话")
        return
    
    # 2. 添加测试消息
    print("\n2️⃣ 添加测试消息...")
    if not add_test_message(session_id):
        print("❌ 测试失败：无法添加消息")
        return
    
    # 3. 检查初始状态
    print("\n3️⃣ 检查初始状态...")
    session_info = get_session_info(session_id)
    if not session_info:
        print("❌ 测试失败：无法获取会话信息")
        return
    
    agent_exists = check_agent_status(session_id)
    
    # 4. 等待一段时间，让Agent可能被清理
    print("\n4️⃣ 等待30秒，模拟Agent可能被清理...")
    time.sleep(30)
    
    # 5. 检查Agent是否被清理
    print("\n5️⃣ 检查Agent是否被清理...")
    agent_still_exists = check_agent_status(session_id)
    
    # 6. 检查SQL数据是否保留
    print("\n6️⃣ 检查SQL数据是否保留...")
    session_info_after = get_session_info(session_id)
    if session_info_after:
        print("✅ SQL数据保留完整")
        print(f"   消息数量: {len(session_info_after['messages'])}")
    else:
        print("❌ SQL数据丢失")
        return
    
    # 7. 测试会话恢复
    print("\n7️⃣ 测试会话恢复...")
    if not agent_still_exists:
        print("🔄 Agent已被清理，测试会话恢复...")
        if test_session_recovery(session_id):
            print("✅ 会话恢复成功")
        else:
            print("❌ 会话恢复失败")
    else:
        print("ℹ️  Agent仍然存在，无需恢复")
    
    # 8. 最终检查
    print("\n8️⃣ 最终检查...")
    final_agent_exists = check_agent_status(session_id)
    final_session_info = get_session_info(session_id)
    
    print("\n📊 测试结果总结:")
    print(f"   会话ID: {session_id}")
    print(f"   SQL数据保留: {'✅' if final_session_info else '❌'}")
    print(f"   Agent状态: {'存在' if final_agent_exists else '不存在'}")
    print(f"   消息数量: {len(final_session_info['messages']) if final_session_info else 0}")
    
    # 9. 清理测试数据
    print("\n9️⃣ 清理测试数据...")
    cleanup_test_session(session_id)
    
    print("\n🎉 会话持久化测试完成！")

if __name__ == "__main__":
    main()
