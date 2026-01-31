"""
Backtest Engine Unit Tests

回测引擎单元测试
"""

from datetime import datetime
from decimal import Decimal

import pytest


# 测试 PerformanceMetrics
class TestPerformanceMetrics:
    """性能指标计算测试"""

    def test_calculate_total_return(self):
        """测试总收益率计算"""
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../web/backend"))

        from app.backtest.performance_metrics import PerformanceMetrics

        metrics = PerformanceMetrics()
        equity_values = [100000, 105000, 110000, 108000, 115000]
        initial_capital = 100000

        total_return = metrics._calculate_total_return(equity_values, initial_capital)
        assert total_return == pytest.approx(0.15, rel=0.01)  # 15% return

    def test_calculate_max_drawdown(self):
        """测试最大回撤计算"""
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../web/backend"))

        from app.backtest.performance_metrics import PerformanceMetrics

        metrics = PerformanceMetrics()
        equity_curve = [
            {"equity": Decimal("100000"), "drawdown": Decimal("0")},
            {"equity": Decimal("110000"), "drawdown": Decimal("0")},  # 新高
            {"equity": Decimal("99000"), "drawdown": Decimal("0.1")},  # 回撤10%
            {"equity": Decimal("105000"), "drawdown": Decimal("0.045")},
            {"equity": Decimal("120000"), "drawdown": Decimal("0")},  # 新高
        ]

        max_dd = metrics._calculate_max_drawdown(equity_curve)
        assert max_dd == pytest.approx(0.1, rel=0.01)  # 10% max drawdown

    def test_calculate_sharpe_ratio(self):
        """测试夏普比率计算"""
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../web/backend"))

        from app.backtest.performance_metrics import PerformanceMetrics

        metrics = PerformanceMetrics(risk_free_rate=0.03)
        annualized_return = 0.15  # 15%
        volatility = 0.20  # 20%

        sharpe = metrics._calculate_sharpe_ratio(annualized_return, volatility)
        expected = (0.15 - 0.03) / 0.20  # = 0.6
        assert sharpe == pytest.approx(expected, rel=0.01)

    def test_calculate_trade_metrics(self):
        """测试交易指标计算"""
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../web/backend"))

        from app.backtest.performance_metrics import PerformanceMetrics

        metrics = PerformanceMetrics()
        trades = [
            {"profit_loss": 1000},  # 赢
            {"profit_loss": -500},  # 输
            {"profit_loss": 800},  # 赢
            {"profit_loss": -300},  # 输
            {"profit_loss": 1200},  # 赢
        ]

        result = metrics._calculate_trade_metrics(trades)
        assert result["win_rate"] == pytest.approx(0.6, rel=0.01)  # 60% win rate
        assert result["avg_win"] > 0
        assert result["avg_loss"] > 0

    def test_empty_metrics(self):
        """测试空数据返回"""
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../web/backend"))

        from app.backtest.performance_metrics import PerformanceMetrics

        metrics = PerformanceMetrics()
        result = metrics.calculate_all_metrics([], [], Decimal("100000"))

        assert result["total_return"] == 0.0
        assert result["sharpe_ratio"] == 0.0


# 测试 PortfolioManager
class TestPortfolioManager:
    """组合管理器测试"""

    def test_initialization(self):
        """测试初始化"""
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../web/backend"))

        from app.backtest.portfolio_manager import PortfolioManager

        pm = PortfolioManager(
            initial_capital=Decimal("100000"),
            commission_rate=Decimal("0.0003"),
            slippage_rate=Decimal("0.001"),
        )

        assert pm.cash == Decimal("100000")
        assert pm.equity == Decimal("100000")
        assert len(pm.positions) == 0

    def test_calculate_position_size(self):
        """测试仓位计算"""
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../web/backend"))

        from app.backtest.portfolio_manager import PortfolioManager

        pm = PortfolioManager(initial_capital=Decimal("100000"))
        quantity = pm.calculate_position_size(
            symbol="000001",
            signal_strength=0.8,
            max_position_size=0.1,
            current_price=Decimal("10"),
        )

        # 100000 * 0.1 * 0.8 = 8000, 8000 / 10 = 800
        # 向下取整到100的倍数 = 800
        assert quantity == 800


# 测试 ExecutionHandler
class TestExecutionHandler:
    """执行处理器测试"""

    def test_calculate_commission(self):
        """测试手续费计算"""
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../web/backend"))

        from app.backtest.execution_handler import ExecutionHandler

        executor = ExecutionHandler(commission_rate=Decimal("0.0003"), min_commission=Decimal("5"))

        # 大额交易
        commission = executor._calculate_commission(1000, Decimal("100"))
        # 100000 * 0.0003 = 30
        assert commission == Decimal("30.00")

        # 小额交易（应用最小手续费）
        commission = executor._calculate_commission(10, Decimal("10"))
        # 100 * 0.0003 = 0.03, 应用最小5
        assert commission == Decimal("5.00")


# 测试 RiskManager
class TestRiskManager:
    """风险管理器测试"""

    def test_check_stop_loss(self):
        """测试止损检查"""
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../web/backend"))

        from app.backtest.portfolio_manager import Position
        from app.backtest.risk_manager import RiskManager

        rm = RiskManager(stop_loss_pct=0.05)

        # 创建一个亏损的持仓
        position = Position("000001")
        position.quantity = 1000
        position.avg_cost = Decimal("100")

        # 当前价格跌幅6%，应该触发止损
        current_price = Decimal("94")
        reason = rm.check_stop_loss_take_profit("000001", position, current_price)
        assert reason is not None
        assert "止损" in reason

    def test_check_take_profit(self):
        """测试止盈检查"""
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../web/backend"))

        from app.backtest.portfolio_manager import Position
        from app.backtest.risk_manager import RiskManager

        rm = RiskManager(take_profit_pct=0.10)

        # 创建一个盈利的持仓
        position = Position("000001")
        position.quantity = 1000
        position.avg_cost = Decimal("100")

        # 当前价格涨幅12%，应该触发止盈
        current_price = Decimal("112")
        reason = rm.check_stop_loss_take_profit("000001", position, current_price)
        assert reason is not None
        assert "止盈" in reason


# 测试 Events
class TestEvents:
    """事件测试"""

    def test_market_event(self):
        """测试市场数据事件"""
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../web/backend"))

        from app.backtest.events import MarketEvent

        event = MarketEvent(
            symbol="000001",
            trade_date=datetime(2024, 1, 1),
            open_price=Decimal("10"),
            high_price=Decimal("11"),
            low_price=Decimal("9.5"),
            close_price=Decimal("10.5"),
            volume=1000000,
        )

        assert event.symbol == "000001"
        assert event.close == Decimal("10.5")

    def test_fill_event(self):
        """测试成交事件"""
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../web/backend"))

        from app.backtest.events import FillEvent

        event = FillEvent(
            symbol="000001",
            trade_date=datetime(2024, 1, 1),
            action="BUY",
            quantity=1000,
            fill_price=Decimal("10"),
            commission=Decimal("3"),
        )

        # 总金额 = 10 * 1000 + 3 = 10003
        assert event.amount == Decimal("10003")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
