#!/usr/bin/env python3
"""Support tests extracted from `scripts/tests/test_validate_gitignore.py`."""

from unittest.mock import patch

from src.utils.validate_gitignore import GitIgnoreValidator


class TestGenerateReport:
    """generate_report方法测试类"""

    def test_perfect_report_generation(self):
        """测试完美情况的报告生成"""
        validator = GitIgnoreValidator()
        validator.successes = ["✅ __pycache__ - 已正确忽略", "✅ *.pyc - 已正确忽略"]
        validator.issues = []
        validator.warnings = []

        with patch.object(validator, "check_gitignore_exists", return_value=True):
            with patch.object(validator, "check_ignored_patterns"):
                with patch.object(validator, "check_exception_files"):
                    report = validator.generate_report()

        assert ".gitignore配置验证报告" in report
        assert "📊 验证统计" in report
        assert "✅ 通过的检查" in report
        assert "🎉 所有验收标准通过" in report
        assert "验收标准检查" in report

    def test_report_with_issues(self):
        """测试包含问题的报告生成"""
        validator = GitIgnoreValidator()
        validator.issues = [
            {
                "type": "NOT_IGNORED",
                "pattern": "__pycache__",
                "files": ["__pycache__/module.pyc"],
                "total": 1,
            }
        ]
        validator.successes = ["✅ .env - 已正确忽略"]
        validator.warnings = ["⚠️  temp/README.md - 文件不存在（可选）"]

        with patch.object(validator, "check_gitignore_exists", return_value=True):
            with patch.object(validator, "check_ignored_patterns"):
                with patch.object(validator, "check_exception_files"):
                    report = validator.generate_report()

        assert "❌ 发现的问题" in report
        assert "__pycache__ 文件未被正确忽略" in report
        assert "⚠️  警告" in report
        assert "部分验收标准未通过" in report

    def test_report_with_wrongly_ignored_issues(self):
        """测试包含错误忽略问题的报告生成（覆盖第212行）"""
        validator = GitIgnoreValidator()
        validator.issues = [
            {
                "type": "WRONGLY_IGNORED",
                "file": ".env.example",
                "message": "应该可见但被忽略",
            }
        ]
        validator.successes = []
        validator.warnings = []

        with patch.object(validator, "check_gitignore_exists", return_value=True):
            with patch.object(validator, "check_ignored_patterns"):
                with patch.object(validator, "check_exception_files"):
                    report = validator.generate_report()

        assert "❌ 发现的问题" in report
        assert ".env.example - 应该可见但被忽略" in report

    def test_report_with_cleanup_suggestions(self):
        """测试包含清理建议的报告生成"""
        validator = GitIgnoreValidator()
        validator.issues = [
            {
                "type": "NOT_IGNORED",
                "pattern": "*.log",
                "files": ["app.log"],
                "total": 1,
            }
        ]

        with patch.object(validator, "check_gitignore_exists", return_value=True):
            with patch.object(validator, "check_ignored_patterns"):
                with patch.object(validator, "check_exception_files"):
                    with patch.object(validator, "generate_cleanup_commands") as mock_cleanup:
                        mock_cleanup.return_value = [
                            "# 清理日志文件",
                            "find . -name '*.log' -delete",
                        ]

                        report = validator.generate_report()

        assert "🧹 清理建议" in report
        assert "# 清理日志文件" in report

    def test_verification_criteria_section(self):
        """测试验收标准部分"""
        validator = GitIgnoreValidator()
        validator.issues = []

        with patch.object(validator, "check_gitignore_exists", return_value=True):
            with patch.object(validator, "check_ignored_patterns"):
                with patch.object(validator, "check_exception_files"):
                    report = validator.generate_report()

        criteria = [
            "git status不显示__pycache__目录",
            "git status不显示*.pyc文件",
            "git status不显示*.log文件",
            "git status不显示.env文件",
            ".gitignore文件存在",
        ]

        for criterion in criteria:
            assert f"✅ PASS - {criterion}" in report

    def test_failed_verification_criteria(self):
        """测试失败的验收标准"""
        validator = GitIgnoreValidator()
        validator.issues = [
            {
                "type": "NOT_IGNORED",
                "pattern": "__pycache__",
                "files": ["__pycache__/module.pyc"],
                "total": 1,
            }
        ]

        with patch.object(validator, "check_gitignore_exists", return_value=True):
            with patch.object(validator, "check_ignored_patterns"):
                with patch.object(validator, "check_exception_files"):
                    report = validator.generate_report()

        assert "❌ FAIL - git status不显示__pycache__目录" in report

    def test_report_formatting(self):
        """测试报告格式"""
        validator = GitIgnoreValidator()
        validator.successes = ["✅ Test success"]
        validator.issues = []
        validator.warnings = []

        with patch.object(validator, "check_gitignore_exists", return_value=True):
            with patch.object(validator, "check_ignored_patterns"):
                with patch.object(validator, "check_exception_files"):
                    report = validator.generate_report()

        assert "=" * 80 in report
        assert "📊" in report
        lines = report.split("\n")
        assert len(lines) > 20
