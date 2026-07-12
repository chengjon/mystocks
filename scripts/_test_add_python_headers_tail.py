#!/usr/bin/env python3
"""Support tests extracted from `scripts/tests/test_add_python_headers.py`."""

import os
import shutil
import tempfile
from unittest.mock import patch

from src.utils.add_python_headers import PythonHeaderAdder


class TestTailScenarios:
    """从集成场景中拆出的尾部测试。"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        os.chdir(self.original_cwd)
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_large_scale_processing(self):
        """测试大规模处理性能"""
        import time

        num_files = 50
        created_files = []

        for i in range(num_files):
            file_path = f"large_test_{i}.py"
            full_path = os.path.join(self.temp_dir, file_path)

            with open(full_path, "w", encoding="utf-8") as file_handle:
                file_handle.write(f"# File {i}\n")
                file_handle.write(f"def function_{i}():\n")
                file_handle.write("    pass\n")

            created_files.append(full_path)

        adder = PythonHeaderAdder()
        start_time = time.time()

        for file_path in created_files:
            adder.add_header_to_file(
                file_path,
                description=f"大规模测试文件 {file_path}",
                author="性能测试",
                created_date="2024-12-22",
            )

        end_time = time.time()
        processing_time = end_time - start_time

        assert adder.added_count == num_files
        assert processing_time < 10.0

        for file_path in created_files:
            backup_path = file_path + ".backup"
            assert os.path.exists(backup_path)

    def test_unicode_and_special_characters(self):
        """测试Unicode和特殊字符处理"""
        special_files = {
            "unicode_test.py": "# 中文测试 🚀💻\nprint('unicode')\n",
            "emoji_test.py": "# Test with emojis: 🎉🔥💯\nprint('emojis')\n",
            "special_chars.py": "# Special chars: áéíóú ñ\nprint('special')\n",
        }

        for file_name, content in special_files.items():
            file_path = os.path.join(self.temp_dir, file_name)
            with open(file_path, "w", encoding="utf-8") as file_handle:
                file_handle.write(content)

        adder = PythonHeaderAdder()

        for file_name, original_content in special_files.items():
            file_path = os.path.join(self.temp_dir, file_name)
            result = adder.add_header_to_file(
                file_path,
                description=f"特殊字符测试 {file_name}",
                author="Unicode测试 👨‍💻",
                created_date="2024年12月22日",
            )
            assert result is True

            with open(file_path, encoding="utf-8") as file_handle:
                new_content = file_handle.read()

            assert original_content in new_content
            assert "Unicode测试 👨‍💻" in new_content
            assert "2024年12月22日" in new_content

    def test_error_recovery_and_resilience(self):
        """测试错误恢复和韧性"""
        normal_file = os.path.join(self.temp_dir, "normal.py")
        with open(normal_file, "w", encoding="utf-8") as file_handle:
            file_handle.write("print('normal')\n")

        error_file = os.path.join(self.temp_dir, "error.py")
        with open(error_file, "w", encoding="utf-8") as file_handle:
            file_handle.write("print('error')\n")

        adder = PythonHeaderAdder()

        normal_result = adder.add_header_to_file(normal_file, "正常文件")
        assert normal_result is True

        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            error_result = adder.add_header_to_file(error_file, "错误文件")
            assert error_result is False

        assert adder.added_count == 1
        assert adder.failed_count == 1
