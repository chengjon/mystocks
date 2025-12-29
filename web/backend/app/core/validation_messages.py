"""
API验证错误消息常量 (中文)

提供统一的中文错误消息，确保用户友好的错误提示
"""

# ==================== 通用错误消息 ====================


class CommonMessages:
    """通用验证错误消息"""

    # 字段验证
    FIELD_REQUIRED = "必填字段不能为空"
    FIELD_INVALID_FORMAT = "字段格式不正确"
    FIELD_OUT_OF_RANGE = "字段值超出允许范围"

    # 股票代码相关
    SYMBOL_REQUIRED = "股票代码不能为空"
    SYMBOL_INVALID_FORMAT = "股票代码格式不正确，应为6位数字或6位数字.交易所后缀(如600519.SH)"
    SYMBOL_INVALID_PREFIX = "股票代码不能以点开头"
    SYMBOL_INVALID_DOTS = "股票代码不能包含连续的点"
    SYMBOL_TOO_SHORT = "股票代码至少需要6位"
    SYMBOL_TOO_LONG = "股票代码最多20个字符"

    # 日期相关
    DATE_INVALID_FORMAT = "日期格式不正确，请使用YYYY-MM-DD格式"
    DATE_FUTURE = "日期不能是未来时间"
    DATE_TOO_OLD = "日期不能早于1990年"
    DATE_RANGE_INVALID = "结束日期必须大于开始日期"
    DATE_RANGE_TOO_LONG = "查询时间范围不能超过365天"

    # 数值相关
    VALUE_MUST_BE_POSITIVE = "数值必须大于0"
    VALUE_MUST_BE_NON_NEGATIVE = "数值不能为负数"
    VALUE_TOO_SMALL = "数值小于最小允许值"
    VALUE_TOO_LARGE = "数值超过最大允许值"

    # 交易相关
    QUANTITY_INVALID = "委托数量必须是100的整数倍(A股交易规则)"
    QUANTITY_MUST_BE_POSITIVE = "委托数量必须大于0"
    DIRECTION_INVALID = "交易方向必须是buy(买入)或sell(卖出)"
    ORDER_TYPE_INVALID = "订单类型必须是limit(限价)或market(市价)"
    PRICE_REQUIRED_FOR_LIMIT = "限价单必须指定价格"
    PRICE_MUST_BE_POSITIVE = "价格必须大于0"


# ==================== Market模块错误消息 ====================


class MarketMessages:
    """Market模块错误消息"""

    # K线数据
    KLINE_INTERVAL_INVALID = "K线周期不正确，支持: 1m, 5m, 15m, 1h, 1d, 1w, 1M"
    KLINE_ADJUST_INVALID = "复权类型不正确，支持: qfq(前复权), hfq(后复权), none(不复权)"
    KLINE_LIMIT_EXCEEDED = "K线数据请求数量超过限制(最多1000条)"

    # 市场概览
    MARKET_TYPE_INVALID = "市场类型不正确，支持: cn(A股), hk(港股), us(美股)"

    # ETF相关
    ETF_CATEGORY_INVALID = "ETF类型不正确，支持: 股票, 债券, 商品, 货币, QDII"

    # 资金流向
    FUND_FLOW_TIMEFRAME_INVALID = "时间维度不正确，支持: 1, 3, 5, 10"


# ==================== Technical模块错误消息 ====================


class TechnicalMessages:
    """Technical模块错误消息"""

    # 技术指标
    INDICATOR_TYPE_INVALID = "指标类型不正确"
    OVERLAY_INDICATOR_INVALID = "主图叠加指标不正确，支持: MA, EMA, BOLL"
    OSCILLATOR_INDICATOR_INVALID = "震荡指标不正确，支持: MACD, KDJ, RSI"

    # 指标参数
    MA_PERIOD_INVALID = "移动平均线周期必须在1-500之间"
    MA_PERIOD_TOO_MANY = "移动平均线周期数量不能超过10个"
    BOLL_PERIOD_INVALID = "布林带周期必须在5-100之间"
    BOLL_STDDEV_INVALID = "布林带标准差必须在1-5之间"

    # MACD参数
    MACD_FAST_INVALID = "MACD快线周期必须在5-50之间"
    MACD_SLOW_INVALID = "MACD慢线周期必须在20-200之间"
    MACD_SIGNAL_INVALID = "MACD信号线周期必须在5-50之间"

    # KDJ参数
    KDJ_PERIOD_INVALID = "KDJ周期必须在5-50之间"

    # RSI参数
    RSI_PERIOD_INVALID = "RSI周期必须在2-100之间"


# ==================== Trade模块错误消息 ====================


