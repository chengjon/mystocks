"""
通用自定义验证器 (Pydantic v2)

提供可重用的业务逻辑验证器，确保数据一致性和业务规则
"""

from datetime import date, datetime
from typing import Any, List, Optional
from decimal import Decimal


from app.core.validation_messages import (
    CommonMessages,
    MarketMessages,
    TechnicalMessages,
)


# ==================== 股票代码验证器 ====================


class StockSymbolValidator:
    """股票代码验证器"""

    @staticmethod
    def validate_format(symbol: str) -> str:
        """
        验证股票代码格式

        支持格式:
        - 6位数字 (如: 600519)
        - 6位数字.交易所后缀 (如: 600519.SH, 000001.SZ)

        Args:
            symbol: 股票代码

        Returns:
            大写化后的股票代码

        Raises:
            ValueError: 格式不正确时抛出
        """
        if not symbol:
            raise ValueError(CommonMessages.SYMBOL_REQUIRED)

        symbol = symbol.strip().upper()

        # 不能以点开头
        if symbol.startswith("."):
            raise ValueError(CommonMessages.SYMBOL_INVALID_PREFIX)

        # 不能包含连续的点
        if ".." in symbol:
            raise ValueError(CommonMessages.SYMBOL_INVALID_DOTS)

        # 检查基本格式 (6位数字，可选.交易所后缀)
        if "." in symbol:
            parts = symbol.split(".")
            if len(parts) != 2:
                raise ValueError(CommonMessages.SYMBOL_INVALID_FORMAT)

            code_part, exchange_part = parts
            if not code_part.isdigit() or len(code_part) != 6:
                raise ValueError(CommonMessages.SYMBOL_INVALID_FORMAT)

            if exchange_part not in ["SH", "SZ"]:
                raise ValueError("交易所后缀必须是SH或SZ")
        else:
            if not symbol.isdigit() or len(symbol) != 6:
                raise ValueError(CommonMessages.SYMBOL_INVALID_FORMAT)

        return symbol

    @staticmethod
    def validate_length(symbol: str, min_length: int = 6, max_length: int = 20) -> str:
        """验证股票代码长度"""
        symbol = symbol.strip()

        if len(symbol) < min_length:
            raise ValueError(CommonMessages.SYMBOL_TOO_SHORT)

        if len(symbol) > max_length:
            raise ValueError(CommonMessages.SYMBOL_TOO_LONG)

        return symbol


# ==================== 日期范围验证器 ====================


class DateRangeValidator:
    """日期范围验证器"""

    @staticmethod
    def validate_date_format(date_str: Optional[str]) -> Optional[str]:
        """
        验证日期格式 (YYYY-MM-DD)

        Args:
            date_str: 日期字符串

        Returns:
            验证通过的日期字符串

        Raises:
            ValueError: 格式不正确时抛出
        """
        if not date_str:
            return None

        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(CommonMessages.DATE_INVALID_FORMAT)

        # 检查日期不能是未来
        if parsed_date > date.today():
            raise ValueError(CommonMessages.DATE_FUTURE)

        # 检查日期不能太久远
        if parsed_date.year < 1990:
            raise ValueError(CommonMessages.DATE_TOO_OLD)

        return date_str

    @staticmethod
    def validate_date_range(start_date: Optional[date], end_date: Optional[date], max_days: int = 365) -> tuple:
        """
        验证日期范围

        Args:
            start_date: 开始日期
            end_date: 结束日期
            max_days: 最大允许天数差

        Returns:
            (start_date, end_date) 元组

        Raises:
            ValueError: 范围不正确时抛出
        """
        if start_date is None or end_date is None:
            return start_date, end_date

        if end_date <= start_date:
            raise ValueError(CommonMessages.DATE_RANGE_INVALID)

        # 计算日期差
        time_diff = end_date - start_date
        if time_diff.days > max_days:
            raise ValueError(CommonMessages.DATE_RANGE_TOO_LONG)

        return start_date, end_date


