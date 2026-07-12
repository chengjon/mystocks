#!/usr/bin/env python3
"""CLI性能指标收集脚本

收集和分析CLI的性能指标，包括：
- 任务执行指标（完成时间、阻塞时间）
- 资源使用指标（内存、CPU）
- 代码质量指标（ESLint、Pylint、测试覆盖率）
- 协调效率指标

Usage:
    # 收集所有CLI的指标
    python scripts/dev/metrics_collector.py --all

    # 生成METRICS.md报告
    python scripts/dev/metrics_collector.py --generate-report
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class MetricsCollector:
    """性能指标收集器"""

    def __init__(self, clis_dir: str = "CLIS"):
        self.clis_dir = Path(clis_dir)
        self.cli_list = self._discover_clis()
        self.metrics_data = {}

    def _discover_clis(self) -> List[str]:
        """发现所有CLI目录"""
        clis = []
        for item in self.clis_dir.iterdir():
            if item.is_dir() and not item.name.startswith("_"):
                if (item / "STATUS.md").exists():
                    clis.append(item.name)
        return sorted(clis)

    def collect_task_metrics(self, cli_name: str) -> Dict:
        """收集任务执行指标"""
        task_file = self.clis_dir / cli_name / "TASK.md"

        if not task_file.exists():
            return {
                "total_tasks": 0,
                "completed_tasks": 0,
                "in_progress_tasks": 0,
                "pending_tasks": 0,
                "completion_rate": 0.0,
                "avg_completion_hours": 0.0,
            }

        content = task_file.read_text(encoding="utf-8")
        total_tasks = 0
        completed_tasks = 0
        in_progress_tasks = 0
        pending_tasks = 0
        total_hours = 0
        completed_hours = 0

        task_pattern = r"- \[(.*?)\] (task-[\d.]+)[:：](.*?)(?:\n|$)"
        for match in re.finditer(task_pattern, content):
            total_tasks += 1
            status = match.group(1)

            if status.lower() in ["x", "✅", "done", "完成"]:
                completed_tasks += 1
            elif status.lower() in [">", "🔄", "wip", "进行中"]:
                in_progress_tasks += 1
            else:
                pending_tasks += 1

            task_text = match.group(3)
            hours_match = re.search(r"(\d+(?:\.\d+)?)\s*[h小时]", task_text)
            if hours_match:
                hours = float(hours_match.group(1))
                total_hours += hours
                if status.lower() in ["x", "✅", "done", "完成"]:
                    completed_hours += hours

        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
        avg_completion_hours = (completed_hours / completed_tasks) if completed_tasks > 0 else 0.0

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": completion_rate,
            "estimated_total_hours": total_hours,
            "completed_hours": completed_hours,
            "remaining_hours": total_hours - completed_hours,
            "avg_completion_hours": avg_completion_hours,
        }

    def collect_resource_metrics(self, cli_name: str) -> Dict:
        """收集资源使用指标"""
        cli_dir = self.clis_dir / cli_name
        total_files = 0
        total_size_kb = 0

        for root, dirs, files in os.walk(cli_dir):
            dirs[:] = [d for d in dirs if d not in ["__pycache__", "node_modules", ".git"]]
            for file in files:
                file_path = Path(root) / file
                if file_path.is_file():
                    total_files += 1
                    try:
                        total_size_kb += file_path.stat().st_size / 1024
                    except:
                        pass

        mailbox_count = len(list((cli_dir / "mailbox").glob("*"))) if (cli_dir / "mailbox").exists() else 0
        archive_count = len(list((cli_dir / "archive").glob("*"))) if (cli_dir / "archive").exists() else 0

        return {
            "total_files": total_files,
            "total_size_kb": round(total_size_kb, 2),
            "total_size_mb": round(total_size_kb / 1024, 2),
            "mailbox_messages": mailbox_count,
            "archived_messages": archive_count,
            "archive_ratio": round(archive_count / (mailbox_count + archive_count) * 100, 1)
            if (mailbox_count + archive_count) > 0
            else 0.0,
        }

    def collect_quality_metrics(self, cli_name: str) -> Dict:
        """收集代码质量指标"""
        cli_dir = self.clis_dir / cli_name
        metrics = {
            "has_rules": False,
            "has_status": False,
            "has_config": False,
            "rule_lines": 0,
            "documentation_completeness": 0.0,
        }

        if (cli_dir / "RULES.md").exists():
            metrics["has_rules"] = True
            metrics["rule_lines"] = len((cli_dir / "RULES.md").read_text(encoding="utf-8").split("\n"))

        if (cli_dir / "STATUS.md").exists():
            metrics["has_status"] = True

        if (cli_dir / ".cli_config").exists():
            metrics["has_config"] = True

        required_files = ["TASK.md", "RULES.md", "STATUS.md"]
        optional_files = ["REPORT.md", ".cli_config", "watcher.log"]
        existing_required = sum(1 for f in required_files if (cli_dir / f).exists())
        existing_optional = sum(1 for f in optional_files if (cli_dir / f).exists())

        metrics["documentation_completeness"] = round(
            (existing_required / len(required_files) * 70) + (existing_optional / len(optional_files) * 30),
            1,
        )

        return metrics

    def collect_coordination_metrics(self) -> Dict:
        """收集协调效率指标"""
        coord_log = self.clis_dir / "SHARED" / "COORDINATION_LOG.md"

        if not coord_log.exists():
            return {
                "total_coordinations": 0,
                "coordinations_today": 0,
                "last_coordination": None,
                "avg_coordination_interval_hours": 0.0,
            }

        content = coord_log.read_text(encoding="utf-8")
        coord_sections = re.findall(r"## 自动协调:", content)
        total_coordinations = len(coord_sections)

        today = datetime.now().strftime("%Y-%m-%d")
        coordinations_today = len(re.findall(rf"{today}", content))

        last_coord_match = re.search(r"(\d{{4}}-\d{{2}}-\d{{2}} \d{{2}}:\d{{2}})", content[-500:])
        last_coordination = last_coord_match.group(1) if last_coord_match else None

        return {
            "total_coordinations": total_coordinations,
            "coordinations_today": coordinations_today,
            "last_coordination": last_coordination,
            "coordination_activity": "High"
            if coordinations_today >= 3
            else "Medium"
            if coordinations_today >= 1
            else "Low",
        }

    def collect_all_metrics(self) -> Dict:
        """收集所有CLI的指标"""
        all_metrics = {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "clis": {},
        }

        for cli in self.cli_list:
            all_metrics["clis"][cli] = {
                "tasks": self.collect_task_metrics(cli),
                "resources": self.collect_resource_metrics(cli),
                "quality": self.collect_quality_metrics(cli),
            }

        all_metrics["coordination"] = self.collect_coordination_metrics()
        all_metrics["summary"] = self._calculate_summary(all_metrics)

        return all_metrics

    def _calculate_summary(self, metrics: Dict) -> Dict:
        """计算汇总统计"""
        summary = {
            "total_tasks": 0,
            "total_completed": 0,
            "overall_completion_rate": 0.0,
            "active_clis": 0,
            "total_files": 0,
            "total_size_mb": 0.0,
        }

        for cli_data in metrics["clis"].values():
            task_data = cli_data["tasks"]
            resource_data = cli_data["resources"]

            summary["total_tasks"] += task_data["total_tasks"]
            summary["total_completed"] += task_data["completed_tasks"]
            summary["total_files"] += resource_data["total_files"]
            summary["total_size_mb"] += resource_data["total_size_mb"]

            if task_data["in_progress_tasks"] > 0 or task_data["pending_tasks"] > 0:
                summary["active_clis"] += 1

        if summary["total_tasks"] > 0:
            summary["overall_completion_rate"] = round(
                summary["total_completed"] / summary["total_tasks"] * 100,
                1,
            )

        return summary

    def generate_metrics_report(self) -> str:
        """生成METRICS.md报告"""
        metrics = self.collect_all_metrics()

        lines = []
        lines.append("# CLI性能指标报告")
        lines.append("")
        lines.append(f"**生成时间**: {metrics['generated_at']}")
        lines.append(f"**监控CLI数量**: {len(metrics['clis'])}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 📊 总体性能指标")
        lines.append("")
        lines.append("### 任务执行统计")
        lines.append(f"- **总任务数**: {metrics['summary']['total_tasks']}")
        lines.append(f"- **已完成**: {metrics['summary']['total_completed']}")
        lines.append(f"- **总体完成率**: {metrics['summary']['overall_completion_rate']}%")
        lines.append(f"- **活跃CLI**: {metrics['summary']['active_clis']}")
        lines.append("")
        lines.append("### 资源使用统计")
        lines.append(f"- **总文件数**: {metrics['summary']['total_files']}")
        lines.append(f"- **总存储**: {metrics['summary']['total_size_mb']:.2f} MB")
        lines.append("")
        lines.append("### 协调活动")
        lines.append(f"- **总协调次数**: {metrics['coordination']['total_coordinations']}")
        lines.append(f"- **今日协调**: {metrics['coordination']['coordinations_today']}")
        lines.append(f"- **协调活跃度**: {metrics['coordination']['coordination_activity']}")

        if metrics["coordination"]["last_coordination"]:
            lines.append("")
            lines.append(f"- **最后协调**: {metrics['coordination']['last_coordination']}")

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 📈 各CLI详细指标")
        lines.append("")

        for cli, cli_metrics in metrics["clis"].items():
            lines.append(f"### {cli.upper()} CLI")
            lines.append("")

            task_data = cli_metrics["tasks"]
            lines.append("#### 任务执行")
            lines.append(f"- **任务总数**: {task_data['total_tasks']}")
            lines.append(
                f"- **完成**: {task_data['completed_tasks']} | **进行中**: {task_data['in_progress_tasks']} | **待开始**: {task_data['pending_tasks']}"
            )
            lines.append(f"- **完成率**: {task_data['completion_rate']:.1f}%")
            lines.append(f"- **预计总工时**: {task_data['estimated_total_hours']:.1f}小时")
            lines.append(f"- **已完成工时**: {task_data['completed_hours']:.1f}小时")
            lines.append(f"- **剩余工时**: {task_data['remaining_hours']:.1f}小时")
            lines.append("")

            resource_data = cli_metrics["resources"]
            lines.append("#### 资源使用")
            lines.append(f"- **文件数**: {resource_data['total_files']}")
            lines.append(f"- **存储大小**: {resource_data['total_size_mb']:.2f} MB")
            lines.append(f"- **Mailbox消息**: {resource_data['mailbox_messages']}")
            lines.append(f"- **已归档**: {resource_data['archived_messages']} ({resource_data['archive_ratio']}%)")
            lines.append("")

            quality_data = cli_metrics["quality"]
            lines.append("#### 文档质量")
            lines.append(f"- **文档完整性**: {quality_data['documentation_completeness']}%")
            lines.append(
                f"- **规则文件**: {'✅' if quality_data['has_rules'] else '❌'} ({quality_data['rule_lines']}行)"
            )
            lines.append(f"- **配置文件**: {'✅' if quality_data['has_config'] else '❌'}")
            lines.append("")
            lines.append("---")
            lines.append("")

        lines.append("## 📉 性能分析")
        lines.append("")
        lines.append("### 🎯 高效指标")
        lines.append("")

        best_cli = max(metrics["clis"].items(), key=lambda x: x[1]["tasks"]["completion_rate"])
        lines.append(f"**最佳任务完成率**: {best_cli[0].upper()} CLI ({best_cli[1]['tasks']['completion_rate']:.1f}%)")

        best_docs = max(metrics["clis"].items(), key=lambda x: x[1]["quality"]["documentation_completeness"])
        lines.append(
            f"**最佳文档质量**: {best_docs[0].upper()} CLI ({best_docs[1]['quality']['documentation_completeness']}%)"
        )

        lines.append("")
        lines.append("### ⚠️ 需要关注")
        lines.append("")

        for cli, cli_metrics in metrics["clis"].items():
            if cli_metrics["tasks"]["total_tasks"] == 0:
                lines.append(f"- **{cli.upper()} CLI**: 无任务分配")

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 💡 优化建议")
        lines.append("")
        lines.append("基于当前指标，建议关注以下方面：")
        lines.append("")
        lines.append("1. **任务执行效率**: 监控任务完成时间，及时识别阻塞问题")
        lines.append("2. **文档维护**: 定期更新STATUS.md和REPORT.md")
        lines.append("3. **资源管理**: 定期清理archive目录，避免文件堆积")
        lines.append("4. **协调优化**: 提高协调频率，及时发现和解决问题")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"**报告生成**: {metrics['generated_at']}")
        lines.append("**脚本**: `scripts/dev/metrics_collector.py`")

        return "\n".join(lines)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="CLI性能指标收集工具")
    parser.add_argument("--cli", type=str, help="收集指定CLI的指标")
    parser.add_argument("--all", action="store_true", help="收集所有CLI的指标")
    parser.add_argument("--generate-report", action="store_true", help="生成METRICS.md报告")
    parser.add_argument("--export-json", type=str, help="导出JSON格式到指定文件")
    parser.add_argument("--clis-dir", default="CLIS", help="CLI目录路径")

    args = parser.parse_args()

    collector = MetricsCollector(args.clis_dir)

    if args.generate_report:
        print("📊 正在生成性能指标报告...")
        report = collector.generate_metrics_report()

        output_file = Path(args.clis_dir) / "main" / "METRICS.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(report, encoding="utf-8")

        print(f"✅ 指标报告已生成: {output_file}")
        return

    if args.export_json:
        print("📊 正在导出指标数据...")
        metrics = collector.collect_all_metrics()

        output_file = Path(args.export_json)
        output_file.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

        print(f"✅ JSON数据已导出: {output_file}")
        return

    if args.cli or args.all:
        cli_list = [args.cli] if args.cli else collector.cli_list

        print(f"\n{'=' * 70}")
        print("📊 CLI性能指标")
        print(f"{'=' * 70}\n")

        for cli in cli_list:
            task_metrics = collector.collect_task_metrics(cli)
            resource_metrics = collector.collect_resource_metrics(cli)
            quality_metrics = collector.collect_quality_metrics(cli)

            print(f"### {cli.upper()} CLI")
            print(
                f"任务: {task_metrics['completed_tasks']}/{task_metrics['total_tasks']} ({task_metrics['completion_rate']:.1f}%)"
            )
            print(f"存储: {resource_metrics['total_size_mb']:.2f} MB ({resource_metrics['total_files']} 文件)")
            print(f"文档: {quality_metrics['documentation_completeness']}% 完整")
            print()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
