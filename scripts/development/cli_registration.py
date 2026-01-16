# scripts/dev/cli_registration.py

"""
CLI报到机制 - 自动角色认领和确认

当CLI启动时，向main报到，main确认角色并分配任务。
"""

import sys
import os
import json
import functools
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class CLIRegistration:
    """CLI报到管理器"""

    def __init__(self):
        self.main_dir = Path("CLIS/main")
        self.registration_file = self.main_dir / "registrations.json"

    def register(self, cli_name, cli_type, capabilities=None):
        """
        CLI报到

        Args:
            cli_name: CLI名称（如: web, api, db, worker1）
            cli_type: CLI类型（main, worker, coordinator）
            capabilities: CLI能力描述（可选）
        """
        registration = {
            'name': cli_name,
            'type': cli_type,
            'capabilities': capabilities or [],
            'registration_time': datetime.now().isoformat(),
            'status': 'pending'
        }

        # 保存报到信息
        registrations = self._load_registrations()
        registrations[cli_name] = registration
        self._save_registrations(registrations)

        # 发送报到消息给main
        self._send_registration_message(registration)

        return registration

    def confirm_registration(self, cli_name, role, assigned_tasks):
        """
        main确认报到并分配角色

        Args:
            cli_name: CLI名称
            role: 分配的角色
            assigned_tasks: 分配的任务ID列表
        """
        registrations = self._load_registrations()

        if cli_name in registrations:
            registrations[cli_name]['status'] = 'confirmed'
            registrations[cli_name]['role'] = role
            registrations[cli_name]['assigned_tasks'] = assigned_tasks
            registrations[cli_name]['confirmation_time'] = datetime.now().isoformat()

            self._save_registrations(registrations)

            # 发送确认消息给CLI
            self._send_confirmation_message(cli_name, role, assigned_tasks)

            return registrations[cli_name]

        return None

    def _load_registrations(self):
        """加载报到信息"""
        if self.registration_file.exists():
            with open(self.registration_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_registrations(self, registrations):
        """保存报到信息"""
        self.registration_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.registration_file, 'w') as f:
            json.dump(registrations, f, indent=2)

    def _send_registration_message(self, registration):
        """发送报到消息给main"""
        message = f"""---
**From**: {registration['name']}
**To**: main
**Type**: NOTIFICATION
**Priority**: HIGH
**Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Subject**: CLI报到请求

**CLI信息**:
- 名称: {registration['name']}
- 类型: {registration['type']}
- 能力: {', '.join(registration['capabilities'])}

**Action Required**:
请确认此CLI的角色并分配初始任务。

此CLI正在等待main的响应...
"""

        mailbox_dir = self.main_dir / "mailbox"
        mailbox_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        message_file = mailbox_dir / f"{registration['name']}_registration_{timestamp}.md"

        with open(message_file, 'w', encoding='utf-8') as f:
            f.write(message)

        print("✅ 已向main发送报到请求")

    def _send_confirmation_message(self, cli_name, role, assigned_tasks):
        """发送确认消息给CLI"""
        cli_dir = Path(f"CLIS/{cli_name}")
        mailbox_dir = cli_dir / "mailbox"
        mailbox_dir.mkdir(parents=True, exist_ok=True)

        message = f"""---
**From**: main
**To**: {cli_name}
**Type**: NOTIFICATION
**Priority**: HIGH
**Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Subject**: 角色确认

**您已被分配角色**: {role}

**初始任务**:
{chr(10).join(f"- {task}" for task in assigned_tasks)}

**下一步**:
1. 查看您的TASK.md: cat CLIS/{cli_name}/TASK.md
2. 查看您的RULES.md: cat CLIS/{cli_name}/RULES.md
3. 开始执行任务！

祝您工作顺利！🚀
"""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        message_file = mailbox_dir / f"main_confirmation_{timestamp}.md"

        with open(message_file, 'w', encoding='utf-8') as f:
            f.write(message)

        print(f"✅ 已向{cli_name}发送角色确认")


def register_as_cli(cli_name, cli_type='worker', capabilities=None):
    """
    CLI报到函数

    Args:
        cli_name: CLI名称
        cli_type: CLI类型（main, worker, coordinator）
        capabilities: CLI能力列表

    Returns:
        registration: 报到信息
    """
    registrar = CLIRegistration()
    return registrar.register(cli_name, cli_type, capabilities)


def confirm_cli_registration(cli_name, role, assigned_tasks):
    """
    main确认CLI报到

    Args:
        cli_name: CLI名称
        role: 分配的角色
        assigned_tasks: 分配的任务列表

    Returns:
        registration: 更新后的报到信息
    """
    registrar = CLIRegistration()
    return registrar.confirm_registration(cli_name, role, assigned_tasks)


# CLI启动时自动报到的装饰器
def auto_register(cli_type='worker', capabilities=None):
    """自动报到装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取CLI名称
            cli_name = kwargs.get('cli_name', 'unknown')

            print(f"📮 {cli_name} 正在向main报到...")

            # 注册CLI
            registration = register_as_cli(cli_name, cli_type, capabilities)

            print(f"✅ {cli_name} 报到成功，等待main确认角色...")

            # 执行原函数
            result = func(*args, **kwargs)

            return result

        return wrapper
    return decorator


# 使用示例
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='CLI报到')
    parser.add_argument('--register', action='store_true', help='CLI报到')
    parser.add_argument('--confirm', action='store_true', help='main确认报到')
    parser.add_argument('--cli', required=True, help='CLI名称')
    parser.add_argument('--type', default='worker', help='CLI类型（main, worker, coordinator）')
    parser.add_argument('--capabilities', help='CLI能力列表（逗号分隔）')
    parser.add_argument('--role', help='分配的角色')
    parser.add_argument('--tasks', help='分配的任务（逗号分隔）')

    args = parser.parse_args()

    if args.register:
        # CLI报到
        capabilities = args.capabilities.split(',') if args.capabilities else []
        register_as_cli(args.cli, args.type, capabilities)

    elif args.confirm:
        # main确认
        tasks = args.tasks.split(',') if args.tasks else []
        confirm_cli_registration(args.cli, args.role, tasks)
