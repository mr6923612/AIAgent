#!/usr/bin/env python3
"""
Test Running Script
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_tests(test_type=None, verbose=False, coverage=True, parallel=False):
    """Run tests"""
    # Switch to project root directory
    os.chdir(project_root.parent)
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=crewaiBackend", "--cov-report=html:htmlcov", "--cov-report=term-missing"])
    
    if parallel:
        cmd.extend(["-n", "auto"])
    
    # Select test directory based on test type
    if test_type:
        if test_type == "unit":
            cmd.append("crewaiBackend/tests/unit/")
        elif test_type == "integration":
            cmd.append("crewaiBackend/tests/integration/")
        elif test_type == "api":
            cmd.append("crewaiBackend/tests/api/")
        elif test_type == "database":
            cmd.append("crewaiBackend/tests/database/")
        elif test_type == "external":
            cmd.append("crewaiBackend/tests/external/")
        elif test_type == "smoke":
            cmd.extend(["-m", "smoke"])
        else:
            print(f"Unknown test type: {test_type}")
            return False
    else:
        cmd.append("crewaiBackend/tests/")
    
    print(f"Running command: {' '.join(cmd)}")
    
    # Run tests
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code: {e.returncode}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run tests for AI Agent project")
    parser.add_argument("--type", choices=["unit", "integration", "api", "database", "external", "smoke"],
                       help="Type of tests to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--no-coverage", action="store_true", help="Disable coverage reporting")
    parser.add_argument("--parallel", "-p", action="store_true", help="Run tests in parallel")
    
    args = parser.parse_args()
    
    success = run_tests(
        test_type=args.type,
        verbose=args.verbose,
        coverage=not args.no_coverage,
        parallel=args.parallel
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()