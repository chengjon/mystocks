"""
Indicator Interface System
===========================

指标计算接口定义，提供标准化的指标计算基类。

功能:
- 指标计算接口抽象
- 数据验证
- 错误处理
- 插件化支持

Version: 1.0.0
Author: MyStocks Project
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class CalculationStatus(str, Enum):
    """计算状态"""

    SUCCESS = "success"
    ERROR = "error"
    INSUFFICIENT_DATA = "insufficient_data"
    SKIPPED = "skipped"


@dataclass
class OHLCVData:
    """OHLCV 数据结构"""

    open: np.ndarray
    high: np.ndarray
    low: np.ndarray
    close: np.ndarray
    volume: np.ndarray
    timestamps: Optional[np.ndarray] = None

    def __post_init__(self):
        """验证数据一致性"""
        n = len(self.close)
        if n == 0:
            return

        expected_len = n

        if len(self.open) != expected_len:
            raise ValueError(f"open 长度 {len(self.open)} 与 close 长度 {expected_len} 不一致")
        if len(self.high) != expected_len:
            raise ValueError(f"high 长度 {len(self.high)} 与 close 长度 {expected_len} 不一致")
        if len(self.low) != expected_len:
            raise ValueError(f"low 长度 {len(self.low)} 与 close 长度 {expected_len} 不一致")
        if len(self.volume) != expected_len:
            raise ValueError(f"volume 长度 {len(self.volume)} 与 close 长度 {expected_len} 不一致")

    @property
    def length(self) -> int:
        """数据长度"""
        return len(self.close)

    def slice(self, start: int, end: Optional[int] = None) -> "OHLCVData":
        """切片获取子数据"""
        if end is None:
            end = self.length
        return OHLCVData(
            open=self.open[start:end],
            high=self.high[start:end],
            low=self.low[start:end],
            close=self.close[start:end],
            volume=self.volume[start:end],
            timestamps=self.timestamps[start:end] if self.timestamps is not None else None,
        )


@dataclass
class IndicatorResult:
    """指标计算结果"""

    status: CalculationStatus
    abbreviation: str
    parameters: Dict[str, Any]
    values: Dict[str, np.ndarray]
    error_message: Optional[str] = None
    data_points: int = 0
    calculation_time_ms: float = 0.0

    @property
    def success(self) -> bool:
        """是否成功"""
        return self.status == CalculationStatus.SUCCESS

    def get_output(self, name: str) -> Optional[np.ndarray]:
        """获取指定输出"""
        return self.values.get(name)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "abbreviation": self.abbreviation,
            "status": self.status.value,
            "parameters": self.parameters,
            "values": {k: v.tolist() for k, v in self.values.items()},
            "error_message": self.error_message,
            "data_points": self.data_points,
            "calculation_time_ms": self.calculation_time_ms,
        }


class IndicatorError(Exception):
    """指标计算异常基类"""

    def __init__(self, message: str, abbreviation: str = "", details: Dict = None):
        self.message = message
        self.abbreviation = abbreviation
        self.details = details or {}
        super().__init__(self.message)


class InsufficientDataError(IndicatorError):
    """数据不足异常"""

    def __init__(self, abbreviation: str, required: int, actual: int, suggestion: str = ""):
        message = f"指标 {abbreviation} 需要至少 {required} 个数据点，实际只有 {actual} 个"
        if suggestion:
            message += f"。建议：{suggestion}"
        super().__init__(message, abbreviation, {"required": required, "actual": actual, "suggestion": suggestion})


class ParameterValidationError(IndicatorError):
    """参数验证异常"""

    def __init__(self, abbreviation: str, param_name: str, reason: str):
        message = f"指标 {abbreviation} 参数 {param_name} 验证失败：{reason}"
        super().__init__(message, abbreviation, {"parameter": param_name, "reason": reason})


class IndicatorInterface(ABC):
    """
    指标计算接口基类

    所有指标实现都应继承此类并实现抽象方法。
    提供了统一的数据验证、错误处理和结果格式化功能。
    """

    # 子类应覆盖这些属性
    ABBREVIATION: str = ""
    FULL_NAME: str = ""
    CHINESE_NAME: str = ""

    def __init__(self):
        """初始化"""
        self._registry = None

    @abstractmethod
    def calculate(self, data: OHLCVData, parameters: Dict[str, Any]) -> IndicatorResult:
        """
        计算指标

        Args:
            data: OHLCV数据
            parameters: 参数字典

        Returns:
            IndicatorResult: 计算结果
        """

    def validate_data(self, data: OHLCVData, min_required: int) -> None:
        """
        验证数据

        Args:
            data: OHLCV数据
            min_required: 最小需要的数据点数

        Raises:
            InsufficientDataError: 数据不足
        """
        if data.length < min_required:
            raise InsufficientDataError(
                self.ABBREVIATION, min_required, data.length, f"请将日期范围扩大至至少 {min_required} 个交易日"
            )

    def validate_parameters(self, parameters: Dict[str, Any], valid_params: Dict[str, Any]) -> None:
        """
        验证参数

        Args:
            parameters: 参数字典
            valid_params: 有效参数定义

        Raises:
            ParameterValidationError: 参数验证失败
        """
        for name, value in parameters.items():
            if name not in valid_params:
                continue

            param_def = valid_params[name]

            # 类型检查
            expected_type = param_def.get("type")
            if expected_type == "int" and not isinstance(value, int):
                raise ParameterValidationError(self.ABBREVIATION, name, f"应为整数，实际为 {type(value).__name__}")
            elif expected_type == "float" and not isinstance(value, (int, float)):
                raise ParameterValidationError(self.ABBREVIATION, name, f"应为数值，实际为 {type(value).__name__}")

            # 范围检查
            if "min" in param_def and value < param_def["min"]:
                raise ParameterValidationError(self.ABBREVIATION, name, f"值 {value} 小于最小值 {param_def['min']}")
            if "max" in param_def and value > param_def["max"]:
                raise ParameterValidationError(self.ABBREVIATION, name, f"值 {value} 大于最大值 {param_def['max']}")

    def _create_success_result(
        self, parameters: Dict[str, Any], values: Dict[str, np.ndarray], calculation_time_ms: float = 0.0
    ) -> IndicatorResult:
        """创建成功结果"""
        data_points = len(values.get("result", values.get(list(values.keys())[0])))
        return IndicatorResult(
            status=CalculationStatus.SUCCESS,
            abbreviation=self.ABBREVIATION,
            parameters=parameters,
            values=values,
            data_points=data_points,
            calculation_time_ms=calculation_time_ms,
        )

    def _create_error_result(self, parameters: Dict[str, Any], error_message: str) -> IndicatorResult:
        """创建错误结果"""
        return IndicatorResult(
            status=CalculationStatus.ERROR,
            abbreviation=self.ABBREVIATION,
            parameters=parameters,
            values={},
            error_message=error_message,
        )

    def _create_insufficient_data_result(
        self, parameters: Dict[str, Any], required: int, actual: int
    ) -> IndicatorResult:
        """创建数据不足结果"""
        return IndicatorResult(
            status=CalculationStatus.INSUFFICIENT_DATA,
            abbreviation=self.ABBREVIATION,
            parameters=parameters,
            values={},
            error_message=f"需要至少 {required} 个数据点，实际只有 {actual} 个",
            data_points=actual,
        )

    def get_parameter_defaults(self) -> Dict[str, Any]:
        """获取参数默认值（子类应覆盖）"""
        return {}

    def get_required_data_fields(self) -> List[str]:
        """获取需要的数据字段（子类应覆盖）"""
        return ["close"]


class IndicatorPluginFactory:
    """指标插件工厂"""

    _plugins: Dict[str, type] = {}

    @classmethod
    def register(cls, abbreviation: str, plugin_class: type):
        """注册指标插件"""
        cls._plugins[abbreviation.upper()] = plugin_class
        logger.info("注册指标插件: %(abbreviation)s")

    @classmethod
    def get_plugin(cls, abbreviation: str) -> Optional[type]:
        """获取指标插件类"""
        return cls._plugins.get(abbreviation.upper())

    @classmethod
    def create_instance(cls, abbreviation: str) -> Optional[IndicatorInterface]:
        """创建指标实例"""
        plugin_class = cls.get_plugin(abbreviation)
        if plugin_class:
            return plugin_class()
        return None

    @classmethod
    def list_plugins(cls) -> List[str]:
        """列出所有注册的插件"""
        return list(cls._plugins.keys())

    @classmethod
    def clear(cls):
        """清空所有插件"""
        cls._plugins.clear()
