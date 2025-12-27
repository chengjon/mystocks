"""
pytest配置文件 - P0改进测试框架

遵循项目Mock数据使用规范：
- 所有模拟数据通过Mock模块提供
- 不在业务代码中硬编码数据
- 使用统一的数据源工厂
"""

import os
import sys
from pathlib import Path

import pytest

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def test_env():
    """会话级环境配置"""
    # 注意：不硬编码Mock开关，使用项目的统一配置
    os.environ["TESTING"] = "true"
    return


@pytest.fixture
def circuit_breaker_manager():
    """提供CircuitBreaker管理器实例"""
    from app.core.circuit_breaker_manager import CircuitBreakerManager

    manager = CircuitBreakerManager()
    yield manager
    # Cleanup
    manager.reset_all_circuit_breakers()


@pytest.fixture
def validation_test_data():
    """提供验证模型的测试数据集合"""
    return {
        "stock_symbols": {
            "valid": ["600519", "000001", "AAPL"],
            "invalid": ["", "a" * 25, "!@#$"],
        },
        "dates": {
            "valid": ["2025-01-01", "2024-12-31"],
            "invalid": ["", "01-01-2025", "2025-13-01"],
        },
        "pagination": {
            "valid": {"page": 1, "page_size": 20},
            "invalid": {"page": 0, "page_size": 1000},
        },
    }
