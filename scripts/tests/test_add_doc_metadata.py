#!/usr/bin/env python3
"""add_doc_metadata模块测试套件
完整测试文档元数据添加功能的所有特性
遵循Phase 6成功模式：功能→边界→异常→性能→集成测试
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入被测试的模块
from src.utils.add_doc_metadata import (
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

    def test_add_metadata_to_existing_metadata(self):
        """测试向已有元数据的文件添加新元数据"""
        # 先添加一次元数据
        add_metadata(self.test_file_path, "原始创建人", "1.0.0")

        # 再次添加元数据
        add_metadata(self.test_file_path, "新创建人", "2.0.0", "2024-01-01", "更新内容")

        with open(self.test_file_path, encoding="utf-8") as f:
            content = f.read()

        # 验证新元数据被添加
        assert "**创建人**: 新创建人" in content
        assert "**版本**: 2.0.0" in content
        assert "**批准日期**: 2024-01-01" in content
        assert "**本次修订内容**: 更新内容" in content

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

    def test_add_metadata_readonly_file(self):
        """测试只读文件"""
        readonly_file = os.path.join(self.temp_dir, "readonly.md")

        # 创建文件并设为只读
        with open(readonly_file, "w", encoding="utf-8") as f:
            f.write("原始内容")

        os.chmod(readonly_file, 0o444)

        # 在某些系统上可能需要不同的处理方式
        try:
            with pytest.raises(PermissionError):
                add_metadata(readonly_file, "创建人", "1.0.0")
        finally:
            # 恢复权限以便清理
            os.chmod(readonly_file, 0o644)

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

    def test_add_metadata_newline_handling(self):
        """测试换行符处理"""
        test_file = os.path.join(self.temp_dir, "newline.md")

        with open(test_file, "w", encoding="utf-8") as f:
            f.write("第一行\n第二行\n第三行")

        add_metadata(test_file, "创建人", "1.0.0")

        with open(test_file, encoding="utf-8") as f:
            content = f.read()

        # 验证内容结构正确
        lines = content.split("\n")
        assert "**创建人**: 创建人" in lines[0]
        assert "第一行" in content
        assert "第二行" in content
        assert "第三行" in content


class TestBatchAddMetadata:
    """batch_add_metadata函数测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()

        # 创建多个测试文件
        self.test_files = []
        for i in range(3):
            file_path = os.path.join(self.temp_dir, f"doc_{i}.md")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# 文档 {i}\n\n内容 {i}")
            self.test_files.append(file_path)

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_batch_add_metadata_basic(self):
        """测试批量添加元数据"""
        creator = "批量创建人"
        version = "1.0.0"

        batch_add_metadata(self.temp_dir, creator, version)

        # 验证所有文件都被添加了元数据
        for file_path in self.test_files:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            assert f"**创建人**: {creator}" in content
            assert f"**版本**: {version}" in content

    def test_batch_add_metadata_with_options(self):
        """测试带选项的批量添加"""
        creator = "批量创建人"
        version = "2.0.0"
        approved_date = "2024-12-22"
        revision_notes = "批量更新"

        batch_add_metadata(
            self.temp_dir,
            creator,
            version,
            approved_date=approved_date,
            revision_notes=revision_notes,
        )

        for file_path in self.test_files:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            assert f"**创建人**: {creator}" in content
            assert f"**版本**: {version}" in content
            assert f"**批准日期**: {approved_date}" in content
            assert f"**本次修订内容**: {revision_notes}" in content

    def test_batch_add_metadata_mixed_files(self):
        """测试混合文件类型"""
        creator = "混合处理人"

        # 创建不同类型的文件
        md_file = os.path.join(self.temp_dir, "test.md")
        txt_file = os.path.join(self.temp_dir, "test.txt")
        rst_file = os.path.join(self.temp_dir, "test.rst")

        for file_path in [md_file, txt_file, rst_file]:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("内容")

        batch_add_metadata(self.temp_dir, creator, "1.0.0")

        # 验证只有.md文件被处理
        for file_path in [md_file]:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            assert f"**创建人**: {creator}" in content

        # 其他文件类型不应该被处理
        for file_path in [txt_file, rst_file]:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            assert f"**创建人**: {creator}" not in content

    def test_batch_add_metadata_empty_directory(self):
        """测试空目录"""
        empty_dir = os.path.join(self.temp_dir, "empty")
        os.makedirs(empty_dir)

        # 应该不报错
        batch_add_metadata(empty_dir, "创建人", "1.0.0")

    def test_batch_add_metadata_nonexistent_directory(self):
        """测试不存在的目录"""
        nonexistent_dir = os.path.join(self.temp_dir, "nonexistent")

        with pytest.raises(FileNotFoundError):
            batch_add_metadata(nonexistent_dir, "创建人", "1.0.0")

    def test_batch_add_metadata_nested_directories(self):
        """测试嵌套目录"""
        nested_dir = os.path.join(self.temp_dir, "subdir", "nested")
        os.makedirs(nested_dir)

        # 在不同层级创建文件
        root_file = os.path.join(self.temp_dir, "root.md")
        subdir_file = os.path.join(self.temp_dir, "subdir", "sub.md")
        nested_file = os.path.join(nested_dir, "nested.md")

        for file_path in [root_file, subdir_file, nested_file]:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("内容")

        batch_add_metadata(self.temp_dir, "创建人", "1.0.0")

        # 验证所有层级的.md文件都被处理
        for file_path in [root_file, subdir_file, nested_file]:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            assert "**创建人**: 创建人" in content

    def test_batch_add_metadata_performance(self):
        """测试批量操作性能"""
        import time

        # 创建更多文件进行性能测试
        large_file_list = []
        for i in range(50):  # 创建50个文件
            file_path = os.path.join(self.temp_dir, f"perf_test_{i}.md")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"性能测试文件 {i}")
            large_file_list.append(file_path)

        start_time = time.time()
        batch_add_metadata(self.temp_dir, "性能测试创建人", "1.0.0")
        end_time = time.time()

        processing_time = end_time - start_time

        # 验证所有文件都被处理
        processed_count = 0
        for file_path in large_file_list:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            if "**创建人**: 性能测试创建人" in content:
                processed_count += 1

        assert processed_count == 50
        assert processing_time < 5.0  # 应该在5秒内完成


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

    def test_main_with_directory_argument(self):
        """测试使用--directory参数的main函数"""
        test_args = [
            "--directory",
            self.temp_dir,
            "--creator",
            "批量命令行创建人",
            "--version",
            "2.0.0",
        ]

        with patch("sys.argv", ["add_doc_metadata.py"] + test_args):
            main()

        with open(self.test_file, encoding="utf-8") as f:
            content = f.read()

        assert "**创建人**: 批量命令行创建人" in content
        assert "**版本**: 2.0.0" in content

    def test_main_with_all_arguments(self):
        """测试使用所有参数的main函数"""
        test_args = [
            "--doc",
            self.test_file,
            "--creator",
            "完整参数创建人",
            "--version",
            "3.0.0",
            "--approved-date",
            "2024-12-22",
            "--revision-notes",
            "命令行测试修订",
        ]

        with patch("sys.argv", ["add_doc_metadata.py"] + test_args):
            main()

        with open(self.test_file, encoding="utf-8") as f:
            content = f.read()

        assert "**创建人**: 完整参数创建人" in content
        assert "**版本**: 3.0.0" in content
        assert "**批准日期**: 2024-12-22" in content
        assert "**本次修订内容**: 命令行测试修订" in content

    def test_main_missing_arguments(self):
        """测试缺少必要参数"""
        test_args = ["--doc", self.test_file]  # 缺少creator和version

        with patch("sys.argv", ["add_doc_metadata.py"] + test_args), pytest.raises(SystemExit):
            main()

    def test_main_both_doc_and_directory(self):
        """测试同时指定doc和directory参数"""
        other_dir = os.path.join(self.temp_dir, "other")
        os.makedirs(other_dir)

        test_args = [
            "--doc",
            self.test_file,
            "--directory",
            other_dir,
            "--creator",
            "创建人",
            "--version",
            "1.0.0",
        ]

        with patch("sys.argv", ["add_doc_metadata.py"] + test_args), pytest.raises(SystemExit):
            main()

    def test_main_neither_doc_nor_directory(self):
        """测试既不指定doc也不指定directory参数"""
        test_args = ["--creator", "创建人", "--version", "1.0.0"]

        with patch("sys.argv", ["add_doc_metadata.py"] + test_args), pytest.raises(SystemExit):
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

        with patch("sys.argv", ["add_doc_metadata.py"] + test_args), pytest.raises(FileNotFoundError):
            main()


