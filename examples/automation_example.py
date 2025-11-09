"""
自动化调度系统完整示例 (Automation System Complete Example)

功能说明:
- 演示如何使用TaskScheduler进行任务调度
- 展示NotificationManager的多渠道通知
- 使用预定义任务进行常见操作
- 监控任务执行和性能

使用场景:
1. 每日自动数据更新
2. 定时策略执行和信号生成
3. 系统健康检查和维护
4. 任务失败通知和重试

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import time
from datetime import datetime, timedelta

from automation import (
    TaskScheduler,
    TaskConfig,
    TaskPriority,
    NotificationManager,
    NotificationConfig,
    NotificationChannel,
    NotificationLevel,
)

from automation.predefined_tasks import (
    PredefinedTasks,
    create_daily_update_task,
    create_strategy_execution_task,
    create_health_check_task,
)


def example_1_basic_scheduling():
    """示例1: 基本任务调度"""
    print("\n" + "=" * 80)
    print("示例1: 基本任务调度")
    print("=" * 80)

    # 创建调度器
    scheduler = TaskScheduler()

    # 定义简单任务
    def test_task(task_id: str):
        print(f"  执行任务: {task_id}")
        time.sleep(1)
        return {"status": "success", "task_id": task_id}

    # 创建任务配置（每5秒执行一次）
    task_config = TaskConfig(
        name="test_interval_task",
        func=test_task,
        trigger_type="interval",
        trigger_args={"seconds": 5},
        kwargs={"task_id": "test_001"},
        max_retries=2,
        timeout=10,
    )

    # 添加任务
    scheduler.add_task(task_config)

    print("\n✓ 任务已添加")
    print(f"  任务名称: {task_config.name}")
    print(f"  触发器: 每5秒执行一次")

    # 查看任务列表
    tasks = scheduler.list_tasks()
    print(f"\n当前任务列表:")
    for task in tasks:
        print(f"  - {task['name']}: {task['status']}")

    return scheduler


def example_2_notification_system():
    """示例2: 通知系统"""
    print("\n" + "=" * 80)
    print("示例2: 通知系统")
    print("=" * 80)

    # 创建通知管理器（使用日志和控制台）
    config = NotificationConfig(
        channels=[NotificationChannel.LOG, NotificationChannel.CONSOLE]
    )

    notification_mgr = NotificationManager(config)

    # 1. 基本通知
    print("\n1. 发送基本通知")
    notification_mgr.send_notification(
        title="系统启动",
        message="MyStocks量化交易系统已成功启动",
        level=NotificationLevel.INFO,
    )

    # 2. 任务成功通知
    print("\n2. 任务成功通知")
    notification_mgr.send_success_notification(
        task_name="数据更新",
        execution_time=15.3,
        result="成功导入500只股票，总计10000条记录",
    )

    # 3. 任务失败通知
    print("\n3. 任务失败通知")
    notification_mgr.send_failure_notification(
        task_name="策略执行", error_message="数据库连接超时", retry_count=2
    )

    # 4. 交易信号通知
    print("\n4. 交易信号通知")
    notification_mgr.send_signal_notification(
        strategy_name="动量策略",
        symbol="sh600000",
        signal="buy",
        price=10.52,
        context={"ma_5": 10.45, "ma_20": 10.38, "rsi": 65.2, "volume_ratio": 1.8},
    )

    # 查看统计
    print("\n5. 通知统计")
    stats = notification_mgr.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    return notification_mgr


def example_3_predefined_tasks():
    """示例3: 使用预定义任务"""
    print("\n" + "=" * 80)
    print("示例3: 使用预定义任务")
    print("=" * 80)

    # 1. 健康检查任务
    print("\n1. 执行系统健康检查")
    health_result = PredefinedTasks.health_check(
        services=["database", "data_source", "strategy"]
    )
    print(f"  结果: {health_result['status']}")
    for service, status in health_result["services"].items():
        print(f"    - {service}: {status}")

    # 2. 创建预定义任务配置
    print("\n2. 创建预定义任务配置")

    # 每日数据更新任务（16:00执行）
    daily_update = create_daily_update_task(market="sh", hour=16, minute=0)
    print(f"  ✓ 每日数据更新任务: {daily_update.name}")
    print(f"      触发时间: 每天16:00")
    print(f"      优先级: {daily_update.priority.name}")

    # 策略执行任务（9:30执行）
    strategy_exec = create_strategy_execution_task(
        strategy_name="momentum", hour=9, minute=30
    )
    print(f"  ✓ 策略执行任务: {strategy_exec.name}")
    print(f"      触发时间: 每天9:30（工作日）")
    print(f"      依赖任务: {strategy_exec.depends_on}")

    # 健康检查任务（每30分钟）
    health_check = create_health_check_task(interval_minutes=30)
    print(f"  ✓ 健康检查任务: {health_check.name}")
    print(f"      触发频率: 每30分钟")

    return [daily_update, strategy_exec, health_check]


def example_4_integrated_system():
    """示例4: 完整集成系统"""
    print("\n" + "=" * 80)
    print("示例4: 完整集成系统")
    print("=" * 80)

    # 1. 创建通知管理器
    print("\n1. 初始化通知管理器")
    notification_config = NotificationConfig(
        channels=[NotificationChannel.LOG, NotificationChannel.CONSOLE],
        rate_limit=60,  # 1分钟内相同通知只发送一次
    )
    notification_mgr = NotificationManager(notification_config)

    # 2. 创建调度器（集成通知）
    print("\n2. 初始化调度器")
    scheduler = TaskScheduler(
        notification_manager=notification_mgr,
        monitoring_db=None,  # 可选：集成监控数据库
    )

    # 3. 定义业务任务
    print("\n3. 添加业务任务")

    def sample_data_update():
        """模拟数据更新"""
        print("  [任务] 开始数据更新...")
        time.sleep(2)
        print("  [任务] 数据更新完成")
        return {"updated_symbols": 100, "records": 5000}

    def sample_strategy_execution():
        """模拟策略执行"""
        print("  [任务] 开始执行策略...")
        time.sleep(1)
        print("  [任务] 策略执行完成")
        return {
            "signals": [
                {"symbol": "sh600000", "signal": "buy", "price": 10.52},
                {"symbol": "sh600016", "signal": "sell", "price": 5.23},
            ]
        }

    # 4. 创建任务配置
    data_update_task = TaskConfig(
        name="sample_data_update",
        func=sample_data_update,
        trigger_type="interval",
        trigger_args={"seconds": 10},
        priority=TaskPriority.HIGH,
        max_retries=3,
        notify_on_success=True,
        notify_on_failure=True,
    )

    strategy_task = TaskConfig(
        name="sample_strategy",
        func=sample_strategy_execution,
        trigger_type="interval",
        trigger_args={"seconds": 15},
        priority=TaskPriority.NORMAL,
        max_retries=2,
        notify_on_failure=True,
        depends_on=["sample_data_update"],
    )

    # 5. 添加任务到调度器
    scheduler.add_task(data_update_task)
    scheduler.add_task(strategy_task)

    print(f"\n✓ 已添加 {len(scheduler.tasks)} 个任务")

    # 6. 显示任务列表
    print("\n4. 当前任务列表")
    for task in scheduler.list_tasks():
        print(f"  - {task['name']}")
        print(f"      状态: {task['status']}")
        print(f"      优先级: {task['priority']}")
        print(f"      下次执行: {task['next_run']}")

    return scheduler, notification_mgr


def example_5_monitoring_and_stats():
    """示例5: 监控和统计"""
    print("\n" + "=" * 80)
    print("示例5: 监控和统计")
    print("=" * 80)

    # 创建调度器和通知管理器
    notification_mgr = NotificationManager(
        NotificationConfig(channels=[NotificationChannel.LOG])
    )
    scheduler = TaskScheduler(notification_manager=notification_mgr)

    # 添加一个测试任务并手动触发
    def quick_task():
        time.sleep(0.5)
        return "success"

    task = TaskConfig(
        name="monitoring_test",
        func=quick_task,
        trigger_type="interval",
        trigger_args={"seconds": 60},
        max_retries=1,
    )

    scheduler.add_task(task)

    # 手动执行任务（用于演示）
    print("\n1. 手动执行任务（演示）")
    try:
        result = quick_task()
        print(f"  ✓ 任务执行成功: {result}")
    except Exception as e:
        print(f"  ✗ 任务执行失败: {e}")

    # 获取调度器统计
    print("\n2. 调度器统计")
    scheduler_stats = scheduler.get_statistics()
    for key, value in scheduler_stats.items():
        print(f"  {key}: {value}")

    # 获取通知统计
    print("\n3. 通知统计")
    notification_stats = notification_mgr.get_statistics()
    for key, value in notification_stats.items():
        print(f"  {key}: {value}")

    # 获取执行历史
    print("\n4. 执行历史")
    history = scheduler.get_execution_history(limit=10)
    if history:
        for execution in history:
            print(f"  [{execution.status.value}] {execution.task_name}")
            print(f"      开始: {execution.start_time}")
            if execution.end_time:
                print(f"      耗时: {execution.duration:.2f}秒")
    else:
        print("  无执行记录")

    return scheduler, notification_mgr


def main():
    """主函数 - 运行所有示例"""
    print("=" * 80)
    print("自动化调度系统完整示例")
    print("=" * 80)

    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # 运行示例
    print("\n提示: 本示例仅演示功能，不会实际启动调度器")
    print("      如需实际运行，请取消 scheduler.start() 的注释\n")

    # 示例1: 基本调度
    scheduler1 = example_1_basic_scheduling()

    # 示例2: 通知系统
    notification_mgr = example_2_notification_system()

    # 示例3: 预定义任务
    predefined_tasks = example_3_predefined_tasks()

    # 示例4: 完整集成
    scheduler4, notification_mgr4 = example_4_integrated_system()

    # 示例5: 监控和统计
    scheduler5, notification_mgr5 = example_5_monitoring_and_stats()

    # 实际启动调度器（演示）
    print("\n" + "=" * 80)
    print("如需启动调度器，请运行:")
    print("=" * 80)
    print(
        """
# 启动调度器
scheduler.start()

# 保持运行
try:
    while True:
        time.sleep(60)
        # 可以在这里检查状态
        stats = scheduler.get_statistics()
        print(f"运行中 - 总任务: {stats['total_tasks']}, 执行: {stats['total_executions']}")
except KeyboardInterrupt:
    print("停止调度器...")
    scheduler.stop()
"""
    )

    print("\n" + "=" * 80)
    print("所有示例运行完成")
    print("=" * 80)

    print("\n提示:")
    print("  1. 示例1-5: 演示各个功能组件")
    print("  2. 实际部署: 使用 config/automation_config.yaml 配置")
    print("  3. 生产环境: 建议使用 systemd 或 supervisor 管理调度器进程")
    print("  4. 监控: 集成监控数据库记录所有任务执行")


if __name__ == "__main__":
    main()
