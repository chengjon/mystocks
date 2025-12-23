"""
Grid Search Optimizer

网格搜索优化器 - 穷举所有参数组合
"""

from typing import Dict, Any, List, Optional
from itertools import product
import logging
import time

from app.backtest.optimization.base import (
    BaseOptimizer,
    OptimizationResult,
    ParameterSpace,
)

logger = logging.getLogger(__name__)


class GridSearchOptimizer(BaseOptimizer):
    """
    网格搜索优化器

    特点:
    - 穷举所有参数组合
    - 保证找到全局最优 (在网格范围内)
    - 适合参数空间较小的情况
    - 计算量随参数维度指数增长
    """

    def __init__(
        self,
        strategy_type: str,
        parameter_spaces: List[ParameterSpace],
        objective: str = "sharpe_ratio",
        maximize: bool = True,
        parallel: bool = False,
        n_jobs: int = 1,
    ):
        """
        初始化网格搜索优化器

        Args:
            strategy_type: 策略类型
            parameter_spaces: 参数空间列表
            objective: 优化目标
            maximize: 是否最大化
            parallel: 是否并行执行
            n_jobs: 并行任务数
        """
        super().__init__(strategy_type, parameter_spaces, objective, maximize)

        self.parallel = parallel
        self.n_jobs = n_jobs

        # 预计算网格大小
        self._grid_size = self._calculate_grid_size()
        logger.info(f"网格搜索优化器初始化: 网格大小={self._grid_size}")

    def _calculate_grid_size(self) -> int:
        """计算网格总大小"""
        size = 1
        for space in self.parameter_spaces:
            values = space.get_grid_values()
            size *= len(values)
        return size

    def _generate_parameter_combinations(self) -> List[Dict[str, Any]]:
        """
        生成所有参数组合

        Returns:
            参数组合列表
        """
        # 获取每个参数的取值列表
        param_values = []
        param_names = []

        for space in self.parameter_spaces:
            param_names.append(space.name)
            param_values.append(space.get_grid_values())

        # 生成笛卡尔积
        combinations = []
        for values in product(*param_values):
            param_dict = dict(zip(param_names, values))
            combinations.append(param_dict)

        return combinations

    def optimize(
        self,
        market_data: Dict[str, Any] = None,
        progress_callback: Optional[callable] = None,
        early_stop: bool = False,
        early_stop_threshold: float = None,
        **kwargs,
    ) -> List[OptimizationResult]:
        """
        执行网格搜索优化

        Args:
            market_data: 市场数据
            progress_callback: 进度回调函数 (current, total, result)
            early_stop: 是否启用早停
            early_stop_threshold: 早停阈值

        Returns:
            所有优化结果
        """
        logger.info(
            f"开始网格搜索优化: 策略={self.strategy_type}, 组合数={self._grid_size}"
        )

        start_time = time.time()

        # 使用传入数据或缓存数据
        data = market_data or self._market_data

        if data is None:
            logger.warning("无市场数据，优化中止")
            return []

        # 生成所有参数组合
        combinations = self._generate_parameter_combinations()
        total = len(combinations)

        self.results = []
        self.best_result = None

        for idx, params in enumerate(combinations):
            # 运行回测
            result = self._run_single_backtest(params, data)
            self.results.append(result)

            # 更新最佳结果
            self._update_best_result(result)

            # 进度回调
            if progress_callback:
                progress_callback(idx + 1, total, result)

            # 日志记录
            if (idx + 1) % 10 == 0 or idx == 0:
                score = result.get_score(self.objective)
                best_score = (
                    self.best_result.get_score(self.objective)
                    if self.best_result
                    else 0
                )
                logger.info(
                    f"网格搜索进度: {idx + 1}/{total} "
                    f"当前{self.objective}={score:.4f} "
                    f"最佳={best_score:.4f}"
                )

            # 早停检查
            if early_stop and early_stop_threshold is not None:
                if self.best_result:
                    best_score = self.best_result.get_score(self.objective)
                    if self.maximize and best_score >= early_stop_threshold:
                        logger.info(
                            f"早停触发: 已达到目标 {best_score:.4f} >= {early_stop_threshold}"
                        )
                        break
                    elif not self.maximize and best_score <= early_stop_threshold:
                        logger.info(
                            f"早停触发: 已达到目标 {best_score:.4f} <= {early_stop_threshold}"
                        )
                        break

        total_time = time.time() - start_time

        logger.info(
            f"网格搜索完成: "
            f"耗时={total_time:.2f}秒 "
            f"测试={len(self.results)}组合 "
            f"最佳{self.objective}={self.best_result.get_score(self.objective):.4f}"
        )

        return self.results

    def get_parameter_sensitivity(self) -> Dict[str, Dict[str, float]]:
        """
        分析参数敏感性

        计算每个参数对目标指标的影响程度

        Returns:
            {参数名: {value: avg_score}}
        """
        if not self.results:
            return {}

        sensitivity = {}

        for space in self.parameter_spaces:
            param_name = space.name
            value_scores = {}

            # 按参数值分组
            for result in self.results:
                value = result.parameters.get(param_name)
                score = result.get_score(self.objective)

                if value not in value_scores:
                    value_scores[value] = []
                value_scores[value].append(score)

            # 计算每个值的平均得分
            sensitivity[param_name] = {
                str(value): sum(scores) / len(scores)
                for value, scores in value_scores.items()
            }

        return sensitivity

    def get_heatmap_data(self, param1: str, param2: str) -> Dict[str, Any]:
        """
        获取两个参数的热力图数据

        Args:
            param1: 第一个参数名
            param2: 第二个参数名

        Returns:
            热力图数据 {x_values, y_values, z_values}
        """
        if not self.results:
            return {}

        # 收集数据
        data_points = {}

        for result in self.results:
            v1 = result.parameters.get(param1)
            v2 = result.parameters.get(param2)
            score = result.get_score(self.objective)

            key = (v1, v2)
            if key not in data_points:
                data_points[key] = []
            data_points[key].append(score)

        # 获取唯一值
        x_values = sorted(set(k[0] for k in data_points.keys()))
        y_values = sorted(set(k[1] for k in data_points.keys()))

        # 构建Z矩阵
        z_values = []
        for y in y_values:
            row = []
            for x in x_values:
                scores = data_points.get((x, y), [0])
                row.append(sum(scores) / len(scores))
            z_values.append(row)

        return {
            "x_values": x_values,
            "y_values": y_values,
            "z_values": z_values,
            "param1": param1,
            "param2": param2,
            "objective": self.objective,
        }

    def get_top_parameter_values(self, top_n: int = 5) -> Dict[str, List[Any]]:
        """
        获取每个参数在Top N结果中的取值分布

        Args:
            top_n: 取前N个结果

        Returns:
            {参数名: [值列表]}
        """
        top_results = self.get_top_results(top_n)

        distributions = {}
        for space in self.parameter_spaces:
            param_name = space.name
            distributions[param_name] = [
                r.parameters.get(param_name) for r in top_results
            ]

        return distributions
