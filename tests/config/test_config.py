#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 统一测试配置系统
集中管理所有测试相关的配置和常量
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


# 测试环境配置
@dataclass
class TestEnvironment:
    """测试环境配置"""

    # 端口配置
    FRONTEND_PORT_RANGE: List[int] = field(default_factory=lambda: [3000, 3009])
    BACKEND_PORT_RANGE: List[int] = field(default_factory=lambda: [8000, 8009])
    API_PORT: int = 8000
    FRONTEND_DEV_PORT: int = 3000

    # 数据库配置
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "mystocks_test"
    TDENGINE_HOST: str = "localhost"
    TDENGINE_PORT: int = 6030
    TDENGINE_DB: str = "mystocks_test"

    # API配置
    API_BASE_URL: str = "http://localhost:8020"
    API_TIMEOUT: int = 30

    # 性能测试配置
    LOAD_TEST_DURATION: int = 300  # 秒
    LOAD_TEST_USERS: int = 100
    LOAD_TEST_RAMPUP: int = 60

    # Mock数据配置
    USE_MOCK_DATA: bool = True
    MOCK_DATA_CACHE_TTL: int = 3600  # 秒
    MOCK_DATA_SEED: int = 20250612


# 测试策略配置
@dataclass
class TestStrategy:
    """测试策略配置"""

    # 覆盖率目标
    COVERAGE_TARGET: Dict[str, float] = field(
        default_factory=lambda: {
            "unit": 80,
            "integration": 75,
            "e2e": 90,
            "overall": 78,
        }
    )

    # 并发配置
    CONCURRENT_TESTS: int = 4
    MAX_TEST_DURATION: int = 120  # 秒

    # 重试配置
    MAX_RETRIES: int = 2
    RETRY_DELAY: int = 5

    # 数据驱动测试配置
    DATADRIVE_PERCENT: int = 30  # 数据驱动测试覆盖率


# 测试数据配置
@dataclass
class TestData:
    """测试数据配置"""

    # 数据源
    TEST_DATA_DIR: Path = Path(__file__).parent / "data"
    FIXTURES_DIR: Path = Path(__file__).parent / "fixtures"
    MOCK_DATA_DIR: Path = Path(__file__).parent / "mock_data"

    # 数据版本
    DATA_VERSION: str = "v1.0.0"

    # 样本数据配置
    SAMPLE_STOCK_CODES: List[str] = field(
        default_factory=lambda: [
            "600519",  # 贵州茅台
            "600036",  # 招商银行
            "000001",  # 平安银行
            "000002",  # 万科A
            "399300",  # 沪深300
        ]
    )

    SAMPLE_INDEX_CODES: List[str] = field(
        default_factory=lambda: [
            "399300",  # 沪深300
            "000001",  # 上证指数
            "399006",  # 创业板指
            "000016",  # 上证50
            "399911",  # 中证500
        ]
    )

    # 常见测试时间范围
    COMMON_DATE_RANGES: Dict[str, Dict[str, str]] = field(
        default_factory=lambda: {
            "recent_30d": {"start_date": "2024-11-12", "end_date": "2024-12-12"},
            "recent_90d": {"start_date": "2024-09-12", "end_date": "2024-12-12"},
            "recent_180d": {"start_date": "2024-06-12", "end_date": "2024-12-12"},
            "recent_1y": {"start_date": "2023-12-12", "end_date": "2024-12-12"},
        }
    )


# AI测试配置
@dataclass
class AITestConfig:
    """AI辅助测试配置"""

    # 代码分析配置
    CODE_COMPLEXITY_THRESHOLD: int = 10
    MAX_METHOD_LENGTH: int = 50

    # 测试用例生成配置
    TEST_GENERATION_MODEL: str = "gpt-4-turbo-preview"
    MAX_TESTS_PER_METHOD: int = 5
    TEST_CASE_GENERATION_TIMEOUT: int = 60

    # 测试优化配置
    OPTIMIZATION_TARGETS: List[str] = field(default_factory=lambda: ["coverage", "performance", "maintainability"])

    # 智能重试配置
    SMART_RETRY_ENABLED: bool = True
    SMART_RETRY_MAX_ATTEMPTS: int = 3
    BACKOFF_STRATEGY: str = "exponential"


# 混沌工程配置
@dataclass
class ChaosConfig:
    """混沌工程测试配置"""

    # 网络故障注入
    NETWORK_FAILURE_RATE: float = 0.1
    NETWORK_DELAY_MIN: int = 1000  # 毫秒
    NETWORK_DELAY_MAX: int = 5000  # 毫秒

    # 数据库故障注入
    DB_FAILURE_RATE: float = 0.05
    DB_TIMEOUT: int = 3000  # 毫秒

    # API故障注入
    API_FAILURE_RATE: float = 0.08
    API_RESPONSE_DELAY_MIN: int = 500  # 毫秒
    API_RESPONSE_DELAY_MAX: int = 3000  # 毫秒

    # 混沌测试开关
    CHAOS_ENABLED: bool = False
    CHAOS_SEED: Optional[int] = None


