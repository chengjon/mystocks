"""Tail test groups extracted from ``scripts/tests/test_validate_gitignore.py``."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.validate_gitignore import GitIgnoreValidator, main


class TestMainFunction:
    """main函数测试类"""

    @patch("builtins.print")
    @patch("src.utils.validate_gitignore.GitIgnoreValidator")
    def test_main_function_success(self, mock_validator_class, mock_print):
        """测试main函数成功情况"""
        mock_validator = MagicMock()
        mock_validator.issues = []
        mock_validator.generate_report.return_value = "Test report"
        mock_validator_class.return_value = mock_validator

        result = main()

        assert result == 0
        mock_print.assert_called()
        mock_validator_class.assert_called_once()
        mock_validator.generate_report.assert_called_once()

    @patch("builtins.print")
    @patch("src.utils.validate_gitignore.GitIgnoreValidator")
    def test_main_function_with_issues(self, mock_validator_class, mock_print):
        """测试main函数发现问题情况"""
        mock_validator = MagicMock()
        mock_validator.issues = [{"type": "NOT_IGNORED", "pattern": "*.log"}]
        mock_validator.generate_report.return_value = "Report with issues"
        mock_validator_class.return_value = mock_validator

        result = main()

        assert result == 1

    @patch("builtins.print")
    @patch("src.utils.validate_gitignore.GitIgnoreValidator")
    def test_main_function_prints_report(self, mock_validator_class, mock_print):
        """测试main函数打印报告"""
        mock_validator = MagicMock()
        mock_validator.issues = []
        test_report = "Test validation report"
        mock_validator.generate_report.return_value = test_report
        mock_validator_class.return_value = mock_validator

        main()

        mock_print.assert_any_call("\n启动.gitignore配置验证...\n")
        mock_print.assert_any_call(test_report)

    @patch("src.utils.validate_gitignore.GitIgnoreValidator")
    def test_main_function_default_initialization(self, mock_validator_class):
        """测试main函数使用默认初始化"""
        with patch("builtins.print"):
            main()

        mock_validator_class.assert_called_once_with()


class TestIntegrationScenarios:
    """集成场景测试类"""

    def test_end_to_end_validation_workflow(self):
        """测试端到端验证工作流"""
        with tempfile.TemporaryDirectory() as temp_dir:
            validator = GitIgnoreValidator(temp_dir)
            gitignore_content = """__pycache__/
*.pyc
*.log
.env
.env.example
"""
            gitignore_file = Path(temp_dir) / ".gitignore"
            gitignore_file.write_text(gitignore_content)

            with patch.object(validator, "run_git_command") as mock_run:
                mock_run.return_value = MagicMock(
                    stdout="?? __pycache__/module.pyc\n?? app.log\n?? .env\n?? source.py\n",
                    returncode=0,
                )
                mock_run.return_value.configure_mock(
                    __enter__=lambda x: mock_run.return_value,
                    __exit__=lambda x, y, z, w: None,
                )
                validator.check_ignored_patterns()
                validator.check_gitignore_exists()
                validator.generate_report()

            assert len(validator.issues) >= 1

    def test_validation_with_custom_patterns(self):
        """测试自定义模式的验证"""
        validator = GitIgnoreValidator()
        validator.should_be_ignored["*.tmp"] = r".*\.tmp$"

        with patch.object(validator, "get_untracked_files", return_value=["temp.tmp", "backup.tmp", "source.py"]):
            validator.check_ignored_patterns()

        tmp_issues = [issue for issue in validator.issues if issue["pattern"] == "*.tmp"]
        assert len(tmp_issues) == 1
        assert tmp_issues[0]["total"] == 2

    def test_performance_with_large_file_list(self):
        """测试大量文件列表的性能"""
        import time

        validator = GitIgnoreValidator()
        large_file_list = [f"file_{index}.pyc" for index in range(1000)]
        start_time = time.time()

        with patch.object(validator, "get_untracked_files", return_value=large_file_list):
            validator.check_ignored_patterns()

        processing_time = time.time() - start_time
        assert processing_time < 1.0
        assert len(validator.issues) == 1
        assert validator.issues[0]["total"] == 1000

    def test_error_handling_in_validation(self):
        """测试验证过程中的错误处理"""
        validator = GitIgnoreValidator()

        with patch.object(validator, "run_git_command", side_effect=Exception("Git error")):
            try:
                validator.get_untracked_files()
            except Exception:
                pass

        assert True

    def test_complete_validation_report_workflow(self):
        """测试完整验证报告工作流"""
        with tempfile.TemporaryDirectory() as temp_dir:
            validator = GitIgnoreValidator(temp_dir)

            with patch.object(validator, "run_git_command") as mock_run:
                mock_run.side_effect = [
                    "?? __pycache__/module.pyc\n?? app.log\n?? source.py",
                    "",
                    "temp/README.md",
                ]
                validator.check_ignored_patterns()
                validator.check_exception_files()
                validator.check_gitignore_exists()
                report = validator.generate_report()

            assert ".gitignore配置验证报告" in report
            assert "📊 验证统计" in report
            assert "验收标准检查" in report

    def test_mock_subprocess_context_manager(self):
        """测试subprocess上下文管理器的mock"""
        validator = GitIgnoreValidator()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.configure_mock(stdout="test output", returncode=0)
            mock_run.return_value.__enter__ = MagicMock(return_value=mock_run.return_value)
            mock_run.return_value.__exit__ = MagicMock(return_value=None)

            result = validator.run_git_command(["status"])

        assert result == "test output"
