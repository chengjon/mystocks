#!/usr/bin/env python3
"""validate_gitignore模块测试套件
基于Phase 6成功模式：功能→边界→异常→性能→集成测试
针对Git忽略规则验证器进行全面测试
"""

import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入被测试的模块
from src.utils.validate_gitignore import GitIgnoreValidator


class TestGitIgnoreValidatorInit:
    """GitIgnoreValidator初始化测试类"""

    def test_default_initialization(self):
        """测试默认初始化"""
        validator = GitIgnoreValidator()

        assert validator.root_dir == Path()
        assert isinstance(validator.should_be_ignored, dict)
        assert isinstance(validator.should_be_visible, list)
        assert isinstance(validator.issues, list)
        assert isinstance(validator.warnings, list)
        assert isinstance(validator.successes, list)

    def test_custom_root_directory(self):
        """测试自定义根目录初始化"""
        custom_dir = "/custom/path"
        validator = GitIgnoreValidator(custom_dir)

        assert validator.root_dir == Path(custom_dir)
        assert isinstance(validator.should_be_ignored, dict)

    def test_should_be_ignored_patterns(self):
        """测试应被忽略的文件模式配置"""
        validator = GitIgnoreValidator()

        expected_patterns = {
            "__pycache__": r"__pycache__/",
            "*.pyc": r".*\.pyc$",
            "*.log": r".*\.log$",
            ".env": r"\.env$",
            "*.swp": r".*\.swp$",
            "*.swo": r".*\.swo$",
            "node_modules": r"node_modules/",
            ".idea": r"\.idea/",
            ".vscode": r"\.vscode/",
            ".DS_Store": r"\.DS_Store$",
            "Thumbs.db": r"Thumbs\.db$",
        }

        assert validator.should_be_ignored == expected_patterns

    def test_should_be_visible_files(self):
        """测试应该可见的文件配置"""
        validator = GitIgnoreValidator()

        expected_visible = [
            ".env.example",
            "temp/README.md",
            "data/backups/.gitkeep",
        ]

        assert validator.should_be_visible == expected_visible


class TestRunGitCommand:
    """run_git_command方法测试类"""

    def test_successful_git_command(self):
        """测试成功的git命令执行"""
        validator = GitIgnoreValidator()

        mock_output = "file1.txt\nfile2.py\n__pycache__/"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=mock_output, returncode=0)
            mock_run.return_value.configure_mock(
                __enter__=lambda x: mock_run.return_value,
                __exit__=lambda x, y, z, w: None,
            )

            result = validator.run_git_command(["status", "--short"])

            assert result == mock_output
            mock_run.assert_called_once_with(
                ["git", "status", "--short"],
                cwd=validator.root_dir,
                capture_output=True,
                text=True,
                check=True,
            )

    def test_git_command_failure(self):
        """测试git命令执行失败"""
        validator = GitIgnoreValidator()

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "git")

            result = validator.run_git_command(["invalid-command"])

            assert result == ""

    def test_git_command_with_different_args(self):
        """测试不同参数的git命令"""
        validator = GitIgnoreValidator()

        test_cases = [
            ["status"],
            ["status", "--short"],
            ["check-ignore", "file.txt"],
            ["log", "--oneline", "-5"],
        ]

        for args in test_cases:
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(stdout="output", returncode=0)
                mock_run.return_value.configure_mock(
                    __enter__=lambda x: mock_run.return_value,
                    __exit__=lambda x, y, z, w: None,
                )

                validator.run_git_command(args)

                mock_run.assert_called_once_with(
                    ["git"] + args,
                    cwd=validator.root_dir,
                    capture_output=True,
                    text=True,
                    check=True,
                )


