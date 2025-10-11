#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音转文字功能测试
测试单一功能：语音转文字转换
支持多种输入：不同格式的音频文件
"""

import os
import sys
import base64

# 添加后端路径
sys.path.append('../crewaiBackend')

from utils.speech_to_text import speech_converter

def test_speech_to_text():
    """测试语音转文字功能"""
    print("=" * 60)
    print("语音转文字功能测试")
    print("=" * 60)
    
    # 测试音频文件列表
    test_files = [
        {
            "file": "../test_audios/Recording.m4a",
            "expected_language": "en-US",
            "description": "英语音频文件1"
        },
        {
            "file": "../test_audios/Recording (2).m4a", 
            "expected_language": "en-US",
            "description": "英语音频文件2"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_files, 1):
        print(f"\n测试 {i}/{len(test_files)}: {test_case['description']}")
        print(f"文件: {test_case['file']}")
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
            # 读取音频文件并转换为Base64
            with open(test_case['file'], 'rb') as f:
                audio_bytes = f.read()
            
            audio_data = base64.b64encode(audio_bytes).decode('utf-8')
            print(f"Base64编码完成，长度: {len(audio_data)}")
            
            # 测试语音转文字
            print("开始语音转文字...")
            result = speech_converter.convert_audio_to_text(audio_data, test_case['expected_language'])
            
            if result:
                print(f"✅ 语音转文字成功!")
                print(f"识别结果: {result}")
                results.append({
                    'file': test_case['file'],
                    'success': True,
                    'result': result,
                    'language': test_case['expected_language']
                })
            else:
                print("❌ 语音转文字失败")
                results.append({
                    'file': test_case['file'],
                    'success': False,
                    'error': '语音转文字失败'
                })
                
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            results.append({
                'file': test_case['file'],
                'success': False,
                'error': str(e)
            })
    
    # 输出测试结果总结
    print(f"\n{'='*60}")
    print("测试结果总结")
    print(f"{'='*60}")
    
    success_count = 0
    for i, result in enumerate(results, 1):
        print(f"\n测试 {i}: {result['file']}")
        if result['success']:
            print(f"✅ 成功: {result['result']}")
            success_count += 1
        else:
            print(f"❌ 失败: {result['error']}")
    
    print(f"\n总计: {success_count}/{len(results)} 个测试成功")
    
    if success_count == len(results):
        print("🎉 所有语音转文字测试通过!")
        return True
    else:
        print("⚠️ 部分测试失败")
        return False

if __name__ == "__main__":
    test_speech_to_text()
