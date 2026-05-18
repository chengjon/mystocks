"""
# pylint: disable=no-member  # TODO owner=search-platform issue=techdebt-expired-markers ttl=2026-06-30: 修复异常类的 to_dict 方法
股票搜索 API
提供统一的股票搜索、报价和新闻接口
支持 A 股和 H 股（港股）

安全级别：分级别访问控制
- User endpoints: 股票搜索、报价、新闻（需要用户认证）
- Admin endpoints: 缓存管理、批量操作（需要管理员权限）
"""

import logging
import re
import time
from typing import Any, Dict, List, Optional  # noqa: F401 — re used inline in search_stocks

from fastapi import APIRouter, Depends, Path, Query
from pydantic import ValidationError

from app.api.auth import User, get_current_user
from app.api.stock_search.openapi_metadata import (
    CACHE_CLEAR_RESPONSES,
    MARKET_NEWS_RESPONSES,
    RECOMMENDATION_RESPONSES,
    SEARCH_ANALYTICS_CLEANUP_RESPONSES,
    SEARCH_ANALYTICS_RESPONSES,
    STOCK_NEWS_RESPONSES,
    STOCK_PROFILE_RESPONSES,
    STOCK_QUOTE_RESPONSES,
    STOCK_SEARCH_RESPONSES,
)
from app.api.stock_search.stock_search_schemas import NewsItem, StockQuote, StockSearchResult
from app.api.stock_search.stock_search_support import (
    _get_mock_stock_data,
    _get_mock_stock_search_results,
    _is_stock_search_mock_enabled,
    _is_stock_search_mock_fallback_enabled,
    check_admin_privileges,
    check_search_rate_limit,
    log_search_operation,
    sanitize_query_params,
    search_analytics,
    validate_stock_symbol,
)
from app.core.circuit_breaker_manager import get_circuit_breaker  # 导入熔断器
from app.core.exceptions import BusinessException, ForbiddenException, NotFoundException, ValidationException
from app.core.responses import UnifiedResponse, create_unified_success_response
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


@router.get(
    "/search",
    response_model=List[StockSearchResult],
    summary="搜索A股与港股股票",
    description="按股票代码或名称检索 A 股与港股标的，支持市场、分页与排序条件，并对搜索频率进行治理。",
    responses=STOCK_SEARCH_RESPONSES,
)
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
            raise BusinessException(
                detail=f"输入参数验证失败: {error_details}",
                status_code=422,
                error_code="VALIDATION_ERROR",
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

        if _is_stock_search_mock_enabled():
            results = _get_mock_stock_search_results(
                clean_query,
                market=params["market"],
                limit=validated_params.page_size,
            )
            # 应用分页
            offset = (validated_params.page - 1) * validated_params.page_size
            return results[offset : offset + validated_params.page_size]

        # P0改进 Task 3: 使用熔断器保护外部API调用
        circuit_breaker = get_circuit_breaker("stock_search")
        if circuit_breaker.is_open():
            if _is_stock_search_mock_fallback_enabled():
                logger.warning("Circuit breaker for stock_search is OPEN, using configured mock fallback")
                results = _get_mock_stock_search_results(
                    clean_query,
                    market=params["market"],
                    limit=validated_params.page_size,
                )
                offset = (validated_params.page - 1) * validated_params.page_size
                return results[offset : offset + validated_params.page_size]

            raise BusinessException(
                detail="股票搜索服务暂时不可用，请稍后重试",
                status_code=503,
                error_code="SERVICE_UNAVAILABLE",
            )

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
                f"Stock search API failed: {api_error.message}, failures: {circuit_breaker.failure_count}",
                extra=api_error.to_dict(),
            )
            raise BusinessException(
                detail="股票搜索服务暂时不可用，请稍后重试", status_code=503, error_code="SERVICE_UNAVAILABLE"
            )
        except Exception as api_error:
            circuit_breaker.record_failure()
            logger.error(
                f"Stock search API failed with unexpected error: {str(api_error)}, "
                f"failures: {circuit_breaker.failure_count}"
            )
            raise BusinessException(detail="股票搜索失败，请稍后重试", status_code=500, error_code="SEARCH_FAILED")

        if validated_params.sort_by and validated_params.sort_by != "relevance":
            reverse = validated_params.sort_order.lower() == "desc"
            results = sorted(results, key=lambda x: x.get(validated_params.sort_by, 0), reverse=reverse)

        return results

    except BusinessException:
        raise
    except (DataFetchError, DataValidationError, ServiceError) as e:
        logger.error("Stock search failed for user {current_user.username}: {e.message}", extra=e.to_dict())
        raise BusinessException(
            detail="搜索参数无效或数据源暂时不可用，请稍后重试", status_code=400, error_code="INVALID_SEARCH_PARAMS"
        )
    except Exception:
        logger.error("Stock search failed for user {current_user.username}: {str(e)}")
        raise BusinessException(detail="搜索失败，请稍后重试", status_code=500, error_code="SEARCH_FAILED")


