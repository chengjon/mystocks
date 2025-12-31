"""
统一错误码体系 (Unified Error Code System)

提供统一的错误码定义、HTTP状态码映射和错误分类
与validation_messages.py集成,实现完整的错误处理体系
"""

from enum import IntEnum
from typing import Dict
from app.core.validation_messages import (
    CommonMessages,
    MarketMessages,
    TechnicalMessages,
    TradeMessages,
)


# ==================== 错误码枚举定义 ====================


class ErrorCode(IntEnum):
    """统一错误码枚举

    错误码设计规则:
    - 0: 成功
    - 1xxx: 通用错误 (参数验证、格式错误等)
    - 2xxx: Market模块错误
    - 3xxx: Technical模块错误
    - 4xxx: Trade模块错误
    - 5xxx: Strategy模块错误
    - 6xxx: System模块错误
    - 9xxx: 服务器内部错误
    """

    # ===== 成功 =====
    SUCCESS = 0

    # ===== 1xxx: 通用错误 =====
    # 请求参数错误 (1000-1099)
    BAD_REQUEST = 1000
    VALIDATION_ERROR = 1001
    MISSING_REQUIRED_FIELD = 1002
    INVALID_FORMAT = 1003
    INVALID_VALUE = 1004
    OUT_OF_RANGE = 1005
    FIELD_VALIDATION_ERROR = 1006

    # 股票代码错误 (1100-1199)
    SYMBOL_INVALID = 1100
    SYMBOL_REQUIRED = 1101
    SYMBOL_INVALID_FORMAT = 1102
    SYMBOL_INVALID_PREFIX = 1103
    SYMBOL_INVALID_DOTS = 1104
    SYMBOL_TOO_SHORT = 1105
    SYMBOL_TOO_LONG = 1106

    # 日期相关错误 (1200-1299)
    DATE_INVALID = 1200
    DATE_INVALID_FORMAT = 1201
    DATE_FUTURE = 1202
    DATE_TOO_OLD = 1203
    DATE_RANGE_INVALID = 1204
    DATE_RANGE_TOO_LONG = 1205

    # 数值相关错误 (1300-1399)
    VALUE_INVALID = 1300
    VALUE_NOT_POSITIVE = 1301
    VALUE_NEGATIVE = 1302
    VALUE_TOO_SMALL = 1303
    VALUE_TOO_LARGE = 1304

    # 交易参数错误 (1400-1499)
    QUANTITY_INVALID = 1400
    DIRECTION_INVALID = 1401
    ORDER_TYPE_INVALID = 1402
    PRICE_INVALID = 1403
    PRICE_REQUIRED = 1404
    PRICE_NOT_POSITIVE = 1405

    # ===== 2xxx: Market模块错误 =====
    # K线数据错误 (2000-2099)
    KLINE_INTERVAL_INVALID = 2000
    KLINE_ADJUST_INVALID = 2001
    KLINE_LIMIT_EXCEEDED = 2002
    KLINE_DATA_NOT_FOUND = 2003

    # 市场数据错误 (2100-2199)
    MARKET_TYPE_INVALID = 2100
    MARKET_DATA_NOT_FOUND = 2101
    MARKET_DATA_UNAVAILABLE = 2102

    # ETF相关错误 (2200-2299)
    ETF_CATEGORY_INVALID = 2200
    ETF_DATA_NOT_FOUND = 2201

    # 资金流向错误 (2300-2399)
    FUND_FLOW_TIMEFRAME_INVALID = 2300
    FUND_FLOW_DATA_NOT_FOUND = 2301

    # ===== 3xxx: Technical模块错误 =====
    # 技术指标错误 (3000-3099)
    INDICATOR_TYPE_INVALID = 3000
    OVERLAY_INDICATOR_INVALID = 3001
    OSCILLATOR_INDICATOR_INVALID = 3002
    INDICATOR_PARAMETER_INVALID = 3003
    INDICATOR_CALCULATION_FAILED = 3004

    # MA指标错误 (3100-3199)
    MA_PERIOD_INVALID = 3100
    MA_PERIOD_TOO_MANY = 3101

    # BOLL指标错误 (3200-3299)
    BOLL_PERIOD_INVALID = 3200
    BOLL_STDDEV_INVALID = 3201

    # MACD指标错误 (3300-3399)
    MACD_FAST_INVALID = 3300
    MACD_SLOW_INVALID = 3301
    MACD_SIGNAL_INVALID = 3302

    # KDJ指标错误 (3400-3499)
    KDJ_PERIOD_INVALID = 3400

    # RSI指标错误 (3500-3599)
    RSI_PERIOD_INVALID = 3500

    # ===== 4xxx: Trade模块错误 =====
    # 订单相关错误 (4000-4099)
    ORDER_NOT_FOUND = 4000
    ORDER_ALREADY_FILLED = 4001
    ORDER_ALREADY_CANCELLED = 4002
    ORDER_CANCELLATION_FAILED = 4003
    ORDER_ID_REQUIRED = 4004

    # 持仓相关错误 (4100-4199)
    INSUFFICIENT_POSITION = 4100
    INSUFFICIENT_AVAILABLE_POSITION = 4101
    POSITION_NOT_FOUND = 4102

    # 账户相关错误 (4200-4299)
    INSUFFICIENT_CASH = 4200
    ACCOUNT_FROZEN = 4201
    ACCOUNT_NOT_FOUND = 4202

    # 交易时间错误 (4300-4399)
    MARKET_CLOSED = 4300
    NOT_IN_TRADING_HOURS = 4301

    # 风控相关错误 (4400-4499)
    EXCEED_DAILY_LIMIT = 4400
    EXCEED_POSITION_LIMIT = 4401
    RISK_LEVEL_HIGH = 4402

    # ===== 5xxx: Strategy模块错误 =====
    STRATEGY_NOT_FOUND = 5000
    STRATEGY_ALREADY_RUNNING = 5001
    STRATEGY_NOT_RUNNING = 5002
    STRATEGY_START_FAILED = 5003
    STRATEGY_STOP_FAILED = 5004
    STRATEGY_PARAMETER_INVALID = 5005

    # ===== 6xxx: System模块错误 =====
    AUTHENTICATION_FAILED = 6000
    AUTHORIZATION_FAILED = 6001
    TOKEN_EXPIRED = 6002
    TOKEN_INVALID = 6003
    SESSION_EXPIRED = 6004
    RATE_LIMIT_EXCEEDED = 6005

    # ===== 9xxx: 服务器内部错误 =====
    INTERNAL_SERVER_ERROR = 9000
    EXTERNAL_SERVICE_ERROR = 9001
    SERVICE_UNAVAILABLE = 9002
    DATABASE_ERROR = 9003
    CACHE_ERROR = 9004
    NETWORK_ERROR = 9005


