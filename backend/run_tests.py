#!/usr/bin/env python3
"""
Test runner script for NETZ AI
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd: list, description: str) -> bool:
    """Run a command and return success status"""
    print(f"\n{'=' * 60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('=' * 60)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Run NETZ AI tests")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--e2e", action="store_true", help="Run only e2e tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--lint", action="store_true", help="Run linting checks")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--failfast", "-x", action="store_true", help="Stop on first failure")
    
    args = parser.parse_args()
    
    # Base pytest command
    pytest_cmd = ["pytest"]
    
    # Add verbosity
    if args.verbose:
        pytest_cmd.append("-vv")
    else:
        pytest_cmd.append("-v")
    
    # Add failfast
    if args.failfast:
        pytest_cmd.append("-x")
    
    # Add parallel execution
    if args.parallel:
        pytest_cmd.extend(["-n", "auto"])
    
    # Add test selection
    if args.unit:
        pytest_cmd.extend(["-m", "unit"])
    elif args.integration:
        pytest_cmd.extend(["-m", "integration"])
    elif args.e2e:
        pytest_cmd.extend(["-m", "e2e"])
    
    # Add coverage if requested
    if args.coverage:
        pytest_cmd.extend([
            "--cov=.",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-report=xml"
        ])
    
    # Run linting if requested
    if args.lint:
        print("\n🔍 Running code quality checks...")
        
        # Black formatting check
        if not run_command(
            ["black", "--check", "."],
            "Black formatting check"
        ):
            print("❌ Black formatting issues found. Run 'black .' to fix.")
            return 1
        
        # isort import ordering check
        if not run_command(
            ["isort", "--check-only", "."],
            "Import ordering check"
        ):
            print("❌ Import ordering issues found. Run 'isort .' to fix.")
            return 1
        
        # Flake8 linting
        if not run_command(
            ["flake8", ".", "--max-line-length=100", "--extend-ignore=E203,W503"],
            "Flake8 linting"
        ):
            print("❌ Flake8 linting issues found.")
            return 1
        
        print("\n✅ All linting checks passed!")
    
    # Run tests
    print("\n🧪 Running tests...")
    success = run_command(pytest_cmd, "Pytest")
    
    if success:
        print("\n✅ All tests passed!")
        
        if args.coverage:
            print("\n📊 Coverage report generated:")
            print("   - HTML report: htmlcov/index.html")
            print("   - XML report: coverage.xml")
    else:
        print("\n❌ Some tests failed!")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())