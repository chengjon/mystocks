#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合测试管理器

提供一个统一的测试管理接口，集成所有测试组件并协调测试执行流程。
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import logging
from abc import ABC, abstractmethod

from statistics import mean

# 导入所有测试组件
from .ai.test_intelligent_generator import TestDataGenerator as AITestDataGenerator
from .contract.test_contract_validator import ContractTestValidator
from .contract.test_contract_generator import APIContractGenerator
from .contract.test_contract_executor import ContractTestExecutor
from .performance.test_performance_suite import PerformanceTestSuite
from .chaos.test_fault_injection import FaultInjectionSystem
from .chaos.test_resilience import ResilienceTestingFramework
from .security.test_security_vulnerabilities import SecurityVulnerabilityScanner
from .security.test_security_compliance import SecurityComplianceTester
from .data.test_data_manager import TestDataOptimizer


class TestType(Enum):
    """测试类型枚举"""

    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    AI_ASSISTED = "ai_assisted"
    CONTRACT = "contract"
    PERFORMANCE = "performance"
    CHAOS = "chaos"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    COMPREHENSIVE = "comprehensive"


class TestStatus(Enum):
    """测试状态枚举"""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class TestCase:
    """测试用例定义"""

    id: str
    name: str
    test_type: TestType
    description: str
    priority: int = 1
    timeout: int = 300
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    setup: Optional[Callable] = None
    teardown: Optional[Callable] = None
    execute: Optional[Callable] = None
    expected_result: Any = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class TestSuite:
    """测试套件定义"""

    id: str
    name: str
    description: str
    test_cases: List[str] = field(default_factory=list)
    test_type: TestType = TestType.COMPREHENSIVE
    execution_order: str = "sequential"  # sequential, parallel, adaptive
    max_parallel: int = 5
    timeout: int = 3600
    setup: Optional[Callable] = None
    teardown: Optional[Callable] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TestExecutionResult:
    """测试执行结果"""

    test_id: str
    test_name: str
    test_type: TestType
    status: TestStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    error_message: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    artifacts: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 0


class _TestComponentInterface(ABC):
    __test__ = False
    """测试组件接口"""

    @abstractmethod
    async def run_test(self, test_case: TestCase) -> TestExecutionResult:
        """运行单个测试"""
        pass

    @abstractmethod
    async def get_test_status(self, test_id: str) -> TestStatus:
        """获取测试状态"""
        pass

    @abstractmethod
    async def cleanup_resources(self):
        """清理资源"""
        pass


class TestExecutionEngine:
    """测试执行引擎"""

    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_tests: Dict[str, asyncio.Task] = {}
        self.test_results: Dict[str, TestExecutionResult] = {}

    async def execute_tests_sequentially(
        self, test_cases: List[TestCase]
    ) -> List[TestExecutionResult]:
        """顺序执行测试"""
        results = []

        for test_case in test_cases:
            try:
                result = await self._execute_single_test(test_case)
                results.append(result)
                self.test_results[test_case.id] = result
            except Exception as e:
                error_result = TestExecutionResult(
                    test_id=test_case.id,
                    test_name=test_case.name,
                    test_type=test_case.test_type,
                    status=TestStatus.FAILED,
                    error_message=str(e),
                )
                results.append(error_result)
                self.test_results[test_case.id] = error_result

        return results

    async def execute_tests_parallelly(
        self, test_cases: List[TestCase]
    ) -> List[TestExecutionResult]:
        """并行执行测试"""
        semaphore = asyncio.Semaphore(self.max_workers)
        results = []

        async def execute_with_semaphore(test_case):
            async with semaphore:
                try:
                    result = await self._execute_single_test(test_case)
                    self.test_results[test_case.id] = result
                    return result
                except Exception as e:
                    error_result = TestExecutionResult(
                        test_id=test_case.id,
                        test_name=test_case.name,
                        test_type=test_case.test_type,
                        status=TestStatus.FAILED,
                        error_message=str(e),
                    )
                    self.test_results[test_case.id] = error_result
                    return error_result

        tasks = [execute_with_semaphore(test_case) for test_case in test_cases]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理异常结果
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                print(f"测试执行失败: {str(result)}")
            else:
                processed_results.append(result)

        return processed_results

    async def _execute_single_test(self, test_case: TestCase) -> TestExecutionResult:
        """执行单个测试"""
        start_time = datetime.now()
        result = TestExecutionResult(
            test_id=test_case.id,
            test_name=test_case.name,
            test_type=test_case.test_type,
            status=TestStatus.RUNNING,
            start_time=start_time,
            tags=test_case.tags,
        )

        try:
            # 执行设置
            if test_case.setup:
                await test_case.setup()

            # 执行测试
            if test_case.execute:
                test_result = await test_case.execute()
                result.result_data = test_result
            else:
                raise Exception("测试执行函数未提供")

            # 执行清理
            if test_case.teardown:
                await test_case.teardown()

            result.status = TestStatus.PASSED
            result.end_time = datetime.now()
            result.duration = (result.end_time - result.start_time).total_seconds()

        except asyncio.TimeoutError:
            result.status = TestStatus.TIMEOUT
            result.error_message = f"测试超时（{test_case.timeout}秒）"
        except Exception as e:
            result.status = TestStatus.FAILED
            result.error_message = str(e)
        finally:
            result.end_time = datetime.now()
            if result.duration is None:
                result.duration = (result.end_time - result.start_time).total_seconds()

        return result