# ==================== HTTP状态码映射 ====================


class HTTPStatus:
    """HTTP状态码常量"""

    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204

    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429

    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504


# 错误码到HTTP状态码的映射
ERROR_CODE_HTTP_MAP: Dict[ErrorCode, int] = {
    # 成功
    ErrorCode.SUCCESS: HTTPStatus.OK,
    # 1xxx: 通用错误 → 400 Bad Request
    ErrorCode.BAD_REQUEST: HTTPStatus.BAD_REQUEST,
    ErrorCode.VALIDATION_ERROR: HTTPStatus.UNPROCESSABLE_ENTITY,
    ErrorCode.MISSING_REQUIRED_FIELD: HTTPStatus.BAD_REQUEST,
    ErrorCode.INVALID_FORMAT: HTTPStatus.BAD_REQUEST,
    ErrorCode.INVALID_VALUE: HTTPStatus.BAD_REQUEST,
    ErrorCode.OUT_OF_RANGE: HTTPStatus.BAD_REQUEST,
    ErrorCode.FIELD_VALIDATION_ERROR: HTTPStatus.UNPROCESSABLE_ENTITY,
    ErrorCode.SYMBOL_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.SYMBOL_REQUIRED: HTTPStatus.BAD_REQUEST,
    ErrorCode.SYMBOL_INVALID_FORMAT: HTTPStatus.BAD_REQUEST,
    ErrorCode.SYMBOL_INVALID_PREFIX: HTTPStatus.BAD_REQUEST,
    ErrorCode.SYMBOL_INVALID_DOTS: HTTPStatus.BAD_REQUEST,
    ErrorCode.SYMBOL_TOO_SHORT: HTTPStatus.BAD_REQUEST,
    ErrorCode.SYMBOL_TOO_LONG: HTTPStatus.BAD_REQUEST,
    ErrorCode.DATE_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.DATE_INVALID_FORMAT: HTTPStatus.BAD_REQUEST,
    ErrorCode.DATE_FUTURE: HTTPStatus.BAD_REQUEST,
    ErrorCode.DATE_TOO_OLD: HTTPStatus.BAD_REQUEST,
    ErrorCode.DATE_RANGE_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.DATE_RANGE_TOO_LONG: HTTPStatus.BAD_REQUEST,
    ErrorCode.VALUE_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.VALUE_NOT_POSITIVE: HTTPStatus.BAD_REQUEST,
    ErrorCode.VALUE_NEGATIVE: HTTPStatus.BAD_REQUEST,
    ErrorCode.VALUE_TOO_SMALL: HTTPStatus.BAD_REQUEST,
    ErrorCode.VALUE_TOO_LARGE: HTTPStatus.BAD_REQUEST,
    ErrorCode.QUANTITY_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.DIRECTION_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.ORDER_TYPE_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.PRICE_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.PRICE_REQUIRED: HTTPStatus.BAD_REQUEST,
    ErrorCode.PRICE_NOT_POSITIVE: HTTPStatus.BAD_REQUEST,
    # 2xxx: Market模块错误 → 400/404
    ErrorCode.KLINE_INTERVAL_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.KLINE_ADJUST_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.KLINE_LIMIT_EXCEEDED: HTTPStatus.BAD_REQUEST,
    ErrorCode.KLINE_DATA_NOT_FOUND: HTTPStatus.NOT_FOUND,
    ErrorCode.MARKET_TYPE_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.MARKET_DATA_NOT_FOUND: HTTPStatus.NOT_FOUND,
    ErrorCode.MARKET_DATA_UNAVAILABLE: HTTPStatus.SERVICE_UNAVAILABLE,
    ErrorCode.ETF_CATEGORY_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.ETF_DATA_NOT_FOUND: HTTPStatus.NOT_FOUND,
    ErrorCode.FUND_FLOW_TIMEFRAME_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.FUND_FLOW_DATA_NOT_FOUND: HTTPStatus.NOT_FOUND,
    # 3xxx: Technical模块错误 → 400/500
    ErrorCode.INDICATOR_TYPE_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.OVERLAY_INDICATOR_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.OSCILLATOR_INDICATOR_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.INDICATOR_PARAMETER_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.INDICATOR_CALCULATION_FAILED: HTTPStatus.INTERNAL_SERVER_ERROR,
    ErrorCode.MA_PERIOD_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.MA_PERIOD_TOO_MANY: HTTPStatus.BAD_REQUEST,
    ErrorCode.BOLL_PERIOD_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.BOLL_STDDEV_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.MACD_FAST_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.MACD_SLOW_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.MACD_SIGNAL_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.KDJ_PERIOD_INVALID: HTTPStatus.BAD_REQUEST,
    ErrorCode.RSI_PERIOD_INVALID: HTTPStatus.BAD_REQUEST,
    # 4xxx: Trade模块错误 → 400/403/404/409
    ErrorCode.ORDER_NOT_FOUND: HTTPStatus.NOT_FOUND,
    ErrorCode.ORDER_ALREADY_FILLED: HTTPStatus.CONFLICT,
    ErrorCode.ORDER_ALREADY_CANCELLED: HTTPStatus.CONFLICT,
    ErrorCode.ORDER_CANCELLATION_FAILED: HTTPStatus.CONFLICT,
    ErrorCode.ORDER_ID_REQUIRED: HTTPStatus.BAD_REQUEST,
    ErrorCode.INSUFFICIENT_POSITION: HTTPStatus.CONFLICT,
    ErrorCode.INSUFFICIENT_AVAILABLE_POSITION: HTTPStatus.CONFLICT,
    ErrorCode.POSITION_NOT_FOUND: HTTPStatus.NOT_FOUND,
    ErrorCode.INSUFFICIENT_CASH: HTTPStatus.CONFLICT,
    ErrorCode.ACCOUNT_FROZEN: HTTPStatus.FORBIDDEN,
    ErrorCode.ACCOUNT_NOT_FOUND: HTTPStatus.NOT_FOUND,
    ErrorCode.MARKET_CLOSED: HTTPStatus.CONFLICT,
    ErrorCode.NOT_IN_TRADING_HOURS: HTTPStatus.CONFLICT,
    ErrorCode.EXCEED_DAILY_LIMIT: HTTPStatus.CONFLICT,
    ErrorCode.EXCEED_POSITION_LIMIT: HTTPStatus.CONFLICT,
    ErrorCode.RISK_LEVEL_HIGH: HTTPStatus.FORBIDDEN,
    # 5xxx: Strategy模块错误 → 400/404/409/500
    ErrorCode.STRATEGY_NOT_FOUND: HTTPStatus.NOT_FOUND,
    ErrorCode.STRATEGY_ALREADY_RUNNING: HTTPStatus.CONFLICT,
    ErrorCode.STRATEGY_NOT_RUNNING: HTTPStatus.CONFLICT,
    ErrorCode.STRATEGY_START_FAILED: HTTPStatus.INTERNAL_SERVER_ERROR,
    ErrorCode.STRATEGY_STOP_FAILED: HTTPStatus.INTERNAL_SERVER_ERROR,
    ErrorCode.STRATEGY_PARAMETER_INVALID: HTTPStatus.BAD_REQUEST,
    # 6xxx: System模块错误 → 401/403/429
    ErrorCode.AUTHENTICATION_FAILED: HTTPStatus.UNAUTHORIZED,
    ErrorCode.AUTHORIZATION_FAILED: HTTPStatus.FORBIDDEN,
    ErrorCode.TOKEN_EXPIRED: HTTPStatus.UNAUTHORIZED,
    ErrorCode.TOKEN_INVALID: HTTPStatus.UNAUTHORIZED,
    ErrorCode.SESSION_EXPIRED: HTTPStatus.UNAUTHORIZED,
    ErrorCode.RATE_LIMIT_EXCEEDED: HTTPStatus.TOO_MANY_REQUESTS,
    # 9xxx: 服务器内部错误 → 500/503
    ErrorCode.INTERNAL_SERVER_ERROR: HTTPStatus.INTERNAL_SERVER_ERROR,
    ErrorCode.EXTERNAL_SERVICE_ERROR: 502,  # HTTPStatus.BAD_GATEWAY (兼容性修复)
    ErrorCode.SERVICE_UNAVAILABLE: HTTPStatus.SERVICE_UNAVAILABLE,
    ErrorCode.DATABASE_ERROR: HTTPStatus.INTERNAL_SERVER_ERROR,
    ErrorCode.CACHE_ERROR: HTTPStatus.INTERNAL_SERVER_ERROR,
    ErrorCode.NETWORK_ERROR: HTTPStatus.SERVICE_UNAVAILABLE,
}


