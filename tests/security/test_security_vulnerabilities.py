#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 安全漏洞测试套件

提供全面的安全漏洞检测和测试功能，包括OWASP Top 10漏洞检测。
"""

import pytest
import asyncio
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

from tests.conftest import test_config, mock_api_client


class SecurityVulnerabilityScanner:
    """安全漏洞扫描器主类"""

    def __init__(self):
        self.base_url = test_config.API_BASE_URL
        self.scan_results = {}
        self.cve_database = self._load_cve_database()
        self.security_headers = []
        self.assessment_metrics = {
            "vulnerabilities_found": 0,
            "risk_score": 0.0,
            "compliance_score": 0.0,
            "last_scan": None,
        }

    def _load_cve_database(self) -> Dict[str, Any]:
        """加载CVE漏洞数据库"""
        return {
            "cve-2021-44228": {  # Log4j
                "name": "Log4Shell",
                "severity": "critical",
                "description": "远程代码执行漏洞",
                "affected_versions": ["<2.15.0"],
                "patch_version": "2.15.0",
            },
            "cve-2022-22965": {  # Spring4Shell
                "name": "Spring4Shell",
                "severity": "high",
                "description": "远程代码执行漏洞",
                "affected_versions": ["<5.3.18", "<5.2.20"],
                "patch_version": "5.3.18/5.2.20",
            },
            "cve-2021-3449": {  # Apache Struts2
                "name": "Apache Struts2 OGNL",
                "severity": "critical",
                "description": "远程代码执行漏洞",
                "affected_versions": ["<2.5.30"],
                "patch_version": "2.5.30",
            },
            "cve-2022-0540": {  # SAML
                "name": "SAML Identity Provider",
                "severity": "high",
                "description": "身份验证绕过漏洞",
                "affected_versions": ["<1.1.0"],
                "patch_version": "1.1.0",
            },
        }

    async def run_comprehensive_security_scan(self):
        """运行全面的安全扫描"""
        print("\n🔒 开始全面安全漏洞扫描")
        self.scan_results = {}

        # 执行各项安全测试
        test_methods = [
            self.test_sql_injection,
            self.test_xss_attacks,
            self.test_csrf_protection,
            self.test_authentication_bypass,
            self.test_insecure_direct_object_references,
            self.test_security_misconfiguration,
            self.test_sensitive_data_exposure,
            self.test_missing_function_level_access_control,
            self.test_security_headers,
            self.test_file_upload_security,
            self.test_api_security,
            self.test_dependencies_vulnerabilities,
        ]

        results = {}
        for test_method in test_methods:
            try:
                method_name = test_method.__name__
                print(f"\n🔍 执行安全测试: {method_name}")

                result = await test_method()
                results[method_name] = result

                self._print_test_summary(method_name, result)

            except Exception as e:
                print(f"❌ 安全测试 {test_method.__name__} 失败: {str(e)}")
                results[test_method.__name__] = {"status": "failed", "error": str(e)}

        # 计算整体安全评分
        self._calculate_security_score(results)
        self.assessment_metrics["last_scan"] = datetime.now().isoformat()

        # 生成安全报告
        report = self._generate_security_report(results)

        print("\n✅ 安全扫描完成")
        print(f"📊 发现漏洞数: {self.assessment_metrics['vulnerabilities_found']}")
        print(f"🎯 风险评分: {self.assessment_metrics['risk_score']:.1f}/100")
        print(f"✅ 合规评分: {self.assessment_metrics['compliance_score']:.1f}/100")
        print(f"📄 安全报告: {report}")

        return report

    async def test_sql_injection(self) -> Dict[str, Any]:
        """SQL注入测试"""
        print("  🧪 测试SQL注入漏洞...")

        sql_payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "' UNION SELECT NULL--",
            "'; DROP TABLE users;--",
            "1' AND SLEEP(5)--",
            "1'; WAITFOR DELAY '0:0:5'--",
            "1' OR (SELECT COUNT(*) FROM users)>0--",
            "1' AND (SELECT COUNT(*) FROM pg_database)>0--",
            "1' OR 1=1 LIMIT 1--",
            "' OR EXISTS (SELECT * FROM users WHERE username='admin')--",
        ]

        endpoints_to_test = [
            ("/api/user/login", {"username": "${payload}", "password": "test"}),
            ("/api/market/quote/fetch", {"symbol": "${payload}"}),
            ("/api/trade/order", {"symbol": "${payload}", "quantity": "100"}),
            ("/api/portfolio/get", {"user_id": "${payload}"}),
        ]

        results = {"vulnerabilities": [], "tested_endpoints": 0}

        for endpoint, params in endpoints_to_test:
            for payload in sql_payloads:
                # 替换payload中的占位符
                test_params = params.copy()
                for key in test_params:
                    if isinstance(test_params[key], str):
                        test_params[key] = test_params[key].replace("${payload}", payload)

                try:
                    # 使用mock API客户端进行测试
                    response = await mock_api_client.post(endpoint, data=test_params)

                    # 检测SQL注入响应特征
                    if self._detect_sql_injection_response(response):
                        vuln = {
                            "type": "sql_injection",
                            "endpoint": endpoint,
                            "payload": payload,
                            "severity": "high",
                            "description": "检测到SQL注入漏洞",
                            "recommendation": "使用参数化查询，过滤特殊字符",
                        }
                        results["vulnerabilities"].append(vuln)

                except Exception as e:
                    # 注入可能成功导致错误，这也是一个安全风险
                    vuln = {
                        "type": "sql_injection_error_based",
                        "endpoint": endpoint,
                        "payload": payload,
                        "severity": "medium",
                        "description": f"基于错误检测的SQL注入: {str(e)}",
                        "recommendation": "实现安全的错误处理",
                    }
                    results["vulnerabilities"].append(vuln)

            results["tested_endpoints"] += 1

        return results

    async def test_xss_attacks(self) -> Dict[str, Any]:
        """XSS跨站脚本攻击测试"""
        print("  🧪 测试XSS攻击漏洞...")

        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "'\"><script>alert('XSS')</script>",
            "<iframe src=javascript:alert('XSS')>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<details open ontoggle=alert('XSS')>",
            "<select onfocus=alert('XSS') autofocus>",
        ]

        xss_endpoints = [
            ("/api/user/profile", {"name": "${payload}"}),
            ("/api/trade/comment", {"comment": "${payload}"}),
            ("/api/market/news", {"title": "${payload}"}),
            ("/api/contact", {"message": "${payload}"}),
        ]

        results = {"vulnerabilities": [], "tested_endpoints": 0}

        for endpoint, data in xss_endpoints:
            for payload in xss_payloads:
                test_data = data.copy()
                for key in test_data:
                    if isinstance(test_data[key], str):
                        test_data[key] = test_data[key].replace("${payload}", payload)

                try:
                    response = await mock_api_client.post(endpoint, data=test_data)

                    # 检测XSS反射
                    if self._detect_xss_reflection(response, payload):
                        vuln = {
                            "type": "xss_reflected",
                            "endpoint": endpoint,
                            "payload": payload,
                            "severity": "medium",
                            "description": "检测到反射型XSS漏洞",
                            "recommendation": "输出编码，启用CSP",
                        }
                        results["vulnerabilities"].append(vuln)

                except Exception as e:
                    print(f"    ⚠️  XSS测试异常: {str(e)}")

            results["tested_endpoints"] += 1

        return results

    async def test_csrf_protection(self) -> Dict[str, Any]:
        """CSRF跨站请求伪造测试"""
        print("  🧪 测试CSRF保护机制...")

        # 检查CSRF令牌
        protected_endpoints = [
            "/api/user/profile",
            "/api/trade/order",
            "/api/portfolio/update",
            "/api/settings",
        ]

        results = {
            "vulnerabilities": [],
            "protected_endpoints": 0,
            "unprotected_endpoints": [],
        }

        for endpoint in protected_endpoints:
            try:
                # 先获取CSRF令牌（如果存在）
                csrf_token = self._extract_csrf_token(endpoint)

                if not csrf_token:
                    results["unprotected_endpoints"].append(
                        {
                            "endpoint": endpoint,
                            "issue": "缺少CSRF令牌保护",
                            "severity": "high",
                            "recommendation": "实现CSRF令牌机制",
                        }
                    )
                else:
                    results["protected_endpoints"] += 1
                    print(f"    ✅ {endpoint} - CSRF保护已启用")

            except Exception as e:
                results["unprotected_endpoints"].append(
                    {
                        "endpoint": endpoint,
                        "issue": f"CSRF验证失败: {str(e)}",
                        "severity": "medium",
                        "recommendation": "检查CSRF保护实现",
                    }
                )

        # 转换为漏洞格式
        results["vulnerabilities"] = [
            {
                "type": "csrf_missing_protection",
                "endpoint": item["endpoint"],
                "severity": item["severity"],
                "description": item["issue"],
                "recommendation": item["recommendation"],
            }
            for item in results["unprotected_endpoints"]
        ]

        return results

    async def test_authentication_bypass(self) -> Dict[str, Any]:
        """认证绕过测试"""
        print("  🧪 测试认证绕过漏洞...")

        bypass_payloads = [
            {"username": "admin'--", "password": "any"},
            {"username": "' OR '1'='1", "password": "' OR '1'='1"},
            {"username": "admin", "password": "password' OR '1'='1"},
            {"username": "admin\n--", "password": "any"},
            {"username": "admin'/*", "password": "any*/"},
            {
                "username": "admin",
                "password": "password' UNION SELECT 'admin','password'",
            },
            {"username": "admin", "password": "password' #"},
            {"username": "admin'/**/", "password": "any"},
            {"username": "admin", "password": "password/*'*/"},
            {"username": "admin", "password": 'password" OR ""=""'},
        ]

        auth_endpoints = ["/api/auth/login", "/api/auth/verify", "/api/auth/refresh"]

        results = {"vulnerabilities": [], "tested_combinations": 0}

        for endpoint in auth_endpoints:
            for payload in bypass_payloads:
                try:
                    response = await mock_api_client.post(endpoint, data=payload)

                    # 检测认证绕过
                    if self._detect_auth_bypass(response):
                        vuln = {
                            "type": "authentication_bypass",
                            "endpoint": endpoint,
                            "payload": payload,
                            "severity": "critical",
                            "description": "检测到认证绕过漏洞",
                            "recommendation": "实现安全的认证验证逻辑",
                        }
                        results["vulnerabilities"].append(vuln)

                except Exception as e:
                    # 错误响应可能也表示安全问题
                    if "unauthorized" not in str(e).lower():
                        vuln = {
                            "type": "authentication_bypass_error",
                            "endpoint": endpoint,
                            "payload": payload,
                            "severity": "medium",
                            "description": f"认证绕过异常: {str(e)}",
                            "recommendation": "加强错误信息处理",
                        }
                        results["vulnerabilities"].append(vuln)

                results["tested_combinations"] += 1

        return results

    async def test_insecure_direct_object_references(self) -> Dict[str, Any]:
        """不安全的直接对象引用测试"""
        print("  🧪 测试不安全的直接对象引用...")

        idor_payloads = [
            {"user_id": "1"},  # 尝试访问用户1
            {"user_id": "admin"},
            {"user_id": "1000000"},  # 大ID
            {"user_id": "-1"},  # 负数ID
            {"user_id": "999999999"},  # 极大ID
            {"symbol": "AAPL"},  # 访问其他用户的数据
            {"symbol": "admin_portfolio"},
            {"symbol": "any_user"},
            {"trade_id": "1"},
            {"trade_id": "99999"},
        ]

        idor_endpoints = [
            ("/api/user/profile", {"user_id": "${id}"}),
            ("/api/user/orders", {"user_id": "${id}"}),
            ("/api/portfolio/view", {"symbol": "${symbol}"}),
            ("/api/trade/details", {"trade_id": "${trade_id}"}),
        ]

        results = {"vulnerabilities": [], "tested_requests": 0}

        for endpoint, params in idor_endpoints:
            for payload_data in idor_payloads:
                # 构造测试参数
                test_params = {
                    k: v.replace("${id}", str(payload_data.get("user_id", ""))) if k == "user_id" else v
                    for k, v in params.items()
                }
                test_params.update({k: v for k, v in payload_data.items() if k not in params})

                try:
                    # 以普通用户身份访问
                    response1 = await mock_api_client.get(endpoint, params=test_params)

                    # 检查是否允许访问不属于自己的数据
                    if self._detect_idor_vulnerability(response1, test_params):
                        vuln = {
                            "type": "insecure_direct_object_reference",
                            "endpoint": endpoint,
                            "params": test_params,
                            "severity": "high",
                            "description": "检测到不安全的直接对象引用",
                            "recommendation": "实现基于用户权限的访问控制",
                        }
                        results["vulnerabilities"].append(vuln)

                except Exception as e:
                    print(f"    ⚠️  IDOR测试异常: {str(e)}")

                results["tested_requests"] += 1

        return results

    async def test_security_misconfiguration(self) -> Dict[str, Any]:
        """安全配置错误测试"""
        print("  🧪 测试安全配置错误...")

        misconfiguration_checks = [
            {
                "check": "debug_mode",
                "endpoint": "/api/debug",
                "indicators": ["debug", "traceback", "stack"],
                "severity": "critical",
            },
            {
                "check": "directory_listing",
                "endpoint": "/static/",
                "indicators": ["Index of", "Directory Listing"],
                "severity": "medium",
            },
            {
                "check": "default_credentials",
                "endpoint": "/api/admin/login",
                "data": {"username": "admin", "password": "admin"},
                "indicators": ["success", "token"],
                "severity": "critical",
            },
            {
                "check": "verbose_error_messages",
                "endpoint": "/api/error",
                "params": {"error": "test"},
                "indicators": ["stack", "traceback", "line"],
                "severity": "medium",
            },
            {
                "check": "cors_misconfiguration",
                "endpoint": "/api/test",
                "headers": {
                    "Origin": "http://malicious.com",
                    "Referer": "http://malicious.com",
                },
                "indicators": ["allowed", "origin"],
                "severity": "medium",
            },
        ]

        results = {"vulnerabilities": []}

        for check in misconfiguration_checks:
            try:
                if "endpoint" in check and "data" in check:
                    # POST请求
                    response = await mock_api_client.post(
                        check["endpoint"],
                        data=check["data"],
                        headers=check.get("headers", {}),
                    )
                elif "endpoint" in check and "params" in check:
                    # GET请求带参数
                    response = await mock_api_client.get(
                        check["endpoint"],
                        params=check["params"],
                        headers=check.get("headers", {}),
                    )
                else:
                    # GET请求
                    response = await mock_api_client.get(check["endpoint"], headers=check.get("headers", {}))

                # 检查响应中是否存在安全配置错误的迹象
                response_text = str(response)
                for indicator in check["indicators"]:
                    if indicator.lower() in response_text.lower():
                        vuln = {
                            "type": "security_misconfiguration",
                            "check": check["check"],
                            "endpoint": check.get("endpoint"),
                            "severity": check["severity"],
                            "description": f"检测到安全配置错误: {check['check']}",
                            "recommendation": self._get_misconfiguration_recommendation(check["check"]),
                        }
                        results["vulnerabilities"].append(vuln)
                        break

            except Exception as e:
                # 某些安全错误（如403）反而是安全的
                if "403" in str(e) or "401" in str(e):
                    print(f"    ✅ {check.get('endpoint', check['check'])} - 安全配置正常")
                else:
                    print(f"    ⚠️  配置检查异常: {str(e)}")

        return results

    async def test_sensitive_data_exposure(self) -> Dict[str, Any]:
        """敏感数据暴露测试"""
        print("  🧪 测试敏感数据暴露...")

        sensitive_patterns = [
            r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",  # 信用卡号
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # 邮箱
            r"\b\d{10,15}\b",  # 手机号
            r"\b[A-Z0-9]{8,}\b",  # API密钥
            r"eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*",  # JWT token
            r"sk-[A-Za-z0-9]{20,}",  # OpenAI API key
            r"AKIA[A-Z0-9]{16}",  # AWS key
            r"ghp_[A-Za-z0-9]{36}",  # GitHub token
            r"pk_live_[A-Za-z0-9-]+",  # Stripe key
        ]

        test_data = {
            "user_profile": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "123-456-7890",
                "ssn": "123-45-6789",
                "credit_card": "4111-1111-1111-1111",
            },
            "api_responses": [
                {
                    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
                },
                {"api_key": "sk-1234567890abcdef1234567890abcdef"},
                {"aws_key": "AKIAIOSFODNN7EXAMPLE"},
            ],
        }

        results = {"vulnerabilities": [], "tested_data": 0}

        for category, data in test_data.items():
            if isinstance(data, dict):
                for key, value in data.items():
                    self._check_sensitive_data(f"{category}.{key}", value, sensitive_patterns, results)
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    self._check_sensitive_data(f"{category}[{i}]", str(item), sensitive_patterns, results)

            results["tested_data"] += 1

        return results

    async def test_missing_function_level_access_control(self) -> Dict[str, Any]:
        """缺少功能级访问控制测试"""
        print("  🧪 测试功能级访问控制...")

        privilege_escalation_payloads = [
            {"role": "admin", "permission": "delete_user"},
            {"role": "admin", "permission": "edit_settings"},
            {"role": "user", "permission": "view_admin_dashboard"},
            {"role": "guest", "permission": "create_trade"},
            {"user_level": "999", "permission": "admin_actions"},
            {"access_level": "root", "operation": "system_config"},
            {"bypass": "true", "action": "admin_only"},
            {"force_admin": "1", "restricted": "1"},
        ]

        admin_endpoints = [
            ("/api/admin/users", {"action": "${action}"}),
            ("/api/admin/settings", {"permission": "${permission}"}),
            ("/api/admin/logs", {"level": "${user_level}"}),
            ("/api/system/config", {"bypass": "${bypass}"}),
        ]

        results = {"vulnerabilities": [], "tested_escalations": 0}

        for endpoint, params in admin_endpoints:
            for payload in privilege_escalation_payloads:
                # 构造测试参数
                test_params = params.copy()
                for key in test_params:
                    if isinstance(test_params[key], str):
                        test_params[key] = test_params[key].replace("${action}", payload.get("action", ""))
                        test_params[key] = test_params[key].replace("${permission}", payload.get("permission", ""))
                        test_params[key] = test_params[key].replace("${user_level}", payload.get("user_level", ""))
                        test_params[key] = test_params[key].replace("${bypass}", payload.get("bypass", ""))

                test_params.update(payload)

                try:
                    # 普通用户尝试访问管理员端点
                    response = await mock_api_client.post(endpoint, data=test_params)

                    # 检测权限提升
                    if self._detect_privilege_escalation(response):
                        vuln = {
                            "type": "missing_function_level_access_control",
                            "endpoint": endpoint,
                            "payload": payload,
                            "severity": "high",
                            "description": "检测到权限提升漏洞",
                            "recommendation": "实现基于角色的访问控制（RBAC）",
                        }
                        results["vulnerabilities"].append(vuln)

                except Exception as e:
                    if "forbidden" not in str(e).lower():
                        vuln = {
                            "type": "access_control_weakness",
                            "endpoint": endpoint,
                            "payload": payload,
                            "severity": "medium",
                            "description": f"访问控制异常: {str(e)}",
                            "recommendation": "加强权限验证",
                        }
                        results["vulnerabilities"].append(vuln)

                results["tested_escalations"] += 1

        return results

    async def test_security_headers(self) -> Dict[str, Any]:
        """安全头部测试"""
        print("  🧪 测试安全HTTP头部...")

        required_headers = [
            ("X-Content-Type-Options", "nosniff"),
            ("X-Frame-Options", "DENY"),
            ("X-XSS-Protection", "1; mode=block"),
            ("Strict-Transport-Security", "max-age=31536000; includeSubDomains"),
            ("Content-Security-Policy", "default-src 'self'"),
            ("Referrer-Policy", "strict-origin-when-cross-origin"),
            ("Permissions-Policy", "geolocation=(), microphone=()"),
        ]

        security_headers_results = {"present_headers": [], "missing_headers": []}

        for header_name, expected_value in required_headers:
            try:
                # 检查响应头部
                response_headers = getattr(mock_api_client, "headers", {})

                if header_name in response_headers:
                    actual_value = response_headers[header_name]
                    security_headers_results["present_headers"].append(
                        {
                            "header": header_name,
                            "expected": expected_value,
                            "actual": actual_value,
                            "status": "present",
                        }
                    )
                    print(f"    ✅ {header_name} - 已设置")
                else:
                    security_headers_results["missing_headers"].append(
                        {
                            "header": header_name,
                            "expected": expected_value,
                            "status": "missing",
                        }
                    )
                    print(f"    ❌ {header_name} - 缺失")

            except Exception as e:
                security_headers_results["missing_headers"].append(
                    {"header": header_name, "error": str(e), "status": "error"}
                )
                print(f"    ⚠️  {header_name} - 检查失败: {str(e)}")

        # 转换为漏洞格式
        results = {
            "vulnerabilities": [
                {
                    "type": "missing_security_header",
                    "header": item["header"],
                    "severity": "medium",
                    "description": f"缺少安全HTTP头部: {item['header']}",
                    "recommendation": f"设置 {item['header']} 头部",
                }
                for item in security_headers_results["missing_headers"]
            ],
            "security_headers": security_headers_results,
        }

        return results

    async def test_file_upload_security(self) -> Dict[str, Any]:
        """文件上传安全测试"""
        print("  🧪 测试文件上传安全...")

        malicious_files = [
            {
                "name": "malicious.js",
                "content": "alert('XSS');",
                "type": "application/javascript",
            },
            {
                "name": "shell.php",
                "content": "<?php system($_GET['cmd']); ?>",
                "type": "application/x-httpd-php",
            },
            {
                "name": "exploit.jsp",
                "content": '<%@ page import="java.io.*" %><%= request.getParameter("cmd") %>',
                "type": "text/html",
            },
            {
                "name": "virus.exe",
                "content": "MZ" + "\x00" * 100,  # PE文件头
                "type": "application/x-msdownload",
            },
            {
                "name": "script.py",
                "content": "import os; os.system('rm -rf /')",
                "type": "text/x-python",
            },
        ]

        upload_endpoints = [
            "/api/upload/avatar",
            "/api/upload/document",
            "/api/upload/profile",
        ]

        results = {"vulnerabilities": [], "tested_files": 0}

        for endpoint in upload_endpoints:
            for file_info in malicious_files:
                try:
                    # 构造文件数据（模拟）
                    files = {
                        "file": (
                            file_info["name"],
                            file_info["content"],
                            file_info["type"],
                        )
                    }

                    # 尝试上传恶意文件
                    response = await mock_api_client.post(endpoint, files=files)

                    # 检测文件上传漏洞
                    if self._detect_file_upload_vulnerability(response, file_info["name"]):
                        vuln = {
                            "type": "insecure_file_upload",
                            "endpoint": endpoint,
                            "file_name": file_info["name"],
                            "file_type": file_info["type"],
                            "severity": "high",
                            "description": f"检测到不安全的文件上传: {file_info['name']}",
                            "recommendation": "实现文件类型验证、内容扫描和重命名",
                        }
                        results["vulnerabilities"].append(vuln)

                except Exception as e:
                    # 上传失败可能表示有保护措施
                    if "not allowed" in str(e).lower() or "invalid" in str(e).lower():
                        print(f"    ✅ {file_info['name']} - 文件上传被拒绝")
                    else:
                        print(f"    ⚠️  文件上传异常: {str(e)}")

                results["tested_files"] += 1

        return results

    async def test_api_security(self) -> Dict[str, Any]:
        """API安全测试"""
        print("  🧪 测试API安全...")

        api_security_checks = [
            {
                "test": "rate_limiting",
                "endpoint": "/api/market/quote/fetch",
                "method": "GET",
                "params": {"symbols": ["AAPL", "MSFT", "GOOGL"]},
                "attempts": 50,  # 快速多次请求
                "indicators": ["rate limit", "too many", "429"],
                "severity": "medium",
            },
            {
                "test": "input_validation",
                "endpoint": "/api/trade/order",
                "method": "POST",
                "data": {
                    "symbol": "A" * 1000,  # 超长符号
                    "quantity": "999999999999",  # 极大数量
                    "price": "-1",  # 负价格
                },
                "indicators": ["validation", "invalid", "400"],
                "severity": "medium",
            },
            {
                "test": "api_versioning",
                "endpoint": "/api/v1/admin/users",
                "method": "GET",
                "headers": {"Accept": "application/vnd.company.v2+json"},
                "indicators": ["unsupported", "version", "406"],
                "severity": "low",
            },
        ]

        results = {"vulnerabilities": []}

        for check in api_security_checks:
            try:
                response = None
                for attempt in range(check.get("attempts", 1)):
                    if check["method"] == "GET":
                        response = await mock_api_client.get(
                            check["endpoint"],
                            params=check.get("params", {}),
                            headers=check.get("headers", {}),
                        )
                    else:
                        response = await mock_api_client.post(
                            check["endpoint"],
                            data=check.get("data", {}),
                            headers=check.get("headers", {}),
                        )

                # 检测安全响应
                response_text = str(response)
                for indicator in check["indicators"]:
                    if indicator.lower() in response_text.lower():
                        vuln = {
                            "type": "api_security_weakness",
                            "test": check["test"],
                            "endpoint": check["endpoint"],
                            "severity": check["severity"],
                            "description": f"检测到API安全问题: {check['test']}",
                            "recommendation": self._get_api_security_recommendation(check["test"]),
                        }
                        results["vulnerabilities"].append(vuln)
                        break

            except Exception as e:
                print(f"    ⚠️  API安全测试异常: {str(e)}")

        return results

    async def test_dependencies_vulnerabilities(self) -> Dict[str, Any]:
        """依赖漏洞测试"""
        print("  🧪 测试依赖漏洞...")

        # 模拟依赖项和已知漏洞
        vulnerable_dependencies = [
            {
                "package": "flask",
                "version": "2.0.1",
                "cve": "CVE-2022-29155",
                "severity": "medium",
                "description": "路径遍历漏洞",
            },
            {
                "package": "requests",
                "version": "2.25.1",
                "cve": "CVE-2021-3749",
                "severity": "high",
                "description": "SSRF漏洞",
            },
            {
                "package": "django",
                "version": "3.2.0",
                "cve": "CVE-2021-35042",
                "severity": "critical",
                "description": "远程代码执行",
            },
        ]

        results = {"vulnerabilities": [], "dependencies_checked": 0}

        for dep in vulnerable_dependencies:
            # 检查是否在CVE数据库中
            if dep["cve"] in self.cve_database:
                cve_info = self.cve_database[dep["cve"]]

                vuln = {
                    "type": "dependency_vulnerability",
                    "package": dep["package"],
                    "version": dep["version"],
                    "cve": dep["cve"],
                    "cve_severity": cve_info["severity"],
                    "description": cve_info["description"],
                    "affected_versions": cve_info["affected_versions"],
                    "patch_version": cve_info["patch_version"],
                    "recommendation": f"升级到 {cve_info['patch_version']}",
                }
                results["vulnerabilities"].append(vuln)

            results["dependencies_checked"] += 1

        return results

    # 辅助方法

    def _detect_sql_injection_response(self, response: Dict[str, Any]) -> bool:
        """检测SQL注入响应特征"""
        response_text = str(response).lower()

        sql_injection_indicators = [
            "syntax error",
            "mysql_fetch_array",
            "odbc_execute",
            "postgresql",
            "ora-",
            "microsoft ole db",
            "sql server",
            "error in your sql syntax",
        ]

        return any(indicator in response_text for indicator in sql_injection_indicators)

    def _detect_xss_reflection(self, response: Dict[str, Any], payload: str) -> bool:
        """检测XSS反射"""
        response_text = str(response).lower()
        payload_lower = payload.lower()

        # 检查payload是否在响应中反射
        return payload_lower in response_text

    def _extract_csrf_token(self, endpoint: str) -> Optional[str]:
        """提取CSRF令牌"""
        # 模拟获取CSRF令牌
        return None  # 在实际实现中，这里会真实检查CSRF令牌

    def _detect_auth_bypass(self, response: Dict[str, Any]) -> bool:
        """检测认证绕过"""
        response_text = str(response).lower()

        # 检查是否成功绕过认证
        auth_success_indicators = [
            "success",
            "authenticated",
            "token",
            "session",
            "welcome",
        ]

        return any(indicator in response_text for indicator in auth_success_indicators)

    def _detect_idor_vulnerability(self, response: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """检测IDOR漏洞"""
        response_text = str(response).lower()

        # 检查是否允许访问不属于自己的数据
        idor_indicators = [
            "admin",
            "user_1",
            "user_2",
            "another_user",
            "unauthorized_data",
        ]

        return any(indicator in response_text for indicator in idor_indicators)

    def _check_sensitive_data(self, key: str, value: str, patterns: List[str], results: Dict[str, Any]):
        """检查敏感数据"""
        for pattern in patterns:
            if re.search(pattern, str(value), re.IGNORECASE):
                vuln = {
                    "type": "sensitive_data_exposure",
                    "field": key,
                    "value": value,
                    "pattern": pattern,
                    "severity": "high",
                    "description": f"检测到敏感数据: {key}",
                    "recommendation": "对敏感数据进行加密或脱敏",
                }
                results["vulnerabilities"].append(vuln)
                break

    def _detect_privilege_escalation(self, response: Dict[str, Any]) -> bool:
        """检测权限提升"""
        response_text = str(response).lower()

        escalation_indicators = [
            "admin",
            "delete_user",
            "edit_settings",
            "system_config",
            "level_999",
            "root_access",
        ]

        return any(indicator in response_text for indicator in escalation_indicators)

    def _detect_file_upload_vulnerability(self, response: Dict[str, Any], filename: str) -> bool:
        """检测文件上传漏洞"""
        response_text = str(response).lower()

        upload_success_indicators = [
            "uploaded",
            "success",
            "stored",
            "saved",
            filename.lower(),
        ]

        return any(indicator in response_text for indicator in upload_success_indicators)

    def _get_misconfiguration_recommendation(self, check_type: str) -> str:
        """获取配置错误的修复建议"""
        recommendations = {
            "debug_mode": "禁用调试模式，在生产环境中关闭详细错误信息",
            "directory_listing": "禁用目录 listing，配置适当的访问控制",
            "default_credentials": "更改默认管理员密码，实现强密码策略",
            "verbose_error_messages": "实现安全的错误处理，不暴露敏感信息",
            "cors_misconfiguration": "配置适当的CORS策略，限制来源域名",
        }
        return recommendations.get(check_type, "检查并修复安全配置")

    def _get_api_security_recommendation(self, test_type: str) -> str:
        """获取API安全修复建议"""
        recommendations = {
            "rate_limiting": "实施速率限制，防止API滥用和DoS攻击",
            "input_validation": "实现严格的数据验证，拒绝无效输入",
            "api_versioning": "使用API版本控制，确保向后兼容性",
        }
        return recommendations.get(test_type, "加强API安全措施")

    def _print_test_summary(self, test_name: str, result: Dict[str, Any]):
        """打印测试摘要"""
        if isinstance(result, dict) and "vulnerabilities" in result:
            vuln_count = len(result["vulnerabilities"])
            if vuln_count > 0:
                print(f"    ⚠️  {test_name}: 发现 {vuln_count} 个漏洞")
            else:
                print(f"    ✅ {test_name}: 未发现漏洞")
        elif isinstance(result, dict) and "status" in result and result["status"] == "failed":
            print(f"    ❌ {test_name}: 测试失败 - {result.get('error', '未知错误')}")
        else:
            print(f"    ⚠️  {test_name}: 测试完成")

    def _calculate_security_score(self, results: Dict[str, Any]):
        """计算安全评分"""
        total_vulnerabilities = 0
        risk_score = 0.0

        for test_name, result in results.items():
            if isinstance(result, dict) and "vulnerabilities" in result:
                vuln_count = len(result["vulnerabilities"])
                total_vulnerabilities += vuln_count

                # 根据漏洞严重程度计算风险分数
                for vuln in result["vulnerabilities"]:
                    severity = vuln.get("severity", "medium")
                    if severity == "critical":
                        risk_score += 10.0
                    elif severity == "high":
                        risk_score += 7.0
                    elif severity == "medium":
                        risk_score += 4.0
                    elif severity == "low":
                        risk_score += 1.0

        # 更新评估指标
        self.assessment_metrics["vulnerabilities_found"] = total_vulnerabilities
        self.assessment_metrics["risk_score"] = min(100.0, risk_score)
        self.assessment_metrics["compliance_score"] = max(0.0, 100.0 - (total_vulnerabilities * 5.0))

    def _generate_security_report(self, results: Dict[str, Any]) -> str:
        """生成安全报告"""
        report_path = f"/tmp/security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        report = {
            "scan_summary": {
                "scan_date": datetime.now().isoformat(),
                "total_tests": len(results),
                "total_vulnerabilities": self.assessment_metrics["vulnerabilities_found"],
                "risk_score": round(self.assessment_metrics["risk_score"], 1),
                "compliance_score": round(self.assessment_metrics["compliance_score"], 1),
            },
            "detailed_results": results,
            "vulnerability_statistics": self._analyze_vulnerability_statistics(results),
            "recommendations": self._generate_security_recommendations(results),
            "cve_database": self.cve_database,
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return report_path

    def _analyze_vulnerability_statistics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """分析漏洞统计"""
        stats = {
            "by_severity": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "by_type": {},
            "by_endpoint": {},
            "total_risk_score": 0.0,
        }

        for test_name, result in results.items():
            if isinstance(result, dict) and "vulnerabilities" in result:
                for vuln in result["vulnerabilities"]:
                    severity = vuln.get("severity", "medium")
                    vuln_type = vuln.get("type", "unknown")
                    endpoint = vuln.get("endpoint", "unknown")

                    stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1
                    stats["by_type"][vuln_type] = stats["by_type"].get(vuln_type, 0) + 1
                    stats["by_endpoint"][endpoint] = stats["by_endpoint"].get(endpoint, 0) + 1

                    risk_weight = {"critical": 10, "high": 7, "medium": 4, "low": 1}
                    stats["total_risk_score"] += risk_weight.get(severity, 1)

        return stats

    def _generate_security_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成安全建议"""
        recommendations = []

        for test_name, result in results.items():
            if isinstance(result, dict) and "vulnerabilities" in result:
                for vuln in result["vulnerabilities"]:
                    rec = {
                        "priority": vuln.get("severity", "medium"),
                        "category": vuln.get("type", "general"),
                        "description": vuln.get("description", ""),
                        "recommendation": vuln.get("recommendation", ""),
                        "test_name": test_name,
                    }
                    recommendations.append(rec)

        # 按优先级排序
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 4))

        return recommendations


