"""
Domain Event Base Class with Serialization
支持序列化的领域事件基类
"""
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from uuid import uuid4
from enum import Enum
from typing import Any, Dict, Type, TypeVar

T = TypeVar("T", bound="DomainEvent")

@dataclass(kw_only=True)
class DomainEvent:
    """
    领域事件基类
    """
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_on: datetime = field(default_factory=datetime.now)

    def event_name(self) -> str:
        return self.__class__.__name__

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典，处理 datetime 和 Enum
        """
        def custom_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, Enum):
                return obj.value
            if isinstance(obj, dict):
                return {k: custom_serializer(v) for k, v in obj.items()}
            if isinstance(obj, (list, tuple)):
                return [custom_serializer(i) for i in obj]
            return obj

        data = asdict(self)
        serializable_data = custom_serializer(data)
        serializable_data["event_name"] = self.event_name()
        return serializable_data

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """从字典还原"""
        if "occurred_on" in data and isinstance(data["occurred_on"], str):
            data["occurred_on"] = datetime.fromisoformat(data["occurred_on"])
        
        data.pop("event_name", None)
        
        # 获取字段列表
        fields_dict = cls.__dataclass_fields__
        filtered_data = {}
        
        for k, v in data.items():
            if k in fields_dict:
                # 尝试处理枚举还原 (如果字段定义中有枚举)
                field_type = fields_dict[k].type
                # 处理 Optional[EnumType]
                if hasattr(field_type, "__args__"): 
                    for arg in field_type.__args__:
                        if isinstance(arg, type) and issubclass(arg, Enum):
                            v = arg(v)
                            break
                elif isinstance(field_type, type) and issubclass(field_type, Enum):
                    v = field_type(v)
                
                filtered_data[k] = v
        
        return cls(**filtered_data)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())