# ==================== 错误码到中文消息映射 ====================


ERROR_CODE_MESSAGE_MAP: Dict[ErrorCode, str] = {
    # ===== 成功 =====
    ErrorCode.SUCCESS: "操作成功",
    # ===== 1xxx: 通用错误 =====
    ErrorCode.BAD_REQUEST: "请求参数错误",
    ErrorCode.VALIDATION_ERROR: "输入参数验证失败",
    ErrorCode.MISSING_REQUIRED_FIELD: "缺少必填字段",
    ErrorCode.INVALID_FORMAT: "格式不正确",
    ErrorCode.INVALID_VALUE: "参数值不正确",
    ErrorCode.OUT_OF_RANGE: "参数值超出范围",
    ErrorCode.FIELD_VALIDATION_ERROR: "字段验证失败",
    ErrorCode.SYMBOL_INVALID: "股票代码不正确",
    ErrorCode.SYMBOL_REQUIRED: CommonMessages.SYMBOL_REQUIRED,
    ErrorCode.SYMBOL_INVALID_FORMAT: CommonMessages.SYMBOL_INVALID_FORMAT,
    ErrorCode.SYMBOL_INVALID_PREFIX: CommonMessages.SYMBOL_INVALID_PREFIX,
    ErrorCode.SYMBOL_INVALID_DOTS: CommonMessages.SYMBOL_INVALID_DOTS,
    ErrorCode.SYMBOL_TOO_SHORT: CommonMessages.SYMBOL_TOO_SHORT,
    ErrorCode.SYMBOL_TOO_LONG: CommonMessages.SYMBOL_TOO_LONG,
    ErrorCode.DATE_INVALID: "日期不正确",
    ErrorCode.DATE_INVALID_FORMAT: CommonMessages.DATE_INVALID_FORMAT,
    ErrorCode.DATE_FUTURE: CommonMessages.DATE_FUTURE,
    ErrorCode.DATE_TOO_OLD: CommonMessages.DATE_TOO_OLD,
    ErrorCode.DATE_RANGE_INVALID: CommonMessages.DATE_RANGE_INVALID,
    ErrorCode.DATE_RANGE_TOO_LONG: CommonMessages.DATE_RANGE_TOO_LONG,
    ErrorCode.VALUE_INVALID: "数值不正确",
    ErrorCode.VALUE_NOT_POSITIVE: "数值必须大于0",
    ErrorCode.VALUE_NEGATIVE: CommonMessages.VALUE_MUST_BE_NON_NEGATIVE,
    ErrorCode.VALUE_TOO_SMALL: "数值太小",
    ErrorCode.VALUE_TOO_LARGE: "数值太大",
    ErrorCode.QUANTITY_INVALID: CommonMessages.QUANTITY_INVALID,
    ErrorCode.DIRECTION_INVALID: CommonMessages.DIRECTION_INVALID,
    ErrorCode.ORDER_TYPE_INVALID: CommonMessages.ORDER_TYPE_INVALID,
    ErrorCode.PRICE_INVALID: "价格不正确",
    ErrorCode.PRICE_REQUIRED: CommonMessages.PRICE_REQUIRED_FOR_LIMIT,
    ErrorCode.PRICE_NOT_POSITIVE: CommonMessages.PRICE_MUST_BE_POSITIVE,
    # ===== 2xxx: Market模块错误 =====
    ErrorCode.KLINE_INTERVAL_INVALID: MarketMessages.KLINE_INTERVAL_INVALID,
    ErrorCode.KLINE_ADJUST_INVALID: MarketMessages.KLINE_ADJUST_INVALID,
    ErrorCode.KLINE_LIMIT_EXCEEDED: MarketMessages.KLINE_LIMIT_EXCEEDED,
    ErrorCode.KLINE_DATA_NOT_FOUND: "K线数据不存在",
    ErrorCode.MARKET_TYPE_INVALID: MarketMessages.MARKET_TYPE_INVALID,
    ErrorCode.MARKET_DATA_NOT_FOUND: "市场数据不存在",
    ErrorCode.MARKET_DATA_UNAVAILABLE: "市场数据暂时不可用",
    ErrorCode.ETF_CATEGORY_INVALID: MarketMessages.ETF_CATEGORY_INVALID,
    ErrorCode.ETF_DATA_NOT_FOUND: "ETF数据不存在",
    ErrorCode.FUND_FLOW_TIMEFRAME_INVALID: MarketMessages.FUND_FLOW_TIMEFRAME_INVALID,
    ErrorCode.FUND_FLOW_DATA_NOT_FOUND: "资金流向数据不存在",
    # ===== 3xxx: Technical模块错误 =====
    ErrorCode.INDICATOR_TYPE_INVALID: TechnicalMessages.INDICATOR_TYPE_INVALID,
    ErrorCode.OVERLAY_INDICATOR_INVALID: TechnicalMessages.OVERLAY_INDICATOR_INVALID,
    ErrorCode.OSCILLATOR_INDICATOR_INVALID: TechnicalMessages.OSCILLATOR_INDICATOR_INVALID,
    ErrorCode.INDICATOR_PARAMETER_INVALID: "技术指标参数不正确",
    ErrorCode.INDICATOR_CALCULATION_FAILED: "技术指标计算失败",
    ErrorCode.MA_PERIOD_INVALID: TechnicalMessages.MA_PERIOD_INVALID,
    ErrorCode.MA_PERIOD_TOO_MANY: TechnicalMessages.MA_PERIOD_TOO_MANY,
    ErrorCode.BOLL_PERIOD_INVALID: TechnicalMessages.BOLL_PERIOD_INVALID,
    ErrorCode.BOLL_STDDEV_INVALID: TechnicalMessages.BOLL_STDDEV_INVALID,
    ErrorCode.MACD_FAST_INVALID: TechnicalMessages.MACD_FAST_INVALID,
    ErrorCode.MACD_SLOW_INVALID: TechnicalMessages.MACD_SLOW_INVALID,
    ErrorCode.MACD_SIGNAL_INVALID: TechnicalMessages.MACD_SIGNAL_INVALID,
    ErrorCode.KDJ_PERIOD_INVALID: TechnicalMessages.KDJ_PERIOD_INVALID,
    ErrorCode.RSI_PERIOD_INVALID: TechnicalMessages.RSI_PERIOD_INVALID,
    # ===== 4xxx: Trade模块错误 =====
    ErrorCode.ORDER_NOT_FOUND: TradeMessages.ORDER_NOT_FOUND,
    ErrorCode.ORDER_ALREADY_FILLED: TradeMessages.ORDER_ALREADY_FILLED,
    ErrorCode.ORDER_ALREADY_CANCELLED: TradeMessages.ORDER_ALREADY_CANCELLED,
    ErrorCode.ORDER_CANCELLATION_FAILED: TradeMessages.ORDER_CANCELLATION_FAILED,
    ErrorCode.ORDER_ID_REQUIRED: TradeMessages.ORDER_ID_REQUIRED,
    ErrorCode.INSUFFICIENT_POSITION: TradeMessages.INSUFFICIENT_POSITION,
    ErrorCode.INSUFFICIENT_AVAILABLE_POSITION: TradeMessages.INSUFFICIENT_AVAILABLE_POSITION,
    ErrorCode.POSITION_NOT_FOUND: "持仓不存在",
    ErrorCode.INSUFFICIENT_CASH: TradeMessages.INSUFFICIENT_CASH,
    ErrorCode.ACCOUNT_FROZEN: TradeMessages.ACCOUNT_FROZEN,
    ErrorCode.ACCOUNT_NOT_FOUND: "账户不存在",
    ErrorCode.MARKET_CLOSED: TradeMessages.MARKET_CLOSED,
    ErrorCode.NOT_IN_TRADING_HOURS: TradeMessages.NOT_IN_TRADING_HOURS,
    ErrorCode.EXCEED_DAILY_LIMIT: TradeMessages.EXCEED_DAILY_LIMIT,
    ErrorCode.EXCEED_POSITION_LIMIT: TradeMessages.EXCEED_POSITION_LIMIT,
    ErrorCode.RISK_LEVEL_HIGH: TradeMessages.RISK_LEVEL_HIGH,
    # ===== 5xxx: Strategy模块错误 =====
    ErrorCode.STRATEGY_NOT_FOUND: "策略不存在",
    ErrorCode.STRATEGY_ALREADY_RUNNING: "策略已在运行中",
    ErrorCode.STRATEGY_NOT_RUNNING: "策略未运行",
    ErrorCode.STRATEGY_START_FAILED: "策略启动失败",
    ErrorCode.STRATEGY_STOP_FAILED: "策略停止失败",
    ErrorCode.STRATEGY_PARAMETER_INVALID: "策略参数不正确",
    # ===== 6xxx: System模块错误 =====
    ErrorCode.AUTHENTICATION_FAILED: "身份验证失败",
    ErrorCode.AUTHORIZATION_FAILED: "权限不足",
    ErrorCode.TOKEN_EXPIRED: "登录已过期，请重新登录",
    ErrorCode.TOKEN_INVALID: "无效的登录凭证",
    ErrorCode.SESSION_EXPIRED: "会话已过期",
    ErrorCode.RATE_LIMIT_EXCEEDED: "请求过于频繁，请稍后再试",
    # ===== 9xxx: 服务器内部错误 =====
    ErrorCode.INTERNAL_SERVER_ERROR: "服务器内部错误",
    ErrorCode.EXTERNAL_SERVICE_ERROR: "外部服务调用失败",
    ErrorCode.SERVICE_UNAVAILABLE: "服务暂不可用",
    ErrorCode.DATABASE_ERROR: "数据库操作失败",
    ErrorCode.CACHE_ERROR: "缓存服务错误",
    ErrorCode.NETWORK_ERROR: "网络连接错误",
}