# 性能基准配置
@dataclass
class PerformanceBaseline:
    """性能基准配置"""

    # API性能基准
    API_RESPONSE_TIME_THRESHOLD: Dict[str, int] = field(
        default_factory=lambda: {
            "market_data": 1000,  # 1秒
            "kline_data": 2000,  # 2秒
            "strategy_backtest": 30000,  # 30秒
            "batch_analysis": 60000,  # 60秒
        }
    )

    # 数据库查询基准
    DB_QUERY_TIME_THRESHOLD: Dict[str, int] = field(
        default_factory=lambda: {
            "simple_lookup": 100,  # 100ms
            "complex_analysis": 5000,  # 5秒
            "batch_insert": 500,  # 500ms per batch
        }
    )

    # 前端加载基准
    FRONTEND_LOAD_TIME: Dict[str, int] = field(
        default_factory=lambda: {
            "dashboard": 2000,  # 2秒
            "stock_detail": 3000,  # 3秒
            "strategy_page": 4000,  # 4秒
        }
    )


# 全局测试配置实例
test_env = TestEnvironment()
test_strategy = TestStrategy()
test_data = TestData()
ai_config = AITestConfig()
chaos_config = ChaosConfig()
performance_baseline = PerformanceBaseline()


# Pytest 配置注册
def pytest_configure(config):
    """pytest配置注册"""
    # 添加自定义标记
    config.addinivalue_line("markers", "unit: Unit tests for individual components")
    config.addinivalue_line("markers", "integration: Integration tests for components interaction")
    config.addinivalue_line("markers", "e2e: End-to-end tests for complete workflows")
    config.addinivalue_line("markers", "performance: Performance and load testing")
    config.addinivalue_line("markers", "security: Security and vulnerability testing")
    config.addinivalue_line("markers", "ai_assisted: AI-generated or optimized tests")
    config.addinivalue_line("markers", "chaos: Chaos engineering tests")
    config.addinivalue_line("markers", "contract: API contract tests")
    config.addinivalue_line("markers", "smoke: Basic functionality smoke tests")
    config.addinivalue_line("markers", "regression: Regression prevention tests")


# 测试环境检查
def validate_test_environment():
    """验证测试环境"""
    issues = []

    # 检查端口分配
    try:
        import socket

        for port in range(test_env.FRONTEND_PORT_RANGE[0], test_env.FRONTEND_PORT_RANGE[1] + 1):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(("localhost", port))
            sock.close()
            if result == 0:
                issues.append(f"前端端口 {port} 已被占用")
    except Exception as e:
        issues.append(f"端口检查失败: {str(e)}")

    # 检查数据库连接
    try:
        import psycopg2

        conn = psycopg2.connect(
            host=test_env.POSTGRES_HOST,
            port=test_env.POSTGRES_PORT,
            database="postgres",
        )
        conn.close()
    except Exception:
        issues.append("PostgreSQL 数据库连接失败")

    try:
        import taos

        conn = taos.connect(
            host=test_env.TDENGINE_HOST,
            port=test_env.TDENGINE_PORT,
            user="root",
            password="taosdata",
        )
        conn.close()
    except Exception:
        issues.append("TDengine 数据库连接失败")

    return issues


# 测试数据初始化
def initialize_test_data():
    """初始化测试数据"""
    # 创建测试数据目录
    test_data.TEST_DATA_DIR.mkdir(exist_ok=True)
    test_data.FIXTURES_DIR.mkdir(exist_ok=True)
    test_data.MOCK_DATA_DIR.mkdir(exist_ok=True)

    # 生成测试数据
    if test_data.TEST_DATA_DIR.exists():
        print(f"✅ 测试数据目录准备就绪: {test_data.TEST_DATA_DIR}")
        print(f"📊 样本股票代码: {test_data.SAMPLE_STOCK_CODES}")
        print(f"📊 样本指数代码: {test_data.SAMPLE_INDEX_CODES}")


# 模块初始化
if __name__ == "__main__":
    # 初始化测试数据
    initialize_test_data()

    # 验证测试环境
    issues = validate_test_environment()
    if issues:
        print("⚠️  测试环境警告:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ 测试环境验证通过")

    print("\n🔧 测试配置完成:")
    print(f"  - 前端端口范围: {test_env.FRONTEND_PORT_RANGE}")
    print(f"  - 后端端口: {test_env.API_PORT}")
    print(f"  - 数据覆盖率目标: {test_strategy.COVERAGE_TARGET}")
    print(f"  - 并发测试数: {test_strategy.CONCURRENT_TESTS}")
