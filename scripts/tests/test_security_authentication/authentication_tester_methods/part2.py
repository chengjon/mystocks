#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证和授权安全测试套件
专门测试身份认证、会话管理和访问控制的安全性
"""

import sys
import os
import json
import time
import requests
import jwt
from datetime import datetime, timedelta
from typing import Dict, List, Any

# 设置项目路径
project_root = "/opt/claude/mystocks_spec"
sys.path.insert(0, project_root)


class AuthenticationTesterTestPasswordResetMixin:
    """AuthenticationTester 方法集 Part 2"""

    def test_password_reset(self):
        """密码重置安全测试"""
        # 1. 密码重置令牌测试
        try:
            # 请求密码重置
            response = self.session.post(
                f"{self.base_url}/api/auth/forgot-password",
                json={"email": "test@example.com"},
            )

            if response.status_code == 200:
                # 检查重置令牌是否包含可预测的信息
                data = response.json()
                if "reset_token" in data:
                    token = data["reset_token"]

                    # 检查令牌是否可预测
                    if (
                        "test@example.com" in token
                        or datetime.now().strftime("%Y%m%d") in token
                    ):
                        self.results.append(
                            AuthTestResult(
                                "密码重置令牌安全性",
                                "密码重置",
                                "HIGH",
                                False,
                                "重置令牌包含可预测的信息",
                                "使用安全的随机令牌生成",
                            )
                        )
                    else:
                        self.results.append(
                            AuthTestResult(
                                "密码重置令牌安全性",
                                "密码重置",
                                "HIGH",
                                True,
                                "重置令牌不可预测",
                            )
                        )

                    # 检查令牌过期时间
                    try:
                        # 尝试解析令牌（如果是 JWT）
                        decoded = jwt.decode(token, options={"verify_signature": False})
                        exp_time = datetime.fromtimestamp(decoded["exp"])
                        current_time = datetime.now()
                        time_to_expiry = exp_time - current_time

                        if time_to_expiry > timedelta(hours=24):
                            self.results.append(
                                AuthTestResult(
                                    "重置令牌过期时间",
                                    "密码重置",
                                    "HIGH",
                                    False,
                                    f"重置令牌过期时间过长: {time_to_expiry}",
                                    "缩短令牌过期时间",
                                )
                            )
                        elif time_to_expiry < timedelta(minutes=5):
                            self.results.append(
                                AuthTestResult(
                                    "重置令牌过期时间",
                                    "密码重置",
                                    "HIGH",
                                    False,
                                    f"重置令牌过期时间过短: {time_to_expiry}",
                                    "延长令牌过期时间",
                                )
                            )
                        else:
                            self.results.append(
                                AuthTestResult(
                                    "重置令牌过期时间",
                                    "密码重置",
                                    "HIGH",
                                    True,
                                    f"重置令牌过期时间适当: {time_to_expiry}",
                                )
                            )

                    except jwt.InvalidTokenError:
                        self.results.append(
                            AuthTestResult(
                                "重置令牌格式",
                                "密码重置",
                                "HIGH",
                                False,
                                "重置令牌格式无效",
                                "使用标准的令牌格式",
                            )
                        )
                else:
                    self.results.append(
                        AuthTestResult(
                            "密码重置令牌检查",
                            "密码重置",
                            "HIGH",
                            False,
                            "响应中未包含重置令牌",
                            "检查密码重置功能",
                        )
                    )

        except Exception as e:
            self.results.append(
                AuthTestResult(
                    "密码重置令牌测试",
                    "密码重置",
                    "HIGH",
                    False,
                    f"测试失败: {str(e)}",
                    "确保密码重置功能正常",
                )
            )

        # 2. 密码重置滥用测试
        try:
            # 尝试多次请求密码重置
            email = "test@example.com"
            requests_count = 0
            successful_requests = 0

            for i in range(5):
                response = self.session.post(
                    f"{self.base_url}/api/auth/forgot-password", json={"email": email}
                )
                requests_count += 1
                if response.status_code == 200:
                    successful_requests += 1

            # 检查速率限制
            if successful_requests >= 3:
                self.results.append(
                    AuthTestResult(
                        "密码重置速率限制",
                        "密码重置",
                        "HIGH",
                        False,
                        f"密码重置请求过多: {successful_requests}/{requests_count}",
                        "实施密码重置速率限制",
                    )
                )
            else:
                self.results.append(
                    AuthTestResult(
                        "密码重置速率限制",
                        "密码重置",
                        "HIGH",
                        True,
                        f"正确限制密码重置请求: {successful_requests}/{requests_count}",
                    )
                )

        except Exception as e:
            self.results.append(
                AuthTestResult(
                    "密码重置滥用测试",
                    "密码重置",
                    "HIGH",
                    False,
                    f"测试失败: {str(e)}",
                    "确保密码重置安全措施正常",
                )
            )

    def generate_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        report = {
            "test_summary": {
                "total_tests": len(self.results),
                "passed": sum(1 for r in self.results if r.passed),
                "failed": sum(1 for r in self.results if not r.passed),
                "test_date": datetime.now().isoformat(),
            },
            "severity_breakdown": {
                "CRITICAL": sum(
                    1 for r in self.results if r.severity == "CRITICAL" and not r.passed
                ),
                "HIGH": sum(
                    1 for r in self.results if r.severity == "HIGH" and not r.passed
                ),
                "MEDIUM": sum(
                    1 for r in self.results if r.severity == "MEDIUM" and not r.passed
                ),
                "LOW": sum(
                    1 for r in self.results if r.severity == "LOW" and not r.passed
                ),
            },
            "category_results": {},
            "detailed_findings": [],
        }

        # 按类别分组结果
        for result in self.results:
            if result.category not in report["category_results"]:
                report["category_results"][result.category] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                }

            report["category_results"][result.category]["total"] += 1
            if result.passed:
                report["category_results"][result.category]["passed"] += 1
            else:
                report["category_results"][result.category]["failed"] += 1

        # 添加详细发现
        for result in self.results:
            if not result.passed:
                report["detailed_findings"].append(
                    {
                        "test_name": result.test_name,
                        "category": result.category,
                        "severity": result.severity,
                        "details": result.details,
                        "recommendation": result.recommendation,
                        "timestamp": result.timestamp,
                    }
                )

        return report

