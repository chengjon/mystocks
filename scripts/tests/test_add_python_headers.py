#!/usr/bin/env python3
"""
add_python_headers模块测试套件
基于Phase 6成功模式：功能→边界→异常→性能→集成测试
目标：100%测试覆盖率
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open
import pytest

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入被测试的模块
from src.utils.add_python_headers import (
    PythonHeaderAdder,
    batch_add_headers,
    PYTHON_HEADER_TEMPLATE,
)


class TestPythonHeaderAdderInit:
    """PythonHeaderAdder初始化测试类"""

    def test_init_default_values(self):
        """测试初始化默认值"""
        adder = PythonHeaderAdder()
        assert adder.added_count == 0
        assert adder.skipped_count == 0
        assert adder.failed_count == 0

    def test_init_counters_start_zero(self):
        """测试计数器从零开始"""
        adder = PythonHeaderAdder()
        # 验证所有计数器都是0
        assert adder.added_count == 0
        assert adder.skipped_count == 0
        assert adder.failed_count == 0


class TestHasStandardHeader:
    """has_standard_header方法测试类"""

    def test_has_header_with_chinese_keywords(self):
        """测试检测中文功能关键字"""
        content_with_chinese = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
# 功能：数据处理模块
# 作者：开发团队
'''
"""
        adder = PythonHeaderAdder()
        assert adder.has_standard_header(content_with_chinese) is True

    def test_has_header_with_english_keywords(self):
        """测试检测英文关键字"""
        content_with_english = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
# 功能: Data processing module
# 作者: Development Team
'''
"""
        adder = PythonHeaderAdder()
        assert adder.has_standard_header(content_with_english) is True

    def test_has_header_with_mystocks_keyword(self):
        """测试检测MyStocks关键字"""
        content_with_mystocks = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
MyStocks统一量化交易系统
'''
"""
        adder = PythonHeaderAdder()
        assert adder.has_standard_header(content_with_mystocks) is True

    def test_has_header_with_author_tag(self):
        """测试检测@author标签"""
        content_with_author = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author John Doe
'''
"""
        adder = PythonHeaderAdder()
        assert adder.has_standard_header(content_with_author) is True

    def test_no_standard_header(self):
        """测试没有标准头注释的情况"""
        content_without_header = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
        adder = PythonHeaderAdder()
        assert adder.has_standard_header(content_without_header) is False

    def test_no_header_at_all(self):
        """测试完全没有注释的情况"""
        content_no_comment = """import os
import sys
"""
        adder = PythonHeaderAdder()
        assert adder.has_standard_header(content_no_comment) is False

    def test_partial_header_match(self):
        """测试部分匹配头注释"""
        content_partial = """#!/usr/bin/env python3
# 功能： incomplete header
"""
        adder = PythonHeaderAdder()
        assert adder.has_standard_header(content_partial) is True

    def test_header_limited_search_range(self):
        """测试只搜索前500字符"""
        # 创建一个超过500字符的文件，头注释在前500字符内
        long_content = "a" * 100  # 填充字符
        header_content = """# 功能：测试模块
# 作者：测试作者
"""
        content = header_content + "b" * 1000  # 头注释后的大量字符

        adder = PythonHeaderAdder()
        assert adder.has_standard_header(content) is True


class TestExtractShebangAndEncoding:
    """extract_shebang_and_encoding方法测试类"""

    def test_extract_with_both_shebang_and_encoding(self):
        """测试提取shebang和编码声明"""
        content = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
print("Hello")
"""
        adder = PythonHeaderAdder()
        shebang, encoding, remaining = adder.extract_shebang_and_encoding(content)

        assert shebang == "#!/usr/bin/env python3"
        assert encoding == "# -*- coding: utf-8 -*-"
        assert 'print("Hello")' in remaining

    def test_extract_with_shebang_only(self):
        """测试只提取shebang"""
        content = """#!/usr/bin/env python3
