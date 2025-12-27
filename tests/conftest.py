"""
测试配置文件

提供全局测试夹具（fixtures）和配置管理，支持所有测试类型。
"""

import asyncio
import os
import pytest
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Generator, Any, Optional

import pytest_asyncio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class TestConfig:
    """测试配置类"""

    # 测试环境配置
    TEST_ENV = os.getenv("TEST_ENV", "development")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///test.db")
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

    # 测试超时设置
    UNIT_TEST_TIMEOUT = int(os.getenv("UNIT_TEST_TIMEOUT", "30"))
    INTEGRATION_TEST_TIMEOUT = int(os.getenv("INTEGRATION_TEST_TIMEOUT", "60"))
    E2E_TEST_TIMEOUT = int(os.getenv("E2E_TEST_TIMEOUT", "300"))

    # 并发测试设置
    MAX_CONCURRENT_TESTS = int(os.getenv("MAX_CONCURRENT_TESTS", "10"))

    # 性能测试设置
    PERFORMANCE_MEMORY_LIMIT_MB = int(os.getenv("PERFORMANCE_MEMORY_LIMIT_MB", "2048"))
    PERFORMANCE_CPU_THRESHOLD = float(os.getenv("PERFORMANCE_CPU_THRESHOLD", "80.0"))


@pytest.fixture(scope="session")
def test_config() -> TestConfig:
    """测试配置夹具"""
    return TestConfig()