class TestGetUntrackedFiles:
    """get_untracked_files方法测试类"""

    def test_parse_untracked_files(self):
        """测试解析未跟踪文件"""
        validator = GitIgnoreValidator()

        mock_status_output = """?? __pycache__/module.cpython-311.pyc
?? test.log
?? .env
?? file.py
?? temp/test.py
?? .DS_Store
 M tracked_file.txt
"""

        with patch.object(
            validator,
            "run_git_command",
            return_value=mock_status_output,
        ):
            untracked = validator.get_untracked_files()

            expected_files = [
                "__pycache__/module.cpython-311.pyc",
                "test.log",
                ".env",
                "file.py",
                "temp/test.py",
                ".DS_Store",
            ]

            assert untracked == expected_files

    def test_empty_untracked_files(self):
        """测试没有未跟踪文件"""
        validator = GitIgnoreValidator()

        with patch.object(validator, "run_git_command", return_value=""):
            untracked = validator.get_untracked_files()

            assert untracked == []

    def test_no_untracked_files_output(self):
        """测试没有未跟踪文件输出的情况"""
        validator = GitIgnoreValidator()

        mock_output = """ M tracked_file.txt
A  added_file.txt
 D  deleted_file.txt
"""

        with patch.object(validator, "run_git_command", return_value=mock_output):
            untracked = validator.get_untracked_files()

            assert untracked == []

    def test_whitespace_handling(self):
        """测试空白字符处理"""
        validator = GitIgnoreValidator()

        mock_output = """?? file with spaces.py
??   indented_file.txt
??

?? file_after_blank.txt
"""

        with patch.object(validator, "run_git_command", return_value=mock_output):
            untracked = validator.get_untracked_files()

            expected = [
                "file with spaces.py",
                "indented_file.txt",
                "file_after_blank.txt",
            ]

            # 过滤空行
            untracked_filtered = [f for f in untracked if f.strip()]
            assert untracked_filtered == expected


class TestCheckIgnoredPatterns:
    """check_ignored_patterns方法测试类"""

    def test_no_violations_found(self):
        """测试没有发现违规文件"""
        validator = GitIgnoreValidator()

        # 模拟没有匹配应忽略模式的未跟踪文件
        untracked_files = [
            "source.py",
            "README.md",
            "config.json",
        ]

        with patch.object(
            validator,
            "get_untracked_files",
            return_value=untracked_files,
        ):
            validator.check_ignored_patterns()

            assert len(validator.issues) == 0
            assert len(validator.successes) > 0

    def test_pycache_violations(self):
        """测试__pycache__违规"""
        validator = GitIgnoreValidator()

        untracked_files = [
            "__pycache__/module1.cpython-311.pyc",
            "__pycache__/module2.cpython-311.pyc",
            "__pycache__/subdir/",
        ]

        with patch.object(
            validator,
            "get_untracked_files",
            return_value=untracked_files,
        ):
            validator.check_ignored_patterns()

            pycache_issues = [i for i in validator.issues if i["pattern"] == "__pycache__"]
            assert len(pycache_issues) == 1
            assert pycache_issues[0]["total"] == 3

    def test_pyc_file_violations(self):
        """测试*.pyc文件违规"""
        validator = GitIgnoreValidator()

        untracked_files = [
            "module1.pyc",
            "module2.cpython-311.pyc",
            "dir/submodule.pyc",
        ]

        with patch.object(
            validator,
            "get_untracked_files",
            return_value=untracked_files,
        ):
            validator.check_ignored_patterns()

            pyc_issues = [i for i in validator.issues if i["pattern"] == "*.pyc"]
            assert len(pyc_issues) == 1
            assert pyc_issues[0]["total"] == 3

    def test_log_file_violations(self):
        """测试日志文件违规"""
        validator = GitIgnoreValidator()

        untracked_files = [
            "app.log",
            "debug.log",
        ]

        with patch.object(
            validator,
            "get_untracked_files",
            return_value=untracked_files,
        ):
            validator.check_ignored_patterns()

            log_issues = [i for i in validator.issues if i["pattern"] == "*.log"]
            assert len(log_issues) == 1
            assert log_issues[0]["total"] == 2

    def test_env_file_violations(self):
        """测试.env文件违规"""
        validator = GitIgnoreValidator()

        untracked_files = [
            ".env",
        ]

        with patch.object(
            validator,
            "get_untracked_files",
            return_value=untracked_files,
        ):
            validator.check_ignored_patterns()

            env_issues = [i for i in validator.issues if i["pattern"] == ".env"]
            assert len(env_issues) == 1
            assert env_issues[0]["total"] == 1

    def test_multiple_violations(self):
        """测试多种违规模式"""
        validator = GitIgnoreValidator()

        untracked_files = [
            "__pycache__/module.pyc",
            "test.pyc",
            "app.log",
            ".env",
            "temp.swp",
            "node_modules/package/",
            ".idea/workspace.xml",
        ]

        with patch.object(
            validator,
            "get_untracked_files",
            return_value=untracked_files,
        ):
            validator.check_ignored_patterns()

            # 应该发现多个违规
            violated_patterns = {issue["pattern"] for issue in validator.issues}
            expected_patterns = {
                "__pycache__",
                "*.pyc",
                "*.log",
                ".env",
                "*.swp",
                "node_modules",
                ".idea",
            }

            assert len(violated_patterns) >= 5  # 至少5种违规

    def test_file_limit_truncation(self):
        """测试文件列表截断（只显示前5个）"""
        validator = GitIgnoreValidator()

        # 创建超过5个违规文件
        untracked_files = [f"file_{i}.pyc" for i in range(10)]

        with patch.object(
            validator,
            "get_untracked_files",
            return_value=untracked_files,
        ):
            validator.check_ignored_patterns()

            pyc_issues = [i for i in validator.issues if i["pattern"] == "*.pyc"]
            assert len(pyc_issues) == 1
            assert pyc_issues[0]["total"] == 10
            assert len(pyc_issues[0]["files"]) == 5  # 只显示前5个

    def test_success_messages_generation(self):
        """测试成功消息生成"""
        validator = GitIgnoreValidator()

        # 没有违规的情况
        untracked_files = ["source.py", "README.md"]

        with patch.object(
            validator,
            "get_untracked_files",
            return_value=untracked_files,
        ):
            validator.check_ignored_patterns()

            # 应该有成功消息
            assert len(validator.successes) > 0
            assert any("✅" in success for success in validator.successes)


