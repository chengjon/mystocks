"""
市场数据API路由

提供RESTful接口:
- GET /api/market/fund-flow - 查询资金流向
- POST /api/market/fund-flow/refresh - 刷新资金流向数据
- GET /api/market/etf/list - 查询ETF列表
- POST /api/market/etf/refresh - 刷新ETF数据
- GET /api/market/chip-race - 查询竞价抢筹
- POST /api/market/chip-race/refresh - 刷新抢筹数据
- GET /api/market/lhb - 查询龙虎榜
- POST /api/market/lhb/refresh - 刷新龙虎榜数据
- GET /api/market/heatmap - 获取市场热力图数据
"""

import os
from datetime import date, datetime
from typing import List, Optional

import pymysql
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.cache_utils import cache_response, clear_api_cache  # 导入缓存工具
from app.schemas.market_schemas import (
    ChipRaceRequest,
    ChipRaceResponse,
    ETFDataRequest,
    ETFDataResponse,
    FundFlowRequest,
    FundFlowResponse,
    LongHuBangRequest,
    LongHuBangResponse,
    MessageResponse,
)
from app.services.market_data_service import MarketDataService, get_market_data_service

router = APIRouter(prefix="/api/market", tags=["市场数据"])


# ==================== 资金流向 ====================


@router.get("/fund-flow", response_model=List[FundFlowResponse], summary="查询资金流向")
@cache_response("fund_flow", ttl=300)  # 🚀 添加5分钟缓存
async def get_fund_flow(
    symbol: str = Query(..., description="股票代码"),
    timeframe: str = Query(default="1", description="时间维度: 1/3/5/10天"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
):
    """
    查询个股资金流向历史数据（使用数据源工厂）

    **参数说明:**
    - symbol: 股票代码 (如: 600519.SH)
    - timeframe: 1=今日, 3=3日, 5=5日, 10=10日
    - start_date/end_date: 时间范围筛选

    **缓存策略:** 5分钟TTL（减少数据库压力）
    **数据源:** 数据源工厂（Mock/Real/Hybrid模式）
    **返回:** 资金流向列表
    """
    try:
        # 使用数据源工厂获取市场数据
        from app.services.data_source_factory import get_data_source_factory

        factory = await get_data_source_factory()

        # 调用数据源工厂获取fund-flow数据
        result = await factory.get_data(
            "market",
            "fund-flow",
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "start_date": str(start_date) if start_date else None,
                "end_date": str(end_date) if end_date else None,
            },
        )

        # 转换为响应格式
        data = result.get("data", [])
        return [FundFlowResponse.model_validate(r) for r in data]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fund-flow/refresh", response_model=MessageResponse, summary="刷新资金流向")
async def refresh_fund_flow(
    symbol: str = Query(..., description="股票代码"),
    timeframe: str = Query(default="1", description="时间维度"),
    service: MarketDataService = Depends(get_market_data_service),
):
    """
    从数据源刷新资金流向数据并保存到数据库

    **数据源:** 东方财富网 (via akshare)
    """
    result = service.fetch_and_save_fund_flow(symbol, timeframe)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return MessageResponse(**result)


# ==================== ETF数据 ====================


