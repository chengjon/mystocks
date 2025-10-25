"""
数据查询 API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Dict, Any
import pandas as pd
from datetime import datetime, timedelta

from app.core.database import db_service
from app.core.security import get_current_user, User

router = APIRouter()

@router.get("/stocks/basic")
async def get_stocks_basic(
    limit: int = Query(100, ge=1, le=1000, description="返回记录数限制"),
    search: Optional[str] = Query(None, description="股票代码或名称搜索关键词"),
    industry: Optional[str] = Query(None, description="行业筛选"),
    market: Optional[str] = Query(None, description="市场筛选: SH/SZ"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取股票基本信息列表
    """
    try:
        # 构建缓存键
        cache_key = f"stocks:basic:{limit}:{search}:{industry}:{market}"

        # 尝试从缓存获取
        cached_data = db_service.get_cache_data(cache_key)
        if cached_data:
            return cached_data

        # 查询数据库
        df = db_service.query_stocks_basic(limit=1000)  # 先查询更多数据用于筛选

        # 应用筛选条件
        if search:
            search_mask = (
                df['symbol'].str.contains(search, case=False, na=False) |
                df['name'].str.contains(search, case=False, na=False)
            )
            df = df[search_mask]

        if industry:
            df = df[df['industry'] == industry]

        if market:
            df = df[df['market'] == market]

        # 限制返回数量
        df = df.head(limit)

        # 转换为响应格式
        result = {
            "success": True,
            "data": df.to_dict('records'),
            "total": len(df),
            "timestamp": datetime.now().isoformat()
        }

        # 缓存结果
        db_service.set_cache_data(cache_key, result, ttl=600)  # 缓存10分钟

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询股票基本信息失败: {str(e)}")

