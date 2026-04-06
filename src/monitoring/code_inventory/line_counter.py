"""行数统计模块"""

import os
from pathlib import Path
from typing import List


def count_lines(file_path: str) -> int:
    """统计文件行数（忽略空行和纯注释行）

    Args:
        file_path: 文件路径

    Returns:
        行数（有效代码行）
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        # 统计非空行和非纯注释行
        count = 0
        for line in lines:
            stripped = line.strip()
            # 跳过空行和纯注释行（# 或 // 开头）
            if stripped and not stripped.startswith("#") and not stripped.startswith("//"):
                count += 1

        return count
    except Exception:
        return 0


def count_total_lines(file_path: str) -> int:
    """统计文件总行数

    Args:
        file_path: 文件路径

    Returns:
        总行数
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return len(f.readlines())
    except Exception:
        return 0


def should_split_file(file_path: str, threshold: int = 1000) -> bool:
    """判断文件是否需要拆分

    Args:
        file_path: 文件路径
        threshold: 行数阈值

    Returns:
        是否超过阈值
    """
    return count_lines(file_path) > threshold


def get_file_type(file_path: str) -> str:
    """获取文件类型

    Args:
        file_path: 文件路径

    Returns:
        文件扩展名（如 .py, .vue）
    """
    return Path(file_path).suffix


def is_excluded_dir(dir_name: str, exclude_dirs: List[str]) -> bool:
    """判断目录是否应该排除

    Args:
        dir_name: 目录名
        exclude_dirs: 排除目录列表

    Returns:
        是否排除
    """
    return dir_name in exclude_dirs or dir_name.startswith(".")


def scan_files(
    base_dir: str,
    extensions: List[str],
    exclude_dirs: List[str]
) -> List[str]:
    """扫描目录下所有指定类型的文件

    Args:
        base_dir: 基础目录
        extensions: 文件扩展名列表
        exclude_dirs: 排除目录列表

    Returns:
        文件路径列表
    """
    files = []

    for root, dirs, filenames in os.walk(base_dir):
        # 过滤排除目录（原地修改 dirs）
        dirs[:] = [d for d in dirs if not is_excluded_dir(d, exclude_dirs)]

        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))

    return files
