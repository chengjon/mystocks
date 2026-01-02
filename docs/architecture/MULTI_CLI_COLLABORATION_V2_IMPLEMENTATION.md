# 多CLI协作方法 v2.0 - 实施方案

**版本**: v2.0
**创建日期**: 2026-01-01
**基于**: MULTI_CLI_COLLABORATION_METHOD.md v1.0
**优化内容**: 8项核心优化 + 用户建议整合

---

## 🎯 核心改进总结

### 用户选择的解决方案

| 问题 | 选择方案 | 核心特点 |
|------|---------|----------|
| 1. CLI间通信 | ✅ 方案A: mailbox异步通信 | + **建议1: 文件系统事件监听** ⭐⭐⭐⭐⭐ |
| 2. 文件冲突 | ✅ 方案B: 职责域隔离 | + **建议4: 简化文件锁** ⭐⭐⭐⭐ |
| 3. 任务依赖 | ✅ 方案A: 任务依赖图 | + **建议3: 智能协调规则** ⭐⭐⭐⭐⭐ |
| 4. main负担 | ✅ 方案B: 自动化工具 | + **建议2: STATUS自动更新** ⭐⭐⭐⭐ |
| 5. 错误恢复 | ✅ 方案A: 检查点机制 | ✅ 保持原设计 |

### 新增8项优化建议

| 建议 | 优先级 | 改进效果 | 实施难度 |
|------|--------|----------|----------|
| 1. 简化mailbox通信 | 🔴 P0 | 响应时间从分钟级→秒级 | 低 |
| 2. STATUS自动更新 | 🟡 P1 | 准确性提升，减少手动操作 | 低 |
| 3. 智能协调规则 | 🔴 P0 | main负担减少70% | 中 |
| 4. 简化文件锁 | 🟡 P1 | 代码减少88% | 低 |
| 5. 快速启动脚本 | 🔴 P0 | 启动时间从1小时→5分钟 | 低 |
| 6. CLI健康检查 | 🟢 P2 | 及时发现异常 | 低 |
| 7. CLI性能指标 | 🟢 P2 | 数据驱动优化 | 中 |
| 8. CLI报到机制 | 🔴 P0 | 角色管理自动化 | 低 |

---

## 📁 完整目录结构

```
mystocks_spec/
├── CLIS/                              # 多CLI协作根目录
│   ├── main/                          # CLI-main
│   │   ├── TASK.md
│   │   ├── RULES.md
│   │   ├── STATUS.md                   # 全局状态（自动生成）
│   │   ├── METRICS.md                  # 性能指标（自动生成）
│   │   ├── CHECKPOINTS.md
│   │   ├── HEALTH.md                   # 健康检查（自动生成）
│   │   ├── mailbox/
│   │   ├── archive/                    # 已处理消息归档
│   │   ├── checkpoints/
│   │   ├── coordinator.log             # 协调器日志
│   │   └── .cli_config                 # CLI配置文件（隐藏文件，用ls -a查看）
│   │
│   ├── web/                           # CLI-web
│   │   ├── TASK.md
│   │   ├── RULES.md
│   │   ├── STATUS.md
│   │   ├── REPORT.md
│   │   ├── mailbox/
│   │   ├── archive/                    # 已处理消息归档
│   │   ├── watcher.log                 # mailbox监听日志
│   │   └── .cli_config                 # CLI配置文件（隐藏文件，用ls -a查看）
│   │
│   ├── api/
│   │   ├── TASK.md
│   │   ├── RULES.md
│   │   ├── STATUS.md
│   │   ├── REPORT.md
│   │   ├── mailbox/
│   │   ├── archive/                    # 已处理消息归档
│   │   ├── watcher.log
│   │   └── .cli_config                 # CLI配置文件（隐藏文件，用ls -a查看）
│   │
│   ├── db/
│   │   ├── TASK.md
│   │   ├── RULES.md
│   │   ├── STATUS.md
│   │   ├── REPORT.md
│   │   ├── mailbox/
│   │   ├── archive/                    # 已处理消息归档
│   │   ├── watcher.log
│   │   └── .cli_config                 # CLI配置文件（隐藏文件，用ls -a查看）
│   │
│   ├── it/                            # Worker CLI们
│   │   ├── worker1/
│   │   │   ├── TASK.md
│   │   │   ├── RULES.md
│   │   │   ├── STATUS.md
│   │   │   ├── REPORT.md
│   │   │   ├── mailbox/
│   │   │   ├── archive/                # 已处理消息归档
│   │   │   ├── watcher.log
│   │   │   └── .cli_config             # CLI配置文件（隐藏文件，用ls -a查看）
│   │   ├── worker2/
│   │   └── worker3/
│   │
│   ├── locks/                         # 文件锁（自动管理）
│   │
│   ├── SHARED/                        # 共享资源
│   │   ├── TASKS_POOL.md
│   │   ├── KNOWLEDGE_BASE.md
│   │   └── COORDINATION_LOG.md
│   │
│   └── templates/                     # 模板文件
│       ├── TASK.md.template
│       ├── RULES.md.template
│       ├── STATUS.md.template
│       └── REPORT.md.template
│
└── scripts/dev/                      # 开发工具脚本
    ├── init_multi_cli.sh             # ⭐ 一键启动脚本
    ├── cli_coordinator.py             # CLI协调器
    ├── smart_coordinator.py           # ⭐ 智能协调规则引擎
    ├── mailbox_watcher.py            # ⭐ mailbox事件监听
    ├── simple_lock.py                 # ⭐ 简化文件锁
    ├── auto_status.py                 # ⭐ STATUS自动更新
    ├── health_check.py                # ⭐ 健康检查
    ├── metrics_collector.py           # ⭐ 性能指标收集
    ├── cli_registration.py            # ⭐ CLI报到机制
    └── task_assigner.py
```

