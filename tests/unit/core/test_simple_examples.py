#!/usr/bin/env python3
"""
简单示例测试
验证测试基础设施工作正常
"""

import pytest


def test_basic_math():
    """基础数学运算测试"""
    assert 1 + 1 == 2
    assert 2 * 3 == 6


def test_string_operations():
    """字符串操作测试"""
    text = "Hello World"
    assert text.startswith("Hello")
    assert text.endswith("World")
    assert " " in text


@pytest.mark.parametrize(
    "input_value,expected", [(1, 1), (2, 4), (3, 9), (4, 16), (5, 25)]
)
def test_square_function(input_value, expected):
    """测试平方函数"""
    result = input_value**2
    assert result == expected


class TestExampleClass:
    """示例测试类"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.value = 42

    def test_value_exists(self):
        """测试值存在"""
        assert hasattr(self, "value")
        assert self.value == 42

    def test_value_modification(self):
        """测试值修改"""
        self.value = 100
        assert self.value == 100


@pytest.fixture
def sample_data():
    """示例数据fixture"""
    return {"name": "Test Data", "values": [1, 2, 3, 4, 5], "config": {"enabled": True}}


def test_fixture_usage(sample_data):
    """测试fixture使用"""
    assert sample_data["name"] == "Test Data"
    assert len(sample_data["values"]) == 5
    assert sample_data["config"]["enabled"] is True


def test_exception_handling():
    """测试异常处理"""
    with pytest.raises(ValueError):
        int("invalid_number")


def test_list_operations():
    """测试列表操作"""
    data = [1, 2, 3, 4, 5]

    # 测试长度
    assert len(data) == 5

    # 测试包含
    assert 3 in data

    # 测试切片
    subset = data[1:4]
    assert subset == [2, 3, 4]


def test_dictionary_operations():
    """测试字典操作"""
    data = {"key1": "value1", "key2": "value2"}

    # 测试键存在
    assert "key1" in data

    # 测试值获取
    assert data["key1"] == "value1"

    # 测试get方法
    assert data.get("key3", "default") == "default"


if __name__ == "__main__":
    pytest.main([__file__])
