"""
Indicators Module
=================

技术指标管理模块，提供指标元数据、注册表、计算接口、依赖管理等功能。

Classes:
    IndicatorCategory: 指标分类枚举
    PanelType: 显示面板类型
    ComplexityLevel: 计算复杂度等级
    ParameterType: 参数类型
    DataField: 基础数据字段
    ParameterConstraint: 参数约束
    IndicatorParameter: 指标参数
    IndicatorOutput: 指标输出
    IndicatorMetadata: 指标元数据
    IndicatorTemplate: 指标模板
    IndicatorConfig: 完整配置
    IndicatorRegistry: 指标注册中心
    OHLCVData: OHLCV数据结构
    IndicatorResult: 计算结果
    IndicatorInterface: 指标计算接口
    IndicatorDependencyGraph: 依赖关系图
    SmartScheduler: 智能调度器

Version: 1.0.0
Author: MyStocks Project
"""

from .indicator_metadata import (
    IndicatorCategory,
    PanelType,
    ComplexityLevel,
    ParameterType,
    DataField,
    ParameterConstraint,
    IndicatorParameter,
    IndicatorOutput,
    IndicatorMetadata,
    IndicatorTemplate,
    IndicatorConfig,
)

from .indicator_registry import (
    IndicatorRegistry,
    RegistryStats,
    get_indicator_registry,
    reset_indicator_registry,
)

from .indicator_interface import (
    OHLCVData,
    IndicatorResult,
    IndicatorInterface,
    IndicatorError,
    InsufficientDataError,
    ParameterValidationError,
    CalculationStatus,
    IndicatorPluginFactory,
)

from .dependency_graph import (
    IndicatorDependencyGraph,
    DependencyNode,
    DependencyEdge,
    NodeState,
    DependencyValidator,
    IncrementalCalculator,
)

from .smart_scheduler import (
    SmartScheduler,
    ScheduleResult,
    ScheduleStats,
    CalculationMode,
    PerformanceMonitor,
    create_scheduler,
)

__all__ = [
    # Enums
    "IndicatorCategory",
    "PanelType",
    "ComplexityLevel",
    "ParameterType",
    "DataField",
    "NodeState",
    "CalculationMode",
    # Data classes
    "ParameterConstraint",
    "IndicatorParameter",
    "IndicatorOutput",
    "IndicatorMetadata",
    "IndicatorTemplate",
    "IndicatorConfig",
    "DependencyNode",
    "DependencyEdge",
    "ScheduleResult",
    "ScheduleStats",
    # Registry
    "IndicatorRegistry",
    "RegistryStats",
    "get_indicator_registry",
    "reset_indicator_registry",
    # Interface
    "OHLCVData",
    "IndicatorResult",
    "IndicatorInterface",
    "IndicatorError",
    "InsufficientDataError",
    "ParameterValidationError",
    "CalculationStatus",
    "IndicatorPluginFactory",
    # Dependency & Scheduling
    "IndicatorDependencyGraph",
    "DependencyValidator",
    "IncrementalCalculator",
    "SmartScheduler",
    "PerformanceMonitor",
    "create_scheduler",
]

__version__ = "1.0.0"