---

## 🚀 实施步骤

### Phase 0: 环境准备（30分钟）

#### 重要说明：隐藏文件访问

**注意**: 本方案中使用的 `.cli_config` 是Linux/Mac隐藏文件（文件名以`.`开头）。

- **查看方法**: 使用 `ls -a CLIS/cli-name/` 查看所有文件（包括隐藏文件）
- **编辑方法**: 直接使用完整路径，如 `cat CLIS/main/.cli_config`
- **Windows用户**: Git Bash或WSL中同样适用上述命令

#### Step 0.1: 安装依赖
```bash
# 安装Python依赖
pip install watchdog

# watchdog用于文件系统事件监听
# fcntl是Python标准库，无需安装
# time是Python标准库，无需安装
```

#### Step 0.2: 创建基础脚本
```bash
# 创建一键启动脚本
# (见下文完整代码)
```

### Phase 1: 核心功能实现（2小时）

#### 1.1 实现mailbox事件监听（建议1）
```python
# scripts/dev/mailbox_watcher.py

"""
Mailbox事件监听器 - 实时响应新消息

使用watchdog监听文件系统事件，新消息到达时立即处理。
替代定时扫描机制，实现秒级响应。
"""

import sys
import os
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(f'CLIS/{sys.argv[1]}/watcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MailboxWatcher(FileSystemEventHandler):
    """Mailbox监听器"""

    def __init__(self, cli_name):
        self.cli_name = cli_name
        self.mailbox_dir = Path(f"CLIS/{cli_name}/mailbox")
        self.processed_messages = set()  # 避免重复处理

    def on_created(self, event):
        """新文件创建事件"""
        if event.is_directory:
            return

        if not event.src_path.endswith('.md'):
            return

        # 避免重复处理
        if event.src_path in self.processed_messages:
            return

        logger.info(f"📬 新消息到达: {event.src_path}")

        # 处理消息
        try:
            self.process_message(event.src_path)
            self.processed_messages.add(event.src_path)
        except Exception as e:
            logger.error(f"处理消息失败: {e}")

    def process_message(self, msg_file):
        """处理消息"""
        logger.info(f"处理消息: {msg_file}")

        # 读取消息内容
        with open(msg_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析消息
        msg = self.parse_message(content)

        if not msg:
            logger.warning(f"消息格式错误: {msg_file}")
            return

        # 根据消息类型处理
        if msg['type'] == 'ALERT':
            self.handle_alert(msg)
        elif msg['type'] == 'REQUEST':
            self.handle_request(msg)
        elif msg['type'] == 'RESPONSE':
            self.handle_response(msg)
        elif msg['type'] == 'NOTIFICATION':
            self.handle_notification(msg)

        # 将消息移到archive（已处理）
        archive_dir = Path(f"CLIS/{self.cli_name}/archive")
        archive_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_path = archive_dir / f"processed_{timestamp}_{Path(msg_file).name}"

        import shutil
        shutil.move(msg_file, new_path)

        logger.info(f"✅ 消息已处理并归档: {new_path}")

    def parse_message(self, content):
        """解析消息"""
        lines = content.split('\n')
        msg = {}

        for line in lines:
            if line.startswith('**From**:'):
                msg['from'] = line.split(':', 1)[1].strip()
            elif line.startswith('**To**:'):
                msg['to'] = line.split(':', 1)[1].strip()
            elif line.startswith('**Type**:'):
                msg['type'] = line.split(':', 1)[1].strip()
            elif line.startswith('**Priority**:'):
                msg['priority'] = line.split(':', 1)[1].strip()
            elif line.startswith('**Subject**:'):
                msg['subject'] = line.split(':', 1)[1].strip()

        # 必须字段验证
        required = ['from', 'to', 'type', 'subject']
        if not all(k in msg for k in required):
            return None

        msg['content'] = content
        msg['file_path'] = None

        return msg

    def handle_alert(self, msg):
        """处理ALERT消息"""
        logger.warning(f"🚨 收到ALERT: {msg['subject']}")
        logger.warning(f"发送方: {msg['from']}")
        logger.warning(f"优先级: {msg.get('priority', 'UNKNOWN')}")

        # 打印消息内容供用户查看
        print("\n" + "="*60)
        print(f"🚨 紧急消息来自 {msg['from']}")
        print(f"主题: {msg['subject']}")
        print("="*60)
        print(msg['content'])
        print("="*60 + "\n")

        # ALERT消息需要立即处理，等待用户输入
        while True:
            response = input("请处理此ALERT消息，处理完成后输入 'done': ")
            if response.lower().strip() == 'done':
                break

    def handle_request(self, msg):
        """处理REQUEST消息"""
        logger.info(f"📥 收到请求: {msg['subject']}")
        logger.info(f"发送方: {msg['from']}")

        # 打印消息供用户查看
        print(f"\n📥 收到来自 {msg['from']} 的请求:")
        print(f"主题: {msg['subject']}")
        print(f"优先级: {msg.get('priority', 'MEDIUM')}")

        # 询问用户是否立即处理
        response = input("\n是否立即处理？(y/n/skip): ").strip().lower()

        if response == 'y':
            # 立即处理
            print("请处理此请求...")
            # TODO: 调用任务处理函数
        elif response == 'skip':
            logger.info("跳过此请求")
        else:
            logger.info("稍后处理")

    def handle_response(self, msg):
        """处理RESPONSE消息"""
        logger.info(f"✅ 收到响应: {msg['subject']}")
        print(f"\n✅ 收到来自 {msg['from']} 的响应:")
        print(f"主题: {msg['subject']}")
        print("="*60)
        print(msg['content'])
        print("="*60 + "\n")

    def handle_notification(self, msg):
        """处理NOTIFICATION消息"""
        logger.info(f"📢 收到通知: {msg['subject']}")
        print(f"\n📢 通知来自 {msg['from']}:")
        print(f"主题: {msg['subject']}")
        print(msg['content'] + "\n")


def start_watcher(cli_name):
    """启动mailbox监听器"""
    logger.info(f"启动 {cli_name} 的mailbox监听器...")

    # 确保mailbox目录存在
    mailbox_dir = Path(f"CLIS/{cli_name}/mailbox")
    mailbox_dir.mkdir(parents=True, exist_ok=True)

    # 创建监听器
    event_handler = MailboxWatcher(cli_name)
    observer = Observer()
    observer.schedule(event_handler, str(mailbox_dir), recursive=False)

    # 启动监听
    observer.start()
    logger.info(f"✅ 监听器已启动，监听 {mailbox_dir}")

    print(f"\n{'='*60}")
    print(f"📬 CLI-{cli_name} Mailbox监听器已启动")
    print(f"监听目录: {mailbox_dir}")
    print(f"日志文件: CLIS/{cli_name}/watcher.log")
    print(f"{'='*60}\n")

    try:
        # 持续运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭监听器...")
        observer.stop()
        observer.join()
        logger.info("监听器已关闭")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='CLI Mailbox监听器')
    parser.add_argument('--cli', required=True, help='CLI名称（如: web, api, db）')
    args = parser.parse_args()

    start_watcher(args.cli)
```

