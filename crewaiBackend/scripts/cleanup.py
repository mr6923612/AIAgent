#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理脚本 - 清理临时文件和缓存
"""

import os
import shutil
import sys

def cleanup_project():
    """清理项目临时文件"""
    print("=" * 50)
    print("项目清理工具")
    print("=" * 50)
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 要清理的文件和目录
    cleanup_items = [
        # Python缓存文件
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".pytest_cache",
        
        # 临时文件
        "*.tmp",
        "*.temp",
        "*.log",
        "*.bak",
        "*.swp",
        "*.swo",
        "*~",
        
        # Word临时文件
        "~$*.docx",
        "~$*.doc",
        
        # IDE文件
        ".vscode",
        ".idea",
        "*.sublime-*",
        
        # 系统文件
        ".DS_Store",
        "Thumbs.db",
        "desktop.ini"
    ]
    
    cleaned_count = 0
    
    # 遍历项目目录
    for root, dirs, files in os.walk(project_root):
        # 跳过某些目录
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'venv', 'env']]
        
        # 清理文件
        for file in files:
            file_path = os.path.join(root, file)
            file_name = os.path.basename(file)
            
            # 检查是否需要清理
            should_clean = False
            for pattern in cleanup_items:
                if pattern.startswith("*"):
                    if file_name.endswith(pattern[1:]):
                        should_clean = True
                        break
                elif pattern.startswith("~$"):
                    if file_name.startswith("~$"):
                        should_clean = True
                        break
                elif file_name == pattern:
                    should_clean = True
                    break
            
            if should_clean:
                try:
                    os.remove(file_path)
                    print(f"删除文件: {file_path}")
                    cleaned_count += 1
                except Exception as e:
                    print(f"删除文件失败: {file_path} - {str(e)}")
        
        # 清理空目录
        for dir_name in dirs[:]:
            dir_path = os.path.join(root, dir_name)
            if dir_name == "__pycache__":
                try:
                    shutil.rmtree(dir_path)
                    print(f"删除目录: {dir_path}")
                    cleaned_count += 1
                    dirs.remove(dir_name)
                except Exception as e:
                    print(f"删除目录失败: {dir_path} - {str(e)}")
    
    print(f"\n清理完成！共清理了 {cleaned_count} 个文件/目录")
    print("=" * 50)

if __name__ == "__main__":
    try:
        cleanup_project()
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
    except Exception as e:
        print(f"\n\n发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
