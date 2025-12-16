#!/usr/bin/env python3
import sys
import os
import subprocess


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def run_command(cmd, description):
    """Run a command and print results"""
    print(f"📝 {description}...")
    print(f"Command: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print(f"\n✅ {description} - PASSED")
    else:
        print(f"\n❌ {description} - FAILED")
    
    return result.returncode


def main():
    """Main test runner"""
    print_header("🧪 AI Event Planner - Test Runner")
    
    # Check if pytest is installed
    try:
        import pytest
        print("✅ pytest is installed")
    except ImportError:
        print("❌ pytest not found!")
        print("Install with: pip install -r requirements-test.txt")
        return 1
    
    # Menu
    print("Choose test option:")
    print("1. Run all tests (quick)")
    print("2. Run all tests (verbose)")
    print("3. Run with coverage report")
    print("4. Run authentication tests only")
    print("5. Run provider tests only")
    print("6. Run search tests only")
    print("7. Run specific test")
    print("8. Run all + generate HTML report")
    print("9. Exit")
    
    choice = input("\n👉 Enter your choice (1-9): ").strip()
    
    if choice == "1":
        print_header("Running All Tests (Quick)")
        return run_command(["pytest"], "All tests")
    
    elif choice == "2":
        print_header("Running All Tests (Verbose)")
        return run_command(["pytest", "-v"], "All tests (verbose)")
    
    elif choice == "3":
        print_header("Running Tests with Coverage")
        returncode = run_command(
            ["pytest", "--cov=src", "--cov-report=html", "--cov-report=term"],
            "Tests with coverage"
        )
        if returncode == 0:
            print("\n📊 Coverage report generated!")
            print("View report: open htmlcov/index.html")
        return returncode
    
    elif choice == "4":
        print_header("Running Authentication Tests")
        return run_command(
            ["pytest", "test_integration.py::TestAuthentication", "-v"],
            "Authentication tests"
        )
    
    elif choice == "5":
        print_header("Running Provider Management Tests")
        return run_command(
            ["pytest", "test_integration.py::TestProviderManagement", "-v"],
            "Provider management tests"
        )
    
    elif choice == "6":
        print_header("Running Search Tests")
        return run_command(
            ["pytest", "test_integration.py::TestSearch", "-v"],
            "Search tests"
        )
    
    elif choice == "7":
        test_name = input("Enter test name (e.g., test_register_user_success): ").strip()
        print_header(f"Running Test: {test_name}")
        return run_command(
            ["pytest", "-k", test_name, "-v"],
            f"Test: {test_name}"
        )
    
    elif choice == "8":
        print_header("Running All Tests + HTML Report")
        returncode = run_command(
            ["pytest", "--html=test_report.html", "--self-contained-html", "-v"],
            "All tests with HTML report"
        )
        if returncode == 0:
            print("\n📄 HTML report generated: test_report.html")
        return returncode
    
    elif choice == "9":
        print("👋 Goodbye!")
        return 0
    
    else:
        print("❌ Invalid choice!")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)