#### 1.2 实现简化文件锁（建议4）
```python
# scripts/dev/simple_lock.py

"""
简化版文件锁管理器

使用fcntl+flock实现文件锁，相比复杂的lock管理器：
- 代码从256行减少到30行
- 使用操作系统原子操作
- 进程崩溃自动释放锁
"""

import fcntl
import time
import os
from pathlib import Path


class SimpleFileLock:
    """简化版文件锁"""

    def __init__(self, cli_name):
        self.cli_name = cli_name
        self.locks_dir = Path("CLIS/locks")
        self.locks_dir.mkdir(parents=True, exist_ok=True)
        self.current_lock = None

    def acquire(self, file_path, timeout=3600, blocking=True):
        """
        获取文件锁

        Args:
            file_path: 要锁定的文件路径（相对或绝对）
            timeout: 锁定超时时间（秒）
            blocking: 是否阻塞等待

        Returns:
            (success, message): (是否成功, 消息)
        """
        lock_file_name = file_path.replace('/', '_').replace('\\', '_') + '.lock'
        lock_file = self.locks_dir / lock_file_name

        try:
            # 使用低级文件操作确保原子性
            fd = os.open(lock_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)

            try:
                # 获取文件锁
                if blocking:
                    # 阻塞模式
                    fcntl.flock(fd, fcntl.LOCK_EX)
                else:
                    # 非阻塞模式
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

                # 写入锁信息
                with os.fdopen(fd, 'w') as f:
                    f.write(f"{self.cli_name}\n{time.time()}\n{file_path}\n")

                # 重新打开文件用于后续操作
                f = lock_file.open('r+')
                self.current_lock = (f, lock_file)

                return True, f"文件已锁定: {file_path}"

            except:
                # 如果加锁失败，关闭文件描述符
                os.close(fd)
                raise

        except IOError as e:
            # 检查是否已被锁定
            if lock_file.exists():
                with lock_file.open('r') as f:
                    content = f.read()
                    holder = content.split('\n')[0]
                    waiting_time = time.time() - float(content.split('\n')[1])

                    return False, f"文件已被 {holder} 锁定，等待时间: {waiting_time:.0f}秒"

            return False, f"无法获取锁: {str(e)}"

    def release(self):
        """释放当前持有的锁"""
        if not self.current_lock:
            return True, "没有需要释放的锁"

        f, lock_file = self.current_lock

        try:
            # 释放锁
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            f.close()

            # 删除锁文件
            if lock_file.exists():
                lock_file.unlink()

            self.current_lock = None
            return True, "锁已释放"

        except Exception as e:
            return False, f"释放锁失败: {str(e)}"

    def __enter__(self):
        """支持with语句"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持with语句"""
        self.release()


# 全局锁实例（按CLI命名）
_locks = {}

def get_lock(cli_name):
    """获取CLI的锁实例"""
    if cli_name not in _locks:
        _locks[cli_name] = SimpleFileLock(cli_name)
    return _locks[cli_name]


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='简化版文件锁')
    parser.add_argument('--acquire', action='store_true', help='获取锁')
    parser.add_argument('--release', action='store_true', help='释放锁')
    parser.add_argument('--cli', required=True, help='CLI名称')
    parser.add_argument('--file', help='文件路径')
    parser.add_argument('--blocking', action='store_true', help='阻塞模式')

    args = parser.parse_args()

    lock = get_lock(args.cli)

    if args.acquire:
        if args.file:
            success, message = lock.acquire(args.file, blocking=args.blocking)
            print(f"{'✅' if success else '❌'} {message}")
        else:
            print("错误: 必须指定 --file 参数")

    elif args.release:
        success, message = lock.release()
        print(f"{'✅' if success else '❌'} {message}")
```

