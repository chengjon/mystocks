#!/usr/bin/env python3
"""Tail mixin extracted from `tests/ai/test_integration_system.py`."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class AITestIntegrationSystemTailMixin:
    """Support methods extracted from `AITestIntegrationSystem`."""

    def analyze_test_results(self, execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """分析测试结果"""
        print("🤖 AI正在分析测试结果...")

        analysis = {
            "overall_summary": {},
            "phase_analysis": {},
            "ai_insights": {},
            "trends": {},
            "recommendations": [],
        }

        total_duration = 0
        total_tests = 0
        total_passed = 0
        total_failed = 0

        for result in execution_results.values():
            total_duration += result.duration
            total_tests += result.test_cases_executed
            total_passed += result.test_cases_passed
            total_failed += result.test_cases_failed

            phase_key = result.phase.value
            analysis["phase_analysis"][phase_key] = {
                "status": result.status,
                "duration": result.duration,
                "efficiency": (
                    result.test_cases_passed / result.test_cases_executed if result.test_cases_executed > 0 else 0
                ),
            }

            if result.ai_insights:
                analysis["ai_insights"][phase_key] = result.ai_insights

        analysis["overall_summary"] = {
            "total_duration": round(total_duration, 2),
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "success_rate": round(total_passed / total_tests * 100, 2) if total_tests > 0 else 0,
        }

        analysis["trends"] = self.data_analyzer.analyze_test_trends(execution_results)

        if total_failed > 0:
            analysis["recommendations"].append(f"优先修复 {total_failed} 个失败的测试")
        if total_duration > 300:
            analysis["recommendations"].append("优化测试执行效率")

        return analysis

    def generate_final_report(self, test_plan: Any, execution_results: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
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

    def save_test_results(self, test_plan: Any, execution_results: Dict[str, Any], report: Dict[str, Any]):
        """保存测试结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{test_plan.id}_{timestamp}.json"
        filepath = Path(self.config.storage_path) / filename

        try:
            with open(filepath, "w", encoding="utf-8") as file_handle:
                json.dump(report, file_handle, ensure_ascii=False, indent=2, default=str)

            latest_link = Path(self.config.storage_path) / "latest_results.json"
            if latest_link.exists():
                latest_link.unlink()
            latest_link.symlink_to(filename)

            logger.info("测试结果已保存: %(filepath)s")

        except Exception as error:
            logger.error("保存测试结果失败: %(e)s")

    async def auto_optimize_testing(self, execution_results: Dict[str, Any]):
        """自动优化测试"""
        print("🤖 AI正在自动优化测试...")

        try:
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

        except Exception as error:
            logger.error("自动优化失败: %(e)s")

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