@pytest.fixture(scope="session")
def temp_directory() -> Generator[Path, None, None]:
    """临时目录夹具"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        yield temp_path


@pytest.fixture(scope="session")
def test_data_directory(test_config: TestConfig, temp_directory: Path) -> Path:
    """测试数据目录夹具"""
    data_dir = temp_directory / "test_data"
    data_dir.mkdir(exist_ok=True)

    # 创建测试数据子目录
    (data_dir / "unit").mkdir(exist_ok=True)
    (data_dir / "integration").mkdir(exist_ok=True)
    (data_dir / "e2e").mkdir(exist_ok=True)
    (data_dir / "performance").mkdir(exist_ok=True)
    (data_dir / "ai").mkdir(exist_ok=True)

    return data_dir


@pytest.fixture(scope="session")
def mock_market_data() -> Dict[str, Any]:
    """模拟市场数据"""
    return {
        "daily": {
            "2024-01-01": {
                "open": 100.0,
                "high": 105.0,
                "low": 99.0,
                "close": 102.0,
                "volume": 1000000,
            },
            "2024-01-02": {
                "open": 102.0,
                "high": 108.0,
                "low": 101.0,
                "close": 106.0,
                "volume": 1200000,
            },
            "2024-01-03": {
                "open": 106.0,
                "high": 110.0,
                "low": 104.0,
                "close": 108.0,
                "volume": 1500000,
            },
        },
        "minute": {
            "2024-01-01 09:30:00": {"price": 100.0, "volume": 1000},
            "2024-01-01 09:31:00": {"price": 100.5, "volume": 1200},
            "2024-01-01 09:32:00": {"price": 101.0, "volume": 1500},
        },
    }


@pytest.fixture(scope="session")
def mock_trading_data() -> Dict[str, Any]:
    """模拟交易数据"""
    return {
        "portfolio": {
            "total_value": 1000000.0,
            "cash": 200000.0,
            "positions": [
                {
                    "symbol": "AAPL",
                    "quantity": 100,
                    "avg_price": 150.0,
                    "current_price": 160.0,
                },
                {
                    "symbol": "MSFT",
                    "quantity": 50,
                    "avg_price": 250.0,
                    "current_price": 260.0,
                },
            ],
        },
        "trades": [
            {
                "id": "001",
                "symbol": "AAPL",
                "quantity": 100,
                "price": 150.0,
                "timestamp": "2024-01-01 10:00:00",
            },
            {
                "id": "002",
                "symbol": "MSFT",
                "quantity": 50,
                "price": 250.0,
                "timestamp": "2024-01-01 11:00:00",
            },
        ],
    }


@pytest.fixture(scope="session")
def mock_ai_models() -> Dict[str, Any]:
    """模拟AI模型数据"""
    return {
        "prediction": {
            "model_name": "lstm_predictor",
            "accuracy": 0.85,
            "predictions": {
                "AAPL": {"current": 160.0, "predicted": 165.0, "confidence": 0.78},
                "MSFT": {"current": 260.0, "predicted": 265.0, "confidence": 0.82},
            },
        },
        "anomaly": {
            "model_name": "isolation_forest",
            "threshold": 0.1,
            "anomalies": [
                {"timestamp": "2024-01-01 10:30:00", "symbol": "AAPL", "score": 0.95},
                {"timestamp": "2024-01-01 14:15:00", "symbol": "TSLA", "score": 0.88},
            ],
        },
    }


@pytest.fixture
async def mock_database_connection():
    """模拟数据库连接夹具"""

    class MockDatabase:
        def __init__(self):
            self.connected = False
            self.data = {}

        async def connect(self):
            self.connected = True
            await asyncio.sleep(0.1)  # 模拟连接延迟

        async def disconnect(self):
            self.connected = False
            await asyncio.sleep(0.1)

        async def execute(self, query: str, params: Optional[Dict] = None):
            # 模拟查询执行
            await asyncio.sleep(0.05)
            return {"status": "success", "rows": 0}

        async def get_market_data(self, symbol: str, start_date: str, end_date: str):
            # 模拟获取市场数据
            await asyncio.sleep(0.1)
            return {
                "symbol": symbol,
                "data": [
                    {
                        "date": start_date,
                        "open": 100,
                        "high": 105,
                        "low": 99,
                        "close": 102,
                    },
                    {
                        "date": end_date,
                        "open": 102,
                        "high": 108,
                        "low": 101,
                        "close": 106,
                    },
                ],
            }

    db = MockDatabase()
    await db.connect()
    try:
        yield db
    finally:
        await db.disconnect()


@pytest.fixture
def mock_api_client():
    """模拟API客户端夹具"""

    class MockAPIClient:
        def __init__(self, base_url: str):
            self.base_url = base_url
            self.session = None

        async def get(self, endpoint: str, params: Optional[Dict] = None):
            # 模拟API请求
            await asyncio.sleep(0.1)
            return {"status": 200, "data": {}}

        async def post(self, endpoint: str, data: Optional[Dict] = None):
            # 模拟API请求
            await asyncio.sleep(0.1)
            return {"status": 201, "data": {}}

    client = MockAPIClient("http://test-api.com")
    return client


@pytest.fixture
def test_report_directory(test_config: TestConfig, temp_directory: Path) -> Path:
    """测试报告目录夹具"""
    report_dir = temp_directory / "reports"
    report_dir.mkdir(exist_ok=True)

    # 创建报告子目录
    (report_dir / "html").mkdir(exist_ok=True)
    (report_dir / "json").mkdir(exist_ok=True)
    (report_dir / "xml").mkdir(exist_ok=True)

    return report_dir


@pytest.fixture
def performance_monitor():
    """性能监控夹具"""

    class PerformanceMonitor:
        def __init__(self):
            self.metrics = {
                "cpu_usage": [],
                "memory_usage": [],
                "execution_times": [],
                "response_times": [],
            }

        def record_metric(self, metric_type: str, value: float):
            if metric_type in self.metrics:
                self.metrics[metric_type].append(value)

        def get_average(self, metric_type: str) -> float:
            values = self.metrics.get(metric_type, [])
            return sum(values) / len(values) if values else 0.0

        def get_summary(self) -> Dict[str, Any]:
            return {
                metric_type: {
                    "average": self.get_average(metric_type),
                    "max": max(values) if values else 0,
                    "min": min(values) if values else 0,
                    "count": len(values),
                }
                for metric_type, values in self.metrics.items()
            }

    return PerformanceMonitor()


@pytest.fixture
def chaos_test_scenarios():
    """混沌工程测试场景"""
    return [
        {
            "name": "database_timeout",
            "description": "模拟数据库超时",
            "duration": 5,
            "severity": "high",
        },
        {
            "name": "network_partition",
            "description": "模拟网络分区",
            "duration": 10,
            "severity": "critical",
        },
        {
            "name": "high_cpu_load",
            "description": "模拟高CPU负载",
            "duration": 15,
            "severity": "medium",
        },
        {
            "name": "memory_pressure",
            "description": "模拟内存压力",
            "duration": 8,
            "severity": "high",
        },
    ]


@pytest.fixture
def security_test_cases():
    """安全测试用例"""
    return [
        {
            "name": "sql_injection",
            "description": "SQL注入攻击测试",
            "vectors": [
                "'; DROP TABLE users; --",
                "1' OR '1'='1",
                "admin'--",
            ],
        },
        {
            "name": "xss_attack",
            "description": "跨站脚本攻击测试",
            "vectors": [
                "<script>alert('XSS')</script>",
                "javascript:alert('XSS')",
                "onload=alert('XSS')",
            ],
        },
        {
            "name": "csrf_attack",
            "description": "跨站请求伪造测试",
            "vectors": [
                "https://evil.com/steal?cookie=<session_id>",
                "http://malicious.site/transfer",
            ],
        },
    ]


@pytest.fixture
def test_ai_assisted_tools():
    """AI辅助测试工具夹具"""

    class AIAssistedTools:
        def __init__(self):
            self.test_data = []
            self.anomalies = []
            self.predictions = {}

        def generate_test_cases(self, code_snippet: str) -> list:
            # 模拟AI生成测试用例
            return [
                {
                    "name": "test_positive_case",
                    "description": "正向测试用例",
                    "code": f"# 自动生成的测试用例\nassert {code_snippet}",
                },
                {
                    "name": "test_negative_case",
                    "description": "负向测试用例",
                    "code": "# 自动生成的测试用例\nraise Exception('Invalid input')",
                },
            ]

        def detect_anomalies(self, metrics: list) -> list:
            # 模拟异常检测
            anomalies = []
            for i, metric in enumerate(metrics):
                if metric > 100:  # 简单的异常检测逻辑
                    anomalies.append(
                        {
                            "index": i,
                            "value": metric,
                            "severity": "high" if metric > 200 else "medium",
                        }
                    )
            return anomalies

        def predict_test_outcome(self, test_history: list) -> Dict[str, float]:
            # 模拟预测测试结果
            return {
                "pass_rate": sum(1 for t in test_history if t.get("passed", False)) / len(test_history),
                "failure_trend": (
                    "increasing"
                    if len(test_history) > 10 and test_history[-5:].count(False) > test_history[-10:-5].count(False)
                    else "stable"
                ),
            }

    return AIAssistedTools()


@pytest.fixture
def contract_test_validator():
    """契约测试验证器夹具"""

    class ContractTestValidator:
        def __init__(self):
            self.contracts = {}

        def validate_api_contract(self, endpoint: str, request: Dict, response: Dict) -> bool:
            # 模拟契约验证
            return "status" in response and isinstance(response["status"], int) and 200 <= response["status"] < 300

        def validate_response_schema(self, response: Dict, schema: Dict) -> Dict[str, Any]:
            # 模拟响应模式验证
            errors = []

            # 简单的模式验证
            required_fields = schema.get("required", [])
            for field in required_fields:
                if field not in response:
                    errors.append(f"缺少必需字段: {field}")

            return {"valid": len(errors) == 0, "errors": errors}

    return ContractTestValidator()


@pytest.fixture
def test_execution_context():
    """测试执行上下文夹具"""

    class ExecutionContext:
        def __init__(self):
            self.start_time = time.time()
            self.test_name = ""
            self.test_markers = []
            self.execution_log = []

        def start_test(self, name: str, markers: list = None):
            self.test_name = name
            self.test_markers = markers or []
            self.start_time = time.time()

        def log_event(self, event: str, **kwargs):
            self.execution_log.append({"timestamp": time.time(), "event": event, **kwargs})

        def get_execution_summary(self) -> Dict[str, Any]:
            duration = time.time() - self.start_time
            return {
                "test_name": self.test_name,
                "duration": duration,
                "markers": self.test_markers,
                "event_count": len(self.execution_log),
                "start_time": self.start_time,
            }

    context = ExecutionContext()
    return context


@pytest.fixture(scope="session")
def event_loop():
    """异步事件循环夹具"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_database_connection():
    """异步数据库连接夹具"""

    class AsyncDatabase:
        def __init__(self):
            self.connected = False

        async def __aenter__(self):
            self.connected = True
            await asyncio.sleep(0.1)
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            self.connected = False
            await asyncio.sleep(0.1)

    db = AsyncDatabase()
    async with db as connection:
        yield connection