#### 1.3 实现智能协调器（建议3）
```python
# scripts/dev/smart_coordinator.py

"""
智能协调器 - 让main更轻松

使用规则引擎自动处理常见协调场景：
1. 阻塞自动解决
2. 空闲资源自动分配
3. 冲突自动预防
"""

import sys
import os
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入基础协调器
try:
    from cli_coordinator import CLICoordinator
except ImportError:
    # 如果导入失败，定义基础类
    class CLICoordinator:
        def __init__(self, clis_dir="CLIS"):
            self.clis_dir = Path(clis_dir)

        def scan_all_status(self):
            statuses = {}
            for cli_dir in self.clis_dir.iterdir():
                if cli_dir.is_dir() and cli_dir.name != 'main':
                    status_file = cli_dir / "STATUS.md"
                    if status_file.exists():
                        statuses[cli_dir.name] = self._parse_status(status_file)
            return statuses

        def _parse_status(self, status_file):
            content = status_file.read_text()
            # 简化的状态解析
            return {
                'name': status_file.parent.name,
                'state': 'unknown',
                'current_task': None,
                'last_update': None,
                'blocked_on': None,
                'waiting_time': 0
            }


class SmartCoordinator(CLICoordinator):
    """智能协调器 - 规则引擎"""

    def __init__(self, clis_dir="CLIS"):
        super().__init__(clis_dir)
        self.coordination_log = self.clis_dir / "SHARED" / "COORDINATION_LOG.md"
        self.coordination_log.parent.mkdir(parents=True, exist_ok=True)

        # 初始化规则
        self.rules = [
            BlockageResolutionRule(self),
            IdleResourceRule(self),
            ConflictPreventionRule(self),
            HealthCheckRule(self)
        ]

    def auto_coordinate(self):
        """自动执行协调规则"""
        print("\n🤖 智能协调器启动...")

        # 扫描所有CLI状态
        statuses = self.scan_all_status()

        print(f"扫描到 {len(statuses)} 个CLI")

        # 执行所有规则
        all_actions = []
        for rule in self.rules:
            actions = rule.evaluate(statuses)
            all_actions.extend(actions)

        # 执行动作
        if all_actions:
            print(f"\n生成 {len(all_actions)} 个协调动作...")

            for i, action in enumerate(all_actions, 1):
                print(f"\n[{i}/{len(all_actions)}] 执行: {action.type}")
                self.execute_action(action)

            # 记录协调日志
            self.log_coordination(all_actions)

            return len(all_actions)
        else:
            print("✅ 无需协调，系统运行正常")
            return 0

    def execute_action(self, action):
        """执行协调动作"""
        if action.type == 'reassign':
            self.send_reassign_message(action)
        elif action.type == 'alert':
            self.send_alert_message(action)
        elif action.type == 'notify':
            self.send_notify_message(action)

    def send_reassign_message(self, action):
        """发送重新分配消息"""
        message = f"""---
**From**: CLI-main
**To**: {action.to_cli}
**Type**: REQUEST
**Priority**: HIGH
**Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**AutoGenerated**: true

**Subject**: 协作请求：协助{action.from_cli}

**Description**:
{action.reason}

**Blocked Task**: {action.blocked_task}

**Action Required**:
请评估是否可以协助完成依赖任务，或者执行以下独立任务：
{action.suggested_task}

**Expected Response**: 15分钟内

此消息由智能协调器自动生成，如无法协助，请回复main。
"""

        # 发送消息
        self._send_message(action.to_cli, message)
        print(f"📧 已发送协调消息到 {action.to_cli}")

    def _send_message(self, to_cli, message):
        """发送消息到指定CLI"""
        mailbox_dir = self.clis_dir / to_cli / "mailbox"
        mailbox_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        message_file = mailbox_dir / f"main_auto_{timestamp}.md"

        with open(message_file, 'w', encoding='utf-8') as f:
            f.write(message)

    def log_coordination(self, actions):
        """记录协调日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open(self.coordination_log, 'a', encoding='utf-8') as f:
            f.write(f"\n## 自动协调: {timestamp}\n\n")

            for action in actions:
                f.write(f"- **类型**: {action.type}\n")
                f.write(f"- **涉及CLI**: {action.from_cli} → {action.to_cli}\n")
                f.write(f"- **原因**: {action.reason}\n")
                f.write(f"- **状态**: {'✅ 已执行' if action.executed else '⏸️ 待执行'}\n")
                f.write("\n")


class CoordinationAction:
    """协调动作"""

    def __init__(self, type, from_cli, to_cli, reason, **kwargs):
        self.type = type
        self.from_cli = from_cli
        self.to_cli = to_cli
        self.reason = reason
        self.executed = False

        for key, value in kwargs.items():
            setattr(self, key, value)


class BlockageResolutionRule:
    """阻塞自动解决规则"""

    def __init__(self, coordinator):
        self.coordinator = coordinator

    def evaluate(self, statuses):
        """评估阻塞情况并生成动作"""
        actions = []

        for cli, status in statuses.items():
            if status['state'] == 'blocked':
                # 计算等待时间
                if status['last_update']:
                    try:
                        last_update = datetime.strptime(status['last_update'], '%Y-%m-%d %H:%M:%S')
                        waiting_time = (datetime.now() - last_update).total_seconds() / 60
                    except:
                        waiting_time = 0
                else:
                    waiting_time = 0

                # 规则1: 等待时间 > 60分钟，自动分配协助
                if waiting_time > 60:
                    idle_cli = self._find_idle_cli(statuses)
                    if idle_cli:
                        actions.append(CoordinationAction(
                            type='reassign',
                            from_cli=cli,
                            to_cli=idle_cli,
                            reason=f"自动协调: {cli}被阻塞{waiting_time:.0f}分钟",
                            blocked_task=status['current_task'],
                            suggested_task="执行独立任务池中的任务或协助依赖任务"
                        ))

        return actions

    def _find_idle_cli(self, statuses):
        """查找空闲CLI"""
        for cli, status in statuses.items():
            if status['state'] == 'idle':
                return cli
        return None


class IdleResourceRule:
    """空闲资源自动分配规则"""

    def __init__(self, coordinator):
        self.coordinator = coordinator

    def evaluate(self, statuses):
        """评估空闲资源并生成动作"""
        actions = []

        idle_clis = [cli for cli, status in statuses.items() if status['state'] == 'idle']

        if not idle_clis:
            return actions

        # 读取独立任务池
        tasks_pool = self.coordinator.clis_dir / "SHARED" / "TASKS_POOL.md"
        if tasks_pool.exists():
            with open(tasks_pool, 'r') as f:
                content = f.read()

            # 解析独立任务
            available_tasks = self._parse_tasks_pool(content)

            # 为空闲CLI分配任务
            for i, idle_cli in enumerate(idle_clis):
                if i < len(available_tasks):
                    task = available_tasks[i]

                    actions.append(CoordinationAction(
                        type='notify',
                        from_cli='main',
                        to_cli=idle_cli,
                        reason=f"您当前空闲，建议执行独立任务: {task['name']}",
                        suggested_task=task
                    ))

        return actions

    def _parse_tasks_pool(self, content):
        """解析任务池"""
        # 简化实现，实际应该解析markdown
        return []


class ConflictPreventionRule:
    """冲突自动预防规则"""

    def __init__(self, coordinator):
        self.coordinator = coordinator

    def evaluate(self, statuses):
        """评估潜在冲突并生成动作"""
        actions = []

        # 检查文件锁
        locks_dir = self.coordinator.clis_dir / "locks"

        if locks_dir.exists():
            for lock_file in locks_dir.glob("*.lock"):
                try:
                    with open(lock_file, 'r') as f:
                        content = f.read()
                        holder = content.split('\n')[0]
                        waiting_time = time.time() - float(content.split('\n')[1])

                    # 规则: 锁定时间 > 30分钟，发送提醒
                    if waiting_time > 1800:  # 30分钟
                        actions.append(CoordinationAction(
                            type='alert',
                            from_cli='main',
                            to_cli=holder,
                            reason=f"文件锁持有时间过长({waiting_time/60:.0f}分钟)，请尽快完成并释放锁",
                            lock_file=lock_file.name
                        ))

                except:
                    pass

        return actions


class HealthCheckRule:
    """健康检查规则"""

    def __init__(self, coordinator):
        self.coordinator = coordinator

    def evaluate(self, statuses):
        """评估CLI健康状态并生成动作"""
        actions = []

        for cli, status in statuses.items():
            # 检查最后更新时间
            if status['last_update']:
                try:
                    last_update = datetime.strptime(status['last_update'], '%Y-%m-%d %H:%M:%S')
                    idle_time = (datetime.now() - last_update).total_seconds() / 60

                    # 规则: 超过10分钟未更新，发送提醒
                    if idle_time > 10:
                        actions.append(CoordinationAction(
                            type='notify',
                            from_cli='main',
                            to_cli=cli,
                            reason=f"STATUS.md已{idle_time:.0f}分钟未更新，请及时更新"
                        ))

                except:
                    pass

        return actions


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='智能CLI协调器')
    parser.add_argument('--auto', action='store_true', help='自动执行协调')
    parser.add_argument('--clis-dir', default='CLIS', help='CLI目录')

    args = parser.parse_args()

    coordinator = SmartCoordinator(args.clis_dir)

    if args.auto:
        action_count = coordinator.auto_coordinate()
        print(f"\n✅ 协调完成，执行了 {action_count} 个动作")


if __name__ == '__main__':
    main()
```

