"""
错误消息映射 - Week 3 简化版
集中管理用户友好的错误消息
"""

from typing import Dict

# 数据库相关错误消息
DATABASE_ERRORS: Dict[str, str] = {
    "connection_failed": "无法连接到数据库，请稍后重试",
    "query_timeout": "数据查询超时，请缩小查询范围后重试",
    "data_not_found": "未找到相关数据",
    "duplicate_entry": "数据已存在，请勿重复添加",
    "constraint_violation": "数据不符合要求，请检查输入",
    "table_not_exist": "数据表不存在，请联系管理员",
}

# 认证相关错误消息
AUTH_ERRORS: Dict[str, str] = {
    "token_expired": "登录已过期，请重新登录",
    "token_invalid": "登录信息无效，请重新登录",
    "credentials_invalid": "用户名或密码错误",
    "permission_denied": "您没有权限执行此操作",
    "user_not_found": "用户不存在",
    "user_inactive": "账户已被禁用，请联系管理员",
}

# 验证相关错误消息
VALIDATION_ERRORS: Dict[str, str] = {
    "missing_field": "缺少必填字段：{field}",
    "invalid_format": "字段格式不正确：{field}",
    "value_too_long": "输入内容过长：{field}",
    "value_too_short": "输入内容过短：{field}",
    "invalid_date_range": "日期范围无效",
    "invalid_stock_code": "股票代码格式不正确",
}

# 业务逻辑错误消息
BUSINESS_ERRORS: Dict[str, str] = {
    "stock_not_found": "股票不存在或已退市",
    "data_source_unavailable": "数据源暂时不可用，请稍后重试",
    "rate_limit_exceeded": "请求过于频繁，请稍后重试",
    "service_unavailable": "服务暂时不可用，请稍后重试",
    "calculation_failed": "指标计算失败，请检查参数设置",
}

# 通用错误消息
GENERIC_ERRORS: Dict[str, str] = {
    "internal_error": "系统错误，我们已记录此问题，请稍后重试",
    "bad_request": "请求参数有误，请检查后重试",
    "not_found": "请求的资源不存在",
    "method_not_allowed": "不支持的请求方式",
    "network_error": "网络错误，请检查连接后重试",
}

# 合并所有错误消息
ALL_ERROR_MESSAGES = {
    **DATABASE_ERRORS,
    **AUTH_ERRORS,
    **VALIDATION_ERRORS,
    **BUSINESS_ERRORS,
    **GENERIC_ERRORS,
}


def get_error_message(error_key: str, **kwargs) -> str:
    """
    获取错误消息（支持参数替换）

    参数:
        error_key: 错误消息键
        **kwargs: 用于替换消息中占位符的参数

    返回:
        str: 格式化后的错误消息

    示例:
        >>> get_error_message("missing_field", field="股票代码")
        "缺少必填字段：股票代码"
    """
    message = ALL_ERROR_MESSAGES.get(error_key, GENERIC_ERRORS["internal_error"])

    # 如果消息包含占位符，进行参数替换
    if kwargs:
        try:
            return message.format(**kwargs)
        except KeyError:
            # 如果占位符不匹配，返回原消息
            return message

    return message


def get_database_error(error_key: str) -> str:
    """快捷方法: 获取数据库错误消息"""
    return DATABASE_ERRORS.get(error_key, GENERIC_ERRORS["internal_error"])


def get_auth_error(error_key: str) -> str:
    """快捷方法: 获取认证错误消息"""
    return AUTH_ERRORS.get(error_key, GENERIC_ERRORS["internal_error"])


def get_validation_error(error_key: str, **kwargs) -> str:
    """快捷方法: 获取验证错误消息"""
    return get_error_message(error_key, **kwargs)
