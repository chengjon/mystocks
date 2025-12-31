"""
Indicator Dependency Graph System
=================================

指标依赖关系图管理，用于：
- 构建指标间依赖关系
- 检测循环依赖
- 确定计算顺序
- 支持增量计算

核心类:
- DependencyNode: 依赖图节点
- IndicatorDependencyGraph: 依赖图
- DependencyValidator: 依赖验证器

Version: 1.0.0
Author: MyStocks Project
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import networkx as nx
import hashlib
import json
import logging


logger = logging.getLogger(__name__)


class NodeState(str, Enum):
    """节点状态"""

    PENDING = "pending"  # 待计算
    COMPUTING = "computing"  # 计算中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败


@dataclass
class DependencyNode:
    """
    依赖图节点

    表示一个需要计算的指标及其参数配置
    """

    abbreviation: str
    params: Dict[str, Any] = field(default_factory=dict)
    state: NodeState = NodeState.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    computation_time_ms: float = 0.0
    from_cache: bool = False

    @property
    def node_id(self) -> str:
        """生成唯一节点ID"""
        if not self.params:
            return self.abbreviation
        param_str = "_".join(f"{k}-{v}" for k, v in sorted(self.params.items()))
        return f"{self.abbreviation}[{param_str}]"

    def add_dependency(self, dep_node_id: str):
        """添加依赖"""
        if dep_node_id not in self.dependencies:
            self.dependencies.append(dep_node_id)

    def add_dependent(self, dep_node_id: str):
        """添加被依赖者"""
        if dep_node_id not in self.dependents:
            self.dependents.append(dep_node_id)


@dataclass
class DependencyEdge:
    """依赖边"""

    from_node: str
    to_node: str
    edge_type: str = "data"  # data: 数据依赖, sequential: 顺序依赖


class IndicatorDependencyGraph:
    """
    指标依赖关系图

    功能:
    - 使用有向无环图(DAG)表示指标间依赖关系
    - 支持循环依赖检测
    - 拓扑排序确定计算顺序
    - 支持增量计算和缓存验证
    """

    def __init__(self):
        # 使用 NetworkX 构建有向图
        self._graph = nx.DiGraph()
        self._reverse_graph = nx.DiGraph()  # 反向图（被依赖 -> 依赖）
        self._nodes: Dict[str, DependencyNode] = {}
        self._edges: List[DependencyEdge] = []
        self._computed_results: Dict[str, Any] = {}

    def add_indicator(
        self,
        abbreviation: str,
        params: Dict[str, Any] = None,
        dependencies: List[str] = None,
        data_requirements: List[str] = None,
    ) -> str:
        """
        添加指标到依赖图

        Args:
            abbreviation: 指标缩写
            params: 参数字典
            dependencies: 依赖的其他指标缩写列表
            data_requirements: 需要的基础数据字段

        Returns:
            节点ID
        """
        params = params or {}
        dependencies = dependencies or []
        data_requirements = data_requirements or ["close"]

        # 创建节点
        node = DependencyNode(abbreviation=abbreviation, params=params, dependencies=[], dependents=[])
        node_id = node.node_id

        # 如果节点已存在，更新信息
        if node_id in self._nodes:
            logger.debug(f"节点 {node_id} 已存在，更新依赖")
            existing_node = self._nodes[node_id]
            for dep in dependencies:
                dep_id = self._get_node_id_with_params(dep, {})
                if dep_id not in existing_node.dependencies:
                    existing_node.add_dependency(dep_id)
            return node_id

        # 添加节点到图
        self._graph.add_node(node_id, abbreviation=abbreviation, params=params)
        self._nodes[node_id] = node

        # 添加依赖边
        for dep in dependencies:
            dep_id = self._get_node_id_with_params(dep, {})
            self._graph.add_edge(dep_id, node_id, edge_type="data")
            node.add_dependency(dep_id)

            # 反向图：被依赖者记录依赖者
            if dep_id not in self._reverse_graph:
                self._reverse_graph.add_node(dep_id)
            self._reverse_graph.add_edge(node_id, dep_id, edge_type="reverse")

            self._edges.append(DependencyEdge(from_node=dep_id, to_node=node_id))

        logger.debug(f"添加节点: {node_id}, 依赖: {dependencies}")
        return node_id

    def _get_node_id_with_params(self, abbreviation: str, default_params: Dict) -> str:
        """根据缩写获取节点ID（使用默认参数）"""
        if abbreviation in self._nodes:
            return self._nodes[abbreviation].node_id
        # 如果不存在，创建临时ID
        if not default_params:
            return abbreviation
        param_str = "_".join(f"{k}-{v}" for k, v in sorted(default_params.items()))
        return f"{abbreviation}[{param_str}]"

    def add_dependency_edge(self, from_node: str, to_node: str, edge_type: str = "data") -> bool:
        """
        添加依赖边

        Args:
            from_node: 依赖方节点ID（先计算）
            to_node: 被依赖方节点ID（后计算）
            edge_type: 边类型

        Returns:
            是否添加成功
        """
        if from_node == to_node:
            logger.warning(f"不能添加自环依赖: {from_node}")
            return False

        if not self._graph.has_node(from_node):
            logger.warning(f"节点不存在: {from_node}")
            return False

        if not self._graph.has_node(to_node):
            logger.warning(f"节点不存在: {to_node}")
            return False

        self._graph.add_edge(from_node, to_node, edge_type=edge_type)
        self._edges.append(DependencyEdge(from_node=from_node, to_node=to_node, edge_type=edge_type))

        # 更新节点的依赖/被依赖关系
        if from_node in self._nodes:
            self._nodes[from_node].add_dependent(to_node)
        if to_node in self._nodes:
            self._nodes[to_node].add_dependency(from_node)

        return True

    def detect_cycles(self) -> Optional[List[List[str]]]:
        """
        检测循环依赖

        Returns:
            如果存在循环，返回循环路径列表；否则返回None
        """
        try:
            cycles = list(nx.simple_cycles(self._graph))
            if cycles:
                cycle_strs = []
                for cycle in cycles:
                    cycle_str = " -> ".join(cycle) + f" -> {cycle[0]}"
                    cycle_strs.append(cycle_str)
                logger.warning(f"检测到循环依赖: {cycle_strs}")
                return cycles
            return None
        except nx.NetworkXNoCycle:
            return None

    def has_cycle(self) -> bool:
        """检查是否存在循环依赖"""
        return nx.is_directed_acyclic_graph(self._graph) is False

    def get_in_degree(self, node_id: str) -> int:
        """获取节点的入度（被依赖数量）"""
        return self._graph.in_degree(node_id)

    def get_out_degree(self, node_id: str) -> int:
        """获取节点的出度（依赖数量）"""
        return self._graph.out_degree(node_id)

    def get_ready_nodes(self) -> List[str]:
        """
        获取所有无依赖的节点（可以立即计算的）

        Returns:
            可立即计算的节点ID列表
        """
        ready = []
        for node_id in self._graph.nodes():
            if self._graph.in_degree(node_id) == 0:
                ready.append(node_id)
        return ready

    def get_node(self, node_id: str) -> Optional[DependencyNode]:
        """获取节点"""
        return self._nodes.get(node_id)

    def get_all_nodes(self) -> Dict[str, DependencyNode]:
        """获取所有节点"""
        return self._nodes.copy()

    def get_node_id(self, abbreviation: str, params: Dict[str, Any]) -> str:
        """根据缩写和参数生成节点ID"""
        abbr_upper = abbreviation.upper()
        if abbr_upper in self._nodes:
            # 检查是否是同一个配置
            node = self._nodes[abbr_upper]
            if node.params == params:
                return node.node_id
        param_str = "_".join(f"{k}-{v}" for k, v in sorted(params.items()))
        return f"{abbr_upper}[{param_str}]"

    def topological_sort_kahn(self) -> Optional[List[str]]:
        """
        拓扑排序 - Kahn算法

        Returns:
            计算顺序列表（从无依赖到有依赖）
        """
        # 检测循环
        if self.has_cycle():
            logger.error("图中存在循环依赖，无法进行拓扑排序")
            return None

        # 复制图以避免修改原图
        graph = self._graph.copy()
        in_degree = {node: graph.in_degree(node) for node in graph.nodes()}

        # 初始化队列
        queue = deque([node for node in graph.nodes() if in_degree[node] == 0])
        result = []

        while queue:
            node = queue.popleft()
            result.append(node)

            # 减少邻居的入度
            for neighbor in graph.successors(node):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(graph.nodes()):
            logger.error("拓扑排序失败，可能存在循环")
            return None

        return result

    def topological_sort_dfs(self) -> Optional[List[str]]:
        """
        拓扑排序 - DFS算法

        Returns:
            计算顺序列表
        """
        visited = set()
        stack = set()
        result = []

        def dfs(node: str):
            if node in stack:
                logger.error(f"检测到循环: {node}")
                return
            if node in visited:
                return

            visited.add(node)
            stack.add(node)

            for neighbor in self._graph.successors(node):
                dfs(neighbor)

            stack.remove(node)
            result.append(node)

        for node in self._graph.nodes():
            if node not in visited:
                dfs(node)

        result.reverse()
        return result if len(result) == len(self._graph.nodes()) else None

    def get_calculation_order(self, indicators: List[Dict]) -> List[Dict]:
        """
        获取最优计算顺序

        Args:
            indicators: 指标列表 [{"abbreviation": "SMA", "params": {...}}, ...]

        Returns:
            按依赖排序的指标列表
        """
        # 清空图
        self._graph.clear()
        self._nodes.clear()
        self._edges.clear()

        # 注册所有指标
        for ind in indicators:
            self.add_indicator(
                ind["abbreviation"],
                ind.get("params", {}),
                ind.get("dependencies", []),
                ind.get("data_requirements", ["close"]),
            )

        # 检测循环
        cycles = self.detect_cycles()
        if cycles:
            raise ValueError(f"检测到循环依赖: {cycles}")

        # 拓扑排序
        order = self.topological_sort_kahn()
        if order is None:
            raise ValueError("无法确定计算顺序")

        # 返回排序后的指标配置
        result = []
        for node_id in order:
            node = self._nodes.get(node_id)
            if node:
                result.append(
                    {
                        "abbreviation": node.abbreviation,
                        "params": node.params,
                        "node_id": node_id,
                        "dependencies": node.dependencies.copy(),
                        "dependents": node.dependents.copy(),
                    }
                )
        return result

    def mark_computed(self, node_id: str, result: Any, computation_time_ms: float = 0.0, from_cache: bool = False):
        """标记节点已计算"""
        if node_id in self._nodes:
            node = self._nodes[node_id]
            node.state = NodeState.COMPLETED
            node.result = result
            node.computation_time_ms = computation_time_ms
            node.from_cache = from_cache

        self._computed_results[node_id] = result

        # 移除以该节点为起点的边
        successors = list(self._graph.successors(node_id))
        self._graph.remove_edges_from([(node_id, s) for s in successors])

    def mark_failed(self, node_id: str, error: str):
        """标记节点计算失败"""
        if node_id in self._nodes:
            node = self._nodes[node_id]
            node.state = NodeState.FAILED
            node.error = error

    def reset(self):
        """重置图状态"""
        for node in self._nodes.values():
            node.state = NodeState.PENDING
            node.result = None
            node.error = None
            node.computation_time_ms = 0.0
            node.from_cache = False
        self._computed_results.clear()

    def get_stats(self) -> Dict:
        """获取图统计信息"""
        return {
            "total_nodes": len(self._nodes),
            "total_edges": len(self._edges),
            "has_cycle": self.has_cycle(),
            "ready_nodes": len(self.get_ready_nodes()),
            "computed_results": len(self._computed_results),
            "nodes_by_state": {
                state.value: sum(1 for n in self._nodes.values() if n.state == state) for state in NodeState
            },
        }

    def export_graph(self) -> Dict:
        """导出图为字典"""
        return {
            "nodes": {
                node_id: {
                    "abbreviation": node.abbreviation,
                    "params": node.params,
                    "state": node.state.value,
                    "dependencies": node.dependencies,
                    "dependents": node.dependents,
                }
                for node_id, node in self._nodes.items()
            },
            "edges": [{"from": edge.from_node, "to": edge.to_node, "type": edge.edge_type} for edge in self._edges],
            "stats": self.get_stats(),
        }


class DependencyValidator:
    """依赖关系验证器"""

    # 指标参数约束规则
    PARAMETER_RULES = {
        "MACD": {
            "fastperiod": {"max": "slowperiod", "message": "快线周期必须小于慢线周期"},
            "slowperiod": {"min": "fastperiod", "message": "慢线周期必须大于快线周期"},
        },
        "KDJ": {
            "k_period": {"min": 1, "max": 100},
            "d_period": {"min": 1, "max": 100},
        },
        "BBANDS": {
            "nbdevup": {"min": 0.1, "max": 5.0},
            "nbdevdn": {"min": 0.1, "max": 5.0},
        },
    }

    @classmethod
    def validate_macd_params(cls, params: Dict) -> Tuple[bool, str]:
        """验证MACD参数逻辑"""
        fast = params.get("fastperiod", 12)
        slow = params.get("slowperiod", 26)

        if fast >= slow:
            return False, f"MACD快线周期({fast})必须小于慢线周期({slow})"
        return True, ""

    @classmethod
    def validate_kdj_params(cls, params: Dict) -> Tuple[bool, str]:
        """验证KDJ参数逻辑"""
        k = params.get("k_period", 9)
        d = params.get("d_period", 3)

        if k <= d:
            return False, f"KDJ K周期({k})应大于D周期({d})"
        return True, ""

    @classmethod
    def validate_bbands_params(cls, params: Dict) -> Tuple[bool, str]:
        """验证布林带参数逻辑"""
        nbdevup = params.get("nbdevup", 2.0)
        nbdevdn = params.get("nbdevdn", 2.0)

        if nbdevup < 0 or nbdevdn < 0:
            return False, "标准差倍数不能为负数"
        return True, ""

    @classmethod
    def validate_indicator_params(cls, abbreviation: str, params: Dict) -> Tuple[bool, str]:
        """验证指标参数"""
        abbr_upper = abbreviation.upper()

        # MACD 验证
        if abbr_upper == "MACD":
            return cls.validate_macd_params(params)

        # KDJ 验证
        if abbr_upper == "KDJ":
            return cls.validate_kdj_params(params)

        # BBANDS 验证
        if abbr_upper == "BBANDS":
            return cls.validate_bbands_params(params)

        # 通用验证
        rules = cls.PARAMETER_RULES.get(abbr_upper, {})
        for param_name, rule in rules.items():
            if param_name in params:
                value = params[param_name]

                # 范围检查
                if "min" in rule and isinstance(rule["min"], (int, float)) and value < rule["min"]:
                    return False, f"{abbr_upper} {param_name} ({value}) 小于最小值 ({rule['min']})"
                if "max" in rule and isinstance(rule["max"], (int, float)) and value > rule["max"]:
                    return False, f"{abbr_upper} {param_name} ({value}) 大于最大值 ({rule['max']})"

                # 依赖检查
                if "max" in rule and isinstance(rule["max"], str):
                    dep_value = params.get(rule["max"], float("inf"))
                    if value >= dep_value:
                        return False, rule.get("message", f"{param_name} 必须小于 {rule['max']}")

        return True, ""

    @classmethod
    def validate_dependency_graph(cls, graph: IndicatorDependencyGraph) -> Tuple[bool, List[str]]:
        """
        验证整个依赖图

        Args:
            graph: 依赖图

        Returns:
            (是否有效, 错误列表)
        """
        errors = []

        # 检测循环
        if graph.has_cycle():
            errors.append("图中存在循环依赖")

        # 验证每个节点的参数
        for node_id, node in graph.get_all_nodes().items():
            is_valid, error_msg = cls.validate_indicator_params(node.abbreviation, node.params)
            if not is_valid:
                errors.append(f"节点 {node_id}: {error_msg}")

        return len(errors) == 0, errors


class IncrementalCalculator:
    """
    增量计算器

    功能:
    - 检测数据是否新增
    - 复用缓存结果
    - 增量计算新数据
    """

    def __init__(self, graph: IndicatorDependencyGraph):
        self._graph = graph
        self._cache: Dict[str, Any] = {}
        self._cache_hash: Dict[str, str] = {}

    def set_cache(self, node_id: str, result: Any):
        """设置缓存"""
        self._cache[node_id] = result
        self._cache_hash[node_id] = self._compute_hash(result)

    def _compute_hash(self, data: Any) -> str:
        """计算数据哈希"""
        try:
            if hasattr(data, "__len__"):
                arr = data[-10:]  # 只用末尾10个点验证
                data_str = json.dumps(arr.tolist() if hasattr(arr, "tolist") else list(arr))
            else:
                data_str = str(data)
            return hashlib.md5(data_str.encode()).hexdigest()
        except Exception:
            return hashlib.md5(str(id(data)).encode()).hexdigest()

    def validate_cache(self, node_id: str, new_data: Any) -> Tuple[bool, bool]:
        """
        验证缓存是否有效

        Returns:
            (是否有效, 是否需要增量更新)
        """
        if node_id not in self._cache:
            return False, False

        old_hash = self._cache_hash[node_id]
        new_hash = self._compute_hash(new_data)

        if old_hash == new_hash:
            return True, False  # 缓存有效，无需更新

        # 检查是否是增量数据（末尾一致）
        if self._is_incremental_extension(self._cache[node_id], new_data):
            return True, True  # 缓存有效，需要增量更新

        return False, False  # 缓存无效

    def _is_incremental_extension(self, old_data: Any, new_data: Any) -> bool:
        """检查新数据是否是旧数据的增量扩展"""
        try:
            if not hasattr(old_data, "__len__") or not hasattr(new_data, "__len__"):
                return False

            if len(new_data) <= len(old_data):
                return False

            old_arr = old_data[-10:] if len(old_data) > 10 else old_data
            new_arr = new_data[-10:] if len(new_data) > 10 else new_data

            # 比较末尾数据
            old_list = old_arr.tolist() if hasattr(old_arr, "tolist") else list(old_arr)
            new_list = new_arr.tolist() if hasattr(new_arr, "tolist") else list(new_arr)

            return old_list == new_list[-len(old_list) :]
        except Exception:
            return False

    def get_cached_result(self, node_id: str) -> Optional[Any]:
        """获取缓存结果"""
        return self._cache.get(node_id)

    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
        self._cache_hash.clear()