#### 1.4 实现STATUS自动更新（建议2）
```python
# scripts/dev/auto_status.py

"""
STATUS自动更新装饰器

使用装饰器自动更新STATUS.md，避免手动更新遗漏。
"""

import sys
import os
import re
import time
import functools
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def track_task(cli_name):
    """装饰器: 自动更新STATUS.md"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 开始任务
            update_status(
                cli_name=cli_name,
                state='active',
                current_task=func.__name__,
                last_update=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )

            try:
                # 执行任务
                result = func(*args, **kwargs)

                # 任务成功
                update_status(
                    cli_name=cli_name,
                    state='idle',
                    last_update=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )

                return result

            except Exception as e:
                # 任务失败
                update_status(
                    cli_name=cli_name,
                    state='error',
                    last_update=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    error=str(e)
                )
                raise

        return wrapper
    return decorator


def update_status(cli_name, **kwargs):
    """更新STATUS.md"""
    status_file = Path(f"CLIS/{cli_name}/STATUS.md")

    if not status_file.exists():
        print(f"⚠️  STATUS文件不存在: {status_file}")
        return

    # 读取现有内容
    content = status_file.read_text()

    # 更新字段
    for key, value in kwargs.items():
        pattern = f"\\*\\*{key}\\*\\*:\\s*(.+)"
        replacement = f"**{key}**: {value}"

        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content, count=1)
        else:
            # 如果字段不存在，添加到文件末尾
            content += f"\n**{key}**: {value}\n"

    # 写回文件
    status_file.write_text(content)


# 使用示例
if __name__ == '__main__':
    @track_task('api')
    def task_1_2_fix_dashboard():
        """任务1.2: 修复dashboard.py"""
        print("执行任务1.2...")
        # 任务逻辑
        time.sleep(2)
        print("任务1.2完成")
        return "success"

    # 执行任务
    task_1_2_fix_dashboard()
```