class TestCheckExceptionFiles:
    """check_exception_files方法测试类"""

    def test_existing_visible_files(self):
        """测试应该可见的文件存在且可见"""
        validator = GitIgnoreValidator()

        # 创建临时文件
        with tempfile.TemporaryDirectory() as temp_dir:
            validator.root_dir = Path(temp_dir)

            # 创建应该可见的文件
            for file_path in validator.should_be_visible:
                full_path = validator.root_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text("test content")

            with patch.object(validator, "run_git_command", return_value=""):
                validator.check_exception_files()

                assert len(validator.issues) == 0
                assert len(validator.successes) >= len(validator.should_be_visible)

    def test_missing_visible_files(self):
        """测试应该可见的文件不存在"""
        validator = GitIgnoreValidator()

        with patch.object(validator, "run_git_command", return_value=""):
            validator.check_exception_files()

            # 应该有文件不存在的警告
            missing_warnings = [w for w in validator.warnings if "不存在" in w]
            assert len(missing_warnings) >= 2  # 至少有2个文件不存在

    def test_wrongly_ignored_files(self):
        """测试应该可见但被忽略的文件"""
        validator = GitIgnoreValidator()

        with tempfile.TemporaryDirectory() as temp_dir:
            validator.root_dir = Path(temp_dir)

            # 创建文件
            test_file = validator.root_dir / ".env.example"
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text("example env")

            # 模拟git check-ignore返回内容（表示文件被忽略）
            with patch.object(
                validator,
                "run_git_command",
                return_value=".env.example",
            ):
                validator.check_exception_files()

                ignore_issues = [i for i in validator.issues if i["type"] == "WRONGLY_IGNORED"]
                assert len(ignore_issues) == 1
                assert ignore_issues[0]["file"] == ".env.example"

    def test_partial_visible_files(self):
        """测试部分可见文件存在"""
        validator = GitIgnoreValidator()

        with tempfile.TemporaryDirectory() as temp_dir:
            validator.root_dir = Path(temp_dir)

            # 只创建部分文件
            created_file = validator.should_be_visible[0]
            full_path = validator.root_dir / created_file
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text("test")

            with patch.object(validator, "run_git_command", return_value=""):
                validator.check_exception_files()

                # 应该有成功消息和警告
                assert len(validator.successes) >= 1
                assert len(validator.warnings) >= 2  # 其他2个文件不存在


