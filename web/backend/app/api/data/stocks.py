"""
股票基础信息路由 (Stocks Basic Info)
"""
import os
from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Query

from app.core.database import db_service
from app.core.exceptions import BusinessException
from app.core.responses import ErrorCodes, create_error_response
from app.core.security import User, get_current_user

router = APIRouter()


def _runtime_fallback_enabled() -> bool:
    return (
        os.getenv("TESTING", "false").lower() == "true"
        or os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"
    )


def _normalize_market_code(symbol: str, raw_market: str) -> str:
    normalized = raw_market.upper()
    if normalized in {"SH", "SZ"}:
        return normalized
    if "上" in raw_market or symbol.startswith("6"):
        return "SH"
    return "SZ"


def _build_runtime_stocks_basic_result(params: Dict[str, Any]) -> Dict[str, Any]:
    from src.mock.mock_market._market_reference import get_stock_list as get_market_reference_list
    from src.mock.mock_stocks import get_real_time_quote, get_stock_detail, get_stock_list

    limit = int(params.get("limit", 100) or 100)
    offset = int(params.get("offset", 0) or 0)
    search = (params.get("search") or "").strip().lower()
    industry = (params.get("industry") or "").strip()
    market = (params.get("market") or "").strip().upper()
    sort_field = params.get("sort_field")
    sort_order = (params.get("sort_order") or "asc").lower()

    exchange = {"SH": "sh", "SZ": "sz"}.get(market.lower() if market else "")
    fetch_limit = max(limit + offset, 20)
    listing_rows = get_stock_list({"exchange": exchange, "limit": fetch_limit, "offset": 0})
    reference_rows = get_market_reference_list(
        limit=fetch_limit,
        exchange={"SH": "SSE", "SZ": "SZSE"}.get(market),
        search=search or None,
        security_type="股票",
    )
    quote_rows = get_real_time_quote([row["symbol"] for row in listing_rows])
    detail_rows = {row["symbol"]: get_stock_detail({"stock_code": row["symbol"]}) for row in listing_rows}
    references_by_symbol = {row["symbol"]: row for row in reference_rows}
    quotes_by_symbol = {row["symbol"]: row for row in quote_rows}

    rows = []
    for row in listing_rows:
        symbol = str(row.get("symbol", ""))
        quote = quotes_by_symbol.get(symbol, {})
        detail = detail_rows.get(symbol, {})
        reference = references_by_symbol.get(symbol, {})
        normalized = {
            "symbol": symbol,
            "name": row.get("name", symbol),
            "industry": row.get("industry", ""),
            "area": row.get("area", ""),
            "market": _normalize_market_code(symbol, str(row.get("market", ""))),
            "list_date": row.get("list_date"),
            "price": quote.get("price", 0),
            "change": quote.get("change", 0),
            "change_pct": quote.get("change_pct", 0),
            "volume": quote.get("volume", 0),
            "turnover": quote.get("turnover", 0),
            "pe": detail.get("pe_ratio", 0),
            "market_cap": reference.get("market_cap", 0),
            "circulating_market_cap": reference.get("circulating_market_cap", 0),
        }
        rows.append(normalized)

    if search:
        rows = [
            row for row in rows
            if search in str(row["symbol"]).lower() or search in str(row["name"]).lower()
        ]

    if industry:
        rows = [row for row in rows if str(row.get("industry", "")) == industry]

    if market:
        rows = [row for row in rows if str(row.get("market", "")).upper() == market]

    if sort_field and sort_field in {"symbol", "name", "industry", "price", "change_pct", "turnover", "volume"}:
        rows = sorted(rows, key=lambda row: row.get(sort_field) or 0, reverse=sort_order == "desc")

    total = len(rows)
    paginated_rows = rows[offset : offset + limit]

    return {
        "status": "success",
        "data": paginated_rows,
        "total": total,
        "message": f"开发态运行时回退返回 {total} 条股票数据",
        "source": "runtime_fallback",
    }

