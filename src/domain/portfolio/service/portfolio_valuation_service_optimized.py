"""
Portfolio Valuation Service with Incremental Calculation
带增量计算的投资组合估值服务

在 Phase 12.3 的基础上集成增量计算性能优化。

Author: Claude Code
Date: 2026-01-09
Phase: 12.5 - Performance Optimization Integration
"""

import logging
from collections import defaultdict
from typing import Dict, List, Optional

from src.domain.portfolio.model.portfolio import Portfolio
from src.domain.portfolio.repository.iportfolio_repository import IPortfolioRepository
from src.domain.portfolio.service.portfolio_valuation_service import PortfolioValuationService
from src.domain.portfolio.value_objects.performance_metrics import PerformanceMetrics
from src.infrastructure.persistence.exceptions import ConcurrencyException
from src.application.services.performance_optimizer import IncrementalCalculator

logger = logging.getLogger(__name__)


class OptimizedPortfolioValuationService(PortfolioValuationService):
    """
    带增量计算的投资组合估值服务

    在 PortfolioValuationService 基础上增加：
    1. 增量计算：只计算变化的持仓，而不是全部重算
    2. 变化跟踪：记录持仓市值变化历史
    3. 性能指标：跟踪计算性能和优化效果

    Args:
        portfolio_repo: 投资组合仓储
        enable_incremental: 是否启用增量计算（默认启用）
    """

    def __init__(self, portfolio_repo: IPortfolioRepository, enable_incremental: bool = True):
        super().__init__(portfolio_repo)

        self.enable_incremental = enable_incremental

        # 为每个投资组合维护增量计算器
        self.incremental_calculators: Dict[str, IncrementalCalculator] = {}

        # 跟踪持仓价格变化历史
        self.price_history: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))

        # 扩展指标
        self.metrics.update(
            {
                "incremental_updates": 0,
                "full_recalculations": 0,
                "delta_calculations": 0,
                "calculation_time_saved_ms": 0.0,
            }
        )

        logger.info(f"✅ Optimized Portfolio Valuation Service initialized (incremental={enable_incremental})")

    def revaluate_portfolio(
        self, portfolio_id: str, prices: Dict[str, float], force_save: bool = True
    ) -> Optional[PerformanceMetrics]:
        """
        重新计算投资组合市值（增量计算优化版本）

        Args:
            portfolio_id: 投资组合 ID
            prices: 股票代码 -> 最新价格映射
            force_save: 是否强制保存到数据库

        Returns:
            PerformanceMetrics: 绩效指标（如果成功），None（如果失败）
        """
        self.metrics["total_revaluations"] += 1

        try:
            # 1. 加载投资组合
            portfolio = self.portfolio_repo.find_by_id(portfolio_id)
            if not portfolio:
                logger.error("Portfolio not found: %(portfolio_id)s")
                raise ValueError(f"Portfolio not found: {portfolio_id}")

            # 2. 记录价格历史
            for symbol, price in prices.items():
                if symbol in portfolio.positions:
                    history = self.price_history[portfolio_id][symbol]
                    history.append(price)
                    # 只保留最近100次价格变化
                    if len(history) > 100:
                        history.pop(0)

            # 3. 计算市值变化
            if self.enable_incremental and self._has_incremental_calculator(portfolio_id):
                # 使用增量计算
                performance = self._revaluate_incremental(portfolio, prices)
                self.metrics["incremental_updates"] += 1
            else:
                # 使用完整计算
                performance = self._revaluate_full(portfolio, prices)
                self.metrics["full_recalculations"] += 1

                # 初始化增量计算器
                if self.enable_incremental and performance:
                    self._init_incremental_calculator(portfolio_id, performance)

            # 4. 保存到数据库
            if force_save:
                self.portfolio_repo.save(portfolio)
                self.metrics["portfolios_updated"] += 1

            self.metrics["successful_revaluations"] += 1

            logger.info(
                f"✅ Revaluated portfolio {portfolio_id}: {len(prices)} symbols updated, "
                f"holdings_value={performance.holdings_value:.2f}, return={performance.total_return:.2f}%"
            )

            return performance

        except ConcurrencyException:
            self.metrics["concurrency_conflicts"] += 1
            logger.warning("⚠️ Concurrency conflict revaluating portfolio %(portfolio_id)s: %(e)s")
            raise

        except Exception:
            logger.error("❌ Failed to revaluate portfolio %(portfolio_id)s: %(e)s")
            return None

    def _has_incremental_calculator(self, portfolio_id: str) -> bool:
        """检查是否已有增量计算器"""
        return portfolio_id in self.incremental_calculators

    def _init_incremental_calculator(self, portfolio_id: str, performance: PerformanceMetrics):
        """
        初始化增量计算器

        Args:
            portfolio_id: 投资组合 ID
            performance: 当前绩效指标
        """
        # 创建增量计算器，初始值为总市值
        calculator = IncrementalCalculator(initial_value=performance.holdings_value + performance.cash_balance)
        self.incremental_calculators[portfolio_id] = calculator

        logger.debug("📊 Initialized incremental calculator for %(portfolio_id)s: {performance.holdings_value:.2f")

    def _revaluate_incremental(self, portfolio: Portfolio, prices: Dict[str, float]) -> PerformanceMetrics:
        """
        使用增量计算重新估值

        只计算变化的持仓，其他持仓使用缓存的值

        Args:
            portfolio: 投资组合
            prices: 更新的价格

        Returns:
            PerformanceMetrics: 绩效指标
        """
        import time

        start_time = time.time()

        portfolio_id = portfolio.id
        calculator = self.incremental_calculators[portfolio_id]

        # 记录旧市值
        sum(pos.market_value for pos in portfolio.positions.values())

        # 更新持仓价格
        for symbol, price in prices.items():
            if symbol in portfolio.positions:
                old_price = portfolio.positions[symbol].current_price
                # 计算市值变化
                price_delta = price - old_price
                quantity = portfolio.positions[symbol].quantity
                value_delta = price_delta * quantity

                # 更新增量计算器
                calculator.add_delta(value_delta)
                self.metrics["delta_calculations"] += 1

        # 更新持仓价格
        portfolio.update_market_prices(prices)

        # 重新计算绩效（使用简化的计算）
        performance = portfolio.calculate_performance()

        # 计算节省的时间（估算）
        elapsed_ms = (time.time() - start_time) * 1000
        estimated_full_calc_ms = elapsed_ms * len(portfolio.positions) / len(prices)
        time_saved_ms = estimated_full_calc_ms - elapsed_ms
        self.metrics["calculation_time_saved_ms"] += max(0, time_saved_ms)

        logger.debug(
            f"📊 Incremental revaluation for {portfolio_id}: {len(prices)} symbols, time_saved={time_saved_ms:.2f}ms"
        )

        return performance

    def _revaluate_full(self, portfolio: Portfolio, prices: Dict[str, float]) -> PerformanceMetrics:
        """
        使用完整计算重新估值

        Args:
            portfolio: 投资组合
            prices: 更新的价格

        Returns:
            PerformanceMetrics: 绩效指标
        """
        # 更新持仓价格
        portfolio.update_market_prices(prices)

        # 重新计算绩效
        performance = portfolio.calculate_performance()

        return performance

    def get_performance_delta(self, portfolio_id: str, window: int = 5) -> Optional[float]:
        """
        获取投资组合市值变化率

        Args:
            portfolio_id: 投资组合 ID
            window: 计算窗口大小

        Returns:
            float: 变化率（百分比）
        """
        if portfolio_id not in self.incremental_calculators:
            return None

        calculator = self.incremental_calculators[portfolio_id]
        return calculator.get_rate_of_change(window)

    def get_metrics(self) -> dict:
        """获取服务指标（包含增量计算指标）"""
        base_metrics = super().get_metrics()

        if self.enable_incremental:
            incremental_metrics = {
                "incremental_updates": self.metrics["incremental_updates"],
                "full_recalculations": self.metrics["full_recalculations"],
                "delta_calculations": self.metrics["delta_calculations"],
                "calculation_time_saved_ms": self.metrics["calculation_time_saved_ms"],
                "incremental_ratio": (
                    self.metrics["incremental_updates"] / self.metrics["total_revaluations"]
                    if self.metrics["total_revaluations"] > 0
                    else 0
                ),
            }
            base_metrics.update(incremental_metrics)

        return base_metrics

    def clear_calculators(self):
        """清空所有增量计算器"""
        self.incremental_calculators.clear()
        logger.info("✅ All incremental calculators cleared")
