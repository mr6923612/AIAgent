#!/usr/bin/env python3
"""
测试运行器 - 提供多种测试选项
"""
import os
import sys
import subprocess
import time
from pathlib import Path

# 修复Windows编码问题
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestRunner:
    """测试运行器类"""
    
    def __init__(self):
        self.project_root = project_root.parent
        self.test_dir = project_root / "tests"
    
    def run_quick_tests(self):
        """运行快速测试（单元测试）"""
        print("Running quick tests (unit tests only)...")
        cmd = [
            "python", "-m", "pytest",
            str(self.test_dir / "unit"),
            "-v",
            "--tb=short",
            "--maxfail=3"
        ]
        return self._run_command(cmd)
    
    def run_integration_tests(self):
        """运行集成测试"""
        print("Running integration tests...")
        cmd = [
            "python", "-m", "pytest",
            str(self.test_dir / "integration"),
            "-v",
            "--tb=short"
        ]
        return self._run_command(cmd)
    
    def run_api_tests(self):
        """运行API测试"""
        print("Running API tests...")
        cmd = [
            "python", "-m", "pytest",
            str(self.test_dir / "api"),
            "-v",
            "--tb=short"
        ]
        return self._run_command(cmd)
    
    def run_database_tests(self):
        """运行数据库测试"""
        print("Running database tests...")
        cmd = [
            "python", "-m", "pytest",
            str(self.test_dir / "database"),
            "-v",
            "--tb=short"
        ]
        return self._run_command(cmd)
    
    def run_external_tests(self):
        """运行外部服务测试"""
        print("Running external service tests...")
        cmd = [
            "python", "-m", "pytest",
            str(self.test_dir / "external"),
            "-v",
            "--tb=short"
        ]
        return self._run_command(cmd)
    
    def run_all_tests(self):
        """运行所有测试"""
        print("Running all tests...")
        cmd = [
            "python", "-m", "pytest",
            str(self.test_dir),
            "-v",
            "--cov=crewaiBackend",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing",
            "--cov-fail-under=70",
            "--html=reports/report.html",
            "--self-contained-html"
        ]
        return self._run_command(cmd)
    
    def run_smoke_tests(self):
        """运行冒烟测试"""
        print("Running smoke tests...")
        cmd = [
            "python", "-m", "pytest",
            str(self.test_dir),
            "-m", "smoke",
            "-v",
            "--tb=short"
        ]
        return self._run_command(cmd)
    
    def run_parallel_tests(self):
        """并行运行测试"""
        print("Running tests in parallel...")
        cmd = [
            "python", "-m", "pytest",
            str(self.test_dir),
            "-v",
            "-n", "auto",
            "--tb=short"
        ]
        return self._run_command(cmd)
    
    def _run_command(self, cmd):
        """运行命令"""
        os.chdir(self.project_root)
        print(f"Running: {' '.join(cmd)}")
        print("-" * 50)
        
        start_time = time.time()
        try:
            result = subprocess.run(cmd, check=True)
            end_time = time.time()
            print(f"\nTests completed successfully in {end_time - start_time:.2f} seconds")
            return True
        except subprocess.CalledProcessError as e:
            end_time = time.time()
            print(f"\nTests failed with exit code: {e.returncode}")
            print(f"Time taken: {end_time - start_time:.2f} seconds")
            return False
    
    def show_test_summary(self):
        """显示测试摘要"""
        print("\n" + "="*60)
        print("AI Agent Test Suite")
        print("="*60)
        print("Available test categories:")
        print("1. Quick tests (unit tests only)")
        print("2. Integration tests")
        print("3. API tests")
        print("4. Database tests")
        print("5. External service tests")
        print("6. All tests (with coverage)")
        print("7. Smoke tests")
        print("8. Parallel tests")
        print("="*60)

def main():
    """主函数"""
    runner = TestRunner()
    
    if len(sys.argv) < 2:
        runner.show_test_summary()
        choice = input("\nEnter your choice (1-8): ").strip()
    else:
        choice = sys.argv[1]
    
    test_functions = {
        "1": runner.run_quick_tests,
        "2": runner.run_integration_tests,
        "3": runner.run_api_tests,
        "4": runner.run_database_tests,
        "5": runner.run_external_tests,
        "6": runner.run_all_tests,
        "7": runner.run_smoke_tests,
        "8": runner.run_parallel_tests
    }
    
    if choice in test_functions:
        success = test_functions[choice]()
        sys.exit(0 if success else 1)
    else:
        print("Invalid choice. Please run the script again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
