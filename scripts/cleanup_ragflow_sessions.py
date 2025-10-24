#!/usr/bin/env python3
"""
RAGFlow会话清理脚本
清理RAGFlow中的所有会话数据
"""

import requests
import json
import os
import sys

def cleanup_ragflow_sessions():
    """清理RAGFlow中的所有会话"""
    
    # 从环境变量读取配置
    base_url = os.environ.get('RAGFLOW_BASE_URL', 'http://localhost:9380')
    api_key = os.environ.get('RAGFLOW_API_KEY')
    
    if not api_key:
        print("❌ 错误: RAGFLOW_API_KEY 环境变量未设置")
        print("请设置环境变量: export RAGFLOW_API_KEY=your_api_key")
        sys.exit(1)
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"🔍 连接RAGFlow: {base_url}")
        
        # 获取所有聊天列表
        response = requests.get(f'{base_url}/api/v1/chats', headers=headers)
        
        if response.status_code == 200:
            chats = response.json().get('data', [])
            print(f"📊 找到 {len(chats)} 个聊天会话")
            
            if len(chats) == 0:
                print("✅ 没有找到需要清理的会话")
                return
            
            # 删除每个聊天会话
            deleted_count = 0
            for chat in chats:
                chat_id = chat.get('id')
                if chat_id:
                    delete_response = requests.delete(f'{base_url}/api/v1/chats/{chat_id}', headers=headers)
                    if delete_response.status_code == 200:
                        print(f"✅ 已删除会话: {chat_id}")
                        deleted_count += 1
                    else:
                        print(f"❌ 删除失败: {chat_id} - {delete_response.status_code}")
            
            print(f"🎉 清理完成！共删除 {deleted_count} 个会话")
            
        else:
            print(f"❌ 获取聊天列表失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            sys.exit(1)
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 无法连接到RAGFlow服务")
        print("请确保RAGFlow服务正在运行")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 清理过程中出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    cleanup_ragflow_sessions()
