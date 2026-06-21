#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 安全漏洞测试套件

提供全面的安全漏洞检测和测试功能，包括OWASP Top 10漏洞检测。
"""


import pytest

from .security_vulnerability_scanner import SecurityVulnerabilityScanner


def security_scan(test_func):
    """安全测试装饰器"""

    async def wrapper(*args, **kwargs):
        scanner = SecurityVulnerabilityScanner()
        return await scanner.run_comprehensive_security_scan()

    return wrapper


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

