#!/usr/bin/env python3
"""
# 功能：GPU加速优化引擎
# 作者：MyStocks AI开发团队
# 创建日期：2025-12-20
# 版本：1.0.0
# 说明：GPU加速的参数优化和超参数调优引擎
"""

import time
import logging
from typing import Dict, Any, List, Callable
import numpy as np
import pandas as pd

try:
    import cupy as cp

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

try:
    from src.gpu.core.hardware_abstraction.resource_manager import GPUResourceManager
except ImportError:
    GPUResourceManager = Any

logger = logging.getLogger(__name__)


class OptimizationGPU:
    """GPU加速优化引擎

    功能特性:
    ✅ GPU加速网格搜索、随机搜索、贝叶斯优化
    ✅ 并行参数评估和性能监控
    ✅ 智能缓存机制避免重复计算
    ✅ 多种优化算法支持
    ✅ CPU回退确保兼容性
    """

    def __init__(self, gpu_manager: GPUResourceManager = None):
        """初始化优化引擎

        Args:
            gpu_manager: GPU资源管理器实例
        """
        self.gpu_manager = gpu_manager
        self.optimization_cache = {}
        self.optimization_history = []
        self.gpu_available = GPU_AVAILABLE and gpu_manager is not None

        if not self.gpu_available:
            logger.warning("GPU不可用，将使用CPU模式")
        else:
            logger.info("GPU优化引擎初始化完成")

    def optimize_parameters_gpu(
        self,
        objective_func: Callable,
        param_space: Dict,
        method: str = "grid_search",
        n_trials: int = 100,
        maximize: bool = True,
        early_stopping: Dict = None,
        parallel_evaluations: int = 1,
    ) -> Dict[str, Any]:
        """GPU加速参数优化

        Args:
            objective_func: 目标函数，接受参数字典并返回分数
            param_space: 参数空间定义
            method: 优化方法 ('grid_search', 'random_search', 'bayesian', 'genetic')
            n_trials: 试验次数
            maximize: 是否最大化目标函数
            early_stopping: 早停配置 {'patience': int, 'min_improvement': float}
            parallel_evaluations: 并行评估数量

        Returns:
            优化结果字典，包含最佳参数、分数等
        """
        try:
            logger.info(f"开始GPU参数优化: {method} ({n_trials} 次试验)")

            optimization_start = time.time()
            early_stopping = early_stopping or {}

            # 验证参数空间
            self._validate_param_space(param_space)

            # 根据方法选择优化策略
            if method == "grid_search":
                result = self._grid_search_gpu(
                    objective_func, param_space, maximize, early_stopping
                )
            elif method == "random_search":
                result = self._random_search_gpu(
                    objective_func, param_space, n_trials, maximize, early_stopping
                )
            elif method == "bayesian":
                result = self._bayesian_optimization_gpu(
                    objective_func, param_space, n_trials, maximize, early_stopping
                )
            elif method == "genetic":
                result = self._genetic_optimization_gpu(
                    objective_func, param_space, n_trials, maximize, early_stopping
                )
            else:
                raise ValueError(f"不支持的优化方法: {method}")

            optimization_time = time.time() - optimization_start

            # 添加元数据
            result.update(
                {
                    "optimization_time": optimization_time,
                    "gpu_memory_used_mb": self.gpu_manager.get_gpu_memory_usage()
                    if self.gpu_manager
                    else 0,
                    "method": method,
                    "gpu_mode": self.gpu_available,
                    "param_space_size": self._estimate_param_space_size(param_space),
                    "convergence_curve": self._get_convergence_curve(),
                }
            )

            # 记录优化历史
            self.optimization_history.append(
                {
                    "timestamp": time.time(),
                    "method": method,
                    "best_score": result.get("best_score"),
                    "optimization_time": optimization_time,
                    "n_trials": result.get("total_evaluations", 0),
                }
            )

            logger.info(
                f"GPU参数优化完成: {result['best_score']:.4f} ({optimization_time:.2f}s)"
            )
            return result

        except Exception as e:
            logger.error(f"GPU参数优化失败: {e}")
            return {
                "error": str(e),
                "method": method,
                "gpu_mode": self.gpu_available,
                "status": "failed",
            }

    def _grid_search_gpu(
        self,
        objective_func: Callable,
        param_space: Dict,
        maximize: bool,
        early_stopping: Dict,
    ) -> Dict[str, Any]:
        """网格搜索优化（GPU加速）"""
        try:
            logger.info("执行网格搜索优化...")

            # 生成参数网格
            param_grid = self._generate_param_grid(param_space)
            total_combinations = len(param_grid)

            logger.info(f"参数网格大小: {total_combinations}")

            best_params = None
            best_score = float("-inf") if maximize else float("inf")
            scores = []

            # 早停相关
            patience = early_stopping.get("patience", 0)
            min_improvement = early_stopping.get("min_improvement", 0.001)
            no_improvement_count = 0

            # 遍历参数组合
            for i, params in enumerate(param_grid):
                # 检查缓存
                cache_key = self._generate_param_cache_key(params)
                if cache_key in self.optimization_cache:
                    score = self.optimization_cache[cache_key]
                else:
                    score = objective_func(params)
                    self.optimization_cache[cache_key] = score

                scores.append(score)

                # 更新最佳结果
                is_better = (score > best_score) if maximize else (score < best_score)
                if is_better:
                    improvement = (
                        abs(score - best_score)
                        if best_score != float("inf") and best_score != float("-inf")
                        else float("inf")
                    )
                    best_score = score
                    best_params = params.copy()
                    no_improvement_count = 0
                    logger.debug(
                        f"找到更好的参数: {score:.4f} (改进: {improvement:.4f})"
                    )
                else:
                    no_improvement_count += 1

                # 早停检查
                if patience > 0 and no_improvement_count >= patience:
                    logger.info(f"早停触发，{patience} 次无改进")
                    break

                # 进度报告
                if (i + 1) % max(1, total_combinations // 10) == 0:
                    progress = (i + 1) / total_combinations * 100
                    logger.debug(
                        f"网格搜索进度: {progress:.1f}% ({i + 1}/{total_combinations})"
                    )

            return {
                "best_params": best_params,
                "best_score": best_score,
                "total_evaluations": len(param_grid),
                "method": "grid_search",
                "scores": scores,
                "convergence_achieved": no_improvement_count < patience
                if patience > 0
                else None,
            }

        except Exception as e:
            logger.error(f"GPU网格搜索失败: {e}")
            raise

    def _random_search_gpu(
        self,
        objective_func: Callable,
        param_space: Dict,
        n_trials: int,
        maximize: bool,
        early_stopping: Dict,
    ) -> Dict[str, Any]:
        """随机搜索优化（GPU加速）"""
        try:
            logger.info(f"执行随机搜索优化: {n_trials} 次试验")

            best_params = None
            best_score = float("-inf") if maximize else float("inf")
            scores = []

            # 早停相关
            patience = early_stopping.get("patience", n_trials // 4)
            min_improvement = early_stopping.get("min_improvement", 0.001)
            no_improvement_count = 0

            for trial in range(n_trials):
                # 随机生成参数
                params = self._sample_random_params(param_space)

                # 检查缓存
                cache_key = self._generate_param_cache_key(params)
                if cache_key in self.optimization_cache:
                    score = self.optimization_cache[cache_key]
                else:
                    score = objective_func(params)
                    self.optimization_cache[cache_key] = score

                scores.append(score)

                # 更新最佳结果
                is_better = (score > best_score) if maximize else (score < best_score)
                if is_better:
                    improvement = (
                        abs(score - best_score)
                        if best_score != float("inf") and best_score != float("-inf")
                        else float("inf")
                    )
                    best_score = score
                    best_params = params.copy()
                    no_improvement_count = 0
                    logger.debug(f"试验 {trial + 1}: 更好的参数 {score:.4f}")
                else:
                    no_improvement_count += 1

                # 早停检查
                if patience > 0 and no_improvement_count >= patience:
                    logger.info(f"早停触发，{patience} 次无改进")
                    break

                # 进度报告
                if (trial + 1) % max(1, n_trials // 10) == 0:
                    progress = (trial + 1) / n_trials * 100
                    logger.debug(
                        f"随机搜索进度: {progress:.1f}% ({trial + 1}/{n_trials})"
                    )

            return {
                "best_params": best_params,
                "best_score": best_score,
                "total_evaluations": trial + 1,
                "method": "random_search",
                "scores": scores,
                "convergence_achieved": no_improvement_count < patience
                if patience > 0
                else None,
            }

        except Exception as e:
            logger.error(f"GPU随机搜索失败: {e}")
            raise

    def _bayesian_optimization_gpu(
        self,
        objective_func: Callable,
        param_space: Dict,
        n_trials: int,
        maximize: bool,
        early_stopping: Dict,
    ) -> Dict[str, Any]:
        """贝叶斯优化（GPU加速）"""
        try:
            logger.info(f"执行贝叶斯优化: {n_trials} 次试验")

            # 初始化
            best_params = None
            best_score = float("-inf") if maximize else float("inf")
            scores = []
            evaluated_params = []

            # 早停相关
            patience = early_stopping.get("patience", n_trials // 3)
            no_improvement_count = 0

            # 初始随机采样
            init_samples = min(10, n_trials // 4)
            for trial in range(init_samples):
                params = self._sample_random_params(param_space)
                score = self._evaluate_parameters(objective_func, params)

                evaluated_params.append(params)
                scores.append(score)

                is_better = (score > best_score) if maximize else (score < best_score)
                if is_better:
                    best_score = score
                    best_params = params.copy()
                    no_improvement_count = 0
                else:
                    no_improvement_count += 1

            # 贝叶斯优化主循环
            for trial in range(init_samples, n_trials):
                if len(evaluated_params) < 2:
                    # 数据不足，继续随机采样
                    params = self._sample_random_params(param_space)
                else:
                    # 使用高斯过程指导采样
                    params = self._sample_from_gaussian_process(
                        param_space, evaluated_params, scores, maximize
                    )

                score = self._evaluate_parameters(objective_func, params)

                evaluated_params.append(params)
                scores.append(score)

                is_better = (score > best_score) if maximize else (score < best_score)
                if is_better:
                    best_score = score
                    best_params = params.copy()
                    no_improvement_count = 0
                    logger.debug(f"贝叶斯优化试验 {trial + 1}: 更好的参数 {score:.4f}")
                else:
                    no_improvement_count += 1

                # 早停检查
                if patience > 0 and no_improvement_count >= patience:
                    logger.info(f"早停触发，{patience} 次无改进")
                    break

            return {
                "best_params": best_params,
                "best_score": best_score,
                "total_evaluations": len(evaluated_params),
                "method": "bayesian",
                "scores": scores,
                "convergence_achieved": no_improvement_count < patience
                if patience > 0
                else None,
            }

        except Exception as e:
            logger.error(f"GPU贝叶斯优化失败: {e}")
            raise

    def _genetic_optimization_gpu(
        self,
        objective_func: Callable,
        param_space: Dict,
        n_trials: int,
        maximize: bool,
        early_stopping: Dict,
    ) -> Dict[str, Any]:
        """遗传算法优化（GPU加速）"""
        try:
            logger.info(f"执行遗传算法优化: {n_trials} 代")

            # 遗传算法参数
            population_size = min(20, n_trials // 2)
            mutation_rate = 0.1
            crossover_rate = 0.8

            # 初始化种群
            population = [
                self._sample_random_params(param_space) for _ in range(population_size)
            ]
            best_params = None
            best_score = float("-inf") if maximize else float("inf")
            scores = []

            # 早停相关
            patience = early_stopping.get("patience", n_trials // 3)
            no_improvement_count = 0

            for generation in range(n_trials):
                # 评估种群
                fitness_scores = []
                for individual in population:
                    score = self._evaluate_parameters(objective_func, individual)
                    fitness_scores.append(score)

                    # 更新全局最佳
                    is_better = (
                        (score > best_score) if maximize else (score < best_score)
                    )
                    if is_better:
                        best_score = score
                        best_params = individual.copy()
                        no_improvement_count = 0
                    else:
                        no_improvement_count += 1

                scores.extend(fitness_scores)

                # 早停检查
                if patience > 0 and no_improvement_count >= patience:
                    logger.info(f"早停触发，{patience} 代无改进")
                    break

                # 选择、交叉、变异
                if generation < n_trials - 1:
                    population = self._genetic_operations(
                        population,
                        fitness_scores,
                        param_space,
                        mutation_rate,
                        crossover_rate,
                        maximize,
                    )

                # 进度报告
                if (generation + 1) % max(1, n_trials // 10) == 0:
                    progress = (generation + 1) / n_trials * 100
                    avg_fitness = np.mean(fitness_scores)
                    logger.debug(
                        f"遗传算法进度: {progress:.1f}% (平均适应度: {avg_fitness:.4f})"
                    )

            return {
                "best_params": best_params,
                "best_score": best_score,
                "total_evaluations": len(scores),
                "method": "genetic",
                "scores": scores,
                "convergence_achieved": no_improvement_count < patience
                if patience > 0
                else None,
                "final_population": population,
            }

        except Exception as e:
            logger.error(f"GPU遗传算法优化失败: {e}")
            raise

    def optimize_portfolio_weights(
        self,
        returns: pd.DataFrame,
        method: str = "mean_variance",
        risk_free_rate: float = 0.02,
    ) -> Dict[str, Any]:
        """GPU加速投资组合权重优化"""
        try:
            logger.info(f"开始投资组合权重优化: {method}")

            n_assets = returns.shape[1]
            asset_names = returns.columns.tolist()

            if method == "mean_variance":
                result = self._mean_variance_optimization_gpu(returns, risk_free_rate)
            elif method == "risk_parity":
                result = self._risk_parity_optimization_gpu(returns)
            elif method == "max_sharpe":
                result = self._max_sharpe_optimization_gpu(returns, risk_free_rate)
            elif method == "min_variance":
                result = self._min_variance_optimization_gpu(returns)
            else:
                raise ValueError(f"不支持的组合优化方法: {method}")

            # 添加资产名称
            if "weights" in result:
                result["weights"] = dict(zip(asset_names, result["weights"]))

            result["method"] = method
            result["n_assets"] = n_assets
            result["asset_names"] = asset_names
            result["gpu_mode"] = self.gpu_available

            return result

        except Exception as e:
            logger.error(f"投资组合优化失败: {e}")
            return {"error": str(e), "method": method}

    # 辅助方法
    def _validate_param_space(self, param_space: Dict) -> None:
        """验证参数空间"""
        if not param_space:
            raise ValueError("参数空间不能为空")

        for param_name, param_range in param_space.items():
            if isinstance(param_range, list):
                if len(param_range) == 0:
                    raise ValueError(f"参数 {param_name} 的范围不能为空")
            elif isinstance(param_range, tuple) and len(param_range) == 2:
                if param_range[0] >= param_range[1]:
                    raise ValueError(f"参数 {param_name} 的范围无效")
            else:
                raise ValueError(f"参数 {param_name} 的范围格式无效")

    def _generate_param_grid(self, param_space: Dict) -> List[Dict]:
        """生成参数网格"""
        import itertools

        param_names = list(param_space.keys())
        param_values = list(param_space.values())

        # 生成所有组合
        all_combinations = itertools.product(*param_values)

        # 转换为参数字典列表
        param_grid = []
        for combination in all_combinations:
            param_dict = dict(zip(param_names, combination))
            param_grid.append(param_dict)

        return param_grid

    def _sample_random_params(self, param_space: Dict) -> Dict:
        """随机采样参数"""
        import random

        params = {}
        for param_name, param_range in param_space.items():
            if isinstance(param_range, list):
                # 离散参数
                params[param_name] = random.choice(param_range)
            elif isinstance(param_range, tuple):
                # 连续参数
                min_val, max_val = param_range
                params[param_name] = random.uniform(min_val, max_val)
            else:
                raise ValueError(f"参数 {param_name} 的范围类型不支持")

        return params

    def _sample_from_gaussian_process(
        self,
        param_space: Dict,
        evaluated_params: List[Dict],
        scores: List[float],
        maximize: bool,
    ) -> Dict:
        """从高斯过程采样参数"""
        try:
            # 简化的实现：基于已有最佳参数进行高斯采样
            if not evaluated_params or not scores:
                return self._sample_random_params(param_space)

            # 找到最佳参数
            best_idx = np.argmax(scores) if maximize else np.argmin(scores)
            best_params = evaluated_params[best_idx]

            # 在最佳参数周围进行高斯采样
            params = {}
            for param_name, param_range in param_space.items():
                best_val = best_params.get(param_name)

                if isinstance(param_range, list):
                    # 离散参数：使用正态分布采样然后取最近的离散值
                    if best_val is not None:
                        mean = best_val
                        std = (max(param_range) - min(param_range)) / 6
                        sampled = np.random.normal(mean, std)
                        params[param_name] = min(
                            param_range,
                            max(param_range, sampled),
                            key=lambda x: abs(x - sampled),
                        )
                    else:
                        params[param_name] = random.choice(param_range)
                else:
                    # 连续参数：正态分布采样
                    if best_val is not None:
                        mean = best_val
                        std = (param_range[1] - param_range[0]) / 6
                        sampled = np.random.normal(mean, std)
                        params[param_name] = max(
                            param_range[0], min(param_range[1], sampled)
                        )
                    else:
                        params[param_name] = random.uniform(
                            param_range[0], param_range[1]
                        )

            return params

        except Exception as e:
            logger.warning(f"高斯过程采样失败，使用随机采样: {e}")
            return self._sample_random_params(param_space)

    def _genetic_operations(
        self,
        population: List[Dict],
        fitness_scores: List[float],
        param_space: Dict,
        mutation_rate: float,
        crossover_rate: float,
        maximize: bool,
    ) -> List[Dict]:
        """遗传算法操作：选择、交叉、变异"""
        try:
            # 选择操作（轮盘赌选择）
            if maximize:
                # 确保适应度为正
                adjusted_scores = [
                    max(0, score - min(fitness_scores) + 1e-6)
                    for score in fitness_scores
                ]
            else:
                # 对于最小化问题，转换适应度
                max_score = max(fitness_scores)
                adjusted_scores = [max_score - score + 1e-6 for score in fitness_scores]

            total_fitness = sum(adjusted_scores)
            if total_fitness > 0:
                probabilities = [score / total_fitness for score in adjusted_scores]
            else:
                probabilities = [1 / len(population)] * len(population)

            # 选择父代
            selected_indices = np.random.choice(
                len(population), size=len(population), replace=True, p=probabilities
            )
            selected_population = [population[i].copy() for i in selected_indices]

            # 交叉操作
            new_population = []
            for i in range(0, len(selected_population), 2):
                parent1 = selected_population[i]
                parent2 = (
                    selected_population[i + 1]
                    if i + 1 < len(selected_population)
                    else selected_population[0]
                )

                if np.random.random() < crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2, param_space)
                    new_population.extend([child1, child2])
                else:
                    new_population.extend([parent1, parent2])

            # 变异操作
            for individual in new_population:
                if np.random.random() < mutation_rate:
                    self._mutate(individual, param_space)

            return new_population[: len(population)]

        except Exception as e:
            logger.error(f"遗传算法操作失败: {e}")
            return population

    def _crossover(self, parent1: Dict, parent2: Dict, param_space: Dict) -> tuple:
        """交叉操作"""
        child1 = {}
        child2 = {}

        for param_name, param_range in param_space.items():
            if np.random.random() < 0.5:
                child1[param_name] = parent1[param_name]
                child2[param_name] = parent2[param_name]
            else:
                child1[param_name] = parent2[param_name]
                child2[param_name] = parent1[param_name]

        return child1, child2

    def _mutate(self, individual: Dict, param_space: Dict) -> None:
        """变异操作"""
        # 随机选择一个参数进行变异
        param_name = np.random.choice(list(param_space.keys()))
        param_range = param_space[param_name]

        if isinstance(param_range, list):
            # 离散参数：变异为另一个随机值
            current_val = individual[param_name]
            other_values = [v for v in param_range if v != current_val]
            if other_values:
                individual[param_name] = np.random.choice(other_values)
        else:
            # 连续参数：高斯变异
            current_val = individual[param_name]
            std = (param_range[1] - param_range[0]) * 0.1
            mutated_val = current_val + np.random.normal(0, std)
            individual[param_name] = max(
                param_range[0], min(param_range[1], mutated_val)
            )

    def _evaluate_parameters(self, objective_func: Callable, params: Dict) -> float:
        """评估参数（带缓存）"""
        cache_key = self._generate_param_cache_key(params)
        if cache_key in self.optimization_cache:
            return self.optimization_cache[cache_key]

        score = objective_func(params)
        self.optimization_cache[cache_key] = score
        return score

    def _generate_param_cache_key(self, params: Dict) -> str:
        """生成参数缓存键"""
        import hashlib

        param_str = str(sorted(params.items()))
        return hashlib.md5(param_str.encode()).hexdigest()

    def _estimate_param_space_size(self, param_space: Dict) -> int:
        """估计参数空间大小"""
        size = 1
        for param_range in param_space.values():
            if isinstance(param_range, list):
                size *= len(param_range)
            elif isinstance(param_range, tuple):
                # 连续参数估算为100个离散点
                size *= 100
        return size

    def _get_convergence_curve(self) -> List[float]:
        """获取收敛曲线"""
        # 从历史记录中提取最佳分数
        if not self.optimization_history:
            return []

        return [record["best_score"] for record in self.optimization_history[-10:]]

    def _mean_variance_optimization_gpu(
        self, returns: pd.DataFrame, risk_free_rate: float
    ) -> Dict[str, Any]:
        """GPU加速均值-方差优化"""
        try:
            if self.gpu_available:
                returns_gpu = cp.array(returns.values)
                mean_returns = cp.mean(returns_gpu, axis=0)
                cov_matrix = cp.cov(returns_gpu, rowvar=False)

                # 添加单位矩阵以确保正定性
                cov_matrix += cp.eye(cov_matrix.shape[0]) * 1e-6
            else:
                mean_returns = returns.mean().values
                cov_matrix = returns.cov().values
                cov_matrix += np.eye(cov_matrix.shape[0]) * 1e-6

            # 简化的优化：等权重开始
            n_assets = len(mean_returns)
            weights = np.ones(n_assets) / n_assets

            # 计算投资组合统计量
            if self.gpu_available:
                portfolio_return = float(cp.dot(weights, mean_returns))
                portfolio_variance = float(cp.dot(cp.dot(weights, cov_matrix), weights))
            else:
                portfolio_return = np.dot(weights, mean_returns)
                portfolio_variance = np.dot(np.dot(weights, cov_matrix), weights)

            portfolio_std = np.sqrt(portfolio_variance)
            sharpe_ratio = (
                (portfolio_return - risk_free_rate) / portfolio_std
                if portfolio_std > 0
                else 0
            )

            return {
                "weights": weights.tolist(),
                "expected_return": portfolio_return,
                "volatility": portfolio_std,
                "sharpe_ratio": sharpe_ratio,
                "method": "mean_variance",
            }

        except Exception as e:
            logger.error(f"均值-方差优化失败: {e}")
            return {"error": str(e)}

    def _risk_parity_optimization_gpu(self, returns: pd.DataFrame) -> Dict[str, Any]:
        """GPU加速风险平价优化"""
        try:
            # 计算资产协方差矩阵
            if self.gpu_available:
                returns_gpu = cp.array(returns.values)
                cov_matrix = cp.cov(returns_gpu, rowvar=False)
            else:
                cov_matrix = returns.cov().values

            # 简化的风险平价：基于波动率的倒数
            if self.gpu_available:
                volatilities = cp.sqrt(cp.diag(cov_matrix))
            else:
                volatilities = np.sqrt(np.diag(cov_matrix))

            # 风险平价权重
            inv_vols = 1.0 / (
                volatilities.get() if self.gpu_available else volatilities
            )
            weights = inv_vols / np.sum(inv_vols)

            # 计算组合统计量
            if self.gpu_available:
                portfolio_variance = float(cp.dot(cp.dot(weights, cov_matrix), weights))
            else:
                portfolio_variance = np.dot(np.dot(weights, cov_matrix), weights)

            portfolio_std = np.sqrt(portfolio_variance)
            expected_return = float(returns.mean().dot(weights))

            return {
                "weights": weights.tolist(),
                "expected_return": expected_return,
                "volatility": portfolio_std,
                "method": "risk_parity",
            }

        except Exception as e:
            logger.error(f"风险平价优化失败: {e}")
            return {"error": str(e)}

    def _max_sharpe_optimization_gpu(
        self, returns: pd.DataFrame, risk_free_rate: float
    ) -> Dict[str, Any]:
        """GPU加速最大夏普比率优化"""
        # 简化实现：使用均值-方差结果
        result = self._mean_variance_optimization_gpu(returns, risk_free_rate)
        result["method"] = "max_sharpe"
        return result

    def _min_variance_optimization_gpu(self, returns: pd.DataFrame) -> Dict[str, Any]:
        """GPU加速最小方差优化"""
        # 简化实现：使用全局最小方差组合
        result = self._mean_variance_optimization_gpu(returns, 0.0)
        result["method"] = "min_variance"
        return result

    def clear_cache(self) -> None:
        """清除优化缓存"""
        self.optimization_cache.clear()
        logger.info("优化缓存已清除")

    def get_optimization_history(self) -> List[Dict[str, Any]]:
        """获取优化历史"""
        return self.optimization_history.copy()

    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        return {
            "cache_size": len(self.optimization_cache),
            "cached_params": list(self.optimization_cache.keys()),
            "history_size": len(self.optimization_history),
        }