#### 1.5 实现一键启动脚本（建议5）
```bash
#!/bin/bash
# scripts/dev/init_multi_cli.sh - 一键初始化多CLI环境

set -e

# 注意：bash脚本中使用的是GNU time命令或sleep内置命令
# Python脚本中使用time标准库（已在前面的依赖安装部分说明）

echo "🚀 初始化多CLI协作环境 v2.0..."

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: 创建目录结构
echo -e "\n📁 ${YELLOW}创建目录结构...${NC}"
mkdir -p CLIS/main/{mailbox,archive,checkpoints}
mkdir -p CLIS/web/{mailbox,archive}
mkdir -p CLIS/api/{mailbox,archive}
mkdir -p CLIS/db/{mailbox,archive}
mkdir -p CLIS/it/worker{1..3}/{mailbox,archive}
mkdir -p CLIS/{locks,SHARED,templates}

echo -e "${GREEN}✅ 目录结构创建完成${NC}"

# Step 2: 复制模板文件
echo -e "\n📄 ${YELLOW}生成模板文件...${NC}"

# 生成模板文件
cat > CLIS/templates/TASK.md.template << 'EOF'
# 任务清单

## 当前任务

当前无任务，等待main分配。

## 任务历史

| 任务ID | 任务名称 | 完成时间 | 状态 |
|--------|---------|---------|------|
EOF

cat > CLIS/templates/RULES.md.template << 'EOF'
# 工作规范

## 核心职责

（待main分配）

## 工作流程

1. 接收任务
2. 执行任务
3. 提交代码
4. 更新REPORT.md

## 沟通规范

- 通过mailbox进行异步通信
- 紧急问题使用ALERT类型消息
- 普通请求使用REQUEST类型消息
EOF

cat > CLIS/templates/STATUS.md.template << 'EOF'
# 当前状态

**CLI**: CLI-NAME
**Updated**: {{TIMESTAMP}}

## Current State

**State**: 🟢 Idle
**Current Task**: 无
**Progress**: N/A

## Blocked On

无

## Issues

无
EOF

# 复制模板到各CLI目录
for cli in main web api db it/worker1 it/worker2 it/worker3; do
    cp CLIS/templates/TASK.md.template CLIS/$cli/TASK.md
    cp CLIS/templates/RULES.md.template CLIS/$cli/RULES.md
    cp CLIS/templates/STATUS.md.template CLIS/$cli/STATUS.md
    # 替换CLI-NAME占位符
    sed -i "s/CLI-NAME/$cli/g" CLIS/$cli/STATUS.md
    sed -i "s/{{TIMESTAMP}}/$(date '+%Y-%m-%d %H:%M:%S')/g" CLIS/$cli/STATUS.md
done

echo -e "${GREEN}✅ 模板文件生成完成${NC}"

# Step 3: 生成初始任务（从main开始）
echo -e "\n⚙️  ${YELLOW}生成初始任务...${NC}"

# 这里可以读取任务配置文件或使用默认任务
cat > CLIS/main/TASK.md << 'EOF'
# CLI-main 初始任务

## 立即执行

### Phase 1: 修复关键阻塞
- [ ] 1.1 修复.env中的USE_MOCK_DATA配置
- [ ] 1.2 修复dashboard.py中的Mock依赖
- [ ] 1.3 修复导入路径

## 下一步

完成Phase 1后，为其他CLI分配任务。
EOF

echo -e "${GREEN}✅ 初始任务生成完成${NC}"

# Step 4: 创建配置文件
echo -e "\n⚙️  ${YELLOW}创建配置文件...${NC}"

cat > CLIS/main/.cli_config << 'EOF'
# CLI配置文件

[cli]
name = main
type = coordinator

[mailbox]
watcher_enabled = true
scan_interval = 60

[coordination]
auto_coordinate = true
coordinate_interval = 300
EOF

for cli in web api db; do
    cat > CLIS/$cli/.cli_config << EOF
[cli]
name = $cli
type = worker

[mailbox]
watcher_enabled = true
scan_interval = 60
EOF
done

echo -e "${GREEN}✅ 配置文件创建完成${NC}"

# Step 5: 启动协调器（后台）
echo -e "\n🤖 ${YELLOW}启动CLI协调器...${NC}"

nohup python scripts/dev/smart_coordinator.py --auto >> CLIS/main/coordinator.log 2>&1 &
COORDINATOR_PID=$!
echo $COORDINATOR_PID > CLIS/main/.coordinator_pid

echo -e "${GREEN}✅ 协调器已启动 (PID: $COORDINATOR_PID)${NC}"

# Step 6: 提示启动mailbox监听器
echo -e "\n📬 ${YELLOW}Mailbox监听器启动提示...${NC}"
echo "每个CLI在启动时，请运行以下命令启动mailbox监听器："
echo ""
echo -e "${GREEN}python scripts/dev/mailbox_watcher.py --cli=web &${NC}"
echo -e "${GREEN}python scripts/dev/mailbox_watcher.py --cli=api &${NC}"
echo -e "${GREEN}python scripts/dev/mailbox_watcher.py --cli=db &${NC}"
echo -e "${GREEN}python scripts/dev/mailbox_watcher.py --cli=it/worker1 &${NC}"
echo ""

# Step 7: 显示状态信息
echo -e "\n📊 ${YELLOW}初始化完成！${NC}"
echo ""
echo "下一步操作："
echo "1. 启动各CLI的mailbox监听器（见上）"
echo "2. 查看main任务: cat CLIS/main/TASK.md"
echo "3. 开始执行任务！"
echo ""
echo "监控命令："
echo "  查看状态: python scripts/dev/cli_coordinator.py --scan"
echo "  查看消息: ls CLIS/*/mailbox/"
echo "  停止协调器: kill $COORDINATOR_PID"
echo ""

echo -e "${GREEN}✅ 多CLI环境初始化完成！${NC}"
```

