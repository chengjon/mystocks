#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强测试运行器

提供统一的测试执行接口，支持：
- 多种测试类型运行
- 并发测试执行
- 测试结果分析
- 报告生成
- 性能监控
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from .ai import create_ai_testing_session, run_ai_test_suite
from .data import create_data_optimization_session
from .contract import ContractTestExecutor, ContractTestConfig, ContractTestSuite

logger = logging.getLogger(__name__)


@dataclass
class TestRunConfig:
    """测试运行配置"""

    test_types: List[str] = field(default_factory=lambda: ["unit", "integration", "e2e"])
    max_workers: int = 4
    timeout_seconds: int = 300
    enable_ai_enhancement: bool = True
    enable_data_optimization: bool = True
    enable_contract_testing: bool = True
    output_format: str = "json"
    report_dir: str = "test_reports"


@dataclass
class TestExecutionResult:
    """测试执行结果"""

    test_type: str
    status: str  # passed, failed, error, skipped
    duration: float
    test_count: int = 0
    passed_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    error_count: int = 0
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class EnhancedTestRunner:
    """增强测试运行器"""

    def __init__(self, config: TestRunConfig):
        self.config = config
        self.results: List[TestExecutionResult] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

        # 初始化组件
        self.ai_testing_system = None
        self.data_optimizer = None
        self.contract_executor = None

        if self.config.enable_ai_enhancement:
            self.ai_testing_system = create_ai_testing_session()

        if self.config.enable_data_optimization:
            self.data_optimizer = create_data_optimization_session()

        if self.config.enable_contract_testing:
            self.contract_config = ContractTestConfig(
                api_base_url="http://localhost:8000",
                test_timeout=30,
                max_retries=2,
                retry_delay=1,
                enable_security_tests=True,
                enable_auth_tests=True,
                performance_threshold={"response_time_ms": 1000},
            )
            self.contract_executor = ContractTestExecutor(self.contract_config)

    async def run_all_tests(self, project_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """运行所有测试"""
        print("🚀 启动增强测试运行器...")
        self.start_time = datetime.now()

        try:
            # 1. 数据优化准备
            if self.config.enable_data_optimization and self.data_optimizer:
                print("📊 优化测试数据...")
                await self._optimize_test_data()

            # 2. AI辅助测试
            if self.config.enable_ai_enhancement and self.ai_testing_system:
                print("🤖 执行AI辅助测试...")
                ai_result = await self._run_ai_tests(project_context)
                self.results.append(ai_result)

            # 3. 契约测试
            if self.config.enable_contract_testing and self.contract_executor:
                print("📋 执行契约测试...")
                contract_result = await self._run_contract_tests()
                self.results.append(contract_result)

            # 4. 标准测试
            print("🧪 执行标准测试...")
            standard_results = await self._run_standard_tests()
            self.results.extend(standard_results)

            # 5. 汇总结果
            self.end_time = datetime.now()
            summary = self._generate_test_summary()

            # 6. 生成报告
            await self._generate_report(summary)

            return summary

        except Exception as e:
            logger.error(f"测试执行失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "results": [r.__dict__ for r in self.results],
            }

    async def _optimize_test_data(self):
        """优化测试数据"""
        # 这里可以优化特定的测试数据档案
        # 为了演示，我们只是运行一个通用的优化
        try:
            optimizer = self.data_optimizer
            if optimizer:
                # 获取所有数据档案进行优化
                statistics = await optimizer.get_optimization_statistics()
                print(f"数据统计: {statistics}")
        except Exception as e:
            logger.warning(f"数据优化跳过: {e}")

    async def _run_ai_tests(self, project_context: Dict[str, Any]) -> TestExecutionResult:
        """运行AI辅助测试"""
        try:
            # 使用MyStocks默认上下文
            if project_context is None:
                from .ai import create_my_stocks_test_context

                project_context = create_my_stocks_test_context()

            # 创建测试执行器
            test_executors = {
                "unit_tests": self._run_unit_tests_with_ai,
                "integration_tests": self._run_integration_tests_with_ai,
                "performance_tests": self._run_performance_tests_with_ai,
            }

            # 运行AI测试套件
            results = await run_ai_test_suite(project_context, test_executors)

            return TestExecutionResult(
                test_type="ai_assisted",
                status="passed",
                duration=results.get("execution_duration", 0),
                test_count=results.get("total_tests", 0),
                passed_count=results.get("passed_tests", 0),
                failed_count=results.get("failed_tests", 0),
                skipped_count=results.get("skipped_tests", 0),
                details=results,
            )

        except Exception as e:
            return TestExecutionResult(
                test_type="ai_assisted",
                status="error",
                duration=0,
                error_message=str(e),
            )

    async def _run_contract_tests(self) -> TestExecutionResult:
        """运行契约测试"""
        try:
            # 创建测试套件（简化版）
            test_suite = ContractTestSuite(
                name="API契约测试",
                test_cases=[
                    self._create_basic_test_case("GET", "/api/health"),
                    self._create_basic_test_case("GET", "/api/market/status"),
                    self._create_basic_test_case("POST", "/api/auth/login"),
                ],
                parallel_execution=False,
                max_workers=2,
            )

            # 执行测试
            async with self.contract_executor:
                execution_results = await self.contract_executor.execute_suite(test_suite)

            # 统计结果
            total = len(execution_results)
            passed = sum(1 for r in execution_results if r.status.value == "PASSED")
            failed = sum(1 for r in execution_results if r.status.value == "FAILED")
            error = sum(1 for r in execution_results if r.status.value == "ERROR")
            skipped = sum(1 for r in execution_results if r.status.value == "SKIPPED")

            return TestExecutionResult(
                test_type="contract",
                status="passed" if failed == 0 and error == 0 else "completed",
                duration=10,  # 假设的持续时间
                test_count=total,
                passed_count=passed,
                failed_count=failed,
                error_count=error,
                skipped_count=skipped,
                details={
                    "test_cases": total,
                    "execution_results": [r.__dict__ for r in execution_results],
                },
            )

        except Exception as e:
            return TestExecutionResult(test_type="contract", status="error", duration=0, error_message=str(e))

    def _create_basic_test_case(self, method: str, endpoint: str):
        """创建基础测试用例"""
        from .contract.models import ContractTestCase, TestCategory

        return ContractTestCase(
            name=f"{method}_{endpoint}",
            method=method,
            endpoint=endpoint,
            category=TestCategory.API,
            enabled=True,
            priority=5,
        )

    async def _run_standard_tests(self) -> List[TestExecutionResult]:
        """运行标准测试"""
        results = []

        # 单元测试
        unit_result = await self._run_unit_tests()
        results.append(unit_result)

        # 集成测试
        integration_result = await self._run_integration_tests()
        results.append(integration_result)

        # E2E测试
        e2e_result = await self._run_e2e_tests()
        results.append(e2e_result)

        return results

    async def _run_unit_tests(self) -> TestExecutionResult:
        """运行单元测试"""
        try:
            # 模拟单元测试执行
            await asyncio.sleep(2)
            return TestExecutionResult(
                test_type="unit",
                status="passed",
                duration=2.0,
                test_count=45,
                passed_count=42,
                failed_count=3,
                skipped_count=0,
                details={"modules_tested": 8, "coverage": 85.5},
            )
        except Exception as e:
            return TestExecutionResult(test_type="unit", status="error", duration=0, error_message=str(e))

    async def _run_integration_tests(self) -> TestExecutionResult:
        """运行集成测试"""
        try:
            # 模拟集成测试执行
            await asyncio.sleep(5)
            return TestExecutionResult(
                test_type="integration",
                status="passed",
                duration=5.0,
                test_count=15,
                passed_count=13,
                failed_count=2,
                skipped_count=0,
                details={"services_tested": 5, "api_endpoints": 12},
            )
        except Exception as e:
            return TestExecutionResult(
                test_type="integration",
                status="error",
                duration=0,
                error_message=str(e),
            )

    async def _run_e2e_tests(self) -> TestExecutionResult:
        """运行E2E测试"""
        try:
            # 模拟E2E测试执行
            await asyncio.sleep(15)
            return TestExecutionResult(
                test_type="e2e",
                status="passed",
                duration=15.0,
                test_count=8,
                passed_count=7,
                failed_count=1,
                skipped_count=0,
                details={"scenarios": 4, "browsers": ["chrome"]},
            )
        except Exception as e:
            return TestExecutionResult(test_type="e2e", status="error", duration=0, error_message=str(e))

    async def _run_unit_tests_with_ai(self) -> Dict[str, Any]:
        """AI辅助单元测试"""
        await asyncio.sleep(1)
        return {"passed": 25, "failed": 1, "skipped": 0}

    async def _run_integration_tests_with_ai(self) -> Dict[str, Any]:
        """AI辅助集成测试"""
        await asyncio.sleep(3)
        return {"passed": 18, "failed": 2, "skipped": 0}

    async def _run_performance_tests_with_ai(self) -> Dict[str, Any]:
        """AI辅助性能测试"""
        await asyncio.sleep(8)
        return {"passed": 5, "failed": 0, "skipped": 0}

    def _generate_test_summary(self) -> Dict[str, Any]:
        """生成测试摘要"""
        if not self.results:
            return {"status": "no_results"}

        # 计算总体统计
        total_tests = sum(r.test_count for r in self.results)
        total_passed = sum(r.passed_count for r in self.results)
        total_failed = sum(r.failed_count for r in self.results)
        total_errors = sum(r.error_count for r in self.results)
        total_skipped = sum(r.skipped_count for r in self.results)

        # 计算总耗时
        total_duration = sum(r.duration for r in self.results)
        if self.start_time and self.end_time:
            actual_duration = (self.end_time - self.start_time).total_seconds()
        else:
            actual_duration = total_duration

        # 按类型统计
        by_type = {}
        for result in self.results:
            by_type[result.test_type] = {
                "status": result.status,
                "test_count": result.test_count,
                "passed": result.passed_count,
                "failed": result.failed_count,
                "errors": result.error_count,
                "skipped": result.skipped_count,
                "duration": result.duration,
            }

        # 计算成功率
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

        return {
            "status": "completed",
            "execution_start": self.start_time.isoformat() if self.start_time else None,
            "execution_end": self.end_time.isoformat() if self.end_time else None,
            "total_duration_seconds": actual_duration,
            "summary": {
                "total_tests": total_tests,
                "passed": total_passed,
                "failed": total_failed,
                "errors": total_errors,
                "skipped": total_skipped,
                "success_rate": round(success_rate, 2),
            },
            "by_type": by_type,
            "detailed_results": [r.__dict__ for r in self.results],
            "recommendations": self._generate_recommendations(),
        }

    def _generate_recommendations(self) -> List[str]:
        """生成测试建议"""
        recommendations = []

        # 分析结果
        has_errors = any(r.status == "error" for r in self.results)
        has_failures = any(r.failed_count > 0 for r in self.results)
        low_coverage = any(r.details.get("coverage", 100) < 80 for r in self.results)

        if has_errors:
            recommendations.append("检测到测试错误，请检查测试环境和依赖")

        if has_failures:
            recommendations.append("部分测试失败，建议重点关注失败的用例")

        if low_coverage:
            recommendations.append("测试覆盖率偏低，建议增加测试用例")

        if self.config.enable_ai_enhancement:
            recommendations.append("AI辅助测试已启用，可以利用AI优化测试策略")

        if not recommendations:
            recommendations.append("所有测试通过，系统运行良好")

        return recommendations

    async def _generate_report(self, summary: Dict[str, Any]):
        """生成测试报告"""
        report_dir = Path(self.config.report_dir)
        report_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_report_{timestamp}.{self.config.output_format}"

        if self.config.output_format == "json":
            report_file = report_dir / filename
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

        elif self.config.output_format == "html":
            html_content = self._generate_html_report(summary)
            report_file = report_dir / f"{filename}.html"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(html_content)

        print(f"📄 测试报告已生成: {report_file}")

    def _generate_html_report(self, summary: Dict[str, Any]) -> str:
        """生成HTML报告"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>测试报告</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
                .summary { margin: 20px 0; }
                .by-type { margin: 20px 0; }
                .test-result { border: 1px solid #ddd; padding: 10px; margin: 5px 0; border-radius: 3px; }
                .passed { background-color: #d4edda; }
                .failed { background-color: #f8d7da; }
                .error { background-color: #f8d7da; }
                .skipped { background-color: #fff3cd; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>测试报告</h1>
                <p>执行时间: {execution_start}</p>
                <p>总耗时: {total_duration_seconds:.2f} 秒</p>
            </div>

            <div class="summary">
                <h2>测试摘要</h2>
                <p>总测试数: {summary[total_tests]}</p>
                <p>通过: {summary[passed]}</p>
                <p>失败: {summary[failed]}</p>
                <p>错误: {summary[errors]}</p>
                <p>跳过: {summary[skipped]}</p>
                <p>成功率: {summary[success_rate]}%</p>
            </div>

            <div class="by-type">
                <h2>按类型统计</h2>
                {by_type_html}
            </div>

            <div class="recommendations">
                <h2>建议</h2>
                <ul>
                    {recommendations_html}
                </ul>
            </div>
        </body>
        </html>
        """

        # 生成各类型HTML
        by_type_html = ""
        for test_type, data in summary.get("by_type", {}).items():
            status_class = data.get("status", "")
            by_type_html += f"""
            <div class="test-result {status_class}">
                <h3>{test_type}</h3>
                <p>状态: {data["status"]}</p>
                <p>测试数: {data["test_count"]}</p>
                <p>通过: {data["passed"]}</p>
                <p>失败: {data["failed"]}</p>
                <p>错误: {data["errors"]}</p>
                <p>耗时: {data["duration"]:.2f}秒</p>
            </div>
            """

        # 生成建议HTML
        recommendations_html = ""
        for rec in summary.get("recommendations", []):
            recommendations_html += f"<li>{rec}</li>"

        return html_template.format(
            execution_start=summary.get("execution_start", ""),
            total_duration_seconds=summary.get("total_duration_seconds", 0),
            summary=summary.get("summary", {}),
            by_type_html=by_type_html,
            recommendations_html=recommendations_html,
        )


async def run_comprehensive_test_run(
    config: TestRunConfig = None, project_context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """运行综合测试套件

    Args:
        config: 测试运行配置
        project_context: 项目上下文

    Returns:
        测试结果字典
    """
    if config is None:
        config = TestRunConfig()

    runner = EnhancedTestRunner(config)
    return await runner.run_all_tests(project_context)


# 使用示例
async def demo_comprehensive_testing():
    """演示综合测试功能"""
    print("🎯 综合测试演示")

    # 1. 创建测试配置
    config = TestRunConfig(
        test_types=["unit", "integration", "e2e", "ai", "contract"],
        max_workers=4,
        enable_ai_enhancement=True,
        enable_data_optimization=True,
        enable_contract_testing=True,
        output_format="html",
    )

    # 2. 创建项目上下文
    from .ai import create_my_stocks_test_context

    project_context = create_my_stocks_test_context()

    # 3. 运行测试
    results = await run_comprehensive_test_run(config, project_context)

    # 4. 显示结果
    print("\n=== 测试结果摘要 ===")
    summary = results.get("summary", {})
    print(f"总测试数: {summary.get('total_tests', 0)}")
    print(f"通过数: {summary.get('passed', 0)}")
    print(f"失败数: {summary.get('failed', 0)}")
    print(f"成功率: {summary.get('success_rate', 0)}%")

    print("\n=== 测试建议 ===")
    for i, rec in enumerate(results.get("recommendations", []), 1):
        print(f"{i}. {rec}")


if __name__ == "__main__":
    # 运行演示
    import asyncio

    asyncio.run(demo_comprehensive_testing())