# ==================== 错误类别定义 ====================


class ErrorCategory(IntEnum):
    """错误类别枚举"""

    SUCCESS = 0
    CLIENT_ERROR = 4  # 4xx 客户端错误
    SERVER_ERROR = 5  # 5xx 服务器错误


ERROR_CODE_CATEGORY_MAP: Dict[ErrorCode, ErrorCategory] = {
    # 成功
    ErrorCode.SUCCESS: ErrorCategory.SUCCESS,
    # 1xxx-6xxx → CLIENT_ERROR
    ErrorCode.BAD_REQUEST: ErrorCategory.CLIENT_ERROR,
    ErrorCode.VALIDATION_ERROR: ErrorCategory.CLIENT_ERROR,
    # ... (所有业务错误都是CLIENT_ERROR)
    ErrorCode.RATE_LIMIT_EXCEEDED: ErrorCategory.CLIENT_ERROR,
    # 9xxx → SERVER_ERROR
    ErrorCode.INTERNAL_SERVER_ERROR: ErrorCategory.SERVER_ERROR,
    ErrorCode.EXTERNAL_SERVICE_ERROR: ErrorCategory.SERVER_ERROR,
    ErrorCode.SERVICE_UNAVAILABLE: ErrorCategory.SERVER_ERROR,
    ErrorCode.DATABASE_ERROR: ErrorCategory.SERVER_ERROR,
    ErrorCode.CACHE_ERROR: ErrorCategory.SERVER_ERROR,
    ErrorCode.NETWORK_ERROR: ErrorCategory.SERVER_ERROR,
}