# ==================== 数值验证器 ====================


class NumericValidator:
    """数值验证器"""

    @staticmethod
    def validate_positive(value: Any, field_name: str = "数值") -> Any:
        """验证数值必须大于0"""
        try:
            num_value = float(value)
            if num_value <= 0:
                raise ValueError(f"{field_name}{CommonMessages.VALUE_MUST_BE_POSITIVE}")
            return value
        except (TypeError, ValueError):
            raise ValueError(f"{field_name}格式不正确")

    @staticmethod
    def validate_non_negative(value: Any, field_name: str = "数值") -> Any:
        """验证数值不能为负数"""
        try:
            num_value = float(value)
            if num_value < 0:
                raise ValueError(f"{field_name}{CommonMessages.VALUE_MUST_BE_NON_NEGATIVE}")
            return value
        except (TypeError, ValueError):
            raise ValueError(f"{field_name}格式不正确")

    @staticmethod
    def validate_range(
        value: Any, min_value: Optional[float] = None, max_value: Optional[float] = None, field_name: str = "数值"
    ) -> Any:
        """
        验证数值范围

        Args:
            value: 待验证值
            min_value: 最小值 (None表示不限制)
            max_value: 最大值 (None表示不限制)
            field_name: 字段名称

        Returns:
            验证通过的值

        Raises:
            ValueError: 超出范围时抛出
        """
        try:
            num_value = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{field_name}格式不正确")

        if min_value is not None and num_value < min_value:
            raise ValueError(f"{field_name}不能小于{min_value}")

        if max_value is not None and num_value > max_value:
            raise ValueError(f"{field_name}不能大于{max_value}")

        return value


# ==================== 交易相关验证器 ====================


class TradingValidator:
    """交易相关验证器"""

    @staticmethod
    def validate_quantity(quantity: int) -> int:
        """
        验证委托数量 (A股规则)

        A股交易规则:
        - 数量必须是100的整数倍
        - 数量必须大于0

        Args:
            quantity: 委托数量

        Returns:
            验证通过的数量

        Raises:
            ValueError: 不符合规则时抛出
        """
        if quantity <= 0:
            raise ValueError(CommonMessages.QUANTITY_MUST_BE_POSITIVE)

        if quantity % 100 != 0:
            raise ValueError(CommonMessages.QUANTITY_INVALID)

        return quantity

    @staticmethod
    def validate_direction(direction: str) -> str:
        """
        验证交易方向

        Args:
            direction: 交易方向

        Returns:
            验证通过的方向

        Raises:
            ValueError: 方向不正确时抛出
        """
        direction = direction.lower().strip()
        if direction not in ["buy", "sell"]:
            raise ValueError(CommonMessages.DIRECTION_INVALID)
        return direction

    @staticmethod
    def validate_order_type(order_type: str) -> str:
        """
        验证订单类型

        Args:
            order_type: 订单类型

        Returns:
            验证通过的订单类型

        Raises:
            ValueError: 类型不正确时抛出
        """
        order_type = order_type.lower().strip()
        if order_type not in ["limit", "market"]:
            raise ValueError(CommonMessages.ORDER_TYPE_INVALID)
        return order_type

    @staticmethod
    def validate_limit_order_price(order_type: str, price: Optional[Decimal]) -> Optional[Decimal]:
        """
        验证限价单价格

        限价单必须指定价格，且价格必须大于0

        Args:
            order_type: 订单类型
            price: 价格

        Returns:
            验证通过的价格

        Raises:
            ValueError: 价格不正确时抛出
        """
        if order_type == "limit":
            if price is None:
                raise ValueError(CommonMessages.PRICE_REQUIRED_FOR_LIMIT)
            if price <= 0:
                raise ValueError(CommonMessages.PRICE_MUST_BE_POSITIVE)
        return price


