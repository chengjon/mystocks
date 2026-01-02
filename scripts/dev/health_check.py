#!/usr/bin/env python3
"""
CLI健康检查脚本

检查所有CLI的健康状态，包括：
- CLI状态文件（STATUS.md）更新情况
- Mailbox监听器进程运行状态
- 资源使用情况（CPU、内存）
- 任务阻塞情况
- 锁文件状态

Usage:
    # 检查单个CLI
    python scripts/dev/health_check.py --cli web

    # 检查所有CLI
    python scripts/dev/health_check.py --all

    # 生成HEALTH.md报告
    python scripts/dev/health_check.py --generate-report
"""

import os
import sys
import psutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class CLIHealthChecker:
    """CLI健康检查器"""

    def __init__(self, clis_dir: str = "CLIS"):
        self.clis_dir = Path(clis_dir)
        self.cli_list = self._discover_clis()

    def _discover_clis(self) -> List[str]:
        """发现所有CLI目录"""
        clis = []
        for item in self.clis_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                # 检查是否包含必要文件
                if (item / "STATUS.md").exists():
                    clis.append(item.name)
        return sorted(clis)

    def check_cli_status(self, cli_name: str) -> Dict:
        """
        检查CLI状态文件

        Args:
            cli_name: CLI名称

        Returns:
            包含状态信息的字典
        """
        status_file = self.clis_dir / cli_name / "STATUS.md"

        if not status_file.exists():
            return {
                "status": "❌ Missing",
                "last_update": None,
                "state": "Unknown",
                "current_task": None,
                "idle_time_minutes": None,
                "issues": ["STATUS.md文件不存在"]
            }

        # 读取STATUS.md内容
        content = status_file.read_text(encoding='utf-8')

        # 解析状态
        last_update = None
        state = "Unknown"
        current_task = None
        blocked_on = None
        issues = []

        for line in content.split('\n'):
            if 'Updated' in line and ':' in line:
                try:
                    time_str = line.split(':', 1)[1].strip()
                    last_update = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                except:
                    pass
            elif line.startswith('**State**'):
                if '🟢 Active' in line or 'Active' in line:
                    state = "Active"
                elif '🟡 Idle' in line or 'Idle' in line:
                    state = "Idle"
                elif '🔴 Blocked' in line or 'Blocked' in line:
                    state = "Blocked"
                elif '🟢 Done' in line or 'Done' in line:
                    state = "Done"
            elif '**Current Task**' in line:
                current_task = line.split(':', 1)[1].strip() if ':' in line else None
            elif '**Blocked On**' in line:
                blocked_line = line.split(':', 1)[1].strip() if ':' in line else ""
                if blocked_line and blocked_line.lower() not in ['无', 'none', 'n/a']:
                    blocked_on = blocked_line

        # 计算空闲时间
        idle_time = None
        if last_update:
            idle_time = (datetime.now() - last_update).total_seconds() / 60
            if idle_time > 30:
                issues.append(f"STATUS.md已{idle_time:.0f}分钟未更新")

        # 构建状态
        status_icon = "🟢" if state == "Active" else "🟡" if state == "Idle" else "🔴"
        return {
            "status": f"{status_icon} {state}",
            "last_update": last_update,
            "state": state,
            "current_task": current_task,
            "blocked_on": blocked_on,
            "idle_time_minutes": idle_time,
            "issues": issues
        }

    def check_cli_process(self, cli_name: str) -> Dict:
        """
        检查CLI相关进程

        Args:
            cli_name: CLI名称

        Returns:
            包含进程信息的字典
        """
        processes = []

        try:
            # 查找mailbox watcher进程
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'memory_info']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and any(f'--cli {cli_name}' in str(cmd) for cmd in cmdline):
                        processes.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "type": "mailbox_watcher",
                            "memory_mb": proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0,
                            "uptime_hours": (datetime.now().timestamp() - proc.info['create_time']) / 3600
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            return {
                "watcher_running": False,
                "processes": [],
                "issues": [f"进程检查失败: {str(e)}"]
            }

        # 检查协调器进程（仅main CLI）
        coordinator_pid_file = self.clis_dir / cli_name / ".coordinator_pid"
        if coordinator_pid_file.exists():
            try:
                coordinator_pid = int(coordinator_pid_file.read_text().strip())
                if psutil.pid_exists(coordinator_pid):
                    proc = psutil.Process(coordinator_pid)
                    processes.append({
                        "pid": coordinator_pid,
                        "name": proc.name(),
                        "type": "coordinator",
                        "memory_mb": proc.memory_info().rss / 1024 / 1024,
                        "uptime_hours": (datetime.now().timestamp() - proc.create_time()) / 3600
                    })
            except:
                pass

        issues = []
        if not processes:
            issues.append("未发现运行中的进程")

        return {
            "watcher_running": len([p for p in processes if p['type'] == 'mailbox_watcher']) > 0,
            "coordinator_running": len([p for p in processes if p['type'] == 'coordinator']) > 0,
            "processes": processes,
            "process_count": len(processes),
            "issues": issues
        }

    def check_cli_resources(self, cli_name: str) -> Dict:
        """
        检查CLI资源使用情况

        Args:
            cli_name: CLI名称

        Returns:
            包含资源使用信息的字典
        """
        cli_dir = self.clis_dir / cli_name

        # 检查文件数量
        file_counts = {}
        for subdir in ['mailbox', 'archive', 'checkpoints']:
            subdir_path = cli_dir / subdir
            if subdir_path.exists():
                files = list(subdir_path.glob('*'))
                file_counts[subdir] = len(files)

        # 检查锁文件
        locks_dir = self.clis_dir / "locks"
        cli_locks = []
        if locks_dir.exists():
            for lock_file in locks_dir.glob(f"{cli_name}_*.lock"):
                try:
                    lock_content = lock_file.read_text().strip()
                    cli_locks.append({
                        "file": lock_file.name,
                        "holder": lock_content.split('\n')[0] if lock_content else "Unknown",
                        "age_minutes": (datetime.now().timestamp() - lock_file.stat().st_mtime) / 60
                    })
                except:
                    pass

        issues = []
        if file_counts.get('archive', 0) > 50:
            issues.append(f"archive目录包含{file_counts['archive']}个文件，建议清理")

        if cli_locks:
            for lock in cli_locks:
                if lock['age_minutes'] > 60:
                    issues.append(f"锁文件{lock['file']}已持有{lock['age_minutes']:.0f}分钟")

        return {
            "file_counts": file_counts,
            "locks": cli_locks,
            "lock_count": len(cli_locks),
            "issues": issues
        }

    def generate_health_report(self) -> str:
        """
        生成完整的健康检查报告

        Returns:
            Markdown格式的健康报告
        """
        report_lines = [
            "# CLI健康状态报告",
            "",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**检查CLI数量**: {len(self.cli_list)}",
            "",
            "---",
            "",
            "## 📊 总体状态",
            ""
        ]

        # 汇总统计
        total_issues = 0
        active_clis = 0
        blocked_clis = 0

        for cli in self.cli_list:
            status_info = self.check_cli_status(cli)
            total_issues += len(status_info['issues'])
            if status_info['state'] == 'Active':
                active_clis += 1
            elif status_info['state'] == 'Blocked':
                blocked_clis += 1

        report_lines.extend([
            f"- **总CLI数**: {len(self.cli_list)}",
            f"- **活跃CLI**: {active_clis}",
            f"- **阻塞CLI**: {blocked_clis}",
            f"- **发现问题**: {total_issues}",
            "",
            "---",
            "",
            "## 📋 各CLI详细状态",
            ""
        ])

        # 各CLI详细状态
        for cli in self.cli_list:
            report_lines.append(f"### {cli.upper()} CLI")
            report_lines.append("")

            # 状态信息
            status_info = self.check_cli_status(cli)
            report_lines.append(f"**状态**: {status_info['status']}")
            if status_info['last_update']:
                report_lines.append(f"**最后更新**: {status_info['last_update'].strftime('%Y-%m-%d %H:%M:%S')}")
                if status_info['idle_time_minutes']:
                    report_lines.append(f"**空闲时间**: {status_info['idle_time_minutes']:.1f}分钟")
            if status_info['current_task']:
                report_lines.append(f"**当前任务**: {status_info['current_task']}")
            if status_info['blocked_on']:
                report_lines.append(f"**阻塞原因**: {status_info['blocked_on']}")

            # 进程信息
            process_info = self.check_cli_process(cli)
            report_lines.append(f"**进程数**: {process_info['process_count']}")
            if process_info['processes']:
                report_lines.append("**进程列表**:")
                for proc in process_info['processes']:
                    report_lines.append(f"  - PID {proc['pid']} ({proc['type']}): "
                                     f"内存{proc['memory_mb']:.1f}MB, "
                                     f"运行{proc['uptime_hours']:.1f}小时")

            # 资源信息
            resource_info = self.check_cli_resources(cli)
            if resource_info['file_counts']:
                report_lines.append("**文件统计**:")
                for subdir, count in resource_info['file_counts'].items():
                    report_lines.append(f"  - {subdir}/: {count}个文件")
            if resource_info['lock_count'] > 0:
                report_lines.append(f"**持有锁**: {resource_info['lock_count']}个")

            # 问题列表
            all_issues = (status_info['issues'] +
                         process_info['issues'] +
                         resource_info['issues'])

            if all_issues:
                report_lines.append("")
                report_lines.append("**⚠️ 发现的问题**:")
                for issue in all_issues:
                    report_lines.append(f"  - {issue}")
            else:
                report_lines.append("")
                report_lines.append("**✅ 无问题**")

            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")

        # 建议
        report_lines.extend([
            "## 💡 建议",
            ""
        ])

        if total_issues > 0:
            report_lines.append("### 🔴 需要立即处理")
            report_lines.append("")
            for cli in self.cli_list:
                status_info = self.check_cli_status(cli)
                if status_info['state'] == 'Blocked':
                    report_lines.append(f"- **{cli} CLI**: 处于阻塞状态，请检查并解决问题")
            report_lines.append("")

        if any(info['idle_time_minutes'] and info['idle_time_minutes'] > 30
               for info in [self.check_cli_status(cli) for cli in self.cli_list]):
            report_lines.append("### 🟡 需要关注")
            report_lines.append("")
            for cli in self.cli_list:
                status_info = self.check_cli_status(cli)
                if status_info['idle_time_minutes'] and status_info['idle_time_minutes'] > 30:
                    report_lines.append(f"- **{cli} CLI**: STATUS.md {status_info['idle_time_minutes']:.0f}分钟未更新")
            report_lines.append("")

        report_lines.append("---")
        report_lines.append("")
        report_lines.append(f"**报告生成**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("**脚本**: `scripts/dev/health_check.py`")

        return '\n'.join(report_lines)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='CLI健康检查工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 检查所有CLI
  python scripts/dev/health_check.py --all

  # 检查特定CLI
  python scripts/dev/health_check.py --cli web

  # 生成HEALTH.md报告
  python scripts/dev/health_check.py --generate-report

  # 检查并显示问题
  python scripts/dev/health_check.py --all --verbose
        """
    )

    parser.add_argument('--cli', type=str, help='检查指定CLI')
    parser.add_argument('--all', action='store_true', help='检查所有CLI')
    parser.add_argument('--generate-report', action='store_true', help='生成HEALTH.md报告')
    parser.add_argument('--clis-dir', default='CLIS', help='CLI目录路径')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细信息')

    args = parser.parse_args()

    checker = CLIHealthChecker(args.clis_dir)

    if args.generate_report:
        # 生成HEALTH.md报告
        print("📊 正在生成健康检查报告...")
        report = checker.generate_health_report()

        output_file = Path(args.clis_dir) / "main" / "HEALTH.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(report, encoding='utf-8')

        print(f"✅ 健康报告已生成: {output_file}")
        return

    if args.cli:
        # 检查单个CLI
        if args.cli not in checker.cli_list:
            print(f"❌ 错误: CLI '{args.cli}' 不存在")
            print(f"可用的CLI: {', '.join(checker.cli_list)}")
            sys.exit(1)

        print(f"\n{'='*60}")
        print(f"📋 {args.cli.upper()} CLI 健康检查")
        print(f"{'='*60}\n")

        status = checker.check_cli_status(args.cli)
        process = checker.check_cli_process(args.cli)
        resources = checker.check_cli_resources(args.cli)

        print(f"状态: {status['status']}")
        if status['last_update']:
            print(f"最后更新: {status['last_update'].strftime('%Y-%m-%d %H:%M:%S')}")
        if status['current_task']:
            print(f"当前任务: {status['current_task']}")

        print(f"\n进程: {process['process_count']}个")
        if args.verbose and process['processes']:
            for proc in process['processes']:
                print(f"  - PID {proc['pid']} ({proc['type']}): "
                      f"内存{proc['memory_mb']:.1f}MB")

        all_issues = status['issues'] + process['issues'] + resources['issues']
        if all_issues:
            print(f"\n⚠️  发现 {len(all_issues)} 个问题:")
            for issue in all_issues:
                print(f"  - {issue}")
        else:
            print("\n✅ 无问题")

    elif args.all:
        # 检查所有CLI
        print(f"\n{'='*60}")
        print(f"📊 所有CLI健康检查")
        print(f"{'='*60}\n")

        for cli in checker.cli_list:
            status = checker.check_cli_status(cli)
            process = checker.check_cli_process(cli)

            status_symbol = "✅" if not status['issues'] and not process['issues'] else "⚠️"
            print(f"{status_symbol} {cli:10s} | {status['status']:15s} | "
                  f"进程: {process['process_count']}个 | "
                  f"任务: {status['current_task'] or '无'}")

            if args.verbose:
                all_issues = status['issues'] + process['issues']
                if all_issues:
                    for issue in all_issues:
                        print(f"     - {issue}")

        print()

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
