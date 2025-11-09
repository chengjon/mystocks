"""
pytest配置和fixtures
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

# ==================== 测试数据Fixtures ====================


@pytest.fixture
def sample_stock_data():
    """
    生成示例股票数据DataFrame
    """
    dates = pd.date_range(start="2024-01-01", periods=10, freq="D")
    data = {
        "date": dates,
        "open": [10.0 + i * 0.1 for i in range(10)],
        "high": [10.5 + i * 0.1 for i in range(10)],
        "low": [9.5 + i * 0.1 for i in range(10)],
        "close": [10.2 + i * 0.1 for i in range(10)],
        "volume": [1000000 + i * 10000 for i in range(10)],
        "amount": [10000000.0 + i * 100000 for i in range(10)],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_realtime_data():
    """
    生成示例实时行情数据
    """
    return {
        "symbol": "000001",
        "name": "平安银行",
        "price": 12.50,
        "change": 0.25,
        "change_pct": 2.04,
        "volume": 1234567,
        "amount": 15432087.50,
        "high": 12.60,
        "low": 12.30,
        "open": 12.40,
        "pre_close": 12.25,
        "timestamp": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_financial_data():
    """
    生成示例财务数据DataFrame
    """
    data = {
        "report_date": ["2024-03-31", "2023-12-31", "2023-09-30"],
        "total_assets": [1000000000, 950000000, 900000000],
        "total_liabilities": [600000000, 570000000, 540000000],
        "shareholders_equity": [400000000, 380000000, 360000000],
        "revenue": [100000000, 380000000, 270000000],
        "net_profit": [20000000, 76000000, 54000000],
    }
    return pd.DataFrame(data)


# ==================== Mock Fixtures ====================


@pytest.fixture
def mock_database_connection():
    """
    Mock数据库连接
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn


@pytest.fixture
def mock_adapter():
    """
    Mock数据源适配器
    """
    adapter = Mock()
    adapter.get_stock_daily = Mock(
        return_value=pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5),
                "close": [10.0, 10.1, 10.2, 10.3, 10.4],
            }
        )
    )
    adapter.get_real_time_data = Mock(return_value={"symbol": "000001", "price": 12.50})
    return adapter


# ==================== 测试环境配置 ====================


@pytest.fixture(scope="session", autouse=True)
def test_environment():
    """
    设置测试环境
    """
    import os

    # 设置测试环境标志
    os.environ["TESTING"] = "1"
    yield
    # 清理
    del os.environ["TESTING"]


@pytest.fixture
def temp_test_dir(tmp_path):
    """
    创建临时测试目录
    """
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()
    return test_dir


# ==================== 回测测试Fixtures ====================


@pytest.fixture
def sample_price_data():
    """
    生成回测用价格数据
    """
    import numpy as np

    n = 100
    dates = pd.date_range("2024-01-01", periods=n, freq="D")

    # 生成趋势向上的价格数据
    np.random.seed(42)
    close_prices = 100 + np.cumsum(np.random.randn(n) * 0.5 + 0.02)

    data = pd.DataFrame(
        {
            "open": close_prices + np.random.randn(n) * 0.5,
            "high": close_prices + np.abs(np.random.randn(n)),
            "low": close_prices - np.abs(np.random.randn(n)),
            "close": close_prices,
            "volume": np.random.uniform(1000000, 10000000, n),
        },
        index=dates,
    )

    return data


@pytest.fixture
def sample_signals():
    """
    生成示例交易信号
    """
    import numpy as np

    n = 100
    dates = pd.date_range("2024-01-01", periods=n, freq="D")

    # 创建简单的买卖信号（每20天买入，10天后卖出）
    signals = pd.DataFrame(index=dates)
    signals["signal"] = None
    signals["strength"] = 0.0

    for i in range(0, n, 20):
        if i < n:
            signals.iloc[i] = ["buy", 0.8]
        if i + 10 < n:
            signals.iloc[i + 10] = ["sell", 0.8]

    return signals


@pytest.fixture
def sample_trades():
    """
    生成示例交易记录
    """
    import sys

    sys.path.insert(0, "/opt/claude/mystocks_spec")
    from backtest.vectorized_backtester import Trade
    from datetime import date

    trades = [
        Trade(
            entry_date=date(2024, 1, 1),
            entry_price=100.0,
            exit_date=date(2024, 1, 5),
            exit_price=105.0,
            shares=100,
            direction="long",
            pnl=500.0,
            pnl_pct=0.05,
            commission=10.0,
            slippage=5.0,
            holding_days=4,
        ),
        Trade(
            entry_date=date(2024, 1, 6),
            entry_price=105.0,
            exit_date=date(2024, 1, 10),
            exit_price=103.0,
            shares=100,
            direction="long",
            pnl=-200.0,
            pnl_pct=-0.02,
            commission=10.0,
            slippage=5.0,
            holding_days=4,
        ),
        Trade(
            entry_date=date(2024, 1, 11),
            entry_price=103.0,
            exit_date=date(2024, 1, 15),
            exit_price=108.0,
            shares=100,
            direction="long",
            pnl=500.0,
            pnl_pct=0.048,
            commission=10.0,
            slippage=5.0,
            holding_days=4,
        ),
    ]

    return trades


@pytest.fixture
def sample_backtest_result(sample_price_data, sample_signals):
    """
    生成示例回测结果
    """
    import sys
    import numpy as np

    sys.path.insert(0, "/opt/claude/mystocks_spec")
    from backtest.vectorized_backtester import VectorizedBacktester, BacktestConfig

    config = BacktestConfig(initial_capital=100000)
    backtester = VectorizedBacktester(config)

    result = backtester.run(sample_price_data, sample_signals)

    return result
