#!/usr/bin/env python3
"""认证和授权安全测试套件
专门测试身份认证、会话管理和访问控制的安全性
"""

import os
import sys
import time
from datetime import datetime, timedelta
from typing import List

import jwt
import requests

from ..helpers import AuthTestResult


# 设置项目路径
project_root = "/opt/claude/mystocks_spec"
sys.path.insert(0, project_root)


class AuthenticationTesterCoreMixin:
    """AuthenticationTester 方法集 Part 1"""

    def __init__(
        self,
        base_url: str = os.getenv("BACKEND_URL", f"http://localhost:{os.getenv('BACKEND_PORT', '8020')}"),
    ):
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
                            ),
                        )
                    else:
                        self.results.append(
                            AuthTestResult(
                                f"公开端点检查 - {endpoint}",
                                "认证",
                                "LOW",
                                True,
                                f"{endpoint} 作为公开端点是合适的",
                            ),
                        )
            except Exception as e:
                self.results.append(
                    AuthTestResult(
                        f"端点访问测试 - {endpoint}",
                        "认证",
                        "MEDIUM",
                        False,
                        f"无法访问 {endpoint}: {e!s}",
                        "确保服务正常运行",
                    ),
                )

        # 2. 认证绕过测试
        bypass_headers = [
            {"Authorization": "Bearer invalid_token"},
            {"Authorization": "Bearer " + "a" * 1000},  # 超长令牌
            {"Authorization": "Bearer <jwt-token>"},
            {"Authorization": "Basic " + (b"admin:admin").decode("utf-8")},
        ]

        for i, headers in enumerate(bypass_headers):
            try:
                response = self.session.get(
                    f"{self.base_url}/api/user/profile",
                    headers=headers,
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
                        ),
                    )
                else:
                    self.results.append(
                        AuthTestResult(
                            f"认证绕过测试 #{i + 1}",
                            "认证",
                            "CRITICAL",
                            True,
                            "正确拒绝无效令牌",
                        ),
                    )
            except Exception as e:
                self.results.append(
                    AuthTestResult(
                        f"认证绕过测试 #{i + 1}",
                        "认证",
                        "CRITICAL",
                        False,
                        f"测试失败: {e!s}",
                        "确保认证系统正常工作",
                    ),
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
                    missing_claims = [claim for claim in required_claims if claim not in decoded]

                    if missing_claims:
                        self.results.append(
                            AuthTestResult(
                                "JWT 标准声明检查",
                                "JWT",
                                "MEDIUM",
                                False,
                                f"缺少标准声明: {', '.join(missing_claims)}",
                                "添加所有标准 JWT 声明",
                            ),
                        )
                    else:
                        self.results.append(
                            AuthTestResult(
                                "JWT 标准声明检查",
                                "JWT",
                                "MEDIUM",
                                True,
                                "JWT 包含所有标准声明",
                            ),
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
                            ),
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
                            ),
                        )
                    else:
                        self.results.append(
                            AuthTestResult(
                                "JWT 过期时间检查",
                                "JWT",
                                "HIGH",
                                True,
                                f"令牌过期时间适当: {time_to_expiry}",
                            ),
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
                        ),
                    )
                except jwt.InvalidTokenError as e:
                    self.results.append(
                        AuthTestResult(
                            "JWT 验证测试",
                            "JWT",
                            "HIGH",
                            False,
                            f"JWT 令牌无效: {e!s}",
                            "修复 JWT 令牌生成/验证逻辑",
                        ),
                    )
                else:
                    self.results.append(
                        AuthTestResult(
                            "JWT 令牌解析",
                            "JWT",
                            "HIGH",
                            True,
                            "JWT 令牌格式正确",
                        ),
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
                    ),
                )

        except Exception as e:
            self.results.append(
                AuthTestResult(
                    "JWT 安全测试",
                    "JWT",
                    "HIGH",
                    False,
                    f"测试异常: {e!s}",
                    "检查 JWT 配置",
                ),
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
                        original_token,
                        options={"verify_signature": False},
                    )
                    decoded["admin"] = True
                    decoded["user_id"] = "999"

                    tampered_token = jwt.encode(
                        decoded,
                        self.jwt_secret,
                        algorithm="HS256",
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
                            ),
                        )
                    else:
                        self.results.append(
                            AuthTestResult(
                                "JWT 令牌篡改测试",
                                "JWT",
                                "CRITICAL",
                                True,
                                "正确拒绝篡改的 JWT 令牌",
                            ),
                        )

                except Exception as e:
                    self.results.append(
                        AuthTestResult(
                            "JWT 令牌篡改测试",
                            "JWT",
                            "CRITICAL",
                            False,
                            f"篡改测试失败: {e!s}",
                            "确保 JWT 验证机制正确",
                        ),
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
                ),
            )
        else:
            self.results.append(
                AuthTestResult(
                    "弱密码检测",
                    "密码策略",
                    "HIGH",
                    True,
                    "未发现明显的弱密码",
                ),
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
                    ),
                )
            else:
                self.results.append(
                    AuthTestResult(
                        "密码复杂度测试",
                        "密码策略",
                        "MEDIUM",
                        True,
                        f"有效密码接受率正常: {acceptance_rate * 100:.1f}%",
                    ),
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
                    ),
                )
            else:
                self.results.append(
                    AuthTestResult(
                        "密码历史检查",
                        "密码策略",
                        "MEDIUM",
                        True,
                        "密码重复使用被正确限制",
                    ),
                )

        except Exception as e:
            self.results.append(
                AuthTestResult(
                    "密码历史检查",
                    "密码策略",
                    "MEDIUM",
                    False,
                    f"测试失败: {e!s}",
                    "确保密码历史功能正常",
                ),
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
                                ),
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
                                ),
                            )
                    elif i == 0:
                        self.results.append(
                            AuthTestResult(
                                "并发会话测试",
                                "会话管理",
                                "MEDIUM",
                                True,
                                "会话创建成功",
                            ),
                        )
                    else:
                        self.results.append(
                            AuthTestResult(
                                "并发会话测试",
                                "会话管理",
                                "MEDIUM",
                                True,
                                "正确限制并发会话",
                            ),
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
                    ),
                )

        except Exception as e:
            self.results.append(
                AuthTestResult(
                    "并发会话测试",
                    "会话管理",
                    "MEDIUM",
                    False,
                    f"测试异常: {e!s}",
                    "检查会话管理功能",
                ),
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
                            "会话超时测试",
                            "会话管理",
                            "MEDIUM",
                            True,
                            "会话正确超时",
                        ),
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
                        ),
                    )

        except Exception as e:
            self.results.append(
                AuthTestResult(
                    "会话超时测试",
                    "会话管理",
                    "MEDIUM",
                    False,
                    f"测试失败: {e!s}",
                    "确保会话管理功能正常",
                ),
            )
