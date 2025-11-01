#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session Monitoring Script
Monitor session Agent status and system performance
"""

import sys
import os
import time
import requests
import json
from datetime import datetime

# Add project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def monitor_sessions():
    """Monitor session status"""
    try:
        response = requests.get('http://localhost:5000/api/sessions/status', timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"=== Session Status ({datetime.now().strftime('%H:%M:%S')}) ===")
            print(f"Total sessions: {status['total_sessions']}")
            print(f"Active sessions: {', '.join(status['sessions'])}")
            
            if status['session_details']:
                print("\nSession details:")
                for session_id, details in status['session_details'].items():
                    print(f"  {session_id[:8]}: Created at {details['created_at']}, "
                          f"Last used {details['last_used']}, "
                          f"Age {details['age_seconds']:.0f} seconds")
            print()
            return status
        else:
            print(f"❌ Failed to get session status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Failed to monitor sessions: {e}")
        return None

def cleanup_sessions(max_age_seconds=1800):
    """Clean up inactive sessions"""
    try:
        data = {"max_age_seconds": max_age_seconds}
        response = requests.post('http://localhost:5000/api/sessions/cleanup', 
                               json=data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Session cleanup completed: {result['message']}")
            return True
        else:
            print(f"❌ Failed to clean up sessions: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to clean up sessions: {e}")
        return False

def test_session_performance():
    """Test session performance"""
    try:
        # Create test session
        session_data = {"user_id": "test_user"}
        create_response = requests.post('http://localhost:5000/api/sessions', 
                                      json=session_data, timeout=5)
        
        if create_response.status_code != 201:
            print(f"❌ Failed to create test session: {create_response.status_code}")
            return None
        
        session_id = create_response.json()['session_id']
        print(f"✅ Test session created: {session_id}")
        
        # Send test message
        test_data = {
            "customer_input": "Test session performance",
            "session_id": session_id
        }
        
        start_time = time.time()
        crew_response = requests.post('http://localhost:5000/api/crew', 
                                    json=test_data, timeout=30)
        end_time = time.time()
        
        if crew_response.status_code == 202:
            job_id = crew_response.json().get('job_id')
            print(f"✅ Test request submitted, job ID: {job_id}")
            print(f"⏱️  Request response time: {(end_time - start_time)*1000:.0f}ms")
            
            # Wait for task completion
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                status_response = requests.get(f'http://localhost:5000/api/crew/{job_id}')
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if status_data['status'] in ['COMPLETE', 'FAILED', 'ERROR']:
                        total_time = time.time() - start_time
                        print(f"✅ Task completed, total time: {total_time:.1f} seconds")
                        print(f"📊 Task status: {status_data['status']}")
                        
                        # Clean up test session
                        requests.delete(f'http://localhost:5000/api/sessions/{session_id}')
                        print(f"🗑️ Test session cleaned: {session_id}")
                        
                        return total_time
                print(f"⏳ Waiting for task completion... ({i+1}/30)")
            
            print("❌ Task timeout")
            return None
        else:
            print(f"❌ Test request failed: {crew_response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return None

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Session monitoring tool')
    parser.add_argument('--monitor', action='store_true', help='Continuous monitoring mode')
    parser.add_argument('--test', action='store_true', help='Run performance test')
    parser.add_argument('--cleanup', action='store_true', help='Clean up inactive sessions')
    parser.add_argument('--interval', type=int, default=10, help='Monitoring interval (seconds)')
    parser.add_argument('--max-age', type=int, default=1800, help='Maximum inactive time (seconds)')
    
    args = parser.parse_args()
    
    if args.cleanup:
        print(f"🧹 Cleaning up inactive sessions (max inactive time: {args.max_age} seconds)...")
        cleanup_sessions(args.max_age)
        return
    
    if args.test:
        print("🧪 Starting session performance test...")
        test_session_performance()
        return
    
    if args.monitor:
        print(f"📊 Starting continuous monitoring mode, interval {args.interval} seconds")
        print("Press Ctrl+C to stop monitoring")
        try:
            while True:
                monitor_sessions()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
    else:
        # Single monitoring
        monitor_sessions()

if __name__ == "__main__":
    main()
