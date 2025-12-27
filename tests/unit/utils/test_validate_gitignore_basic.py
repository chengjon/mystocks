"""
Validate GitIgnore基础测试
专注于提升validate_gitignore模块覆盖率（318行代码）
"""

import os
import subprocess
import sys
from unittest.mock import Mock, patch

import pytest

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

# 测试目标模块
from src.utils.validate_gitignore import GitIgnoreValidator


class TestGitIgnoreValidatorBasic:
    """GitIgnoreValidator基础测试 - 专注覆盖率"""

    def test_initialization_default(self):
        """测试默认初始化"""
        validator = GitIgnoreValidator()

        # 验证基本属性
        assert hasattr(validator, "root_dir")
        assert hasattr(validator, "should_be_ignored")
        assert hasattr(validator, "should_be_visible")
        assert hasattr(validator, "issues")
        assert hasattr(validator, "warnings")
        assert hasattr(validator, "successes")

        # 验证默认值
        assert hasattr(validator, "root_dir")

    def test_initialization_with_path(self):
        """测试带路径的初始化"""
        validator = GitIgnoreValidator("/tmp")

        # 验证路径设置
        assert str(validator.root_dir) == "/tmp"

    def test_should_be_ignored_patterns(self):
        """测试应该被忽略的模式"""
        validator = GitIgnoreValidator()

        # 验证关键忽略模式
        expected_patterns = [
            "__pycache__",
            "*.pyc",
            "*.log",
            ".env",
            "*.swp",
            "node_modules",
            ".idea",
        ]

        for pattern in expected_patterns:
            assert pattern in validator.should_be_ignored, f"缺少忽略模式: {pattern}"

    def test_should_be_visible_files(self):
        """测试应该可见的文件"""
        validator = GitIgnoreValidator()

        # 验证关键可见文件
        expected_files = [".env.example", "temp/README.md", "data/backups/.gitkeep"]

        for file_path in expected_files:
            assert file_path in validator.should_be_visible, f"缺少可见文件: {file_path}"

    def test_run_git_command_success(self):
        """测试git命令执行成功"""
        validator = GitIgnoreValidator()

        with patch("subprocess.run") as mock_run:
            # 模拟成功执行
            mock_run.return_value = Mock(stdout="test output", returncode=0, check=True)

            result = validator.run_git_command(["status"])

            assert result == "test output"
            mock_run.assert_called_once()

    def test_run_git_command_failure(self):
        """测试git命令执行失败"""
        validator = GitIgnoreValidator()

        with patch("subprocess.run") as mock_run:
            # 模拟执行失败
            mock_run.side_effect = subprocess.CalledProcessError(1, "git")

            result = validator.run_git_command(["status"])

            assert result == ""

    def test_get_untracked_files(self):
        """测试获取未跟踪文件"""
        validator = GitIgnoreValidator()

        with patch.object(validator, "run_git_command") as mock_command:
            mock_command.return_value = """?? file1.py
?? file2.py
?? directory/
 M modified_file.py"""

            result = validator.get_untracked_files()

            assert "file1.py" in result
            assert "file2.py" in result
            assert "directory/" in result
            assert "modified_file.py" not in result  # 已修改的文件不在未跟踪列表中

    def test_get_untracked_files_empty(self):
        """测试获取未跟踪文件为空"""
        validator = GitIgnoreValidator()

        with patch.object(validator, "run_git_command") as mock_command:
            mock_command.return_value = ""

            result = validator.get_untracked_files()

            assert len(result) == 0

    def test_exclude_patterns_count(self):
        """测试排除模式数量"""
        validator = GitIgnoreValidator()

        # 验证排除模式字典不为空
        assert len(validator.should_be_ignored) > 0

    def test_check_ignored_patterns_with_violations(self):
        """测试检查忽略模式发现违规"""
        validator = GitIgnoreValidator()

        with patch.object(validator, "get_untracked_files") as mock_untracked:
            # 模拟有未跟踪的Python缓存文件
            mock_untracked.return_value = [
                "some/__pycache__/file.pyc",
                "test.pyc",
                ".env",
                "normal.py",
            ]  # 正常文件

            validator.check_ignored_patterns()

            # 验证issues被添加
            assert len(validator.issues) > 0
            assert len(validator.successes) > 0

    def test_check_ignored_patterns_no_violations(self):
        """测试检查忽略模式无违规"""
        validator = GitIgnoreValidator()

        with patch.object(validator, "get_untracked_files") as mock_untracked:
            # 模拟没有违规文件
            mock_untracked.return_value = ["normal.py", "README.md", "config.json"]

            validator.check_ignored_patterns()

            # 验证只有successes，没有issues
            assert len(validator.issues) == 0
            assert len(validator.successes) > 0

    def test_check_exception_files_existing(self):
        """测试检查异常文件存在"""
        validator = GitIgnoreValidator()

        with patch("pathlib.Path.exists") as mock_exists:
            with patch.object(validator, "run_git_command") as mock_git:
                # 模拟文件存在且未被忽略
                mock_exists.return_value = True
                mock_git.return_value = ""  # 不被忽略

                validator.check_exception_files()

                # 验证successes被添加
                assert len(validator.successes) > 0

    def test_check_exception_files_missing(self):
        """测试检查异常文件不存在"""
        validator = GitIgnoreValidator()

        with patch("pathlib.Path.exists") as mock_exists:
            # 模拟文件不存在
            mock_exists.return_value = False

            validator.check_exception_files()

            # 验证warnings被添加
            assert len(validator.warnings) > 0

    def test_check_exception_files_ignored(self):
        """测试检查异常文件被忽略"""
        validator = GitIgnoreValidator()

        with patch("pathlib.Path.exists") as mock_exists:
            with patch.object(validator, "run_git_command") as mock_git:
                # 模拟文件存在但被忽略
                mock_exists.return_value = True
                mock_git.return_value = "ignored"  # 被忽略

                validator.check_exception_files()

                # 验证issues被添加
                assert len(validator.issues) > 0

    def test_check_gitignore_exists(self):
        """测试检查.gitignore文件存在"""
        validator = GitIgnoreValidator()

        with patch("pathlib.Path.exists") as mock_exists:
            # 模拟.gitignore文件存在
            mock_exists.return_value = True

            result = validator.check_gitignore_exists()

            assert result == True
            assert len(validator.successes) > 0

    def test_check_gitignore_missing(self):
        """测试检查.gitignore文件缺失"""
        validator = GitIgnoreValidator()

        with patch("pathlib.Path.exists") as mock_exists:
            # 模拟.gitignore文件不存在
            mock_exists.return_value = False

            result = validator.check_gitignore_exists()

            assert result == False
            assert len(validator.issues) > 0

    def test_generate_cleanup_commands(self):
        """测试生成清理命令"""
        validator = GitIgnoreValidator()

        # 添加一些issues
        validator.issues = [
            {
                "type": "NOT_IGNORED",
                "pattern": "__pycache__",
                "files": ["dir1/__pycache__", "dir2/__pycache__"],
                "total": 2,
            },
            {
                "type": "NOT_IGNORED",
                "pattern": "*.log",
                "files": ["debug.log", "error.log"],
                "total": 2,
            },
        ]

        commands = validator.generate_cleanup_commands()

        # 验证生成的清理命令
        assert any("__pycache__" in cmd for cmd in commands)
        assert any("*.log" in cmd for cmd in commands)

    def test_generate_report(self):
        """测试生成报告"""
        validator = GitIgnoreValidator()

        # 添加一些测试数据
        validator.issues = [
            {
                "type": "NOT_IGNORED",
                "pattern": "*.pyc",
                "files": ["test.pyc"],
                "total": 1,
            }
        ]
        validator.warnings = ["测试警告"]
        validator.successes = ["✅ 成功项1", "✅ 成功项2"]

        report = validator.generate_report()

        # 验证报告内容
        assert ".gitignore配置验证报告" in report
        assert "通过检查" in report
        assert "发现问题" in report
        assert "警告" in report
        assert "清理建议" in report

    def test_class_import_compatibility(self):
        """测试类导入兼容性"""
        try:
            from src.utils.validate_gitignore import GitIgnoreValidator

            validator = GitIgnoreValidator()
            assert validator is not None
            assert isinstance(validator, GitIgnoreValidator)
        except ImportError:
            pytest.skip("GitIgnoreValidator不可用")

    def test_attribute_types(self):
        """测试属性类型"""
        validator = GitIgnoreValidator()

        # 验证字典类型
        assert isinstance(validator.should_be_ignored, dict)
        assert isinstance(validator.should_be_visible, list)

        # 验证列表类型
        assert isinstance(validator.issues, list)
        assert isinstance(validator.warnings, list)
        assert isinstance(validator.successes, list)

    def test_regex_patterns_in_should_be_ignored(self):
        """测试should_be_ignored中的正则表达式"""
        validator = GitIgnoreValidator()

        # 验证正则表达式有效性
        for pattern_name, pattern_regex in validator.should_be_ignored.items():
            import re

            try:
                re.compile(pattern_regex)
            except re.error:
                pytest.fail(f"无效的正则表达式: {pattern_name} -> {pattern_regex}")

    def test_module_documentation(self):
        """测试模块文档"""
        import src.utils.validate_gitignore as gitignore_module

        assert gitignore_module.__doc__ is not None
        assert len(gitignore_module.__doc__.strip()) > 0
        assert "gitignore" in gitignore_module.__doc__.lower()

    def test_class_documentation(self):
        """测试类文档"""
        class_doc = GitIgnoreValidator.__doc__
        assert class_doc is not None
        assert len(class_doc.strip()) > 0
        assert "Git" in class_doc

    def test_validate_standards_check(self):
        """测试验收标准检查"""
        validator = GitIgnoreValidator()

        # 添加一个通过的验收标准
        validator.successes.append("✅ __pycache__ - 已正确忽略")

        report = validator.generate_report()

        # 验证验收标准部分存在
        assert "验收标准检查" in report
        assert "PASS" in report or "FAIL" in report

    def test_edge_cases(self):
        """测试边界情况"""
        validator = GitIgnoreValidator()

        # 测试空路径
        empty_validator = GitIgnoreValidator("")
        assert hasattr(empty_validator, "root_dir")

        # 测试非常长的路径
        long_path = "/very/long/path/that/should/still/work/for/validation"
        long_validator = GitIgnoreValidator(long_path)
        assert hasattr(long_validator, "root_dir")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__])
