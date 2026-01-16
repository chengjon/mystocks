# scripts/dev/mailbox_watcher.py

"""
Mailbox事件监听器 - 实时响应新消息

使用watchdog监听文件系统事件，新消息到达时立即处理。
替代定时扫描机制，实现秒级响应。
"""

import sys
import os
import time
import logging
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 先解析参数
import argparse

parser = argparse.ArgumentParser(description="CLI Mailbox监听器")
parser.add_argument("--cli", required=True, help="CLI名称（如: web, api, db）")
args = parser.parse_args()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(f"CLIS/{args.cli}/watcher.log"), logging.StreamHandler()],
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

        if not event.src_path.endswith(".md"):
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
        with open(msg_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 解析消息
        msg = self.parse_message(content)

        if not msg:
            logger.warning(f"消息格式错误: {msg_file}")
            return

        # 根据消息类型处理
        if msg["type"] == "ALERT":
            self.handle_alert(msg)
        elif msg["type"] == "REQUEST":
            self.handle_request(msg)
        elif msg["type"] == "RESPONSE":
            self.handle_response(msg)
        elif msg["type"] == "NOTIFICATION":
            self.handle_notification(msg)

        # 将消息移到archive（已处理）
        archive_dir = Path(f"CLIS/{self.cli_name}/archive")
        archive_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_path = archive_dir / f"processed_{timestamp}_{Path(msg_file).name}"

        import shutil

        shutil.move(msg_file, new_path)

        logger.info(f"✅ 消息已处理并归档: {new_path}")

    def parse_message(self, content):
        """解析消息"""
        lines = content.split("\n")
        msg = {}

        for line in lines:
            if line.startswith("**From**:"):
                msg["from"] = line.split(":", 1)[1].strip()
            elif line.startswith("**To**:"):
                msg["to"] = line.split(":", 1)[1].strip()
            elif line.startswith("**Type**:"):
                msg["type"] = line.split(":", 1)[1].strip()
            elif line.startswith("**Priority**:"):
                msg["priority"] = line.split(":", 1)[1].strip()
            elif line.startswith("**Subject**:"):
                msg["subject"] = line.split(":", 1)[1].strip()

        # 必须字段验证
        required = ["from", "to", "type", "subject"]
        if not all(k in msg for k in required):
            return None

        msg["content"] = content
        msg["file_path"] = None

        return msg

    def handle_alert(self, msg):
        """处理ALERT消息"""
        logger.warning(f"🚨 收到ALERT: {msg['subject']}")
        logger.warning(f"发送方: {msg['from']}")
        logger.warning(f"优先级: {msg.get('priority', 'UNKNOWN')}")

        # 打印消息内容供用户查看
        print("\n" + "=" * 60)
        print(f"🚨 紧急消息来自 {msg['from']}")
        print(f"主题: {msg['subject']}")
        print("=" * 60)
        print(msg["content"])
        print("=" * 60 + "\n")

        # ALERT消息需要立即处理，等待用户输入
        while True:
            response = input("请处理此ALERT消息，处理完成后输入 'done': ")
            if response.lower().strip() == "done":
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

        if response == "y":
            # 立即处理
            print("请处理此请求...")
            # TODO: 调用任务处理函数
        elif response == "skip":
            logger.info("跳过此请求")
        else:
            logger.info("稍后处理")

    def handle_response(self, msg):
        """处理RESPONSE消息"""
        logger.info(f"✅ 收到响应: {msg['subject']}")
        print(f"\n✅ 收到来自 {msg['from']} 的响应:")
        print(f"主题: {msg['subject']}")
        print("=" * 60)
        print(msg["content"])
        print("=" * 60 + "\n")

    def handle_notification(self, msg):
        """处理NOTIFICATION消息"""
        logger.info(f"📢 收到通知: {msg['subject']}")
        print(f"\n📢 通知来自 {msg['from']}:")
        print(f"主题: {msg['subject']}")
        print(msg["content"] + "\n")


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

    print(f"\n{'=' * 60}")
    print(f"📬 CLI-{cli_name} Mailbox监听器已启动")
    print(f"监听目录: {mailbox_dir}")
    print(f"日志文件: CLIS/{cli_name}/watcher.log")
    print(f"{'=' * 60}\n")

    try:
        # 持续运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭监听器...")
        observer.stop()
        observer.join()
        logger.info("监听器已关闭")


if __name__ == "__main__":
    start_watcher(args.cli)