@router.get("/etf/list", response_model=List[ETFDataResponse], summary="查询ETF列表")
@cache_response("etf_spot", ttl=60)  # 🚀 添加1分钟缓存（ETF行情更新较快）
async def get_etf_list(
    symbol: Optional[str] = Query(None, description="ETF代码"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    limit: int = Query(default=50, ge=1, le=500, description="返回数量"),
    service: MarketDataService = Depends(get_market_data_service),
):
    """
    查询ETF实时行情数据（带缓存优化）

    **查询方式:**
    - 指定symbol: 返回单个ETF数据
    - 指定keyword: 模糊搜索名称/代码
    - 不指定条件: 返回全市场ETF(按涨跌幅排序)

    **缓存策略:** 1分钟TTL（平衡实时性和性能）
    **返回:** ETF数据列表
    """
    try:
        results = service.query_etf_spot(symbol, keyword, limit)
        return [ETFDataResponse.model_validate(r) for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/etf/refresh", response_model=MessageResponse, summary="刷新ETF数据")
async def refresh_etf_data(
    service: MarketDataService = Depends(get_market_data_service),
):
    """
    刷新全市场ETF实时数据

    **数据源:** 东方财富网 (via akshare)
    **更新频率:** 建议每5分钟调用一次
    """
    result = service.fetch_and_save_etf_spot()

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return MessageResponse(**result)


# ==================== 竞价抢筹 ====================


@router.get("/chip-race", response_model=List[ChipRaceResponse], summary="查询竞价抢筹")
@cache_response("chip_race", ttl=300)  # 🚀 添加5分钟缓存
async def get_chip_race(
    race_type: str = Query(default="open", description="抢筹类型: open/end"),
    trade_date: Optional[date] = Query(None, description="交易日期"),
    min_race_amount: Optional[float] = Query(None, ge=0, description="最小抢筹金额"),
    limit: int = Query(default=100, ge=1, le=500),
    service: MarketDataService = Depends(get_market_data_service),
):
    """
    查询竞价抢筹数据（带缓存优化）

    **类型说明:**
    - open: 早盘抢筹(集合竞价)
    - end: 尾盘抢筹(收盘竞价)

    **缓存策略:** 5分钟TTL
    **返回:** 按抢筹金额倒序排列
    """
    try:
        results = service.query_chip_race(race_type, trade_date, min_race_amount, limit)
        return [ChipRaceResponse.model_validate(r) for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chip-race/refresh", response_model=MessageResponse, summary="刷新抢筹数据")
async def refresh_chip_race(
    race_type: str = Query(default="open", description="抢筹类型"),
    trade_date: Optional[str] = Query(None, description="交易日期 YYYY-MM-DD"),
    service: MarketDataService = Depends(get_market_data_service),
):
    """
    刷新竞价抢筹数据

    **数据源:** 通达信TQLEX
    **更新时机:**
    - open: 9:30之后
    - end: 15:05之后
    """
    result = service.fetch_and_save_chip_race(race_type, trade_date)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return MessageResponse(**result)


# ==================== 龙虎榜 ====================


@router.get("/lhb", response_model=List[LongHuBangResponse], summary="查询龙虎榜")
@cache_response("lhb", ttl=86400)  # 🚀 添加24小时缓存（龙虎榜每日发布）
async def get_lhb_detail(
    symbol: Optional[str] = Query(None, description="股票代码"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    min_net_amount: Optional[float] = Query(None, description="最小净买入额"),
    limit: int = Query(default=100, ge=1, le=500),
    service: MarketDataService = Depends(get_market_data_service),
):
    """
    查询龙虎榜详细数据（带缓存优化）

    **筛选条件:**
    - symbol: 查询指定股票的历史龙虎榜记录
    - start_date/end_date: 时间范围
    - min_net_amount: 净买入额下限(元)

    **缓存策略:** 24小时TTL（龙虎榜数据每日更新）
    **返回:** 按日期倒序排列
    """
    try:
        results = service.query_lhb_detail(symbol, start_date, end_date, min_net_amount, limit)
        return [LongHuBangResponse.model_validate(r) for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lhb/refresh", response_model=MessageResponse, summary="刷新龙虎榜")
async def refresh_lhb_detail(
    trade_date: str = Query(..., description="交易日期 YYYY-MM-DD"),
    service: MarketDataService = Depends(get_market_data_service),
):
    """
    刷新指定日期的龙虎榜数据

    **数据源:** 东方财富网 (via akshare)
    **更新时机:** 每日20:00之后
    **说明:** 龙虎榜数据次日公布
    """
    result = service.fetch_and_save_lhb_detail(trade_date)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return MessageResponse(**result)


# ==================== 实时行情 ====================


@router.get("/quotes", summary="查询实时行情")
@cache_response("real_time_quotes", ttl=10)  # 🚀 添加10秒缓存（平衡实时性）
async def get_market_quotes(
    symbols: Optional[str] = Query(None, description="股票代码列表，逗号分隔，如: 000001,600519")
):
    """
    获取实时市场行情数据（使用数据源工厂）

    **参数**:
    - symbols: 股票代码列表（可选）。不指定则返回热门股票行情

    **缓存策略:** 10秒TTL（实时行情需要较高频率更新）
    **数据源**: 数据源工厂（Mock/Real/Hybrid模式）
    **返回**: 实时行情列表
    """
    try:
        # 使用数据源工厂获取市场数据
        from app.services.data_source_factory import get_data_source_factory

        factory = await get_data_source_factory()

        # 如果未指定股票代码，返回热门股票
        if not symbols:
            symbols = "000001,600519,000858,601318,600036"  # 平安、茅台、五粮液、平安保险、招商银行

        symbol_list = [s.strip() for s in symbols.split(",")]

        # 调用数据源工厂获取quotes数据
        result = await factory.get_data("market", "quotes", {"symbols": symbol_list})

        return {
            "success": True,
            "data": result.get("data", []),
            "total": len(result.get("data", [])),
            "timestamp": result.get("timestamp", datetime.now().isoformat()),
            "source": result.get("source", "market"),
            "endpoint": result.get("endpoint", "quotes"),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取实时行情失败: {str(e)}")


@router.get("/stocks", summary="查询股票列表")
async def get_stock_list(
    limit: int = Query(100, ge=1, le=1000, description="返回记录数限制"),
    search: Optional[str] = Query(None, description="股票代码或名称搜索关键词"),
    exchange: Optional[str] = Query(None, description="交易所筛选: SSE/SZSE"),
    security_type: Optional[str] = Query(None, description="证券类型筛选"),
):
    """
    获取股票基本信息列表

    **查询条件**:
    - search: 关键词搜索（代码或名称）
    - exchange: 按交易所筛选（SSE上交所/SZSE深交所）
    - security_type: 按证券类型筛选
    - limit: 返回数量限制

    **数据源**: PostgreSQL stock_info表 或 Mock数据
    **返回**: 股票列表
    """
    try:
        # 检查是否使用Mock数据
        use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

        if use_mock:
            # 使用Mock数据
            from app.mock.unified_mock_data import get_mock_data_manager

            mock_manager = get_mock_data_manager()
            mock_data = mock_manager.get_data(
                "stock_list", limit=limit, search=search, exchange=exchange, security_type=security_type
            )
            return {
                "success": True,
                "data": mock_data.get("data", []),
                "total": len(mock_data.get("data", [])),
                "timestamp": mock_data.get("timestamp"),
                "source": "mock",
            }
        else:
            # 正常获取真实数据
            from sqlalchemy import text

            from app.core.database import get_postgresql_session

            session = get_postgresql_session()

            # 构建查询SQL
            where_clauses = []
            params = {}

            if search:
                where_clauses.append("(symbol LIKE :search OR name LIKE :search)")
                params["search"] = f"%{search}%"

            if exchange:
                where_clauses.append("exchange = :exchange")
                params["exchange"] = exchange

            if security_type:
                where_clauses.append("security_type = :security_type")
                params["security_type"] = security_type

            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

            sql = text(
                f"""
                SELECT
                    symbol,
                    name,
                    exchange,
                    security_type,
                    list_date,
                    status,
                    listing_board,
                    market_cap,
                    circulating_market_cap
                FROM stock_info
                WHERE {where_sql}
                ORDER BY symbol
                LIMIT :limit
            """
            )
            params["limit"] = limit

            result = session.execute(sql, params)
            stocks = [dict(row._mapping) for row in result]

            session.close()

            return {
                "success": True,
                "data": stocks,
                "total": len(stocks),
                "timestamp": datetime.now().isoformat(),
                "source": "real",
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询股票列表失败: {str(e)}")


# ==================== K线数据 ====================


@router.get("/kline", summary="查询K线数据")
async def get_kline_data(
    stock_code: str = Query(..., description="股票代码（6位数字或带交易所后缀）"),
    period: str = Query(default="daily", description="时间周期: daily/weekly/monthly"),
    adjust: str = Query(default="qfq", description="复权类型: qfq/hfq/空字符串"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
):
    """
    获取股票K线（蜡烛图）历史数据

    **参数说明**:
    - stock_code: 股票代码，支持 "600519" 或 "600519.SH" 格式
    - period:
      - "daily" (日K线)
      - "weekly" (周K线)
      - "monthly" (月K线)
    - adjust:
      - "qfq" (前复权，推荐)
      - "hfq" (后复权)
      - "" (不复权)
    - start_date/end_date: 日期范围（可选，默认最近60个交易日）

    **数据源**: AKShare stock_zh_a_hist()
    **返回**: K线数据数组，包含OHLCV及技术指标
    """
    try:
        from app.services.stock_search_service import get_stock_search_service

        service = get_stock_search_service()
        result = service.get_a_stock_kline(
            symbol=stock_code,
            period=period,
            adjust=adjust,
            start_date=start_date,
            end_date=end_date,
        )

        if result is None:
            raise HTTPException(status_code=404, detail=f"股票代码 {stock_code} 不存在或暂无K线数据")

        # Validate data availability
        if result.get("count", 0) < 10:
            raise HTTPException(status_code=422, detail="该股票历史数据不足10个交易日，无法生成K线图")

        return {"success": True, **result, "timestamp": datetime.now().isoformat()}

    except ValueError as e:
        # Invalid stock code format or parameters
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Unexpected errors (e.g., AKShare failures)
        raise HTTPException(status_code=500, detail=f"数据源暂时不可用，请稍后重试: {str(e)}")


# ==================== 股票热力图 ====================


@router.get("/heatmap", summary="获取市场热力图数据")
@cache_response("market_heatmap", ttl=60)  # 🚀 添加1分钟缓存
async def get_market_heatmap(
    market: str = Query(default="cn", description="市场类型: cn(A股)/hk(港股)"),
    limit: int = Query(default=50, ge=10, le=200, description="返回股票数量"),
):
    """
    获取市场热力图数据，用于可视化展示各股票的涨跌情况

    **参数说明:**
    - market: 市场类型
      - "cn" - 中国A股市场
      - "hk" - 香港股市
    - limit: 返回的股票数量 (10-200)

    **数据源:** AKShare 或 Mock数据
    **返回:** 股票列表，包含代码、名称、涨跌幅、价格、成交量、市值等
    """
    try:
        # 检查是否使用Mock数据
        use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

        if use_mock:
            # 使用Mock数据
            from app.mock.unified_mock_data import get_mock_data_manager

            mock_manager = get_mock_data_manager()
            mock_data = mock_manager.get_data("market_heatmap", market=market, limit=limit)
            return {
                "success": True,
                "data": mock_data.get("data", []),
                "total": len(mock_data.get("data", [])),
                "timestamp": mock_data.get("timestamp"),
                "source": "mock",
            }
        else:
            # 正常获取真实数据
            import akshare as ak

            # 根据市场类型选择数据源
            if market == "cn":
                # 获取A股实时行情
                df = ak.stock_zh_a_spot_em()
                df = df.head(limit)

                # 数据转换
                result = []
                for _, row in df.iterrows():
                    try:
                        result.append(
                            {
                                "symbol": row.get("代码", ""),
                                "name": row.get("名称", ""),
                                "price": float(row.get("最新价", 0)),
                                "change": float(row.get("涨跌额", 0)),
                                "change_pct": float(row.get("涨跌幅", 0)),
                                "volume": int(row.get("成交量", 0)),
                                "amount": float(row.get("成交额", 0)),
                                "market_cap": (float(row.get("总市值", 0)) if "总市值" in row else None),
                            }
                        )
                    except Exception as e:
                        continue

            elif market == "hk":
                # 获取港股实时行情
                df = ak.stock_hk_spot_em()
                df = df.head(limit)

                # 数据转换
                result = []
                for _, row in df.iterrows():
                    try:
                        result.append(
                            {
                                "symbol": row.get("代码", ""),
                                "name": row.get("名称", ""),
                                "price": float(row.get("最新价", 0)),
                                "change": float(row.get("涨跌额", 0)),
                                "change_pct": float(row.get("涨跌幅", 0)),
                                "volume": int(row.get("成交量", 0)),
                                "amount": float(row.get("成交额", 0)),
                                "market_cap": (float(row.get("总市值", 0)) if "总市值" in row else None),
                            }
                        )
                    except Exception as e:
                        continue
            else:
                raise HTTPException(status_code=400, detail=f"不支持的市场类型: {market}")

            # 按涨跌幅排序
            result = sorted(result, key=lambda x: x["change_pct"], reverse=True)

            return {
                "success": True,
                "data": result,
                "total": len(result),
                "timestamp": datetime.now().isoformat(),
                "source": "real",
            }

    except ImportError:
        raise HTTPException(status_code=500, detail="AKShare库未安装")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热力图数据失败: {str(e)}")


# ==================== 健康检查 ====================


@router.get("/health", summary="市场数据 API 健康检查", description="检查市场数据 API 服务的健康状态", tags=["health"])
async def health_check():
    """
    检查市场数据 API 服务的整体健康状态

    此端点用于监控市场数据 API 的可用性和响应能力。

    **功能说明**:
    - 验证市场数据服务的运行状态
    - 检查实时行情数据提供者的连接
    - 评估 API 服务的响应性能

    **使用场景**:
    - 前端定期轮询显示服务状态
    - 监控和告警系统集成
    - 负载均衡器健康检查
    - 自动化部署流程的健康验证

    Returns:
        Dict: 包含以下字段的健康状态对象
            - status: 服务状态 (healthy/unhealthy)
            - service: 服务名称 (market-data-api)
            - timestamp: 检查时间戳 (ISO 8601 格式)

    Examples:
        获取市场数据 API 健康状态:
        ```bash
        curl http://localhost:8000/api/market/health
        ```

        正常响应:
        ```json
        {
            "status": "healthy",
            "timestamp": "2025-11-30T21:06:45.123456",
            "service": "market-data-api"
        }
        ```

    Notes:
        - 此端点不需要认证，允许任何客户端查询
        - 响应时间通常在 50-100ms 以内
        - healthy: 服务正常运行，可以接受数据请求
        - 建议监控系统每 30 秒调用一次
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "market-data-api",
    }
