"""
config_loader 模块单元测试

测试YAML配置加载器的功能:
- 加载有效的YAML配置文件
- 处理文件不存在错误
- 处理YAML格式错误
- 处理空文件和空配置
"""

import pytest
import sys
import os
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# 确保能导入src模块
sys.path.insert(0, "/opt/claude/mystocks_spec")

from src.core.config_loader import ConfigLoader


class TestConfigLoaderBasicFunctionality:
    """测试ConfigLoader基本功能"""

    def test_load_config_valid_yaml(self, tmp_path):
        """测试加载有效的YAML配置文件"""
        # 创建临时配置文件
        config_file = tmp_path / "test_config.yaml"
        config_data = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "test_db"
            },
            "server": {
                "host": "0.0.0.0",
                "port": 8000
            },
            "debug": True
        }

        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        # 加载配置
        loaded_config = ConfigLoader.load_config(str(config_file))

        # 验证
        assert loaded_config == config_data
        assert loaded_config["database"]["host"] == "localhost"
        assert loaded_config["database"]["port"] == 5432
        assert loaded_config["server"]["port"] == 8000
        assert loaded_config["debug"] is True

    def test_load_config_returns_dict(self, tmp_path):
        """测试load_config返回字典类型"""
        config_file = tmp_path / "simple_config.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            f.write("key: value\n")

        result = ConfigLoader.load_config(str(config_file))

        assert isinstance(result, dict)

    def test_load_config_complex_nested_structure(self, tmp_path):
        """测试加载复杂嵌套结构的YAML"""
        config_file = tmp_path / "nested_config.yaml"
        config_data = {
            "level1": {
                "level2": {
                    "level3": {
                        "key": "deep_value",
                        "number": 42
                    },
                    "list": [1, 2, 3]
                }
            },
            "top_level_list": ["a", "b", "c"]
        }

        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        loaded_config = ConfigLoader.load_config(str(config_file))

        assert loaded_config["level1"]["level2"]["level3"]["key"] == "deep_value"
        assert loaded_config["level1"]["level2"]["level3"]["number"] == 42
        assert loaded_config["level1"]["level2"]["list"] == [1, 2, 3]
        assert loaded_config["top_level_list"] == ["a", "b", "c"]


class TestConfigLoaderErrorHandling:
    """测试ConfigLoader错误处理"""

    def test_load_config_file_not_found(self):
        """测试文件不存在时抛出FileNotFoundError"""
        non_existent_file = "/path/to/non_existent_config.yaml"

        with pytest.raises(FileNotFoundError, match="配置文件不存在"):
            ConfigLoader.load_config(non_existent_file)

    def test_load_config_invalid_yaml_syntax(self, tmp_path):
        """测试无效YAML格式时抛出YAMLError"""
        config_file = tmp_path / "invalid_config.yaml"

        # 写入无效的YAML
        with open(config_file, "w", encoding="utf-8") as f:
            f.write("invalid: yaml: content:\n  - missing closing bracket [")

        with pytest.raises(yaml.YAMLError):
            ConfigLoader.load_config(str(config_file))

    def test_load_config_malformed_yaml(self, tmp_path):
        """测试格式错误的YAML"""
        config_file = tmp_path / "malformed_config.yaml"

        # 写入格式错误的YAML
        with open(config_file, "w", encoding="utf-8") as f:
            f.write("key1: value1\n  indentation_error: bad_indent\n")

        with pytest.raises(yaml.YAMLError):
            ConfigLoader.load_config(str(config_file))


class TestConfigLoaderEmptyAndNullCases:
    """测试ConfigLoader空文件和null情况"""

    def test_load_config_empty_file(self, tmp_path):
        """测试加载空配置文件"""
        config_file = tmp_path / "empty_config.yaml"

        # 创建空文件
        config_file.touch()

        loaded_config = ConfigLoader.load_config(str(config_file))

        # 空文件应返回空字典
        assert loaded_config == {}
        assert isinstance(loaded_config, dict)
        assert len(loaded_config) == 0

    def test_load_config_null_content(self, tmp_path):
        """测试YAML内容为null的情况"""
        config_file = tmp_path / "null_config.yaml"

        with open(config_file, "w", encoding="utf-8") as f:
            f.write("# Just a comment\n")

        loaded_config = ConfigLoader.load_config(str(config_file))

        # null内容应返回空字典
        assert loaded_config == {}

    def test_load_config_whitespace_only(self, tmp_path):
        """测试仅包含空白字符的配置文件"""
        config_file = tmp_path / "whitespace_config.yaml"

        with open(config_file, "w", encoding="utf-8") as f:
            f.write("   \n\n   \n")

        loaded_config = ConfigLoader.load_config(str(config_file))

        assert loaded_config == {}


