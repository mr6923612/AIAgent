#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话监控脚本
监控会话Agent状态和系统性能
"""

import sys
import os
import time
import requests
import json
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def monitor_sessions():
    """监控会话状态"""
    try:
        response = requests.get('http://localhost:5000/api/sessions/status', timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"=== 会话状态 ({datetime.now().strftime('%H:%M:%S')}) ===")
            print(f"总会话数: {status['total_sessions']}")
            print(f"活跃会话: {', '.join(status['sessions'])}")
            
            if status['session_details']:
                print("\n会话详情:")
                for session_id, details in status['session_details'].items():
                    print(f"  {session_id[:8]}: 创建于 {details['created_at']}, "
                          f"最后使用 {details['last_used']}, "
                          f"存活 {details['age_seconds']:.0f}秒")
            print()
            return status
        else:
            print(f"❌ 获取会话状态失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 监控会话失败: {e}")
        return None

def cleanup_sessions(max_age_seconds=1800):
    """清理非活跃会话"""
    try:
        data = {"max_age_seconds": max_age_seconds}
        response = requests.post('http://localhost:5000/api/sessions/cleanup', 
                               json=data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 会话清理完成: {result['message']}")
            return True
        else:
            print(f"❌ 清理会话失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 清理会话失败: {e}")
        return False

def test_session_performance():
    """测试会话性能"""
    try:
        # 创建测试会话
        session_data = {"user_id": "test_user"}
        create_response = requests.post('http://localhost:5000/api/sessions', 
                                      json=session_data, timeout=5)
        
        if create_response.status_code != 201:
            print(f"❌ 创建测试会话失败: {create_response.status_code}")
            return None
        
        session_id = create_response.json()['session_id']
        print(f"✅ 测试会话已创建: {session_id}")
        
        # 发送测试消息
        test_data = {
            "customer_input": "测试会话性能",
            "session_id": session_id
        }
        
        start_time = time.time()
        crew_response = requests.post('http://localhost:5000/api/crew', 
                                    json=test_data, timeout=30)
        end_time = time.time()
        
        if crew_response.status_code == 202:
            job_id = crew_response.json().get('job_id')
            print(f"✅ 测试请求已提交，任务ID: {job_id}")
            print(f"⏱️  请求响应时间: {(end_time - start_time)*1000:.0f}ms")
            
            # 等待任务完成
            for i in range(30):  # 最多等待30秒
                time.sleep(1)
                status_response = requests.get(f'http://localhost:5000/api/crew/{job_id}')
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if status_data['status'] in ['COMPLETE', 'FAILED', 'ERROR']:
                        total_time = time.time() - start_time
                        print(f"✅ 任务完成，总耗时: {total_time:.1f}秒")
                        print(f"📊 任务状态: {status_data['status']}")
                        
                        # 清理测试会话
                        requests.delete(f'http://localhost:5000/api/sessions/{session_id}')
                        print(f"🗑️ 测试会话已清理: {session_id}")
                        
                        return total_time
                print(f"⏳ 等待任务完成... ({i+1}/30)")
            
            print("❌ 任务超时")
            return None
        else:
            print(f"❌ 测试请求失败: {crew_response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        return None

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='会话监控工具')
    parser.add_argument('--monitor', action='store_true', help='持续监控模式')
    parser.add_argument('--test', action='store_true', help='运行性能测试')
    parser.add_argument('--cleanup', action='store_true', help='清理非活跃会话')
    parser.add_argument('--interval', type=int, default=10, help='监控间隔（秒）')
    parser.add_argument('--max-age', type=int, default=1800, help='最大非活跃时间（秒）')
    
    args = parser.parse_args()
    
    if args.cleanup:
        print(f"🧹 清理非活跃会话（最大非活跃时间: {args.max_age}秒）...")
        cleanup_sessions(args.max_age)
        return
    
    if args.test:
        print("🧪 开始会话性能测试...")
        test_session_performance()
        return
    
    if args.monitor:
        print(f"📊 开始持续监控模式，间隔 {args.interval} 秒")
        print("按 Ctrl+C 停止监控")
        try:
            while True:
                monitor_sessions()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n👋 监控已停止")
    else:
        # 单次监控
        monitor_sessions()

if __name__ == "__main__":
    main()
