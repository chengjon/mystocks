"""
Backtest Engine

事件驱动的回测引擎核心实现
"""

import logging
from collections import deque
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Callable, Dict, Optional

from app.backtest.events import (
    FillEvent,
    MarketEvent,
    OrderEvent,
    ProgressEvent,
    SignalEvent,
)
from app.backtest.execution_handler import ExecutionHandler
from app.backtest.performance_metrics import PerformanceMetrics
from app.backtest.portfolio_manager import PortfolioManager
from app.backtest.risk_manager import RiskManager

logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    事件驱动的回测引擎

    核心组件：
    - PortfolioManager: 管理持仓和资金
    - RiskManager: 风险控制
    - ExecutionHandler: 订单执行模拟
    - PerformanceMetrics: 性能指标计算
    """

    def __init__(
        self,
        strategy_config: Dict[str, Any],
        backtest_config: Dict[str, Any],
        data_source: Any,  # 数据源（Composite/Mock/Real）
        progress_callback: Optional[Callable[[ProgressEvent], None]] = None,
    ):
        """
        初始化回测引擎

        Args:
            strategy_config: 策略配置
            backtest_config: 回测配置
            data_source: 数据源
            progress_callback: 进度回调函数（用于WebSocket推送）
        """
        self.strategy_config = strategy_config
        self.backtest_config = backtest_config
        self.data_source = data_source
        self.progress_callback = progress_callback

        # 提取配置
        self.symbols = backtest_config["symbols"]
        self.start_date = backtest_config["start_date"]
        self.end_date = backtest_config["end_date"]
        self.initial_capital = Decimal(str(backtest_config["initial_capital"]))
        self.commission_rate = Decimal(str(backtest_config.get("commission_rate", 0.0003)))
        self.slippage_rate = Decimal(str(backtest_config.get("slippage_rate", 0.001)))
        self.benchmark = backtest_config.get("benchmark", "sh000001")  # 默认上证指数

        # 策略参数
        self.strategy_type = strategy_config.get("strategy_type", "custom")
        self.max_position_size = strategy_config.get("max_position_size", 0.1)
        self.stop_loss_pct = strategy_config.get("stop_loss_percent")
        self.take_profit_pct = strategy_config.get("take_profit_percent")

        # 初始化组件
        self.portfolio = PortfolioManager(
            initial_capital=self.initial_capital,
            commission_rate=self.commission_rate,
            slippage_rate=self.slippage_rate,
        )

        self.risk_manager = RiskManager(
            max_position_size=self.max_position_size,
            stop_loss_pct=self.stop_loss_pct,
            take_profit_pct=self.take_profit_pct,
        )

        self.execution = ExecutionHandler(commission_rate=self.commission_rate, slippage_rate=self.slippage_rate)

        self.performance = PerformanceMetrics()

        # 事件队列
        self.event_queue: deque = deque()

        # 市场数据缓存
        self.market_data: Dict[str, Dict[datetime, MarketEvent]] = {}
        self.current_date: Optional[datetime] = None

        # 回测状态
        self.is_running = False
        self.total_days = 0
        self.current_day_index = 0

        logger.info("回测引擎初始化完成: {len(self.symbols)}只股票, {self.start_date} 到 {self.end_date}")

    def run(self) -> Dict[str, Any]:
        """
        运行回测

        Returns:
            回测结果字典
        """
        logger.info("开始回测...")
        self.is_running = True

        try:
            # 1. 加载市场数据
            self._load_market_data()

            # 2. 执行回测循环
            self._run_backtest_loop()

            # 3. 计算性能指标
            results = self._calculate_results()

            logger.info("回测完成")
            self._send_progress(100.0, self.end_date, "回测完成")

            return results

        except Exception as e:
            logger.error("回测过程中发生错误: {str(e)}", exc_info=True)
            self._send_progress(0.0, self.current_date or self.start_date, f"回测失败: {str(e)}")
            raise

        finally:
            self.is_running = False

    def _load_market_data(self):
        """从数据源加载市场数据"""
        logger.info("加载市场数据...")

        for symbol in self.symbols:
            try:
                # 从数据源获取历史数据
                df = self.data_source.get_stock_history(
                    symbol=symbol, start_date=self.start_date, end_date=self.end_date
                )

                if df is None or df.empty:
                    logger.warning("未找到 %(symbol)s 的历史数据")
                    continue

                # 转换为MarketEvent并缓存
                self.market_data[symbol] = {}
                for idx, row in df.iterrows():
                    trade_date = row.get("trade_date") or idx
                    if not isinstance(trade_date, datetime):
                        trade_date = datetime.strptime(str(trade_date), "%Y-%m-%d")

                    market_event = MarketEvent(
                        symbol=symbol,
                        trade_date=trade_date,
                        open_price=Decimal(str(row.get("open", 0))),
                        high_price=Decimal(str(row.get("high", 0))),
                        low_price=Decimal(str(row.get("low", 0))),
                        close_price=Decimal(str(row.get("close", 0))),
                        volume=int(row.get("volume", 0)),
                        adj_close=Decimal(str(row.get("adj_close", row.get("close", 0)))),
                    )
                    self.market_data[symbol][trade_date] = market_event

                logger.info("加载 %(symbol)s 数据: {len(self.market_data[symbol])} 条记录")

            except Exception:
                logger.error("加载 %(symbol)s 数据失败: {str(e)}")
                continue

        if not self.market_data:
            raise ValueError("没有加载到任何市场数据")

        # 计算总交易日数
        all_dates = set()
        for symbol_data in self.market_data.values():
            all_dates.update(symbol_data.keys())
        self.total_days = len(sorted(all_dates))

        logger.info("市场数据加载完成: {len(self.market_data)} 只股票, {self.total_days} 个交易日")

    def _run_backtest_loop(self):
        """执行回测主循环"""
        # 获取所有交易日期并排序
        all_dates = set()
        for symbol_data in self.market_data.values():
            all_dates.update(symbol_data.keys())
        trading_dates = sorted(all_dates)

        logger.info("开始事件循环: {len(trading_dates)} 个交易日")

        for day_index, trade_date in enumerate(trading_dates):
            self.current_date = trade_date
            self.current_day_index = day_index

            # 发送进度更新
            progress = (day_index / len(trading_dates)) * 100
            self._send_progress(progress, trade_date, f"处理第 {day_index + 1}/{len(trading_dates)} 天")

            # 1. 生成市场数据事件
            self._generate_market_events(trade_date)

            # 2. 处理事件队列
            self._process_event_queue()

            # 3. 检查止损止盈
            self._check_stop_loss_take_profit(trade_date)

            # 4. 记录资金曲线
            self.portfolio.record_equity_curve(trade_date)

            # 5. 更新风险指标
            self.risk_manager.update_risk_metrics(self.portfolio, trade_date)

        logger.info("事件循环完成")

    def _generate_market_events(self, trade_date: datetime):
        """生成市场数据事件"""
        for symbol, data_dict in self.market_data.items():
            if trade_date in data_dict:
                market_event = data_dict[trade_date]
                self.event_queue.append(market_event)

    def _process_event_queue(self):
        """处理事件队列"""
        while len(self.event_queue) > 0:
            event = self.event_queue.popleft()

            if isinstance(event, MarketEvent):
                self._on_market_event(event)
            elif isinstance(event, SignalEvent):
                self._on_signal_event(event)
            elif isinstance(event, OrderEvent):
                self._on_order_event(event)
            elif isinstance(event, FillEvent):
                self._on_fill_event(event)

    def _on_market_event(self, event: MarketEvent):
        """
        处理市场数据事件

        1. 更新Portfolio的市场数据
        2. 生成交易信号
        """
        # 更新组合的市场数据
        self.portfolio.update_market_data(event)

        # 生成交易信号
        signal = self._generate_signal(event)
        if signal:
            self.event_queue.append(signal)

    def _generate_signal(self, market_event: MarketEvent) -> Optional[SignalEvent]:
        """
        生成交易信号（策略逻辑）

        这里实现一个简单的动量策略示例
        实际使用时应该根据strategy_type调用不同的策略

        Args:
            market_event: 市场数据事件

        Returns:
            交易信号（如果有）
        """
        symbol = market_event.symbol

        # 获取历史数据用于计算指标
        symbol_history = self.market_data.get(symbol, {})
        current_date = market_event.trade_date

        # 获取过去N天的收盘价
        lookback_days = 20
        past_closes = []
        for i in range(lookback_days, 0, -1):
            past_date = current_date - timedelta(days=i)
            if past_date in symbol_history:
                past_closes.append(float(symbol_history[past_date].close))

        if len(past_closes) < lookback_days:
            # 数据不足，不生成信号
            return None

        # 简单动量策略：计算价格相对于均线的位置
        current_price = float(market_event.close)
        ma20 = sum(past_closes) / len(past_closes)

        # 检查当前持仓
        position = self.portfolio.get_position(symbol)
        has_position = position and position.quantity > 0

        # 生成信号
        if current_price > ma20 * 1.02 and not has_position:
            # 价格突破均线2%，买入信号
            return SignalEvent(
                symbol=symbol,
                trade_date=current_date,
                signal_type="LONG",
                strength=0.8,
                reason=f"价格突破MA20: {current_price:.2f} > {ma20:.2f}",
            )
        elif current_price < ma20 * 0.98 and has_position:
            # 价格跌破均线2%，卖出信号
            return SignalEvent(
                symbol=symbol,
                trade_date=current_date,
                signal_type="EXIT",
                strength=1.0,
                reason=f"价格跌破MA20: {current_price:.2f} < {ma20:.2f}",
            )

        return None

    def _on_signal_event(self, event: SignalEvent):
        """
        处理交易信号事件

        1. 计算仓位大小
        2. 生成订单
        """
        symbol = event.symbol
        current_price = self.portfolio.current_prices.get(symbol)

        if not current_price:
            logger.warning("未找到 %(symbol)s 的当前价格")
            return

        # 计算仓位大小
        if event.signal_type == "LONG":
            quantity = self.portfolio.calculate_position_size(
                symbol=symbol,
                signal_strength=event.strength,
                max_position_size=self.max_position_size,
                current_price=current_price,
            )

            if quantity > 0:
                order = OrderEvent(
                    symbol=symbol,
                    trade_date=event.trade_date,
                    order_type="MARKET",
                    action="BUY",
                    quantity=quantity,
                    strategy_id=self.strategy_config.get("strategy_id"),
                )
                self.event_queue.append(order)

        elif event.signal_type in ["SHORT", "EXIT"]:
            # 平仓
            position = self.portfolio.get_position(symbol)
            if position and position.quantity > 0:
                order = OrderEvent(
                    symbol=symbol,
                    trade_date=event.trade_date,
                    order_type="MARKET",
                    action="SELL",
                    quantity=position.quantity,
                    strategy_id=self.strategy_config.get("strategy_id"),
                )
                self.event_queue.append(order)

    def _on_order_event(self, event: OrderEvent):
        """
        处理订单事件

        1. 风险检查
        2. 执行订单
        3. 生成成交事件
        """
        symbol = event.symbol
        current_price = self.portfolio.current_prices.get(symbol)

        if not current_price:
            logger.warning("未找到 %(symbol)s 的当前价格")
            return

        # 风险检查
        is_valid, reject_reason = self.risk_manager.validate_order(event, self.portfolio, current_price)

        if not is_valid:
            logger.info("订单被拒绝: %(symbol)s {event.action} {event.quantity} - %(reject_reason)s")
            return

        # 执行订单
        fill_event = self.execution.execute_order(event, current_price)

        if fill_event:
            self.event_queue.append(fill_event)

    def _on_fill_event(self, event: FillEvent):
        """
        处理成交事件

        更新Portfolio
        """
        success = self.portfolio.process_fill(event)
        if success:
            logger.info("成交: {event.symbol} {event.action} {event.quantity}@{event.fill_price}")
        else:
            logger.warning("成交失败: %(event)s")

    def _check_stop_loss_take_profit(self, trade_date: datetime):
        """检查所有持仓的止损止盈"""
        for symbol, position in list(self.portfolio.positions.items()):
            if position.quantity == 0:
                continue

            current_price = self.portfolio.current_prices.get(symbol)
            if not current_price:
                continue

            # 检查是否需要强制平仓
            should_close, reason = self.risk_manager.should_force_close_position(symbol, position, current_price)

            if should_close:
                logger.info("强制平仓: %(symbol)s - %(reason)s")

                # 生成平仓订单
                order = OrderEvent(
                    symbol=symbol,
                    trade_date=trade_date,
                    order_type="MARKET",
                    action="SELL",
                    quantity=abs(position.quantity),
                    strategy_id=self.strategy_config.get("strategy_id"),
                )
                self.event_queue.append(order)

    def _calculate_results(self) -> Dict[str, Any]:
        """计算回测结果"""
        logger.info("计算性能指标...")

        # 获取资金曲线和交易记录
        equity_curve = self.portfolio.get_equity_curve()
        trades = self.portfolio.get_trades()

        # 计算性能指标
        performance_metrics = self.performance.calculate_all_metrics(
            equity_curve=equity_curve,
            trades=trades,
            initial_capital=self.initial_capital,
        )

        # 组合摘要
        portfolio_summary = self.portfolio.get_portfolio_summary()

        # 风险摘要
        risk_summary = self.risk_manager.get_risk_summary(self.portfolio)

        # 返回完整结果
        return {
            "backtest_id": self.backtest_config.get("backtest_id"),
            "strategy_id": self.strategy_config.get("strategy_id"),
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "symbols": self.symbols,
            "initial_capital": float(self.initial_capital),
            "final_capital": float(self.portfolio.equity),
            "performance_metrics": performance_metrics,
            "portfolio_summary": portfolio_summary,
            "risk_summary": risk_summary,
            "equity_curve": [
                {
                    "trade_date": point["trade_date"].isoformat(),
                    "equity": float(point["equity"]),
                    "drawdown": float(point["drawdown"]),
                }
                for point in equity_curve
            ],
            "trades": trades,
            "total_trades": len(trades),
            "status": "completed",
        }

    def _send_progress(self, progress: float, current_date: datetime, message: str):
        """发送进度更新"""
        if self.progress_callback:
            progress_event = ProgressEvent(
                backtest_id=self.backtest_config.get("backtest_id", 0),
                progress=progress,
                current_date=current_date,
                message=message,
            )
            try:
                self.progress_callback(progress_event)
            except Exception:
                logger.warning("发送进度更新失败: {str(e)}")

    def stop(self):
        """停止回测"""
        logger.info("停止回测...")
        self.is_running = False