class TradeMessages:
    """Trade模块错误消息"""

    # 订单相关
    ORDER_ID_REQUIRED = "委托ID不能为空"
    ORDER_NOT_FOUND = "委托不存在"
    ORDER_ALREADY_FILLED = "委托已完全成交，无法撤销"
    ORDER_ALREADY_CANCELLED = "委托已被撤销"
    ORDER_CANCELLATION_FAILED = "撤单失败"

    # 持仓相关
    INSUFFICIENT_POSITION = "持仓数量不足"
    INSUFFICIENT_AVAILABLE_POSITION = "可用持仓数量不足"

    # 账户相关
    INSUFFICIENT_CASH = "可用资金不足"
    ACCOUNT_FROZEN = "账户已冻结，无法交易"

    # 交易时间
    MARKET_CLOSED = "市场休市中，无法交易"
    NOT_IN_TRADING_HOURS = "非交易时间"

    # 风控相关
    EXCEED_DAILY_LIMIT = "超过单日交易限额"
    EXCEED_POSITION_LIMIT = "超过持仓限制"
    RISK_LEVEL_HIGH = "风险等级过高，禁止交易"


# ==================== 错误代码映射 ====================


class ErrorMessages:
    """错误消息映射(将错误代码映射到中文消息)"""

    ERROR_CODE_MAP = {
        # 通用错误 (4xx)
        "BAD_REQUEST": "请求参数错误",
        "UNAUTHORIZED": "未授权访问，请先登录",
        "FORBIDDEN": "禁止访问，权限不足",
        "NOT_FOUND": "资源未找到",
        "METHOD_NOT_ALLOWED": "请求方法不支持",
        "DUPLICATE_RESOURCE": "资源已存在",
        "VALIDATION_ERROR": "输入参数验证失败",
        "RATE_LIMIT_EXCEEDED": "请求过于频繁，请稍后再试",
        # 服务器错误 (5xx)
        "INTERNAL_SERVER_ERROR": "服务器内部错误",
        "EXTERNAL_SERVICE_ERROR": "外部服务调用失败",
        "SERVICE_UNAVAILABLE": "服务暂不可用",
        # 业务错误
        "DATA_NOT_FOUND": "数据不存在",
        "OPERATION_FAILED": "操作失败",
        "DATABASE_ERROR": "数据库操作失败",
        # 验证错误细分
        "INVALID_FORMAT": "格式不正确",
        "MISSING_REQUIRED_FIELD": "缺少必填字段",
        "INVALID_VALUE": "参数值不正确",
        "OUT_OF_RANGE": "参数值超出范围",
    }

    @classmethod
    def get_message(cls, error_code: str) -> str:
        """获取错误代码对应的中文消息"""
        return cls.ERROR_CODE_MAP.get(error_code, "未知错误")


# ==================== 详细错误说明生成器 ====================


class ValidationErrorBuilder:
    """构建详细的验证错误信息"""

    @staticmethod
    def build_field_error(field_name: str, message: str) -> dict:
        """构建单个字段错误"""
        return {"field": field_name, "message": message, "code": "FIELD_VALIDATION_ERROR"}

    @staticmethod
    def build_symbol_error(symbol: str, error_type: str) -> dict:
        """构建股票代码错误"""
        error_map = {
            "empty": CommonMessages.SYMBOL_REQUIRED,
            "format": CommonMessages.SYMBOL_INVALID_FORMAT,
            "prefix": CommonMessages.SYMBOL_INVALID_PREFIX,
            "dots": CommonMessages.SYMBOL_INVALID_DOTS,
            "too_short": CommonMessages.SYMBOL_TOO_SHORT,
            "too_long": CommonMessages.SYMBOL_TOO_LONG,
        }
        return ValidationErrorBuilder.build_field_error(
            "symbol", error_map.get(error_type, CommonMessages.SYMBOL_INVALID_FORMAT)
        )

    @staticmethod
    def build_date_error(field_name: str, error_type: str) -> dict:
        """构建日期错误"""
        error_map = {
            "format": CommonMessages.DATE_INVALID_FORMAT,
            "future": CommonMessages.DATE_FUTURE,
            "too_old": CommonMessages.DATE_TOO_OLD,
            "range": CommonMessages.DATE_RANGE_INVALID,
            "too_long": CommonMessages.DATE_RANGE_TOO_LONG,
        }
        return ValidationErrorBuilder.build_field_error(
            field_name, error_map.get(error_type, CommonMessages.DATE_INVALID_FORMAT)
        )

    @staticmethod
    def build_trade_error(error_type: str, detail: str = "") -> dict:
        """构建交易相关错误"""
        error_map = {
            "quantity": CommonMessages.QUANTITY_INVALID,
            "direction": CommonMessages.DIRECTION_INVALID,
            "order_type": CommonMessages.ORDER_TYPE_INVALID,
            "price_required": CommonMessages.PRICE_REQUIRED_FOR_LIMIT,
            "insufficient_cash": TradeMessages.INSUFFICIENT_CASH,
            "insufficient_position": TradeMessages.INSUFFICIENT_POSITION,
            "market_closed": TradeMessages.MARKET_CLOSED,
        }

        message = error_map.get(error_type, detail or "交易参数错误")
        return {"field": "trade", "message": message, "code": error_type.upper() + "_ERROR"}


# ==================== 导出 ====================


__all__ = [
    "CommonMessages",
    "MarketMessages",
    "TechnicalMessages",
    "TradeMessages",
    "ErrorMessages",
    "ValidationErrorBuilder",
]
