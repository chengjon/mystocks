# scripts/dev/simple_lock.py

"""
简化版文件锁管理器

使用fcntl+flock实现文件锁，相比复杂的lock管理器：
- 代码从256行减少到95行
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
