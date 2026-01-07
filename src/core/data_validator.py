"""
数据验证器 - 入库前验证

验证规则:
1. 数据完整性检查（必需列）
2. 数据类型验证
3. 数据范围验证
4. 重复数据检测
5. 业务逻辑验证（如OHLC价格合理性）
6. 自定义验证规则

作者: Claude Code
版本: v1.0
创建日期: 2026-01-07
"""

from typing import Dict, Any, List
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """数据验证器"""

    def __init__(self):
        """初始化验证器"""
        self.rules: Dict[str, List[Dict]] = {}
        self.setup_default_rules()

    def register_rule(self, table_name: str, rule: Dict):
        """
        注册验证规则

        参数:
            table_name: 表名
            rule: 规则字典
        """
        if table_name not in self.rules:
            self.rules[table_name] = []
        self.rules[table_name].append(rule)
        logger.debug(f"已为表 {table_name} 注册规则: {rule.get('type')}")

    def validate(self, table_name: str, data: pd.DataFrame) -> Dict[str, Any]:
        """
        验证数据

        参数:
            table_name: 表名
            data: 要验证的数据

        返回:
            {
                "is_valid": bool,
                "errors": List[str],
                "warnings": List[str],
                "rule_results": List[Dict]
            }
        """
        result = {"is_valid": True, "errors": [], "warnings": [], "rule_results": []}

        if data is None or data.empty:
            result["is_valid"] = False
            result["errors"].append("数据为空")
            return result

        if table_name not in self.rules:
            # 没有规则，跳过验证
            logger.debug(f"表 {table_name} 没有注册的验证规则")
            return result

        # 按优先级排序并应用规则
        sorted_rules = sorted(
            self.rules[table_name], key=lambda x: self._get_priority_score(x.get("priority", "MEDIUM")), reverse=True
        )

        for rule in sorted_rules:
            rule_result = self._apply_rule(data, rule)
            result["rule_results"].append(rule_result)

            if not rule_result["is_valid"]:
                result["is_valid"] = False
                result["errors"].extend(rule_result["errors"])

            if rule_result["warnings"]:
                result["warnings"].extend(rule_result["warnings"])

        return result

    def _apply_rule(self, data: pd.DataFrame, rule: Dict) -> Dict[str, Any]:
        """
        应用单个验证规则

        参数:
            data: 数据
            rule: 规则

        返回:
            验证结果
        """
        rule_type = rule.get("type")

        validators = {
            "required_columns": self._check_required_columns,
            "column_types": self._check_column_types,
            "ohlc_logic": self._check_ohlc_logic,
            "no_duplicates": self._check_no_duplicates,
            "value_range": self._check_value_range,
            "custom": self._check_custom_rule,
        }

        validator = validators.get(rule_type)

        if validator:
            try:
                return validator(data, rule)
            except Exception as e:
                logger.error(f"应用规则 {rule_type} 失败: {e}")
                return {"is_valid": False, "errors": [f"规则 {rule_type} 执行失败: {str(e)}"], "warnings": []}
        else:
            logger.warning(f"未知的规则类型: {rule_type}")
            return {"is_valid": True, "errors": [], "warnings": []}

    def _check_required_columns(self, data: pd.DataFrame, rule: Dict) -> Dict[str, Any]:
        """检查必需列"""
        required = rule.get("columns", [])
        missing = [col for col in required if col not in data.columns]

        if missing:
            return {"is_valid": False, "errors": [f"缺少必需列: {', '.join(missing)}"], "warnings": []}

        return {"is_valid": True, "errors": [], "warnings": []}

    def _check_column_types(self, data: pd.DataFrame, rule: Dict) -> Dict[str, Any]:
        """检查列类型"""
        type_mappings = rule.get("mappings", {})
        errors = []
        warnings = []

        for col, expected_type in type_mappings.items():
            if col not in data.columns:
                warnings.append(f"列 '{col}' 不存在，跳过类型检查")
                continue

            actual_type = str(data[col].dtype)

            if expected_type == "numeric":
                if not pd.api.types.is_numeric_dtype(data[col]):
                    errors.append(f"列 '{col}' 应为数值类型，实际为 {actual_type}")
            elif expected_type == "datetime":
                if not pd.api.types.is_datetime64_any_dtype(data[col]):
                    errors.append(f"列 '{col}' 应为日期时间类型，实际为 {actual_type}")
            elif expected_type == "string":
                if not (pd.api.types.is_string_dtype(data[col]) or pd.api.types.is_object_dtype(data[col])):
                    errors.append(f"列 '{col}' 应为字符串类型，实际为 {actual_type}")

        return {"is_valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _check_ohlc_logic(self, data: pd.DataFrame, rule: Dict) -> Dict[str, Any]:
        """检查OHLC价格逻辑"""
        errors = []

        required_cols = ["open", "high", "low", "close"]
        if not all(col in data.columns for col in required_cols):
            return {"is_valid": True, "errors": [], "warnings": ["缺少OHLC列，跳过逻辑检查"]}

        # high >= max(open, close)
        invalid_high = data["high"] < data[["open", "close"]].max(axis=1)
        high_count = invalid_high.sum()

        if high_count > 0:
            errors.append(f"发现 {high_count} 条记录的high < max(open, close)")

        # low <= min(open, close)
        invalid_low = data["low"] > data[["open", "close"]].min(axis=1)
        low_count = invalid_low.sum()

        if low_count > 0:
            errors.append(f"发现 {low_count} 条记录的low > min(open, close)")

        # open, high, low, close > 0
        negative_prices = (data[["open", "high", "low", "close"]] <= 0).any(axis=1)
        negative_count = negative_prices.sum()

        if negative_count > 0:
            errors.append(f"发现 {negative_count} 条记录的价格 <= 0")

        # high >= low
        invalid_hl = data["high"] < data["low"]
        hl_count = invalid_hl.sum()

        if hl_count > 0:
            errors.append(f"发现 {hl_count} 条记录的high < low")

        return {"is_valid": len(errors) == 0, "errors": errors, "warnings": []}

    def _check_no_duplicates(self, data: pd.DataFrame, rule: Dict) -> Dict[str, Any]:
        """检查重复数据"""
        key_columns = rule.get("keys", [])

        if not key_columns:
            return {"is_valid": True, "errors": [], "warnings": ["未指定键列，跳过重复检查"]}

        missing_keys = [col for col in key_columns if col not in data.columns]

        if missing_keys:
            return {"is_valid": False, "errors": [f"重复检查的键列不存在: {', '.join(missing_keys)}"], "warnings": []}

        duplicates = data.duplicated(subset=key_columns)
        dup_count = duplicates.sum()

        if dup_count > 0:
            return {
                "is_valid": False,
                "errors": [f"发现 {dup_count} 条重复数据（基于列: {', '.join(key_columns)}）"],
                "warnings": [],
            }

        return {"is_valid": True, "errors": [], "warnings": []}

    def _check_value_range(self, data: pd.DataFrame, rule: Dict) -> Dict[str, Any]:
        """检查数值范围"""
        column = rule.get("column")
        min_val = rule.get("min")
        max_val = rule.get("max")

        if column not in data.columns:
            return {"is_valid": True, "errors": [], "warnings": [f"列 '{column}' 不存在，跳过范围检查"]}

        errors = []

        # 最小值检查
        if min_val is not None:
            out_of_min = data[column] < min_val
            min_count = out_of_min.sum()

            if min_count > 0:
                errors.append(f"列 '{column}' 有 {min_count} 条数据小于最小值 {min_val}")

        # 最大值检查
        if max_val is not None:
            out_of_max = data[column] > max_val
            max_count = out_of_max.sum()

            if max_count > 0:
                errors.append(f"列 '{column}' 有 {max_count} 条数据大于最大值 {max_val}")

        return {"is_valid": len(errors) == 0, "errors": errors, "warnings": []}

    def _check_custom_rule(self, data: pd.DataFrame, rule: Dict) -> Dict[str, Any]:
        """检查自定义规则"""
        validator_func = rule.get("validator")

        if not callable(validator_func):
            return {"is_valid": False, "errors": ["自定义规则必须提供validator函数"], "warnings": []}

        try:
            return validator_func(data)
        except Exception as e:
            return {"is_valid": False, "errors": [f"自定义规则执行失败: {str(e)}"], "warnings": []}

    def _get_priority_score(self, priority: str) -> int:
        """获取优先级分数"""
        scores = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        return scores.get(priority.upper(), 2)

    def setup_default_rules(self):
        """设置默认验证规则"""

        # K线数据规则
        self.register_rule(
            "stocks_daily",
            {
                "type": "required_columns",
                "columns": ["symbol", "trade_date", "open", "high", "low", "close", "volume"],
                "priority": "HIGH",
            },
        )

        self.register_rule(
            "stocks_daily",
            {
                "type": "column_types",
                "mappings": {
                    "open": "numeric",
                    "high": "numeric",
                    "low": "numeric",
                    "close": "numeric",
                    "volume": "numeric",
                    "trade_date": "datetime",
                },
                "priority": "HIGH",
            },
        )

        self.register_rule("stocks_daily", {"type": "ohlc_logic", "priority": "HIGH"})

        self.register_rule(
            "stocks_daily", {"type": "no_duplicates", "keys": ["symbol", "trade_date"], "priority": "HIGH"}
        )

        self.register_rule("stocks_daily", {"type": "value_range", "column": "volume", "min": 0, "priority": "MEDIUM"})

        # 周K线规则
        self.register_rule(
            "stocks_weekly",
            {
                "type": "required_columns",
                "columns": ["symbol", "trade_date", "open", "high", "low", "close", "volume"],
                "priority": "HIGH",
            },
        )

        self.register_rule("stocks_weekly", {"type": "ohlc_logic", "priority": "HIGH"})

        self.register_rule(
            "stocks_weekly", {"type": "no_duplicates", "keys": ["symbol", "trade_date"], "priority": "HIGH"}
        )

        # 股票基本信息规则
        self.register_rule(
            "stocks_basic", {"type": "required_columns", "columns": ["symbol", "name"], "priority": "HIGH"}
        )

        self.register_rule("stocks_basic", {"type": "no_duplicates", "keys": ["symbol"], "priority": "HIGH"})

        self.register_rule(
            "stocks_basic",
            {
                "type": "custom",
                "description": "行业数据不应等于股票名称",
                "priority": "MEDIUM",
                "validator": lambda df: {
                    "is_valid": not (df["industry"] == df["name"]).any(),
                    "errors": [],
                    "warnings": (
                        []
                        if "industry" not in df.columns or not (df["industry"] == df["name"]).any()
                        else ["发现industry等于name的脏数据"]
                    ),
                },
            },
        )

        # Tick数据规则
        self.register_rule(
            "stock_tick",
            {"type": "required_columns", "columns": ["symbol", "trade_time", "price", "volume"], "priority": "HIGH"},
        )

        self.register_rule("stock_tick", {"type": "value_range", "column": "price", "min": 0, "priority": "HIGH"})

        self.register_rule("stock_tick", {"type": "value_range", "column": "volume", "min": 0, "priority": "MEDIUM"})

        logger.info(f"已加载 {sum(len(rules) for rules in self.rules.values())} 个默认验证规则")


# 全局验证器实例
_validator = DataValidator()


def get_validator() -> DataValidator:
    """获取全局验证器实例"""
    return _validator


def validate_data(table_name: str, data: pd.DataFrame, raise_on_error: bool = False) -> Dict[str, Any]:
    """
    验证数据（便捷函数）

    参数:
        table_name: 表名
        data: 要验证的数据
        raise_on_error: 验证失败时是否抛出异常

    返回:
        验证结果

    抛出:
        ValueError: 如果验证失败且raise_on_error为True
    """
    result = get_validator().validate(table_name, data)

    if not result["is_valid"] and raise_on_error:
        error_msg = f"数据验证失败: {', '.join(result['errors'])}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    return result