class TestConfigLoaderDataTypes:
    """测试ConfigLoader处理各种数据类型"""

    def test_load_config_with_strings(self, tmp_path):
        """测试字符串类型"""
        config_file = tmp_path / "string_config.yaml"
        config_data = {
            "simple_string": "value",
            "quoted_string": "value with spaces",
            "multiline_string": "line1\nline2\nline3"
        }

        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        loaded_config = ConfigLoader.load_config(str(config_file))

        assert loaded_config["simple_string"] == "value"
        assert loaded_config["quoted_string"] == "value with spaces"
        assert "line1" in loaded_config["multiline_string"]

    def test_load_config_with_numbers(self, tmp_path):
        """测试数字类型"""
        config_file = tmp_path / "number_config.yaml"
        config_data = {
            "integer": 42,
            "float": 3.14159,
            "negative": -100,
            "zero": 0
        }

        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        loaded_config = ConfigLoader.load_config(str(config_file))

        assert loaded_config["integer"] == 42
        assert loaded_config["float"] == 3.14159
        assert loaded_config["negative"] == -100
        assert loaded_config["zero"] == 0

    def test_load_config_with_booleans(self, tmp_path):
        """测试布尔类型"""
        config_file = tmp_path / "boolean_config.yaml"
        config_data = {
            "true_value": True,
            "false_value": False,
            "yes_value": True,
            "no_value": False
        }

        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        loaded_config = ConfigLoader.load_config(str(config_file))

        assert loaded_config["true_value"] is True
        assert loaded_config["false_value"] is False

    def test_load_config_with_lists(self, tmp_path):
        """测试列表类型"""
        config_file = tmp_path / "list_config.yaml"
        config_data = {
            "simple_list": [1, 2, 3, 4, 5],
            "string_list": ["apple", "banana", "cherry"],
            "mixed_list": [1, "two", 3.0, True, None]
        }

        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        loaded_config = ConfigLoader.load_config(str(config_file))

        assert loaded_config["simple_list"] == [1, 2, 3, 4, 5]
        assert loaded_config["string_list"] == ["apple", "banana", "cherry"]
        assert len(loaded_config["mixed_list"]) == 5

    def test_load_config_with_null_values(self, tmp_path):
        """测试null值"""
        config_file = tmp_path / "null_values_config.yaml"
        config_data = {
            "null_value": None,
            "empty_value": "",
            "key_with_null": None
        }

        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        loaded_config = ConfigLoader.load_config(str(config_file))

        assert loaded_config["null_value"] is None
        assert loaded_config["empty_value"] == ""


class TestConfigLoaderStaticMethod:
    """测试ConfigLoader静态方法特性"""

    def test_load_config_is_static_method(self):
        """测试load_config是静态方法"""
        assert callable(ConfigLoader.load_config)
        # 静态方法可以通过类直接调用,不需要实例

    def test_load_config_without_instance(self, tmp_path):
        """测试无需实例化即可调用load_config"""
        config_file = tmp_path / "test.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump({"key": "value"}, f)

        # 直接通过类调用,不创建实例
        result = ConfigLoader.load_config(str(config_file))

        assert result == {"key": "value"}


class TestConfigLoaderEncoding:
    """测试ConfigLoader编码处理"""

    def test_load_config_utf8_chinese_characters(self, tmp_path):
        """测试UTF-8编码的中文字符"""
        config_file = tmp_path / "chinese_config.yaml"
        config_data = {
            "中文键": "中文值",
            "database": {
                "名称": "测试数据库",
                "描述": "这是一个测试配置"
            }
        }

        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f, allow_unicode=True)

        loaded_config = ConfigLoader.load_config(str(config_file))

        assert loaded_config["中文键"] == "中文值"
        assert loaded_config["database"]["名称"] == "测试数据库"
        assert loaded_config["database"]["描述"] == "这是一个测试配置"

    def test_load_config_special_characters(self, tmp_path):
        """测试特殊字符"""
        config_file = tmp_path / "special_chars_config.yaml"
        config_data = {
            "special": "!@#$%^&*()",
            "emoji": "😀🎉🚀",
            "unicode": "Ñoño Müller"
        }

        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f, allow_unicode=True)

        loaded_config = ConfigLoader.load_config(str(config_file))

        assert loaded_config["special"] == "!@#$%^&*()"
        assert "emoji" in loaded_config


class TestConfigLoaderEdgeCases:
    """测试ConfigLoader边界情况"""

    def test_load_config_very_large_file(self, tmp_path):
        """测试加载大型配置文件"""
        config_file = tmp_path / "large_config.yaml"

        # 创建一个大配置
        config_data = {
            f"key_{i}": {
                "value": i,
                "nested": {
                    "data": f"value_{i}"
                }
            }
            for i in range(1000)
        }

        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        loaded_config = ConfigLoader.load_config(str(config_file))

        assert len(loaded_config) == 1000
        assert loaded_config["key_999"]["value"] == 999

    def test_load_config_with_comments(self, tmp_path):
        """测试包含注释的YAML文件"""
        config_file = tmp_path / "commented_config.yaml"

        with open(config_file, "w", encoding="utf-8") as f:
            f.write("""
# This is a comment
database:
  host: localhost  # inline comment
  port: 5432
# Another comment
server:
  port: 8000
""")

        loaded_config = ConfigLoader.load_config(str(config_file))

        # 注释应该被忽略
        assert loaded_config["database"]["host"] == "localhost"
        assert loaded_config["database"]["port"] == 5432
        assert loaded_config["server"]["port"] == 8000

    def test_load_config_returns_empty_dict_not_none(self, tmp_path):
        """测试空文件返回空字典而不是None"""
        config_file = tmp_path / "empty.yaml"
        config_file.touch()

        result = ConfigLoader.load_config(str(config_file))

        # 必须返回字典,不能返回None
        assert result is not None
        assert result == {}
        assert isinstance(result, dict)
