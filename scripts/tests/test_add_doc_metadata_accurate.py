#!/usr/bin/env python3
"""add_doc_metadata模块准确测试套件
基于实际源代码函数签名和行为编写测试
遵循Phase 6成功模式：功能→边界→异常→性能→集成测试
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest


# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入被测试的模块
from src.utils.add_doc_metadata import (
    METADATA_TEMPLATE,
    add_metadata,
    batch_add_metadata,
    main,
)


class TestAddMetadata:
    """add_metadata函数核心功能测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()
        self.test_file_path = os.path.join(self.temp_dir, "test_document.md")

        # 创建测试文档
        with open(self.test_file_path, "w", encoding="utf-8") as f:
            f.write("# 测试文档\n\n这是一个测试文档的内容。\n")

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        # 清理临时目录
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_add_basic_metadata(self):
        """测试基本元数据添加"""
        creator = "测试创建人"
        version = "1.0.0"

        add_metadata(self.test_file_path, creator, version)

        # 验证元数据被添加
        with open(self.test_file_path, encoding="utf-8") as f:
            content = f.read()

        assert f"**创建人**: {creator}" in content
        assert f"**版本**: {version}" in content
        assert "**批准日期**:" in content
        assert "**最后修订**:" in content
        assert "**本次修订内容**: 添加文档元数据标记" in content
        assert "---" in content

    def test_add_metadata_with_custom_notes(self):
        """测试添加自定义修订说明"""
        creator = "测试创建人"
        version = "1.0.0"
        revision_notes = "更新了API文档"
        approved_date = "2024-01-01"

        add_metadata(
            self.test_file_path,
            creator,
            version,
            approved_date,
            revision_notes,
        )

        # 验证自定义元数据
        with open(self.test_file_path, encoding="utf-8") as f:
            content = f.read()

        assert f"**创建人**: {creator}" in content
        assert f"**版本**: {version}" in content
        assert f"**批准日期**: {approved_date}" in content
        assert f"**本次修订内容**: {revision_notes}" in content

    def test_add_metadata_with_chinese_date(self):
        """测试中文日期格式"""
        creator = "张三"
        version = "2.0.0"
        approved_date = "2024年12月22日"

        add_metadata(self.test_file_path, creator, version, approved_date)

        with open(self.test_file_path, encoding="utf-8") as f:
            content = f.read()

        assert f"**批准日期**: {approved_date}" in content

    def test_add_metadata_preserves_original_content(self):
        """测试添加元数据时保留原文内容"""
        original_content = "# 原始文档标题\n\n这是原始内容。\n## 章节1\n内容1\n"

        with open(self.test_file_path, "w", encoding="utf-8") as f:
            f.write(original_content)

        add_metadata(self.test_file_path, "创建人", "1.0.0")

        with open(self.test_file_path, encoding="utf-8") as f:
            content = f.read()

        # 验证原文内容被保留
        assert original_content in content
        # 验证元数据被添加到开头
        assert content.startswith("**创建人**: 创建人")

    def test_add_metadata_unicode_content(self):
        """测试包含Unicode字符的文档"""
        unicode_content = "# Unicode测试文档\n\n测试内容：🚀💻📊 中文字符和emoji"

        with open(self.test_file_path, "w", encoding="utf-8") as f:
            f.write(unicode_content)

        add_metadata(self.test_file_path, "张三👨‍💻", "版本1.0")

        with open(self.test_file_path, encoding="utf-8") as f:
            content = f.read()

        assert unicode_content in content
        assert "张三👨‍💻" in content
        assert "版本1.0" in content

    def test_add_metadata_special_characters(self):
        """测试特殊字符处理"""
        creator = "John & Jane O'Reilly"
        version = "v1.2.3-beta"
        revision_notes = "包含特殊字符: @#$%^&*()_+-=[]{}|;':\",./<>?"

        add_metadata(
            self.test_file_path,
            creator,
            version,
            revision_notes=revision_notes,
        )

        with open(self.test_file_path, encoding="utf-8") as f:
            content = f.read()

        assert creator in content
        assert version in content
        assert revision_notes in content


