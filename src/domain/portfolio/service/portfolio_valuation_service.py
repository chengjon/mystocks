"""
Portfolio Valuation Service
投资组合估值服务

负责：
1. 根据最新价格重新计算投资组合市值
2. 更新持仓的未实现盈亏
3. 计算投资组合绩效指标
4. 集成并发控制（版本号 + 分布式锁）
"""

import logging
from typing import Dict, List, Optional

from src.domain.portfolio.repository.iportfolio_repository import IPortfolioRepository
from src.domain.portfolio.value_objects.performance_metrics import PerformanceMetrics
from src.infrastructure.persistence.exceptions import ConcurrencyException

logger = logging.getLogger(__name__)


class PortfolioValuationService:
    """
    投资组合估值服务

    职责：
    - 根据最新价格重新计算投资组合市值
    - 更新持仓的未实现盈亏
    - 计算投资组合绩效指标
    - 处理并发冲突（乐观锁 + 分布式锁）

    Args:
        portfolio_repo: 投资组合仓储
    """

    def __init__(self, portfolio_repo: IPortfolioRepository):
        self.portfolio_repo = portfolio_repo

        self.metrics = {
            "total_revaluations": 0,
            "successful_revaluations": 0,
            "concurrency_conflicts": 0,
            "portfolios_updated": 0,
            "last_revaluation_time": None,
        }

        logger.info("✅ Portfolio Valuation Service initialized")

    def revaluate_portfolio(
        self, portfolio_id: str, prices: Dict[str, float], force_save: bool = True
    ) -> Optional[PerformanceMetrics]:
        """
        重新计算投资组合市值

        Args:
            portfolio_id: 投资组合ID
            prices: 股票代码 -> 最新价格映射
            force_save: 是否强制保存到数据库

        Returns:
            PerformanceMetrics: 绩效指标（如果成功），None（如果失败）

        Raises:
            ValueError: 投资组合不存在
            ConcurrencyException: 并发冲突
        """
        self.metrics["total_revaluations"] += 1

        try:
            # 1. 加载投资组合
            portfolio = self.portfolio_repo.find_by_id(portfolio_id)
            if not portfolio:
                logger.error("Portfolio not found: %(portfolio_id)s")
                raise ValueError(f"Portfolio not found: {portfolio_id}")

            # 2. 更新持仓价格
            prices_before = {}
            prices_after = {}

            for symbol, position in portfolio.positions.items():
                if symbol in prices:
                    old_price = position.current_price
                    new_price = prices[symbol]

                    prices_before[symbol] = old_price
                    prices_after[symbol] = new_price

            # 3. 批量更新价格（Domain 层方法）
            portfolio.update_market_prices(prices)

            # 4. 重新计算绩效
            performance = portfolio.calculate_performance()

            # 5. 保存到数据库（会触发乐观锁检查）
            if force_save:
                self.portfolio_repo.save(portfolio)
                self.metrics["portfolios_updated"] += 1

            self.metrics["successful_revaluations"] += 1

            logger.info(
                f"✅ Revaluated portfolio {portfolio_id}: {len(prices_after)} symbols updated, "
                f"holdings_value={performance.holdings_value:.2f}, return={performance.total_return:.2f}%"
            )

            return performance

        except ConcurrencyException as e:
            self.metrics["concurrency_conflicts"] += 1
            logger.warning("⚠️ Concurrency conflict revaluating portfolio %(portfolio_id)s: %(e)s")
            raise

        except Exception as e:
            logger.error("❌ Failed to revaluate portfolio %(portfolio_id)s: %(e)s")
            return None

    def batch_revaluate_portfolios(
        self, portfolio_ids: List[str], prices: Dict[str, float]
    ) -> Dict[str, Optional[PerformanceMetrics]]:
        """
        批量重新计算多个投资组合

        Args:
            portfolio_ids: 投资组合ID列表
            prices: 股票代码 -> 最新价格映射

        Returns:
            Dict[str, PerformanceMetrics]: 投资组合ID -> 绩效指标映射
        """
        results = {}

        for portfolio_id in portfolio_ids:
            try:
                performance = self.revaluate_portfolio(portfolio_id, prices)
                results[portfolio_id] = performance
            except Exception as e:
                logger.error("Failed to revaluate portfolio %(portfolio_id)s: %(e)s")
                results[portfolio_id] = None

        logger.info(
            f"✅ Batch revaluation completed: {len([p for p in results.values() if p])} / {len(portfolio_ids)} successful"
        )

        return results

    def get_portfolio_symbols(self, portfolio_id: str) -> List[str]:
        """
        获取投资组合的股票代码列表

        Args:
            portfolio_id: 投资组合ID

        Returns:
            List[str]: 股票代码列表
        """
        portfolio = self.portfolio_repo.find_by_id(portfolio_id)
        if not portfolio:
            return []

        return list(portfolio.positions.keys())

    def get_all_portfolio_symbols(self) -> Dict[str, List[str]]:
        """
        获取所有投资组合的股票代码映射

        Returns:
            Dict[str, List[str]]: 投资组合ID -> 股票代码列表映射
        """
        portfolios = self.portfolio_repo.find_all(limit=1000)
        return {p.id: list(p.positions.keys()) for p in portfolios}

    def get_metrics(self) -> dict:
        """获取服务指标"""
        return {
            **self.metrics,
            "success_rate": (
                self.metrics["successful_revaluations"] / self.metrics["total_revaluations"]
                if self.metrics["total_revaluations"] > 0
                else 0
            ),
            "conflict_rate": (
                self.metrics["concurrency_conflicts"] / self.metrics["total_revaluations"]
                if self.metrics["total_revaluations"] > 0
                else 0
            ),
        }
