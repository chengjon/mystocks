#!/usr/bin/env python3
"""任务分配辅助工具

协助main CLI进行任务分配，提供：
- CLI任务状态查看
- 智能任务分配建议
- 自动生成任务分配通知
- TASK.md文件更新

Usage:
    # 查看所有CLI的任务状态
    python scripts/dev/task_assigner.py --status

    # 为指定CLI分配任务
    python scripts/dev/task_assigner.py --assign web --task "task-5.1" --priority "高"

    # 生成任务分配建议
    python scripts/dev/task_assigner.py --suggest
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class TaskAssigner:
    """任务分配助手"""

    def __init__(self, clis_dir: str = "CLIS"):
        self.clis_dir = Path(clis_dir)
        self.cli_list = self._discover_clis()

    def _discover_clis(self) -> List[str]:
        """发现所有CLI目录"""
        clis = []
        for item in self.clis_dir.iterdir():
            if item.is_dir() and not item.name.startswith("_") and item.name != "SHARED":
                if (item / "TASK.md").exists():
                    clis.append(item.name)
        return sorted(clis)

    def get_cli_task_status(self, cli_name: str) -> Dict:
        """获取CLI的任务状态"""
        task_file = self.clis_dir / cli_name / "TASK.md"
        status_file = self.clis_dir / cli_name / "STATUS.md"

        if not task_file.exists():
            return {
                "cli": cli_name,
                "has_tasks": False,
                "total_tasks": 0,
                "completed": 0,
                "in_progress": 0,
                "pending": 0,
                "current_task": None,
                "state": "Unknown",
            }

        # 读取任务文件
        task_content = task_file.read_text(encoding="utf-8")
        lines = task_content.split("\n")

        total = 0
        completed = 0
        in_progress = 0
        pending = 0
        current_task = None

        for line in lines:
            if line.startswith("- [x]") or line.startswith("- [✅]"):
                total += 1
                completed += 1
            elif line.startswith("- [>]") or line.startswith("- [🔄]"):
                total += 1
                in_progress += 1
                # 提取当前任务
                if "task-" in line:
                    task_id = line.split("task-")[1].split()[0]
                    current_task = f"task-{task_id}"
            elif line.startswith("- [ ]"):
                total += 1
                pending += 1

        # 读取状态文件
        state = "Unknown"
        if status_file.exists():
            status_content = status_file.read_text(encoding="utf-8")
            if "🟢 Active" in status_content or "Active" in status_content:
                state = "Active"
            elif "🟡 Idle" in status_content or "Idle" in status_content:
                state = "Idle"
            elif "🔴 Blocked" in status_content or "Blocked" in status_content:
                state = "Blocked"

        return {
            "cli": cli_name,
            "has_tasks": True,
            "total_tasks": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "current_task": current_task,
            "state": state,
        }

    def suggest_task_assignment(self) -> List[Dict]:
        """生成任务分配建议"""
        suggestions = []

        for cli in self.cli_list:
            status = self.get_cli_task_status(cli)

            # 规则1: 如果CLI处于Idle状态且没有待处理任务，建议分配新任务
            if status["state"] == "Idle" and status["pending"] == 0:
                suggestions.append(
                    {
                        "cli": cli,
                        "action": "assign",
                        "reason": f"{cli} CLI处于空闲状态，无待处理任务",
                        "priority": "High",
                    }
                )

            # 规则2: 如果CLI完成率>80%且还有待处理任务，建议继续分配
            elif status["total_tasks"] > 0 and status["completed"] / status["total_tasks"] > 0.8:
                suggestions.append(
                    {
                        "cli": cli,
                        "action": "continue",
                        "reason": f"{cli} CLI完成率{status['completed'] / status['total_tasks'] * 100:.0f}%，可以继续分配",
                        "priority": "Medium",
                    }
                )

            # 规则3: 如果CLI处于Blocked状态，需要优先解决
            elif status["state"] == "Blocked":
                suggestions.append(
                    {
                        "cli": cli,
                        "action": "unblock",
                        "reason": f"{cli} CLI处于阻塞状态，需要优先解决",
                        "priority": "Critical",
                    }
                )

        return sorted(
            suggestions,
            key=lambda x: {
                "Critical": 0,
                "High": 1,
                "Medium": 2,
                "Low": 3,
            }.get(x["priority"], 4),
        )

    def create_task_assignment(
        self,
        cli_name: str,
        task_id: str,
        task_title: str,
        priority: str = "Medium",
        estimated_hours: float = 8.0,
        description: str = "",
    ) -> str:
        """创建任务分配通知"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"task_assignment_{timestamp}.md"
        output_file = self.clis_dir / cli_name / "mailbox" / filename

        # 生成任务分配通知
        content = f"""# 任务分配通知

**Subject**: 新任务分配 - {task_id}
**From**: main CLI
**To**: {cli_name} CLI
**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Priority**: {priority}

---

## 任务信息

**任务ID**: {task_id}
**任务标题**: {task_title}
**优先级**: {priority}
**预计工时**: {estimated_hours}小时

## 任务描述

{description or "请参考TASK.md中的详细任务描述。"}

## 下一步

1. 查看TASK.md中的任务详情
2. 规划实现步骤
3. 开始执行任务
4. 定期更新STATUS.md
5. 完成后提交REPORT.md

---

**通知类型**: TASK_ASSIGNMENT
**自动生成**: scripts/dev/task_assigner.py
"""

        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content, encoding="utf-8")

        return str(output_file)

    def update_cli_task_file(
        self,
        cli_name: str,
        task_id: str,
        task_title: str,
        priority: str = "Medium",
        estimated_hours: float = 8.0,
    ) -> bool:
        """更新CLI的TASK.md文件"""
        task_file = self.clis_dir / cli_name / "TASK.md"

        if not task_file.exists():
            print(f"❌ 错误: {cli_name} CLI的TASK.md不存在")
            return False

        # 读取现有任务
        content = task_file.read_text(encoding="utf-8")

        # 添加新任务
        priority_icon = {
            "Critical": "🔴",
            "High": "🟠",
            "Medium": "🟡",
            "Low": "🟢",
        }.get(priority, "⚪")

        new_task = f"\n- [ ] **{task_id}**: {task_title} [{priority_icon} {priority} - {estimated_hours}h]\n"

        # 找到任务列表的末尾
        lines = content.split("\n")
        insert_position = len(lines)

        for i, line in enumerate(lines):
            if i > 0 and lines[i - 1].strip() == "" and not line.startswith("-"):
                insert_position = i
                break

        lines.insert(insert_position, new_task.strip())
        updated_content = "\n".join(lines)

        # 写回文件
        task_file.write_text(updated_content, encoding="utf-8")

        return True

    def print_status_report(self):
        """打印任务状态报告"""
        print(f"\n{'=' * 70}")
        print("📋 CLI任务状态报告")
        print(f"{'=' * 70}\n")

        for cli in self.cli_list:
            status = self.get_cli_task_status(cli)

            # 状态图标
            state_icon = {
                "Active": "🟢",
                "Idle": "🟡",
                "Blocked": "🔴",
                "Unknown": "⚪",
            }.get(status["state"], "⚪")

            print(f"### {cli.upper()} CLI")
            print(f"状态: {state_icon} {status['state']}")

            if status["has_tasks"]:
                print(
                    f"任务: {status['completed']}/{status['total_tasks']} "
                    f"(完成: {status['completed']} | "
                    f"进行中: {status['in_progress']} | "
                    f"待开始: {status['pending']})"
                )

                if status["current_task"]:
                    print(f"当前: {status['current_task']}")
            else:
                print("任务: 无任务")

            print()

    def print_suggestions(self):
        """打印任务分配建议"""
        suggestions = self.suggest_task_assignment()

        if not suggestions:
            print("\n✅ 所有CLI状态良好，无需特殊处理")
            return

        print(f"\n{'=' * 70}")
        print("💡 任务分配建议")
        print(f"{'=' * 70}\n")

        priority_order = ["Critical", "High", "Medium", "Low"]
        current_priority = None

        for suggestion in suggestions:
            if suggestion["priority"] != current_priority:
                current_priority = suggestion["priority"]
                priority_icon = {
                    "Critical": "🔴",
                    "High": "🟠",
                    "Medium": "🟡",
                    "Low": "🟢",
                }.get(current_priority, "⚪")

                print(f"\n### {priority_icon} {current_priority} Priority")

            print(f"\n**{suggestion['cli'].upper()} CLI**: {suggestion['action']}")
            print(f"   原因: {suggestion['reason']}")

        print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="任务分配辅助工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 查看所有CLI的任务状态
  python scripts/dev/task_assigner.py --status

  # 生成任务分配建议
  python scripts/dev/task_assigner.py --suggest

  # 为web CLI分配新任务
  python scripts/dev/task_assigner.py --assign web --task "task-5.1" --title "实现响应式数据可视化组件" --priority "高"

  # 同时更新TASK.md文件
  python scripts/dev/task_assigner.py --assign web --task "task-5.2" --title "实现用户认证UI界面" --priority "中" --update-task-file
        """,
    )

    parser.add_argument("--status", action="store_true", help="查看所有CLI的任务状态")
    parser.add_argument("--suggest", action="store_true", help="生成任务分配建议")
    parser.add_argument("--assign", type=str, metavar="CLI", help="为指定CLI分配任务")
    parser.add_argument("--task", type=str, metavar="TASK_ID", help="任务ID（如: task-5.1）")
    parser.add_argument("--title", type=str, metavar="TITLE", help="任务标题")
    parser.add_argument(
        "--priority", type=str, default="Medium", metavar="PRIORITY", help="任务优先级（Critical/High/Medium/Low）"
    )
    parser.add_argument("--hours", type=float, default=8.0, metavar="HOURS", help="预计工时（小时）")
    parser.add_argument("--description", type=str, default="", metavar="DESC", help="任务描述")
    parser.add_argument("--update-task-file", action="store_true", help="同时更新TASK.md文件")
    parser.add_argument("--clis-dir", default="CLIS", help="CLI目录路径")

    args = parser.parse_args()

    assigner = TaskAssigner(args.clis_dir)

    if args.status:
        # 显示状态报告
        assigner.print_status_report()
        return

    if args.suggest:
        # 显示分配建议
        assigner.print_suggestions()
        return

    if args.assign:
        # 分配任务
        if not args.task or not args.title:
            print("❌ 错误: --assign需要同时指定--task和--title")
            parser.print_help()
            sys.exit(1)

        if args.assign not in assigner.cli_list:
            print(f"❌ 错误: CLI '{args.assign}' 不存在")
            print(f"可用的CLI: {', '.join(assigner.cli_list)}")
            sys.exit(1)

        # 创建任务分配通知
        print(f"\n📝 为 {args.assign} CLI分配任务...")
        output_file = assigner.create_task_assignment(
            cli_name=args.assign,
            task_id=args.task,
            task_title=args.title,
            priority=args.priority,
            estimated_hours=args.hours,
            description=args.description,
        )

        print(f"✅ 任务分配通知已创建: {output_file}")

        # 更新TASK.md
        if args.update_task_file:
            print("📝 更新TASK.md文件...")
            success = assigner.update_cli_task_file(
                cli_name=args.assign,
                task_id=args.task,
                task_title=args.title,
                priority=args.priority,
                estimated_hours=args.hours,
            )

            if success:
                print("✅ TASK.md已更新")
            else:
                print("❌ TASK.md更新失败")

        print()
        return

    # 默认显示状态报告
    assigner.print_status_report()


if __name__ == "__main__":
    main()
