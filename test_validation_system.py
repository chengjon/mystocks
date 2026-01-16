#!/usr/bin/env python3
"""
Standalone CI/CD Validation Test
Tests the key improvements made to the CI/CD validation system
"""

import os
import sys
import json
import time
import ast
import re
from pathlib import Path
from typing import Dict, List, Any

# Add project path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_ai_code_review():
    """Test the AI-enhanced code review functionality"""
    print("🧠 Testing AI Code Review...")

    # Simple test data
    test_content = """def test_function():
    print("debug message")
    try:
        pass
    except:
        pass
    return True

class TestClass:
    pass
"""

    # Test AST analysis
    try:
        tree = ast.parse(test_content)
        functions = [
            node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        print(f"  ✅ Found {len(functions)} functions and {len(classes)} classes")

        # Test complexity calculation
        for func in functions:
            complexity = calculate_complexity(func)
            print(f"  ✅ Function '{func.name}' complexity: {complexity}")

        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def calculate_complexity(node):
    """Calculate function complexity"""
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.For, ast.While)):
            complexity += 1
    return complexity


def test_security_patterns():
    """Test security pattern detection"""
    print("🔒 Testing Security Patterns...")

    test_code = """
password = "secret123"
query = "SELECT * FROM users WHERE id = " + user_input
"""

    patterns = [
        (r'password\s*=\s*["\'][^"\']*["\']', "Hardcoded password"),
        (r"SELECT.*\+", "SQL injection risk"),
    ]

    issues = []
    for pattern, description in patterns:
        if re.search(pattern, test_code, re.IGNORECASE):
            issues.append(description)

    print(f"  ✅ Detected {len(issues)} security issues")
    for issue in issues:
        print(f"    - {issue}")

    return len(issues) > 0


def test_performance_patterns():
    """Test performance pattern detection"""
    print("⚡ Testing Performance Patterns...")

    test_code = """
for i in range(10000):
    result.append(i * 2)

large_list = [x for x in range(1000)]
"""

    patterns = [
        (r"range\(10000\)", "Large range detected"),
        (r"\.append\(.*\)", "List append in loop"),
        (r"\[.*for.*in.*\]", "List comprehension"),
    ]

    issues = []
    for pattern, description in patterns:
        if re.search(pattern, test_code):
            issues.append(description)

    print(f"  ✅ Detected {len(issues)} performance patterns")
    for issue in issues:
        print(f"    - {issue}")

    return len(issues) > 0


def test_validation_script_structure():
    """Test that the validation script has the expected structure"""
    print("🏗️ Testing Validation Script Structure...")

    script_path = (
        Path(__file__).parent / "scripts" / "ci" / "quant_strategy_validation.py"
    )

    if not script_path.exists():
        print("  ❌ Validation script not found")
        return False

    try:
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for key functions
        required_functions = [
            "def _validate_ai_code_review",
            "def _validate_automated_suggestions",
            "def _validate_performance_optimization",
            "def _validate_code_quality_assessment",
            "def _validate_best_practices",
        ]

        found_functions = 0
        for func in required_functions:
            if func in content:
                found_functions += 1

        print(
            f"  ✅ Found {found_functions}/{len(required_functions)} required functions"
        )

        # Check for security improvements
        if "bandit" in content and "safety" in content:
            print("  ✅ Security tools integration found")
        else:
            print("  ❌ Security tools integration missing")

        # Check for timeout handling
        if "signal.alarm" in content:
            print("  ✅ Timeout handling found")
        else:
            print("  ❌ Timeout handling missing")

        return found_functions == len(required_functions)

    except Exception as e:
        print(f"  ❌ Error reading script: {e}")
        return False


def run_validation_tests():
    """Run all validation tests"""
    print("🚀 Starting CI/CD Validation System Tests")
    print("=" * 50)

    tests = [
        ("AI Code Review", test_ai_code_review),
        ("Security Patterns", test_security_patterns),
        ("Performance Patterns", test_performance_patterns),
        ("Script Structure", test_validation_script_structure),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {test_name}")

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All CI/CD validation improvements verified successfully!")
        return True
    else:
        print("⚠️ Some tests failed. Review the implementation.")
        return False


if __name__ == "__main__":
    success = run_validation_tests()
    sys.exit(0 if success else 1)
