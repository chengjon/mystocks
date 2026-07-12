#!/usr/bin/env python3
"""OWASP Top 10 安全测试套件
实现针对 OWASP Top 10 2017/2021 的自动化安全测试
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests

from scripts._test_security_owasp_top10_tail import (
    owasp_generate_report,
    owasp_has_valid_session,
    owasp_test_ssrf,
)
from scripts._test_security_owasp_top10_tail import (
    run_owasp_security_tests as run_owasp_security_tests_helper,
)


# 设置项目路径
project_root = "/opt/claude/mystocks_spec"
sys.path.insert(0, project_root)


class SecurityTestResult:
    """安全测试结果类"""

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


class OWASPSecurityTester:
    """OWASP Top 10 安全测试器"""

    def __init__(self):
        self.base_url = os.getenv("BACKEND_URL", f"http://localhost:{os.getenv('BACKEND_PORT', '8020')}")
        self.results: List[SecurityTestResult] = []
        self.security_headers = {}
        self.session = requests.Session()

    def run_all_tests(self) -> List[SecurityTestResult]:
        """运行所有 OWASP Top 10 测试"""
        print("开始执行 OWASP Top 10 安全测试套件...\n")

        # OWASP Top 10 2021 测试
        print("=" * 80)
        print("A01:2021 - 访问控制失效 (Broken Access Control)")
        print("=" * 80)
        self.test_broken_access_control()

        print("\n" + "=" * 80)
        print("A02:2021 - 加密机制失效 (Cryptographic Failures)")
        print("=" * 80)
        self.test_cryptographic_failures()

        print("\n" + "=" * 80)
        print("A03:2021 - 注入 (Injection)")
        print("=" * 80)
        self.test_injection()

        print("\n" + "=" * 80)
        print("A04:2021 - 不安全设计 (Insecure Design)")
        print("=" * 80)
        self.test_insecure_design()

        print("\n" + "=" * 80)
        print("A05:2021 - 安全配置错误 (Security Misconfiguration)")
        print("=" * 80)
        self.test_security_misconfiguration()

        print("\n" + "=" * 80)
        print("A06:2021 - 脆弱和过时的组件 (Vulnerable and Outdated Components)")
        print("=" * 80)
        self.test_vulnerable_components()

        print("\n" + "=" * 80)
        print("A07:2021 - 身份认证失效 (Identification and Authentication Failures)")
        print("=" * 80)
        self.test_auth_failures()

        print("\n" + "=" * 80)
        print("A08:2021 - 软件和数据完整性失效 (Software and Data Integrity Failures)")
        print("=" * 80)
        self.test_data_integrity()

        print("\n" + "=" * 80)
        print(
            "A09:2021 - 安全日志和监控失效 (Security Logging and Monitoring Failures)",
        )
        print("=" * 80)
        self.test_security_logging()

        print("\n" + "=" * 80)
        print("A10:2021 - 服务端请求伪造 (Server-Side Request Forgery)")
        print("=" * 80)
        self.test_ssrf()

        return self.results

    def test_broken_access_control(self):
        """测试访问控制失效"""
        # 1. 未授权访问管理员接口
        try:
            response = self.session.get(f"{self.base_url}/api/admin/users")
            if response.status_code != 401 and response.status_code != 403:
                self.results.append(
                    SecurityTestResult(
                        "未授权访问管理员接口",
                        "A01:2021",
                        "HIGH",
                        False,
                        f"状态码: {response.status_code}",
                        "实施适当的访问控制和认证",
                    ),
                )
            else:
                self.results.append(
                    SecurityTestResult(
                        "未授权访问管理员接口",
                        "A01:2021",
                        "HIGH",
                        True,
                        "正确返回 401/403",
                    ),
                )
        except Exception as e:
            self.results.append(
                SecurityTestResult(
                    "未授权访问管理员接口",
                    "A01:2021",
                    "HIGH",
                    False,
                    f"连接失败: {e!s}",
                    "确保服务正在运行",
                ),
            )

        # 2. 权限提升测试
        if self._has_valid_session():
            # 尝试升级权限
            response = self.session.post(
                f"{self.base_url}/api/admin/users",
                json={"action": "promote"},
            )
            if response.status_code == 200:
                self.results.append(
                    SecurityTestResult(
                        "权限提升测试",
                        "A01:2021",
                        "CRITICAL",
                        False,
                        "成功执行提升权限操作",
                        "实施基于角色的访问控制(RBAC)",
                    ),
                )
            else:
                self.results.append(
                    SecurityTestResult(
                        "权限提升测试",
                        "A01:2021",
                        "CRITICAL",
                        True,
                        "权限提升被阻止",
                    ),
                )

    def test_cryptographic_failures(self):
        """测试加密机制失效"""
        # 1. 检查 HTTPS 强制
        try:
            response = requests.get(
                f"{self.base_url.replace('http', 'https')}/api/health",
                timeout=5,
            )
            if response.status_code == 200:
                self.results.append(
                    SecurityTestResult(
                        "HTTPS 强制检查",
                        "A02:2021",
                        "HIGH",
                        True,
                        "正确强制 HTTPS",
                    ),
                )
            else:
                self.results.append(
                    SecurityTestResult(
                        "HTTPS 强制检查",
                        "A02:2021",
                        "MEDIUM",
                        False,
                        "HTTPS 可用但未强制",
                        "配置中间件强制 HTTPS",
                    ),
                )
        except requests.exceptions.SSLError:
            self.results.append(
                SecurityTestResult(
                    "HTTPS 强制检查",
                    "A02:2021",
                    "HIGH",
                    False,
                    "不支持 HTTPS",
                    "配置 SSL 证书",
                ),
            )
        except requests.exceptions.Timeout:
            self.results.append(
                SecurityTestResult(
                    "HTTPS 强制检查",
                    "A02:2021",
                    "MEDIUM",
                    False,
                    "HTTPS 超时",
                    "检查 SSL 配置",
                ),
            )

        # 2. 密码强度测试
        weak_passwords = ["password", "123456", "admin", "qwerty", "111111"]
        for password in weak_passwords:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": "test_user", "password": password},
            )
            if response.status_code == 200:
                self.results.append(
                    SecurityTestResult(
                        "密码强度测试",
                        "A02:2021",
                        "MEDIUM",
                        False,
                        f"弱密码 '{password}' 被接受",
                        "实施密码复杂度策略",
                    ),
                )
                break

    def test_injection(self):
        """测试注入攻击"""
        # 1. SQL 注入测试
        sql_injection_payloads = [
            "' OR '1'='1",
            "' UNION SELECT NULL--",
            "'; DROP TABLE users--",
            "admin'--",
        ]

        for payload in sql_injection_payloads:
            try:
                response = self.session.get(
                    f"{self.base_url}/api/market/data",
                    params={"symbol": payload, "limit": 10},
                )
                # 检查是否返回错误或包含注入内容
                if "sql" in response.text.lower() or "error" in response.text.lower():
                    self.results.append(
                        SecurityTestResult(
                            f"SQL 注入检测 - {payload}",
                            "A03:2021",
                            "HIGH",
                            False,
                            "可能存在 SQL 注入漏洞",
                            "使用参数化查询和 ORM",
                        ),
                    )
                    break
            except Exception:
                pass

        # 2. XSS 测试
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
        ]

        for payload in xss_payloads:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/feedback",
                    json={"message": payload},
                )
                # 检查响应中是否包含转义后的 payload
                if payload not in response.text and "alert" not in response.text:
                    self.results.append(
                        SecurityTestResult(
                            f"XSS 防护测试 - {payload}",
                            "A03:2021",
                            "MEDIUM",
                            True,
                            "XSS 载荷被正确处理",
                        ),
                    )
                else:
                    self.results.append(
                        SecurityTestResult(
                            f"XSS 防护测试 - {payload}",
                            "A03:2021",
                            "MEDIUM",
                            False,
                            "XSS 载荷未被处理",
                            "实施输出编码和 CSP",
                        ),
                    )
            except Exception:
                pass

    def test_insecure_design(self):
        """测试不安全设计"""
        # 1. 检查 API 版本控制
        api_endpoints = ["/api/v1/", "/api/v2/"]
        versioning_found = False

        for endpoint in api_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}/health")
                if response.status_code == 200:
                    versioning_found = True
                    break
            except Exception:
                pass

        if not versioning_found:
            self.results.append(
                SecurityTestResult(
                    "API 版本控制",
                    "A04:2021",
                    "MEDIUM",
                    False,
                    "未实施 API 版本控制",
                    "添加版本控制以支持向后兼容",
                ),
            )
        else:
            self.results.append(
                SecurityTestResult(
                    "API 版本控制",
                    "A04:2021",
                    "MEDIUM",
                    True,
                    "API 版本控制已实现",
                ),
            )

        # 2. 检查速率限制
        rapid_requests = []
        for i in range(10):
            rapid_requests.append(self.session.get(f"{self.base_url}/api/market/data"))

        failed_requests = sum(1 for r in rapid_requests if r.status_code == 429)
        if failed_requests < 3:
            self.results.append(
                SecurityTestResult(
                    "速率限制",
                    "A04:2021",
                    "MEDIUM",
                    False,
                    f"仅 {failed_requests} 个请求被限制",
                    "实施 API 速率限制",
                ),
            )
        else:
            self.results.append(
                SecurityTestResult(
                    "速率限制",
                    "A04:2021",
                    "MEDIUM",
                    True,
                    f"正确限制 {failed_requests} 个请求",
                ),
            )

    def test_security_misconfiguration(self):
        """测试安全配置错误"""
        # 1. 检查安全头
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            self.security_headers = response.headers

            required_headers = [
                ("X-Content-Type-Options", "nosniff"),
                ("X-Frame-Options", "DENY"),
                ("X-XSS-Protection", "1; mode=block"),
                ("Strict-Transport-Security", "max-age=31536000"),
                ("Content-Security-Policy", "default-src 'self'"),
            ]

            for header, expected_value in required_headers:
                if header not in response.headers:
                    self.results.append(
                        SecurityTestResult(
                            f"安全头缺失 - {header}",
                            "A05:2021",
                            "MEDIUM",
                            False,
                            f"缺少 {header}",
                            "配置安全 HTTP 头",
                        ),
                    )
                else:
                    self.results.append(
                        SecurityTestResult(
                            f"安全头检查 - {header}",
                            "A05:2021",
                            "MEDIUM",
                            True,
                            f"{header} 已设置",
                        ),
                    )
        except Exception as e:
            self.results.append(
                SecurityTestResult(
                    "安全头检查",
                    "A05:2021",
                    "MEDIUM",
                    False,
                    f"无法获取响应头: {e!s}",
                    "确保 API 服务正常运行",
                ),
            )

        # 2. 检查调试模式
        try:
            response = self.session.get(f"{self.base_url}/api/debug")
            if response.status_code == 200:
                self.results.append(
                    SecurityTestResult(
                        "调试模式检查",
                        "A05:2021",
                        "HIGH",
                        False,
                        "调试接口可访问",
                        "禁用生产环境的调试功能",
                    ),
                )
        except Exception:
            self.results.append(
                SecurityTestResult(
                    "调试模式检查",
                    "A05:2021",
                    "HIGH",
                    True,
                    "调试接口不可访问",
                ),
            )

    def test_vulnerable_components(self):
        """测试脆弱组件"""
        # 1. 依赖项扫描
        try:
            # 检查 requirements.txt
            req_file = Path(project_root) / "web/backend/requirements.txt"
            if req_file.exists():
                with open(req_file) as f:
                    dependencies = f.read()

                # 查找可能过时的包
                outdated_patterns = [
                    "requests<2.25.0",
                    "django<3.2.0",
                    "flask<2.0.0",
                    "sqlalchemy<1.4.0",
                ]

                for pattern in outdated_patterns:
                    if pattern in dependencies:
                        self.results.append(
                            SecurityTestResult(
                                "过时依赖检查",
                                "A06:2021",
                                "MEDIUM",
                                False,
                                f"发现过时的依赖模式: {pattern}",
                                "更新到最新稳定版本",
                            ),
                        )

                self.results.append(
                    SecurityTestResult(
                        "依赖项扫描",
                        "A06:2021",
                        "MEDIUM",
                        True,
                        f"扫描了 {len(dependencies.splitlines())} 个依赖项",
                    ),
                )
        except Exception as e:
            self.results.append(
                SecurityTestResult(
                    "依赖项扫描",
                    "A06:2021",
                    "MEDIUM",
                    False,
                    f"扫描失败: {e!s}",
                    "确保 requirements.txt 存在并可读",
                ),
            )

        # 2. 检查已知漏洞
        try:
            # 模拟漏洞检查（实际使用时集成 Safety 或 Trivy）
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                # 检查 Python 版本
                python_version = sys.version_info
                if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
                    self.results.append(
                        SecurityTestResult(
                            "Python 版本检查",
                            "A06:2021",
                            "HIGH",
                            False,
                            f"过时的 Python 版本: {python_version.major}.{python_version.minor}",
                            "升级到 Python 3.8+",
                        ),
                    )
                else:
                    self.results.append(
                        SecurityTestResult(
                            "Python 版本检查",
                            "A06:2021",
                            "HIGH",
                            True,
                            f"Python 版本符合要求: {python_version.major}.{python_version.minor}",
                        ),
                    )
        except Exception as e:
            self.results.append(
                SecurityTestResult(
                    "Python 版本检查",
                    "A06:2021",
                    "HIGH",
                    False,
                    f"检查失败: {e!s}",
                    "确保 Python 环境正确配置",
                ),
            )

    def test_auth_failures(self):
        """测试身份认证失效"""
        # 1. 弱密码测试
        weak_credentials = [
            ("admin", "admin"),
            ("admin", "password"),
            ("admin", "123456"),
            ("administrator", "administrator"),
            ("root", "root"),
        ]

        for username, password in weak_credentials:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/auth/login",
                    json={"username": username, "password": password},
                )
                if response.status_code == 200:
                    self.results.append(
                        SecurityTestResult(
                            "弱密码测试",
                            "A07:2021",
                            "CRITICAL",
                            False,
                            f"弱凭证 {username}/{password} 成功登录",
                            "实施强密码策略和账户锁定",
                        ),
                    )
                    break
            except Exception:
                pass

        # 2. 会话管理测试
        if self._has_valid_session():
            # 测试会话超时
            time.sleep(1)  # 短暂等待

            # 尝试使用之前的令牌
            response = self.session.get(f"{self.base_url}/api/user/profile")
            if response.status_code == 200:
                self.results.append(
                    SecurityTestResult(
                        "会话管理测试",
                        "A07:2021",
                        "MEDIUM",
                        True,
                        "会话管理正常",
                    ),
                )
            else:
                self.results.append(
                    SecurityTestResult(
                        "会话管理测试",
                        "A07:2021",
                        "MEDIUM",
                        False,
                        "会话过早过期",
                        "检查会话超时配置",
                    ),
                )

    def test_data_integrity(self):
        """测试数据完整性失效"""
        # 1. 检查文件上传安全性
        try:
            # 测试恶意文件上传
            files = {
                "file": (
                    "malicious.php",
                    '<?php system($_GET["cmd"]); ?>',
                    "application/php",
                ),
            }
            response = self.session.post(f"{self.base_url}/api/upload", files=files)

            if response.status_code == 200:
                self.results.append(
                    SecurityTestResult(
                        "文件上传安全",
                        "A08:2021",
                        "HIGH",
                        False,
                        "恶意文件上传被允许",
                        "实施文件类型验证和病毒扫描",
                    ),
                )
            else:
                self.results.append(
                    SecurityTestResult(
                        "文件上传安全",
                        "A08:2021",
                        "HIGH",
                        True,
                        "恶意文件上传被拒绝",
                    ),
                )
        except Exception:
            self.results.append(
                SecurityTestResult(
                    "文件上传安全",
                    "A08:2021",
                    "HIGH",
                    False,
                    "文件上传接口不可用",
                    "确保上传功能正确配置",
                ),
            )

        # 2. 检查数据传输安全
        try:
            response = self.session.post(
                f"{self.base_url}/api/trading/order",
                json={"symbol": "AAPL", "quantity": 100, "price": 150.0},
            )

            if "https://" in str(response.request.url):
                self.results.append(
                    SecurityTestResult(
                        "数据传输安全",
                        "A08:2021",
                        "HIGH",
                        True,
                        "使用 HTTPS 传输数据",
                    ),
                )
            else:
                self.results.append(
                    SecurityTestResult(
                        "数据传输安全",
                        "A08:2021",
                        "HIGH",
                        False,
                        "使用 HTTP 传输敏感数据",
                        "强制使用 HTTPS",
                    ),
                )
        except Exception as e:
            self.results.append(
                SecurityTestResult(
                    "数据传输安全",
                    "A08:2021",
                    "HIGH",
                    False,
                    f"检查失败: {e!s}",
                    "确保 HTTPS 配置正确",
                ),
            )

    def test_security_logging(self):
        """测试安全日志和监控失效"""
        # 1. 检查日志记录
        try:
            # 模拟安全事件
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": "test_user", "password": "wrong_password"},
            )

            # 尝试访问审计日志
            audit_response = self.session.get(f"{self.base_url}/api/admin/audit")

            if audit_response.status_code == 200:
                self.results.append(
                    SecurityTestResult(
                        "安全审计日志",
                        "A09:2021",
                        "MEDIUM",
                        True,
                        "安全审计日志可访问",
                    ),
                )
            else:
                self.results.append(
                    SecurityTestResult(
                        "安全审计日志",
                        "A09:2021",
                        "MEDIUM",
                        False,
                        "安全审计日志不可访问",
                        "实施安全事件日志记录",
                    ),
                )
        except Exception as e:
            self.results.append(
                SecurityTestResult(
                    "安全审计日志",
                    "A09:2021",
                    "MEDIUM",
                    False,
                    f"检查失败: {e!s}",
                    "确保日志系统正常工作",
                ),
            )

        # 2. 检查入侵检测
        try:
            # 模拟可疑活动
            for i in range(5):
                self.session.get(f"{self.base_url}/api/admin/users")

            # 检查是否被阻止
            response = self.session.get(f"{self.base_url}/api/admin/users")

            if response.status_code == 429:
                self.results.append(
                    SecurityTestResult(
                        "入侵检测",
                        "A09:2021",
                        "MEDIUM",
                        True,
                        "入侵检测系统正常工作",
                    ),
                )
            else:
                self.results.append(
                    SecurityTestResult(
                        "入侵检测",
                        "A09:2021",
                        "MEDIUM",
                        False,
                        "缺少入侵检测",
                        "实施异常行为检测",
                    ),
                )
        except Exception:
            self.results.append(
                SecurityTestResult(
                    "入侵检测",
                    "A09:2021",
                    "MEDIUM",
                    False,
                    "入侵检测检查失败",
                    "确保监控系统正常运行",
                ),
            )

    def test_ssrf(self):
        """测试服务端请求伪造"""
        return owasp_test_ssrf(self, SecurityTestResult)

    def _has_valid_session(self) -> bool:
        """检查是否有有效会话"""
        return owasp_has_valid_session(self)

    def generate_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        return owasp_generate_report(self)


def run_owasp_security_tests():
    """运行 OWASP 安全测试"""
    return run_owasp_security_tests_helper(OWASPSecurityTester, json)


if __name__ == "__main__":
    exit_code = run_owasp_security_tests()
    sys.exit(exit_code)
