#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖包检查脚本
验证requirements.txt中的所有包是否正确安装
"""

import sys
import os
import subprocess
from pathlib import Path

# 设置编码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_package(package_name, version_spec=None):
    """检查单个包是否安装"""
    try:
        if version_spec:
            # 检查特定版本
            import pkg_resources
            pkg_resources.require(f"{package_name}{version_spec}")
        else:
            # 只检查包是否存在
            __import__(package_name)
        return True, None
    except ImportError as e:
        return False, str(e)
    except pkg_resources.DistributionNotFound as e:
        return False, str(e)
    except pkg_resources.VersionConflict as e:
        return False, str(e)

def check_requirements():
    """检查requirements.txt中的所有依赖"""
    print("🔍 检查项目依赖包...")
    print("=" * 50)
    
    # 读取requirements.txt
    requirements_file = Path(__file__).parent.parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt 文件不存在")
        return False
    
    with open(requirements_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 解析依赖
    dependencies = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            # 解析包名和版本
            if '>=' in line:
                package, version = line.split('>=')
                dependencies.append((package.strip(), f">={version.strip()}"))
            elif '==' in line:
                package, version = line.split('==')
                dependencies.append((package.strip(), f"=={version.strip()}"))
            elif '<' in line:
                package, version = line.split('<')
                dependencies.append((package.strip(), f"<{version.strip()}"))
            else:
                dependencies.append((line, None))
    
    # 检查每个依赖
    all_ok = True
    for package, version_spec in dependencies:
        is_installed, error = check_package(package, version_spec)
        
        if is_installed:
            print(f"✅ {package}{version_spec or ''}")
        else:
            print(f"❌ {package}{version_spec or ''} - {error}")
            all_ok = False
    
    print("=" * 50)
    
    if all_ok:
        print("🎉 所有依赖包检查通过！")
        return True
    else:
        print("⚠️ 部分依赖包缺失或版本不匹配")
        print("\n💡 解决方案:")
        print("1. 运行: pip install -r requirements.txt")
        print("2. 或者: pip install --upgrade -r requirements.txt")
        return False

def install_requirements():
    """安装requirements.txt中的依赖"""
    print("📦 安装项目依赖...")
    
    requirements_file = Path(__file__).parent.parent / "requirements.txt"
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True, check=True)
        
        print("✅ 依赖安装成功")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='检查或安装项目依赖')
    parser.add_argument('--install', action='store_true', help='安装缺失的依赖')
    parser.add_argument('--check-only', action='store_true', help='只检查不安装')
    
    args = parser.parse_args()
    
    if args.install:
        # 先检查，再安装
        if not check_requirements():
            print("\n📦 开始安装缺失的依赖...")
            install_requirements()
            print("\n🔍 重新检查依赖...")
            check_requirements()
    else:
        # 只检查
        check_requirements()

if __name__ == "__main__":
    main()