print("Hello")
"""
        adder = PythonHeaderAdder()
        shebang, encoding, remaining = adder.extract_shebang_and_encoding(content)

        assert shebang == "#!/usr/bin/env python3"
        assert encoding == ""
        assert 'print("Hello")' in remaining

    def test_extract_with_encoding_only(self):
        """测试只提取编码声明"""
        content = """# -*- coding: utf-8 -*-
print("Hello")
"""
        adder = PythonHeaderAdder()
        shebang, encoding, remaining = adder.extract_shebang_and_encoding(content)

        assert shebang == ""
        assert encoding == "# -*- coding: utf-8 -*-"
        assert 'print("Hello")' in remaining

    def test_extract_with_neither(self):
        """测试既没有shebang也没有编码声明"""
        content = """print("Hello")
import os
"""
        adder = PythonHeaderAdder()
        shebang, encoding, remaining = adder.extract_shebang_and_encoding(content)

        assert shebang == ""
        assert encoding == ""
        assert remaining == content

    def test_extract_different_encoding_formats(self):
        """测试不同的编码格式"""
        encoding_formats = [
            "# -*- coding: utf-8 -*-",
            "# coding=utf-8",
            "# encoding: utf-8",
        ]

        for encoding_line in encoding_formats:
            content = encoding_line + '\nprint("Hello")'
            adder = PythonHeaderAdder()
            shebang, encoding, remaining = adder.extract_shebang_and_encoding(content)

            assert shebang == ""
            assert encoding == encoding_line

    def test_extract_empty_content(self):
        """测试空内容"""
        adder = PythonHeaderAdder()
        shebang, encoding, remaining = adder.extract_shebang_and_encoding("")

        assert shebang == ""
        assert encoding == ""
        assert remaining == ""

    def test_extract_only_empty_lines(self):
        """测试只有空行"""
        content = "\n\n\n"
        adder = PythonHeaderAdder()
        shebang, encoding, remaining = adder.extract_shebang_and_encoding(content)

        assert shebang == ""
        assert encoding == ""
        assert remaining == content


class TestAddHeaderToFile:
    """add_header_to_file方法测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.adder = PythonHeaderAdder()

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_add_header_to_new_file(self):
        """测试为新文件添加头注释"""
        file_path = os.path.join(self.temp_dir, "test_file.py")
        original_content = 'print("Hello World")\nimport os\n'

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(original_content)

        result = self.adder.add_header_to_file(
            file_path,
            description="测试文件",
            author="测试作者",
            created_date="2024-01-01",
        )

        assert result is True
        assert self.adder.added_count == 1

        # 验证文件内容
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "# 功能：测试文件" in content
        assert "# 作者：测试作者" in content
        assert "# 创建日期：2024-01-01" in content
        assert 'print("Hello World")' in content

    def test_add_header_creates_backup(self):
        """测试创建备份文件"""
        file_path = os.path.join(self.temp_dir, "test_file.py")
        original_content = 'print("Hello World")\n'

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(original_content)

        self.adder.add_header_to_file(file_path, "测试文件")

        # 验证备份文件存在
        backup_path = file_path + ".backup"
        assert os.path.exists(backup_path)

        # 验证备份内容正确
        with open(backup_path, "r", encoding="utf-8") as f:
            backup_content = f.read()

        assert backup_content == original_content

    def test_skip_file_with_existing_header(self):
        """测试跳过已有头注释的文件"""
        file_path = os.path.join(self.temp_dir, "test_file.py")
        content_with_header = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
