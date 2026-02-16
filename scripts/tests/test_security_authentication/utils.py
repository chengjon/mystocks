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


