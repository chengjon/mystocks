"""
数据映射器框架
提供统一的数据对象映射功能，解决手动数据转换的技术债务
"""

import logging
from typing import Any, Dict, List, Optional, TypeVar, Union, Callable
from datetime import datetime, date
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

T = TypeVar("T")


class FieldType(Enum):
    """字段类型枚举"""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    DATE = "date"
    JSON = "json"
    DECIMAL = "decimal"


@dataclass
class FieldMapping:
    """字段映射配置"""

    source_field: str  # 数据库字段名或索引
    target_field: str  # 目标对象属性名
    field_type: FieldType = FieldType.STRING
    required: bool = False
    default_value: Any = None
    transformer: Optional[Callable[[Any], Any]] = None
    validator: Optional[Callable[[Any], bool]] = None
    description: str = ""

    def __post_init__(self):
        """初始化后处理"""
        # 如果source_field是数字字符串，转换为整数
        if isinstance(self.source_field, str) and self.source_field.isdigit():
            self.source_field = int(self.source_field)


class TypeConverter:
    """类型转换器"""

    @staticmethod
    def convert_value(value: Any, field_type: FieldType, field_name: str = "") -> Any:
        """
        将数据库值转换为目标类型

        Args:
            value: 数据库中的原始值
            field_type: 目标字段类型
            field_name: 字段名（用于错误信息）

        Returns:
            转换后的值
        """
        if value is None:
            return None

        try:
            if field_type == FieldType.STRING:
                return str(value)
            elif field_type == FieldType.INTEGER:
                return int(value) if value != 0 and value != "" else 0
            elif field_type == FieldType.FLOAT:
                return float(value)
            elif field_type == FieldType.BOOLEAN:
                return bool(value)
            elif field_type == FieldType.DATETIME:
                if isinstance(value, datetime):
                    return value
                elif isinstance(value, date):
                    return datetime.combine(value, datetime.min.time())
                elif isinstance(value, str):
                    # 尝试解析字符串日期
                    return datetime.fromisoformat(value.replace("Z", "+00:00"))
                else:
                    return datetime(value)
            elif field_type == FieldType.DATE:
                if isinstance(value, date):
                    return value
                elif isinstance(value, datetime):
                    return value.date()
                elif isinstance(value, str):
                    return date.fromisoformat(value.split("T")[0])
                else:
                    return date(value)
            elif field_type == FieldType.JSON:
                if isinstance(value, (dict, list)):
                    return value
                elif isinstance(value, str):
                    return json.loads(value)
                else:
                    return value
            else:
                return value

        except (ValueError, TypeError) as e:
            logger.warning("类型转换失败 - 字段: %s, 值: %s, 类型: %s, 错误: %s", field_name, value, field_type, e)
            return None