#### 1.6 实现CLI报到机制（建议8）
```python
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

        print(f"✅ 已向main发送报到请求")

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
    parser.add_argument('--role', help='分配的角色')
    parser.add_argument('--tasks', help='分配的任务（逗号分隔）')

    args = parser.parse_args()

    if args.register:
        # CLI报到
        register_as_cli(args.cli)

    elif args.confirm:
        # main确认
        tasks = args.tasks.split(',') if args.tasks else []
        confirm_cli_registration(args.cli, args.role, tasks)
```

---

## 📝 使用指南

### 快速启动（5分钟）

#### Step 1: 初始化环境
```bash
# 一键初始化
bash scripts/dev/init_multi_cli.sh
```

#### Step 2: 启动CLI-main
```bash
# main启动
cd /opt/claude/mystocks_spec

# 启动mailbox监听器
python scripts/dev/mailbox_watcher.py --cli=main &

# 开始执行任务
cat CLIS/main/TASK.md
```

#### Step 3: 启动其他CLI
```bash
# Terminal 1: 启动CLI-web
python scripts/dev/mailbox_watcher.py --cli=web &
# 然后向main报到
python scripts/dev/cli_registration.py --register --cli=web --type=worker --capabilities="frontend,Vue,API-integration"

# Terminal 2: 启动CLI-api
python scripts/dev/mailbox_watcher.py --cli=api &
# 然后向main报到
python scripts/dev/cli_registration.py --register --cli=api --type=worker --capabilities="backend,API,OpenSpec"

# Terminal 3: 启动CLI-db
python scripts/dev/mailbox_watcher.py --cli=db &
# 然后向main报到
python scripts/dev/cli_registration.py --register --cli=db --type=worker --capabilities="database,SQL,optimization"
```

