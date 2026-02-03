"""
Base Optimizer

参数优化基类 - 定义优化器接口和通用功能
"""

import copy
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """
    优化结果

    存储单次参数组合的回测结果
    """

    # 参数组合
    parameters: Dict[str, Any]

    # 性能指标
    total_return: float = 0.0  # 总收益率
    annual_return: float = 0.0  # 年化收益率
    sharpe_ratio: float = 0.0  # 夏普比率
    max_drawdown: float = 0.0  # 最大回撤
    win_rate: float = 0.0  # 胜率
    profit_factor: float = 0.0  # 盈亏比

    # 交易统计
    total_trades: int = 0  # 总交易次数
    winning_trades: int = 0  # 盈利交易次数
    losing_trades: int = 0  # 亏损交易次数

    # 其他指标
    calmar_ratio: float = 0.0  # 卡玛比率
    sortino_ratio: float = 0.0  # 索提诺比率

    # 元数据
    optimization_time: float = 0.0  # 优化耗时(秒)
    backtest_start: Optional[datetime] = None
    backtest_end: Optional[datetime] = None

    # 额外信息
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """计算衍生指标"""
        if self.total_trades > 0:
            self.win_rate = self.winning_trades / self.total_trades

    def get_score(self, metric: str = "sharpe_ratio") -> float:
        """
        获取评分指标值

        Args:
            metric: 评分指标名称

        Returns:
            指标值
        """
        return getattr(self, metric, 0.0)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "parameters": self.parameters,
            "total_return": self.total_return,
            "annual_return": self.annual_return,
            "sharpe_ratio": self.sharpe_ratio,
            "max_drawdown": self.max_drawdown,
            "win_rate": self.win_rate,
            "profit_factor": self.profit_factor,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "calmar_ratio": self.calmar_ratio,
            "sortino_ratio": self.sortino_ratio,
            "optimization_time": self.optimization_time,
            "metadata": self.metadata,
        }


@dataclass
class ParameterSpace:
    """
    参数空间定义

    定义单个参数的取值范围
    """

    name: str  # 参数名
    param_type: str  # 参数类型: int, float, choice
    min_value: Optional[float] = None  # 最小值 (int/float)
    max_value: Optional[float] = None  # 最大值 (int/float)
    step: Optional[float] = None  # 步长 (网格搜索用)
    choices: Optional[List[Any]] = None  # 选项列表 (choice类型)

    def get_grid_values(self) -> List[Any]:
        """获取网格搜索的所有取值"""
        if self.param_type == "choice":
            return self.choices or []

        if self.min_value is None or self.max_value is None:
            return []

        step = self.step or 1
        values = []
        current = self.min_value

        while current <= self.max_value:
            if self.param_type == "int":
                values.append(int(current))
            else:
                values.append(current)
            current += step

        return values

    def get_random_value(self, rng=None) -> Any:
        """获取随机取值"""
        import random

        rand = rng or random

        if self.param_type == "choice":
            return rand.choice(self.choices) if self.choices else None

        if self.min_value is None or self.max_value is None:
            return None

        if self.param_type == "int":
            return rand.randint(int(self.min_value), int(self.max_value))
        else:
            return rand.uniform(self.min_value, self.max_value)