# ==================== K线数据验证器 ====================


class KLineValidator:
    """K线数据验证器"""

    VALID_INTERVALS = ["1m", "5m", "15m", "30m", "1h", "1d", "1w", "1M"]
    VALID_ADJUST_TYPES = ["qfq", "hfq", "none"]

    @staticmethod
    def validate_interval(interval: str) -> str:
        """
        验证K线周期

        Args:
            interval: K线周期

        Returns:
            验证通过的周期

        Raises:
            ValueError: 周期不正确时抛出
        """
        interval = interval.lower().strip()
        if interval not in KLineValidator.VALID_INTERVALS:
            raise ValueError(MarketMessages.KLINE_INTERVAL_INVALID)
        return interval

    @staticmethod
    def validate_adjust(adjust: str) -> str:
        """
        验证复权类型

        Args:
            adjust: 复权类型

        Returns:
            验证通过的复权类型

        Raises:
            ValueError: 类型不正确时抛出
        """
        adjust = adjust.lower().strip() if adjust else "none"
        if adjust not in KLineValidator.VALID_ADJUST_TYPES:
            raise ValueError(MarketMessages.KLINE_ADJUST_INVALID)
        return adjust

    @staticmethod
    def validate_limit(limit: int, max_limit: int = 1000) -> int:
        """
        验证数据量限制

        Args:
            limit: 请求数量
            max_limit: 最大允许数量

        Returns:
            验证通过的数量

        Raises:
            ValueError: 超出限制时抛出
        """
        if limit <= 0:
            raise ValueError("请求数量必须大于0")

        if limit > max_limit:
            raise ValueError(MarketMessages.KLINE_LIMIT_EXCEEDED)

        return limit


# ==================== 技术指标验证器 ====================


class IndicatorValidator:
    """技术指标验证器"""

    # 主图叠加指标
    VALID_OVERLAY_INDICATORS = ["MA", "EMA", "BOLL"]

    # 震荡指标
    VALID_OSCILLATOR_INDICATORS = ["MACD", "KDJ", "RSI"]

    @staticmethod
    def validate_indicator_type(indicator_type: str, category: str = "overlay") -> str:
        """
        验证指标类型

        Args:
            indicator_type: 指标类型
            category: 指标类别 (overlay/oscillator)

        Returns:
            验证通过的指标类型

        Raises:
            ValueError: 类型不正确时抛出
        """
        indicator_type = indicator_type.upper().strip()

        if category == "overlay":
            valid_types = IndicatorValidator.VALID_OVERLAY_INDICATORS
            if indicator_type not in valid_types:
                raise ValueError(TechnicalMessages.OVERLAY_INDICATOR_INVALID)
        elif category == "oscillator":
            valid_types = IndicatorValidator.VALID_OSCILLATOR_INDICATORS
            if indicator_type not in valid_types:
                raise ValueError(TechnicalMessages.OSCILLATOR_INDICATOR_INVALID)

        return indicator_type

    @staticmethod
    def validate_ma_period(period: int) -> int:
        """验证移动平均线周期"""
        if not (1 <= period <= 500):
            raise ValueError(TechnicalMessages.MA_PERIOD_INVALID)
        return period

    @staticmethod
    def validate_ma_periods(periods: List[int]) -> List[int]:
        """
        验证多个移动平均线周期

        Args:
            periods: 周期列表

        Returns:
            去重并排序后的周期列表

        Raises:
            ValueError: 不正确时抛出
        """
        if len(periods) > 10:
            raise ValueError(TechnicalMessages.MA_PERIOD_TOO_MANY)

        for period in periods:
            IndicatorValidator.validate_ma_period(period)

        return sorted(set(periods))


# ==================== 导出 ====================


__all__ = [
    "StockSymbolValidator",
    "DateRangeValidator",
    "NumericValidator",
    "TradingValidator",
    "KLineValidator",
    "IndicatorValidator",
]