# ==================== 工具函数 ====================


def get_http_status(error_code: ErrorCode) -> int:
    """
    获取错误码对应的HTTP状态码

    Args:
        error_code: 错误码

    Returns:
        HTTP状态码
    """
    return ERROR_CODE_HTTP_MAP.get(error_code, HTTPStatus.INTERNAL_SERVER_ERROR)


def get_error_message(error_code: ErrorCode) -> str:
    """
    获取错误码对应的中文消息

    Args:
        error_code: 错误码

    Returns:
        中文错误消息
    """
    return ERROR_CODE_MESSAGE_MAP.get(error_code, "未知错误")


def get_error_category(error_code: ErrorCode) -> ErrorCategory:
    """
    获取错误码的类别

    Args:
        error_code: 错误码

    Returns:
        错误类别
    """
    return ERROR_CODE_CATEGORY_MAP.get(error_code, ErrorCategory.SERVER_ERROR)


def is_success(error_code: ErrorCode) -> bool:
    """判断是否为成功错误码"""
    return error_code == ErrorCode.SUCCESS


def is_client_error(error_code: ErrorCode) -> bool:
    """判断是否为客户端错误"""
    category = get_error_category(error_code)
    return category == ErrorCategory.CLIENT_ERROR


def is_server_error(error_code: ErrorCode) -> bool:
    """判断是否为服务器错误"""
    category = get_error_category(error_code)
    return category == ErrorCategory.SERVER_ERROR


# ==================== 导出 ====================


__all__ = [
    "ErrorCode",
    "HTTPStatus",
    "ErrorCategory",
    "get_http_status",
    "get_error_message",
    "get_error_category",
    "is_success",
    "is_client_error",
    "is_server_error",
    "ERROR_CODE_HTTP_MAP",
    "ERROR_CODE_MESSAGE_MAP",
    "ERROR_CODE_CATEGORY_MAP",
]
