"""
Random Search Optimizer

随机搜索优化器 - 随机采样参数组合
"""

import logging
import random
import time
from typing import Any, Dict, List, Optional

from app.backtest.optimization.base import (
    BaseOptimizer,
    OptimizationResult,
    ParameterSpace,
)

logger = logging.getLogger(__name__)


class RandomSearchOptimizer(BaseOptimizer):
    """
    随机搜索优化器

    特点:
    - 随机采样参数空间
    - 比网格搜索更高效
    - 不保证全局最优，但概率上能找到好解
    - 适合高维参数空间
    - 支持设置随机种子保证可复现
    """

    def __init__(
        self,
        strategy_type: str,
        parameter_spaces: List[ParameterSpace],
        objective: str = "sharpe_ratio",
        maximize: bool = True,
        n_iterations: int = 100,
        random_seed: Optional[int] = None,
    ):
        """
        初始化随机搜索优化器

        Args:
            strategy_type: 策略类型
            parameter_spaces: 参数空间列表
            objective: 优化目标
            maximize: 是否最大化
            n_iterations: 迭代次数
            random_seed: 随机种子 (用于复现)
        """
        super().__init__(strategy_type, parameter_spaces, objective, maximize)

        self.n_iterations = n_iterations
        self.random_seed = random_seed

        # 初始化随机数生成器
        self.rng = random.Random(random_seed)

        logger.info("随机搜索优化器初始化: 迭代数=%(n_iterations)s, 种子=%(random_seed)s"")

    def _generate_random_parameters(self) -> Dict[str, Any]:
        """
        生成随机参数组合

        Returns:
            参数字典
        """
        params = {}

        for space in self.parameter_spaces:
            params[space.name] = space.get_random_value(self.rng)

        return params

    def _generate_unique_parameters(
        self, existing: List[Dict[str, Any]], max_attempts: int = 100
    ) -> Optional[Dict[str, Any]]:
        """
        生成唯一的参数组合 (避免重复)

        Args:
            existing: 已有的参数组合
            max_attempts: 最大尝试次数

        Returns:
            新的参数组合，如果无法生成则返回None
        """
        for _ in range(max_attempts):
            params = self._generate_random_parameters()

            # 检查是否与现有组合重复
            is_duplicate = False
            for exist_params in existing:
                if params == exist_params:
                    is_duplicate = True
                    break

            if not is_duplicate:
                return params

        return None

    def optimize(
        self,
        market_data: Dict[str, Any] = None,
        progress_callback: Optional[callable] = None,
        early_stop: bool = True,
        patience: int = 20,
        min_improvement: float = 0.001,
        **kwargs,
    ) -> List[OptimizationResult]:
        """
        执行随机搜索优化

        Args:
            market_data: 市场数据
            progress_callback: 进度回调
            early_stop: 是否启用早停
            patience: 早停耐心值 (连续多少次无改进后停止)
            min_improvement: 最小改进阈值

        Returns:
            所有优化结果
        """
        logger.info("开始随机搜索优化: 策略={self.strategy_type}, 迭代={self.n_iterations}"")

        start_time = time.time()

        data = market_data or self._market_data

        if data is None:
            logger.warning("无市场数据，优化中止")
            return []

        self.results = []
        self.best_result = None
        tested_params = []

        no_improvement_count = 0
        prev_best_score = None

        for iteration in range(self.n_iterations):
            # 生成唯一参数组合
            params = self._generate_unique_parameters(tested_params)

            if params is None:
                logger.info("参数空间已穷尽")
                break

            tested_params.append(params)

            # 运行回测
            result = self._run_single_backtest(params, data)
            self.results.append(result)

            # 更新最佳结果
            self._update_best_result(result)

            # 进度回调
            if progress_callback:
                progress_callback(iteration + 1, self.n_iterations, result)

            # 日志
            current_score = result.get_score(self.objective)
            best_score = self.best_result.get_score(self.objective) if self.best_result else 0

            if (iteration + 1) % 10 == 0 or iteration == 0:
                logger.info(
                    f"随机搜索进度: {iteration + 1}/{self.n_iterations} "
                    f"当前{self.objective}={current_score:.4f} "
                    f"最佳={best_score:.4f}"
                )

            # 早停检查
            if early_stop:
                if prev_best_score is not None:
                    improvement = abs(best_score - prev_best_score)
                    if improvement < min_improvement:
                        no_improvement_count += 1
                    else:
                        no_improvement_count = 0

                    if no_improvement_count >= patience:
                        logger.info("早停触发: 连续{patience}次无显著改进 " f"(阈值={min_improvement})")
                        break

                prev_best_score = best_score

        total_time = time.time() - start_time

        logger.info(
            f"随机搜索完成: "
            f"耗时={total_time:.2f}秒 "
            f"测试={len(self.results)}组合 "
            f"最佳{self.objective}={self.best_result.get_score(self.objective):.4f}"
        )

        return self.results

    def optimize_with_restarts(
        self,
        market_data: Dict[str, Any] = None,
        n_restarts: int = 3,
        iterations_per_restart: int = None,
        **kwargs,
    ) -> List[OptimizationResult]:
        """
        带重启的随机搜索

        多次重启，每次从不同的随机种子开始

        Args:
            market_data: 市场数据
            n_restarts: 重启次数
            iterations_per_restart: 每次重启的迭代数

        Returns:
            所有优化结果
        """
        iters = iterations_per_restart or (self.n_iterations // n_restarts)

        all_results = []
        best_overall = None

        for restart in range(n_restarts):
            # 更新随机种子
            if self.random_seed is not None:
                new_seed = self.random_seed + restart * 1000
            else:
                new_seed = None

            self.rng = random.Random(new_seed)

            logger.info("随机搜索重启 {restart + 1}/%(n_restarts)s, 种子=%(new_seed)s"")

            # 临时修改迭代次数
            original_iters = self.n_iterations
            self.n_iterations = iters

            # 执行优化
            results = self.optimize(market_data, **kwargs)
            all_results.extend(results)

            # 更新全局最佳
            if self.best_result:
                if best_overall is None:
                    best_overall = self.best_result
                else:
                    score = self.best_result.get_score(self.objective)
                    best_score = best_overall.get_score(self.objective)
                    if (self.maximize and score > best_score) or (not self.maximize and score < best_score):
                        best_overall = self.best_result

            # 恢复迭代次数
            self.n_iterations = original_iters

        # 更新最终结果
        self.results = all_results
        self.best_result = best_overall

        logger.info(
            f"多重启随机搜索完成: "
            f"重启={n_restarts}次 "
            f"总测试={len(all_results)}组合 "
            f"最佳{self.objective}={best_overall.get_score(self.objective):.4f}"
        )

        return all_results

    def get_convergence_curve(self) -> List[float]:
        """
        获取收敛曲线 (最佳得分随迭代的变化)

        Returns:
            最佳得分列表
        """
        if not self.results:
            return []

        curve = []
        best_score = None

        for result in self.results:
            score = result.get_score(self.objective)

            if best_score is None:
                best_score = score
            elif self.maximize:
                best_score = max(best_score, score)
            else:
                best_score = min(best_score, score)

            curve.append(best_score)

        return curve

    def get_exploration_stats(self) -> Dict[str, Any]:
        """
        获取探索统计

        Returns:
            探索统计信息
        """
        if not self.results:
            return {}

        scores = [r.get_score(self.objective) for r in self.results]

        return {
            "total_explored": len(self.results),
            "unique_combinations": len(self.results),  # 随机搜索都是唯一的
            "score_mean": sum(scores) / len(scores),
            "score_std": (sum((s - sum(scores) / len(scores)) ** 2 for s in scores) / len(scores)) ** 0.5,
            "score_min": min(scores),
            "score_max": max(scores),
            "convergence_iteration": self._find_convergence_point(),
            "random_seed": self.random_seed,
        }

    def _find_convergence_point(self, threshold: float = 0.01) -> int:
        """
        找到收敛点 (最佳得分稳定的迭代次数)

        Args:
            threshold: 改进阈值

        Returns:
            收敛迭代次数
        """
        curve = self.get_convergence_curve()

        if len(curve) < 2:
            return len(curve)

        final_best = curve[-1]

        for i, score in enumerate(curve):
            if abs(final_best - score) < threshold * abs(final_best):
                return i + 1

        return len(curve)
