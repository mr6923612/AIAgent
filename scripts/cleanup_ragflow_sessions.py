#!/usr/bin/env python3
"""
RAGFlow Session Cleanup Script
Clean up all session data in RAGFlow
"""

import requests
import json
import os
import sys

def cleanup_ragflow_sessions():
    """Clean up all sessions in RAGFlow"""
    
    # Read configuration from environment variables
    base_url = os.environ.get('RAGFLOW_BASE_URL', 'http://localhost:9380')
    api_key = os.environ.get('RAGFLOW_API_KEY')
    
    if not api_key:
        print("❌ Error: RAGFLOW_API_KEY environment variable not set")
        print("Please set environment variable: export RAGFLOW_API_KEY=your_api_key")
        sys.exit(1)
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"🔍 Connecting to RAGFlow: {base_url}")
        
        # Get all chat list
        response = requests.get(f'{base_url}/api/v1/chats', headers=headers)
        
        if response.status_code == 200:
            chats = response.json().get('data', [])
            print(f"📊 Found {len(chats)} chat sessions")
            
            if len(chats) == 0:
                print("✅ No sessions found that need cleanup")
                return
            
            # Delete each chat session
            deleted_count = 0
            for chat in chats:
                chat_id = chat.get('id')
                if chat_id:
                    delete_response = requests.delete(f'{base_url}/api/v1/chats/{chat_id}', headers=headers)
                    if delete_response.status_code == 200:
                        print(f"✅ Deleted session: {chat_id}")
                        deleted_count += 1
                    else:
                        print(f"❌ Deletion failed: {chat_id} - {delete_response.status_code}")
            
            print(f"🎉 Cleanup completed! Deleted {deleted_count} sessions in total")
            
        else:
            print(f"❌ Failed to get chat list: {response.status_code}")
            print(f"Response content: {response.text}")
            sys.exit(1)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed: Unable to connect to RAGFlow service")
        print("Please ensure RAGFlow service is running")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error occurred during cleanup: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    cleanup_ragflow_sessions()
