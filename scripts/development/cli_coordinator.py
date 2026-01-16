# scripts/dev/cli_coordinator.py

"""
CLI协调器 - 基础类
"""

import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class CLICoordinator:
    """CLI协调器基类"""

    def __init__(self, clis_dir="CLIS"):
        self.clis_dir = Path(clis_dir)
        self.clis_dir.mkdir(parents=True, exist_ok=True)

    def scan_all_status(self):
        """扫描所有CLI状态"""
        statuses = {}

        for cli_dir in self.clis_dir.iterdir():
            if cli_dir.is_dir() and cli_dir.name not in ['locks', 'SHARED', 'templates', 'main']:
                status_file = cli_dir / "STATUS.md"
                if status_file.exists():
                    statuses[cli_dir.name] = self._parse_status(status_file)

        return statuses

    def _parse_status(self, status_file):
        """解析STATUS.md文件"""
        content = status_file.read_text()

        # 解析状态字段
        status = {
            'name': status_file.parent.name,
            'state': 'unknown',
            'current_task': None,
            'last_update': None,
            'blocked_on': None,
            'waiting_time': 0,
            'error': None
        }

        for line in content.split('\n'):
            if line.startswith('**State**:'):
                status['state'] = line.split(':', 1)[1].strip().split()[0]
            elif line.startswith('**Current Task**:'):
                status['current_task'] = line.split(':', 1)[1].strip()
            elif line.startswith('**last_update**:'):
                status['last_update'] = line.split(':', 1)[1].strip()
            elif line.startswith('**Blocked On**:'):
                status['blocked_on'] = line.split(':', 1)[1].strip()
            elif line.startswith('**error**:'):
                status['error'] = line.split(':', 1)[1].strip()

        # 计算等待时间
        if status['last_update']:
            try:
                last_update = datetime.strptime(status['last_update'], '%Y-%m-%d %H:%M:%S')
                waiting_time = (datetime.now() - last_update).total_seconds() / 60
                status['waiting_time'] = waiting_time
            except:
                pass

        return status

    def get_cli_info(self, cli_name):
        """获取指定CLI的信息"""
        cli_dir = self.clis_dir / cli_name

        if not cli_dir.exists():
            return None

        info = {
            'name': cli_name,
            'exists': True,
            'has_task': (cli_dir / "TASK.md").exists(),
            'has_rules': (cli_dir / "RULES.md").exists(),
            'has_status': (cli_dir / "STATUS.md").exists(),
            'has_report': (cli_dir / "REPORT.md").exists(),
            'has_mailbox': (cli_dir / "mailbox").exists(),
            'has_archive': (cli_dir / "archive").exists(),
            'has_config': (cli_dir / ".cli_config").exists()
        }

        # 解析状态
        status_file = cli_dir / "STATUS.md"
        if status_file.exists():
            info['status'] = self._parse_status(status_file)
        else:
            info['status'] = None

        return info

    def send_message(self, to_cli, message):
        """发送消息到指定CLI"""
        mailbox_dir = self.clis_dir / to_cli / "mailbox"
        mailbox_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        message_file = mailbox_dir / f"main_{timestamp}.md"

        with open(message_file, 'w', encoding='utf-8') as f:
            f.write(message)

        return True, f"消息已发送到 {to_cli}"


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='CLI协调器')
    parser.add_argument('--scan', action='store_true', help='扫描所有CLI状态')
    parser.add_argument('--info', help='获取指定CLI信息')
    parser.add_argument('--clis-dir', default='CLIS', help='CLI目录')

    args = parser.parse_args()

    coordinator = CLICoordinator(args.clis_dir)

    if args.scan:
        statuses = coordinator.scan_all_status()

        print(f"\n扫描到 {len(statuses)} 个CLI:\n")
        for cli_name, status in statuses.items():
            print(f"CLI: {cli_name}")
            print(f"  状态: {status['state']}")
            print(f"  当前任务: {status['current_task'] or '无'}")
            print(f"  最后更新: {status['last_update'] or '未知'}")
            print(f"  等待时间: {status['waiting_time']:.0f}分钟")
            print()

    elif args.info:
        info = coordinator.get_cli_info(args.info)

        if info:
            print(f"\nCLI信息: {info['name']}\n")
            print(f"  存在: {info['exists']}")
            print(f"  TASK.md: {'✅' if info['has_task'] else '❌'}")
            print(f"  RULES.md: {'✅' if info['has_rules'] else '❌'}")
            print(f"  STATUS.md: {'✅' if info['has_status'] else '❌'}")
            print(f"  REPORT.md: {'✅' if info['has_report'] else '❌'}")
            print(f"  mailbox: {'✅' if info['has_mailbox'] else '❌'}")
            print(f"  archive: {'✅' if info['has_archive'] else '❌'}")
            print(f"  .cli_config: {'✅' if info['has_config'] else '❌'}")

            if info['status']:
                print(f"\n  状态: {info['status']['state']}")
                print(f"  任务: {info['status']['current_task'] or '无'}")
        else:
            print(f"❌ CLI '{args.info}' 不存在")