@router.get(
    "/quote/{symbol}",
    response_model=StockQuote,
    summary="获取A股或港股实时报价",
    description="返回单只 A 股或港股股票的实时行情快照，包括最新价、涨跌幅、成交量和成交额等关键字段。",
    responses=STOCK_QUOTE_RESPONSES,
)
async def get_stock_quote(
    symbol: str = Path(..., description="股票代码，例如 A股 `600519`、港股 `00700`"),
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

        if _is_stock_search_mock_enabled():
            quote_data = _get_mock_stock_data("stock_quote", symbol=validated_symbol, market=market) or {}

            if not quote_data:
                raise NotFoundException(resource="股票报价", identifier="查询条件")

            return quote_data

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

    except BusinessException:
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
    except Exception:
        logger.error("Get stock quote failed for user {current_user.username}, symbol %(symbol)s: {str(e)}")
        raise BusinessException(detail="获取报价失败，请稍后重试", status_code=500, error_code="QUOTE_RETRIEVAL_FAILED")


@router.get(
    "/profile/{symbol}",
    summary="获取A股或港股公司资料",
    description="返回 A 股或港股股票的公司基础档案。当前真实数据源尚未启用时，仅在显式开启 mock 配置时返回 mock 数据，否则按契约返回 501。",
    responses=STOCK_PROFILE_RESPONSES,
)
async def get_company_profile(
    symbol: str = Path(..., description="股票代码，例如 A股 `600519`、港股 `00700`"),
    market: str = Query("cn", description="市场类型: cn, hk", pattern=r"^(cn|hk)$"),
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    获取公司基本信息

    Args:
        symbol: 股票代码
        market: 市场类型
    """
    try:
        if _is_stock_search_mock_enabled():
            return _get_mock_stock_data("stock_profile", symbol=symbol, market=market) or {}

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
    except Exception:
        logger.error("Get company profile failed for symbol %(symbol)s: {str(e)}")
        raise BusinessException(
            detail="获取公司信息失败，请稍后重试", status_code=500, error_code="COMPANY_INFO_RETRIEVAL_FAILED"
        )


@router.get(
    "/news/{symbol}",
    response_model=List[NewsItem],
    summary="获取A股或港股个股新闻",
    description="返回指定 A 股或港股股票最近数日的新闻列表，适用于个股资讯面板与事件回溯场景。",
    responses=STOCK_NEWS_RESPONSES,
)
async def get_stock_news(
    symbol: str = Path(..., description="股票代码，例如 A股 `600519`、港股 `00700`"),
    market: str = Query("cn", description="市场类型: cn, hk", pattern=r"^(cn|hk)$"),
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
        if _is_stock_search_mock_enabled():
            return _get_mock_stock_data("stock_news", symbol=symbol, market=market, days=days) or []

        service = get_stock_search_service()

        if market.lower() == "cn":
            news = service.get_a_stock_news(symbol, days=days)
        elif market.lower() == "hk":
            news = service.get_hk_stock_news(symbol)
        else:
            raise ValidationException(detail="不支持的市场类型，仅支持: cn, hk", field="market")

        return news
    except BusinessException:
        raise
    except (DataFetchError, ServiceError, NetworkError) as e:
        logger.error("Get stock news failed for symbol {symbol}: {e.message}", extra=e.to_dict())
        raise BusinessException(
            detail="新闻服务暂时不可用，请稍后重试", status_code=503, error_code="NEWS_SERVICE_UNAVAILABLE"
        )
    except Exception:
        logger.error("Get stock news failed for symbol %(symbol)s: {str(e)}")
        raise BusinessException(detail="获取新闻失败，请稍后重试", status_code=500, error_code="NEWS_RETRIEVAL_FAILED")


@router.get(
    "/news/market/{category}",
    response_model=List[NewsItem],
    summary="获取A股或港股市场新闻",
    description="按新闻分类返回 A 股或港股市场级资讯，用于市场概览、主题跟踪和盘中快讯聚合。",
    responses=MARKET_NEWS_RESPONSES,
)
async def get_market_news(
    category: str = Path(..., description="市场新闻分类，例如 `general`、`macro`、`industry`"),
    market: str = Query("cn", description="市场类型: cn, hk", pattern=r"^(cn|hk)$"),
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
    except BusinessException:
        raise
    except (DataFetchError, ServiceError, NetworkError) as e:
        logger.error("Get market news failed for category {category}: {e.message}", extra=e.to_dict())
        raise BusinessException(
            detail="市场新闻服务暂时不可用，请稍后重试", status_code=503, error_code="MARKET_NEWS_SERVICE_UNAVAILABLE"
        )
    except Exception:
        logger.error("Get market news failed for category %(category)s: {str(e)}")
        raise BusinessException(
            detail="获取市场新闻失败，请稍后重试", status_code=500, error_code="MARKET_NEWS_RETRIEVAL_FAILED"
        )


@router.get(
    "/recommendation/{symbol}",
    summary="获取个股分析师推荐趋势",
    description="返回指定股票的分析师评级趋势或 mock 示例，在真实推荐数据源未启用时按契约返回 501。",
    responses=RECOMMENDATION_RESPONSES,
)
async def get_recommendation_trends(
    symbol: str = Path(..., description="股票代码，例如 A股 `600519`、港股 `00700`"),
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    获取分析师推荐趋势

    Args:
        symbol: 股票代码
    """
    try:
        if _is_stock_search_mock_enabled():
            return _get_mock_stock_data("stock_recommendation", symbol=symbol) or {}

        raise BusinessException(
            detail="分析师推荐功能暂不支持，本系统仅支持 A 股和 H 股（港股），不支持美股",
            status_code=501,
            error_code="FEATURE_NOT_SUPPORTED",
        )
    except BusinessException:
        raise
    except (DataFetchError, ServiceError) as e:
        logger.error("Get recommendation trends failed for symbol {symbol}: {e.message}", extra=e.to_dict())
        raise BusinessException(
            detail="推荐分析服务暂时不可用，请稍后重试",
            status_code=503,
            error_code="RECOMMENDATION_SERVICE_UNAVAILABLE",
        )
    except Exception:
        logger.error("Get recommendation trends failed for symbol %(symbol)s: {str(e)}")
        raise BusinessException(
            detail="获取分析师推荐失败，请稍后重试", status_code=500, error_code="RECOMMENDATION_RETRIEVAL_FAILED"
        )


@router.post(
    "/cache/clear",
    response_model=UnifiedResponse,
    summary="清除股票搜索缓存",
    description="管理员清空股票搜索相关缓存，用于数据源切换、异常恢复和排查缓存脏数据。",
    responses=CACHE_CLEAR_RESPONSES,
)
async def clear_search_cache(current_user: User = Depends(get_current_user)) -> UnifiedResponse:
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

        return create_unified_success_response(data={"cleared_by": current_user.username}, message="搜索缓存已清除")

    except BusinessException:
        raise
    except (DatabaseNotFoundError, ServiceError) as e:
        logger.error("Failed to clear search cache for admin {current_user.username}: {e.message}", extra=e.to_dict())
        raise BusinessException(detail="清除缓存失败", status_code=500, error_code="CACHE_CLEAR_FAILED")
    except Exception:
        logger.error("Failed to clear search cache for admin {current_user.username}: {str(e)}")
        raise BusinessException(detail="清除缓存失败", status_code=500, error_code="CACHE_CLEAR_FAILED")


@router.get(
    "/analytics/searches",
    response_model=Dict[str, Any],
    summary="查询股票搜索分析数据",
    description="管理员查询股票搜索行为分析结果，支持按操作类型和用户名过滤，并返回聚合统计。",
    responses=SEARCH_ANALYTICS_RESPONSES,
)
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

    except BusinessException:
        raise
    except (DatabaseNotFoundError, DataValidationError) as e:
        logger.error(
            f"Failed to get search analytics for admin {current_user.username}: {e.message}", extra=e.to_dict()
        )
        raise BusinessException(
            detail="获取搜索分析数据失败", status_code=500, error_code="SEARCH_ANALYTICS_DATA_RETRIEVAL_FAILED"
        )
    except Exception:
        logger.error("Failed to get search analytics for admin {current_user.username}: {str(e)}")
        raise BusinessException(
            detail="获取搜索分析数据失败", status_code=500, error_code="SEARCH_ANALYTICS_DATA_RETRIEVAL_FAILED"
        )


@router.post(
    "/analytics/cleanup",
    response_model=UnifiedResponse,
    summary="清理股票搜索分析数据",
    description="管理员按保留天数清理旧的股票搜索分析记录，控制运营审计数据体积。",
    responses=SEARCH_ANALYTICS_CLEANUP_RESPONSES,
)
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

        return create_unified_success_response(
            data={"cleaned_count": cleaned_count, "remaining_count": len(search_analytics), "cutoff_days": days},
            message=f"已清理 {cleaned_count} 条旧搜索分析数据",
        )

    except BusinessException:
        raise
    except (DatabaseNotFoundError, DatabaseOperationError) as e:
        logger.error(
            f"Failed to cleanup search analytics for admin {current_user.username}: {e.message}", extra=e.to_dict()
        )
        raise BusinessException(
            detail="清理搜索分析数据失败", status_code=500, error_code="SEARCH_ANALYTICS_DATA_CLEANUP_FAILED"
        )
    except Exception:
        logger.error("Failed to cleanup search analytics for admin {current_user.username}: {str(e)}")
        raise BusinessException(
            detail="清理搜索分析数据失败", status_code=500, error_code="SEARCH_ANALYTICS_DATA_CLEANUP_FAILED"
        )
