#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试
测试单一功能：完整的语音转文字到LLM回复流程
支持多种输入：不同的语音内容
"""

import requests
import os
import time

def test_voice_to_llm_integration():
    """测试语音转文字到LLM回复的完整流程"""
    print("=" * 60)
    print("语音转文字到LLM回复集成测试")
    print("=" * 60)
    
    # 测试用例
    test_cases = [
        {
            "file": "../test_audios/Recording.m4a",
            "description": "英语语音1",
            "expected_content": "other thing is"
        },
        {
            "file": "../test_audios/Recording (2).m4a",
            "description": "英语语音2", 
            "expected_content": "hello hello"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}/{len(test_cases)}: {test_case['description']}")
        print(f"文件: {test_case['file']}")
        print(f"预期内容: {test_case['expected_content']}")
        print("-" * 40)
        
        if not os.path.exists(test_case['file']):
            print(f"❌ 文件不存在: {test_case['file']}")
            results.append({
                'file': test_case['file'],
                'success': False,
                'error': '文件不存在'
            })
            continue
        
        file_size = os.path.getsize(test_case['file'])
        print(f"文件大小: {file_size} bytes")
        
        try:
            # 发送音频到后端
            with open(test_case['file'], 'rb') as f:
                files = {'audio': (os.path.basename(test_case['file']), f, 'audio/m4a')}
                data = {
                    'customer_input': '',
                    'input_type': 'voice',
                    'additional_context': '',
                    'customer_domain': 'example.com',
                    'project_description': f'集成测试: {test_case["description"]}'
                }
                
                print("发送音频到后端...")
                response = requests.post('http://127.0.0.1:8012/api/crew', files=files, data=data, timeout=60)
            
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 202:
                result = response.json()
                job_id = result.get('job_id')
                print(f"✅ 任务创建成功，Job ID: {job_id}")
                
                # 等待任务完成并获取LLM回复
                print("等待语音转文字和LLM处理...")
                llm_response = wait_for_llm_response(job_id)
                
                if llm_response:
                    print(f"✅ LLM回复: {llm_response[:100]}...")
                    results.append({
                        'file': test_case['file'],
                        'success': True,
                        'job_id': job_id,
                        'llm_response': llm_response
                    })
                else:
                    print("❌ 获取LLM回复失败")
                    results.append({
                        'file': test_case['file'],
                        'success': False,
                        'error': 'LLM回复失败'
                    })
                    
            elif response.status_code == 400:
                result = response.json()
                error_message = result.get('error')
                print(f"⚠️ 语音识别失败: {error_message}")
                results.append({
                    'file': test_case['file'],
                    'success': False,
                    'error': '语音识别失败'
                })
            else:
                print(f"❌ API请求失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                results.append({
                    'file': test_case['file'],
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            results.append({
                'file': test_case['file'],
                'success': False,
                'error': str(e)
            })
    
    return results

def wait_for_llm_response(job_id, max_wait=120):
    """等待LLM回复"""
    for i in range(max_wait // 2):
        time.sleep(2)
        try:
            response = requests.get(f'http://127.0.0.1:8012/api/crew/{job_id}')
            if response.status_code == 200:
                result = response.json()
                status = result.get('status')
                print(f"任务状态: {status}")
                
                if status == 'COMPLETE':
                    llm_response = result.get('result')
                    if llm_response:
                        return llm_response
                    else:
                        print("❌ LLM回复为空")
                        return None
                elif status == 'ERROR':
                    print(f"❌ 任务失败: {result.get('error')}")
                    return None
        except Exception as e:
            print(f"检查状态异常: {str(e)}")
    
    print("⏰ 任务超时")
    return None

def main():
    """主测试函数"""
    print("集成测试 - 语音转文字到LLM回复")
    print("=" * 60)
    
    # 检查后端服务
    try:
        response = requests.get("http://127.0.0.1:8012/api/crew", timeout=5)
        print("✅ 后端服务运行正常")
    except:
        print("❌ 后端服务未运行")
        print("请先启动后端服务: cd crewaiBackend && python main.py")
        return
    
    # 运行集成测试
    results = test_voice_to_llm_integration()
    
    # 输出测试结果
    print(f"\n{'='*60}")
    print("集成测试结果总结")
    print(f"{'='*60}")
    
    success_count = 0
    for i, result in enumerate(results, 1):
        print(f"\n测试 {i}: {result['file']}")
        if result['success']:
            print("✅ 成功")
            if 'llm_response' in result:
                print(f"LLM回复: {result['llm_response'][:100]}...")
            success_count += 1
        else:
            print(f"❌ 失败: {result.get('error', '未知错误')}")
    
    print(f"\n总计: {success_count}/{len(results)} 个集成测试成功")
    
    if success_count == len(results):
        print("🎉 所有集成测试通过!")
    else:
        print("⚠️ 部分集成测试失败")

if __name__ == "__main__":
    main()
