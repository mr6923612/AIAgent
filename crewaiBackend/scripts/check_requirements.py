#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dependency Package Check Script
Verify that all packages in requirements.txt are correctly installed
"""

import sys
import os
import subprocess
from pathlib import Path

# Set encoding
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Add project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_package(package_name, version_spec=None):
    """Check if a single package is installed"""
    try:
        if version_spec:
            # Check specific version
            import pkg_resources
            pkg_resources.require(f"{package_name}{version_spec}")
        else:
            # Only check if package exists
            __import__(package_name)
        return True, None
    except ImportError as e:
        return False, str(e)
    except pkg_resources.DistributionNotFound as e:
        return False, str(e)
    except pkg_resources.VersionConflict as e:
        return False, str(e)

def check_requirements():
    """Check all dependencies in requirements.txt"""
    print("🔍 Checking project dependencies...")
    print("=" * 50)
    
    # Read requirements.txt
    requirements_file = Path(__file__).parent.parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt file does not exist")
        return False
    
    with open(requirements_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Parse dependencies
    dependencies = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            # Parse package name and version
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
    
    # Check each dependency
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
        print("🎉 All dependency checks passed!")
        return True
    else:
        print("⚠️ Some dependencies are missing or version mismatch")
        print("\n💡 Solution:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Or: pip install --upgrade -r requirements.txt")
        return False

def install_requirements():
    """Install dependencies in requirements.txt"""
    print("📦 Installing project dependencies...")
    
    requirements_file = Path(__file__).parent.parent / "requirements.txt"
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True, check=True)
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Dependency installation failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Check or install project dependencies')
    parser.add_argument('--install', action='store_true', help='Install missing dependencies')
    parser.add_argument('--check-only', action='store_true', help='Only check, do not install')
    
    args = parser.parse_args()
    
    if args.install:
        # Check first, then install
        if not check_requirements():
            print("\n📦 Starting to install missing dependencies...")
            install_requirements()
            print("\n🔍 Rechecking dependencies...")
            check_requirements()
    else:
        # Only check
        check_requirements()

if __name__ == "__main__":
    main()
