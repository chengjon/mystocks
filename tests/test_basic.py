"""
基础测试验证文件
用于验证pytest配置是否正确
"""


def test_basic_pytest_function():
    """基础测试函数，验证pytest配置是否正常工作"""
    assert 1 + 1 == 2
    print("pytest配置验证通过")


def test_example_data_structure():
    """示例数据结构测试"""
    test_data = {"key": "value", "number": 42}
    assert isinstance(test_data, dict)
    assert test_data["number"] == 42
