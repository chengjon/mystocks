"""
回测引擎 - 支持策略回测和性能评估

复用现有组件:
- DataService: 获取历史OHLCV数据
- StrategyRegistry: 获取策略实例
"""

from dataclasses import dataclass
from typing import Dict, Any
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


@dataclass
class BacktestConfig:
    """回测配置"""

    initial_capital: float = 1000000.0  # 初始资金
    commission_rate: float = 0.0003  # 佣金率
    slippage_rate: float = 0.0001  # 滑点率
    position_size: float = 0.1  # 单次交易仓位比例
    max_positions: int = 10  # 最大持仓数


@dataclass
class BacktestResult:
    """回测结果"""

    backtest_id: str
    strategy_id: str
    symbol: str
    total_return: float  # 总收益率
    annual_return: float  # 年化收益率
    sharpe_ratio: float  # 夏普比率
    max_drawdown: float  # 最大回撤
    win_rate: float  # 胜率
    total_trades: int  # 总交易次数
    profit_factor: float  # 盈亏比
    equity_curve: pd.DataFrame  # 权益曲线
    trade_history: pd.DataFrame  # 交易历史


class BacktestEngine:
    """回测引擎"""

    def __init__(self, config: BacktestConfig = None):
        self.config = config or BacktestConfig()

    def run_backtest(
        self,
        strategy_id: str,
        symbol: str,
        start_date: str,
        end_date: str,
        strategy_params: Dict[str, Any] = None,
    ) -> BacktestResult:
        """
        运行单策略回测

        Args:
            strategy_id: 策略ID
            symbol: 股票代码
            start_date: 回测开始日期
            end_date: 回测结束日期
            strategy_params: 策略参数

        Returns:
            BacktestResult: 回测结果
        """
        try:
            from app.strategies.strategy_base import get_strategy_registry
            import uuid

            # 1. 获取策略实例
            registry = get_strategy_registry()
            strategy = registry.get_strategy(strategy_id)

            if not strategy:
                raise ValueError(f"未知策略: {strategy_id}")

            # 2. 执行策略生成信号
            signals_df = strategy.execute(symbol, start_date, end_date, strategy_params or {})

            if signals_df.empty:
                logger.warning(f"策略 {strategy_id} 未生成任何信号")
                return self._empty_result(strategy_id, symbol)

            # 3. 模拟交易执行
            trades_df = self._simulate_trades(signals_df)

            # 4. 计算回测指标
            result = self._calculate_metrics(
                backtest_id=str(uuid.uuid4()),
                strategy_id=strategy_id,
                symbol=symbol,
                trades_df=trades_df,
                signals_df=signals_df,
            )

            return result

        except Exception as e:
            logger.error(f"回测执行失败: {e}")
            raise

    def _simulate_trades(self, signals_df: pd.DataFrame) -> pd.DataFrame:
        """模拟交易执行"""
        trades = []
        position = 0  # 0=空仓, 1=持仓
        entry_price = 0.0

        for idx, row in signals_df.iterrows():
            signal = row["signal"]
            price = row["price"]
            date = row["date"]

            # 买入信号
            if signal == 1 and position == 0:
                position = 1
                entry_price = price * (1 + self.config.slippage_rate)
                shares = int((self.config.initial_capital * self.config.position_size) / entry_price)
                trades.append(
                    {
                        "date": date,
                        "action": "BUY",
                        "price": entry_price,
                        "shares": shares,
                        "amount": entry_price * shares,
                    }
                )

            # 卖出信号
            elif signal == -1 and position == 1:
                exit_price = price * (1 - self.config.slippage_rate)
                shares = trades[-1]["shares"]

                # 计算盈亏
                profit = (exit_price - entry_price) * shares
                commission = (entry_price + exit_price) * shares * self.config.commission_rate
                net_profit = profit - commission

                trades.append(
                    {
                        "date": date,
                        "action": "SELL",
                        "price": exit_price,
                        "shares": shares,
                        "amount": exit_price * shares,
                        "commission": commission,
                        "profit": net_profit,
                        "return_rate": net_profit / (entry_price * shares),
                    }
                )

                position = 0

        return pd.DataFrame(trades)

    def _calculate_metrics(
        self,
        backtest_id: str,
        strategy_id: str,
        symbol: str,
        trades_df: pd.DataFrame,
        signals_df: pd.DataFrame,
    ) -> BacktestResult:
        """计算回测指标"""
        if trades_df.empty:
            return self._empty_result(strategy_id, symbol, backtest_id)

        # 提取买卖对
        sell_trades = trades_df[trades_df["action"] == "SELL"]

        # 总收益率
        total_profit = sell_trades["profit"].sum() if not sell_trades.empty else 0
        total_return = total_profit / self.config.initial_capital

        # 年化收益率
        days = (pd.to_datetime(signals_df["date"].max()) - pd.to_datetime(signals_df["date"].min())).days
        annual_return = (1 + total_return) ** (365.0 / days) - 1 if days > 0 else 0

        # 胜率
        if not sell_trades.empty:
            wins = (sell_trades["profit"] > 0).sum()
            win_rate = wins / len(sell_trades)
        else:
            win_rate = 0.0

        # 夏普比率
        returns = sell_trades["return_rate"].values if not sell_trades.empty else np.array([])
        sharpe_ratio = (
            (returns.mean() / returns.std() * np.sqrt(252)) if len(returns) > 1 and returns.std() > 0 else 0.0
        )

        # 盈亏比
        if not sell_trades.empty:
            profits = sell_trades[sell_trades["profit"] > 0]["profit"].sum()
            losses = abs(sell_trades[sell_trades["profit"] < 0]["profit"].sum())
            profit_factor = profits / losses if losses > 0 else 0.0
        else:
            profit_factor = 0.0

        # 权益曲线
        equity_curve = self._calculate_equity_curve(signals_df, trades_df)

        # 最大回撤
        max_drawdown = self._calculate_max_drawdown(equity_curve)

        return BacktestResult(
            backtest_id=backtest_id,
            strategy_id=strategy_id,
            symbol=symbol,
            total_return=total_return,
            annual_return=annual_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            total_trades=len(sell_trades),
            profit_factor=profit_factor,
            equity_curve=equity_curve,
            trade_history=trades_df,
        )

    def _calculate_equity_curve(self, signals_df: pd.DataFrame, trades_df: pd.DataFrame) -> pd.DataFrame:
        """计算权益曲线"""
        equity = pd.DataFrame({"date": signals_df["date"], "equity": self.config.initial_capital})

        cumulative_profit = 0.0
        for idx, row in trades_df.iterrows():
            if row["action"] == "SELL":
                cumulative_profit += row["profit"]
                mask = equity["date"] >= row["date"]
                equity.loc[mask, "equity"] = self.config.initial_capital + cumulative_profit

        return equity

    def _calculate_max_drawdown(self, equity_curve: pd.DataFrame) -> float:
        """计算最大回撤"""
        if equity_curve.empty:
            return 0.0

        equity_values = equity_curve["equity"].values
        running_max = np.maximum.accumulate(equity_values)
        drawdown = (equity_values - running_max) / running_max
        return abs(drawdown.min())

    def _empty_result(self, strategy_id: str, symbol: str, backtest_id: str = "unknown") -> BacktestResult:
        """返回空回测结果"""
        return BacktestResult(
            backtest_id=backtest_id,
            strategy_id=strategy_id,
            symbol=symbol,
            total_return=0.0,
            annual_return=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            win_rate=0.0,
            total_trades=0,
            profit_factor=0.0,
            equity_curve=pd.DataFrame(),
            trade_history=pd.DataFrame(),
        )


# 全局单例
_backtest_engine = None


def get_backtest_engine() -> BacktestEngine:
    """获取回测引擎单例"""
    global _backtest_engine
    if _backtest_engine is None:
        _backtest_engine = BacktestEngine()
    return _backtest_engine
