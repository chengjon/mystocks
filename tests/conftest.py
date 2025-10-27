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


# ==================== 集成测试Fixtures ====================


@pytest.fixture
def sample_tick_data():
    """
    生成 Tick 数据样本 (高频时序数据)

    Returns:
        pd.DataFrame: Tick 数据 (1000 条记录)
    """
    import numpy as np

    base_time = datetime(2025, 1, 1, 9, 30, 0)
    return pd.DataFrame(
        {
            "ts": [base_time + timedelta(seconds=i) for i in range(1000)],
            "symbol": ["600000.SH"] * 1000,
            "exchange": ["SSE"] * 1000,
            "price": np.random.uniform(10.0, 20.0, 1000),
            "volume": np.random.randint(100, 10000, 1000),
            "amount": np.random.uniform(1000, 100000, 1000),
        }
    )


@pytest.fixture
def sample_minute_kline_data():
    """
    生成分钟 K 线数据样本

    Returns:
        pd.DataFrame: 分钟 K 线数据 (500 条记录)
    """
    import numpy as np

    base_time = datetime(2025, 1, 1, 9, 30, 0)
    return pd.DataFrame(
        {
            "ts": [base_time + timedelta(minutes=i) for i in range(500)],
            "symbol": ["600000.SH"] * 500,
            "exchange": ["SSE"] * 500,
            "open": np.random.uniform(10.0, 20.0, 500),
            "high": np.random.uniform(10.5, 20.5, 500),
            "low": np.random.uniform(9.5, 19.5, 500),
            "close": np.random.uniform(10.0, 20.0, 500),
            "volume": np.random.randint(10000, 100000, 500),
        }
    )


@pytest.fixture
def sample_daily_kline_data():
    """
    生成日线 K 线数据样本

    Returns:
        pd.DataFrame: 日线 K 线数据 (250 条记录)
    """
    import numpy as np

    base_date = datetime(2024, 1, 1)
    # Create 250 symbols by cycling through 3 symbols (83*3 + 1 = 250)
    symbols = ["600000.SH", "000001.SZ", "000858.SZ"] * 83 + ["600000.SH"]
    return pd.DataFrame(
        {
            "symbol": symbols,
            "trade_date": [base_date + timedelta(days=i) for i in range(250)],
            "open": np.random.uniform(10.0, 20.0, 250),
            "high": np.random.uniform(10.5, 20.5, 250),
            "low": np.random.uniform(9.5, 19.5, 250),
            "close": np.random.uniform(10.0, 20.0, 250),
            "volume": np.random.randint(10000000, 100000000, 250),
            "turnover": np.random.uniform(100000000, 1000000000, 250),
        }
    )


@pytest.fixture
def sample_symbols_info():
    """
    生成股票信息样本

    Returns:
        pd.DataFrame: 股票信息 (50 条记录)
    """
    symbols = [f"{i:06d}.SH" for i in range(600000, 600050)]
    return pd.DataFrame(
        {
            "symbol": symbols,
            "name": [f"股票{i}" for i in range(50)],
            "exchange": ["SSE"] * 50,
            "list_date": [datetime(2020, 1, 1) + timedelta(days=i) for i in range(50)],
            "total_share": [i * 1000000000 for i in range(1, 51)],
            "float_share": [i * 500000000 for i in range(1, 51)],
        }
    )


@pytest.fixture
def sample_technical_indicators():
    """
    生成技术指标样本

    Returns:
        pd.DataFrame: 技术指标 (1000 条记录)
    """
    import numpy as np

    base_date = datetime(2024, 1, 1)
    return pd.DataFrame(
        {
            "symbol": ["600000.SH"] * 1000,
            "trade_date": [base_date + timedelta(days=i // 4) for i in range(1000)],
            "sma_5": np.random.uniform(10.0, 20.0, 1000),
            "sma_10": np.random.uniform(10.0, 20.0, 1000),
            "sma_20": np.random.uniform(10.0, 20.0, 1000),
            "rsi": np.random.uniform(0, 100, 1000),
            "macd": np.random.uniform(-5, 5, 1000),
            "bb_upper": np.random.uniform(15.0, 25.0, 1000),
            "bb_lower": np.random.uniform(5.0, 15.0, 1000),
        }
    )


@pytest.fixture
def integration_test_data(
    sample_tick_data,
    sample_minute_kline_data,
    sample_daily_kline_data,
    sample_symbols_info,
    sample_technical_indicators,
):
    """
    提供所有集成测试所需的示例数据

    Returns:
        dict: 包含所有示例数据的字典
    """
    return {
        "tick_data": sample_tick_data,
        "minute_kline": sample_minute_kline_data,
        "daily_kline": sample_daily_kline_data,
        "symbols_info": sample_symbols_info,
        "technical_indicators": sample_technical_indicators,
    }


@pytest.fixture
def unified_manager():
    """
    创建测试用统一管理器（禁用监控）

    Returns:
        MyStocksUnifiedManager: 统一管理器实例
    """
    import sys

    sys.path.insert(0, "/opt/claude/mystocks_spec")
    from unified_manager import MyStocksUnifiedManager

    return MyStocksUnifiedManager(enable_monitoring=False)