class ComprehensiveTestManager:
    """综合测试管理器"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = (
            config_path
            or "/opt/claude/mystocks_spec/tests/integration/test_config.json"
        )
        self.config = self._load_config()

        # 初始化测试组件
        self.ai_generator = AITestDataGenerator()
        self.contract_validator = ContractTestValidator()
        self.contract_generator = APIContractGenerator()
        self.contract_executor = ContractTestExecutor()
        self.performance_suite = PerformanceTestSuite()
        self.fault_injection = FaultInjectionSystem()
        self.resilience_framework = ResilienceTestingFramework()
        self.security_scanner = SecurityVulnerabilityScanner()
        self.compliance_tester = SecurityComplianceTester()
        self.data_optimizer = TestDataOptimizer()

        # 初始化执行引擎
        self.execution_engine = TestExecutionEngine(
            max_workers=self.config.get("max_workers", 10)
        )

        # 测试用例和套件存储
        self.test_cases: Dict[str, TestCase] = {}
        self.test_suites: Dict[str, TestSuite] = {}

        # 统计信息
        self.stats = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "total_duration": 0,
            "average_duration": 0,
            "last_execution_time": None,
        }

        # 日志配置
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "max_workers": 10,
            "timeout": 300,
            "retry_count": 3,
            "parallel_execution": True,
            "enable_performance_monitoring": True,
            "enable_compliance_reporting": True,
            "artifact_storage_path": "/tmp/test_artifacts",
        }

    def register_test_case(self, test_case: TestCase):
        """注册测试用例"""
        self.test_cases[test_case.id] = test_case
        self.stats["total_tests"] += 1
        print(f"✓ 注册测试用例: {test_case.name} ({test_case.id})")

    def register_test_suite(self, test_suite: TestSuite):
        """注册测试套件"""
        self.test_suites[test_suite.id] = test_suite
        print(f"✓ 注册测试套件: {test_suite.name} ({test_suite.id})")

    async def run_test_by_id(
        self, test_id: str, retry_count: int = 0
    ) -> TestExecutionResult:
        """运行指定ID的测试"""
        if test_id not in self.test_cases:
            raise ValueError(f"测试用例不存在: {test_id}")

        test_case = self.test_cases[test_id]

        # 执行测试
        result = await self.execution_engine._execute_single_test(test_case)

        # 更新统计信息
        if result.status == TestStatus.PASSED:
            self.stats["passed_tests"] += 1
        elif result.status == TestStatus.FAILED:
            self.stats["failed_tests"] += 1
        elif result.status == TestStatus.SKIPPED:
            self.stats["skipped_tests"] += 1

        return result

    async def run_test_suite(
        self, suite_id: str, execution_mode: str = "adaptive"
    ) -> List[TestExecutionResult]:
        """运行测试套件"""
        if suite_id not in self.test_suites:
            raise ValueError(f"测试套件不存在: {suite_id}")

        suite = self.test_suites[suite_id]
        test_cases = [
            self.test_cases[case_id]
            for case_id in suite.test_cases
            if case_id in self.test_cases
        ]

        print(f"\n🚀 运行测试套件: {suite.name}")
        print(f"📊 测试数量: {len(test_cases)}")
        print(f"⚡ 执行模式: {execution_mode}")

        start_time = datetime.now()

        # 根据执行模式运行测试
        if execution_mode == "sequential":
            results = await self.execution_engine.execute_tests_sequentially(test_cases)
        elif execution_mode == "parallel":
            results = await self.execution_engine.execute_tests_parallelly(test_cases)
        else:  # adaptive
            # 自适应执行：根据测试类型决定执行策略
            results = await self._execute_tests_adaptively(test_cases)

        # 更新统计信息
        end_time = datetime.now()
        suite_duration = (end_time - start_time).total_seconds()
        self.stats["last_execution_time"] = end_time

        # 计算总体统计
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.status == TestStatus.PASSED)
        failed_tests = sum(1 for r in results if r.status == TestStatus.FAILED)

        print("\n✅ 测试套件执行完成")
        print(f"📈 总耗时: {suite_duration:.2f}秒")
        print(f"✅ 通过: {passed_tests}/{total_tests}")
        print(f"❌ 失败: {failed_tests}/{total_tests}")
        print(f"📊 成功率: {passed_tests / total_tests * 100:.1f}%")

        # 生成套件结果报告
        suite_result = self._generate_suite_report(suite, results, suite_duration)

        return results

    async def _execute_tests_adaptively(
        self, test_cases: List[TestCase]
    ) -> List[TestExecutionResult]:
        """自适应执行测试"""
        # 按测试类型分组
        by_type = {}
        for test_case in test_cases:
            test_type = test_case.test_type
            if test_type not in by_type:
                by_type[test_type] = []
            by_type[test_type].append(test_case)

        results = []

        # 根据测试类型选择执行策略
        for test_type, cases in by_type.items():
            if test_type in [
                TestType.PERFORMANCE,
                TestType.SECURITY,
                TestType.COMPLIANCE,
            ]:
                # 性能、安全、合规测试：顺序执行
                case_results = await self.execution_engine.execute_tests_sequentially(
                    cases
                )
            else:
                # 其他测试：并行执行
                case_results = await self.execution_engine.execute_tests_parallelly(
                    cases
                )
            results.extend(case_results)

        return results

    def _generate_suite_report(
        self, suite: TestSuite, results: List[TestExecutionResult], duration: float
    ) -> Dict[str, Any]:
        """生成套件报告"""
        passed_count = sum(1 for r in results if r.status == TestStatus.PASSED)
        failed_count = sum(1 for r in results if r.status == TestStatus.FAILED)
        skipped_count = sum(1 for r in results if r.status == TestStatus.SKIPPED)

        by_type = {}
        for result in results:
            test_type = result.test_type.value
            if test_type not in by_type:
                by_type[test_type] = {"passed": 0, "failed": 0, "total": 0}
            by_type[test_type]["total"] += 1
            if result.status == TestStatus.PASSED:
                by_type[test_type]["passed"] += 1
            elif result.status == TestStatus.FAILED:
                by_type[test_type]["failed"] += 1

        # 计算平均执行时间
        valid_durations = [r.duration for r in results if r.duration is not None]
        avg_duration = mean(valid_durations) if valid_durations else 0

        report = {
            "suite_id": suite.id,
            "suite_name": suite.name,
            "execution_time": datetime.now().isoformat(),
            "duration_seconds": round(duration, 2),
            "summary": {
                "total_tests": len(results),
                "passed": passed_count,
                "failed": failed_count,
                "skipped": skipped_count,
                "success_rate": round(passed_count / len(results) * 100, 1)
                if results
                else 0,
            },
            "by_type": by_type,
            "performance": {
                "average_duration_seconds": round(avg_duration, 2),
                "longest_test": max(valid_durations) if valid_durations else 0,
                "shortest_test": min(valid_durations) if valid_durations else 0,
            },
            "failed_tests": [
                {"id": r.test_id, "name": r.test_name, "error": r.error_message}
                for r in results
                if r.status == TestStatus.FAILED
            ],
        }

        # 保存报告
        report_path = f"/tmp/suite_report_{suite.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"📄 套件报告已保存: {report_path}")
        return report

    async def run_comprehensive_test_session(self) -> Dict[str, Any]:
        """运行综合测试会话"""
        print("\n🎯 开始综合测试会话")
        print(f"⏰ 开始时间: {datetime.now()}")
        print(f"📊 已注册测试用例: {len(self.test_cases)}")
        print(f"📊 已注册测试套件: {len(self.test_suites)}")

        session_start = datetime.now()
        session_results = {}

        # 执行所有测试套件
        for suite_id in self.test_suites:
            try:
                suite_results = await self.run_test_suite(
                    suite_id, execution_mode="adaptive"
                )
                session_results[suite_id] = suite_results
            except Exception as e:
                print(f"❌ 测试套件 {suite_id} 执行失败: {str(e)}")
                session_results[suite_id] = {"error": str(e)}

        # 生成综合报告
        session_duration = (datetime.now() - session_start).total_seconds()
        comprehensive_report = self._generate_comprehensive_report(
            session_results, session_duration
        )

        print("\n🎉 综合测试会话完成")
        print(f"⏱️  总耗时: {session_duration:.2f}秒")
        print(f"📊 执行了 {len(session_results)} 个测试套件")

        return comprehensive_report

    def _generate_comprehensive_report(
        self, session_results: Dict, duration: float
    ) -> Dict[str, Any]:
        """生成综合报告"""
        total_suites = len(session_results)
        successful_suites = sum(1 for r in session_results.values() if "error" not in r)

        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_skipped = 0

        for suite_results in session_results.values():
            if isinstance(suite_results, list):
                total_tests += len(suite_results)
                total_passed += sum(
                    1 for r in suite_results if r.status == TestStatus.PASSED
                )
                total_failed += sum(
                    1 for r in suite_results if r.status == TestStatus.FAILED
                )
                total_skipped += sum(
                    1 for r in suite_results if r.status == TestStatus.SKIPPED
                )

        overall_success_rate = (
            (total_passed / total_tests * 100) if total_tests > 0 else 0
        )

        report = {
            "session_type": "comprehensive",
            "execution_time": datetime.now().isoformat(),
            "duration_seconds": round(duration, 2),
            "summary": {
                "total_suites": total_suites,
                "successful_suites": successful_suites,
                "failed_suites": total_suites - successful_suites,
                "total_tests": total_tests,
                "passed_tests": total_passed,
                "failed_tests": total_failed,
                "skipped_tests": total_skipped,
                "overall_success_rate": round(overall_success_rate, 1),
            },
            "suite_results": session_results,
            "statistics": self.stats,
            "recommendations": self._generate_recommendations(session_results),
        }

        # 保存综合报告
        report_path = f"/tmp/comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"📊 综合报告已保存: {report_path}")
        return report

    def _generate_recommendations(self, session_results: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []

        # 分析失败模式
        failed_suites = [s for s, r in session_results.items() if "error" in r]
        if failed_suites:
            recommendations.append(f"检查失败的测试套件: {', '.join(failed_suites)}")

        # 分析性能问题
        all_durations = []
        for suite_results in session_results.values():
            if isinstance(suite_results, list):
                all_durations.extend(
                    [r.duration for r in suite_results if r.duration is not None]
                )

        if all_durations:
            avg_duration = mean(all_durations)
            max_duration = max(all_durations)

            if avg_duration > 60:  # 超过1分钟
                recommendations.append(
                    f"考虑优化测试性能，平均执行时间 {avg_duration:.2f}秒"
                )

            if max_duration > 300:  # 超过5分钟
                recommendations.append(
                    f"有测试执行时间过长（{max_duration:.2f}秒），需要检查"
                )

        # 基于成功率提供建议
        if session_results:
            success_rate = sum(
                1 for r in session_results.values() if "error" not in r
            ) / len(session_results)
            if success_rate < 0.8:
                recommendations.append("测试成功率偏低，建议检查测试环境配置")

        if not recommendations:
            recommendations.append("测试执行正常，继续保持")

        return recommendations

    async def get_test_status_dashboard(self) -> Dict[str, Any]:
        """获取测试状态仪表盘数据"""
        # 计算各状态测试数量
        status_counts = {status.value: 0 for status in TestStatus}

        for result in self.execution_engine.test_results.values():
            status_counts[result.status.value] += 1

        # 生成仪表盘数据
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "total_test_cases": len(self.test_cases),
            "total_test_suites": len(self.test_suites),
            "execution_stats": self.stats,
            "status_counts": status_counts,
            "recent_executions": list(self.execution_engine.test_results.keys())[-10:],
            "performance_metrics": {
                "average_test_duration": mean(
                    [
                        r.duration
                        for r in self.execution_engine.test_results.values()
                        if r.duration
                    ]
                )
                or 0,
                "success_rate": (
                    self.stats["passed_tests"] / max(self.stats["total_tests"], 1)
                )
                * 100,
            },
        }

        return dashboard

    def export_test_configuration(self, output_path: str):
        """导出测试配置"""
        config = {
            "test_cases": {
                test_id: {
                    "name": case.name,
                    "type": case.test_type.value,
                    "priority": case.priority,
                    "timeout": case.timeout,
                    "tags": case.tags,
                }
                for test_id, case in self.test_cases.items()
            },
            "test_suites": {
                suite_id: {
                    "name": suite.name,
                    "test_cases": suite.test_cases,
                    "execution_order": suite.execution_order,
                }
                for suite_id, suite in self.test_suites.items()
            },
            "config": self.config,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"📁 测试配置已导出: {output_path}")


# 示例使用
async def demo_comprehensive_manager():
    """演示综合测试管理器功能"""
    print("🚀 演示综合测试管理器")

    # 创建管理器
    manager = ComprehensiveTestManager()

    # 创建一些测试用例
    ai_test = TestCase(
        id="ai_test_001",
        name="AI测试生成器验证",
        test_type=TestType.AI_ASSISTED,
        description="测试AI辅助测试生成器功能",
        execute=lambda: manager.ai_generator.generate_test_cases("sample_function()"),
        tags=["ai", "validation"],
    )

    performance_test = TestCase(
        id="perf_test_001",
        name="性能基准测试",
        test_type=TestType.PERFORMANCE,
        description="执行API性能基准测试",
        timeout=600,
        execute=lambda: manager.performance_suite.run_performance_benchmark(),
        tags=["performance", "api"],
    )

    security_test = TestCase(
        id="sec_test_001",
        name="安全漏洞扫描",
        test_type=TestType.SECURITY,
        description="运行安全漏洞扫描",
        timeout=300,
        execute=lambda: manager.security_scanner.run_comprehensive_security_scan(),
        tags=["security", "vulnerability"],
    )

    # 注册测试用例
    manager.register_test_case(ai_test)
    manager.register_test_case(performance_test)
    manager.register_test_case(security_test)

    # 创建测试套件
    comprehensive_suite = TestSuite(
        id="comprehensive_suite_001",
        name="综合测试套件",
        description="包含所有测试类型的综合套件",
        test_cases=[ai_test.id, performance_test.id, security_test.id],
        execution_order="adaptive",
        max_parallel=3,
    )

    manager.register_test_suite(comprehensive_suite)

    # 运行测试套件
    results = await manager.run_test_suite("comprehensive_suite_001", "adaptive")

    # 生成仪表盘
    dashboard = await manager.get_test_status_dashboard()
    print("\n📊 测试状态仪表盘:")
    print(f"- 总测试用例: {dashboard['total_test_cases']}")
    print(f"- 总测试套件: {dashboard['total_test_suites']}")
    print(f"- 成功率: {dashboard['performance_metrics']['success_rate']:.1f}%")

    # 导出配置
    manager.export_test_configuration("/tmp/test_config_export.json")

    print("\n✅ 综合测试管理器演示完成")


if __name__ == "__main__":
    asyncio.run(demo_comprehensive_manager())
