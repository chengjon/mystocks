"""
Regression tests for APIHealthChecker.generate_report
"""

import sys
import os
from unittest.mock import patch, MagicMock
import pytest
import io

# Add source path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

from src.utils.check_api_health_v2 import APIHealthChecker


def test_generate_report_output_consistency():
    """Test if generate_report produces expected summary info"""
    checker = APIHealthChecker()
    checker.results = [
        {"name": "Test 1", "status": "PASS", "priority": "P1", "response_time": 100},
        {"name": "Test 2", "status": "FAIL", "priority": "P1", "response_time": 200},
        {"name": "TDX Test", "status": "PASS", "priority": "P2", "response_time": 150},
    ]

    # Capture stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output

    try:
        checker.generate_report()
    finally:
        sys.stdout = sys.__stdout__

    output = captured_output.getvalue()

    # Verify key stats are present
    assert "总测试数: 3" in output
    assert "通过: 2" in output
    assert "失败: 1" in output
    assert "P1: 1/2" in output
    assert "P2: 1/1" in output
    assert "响应时间统计" in output
    assert (
        "平均: 125ms" in output
    )  # Only PASS results are counted for response time stats in original code