@pytest.fixture
def benchmark_timer():
    """基准测试计时器夹具"""

    class BenchmarkTimer:
        def __init__(self):
            self.start_times = {}
            self.end_times = {}

        def start(self, name: str):
            self.start_times[name] = time.time()

        def stop(self, name: str):
            self.end_times[name] = time.time()

        def get_duration(self, name: str) -> float:
            start = self.start_times.get(name, 0)
            end = self.end_times.get(name, 0)
            return end - start if end > start else 0.0

        def get_all_durations(self) -> Dict[str, float]:
            return {name: self.get_duration(name) for name in self.start_times.keys()}

    timer = BenchmarkTimer()
    return timer


@pytest.fixture
def test_data_generator():
    """测试数据生成器夹具"""

    class TestDataGenerator:
        def __init__(self):
            self.sequences = {}

        def generate_sequence(self, name: str, count: int, start: int = 1) -> list:
            sequence = list(range(start, start + count))
            self.sequences[name] = sequence
            return sequence

        def generate_random_data(self, size: int, min_val: float = 0.0, max_val: float = 100.0) -> list:
            import random

            return [random.uniform(min_val, max_val) for _ in range(size)]

        def generate_time_series(self, start_time: str, end_time: str, interval_minutes: int = 60) -> list:
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)

            series = []
            current = start
            while current <= end:
                series.append({"timestamp": current.isoformat(), "value": float(len(series))})
                current += timedelta(minutes=interval_minutes)

            return series

    generator = TestDataGenerator()
    return generator


