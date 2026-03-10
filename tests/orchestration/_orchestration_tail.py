from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tests.orchestration.test_orchestration import (
        CheckpointManager,
        OrchestrationConfig,
        TaskPriority,
        TestOrchestrator,
        TestTask,
    )


class OrchestrationManager:
    """编排管理器工厂"""

    @staticmethod
    def create_default_orchestrator(
        orchestrator_cls: type["TestOrchestrator"],
        config_cls: type["OrchestrationConfig"],
    ) -> "TestOrchestrator":
        config = config_cls(
            max_concurrent_tasks=5,
            enable_parallel=True,
            enable_monitoring=True,
            checkpoint_enabled=True,
        )
        return orchestrator_cls(config)

    @staticmethod
    def create_performance_orchestrator(
        orchestrator_cls: type["TestOrchestrator"],
        config_cls: type["OrchestrationConfig"],
    ) -> "TestOrchestrator":
        config = config_cls(
            max_concurrent_tasks=3,
            enable_parallel=False,
            task_timeout=1800,
            enable_retry=True,
        )
        return orchestrator_cls(config)

    @staticmethod
    def create_chaos_orchestrator(
        orchestrator_cls: type["TestOrchestrator"],
        config_cls: type["OrchestrationConfig"],
    ) -> "TestOrchestrator":
        config = config_cls(
            max_concurrent_tasks=2,
            enable_parallel=False,
            task_timeout=600,
            fail_fast=False,
            log_level="WARNING",
        )
        return orchestrator_cls(config)


async def demo_orchestration(
    manager_cls: type[OrchestrationManager],
    orchestrator_cls: type["TestOrchestrator"],
    config_cls: type["OrchestrationConfig"],
    task_cls: type["TestTask"],
    priority_cls: type["TaskPriority"],
    checkpoint_manager_cls: type["CheckpointManager"],
):
    """演示编排功能"""
    print("🚀 演示测试编排功能")

    orchestrator = manager_cls.create_default_orchestrator(orchestrator_cls, config_cls)

    tasks = [
        task_cls(
            id="task_001",
            name="数据库连接测试",
            description="测试数据库连接",
            test_type="unit",
            priority=priority_cls.HIGH,
            timeout=30,
        ),
        task_cls(
            id="task_002",
            name="API集成测试",
            description="测试API集成",
            test_type="integration",
            priority=priority_cls.HIGH,
            dependencies=["task_001"],
            timeout=60,
        ),
        task_cls(
            id="task_003",
            name="端到端测试",
            description="执行端到端测试",
            test_type="e2e",
            priority=priority_cls.NORMAL,
            dependencies=["task_002"],
            timeout=120,
        ),
        task_cls(
            id="task_004",
            name="性能测试",
            description="执行性能测试",
            test_type="performance",
            priority=priority_cls.NORMAL,
            timeout=300,
        ),
        task_cls(
            id="task_005",
            name="安全扫描",
            description="执行安全扫描",
            test_type="security",
            priority=priority_cls.LOW,
            timeout=180,
        ),
    ]

    for task in tasks:
        orchestrator.add_task(task)

    report = await orchestrator.execute_all_tasks()

    print("\n📊 执行报告:")
    print(f"总任务数: {report['execution_summary']['total_tasks']}")
    print(f"成功任务: {report['execution_summary']['completed_tasks']}")
    print(f"失败任务: {report['execution_summary']['failed_tasks']}")
    print(f"成功率: {report['execution_summary']['success_rate']:.2%}")
    print(f"平均执行时间: {report['execution_summary']['average_duration']:.2f}秒")

    print("\n📈 任务类型统计:")
    for test_type, stats in report["task_type_statistics"].items():
        print(f"  {test_type}: {stats['completed']}/{stats['total']} 成功")

    checkpoint_manager = checkpoint_manager_cls()
    checkpoints = checkpoint_manager.list_checkpoints()
    print(f"\n📍 检查点数量: {len(checkpoints)}")
