"""
自动化系统测试 (Automation System Tests)

测试覆盖:
- TaskScheduler: 任务调度器
- NotificationManager: 通知管理器
- JobLock: 任务锁
- PredefinedTasks: 预定义任务

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

from src.ml_strategy.automation import (
    TaskScheduler,
    TaskConfig,
    TaskStatus,
    TaskPriority,
    TaskExecution,
    JobLock,
    NotificationManager,
    NotificationConfig,
    NotificationChannel,
    NotificationLevel,
    Notification,
)

from src.ml_strategy.automation.predefined_tasks import (
    PredefinedTasks,
    create_daily_update_task,
    create_strategy_execution_task,
    create_health_check_task,
)


# =============================================================================
# JobLock Tests
# =============================================================================


class TestJobLock:
    """任务锁测试"""

    def test_acquire_lock(self):
        """测试获取锁"""
        lock = JobLock()

        # 第一次获取应该成功
        assert lock.acquire("job1") == True
        assert lock.is_locked("job1") == True

    def test_acquire_locked_job(self):
        """测试获取已锁定的任务"""
        lock = JobLock()

        # 第一次获取成功
        lock.acquire("job1")

        # 第二次获取应该失败
        assert lock.acquire("job1") == False

    def test_release_lock(self):
        """测试释放锁"""
        lock = JobLock()

        lock.acquire("job1")
        assert lock.is_locked("job1") == True

        lock.release("job1")
        assert lock.is_locked("job1") == False

    def test_lock_timeout(self):
        """测试锁超时"""
        lock = JobLock()

        # 获取锁
        lock.acquire("job1", timeout=1)
        assert lock.is_locked("job1") == True

        # 等待超时
        time.sleep(1.5)

        # 超时后应该可以重新获取
        assert lock.acquire("job1", timeout=1) == True

    def test_multiple_jobs(self):
        """测试多个任务的锁"""
        lock = JobLock()

        assert lock.acquire("job1") == True
        assert lock.acquire("job2") == True
        assert lock.acquire("job3") == True

        assert lock.is_locked("job1") == True
        assert lock.is_locked("job2") == True
        assert lock.is_locked("job3") == True


# =============================================================================
# NotificationManager Tests
# =============================================================================


class TestNotificationManager:
    """通知管理器测试"""

    def test_basic_notification(self):
        """测试基本通知发送"""
        config = NotificationConfig(channels=[NotificationChannel.LOG])
        manager = NotificationManager(config)

        result = manager.send_notification(
            title="Test", message="Test message", level=NotificationLevel.INFO
        )

        assert result == True
        assert len(manager.notifications) == 1
        assert manager.stats["total_sent"] == 1

    def test_multiple_channels(self):
        """测试多渠道通知"""
        config = NotificationConfig(
            channels=[NotificationChannel.LOG, NotificationChannel.CONSOLE]
        )
        manager = NotificationManager(config)

        result = manager.send_notification(
            title="Multi-channel", message="Test", level=NotificationLevel.INFO
        )

        assert result == True
        assert manager.stats["log_sent"] == 1
        assert manager.stats["console_sent"] == 1

    def test_rate_limiting(self):
        """测试频率限制"""
        config = NotificationConfig(
            channels=[NotificationChannel.LOG], rate_limit=5  # 5秒限制
        )
        manager = NotificationManager(config)

        # 第一次发送应该成功
        result1 = manager.send_notification(
            title="Same", message="Same", level=NotificationLevel.INFO
        )
        assert result1 == True

        # 立即再次发送应该被限制
        result2 = manager.send_notification(
            title="Same", message="Same", level=NotificationLevel.INFO
        )
        assert result2 == False
        assert manager.stats["rate_limited"] == 1

    def test_success_notification(self):
        """测试成功通知"""
        config = NotificationConfig(channels=[NotificationChannel.LOG])
        manager = NotificationManager(config)

        manager.send_success_notification(
            task_name="test_task", execution_time=12.5, result="success"
        )

        assert len(manager.notifications) == 1
        assert manager.notifications[0].level == NotificationLevel.INFO

    def test_failure_notification(self):
        """测试失败通知"""
        config = NotificationConfig(channels=[NotificationChannel.LOG])
        manager = NotificationManager(config)

        manager.send_failure_notification(
            task_name="test_task", error_message="Test error", retry_count=2
        )

        assert len(manager.notifications) == 1
        assert manager.notifications[0].level == NotificationLevel.ERROR

    def test_signal_notification(self):
        """测试交易信号通知"""
        config = NotificationConfig(channels=[NotificationChannel.LOG])
        manager = NotificationManager(config)

        manager.send_signal_notification(
            strategy_name="momentum", symbol="sh600000", signal="buy", price=10.52
        )

        assert len(manager.notifications) == 1
        assert manager.notifications[0].level == NotificationLevel.WARNING

    def test_notification_history(self):
        """测试通知历史"""
        config = NotificationConfig(channels=[NotificationChannel.LOG])
        manager = NotificationManager(config)

        # 发送多条通知
        for i in range(5):
            manager.send_notification(
                title=f"Test {i}", message="Test", level=NotificationLevel.INFO
            )

        history = manager.get_notification_history(limit=3)
        assert len(history) == 3

    def test_notification_history_filter(self):
        """测试通知历史过滤"""
        config = NotificationConfig(
            channels=[NotificationChannel.LOG],
            rate_limit=0,  # Disable rate limiting for this test
        )
        manager = NotificationManager(config)

        manager.send_notification("Test 1", "msg 1", NotificationLevel.INFO)
        manager.send_notification("Test 2", "msg 2", NotificationLevel.ERROR)
        manager.send_notification("Test 3", "msg 3", NotificationLevel.INFO)

        error_history = manager.get_notification_history(level=NotificationLevel.ERROR)
        assert len(error_history) == 1

    def test_statistics(self):
        """测试统计信息"""
        config = NotificationConfig(channels=[NotificationChannel.LOG])
        manager = NotificationManager(config)

        manager.send_notification("Test 1", "msg", NotificationLevel.INFO)
        manager.send_notification("Test 2", "msg", NotificationLevel.ERROR)

        stats = manager.get_statistics()
        assert stats["total_sent"] == 2
        assert stats["total_notifications"] == 2
        assert stats["success_rate"] == 100.0


# =============================================================================
# TaskScheduler Tests
# =============================================================================


class TestTaskScheduler:
    """任务调度器测试"""

    def test_create_scheduler(self):
        """测试创建调度器"""
        scheduler = TaskScheduler()
        assert scheduler is not None
        assert len(scheduler.tasks) == 0

    def test_add_task(self):
        """测试添加任务"""
        scheduler = TaskScheduler()

        def test_func():
            return "success"

        config = TaskConfig(
            name="test_task",
            func=test_func,
            trigger_type="interval",
            trigger_args={"seconds": 10},
        )

        task_id = scheduler.add_task(config)
        assert task_id == "test_task"
        assert "test_task" in scheduler.tasks

    def test_add_disabled_task(self):
        """测试添加禁用的任务"""
        scheduler = TaskScheduler()

        def test_func():
            return "success"

        config = TaskConfig(
            name="disabled_task",
            func=test_func,
            trigger_type="interval",
            trigger_args={"seconds": 10},
            enabled=False,
        )

        task_id = scheduler.add_task(config)
        assert task_id == ""  # 禁用的任务不会被添加

    def test_list_tasks(self):
        """测试列出任务"""
        scheduler = TaskScheduler()

        def test_func():
            pass

        for i in range(3):
            config = TaskConfig(
                name=f"task_{i}",
                func=test_func,
                trigger_type="interval",
                trigger_args={"seconds": 10},
            )
            scheduler.add_task(config)

        tasks = scheduler.list_tasks()
        assert len(tasks) == 3

    def test_get_statistics(self):
        """测试获取统计信息"""
        scheduler = TaskScheduler()

        def test_func():
            pass

        config = TaskConfig(
            name="test_task",
            func=test_func,
            trigger_type="interval",
            trigger_args={"seconds": 10},
        )
        scheduler.add_task(config)

        stats = scheduler.get_statistics()
        assert stats["total_tasks"] == 1
        assert stats["active_tasks"] == 1


# =============================================================================
# PredefinedTasks Tests
# =============================================================================


class TestPredefinedTasks:
    """预定义任务测试"""

    def test_health_check(self):
        """测试健康检查"""
        result = PredefinedTasks.health_check()

        assert result["status"] in ["healthy", "unhealthy"]
        assert "services" in result
        assert "timestamp" in result

    def test_health_check_specific_services(self):
        """测试特定服务健康检查"""
        result = PredefinedTasks.health_check(services=["database"])

        assert "database" in result["services"]
        assert result["services"]["database"] == "healthy"

    def test_generate_daily_report(self):
        """测试生成每日报告"""
        result = PredefinedTasks.generate_daily_report()

        assert result["status"] == "success"
        assert "date" in result
        assert "report" in result

    def test_create_daily_update_task(self):
        """测试创建每日更新任务配置"""
        task = create_daily_update_task(market="sh", hour=16, minute=0)

        assert task.name == "daily_data_update_sh"
        assert task.trigger_type == "cron"
        assert task.priority == TaskPriority.HIGH
        assert task.kwargs["market"] == "sh"

    def test_create_strategy_execution_task(self):
        """测试创建策略执行任务配置"""
        task = create_strategy_execution_task(
            strategy_name="momentum", hour=9, minute=30
        )

        assert task.name == "execute_momentum"
        assert task.trigger_type == "cron"
        assert task.kwargs["strategy_name"] == "momentum"
        assert "daily_data_update_sh" in task.depends_on

    def test_create_health_check_task(self):
        """测试创建健康检查任务配置"""
        task = create_health_check_task(interval_minutes=30)

        assert task.name == "system_health_check"
        assert task.trigger_type == "interval"
        assert task.trigger_args["minutes"] == 30
        assert task.priority == TaskPriority.LOW


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """集成测试"""

    def test_scheduler_with_notification(self):
        """测试调度器与通知集成"""
        notification_config = NotificationConfig(channels=[NotificationChannel.LOG])
        notification_mgr = NotificationManager(notification_config)

        scheduler = TaskScheduler(notification_manager=notification_mgr)

        def test_func():
            return "success"

        config = TaskConfig(
            name="integration_test",
            func=test_func,
            trigger_type="interval",
            trigger_args={"seconds": 10},
            notify_on_success=True,
        )

        scheduler.add_task(config)
        assert len(scheduler.tasks) == 1

    def test_task_execution_flow(self):
        """测试任务执行流程"""
        scheduler = TaskScheduler()

        execution_count = [0]

        def task_func():
            execution_count[0] += 1
            return "success"

        config = TaskConfig(
            name="flow_test",
            func=task_func,
            trigger_type="interval",
            trigger_args={"seconds": 1},
            max_retries=2,
        )

        scheduler.add_task(config)
        assert "flow_test" in scheduler.tasks

    def test_multiple_tasks_coordination(self):
        """测试多任务协调"""
        scheduler = TaskScheduler()

        def task1():
            return "task1_done"

        def task2():
            return "task2_done"

        config1 = TaskConfig(
            name="coordinated_task1",
            func=task1,
            trigger_type="interval",
            trigger_args={"seconds": 10},
            next_tasks=["coordinated_task2"],
        )

        config2 = TaskConfig(
            name="coordinated_task2",
            func=task2,
            trigger_type="interval",
            trigger_args={"seconds": 10},
            depends_on=["coordinated_task1"],
        )

        scheduler.add_task(config1)
        scheduler.add_task(config2)

        assert len(scheduler.tasks) == 2
        assert config1.next_tasks == ["coordinated_task2"]
        assert config2.depends_on == ["coordinated_task1"]


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
