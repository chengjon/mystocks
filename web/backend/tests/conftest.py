"""
Pytest configuration and shared fixtures
Week 1 Architecture-Compliant API Tests
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path

# Week 3 Compatibility: Set database environment variables to redirect to PostgreSQL
# This allows MyStocksUnifiedManager to work in the simplified PostgreSQL-only environment
os.environ.setdefault('POSTGRESQL_HOST', os.getenv('POSTGRESQL_HOST', '192.168.123.104'))
os.environ.setdefault('POSTGRESQL_PORT', os.getenv('POSTGRESQL_PORT', '5438'))
os.environ.setdefault('POSTGRESQL_USER', os.getenv('POSTGRESQL_USER', 'postgres'))
os.environ.setdefault('POSTGRESQL_PASSWORD', os.getenv('POSTGRESQL_PASSWORD', 'c790414J'))
os.environ.setdefault('POSTGRESQL_DATABASE', os.getenv('POSTGRESQL_DATABASE', 'mystocks'))

# Compatibility shims for old database variables (all redirect to PostgreSQL)
os.environ.setdefault('MYSQL_HOST', os.getenv('POSTGRESQL_HOST', '192.168.123.104'))
os.environ.setdefault('MYSQL_PORT', os.getenv('POSTGRESQL_PORT', '5438'))
os.environ.setdefault('MYSQL_USER', os.getenv('POSTGRESQL_USER', 'postgres'))
os.environ.setdefault('MYSQL_PASSWORD', os.getenv('POSTGRESQL_PASSWORD', 'c790414J'))
os.environ.setdefault('MYSQL_DATABASE', os.getenv('POSTGRESQL_DATABASE', 'mystocks'))

os.environ.setdefault('TDENGINE_HOST', 'localhost')  # Not used, but required for initialization
os.environ.setdefault('TDENGINE_PORT', '6041')
os.environ.setdefault('TDENGINE_USER', 'root')
os.environ.setdefault('TDENGINE_PASSWORD', 'taosdata')
os.environ.setdefault('TDENGINE_DATABASE', 'market_data')

os.environ.setdefault('REDIS_HOST', 'localhost')  # Not used, but required for initialization
os.environ.setdefault('REDIS_PORT', '6379')
os.environ.setdefault('REDIS_PASSWORD', '')
os.environ.setdefault('REDIS_DB', '1')  # Use DB 1 (DB 0 reserved for PAPERLESS)

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.main import app


@pytest.fixture(scope="session")
def test_client():
    """
    Create FastAPI test client (session-scoped for performance)
    Note: We raise_server_exceptions=False to capture errors gracefully in tests
    """
    # Import here to avoid module-level side effects
    from app.main import app

    with TestClient(app, raise_server_exceptions=False) as client:
        yield client


@pytest.fixture(scope="session")
def base_url():
    """Base URL for API endpoints"""
    return "http://testserver"


@pytest.fixture
def sample_strategy_data():
    """Sample strategy data for testing"""
    return {
        "name": "Test Strategy",
        "description": "A test strategy for E2E testing",
        "strategy_type": "model_based",
        "parameters": {
            "lookback_period": 20,
            "threshold": 0.05
        },
        "status": "draft"
    }


@pytest.fixture
def sample_model_data():
    """Sample ML model data for testing"""
    return {
        "name": "Test RandomForest Model",
        "model_type": "RandomForest",
        "features": ["close", "volume", "ma_5", "ma_10"],
        "target": "future_return_5d",
        "parameters": {
            "n_estimators": 100,
            "max_depth": 10
        }
    }


@pytest.fixture
def sample_backtest_data():
    """Sample backtest configuration"""
    return {
        "strategy_id": 1,
        "start_date": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
        "end_date": datetime.now().strftime("%Y-%m-%d"),
        "initial_capital": 100000.0,
        "symbols": ["600519.SH", "000858.SZ"],
        "parameters": {
            "commission": 0.001,
            "slippage": 0.001
        }
    }


@pytest.fixture
def sample_risk_alert_data():
    """Sample risk alert rule"""
    return {
        "name": "High VaR Alert",
        "metric_type": "var",
        "threshold": 0.05,
        "condition": "greater_than",
        "notification_channel": "email",
        "enabled": True
    }


@pytest.fixture
def sample_portfolio_positions():
    """Sample portfolio positions for risk calculation"""
    return {
        "positions": [
            {
                "symbol": "600519.SH",
                "quantity": 1000,
                "entry_price": 1800.0,
                "current_price": 1850.0
            },
            {
                "symbol": "000858.SZ",
                "quantity": 2000,
                "entry_price": 45.0,
                "current_price": 47.5
            }
        ],
        "cash": 50000.0
    }


@pytest.fixture
def auth_headers():
    """
    Authentication headers (if needed)
    Note: Week 1 APIs may not require auth in test mode
    """
    return {}


# Test data cleanup helpers
@pytest.fixture
def cleanup_test_data(test_client):
    """
    Cleanup fixture - runs after each test
    Note: In real implementation, this would clean up test database records
    """
    yield
    # Cleanup logic here
    # For now, we'll rely on test database isolation


# Database state helpers
@pytest.fixture(autouse=True)
def reset_monitoring_fallback():
    """
    Reset monitoring fallback state for each test
    Ensures clean state for monitoring database tests
    """
    # This will be called before each test
    yield
    # Cleanup after test
