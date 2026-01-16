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