# 自定义命令行参数支持
def pytest_addoption(parser):
    """添加自定义命令行参数"""
    parser.addoption("--run-ai", action="store_true", default=False, help="运行AI辅助测试")
    parser.addoption("--run-performance", action="store_true", default=False, help="运行性能测试")
    parser.addoption("--run-security", action="store_true", default=False, help="运行安全测试")
    parser.addoption("--run-chaos", action="store_true", default=False, help="运行混沌工程测试")


def pytest_configure(config):
    """配置pytest"""
    # 导入标记定义
    from .markers import pytest_configure as markers_configure

    markers_configure(config)


def pytest_collection_modifyitems(config, items):
    """修改收集的测试项目"""
    # 根据命令行参数过滤测试
    if not config.getoption("--run-ai"):
        skip_ai = pytest.mark.skip(reason="需要 --run-ai 参数运行AI测试")
        for item in items:
            if "ai" in item.keywords:
                item.add_marker(skip_ai)

    if not config.getoption("--run-performance"):
        skip_performance = pytest.mark.skip(reason="需要 --run-performance 参数运行性能测试")
        for item in items:
            if "performance" in item.keywords:
                item.add_marker(skip_performance)

    if not config.getoption("--run-security"):
        skip_security = pytest.mark.skip(reason="需要 --run-security 参数运行安全测试")
        for item in items:
            if "security" in item.keywords:
                item.add_marker(skip_security)

    if not config.getoption("--run-chaos"):
        skip_chaos = pytest.mark.skip(reason="需要 --run-chaos 参数运行混沌工程测试")
        for item in items:
            if "chaos" in item.keywords:
                item.add_marker(skip_chaos)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """终端报告总结"""
    # 这里可以添加自定义的总结逻辑
    failed = terminalreporter.stats.get("failed", [])
    passed = terminalreporter.stats.get("passed", [])
    skipped = terminalreporter.stats.get("skipped", [])

    if failed:
        print(f"\n⚠️  有 {len(failed)} 个测试失败")
    if passed:
        print(f"✅ {len(passed)} 个测试通过")
    if skipped:
        print(f"⏭️  {len(skipped)} 个测试跳过")
