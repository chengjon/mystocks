#!/usr/bin/env python3
"""认证和授权安全测试套件
专门测试身份认证、会话管理和访问控制的安全性
"""

from ..helpers import AuthTestResult


class AuthenticationTesterAccessControlMfaMixin:
    """AuthenticationTester 方法集 Part 3"""

    def test_access_control(self):
        """访问控制测试"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": "user1", "password": "password123"},
            )

            if response.status_code == 200:
                token = response.json().get("access_token")
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
                        ),
                    )
                elif response.status_code == 403:
                    self.results.append(
                        AuthTestResult(
                            "水平权限越权测试",
                            "访问控制",
                            "HIGH",
                            True,
                            "正确阻止水平权限越权",
                        ),
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
                        ),
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
                    ),
                )

        except Exception as error:
            self.results.append(
                AuthTestResult(
                    "水平权限越权测试",
                    "访问控制",
                    "HIGH",
                    False,
                    f"测试异常: {error!s}",
                    "检查访问控制功能",
                ),
            )

        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": "user1", "password": "password123"},
            )

            if response.status_code == 200:
                token = response.json().get("access_token")
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
                            ),
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
                        ),
                    )

        except Exception as error:
            self.results.append(
                AuthTestResult(
                    "垂直权限越权测试",
                    "访问控制",
                    "CRITICAL",
                    False,
                    f"测试异常: {error!s}",
                    "检查权限控制功能",
                ),
            )

    def test_mfa(self):
        """多因素认证测试"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": "admin", "password": "admin123"},
            )

            if response.status_code == 200:
                data = response.json()
                if "mfa_required" in data or "totp_secret" in data:
                    self.results.append(
                        AuthTestResult(
                            "MFA 可选性检查",
                            "多因素认证",
                            "MEDIUM",
                            True,
                            "支持多因素认证",
                        ),
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
                        ),
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
                    ),
                )

        except Exception as error:
            self.results.append(
                AuthTestResult(
                    "MFA 可选性检查",
                    "多因素认证",
                    "MEDIUM",
                    False,
                    f"测试失败: {error!s}",
                    "检查 MFA 功能",
                ),
            )

        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/mfa/verify",
                json={"code": "123456"},
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
                    ),
                )
            elif response.status_code == 400:
                self.results.append(
                    AuthTestResult(
                        "MFA 令牌验证测试",
                        "多因素认证",
                        "HIGH",
                        True,
                        "正确拒绝无效的 MFA 代码",
                    ),
                )
            else:
                self.results.append(
                    AuthTestResult(
                        "MFA 令牌验证测试",
                        "多因素认证",
                        "HIGH",
                        True,
                        f"MFA 验证正常 (状态码: {response.status_code})",
                    ),
                )

        except Exception as error:
            self.results.append(
                AuthTestResult(
                    "MFA 令牌验证测试",
                    "多因素认证",
                    "HIGH",
                    False,
                    f"测试失败: {error!s}",
                    "确保 MFA 功能正常",
                ),
            )
