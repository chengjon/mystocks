"""Tail helpers extracted from `tests/ci/test_continuous_integration.py`."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional


class ContinuousIntegrationManagerTailMixin:
    """Support methods extracted from `ContinuousIntegrationManager`."""

    async def get_pipeline_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取流水线历史"""
        sorted_pipelines = sorted(self.pipelines.values(), key=lambda item: item.get("start_time", ""), reverse=True)
        return sorted_pipelines[:limit]

    async def generate_report(self, pipeline_id: str) -> Dict[str, Any]:
        """生成流水线报告"""
        pipeline = self.pipelines.get(pipeline_id, {})
        if not pipeline:
            return {"error": "Pipeline not found"}

        reports = self.reports.get(pipeline_id, [])
        report = {
            "pipeline_id": pipeline_id,
            "pipeline_name": pipeline.get("name"),
            "status": pipeline.get("status"),
            "start_time": pipeline.get("start_time"),
            "end_time": pipeline.get("end_time"),
            "duration": self._calculate_duration(pipeline.get("start_time"), pipeline.get("end_time")),
            "total_steps": len(pipeline.get("steps", [])),
            "successful_steps": len(
                [step for step in pipeline.get("steps", []) if step.get("status") == self._status_success_value()]
            ),
            "failed_steps": len(
                [step for step in pipeline.get("steps", []) if step.get("status") == self._status_failed_value()]
            ),
            "test_reports": [],
            "artifacts": pipeline.get("artifacts", []),
            "quality_checks": {},
            "recommendations": self._generate_recommendations(pipeline, reports),
        }

        for test_report in reports:
            report["test_reports"].append(
                {
                    "test_suite_id": test_report.test_suite_id,
                    "test_type": test_report.test_type.value,
                    "summary": test_report.summary,
                    "coverage": test_report.coverage,
                    "duration": test_report.duration,
                    "artifacts": test_report.artifacts,
                }
            )

        return report

    def _calculate_duration(self, start_time: Optional[str], end_time: Optional[str]) -> str:
        """计算持续时间"""
        if not start_time:
            return "0s"

        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time) if end_time else datetime.now()
        duration = end - start
        minutes = int(duration.total_seconds() // 60)
        seconds = int(duration.total_seconds() % 60)
        return f"{minutes}m {seconds}s"

    def _generate_recommendations(self, pipeline: Dict[str, Any], reports: List[Any]) -> List[str]:
        """生成改进建议"""
        recommendations = []

        failed_steps = [step for step in pipeline.get("steps", []) if step.get("status") == self._status_failed_value()]
        if failed_steps:
            recommendations.append(f"有 {len(failed_steps)} 个步骤失败，请检查错误详情")

        for report in reports:
            if report.coverage < 80:
                recommendations.append(f"测试覆盖率较低 ({report.coverage:.1f}%)，建议增加测试用例")

        total_duration = sum(report.duration for report in reports)
        if total_duration > 300:
            recommendations.append("测试执行时间较长，可以考虑并行执行优化")

        return recommendations

    async def close(self):
        """关闭资源"""
        if self.session:
            await self.session.close()
        if self.docker_client:
            self.docker_client.close()

    @staticmethod
    def _status_success_value() -> str:
        return "success"

    @staticmethod
    def _status_failed_value() -> str:
        return "failed"


async def demo_ci_system(manager_cls: Any, pipeline_step_cls: Any, test_type_enum: Any, test_suite_cls: Any):
    """演示CI系统功能"""
    async with manager_cls() as ci:
        config = ci.load_config()

        if not config.steps:
            config.steps = [
                pipeline_step_cls(id="1", name="依赖检查", type=test_type_enum.UNIT, command="pip list"),
                pipeline_step_cls(
                    id="2",
                    name="代码检查",
                    type=test_type_enum.UNIT,
                    command="python -m pylint src/ -E",
                ),
                pipeline_step_cls(
                    id="3",
                    name="单元测试",
                    type=test_type_enum.UNIT,
                    command="python -m pytest tests/unit tests/test_data_format.py --tb=short",
                ),
                pipeline_step_cls(
                    id="4",
                    name="集成测试",
                    type=test_type_enum.INTEGRATION,
                    command="python -m pytest tests/integration --tb=short",
                ),
                pipeline_step_cls(
                    id="5",
                    name="E2E测试",
                    type=test_type_enum.E2E,
                    command="python -m pytest tests/e2e --tb=short",
                ),
            ]

        for step in config.steps:
            if not step.environment:
                step.environment = {}
            step.environment.update(config.variables)

        if not config.test_suites:
            config.test_suites = [
                test_suite_cls(
                    id="unit_tests",
                    name="单元测试套件",
                    description="运行所有单元测试",
                    test_type=test_type_enum.UNIT,
                    tests=[
                        "tests/test_data_format.py",
                        "tests/unit/test_config_driven_table_manager.py",
                        "tests/unit/test_config_validation.py",
                    ],
                    parallel=True,
                ),
                test_suite_cls(
                    id="integration_tests",
                    name="集成测试套件",
                    description="运行所有集成测试",
                    test_type=test_type_enum.INTEGRATION,
                    tests=[
                        "tests/integration/test_api_integration.py",
                        "tests/integration/test_datasource_switching.py",
                    ],
                    parallel=True,
                ),
                test_suite_cls(
                    id="e2e_tests",
                    name="端到端测试套件",
                    description="运行E2E测试",
                    test_type=test_type_enum.E2E,
                    tests=[
                        "tests/e2e/test_web_e2e.py",
                        "tests/e2e/test_dashboard_page.py",
                    ],
                    parallel=True,
                ),
            ]

        pipeline_result = await ci.run_pipeline("demo_pipeline", config)
        monitor_info = await ci.monitor_pipeline("demo_pipeline")
        report = await ci.generate_report("demo_pipeline")

        print("=== CI系统演示完成 ===")
        print(f"流水线状态: {pipeline_result['status']}")
        print(f"监控信息: {monitor_info}")
        print(f"报告摘要: {report}")

        failed_steps = [step for step in pipeline_result.get("steps", []) if step.get("status") == "failed"]
        if failed_steps:
            print("\n=== 失败步骤详情 ===")
            for step in failed_steps:
                print(f"\n[{step['name']}] Output:")
                print(step.get("output", "No output"))
                if step.get("error"):
                    print(f"[{step['name']}] Error:")
                    print(step.get("error"))

        return pipeline_result
