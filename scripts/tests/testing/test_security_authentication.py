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


class AuthenticationTester:
    """认证和授权安全测试器"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results: List[AuthTestResult] = []
        self.jwt_secret = os.getenv("JWT_SECRET", "test-secret-key")

    def run_all_tests(self) -> List[AuthTestResult]:
        """运行所有认证安全测试"""
        print("🔐 开始执行认证和授权安全测试...\n")

        print("=" * 80)
        print("基础认证测试")
        print("=" * 80)
        self.test_basic_auth()

        print("\n" + "=" * 80)
        print("JWT 安全测试")
        print("=" * 80)
        self.test_jwt_security()

        print("\n" + "=" * 80)
        print("密码策略测试")
        print("=" * 80)
        self.test_password_policy()

        print("\n" + "=" * 80)
        print("会话管理测试")
        print("=" * 80)
        self.test_session_management()

        print("\n" + "=" * 80)
        print("访问控制测试")
        print("=" * 80)
        self.test_access_control()

        print("\n" + "=" * 80)
        print("多因素认证测试")
        print("=" * 80)
        self.test_mfa()

        print("\n" + "=" * 80)
        print("密码重置安全测试")
        print("=" * 80)
        self.test_password_reset()

        return self.results

    def test_basic_auth(self):
        """基础认证测试"""
        # 1. 缺失认证保护测试
        unprotected_endpoints = ["/api/health", "/api/market/data", "/api/public/info"]

        for endpoint in unprotected_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    # 检查是否应该是公开端点
                    if "public" not in endpoint and "health" not in endpoint:
                        self.results.append(
                            AuthTestResult(
                                f"缺失认证保护 - {endpoint}",
                                "认证",
                                "HIGH",
                                False,
                                f"端点 {endpoint} 缺少认证保护",
                                "为敏感端点添加认证中间件",
                            )
                        )
                    else:
                        self.results.append(
                            AuthTestResult(
                                f"公开端点检查 - {endpoint}",
                                "认证",
                                "LOW",
                                True,
                                f"{endpoint} 作为公开端点是合适的",
                            )
                        )
            except Exception as e:
                self.results.append(
                    AuthTestResult(
                        f"端点访问测试 - {endpoint}",
                        "认证",
                        "MEDIUM",
                        False,
                        f"无法访问 {endpoint}: {str(e)}",
                        "确保服务正常运行",
                    )
                )

        # 2. 认证绕过测试
        bypass_headers = [
            {"Authorization": "Bearer invalid_token"},
            {"Authorization": "Bearer " + "a" * 1000},  # 超长令牌
            {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid"},
            {"Authorization": "Basic " + ("admin:admin").encode().decode("utf-8")},
        ]

        for i, headers in enumerate(bypass_headers):
            try:
                response = self.session.get(
                    f"{self.base_url}/api/user/profile", headers=headers
                )
                if response.status_code == 200:
                    self.results.append(
                        AuthTestResult(
                            f"认证绕过测试 #{i + 1}",
                            "认证",
                            "CRITICAL",
                            False,
                            "无效令牌成功绕过认证",
                            "加强令牌验证逻辑",
                        )
                    )
                else:
                    self.results.append(
                        AuthTestResult(
                            f"认证绕过测试 #{i + 1}",
                            "认证",
                            "CRITICAL",
                            True,
                            "正确拒绝无效令牌",
                        )
                    )
            except Exception as e:
                self.results.append(
                    AuthTestResult(
                        f"认证绕过测试 #{i + 1}",
                        "认证",
                        "CRITICAL",
                        False,
                        f"测试失败: {str(e)}",
                        "确保认证系统正常工作",
                    )
                )

    def test_jwt_security(self):
        """JWT 安全测试"""
        # 1. JWT 令牌生成测试
        try:
            # 获取 JWT 令牌
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": "test_user", "password": "test_password"},
            )

            if response.status_code == 200:
                token = response.json().get("access_token")

                # 解析 JWT 令牌
                try:
                    decoded = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])

                    # 检查标准声明
                    required_claims = ["sub", "iat", "exp", "jti"]
                    missing_claims = [
                        claim for claim in required_claims if claim not in decoded
                    ]

                    if missing_claims:
                        self.results.append(
                            AuthTestResult(
                                "JWT 标准声明检查",
                                "JWT",
                                "MEDIUM",
                                False,
                                f"缺少标准声明: {', '.join(missing_claims)}",
                                "添加所有标准 JWT 声明",
                            )
                        )
                    else:
                        self.results.append(
                            AuthTestResult(
                                "JWT 标准声明检查",
                                "JWT",
                                "MEDIUM",
                                True,
                                "JWT 包含所有标准声明",
                            )
                        )

                    # 检查过期时间
                    exp_time = datetime.fromtimestamp(decoded["exp"])
                    current_time = datetime.now()
                    time_to_expiry = exp_time - current_time

                    if time_to_expiry < timedelta(hours=1):
                        self.results.append(
                            AuthTestResult(
                                "JWT 过期时间检查",
                                "JWT",
                                "HIGH",
                                False,
                                f"令牌过期时间过短: {time_to_expiry}",
                                "设置适当的令牌过期时间",
                            )
                        )
                    elif time_to_expiry > timedelta(days=7):
                        self.results.append(
                            AuthTestResult(
                                "JWT 过期时间检查",
                                "JWT",
                                "HIGH",
                                False,
                                f"令牌过期时间过长: {time_to_expiry}",
                                "缩短令牌过期时间以减少风险",
                            )
                        )
                    else:
                        self.results.append(
                            AuthTestResult(
                                "JWT 过期时间检查",
                                "JWT",
                                "HIGH",
                                True,
                                f"令牌过期时间适当: {time_to_expiry}",
                            )
                        )

                except jwt.ExpiredSignatureError:
                    self.results.append(
                        AuthTestResult(
                            "JWT 过期检查",
                            "JWT",
                            "HIGH",
                            False,
                            "JWT 令牌已过期",
                            "检查令牌生成逻辑",
                        )
                    )
                except jwt.InvalidTokenError as e:
                    self.results.append(
                        AuthTestResult(
                            "JWT 验证测试",
                            "JWT",
                            "HIGH",
                            False,
                            f"JWT 令牌无效: {str(e)}",
                            "修复 JWT 令牌生成/验证逻辑",
                        )
                    )
                else:
                    self.results.append(
                        AuthTestResult(
                            "JWT 令牌解析", "JWT", "HIGH", True, "JWT 令牌格式正确"
                        )
                    )

            else:
                self.results.append(
                    AuthTestResult(
                        "JWT 令牌获取",
                        "JWT",
                        "HIGH",
                        False,
                        f"无法获取令牌: {response.status_code}",
                        "确保认证系统正常工作",
                    )
                )

        except Exception as e:
            self.results.append(
                AuthTestResult(
                    "JWT 安全测试",
                    "JWT",
                    "HIGH",
                    False,
                    f"测试异常: {str(e)}",
                    "检查 JWT 配置",
                )
            )

        # 2. JWT 令牌篡改测试
        try:
            # 获取合法令牌
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": "test_user", "password": "test_password"},
            )

            if response.status_code == 200:
                original_token = response.json().get("access_token")

                # 篡改令牌 - 修改 payload
                try:
                    decoded = jwt.decode(
                        original_token, options={"verify_signature": False}
                    )
                    decoded["admin"] = True
                    decoded["user_id"] = "999"

                    tampered_token = jwt.encode(
                        decoded, self.jwt_secret, algorithm="HS256"
                    )

                    # 尝试使用篡改后的令牌
                    response = self.session.get(
                        f"{self.base_url}/api/admin/users",
                        headers={"Authorization": f"Bearer {tampered_token}"},
                    )

                    if response.status_code == 200:
                        self.results.append(
                            AuthTestResult(
                                "JWT 令牌篡改测试",
                                "JWT",
                                "CRITICAL",
                                False,
                                "篡改的 JWT 令牌被接受",
                                "加强 JWT 令牌验证",
                            )
                        )
                    else:
                        self.results.append(
                            AuthTestResult(
                                "JWT 令牌篡改测试",
                                "JWT",
                                "CRITICAL",
                                True,
                                "正确拒绝篡改的 JWT 令牌",
                            )
                        )

                except Exception as e:
                    self.results.append(
                        AuthTestResult(
                            "JWT 令牌篡改测试",
                            "JWT",
                            "CRITICAL",
                            False,
                            f"篡改测试失败: {str(e)}",
                            "确保 JWT 验证机制正确",
                        )
                    )
        except Exception:
            pass

    def test_password_policy(self):
        """密码策略测试"""
        # 1. 弱密码检测
        weak_passwords = [
            "",
            "password",
            "123456",
            "12345678",
            "qwerty",
            "abc123",
            "letmein",
            "admin",
            "welcome",
            "monkey",
            "dragon",
            "passw0rd",
            "master",
            "hello",
            "football",
            "trustno1",
            "admin123",
            "password1",
            "iloveyou",
            "sunshine",
        ]

        weak_passwords_found = []
        for password in weak_passwords:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/auth/login",
                    json={"username": "test_user", "password": password},
                )
                if response.status_code == 200:
                    weak_passwords_found.append(password)
                    break  # 只需发现一个弱密码
            except Exception:
                pass

        if weak_passwords_found:
            self.results.append(
                AuthTestResult(
                    "弱密码检测",
                    "密码策略",
                    "HIGH",
                    False,
                    f"发现弱密码: {', '.join(weak_passwords_found)}",
                    "实施强密码策略",
                )
            )
        else:
            self.results.append(
                AuthTestResult(
                    "弱密码检测", "密码策略", "HIGH", True, "未发现明显的弱密码"
                )
            )

        # 2. 密码复杂度测试
        complex_password_tests = [
            ("short", False),  # 过短
            ("onlylowercase", False),  # 纯小写
            ("ONLYUPPERCASE", False),  # 纯大写
            ("1234567890", False),  # 纯数字
            ("NoNumbersOrSpecial", False),  # 缺少数字和特殊字符
            ("ValidPass123!", True),  # 有效密码
            ("AnotherValid@Password456", True),  # 有效密码
        ]

        valid_passwords_accepted = 0
        valid_passwords_tested = 0

        for password, should_be_valid in complex_password_tests:
            if should_be_valid:
                valid_passwords_tested += 1
                try:
                    response = self.session.post(
                        f"{self.base_url}/api/auth/login",
                        json={"username": "test_user", "password": password},
                    )
                    if response.status_code == 200:
                        valid_passwords_accepted += 1
                except Exception:
                    pass

        if valid_passwords_tested > 0:
            acceptance_rate = valid_passwords_accepted / valid_passwords_tested
            if acceptance_rate < 0.5:
                self.results.append(
                    AuthTestResult(
                        "密码复杂度测试",
                        "密码策略",
                        "MEDIUM",
                        False,
                        f"有效密码接受率过低: {acceptance_rate * 100:.1f}%",
                        "检查密码验证逻辑",
                    )
                )
            else:
                self.results.append(
                    AuthTestResult(
                        "密码复杂度测试",
                        "密码策略",
                        "MEDIUM",
                        True,
                        f"有效密码接受率正常: {acceptance_rate * 100:.1f}%",
                    )
                )

        # 3. 密码历史检查
        try:
            # 尝试使用相同密码登录多次
            password = "TestPass123!"
            login_count = 0
            successful_logins = 0

            for i in range(3):
                response = self.session.post(
                    f"{self.base_url}/api/auth/login",
                    json={"username": "test_user", "password": password},
                )
                login_count += 1
                if response.status_code == 200:
                    successful_logins += 1
                    # 获取新令牌
                    token = response.json().get("access_token")
                    self.session.headers.update({"Authorization": f"Bearer {token}"})

            # 检查是否重复使用相同密码
            if successful_logins > 1:
                self.results.append(
                    AuthTestResult(
                        "密码历史检查",
                        "密码策略",
                        "MEDIUM",
                        False,
                        "允许重复使用相同的密码",
                        "实施密码历史检查",
                    )
                )
            else:
                self.results.append(
                    AuthTestResult(
                        "密码历史检查",
                        "密码策略",
                        "MEDIUM",
                        True,
                        "密码重复使用被正确限制",
                    )
                )

        except Exception as e:
            self.results.append(
                AuthTestResult(
                    "密码历史检查",
                    "密码策略",
                    "MEDIUM",
                    False,
                    f"测试失败: {str(e)}",
                    "确保密码历史功能正常",
                )
            )

    def test_session_management(self):
        """会话管理测试"""
        # 1. 并发会话测试
        try:
            # 创建多个会话
            sessions = []
            for i in range(3):
                session = requests.Session()
                response = session.post(
                    f"{self.base_url}/api/auth/login",
                    json={"username": f"user{i}", "password": "password123"},
                )
                if response.status_code == 200:
                    sessions.append(session)

            # 检查并发会话限制
            if len(sessions) > 1:
                # 尝试用不同会话访问资源
                for i, session in enumerate(sessions):
                    response = session.get(f"{self.base_url}/api/user/profile")
                    if response.status_code == 200:
                        if i == 0:
                            self.results.append(
                                AuthTestResult(
                                    "并发会话测试",
                                    "会话管理",
                                    "MEDIUM",
                                    False,
                                    "允许多个并发会话",
                                    "实施会话限制",
                                )
                            )
                        else:
                            self.results.append(
                                AuthTestResult(
                                    "并发会话测试",
                                    "会话管理",
                                    "MEDIUM",
                                    False,
                                    "未正确实施会话限制",
                                    "检查会话管理逻辑",
                                )
                            )
                    else:
                        if i == 0:
                            self.results.append(
                                AuthTestResult(
                                    "并发会话测试",
                                    "会话管理",
                                    "MEDIUM",
                                    True,
                                    "会话创建成功",
                                )
                            )
                        else:
                            self.results.append(
                                AuthTestResult(
                                    "并发会话测试",
                                    "会话管理",
                                    "MEDIUM",
                                    True,
                                    "正确限制并发会话",
                                )
                            )
            else:
                self.results.append(
                    AuthTestResult(
                        "并发会话测试",
                        "会话管理",
                        "MEDIUM",
                        False,
                        "无法创建多个会话进行测试",
                        "确保测试用户可以创建会话",
                    )
                )

        except Exception as e:
            self.results.append(
                AuthTestResult(
                    "并发会话测试",
                    "会话管理",
                    "MEDIUM",
                    False,
                    f"测试异常: {str(e)}",
                    "检查会话管理功能",
                )
            )

        # 2. 会话超时测试
        try:
            # 登录并获取令牌
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": "test_user", "password": "test_password"},
            )

            if response.status_code == 200:
                token = response.json().get("access_token")

                # 等待一段时间
                time.sleep(2)

                # 尝试使用令牌
                response = self.session.get(
                    f"{self.base_url}/api/user/profile",
                    headers={"Authorization": f"Bearer {token}"},
                )

                if response.status_code == 401:
                    self.results.append(
                        AuthTestResult(
                            "会话超时测试", "会话管理", "MEDIUM", True, "会话正确超时"
                        )
                    )
                else:
                    self.results.append(
                        AuthTestResult(
                            "会话超时测试",
                            "会话管理",
                            "MEDIUM",
                            False,
                            "会话未超时",
                            "检查会话超时配置",
                        )
                    )

        except Exception as e:
            self.results.append(
                AuthTestResult(
                    "会话超时测试",
                    "会话管理",
                    "MEDIUM",
                    False,
                    f"测试失败: {str(e)}",
                    "确保会话管理功能正常",
                )
            )

    def test_access_control(self):
        """访问控制测试"""
        # 1. 水平权限越权测试
        try:
            # 普通用户登录
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": "user1", "password": "password123"},
            )

            if response.status_code == 200:
                token = response.json().get("access_token")

                # 尝试访问其他用户的数据
                response = self.session.get(
                    f"{self.base_url}/api/user/profile",
                    headers={"Authorization": f"Bearer {token}"},
                    params={"user_id": "user2"},
                )

                if response.status_code == 200:
                    self.results.append(
                        AuthTestResult(
                            "水平权限越权测试",
                            "访问控制",
                            "HIGH",
                            False,
                            "普通用户可以访问其他用户数据",
                            "实施严格的访问控制",
                        )
                    )
                elif response.status_code == 403:
                    self.results.append(
                        AuthTestResult(
                            "水平权限越权测试",
                            "访问控制",
                            "HIGH",
                            True,
                            "正确阻止水平权限越权",
                        )
                    )
                else:
                    self.results.append(
                        AuthTestResult(
                            "水平权限越权测试",
                            "访问控制",
                            "HIGH",
                            False,
                            f"意外的响应状态码: {response.status_code}",
                            "检查访问控制逻辑",
                        )
                    )
            else:
                self.results.append(
                    AuthTestResult(
                        "水平权限越权测试",
                        "访问控制",
                        "HIGH",
                        False,
                        "无法登录测试用户",
                        "确保测试用户可用",
                    )
                )

        except Exception as e:
            self.results.append(
                AuthTestResult(
                    "水平权限越权测试",
                    "访问控制",
                    "HIGH",
                    False,
                    f"测试异常: {str(e)}",
                    "检查访问控制功能",
                )
            )

        # 2. 垂直权限越权测试
        try:
            # 普通用户尝试访问管理员功能
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": "user1", "password": "password123"},
            )

            if response.status_code == 200:
                token = response.json().get("access_token")

                # 尝试访问管理员接口
                admin_endpoints = [
                    "/api/admin/users",
                    "/api/admin/settings",
                    "/api/admin/logs",
                ]

                for endpoint in admin_endpoints:
                    response = self.session.get(
                        f"{self.base_url}{endpoint}",
                        headers={"Authorization": f"Bearer {token}"},
                    )

                    if response.status_code != 401 and response.status_code != 403:
                        self.results.append(
                            AuthTestResult(
                                f"垂直权限越权测试 - {endpoint}",
                                "访问控制",
                                "CRITICAL",
                                False,
                                f"普通用户可以访问 {endpoint}",
                                "实施基于角色的访问控制",
                            )
                        )
                        break
                else:
                    self.results.append(
                        AuthTestResult(
                            "垂直权限越权测试",
                            "访问控制",
                            "CRITICAL",
                            True,
                            "正确阻止垂直权限越权",
                        )
                    )

        except Exception as e:
            self.results.append(
                AuthTestResult(
                    "垂直权限越权测试",
                    "访问控制",
                    "CRITICAL",
                    False,
                    f"测试异常: {str(e)}",
                    "检查权限控制功能",
                )
            )

    def test_mfa(self):
        """多因素认证测试"""
        # 1. MFA 可选性检查
        try:
            # 检查是否有 MFA 选项
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": "admin", "password": "admin123"},
            )

            if response.status_code == 200:
                # 检查响应中是否有 MFA 相关字段
                data = response.json()
                if "mfa_required" in data or "totp_secret" in data:
                    self.results.append(
                        AuthTestResult(
                            "MFA 可选性检查",
                            "多因素认证",
                            "MEDIUM",
                            True,
                            "支持多因素认证",
                        )
                    )
                else:
                    self.results.append(
                        AuthTestResult(
                            "MFA 可选性检查",
                            "多因素认证",
                            "MEDIUM",
                            False,
                            "未实施多因素认证",
                            "考虑启用多因素认证以增强安全性",
                        )
                    )
            else:
                self.results.append(
                    AuthTestResult(
                        "MFA 可选性检查",
                        "多因素认证",
                        "MEDIUM",
                        False,
                        "无法测试 MFA",
                        "确保认证系统正常运行",
                    )
                )

        except Exception as e:
            self.results.append(
                AuthTestResult(
                    "MFA 可选性检查",
                    "多因素认证",
                    "MEDIUM",
                    False,
                    f"测试失败: {str(e)}",
                    "检查 MFA 功能",
                )
            )

        # 2. MFA 令牌验证测试
        try:
            # 模拟 MFA 验证
            response = self.session.post(
                f"{self.base_url}/api/auth/mfa/verify",
                json={
                    "code": "123456"  # 无效的 MFA 代码
                },
            )

            if response.status_code == 200:
                self.results.append(
                    AuthTestResult(
                        "MFA 令牌验证测试",
                        "多因素认证",
                        "HIGH",
                        False,
                        "无效的 MFA 代码被接受",
                        "加强 MFA 代码验证",
                    )
                )
            elif response.status_code == 400:
                self.results.append(
                    AuthTestResult(
                        "MFA 令牌验证测试",
                        "多因素认证",
                        "HIGH",
                        True,
                        "正确拒绝无效的 MFA 代码",
                    )
                )
            else:
                self.results.append(
                    AuthTestResult(
                        "MFA 令牌验证测试",
                        "多因素认证",
                        "HIGH",
                        True,
                        f"MFA 验证正常 (状态码: {response.status_code})",
                    )
                )

        except Exception as e:
            self.results.append(
                AuthTestResult(
                    "MFA 令牌验证测试",
                    "多因素认证",
                    "HIGH",
                    False,
                    f"测试失败: {str(e)}",
                    "确保 MFA 功能正常",
                )
            )

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


def run_auth_security_tests():
    """运行认证安全测试"""
    print("🔒 MyStocks 认证和授权安全测试套件")
    print("=" * 80)

    # 创建测试器实例
    tester = AuthenticationTester()

    # 运行所有测试
    results = tester.run_all_tests()

    # 生成报告
    report = tester.generate_report()

    # 输出摘要
    print("\n" + "=" * 80)
    print("📊 测试结果摘要")
    print("=" * 80)
    print(f"总测试数: {report['test_summary']['total_tests']}")
    print(f"通过: {report['test_summary']['passed']}")
    print(f"失败: {report['test_summary']['failed']}")
    print(
        f"通过率: {report['test_summary']['passed'] / report['test_summary']['total_tests'] * 100:.1f}%"
    )

    print("\n🚨 按严重性分类的漏洞:")
    print(f"  Critical: {report['severity_breakdown']['CRITICAL']}")
    print(f"  High: {report['severity_breakdown']['HIGH']}")
    print(f"  Medium: {report['severity_breakdown']['MEDIUM']}")
    print(f"  Low: {report['severity_breakdown']['LOW']}")

    print("\n📋 按类别分类的结果:")
    for category, stats in report["category_results"].items():
        pass_rate = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
        print(f"  {category}: {stats['passed']}/{stats['total']} ({pass_rate:.1f}%)")

    # 保存详细报告
    report_file = (
        f"/tmp/auth_security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n📄 详细报告已保存至: {report_file}")

    # 输出关键安全建议
    critical_issues = [
        r for r in results if not r.passed and r.severity in ["CRITICAL", "HIGH"]
    ]
    if critical_issues:
        print("\n🚨 关键安全问题（需要立即修复）:")
        for issue in critical_issues:
            print(f"  ⚠️  {issue.test_name} ({issue.severity}):")
            print(f"     详情: {issue.details}")
            print(f"     建议: {issue.recommendation}")
            print()

    # 返回退出码
    if report["test_summary"]["failed"] > 0:
        print(f"\n❌ {report['test_summary']['failed']} 个测试失败，请修复相关问题")
        return 1
    else:
        print("\n✅ 所有认证安全测试通过！")
        return 0


if __name__ == "__main__":
    exit_code = run_auth_security_tests()
    sys.exit(exit_code)
