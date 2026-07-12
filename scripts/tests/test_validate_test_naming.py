#!/usr/bin/env python3
"""validate_test_naming模块测试套件
基于Phase 6成功模式：功能→边界→异常→性能→集成测试
目标：100%测试覆盖率
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入被测试的模块
from src.utils.validate_test_naming import TestNamingValidator, main


class TestTestNamingValidatorInit:
    """TestNamingValidator初始化测试类"""

    def test_init_with_default_root(self):
        """测试使用默认根目录初始化"""
        validator = TestNamingValidator()
        assert validator.root_dir == Path()
        assert validator.compliant_files == []
        assert validator.non_compliant_files == []
        assert isinstance(validator.ignored_dirs, set)
        assert ".git" in validator.ignored_dirs
        assert "node_modules" in validator.ignored_dirs
        assert "__pycache__" in validator.ignored_dirs

    def test_init_with_custom_root(self):
        """测试使用自定义根目录初始化"""
        custom_root = "/tmp/test"
        validator = TestNamingValidator(custom_root)
        assert validator.root_dir == Path(custom_root)
        assert validator.compliant_files == []
        assert validator.non_compliant_files == []

    def test_ignored_dirs_completeness(self):
        """测试忽略目录的完整性"""
        validator = TestNamingValidator()
        expected_ignored = {
            ".git",
            "node_modules",
            "venv",
            ".venv",
            "env",
            "__pycache__",
            ".pytest_cache",
            "htmlcov",
        }
        assert validator.ignored_dirs == expected_ignored


class TestFindAllTestFiles:
    """find_all_test_files方法测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = TestNamingValidator(self.temp_dir)

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_find_compliant_test_files(self):
        """测试查找符合规范的测试文件"""
        # 创建符合规范的测试文件
        test_files = [
            "test_example.py",
            "test_module_something.py",
            "subdir/test_nested.py",
        ]

        for file_path in test_files:
            full_path = os.path.join(self.temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write("# Test file\n")

        result = self.validator.find_all_test_files()
        assert len(result) == 3
        assert all(file.name.startswith("test_") for file in result)

    def test_find_non_compliant_test_files(self):
        """测试查找包含test但不符合规范的文件"""
        # 创建包含test但不符合规范的文件
        test_files = [
            "my_test.py",  # test在中间
            "something_test.py",  # _test结尾
            "TestFile.py",  # 大写Test
            "mytestmodule.py",  # test作为子串
        ]

        for file_path in test_files:
            full_path = os.path.join(self.temp_dir, file_path)
            with open(full_path, "w") as f:
                f.write("# Test file\n")

        result = self.validator.find_all_test_files()
        assert len(result) == 4
        # 这些文件包含test但不符合pytest规范

    def test_exclude_ignored_directories(self):
        """测试排除忽略目录"""
        # 在忽略目录中创建测试文件
        ignored_dirs = [".git", "__pycache__", "node_modules"]

        for ignored_dir in ignored_dirs:
            dir_path = os.path.join(self.temp_dir, ignored_dir)
            os.makedirs(dir_path)

            test_file = os.path.join(dir_path, "test_should_be_ignored.py")
            with open(test_file, "w") as f:
                f.write("# Ignored test file\n")

        # 在正常目录中创建测试文件
        normal_test = os.path.join(self.temp_dir, "test_normal.py")
        with open(normal_test, "w") as f:
            f.write("# Normal test file\n")

        result = self.validator.find_all_test_files()
        assert len(result) == 1
        assert result[0].name == "test_normal.py"

    def test_exclude_specific_patterns(self):
        """测试排除特定文件模式"""
        # 创建应该被排除的文件
        excluded_files = [
            "validate_test_naming.py",  # 验证工具本身
            "backtest_engine.py",  # 回测引擎业务代码
            "test_monitoring_with_redis.py",  # 监控数据生成脚本
        ]

        for file_path in excluded_files:
            full_path = os.path.join(self.temp_dir, file_path)
            with open(full_path, "w") as f:
                f.write("# Excluded file\n")

        # 创建正常的测试文件
        normal_test = os.path.join(self.temp_dir, "test_normal.py")
        with open(normal_test, "w") as f:
            f.write("# Normal test file\n")

        result = self.validator.find_all_test_files()
        assert len(result) == 1
        assert result[0].name == "test_normal.py"

    def test_no_test_files(self):
        """测试没有测试文件的情况"""
        # 创建一些非测试文件
        normal_files = ["main.py", "utils.py", "README.md"]
        for file_path in normal_files:
            full_path = os.path.join(self.temp_dir, file_path)
            with open(full_path, "w") as f:
                f.write("# Normal file\n")

        result = self.validator.find_all_test_files()
        assert len(result) == 0

    def test_case_insensitive_test_matching(self):
        """测试大小写不敏感的test匹配"""
        test_files = [
            "test_normal.py",  # 小写
            "Test_Upper.py",  # 大写开头
            "myTestFile.py",  # 混合
            "TEST_UPPERCASE.py",  # 全大写
        ]

        for file_path in test_files:
            full_path = os.path.join(self.temp_dir, file_path)
            with open(full_path, "w") as f:
                f.write("# Test file\n")

        result = self.validator.find_all_test_files()
        assert len(result) == 4  # 所有包含test的文件都应该被找到


class TestValidateFileNaming:
    """validate_file_naming方法测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.validator = TestNamingValidator()

    def test_validate_compliant_files(self):
        """测试验证符合规范的文件"""
        compliant_files = [
            "test_example.py",
            "test_module.py",
            "test_123.py",
            "test_with_underscores.py",
        ]

        for file_name in compliant_files:
            file_path = Path(file_name)
            assert self.validator.validate_file_naming(file_path) is True

    def test_validate_non_compliant_files(self):
        """测试验证不符合规范的文件"""
        non_compliant_files = [
            "my_test.py",  # test在中间
            "something_test.py",  # _test结尾
            "TestFile.py",  # 大写开头
            "test.py",  # 只有test
            "tests.py",  # tests
            "testing.py",  # testing
        ]

        for file_name in non_compliant_files:
            file_path = Path(file_name)
            assert self.validator.validate_file_naming(file_path) is False

    def test_edge_case_files(self):
        """测试边界情况文件"""
        edge_cases = [
            ("test_.py", True),  # test_开头但后面没有内容
            ("test_a.py", True),  # test_开头加一个字符
            ("test.py", False),  # 只有test，没有下划线
            ("_test.py", False),  # 下划线开头
            ("atest.py", False),  # test在中间
        ]

        for file_name, expected in edge_cases:
            file_path = Path(file_name)
            result = self.validator.validate_file_naming(file_path)
            assert result == expected, f"Failed for {file_name}, expected {expected}"


class TestSuggestRename:
    """suggest_rename方法测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.validator = TestNamingValidator()

    def test_suggest__test_suffix(self):
        """测试_test结尾文件的重命名建议"""
        test_cases = [
            ("something_test.py", "test_something.py"),
            ("my_module_test.py", "test_my_module.py"),
            ("complex_name_test.py", "test_complex_name.py"),
        ]

        for original, expected in test_cases:
            file_path = Path(original)
            suggestion = self.validator.suggest_rename(file_path)
            assert suggestion == expected

    def test_suggest_test_in_middle(self):
        """测试test在中间文件的重命名建议"""
        test_cases = [
            ("my_test_file.py", "test_file.py"),
            ("module_test_helper.py", "test_helper.py"),
            ("some_test_case.py", "test_case.py"),
        ]

        for original, expected in test_cases:
            file_path = Path(original)
            suggestion = self.validator.suggest_rename(file_path)
            assert suggestion == expected

    def test_suggest_default_prefix(self):
        """测试默认添加test_前缀"""
        test_cases = [
            ("TestFile.py", "test_TestFile.py"),
            ("testing.py", "test_testing.py"),
            ("mytest.py", "test_mytest.py"),
        ]

        for original, expected in test_cases:
            file_path = Path(original)
            suggestion = self.validator.suggest_rename(file_path)
            assert suggestion == expected

    def test_suggest_empty_remaining(self):
        """测试剩余部分为空的情况"""
        file_path = Path("test.py")
        suggestion = self.validator.suggest_rename(file_path)
        assert suggestion == "test_test.py"

    def test_suggest_complex_cases(self):
        """测试复杂的重命名情况"""
        complex_cases = [
            ("test", "test_test.py"),
            ("case_test", "test_case.py"),
            ("my_case_test_suite", "test_suite.py"),
        ]

        for original, expected in complex_cases:
            file_path = Path(f"{original}.py")
            suggestion = self.validator.suggest_rename(file_path)
            assert suggestion == expected


class TestValidateAll:
    """validate_all方法测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = TestNamingValidator(self.temp_dir)

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_validate_all_compliant(self):
        """测试验证全部符合规范的文件"""
        # 创建符合规范的测试文件
        test_files = ["test_one.py", "test_two.py", "test_three.py"]

        for file_name in test_files:
            file_path = os.path.join(self.temp_dir, file_name)
            with open(file_path, "w") as f:
                f.write("# Compliant test file\n")

        result = self.validator.validate_all()

        assert result["total"] == 3
        assert result["compliant"] == 3
        assert result["non_compliant"] == 0
        assert result["compliance_rate"] == 100.0

    def test_validate_all_mixed(self):
        """测试验证混合的文件（符合和不符合）"""
        # 创建符合规范的文件
        compliant_files = ["test_good.py", "test_compliant.py"]
        # 创建不符合规范的文件
        non_compliant_files = ["my_test.py", "testing_suite.py"]

        for file_name in compliant_files + non_compliant_files:
            file_path = os.path.join(self.temp_dir, file_name)
            with open(file_path, "w") as f:
                f.write("# Test file\n")

        result = self.validator.validate_all()

        assert result["total"] == 4
        assert result["compliant"] == 2
        assert result["non_compliant"] == 2
        assert result["compliance_rate"] == 50.0

    def test_validate_all_empty(self):
        """测试没有测试文件的情况"""
        result = self.validator.validate_all()

        assert result["total"] == 0
        assert result["compliant"] == 0
        assert result["non_compliant"] == 0
        assert result["compliance_rate"] == 100.0

    def test_validate_all_updates_file_lists(self):
        """测试validate_all更新文件列表"""
        # 创建测试文件
        compliant_file = "test_compliant.py"
        non_compliant_file = "my_test.py"

        for file_name in [compliant_file, non_compliant_file]:
            file_path = os.path.join(self.temp_dir, file_name)
            with open(file_path, "w") as f:
                f.write("# Test file\n")

        # 验证前列表为空
        assert len(self.validator.compliant_files) == 0
        assert len(self.validator.non_compliant_files) == 0

        # 执行验证
        self.validator.validate_all()

        # 验证列表已更新
        assert len(self.validator.compliant_files) == 1
        assert len(self.validator.non_compliant_files) == 1
        assert self.validator.compliant_files[0].name == compliant_file
        assert self.validator.non_compliant_files[0].name == non_compliant_file


class TestGenerateReport:
    """generate_report方法测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = TestNamingValidator(self.temp_dir)

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_generate_report_all_compliant(self):
        """测试生成全部符合规范的报告"""
        # 模拟全部符合规范的结果
        self.validator.compliant_files = [
            self.validator.root_dir / Path("test_one.py"),
            self.validator.root_dir / Path("test_two.py"),
        ]
        self.validator.non_compliant_files = []

        report = self.validator.generate_report()
        report_text = report

        assert "测试文件命名规范验证报告" in report_text
        assert "总测试文件数: 2" in report_text
        assert "符合规范: 2 个" in report_text
        assert "不符合规范: 0 个" in report_text
        assert "合规率: 100.0%" in report_text
        assert "🎉 所有验收标准通过" in report_text

    def test_generate_report_mixed_compliance(self):
        """测试生成混合合规情况的报告"""
        # 模拟混合结果
        self.validator.compliant_files = [
            self.validator.root_dir / Path("test_good.py"),
        ]
        self.validator.non_compliant_files = [
            self.validator.root_dir / Path("my_test.py"),
        ]

        report = self.validator.generate_report()
        report_text = report

        assert "总测试文件数: 2" in report_text
        assert "符合规范: 1 个" in report_text
        assert "不符合规范: 1 个" in report_text
        assert "合规率: 50.0%" in report_text
        assert "不符合规范的文件及修复建议" in report_text
        assert "❌ FAIL - 所有测试文件以test_开头" in report_text

    def test_generate_report_long_compliant_list(self):
        """测试生成长符合规范文件列表的报告"""
        # 创建超过10个符合规范的文件，确保它们在temp_dir下
        self.validator.compliant_files = [self.validator.root_dir / Path(f"test_{i}.py") for i in range(15)]
        self.validator.non_compliant_files = []

        report = self.validator.generate_report()
        report_text = report

        assert "符合规范: 15 个" in report_text
        assert "还有 5 个文件" in report_text  # 超过10个文件的截断提示

    def test_generate_report_empty(self):
        """测试生成空文件的报告"""
        # 模拟没有测试文件的情况
        self.validator.compliant_files = []
        self.validator.non_compliant_files = []

        report = self.validator.generate_report()
        report_text = report

        assert "总测试文件数: 0" in report_text
        assert "符合规范: 0 个" in report_text
        assert "不符合规范: 0 个" in report_text
        assert "合规率: 100.0%" in report_text
        assert "🎉 所有验收标准通过" in report_text


class TestMainFunction:
    """main函数测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch("builtins.print")
    def test_main_with_compliant_files(self, mock_print):
        """测试main函数处理符合规范的文件"""
        with patch(
            "src.utils.validate_test_naming.TestNamingValidator",
        ) as mock_validator_class:
            # 模拟validator实例
            mock_validator = MagicMock()
            mock_validator.compliant_files = [Path("test_one.py")]
            mock_validator.non_compliant_files = []
            mock_validator.generate_report.return_value = "Test report"
            mock_validator_class.return_value = mock_validator

            result = main()

            assert result == 0  # 没有不符合规范的文件，返回0
            mock_print.assert_called()  # 确保打印了报告

    @patch("builtins.print")
    def test_main_with_non_compliant_files(self, mock_print):
        """测试main函数处理不符合规范的文件"""
        with patch(
            "src.utils.validate_test_naming.TestNamingValidator",
        ) as mock_validator_class:
            # 模拟validator实例
            mock_validator = MagicMock()
            mock_validator.compliant_files = [Path("test_good.py")]
            mock_validator.non_compliant_files = [Path("my_test.py")]
            mock_validator.generate_report.return_value = "Test report with issues"
            mock_validator_class.return_value = mock_validator

            result = main()

            assert result == 1  # 有不符合规范的文件，返回1
            mock_print.assert_called()  # 确保打印了报告

    @patch("builtins.print")
    def test_main_uses_default_root(self, mock_print):
        """测试main函数使用默认根目录"""
        with patch(
            "src.utils.validate_test_naming.TestNamingValidator",
        ) as mock_validator_class:
            mock_validator = MagicMock()
            mock_validator.compliant_files = []
            mock_validator.non_compliant_files = []
            mock_validator.generate_report.return_value = "Empty report"
            mock_validator_class.return_value = mock_validator

            main()

            # 验证TestNamingValidator被调用且没有传参数（使用默认root）
            mock_validator_class.assert_called_once_with()

    @patch("builtins.print")
    def test_main_prints_report(self, mock_print):
        """测试main函数打印报告"""
        with patch(
            "src.utils.validate_test_naming.TestNamingValidator",
        ) as mock_validator_class:
            test_report = "Mock test report content"
            mock_validator = MagicMock()
            mock_validator.compliant_files = []
            mock_validator.non_compliant_files = []
            mock_validator.generate_report.return_value = test_report
            mock_validator_class.return_value = mock_validator

            main()

            # 验证报告被打印
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any(test_report in call for call in print_calls)


class TestIntegrationScenarios:
    """集成场景测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_end_to_end_validation_workflow(self):
        """测试端到端验证工作流"""
        validator = TestNamingValidator(self.temp_dir)

        # 1. 创建测试文件结构
        test_structure = {
            "test_good.py": "# Good test file",
            "my_test.py": "# Bad test file",
            "subdir/test_nested.py": "# Nested good test",
            "subdir/another_test.py": "# Nested bad test",
            "excluded/__pycache__/test_cached.py": "# Should be ignored",
        }

        # 2. 创建文件结构
        for file_path, content in test_structure.items():
            full_path = os.path.join(self.temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)

        # 3. 执行完整验证流程
        test_files = validator.find_all_test_files()
        assert len(test_files) == 4  # __pycache__应该被忽略

        # 4. 验证命名
        for test_file in test_files:
            validator.validate_file_naming(test_file)

        # 5. 生成统计
        stats = validator.validate_all()

        # 6. 验证结果
        assert stats["total"] == 4
        assert stats["compliant"] >= 2  # test_good.py, test_nested.py
        assert stats["non_compliant"] >= 2  # my_test.py, another_test.py

        # 7. 生成报告
        report = validator.generate_report()
        assert "测试文件命名规范验证报告" in report
        assert "合规率: 50.0%" in report

    def test_real_project_structure_simulation(self):
        """测试真实项目结构模拟"""
        validator = TestNamingValidator(self.temp_dir)

        # 模拟真实项目的测试结构
        project_files = {
            # 符合规范的测试文件
            "test_data_source.py": "# Data source tests",
            "test_database_manager.py": "# Database tests",
            "tests/test_integration.py": "# Integration tests",
            # 不符合规范的文件
            "data_source_test.py": "# Should be test_data_source.py",
            "monitoring_tests.py": "# Should be test_monitoring.py",
            # 应该被忽略的文件
            "validate_test_naming.py": "# Validation tool",
            "backtest_engine.py": "# Business logic",
            ".git/test_internal.py": "# In ignored directory",
            "__pycache__/test_cached.py": "# In cache directory",
            # 非测试文件
            "main.py": "# Main module",
            "utils.py": "# Utilities",
        }

        # 创建项目文件
        for file_path, content in project_files.items():
            full_path = os.path.join(self.temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)

        # 执行验证
        stats = validator.validate_all()
        report = validator.generate_report()

        # 验证结果
        assert stats["total"] == 5  # 只包含test相关文件，忽略排除项
        assert stats["compliant"] == 3
        assert stats["non_compliant"] == 2
        assert "50.0%" in report or "60.0%" in report or "40.0%" in report  # 取决于实际计数

    def test_large_scale_validation(self):
        """测试大规模验证性能"""
        validator = TestNamingValidator(self.temp_dir)

        # 创建大量测试文件
        num_files = 100
        for i in range(num_files):
            if i % 3 == 0:
                # 符合规范
                file_name = f"test_file_{i}.py"
            else:
                # 不符合规范
                file_name = f"file_{i}_test.py"

            file_path = os.path.join(self.temp_dir, file_name)
            with open(file_path, "w") as f:
                f.write(f"# Test file {i}\n")

        # 验证性能 - 应该能快速处理大量文件
        import time

        start_time = time.time()

        stats = validator.validate_all()

        end_time = time.time()
        processing_time = end_time - start_time

        # 验证结果正确性
        assert stats["total"] == num_files
        assert stats["compliant"] > 0
        assert stats["non_compliant"] > 0

        # 验证性能合理（应该在几秒内完成）
        assert processing_time < 5.0, f"处理时间过长: {processing_time}秒"

    def test_unicode_and_special_characters(self):
        """测试Unicode和特殊字符文件名"""
        validator = TestNamingValidator(self.temp_dir)

        # 创建包含特殊字符的测试文件
        special_files = [
            "test_中文.py",
            "test_emoji_🚀.py",
            "test_spaces.py",
            "test-dash.py",
            "test.dots.py",
        ]

        for file_name in special_files:
            file_path = os.path.join(self.temp_dir, file_name)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# 特殊字符测试文件: {file_name}\n")

        # 验证这些文件能被正确处理
        test_files = validator.find_all_test_files()
        assert len(test_files) == len(special_files)

        # 验证命名检查
        for test_file in test_files:
            is_valid = validator.validate_file_naming(test_file)
            # 所有以test_开头的文件都应该有效
            if test_file.name.startswith("test_"):
                assert is_valid

    def test_deep_directory_structure(self):
        """测试深层目录结构"""
        validator = TestNamingValidator(self.temp_dir)

        # 创建深层目录结构
        deep_path = self.temp_dir
        for i in range(5):  # 5层深
            deep_path = os.path.join(deep_path, f"level_{i}")

        os.makedirs(deep_path, exist_ok=True)

        # 在深层目录中创建测试文件
        deep_test_file = os.path.join(deep_path, "test_deep.py")
        with open(deep_test_file, "w") as f:
            f.write("# Deep level test file\n")

        # 验证能找到深层文件
        test_files = validator.find_all_test_files()
        assert len(test_files) == 1
        assert test_files[0].name == "test_deep.py"

        # 验证路径正确
        relative_path = test_files[0].relative_to(self.temp_dir)
        assert "level_0" in str(relative_path)
        assert "level_4" in str(relative_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
