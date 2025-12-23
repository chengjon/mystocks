#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI测试集成系统
提供智能的测试编排、执行和协调功能
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

from .test_ai_assisted_testing import AITestGenerator
from .test_data_analyzer import AITestDataAnalyzer
from .test_data_manager import AITestDataManager
from ..contract.contract_engine import ContractTestEngine

logger = logging.getLogger(__name__)


class TestPhase(Enum):
    """测试阶段枚举"""

    PLANNING = "planning"
    GENERATION = "generation"
    EXECUTION = "execution"
    ANALYSIS = "analysis"
    OPTIMIZATION = "optimization"
    REPORTING = "reporting"


@dataclass
class TestOrchestrationConfig:
    """测试编排配置"""

    max_concurrent_tests: int = 10
    enable_ai_enhancement: bool = True
    auto_optimize: bool = True
    enable_smart_retry: bool = True
    enable_performance_monitoring: bool = True
    report_format: str = "comprehensive"  # basic, detailed, comprehensive
    storage_path: str = "test_results/ai_integrated"
    data_retention_days: int = 30


@dataclass
class TestExecutionPlan:
    """测试执行计划"""

    id: str
    name: str
    description: str
    phases: List[TestPhase]
    test_suites: List[str]
    data_profiles: List[str]
    execution_order: List[str]
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    estimated_duration: float = 0.0
    priority: int = 1
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestExecutionResult:
    """测试执行结果"""

    plan_id: str
    phase: TestPhase
    status: str  # pending, running, completed, failed, cancelled
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: float = 0.0
    test_cases_executed: int = 0
    test_cases_passed: int = 0
    test_cases_failed: int = 0
    test_cases_skipped: int = 0
    error_message: Optional[str] = None
    ai_insights: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    data_analysis: Dict[str, Any] = field(default_factory=dict)


