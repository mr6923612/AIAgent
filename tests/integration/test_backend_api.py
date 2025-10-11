#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后端API功能测试
测试单一功能：后端API接口
支持多种输入：文本、图片、音频
"""

import requests
import os
import time

def test_backend_health():
    """测试后端服务健康状态"""
    print("=" * 60)
    print("后端API健康状态测试")
    print("=" * 60)
    
    try:
        response = requests.get("http://127.0.0.1:8012/api/crew", timeout=5)
        print("✅ 后端服务运行正常")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ 后端服务未运行")
        print("请先启动后端服务: cd crewaiBackend && python main.py")
        return False
    except Exception as e:
        print(f"❌ 后端服务异常: {str(e)}")
        return False

def test_text_api():
    """测试文本输入API"""
    print("\n" + "=" * 60)
    print("文本输入API测试")
    print("=" * 60)
    
    test_cases = [
        {
            "input": "你好，我想了解你们的产品",
            "description": "简单问候"
        },
        {
            "input": "这个产品怎么样？价格是多少？",
            "description": "产品咨询"
        },
        {
            "input": "我的订单还没有发货，请帮我查询一下",
            "description": "订单查询"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}/{len(test_cases)}: {test_case['description']}")
        print(f"输入: {test_case['input']}")
        print("-" * 40)
        
        try:
            response = requests.post('http://127.0.0.1:8012/api/crew', json={
                'customer_input': test_case['input'],
                'input_type': 'text',
                'additional_context': '',
                'customer_domain': 'example.com',
                'project_description': test_case['input']
            }, timeout=30)
            
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 202:
                result = response.json()
                job_id = result.get('job_id')
                print(f"✅ 任务创建成功，Job ID: {job_id}")
                
                # 等待任务完成
                print("等待任务完成...")
                success = wait_for_job_completion(job_id)
                
                results.append({
                    'input': test_case['input'],
                    'success': success,
                    'job_id': job_id
                })
            else:
                print(f"❌ API请求失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                results.append({
                    'input': test_case['input'],
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            results.append({
                'input': test_case['input'],
                'success': False,
                'error': str(e)
            })
    
    return results

def test_audio_api():
    """测试音频输入API"""
    print("\n" + "=" * 60)
    print("音频输入API测试")
    print("=" * 60)
    
    audio_file = "../test_audios/Recording (2).m4a"
    
    if not os.path.exists(audio_file):
        print(f"❌ 测试音频文件不存在: {audio_file}")
        return []
    
    print(f"使用测试文件: {audio_file}")
    print(f"文件大小: {os.path.getsize(audio_file)} bytes")
    
    try:
        with open(audio_file, 'rb') as f:
            files = {'audio': (os.path.basename(audio_file), f, 'audio/m4a')}
            data = {
                'customer_input': '',
                'input_type': 'voice',
                'additional_context': '',
                'customer_domain': 'example.com',
                'project_description': '音频输入测试'
            }
            
            print("发送音频请求...")
            response = requests.post('http://127.0.0.1:8012/api/crew', files=files, data=data, timeout=60)
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 202:
            result = response.json()
            job_id = result.get('job_id')
            print(f"✅ 任务创建成功，Job ID: {job_id}")
            
            # 等待任务完成
            print("等待任务完成...")
            success = wait_for_job_completion(job_id)
            
            return [{
                'input': '音频输入',
                'success': success,
                'job_id': job_id
            }]
        elif response.status_code == 400:
            result = response.json()
            error_message = result.get('error')
            print(f"⚠️ 语音识别失败: {error_message}")
            return [{
                'input': '音频输入',
                'success': False,
                'error': '语音识别失败'
            }]
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return [{
                'input': '音频输入',
                'success': False,
                'error': f"HTTP {response.status_code}"
            }]
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return [{
            'input': '音频输入',
            'success': False,
            'error': str(e)
        }]

def wait_for_job_completion(job_id, max_wait=60):
    """等待任务完成"""
    for i in range(max_wait // 2):
        time.sleep(2)
        try:
            response = requests.get(f'http://127.0.0.1:8012/api/crew/{job_id}')
            if response.status_code == 200:
                result = response.json()
                status = result.get('status')
                print(f"任务状态: {status}")
                
                if status == 'COMPLETE':
                    print("✅ 任务完成!")
                    return True
                elif status == 'ERROR':
                    print(f"❌ 任务失败: {result.get('error')}")
                    return False
        except Exception as e:
            print(f"检查状态异常: {str(e)}")
    
    print("⏰ 任务超时")
    return False

def main():
    """主测试函数"""
    print("后端API功能测试")
    print("=" * 60)
    
    # 检查后端健康状态
    if not test_backend_health():
        return
    
    # 测试文本API
    text_results = test_text_api()
    
    # 测试音频API
    audio_results = test_audio_api()
    
    # 汇总结果
    all_results = text_results + audio_results
    
    print(f"\n{'='*60}")
    print("API测试结果总结")
    print(f"{'='*60}")
    
    success_count = 0
    for result in all_results:
        print(f"\n输入: {result['input']}")
        if result['success']:
            print("✅ 成功")
            success_count += 1
        else:
            print(f"❌ 失败: {result.get('error', '未知错误')}")
    
    print(f"\n总计: {success_count}/{len(all_results)} 个API测试成功")
    
    if success_count == len(all_results):
        print("🎉 所有API测试通过!")
    else:
        print("⚠️ 部分API测试失败")

if __name__ == "__main__":
    main()
