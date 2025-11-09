"""
数据模型定义 - MyStocks Function Classification Manual

定义所有代码分析和手册生成使用的数据结构。

作者: MyStocks Team
日期: 2025-10-19
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum
from datetime import datetime


class CategoryEnum(Enum):
    """功能类别枚举"""

    CORE = "core"  # 核心功能
    AUXILIARY = "auxiliary"  # 辅助功能
    INFRASTRUCTURE = "infrastructure"  # 基础设施功能
    MONITORING = "monitoring"  # 监控功能
    UTILITY = "utility"  # 工具功能
    UNKNOWN = "unknown"  # 未分类


class SeverityEnum(Enum):
    """严重性级别枚举"""

    CRITICAL = "critical"  # 关键 (>=95% 相似度)
    HIGH = "high"  # 高 (80-94% 相似度)
    MEDIUM = "medium"  # 中 (60-79% 相似度)
    LOW = "low"  # 低 (40-59% 相似度)


class PriorityEnum(Enum):
    """优先级枚举"""

    P0 = "p0"  # 紧急
    P1 = "p1"  # 高优先级
    P2 = "p2"  # 中优先级
    P3 = "p3"  # 低优先级


@dataclass
class ParameterMetadata:
    """函数参数元数据"""

    name: str
    type_annotation: Optional[str] = None
    default_value: Optional[str] = None
    is_required: bool = True


@dataclass
class FunctionMetadata:
    """函数元数据"""

    name: str
    line_number: int
    parameters: List[ParameterMetadata] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    is_async: bool = False
    decorators: List[str] = field(default_factory=list)
    body_lines: int = 0
    complexity: int = 0  # 圈复杂度


@dataclass
class ClassMetadata:
    """类元数据"""

    name: str
    line_number: int
    base_classes: List[str] = field(default_factory=list)
    methods: List[FunctionMetadata] = field(default_factory=list)
    docstring: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    is_abstract: bool = False


@dataclass
class ModuleMetadata:
    """模块元数据"""

    file_path: str
    module_name: str
    category: CategoryEnum = CategoryEnum.UNKNOWN
    classes: List[ClassMetadata] = field(default_factory=list)
    functions: List[FunctionMetadata] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    lines_of_code: int = 0
    blank_lines: int = 0
    comment_lines: int = 0
    last_modified: Optional[datetime] = None


@dataclass
class CodeBlock:
    """代码块（用于相似性比较）"""

    file_path: str
    start_line: int
    end_line: int
    content: str
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    tokens: List[str] = field(default_factory=list)
    ast_hash: Optional[str] = None


@dataclass
class DuplicationCase:
    """代码重复案例"""

    id: str
    severity: SeverityEnum
    blocks: List[CodeBlock] = field(default_factory=list)
    token_similarity: float = 0.0
    ast_similarity: float = 0.0
    description: str = ""
    merge_suggestion: str = ""
    affected_files: List[str] = field(default_factory=list)


@dataclass
class Dependency:
    """模块依赖关系"""

    source_module: str
    target_module: str
    import_type: str  # "import", "from_import", "dynamic"
    symbols: List[str] = field(default_factory=list)


@dataclass
class OptimizationOpportunity:
    """优化机会"""

    id: str
    title: str
    category: str  # "performance", "architecture", "code_quality"
    priority: PriorityEnum
    current_state: str
    proposed_change: str
    expected_impact: str
    effort_estimate: str  # "1-2 hours", "1 day", "2-3 days", etc.
    affected_modules: List[str] = field(default_factory=list)
    related_duplications: List[str] = field(default_factory=list)


@dataclass
class MergeRecommendation:
    """合并建议"""

    id: str
    title: str
    modules_to_merge: List[str] = field(default_factory=list)
    common_functionality: str = ""
    merge_strategy: str = ""
    new_module_name: Optional[str] = None
    migration_steps: List[str] = field(default_factory=list)
    risk_level: str = "medium"  # "low", "medium", "high"
    effort_estimate: str = ""


@dataclass
class DataFlow:
    """数据流"""

    id: str
    name: str
    description: str
    steps: List[Dict[str, str]] = field(default_factory=list)
    # steps format: [{"module": "...", "function": "...", "action": "..."}]
    data_classification: Optional[str] = None  # From 5-tier system
    database_target: Optional[str] = None


@dataclass
class ArchitectureIssue:
    """架构问题"""

    id: str
    type: str  # "circular_dependency", "god_object", "tight_coupling", etc.
    severity: SeverityEnum
    description: str
    affected_modules: List[str] = field(default_factory=list)
    recommendation: str = ""
    refactoring_guide: str = ""


@dataclass
class ManualMetadata:
    """手册元数据"""

    version: str
    generation_date: datetime
    total_modules: int = 0
    total_classes: int = 0
    total_functions: int = 0
    total_lines: int = 0
    duplication_count: int = 0
    optimization_count: int = 0

    # 按类别统计
    category_stats: Dict[str, Dict[str, int]] = field(default_factory=dict)
    # format: {"core": {"modules": 10, "functions": 50, "lines": 1000}}

    # 代码质量指标
    avg_function_complexity: float = 0.0
    max_function_complexity: int = 0
    test_coverage: Optional[float] = None

    # 重复统计
    critical_duplications: int = 0
    high_duplications: int = 0
    medium_duplications: int = 0
    low_duplications: int = 0


@dataclass
class ModuleInventory:
    """模块清单"""

    modules: List[ModuleMetadata] = field(default_factory=list)
    dependencies: List[Dependency] = field(default_factory=list)
    metadata: Optional[ManualMetadata] = None

    def get_modules_by_category(self, category: CategoryEnum) -> List[ModuleMetadata]:
        """按类别获取模块列表"""
        return [m for m in self.modules if m.category == category]

    def get_module_by_path(self, file_path: str) -> Optional[ModuleMetadata]:
        """根据文件路径获取模块"""
        for module in self.modules:
            if module.file_path == file_path:
                return module
        return None

    def get_total_functions(self) -> int:
        """获取总函数数量"""
        total = 0
        for module in self.modules:
            total += len(module.functions)
            for cls in module.classes:
                total += len(cls.methods)
        return total

    def get_total_classes(self) -> int:
        """获取总类数量"""
        return sum(len(m.classes) for m in self.modules)


@dataclass
class DuplicationIndex:
    """重复索引"""

    duplications: List[DuplicationCase] = field(default_factory=list)
    total_cases: int = 0

    # 按严重性分组
    critical: List[DuplicationCase] = field(default_factory=list)
    high: List[DuplicationCase] = field(default_factory=list)
    medium: List[DuplicationCase] = field(default_factory=list)
    low: List[DuplicationCase] = field(default_factory=list)

    def add_duplication(self, dup: DuplicationCase):
        """添加重复案例并自动分类"""
        self.duplications.append(dup)
        self.total_cases += 1

        if dup.severity == SeverityEnum.CRITICAL:
            self.critical.append(dup)
        elif dup.severity == SeverityEnum.HIGH:
            self.high.append(dup)
        elif dup.severity == SeverityEnum.MEDIUM:
            self.medium.append(dup)
        elif dup.severity == SeverityEnum.LOW:
            self.low.append(dup)

    def get_by_severity(self, severity: SeverityEnum) -> List[DuplicationCase]:
        """按严重性获取重复案例"""
        if severity == SeverityEnum.CRITICAL:
            return self.critical
        elif severity == SeverityEnum.HIGH:
            return self.high
        elif severity == SeverityEnum.MEDIUM:
            return self.medium
        elif severity == SeverityEnum.LOW:
            return self.low
        return []


@dataclass
class OptimizationRoadmap:
    """优化路线图"""

    opportunities: List[OptimizationOpportunity] = field(default_factory=list)

    # 按类别分组
    performance: List[OptimizationOpportunity] = field(default_factory=list)
    architecture: List[OptimizationOpportunity] = field(default_factory=list)
    code_quality: List[OptimizationOpportunity] = field(default_factory=list)

    def add_opportunity(self, opp: OptimizationOpportunity):
        """添加优化机会并自动分类"""
        self.opportunities.append(opp)

        if opp.category == "performance":
            self.performance.append(opp)
        elif opp.category == "architecture":
            self.architecture.append(opp)
        elif opp.category == "code_quality":
            self.code_quality.append(opp)

    def get_by_priority(self, priority: PriorityEnum) -> List[OptimizationOpportunity]:
        """按优先级获取优化机会"""
        return [o for o in self.opportunities if o.priority == priority]

    def get_quick_wins(self) -> List[OptimizationOpportunity]:
        """获取快速胜利项（高优先级 + 低工作量）"""
        quick_wins = []
        for opp in self.opportunities:
            if opp.priority in [PriorityEnum.P0, PriorityEnum.P1]:
                if any(
                    keyword in opp.effort_estimate.lower()
                    for keyword in ["hour", "小时", "1 day", "1天"]
                ):
                    quick_wins.append(opp)
        return quick_wins


@dataclass
class ConsolidationGuide:
    """合并指南"""

    recommendations: List[MergeRecommendation] = field(default_factory=list)

    def add_recommendation(self, rec: MergeRecommendation):
        """添加合并建议"""
        self.recommendations.append(rec)

    def get_by_risk_level(self, risk_level: str) -> List[MergeRecommendation]:
        """按风险级别获取建议"""
        return [r for r in self.recommendations if r.risk_level == risk_level]

    def get_high_impact(self) -> List[MergeRecommendation]:
        """获取高影响合并建议（合并 3+ 模块）"""
        return [r for r in self.recommendations if len(r.modules_to_merge) >= 3]


# 辅助函数


def severity_from_similarity(token_sim: float, ast_sim: float) -> SeverityEnum:
    """根据相似度计算严重性级别"""
    if token_sim >= 0.95 and ast_sim >= 0.90:
        return SeverityEnum.CRITICAL
    elif token_sim >= 0.80 and ast_sim >= 0.70:
        return SeverityEnum.HIGH
    elif token_sim >= 0.60 and ast_sim >= 0.50:
        return SeverityEnum.MEDIUM
    else:
        return SeverityEnum.LOW


def categorize_module_by_path(file_path: str) -> CategoryEnum:
    """根据文件路径推断模块类别（初步分类）"""
    path_lower = file_path.lower()

    # 核心功能特征
    if any(
        keyword in path_lower
        for keyword in ["unified_manager", "core.py", "data_access", "main.py"]
    ):
        return CategoryEnum.CORE

    # 辅助功能特征
    if any(
        keyword in path_lower
        for keyword in ["adapter", "factory", "strategy", "backtest"]
    ):
        return CategoryEnum.AUXILIARY

    # 基础设施特征
    if any(
        keyword in path_lower
        for keyword in ["db_manager", "database", "config", "model"]
    ):
        return CategoryEnum.INFRASTRUCTURE

    # 监控功能特征
    if any(
        keyword in path_lower
        for keyword in ["monitoring", "alert", "performance_monitor", "data_quality"]
    ):
        return CategoryEnum.MONITORING

    # 工具功能特征
    if any(
        keyword in path_lower
        for keyword in ["util", "helper", "decorator", "validation"]
    ):
        return CategoryEnum.UTILITY

    return CategoryEnum.UNKNOWN


def estimate_complexity(function_ast) -> int:
    """
    估算函数圈复杂度

    简化版本：计算决策点数量（if, for, while, try, except, and, or）
    """
    import ast

    complexity = 1  # 基础复杂度

    for node in ast.walk(function_ast):
        if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            complexity += len(node.values) - 1

    return complexity
