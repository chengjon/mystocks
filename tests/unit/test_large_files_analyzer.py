"""
T0XX: 大文件分析脚本单元测试

验证large_files_analyzer.py脚本的功能，包括文件扫描、行数统计和报告生成。
"""

import os
import sys
from io import StringIO
from unittest.mock import patch, MagicMock
from pathlib import Path
import pytest

# 假设脚本在项目的scripts/dev目录下，需要调整路径使其可导入
# 获取当前文件所在目录的父目录（即tests/unit）
current_dir = Path(__file__).parent
# 获取项目根目录（tests/unit的父目录的父目录）
project_root = current_dir.parent.parent
# 将scripts/dev添加到sys.path
sys.path.insert(0, str(project_root / "scripts" / "dev"))


class TestLargeFilesAnalyzer:
    """大文件分析脚本测试类"""

    @pytest.fixture
    def mock_os_walk(self):
        """模拟os.walk的fixture，返回自定义的文件结构"""

        def _mock_walk_side_effect(top):
            if top == str(project_root):
                yield str(project_root), ["dir1", "scripts"], ["small_file.py"]
                yield str(project_root / "dir1"), [], ["medium_file.py"]
                yield str(project_root / "scripts"), ["dev"], []
                yield (
                    str(project_root / "scripts" / "dev"),
                    [],
                    ["large_file.py", "another_large_file.py", "non_py_file.txt"],
                )
            # 模拟跳过目录
            elif ".git" in top or "__pycache__" in top:
                yield top, [], []  # 空结果，模拟跳过
            else:
                yield top, [], []

        return _mock_walk_side_effect

    @pytest.fixture
    def mock_open(self):
        """模拟open函数，返回不同文件内容的MagicMock"""

        def _mock_open_side_effect(file_path, mode="r", encoding="utf-8", errors="ignore"):
            mock_file = MagicMock()
            filename = os.path.basename(file_path)  # Get just the filename
            if filename == "small_file.py":
                mock_file.__enter__.return_value.__iter__.return_value = ["line"] * 10
            elif filename == "medium_file.py":
                mock_file.__enter__.return_value.__iter__.return_value = ["line"] * 500
            elif filename == "large_file.py":
                mock_file.__enter__.return_value.__iter__.return_value = ["line"] * 2500
            elif filename == "another_large_file.py":
                mock_file.__enter__.return_value.__iter__.return_value = ["line"] * 3500
            elif filename == "non_py_file.txt":
                mock_file.__enter__.return_value.__iter__.return_value = ["text line"] * 100
            else:
                mock_file.__enter__.return_value.__iter__.return_value = ["line"] * 1
            return mock_file

        return _mock_open_side_effect

    @patch("os.walk", autospec=True)
    @patch("builtins.open", new_callable=MagicMock)
    @patch("sys.stdout", new_callable=StringIO)
    @patch("large_files_analyzer.Path")
    def test_analyze_python_files(
        self,
        mock_path_in_analyzer_module,
        mock_stdout,
        mock_open_func,
        mock_os_walk_func,
        mock_os_walk,
        mock_open,
    ):
        """测试analyze_python_files函数"""
        print("\n📍 测试analyze_python_files函数")

        # Configure mock_os_walk and mock_open
        mock_os_walk_func.side_effect = mock_os_walk
        mock_open_func.side_effect = mock_open

        # Mock Path(root_dir).rglob('*.py') from within the large_files_analyzer module
        mock_root_path_instance = MagicMock(spec=Path)
        mock_root_path_instance.rglob.return_value = [
            MagicMock(spec=Path, name="small_file.py"),
            MagicMock(spec=Path, name="medium_file.py"),
            MagicMock(spec=Path, name="large_file.py"),
            MagicMock(spec=Path, name="another_large_file.py"),
        ]
        # When large_files_analyzer.Path(str(project_root)) is called, it should return our mock_root_path_instance
        mock_path_in_analyzer_module.return_value = mock_root_path_instance

        # Import the function after patching is set up
        from large_files_analyzer import analyze_python_files

        # Call the function
        large_files = analyze_python_files(str(project_root))

        # 验证返回的大文件列表
        assert len(large_files) == 2
        assert any(f["relative_path"] == "scripts/dev/another_large_file.py" for f in large_files)
        assert any(f["relative_path"] == "scripts/dev/large_file.py" for f in large_files)
        assert large_files[0]["lines"] == 3500  # 确认按行数排序

        # 验证输出
        output = mock_stdout.getvalue()
        assert "=== MyStocks 大文件分析报告 ===" in output
        assert "总Python文件数: 4" in output  # 基于mock_pathlib_path.rglob的返回值
        assert "总代码行数: 6,510" in output  # 10 + 500 + 2500 + 3500
        assert "超过2000行的文件: 2个" in output
        assert "超大文件列表 (建议拆分):" in output
        assert "another_large_file.py" in output
        assert "large_file.py" in output
        print("  ✅ analyze_python_files函数验证通过")

    @pytest.mark.parametrize(
        "file_name, expected_suggestion_part",
        [
            ("test_exchange.py", "核心测试"),
            ("test_freqtradebot.py", "核心机器人测试"),
            ("exchange.py", "交易所核心类"),
            ("my_module.py", "核心功能"),
        ],
    )
    @patch("sys.stdout", new_callable=StringIO)
    def test_suggest_split(self, mock_stdout, file_name, expected_suggestion_part):
        """测试suggest_split函数"""
        print(f"\n📍 测试suggest_split函数 - 文件: {file_name}")

        # Import the function after patching is set up
        from large_files_analyzer import suggest_split

        # 模拟文件路径，虽然函数只用文件名
        mock_file_path = f"/path/to/{file_name}"
        suggest_split(mock_file_path, 3000)  # 行数在此测试中不重要

        output = mock_stdout.getvalue()
        assert expected_suggestion_part in output
        print("  ✅ suggest_split函数验证通过")


# Clean up sys.path after tests
@pytest.fixture(scope="session", autouse=True)
def cleanup_sys_path():
    yield
    # Remove the added path from sys.path
    global project_root
    try:
        sys.path.remove(str(project_root / "scripts" / "dev"))
    except ValueError:
        pass