class IntelligentTestPlanner:
    """智能测试规划器"""

    def __init__(self, ai_generator: AITestGenerator, data_manager: AITestDataManager):
        self.ai_generator = ai_generator
        self.data_manager = data_manager

    def create_test_plan(self, project_context: Dict[str, Any]) -> TestExecutionPlan:
        """创建智能测试计划"""
        print("🤖 AI正在创建测试计划...")

        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        plan_name = (
            f"AI优化测试计划 - {project_context.get('project_name', 'MyStocks')}"
        )

        # 分析项目上下文
        analysis = self._analyze_project_context(project_context)

        # 确定测试阶段
        phases = self._determine_test_phases(analysis)

        # 选择测试套件
        test_suites = self._select_test_suites(analysis)

        # 选择数据档案
        data_profiles = self._select_data_profiles(analysis)

        # 确定执行顺序
        execution_order = self._determine_execution_order(test_suites, data_profiles)

        # 计算预估时间
        estimated_duration = self._estimate_duration(test_suites, data_profiles)

        # 创建执行计划
        plan = TestExecutionPlan(
            id=plan_id,
            name=plan_name,
            description=f"基于AI分析的全面测试计划，覆盖 {len(test_suites)} 个测试套件",
            phases=phases,
            test_suites=test_suites,
            data_profiles=data_profiles,
            execution_order=execution_order,
            estimated_duration=estimated_duration,
            priority=analysis.get("priority", 1),
            tags=analysis.get("tags", []),
            metadata={
                "project_context": project_context,
                "ai_analysis": analysis,
                "created_at": datetime.now().isoformat(),
            },
        )

        logger.info(f"创建测试计划: {plan_name} (预估时间: {estimated_duration:.2f}s)")
        return plan

    def _analyze_project_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析项目上下文"""
        analysis = {
            "project_type": context.get("project_type", "web_application"),
            "complexity": "medium",
            "critical_components": [],
            "test_coverage_areas": [],
            "risk_factors": [],
            "priority": 1,
            "tags": [],
        }

        # 分析复杂度
        if context.get("modules_count", 0) > 20:
            analysis["complexity"] = "high"
        elif context.get("modules_count", 0) < 10:
            analysis["complexity"] = "low"

        # 识别关键组件
        critical_modules = ["authentication", "database", "api", "payment", "security"]
        for module in context.get("modules", []):
            if any(crit in module.lower() for crit in critical_modules):
                analysis["critical_components"].append(module)

        # 确定测试覆盖领域
        if "api" in context.get("features", []):
            analysis["test_coverage_areas"].append("api_contract")
        if "database" in context.get("features", []):
            analysis["test_coverage_areas"].append("database")
        if "ui" in context.get("features", []):
            analysis["test_coverage_areas"].append("ui_e2e")

        # 评估风险因素
        if analysis["complexity"] == "high":
            analysis["risk_factors"].append("high_complexity")
        if len(analysis["critical_components"]) > 3:
            analysis["risk_factors"].append("many_critical_components")

        return analysis

    def _determine_test_phases(self, analysis: Dict[str, Any]) -> List[TestPhase]:
        """确定测试阶段"""
        phases = [TestPhase.PLANNING]

        # 基于复杂度决定是否需要数据生成阶段
        if analysis["complexity"] in ["high", "medium"]:
            phases.append(TestPhase.GENERATION)

        phases.extend([TestPhase.EXECUTION, TestPhase.ANALYSIS])

        # 如果有优化需求，添加优化阶段
        if analysis.get("risk_factors"):
            phases.append(TestPhase.OPTIMIZATION)

        phases.append(TestPhase.REPORTING)
        return phases

    def _select_test_suites(self, analysis: Dict[str, Any]) -> List[str]:
        """选择测试套件"""
        suites = ["unit_tests", "integration_tests"]

        # 基于测试覆盖领域选择
        if "api_contract" in analysis["test_coverage_areas"]:
            suites.append("api_contract_tests")
        if "database" in analysis["test_coverage_areas"]:
            suites.append("database_tests")
        if "ui_e2e" in analysis["test_coverage_areas"]:
            suites.append("e2e_tests")

        # 如果复杂度高，添加性能测试
        if analysis["complexity"] == "high":
            suites.append("performance_tests")

        return suites

    def _select_data_profiles(self, analysis: Dict[str, Any]) -> List[str]:
        """选择数据档案"""
        profiles = ["unit_test_data", "integration_test_data"]

        # 基于测试覆盖领域选择
        if "api_contract" in analysis["test_coverage_areas"]:
            profiles.append("integration_test_data")
        if "database" in analysis["test_coverage_areas"]:
            profiles.append("integration_test_data")
        if "e2e_tests" in analysis.get("test_suites", []):
            profiles.append("e2e_test_data")

        return list(set(profiles))  # 去重

    def _determine_execution_order(
        self, test_suites: List[str], data_profiles: List[str]
    ) -> List[str]:
        """确定执行顺序"""
        order = []

        # 优先执行单元测试
        if "unit_tests" in test_suites:
            order.append("unit_tests")

        # 然后是数据准备
        for profile in data_profiles:
            order.append(f"prepare_{profile}")

        # 接着是其他测试
        for suite in test_suites:
            if suite not in order:
                order.append(suite)

        # 最后是清理
        order.append("cleanup")

        return order

    def _estimate_duration(
        self, test_suites: List[str], data_profiles: List[str]
    ) -> float:
        """预估执行时间"""
        base_times = {
            "unit_tests": 30,
            "integration_tests": 60,
            "api_contract_tests": 45,
            "database_tests": 40,
            "e2e_tests": 120,
            "performance_tests": 180,
            "prepare_unit_test_data": 5,
            "prepare_integration_test_data": 10,
            "prepare_e2e_test_data": 15,
            "cleanup": 10,
        }

        total_time = 0
        for item in self._determine_execution_order(test_suites, data_profiles):
            total_time += base_times.get(item, 30)

        # 添加缓冲时间
        total_time *= 1.2

        return total_time


class SmartTestExecutor:
    """智能测试执行器"""

    def __init__(self, config: TestOrchestrationConfig):
        self.config = config
        self.max_workers = config.max_concurrent_tests
        self.semaphore = asyncio.Semaphore(self.max_workers)
        self.execution_results: Dict[str, TestExecutionResult] = {}

    async def execute_test_plan(
        self, plan: TestExecutionPlan, test_executors: Dict[str, Callable]
    ) -> Dict[str, TestExecutionResult]:
        """执行测试计划"""
        print(f"🤖 AI正在执行测试计划: {plan.name}")

        self.execution_results = {}
        start_time = datetime.now()

        # 按阶段执行
        for phase in plan.phases:
            if phase == TestPhase.PLANNING:
                await self._execute_planning_phase(plan)
            elif phase == TestPhase.GENERATION:
                await self._execute_generation_phase(plan)
            elif phase == TestPhase.EXECUTION:
                await self._execute_execution_phase(plan, test_executors)
            elif phase == TestPhase.ANALYSIS:
                await self._execute_analysis_phase(plan)
            elif phase == TestPhase.OPTIMIZATION:
                await self._execute_optimization_phase(plan)
            elif phase == TestPhase.REPORTING:
                await self._execute_reporting_phase(plan)

        # 计算总执行时间
        total_duration = (datetime.now() - start_time).total_seconds()

        logger.info(f"测试计划执行完成: {plan.name} (耗时: {total_duration:.2f}s)")
        return self.execution_results

    async def _execute_planning_phase(self, plan: TestExecutionPlan):
        """执行规划阶段"""
        result = TestExecutionResult(
            plan_id=plan.id, phase=TestPhase.PLANNING, status="completed"
        )
        result.start_time = datetime.now()
        result.end_time = datetime.now()
        result.duration = 0.0
        result.ai_insights = {
            "plan_created": True,
            "phases_count": len(plan.phases),
            "test_suites_count": len(plan.test_suites),
            "estimated_duration": plan.estimated_duration,
        }

        self.execution_results[TestPhase.PLANNING.value] = result

    async def _execute_generation_phase(self, plan: TestExecutionPlan):
        """执行数据生成阶段"""
        print("🤖 AI正在生成测试数据...")

        result = TestExecutionResult(
            plan_id=plan.id, phase=TestPhase.GENERATION, status="running"
        )
        result.start_time = datetime.now()

        try:
            # 并行生成数据
            generation_tasks = []
            for profile_name in plan.data_profiles:
                task = asyncio.create_task(
                    self._generate_data_for_profile(profile_name),
                    name=f"generate_{profile_name}",
                )
                generation_tasks.append(task)

            # 等待所有数据生成完成
            await asyncio.gather(*generation_tasks)

            result.status = "completed"
            result.test_cases_executed = len(plan.data_profiles)
            result.test_cases_passed = len(plan.data_profiles)  # 假设都成功

        except Exception as e:
            result.status = "failed"
            result.error_message = str(e)

        finally:
            result.end_time = datetime.now()
            result.duration = (result.end_time - result.start_time).total_seconds()

        self.execution_results[TestPhase.GENERATION.value] = result

    async def _generate_data_for_profile(self, profile_name: str):
        """为指定档案生成数据"""
        try:
            # 这里应该调用实际的AI数据生成器
            await asyncio.sleep(1)  # 模拟生成过程
            print(f"✓ 数据档案生成完成: {profile_name}")
        except Exception as e:
            logger.error(f"数据档案 {profile_name} 生成失败: {e}")

    async def _execute_execution_phase(
        self, plan: TestExecutionPlan, test_executors: Dict[str, Callable]
    ):
        """执行测试阶段"""
        print("🤖 AI正在执行测试用例...")

        result = TestExecutionResult(
            plan_id=plan.id, phase=TestPhase.EXECUTION, status="running"
        )
        result.start_time = datetime.now()

        try:
            # 使用信号量限制并发数
            execution_tasks = []
            for test_suite in plan.test_suites:
                if test_suite in test_executors:
                    task = asyncio.create_task(
                        self._execute_test_suite_with_semaphore(
                            test_suite, test_executors[test_suite]
                        ),
                        name=f"execute_{test_suite}",
                    )
                    execution_tasks.append(task)

            # 等待所有测试执行完成
            suite_results = await asyncio.gather(
                *execution_tasks, return_exceptions=True
            )

            # 汇总结果
            total_passed = 0
            total_failed = 0
            total_skipped = 0

            for i, suite_result in enumerate(suite_results):
                if isinstance(suite_result, Exception):
                    total_failed += 1
                elif isinstance(suite_result, dict):
                    total_passed += suite_result.get("passed", 0)
                    total_failed += suite_result.get("failed", 0)
                    total_skipped += suite_result.get("skipped", 0)
                else:
                    total_passed += 1

            result.test_cases_executed = len(plan.test_suites)
            result.test_cases_passed = total_passed
            result.test_cases_failed = total_failed
            result.test_cases_skipped = total_skipped

            result.status = (
                "completed" if total_failed == 0 else "completed_with_failures"
            )

        except Exception as e:
            result.status = "failed"
            result.error_message = str(e)

        finally:
            result.end_time = datetime.now()
            result.duration = (result.end_time - result.start_time).total_seconds()

        self.execution_results[TestPhase.EXECUTION.value] = result

    async def _execute_test_suite_with_semaphore(
        self, test_suite: str, executor: Callable
    ):
        """使用信号量执行测试套件"""
        async with self.semaphore:
            return await executor()

    async def _execute_analysis_phase(self, plan: TestExecutionPlan):
        """执行分析阶段"""
        print("🤖 AI正在分析测试结果...")

        result = TestExecutionResult(
            plan_id=plan.id, phase=TestPhase.ANALYSIS, status="running"
        )
        result.start_time = datetime.now()

        try:
            # 收集执行结果
            execution_result = self.execution_results.get(TestPhase.EXECUTION.value)
            if not execution_result:
                raise ValueError("执行阶段结果不存在")

            # 执行AI分析
            analysis = self._perform_ai_analysis(execution_result)

            result.status = "completed"
            result.test_cases_executed = 1  # 分析作为一个整体任务
            result.test_cases_passed = 1
            result.data_analysis = analysis

        except Exception as e:
            result.status = "failed"
            result.error_message = str(e)

        finally:
            result.end_time = datetime.now()
            result.duration = (result.end_time - result.start_time).total_seconds()

        self.execution_results[TestPhase.ANALYSIS.value] = result

    def _perform_ai_analysis(
        self, execution_result: TestExecutionResult
    ) -> Dict[str, Any]:
        """执行AI分析"""
        analysis = {
            "test_quality_score": 0.0,
            "performance_insights": [],
            "optimization_suggestions": [],
            "risk_assessment": "low",
        }

        # 计算测试质量分数
        if execution_result.test_cases_executed > 0:
            pass_rate = (
                execution_result.test_cases_passed
                / execution_result.test_cases_executed
            )
            analysis["test_quality_score"] = round(pass_rate * 100, 2)

        # 性能洞察
        if execution_result.duration > 60:  # 超过1分钟
            analysis["performance_insights"].append(
                "测试执行时间较长，建议优化测试用例"
            )

        # 优化建议
        if execution_result.test_cases_failed > 0:
            analysis["optimization_suggestions"].append(
                f"修复 {execution_result.test_cases_failed} 个失败的测试用例"
            )

        # 风险评估
        if analysis["test_quality_score"] < 80:
            analysis["risk_assessment"] = "high"
        elif analysis["test_quality_score"] < 90:
            analysis["risk_assessment"] = "medium"

        return analysis

    async def _execute_optimization_phase(self, plan: TestExecutionPlan):
        """执行优化阶段"""
        print("🤖 AI正在优化测试配置...")

        result = TestExecutionResult(
            plan_id=plan.id, phase=TestPhase.OPTIMIZATION, status="running"
        )
        result.start_time = datetime.now()

        try:
            # 执行AI优化
            optimization_result = self._perform_ai_optimization(plan)

            result.status = "completed"
            result.test_cases_executed = 1
            result.test_cases_passed = 1
            result.ai_insights = optimization_result

        except Exception as e:
            result.status = "failed"
            result.error_message = str(e)

        finally:
            result.end_time = datetime.now()
            result.duration = (result.end_time - result.start_time).total_seconds()

        self.execution_results[TestPhase.OPTIMIZATION.value] = result

    def _perform_ai_optimization(self, plan: TestExecutionPlan) -> Dict[str, Any]:
        """执行AI优化"""
        optimizations = {
            "suggested_changes": [],
            "performance_improvements": [],
            "quality_enhancements": [],
        }

        # 基于执行结果生成优化建议
        execution_result = self.execution_results.get(TestPhase.EXECUTION.value)
        if execution_result and execution_result.test_cases_failed > 0:
            optimizations["suggested_changes"].append(
                {
                    "type": "test_fix",
                    "description": f"修复 {execution_result.test_cases_failed} 个失败的测试用例",
                    "priority": "high",
                }
            )

        analysis_result = self.execution_results.get(TestPhase.ANALYSIS.value)
        if analysis_result and analysis_result.data_analysis:
            quality_score = analysis_result.data_analysis.get("test_quality_score", 0)
            if quality_score < 90:
                optimizations["quality_enhancements"].append(
                    {
                        "type": "test_coverage",
                        "description": f"提升测试覆盖率至 90% (当前: {quality_score}%)",
                        "priority": "medium",
                    }
                )

        return optimizations

    async def _execute_reporting_phase(self, plan: TestExecutionPlan):
        """执行报告阶段"""
        print("🤖 AI正在生成测试报告...")

        result = TestExecutionResult(
            plan_id=plan.id, phase=TestPhase.REPORTING, status="running"
        )
        result.start_time = datetime.now()

        try:
            # 生成综合报告
            report = self._generate_comprehensive_report(plan)

            result.status = "completed"
            result.test_cases_executed = 1
            result.test_cases_passed = 1
            result.ai_insights = {
                "report_generated": True,
                "report_summary": report["summary"],
            }

        except Exception as e:
            result.status = "failed"
            result.error_message = str(e)

        finally:
            result.end_time = datetime.now()
            result.duration = (result.end_time - result.start_time).total_seconds()

        self.execution_results[TestPhase.REPORTING.value] = result

    def _generate_comprehensive_report(self, plan: TestExecutionPlan) -> Dict[str, Any]:
        """生成综合报告"""
        report = {
            "summary": {
                "plan_name": plan.name,
                "total_duration": 0,
                "total_test_cases": 0,
                "total_passed": 0,
                "total_failed": 0,
                "overall_success_rate": 0,
            },
            "phase_results": {},
            "ai_insights": {},
            "recommendations": [],
        }

        # 汇总各阶段结果
        total_duration = 0
        total_test_cases = 0
        total_passed = 0
        total_failed = 0

        for phase_result in self.execution_results.values():
            total_duration += phase_result.duration
            total_test_cases += phase_result.test_cases_executed
            total_passed += phase_result.test_cases_passed
            total_failed += phase_result.test_cases_failed

            report["phase_results"][phase_result.phase.value] = {
                "status": phase_result.status,
                "duration": phase_result.duration,
                "test_cases": {
                    "executed": phase_result.test_cases_executed,
                    "passed": phase_result.test_cases_passed,
                    "failed": phase_result.test_cases_failed,
                    "skipped": phase_result.test_cases_skipped,
                },
            }

            # 收集AI洞察
            if phase_result.ai_insights:
                report["ai_insights"][phase_result.phase.value] = (
                    phase_result.ai_insights
                )

        # 计算总体统计
        report["summary"]["total_duration"] = round(total_duration, 2)
        report["summary"]["total_test_cases"] = total_test_cases
        report["summary"]["total_passed"] = total_passed
        report["summary"]["total_failed"] = total_failed
        report["summary"]["overall_success_rate"] = round(
            (total_passed / total_test_cases * 100) if total_test_cases > 0 else 0, 2
        )

        # 生成建议
        if total_failed > 0:
            report["recommendations"].append(f"修复 {total_failed} 个失败的测试用例")
        if total_duration > 300:  # 超过5分钟
            report["recommendations"].append("优化测试执行速度")

        return report


class AITestIntegrationSystem:
    """AI测试集成系统 - 主控制器"""

    def __init__(self, config: TestOrchestrationConfig):
        self.config = config
        self.ai_generator = AITestGenerator()
        self.data_analyzer = AITestDataAnalyzer()
        self.data_manager = AITestDataManager()
        self.test_planner = IntelligentTestPlanner(self.ai_generator, self.data_manager)
        self.test_executor = SmartTestExecutor(config)
        self.test_engine = ContractTestEngine()

        # 创建存储目录
        Path(config.storage_path).mkdir(parents=True, exist_ok=True)

    async def run_intelligent_testing(
        self, project_context: Dict[str, Any], test_executors: Dict[str, Callable]
    ) -> Dict[str, Any]:
        """运行智能测试"""
        print("🚀 启动AI智能测试系统...")

        try:
            # 1. 创建测试计划
            test_plan = self.test_planner.create_test_plan(project_context)

            # 2. 执行测试计划
            execution_results = await self.test_executor.execute_test_plan(
                test_plan, test_executors
            )

            # 3. 分析测试结果
            analysis_result = self.analyze_test_results(execution_results)

            # 4. 生成最终报告
            final_report = self.generate_final_report(
                test_plan, execution_results, analysis_result
            )

            # 5. 保存结果
            self.save_test_results(test_plan, execution_results, final_report)

            # 6. 自动优化（如果启用）
            if self.config.auto_optimize:
                await self.auto_optimize_testing(execution_results)

            print("✅ AI智能测试完成!")
            return final_report

        except Exception as e:
            logger.error(f"智能测试执行失败: {e}")
            return {"error": str(e), "status": "failed"}

    def analyze_test_results(
        self, execution_results: Dict[str, TestExecutionResult]
    ) -> Dict[str, Any]:
        """分析测试结果"""
        print("🤖 AI正在分析测试结果...")

        analysis = {
            "overall_summary": {},
            "phase_analysis": {},
            "ai_insights": {},
            "trends": {},
            "recommendations": [],
        }

        # 总体分析
        total_duration = 0
        total_tests = 0
        total_passed = 0
        total_failed = 0

        for result in execution_results.values():
            total_duration += result.duration
            total_tests += result.test_cases_executed
            total_passed += result.test_cases_passed
            total_failed += result.test_cases_failed

            # 阶段分析
            phase_key = result.phase.value
            analysis["phase_analysis"][phase_key] = {
                "status": result.status,
                "duration": result.duration,
                "efficiency": result.test_cases_passed / result.test_cases_executed
                if result.test_cases_executed > 0
                else 0,
            }

            # AI洞察
            if result.ai_insights:
                analysis["ai_insights"][phase_key] = result.ai_insights

        # 总体统计
        analysis["overall_summary"] = {
            "total_duration": round(total_duration, 2),
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "success_rate": round(total_passed / total_tests * 100, 2)
            if total_tests > 0
            else 0,
        }

        # 趋势分析
        analysis["trends"] = self.data_analyzer.analyze_test_trends(execution_results)

        # 生成建议
        if total_failed > 0:
            analysis["recommendations"].append(f"优先修复 {total_failed} 个失败的测试")
        if total_duration > 300:
            analysis["recommendations"].append("优化测试执行效率")

        return analysis

    def generate_final_report(
        self,
        test_plan: TestExecutionPlan,
        execution_results: Dict[str, TestExecutionResult],
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """生成最终报告"""
        print("🤖 AI正在生成最终报告...")

        report = {
            "metadata": {
                "plan_id": test_plan.id,
                "plan_name": test_plan.name,
                "generated_at": datetime.now().isoformat(),
                "system_version": "1.0.0",
            },
            "execution_summary": analysis["overall_summary"],
            "plan_details": {
                "phases": [phase.value for phase in test_plan.phases],
                "test_suites": test_plan.test_suites,
                "data_profiles": test_plan.data_profiles,
                "estimated_duration": test_plan.estimated_duration,
                "actual_duration": analysis["overall_summary"]["total_duration"],
            },
            "execution_results": {},
            "ai_analysis": analysis["ai_insights"],
            "trends_analysis": analysis["trends"],
            "recommendations": analysis["recommendations"],
            "data_management_insights": self.data_manager.get_data_insights(),
        }

        # 添加各阶段详细结果
        for phase, result in execution_results.items():
            report["execution_results"][phase] = {
                "status": result.status,
                "duration": result.duration,
                "test_cases": {
                    "executed": result.test_cases_executed,
                    "passed": result.test_cases_passed,
                    "failed": result.test_cases_failed,
                    "skipped": result.test_cases_skipped,
                },
                "performance_metrics": result.performance_metrics,
                "data_analysis": result.data_analysis,
            }

        return report

    def save_test_results(
        self,
        test_plan: TestExecutionPlan,
        execution_results: Dict[str, TestExecutionResult],
        report: Dict[str, Any],
    ):
        """保存测试结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{test_plan.id}_{timestamp}.json"
        filepath = Path(self.config.storage_path) / filename

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)

            # 创建符号链接
            latest_link = Path(self.config.storage_path) / "latest_results.json"
            if latest_link.exists():
                latest_link.unlink()
            latest_link.symlink_to(filename)

            logger.info(f"测试结果已保存: {filepath}")

        except Exception as e:
            logger.error(f"保存测试结果失败: {e}")

    async def auto_optimize_testing(
        self, execution_results: Dict[str, TestExecutionResult]
    ):
        """自动优化测试"""
        print("🤖 AI正在自动优化测试...")

        try:
            # 优化数据管理
            test_data_for_optimization = [
                {
                    "profile_name": "unit_test_data",
                    "status": "success" if result.status == "completed" else "failed",
                    "execution_time": result.duration,
                    "timestamp": datetime.now().isoformat(),
                }
                for result in execution_results.values()
                if result.test_cases_executed > 0
            ]

            self.data_manager.optimize_data_management(test_data_for_optimization)

            logger.info("测试自动优化完成")

        except Exception as e:
            logger.error(f"自动优化失败: {e}")

    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "config": {
                "max_concurrent_tests": self.config.max_concurrent_tests,
                "enable_ai_enhancement": self.config.enable_ai_enhancement,
                "auto_optimize": self.config.auto_optimize,
                "storage_path": self.config.storage_path,
            },
            "system_components": {
                "ai_generator": "active",
                "data_analyzer": "active",
                "data_manager": "active",
                "test_planner": "active",
                "test_executor": "active",
                "test_engine": "active",
            },
            "data_storage": self.data_manager.get_data_insights(),
            "recent_executions": len(self.test_executor.execution_results),
        }
