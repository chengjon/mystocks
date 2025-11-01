"""
Test Configuration and Fixtures
Day 5 API Testing Infrastructure
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import FastAPI app
try:
    from app.main import app
except ImportError:
    # Fallback if app.main doesn't exist yet
    from fastapi import FastAPI
    app = FastAPI()


@pytest.fixture
def client():
    """FastAPI测试客户端"""
    return TestClient(app)


@pytest.fixture
def sample_strategy():
    """示例策略数据"""
    return {
        "name": "测试策略",
        "description": "用于测试的策略",
        "strategy_type": "rule_based",
        "parameters": {"param1": "value1"},
        "status": "draft"
    }


@pytest.fixture
def sample_model():
    """示例模型数据"""
    return {
        "name": "测试模型",
        "model_type": "random_forest",
        "hyperparameters": {"n_estimators": 100},
        "training_config": {"test_size": 0.2}
    }


@pytest.fixture
def sample_backtest_config():
    """示例回测配置"""
    return {
        "name": "测试回测",
        "strategy_id": 1,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "initial_cash": 1000000,
        "commission_rate": 0.0003
    }


@pytest.fixture
def sample_risk_alert():
    """示例风险预警"""
    return {
        "name": "VaR预警",
        "metric_type": "var_95",
        "threshold_value": -0.05,
        "comparison_operator": "<",
        "is_active": True,
        "notification_channels": ["email"]
    }
