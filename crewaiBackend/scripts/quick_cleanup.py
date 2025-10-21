#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速清理脚本
一键清理所有会话和测试数据
"""

import sys
import os
import argparse
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.cleanup_sessions import SessionCleaner
from scripts.test_cleanup import cleanup_all_sessions

def quick_cleanup(confirm=False, clean_database=False):
    """快速清理所有数据"""
    print("🚀 快速清理工具")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    if not confirm:
        print("⚠️ 警告：此操作将删除所有数据！")
        print("包括：")
        print("  - 所有本地会话和消息")
        print("  - 所有RAGFlow会话")
        if clean_database:
            print("  - 数据库表数据")
        
        response = input("\n确认继续吗？(yes/no): ").lower().strip()
        if response not in ['yes', 'y']:
            print("❌ 操作已取消")
            return False
    
    try:
        # 1. 清理测试会话
        print("\n🧹 清理测试会话...")
        cleanup_all_sessions()
        
        # 2. 清理所有会话
        print("\n🧹 清理所有会话...")
        cleaner = SessionCleaner()
        cleaner.run_cleanup(clean_database=clean_database, clean_ragflow=True)
        
        print("\n✅ 快速清理完成！")
        return True
        
    except Exception as e:
        print(f"\n❌ 清理失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='快速清理工具')
    parser.add_argument('--confirm', action='store_true', help='跳过确认提示')
    parser.add_argument('--database', action='store_true', help='清理数据库表')
    parser.add_argument('--test-only', action='store_true', help='只清理测试数据')
    
    args = parser.parse_args()
    
    if args.test_only:
        print("🧹 只清理测试数据...")
        cleanup_all_sessions()
        print("✅ 测试数据清理完成")
        return 0
    
    success = quick_cleanup(confirm=args.confirm, clean_database=args.database)
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
