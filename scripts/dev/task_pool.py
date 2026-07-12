# scripts/dev/task_pool.py

"""任务池系统 - 任务发布、查看、认领、更新

支持功能：
1. main发布任务到任务池
2. CLI查看可认领的任务
3. CLI认领任务
4. CLI更新任务进度
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TaskPool:
    """任务池管理器"""

    def __init__(self, clis_dir="CLIS"):
        self.clis_dir = Path(clis_dir)
        self.tasks_pool_file = self.clis_dir / "SHARED" / "TASKS_POOL.md"
        self.tasks_db_file = self.clis_dir / "SHARED" / "tasks.json"

        # 确保目录存在
        self.tasks_pool_file.parent.mkdir(parents=True, exist_ok=True)

    def publish_task(self, task_id, title, description, priority="MEDIUM", skills=None, estimated_hours=None):
        """发布任务到任务池

        Args:
            task_id: 任务ID（如: task-1.1, feature-web-homepage）
            title: 任务标题
            description: 任务描述
            priority: 优先级（HIGH, MEDIUM, LOW）
            skills: 需要的技能列表（如: ['frontend', 'Vue']）
            estimated_hours: 预计工时

        """
        # 加载现有任务
        tasks = self._load_tasks_db()

        # 创建新任务
        task = {
            "task_id": task_id,
            "title": title,
            "description": description,
            "priority": priority,
            "skills": skills or [],
            "estimated_hours": estimated_hours,
            "status": "open",  # open, claimed, completed
            "claimed_by": None,
            "claimed_time": None,
            "published_time": datetime.now().isoformat(),
            "progress": 0,
        }

        tasks[task_id] = task

        # 保存到数据库
        self._save_tasks_db(tasks)

        # 更新TASKS_POOL.md
        self._update_tasks_pool_md(tasks)

        print(f"✅ 任务已发布: {task_id} - {title}")

        return task

    def list_tasks(self, status="open", cli_name=None, skills=None):
        """列出任务

        Args:
            status: 任务状态过滤（open, claimed, completed, all）
            cli_name: CLI名称（只显示该CLI认领的任务）
            skills: 技能过滤（只显示需要这些技能的任务）

        Returns:
            tasks: 任务列表

        """
        tasks = self._load_tasks_db()

        # 过滤任务
        filtered = {}
        for task_id, task in tasks.items():
            # 状态过滤
            if status != "all" and task["status"] != status:
                continue

            # CLI过滤
            if cli_name and task.get("claimed_by") != cli_name:
                continue

            # 技能过滤
            if skills:
                if not any(skill in task.get("skills", []) for skill in skills):
                    continue

            filtered[task_id] = task

        return filtered

    def claim_task(self, task_id, cli_name):
        """认领任务

        Args:
            task_id: 任务ID
            cli_name: CLI名称

        Returns:
            task: 认领的任务信息

        """
        tasks = self._load_tasks_db()

        if task_id not in tasks:
            raise ValueError(f"任务不存在: {task_id}")

        task = tasks[task_id]

        if task["status"] != "open":
            raise ValueError(f"任务不可认领（当前状态: {task['status']}）: {task_id}")

        # 更新任务状态
        task["status"] = "claimed"
        task["claimed_by"] = cli_name
        task["claimed_time"] = datetime.now().isoformat()

        # 保存
        self._save_tasks_db(tasks)
        self._update_tasks_pool_md(tasks)

        print(f"✅ {cli_name} 已认领任务: {task_id} - {task['title']}")

        # 更新CLI的TASK.md
        self._update_cli_task_md(cli_name, task)

        return task

    def update_task_progress(self, task_id, cli_name, progress, status=None):
        """更新任务进度

        Args:
            task_id: 任务ID
            cli_name: CLI名称
            progress: 进度百分比（0-100）
            status: 新状态（claimed, completed）

        """
        tasks = self._load_tasks_db()

        if task_id not in tasks:
            raise ValueError(f"任务不存在: {task_id}")

        task = tasks[task_id]

        if task.get("claimed_by") != cli_name:
            raise ValueError(f"此任务未由该CLI认领: {task_id}")

        # 更新进度
        task["progress"] = progress

        if status:
            task["status"] = status

        if status == "completed":
            task["completed_time"] = datetime.now().isoformat()

        # 保存
        self._save_tasks_db(tasks)
        self._update_tasks_pool_md(tasks)

        print(f"✅ 任务进度已更新: {task_id} - {task['title']} ({progress}%)")

        # 更新CLI的TASK.md
        self._update_cli_task_md(cli_name, task)

        return task

    def release_task(self, task_id, cli_name):
        """释放任务（取消认领）

        Args:
            task_id: 任务ID
            cli_name: CLI名称

        """
        tasks = self._load_tasks_db()

        if task_id not in tasks:
            raise ValueError(f"任务不存在: {task_id}")

        task = tasks[task_id]

        if task.get("claimed_by") != cli_name:
            raise ValueError(f"此任务未由该CLI认领: {task_id}")

        # 重置任务状态
        task["status"] = "open"
        task["claimed_by"] = None
        task["claimed_time"] = None
        task["progress"] = 0

        # 保存
        self._save_tasks_db(tasks)
        self._update_tasks_pool_md(tasks)

        print(f"✅ 任务已释放: {task_id} - {task['title']}")

        return task

    def _load_tasks_db(self):
        """加载任务数据库"""
        if self.tasks_db_file.exists():
            with open(self.tasks_db_file, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_tasks_db(self, tasks):
        """保存任务数据库"""
        with open(self.tasks_db_file, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)

    def _update_tasks_pool_md(self, tasks):
        """更新TASKS_POOL.md文件"""
        content = f"""# 任务池