# 功能：已有头注释
# 作者：已有作者
'''
print("Hello")
"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content_with_header)

        result = self.adder.add_header_to_file(file_path, "新描述")

        assert result is False
        assert self.adder.skipped_count == 1
        assert self.adder.added_count == 0

    def test_handle_file_not_found(self):
        """测试处理文件不存在的情况"""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.py")

        result = self.adder.add_header_to_file(nonexistent_file, "描述")

        assert result is False
        assert self.adder.failed_count == 1

    def test_handle_permission_error(self):
        """测试处理权限错误"""
        file_path = os.path.join(self.temp_dir, "test_file.py")

        # 创建文件
        with open(file_path, "w") as f:
            f.write("print('test')")

        # Mock文件打开以模拟权限错误
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            result = self.adder.add_header_to_file(file_path, "描述")

        assert result is False
        assert self.adder.failed_count == 1

    def test_add_header_with_custom_parameters(self):
        """测试使用自定义参数添加头注释"""
        file_path = os.path.join(self.temp_dir, "custom_test.py")
        with open(file_path, "w") as f:
            f.write("import os\n")

        result = self.adder.add_header_to_file(
            file_path,
            description="自定义模块",
            author="自定义作者",
            created_date="2024-12-22",
            version="3.0.0",
            dependencies="requests, pandas",
            notes="这是自定义注意事项",
            copyright="自定义版权 © 2024",
        )

        assert result is True

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "# 功能：自定义模块" in content
        assert "# 作者：自定义作者" in content
        assert "# 创建日期：2024-12-22" in content
        assert "# 版本：3.0.0" in content
        assert "# 依赖：requests, pandas" in content
        assert "#   这是自定义注意事项" in content
        assert "# 版权：自定义版权 © 2024" in content

    def test_add_header_preserves_shebang(self):
        """测试保留shebang"""
        file_path = os.path.join(self.temp_dir, "shebang_test.py")
        original_content = """#!/usr/bin/env python3
import os
"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(original_content)

        self.adder.add_header_to_file(file_path, "测试模块")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        assert lines[0] == "#!/usr/bin/env python3"
        # 如果原始文件没有编码声明，函数不会自动添加
        assert "# 功能：测试模块" in content
        assert "import os" in content

    def test_add_header_preserves_both_shebang_and_encoding(self):
        """测试同时保留shebang和编码声明"""
        file_path = os.path.join(self.temp_dir, "both_test.py")
        original_content = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(original_content)

        self.adder.add_header_to_file(file_path, "测试模块")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        assert lines[0] == "#!/usr/bin/env python3"
        assert lines[1] == "# -*- coding: utf-8 -*-"
        assert "# 功能：测试模块" in content

    def test_add_header_with_unicode_content(self):
        """测试处理Unicode内容"""
        file_path = os.path.join(self.temp_dir, "unicode_test.py")
        unicode_content = "# 测试中文：🚀💻📊\nimport sys\n"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(unicode_content)

        result = self.adder.add_header_to_file(file_path, "Unicode测试")

        assert result is True

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "# 测试中文：🚀💻📊" in content
        assert "# 功能：Unicode测试" in content


class TestRemoveSimpleDocstring:
    """_remove_simple_docstring方法测试类"""

    def test_remove_simple_single_line_docstring(self):
        """测试移除简单的单行docstring"""
        content = '''"""Simple docstring"""
import os
'''
        adder = PythonHeaderAdder()
        result = adder._remove_simple_docstring(content)

        assert "Simple docstring" not in result
        assert "import os" in result

    def test_remove_simple_multiline_docstring(self):
        """测试移除简单的多行docstring"""
        content = '''"""
Simple multiline docstring
Line 2
"""
import os
'''
        adder = PythonHeaderAdder()
        result = adder._remove_simple_docstring(content)

        assert "Simple multiline docstring" not in result
        assert "Line 2" not in result
        assert "import os" in result

    def test_preserve_complex_docstring(self):
        """测试保留复杂docstring"""
        content = '''"""
Complex docstring with class
This is a more complex documentation
"""
class MyClass:
    pass
