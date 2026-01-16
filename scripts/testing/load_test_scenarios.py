"""
压测场景定义和执行脚本
定义4种不同的压测场景，用于全面验证系统性能

任务14.1: Locust压测脚本和用户行为建模
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 计算项目根目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from load_test_user_behaviors import (
    TrafficModelGenerator,
    LoadTestMetrics,
)
import structlog

logger = structlog.get_logger()


class LoadTestScenario:
    """压测场景基类"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.duration = 600  # 默认10分钟
        self.target_users = 1000

    def get_config(self) -> Dict[str, Any]:
        """获取场景配置"""
        raise NotImplementedError


class Scenario1_Baseline(LoadTestScenario):
    """场景1: 基准测试 - 验证基础性能"""

    def __init__(self):
        super().__init__(
            name="Baseline Test",
            description="Verify basic API performance with 100 concurrent users",
        )
        self.target_users = 100
        self.duration = 300  # 5分钟

    def get_config(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "target_users": self.target_users,
            "spawn_rate": 10,  # 每秒增加10个用户
            "duration": self.duration,
            "objectives": [
                "Response time < 500ms for 95% of requests",
                "Error rate < 1%",
                "Database connection pool: 20-30 connections",
            ],
            "monitored_endpoints": [
                "/health",
                "/api/market/realtime/000001",
                "/api/auth/login",
            ],
        }


class Scenario2_NormalLoad(LoadTestScenario):
    """场景2: 正常负载 - 模拟日常交易时段"""

    def __init__(self):
        super().__init__(
            name="Normal Load Test",
            description="Simulate typical daytime trading activity with 500 users",
        )
        self.target_users = 500
        self.duration = 600  # 10分钟

    def get_config(self) -> Dict[str, Any]:
        # 白天流量分布
        traffic_profile = TrafficModelGenerator.generate_hourly_traffic_profile()
        user_distribution = TrafficModelGenerator.generate_user_distribution(
            self.target_users
        )

        return {
            "name": self.name,
            "description": self.description,
            "target_users": self.target_users,
            "spawn_rate": 25,  # 每秒增加25个用户
            "duration": self.duration,
            "traffic_profile": traffic_profile,
            "user_distribution": {k.value: v for k, v in user_distribution.items()},
            "objectives": [
                "Response time < 1s for 95% of requests",
                "Error rate < 0.5%",
                "Database connections: 30-50",
                "Cache hit rate > 70%",
            ],
            "monitored_endpoints": [
                "/api/market/realtime/[stock_code]",
                "/api/market/kline/[stock_code]",
                "/api/market/fund-flow/[stock_code]",
            ],
            "monitored_services": ["api", "database", "cache", "websocket"],
        }


class Scenario3_PeakLoad(LoadTestScenario):
    """场景3: 高峰负载 - 模拟开盘/收盘时段"""

    def __init__(self):
        super().__init__(
            name="Peak Load Test",
            description="Simulate market open/close peak traffic with 1000 users",
        )
        self.target_users = 1000
        self.duration = 600  # 10分钟

    def get_config(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "target_users": self.target_users,
            "spawn_rate": 50,  # 每秒增加50个用户
            "duration": self.duration,
            "scenarios": {
                "day_traders": {
                    "user_count": 150,  # 150个日内交易者
                    "behavior": "high_frequency",  # 高频查询
                    "avg_requests_per_second": 2.0,
                    "avg_response_time_target": 800,  # 毫秒
                },
                "swing_traders": {
                    "user_count": 250,
                    "behavior": "medium_frequency",
                    "avg_requests_per_second": 0.8,
                    "avg_response_time_target": 1000,
                },
                "investors": {
                    "user_count": 400,
                    "behavior": "low_frequency",
                    "avg_requests_per_second": 0.2,
                    "avg_response_time_target": 1200,
                },
                "analysts": {
                    "user_count": 150,
                    "behavior": "analysis_heavy",
                    "avg_requests_per_second": 1.5,
                    "avg_response_time_target": 1000,
                },
                "monitoring": {
                    "user_count": 50,
                    "behavior": "monitoring",
                    "avg_requests_per_second": 0.1,
                    "avg_response_time_target": 500,
                },
            },
            "objectives": [
                "Response time < 2s for 95% of requests",
                "Error rate < 1%",
                "Database connections: 60-100",
                "WebSocket connections: > 500",
                "Cache hit rate > 60%",
            ],
            "stress_points": [
                "Market open (9:30)",
                "Lunch break (11:30-13:00)",
                "Market close (15:00)",
                "After hours (18:00)",
            ],
        }


class Scenario4_StressTest(LoadTestScenario):
    """场景4: 压力测试 - 测试系统极限"""

    def __init__(self):
        super().__init__(
            name="Stress Test",
            description="Push system to its limits with 2000 concurrent users",
        )
        self.target_users = 2000
        self.duration = 900  # 15分钟

    def get_config(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "target_users": self.target_users,
            "spawn_rate": 100,  # 每秒增加100个用户
            "ramp_up_time": 200,  # 线性增加200秒到达2000用户
            "duration": self.duration,
            "test_phases": [
                {
                    "phase": "ramp_up",
                    "duration": 200,
                    "users": "0 -> 2000",
                    "description": "Gradually increase users",
                },
                {
                    "phase": "sustained",
                    "duration": 600,
                    "users": "2000",
                    "description": "Hold at peak load",
                },
                {
                    "phase": "breakdown",
                    "duration": 100,
                    "users": "0",
                    "description": "Gracefully disconnect users",
                },
            ],
            "objectives": [
                "System remains operational",
                "Error rate < 5% acceptable",
                "No deadlocks or hangs",
                "Database connection pool limits respected",
                "Graceful degradation observed",
            ],
            "monitoring_targets": [
                "CPU usage",
                "Memory consumption",
                "Network bandwidth",
                "Disk I/O",
                "Database connection pool exhaustion",
                "WebSocket connection limits",
                "Request queue depths",
            ],
            "alerts": [
                {"metric": "error_rate", "threshold": 0.05, "severity": "critical"},
                {
                    "metric": "response_time_p95",
                    "threshold": 5000,  # 5秒
                    "severity": "warning",
                },
                {
                    "metric": "db_connection_pool_exhaustion",
                    "threshold": 0.9,  # 90%利用率
                    "severity": "critical",
                },
                {
                    "metric": "websocket_connection_failures",
                    "threshold": 0.01,  # 1%失败率
                    "severity": "warning",
                },
            ],
        }