class TestCheckGitignoreExists:
    """check_gitignore_exists方法测试类"""

    def test_all_gitignore_files_exist(self):
        """测试所有.gitignore文件都存在"""
        validator = GitIgnoreValidator()

        with tempfile.TemporaryDirectory() as temp_dir:
            validator.root_dir = Path(temp_dir)

            # 创建所有.gitignore文件
            gitignore_files = [
                validator.root_dir / ".gitignore",
                validator.root_dir / "web" / "frontend" / ".gitignore",
            ]

            for gitignore_file in gitignore_files:
                gitignore_file.parent.mkdir(parents=True, exist_ok=True)
                gitignore_file.write_text("# Git ignore rules")

            result = validator.check_gitignore_exists()

            assert result == True
            assert len(validator.issues) == 0
            assert len(validator.successes) >= 2

    def test_missing_gitignore_files(self):
        """测试缺少.gitignore文件"""
        validator = GitIgnoreValidator()

        with tempfile.TemporaryDirectory() as temp_dir:
            validator.root_dir = Path(temp_dir)
            # 不创建任何.gitignore文件

            result = validator.check_gitignore_exists()

            assert result == False
            assert len(validator.issues) == 2
            assert all(issue["type"] == "MISSING_GITIGNORE" for issue in validator.issues)

    def test_partial_gitignore_files_exist(self):
        """测试部分.gitignore文件存在"""
        validator = GitIgnoreValidator()

        with tempfile.TemporaryDirectory() as temp_dir:
            validator.root_dir = Path(temp_dir)

            # 只创建根目录的.gitignore
            root_gitignore = validator.root_dir / ".gitignore"
            root_gitignore.parent.mkdir(parents=True, exist_ok=True)
            root_gitignore.write_text("# Root gitignore")

            result = validator.check_gitignore_exists()

            assert result == False
            assert len(validator.issues) == 1  # web/frontend/.gitignore缺失
            assert len(validator.successes) == 1


class TestGenerateCleanupCommands:
    """generate_cleanup_commands方法测试类"""

    def test_pycache_cleanup_commands(self):
        """测试__pycache__清理命令"""
        validator = GitIgnoreValidator()
        validator.issues = [
            {
                "type": "NOT_IGNORED",
                "pattern": "__pycache__",
                "files": ["__pycache__/module.pyc"],
                "total": 1,
            },
        ]

        commands = validator.generate_cleanup_commands()

        assert any("清理Python缓存" in cmd for cmd in commands)
        assert any("find . -type d -name '__pycache__'" in cmd for cmd in commands)
        assert any("*.pyc" in cmd for cmd in commands)

    def test_log_file_cleanup_commands(self):
        """测试日志文件清理命令"""
        validator = GitIgnoreValidator()
        validator.issues = [
            {
                "type": "NOT_IGNORED",
                "pattern": "*.log",
                "files": ["app.log"],
                "total": 1,
            },
        ]

        commands = validator.generate_cleanup_commands()

        assert any("清理日志文件" in cmd for cmd in commands)
        assert any("find . -type f -name '*.log' -delete" in cmd for cmd in commands)

    def test_node_modules_cleanup_commands(self):
        """测试node_modules清理命令"""
        validator = GitIgnoreValidator()
        validator.issues = [
            {
                "type": "NOT_IGNORED",
                "pattern": "node_modules",
                "files": ["node_modules/package/"],
                "total": 1,
            },
        ]

        commands = validator.generate_cleanup_commands()

        assert any("Node.js依赖" in cmd for cmd in commands)
        assert any("node_modules" in cmd for cmd in commands)

    def test_no_cleanup_commands_for_non_file_issues(self):
        """测试非文件问题不生成清理命令"""
        validator = GitIgnoreValidator()
        validator.issues = [
            {"type": "MISSING_GITIGNORE", "file": ".gitignore", "message": "文件缺失"},
            {
                "type": "WRONGLY_IGNORED",
                "file": ".env.example",
                "message": "被错误忽略",
            },
        ]

        commands = validator.generate_cleanup_commands()

        assert len(commands) == 0

    def test_multiple_violation_cleanup_commands(self):
        """测试多种违规的清理命令"""
        validator = GitIgnoreValidator()
        validator.issues = [
            {
                "type": "NOT_IGNORED",
                "pattern": "__pycache__",
                "files": ["__pycache__/module.pyc"],
                "total": 1,
            },
            {
                "type": "NOT_IGNORED",
                "pattern": "*.log",
                "files": ["app.log"],
                "total": 1,
            },
        ]

        commands = validator.generate_cleanup_commands()

        assert len(commands) >= 4  # 2个标题 + 2个清理命令


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