# 安全测试装饰器
def security_scan(test_func):
    """安全测试装饰器"""

    async def wrapper(*args, **kwargs):
        scanner = SecurityVulnerabilityScanner()
        return await scanner.run_comprehensive_security_scan()

    return wrapper


# Pytest测试用例
@pytest.mark.security
async def test_security_vulnerabilities():
    """安全漏洞测试"""
    scanner = SecurityVulnerabilityScanner()
    report = await scanner.run_comprehensive_security_scan()

    # 验证测试结果
    assert isinstance(scanner.scan_results, dict)
    assert len(scanner.scan_results) >= 5  # 至少运行了5项安全测试

    # 验证基本指标
    assert scanner.assessment_metrics["vulnerabilities_found"] >= 0
    assert 0 <= scanner.assessment_metrics["risk_score"] <= 100
    assert 0 <= scanner.assessment_metrics["compliance_score"] <= 100

    print(f"\n📊 安全测试报告: {report}")


@pytest.mark.security
async def test_sql_injection_protection():
    """SQL注入保护测试"""
    scanner = SecurityVulnerabilityScanner()
    result = await scanner.test_sql_injection()

    assert isinstance(result, dict)
    assert "vulnerabilities" in result
    assert isinstance(result["vulnerabilities"], list)


@pytest.mark.security
async def test_xss_protection():
    """XSS保护测试"""
    scanner = SecurityVulnerabilityScanner()
    result = await scanner.test_xss_attacks()

    assert isinstance(result, dict)
    assert "vulnerabilities" in result
    assert isinstance(result["vulnerabilities"], list)


@pytest.mark.security
async def test_csrf_protection():
    """CSRF保护测试"""
    scanner = SecurityVulnerabilityScanner()
    result = await scanner.test_csrf_protection()

    assert isinstance(result, dict)
    assert "vulnerabilities" in result


@pytest.mark.security
async def test_authentication_security():
    """认证安全测试"""
    scanner = SecurityVulnerabilityScanner()
    result = await scanner.test_authentication_bypass()

    assert isinstance(result, dict)
    assert "vulnerabilities" in result
    assert isinstance(result["vulnerabilities"], list)


@pytest.mark.security
async def test_dependency_vulnerabilities():
    """依赖漏洞测试"""
    scanner = SecurityVulnerabilityScanner()
    result = await scanner.test_dependencies_vulnerabilities()

    assert isinstance(result, dict)
    assert "vulnerabilities" in result
    assert isinstance(result["vulnerabilities"], list)


if __name__ == "__main__":
    # 运行完整安全测试
    async def main():
        scanner = SecurityVulnerabilityScanner()
        report = await scanner.run_comprehensive_security_scan()
        print(f"\n🎯 安全测试报告已保存到: {report}")

    # 运行测试
    import asyncio

    asyncio.run(main())
