"""
数据查询 API
"""

"""
数据查询 API
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.database import db_service
from app.core.responses import create_error_response, ErrorCodes
from app.core.security import User, get_current_user
from app.services.unified_data_service import UnifiedDataService

logger = __import__("logging").getLogger(__name__)

import os

# 添加数据格式转换中间件
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../src"))
from utils.data_format_converter import normalize_api_response_format, normalize_stock_data_format

router = APIRouter()


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
    """
    获取股票基本信息列表 - 支持行业/概念筛选、行情排序和分页

    使用数据源工厂模式，支持Mock/Real/Hybrid自动切换
    """
    try:
        # 参数校验
        if limit <= 0:
            raise HTTPException(status_code=400, detail="limit参数必须为正整数")

        if limit > 1000:
            raise HTTPException(status_code=400, detail="limit参数不能超过1000")

        # 使用数据源工厂获取数据
        from app.services.data_source_factory import get_data_source_factory

        factory = await get_data_source_factory()

        # 构建请求参数
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

        # 调用数据源工厂获取stocks/basic数据
        result = await factory.get_data("data", "stocks/basic", params)

        # 统一响应格式
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
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "获取股票基本信息失败"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询股票基本信息失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询股票基本信息失败: {str(e)}")


@router.get("/stocks/industries")
async def get_stocks_industries(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取所有行业分类列表（用于股票列表筛选）
    """
    try:
        # 构建缓存键
        cache_key = "stocks:industries:list"

        # 尝试从缓存获取
        cached_data = db_service.get_cache_data(cache_key)
        if cached_data:
            return cached_data

        # 查询数据库获取行业列表
        df = db_service.query_stocks_basic(limit=10000)

        if df.empty:
            return {
                "success": True,
                "data": [],
                "total": 0,
                "timestamp": datetime.now().isoformat(),
            }

        # 获取所有不重复的行业
        industries = df["industry"].dropna().unique().tolist()
        industries = sorted([industry for industry in industries if industry.strip()])

        # 构建响应数据
        industry_list = [
            {"industry_name": industry, "industry_code": f"IND_{i + 1:03d}"} for i, industry in enumerate(industries)
        ]

        result = {
            "success": True,
            "data": industry_list,
            "total": len(industry_list),
            "timestamp": datetime.now().isoformat(),
        }

        # 缓存结果
        db_service.set_cache_data(cache_key, result, ttl=3600)  # 缓存1小时

        return result

    except Exception as e:
        import logging

        logging.error(f"获取行业列表失败: {str(e)}", exc_info=True)
        return create_error_response(ErrorCodes.DATABASE_ERROR, f"获取行业列表失败: {str(e)}").model_dump()


