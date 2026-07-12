#!/usr/bin/env python3
"""认证和授权安全测试套件
专门测试身份认证、会话管理和访问控制的安全性
"""

import sys
from datetime import datetime


# 设置项目路径
project_root = "/opt/claude/mystocks_spec"
sys.path.insert(0, project_root)


class AuthTestResult:
    """认证测试结果类"""

    def __init__(
        self,
        test_name: str,
        category: str,
        severity: str,
        passed: bool,
        details: str = "",
        recommendation: str = "",
    ):
        self.test_name = test_name
        self.category = category
        self.severity = severity
        self.passed = passed
        self.details = details
        self.recommendation = recommendation
        self.timestamp = datetime.now().isoformat()