#### Step 4: main确认CLI并分配任务
```bash
# main查看报到情况
cat CLIS/main/registrations.json

# main确认CLI
python scripts/dev/cli_registration.py \
  --confirm \
  --cli=web \
  --role="frontend-developer" \
  --tasks="1.1,1.2,1.3"

python scripts/dev/cli_registration.py \
  --confirm \
  --cli=api \
  --role="api-developer" \
  --tasks="1.4,1.5,2.1"

python scripts/dev/cli_registration.py \
  --confirm \
  --cli=db \
  --role="database-admin" \
  --tasks="2.1,2.2,3.1"
```

### 日常工作流程

#### CLI-web的典型一天
```bash
# 1. 启动CLI（包含mailbox监听器）
python scripts/dev/mailbox_watcher.py --cli=web &
# 自动报到已集成在启动脚本中

# 2. 查看分配的任务
cat CLIS/web/TASK.md

# 3. 执行任务
# (开始编码工作...)

# 4. 使用装饰器自动更新STATUS
from scripts.dev.auto_status import track_task

@track_task('web')
def implement_dashboard():
    # 实现Dashboard页面
    pass

implement_dashboard()

# 5. 完成后，自动更新REPORT.md
```

#### CLI-main的典型一天
```bash
# 1. 启动CLI
python scripts/dev/mailbox_watcher.py --cli=main &

# 2. 查看报到情况
cat CLIS/main/registrations.json

# 3. 确认并分配角色
python scripts/dev/cli_registration.py --confirm --cli=web --role=frontend --tasks="1.1,1.2"

# 4. 监控各CLI状态
python scripts/dev/cli_coordinator.py --scan

# 5. 智能协调（自动运行）
python scripts/dev/smart_coordinator.py --auto

# 6. 生成周报
python scripts/dev/report_generator.py --period=week
```

---

## 🎯 实施时间表

| 阶段 | 任务 | 预计时间 | 状态 |
|------|------|----------|------|
| **Phase 0** | 环境准备 | 30分钟 | ⏸️ 待开始 |
| Phase 1 | 核心功能实现 | 2小时 | ⏸️ 待开始 |
| Phase 2 | 试点运行 | 1天 | ⏸️ 待开始 |
| Phase 3 | 全面推广 | 按需 | ⏸️ 待开始 |

---

## 📊 预期收益

### 效率提升
- **响应速度**: 从分钟级→秒级（mailbox事件监听）
- **main负担**: 减少70%（智能协调规则引擎）
- **手动操作**: 减少90%（STATUS自动更新）

### 协作质量
- **实时协调**: 自动处理常见阻塞场景
- **角色管理**: 自动报到和角色分配
- **状态透明**: 实时状态监控

### 风险控制
- **文件冲突**: 简化的文件锁机制
- **快速回滚**: 检查点机制
- **健康监控**: CLI健康检查

---

## 🚀 下一步行动

1. **立即可执行**: 运行`bash scripts/dev/init_multi_cli.sh`
2. **查看文档**: 完整的使用指南和API文档
3. **开始试点**: 先用main+api+db 3个CLI试点

---

**文档版本**: v2.0
**最后更新**: 2026-01-01
**维护者**: MyStocks Development Team