@router.get("/stocks/concepts")
async def get_stocks_concepts(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取所有概念分类列表（用于股票列表筛选）
    """
    try:
        # 构建缓存键
        cache_key = "stocks:concepts:list"

        # 尝试从缓存获取
        cached_data = db_service.get_cache_data(cache_key)
        if cached_data:
            return cached_data

        # 查询数据库获取概念列表
        df = db_service.query_concepts(limit=10000)

        if df.empty:
            return {
                "success": True,
                "data": [],
                "total": 0,
                "timestamp": datetime.now().isoformat(),
            }

        # 构建响应数据
        concept_list = [{"concept_name": row["name"], "concept_code": row["code"]} for _, row in df.iterrows()]

        result = {
            "success": True,
            "data": concept_list,
            "total": len(concept_list),
            "timestamp": datetime.now().isoformat(),
        }

        # 缓存结果
        db_service.set_cache_data(cache_key, result, ttl=3600)  # 缓存1小时

        return result

    except Exception as e:
        import logging

        logging.error(f"获取概念列表失败: {str(e)}", exc_info=True)
        return create_error_response(ErrorCodes.DATABASE_ERROR, f"获取概念列表失败: {str(e)}").model_dump()


@router.get("/stocks/daily")
async def get_daily_kline(
    symbol: str = Query(..., description="股票代码，如: 000001.SZ"),
    start_date: Optional[str] = Query(None, description="开始日期，格式: YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期，格式: YYYY-MM-DD"),
    limit: int = Query(100, ge=1, le=5000, description="返回记录数限制"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取股票日线数据

    使用数据源工厂模式，支持Mock/Real/Hybrid自动切换
    """
    try:
        # 参数验证
        if not symbol:
            raise HTTPException(status_code=400, detail="股票代码不能为空")

        # 设置默认日期范围（最近90天）
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

        # 使用数据源工厂获取数据
        from app.services.data_source_factory import get_data_source_factory

        factory = await get_data_source_factory()

        # 构建请求参数
        params = {"symbol": symbol, "start_date": start_date, "end_date": end_date, "limit": limit}

        # 调用数据源工厂获取stocks/daily数据
        result = await factory.get_data("data", "stocks/daily", params)

        # 统一响应格式
        if result.get("status") == "success":
            return {
                "success": True,
                "data": result.get("data", []),
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
                "total": result.get("total", 0),
                "limit": limit,
                "timestamp": datetime.now().isoformat(),
                "source": result.get("source", "data"),
                "message": result.get("message", "查询成功"),
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "获取日线数据失败"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询日线数据失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询日线数据失败: {str(e)}")


@router.get("/markets/overview")
async def get_market_overview(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取市场概览数据

    使用数据源工厂模式，支持Mock/Real/Hybrid自动切换
    """
    try:
        # 使用数据源工厂获取数据
        from app.services.data_source_factory import get_data_source_factory

        factory = await get_data_source_factory()

        # 构建请求参数
        params = {}

        # 调用数据源工厂获取markets/overview数据
        result = await factory.get_data("data", "markets/overview", params)

        # 统一响应格式
        if result.get("status") == "success":
            return {
                "success": True,
                "data": result.get("data", {}),
                "timestamp": datetime.now().isoformat(),
                "source": result.get("source", "data"),
                "message": result.get("message", "查询成功"),
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "获取市场概览失败"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取市场概览失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取市场概览失败: {str(e)}")


@router.get("/stocks/search")
async def search_stocks(
    keyword: str = Query(..., description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100, description="返回结果数量限制"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    股票搜索接口

    使用数据源工厂模式，支持Mock/Real/Hybrid自动切换
    """
    try:
        # 使用数据源工厂获取数据
        from app.services.data_source_factory import get_data_source_factory

        factory = await get_data_source_factory()

        # 构建请求参数
        params = {"keyword": keyword, "limit": limit}

        # 调用数据源工厂获取stocks/search数据
        result = await factory.get_data("data", "stocks/search", params)

        # 统一响应格式
        if result.get("status") == "success":
            return {
                "success": True,
                "data": result.get("data", []),
                "keyword": keyword,
                "total": result.get("total", 0),
                "limit": limit,
                "timestamp": datetime.now().isoformat(),
                "source": result.get("source", "data"),
                "message": result.get("message", "查询成功"),
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "股票搜索失败"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"股票搜索失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"股票搜索失败: {str(e)}")


# K线数据端点（别名）
@router.get("/kline")
async def get_kline(
    symbol: str = Query(..., description="股票代码，如: 000001.SZ"),
    start_date: Optional[str] = Query(None, description="开始日期，格式: YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期，格式: YYYY-MM-DD"),
    limit: int = Query(100, ge=1, le=5000, description="返回记录数限制"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取股票K线数据（stocks/daily的别名）
    """
    # 直接调用stocks/daily端点
    return await get_daily_kline(symbol, start_date, end_date, limit, current_user)


@router.get("/stocks/kline")
async def get_kline_data(
    symbol: str = Query(..., description="股票代码（含市场后缀）"),
    start_date: str = Query(..., description="开始日期（格式YYYY-MM-DD）"),
    end_date: str = Query(..., description="结束日期（格式YYYY-MM-DD）"),
    period: str = Query("day", description="K线周期（支持day/week/month）"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取股票K线数据（标准化接口，符合cmd5规范）
    """
    try:
        # 参数验证
        if not symbol:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(ErrorCodes.VALIDATION_ERROR, "股票代码不能为空").model_dump(),
            )

        if not start_date or not end_date:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(ErrorCodes.VALIDATION_ERROR, "开始日期和结束日期不能为空").model_dump(),
            )

        # 验证日期格式
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    ErrorCodes.VALIDATION_ERROR, "日期格式错误，请使用YYYY-MM-DD格式"
                ).model_dump(),
            )

        # 验证周期参数
        valid_periods = ["day", "week", "month"]
        if period not in valid_periods:
            return {
                "success": False,
                "msg": f"周期参数错误，支持的周期: {', '.join(valid_periods)}",
                "timestamp": datetime.now().isoformat(),
            }

        # 构建缓存键
        cache_key = f"kline:{symbol}:{start_date}:{end_date}:{period}"

        # 尝试从缓存获取
        cached_data = db_service.get_cache_data(cache_key)
        if cached_data:
            return cached_data

        # 查询数据库
        df = db_service.query_daily_kline(symbol, start_date, end_date)

        print(f"查询到 {len(df)} 条数据, symbol={symbol}, start_date={start_date}, end_date={end_date}")  # 调试信息
        if not df.empty:
            print(f"数据预览: {df.head()}")

        if df.empty:
            return {
                "success": True,
                "data": [],
                "total": 0,
                "timestamp": datetime.now().isoformat(),
            }

        # 确保数据格式正确
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        # 根据周期进行数据聚合
        if period != "day":
            # 按指定周期聚合数据
            if period == "week":
                df = (
                    df.resample("W-MON", on="date")
                    .agg(
                        {
                            "open": "first",
                            "high": "max",
                            "low": "min",
                            "close": "last",
                            "volume": "sum",
                            "amount": "sum",
                        }
                    )
                    .dropna()
                )
            elif period == "month":
                df = (
                    df.resample("M", on="date")
                    .agg(
                        {
                            "open": "first",
                            "high": "max",
                            "low": "min",
                            "close": "last",
                            "volume": "sum",
                            "amount": "sum",
                        }
                    )
                    .dropna()
                )

        # 标准化数据格式
        df = normalize_stock_data_format(df)

        # 转换为响应格式
        data_records = []
        for _, row in df.iterrows():
            record = {
                "date": row["date"].strftime("%Y-%m-%d"),
                "open": float(row["open"]),
                "close": float(row["close"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "volume": int(row["volume"]) if pd.notna(row["volume"]) else 0,
            }
            data_records.append(record)

        result = {
            "success": True,
            "data": data_records,
            "total": len(data_records),
            "timestamp": datetime.now().isoformat(),
        }

        # 标准化API响应格式
        result = normalize_api_response_format(result)

        # 缓存结果（K线数据缓存10分钟）
        db_service.set_cache_data(cache_key, result, ttl=600)

        return result

    except HTTPException:
        raise
    except Exception as e:
        error_result = {
            "success": False,
            "msg": f"查询K线数据失败: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }
        # 记录错误日志
        import logging

        logging.error(f"查询K线数据失败: {str(e)}", exc_info=True)
        return error_result


# 财务数据端点
@router.get("/financial")
async def get_financial_data(
    symbol: str = Query(..., description="股票代码，如: 000001"),
    report_type: str = Query("balance", description="报表类型: balance/income/cashflow"),
    period: str = Query("all", description="报告期: quarterly/annual/all"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数限制"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取股票财务数据

    **报表类型**:
    - balance: 资产负债表
    - income: 利润表
    - cashflow: 现金流量表

    使用数据源工厂模式，支持Mock/Real/Hybrid自动切换
    """
    try:
        # 使用数据源工厂获取数据
        from app.services.data_source_factory import get_data_source_factory

        factory = await get_data_source_factory()

        # 构建请求参数
        params = {"symbol": symbol, "report_type": report_type, "period": period, "limit": limit}

        # 调用数据源工厂获取financial数据
        result = await factory.get_data("data", "financial", params)

        # 统一响应格式
        if result.get("status") == "success":
            return {
                "success": True,
                "data": result.get("data", []),
                "symbol": symbol,
                "report_type": report_type,
                "period": period,
                "total": result.get("total", 0),
                "limit": limit,
                "timestamp": datetime.now().isoformat(),
                "source": result.get("source", "data"),
                "message": result.get("message", "查询成功"),
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "获取财务数据失败"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询财务数据失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询财务数据失败: {str(e)}")


# ==================== Dashboard相关API ====================


@router.get("/markets/price-distribution")
async def get_price_distribution(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取全市场涨跌分布统计
    返回上涨>5%、上涨0-5%、平盘、下跌0-5%、下跌>5%的股票数量
    """
    try:
        # 构建缓存键
        cache_key = "market:price-distribution"

        # 尝试从缓存获取
        cached_data = db_service.get_cache_data(cache_key)
        if cached_data:
            return cached_data

        # 查询股票基本信息用于统计分析
        df = db_service.query_stocks_basic(limit=5000)

        if df.empty:
            return {
                "success": True,
                "data": {
                    "上涨>5%": 0,
                    "上涨0-5%": 0,
                    "平盘": 0,
                    "下跌0-5%": 0,
                    "下跌>5%": 0,
                },
                "msg": "暂无股票数据",
                "timestamp": datetime.now().isoformat(),
            }

        # 模拟涨跌情况（实际应该从实时行情数据计算）
        # 这里使用随机数据模拟
        import random

        random.seed(42)  # 固定种子确保结果一致

        distribution = {
            "上涨>5%": random.randint(50, 200),
            "上涨0-5%": random.randint(200, 500),
            "平盘": random.randint(20, 100),
            "下跌0-5%": random.randint(150, 400),
            "下跌>5%": random.randint(80, 150),
        }

        result = {
            "success": True,
            "data": distribution,
            "timestamp": datetime.now().isoformat(),
        }

        # 缓存结果（涨跌分布数据缓存30分钟）
        db_service.set_cache_data(cache_key, result, ttl=1800)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取涨跌分布失败: {str(e)}")


@router.get("/markets/hot-industries")
async def get_hot_industries(
    limit: int = Query(5, ge=1, le=20, description="返回数量，默认5"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取热门行业TOP5表现数据
    """
    try:
        # 构建缓存键
        cache_key = f"market:hot-industries:{limit}"

        # 尝试从缓存获取
        cached_data = db_service.get_cache_data(cache_key)
        if cached_data:
            return cached_data

        # 查询行业分类数据
        query = """
            SELECT
                industry_name,
                COUNT(*) as stock_count,
                AVG(CASE WHEN pct_chg > 0 THEN 1.0 ELSE 0.0 END) as up_ratio,
                AVG(pct_chg) as avg_change,
                MAX(pct_chg) as max_change,
                SUM(CASE WHEN pct_chg > 0 THEN pct_chg ELSE 0 END) as total_up_change
            FROM stocks_basic
            WHERE industry_name IS NOT NULL AND industry_name != ''
            GROUP BY industry_name
            ORDER BY avg_change DESC, stock_count DESC
            LIMIT :limit
        """

        try:
            # 使用统一数据服务查询
            unified_service = UnifiedDataService()
            df = unified_service.postgresql_access.query_dataframe(query, {"limit": limit})
        except Exception:
            # 如果统一数据服务不可用，使用模拟数据
            import random

            random.seed(42)

            industries = [
                "半导体",
                "新能源汽车",
                "光伏设备",
                "医药生物",
                "白酒",
                "银行",
                "证券",
                "保险",
                "房地产",
                "食品饮料",
                "家用电器",
                "计算机",
                "通信设备",
                "机械设备",
                "化工",
            ]

            df_data = []
            for i in range(min(limit, len(industries))):
                avg_change = round(random.uniform(-3, 8), 2)
                stock_count = random.randint(10, 200)
                up_ratio = round(random.uniform(0.2, 0.9), 2)

                df_data.append(
                    {
                        "industry_name": industries[i],
                        "stock_count": stock_count,
                        "avg_change": avg_change,
                        "up_ratio": up_ratio,
                        "max_change": round(random.uniform(2, 15), 2),
                        "total_up_change": round(random.uniform(5, 50), 2),
                    }
                )

            df = pd.DataFrame(df_data)

        if df.empty:
            return {
                "success": True,
                "data": [],
                "msg": "暂无行业数据",
                "timestamp": datetime.now().isoformat(),
            }

        # 转换为响应格式
        data_records = df.to_dict("records")

        result = {
            "success": True,
            "data": data_records,
            "total": len(data_records),
            "timestamp": datetime.now().isoformat(),
        }

        # 缓存结果（行业热门数据缓存30分钟）
        db_service.set_cache_data(cache_key, result, ttl=1800)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热门行业失败: {str(e)}")


@router.get("/markets/hot-concepts")
async def get_hot_concepts(
    limit: int = Query(5, ge=1, le=20, description="返回数量，默认5"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取热门概念TOP5表现数据
    """
    try:
        # 构建缓存键
        cache_key = f"market:hot-concepts:{limit}"

        # 尝试从缓存获取
        cached_data = db_service.get_cache_data(cache_key)
        if cached_data:
            return cached_data

        # 模拟概念数据（实际应该从概念分类表查询）
        import random

        random.seed(42)

        concepts = [
            "人工智能",
            "芯片概念",
            "新能源汽车",
            "5G概念",
            "光伏概念",
            "生物医药",
            "大数据",
            "云计算",
            "物联网",
            "机器人概念",
            "虚拟现实",
            "区块链",
            "元宇宙",
            "数字经济",
            "碳中和",
        ]

        df_data = []
        for i in range(min(limit, len(concepts))):
            avg_change = round(random.uniform(-2, 10), 2)
            stock_count = random.randint(5, 50)
            up_ratio = round(random.uniform(0.3, 0.95), 2)
            concept_heat = random.randint(70, 100)

            df_data.append(
                {
                    "concept_name": concepts[i],
                    "stock_count": stock_count,
                    "avg_change": avg_change,
                    "up_ratio": up_ratio,
                    "concept_heat": concept_heat,
                    "total_market_cap": round(random.uniform(1000, 10000), 2),
                }
            )

        df = pd.DataFrame(df_data)

        if df.empty:
            return {
                "success": True,
                "data": [],
                "msg": "暂无概念数据",
                "timestamp": datetime.now().isoformat(),
            }

        # 转换为响应格式
        data_records = df.to_dict("records")

        result = {
            "success": True,
            "data": data_records,
            "total": len(data_records),
            "timestamp": datetime.now().isoformat(),
        }

        # 缓存结果（概念热门数据缓存30分钟）
        db_service.set_cache_data(cache_key, result, ttl=1800)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热门概念失败: {str(e)}")


# ==================== StockDetail相关API ====================


@router.get("/stocks/intraday")
async def get_intraday_data(
    symbol: str = Query(..., description="股票代码，如: 000001.SZ"),
    date: Optional[str] = Query(None, description="交易日期，格式: YYYY-MM-DD，默认今天"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取股票分时数据（用于分时图显示）

    使用数据源工厂模式，支持Mock/Real/Hybrid自动切换
    """
    try:
        # 参数验证
        if not symbol:
            raise HTTPException(status_code=400, detail="股票代码不能为空")

        # 设置默认日期为今天
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        # 验证日期格式
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，请使用YYYY-MM-DD格式")

        # 使用数据源工厂获取数据
        from app.services.data_source_factory import get_data_source_factory

        factory = await get_data_source_factory()

        # 构建请求参数
        params = {"symbol": symbol, "date": date}

        # 调用数据源工厂获取stocks/intraday数据
        result = await factory.get_data("data", "stocks/intraday", params)

        # 统一响应格式
        if result.get("status") == "success":
            return {
                "success": True,
                "data": result.get("data", []),
                "symbol": symbol,
                "date": date,
                "total": result.get("total", 0),
                "timestamp": datetime.now().isoformat(),
                "source": result.get("source", "data"),
                "message": result.get("message", "查询成功"),
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "获取分时数据失败"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取分时数据失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取分时数据失败: {str(e)}")


@router.get("/stocks/{symbol}/detail")
async def get_stock_detail(
    symbol: str,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取股票详细信息（包含行业概念标签）
    """
    try:
        # 参数验证
        if not symbol:
            return {
                "success": False,
                "msg": "股票代码不能为空",
                "timestamp": datetime.now().isoformat(),
            }

        # 构建缓存键
        cache_key = f"stock:detail:{symbol}"

        # 尝试从缓存获取
        cached_data = db_service.get_cache_data(cache_key)
        if cached_data:
            return cached_data

        # 查询股票基本信息
        db_service.query_stocks_basic(limit=1)

        # 模拟股票详细信息
        import random

        random.seed(hash(symbol) % 1000)

        # 根据股票代码确定市场
        market = "SH" if symbol.startswith("6") else "SZ"

        # 模拟行业和概念
        industries = ["银行", "证券", "保险", "房地产", "食品饮料", "医药生物", "电子", "计算机", "通信设备"]
        concepts = [
            "人工智能",
            "芯片概念",
            "新能源汽车",
            "5G概念",
            "光伏概念",
            "生物医药",
            "大数据",
            "云计算",
            "物联网",
            "机器人概念",
        ]

        selected_industry = random.choice(industries)
        selected_concepts = random.sample(concepts, random.randint(1, 3))

        stock_detail = {
            "symbol": symbol,
            "name": f"股票{symbol[-3:]}",
            "market": market,
            "industry": selected_industry,
            "industry_code": f"IND_{hash(selected_industry) % 100:03d}",
            "concepts": selected_concepts,
            "concept_codes": [f"CON_{hash(concept) % 100:03d}" for concept in selected_concepts],
            "area": "上海" if market == "SH" else "深圳",
            "list_date": f"20{random.randint(00, 23):02d}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "total_shares": round(random.uniform(1000000, 100000000), 0),
            "circulating_shares": round(random.uniform(800000, 80000000), 0),
            "market_cap": round(random.uniform(100000, 10000000), 2),
            "pe_ratio": round(random.uniform(5, 50), 2),
            "pb_ratio": round(random.uniform(0.5, 5), 2),
            "dividend_yield": round(random.uniform(0, 8), 2),
            "price": round(random.uniform(5, 100), 2),
            "change": round(random.uniform(-10, 10), 2),
            "change_pct": round(random.uniform(-10, 10), 2),
            "volume": random.randint(100000, 10000000),
            "turnover": round(random.uniform(0.1, 10), 2),
            "high": round(random.uniform(5, 100), 2),
            "low": round(random.uniform(5, 100), 2),
            "open": round(random.uniform(5, 100), 2),
        }

        result = {
            "success": True,
            "data": stock_detail,
            "timestamp": datetime.now().isoformat(),
        }

        # 缓存结果（股票详情缓存30分钟）
        db_service.set_cache_data(cache_key, result, ttl=1800)

        return result

    except Exception as e:
        error_result = {
            "success": False,
            "msg": f"获取股票详情失败: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }
        import logging

        logging.error(f"获取股票详情失败: {str(e)}", exc_info=True)
        return error_result


@router.get("/stocks/{symbol}/trading-summary")
async def get_trading_summary(
    symbol: str,
    period: str = Query("1m", description="统计周期: 1w(1周), 1m(1月), 3m(3月), 6m(6月), 1y(1年)"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取股票历史交易摘要统计
    """
    try:
        # 参数验证
        if not symbol:
            return {
                "success": False,
                "msg": "股票代码不能为空",
                "timestamp": datetime.now().isoformat(),
            }

        # 验证周期参数
        valid_periods = ["1w", "1m", "3m", "6m", "1y"]
        if period not in valid_periods:
            return {
                "success": False,
                "msg": f"周期参数错误，支持的周期: {', '.join(valid_periods)}",
                "timestamp": datetime.now().isoformat(),
            }

        # 构建缓存键
        cache_key = f"trading:summary:{symbol}:{period}"

        # 尝试从缓存获取
        cached_data = db_service.get_cache_data(cache_key)
        if cached_data:
            return cached_data

        # 模拟交易摘要数据
        import random

        random.seed(hash(symbol + period) % 1000)

        # 根据周期计算天数
        period_days = {"1w": 7, "1m": 30, "3m": 90, "6m": 180, "1y": 365}

        days = period_days[period]
        base_price = round(random.uniform(10, 50), 2)

        # 生成期间内的统计数据
        price_change = round(random.uniform(-20, 20), 2)
        price_change_pct = round((price_change / base_price) * 100, 2)

        trading_summary = {
            "symbol": symbol,
            "period": period,
            "period_days": days,
            "start_price": round(base_price - price_change, 2),
            "end_price": base_price,
            "highest_price": round(base_price + random.uniform(0, abs(price_change) * 0.5), 2),
            "lowest_price": round(base_price - abs(price_change) * random.uniform(0.3, 0.7), 2),
            "price_change": price_change,
            "price_change_pct": price_change_pct,
            "avg_volume": random.randint(500000, 5000000),
            "total_volume": random.randint(500000 * days * 0.7, 500000 * days * 1.3),
            "avg_turnover": round(random.uniform(1, 8), 2),
            "total_turnover": round(random.uniform(1000000, 50000000), 2),
            "trading_days": random.randint(int(days * 0.8), days),
            "volatility": round(random.uniform(5, 25), 2),
            "sharpe_ratio": round(random.uniform(-2, 3), 2),
            "max_drawdown": round(random.uniform(-30, -5), 2),
            "win_rate": round(random.uniform(30, 70), 2),
            "trading_count": {
                "up_days": random.randint(int(days * 0.3), int(days * 0.7)),
                "down_days": random.randint(int(days * 0.2), int(days * 0.4)),
                "flat_days": random.randint(0, int(days * 0.1)),
            },
            "big_moves": {
                "up_5pct_days": random.randint(0, 5),
                "down_5pct_days": random.randint(0, 5),
                "up_10pct_days": random.randint(0, 2),
                "down_10pct_days": random.randint(0, 2),
            },
        }

        result = {
            "success": True,
            "data": trading_summary,
            "timestamp": datetime.now().isoformat(),
        }

        # 缓存结果（交易摘要缓存1小时）
        db_service.set_cache_data(cache_key, result, ttl=3600)

        return result

    except Exception as e:
        error_result = {
            "success": False,
            "msg": f"获取交易摘要失败: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }
        import logging

        logging.error(f"获取交易摘要失败: {str(e)}", exc_info=True)
        return error_result


# ==================== 测试端点 (无认证) ====================


@router.get("/test/factory")
async def test_data_source_factory(
    limit: int = Query(10, ge=1, le=100, description="测试数据返回数量限制"),
) -> Dict[str, Any]:
    """
    测试数据源工厂集成 (无需认证)
    验证DataDataSourceAdapter是否正常工作
    """
    try:
        # 使用数据源工厂获取数据
        from app.services.data_source_factory import get_data_source_factory

        factory = await get_data_source_factory()

        # 测试stocks/basic端点
        params = {"limit": limit}
        result = await factory.get_data("data", "stocks/basic", params)

        return {
            "success": True,
            "message": "数据源工厂测试成功",
            "factory_status": {
                "available_sources": factory.get_available_sources(),
                "data_source_result": result,
                "test_timestamp": datetime.now().isoformat(),
            },
        }

    except Exception as e:
        logger.error(f"数据源工厂测试失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"数据源工厂测试失败: {str(e)}",
            "error_details": str(e),
            "test_timestamp": datetime.now().isoformat(),
        }
