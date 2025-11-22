"""
Genetic Algorithm Optimizer

遗传算法优化器 - 模拟生物进化的优化方法
"""
from typing import Dict, Any, List, Optional, Tuple
import random
import copy
import logging
import time

from app.backtest.optimization.base import (
    BaseOptimizer,
    OptimizationResult,
    ParameterSpace
)

logger = logging.getLogger(__name__)


class Individual:
    """个体 (代表一个参数组合)"""

    def __init__(self, genes: Dict[str, Any]):
        """
        Args:
            genes: 基因 (参数字典)
        """
        self.genes = genes
        self.fitness: float = 0.0
        self.result: Optional[OptimizationResult] = None

    def __repr__(self):
        return f"Individual(fitness={self.fitness:.4f}, genes={self.genes})"


class GeneticOptimizer(BaseOptimizer):
    """
    遗传算法优化器

    核心概念:
    - 种群 (Population): 一组参数组合
    - 个体 (Individual): 单个参数组合
    - 基因 (Gene): 单个参数值
    - 适应度 (Fitness): 优化目标值
    - 选择 (Selection): 选择优秀个体繁殖
    - 交叉 (Crossover): 组合两个个体的基因
    - 变异 (Mutation): 随机改变基因

    特点:
    - 全局搜索能力强
    - 适合复杂非凸优化问题
    - 可以跳出局部最优
    - 支持并行计算
    """

    def __init__(
        self,
        strategy_type: str,
        parameter_spaces: List[ParameterSpace],
        objective: str = 'sharpe_ratio',
        maximize: bool = True,
        population_size: int = 50,
        n_generations: int = 20,
        crossover_rate: float = 0.8,
        mutation_rate: float = 0.1,
        elite_size: int = 2,
        tournament_size: int = 3,
        random_seed: Optional[int] = None
    ):
        """
        初始化遗传算法优化器

        Args:
            strategy_type: 策略类型
            parameter_spaces: 参数空间
            objective: 优化目标
            maximize: 是否最大化
            population_size: 种群大小
            n_generations: 进化代数
            crossover_rate: 交叉率
            mutation_rate: 变异率
            elite_size: 精英保留数量
            tournament_size: 锦标赛选择大小
            random_seed: 随机种子
        """
        super().__init__(strategy_type, parameter_spaces, objective, maximize)

        self.population_size = population_size
        self.n_generations = n_generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        self.tournament_size = tournament_size
        self.random_seed = random_seed

        # 随机数生成器
        self.rng = random.Random(random_seed)

        # 进化历史
        self.generation_history: List[Dict[str, Any]] = []

        logger.info(
            f"遗传算法优化器初始化: "
            f"种群={population_size}, 代数={n_generations}, "
            f"交叉率={crossover_rate}, 变异率={mutation_rate}"
        )

    def _create_random_individual(self) -> Individual:
        """创建随机个体"""
        genes = {}
        for space in self.parameter_spaces:
            genes[space.name] = space.get_random_value(self.rng)
        return Individual(genes)

    def _initialize_population(self) -> List[Individual]:
        """初始化种群"""
        population = []
        for _ in range(self.population_size):
            individual = self._create_random_individual()
            population.append(individual)
        return population

    def _evaluate_individual(
        self,
        individual: Individual,
        market_data: Dict[str, Any]
    ) -> float:
        """
        评估个体适应度

        Args:
            individual: 待评估个体
            market_data: 市场数据

        Returns:
            适应度值
        """
        result = self._run_single_backtest(individual.genes, market_data)
        individual.result = result

        fitness = result.get_score(self.objective)
        individual.fitness = fitness

        return fitness

    def _evaluate_population(
        self,
        population: List[Individual],
        market_data: Dict[str, Any]
    ):
        """评估整个种群"""
        for individual in population:
            if individual.result is None:  # 跳过已评估的
                self._evaluate_individual(individual, market_data)

    def _tournament_selection(self, population: List[Individual]) -> Individual:
        """
        锦标赛选择

        Args:
            population: 种群

        Returns:
            获胜个体
        """
        tournament = self.rng.sample(population, min(self.tournament_size, len(population)))

        if self.maximize:
            winner = max(tournament, key=lambda ind: ind.fitness)
        else:
            winner = min(tournament, key=lambda ind: ind.fitness)

        return winner

    def _roulette_selection(self, population: List[Individual]) -> Individual:
        """
        轮盘赌选择

        Args:
            population: 种群

        Returns:
            选中个体
        """
        # 计算适应度总和 (处理负值)
        min_fitness = min(ind.fitness for ind in population)
        adjusted_fitness = [ind.fitness - min_fitness + 1 for ind in population]
        total_fitness = sum(adjusted_fitness)

        # 轮盘赌选择
        pick = self.rng.uniform(0, total_fitness)
        current = 0

        for i, fitness in enumerate(adjusted_fitness):
            current += fitness
            if current >= pick:
                return population[i]

        return population[-1]

    def _crossover(
        self,
        parent1: Individual,
        parent2: Individual
    ) -> Tuple[Individual, Individual]:
        """
        交叉操作 (均匀交叉)

        Args:
            parent1: 父本1
            parent2: 父本2

        Returns:
            两个子代
        """
        if self.rng.random() > self.crossover_rate:
            # 不交叉，直接复制
            return (
                Individual(copy.deepcopy(parent1.genes)),
                Individual(copy.deepcopy(parent2.genes))
            )

        child1_genes = {}
        child2_genes = {}

        for space in self.parameter_spaces:
            param_name = space.name

            # 均匀交叉: 随机选择来自哪个父本
            if self.rng.random() < 0.5:
                child1_genes[param_name] = parent1.genes[param_name]
                child2_genes[param_name] = parent2.genes[param_name]
            else:
                child1_genes[param_name] = parent2.genes[param_name]
                child2_genes[param_name] = parent1.genes[param_name]

        return Individual(child1_genes), Individual(child2_genes)

    def _blend_crossover(
        self,
        parent1: Individual,
        parent2: Individual,
        alpha: float = 0.5
    ) -> Tuple[Individual, Individual]:
        """
        混合交叉 (BLX-α)

        适用于连续参数

        Args:
            parent1, parent2: 父本
            alpha: 扩展系数

        Returns:
            两个子代
        """
        if self.rng.random() > self.crossover_rate:
            return (
                Individual(copy.deepcopy(parent1.genes)),
                Individual(copy.deepcopy(parent2.genes))
            )

        child1_genes = {}
        child2_genes = {}

        for space in self.parameter_spaces:
            param_name = space.name
            v1 = parent1.genes[param_name]
            v2 = parent2.genes[param_name]

            if space.param_type == 'choice':
                # 离散参数: 随机选择
                child1_genes[param_name] = self.rng.choice([v1, v2])
                child2_genes[param_name] = self.rng.choice([v1, v2])
            else:
                # 连续参数: 混合
                min_v = min(v1, v2)
                max_v = max(v1, v2)
                range_v = max_v - min_v

                # BLX-α 范围
                low = min_v - alpha * range_v
                high = max_v + alpha * range_v

                # 限制在参数范围内
                if space.min_value is not None:
                    low = max(low, space.min_value)
                if space.max_value is not None:
                    high = min(high, space.max_value)

                new_v1 = self.rng.uniform(low, high)
                new_v2 = self.rng.uniform(low, high)

                if space.param_type == 'int':
                    new_v1 = int(round(new_v1))
                    new_v2 = int(round(new_v2))

                child1_genes[param_name] = new_v1
                child2_genes[param_name] = new_v2

        return Individual(child1_genes), Individual(child2_genes)

    def _mutate(self, individual: Individual):
        """
        变异操作

        Args:
            individual: 待变异个体 (原地修改)
        """
        for space in self.parameter_spaces:
            if self.rng.random() < self.mutation_rate:
                # 随机变异
                individual.genes[space.name] = space.get_random_value(self.rng)

    def _gaussian_mutate(self, individual: Individual, sigma: float = 0.1):
        """
        高斯变异

        Args:
            individual: 待变异个体
            sigma: 变异强度
        """
        for space in self.parameter_spaces:
            if self.rng.random() < self.mutation_rate:
                current = individual.genes[space.name]

                if space.param_type == 'choice':
                    # 离散参数: 随机选择
                    individual.genes[space.name] = space.get_random_value(self.rng)
                else:
                    # 连续参数: 高斯扰动
                    if space.min_value is not None and space.max_value is not None:
                        range_v = space.max_value - space.min_value
                        noise = self.rng.gauss(0, sigma * range_v)
                        new_value = current + noise

                        # 限制范围
                        new_value = max(space.min_value, min(space.max_value, new_value))

                        if space.param_type == 'int':
                            new_value = int(round(new_value))

                        individual.genes[space.name] = new_value

    def _select_elites(self, population: List[Individual]) -> List[Individual]:
        """
        选择精英个体

        Args:
            population: 种群

        Returns:
            精英个体列表
        """
        sorted_pop = sorted(
            population,
            key=lambda ind: ind.fitness,
            reverse=self.maximize
        )
        return [Individual(copy.deepcopy(ind.genes)) for ind in sorted_pop[:self.elite_size]]

    def optimize(
        self,
        market_data: Dict[str, Any] = None,
        progress_callback: Optional[callable] = None,
        use_blend_crossover: bool = True,
        use_gaussian_mutation: bool = True,
        early_stop: bool = True,
        patience: int = 5,
        **kwargs
    ) -> List[OptimizationResult]:
        """
        执行遗传算法优化

        Args:
            market_data: 市场数据
            progress_callback: 进度回调
            use_blend_crossover: 使用混合交叉
            use_gaussian_mutation: 使用高斯变异
            early_stop: 启用早停
            patience: 早停耐心值

        Returns:
            所有优化结果
        """
        logger.info(
            f"开始遗传算法优化: "
            f"策略={self.strategy_type}, "
            f"种群={self.population_size}, "
            f"代数={self.n_generations}"
        )

        start_time = time.time()

        data = market_data or self._market_data

        if data is None:
            logger.warning("无市场数据，优化中止")
            return []

        # 初始化种群
        population = self._initialize_population()

        # 评估初始种群
        self._evaluate_population(population, data)

        # 记录初始结果
        self.results = [ind.result for ind in population if ind.result]

        # 更新最佳
        for ind in population:
            if ind.result:
                self._update_best_result(ind.result)

        # 记录第0代
        best_ind = max(population, key=lambda i: i.fitness) if self.maximize else min(population, key=lambda i: i.fitness)
        avg_fitness = sum(ind.fitness for ind in population) / len(population)

        self.generation_history.append({
            'generation': 0,
            'best_fitness': best_ind.fitness,
            'avg_fitness': avg_fitness,
            'best_genes': copy.deepcopy(best_ind.genes)
        })

        logger.info(f"第0代: 最佳={best_ind.fitness:.4f}, 平均={avg_fitness:.4f}")

        no_improvement_count = 0
        prev_best_fitness = best_ind.fitness

        # 进化循环
        for generation in range(1, self.n_generations + 1):
            new_population = []

            # 保留精英
            elites = self._select_elites(population)
            new_population.extend(elites)

            # 生成新个体
            while len(new_population) < self.population_size:
                # 选择父本
                parent1 = self._tournament_selection(population)
                parent2 = self._tournament_selection(population)

                # 交叉
                if use_blend_crossover:
                    child1, child2 = self._blend_crossover(parent1, parent2)
                else:
                    child1, child2 = self._crossover(parent1, parent2)

                # 变异
                if use_gaussian_mutation:
                    self._gaussian_mutate(child1)
                    self._gaussian_mutate(child2)
                else:
                    self._mutate(child1)
                    self._mutate(child2)

                new_population.extend([child1, child2])

            # 截取到种群大小
            population = new_population[:self.population_size]

            # 评估新种群 (精英不需要重新评估)
            self._evaluate_population(population, data)

            # 收集结果
            for ind in population:
                if ind.result and ind.result not in self.results:
                    self.results.append(ind.result)
                    self._update_best_result(ind.result)

            # 统计
            best_ind = max(population, key=lambda i: i.fitness) if self.maximize else min(population, key=lambda i: i.fitness)
            avg_fitness = sum(ind.fitness for ind in population) / len(population)

            self.generation_history.append({
                'generation': generation,
                'best_fitness': best_ind.fitness,
                'avg_fitness': avg_fitness,
                'best_genes': copy.deepcopy(best_ind.genes)
            })

            # 进度回调
            if progress_callback:
                progress_callback(generation, self.n_generations, best_ind.result)

            # 日志
            logger.info(
                f"第{generation}代: "
                f"最佳={best_ind.fitness:.4f}, "
                f"平均={avg_fitness:.4f}"
            )

            # 早停检查
            if early_stop:
                if abs(best_ind.fitness - prev_best_fitness) < 0.0001:
                    no_improvement_count += 1
                else:
                    no_improvement_count = 0

                if no_improvement_count >= patience:
                    logger.info(f"早停触发: 连续{patience}代无改进")
                    break

                prev_best_fitness = best_ind.fitness

        total_time = time.time() - start_time

        logger.info(
            f"遗传算法完成: "
            f"耗时={total_time:.2f}秒 "
            f"代数={len(self.generation_history)} "
            f"评估={len(self.results)}组合 "
            f"最佳{self.objective}={self.best_result.get_score(self.objective):.4f}"
        )

        return self.results

    def get_evolution_curve(self) -> Dict[str, List[float]]:
        """
        获取进化曲线

        Returns:
            {'generations': [...], 'best': [...], 'avg': [...]}
        """
        return {
            'generations': [h['generation'] for h in self.generation_history],
            'best': [h['best_fitness'] for h in self.generation_history],
            'avg': [h['avg_fitness'] for h in self.generation_history]
        }

    def get_diversity_metrics(self, population: List[Individual]) -> Dict[str, float]:
        """
        计算种群多样性指标

        Args:
            population: 种群

        Returns:
            多样性指标
        """
        if not population:
            return {}

        diversity_scores = []

        for space in self.parameter_spaces:
            param_name = space.name
            values = [ind.genes[param_name] for ind in population]

            if space.param_type == 'choice':
                # 离散参数: 计算不同值的数量
                unique_ratio = len(set(values)) / len(values)
                diversity_scores.append(unique_ratio)
            else:
                # 连续参数: 计算标准差
                mean = sum(values) / len(values)
                std = (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5
                if space.max_value and space.min_value:
                    normalized_std = std / (space.max_value - space.min_value)
                else:
                    normalized_std = std
                diversity_scores.append(min(1.0, normalized_std))

        return {
            'avg_diversity': sum(diversity_scores) / len(diversity_scores) if diversity_scores else 0,
            'per_parameter': dict(zip([s.name for s in self.parameter_spaces], diversity_scores))
        }
