"""
智能路由器模块 (SmartRouter)

实现多维度数据源路由决策，综合考虑性能、成本、负载和地域因素。
"""

import logging
from typing import Dict, List, Optional, Any
from collections import defaultdict
import time

logger = logging.getLogger(__name__)


class SmartRouter:
    """
    智能路由器

    特性:
    - 多维度决策: 性能评分、成本优化、负载均衡、地域感知
    - 可配置权重
    - 实时性能统计
    - 自动选择最优数据源
    """

    def __init__(
        self,
        performance_weight: float = 0.4,  # 性能权重
        cost_weight: float = 0.3,  # 成本权重
        load_weight: float = 0.2,  # 负载权重
        location_weight: float = 0.1,  # 地域权重
    ):
        """
        初始化智能路由器

        Args:
            performance_weight: 性能评分权重 (0.0-1.0)
            cost_weight: 成本优化权重 (0.0-1.0)
            load_weight: 负载均衡权重 (0.0-1.0)
            location_weight: 地域感知权重 (0.0-1.0)
        """
        self.performance_weight = performance_weight
        self.cost_weight = cost_weight
        self.load_weight = load_weight
        self.location_weight = location_weight

        # 性能统计 (endpoint -> stats)
        self.performance_stats: Dict[str, Dict] = defaultdict(
            lambda: {
                "call_count": 0,
                "total_latency": 0.0,
                "success_count": 0,
                "p50_latency": 0.0,
                "p95_latency": 0.0,
                "p99_latency": 0.0,
                "last_call_time": None,
                "latencies": [],  # 保留最近 100 次延迟
            }
        )

        # 负载统计 (endpoint -> current_call_count)
        self.current_load: Dict[str, int] = defaultdict(int)

        logger.info(
            f"SmartRouter initialized: performance={performance_weight}, "
            f"cost={cost_weight}, load={load_weight}, location={location_weight}"
        )

    def route(
        self,
        endpoints: List[Dict[str, Any]],
        data_category: str,
        caller_location: str = "default",
    ) -> Optional[Dict[str, Any]]:
        """
        智能选择最优数据源

        Args:
            endpoints: 候选数据源列表
            data_category: 数据分类
            caller_location: 调用方位置

        Returns:
            选中的最优数据源，如果没有可用数据源则返回 None
        """
        if not endpoints:
            return None

        # 只有一个选择，直接返回
        if len(endpoints) == 1:
            return endpoints[0]

        # 计算每个数据源的综合评分
        scored_endpoints = []
        for endpoint in endpoints:
            endpoint_name = endpoint.get("endpoint_name") or endpoint.get("name", "unknown")

            score = self._calculate_score(
                endpoint,
                data_category,
                caller_location,
            )

            scored_endpoints.append((score, endpoint))

        # 按评分排序，选择最高分
        scored_endpoints.sort(key=lambda x: x[0], reverse=True)

        best_score, best_endpoint = scored_endpoints[0]

        logger.debug(f"SmartRouter selected: {best_endpoint.get('endpoint_name')} " f"(score={best_score:.2f})")

        return best_endpoint

    def _calculate_score(
        self,
        endpoint: Dict[str, Any],
        data_category: str,
        caller_location: str,
    ) -> float:
        """
        计算数据源的综合评分

        Args:
            endpoint: 数据源配置
            data_category: 数据分类
            caller_location: 调用方位置

        Returns:
            综合评分 (0-100)
        """
        endpoint_name = endpoint.get("endpoint_name") or endpoint.get("name", "unknown")

        # 1. 性能评分 (P50/P95/P99 延迟 + 成功率)
        performance_score = self._score_by_performance(endpoint_name)

        # 2. 成本评分 (免费源优先)
        cost_score = self._adjust_by_cost(endpoint)

        # 3. 负载评分 (当前调用数)
        load_score = self._adjust_by_load(endpoint_name)

        # 4. 地域评分 (最近节点)
        location_score = self._adjust_by_location(endpoint, caller_location)

        # 综合评分
        total_score = (
            performance_score * self.performance_weight
            + cost_score * self.cost_weight
            + load_score * self.load_weight
            + location_score * self.location_weight
        )

        return total_score

    def _score_by_performance(self, endpoint_name: str) -> float:
        """
        根据性能评分

        考虑因素:
        - P50/P95/P99 延迟
        - 成功率
        - 调用次数

        Returns:
            性能评分 (0-100)
        """
        stats = self.performance_stats[endpoint_name]

        # 如果没有历史数据，返回基础分 50
        if stats["call_count"] == 0:
            return 50.0

        # 计算平均延迟 (P50 权重最高)
        avg_latency = stats["p50_latency"] * 0.5 + stats["p95_latency"] * 0.3 + stats["p99_latency"] * 0.2

        # 计算成功率
        success_rate = stats["success_count"] / stats["call_count"] if stats["call_count"] > 0 else 0

        # 延迟评分: 延迟越低，分数越高
        # 0ms -> 100分, 1000ms -> 0分
        latency_score = max(0, 100 - avg_latency / 10)

        # 成功率评分: 成功率越高，分数越高
        success_score = success_rate * 100

        # 综合性能评分
        performance_score = latency_score * 0.6 + success_score * 0.4

        return performance_score

    def _adjust_by_cost(self, endpoint: Dict[str, Any]) -> float:
        """
        根据成本调整评分

        规则:
        - 免费数据源: +50 分加成
        - 有免费额度: +20 分加成
        - 付费数据源: 基础分

        Returns:
            成本评分 (0-100)
        """
        source_type = endpoint.get("source_type", "")
        cost_info = endpoint.get("cost", {})

        base_score = 50.0

        # 免费数据源
        if cost_info.get("is_free", False):
            return base_score + 50.0

        # 有免费额度
        if cost_info.get("has_free_quota", False):
            return base_score + 20.0

        # 付费数据源
        return base_score

    def _adjust_by_load(self, endpoint_name: str) -> float:
        """
        根据当前负载调整评分

        规则:
        - 当前调用数越少，分数越高
        - 0 调用 -> 100分
        - 10+ 调用 -> 0分

        Returns:
            负载评分 (0-100)
        """
        current_calls = self.current_load[endpoint_name]

        # 线性衰减: 0 调用 -> 100分, 10 调用 -> 0分
        load_score = max(0, 100 - current_calls * 10)

        return load_score

    def _adjust_by_location(self, endpoint: Dict[str, Any], caller_location: str) -> float:
        """
        根据地域调整评分

        规则:
        - 同地域: 100分
        - 不同地域: 50分
        - 未知地域: 50分

        Returns:
            地域评分 (0-100)
        """
        endpoint_location = endpoint.get("location", "unknown")

        # 如果没有地域信息，返回基础分
        if endpoint_location == "unknown" or caller_location == "default":
            return 50.0

        # 同地域
        if endpoint_location == caller_location:
            return 100.0

        # 不同地域
        return 50.0

    def record_call(
        self,
        endpoint_name: str,
        latency: float,
        success: bool,
    ):
        """
        记录调用结果

        Args:
            endpoint_name: 数据源名称
            latency: 调用延迟 (秒)
            success: 是否成功
        """
        stats = self.performance_stats[endpoint_name]

        # 更新统计
        stats["call_count"] += 1
        stats["total_latency"] += latency
        stats["last_call_time"] = time.time()

        if success:
            stats["success_count"] += 1

        # 记录延迟 (保留最近 100 次)
        stats["latencies"].append(latency)
        if len(stats["latencies"]) > 100:
            stats["latencies"].pop(0)

        # 更新百分位数
        self._update_percentiles(endpoint_name)

        # 增加负载计数
        self.current_load[endpoint_name] += 1

        logger.debug(f"Recorded call: {endpoint_name}, latency={latency:.3f}s, success={success}")

    def record_call_complete(self, endpoint_name: str):
        """
        记录调用完成

        Args:
            endpoint_name: 数据源名称
        """
        # 减少负载计数
        if self.current_load[endpoint_name] > 0:
            self.current_load[endpoint_name] -= 1

    def _update_percentiles(self, endpoint_name: str):
        """
        更新延迟百分位数

        Args:
            endpoint_name: 数据源名称
        """
        stats = self.performance_stats[endpoint_name]
        latencies = sorted(stats["latencies"])

        if not latencies:
            return

        n = len(latencies)
        stats["p50_latency"] = latencies[int(n * 0.5)]
        stats["p95_latency"] = latencies[int(n * 0.95)]
        stats["p99_latency"] = latencies[int(n * 0.99)]

    def get_stats(self, endpoint_name: str) -> Dict[str, Any]:
        """
        获取数据源统计信息

        Args:
            endpoint_name: 数据源名称

        Returns:
            统计信息字典
        """
        stats = self.performance_stats[endpoint_name]

        return {
            "endpoint_name": endpoint_name,
            "call_count": stats["call_count"],
            "avg_latency": (stats["total_latency"] / stats["call_count"] if stats["call_count"] > 0 else 0),
            "p50_latency": stats["p50_latency"],
            "p95_latency": stats["p95_latency"],
            "p99_latency": stats["p99_latency"],
            "success_rate": (stats["success_count"] / stats["call_count"] if stats["call_count"] > 0 else 0),
            "current_load": self.current_load[endpoint_name],
            "performance_score": self._score_by_performance(endpoint_name),
        }

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有数据源的统计信息

        Returns:
            所有数据源的统计信息
        """
        return {endpoint_name: self.get_stats(endpoint_name) for endpoint_name in self.performance_stats.keys()}

    def reset_stats(self, endpoint_name: Optional[str] = None):
        """
        重置统计信息

        Args:
            endpoint_name: 数据源名称，None 表示重置所有
        """
        if endpoint_name:
            if endpoint_name in self.performance_stats:
                del self.performance_stats[endpoint_name]
            if endpoint_name in self.current_load:
                del self.current_load[endpoint_name]
        else:
            self.performance_stats.clear()
            self.current_load.clear()

        logger.info(f"Reset stats for: {endpoint_name or 'all endpoints'}")
