"""
策略参数优化演示脚本

演示如何使用三种优化方法:
1. 网格搜索 (Grid Search)
2. 随机搜索 (Random Search)
3. 遗传算法 (Genetic Algorithm)

重要: 本脚本使用mock数据源，遵循项目mock数据使用规则
"""

import sys
import os
import logging
from datetime import datetime
from typing import Dict, Any, List

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "web", "backend")
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SimplifiedBacktestEngine:
    """
    简化的回测引擎 (用于优化演示)

    使用mock数据源进行快速回测
    """

    def __init__(self, data_source=None):
        """
        初始化简化回测引擎

        Args:
            data_source: 数据源 (None则使用mock)
        """
        self.data_source = data_source
        self._market_data_cache = {}

    def _get_data_source(self):
        """
        获取数据源

        遵循项目mock数据使用规则:
        - 通过工厂函数获取数据源
        - 不直接在代码中写入数据
        """
        if self.data_source is not None:
            return self.data_source

        try:
            from src.data_sources.factory import get_timeseries_source

            self.data_source = get_timeseries_source(source_type="mock")
            logger.info("成功获取mock数据源")
        except ImportError as e:
            logger.warning(f"无法导入mock数据源工厂: {e}")
            # 使用备用方案: 生成模拟数据
            self.data_source = MockDataSourceFallback()

        return self.data_source

    def load_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d",
    ) -> List[Dict[str, Any]]:
        """
        加载市场数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            interval: 时间间隔

        Returns:
            K线数据列表
        """
        cache_key = f"{symbol}_{start_date}_{end_date}_{interval}"

        if cache_key in self._market_data_cache:
            return self._market_data_cache[cache_key]

        source = self._get_data_source()

        try:
            df = source.get_kline_data(
                symbol=symbol,
                start_time=start_date,
                end_time=end_date,
                interval=interval,
            )

            if df is None or df.empty:
                logger.warning(f"未获取到{symbol}的数据")
                return []

            # 转换为字典列表
            data = []
            for idx, row in df.iterrows():
                data.append(
                    {
                        "date": idx
                        if isinstance(idx, datetime)
                        else datetime.strptime(str(idx), "%Y-%m-%d"),
                        "open": float(row.get("open", 0)),
                        "high": float(row.get("high", 0)),
                        "low": float(row.get("low", 0)),
                        "close": float(row.get("close", 0)),
                        "volume": int(row.get("volume", 0)),
                    }
                )

            self._market_data_cache[cache_key] = data
            return data

        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            return []

    def run(
        self,
        strategy_type: str,
        parameters: Dict[str, Any],
        market_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        执行回测

        Args:
            strategy_type: 策略类型
            parameters: 策略参数
            market_data: 市场数据 {symbol: data_list}

        Returns:
            回测结果
        """
        from app.backtest.strategies.factory import StrategyFactory

        try:
            # 创建策略实例
            strategy = StrategyFactory.create_strategy(strategy_type, parameters)
        except Exception as e:
            logger.warning(f"创建策略失败: {e}")
            return self._empty_result()

        # 执行简化回测
        initial_capital = 1000000
        capital = initial_capital
        position = 0
        entry_price = 0
        trades = []

        # 遍历所有数据
        for symbol, data_list in market_data.items():
            if not data_list:
                continue

            for i, bar in enumerate(data_list):
                if i < 30:  # 需要足够的历史数据
                    continue

                # 准备当前数据
                current_data = {
                    "open": bar["open"],
                    "high": bar["high"],
                    "low": bar["low"],
                    "close": bar["close"],
                    "volume": bar["volume"],
                }

                # 生成信号
                position_info = {"quantity": position} if position > 0 else None
                signal = strategy.generate_signal(symbol, current_data, position_info)

                current_price = bar["close"]

                if signal:
                    from app.backtest.strategies.base import SignalType

                    if signal.signal_type == SignalType.LONG and position == 0:
                        # 买入
                        position = int(capital * 0.95 / current_price)
                        entry_price = current_price
                        capital -= position * current_price
                        trades.append(
                            {
                                "action": "BUY",
                                "price": current_price,
                                "quantity": position,
                            }
                        )

                    elif signal.signal_type == SignalType.EXIT and position > 0:
                        # 卖出
                        capital += position * current_price
                        profit = (current_price - entry_price) * position
                        trades.append(
                            {
                                "action": "SELL",
                                "price": current_price,
                                "quantity": position,
                                "profit": profit,
                            }
                        )
                        position = 0

        # 计算最终价值
        if position > 0 and data_list:
            final_price = data_list[-1]["close"]
            capital += position * final_price

        # 计算指标
        total_return = (capital - initial_capital) / initial_capital
        winning_trades = sum(1 for t in trades if t.get("profit", 0) > 0)
        losing_trades = sum(1 for t in trades if t.get("profit", 0) < 0)
        total_trades = len([t for t in trades if t["action"] == "SELL"])

        # 计算最大回撤 (简化)
        max_drawdown = abs(min(0, total_return))

        # 计算夏普比率 (简化估计)
        if total_trades > 0:
            sharpe_ratio = total_return * 2.5  # 简化计算
        else:
            sharpe_ratio = 0

        return {
            "total_return": total_return,
            "annual_return": total_return * 2.5,  # 假设测试期约5个月
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "win_rate": winning_trades / total_trades if total_trades > 0 else 0,
            "profit_factor": 1.5 if winning_trades > losing_trades else 0.8,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "calmar_ratio": total_return / max_drawdown if max_drawdown > 0 else 0,
            "sortino_ratio": sharpe_ratio * 0.9,
        }

    def _empty_result(self):
        """返回空结果"""
        return {
            "total_return": 0,
            "annual_return": 0,
            "sharpe_ratio": 0,
            "max_drawdown": 0,
            "win_rate": 0,
            "profit_factor": 0,
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "calmar_ratio": 0,
            "sortino_ratio": 0,
        }


class MockDataSourceFallback:
    """
    Mock数据源备用方案

    当无法导入真实mock数据源时使用
    """

    def __init__(self, random_seed: int = 42):
        import random

        self.rng = random.Random(random_seed)

    def get_kline_data(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        interval: str = "1d",
    ):
        """生成模拟K线数据"""
        import pandas as pd

        # 生成日期序列
        dates = pd.date_range(start=start_time, end=end_time, freq="D")
        dates = [d for d in dates if d.weekday() < 5]  # 排除周末

        # 生成价格数据
        base_price = 10 + self.rng.random() * 40  # 10-50元
        data = []

        for i, date in enumerate(dates):
            # 随机波动
            change = (self.rng.random() - 0.48) * 0.03  # 略有上涨偏向
            base_price *= 1 + change

            high = base_price * (1 + self.rng.random() * 0.02)
            low = base_price * (1 - self.rng.random() * 0.02)
            open_price = low + self.rng.random() * (high - low)
            close = low + self.rng.random() * (high - low)
            volume = int(1000000 + self.rng.random() * 5000000)

            data.append(
                {
                    "open": round(open_price, 2),
                    "high": round(high, 2),
                    "low": round(low, 2),
                    "close": round(close, 2),
                    "volume": volume,
                }
            )

        return pd.DataFrame(data, index=dates)


def demo_grid_search():
    """演示网格搜索优化"""
    print("\n" + "=" * 60)
    print("网格搜索优化演示")
    print("=" * 60)

    from app.backtest.optimization.grid_search import GridSearchOptimizer
    from app.backtest.optimization.base import ParameterSpace

    # 定义参数空间 (简化版，减少组合数)
    parameter_spaces = [
        ParameterSpace(
            name="short_period",
            param_type="int",
            min_value=5,
            max_value=15,
            step=5,  # 5, 10, 15
        ),
        ParameterSpace(
            name="long_period",
            param_type="int",
            min_value=20,
            max_value=30,
            step=5,  # 20, 25, 30
        ),
    ]

    # 创建优化器
    optimizer = GridSearchOptimizer(
        strategy_type="dual_ma",
        parameter_spaces=parameter_spaces,
        objective="sharpe_ratio",
        maximize=True,
    )

    # 创建回测引擎
    engine = SimplifiedBacktestEngine()
    optimizer.set_backtest_engine(engine)

    # 加载数据
    start_date = datetime(2025, 6, 1)
    end_date = datetime(2025, 10, 31)

    market_data = {}
    for symbol in ["600000", "600519"]:
        data = engine.load_data(symbol, start_date, end_date)
        if data:
            market_data[symbol] = data

    if not market_data:
        print("警告: 无法加载市场数据，使用备用数据源")
        engine.data_source = MockDataSourceFallback(random_seed=42)
        for symbol in ["600000", "600519"]:
            data = engine.load_data(symbol, start_date, end_date)
            if data:
                market_data[symbol] = data

    # 执行优化
    print(f"参数组合数: {optimizer._grid_size}")
    results = optimizer.optimize(market_data=market_data)

    # 输出结果
    print(f"\n测试组合数: {len(results)}")
    print(f"最佳夏普比率: {optimizer.best_result.get_score('sharpe_ratio'):.4f}")
    print(f"最佳参数: {optimizer.best_result.parameters}")

    # 参数敏感性
    sensitivity = optimizer.get_parameter_sensitivity()
    print("\n参数敏感性分析:")
    for param, values in sensitivity.items():
        print(f"  {param}: {values}")

    return optimizer


def demo_random_search():
    """演示随机搜索优化"""
    print("\n" + "=" * 60)
    print("随机搜索优化演示")
    print("=" * 60)

    from app.backtest.optimization.random_search import RandomSearchOptimizer
    from app.backtest.optimization.base import ParameterSpace

    # 定义参数空间
    parameter_spaces = [
        ParameterSpace(
            name="short_period", param_type="int", min_value=5, max_value=20
        ),
        ParameterSpace(
            name="long_period", param_type="int", min_value=20, max_value=60
        ),
        ParameterSpace(
            name="stop_loss_pct", param_type="float", min_value=0.03, max_value=0.10
        ),
    ]

    # 创建优化器
    optimizer = RandomSearchOptimizer(
        strategy_type="dual_ma",
        parameter_spaces=parameter_spaces,
        objective="sharpe_ratio",
        maximize=True,
        n_iterations=20,
        random_seed=42,  # 可复现
    )

    # 创建回测引擎
    engine = SimplifiedBacktestEngine()
    engine.data_source = MockDataSourceFallback(random_seed=42)
    optimizer.set_backtest_engine(engine)

    # 加载数据
    start_date = datetime(2025, 6, 1)
    end_date = datetime(2025, 10, 31)

    market_data = {}
    for symbol in ["600000", "600519"]:
        data = engine.load_data(symbol, start_date, end_date)
        if data:
            market_data[symbol] = data

    # 执行优化
    print(f"计划迭代数: {optimizer.n_iterations}")
    results = optimizer.optimize(market_data=market_data, patience=10)

    # 输出结果
    print(f"\n实际测试组合数: {len(results)}")
    print(f"最佳夏普比率: {optimizer.best_result.get_score('sharpe_ratio'):.4f}")
    print(f"最佳参数: {optimizer.best_result.parameters}")

    # 收敛曲线
    curve = optimizer.get_convergence_curve()
    print(f"\n收敛曲线 (前5个): {curve[:5]}")
    print(f"收敛曲线 (后5个): {curve[-5:]}")

    # 探索统计
    stats = optimizer.get_exploration_stats()
    print(f"\n探索统计: {stats}")

    return optimizer


def demo_genetic_algorithm():
    """演示遗传算法优化"""
    print("\n" + "=" * 60)
    print("遗传算法优化演示")
    print("=" * 60)

    from app.backtest.optimization.genetic import GeneticOptimizer
    from app.backtest.optimization.base import ParameterSpace

    # 定义参数空间
    parameter_spaces = [
        ParameterSpace(
            name="short_period", param_type="int", min_value=5, max_value=20
        ),
        ParameterSpace(
            name="long_period", param_type="int", min_value=20, max_value=60
        ),
        ParameterSpace(
            name="signal_threshold", param_type="float", min_value=0.01, max_value=0.05
        ),
    ]

    # 创建优化器
    optimizer = GeneticOptimizer(
        strategy_type="dual_ma",
        parameter_spaces=parameter_spaces,
        objective="sharpe_ratio",
        maximize=True,
        population_size=10,
        n_generations=5,
        crossover_rate=0.8,
        mutation_rate=0.1,
        random_seed=42,
    )

    # 创建回测引擎
    engine = SimplifiedBacktestEngine()
    engine.data_source = MockDataSourceFallback(random_seed=42)
    optimizer.set_backtest_engine(engine)

    # 加载数据
    start_date = datetime(2025, 6, 1)
    end_date = datetime(2025, 10, 31)

    market_data = {}
    for symbol in ["600000", "600519"]:
        data = engine.load_data(symbol, start_date, end_date)
        if data:
            market_data[symbol] = data

    # 执行优化
    print(f"种群大小: {optimizer.population_size}")
    print(f"进化代数: {optimizer.n_generations}")
    results = optimizer.optimize(market_data=market_data, patience=3)

    # 输出结果
    print(f"\n总评估组合数: {len(results)}")
    print(f"最佳夏普比率: {optimizer.best_result.get_score('sharpe_ratio'):.4f}")
    print(f"最佳参数: {optimizer.best_result.parameters}")

    # 进化曲线
    evolution = optimizer.get_evolution_curve()
    print("\n进化曲线:")
    for gen, best, avg in zip(
        evolution["generations"], evolution["best"], evolution["avg"]
    ):
        print(f"  第{gen}代: 最佳={best:.4f}, 平均={avg:.4f}")

    return optimizer


def compare_optimizers():
    """比较三种优化方法"""
    print("\n" + "=" * 60)
    print("优化方法比较")
    print("=" * 60)

    results = {}

    # 网格搜索
    try:
        grid_opt = demo_grid_search()
        results["grid_search"] = {
            "best_score": grid_opt.best_result.get_score("sharpe_ratio"),
            "iterations": len(grid_opt.results),
            "best_params": grid_opt.best_result.parameters,
        }
    except Exception as e:
        print(f"网格搜索失败: {e}")
        results["grid_search"] = {"error": str(e)}

    # 随机搜索
    try:
        random_opt = demo_random_search()
        results["random_search"] = {
            "best_score": random_opt.best_result.get_score("sharpe_ratio"),
            "iterations": len(random_opt.results),
            "best_params": random_opt.best_result.parameters,
        }
    except Exception as e:
        print(f"随机搜索失败: {e}")
        results["random_search"] = {"error": str(e)}

    # 遗传算法
    try:
        genetic_opt = demo_genetic_algorithm()
        results["genetic"] = {
            "best_score": genetic_opt.best_result.get_score("sharpe_ratio"),
            "iterations": len(genetic_opt.results),
            "best_params": genetic_opt.best_result.parameters,
        }
    except Exception as e:
        print(f"遗传算法失败: {e}")
        results["genetic"] = {"error": str(e)}

    # 输出比较结果
    print("\n" + "=" * 60)
    print("比较结果汇总")
    print("=" * 60)

    for method, data in results.items():
        print(f"\n{method}:")
        if "error" in data:
            print(f"  错误: {data['error']}")
        else:
            print(f"  最佳得分: {data['best_score']:.4f}")
            print(f"  评估次数: {data['iterations']}")
            print(f"  最佳参数: {data['best_params']}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="策略参数优化演示")
    parser.add_argument(
        "--method",
        choices=["grid", "random", "genetic", "all"],
        default="all",
        help="优化方法",
    )

    args = parser.parse_args()

    if args.method == "grid":
        demo_grid_search()
    elif args.method == "random":
        demo_random_search()
    elif args.method == "genetic":
        demo_genetic_algorithm()
    else:
        compare_optimizers()
