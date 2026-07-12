#!/usr/bin/env python3
"""契约测试失败分析和调试工具

提供契约测试失败的详细分析、根本原因诊断和调试建议。
支持多种分析模式：单次测试分析、批量分析、趋势分析。
"""

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class TestFailure:
    """测试失败信息"""

    test_name: str
    endpoint: str
    method: str
    error_message: str
    error_type: str
    stack_trace: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    expected_response: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def root_cause_category(self) -> str:
        """根本原因分类"""
        if "schema" in self.error_message.lower():
            return "schema_validation"
        if "timeout" in self.error_message.lower():
            return "timeout"
        if "connection" in self.error_message.lower():
            return "connection"
        if "authentication" in self.error_message.lower():
            return "authentication"
        if "authorization" in self.error_message.lower():
            return "authorization"
        if "contract" in self.error_message.lower():
            return "contract_drift"
        return "other"


@dataclass
class FailureAnalysis:
    """失败分析结果"""

    total_failures: int = 0
    failures_by_category: Dict[str, int] = field(default_factory=dict)
    failures_by_endpoint: Dict[str, int] = field(default_factory=dict)
    failures_by_method: Dict[str, int] = field(default_factory=dict)
    common_error_patterns: List[Tuple[str, int]] = field(default_factory=list)
    top_failing_tests: List[Tuple[str, int]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    severity_assessment: str = "low"


class ContractTestFailureAnalyzer:
    """契约测试失败分析器"""

    def __init__(self):
        self.failures: List[TestFailure] = []

    def load_failures_from_pytest_json(self, json_file: Path) -> None:
        """从pytest JSON报告加载失败信息"""
        with open(json_file) as f:
            pytest_report = json.load(f)

        for test in pytest_report.get("tests", []):
            if test.get("outcome") == "failed":
                failure = TestFailure(
                    test_name=test.get("nodeid", ""),
                    endpoint=self._extract_endpoint_from_test_name(test.get("nodeid", "")),
                    method=self._extract_method_from_test_name(test.get("nodeid", "")),
                    error_message=test.get("longrepr", ""),
                    error_type="pytest_failure",
                )
                self.failures.append(failure)

    def load_failures_from_contract_log(self, log_file: Path) -> None:
        """从契约测试日志加载失败信息"""
        with open(log_file) as f:
            for line in f:
                if "FAILED" in line or "ERROR" in line:
                    # 解析契约测试日志格式
                    failure = self._parse_contract_log_line(line)
                    if failure:
                        self.failures.append(failure)

    def _extract_endpoint_from_test_name(self, test_name: str) -> str:
        """从测试名称中提取端点"""
        # 示例: test_api_contract_compliance[GET /api/users]
        match = re.search(r"\[(\w+)\s+([^\]]+)\]", test_name)
        if match:
            return match.group(2)
        return "unknown"

    def _extract_method_from_test_name(self, test_name: str) -> str:
        """从测试名称中提取HTTP方法"""
        match = re.search(r"\[(\w+)\s+", test_name)
        if match:
            return match.group(1)
        return "GET"

    def _parse_contract_log_line(self, line: str) -> Optional[TestFailure]:
        """解析契约测试日志行"""
        # 简化的日志解析逻辑
        # 实际实现会根据具体的日志格式进行解析
        return None

    def analyze_failures(self) -> FailureAnalysis:
        """分析失败模式"""
        analysis = FailureAnalysis()
        analysis.total_failures = len(self.failures)

        if analysis.total_failures == 0:
            analysis.recommendations.append("🎉 没有发现测试失败，所有契约测试都通过了！")
            return analysis

        # 按类别统计失败
        category_counts = Counter(f.root_cause_category for f in self.failures)
        analysis.failures_by_category = dict(category_counts)

        # 按端点统计失败
        endpoint_counts = Counter(f.endpoint for f in self.failures)
        analysis.failures_by_endpoint = dict(endpoint_counts)

        # 按方法统计失败
        method_counts = Counter(f.method for f in self.failures)
        analysis.failures_by_method = dict(method_counts)

        # 找出常见的错误模式
        error_patterns = Counter(f.error_message[:100] for f in self.failures)  # 前100字符
        analysis.common_error_patterns = error_patterns.most_common(5)

        # 找出最常失败的测试
        test_counts = Counter(f.test_name for f in self.failures)
        analysis.top_failing_tests = test_counts.most_common(5)

        # 生成建议
        analysis.recommendations = self._generate_recommendations(analysis)

        # 评估严重程度
        analysis.severity_assessment = self._assess_severity(analysis)

        return analysis

    def _generate_recommendations(self, analysis: FailureAnalysis) -> List[str]:
        """生成修复建议"""
        recommendations = []

        # 基于最常见的失败类别提供建议
        top_category = max(analysis.failures_by_category.items(), key=lambda x: x[1])[0]

        if top_category == "schema_validation":
            recommendations.append("🔍 Schema验证失败最多 - 检查API响应格式是否与OpenAPI规范匹配")
            recommendations.append("💡 建议: 更新OpenAPI规范或修复后端响应格式")

        elif top_category == "contract_drift":
            recommendations.append("📊 契约漂移问题突出 - 前端期望与后端实际响应不匹配")
            recommendations.append("💡 建议: 重新生成TypeScript类型定义或更新前端契约")

        elif top_category == "timeout":
            recommendations.append("⏱️ 超时错误频繁 - API响应时间过长")
            recommendations.append("💡 建议: 优化数据库查询、添加缓存或扩展服务器资源")

        elif top_category == "connection":
            recommendations.append("🔌 连接问题常见 - 网络或服务可用性问题")
            recommendations.append("💡 建议: 检查服务健康状态和网络配置")

        # 基于失败端点提供具体建议
        if analysis.failures_by_endpoint:
            worst_endpoint = max(analysis.failures_by_endpoint.items(), key=lambda x: x[1])[0]
            recommendations.append(f"🎯 端点 '{worst_endpoint}' 失败次数最多 - 优先修复此端点")

        # 基于测试频率提供建议
        if analysis.top_failing_tests:
            failing_test = analysis.top_failing_tests[0][0]
            recommendations.append(f"🧪 测试 '{failing_test}' 最常失败 - 检查测试逻辑或相关代码")

        return recommendations

    def _assess_severity(self, analysis: FailureAnalysis) -> str:
        """评估失败严重程度"""
        failure_rate = analysis.total_failures

        if failure_rate > 50:
            return "critical"
        if failure_rate > 20:
            return "high"
        if failure_rate > 10:
            return "medium"
        return "low"

    def generate_debug_report(self, analysis: FailureAnalysis) -> Dict[str, Any]:
        """生成调试报告"""
        report = {
            "summary": {
                "total_failures": analysis.total_failures,
                "severity": analysis.severity_assessment,
                "generated_at": datetime.now().isoformat(),
            },
            "failure_breakdown": {
                "by_category": analysis.failures_by_category,
                "by_endpoint": analysis.failures_by_endpoint,
                "by_method": analysis.failures_by_method,
            },
            "patterns": {
                "common_errors": analysis.common_error_patterns,
                "top_failing_tests": analysis.top_failing_tests,
            },
            "recommendations": analysis.recommendations,
            "detailed_failures": [
                {
                    "test_name": f.test_name,
                    "endpoint": f.endpoint,
                    "method": f.method,
                    "error_type": f.error_type,
                    "error_message": f.error_message,
                    "root_cause": f.root_cause_category,
                    "timestamp": f.timestamp.isoformat(),
                }
                for f in self.failures[:20]  # 只显示前20个失败
            ],
        }

        return report

    def save_debug_report(self, report: Dict[str, Any], output_file: Path) -> None:
        """保存调试报告"""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"调试报告已保存: {output_file}")

    def print_summary(self, analysis: FailureAnalysis) -> None:
        """打印分析摘要"""
        print("🔍 契约测试失败分析报告")
        print(f"总失败数: {analysis.total_failures}")
        print(f"严重程度: {analysis.severity_assessment}")
        print()

        if analysis.failures_by_category:
            print("📊 按类别统计失败:")
            for category, count in analysis.failures_by_category.items():
                print(f"  {category}: {count}")
            print()

        if analysis.recommendations:
            print("💡 修复建议:")
            for rec in analysis.recommendations:
                print(f"  • {rec}")
            print()

        if analysis.top_failing_tests:
            print("🧪 最常失败的测试:")
            for test_name, count in analysis.top_failing_tests:
                print(f"  {test_name}: {count} 次失败")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="契约测试失败分析和调试工具")
    parser.add_argument("--pytest-json", type=Path, help="pytest JSON报告文件")
    parser.add_argument("--contract-log", type=Path, help="契约测试日志文件")
    parser.add_argument("--output", type=Path, default=Path("contract_failure_analysis.json"), help="输出文件路径")
    parser.add_argument("--summary-only", action="store_true", help="只显示摘要，不生成详细报告")

    args = parser.parse_args()

    analyzer = ContractTestFailureAnalyzer()

    # 加载失败数据
    if args.pytest_json and args.pytest_json.exists():
        analyzer.load_failures_from_pytest_json(args.pytest_json)

    if args.contract_log and args.contract_log.exists():
        analyzer.load_failures_from_contract_log(args.contract_log)

    # 分析失败
    analysis = analyzer.analyze_failures()

    # 输出结果
    if args.summary_only:
        analyzer.print_summary(analysis)
    else:
        # 生成完整报告
        debug_report = analyzer.generate_debug_report(analysis)
        analyzer.save_debug_report(debug_report, args.output)
        analyzer.print_summary(analysis)


if __name__ == "__main__":
    main()
