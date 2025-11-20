"""
MyStocks项目测试配置文件
提供测试夹具、mock数据和通用测试设置
"""

import pytest
import sys
import os
from pathlib import Path

# 确保能够导入项目模块
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 先不导入pandas, numpy等可能导致问题的库
# 只保留基础配置

# 标记配置
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line(
        "markers", "unit: 单元测试标记"
    )
    config.addinivalue_line(
        "markers", "integration: 集成测试标记"
    )
    config.addinivalue_line(
        "markers", "e2e: 端到端测试标记"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速测试标记"
    )
    config.addinivalue_line(
        "markers", "api: API测试标记"
    )
    config.addinivalue_line(
        "markers", "database: 数据库测试标记"
    )
    config.addinivalue_line(
        "markers", "adapter: 适配器测试标记"
    )
    config.addinivalue_line(
        "markers", "fast: 快速测试标记"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试项目"""
    # 自动为测试添加标记
    for item in items:
        # 根据路径自动添加标记
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif "database" in str(item.fspath):
            item.add_marker(pytest.mark.database)
        elif "adapter" in str(item.fspath):
            item.add_marker(pytest.mark.adapter)


# 测试钩子
def pytest_runtest_setup(item):
    """每个测试运行前的设置"""
    pass


def pytest_runtest_teardown(item):
    """每个测试运行后的清理"""
    pass


def pytest_report_header(config):
    """自定义报告头部"""
    return [
        f"Python: {sys.version.split()[0]}",
        f"Project: MyStocks",
        f"Test environment: {'development' if os.getenv('TESTING') else 'production'}",
    ]