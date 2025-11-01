"""
市场数据API路由 V2
使用东方财富直接API

提供RESTful接口:
- 个股资金流向
- ETF数据
- 龙虎榜
- 行业/概念资金流向
- 股票分红配送
- 股票大宗交易
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import date, datetime

from app.services.market_data_service_v2 import get_market_data_service_v2

router = APIRouter(prefix="/api/market/v2", tags=["市场数据V2"])


# ==================== 个股资金流向 ====================

@router.get("/fund-flow", summary="查询个股资金流向")
async def get_fund_flow(
    symbol: str = Query(..., description="股票代码"),
    timeframe: str = Query(default="1", description="时间维度: 1/3/5/10天"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期")
):
    """
    查询个股资金流向历史数据

    Args:
        symbol: 股票代码 (如: 600519)
        timeframe: 1=今日, 3=3日, 5=5日, 10=10日
        start_date/end_date: 时间范围筛选
    """
    try:
        service = get_market_data_service_v2()
        results = service.query_fund_flow(symbol, timeframe, start_date, end_date)
        return {"success": True, "data": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fund-flow/refresh", summary="刷新资金流向数据")
async def refresh_fund_flow(
    symbol: Optional[str] = Query(None, description="股票代码，不传则刷新全市场"),
    timeframe: str = Query(default="今日", description="时间维度: 今日/3日/5日/10日")
):
    """
    从东方财富刷新资金流向数据

    不传symbol则刷新全市场数据（约4000+只股票）
    """
    try:
        service = get_market_data_service_v2()
        result = service.fetch_and_save_fund_flow(symbol, timeframe)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ETF数据 ====================

@router.get("/etf/list", summary="查询ETF列表")
async def get_etf_list(
    symbol: Optional[str] = Query(None, description="ETF代码"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    limit: int = Query(default=50, ge=1, le=500, description="返回数量")
):
    """
    查询ETF实时行情数据

    支持按代码精确查询或按关键词模糊搜索
    """
    try:
        service = get_market_data_service_v2()
        results = service.query_etf_spot(symbol, keyword, limit)
        return {"success": True, "data": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/etf/refresh", summary="刷新ETF数据")
async def refresh_etf_spot():
    """
    从东方财富刷新全市场ETF数据
    """
    try:
        service = get_market_data_service_v2()
        result = service.fetch_and_save_etf_spot()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 龙虎榜 ====================

@router.get("/lhb", summary="查询龙虎榜")
async def get_lhb_detail(
    symbol: Optional[str] = Query(None, description="股票代码"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    min_net_amount: Optional[float] = Query(None, description="最小净买入额(元)"),
    limit: int = Query(default=100, ge=1, le=500, description="返回数量")
):
    """
    查询龙虎榜详细数据

    支持按股票代码、日期范围、净买入额筛选
    """
    try:
        service = get_market_data_service_v2()
        results = service.query_lhb_detail(symbol, start_date, end_date, min_net_amount, limit)
        return {"success": True, "data": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lhb/refresh", summary="刷新龙虎榜数据")
async def refresh_lhb_detail(
    trade_date: str = Query(..., description="交易日期 (YYYY-MM-DD)")
):
    """
    从东方财富刷新指定日期的龙虎榜数据
    """
    try:
        service = get_market_data_service_v2()
        result = service.fetch_and_save_lhb_detail(trade_date)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 行业/概念资金流向 ====================

@router.get("/sector/fund-flow", summary="查询行业/概念资金流向")
async def get_sector_fund_flow(
    sector_type: str = Query(default="行业", description="板块类型: 行业/概念/地域"),
    timeframe: str = Query(default="今日", description="时间维度: 今日/3日/5日/10日"),
    limit: int = Query(default=100, ge=1, le=500, description="返回数量")
):
    """
    查询行业/概念板块资金流向

    Args:
        sector_type: 行业、概念或地域板块
        timeframe: 今日、3日、5日或10日
    """
    try:
        service = get_market_data_service_v2()
        results = service.query_sector_fund_flow(sector_type, timeframe, limit)
        return {"success": True, "data": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sector/fund-flow/refresh", summary="刷新行业/概念资金流向")
async def refresh_sector_fund_flow(
    sector_type: str = Query(default="行业", description="板块类型: 行业/概念/地域"),
    timeframe: str = Query(default="今日", description="时间维度: 今日/3日/5日/10日")
):
    """
    从东方财富刷新行业/概念资金流向数据
    """
    try:
        service = get_market_data_service_v2()
        result = service.fetch_and_save_sector_fund_flow(sector_type, timeframe)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 股票分红配送 ====================

@router.get("/dividend", summary="查询股票分红配送")
async def get_stock_dividend(
    symbol: str = Query(..., description="股票代码"),
    limit: int = Query(default=50, ge=1, le=200, description="返回数量")
):
    """
    查询股票分红配送历史记录

    Args:
        symbol: 股票代码 (如: 600519)
    """
    try:
        service = get_market_data_service_v2()
        results = service.query_stock_dividend(symbol, limit)
        return {"success": True, "data": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dividend/refresh", summary="刷新股票分红配送数据")
async def refresh_stock_dividend(
    symbol: str = Query(..., description="股票代码")
):
    """
    从东方财富刷新股票分红配送数据
    """
    try:
        service = get_market_data_service_v2()
        result = service.fetch_and_save_stock_dividend(symbol)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 股票大宗交易 ====================

@router.get("/blocktrade", summary="查询股票大宗交易")
async def get_stock_blocktrade(
    symbol: Optional[str] = Query(None, description="股票代码"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    limit: int = Query(default=100, ge=1, le=500, description="返回数量")
):
    """
    查询股票大宗交易记录

    Args:
        symbol: 股票代码 (可选)
        start_date/end_date: 日期范围 (可选)
    """
    try:
        service = get_market_data_service_v2()
        results = service.query_blocktrade(symbol, start_date, end_date, limit)
        return {"success": True, "data": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/blocktrade/refresh", summary="刷新股票大宗交易数据")
async def refresh_stock_blocktrade(
    trade_date: Optional[str] = Query(None, description="交易日期 (YYYY-MM-DD)，不传则获取最新")
):
    """
    从东方财富刷新大宗交易数据
    """
    try:
        service = get_market_data_service_v2()
        result = service.fetch_and_save_blocktrade(trade_date)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 批量刷新 ====================

@router.post("/refresh-all", summary="批量刷新所有市场数据")
async def refresh_all_market_data():
    """
    一键刷新所有市场数据（用于定时任务）

    包括：
    - 全市场资金流向（今日）
    - 全市场ETF数据
    - 行业资金流向
    - 概念资金流向
    - 当日龙虎榜
    - 当日大宗交易
    """
    try:
        service = get_market_data_service_v2()
        results = {}

        # 1. 刷新资金流向
        results['fund_flow'] = service.fetch_and_save_fund_flow(None, "今日")

        # 2. 刷新ETF数据
        results['etf'] = service.fetch_and_save_etf_spot()

        # 3. 刷新行业资金流向
        results['sector_industry'] = service.fetch_and_save_sector_fund_flow("行业", "今日")

        # 4. 刷新概念资金流向
        results['sector_concept'] = service.fetch_and_save_sector_fund_flow("概念", "今日")

        # 5. 刷新龙虎榜（最近交易日）
        today_str = datetime.now().strftime('%Y-%m-%d')
        results['lhb'] = service.fetch_and_save_lhb_detail(today_str)

        # 6. 刷新大宗交易
        results['blocktrade'] = service.fetch_and_save_blocktrade(today_str)

        return {
            "success": True,
            "message": "批量刷新完成",
            "details": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
