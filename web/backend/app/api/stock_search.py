"""
# pylint: disable=no-member  # TODO: 修复异常类的 to_dict 方法
股票搜索 API
提供统一的股票搜索、报价和新闻接口
支持 A 股和 H 股（港股）

安全级别：分级别访问控制
- User endpoints: 股票搜索、报价、新闻（需要用户认证）
- Admin endpoints: 缓存管理、批量操作（需要管理员权限）
"""

import logging
import os
import re
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field, ValidationError, field_validator

from app.api.auth import User, get_current_user
from app.core.circuit_breaker_manager import get_circuit_breaker  # 导入熔断器
from app.core.exceptions import BusinessException, ForbiddenException, NotFoundException, ValidationException
from app.core.responses import APIResponse, create_error_response
from app.schema import StockListQueryModel  # 导入P0改进的验证模型
from app.services.stock_search_service import get_stock_search_service
from src.core.exceptions import (
    DatabaseNotFoundError,
    DatabaseOperationError,
    DataFetchError,
    DataValidationError,
    NetworkError,
    ServiceError,
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Rate limiting for search operations
search_operation_count = {}

# Search analytics
search_analytics = []


class StockSearchResult(BaseModel):
    """股票搜索结果"""

    symbol: str = Field(..., description="股票代码")
    description: str = Field(..., description="股票名称")
    displaySymbol: str = Field(..., description="显示代码")
    type: str = Field(..., description="类型")
    exchange: str = Field(..., description="交易所")
    market: Optional[str] = Field(None, description="市场")


class StockQuote(BaseModel):
    """股票报价"""

    symbol: Optional[str] = None
    name: Optional[str] = None
    current: float = Field(..., description="当前价格")
    change: float = Field(..., description="涨跌额")
    percent_change: float = Field(..., description="涨跌幅")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    open: float = Field(..., description="开盘价")
    previous_close: float = Field(..., description="昨收")
    volume: Optional[float] = Field(None, description="成交量")
    amount: Optional[float] = Field(None, description="成交额")
    timestamp: float = Field(..., description="时间戳")


class NewsItem(BaseModel):
    """新闻条目"""

    headline: str = Field(..., description="标题", max_length=200)
    summary: str = Field(..., description="摘要", max_length=1000)
    source: str = Field(..., description="来源", max_length=100)
    datetime: float = Field(..., description="时间戳")
    url: str = Field(..., description="链接", max_length=500)
    image: Optional[str] = Field(None, description="图片", max_length=500)
    category: Optional[str] = Field(None, description="分类", max_length=50)

    @field_validator("headline")
    @classmethod
    def validate_headline(cls, v: str) -> str:
        """验证新闻标题"""
        if not v.strip():
            raise ValueError("新闻标题不能为空")

        # 检查是否包含恶意脚本
        if re.search(r"<script|javascript:|onload=|onerror=", v, re.IGNORECASE):
            raise ValueError("新闻标题包含不安全的脚本或标签")

        return v.strip()

    @field_validator("summary")
    @classmethod
    def validate_summary(cls, v: str) -> str:
        """验证新闻摘要"""
        if not v.strip():
            raise ValueError("新闻摘要不能为空")

        # 检查是否包含恶意脚本
        if re.search(r"<script|javascript:|onload=|onerror=", v, re.IGNORECASE):
            raise ValueError("新闻摘要包含不安全的脚本或标签")

        return v.strip()


class SearchRequest(BaseModel):
    """搜索请求模型"""

    query: str = Field(..., description="搜索关键词", min_length=1, max_length=100)
    market: str = Field("auto", description="市场类型", pattern=r"^(auto|cn|hk)$")
    limit: int = Field(20, description="返回结果数量", ge=1, le=100)

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """验证搜索关键词"""
        if not v.strip():
            raise ValueError("搜索关键词不能为空")

        # 移除特殊字符，防止SQL注入
        v = re.sub(r'[<>"\'/\\]', "", v)

        # 检查长度
        if len(v.strip()) > 100:
            raise ValueError("搜索关键词过长，最多100个字符")

        return v.strip()


# ============================================================================
# Security Helper Functions
# ============================================================================


def check_search_rate_limit(user_id: int, max_searches_per_minute: int = 30) -> bool:
    """
    检查搜索操作频率限制

    Args:
        user_id: 用户ID
        max_searches_per_minute: 每分钟最大搜索数

    Returns:
        bool: 是否允许搜索
    """
    current_time = int(time.time() / 60)  # 分钟级时间窗口

    if user_id not in search_operation_count:
        search_operation_count[user_id] = {}

    if current_time not in search_operation_count[user_id]:
        search_operation_count[user_id][current_time] = 0

    search_operation_count[user_id][current_time] += 1

    # 清理过期的时间窗口
    for old_time in list(search_operation_count[user_id].keys()):
        if current_time - old_time > 5:  # 保留5分钟内的记录
            del search_operation_count[user_id][old_time]

    return search_operation_count[user_id][current_time] <= max_searches_per_minute


def check_admin_privileges(user: User) -> bool:
    """检查管理员权限"""
    return user.role in ["admin", "backup_operator"]


def log_search_operation(user: User, operation: str, query: Optional[str] = None, details: Optional[Dict] = None):
    """
    记录搜索操作分析

    Args:
        user: 操作用户
        operation: 操作类型
        query: 搜索查询（可选）
        details: 操作详情（可选）
    """
    analytics_entry = {
        "timestamp": time.time(),
        "user_id": user.id,
        "username": user.username,
        "operation": operation,
        "query": query,
        "details": details,
        "ip_address": getattr(user, "ip_address", "unknown"),
    }

    search_analytics.append(analytics_entry)

    # 限制分析数据大小，保留最近1000条记录
    if len(search_analytics) > 1000:
        search_analytics.pop(0)

    logger.info("Search operation logged: {operation} by {user.username}", analytics_data=analytics_entry)


def validate_stock_symbol(symbol: str, market: str) -> str:
    """
    验证股票代码格式

    Args:
        symbol: 股票代码
        market: 市场类型

    Returns:
        str: 验证后的股票代码
    """
    if not symbol:
        raise ValueError("股票代码不能为空")

    symbol = symbol.strip().upper()

    if market.lower() == "cn":
        # A股代码验证 (6位数字)
        if not re.match(r"^\d{6}$", symbol):
            raise ValueError("A股代码格式错误，应为6位数字")

    elif market.lower() == "hk":
        # 港股代码验证 (5位数字或4位数字+字母)
        if not re.match(r"^\d{4,5}$|^\d{4}[A-Z]$", symbol):
            raise ValueError("港股代码格式错误，应为4-5位数字或4位数字+字母")

    return symbol


def sanitize_query_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    清理查询参数

    Args:
        params: 原始查询参数

    Returns:
        Dict: 清理后的参数
    """
    sanitized = {}
    for key, value in params.items():
        if isinstance(value, str):
            # 移除潜在的SQL注入和XSS攻击字符
            value = re.sub(r'[<>"\'/\\;]', "", value)
            sanitized[key] = value.strip()
        else:
            sanitized[key] = value
    return sanitized


@router.get("/search", response_model=List[StockSearchResult])
async def search_stocks(
    q: str = Query(..., description="搜索关键词", min_length=1, max_length=100),
    market: str = Query("auto", description="市场类型: auto, cn, hk", pattern=r"^(auto|cn|hk)$"),
    page: int = Query(1, description="页码", ge=1, le=10000),
    page_size: int = Query(20, description="每页数量", ge=1, le=100),
    sort_by: str = Query("relevance", description="排序字段"),
    sort_order: str = Query("desc", description="排序顺序: asc, desc"),
    current_user: User = Depends(get_current_user),
) -> List[Dict]:
    """
    搜索股票

    Security:
        - 需要用户认证
        - 搜索频率限制
        - 搜索关键词验证和清理
        - 操作分析记录

    支持：
    - A 股：股票代码或名称
    - H 股（港股）：股票代码或名称
    """
    try:
        # 检查搜索频率限制
        if not check_search_rate_limit(current_user.id, max_searches_per_minute=30):
            raise BusinessException(
                detail="搜索频率过高，请稍后再试", status_code=429, error_code="RATE_LIMIT_EXCEEDED"
            )

        # 使用 StockListQueryModel 验证参数
        try:
            validated_params = StockListQueryModel(
                query=q, page=page, page_size=page_size, sort_by=sort_by, sort_order=sort_order
            )
        except ValidationError as ve:
            error_details = [{"field": str(err["loc"][0]), "message": err["msg"]} for err in ve.errors()]
            return create_error_response(
                error_code="VALIDATION_ERROR", message="输入参数验证失败", details=error_details
            )

        # 清理搜索关键词，防止注入攻击
        clean_query = re.sub(r'[<>"\'/\\;]', "", validated_params.query.strip())
        if len(clean_query) > 100:
            raise ValidationException(detail="搜索关键词过长，最多100个字符", field="search")

        # 记录搜索操作分析
        log_search_operation(
            user=current_user,
            operation="search_stocks",
            query=clean_query,
            details={
                "market": market,
                "page": validated_params.page,
                "page_size": validated_params.page_size,
                "sort_by": validated_params.sort_by,
                "sort_order": validated_params.sort_order,
                "original_length": len(q),
                "cleaned_length": len(clean_query),
            },
        )

        # 清理查询参数
        params = sanitize_query_params({"market": market, "limit": validated_params.page_size})

        # 检查是否使用Mock数据
        use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

        if use_mock:
            # 使用Mock数据
            from app.mock.unified_mock_data import get_mock_data_manager

            mock_manager = get_mock_data_manager()
            mock_data = mock_manager.get_data("stock_search", keyword=clean_query, **params)
            results = mock_data.get("data", [])

            # 应用分页
            offset = (validated_params.page - 1) * validated_params.page_size
            return results[offset : offset + validated_params.page_size]
        else:
            # P0改进 Task 3: 使用熔断器保护外部API调用
            circuit_breaker = get_circuit_breaker("stock_search")

            if circuit_breaker.is_open():
                # 熔断器打开，降级到Mock数据
                logger.warning("⚠️ Circuit breaker for stock_search is OPEN, falling back to mock data")
                from app.mock.unified_mock_data import get_mock_data_manager

                mock_manager = get_mock_data_manager()
                mock_data = mock_manager.get_data("stock_search", keyword=clean_query, **params)
                results = mock_data.get("data", [])

                # 应用分页
                offset = (validated_params.page - 1) * validated_params.page_size
                return results[offset : offset + validated_params.page_size]

            # 正常获取真实数据
            service = get_stock_search_service()
            try:
                results = service.unified_search(
                    clean_query,
                    market=market,
                    limit=validated_params.page_size,
                    offset=(validated_params.page - 1) * validated_params.page_size,
                )
                circuit_breaker.record_success()
            except (DataFetchError, ServiceError, NetworkError) as api_error:
                circuit_breaker.record_failure()
                logger.error(
                    f"❌ Stock search API failed: {api_error.message}, failures: {circuit_breaker.failure_count}",
                    extra=api_error.to_dict(),
                )
                raise BusinessException(
                    detail="股票搜索服务暂时不可用，请稍后重试", status_code=503, error_code="SERVICE_UNAVAILABLE"
                )
            except Exception as api_error:
                circuit_breaker.record_failure()
                logger.error(
                    f"❌ Stock search API failed with unexpected error: {str(api_error)}, "
                    f"failures: {circuit_breaker.failure_count}"
                )
                raise BusinessException(detail="股票搜索失败，请稍后重试", status_code=500, error_code="SEARCH_FAILED")

            # 应用排序
            if validated_params.sort_by and validated_params.sort_by != "relevance":
                reverse = validated_params.sort_order.lower() == "desc"
                results = sorted(results, key=lambda x: x.get(validated_params.sort_by, 0), reverse=reverse)

            return results

    except HTTPException:
        raise
    except (DataFetchError, DataValidationError, ServiceError) as e:
        logger.error("Stock search failed for user {current_user.username}: {e.message}", extra=e.to_dict())
        raise BusinessException(
            detail="搜索参数无效或数据源暂时不可用，请稍后重试", status_code=400, error_code="INVALID_SEARCH_PARAMS"
        )
    except Exception as e:
        logger.error("Stock search failed for user {current_user.username}: {str(e)}")
        raise BusinessException(detail="搜索失败，请稍后重试", status_code=500, error_code="SEARCH_FAILED")


@router.get("/quote/{symbol}", response_model=StockQuote)
async def get_stock_quote(
    symbol: str,
    market: str = Query("cn", description="市场类型: cn, hk", pattern=r"^(cn|hk)$"),
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    获取股票实时报价

    Security:
        - 需要用户认证
        - 股票代码格式验证
        - 访问频率限制
        - 操作分析记录

    Args:
        symbol: 股票代码
        market: 市场类型（cn=A股, hk=港股）
    """
    try:
        # 检查访问频率限制
        if not check_search_rate_limit(current_user.id, max_searches_per_minute=60):
            raise BusinessException(
                detail="访问频率过高，请稍后再试", status_code=429, error_code="RATE_LIMIT_EXCEEDED"
            )

        # 验证股票代码格式
        validated_symbol = validate_stock_symbol(symbol, market)

        # 记录操作分析
        log_search_operation(
            user=current_user,
            operation="get_stock_quote",
            query=validated_symbol,
            details={"market": market, "original_symbol": symbol, "validated_symbol": validated_symbol},
        )

        # 检查是否使用Mock数据
        use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

        if use_mock:
            # 使用Mock数据
            from app.mock.unified_mock_data import get_mock_data_manager

            mock_manager = get_mock_data_manager()
            mock_data = mock_manager.get_data("stock_quote", symbol=validated_symbol, market=market)
            quote_data = mock_data.get("data", {})

            if not quote_data:
                raise NotFoundException(resource="股票报价", identifier="查询条件")

            return quote_data
        else:
            # 正常获取真实数据
            service = get_stock_search_service()

            if market.lower() == "cn":
                quote = service.get_a_stock_realtime(validated_symbol)
            elif market.lower() == "hk":
                quote = service.get_hk_stock_realtime(validated_symbol)
            else:
                raise ValidationException(detail="不支持的市场类型，仅支持: cn, hk", field="market")

            if not quote:
                raise NotFoundException(resource="股票报价", identifier="查询条件")

            return quote

    except HTTPException:
        raise
    except ValueError as e:
        raise BusinessException(detail=str(e), status_code=400, error_code="VALIDATION_ERROR")
    except (DataFetchError, NetworkError, ServiceError) as e:
        logger.error(
            f"Get stock quote failed for user {current_user.username}, symbol {symbol}: {e.message}", extra=e.to_dict()
        )
        raise BusinessException(
            detail="数据源暂时不可用，请稍后重试", status_code=503, error_code="SERVICE_UNAVAILABLE"
        )
    except Exception as e:
        logger.error("Get stock quote failed for user {current_user.username}, symbol %(symbol)s: {str(e)}")
        raise BusinessException(detail="获取报价失败，请稍后重试", status_code=500, error_code="QUOTE_RETRIEVAL_FAILED")


@router.get("/profile/{symbol}")
async def get_company_profile(
    symbol: str,
    market: str = Query("cn", description="市场类型: cn, hk"),
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    获取公司基本信息

    Args:
        symbol: 股票代码
        market: 市场类型
    """
    try:
        # 检查是否使用Mock数据
        use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

        if use_mock:
            # 使用Mock数据
            from app.mock.unified_mock_data import get_mock_data_manager

            mock_manager = get_mock_data_manager()
            mock_data = mock_manager.get_data("stock_profile", symbol=symbol, market=market)
            return mock_data.get("data", {})
        else:
            # 正常获取真实数据
            raise BusinessException(
                detail="公司基本信息功能暂不支持，本系统仅支持 A 股和 H 股（港股），不支持美股",
                status_code=501,
                error_code="FEATURE_NOT_SUPPORTED",
            )
    except (BusinessException, ValidationException, NotFoundException, ForbiddenException):
        raise
    except (DataFetchError, ServiceError) as e:
        logger.error("Get company profile failed for symbol {symbol}: {e.message}", extra=e.to_dict())
        raise BusinessException(
            detail="公司信息服务暂时不可用，请稍后重试", status_code=503, error_code="COMPANY_INFO_SERVICE_UNAVAILABLE"
        )
    except Exception as e:
        logger.error("Get company profile failed for symbol %(symbol)s: {str(e)}")
        raise BusinessException(
            detail="获取公司信息失败，请稍后重试", status_code=500, error_code="COMPANY_INFO_RETRIEVAL_FAILED"
        )


@router.get("/news/{symbol}", response_model=List[NewsItem])
async def get_stock_news(
    symbol: str,
    market: str = Query("cn", description="市场类型: cn, hk"),
    days: int = Query(7, description="获取最近几天的新闻", ge=1, le=30),
    current_user: User = Depends(get_current_user),
) -> List[Dict]:
    """
    获取股票新闻

    Args:
        symbol: 股票代码
        market: 市场类型（cn=A股, hk=港股）
        days: 获取最近几天的新闻
    """
    try:
        # 检查是否使用Mock数据
        use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

        if use_mock:
            # 使用Mock数据
            from app.mock.unified_mock_data import get_mock_data_manager

            mock_manager = get_mock_data_manager()
            mock_data = mock_manager.get_data("stock_news", symbol=symbol, market=market, days=days)
            return mock_data.get("data", [])
        else:
            # 正常获取真实数据
            service = get_stock_search_service()

            if market.lower() == "cn":
                news = service.get_a_stock_news(symbol, days=days)
            elif market.lower() == "hk":
                news = service.get_hk_stock_news(symbol)
            else:
                raise ValidationException(detail="不支持的市场类型，仅支持: cn, hk", field="market")

            return news
    except (DataFetchError, ServiceError, NetworkError) as e:
        logger.error("Get stock news failed for symbol {symbol}: {e.message}", extra=e.to_dict())
        raise BusinessException(
            detail="新闻服务暂时不可用，请稍后重试", status_code=503, error_code="NEWS_SERVICE_UNAVAILABLE"
        )
    except Exception as e:
        logger.error("Get stock news failed for symbol %(symbol)s: {str(e)}")
        raise BusinessException(detail="获取新闻失败，请稍后重试", status_code=500, error_code="NEWS_RETRIEVAL_FAILED")


@router.get("/news/market/{category}", response_model=List[NewsItem])
async def get_market_news(
    category: str = "general",
    market: str = Query("cn", description="市场类型: cn, hk"),
    current_user: User = Depends(get_current_user),
) -> List[Dict]:
    """
    获取市场新闻

    Args:
        category: 新闻类别
        market: 市场类型（cn=A股, hk=港股）
    """
    try:
        service = get_stock_search_service()

        if market.lower() == "cn":
            news = service.get_a_stock_news(days=7)
        elif market.lower() == "hk":
            news = service.get_hk_stock_news()
        else:
            raise ValidationException(detail="不支持的市场类型，仅支持: cn, hk", field="market")

        return news
    except (DataFetchError, ServiceError, NetworkError) as e:
        logger.error("Get market news failed for category {category}: {e.message}", extra=e.to_dict())
        raise BusinessException(
            detail="市场新闻服务暂时不可用，请稍后重试", status_code=503, error_code="MARKET_NEWS_SERVICE_UNAVAILABLE"
        )
    except Exception as e:
        logger.error("Get market news failed for category %(category)s: {str(e)}")
        raise BusinessException(
            detail="获取市场新闻失败，请稍后重试", status_code=500, error_code="MARKET_NEWS_RETRIEVAL_FAILED"
        )


@router.get("/recommendation/{symbol}")
async def get_recommendation_trends(symbol: str, current_user: User = Depends(get_current_user)) -> Dict:
    """
    获取分析师推荐趋势

    Args:
        symbol: 股票代码
    """
    try:
        # 检查是否使用Mock数据
        use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

        if use_mock:
            # 使用Mock数据
            from app.mock.unified_mock_data import get_mock_data_manager

            mock_manager = get_mock_data_manager()
            mock_data = mock_manager.get_data("stock_recommendation", symbol=symbol)
            return mock_data.get("data", {})
        else:
            # 正常获取真实数据
            raise BusinessException(
                detail="分析师推荐功能暂不支持，本系统仅支持 A 股和 H 股（港股），不支持美股",
                status_code=501,
                error_code="FEATURE_NOT_SUPPORTED",
            )
    except HTTPException:
        raise
    except (DataFetchError, ServiceError) as e:
        logger.error("Get recommendation trends failed for symbol {symbol}: {e.message}", extra=e.to_dict())
        raise BusinessException(
            detail="推荐分析服务暂时不可用，请稍后重试",
            status_code=503,
            error_code="RECOMMENDATION_SERVICE_UNAVAILABLE",
        )
    except Exception as e:
        logger.error("Get recommendation trends failed for symbol %(symbol)s: {str(e)}")
        raise BusinessException(
            detail="获取分析师推荐失败，请稍后重试", status_code=500, error_code="RECOMMENDATION_RETRIEVAL_FAILED"
        )


@router.post("/cache/clear", response_model=APIResponse)
async def clear_search_cache(current_user: User = Depends(get_current_user)) -> APIResponse:
    """
    清除搜索缓存

    Security:
        - 仅管理员可访问
        - 需要管理员权限
        - 操作审计记录
    """
    try:
        # 检查管理员权限
        if not check_admin_privileges(current_user):
            logger.warning("Unauthorized cache clear attempt by user: {current_user.username}")
            raise ForbiddenException(detail="需要管理员权限访问此端点")

        # 记录操作分析
        log_search_operation(user=current_user, operation="clear_search_cache", details={"admin_action": True})

        service = get_stock_search_service()
        service.clear_cache()

        logger.info("Search cache cleared by admin: {current_user.username}")

        return APIResponse(success=True, data={"cleared_by": current_user.username}, message="搜索缓存已清除")

    except HTTPException:
        raise
    except (DatabaseNotFoundError, ServiceError) as e:
        logger.error("Failed to clear search cache for admin {current_user.username}: {e.message}", extra=e.to_dict())
        raise BusinessException(detail="清除缓存失败", status_code=500, error_code="CACHE_CLEAR_FAILED")
    except Exception as e:
        logger.error("Failed to clear search cache for admin {current_user.username}: {str(e)}")
        raise BusinessException(detail="清除缓存失败", status_code=500, error_code="CACHE_CLEAR_FAILED")


# ==================== 管理员专用分析端点 ====================


@router.get("/analytics/searches", response_model=Dict[str, Any])
async def get_search_analytics(
    limit: int = Query(100, description="返回记录数", ge=1, le=500),
    operation: Optional[str] = Query(None, description="操作类型过滤"),
    username: Optional[str] = Query(None, description="用户名过滤"),
    current_user: User = Depends(get_current_user),
):
    """
    获取搜索操作分析数据

    Security:
        - 仅管理员可访问
        - 需要管理员权限
        - 支持过滤查询
    """
    try:
        # 检查管理员权限
        if not check_admin_privileges(current_user):
            logger.warning("Unauthorized analytics access attempt by user: {current_user.username}")
            raise ForbiddenException(detail="需要管理员权限访问此端点")

        # 记录分析访问
        log_search_operation(
            user=current_user,
            operation="access_search_analytics",
            details={"limit": limit, "operation_filter": operation, "username_filter": username},
        )

        # 过滤分析数据
        filtered_analytics = search_analytics.copy()

        if operation:
            filtered_analytics = [entry for entry in filtered_analytics if entry.get("operation") == operation]

        if username:
            filtered_analytics = [entry for entry in filtered_analytics if entry.get("username") == username]

        # 按时间倒序排列，取最近的记录
        filtered_analytics.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

        # 返回指定的记录数
        result_analytics = filtered_analytics[:limit]

        # 计算统计信息
        operation_counts = {}
        user_counts = {}
        for entry in filtered_analytics:
            op = entry.get("operation", "unknown")
            user = entry.get("username", "unknown")
            operation_counts[op] = operation_counts.get(op, 0) + 1
            user_counts[user] = user_counts.get(user, 0) + 1

        logger.info("Search analytics accessed by admin {current_user.username}: {len(result_analytics)} records")

        return {
            "analytics": result_analytics,
            "total_count": len(filtered_analytics),
            "statistics": {
                "operation_counts": operation_counts,
                "user_counts": dict(sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:10]),  # Top 10 users
            },
            "filter_applied": {"operation": operation, "username": username},
            "returned_count": len(result_analytics),
        }

    except HTTPException:
        raise
    except (DatabaseNotFoundError, DataValidationError) as e:
        logger.error(
            f"Failed to get search analytics for admin {current_user.username}: {e.message}", extra=e.to_dict()
        )
        raise BusinessException(
            detail="获取搜索分析数据失败", status_code=500, error_code="SEARCH_ANALYTICS_DATA_RETRIEVAL_FAILED"
        )
    except Exception as e:
        logger.error("Failed to get search analytics for admin {current_user.username}: {str(e)}")
        raise BusinessException(
            detail="获取搜索分析数据失败", status_code=500, error_code="SEARCH_ANALYTICS_DATA_RETRIEVAL_FAILED"
        )


@router.post("/analytics/cleanup", response_model=APIResponse)
async def cleanup_search_analytics(
    days: int = Query(7, description="保留最近几天的数据", ge=1, le=30), current_user: User = Depends(get_current_user)
):
    """
    清理旧的搜索分析数据

    Security:
        - 仅管理员可访问
        - 需要管理员权限
    """
    try:
        # 检查管理员权限
        if not check_admin_privileges(current_user):
            logger.warning("Unauthorized analytics cleanup attempt by user: {current_user.username}")
            raise ForbiddenException(detail="需要管理员权限访问此端点")

        # 计算清理时间点
        cutoff_time = time.time() - (days * 24 * 60 * 60)

        # 清理旧的分析数据
        original_count = len(search_analytics)
        search_analytics[:] = [entry for entry in search_analytics if entry.get("timestamp", 0) >= cutoff_time]
        cleaned_count = original_count - len(search_analytics)

        # 记录清理操作
        log_search_operation(
            user=current_user,
            operation="cleanup_search_analytics",
            details={"days": days, "cleaned_count": cleaned_count, "remaining_count": len(search_analytics)},
        )

        logger.info("Search analytics cleaned by admin {current_user.username}: %(cleaned_count)s records removed")

        return APIResponse(
            success=True,
            data={"cleaned_count": cleaned_count, "remaining_count": len(search_analytics), "cutoff_days": days},
            message=f"已清理 {cleaned_count} 条旧搜索分析数据",
        )

    except HTTPException:
        raise
    except (DatabaseNotFoundError, DatabaseOperationError) as e:
        logger.error(
            f"Failed to cleanup search analytics for admin {current_user.username}: {e.message}", extra=e.to_dict()
        )
        raise BusinessException(
            detail="清理搜索分析数据失败", status_code=500, error_code="SEARCH_ANALYTICS_DATA_CLEANUP_FAILED"
        )
    except Exception as e:
        logger.error("Failed to cleanup search analytics for admin {current_user.username}: {str(e)}")
        raise BusinessException(
            detail="清理搜索分析数据失败", status_code=500, error_code="SEARCH_ANALYTICS_DATA_CLEANUP_FAILED"
        )


@router.get("/rate-limits/status", response_model=APIResponse)
async def get_rate_limits_status(
    user_id: Optional[int] = Query(None, description="查询特定用户的限制状态"),
    current_user: User = Depends(get_current_user),
):
    """
    获取访问频率限制状态

    Security:
        - 仅管理员可访问
        - 需要管理员权限
    """
    try:
        # 检查管理员权限
        if not check_admin_privileges(current_user):
            logger.warning("Unauthorized rate limits access attempt by user: {current_user.username}")
            raise ForbiddenException(detail="需要管理员权限访问此端点")

        # 获取频率限制状态
        if user_id:
            # 查询特定用户
            user_limits = search_operation_count.get(user_id, {})
            return APIResponse(
                success=True,
                data={"user_id": user_id, "rate_limits": user_limits, "total_minutes": len(user_limits)},
                message=f"用户 {user_id} 的频率限制状态",
            )
        else:
            # 查询所有用户
            all_limits = {}
            for uid, limits in search_operation_count.items():
                all_limits[uid] = {
                    "rate_limits": limits,
                    "total_minutes": len(limits),
                    "current_minute_requests": limits.get(int(time.time() / 60), 0),
                }

            return APIResponse(
                success=True,
                data={"total_users": len(all_limits), "user_limits": all_limits},
                message="所有用户的频率限制状态",
            )

    except HTTPException:
        raise
    except (DatabaseNotFoundError, DataValidationError) as e:
        logger.error(
            f"Failed to get rate limits status for admin {current_user.username}: {e.message}", extra=e.to_dict()
        )
        raise BusinessException(
            detail="获取频率限制状态失败", status_code=500, error_code="RATE_LIMIT_STATUS_RETRIEVAL_FAILED"
        )
    except Exception as e:
        logger.error("Failed to get rate limits status for admin {current_user.username}: {str(e)}")
        raise BusinessException(
            detail="获取频率限制状态失败", status_code=500, error_code="RATE_LIMIT_STATUS_RETRIEVAL_FAILED"
        )
