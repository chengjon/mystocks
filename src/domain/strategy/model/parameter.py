"""
Parameter Entity
参数实体

表示策略的可配置参数。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from ...shared.event import DomainEvent


@dataclass
class Parameter:
    """
    参数实体

    职责：
    - 管理策略的可配置参数
    - 提供参数验证和类型检查
    - 追踪参数变更历史

    特性：
    - 参数类型安全
    - 参数范围验证
    - 参数变更记录
    """

    name: str
    value: Any
    parameter_type: str  # string, int, float, bool, list, dict
    id: str = field(default_factory=lambda: str(uuid4()))
    description: str = ""
    default_value: Any = None
    min_value: Optional[float] = None  # 对于数值类型
    max_value: Optional[float] = None  # 对于数值类型
    allowed_values: Optional[list] = None  # 对于枚举类型
    is_required: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # 领域事件集合
    _domain_events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self):
        """验证参数"""
        if not self.name:
            raise ValueError("Parameter name cannot be empty")

        if self.is_required and self.value is None:
            raise ValueError(f"Required parameter '{self.name}' cannot have None value")

        # 验证参数类型
        self._validate_type()

        # 验证参数值
        self._validate_value()

    def _validate_type(self):
        """验证参数类型"""
        type_map = {
            "string": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
        }

        expected_type = type_map.get(self.parameter_type)
        if expected_type and not isinstance(self.value, expected_type):
            raise TypeError(
                f"Parameter '{self.name}' expects {self.parameter_type}, "
                f"got {type(self.value).__name__}"
            )

    def _validate_value(self):
        """验证参数值"""
        if self.parameter_type in ["int", "float"] and self.value is not None:
            value = float(self.value)

            if self.min_value is not None and value < self.min_value:
                raise ValueError(
                    f"Parameter '{self.name}' value {value} < min_value {self.min_value}"
                )

            if self.max_value is not None and value > self.max_value:
                raise ValueError(
                    f"Parameter '{self.name}' value {value} > max_value {self.max_value}"
                )

        if self.allowed_values and self.value not in self.allowed_values:
            raise ValueError(
                f"Parameter '{self.name}' value {self.value} not in allowed values {self.allowed_values}"
            )

    def update(self, new_value: Any) -> None:
        """
        更新参数值

        Args:
            new_value: 新值
        """
        old_value = self.value
        self.value = new_value
        self.updated_at = datetime.now()

        # 重新验证
        self._validate_type()
        self._validate_value()

        # 如果值发生变化，添加领域事件
        if old_value != new_value:
            self._add_domain_event(
                ParameterChangedEvent(
                    parameter_id=self.id,
                    parameter_name=self.name,
                    old_value=old_value,
                    new_value=new_value,
                )
            )

    def _add_domain_event(self, event: DomainEvent) -> None:
        """添加领域事件"""
        self._domain_events.append(event)

    def get_domain_events(self) -> list[DomainEvent]:
        """获取并清空领域事件"""
        events = self._domain_events
        self._domain_events = []
        return events

    @classmethod
    def create_int_parameter(
        cls,
        name: str,
        value: int,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        description: str = "",
        default_value: Optional[int] = None,
    ) -> "Parameter":
        """创建整数参数"""
        return cls(
            name=name,
            value=value,
            parameter_type="int",
            description=description,
            default_value=default_value,
            min_value=float(min_value) if min_value is not None else None,
            max_value=float(max_value) if max_value is not None else None,
        )

    @classmethod
    def create_float_parameter(
        cls,
        name: str,
        value: float,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        description: str = "",
        default_value: Optional[float] = None,
    ) -> "Parameter":
        """创建浮点数参数"""
        return cls(
            name=name,
            value=value,
            parameter_type="float",
            description=description,
            default_value=default_value,
            min_value=min_value,
            max_value=max_value,
        )

    @classmethod
    def create_string_parameter(
        cls,
        name: str,
        value: str,
        description: str = "",
        default_value: Optional[str] = None,
    ) -> "Parameter":
        """创建字符串参数"""
        return cls(
            name=name,
            value=value,
            parameter_type="string",
            description=description,
            default_value=default_value,
        )

    def __str__(self) -> str:
        return f"Parameter(name={self.name}, type={self.parameter_type}, value={self.value})"


@dataclass
class ParameterChangedEvent:
    """参数变更事件"""
    parameter_id: str
    parameter_name: str
    old_value: Any
    new_value: Any
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_on: datetime = field(default_factory=datetime.now)

    def event_name(self) -> str:
        return "ParameterChangedEvent"
