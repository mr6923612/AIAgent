#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本
运行所有测试用例并确保清理
"""

import sys
import os
import time
import subprocess
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.test_cleanup import cleanup_all_sessions

def run_test(test_name, test_file, test_args=None):
    """运行单个测试"""
    print(f"\n{'='*60}")
    print(f"🧪 运行测试: {test_name}")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    try:
        # 构建命令
        cmd = [sys.executable, test_file]
        if test_args:
            cmd.extend(test_args)
        
        # 运行测试
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        # 输出结果
        if result.stdout:
            print("📤 测试输出:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️ 测试错误:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ 测试 {test_name} 通过")
            return True
        else:
            print(f"❌ 测试 {test_name} 失败 (退出码: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ 测试 {test_name} 超时")
        return False
    except Exception as e:
        print(f"❌ 运行测试 {test_name} 异常: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行所有测试...")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试前清理
    print("\n🧹 测试前清理...")
    cleanup_all_sessions()
    
    # 定义测试列表
    tests = [
        {
            "name": "会话管理测试",
            "file": "tests/test_session_management.py",
            "args": ["--test", "all"]
        },
        {
            "name": "API测试",
            "file": "tests/integration/test_backend_api.py",
            "args": []
        }
    ]
    
    # 运行测试
    passed_tests = 0
    failed_tests = 0
    
    for test in tests:
        if os.path.exists(test["file"]):
            success = run_test(test["name"], test["file"], test["args"])
            if success:
                passed_tests += 1
            else:
                failed_tests += 1
        else:
            print(f"⚠️ 测试文件不存在: {test['file']}")
            failed_tests += 1
    
    # 测试后清理
    print("\n🧹 测试后清理...")
    cleanup_all_sessions()
    
    # 输出总结
    print(f"\n{'='*60}")
    print("📊 测试总结")
    print(f"{'='*60}")
    print(f"✅ 通过: {passed_tests}")
    print(f"❌ 失败: {failed_tests}")
    print(f"📊 总计: {passed_tests + failed_tests}")
    print(f"⏰ 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if failed_tests == 0:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠️ 部分测试失败")
        return 1

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='测试运行脚本')
    parser.add_argument('--test', help='运行指定测试')
    parser.add_argument('--cleanup-only', action='store_true', help='只运行清理')
    parser.add_argument('--no-cleanup', action='store_true', help='跳过清理')
    
    args = parser.parse_args()
    
    if args.cleanup_only:
        print("🧹 只运行清理...")
        cleanup_all_sessions()
        print("✅ 清理完成")
        return 0
    
    if args.test:
        # 运行指定测试
        test_file = f"tests/{args.test}.py"
        if not os.path.exists(test_file):
            print(f"❌ 测试文件不存在: {test_file}")
            return 1
        
        if not args.no_cleanup:
            print("🧹 测试前清理...")
            cleanup_all_sessions()
        
        success = run_test(args.test, test_file)
        
        if not args.no_cleanup:
            print("🧹 测试后清理...")
            cleanup_all_sessions()
        
        return 0 if success else 1
    else:
        # 运行所有测试
        return run_all_tests()

if __name__ == "__main__":
    exit(main())
