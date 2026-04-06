#!/usr/bin/env python3
"""
更新项目中的import路径
将旧的直接导入改为从src目录导入
"""

import re
from pathlib import Path

# 定义需要更新的模块映射
MODULE_MAPPINGS = {
    "from core": "from src.core",
    "from adapters": "from src.adapters",
    "from data_access": "from src.data_access",
    "from data_sources": "from src.data_sources",
    "from db_manager": "from src.storage.database",
    "from monitoring": "from src.monitoring",
    "from ml_strategy": "from src.ml_strategy",
    "from reporting": "from src.reporting",
    "from visualization": "from src.visualization",
    "from utils": "from src.utils",
    "from interfaces": "from src.interfaces",
    "import core": "import src.core",
    "import adapters": "import src.adapters",
    "import data_access": "import src.data_access",
    "import data_sources": "import src.data_sources",
    "import db_manager": "import src.storage.database",
    "import monitoring": "import src.monitoring",
    "import ml_strategy": "import src.ml_strategy",
    "import reporting": "import src.reporting",
    "import visualization": "import src.visualization",
    "import utils": "import src.utils",
    "import interfaces": "import src.interfaces",
}


def update_imports_in_file(file_path):
    """更新单个文件中的import语句"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        changes_made = []

        # 应用所有映射
        for old_import, new_import in MODULE_MAPPINGS.items():
            if old_import in content:
                # 使用正则确保只替换完整的模块名
                pattern = re.escape(old_import) + r"(?=\s|\.|$)"
                if re.search(pattern, content):
                    content = re.sub(pattern, new_import, content)
                    changes_made.append(f"{old_import} -> {new_import}")

        # 如果有更改，写回文件
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return changes_made

        return None

    except Exception as e:
        print(f"❌ 处理文件失败 {file_path}: {e}")
        return None


def find_python_files(root_dir, exclude_dirs=None):
    """查找所有Python文件"""
    if exclude_dirs is None:
        exclude_dirs = {
            ".git",
            "node_modules",
            "__pycache__",
            "venv",
            "env",
            ".pytest_cache",
            "htmlcov",
            "temp",
            ".archive",
            ".claude",
            ".taskmaster",
            ".specify",
        }

    python_files = []
    root_path = Path(root_dir)

    for py_file in root_path.rglob("*.py"):
        # 检查是否在排除目录中
        if any(excluded in py_file.parts for excluded in exclude_dirs):
            continue
        python_files.append(py_file)

    return python_files


def main():
    print("=" * 60)
    print(" Import路径更新工具")
    print("=" * 60)
    print()

    # 获取项目根目录
    project_root = Path(__file__).parent

    print(f"📁 项目根目录: {project_root}")
    print("🔍 查找Python文件...")

    # 查找所有Python文件
    python_files = find_python_files(project_root)
    print(f"✓ 找到 {len(python_files)} 个Python文件")
    print()

    # 询问是否继续
    response = input("是否开始更新import路径? (y/N): ")
    if not response.lower().startswith("y"):
        print("❌ 已取消")
        return

    print()
    print("开始更新...")
    print()

    updated_files = []
    total_changes = 0

    for file_path in python_files:
        changes = update_imports_in_file(file_path)
        if changes:
            updated_files.append(file_path)
            total_changes += len(changes)
            print(f"✓ {file_path.relative_to(project_root)}")
            for change in changes:
                print(f"  • {change}")

    print()
    print("=" * 60)
    print(" 更新完成")
    print("=" * 60)
    print("📊 统计:")
    print(f"  - 更新文件数: {len(updated_files)}")
    print(f"  - 总更改数: {total_changes}")
    print()

    if updated_files:
        print("⚠️  下一步:")
        print("  1. 检查更改: git diff")
        print("  2. 运行测试: pytest tests/")
        print(
            "  3. 提交更改: git add -A && git commit -m 'refactor: update import paths to src module'"
        )
    else:
        print("✓ 没有需要更新的文件")


if __name__ == "__main__":
    main()
