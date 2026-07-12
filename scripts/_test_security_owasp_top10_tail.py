#!/usr/bin/env python3
"""Support helpers extracted from `scripts/tests/test_security_owasp_top10.py`."""

from datetime import datetime


def owasp_test_ssrf(self, result_cls):
    """测试服务端请求伪造"""
    ssrf_payloads = [
        "http://localhost",
        "http://169.254.169.254/latest/meta-data/",
        "http://127.0.0.1:8080",
        "file:///etc/passwd",
    ]

    for payload in ssrf_payloads:
        try:
            response = self.session.get(f"{self.base_url}/api/proxy", params={"url": payload})

            if response.status_code == 200 and "localhost" in response.text:
                self.results.append(
                    result_cls(
                        f"SSRF 测试 - {payload}",
                        "A10:2021",
                        "HIGH",
                        False,
                        "可能存在 SSRF 漏洞",
                        "实施 URL 验证和限制",
                    ),
                )
                break
        except Exception:
            pass

    try:
        response = self.session.get(f"{self.base_url}/api/proxy", params={"url": "http://evil.com"})
        if response.status_code == 400:
            self.results.append(
                result_cls("URL 白名单检查", "A10:2021", "HIGH", True, "URL 白名单正常工作"),
            )
        else:
            self.results.append(
                result_cls(
                    "URL 白名单检查",
                    "A10:2021",
                    "HIGH",
                    False,
                    "URL 白名单未正确实施",
                    "配置允许的域名白名单",
                ),
            )
    except Exception as error:
        self.results.append(
            result_cls(
                "URL 白名单检查",
                "A10:2021",
                "HIGH",
                False,
                f"检查失败: {error!s}",
                "确保代理接口正确配置",
            ),
        )


def owasp_has_valid_session(self) -> bool:
    """检查是否有有效会话"""
    try:
        response = self.session.get(f"{self.base_url}/api/user/profile")
        return response.status_code == 200
    except Exception:
        return False


def owasp_generate_report(self):
    """生成测试报告"""
    report = {
        "test_summary": {
            "total_tests": len(self.results),
            "passed": sum(1 for result in self.results if result.passed),
            "failed": sum(1 for result in self.results if not result.passed),
            "test_date": datetime.now().isoformat(),
        },
        "severity_breakdown": {
            "CRITICAL": sum(1 for result in self.results if result.severity == "CRITICAL" and not result.passed),
            "HIGH": sum(1 for result in self.results if result.severity == "HIGH" and not result.passed),
            "MEDIUM": sum(1 for result in self.results if result.severity == "MEDIUM" and not result.passed),
            "LOW": sum(1 for result in self.results if result.severity == "LOW" and not result.passed),
        },
        "category_results": {},
        "detailed_findings": [],
    }

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
                },
            )

    return report


def run_owasp_security_tests(tester_cls, json_module):
    """运行 OWASP 安全测试"""
    print("🔒 MyStocks OWASP Top 10 安全测试套件")
    print("=" * 80)

    tester = tester_cls()
    results = tester.run_all_tests()
    report = tester.generate_report()

    print("\n" + "=" * 80)
    print("📊 测试结果摘要")
    print("=" * 80)
    print(f"总测试数: {report['test_summary']['total_tests']}")
    print(f"通过: {report['test_summary']['passed']}")
    print(f"失败: {report['test_summary']['failed']}")
    print(f"通过率: {report['test_summary']['passed'] / report['test_summary']['total_tests'] * 100:.1f}%")

    print("\n🚨 按严重性分类的漏洞:")
    print(f"  Critical: {report['severity_breakdown']['CRITICAL']}")
    print(f"  High: {report['severity_breakdown']['HIGH']}")
    print(f"  Medium: {report['severity_breakdown']['MEDIUM']}")
    print(f"  Low: {report['severity_breakdown']['LOW']}")

    print("\n📋 按类别分类的结果:")
    for category, stats in report["category_results"].items():
        pass_rate = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
        print(f"  {category}: {stats['passed']}/{stats['total']} ({pass_rate:.1f}%)")

    report_file = f"/tmp/owasp_security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as file_obj:
        json_module.dump(report, file_obj, indent=2, ensure_ascii=False)

    print(f"\n📄 详细报告已保存至: {report_file}")

    critical_high_issues = [
        result for result in results if not result.passed and result.severity in ["CRITICAL", "HIGH"]
    ]
    if critical_high_issues:
        print("\n⚠️  需要立即修复的关键问题:")
        for issue in critical_high_issues:
            print(f"  - {issue.test_name} ({issue.severity}): {issue.details}")
            print(f"    建议: {issue.recommendation}")

    if report["test_summary"]["failed"] > 0:
        print(f"\n❌ {report['test_summary']['failed']} 个测试失败，请修复相关问题")
        return 1

    print("\n✅ 所有安全测试通过！")
    return 0
