#!/usr/bin/env python3
"""
契约测试覆盖率报告生成器

生成专门针对API契约测试的覆盖率报告，包括：
- 契约测试执行统计
- API端点覆盖率分析
- 契约验证覆盖率
- 详细的覆盖率报告
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ContractCoverageMetrics:
    """契约测试覆盖率指标"""

    total_endpoints: int = 0
    tested_endpoints: int = 0
    total_operations: int = 0
    tested_operations: int = 0
    total_contracts: int = 0
    tested_contracts: int = 0
    response_validations: int = 0
    schema_validations: int = 0
    security_validations: int = 0
    performance_validations: int = 0

    @property
    def endpoint_coverage_rate(self) -> float:
        """端点覆盖率"""
        return self.tested_endpoints / self.total_endpoints if self.total_endpoints > 0 else 0

    @property
    def operation_coverage_rate(self) -> float:
        """操作覆盖率"""
        return self.tested_operations / self.total_operations if self.total_operations > 0 else 0

    @property
    def contract_coverage_rate(self) -> float:
        """契约覆盖率"""
        return self.tested_contracts / self.total_contracts if self.total_contracts > 0 else 0


@dataclass
class ContractTestResult:
    """契约测试结果"""

    test_name: str
    endpoint: str
    method: str
    status: str  # 'passed', 'failed', 'skipped'
    duration: float
    violations: List[Dict[str, Any]] = field(default_factory=list)
    coverage: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class ContractCoverageReporter:
    """契约测试覆盖率报告生成器"""

    def __init__(self, output_dir: str = "contract_coverage_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_coverage_report(self, test_results: List[ContractTestResult]) -> Dict[str, Any]:
        """生成覆盖率报告"""

        metrics = ContractCoverageMetrics()

        # 分析测试结果
        endpoint_coverage = {}
        operation_coverage = {}
        contract_coverage = {}

        for result in test_results:
            # 统计端点覆盖
            endpoint_key = result.endpoint
            if endpoint_key not in endpoint_coverage:
                endpoint_coverage[endpoint_key] = {"total_operations": 0, "tested_operations": 0, "methods": set()}

            endpoint_coverage[endpoint_key]["methods"].add(result.method)
            endpoint_coverage[endpoint_key]["total_operations"] += 1

            if result.status == "passed":
                endpoint_coverage[endpoint_key]["tested_operations"] += 1
                metrics.tested_operations += 1
                operation_coverage[f"{endpoint_key}:{result.method}"] = True

            # 统计验证类型
            self._analyze_validation_types(result, metrics)

        # 计算总指标
        metrics.total_endpoints = len(endpoint_coverage)
        metrics.tested_endpoints = len([e for e in endpoint_coverage.values() if e["tested_operations"] > 0])
        metrics.total_operations = sum(e["total_operations"] for e in endpoint_coverage.values())

        # 生成报告
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_tests": len(test_results),
                "test_period": self._calculate_test_period(test_results),
            },
            "metrics": {
                "endpoint_coverage_rate": metrics.endpoint_coverage_rate,
                "operation_coverage_rate": metrics.operation_coverage_rate,
                "contract_coverage_rate": metrics.contract_coverage_rate,
                "total_endpoints": metrics.total_endpoints,
                "tested_endpoints": metrics.tested_endpoints,
                "total_operations": metrics.total_operations,
                "tested_operations": metrics.tested_operations,
                "response_validations": metrics.response_validations,
                "schema_validations": metrics.schema_validations,
                "security_validations": metrics.security_validations,
                "performance_validations": metrics.performance_validations,
            },
            "coverage_details": {
                "endpoints": endpoint_coverage,
                "operations": operation_coverage,
                "contracts": contract_coverage,
            },
            "test_results": [self._serialize_test_result(r) for r in test_results],
            "recommendations": self._generate_recommendations(metrics, endpoint_coverage),
        }

        return report

    def _analyze_validation_types(self, result: ContractTestResult, metrics: ContractCoverageMetrics):
        """分析验证类型"""

        for violation in result.violations:
            violation_type = violation.get("violation_type", "")

            if "response" in violation_type.lower():
                metrics.response_validations += 1
            elif "schema" in violation_type.lower():
                metrics.schema_validations += 1
            elif "security" in violation_type.lower():
                metrics.security_validations += 1
            elif "performance" in violation_type.lower() or "time" in violation_type.lower():
                metrics.performance_validations += 1

    def _calculate_test_period(self, test_results: List[ContractTestResult]) -> str:
        """计算测试周期"""
        if not test_results:
            return "0s"

        timestamps = [r.timestamp for r in test_results]
        duration = max(timestamps) - min(timestamps)
        return f"{duration.total_seconds():.2f}s"

    def _serialize_test_result(self, result: ContractTestResult) -> Dict[str, Any]:
        """序列化测试结果"""
        return {
            "test_name": result.test_name,
            "endpoint": result.endpoint,
            "method": result.method,
            "status": result.status,
            "duration": result.duration,
            "violations_count": len(result.violations),
            "coverage": result.coverage,
            "timestamp": result.timestamp.isoformat(),
        }

    def _generate_recommendations(
        self, metrics: ContractCoverageMetrics, endpoint_coverage: Dict[str, Any]
    ) -> List[str]:
        """生成改进建议"""

        recommendations = []

        # 覆盖率检查
        if metrics.endpoint_coverage_rate < 0.8:
            recommendations.append(
                f"端点覆盖率仅为{metrics.endpoint_coverage_rate:.1%}，建议增加对未测试端点的契约测试"
            )

        if metrics.operation_coverage_rate < 0.8:
            recommendations.append(f"操作覆盖率仅为{metrics.operation_coverage_rate:.1%}，建议为更多HTTP方法添加测试")

        # 查找未测试的端点
        untested_endpoints = [
            endpoint for endpoint, data in endpoint_coverage.items() if data["tested_operations"] == 0
        ]

        if untested_endpoints:
            recommendations.append(
                f"发现{len(untested_endpoints)}个完全未测试的端点: "
                f"{', '.join(untested_endpoints[:5])}{'...' if len(untested_endpoints) > 5 else ''}"
            )

        # 验证类型检查
        if metrics.schema_validations == 0:
            recommendations.append("未发现schema验证，建议添加JSON Schema验证测试")

        if metrics.security_validations == 0:
            recommendations.append("未发现安全验证，建议添加JWT/CSRF验证测试")

        if metrics.performance_validations == 0:
            recommendations.append("未发现性能验证，建议添加响应时间验证测试")

        return recommendations

    def save_report(self, report: Dict[str, Any], format: str = "json"):
        """保存报告"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == "json":
            output_file = self.output_dir / f"contract_coverage_{timestamp}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

        elif format == "html":
            output_file = self.output_dir / f"contract_coverage_{timestamp}.html"
            html_content = self._generate_html_report(report)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)

        print(f"契约测试覆盖率报告已保存: {output_file}")
        return output_file

    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """生成HTML报告"""

        metrics = report["metrics"]

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>API契约测试覆盖率报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; margin-bottom: 20px; }}
                .metrics {{ background-color: #e8f4f8; padding: 15px; margin-bottom: 20px; }}
                .coverage-high {{ color: #28a745; }}
                .coverage-medium {{ color: #ffc107; }}
                .coverage-low {{ color: #dc3545; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .recommendations {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>API契约测试覆盖率报告</h1>
                <p><strong>生成时间:</strong> {report["metadata"]["generated_at"]}</p>
                <p><strong>测试总数:</strong> {report["metadata"]["total_tests"]}</p>
                <p><strong>测试周期:</strong> {report["metadata"]["test_period"]}</p>
            </div>

            <div class="metrics">
                <h2>覆盖率指标</h2>
                <table>
                    <tr>
                        <td>端点覆盖率</td>
                        <td class="{self._get_coverage_class(metrics["endpoint_coverage_rate"])}">
                            {metrics["endpoint_coverage_rate"]:.1%}
                        </td>
                        <td>({metrics["tested_endpoints"]}/{metrics["total_endpoints"]} 端点)</td>
                    </tr>
                    <tr>
                        <td>操作覆盖率</td>
                        <td class="{self._get_coverage_class(metrics["operation_coverage_rate"])}">
                            {metrics["operation_coverage_rate"]:.1%}
                        </td>
                        <td>({metrics["tested_operations"]}/{metrics["total_operations"]} 操作)</td>
                    </tr>
                    <tr>
                        <td>契约覆盖率</td>
                        <td class="{self._get_coverage_class(metrics["contract_coverage_rate"])}">
                            {metrics["contract_coverage_rate"]:.1%}
                        </td>
                        <td>({metrics["tested_contracts"]}/{metrics["total_contracts"]} 契约)</td>
                    </tr>
                </table>

                <h3>验证类型统计</h3>
                <table>
                    <tr><td>响应验证</td><td>{metrics["response_validations"]}</td></tr>
                    <tr><td>Schema验证</td><td>{metrics["schema_validations"]}</td></tr>
                    <tr><td>安全验证</td><td>{metrics["security_validations"]}</td></tr>
                    <tr><td>性能验证</td><td>{metrics["performance_validations"]}</td></tr>
                </table>
            </div>

            <div class="recommendations">
                <h2>改进建议</h2>
                <ul>
        """

        for rec in report.get("recommendations", []):
            html += f"<li>{rec}</li>"

        html += """
                </ul>
            </div>
        </body>
        </html>
        """

        return html

    def _get_coverage_class(self, rate: float) -> str:
        """获取覆盖率CSS类"""
        if rate >= 0.8:
            return "coverage-high"
        elif rate >= 0.6:
            return "coverage-medium"
        else:
            return "coverage-low"


def main():
    """主函数"""

    # 示例测试结果（实际使用时会从pytest结果中获取）
    sample_results = [
        ContractTestResult(
            test_name="test_user_login_contract",
            endpoint="/api/auth/login",
            method="POST",
            status="passed",
            duration=0.234,
            violations=[],
        ),
        ContractTestResult(
            test_name="test_get_market_data_contract",
            endpoint="/api/market/data",
            method="GET",
            status="passed",
            duration=0.156,
            violations=[],
        ),
        ContractTestResult(
            test_name="test_create_strategy_contract",
            endpoint="/api/strategies",
            method="POST",
            status="failed",
            duration=0.345,
            violations=[{"violation_type": "schema_mismatch", "message": "Response schema validation failed"}],
        ),
    ]

    # 生成报告
    reporter = ContractCoverageReporter()
    report = reporter.generate_coverage_report(sample_results)

    # 保存报告
    json_file = reporter.save_report(report, "json")
    html_file = reporter.save_report(report, "html")

    print(f"报告生成完成:")
    print(f"  JSON: {json_file}")
    print(f"  HTML: {html_file}")

    # 打印摘要
    metrics = report["metrics"]
    print(f"\n覆盖率摘要:")
    print(f"  端点覆盖率: {metrics['endpoint_coverage_rate']:.1%}")
    print(f"  操作覆盖率: {metrics['operation_coverage_rate']:.1%}")
    print(f"  建议数量: {len(report.get('recommendations', []))}")


if __name__ == "__main__":
    main()