class TestAddMetadataEdgeCases:
    """add_metadata函数边界条件和异常处理测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_add_metadata_nonexistent_file(self):
        """测试不存在的文件"""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.md")

        with pytest.raises(FileNotFoundError):
            add_metadata(nonexistent_file, "创建人", "1.0.0")

    def test_add_metadata_empty_file(self):
        """测试空文件"""
        empty_file = os.path.join(self.temp_dir, "empty.md")

        # 创建空文件
        with open(empty_file, "w", encoding="utf-8") as f:
            pass

        add_metadata(empty_file, "创建人", "1.0.0")

        with open(empty_file, encoding="utf-8") as f:
            content = f.read()

        assert "**创建人**: 创建人" in content
        assert "**版本**: 1.0.0" in content

    def test_add_metadata_long_creator_name(self):
        """测试超长的创建人名称"""
        long_creator = "A" * 1000  # 1000个字符
        test_file = os.path.join(self.temp_dir, "long_creator.md")

        with open(test_file, "w", encoding="utf-8") as f:
            f.write("内容")

        # 应该能处理长名称
        add_metadata(test_file, long_creator, "1.0.0")

        with open(test_file, encoding="utf-8") as f:
            content = f.read()

        assert long_creator in content

    def test_add_metadata_empty_creator_name(self):
        """测试空的创建人名称"""
        test_file = os.path.join(self.temp_dir, "empty_creator.md")

        with open(test_file, "w", encoding="utf-8") as f:
            f.write("内容")

        add_metadata(test_file, "", "1.0.0")

        with open(test_file, encoding="utf-8") as f:
            content = f.read()

        assert "**创建人**: " in content

    def test_add_metadata_empty_version(self):
        """测试空的版本号"""
        test_file = os.path.join(self.temp_dir, "empty_version.md")

        with open(test_file, "w", encoding="utf-8") as f:
            f.write("内容")

        add_metadata(test_file, "创建人", "")

        with open(test_file, encoding="utf-8") as f:
            content = f.read()

        assert "**版本**: " in content

    def test_add_metadata_none_parameters(self):
        """测试None参数"""
        test_file = os.path.join(self.temp_dir, "none_params.md")

        with open(test_file, "w", encoding="utf-8") as f:
            f.write("内容")

        # approved_date应该能接受None
        add_metadata(test_file, "创建人", "1.0.0", None)

        with open(test_file, encoding="utf-8") as f:
            content = f.read()

        assert "**创建人**: 创建人" in content
        assert "**版本**: 1.0.0" in content


class TestBatchAddMetadata:
    """batch_add_metadata函数测试类"""

    def test_batch_add_metadata_structure(self):
        """测试批量添加元数据函数结构"""
        # 这个函数不接受参数，处理预定义的文档列表
        with patch("builtins.open", mock_open(read_data="content")) as mock_file:
            with patch("os.path.exists", return_value=True):
                with patch("src.utils.add_doc_metadata.add_metadata") as mock_add:
                    batch_add_metadata()

                    # 验证函数被调用（应该处理预定义的文档列表）
                    assert mock_add.called

    def test_batch_add_metadata_mock_calls(self):
        """测试批量添加元数据的调用模式"""
        # 模拟核心文档存在的情况
        mock_files = []
        for doc_info in [
            ("README.md", "JohnC & Claude", "2.1.0"),
            ("CHANGELOG_v2.1.md", "Claude", "2.1.0"),
            ("QUICKSTART.md", "Claude", "2.1.0"),
        ]:
            mock_file = MagicMock()
            mock_files.append((doc_info[0], mock_file))

        with patch("src.utils.add_doc_metadata.add_metadata") as mock_add:
            batch_add_metadata()

            # 验证对预定义文档的调用
            assert mock_add.called

    def test_batch_add_metadata_no_parameters(self):
        """测试batch_add_metadata不接受参数"""
        # 确保函数不接受任何参数
        import inspect

        sig = inspect.signature(batch_add_metadata)
        assert len(sig.parameters) == 0

    def test_batch_add_metadata_exception_handling(self):
        """测试批量添加元数据时的异常处理（覆盖179-181行）"""
        # 模拟add_metadata抛出异常的情况
        with patch("src.utils.add_doc_metadata.add_metadata") as mock_add:
            # 设置第一次调用正常，第二次调用抛出异常
            mock_add.side_effect = [True, Exception("模拟异常"), False]

            with patch("builtins.print") as mock_print:
                batch_add_metadata()

                # 验证异常消息被打印（包含"❌"的消息）
                error_calls = [call for call in mock_print.call_args_list if "❌" in str(call)]
                assert len(error_calls) > 0
                # 验证统计数据被打印
                print_calls = [str(call) for call in mock_print.call_args_list if "完成统计" in str(call)]
                assert len(print_calls) > 0


class TestMainFunction:
    """main函数测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.md")

        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("测试内容")

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_main_with_doc_argument(self):
        """测试使用--doc参数的main函数"""
        test_args = [
            "--doc",
            self.test_file,
            "--creator",
            "命令行创建人",
            "--version",
            "1.0.0",
        ]

        with patch("sys.argv", ["add_doc_metadata.py"] + test_args):
            main()

        with open(self.test_file, encoding="utf-8") as f:
            content = f.read()

        assert "**创建人**: 命令行创建人" in content
        assert "**版本**: 1.0.0" in content

    def test_main_with_batch_argument(self):
        """测试使用--batch参数的main函数"""
        test_args = ["--batch"]

        with patch("sys.argv", ["add_doc_metadata.py"] + test_args):
            with patch("src.utils.add_doc_metadata.batch_add_metadata") as mock_batch:
                main()

                mock_batch.assert_called_once()

    def test_main_with_defaults(self):
        """测试使用默认参数的main函数"""
        test_args = ["--doc", self.test_file]  # 只指定doc，使用默认creator和version

        with patch("sys.argv", ["add_doc_metadata.py"] + test_args):
            main()

        with open(self.test_file, encoding="utf-8") as f:
            content = f.read()

        assert "**创建人**: Claude" in content  # 默认值
        assert "**版本**: 1.0.0" in content  # 默认值

    def test_main_with_both_doc_and_batch(self):
        """测试同时指定doc和batch参数"""
        test_args = ["--doc", self.test_file, "--batch"]

        with patch("sys.argv", ["add_doc_metadata.py"] + test_args):
            # argparse应该处理这种冲突
            with pytest.raises(SystemExit):
                main()

    def test_main_neither_doc_nor_batch(self):
        """测试既不指定doc也不指定batch参数"""
        test_args = []  # 空参数列表

        with patch("sys.argv", ["add_doc_metadata.py"] + test_args):
            # 应该显示帮助信息并退出
            with pytest.raises(SystemExit):
                main()

    def test_main_help_argument(self):
        """测试帮助参数"""
        test_args = ["--help"]

        with patch("sys.argv", ["add_doc_metadata.py"] + test_args), pytest.raises(SystemExit):
            main()

    def test_main_invalid_file_path(self):
        """测试无效文件路径"""
        invalid_file = os.path.join(self.temp_dir, "nonexistent.md")
        test_args = ["--doc", invalid_file, "--creator", "创建人", "--version", "1.0.0"]

        with patch("sys.argv", ["add_doc_metadata.py"] + test_args):
            # 应该处理文件不存在的情况
            with patch("builtins.print") as mock_print:
                with patch(
                    "src.utils.add_doc_metadata.add_metadata",
                    side_effect=FileNotFoundError,
                ):
                    main()

                    # 验证错误消息被打印
                    mock_print.assert_called()

    def test_main_argument_parsing(self):
        """测试参数解析"""
        test_args = [
            "--doc",
            self.test_file,
            "--creator",
            "特定创建人",
            "--version",
            "特定版本号",
        ]

        with patch("sys.argv", ["add_doc_metadata.py"] + test_args):
            with patch("src.utils.add_doc_metadata.add_metadata") as mock_add:
                main()

                # 验证调用使用了正确的参数
                mock_add.assert_called_once_with(
                    self.test_file,
                    "特定创建人",
                    "特定版本号",
                )