@router.get("/stocks/daily")
async def get_daily_kline(
    symbol: str = Query(..., description="股票代码，如: 000001.SZ"),
    start_date: Optional[str] = Query(None, description="开始日期，格式: YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期，格式: YYYY-MM-DD"),
    limit: int = Query(100, ge=1, le=5000, description="返回记录数限制"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取股票日线数据
    """
    try:
        # 参数验证
        if not symbol:
            raise HTTPException(status_code=400, detail="股票代码不能为空")

        # 设置默认日期范围（最近90天）
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

        # 构建缓存键
        cache_key = f"daily:{symbol}:{start_date}:{end_date}:{limit}"

        # 尝试从缓存获取
        cached_data = db_service.get_cache_data(cache_key)
        if cached_data:
            return cached_data

        # 查询数据库
        df = db_service.query_daily_kline(symbol, start_date, end_date)

        if df.empty:
            return {
                "success": True,
                "data": [],
                "message": f"未找到股票 {symbol} 在指定时间范围内的数据",
                "timestamp": datetime.now().isoformat()
            }

        # 限制返回数量
        df = df.tail(limit)

        # 确保数据格式正确
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        # 转换为响应格式
        data_records = []
        for _, row in df.iterrows():
            record = {
                "date": row['date'].strftime('%Y-%m-%d'),
                "open": float(row['open']),
                "high": float(row['high']),
                "low": float(row['low']),
                "close": float(row['close']),
                "volume": int(row['volume']) if pd.notna(row['volume']) else 0,
                "amount": float(row['amount']) if pd.notna(row['amount']) else 0.0
            }
            data_records.append(record)

        result = {
            "success": True,
            "data": data_records,
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "total": len(data_records),
            "timestamp": datetime.now().isoformat()
        }

        # 缓存结果（日线数据缓存时间较短）
        db_service.set_cache_data(cache_key, result, ttl=300)  # 缓存5分钟

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询日线数据失败: {str(e)}")

@router.get("/markets/overview")
async def get_market_overview(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取市场概览数据
    """
    try:
        # 构建缓存键
        cache_key = "market:overview"

        # 尝试从缓存获取
        cached_data = db_service.get_cache_data(cache_key)
        if cached_data:
            return cached_data

        # 查询股票基本信息用于统计
        df = db_service.query_stocks_basic(limit=5000)

        if df.empty:
            return {
                "success": True,
                "data": {
                    "total_stocks": 0,
                    "by_market": {},
                    "by_industry": {},
                    "by_area": {}
                },
                "timestamp": datetime.now().isoformat()
            }

        # 统计数据
        total_stocks = len(df)

        # 按市场统计
        by_market = df['market'].value_counts().to_dict()

        # 按行业统计（取前10）
        by_industry = df['industry'].value_counts().head(10).to_dict()

        # 按地区统计（取前10）
        by_area = df['area'].value_counts().head(10).to_dict()

        result = {
            "success": True,
            "data": {
                "total_stocks": total_stocks,
                "by_market": by_market,
                "by_industry": by_industry,
                "by_area": by_area
            },
            "timestamp": datetime.now().isoformat()
        }

        # 缓存结果（市场概览缓存时间较长）
        db_service.set_cache_data(cache_key, result, ttl=3600)  # 缓存1小时

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取市场概览失败: {str(e)}")

@router.get("/stocks/search")
async def search_stocks(
    keyword: str = Query(..., description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100, description="返回结果数量限制"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    股票搜索接口
    """
    try:
        if not keyword or len(keyword.strip()) < 2:
            return {
                "success": True,
                "data": [],
                "message": "搜索关键词至少需要2个字符",
                "timestamp": datetime.now().isoformat()
            }

        # 查询股票基本信息
        df = db_service.query_stocks_basic(limit=5000)

        if df.empty:
            return {
                "success": True,
                "data": [],
                "timestamp": datetime.now().isoformat()
            }

        # 搜索匹配
        keyword = keyword.strip().lower()
        search_mask = (
            df['symbol'].str.lower().str.contains(keyword, na=False) |
            df['name'].str.lower().str.contains(keyword, na=False)
        )

        matched_stocks = df[search_mask].head(limit)

        # 转换为响应格式
        result_data = []
        for _, row in matched_stocks.iterrows():
            result_data.append({
                "symbol": row['symbol'],
                "name": row['name'],
                "industry": row.get('industry', ''),
                "market": row.get('market', ''),
                "area": row.get('area', ''),
                "list_date": row.get('list_date', '')
            })

        result = {
            "success": True,
            "data": result_data,
            "keyword": keyword,
            "total": len(result_data),
            "timestamp": datetime.now().isoformat()
        }

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"股票搜索失败: {str(e)}")


# K线数据端点（别名）
@router.get("/kline")
async def get_kline(
    symbol: str = Query(..., description="股票代码，如: 000001.SZ"),
    start_date: Optional[str] = Query(None, description="开始日期，格式: YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期，格式: YYYY-MM-DD"),
    limit: int = Query(100, ge=1, le=5000, description="返回记录数限制"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取股票K线数据（stocks/daily的别名）
    """
    # 直接调用stocks/daily端点
    return await get_daily_kline(symbol, start_date, end_date, limit, current_user)


# 财务数据端点
@router.get("/financial")
async def get_financial_data(
    symbol: str = Query(..., description="股票代码，如: 000001"),
    report_type: str = Query("balance", description="报表类型: balance/income/cashflow"),
    period: str = Query("all", description="报告期: quarterly/annual/all"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数限制"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取股票财务数据

    **报表类型**:
    - balance: 资产负债表
    - income: 利润表
    - cashflow: 现金流量表

    **数据源**: AkShare财务数据
    """
    try:
        # 使用统一的适配器加载器（移除硬编码路径）
        from app.core.adapter_loader import get_akshare_adapter

        ak = get_akshare_adapter()

        # 根据报表类型获取数据
        if report_type == "balance":
            df = ak.get_balance_sheet(symbol)
        elif report_type == "income":
            df = ak.get_income_statement(symbol)
        elif report_type == "cashflow":
            df = ak.get_cashflow_statement(symbol)
        else:
            raise HTTPException(status_code=400, detail=f"不支持的报表类型: {report_type}")

        if df is None or df.empty:
            return {
                "success": True,
                "data": [],
                "message": f"未找到股票 {symbol} 的{report_type}数据",
                "timestamp": datetime.now().isoformat()
            }

        # 限制返回数量
        df = df.head(limit)

        # 转换为响应格式
        data_records = df.to_dict('records')

        result = {
            "success": True,
            "data": data_records,
            "symbol": symbol,
            "report_type": report_type,
            "total": len(data_records),
            "timestamp": datetime.now().isoformat()
        }

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询财务数据失败: {str(e)}")