class TestIntegrationScenarios:
    """集成场景测试类"""

    def test_end_to_end_workflow(self):
        """测试端到端工作流"""
        temp_dir = tempfile.mkdtemp()
        try:
            # 1. 创建文档
            doc_file = os.path.join(temp_dir, "project_documentation.md")
            with open(doc_file, "w", encoding="utf-8") as f:
                f.write("# 项目文档\n\n这是项目的详细说明文档。\n")

            # 2. 添加初始元数据
            add_metadata(doc_file, "初始作者", "1.0.0", "2024-01-01", "创建初始文档")

            # 3. 更新元数据
            add_metadata(doc_file, "更新作者", "1.1.0", "2024-01-15", "添加新功能说明")

            # 4. 验证最终状态
            with open(doc_file, encoding="utf-8") as f:
                final_content = f.read()

            # 验证最新元数据存在
            assert "**创建人**: 更新作者" in final_content
            assert "**版本**: 1.1.0" in final_content
            assert "**批准日期**: 2024-01-15" in final_content
            assert "**本次修订内容**: 添加新功能说明" in final_content

            # 验证原文内容保留
            assert "# 项目文档" in final_content
            assert "这是项目的详细说明文档" in final_content

        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def test_multiple_document_types(self):
        """测试多种文档类型的处理"""
        temp_dir = tempfile.mkdtemp()
        try:
            # 创建不同类型的文档
            documents = {
                "README.md": "# 项目说明\n\n项目的基本介绍。",
                "CHANGELOG.md": "# 变更日志\n\n版本更新记录。",
                "API.md": "# API文档\n\n接口详细说明。",
                "DEVELOPMENT.md": "# 开发指南\n\n开发环境配置。",
            }

            for filename, content in documents.items():
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

            # 批量添加元数据
            batch_add_metadata(
                temp_dir,
                "文档维护团队",
                "2.0.0",
                "2024-12-22",
                "统一添加元数据",
            )

            # 验证所有文档都被正确处理
            for filename in documents:
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                assert "**创建人**: 文档维护团队" in content
                assert "**版本**: 2.0.0" in content
                assert "**批准日期**: 2024-12-22" in content
                assert "**本次修订内容**: 统一添加元数据" in content

                # 验证原文保留
                assert documents[filename] in content

        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