**Updated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 统计信息

- 总任务数: {len(tasks)}
- 待认领: {len([t for t in tasks.values() if t["status"] == "open"])}
- 进行中: {len([t for t in tasks.values() if t["status"] == "claimed"])}
- 已完成: {len([t for t in tasks.values() if t["status"] == "completed"])}

---

## 待认领任务

"""

        # 按优先级排序
        open_tasks = [t for t in tasks.values() if t["status"] == "open"]
        open_tasks.sort(key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}.get(x["priority"], 3))

        for task in open_tasks:
            priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(task["priority"], "⚪")
            skills_str = ", ".join(task["skills"]) if task["skills"] else "无特殊要求"
            hours_str = f"{task['estimated_hours']}小时" if task["estimated_hours"] else "未估计"

            content += f"""
### {priority_emoji} {task["task_id"]}: {task["title"]}

**任务ID**: `{task["task_id"]}`
**优先级**: {task["priority"]}
**需要技能**: {skills_str}
**预计工时**: {hours_str}
**发布时间**: {task["published_time"]}

**任务描述**:
{task["description"]}

**认领命令**:
```bash
python scripts/dev/task_pool.py --claim --task={task["task_id"]} --cli=YOUR_CLI_NAME
```

---

"""

        # 添加进行中和已完成任务
        claimed_tasks = [t for t in tasks.values() if t["status"] == "claimed"]
        completed_tasks = [t for t in tasks.values() if t["status"] == "completed"]

        if claimed_tasks:
            content += "\n## 进行中任务\n\n"
            for task in claimed_tasks:
                content += f"- **{task['task_id']}**: {task['title']} (认领者: {task['claimed_by']}, 进度: {task['progress']}%)\n"

        if completed_tasks:
            content += "\n## 已完成任务\n\n"
            for task in completed_tasks:
                content += f"- ~~**{task['task_id']}**: {task['title']}~~ (完成者: {task['claimed_by']}, 完成时间: {task['completed_time']})\n"

        # 写入文件
        with open(self.tasks_pool_file, "w", encoding="utf-8") as f:
            f.write(content)

    def _update_cli_task_md(self, cli_name, task):
        """更新CLI的TASK.md文件"""
        task_file = self.clis_dir / cli_name / "TASK.md"

        if not task_file.exists():
            return

        # 读取现有内容
        content = task_file.read_text(encoding="utf-8")

        # 检查是否已有该任务
        task_pattern = rf"- \[ \] {re.escape(task['task_id'])}:.*"

        if re.search(task_pattern, content):
            # 更新现有任务
            new_task = f"- [{task['task_id']}] {task['title']} - {task['description']} (进度: {task['progress']}%)"
            content = re.sub(task_pattern, new_task, content)
        # 添加新任务
        elif "## 当前任务" in content:
            # 在当前任务部分添加
            section_end = content.find("\n\n", content.find("## 当前任务"))
            if section_end == -1:
                section_end = len(content)

            new_task = f"\n- [{task['task_id']}] {task['title']} - {task['description']} (进度: {task['progress']}%)"
            content = content[:section_end] + new_task + content[section_end:]

        # 写回文件
        task_file.write_text(content, encoding="utf-8")


def print_task_table(tasks):
    """打印任务表格"""
    if not tasks:
        print("📭 没有符合条件的任务")
        return

    print(f"\n找到 {len(tasks)} 个任务:\n")

    for task_id, task in tasks.items():
        status_emoji = {
            "open": "📋",
            "claimed": "🔧",
            "completed": "✅",
        }.get(task["status"], "❓")

        priority_emoji = {
            "HIGH": "🔴",
            "MEDIUM": "🟡",
            "LOW": "🟢",
        }.get(task["priority"], "⚪")

        claimed_by = task.get("claimed_by") or "待认领"
        skills = ", ".join(task["skills"]) if task["skills"] else "无"
        progress = f"{task['progress']}%" if "progress" in task else "0%"

        print(f"{status_emoji} {priority_emoji} **{task_id}**: {task['title']}")
        print(f"   状态: {task['status']} | 认领者: {claimed_by} | 进度: {progress}")
        print(f"   技能: {skills}")
        print(
            f"   描述: {task['description'][:80]}..."
            if len(task["description"]) > 80
            else f"   描述: {task['description']}"
        )
        print()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="任务池管理系统")
    parser.add_argument("--publish", action="store_true", help="发布任务")
    parser.add_argument("--list", action="store_true", help="查看任务")
    parser.add_argument("--claim", action="store_true", help="认领任务")
    parser.add_argument("--update", action="store_true", help="更新任务进度")
    parser.add_argument("--release", action="store_true", help="释放任务")
    parser.add_argument("--task", help="任务ID")
    parser.add_argument("--cli", help="CLI名称")
    parser.add_argument("--title", help="任务标题")
    parser.add_argument("--description", help="任务描述")
    parser.add_argument("--priority", default="MEDIUM", help="优先级（HIGH, MEDIUM, LOW）")
    parser.add_argument("--skills", help="需要的技能（逗号分隔）")
    parser.add_argument("--hours", type=int, help="预计工时")
    parser.add_argument("--progress", type=int, help="进度百分比（0-100）")
    parser.add_argument("--status", help="新状态（claimed, completed）")
    parser.add_argument("--clis-dir", default="CLIS", help="CLI目录")

    args = parser.parse_args()

    pool = TaskPool(args.clis_dir)

    if args.publish:
        # 发布任务
        if not args.task or not args.title or not args.description:
            print("❌ 发布任务需要: --task, --title, --description")
            return

        skills = args.skills.split(",") if args.skills else None
        pool.publish_task(
            task_id=args.task,
            title=args.title,
            description=args.description,
            priority=args.priority,
            skills=skills,
            estimated_hours=args.hours,
        )

    elif args.list:
        # 查看任务
        status = "all"
        cli_name = args.cli or None
        skills = args.skills.split(",") if args.skills else None

        tasks = pool.list_tasks(status=status, cli_name=cli_name, skills=skills)
        print_task_table(tasks)

    elif args.claim:
        # 认领任务
        if not args.task or not args.cli:
            print("❌ 认领任务需要: --task, --cli")
            return

        try:
            task = pool.claim_task(args.task, args.cli)
            print("\n任务详情:")
            print(f"  标题: {task['title']}")
            print(f"  描述: {task['description']}")
            print(f"  技能: {', '.join(task['skills'])}")
            print(f"  预计工时: {task['estimated_hours']}小时" if task["estimated_hours"] else "")
        except ValueError as e:
            print(f"❌ {e}")

    elif args.update:
        # 更新进度
        if not args.task or not args.cli:
            print("❌ 更新进度需要: --task, --cli")
            return

        try:
            task = pool.update_task_progress(
                task_id=args.task,
                cli_name=args.cli,
                progress=args.progress or 0,
                status=args.status,
            )
            print(f"\n任务 {args.task} 进度已更新到 {args.progress}%")
        except ValueError as e:
            print(f"❌ {e}")

    elif args.release:
        # 释放任务
        if not args.task or not args.cli:
            print("❌ 释放任务需要: --task, --cli")
            return

        try:
            pool.release_task(args.task, args.cli)
        except ValueError as e:
            print(f"❌ {e}")

    else:
        # 默认显示所有待认领任务
        print("📋 任务池 - 待认领任务\n")
        tasks = pool.list_tasks(status="open")
        print_task_table(tasks)
        print("\n💡 使用 --help 查看更多命令")


if __name__ == "__main__":
    main()
