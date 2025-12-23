"""
输入验证和安全处理中间件
"""

import re
import html
from typing import Dict, Optional
from fastapi import Request, HTTPException, status
import logging

logger = logging.getLogger(__name__)


class SQLInjectionPattern:
    """SQL注入模式检测"""

    # 常见SQL注入模式
    PATTERNS = [
        r"(union\s+select)",
        r"(or\s+1\s*=\s*1)",
        r"(and\s+1\s*=\s*1)",
        r"(drop\s+table)",
        r"(delete\s+from)",
        r"(insert\s+into)",
        r"(update\s+set)",
        r"(exec\()",
        r"(--)",
        r"(/\*.*?\*/)",
        r"(;)",
        r"(')",
        r'(")',
        r"(<)",
        r"(>)",
        r"(\|)",
        r"(&)",
        r"(\')",
        r'(")',
        r"(\x00)",
        r"(\n)",
        r"(\r)",
        r"(\t)",
        r"(\x08)",
        r"(\x0b)",
    ]

    @classmethod
    def contains_patterns(cls, text: str) -> bool:
        """检查文本是否包含SQL注入模式"""
        if not text:
            return False

        text_lower = text.lower()
        for pattern in cls.PATTERNS:
            if re.search(pattern, text_lower):
                logger.warning(f"检测到SQL注入模式: {pattern} 在输入: {text[:50]}...")
                return True
        return False


class XSSPattern:
    """XSS攻击模式检测"""

    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"<applet[^>]*>",
        r"<meta[^>]*>",
        r"<link[^>]*>",
        r"<style[^>]*>.*?</style>",
        r"<\?php.*?\?>",
        r"<%.*?%>",
        r"{{.*?}}",
        r"{{.*?}}",
    ]

    @classmethod
    def contains_patterns(cls, text: str) -> bool:
        """检查文本是否包含XSS攻击模式"""
        if not text:
            return False

        text_lower = text.lower()
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, text_lower):
                logger.warning(f"检测到XSS攻击模式: {pattern} 在输入: {text[:50]}...")
                return True
        return False


def sanitize_input(text: str) -> str:
    """
    清理用户输入，防止XSS和注入攻击

    Args:
        text: 原始输入文本

    Returns:
        str: 清理后的安全文本
    """
    if not text:
        return text

    # HTML转义
    sanitized = html.escape(text)

    # 移除控制字符
    sanitized = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", sanitized)

    # 标准化换行符
    sanitized = sanitized.replace("\r\n", "\n").replace("\r", "\n")

    return sanitized


def validate_input(
    value: str,
    max_length: int = 1000,
    input_type: str = "general",
    allow_empty: bool = False,
) -> str:
    """
    验证和清理用户输入

    Args:
        value: 输入值
        max_length: 最大长度限制
        input_type: 输入类型 (general, username, password, symbol)
        allow_empty: 是否允许空值

    Returns:
        str: 验证和清理后的安全值

    Raises:
        HTTPException: 输入验证失败时抛出
    """
    if not value:
        if allow_empty:
            return ""
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="输入不能为空"
        )

    # 检查长度
    if len(value) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"输入长度超过限制 ({max_length} 字符)",
        )

    # 根据输入类型进行特定验证
    if input_type == "username":
        # 用户名验证：只允许字母、数字、下划线，3-20个字符
        if not re.match(r"^[a-zA-Z0-9_]{3,20}$", value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名只能包含字母、数字和下划线，长度3-20个字符",
            )

    elif input_type == "password":
        # 密码验证在security.py中处理
        pass

    elif input_type == "symbol":
        # 股票代码验证：只允许字母、数字、点、横线
        if not re.match(r"^[A-Za-z0-9.-]+$", value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="股票代码格式无效"
            )

    # 检查SQL注入
    if SQLInjectionPattern.contains_patterns(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="输入包含非法字符或攻击模式"
        )

    # 检查XSS攻击
    if XSSPattern.contains_patterns(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="输入包含潜在的XSS攻击代码"
        )

    # 返回清理后的输入
    return sanitize_input(value)


class SecureQueryParams:
    """安全查询参数验证"""

    @staticmethod
    def validate_pagination_params(page: int = 1, size: int = 100) -> Dict[str, int]:
        """验证分页参数"""
        if page < 1:
            page = 1
        if size < 1:
            size = 1
        if size > 1000:  # 限制最大单页数量
            size = 1000

        return {"page": page, "size": size}

    @staticmethod
    def validate_date_range(
        start_date: Optional[str], end_date: Optional[str]
    ) -> Dict[str, str]:
        """验证日期范围参数"""
        import re
        from datetime import datetime

        date_pattern = r"^\d{4}-\d{2}-\d{2}$"

        if start_date and not re.match(date_pattern, start_date):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="开始日期格式无效，请使用 YYYY-MM-DD 格式",
            )

        if end_date and not re.match(date_pattern, end_date):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="结束日期格式无效，请使用 YYYY-MM-DD 格式",
            )

        # 简单的日期逻辑验证
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d")
                if start > end:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="开始日期不能晚于结束日期",
                    )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="日期格式无效"
                )

        return {"start_date": start_date, "end_date": end_date}


async def request_middleware(request: Request, call_next):
    """
    请求安全中间件

    对所有请求进行基本的安全检查
    """
    # 记录请求信息（不记录敏感数据）
    logger.info(f"Request: {request.method} {request.url}")

    # 检查请求头中的潜在攻击
    headers = dict(request.headers)
    for key, value in headers.items():
        if SQLInjectionPattern.contains_patterns(
            str(value)
        ) or XSSPattern.contains_patterns(str(value)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="请求头包含非法内容"
            )

    # 检查查询参数
    query_params = dict(request.query_params)
    for key, value in query_params.items():
        if SQLInjectionPattern.contains_patterns(
            str(value)
        ) or XSSPattern.contains_patterns(str(value)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"查询参数 '{key}' 包含非法内容",
            )

    # 处理请求
    response = await call_next(request)

    # 添加安全响应头
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    return response