@router.get("/stocks/basic")
async def get_stocks_basic(
    limit: int = Query(100, ge=1, le=1000, description="返回记录数限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    search: Optional[str] = Query(None, description="股票代码或名称搜索关键词"),
    industry: Optional[str] = Query(None, description="行业筛选"),
    concept: Optional[str] = Query(None, description="概念筛选"),
    market: Optional[str] = Query(None, description="市场筛选: SH/SZ"),
    sort_field: Optional[str] = Query(
        None, description="排序字段: symbol,name,industry,price,change_pct,turnover,volume"
    ),
    sort_order: Optional[str] = Query(None, description="排序方向: asc,desc"),
    current_user: User = Depends(get_current_user),
):
    """获取股票基本信息列表"""
    params = {
        "limit": limit,
        "offset": offset,
        "search": search,
        "industry": industry,
        "concept": concept,
        "market": market,
        "sort_field": sort_field,
        "sort_order": sort_order,
    }
    try:
        from app.services.data_source_factory import get_data_source_factory

        factory = await get_data_source_factory()
        result = await factory.get_data("data", "stocks/basic", params)
        if result.get("status") == "success":
            return {
                "success": True,
                "data": result.get("data", []),
                "total": result.get("total", 0),
                "limit": limit,
                "offset": offset,
                "timestamp": datetime.now().isoformat(),
                "source": result.get("source", "data"),
                "message": result.get("message", "查询成功"),
            }
        if _runtime_fallback_enabled():
            fallback_result = _build_runtime_stocks_basic_result(params)
            return {
                "success": True,
                "data": fallback_result.get("data", []),
                "total": fallback_result.get("total", 0),
                "limit": limit,
                "offset": offset,
                "timestamp": datetime.now().isoformat(),
                "source": fallback_result.get("source", "runtime_fallback"),
                "message": fallback_result.get("message", "查询成功"),
            }
        raise BusinessException(detail=result.get("message", "获取股票基本信息失败"), status_code=500)
    except Exception as e:
        if _runtime_fallback_enabled():
            fallback_result = _build_runtime_stocks_basic_result(params)
            return {
                "success": True,
                "data": fallback_result.get("data", []),
                "total": fallback_result.get("total", 0),
                "limit": limit,
                "offset": offset,
                "timestamp": datetime.now().isoformat(),
                "source": fallback_result.get("source", "runtime_fallback"),
                "message": fallback_result.get("message", "查询成功"),
            }
        raise BusinessException(detail=f"查询失败: {str(e)}", status_code=500)

@router.get("/stocks/industries")
async def get_stocks_industries(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """获取所有行业分类列表"""
    try:
        cache_key = "stocks:industries:list"
        cached_data = db_service.get_cache_data(cache_key)
        if cached_data: return cached_data

        df = db_service.query_stocks_basic(limit=10000)
        if df.empty: return {"success": True, "data": [], "total": 0}

        industries = sorted(df["industry"].dropna().unique().tolist())
        industry_list = [{"industry_name": ind, "industry_code": f"IND_{i+1:03d}"} for i, ind in enumerate(industries)]
        result = {"success": True, "data": industry_list, "total": len(industry_list), "timestamp": datetime.now().isoformat()}
        db_service.set_cache_data(cache_key, result, ttl=3600)
        return result
    except Exception as e:
        return create_error_response(ErrorCodes.DATABASE_ERROR, str(e)).model_dump()

@router.get("/stocks/concepts")
async def get_stocks_concepts(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """获取所有概念分类列表"""
    try:
        cache_key = "stocks:concepts:list"
        cached_data = db_service.get_cache_data(cache_key)
        if cached_data: return cached_data

        df = db_service.query_concepts(limit=10000)
        if df.empty: return {"success": True, "data": [], "total": 0}

        concept_list = [{"concept_name": row["name"], "concept_code": row["code"]} for _, row in df.iterrows()]
        result = {"success": True, "data": concept_list, "total": len(concept_list), "timestamp": datetime.now().isoformat()}
        db_service.set_cache_data(cache_key, result, ttl=3600)
        return result
    except Exception as e:
        return create_error_response(ErrorCodes.DATABASE_ERROR, str(e)).model_dump()

@router.get("/stocks/search")
async def search_stocks(
    keyword: str = Query(..., description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """股票搜索接口"""
    try:
        from app.services.data_source_factory import get_data_source_factory
        factory = await get_data_source_factory()
        result = await factory.get_data("data", "stocks/search", {"keyword": keyword, "limit": limit})
        if result.get("status") == "success":
            return {
                "success": True,
                "data": result.get("data", []),
                "keyword": keyword,
                "total": result.get("total", 0),
                "limit": limit,
                "timestamp": datetime.now().isoformat(),
                "source": result.get("source", "data"),
            }
        raise BusinessException(detail="搜索失败", status_code=500)
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500)

@router.get("/stocks/{symbol}/detail")
async def get_stock_detail(symbol: str, current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """获取股票详细信息 — OpenStock 真实数据"""
    try:
        cache_key = f"stock:detail:{symbol}"
        cached_data = db_service.get_cache_data(cache_key)
        if cached_data:
            return cached_data

        # 复用 /market/quotes 的 OpenStock 真实数据管道
        from app.services.data_source_factory import get_data_source_factory
        factory = await get_data_source_factory()
        result = await factory.get_data_with_fallback(
            "openstock_market", "quotes", {"symbols": [symbol]}
        )

        quote = None
        if result.get("status") == "success" and result.get("data"):
            data = result["data"]
            if isinstance(data, list) and data:
                quote = data[0]
            elif isinstance(data, dict):
                quote = data

        if quote:
            stock_detail = {
                "symbol": symbol,
                "name": quote.get("name") or str(symbol),
                "market": "SH" if symbol.startswith("6") else "SZ",
                "price": float(quote.get("last_price", quote.get("price", 0)) or 0),
                "change_pct": float(quote.get("change_percent", quote.get("change_pct", 0)) or 0),
                "volume": int(quote.get("volume", 0) or 0),
                "high": float(quote.get("high", 0) or 0),
                "low": float(quote.get("low", 0) or 0),
                "open": float(quote.get("open", 0) or 0),
                "prev_close": float(quote.get("prev_close", quote.get("pre_close", 0)) or 0),
            }
        else:
            stock_detail = {
                "symbol": symbol,
                "name": str(symbol),
                "market": "SH" if symbol.startswith("6") else "SZ",
                "price": 0, "change_pct": 0,
            }

        result_out = {"success": True, "data": stock_detail, "timestamp": datetime.now().isoformat()}
        db_service.set_cache_data(cache_key, result_out, ttl=300)
        return result_out
    except Exception as e:
        return {"success": False, "msg": str(e)}