class ResultSetMapper:
    """结果集映射器"""

    def __init__(self, field_mappings: List[FieldMapping]):
        """
        初始化结果集映射器

        Args:
            field_mappings: 字段映射配置列表
        """
        self.field_mappings = field_mappings
        self._build_mapping_cache()

    def _build_mapping_cache(self):
        """构建映射缓存"""
        self._index_mappings = {}
        self._name_mappings = {}

        for mapping in self.field_mappings:
            if isinstance(mapping.source_field, int):
                self._index_mappings[mapping.source_field] = mapping
            else:
                self._name_mappings[mapping.source_field] = mapping

    def map_row(self, row: Union[List, Dict[str, Any]]) -> Dict[str, Any]:
        """
        映射单行数据

        Args:
            row: 数据库行数据（列表或字典）

        Returns:
            映射后的字典
        """
        result = {}

        try:
            # 处理列表类型的行数据
            if isinstance(row, (list, tuple)):
                for index, mapping in self._index_mappings.items():
                    if index < len(row):
                        value = row[index]
                        mapped_value = self._map_field(value, mapping)
                        if mapped_value is not None or mapping.default_value is not None:
                            result[mapping.target_field] = mapped_value
                    elif mapping.required:
                        raise ValueError(f"必需字段 {mapping.target_field} 缺失")

            # 处理字典类型的行数据
            elif isinstance(row, dict):
                for source_name, mapping in self._name_mappings.items():
                    if source_name in row:
                        value = row[source_name]
                        mapped_value = self._map_field(value, mapping)
                        if mapped_value is not None or mapping.default_value is not None:
                            result[mapping.target_field] = mapped_value
                    elif mapping.required:
                        raise ValueError(f"必需字段 {mapping.target_field} 缺失")

            # 应用默认值
            for mapping in self.field_mappings:
                if mapping.target_field not in result and mapping.default_value is not None:
                    result[mapping.target_field] = mapping.default_value

            return result

        except Exception as e:
            logger.error("行映射失败: %s, 数据: %s", e, row)
            raise

    def _map_field(self, value: Any, mapping: FieldMapping) -> Any:
        """
        映射单个字段

        Args:
            value: 原始值
            mapping: 字段映射配置

        Returns:
            映射后的值
        """
        # 应用自定义转换器
        if mapping.transformer:
            try:
                value = mapping.transformer(value)
            except Exception as e:
                logger.warning("自定义转换器失败 - 字段: %s, 错误: %s", mapping.target_field, e)
                return None

        # 应用类型转换
        mapped_value = TypeConverter.convert_value(value, mapping.field_type, mapping.target_field)

        # 应用验证器
        if mapping.validator and mapped_value is not None:
            try:
                if not mapping.validator(mapped_value):
                    logger.warning("字段验证失败 - 字段: %s, 值: %s", mapping.target_field, mapped_value)
                    return None
            except Exception as e:
                logger.warning("验证器执行失败 - 字段: %s, 错误: %s", mapping.target_field, e)
                return None

        return mapped_value

    def map_rows(self, rows: List[Union[List, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        批量映射多行数据

        Args:
            rows: 数据库行数据列表

        Returns:
            映射后的字典列表
        """
        results = []

        for row in rows:
            try:
                mapped_row = self.map_row(row)
                results.append(mapped_row)
            except Exception as e:
                logger.error("跳过无效行: %s", e)
                continue

        return results


class BaseDataMapper:
    """数据映射器基类"""

    def __init__(self, field_mappings: Optional[List[FieldMapping]] = None):
        """
        初始化数据映射器

        Args:
            field_mappings: 字段映射配置列表
        """
        self.field_mappings = field_mappings or []
        self.result_set_mapper = ResultSetMapper(self.field_mappings)

    def add_field_mapping(self, mapping: FieldMapping):
        """添加字段映射"""
        self.field_mappings.append(mapping)
        self.result_set_mapper = ResultSetMapper(self.field_mappings)

    def remove_field_mapping(self, target_field: str):
        """移除字段映射"""
        self.field_mappings = [m for m in self.field_mappings if m.target_field != target_field]
        self.result_set_mapper = ResultSetMapper(self.field_mappings)

    def map_row(self, row: Union[List, Dict[str, Any]]) -> Dict[str, Any]:
        """映射单行数据"""
        return self.result_set_mapper.map_row(row)

    def map_rows(self, rows: List[Union[List, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """批量映射数据"""
        return self.result_set_mapper.map_rows(rows)

    def get_field_names(self) -> List[str]:
        """获取所有目标字段名"""
        return [mapping.target_field for mapping in self.field_mappings]

    def get_required_fields(self) -> List[str]:
        """获取必需字段列表"""
        return [mapping.target_field for mapping in self.field_mappings if mapping.required]


class MapperRegistry:
    """映射器注册中心"""

    _instance = None
    _mappers: Dict[str, BaseDataMapper] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register_mapper(cls, name: str, mapper: BaseDataMapper):
        """注册映射器"""
        cls._mappers[name] = mapper
        logger.info("数据映射器已注册: %s", name)

    @classmethod
    def get_mapper(cls, name: str) -> Optional[BaseDataMapper]:
        """获取映射器"""
        return cls._mappers.get(name)

    @classmethod
    def list_mappers(cls) -> List[str]:
        """列出所有映射器"""
        return list(cls._mappers.keys())

    @classmethod
    def unregister_mapper(cls, name: str):
        """注销映射器"""
        if name in cls._mappers:
            del cls._mappers[name]
            logger.info("数据映射器已注销: %s", name)


# 预定义的常用转换器
class CommonTransformers:
    """常用转换器集合"""

    @staticmethod
    def datetime_formatter(fmt: str = "%Y-%m-%d %H:%M:%S"):
        """日期时间格式化转换器"""

        def transformer(value):
            if isinstance(value, datetime):
                return value.strftime(fmt)
            return value

        return transformer

    @staticmethod
    def safe_string():
        """安全字符串转换器"""

        def transformer(value):
            if value is None:
                return ""
            return str(value)

        return transformer

    @staticmethod
    def safe_int(default: int = 0):
        """安全整数转换器"""

        def transformer(value):
            if value is None or value == "":
                return default
            try:
                return int(value)
            except (ValueError, TypeError):
                return default

        return transformer

    @staticmethod
    def safe_float(default: float = 0.0):
        """安全浮点数转换器"""

        def transformer(value):
            if value is None or value == "":
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        return transformer

    @staticmethod
    def bool_converter(true_values: List[str] = None):
        """布尔值转换器"""
        if true_values is None:
            true_values = ["true", "1", "yes", "on", "t", "y"]

        def transformer(value):
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in true_values
            return bool(value)

        return transformer


# 预定义的常用验证器
class CommonValidators:
    """常用验证器集合"""

    @staticmethod
    def not_empty():
        """非空验证器"""

        def validator(value):
            return value is not None and value != ""

        return validator

    @staticmethod
    def positive_number():
        """正数验证器"""

        def validator(value):
            try:
                return float(value) > 0
            except (ValueError, TypeError):
                return False

        return validator

    @staticmethod
    def email_format():
        """邮箱格式验证器"""
        import re

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        def validator(value):
            if not isinstance(value, str):
                return False
            return re.match(email_pattern, value) is not None

        return validator

    @staticmethod
    def length_range(min_length: int = 0, max_length: int = None):
        """长度范围验证器"""

        def validator(value):
            if value is None:
                return min_length == 0
            str_value = str(value)
            length = len(str_value)
            if length < min_length:
                return False
            if max_length is not None and length > max_length:
                return False
            return True

        return validator