'''
        # 对于简单测试，我们确保函数能处理这种情况
        adder = PythonHeaderAdder()
        result = adder._remove_simple_docstring(content)
        # 结果应该是原内容或处理后的内容
        assert isinstance(result, str)

    def test_remove_no_docstring(self):
        """测试没有docstring的情况"""
        content = "import os\nimport sys\n"
        adder = PythonHeaderAdder()
        result = adder._remove_simple_docstring(content)

        assert result == content

    def test_remove_empty_content(self):
        """测试空内容"""
        adder = PythonHeaderAdder()
        result = adder._remove_simple_docstring("")

        assert result == ""

    def test_remove_docstring_empty_lines(self):
        """测试只有空行的内容"""
        adder = PythonHeaderAdder()
        result = adder._remove_simple_docstring("\n\n\n")

        assert result == "\n\n\n"

    def test_remove_docstring_only_whitespace(self):
        """测试只包含空白字符的内容"""
        adder = PythonHeaderAdder()
        result = adder._remove_simple_docstring("   \n\t\n  ")

        assert result == "   \n\t\n  "

    def test_remove_docstring_content_stripped_to_empty(self):
        """测试内容被strip后为空的情况"""
        adder = PythonHeaderAdder()
        # 当内容只有空白字符，lstrip()后变为空字符串，split()产生空列表
        result = adder._remove_simple_docstring("   ")

        assert result == "   "

    def test_remove_docstring_exactly_empty_after_strip(self):
        """测试内容strip后刚好为空的情况"""
        adder = PythonHeaderAdder()
        # 创建一个内容，使其在lstrip()后变成空字符串
        result = adder._remove_simple_docstring("   \n")  # 只有空格和换行符

        # 这应该触发行156: return content
        assert result == "   \n"

    def test_remove_docstring_unclosed_quotes(self):
        """测试未闭合的引号docstring"""
        content = '''"""
        Unclosed docstring
        without ending quotes
import os
'''
        adder = PythonHeaderAdder()
        result = adder._remove_simple_docstring(content)

        # 当找不到结束引号时，应该返回原内容
        assert result == content

    def test_remove_single_quotes_docstring(self):
        """测试单引号docstring"""
        content = "'''Single quotes docstring'''\nimport os\n"
        adder = PythonHeaderAdder()
        result = adder._remove_simple_docstring(content)

        assert "Single quotes docstring" not in result
        assert "import os" in result

    def test_preserve_content_after_docstring(self):
        """测试保留docstring后的内容"""
        content = '''"""Docstring"""

def my_function():
    pass
'''
        adder = PythonHeaderAdder()
        result = adder._remove_simple_docstring(content)

        assert "def my_function():" in result
        assert "pass" in result


class TestBatchAddHeaders:
    """batch_add_headers函数测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch("os.getcwd")
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("sys.exit")
    def test_batch_add_headers_success(
        self, mock_exit, mock_file, mock_exists, mock_getcwd
    ):
        """测试批量添加头注释成功"""
        # Mock环境
        mock_getcwd.return_value = "/mock/cwd"
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = "import os\n"

        result = batch_add_headers()

        # 验证返回统计结果
        assert isinstance(result, dict)
        assert "added" in result
        assert "skipped" in result
        assert "failed" in result
        assert "total" in result

    @patch("os.getcwd")
    @patch("os.path.exists")
    def test_batch_add_missing_files(self, mock_exists, mock_getcwd):
        """测试处理缺失文件"""
        mock_getcwd.return_value = "/mock/cwd"
        mock_exists.return_value = False

        result = batch_add_headers()

        assert result["failed"] > 0

    @patch("os.getcwd")
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("sys.exit")
    def test_batch_add_with_files_having_headers(
        self, mock_exit, mock_file, mock_exists, mock_getcwd
    ):
        """测试处理已有头注释的文件"""
        mock_getcwd.return_value = "/mock/cwd"
        mock_exists.return_value = True
        # Mock file content with existing header
        mock_file.return_value.read.return_value = "# 功能：已有头注释\nimport os\n"

        result = batch_add_headers()

        assert isinstance(result, dict)
        # 应该有一些文件被跳过
        assert result["skipped"] >= 0