class LoadTestOrchestrator:
    """压测编排器 - 管理和执行压测场景"""

    def __init__(self, output_dir: str = "./load_test_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.scenarios = [
            Scenario1_Baseline(),
            Scenario2_NormalLoad(),
            Scenario3_PeakLoad(),
            Scenario4_StressTest(),
        ]
        self.metrics = LoadTestMetrics()

    def list_scenarios(self) -> List[str]:
        """列出所有场景"""
        return [
            f"{i + 1}. {s.name}: {s.description}" for i, s in enumerate(self.scenarios)
        ]

    def get_scenario(self, index: int) -> LoadTestScenario:
        """获取指定的场景"""
        if 0 <= index < len(self.scenarios):
            return self.scenarios[index]
        raise ValueError(f"Invalid scenario index: {index}")

    def generate_configuration_file(self, scenario_index: int) -> str:
        """为指定场景生成配置文件"""
        scenario = self.get_scenario(scenario_index)
        config = scenario.get_config()

        # 添加通用配置
        config.update(
            {
                "api_host": os.getenv("API_HOST", "http://localhost:8000"),
                "api_timeout": 30,
                "generated_at": datetime.now().isoformat(),
                "task": "Task 14.1: Load Testing",
                "performance_targets": {
                    "response_time_p50_ms": 200,
                    "response_time_p95_ms": 1000,
                    "response_time_p99_ms": 2000,
                    "error_rate_percent": 1.0,
                    "cache_hit_rate_percent": 70,
                    "throughput_requests_per_second": 500,
                },
            }
        )

        config_file = self.output_dir / f"scenario_{scenario_index + 1}_config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        logger.info(f"Configuration generated: {config_file}")
        return str(config_file)

    def generate_test_plan(self) -> str:
        """生成完整的测试计划"""
        plan = {
            "project": "MyStocks Load Testing - Task 14.1",
            "generated_at": datetime.now().isoformat(),
            "scenarios": [],
        }

        for i, scenario in enumerate(self.scenarios, 1):
            config = scenario.get_config()
            plan["scenarios"].append({"sequence": i, "scenario": config})

        plan_file = self.output_dir / "load_test_plan.json"
        with open(plan_file, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)

        logger.info(f"Test plan generated: {plan_file}")
        return str(plan_file)

    def print_scenario_details(self, scenario_index: int):
        """打印场景详细信息"""
        scenario = self.get_scenario(scenario_index)
        config = scenario.get_config()

        print(f"\n{'=' * 60}")
        print(f"Scenario {scenario_index + 1}: {scenario.name}")
        print(f"{'=' * 60}")
        print(f"Description: {scenario.description}")
        print(f"Duration: {scenario.duration}s")
        print(f"Target Users: {scenario.target_users}")
        print()
        print("Configuration:")
        print(json.dumps(config, indent=2, ensure_ascii=False))
        print(f"{'=' * 60}\n")

    def export_scenarios_as_markdown(self) -> str:
        """导出所有场景为Markdown"""
        md_file = self.output_dir / "load_test_scenarios.md"

        with open(md_file, "w", encoding="utf-8") as f:
            f.write("# MyStocks Load Testing Scenarios\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("Task: 14.1 - Locust Load Testing Scripts\n\n")

            for i, scenario in enumerate(self.scenarios, 1):
                config = scenario.get_config()
                f.write(f"## Scenario {i}: {scenario.name}\n\n")
                f.write(f"{scenario.description}\n\n")
                f.write(f"**Duration**: {scenario.duration}s\n")
                f.write(f"**Target Users**: {scenario.target_users}\n\n")

                # 写入配置
                f.write("### Configuration\n\n")
                f.write("```json\n")
                f.write(json.dumps(config, indent=2, ensure_ascii=False))
                f.write("\n```\n\n")

                # 写入目标
                if "objectives" in config:
                    f.write("### Objectives\n\n")
                    for obj in config["objectives"]:
                        f.write(f"- {obj}\n")
                    f.write("\n")

        logger.info(f"Scenarios exported: {md_file}")
        return str(md_file)


def main():
    """主函数 - 示例用法"""
    orchestrator = LoadTestOrchestrator()

    print("Available Load Test Scenarios:")
    print("=" * 60)
    for scenario_desc in orchestrator.list_scenarios():
        print(scenario_desc)
    print("=" * 60)

    # 生成所有配置文件
    for i in range(len(orchestrator.scenarios)):
        config_file = orchestrator.generate_configuration_file(i)
        print(f"✓ Generated: {config_file}")

    # 生成测试计划
    plan_file = orchestrator.generate_test_plan()
    print(f"✓ Generated: {plan_file}")

    # 导出为Markdown
    md_file = orchestrator.export_scenarios_as_markdown()
    print(f"✓ Generated: {md_file}")

    print(f"\nAll files saved to: {orchestrator.output_dir}")


if __name__ == "__main__":
    main()
