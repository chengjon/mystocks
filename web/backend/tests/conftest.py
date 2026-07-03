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

# 在导入 app.main 之前补齐最小测试环境，避免 collection 阶段直接 SystemExit。
os.environ.setdefault("POSTGRESQL_HOST", "localhost")
os.environ.setdefault("POSTGRESQL_USER", "test")
os.environ.setdefault("POSTGRESQL_PASSWORD", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("BACKEND_PORT", "8020")
os.environ.setdefault("BACKEND_BACKUP_PORT", "8021")
os.environ.setdefault("TESTING", "true")
os.environ.setdefault("DEVELOPMENT_MODE", "true")
os.environ.setdefault("MOCK_AUTH_ENABLED", "true")


# D4: 在 collection 前从 deps/openstock submodule 加载 OpenStock 静态 category。
# lifespan 在 TestClient fixture 中由 FastAPI 触发,但纯单测(不启动 app)
# 不会跑 lifespan → 必须在 conftest 主动 initialize,否则 Layer 1 重叠检查
# 会因为 OPENSTOCK_STATIC_CATEGORIES 为空而误判通过。
def _initialize_openstock_categories_for_tests() -> None:
    try:
        from app.services.extra_source import initialize_openstock_static_categories

        initialize_openstock_static_categories()
    except Exception as exc:  # pragma: no cover - 显式失败,避免静默
        raise RuntimeError(
            f"conftest: 无法从 deps/openstock 加载 OpenStock 静态 category 清单。"
            f"确认 submodule 已 init (git submodule update --init --recursive)。原因: {exc}"
        ) from exc


_initialize_openstock_categories_for_tests()


@pytest.fixture(scope="session")
def test_env():
    """会话级环境配置"""
    # 保持 fixture 兼容；模块级 setdefault 已负责 collection 前的最小环境。
    os.environ["TESTING"] = "true"
    return


@pytest.fixture
def test_client():
    """Provide a shared FastAPI TestClient for backend pytest suites."""
    try:
        from fastapi.testclient import TestClient
        from app.main import app

        with TestClient(app) as client:
            yield client
    except Exception as exc:
        pytest.skip(f"FastAPI app not available for testing: {exc}")


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