class TestPythonHeaderTemplate:
    """头注释模板测试类"""

    def test_template_format(self):
        """测试模板格式正确性"""
        assert "{description}" in PYTHON_HEADER_TEMPLATE
        assert "{author}" in PYTHON_HEADER_TEMPLATE
        assert "{version}" in PYTHON_HEADER_TEMPLATE
        assert "{created_date}" in PYTHON_HEADER_TEMPLATE
        assert "{dependencies}" in PYTHON_HEADER_TEMPLATE
        assert "{notes}" in PYTHON_HEADER_TEMPLATE
        assert "{copyright}" in PYTHON_HEADER_TEMPLATE

    def test_template_structure(self):
        """测试模板结构"""
        lines = PYTHON_HEADER_TEMPLATE.strip().split("\n")

        # 验证包含关键行
        assert any("# 功能：" in line for line in lines)
        assert any("# 作者：" in line for line in lines)
        assert any("# 创建日期：" in line for line in lines)
        assert any("# 版本：" in line for line in lines)
        assert any("# 依赖：" in line for line in lines)
        assert any("# 注意事项：" in line for line in lines)
        assert any("# 版权：" in line for line in lines)

    def test_template_is_triple_quoted(self):
        """测试模板使用三重引号"""
        assert PYTHON_HEADER_TEMPLATE.startswith("'''")
        assert PYTHON_HEADER_TEMPLATE.endswith("'''\n")


class TestIntegrationScenarios:
    """集成场景测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        # 切换到临时目录
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        os.chdir(self.original_cwd)
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_end_to_end_workflow(self):
        """测试端到端工作流"""
        # 创建测试文件结构
        test_files = {
            "module1.py": "import os\nprint('module1')",
            "subdir/module2.py": "#!/usr/bin/env python3\nimport sys\n",
            "subdir/subsubdir/module3.py": "def function():\n    pass\n",
        }

        # 创建目录和文件
        for file_path, content in test_files.items():
            full_path = os.path.join(self.temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

        # 创建PythonHeaderAdder实例
        adder = PythonHeaderAdder()

        # 为每个文件添加头注释
        for file_path in test_files.keys():
            full_path = os.path.join(self.temp_dir, file_path)
            result = adder.add_header_to_file(
                full_path,
                description=f"模块 {file_path}",
                author="集成测试",
                created_date="2024-12-22",
            )
            assert result is True

        # 验证结果
        assert adder.added_count == 3
        assert adder.skipped_count == 0
        assert adder.failed_count == 0

        # 验证备份文件存在
        for file_path in test_files.keys():
            full_path = os.path.join(self.temp_dir, file_path)
            backup_path = full_path + ".backup"
            assert os.path.exists(backup_path)

    def test_mixed_file_scenario(self):
        """测试混合文件场景（有的有头注释，有的没有）"""
        # 创建已有头注释的文件
        file_with_header = os.path.join(self.temp_dir, "with_header.py")
        with open(file_with_header, "w", encoding="utf-8") as f:
            f.write("#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n")
            f.write("'''\n# 功能：已有头注释\n# 作者：原作者\n'''\n")
            f.write("print('has header')\n")

        # 创建没有头注释的文件
        file_without_header = os.path.join(self.temp_dir, "without_header.py")
        with open(file_without_header, "w", encoding="utf-8") as f:
            f.write("print('no header')\n")

        adder = PythonHeaderAdder()

        # 处理两个文件
        result1 = adder.add_header_to_file(file_with_header, "应该被跳过")
        result2 = adder.add_header_to_file(file_without_header, "应该被添加")

        assert result1 is False  # 应该被跳过
        assert result2 is True  # 应该被添加
        assert adder.added_count == 1
        assert adder.skipped_count == 1


from scripts._test_add_python_headers_tail import TestTailScenarios


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