class BaseOptimizer(ABC):
    """
    参数优化基类

    提供优化器的通用接口和辅助方法
    """

    def __init__(
        self,
        strategy_type: str,
        parameter_spaces: List[ParameterSpace],
        objective: str = "sharpe_ratio",
        maximize: bool = True,
    ):
        """
        初始化优化器

        Args:
            strategy_type: 策略类型
            parameter_spaces: 参数空间列表
            objective: 优化目标指标
            maximize: 是否最大化目标
        """
        self.strategy_type = strategy_type
        self.parameter_spaces = parameter_spaces
        self.objective = objective
        self.maximize = maximize

        # 结果存储
        self.results: List[OptimizationResult] = []
        self.best_result: Optional[OptimizationResult] = None

        # 回测引擎引用 (由子类设置)
        self.backtest_engine = None

        # 数据源 (使用mock数据)
        self._data_source = None
        self._market_data = None

        logger.info("优化器初始化: 策略=%(strategy_type)s, 目标=%(objective)s, 参数数={len(parameter_spaces)}")

    def set_backtest_engine(self, engine):
        """设置回测引擎"""
        self.backtest_engine = engine

    def _get_mock_data_source(self):
        """
        获取mock数据源

        遵循项目mock数据使用规则:
        - 通过工厂函数获取数据源
        - 不直接在代码中写入数据
        """
        if self._data_source is None:
            try:
                from src.data_sources.factory import get_timeseries_source

                self._data_source = get_timeseries_source(source_type="mock")
                logger.info("Mock数据源初始化成功")
            except ImportError:
                logger.warning("无法导入mock数据源工厂，将使用备用方案")
                self._data_source = None

        return self._data_source

    def load_market_data(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d",
    ) -> Dict[str, Any]:
        """
        加载市场数据 (使用mock数据源)

        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            interval: 时间间隔

        Returns:
            市场数据字典 {symbol: DataFrame}
        """
        source = self._get_mock_data_source()

        if source is None:
            logger.warning("数据源不可用，返回空数据")
            return {}

        market_data = {}

        for symbol in symbols:
            try:
                df = source.get_kline_data(
                    symbol=symbol,
                    start_time=start_date,
                    end_time=end_date,
                    interval=interval,
                )
                if df is not None and not df.empty:
                    market_data[symbol] = df
                    logger.debug("加载%(symbol)s数据: {len(df)}条")
            except Exception as e:
                logger.error("加载%(symbol)s数据失败: %(e)s")

        self._market_data = market_data
        return market_data

    def _run_single_backtest(
        self, parameters: Dict[str, Any], market_data: Dict[str, Any] = None
    ) -> OptimizationResult:
        """
        运行单次回测

        Args:
            parameters: 参数组合
            market_data: 市场数据 (可选，使用缓存)

        Returns:
            优化结果
        """
        import time

        start_time = time.time()

        data = market_data or self._market_data

        if self.backtest_engine is None:
            logger.warning("回测引擎未设置，返回空结果")
            return OptimizationResult(parameters=parameters)

        try:
            # 运行回测
            backtest_result = self.backtest_engine.run(
                strategy_type=self.strategy_type,
                parameters=parameters,
                market_data=data,
            )

            # 转换结果
            result = OptimizationResult(
                parameters=copy.deepcopy(parameters),
                total_return=backtest_result.get("total_return", 0.0),
                annual_return=backtest_result.get("annual_return", 0.0),
                sharpe_ratio=backtest_result.get("sharpe_ratio", 0.0),
                max_drawdown=backtest_result.get("max_drawdown", 0.0),
                win_rate=backtest_result.get("win_rate", 0.0),
                profit_factor=backtest_result.get("profit_factor", 0.0),
                total_trades=backtest_result.get("total_trades", 0),
                winning_trades=backtest_result.get("winning_trades", 0),
                losing_trades=backtest_result.get("losing_trades", 0),
                calmar_ratio=backtest_result.get("calmar_ratio", 0.0),
                sortino_ratio=backtest_result.get("sortino_ratio", 0.0),
                optimization_time=time.time() - start_time,
            )

        except Exception as e:
            logger.error("回测执行失败: %(e)s")
            result = OptimizationResult(
                parameters=parameters,
                optimization_time=time.time() - start_time,
                metadata={"error": str(e)},
            )

        return result

    def _update_best_result(self, result: OptimizationResult):
        """更新最佳结果"""
        score = result.get_score(self.objective)

        if self.best_result is None:
            self.best_result = result
        else:
            best_score = self.best_result.get_score(self.objective)

            if self.maximize:
                if score > best_score:
                    self.best_result = result
            else:
                if score < best_score:
                    self.best_result = result

    @abstractmethod
    def optimize(self, market_data: Dict[str, Any] = None, **kwargs) -> List[OptimizationResult]:
        """
        执行参数优化

        Args:
            market_data: 市场数据
            **kwargs: 优化器特定参数

        Returns:
            所有优化结果列表
        """

    def get_top_results(self, n: int = 10) -> List[OptimizationResult]:
        """
        获取前N个最佳结果

        Args:
            n: 返回数量

        Returns:
            排序后的结果列表
        """
        sorted_results = sorted(
            self.results,
            key=lambda r: r.get_score(self.objective),
            reverse=self.maximize,
        )
        return sorted_results[:n]

    def get_optimization_summary(self) -> Dict[str, Any]:
        """
        获取优化摘要

        Returns:
            摘要字典
        """
        if not self.results:
            return {"status": "no_results"}

        scores = [r.get_score(self.objective) for r in self.results]

        return {
            "strategy_type": self.strategy_type,
            "objective": self.objective,
            "total_iterations": len(self.results),
            "best_score": max(scores) if self.maximize else min(scores),
            "worst_score": min(scores) if self.maximize else max(scores),
            "avg_score": sum(scores) / len(scores),
            "best_parameters": self.best_result.parameters if self.best_result else None,
            "total_time": sum(r.optimization_time for r in self.results),
        }

    def export_results(self, filepath: str):
        """
        导出结果到文件

        Args:
            filepath: 文件路径
        """
        import json

        export_data = {
            "summary": self.get_optimization_summary(),
            "results": [r.to_dict() for r in self.results],
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)

        logger.info("优化结果已导出: %(filepath)s")