class TestMetadataTemplate:
    """元数据模板测试类"""

    def test_metadata_template_format(self):
        """测试元数据模板格式"""
        # 模板应该包含所有必需的占位符
        assert "{creator}" in METADATA_TEMPLATE
        assert "{version}" in METADATA_TEMPLATE
        assert "{approved_date}" in METADATA_TEMPLATE
        assert "{last_modified}" in METADATA_TEMPLATE
        assert "{revision_notes}" in METADATA_TEMPLATE

    def test_metadata_template_structure(self):
        """测试元数据模板结构"""
        lines = METADATA_TEMPLATE.strip().split("\n")

        # 验证包含关键行
        assert any("**创建人**:" in line for line in lines)
        assert any("**版本**:" in line for line in lines)
        assert any("**批准日期**:" in line for line in lines)
        assert any("**最后修订**:" in line for line in lines)
        assert any("**本次修订内容**:" in line for line in lines)


class TestIntegrationScenarios:
    """集成场景测试类"""

    def test_end_to_end_single_file_workflow(self):
        """测试单文件端到端工作流"""
        temp_dir = tempfile.mkdtemp()
        try:
            # 1. 创建文档
            doc_file = os.path.join(temp_dir, "project_documentation.md")
            with open(doc_file, "w", encoding="utf-8") as f:
                f.write("# 项目文档\n\n这是项目的详细说明文档。\n")

            # 2. 使用main函数添加元数据
            test_args = [
                "--doc",
                doc_file,
                "--creator",
                "集成测试创建人",
                "--version",
                "2.0.0",
            ]

            with patch("sys.argv", ["add_doc_metadata.py"] + test_args):
                main()

            # 3. 验证最终状态
            with open(doc_file, encoding="utf-8") as f:
                final_content = f.read()

            # 验证元数据存在
            assert "**创建人**: 集成测试创建人" in final_content
            assert "**版本**: 2.0.0" in final_content

            # 验证原文内容保留
            assert "# 项目文档" in final_content
            assert "这是项目的详细说明文档" in final_content

        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def test_multiple_files_workflow(self):
        """测试多文件工作流"""
        temp_dir = tempfile.mkdtemp()
        try:
            # 创建多个文档
            documents = {
                "README.md": "# 项目说明\n\n项目的基本介绍。",
                "API.md": "# API文档\n\n接口详细说明。",
                "CHANGELOG.md": "# 变更日志\n\n版本更新记录。",
            }

            for filename, content in documents.items():
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

            # 为每个文件添加元数据
            for filename in documents:
                file_path = os.path.join(temp_dir, filename)
                test_args = [
                    "--doc",
                    file_path,
                    "--creator",
                    "多文档创建人",
                    "--version",
                    "1.0.0",
                ]

                with patch("sys.argv", ["add_doc_metadata.py"] + test_args):
                    main()

            # 验证所有文档都被正确处理
            for filename in documents:
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                assert "**创建人**: 多文档创建人" in content
                assert "**版本**: 1.0.0" in content
                assert documents[filename] in content

        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
