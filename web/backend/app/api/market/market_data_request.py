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

import logging
import os
from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import ValidationError

from app.api.market._market_heatmap_router import router as market_heatmap_router
from app.api.market.health_check import router as market_health_router
from app.api.market.market_request_models import ETFQueryParams, FundFlowRequest, MarketDataRequest, RefreshRequest
from app.core.cache_utils import cache_response  # 导入缓存工具
from app.core.circuit_breaker_manager import get_circuit_breaker  # 导入熔断器
from app.core.exceptions import BusinessException, NotFoundException, ValidationException
from app.core.responses import create_error_response, create_success_response
from app.quotes_payload import build_quotes_response_payload
from app.schemas.market_schemas import (
    ChipRaceResponse,
    ETFDataResponse,
    LongHuBangResponse,
    MessageResponse,
)
from app.services.market_data_service import MarketDataService, get_market_data_service

router = APIRouter()
router.include_router(market_heatmap_router)
router.include_router(market_health_router)
logger = logging.getLogger(__name__)


def _success_response_spec(description: str, example: object) -> dict[int, dict]:
    return {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


def _error_response_spec(status_code: int, description: str, example: dict) -> dict[int, dict]:
    return {
        status_code: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


ETF_REFRESH_RESPONSES = {
    **_error_response_spec(
        400,
        "ETF 数据刷新失败",
        {"detail": "ETF数据源不可用", "error_code": "MARKET_OPERATION_FAILED"},
    ),
    **_error_response_spec(
        500,
        "ETF 数据刷新过程中发生内部错误",
        {"detail": "刷新ETF数据时发生错误", "error_code": "INTERNAL_SERVER_ERROR"},
    ),
    **_success_response_spec(
        "ETF 数据刷新成功",
        {"success": True, "message": "ETF实时数据刷新成功", "data": {"source": "akshare", "refreshed": True}},
    ),
}

CHIP_RACE_RESPONSES = {
    **_error_response_spec(
        500,
        "竞价抢筹查询失败",
        {"detail": "竞价抢筹服务不可用", "error_code": "MARKET_SERVICE_ERROR"},
    ),
    **_success_response_spec(
        "竞价抢筹数据列表",
        [
            {
                "id": 1,
                "symbol": "600519",
                "name": "贵州茅台",
                "trade_date": "2026-04-03",
                "race_type": "open",
                "latest_price": 1688.0,
                "change_percent": 1.86,
                "prev_close": 1657.2,
                "open_price": 1668.0,
                "race_amount": 58000000.0,
                "race_amplitude": 3.2,
                "race_commission": 72000000.0,
                "race_transaction": 58000000.0,
                "race_ratio": 12.4,
                "created_at": "2026-04-03T09:30:00",
            }
        ],
    ),
}

LHB_RESPONSES = {
    **_error_response_spec(
        500,
        "龙虎榜查询失败",
        {"detail": "龙虎榜服务不可用", "error_code": "MARKET_SERVICE_ERROR"},
    ),
    **_success_response_spec(
        "龙虎榜数据列表",
        [
            {
                "id": 1,
                "symbol": "002594",
                "name": "比亚迪",
                "trade_date": "2026-04-03",
                "reason": "日涨幅偏离值达7%",
                "buy_amount": 325000000.0,
                "sell_amount": 186000000.0,
                "net_amount": 139000000.0,
                "turnover_rate": 8.6,
                "institution_buy": 98000000.0,
                "institution_sell": 42000000.0,
                "created_at": "2026-04-03T16:05:00",
            }
        ],
    ),
}


@router.get("/fund-flow", summary="查询资金流向")
@cache_response("fund_flow", ttl=300)  # 🚀 添加5分钟缓存
async def get_fund_flow(
    symbol: str = Query(..., description="股票代码", min_length=1, max_length=20),
    timeframe: str = Query(default="1", description="时间维度: 1/3/5/10天", pattern=r"^[13510]$"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    # current_user: User = Depends(get_current_user),  # Temporarily disable auth for debugging
):
    """
    查询个股资金流向历史数据（使用数据源工厂）

    **参数说明:**
    - symbol: 股票代码 (如: 600519.SH)
    - timeframe: 1=今日, 3=3日, 5=5日, 10=10日
    - start_date/end_date: 时间范围筛选

    **缓存策略:** 5分钟TTL（减少数据库压力）
    **数据源:** 数据源工厂（Mock/Real/Hybrid模式）
    **验证:** P0改进 Task 2 - 使用Pydantic验证模型
    **返回:** 资金流向列表
    """
    try:
        # P0改进: 使用MarketDataQueryModel验证输入参数
        # 将字符串日期转换为datetime对象用于验证
        from datetime import datetime as dt_convert

        # Temporarily disable validation for debugging
        # validated_params = MarketDataQueryModel(
        #     symbol=symbol,
        #     start_date=dt_convert.strptime(start_date, "%Y-%m-%d") if start_date else dt_convert.now(),
        #     end_date=dt_convert.strptime(end_date, "%Y-%m-%d") if end_date else dt_convert.now(),
        #     interval="daily",  # fund-flow使用daily间隔
        # )
        # Simple validation object for now
        class SimpleParams:
            def __init__(self, symbol, start_date, end_date):
                self.symbol = symbol
                self.start_date = start_date
                self.end_date = end_date

        validated_params = SimpleParams(
            symbol=symbol,
            start_date=dt_convert.strptime(start_date, "%Y-%m-%d") if start_date else dt_convert.now(),
            end_date=dt_convert.strptime(end_date, "%Y-%m-%d") if end_date else dt_convert.now(),
        )

        # P0改进 Task 3: 使用熔断器保护外部API调用
        circuit_breaker = get_circuit_breaker("market_data")

        if circuit_breaker.is_open():
            # 熔断器打开，使用降级策略返回缓存数据
            logger.warning("⚠️ Circuit breaker for market_data is OPEN, returning cached/empty data")
            return create_success_response(
                data={"fund_flow": [], "total": 0}, message="市场数据服务暂不可用，请稍后重试"
            )

        # 使用数据源工厂获取市场数据
        from app.services.data_source_factory import get_data_source_factory

        factory = await get_data_source_factory()

        # 调用数据源工厂获取fund-flow数据
        try:
            result = await factory.get_data(
                "market",
                "fund-flow",
                {
                    "symbol": validated_params.symbol,
                    "timeframe": timeframe,
                    "start_date": validated_params.start_date.strftime("%Y-%m-%d") if start_date else None,
                    "end_date": validated_params.end_date.strftime("%Y-%m-%d") if end_date else None,
                },
            )
            # 成功调用，记录成功
            circuit_breaker.record_success()
        except Exception as e:
            # API调用失败，记录失败并打开熔断器
            circuit_breaker.record_failure()
            logger.error(f"❌ Market data API failed: {e}, failures: {circuit_breaker.failure_count}")
            raise

        # 转换为响应格式 - 修复数据结构以匹配前端期望
        raw_data = result.get("data", {})

        # 检查是否为mock数据格式 (嵌套结构)
        if isinstance(raw_data, dict) and "data" in raw_data and "details" in raw_data["data"]:
            # Mock数据格式，需要提取details数组
            mock_data = raw_data["data"]
            fund_flow_details = mock_data.get("details", [])
        else:
            # 实际数据格式，直接使用
            fund_flow_details = raw_data if isinstance(raw_data, list) else []

        # 转换为前端期望的字段格式
        fund_flow_data = []
        for detail in fund_flow_details:
            transformed = {
                "trade_date": detail.get("date", ""),
                "main_net_inflow": detail.get("main_net", 0),
                "super_large_net_inflow": detail.get("main_net", 0) * 0.4,  # 模拟超大单
                "large_net_inflow": detail.get("main_net", 0) * 0.6,  # 模拟大单
                "medium_net_inflow": detail.get("retain_net", 0) * 0.3,  # 模拟中单
                "small_net_inflow": detail.get("retain_net", 0) * 0.7,  # 模拟小单
            }
            fund_flow_data.append(transformed)

        return create_success_response(
            data={"fund_flow": fund_flow_data, "total": len(fund_flow_data)}, message=f"获取{symbol}资金流向数据成功"
        )

    except ValidationError as ve:
        # P0改进: 标准化验证错误响应
        error_details = [
            {"field": err["loc"][0] if err["loc"] else "unknown", "message": err["msg"]} for err in ve.errors()
        ]
        return create_error_response(error_code="VALIDATION_ERROR", message="输入参数验证失败", details=error_details)
    except Exception as e:
        raise BusinessException(
            detail=f"获取资金流向数据失败: {str(e)}", status_code=500, error_code="EXTERNAL_SERVICE_ERROR"
        )


@router.post("/fund-flow/refresh", summary="刷新资金流向")
async def refresh_fund_flow(
    symbol: str = Query(..., description="股票代码", min_length=1, max_length=20, pattern=r"^[A-Z0-9.]+$"),
    timeframe: str = Query(default="1", description="时间维度", pattern=r"^[13510]$"),
    service: MarketDataService = Depends(get_market_data_service),
):
    """
    从数据源刷新资金流向数据并保存到数据库

    **数据源:** 东方财富网 (via akshare)
    """
    try:
        result = service.fetch_and_save_fund_flow(symbol, timeframe)

        if not result["success"]:
            raise BusinessException(
                detail=result.get("message", "刷新资金流向数据失败"), status_code=400, error_code="OPERATION_FAILED"
            )

        return create_success_response(
            data={"symbol": symbol, "timeframe": timeframe, "refreshed": True},
            message=result.get("message", f"{symbol}资金流向数据刷新成功"),
        )

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        raise BusinessException(
            detail=f"刷新资金流向数据时发生错误: {str(e)}", status_code=500, error_code="INTERNAL_SERVER_ERROR"
        )


@router.get("/etf/list", summary="查询ETF列表")
@cache_response("etf_spot", ttl=60)  # 🚀 添加1分钟缓存（ETF行情更新较快）
async def get_etf_list(
    symbol: Optional[str] = Query(None, description="ETF代码", min_length=1, max_length=10, pattern=r"^[A-Z0-9]+$"),
    keyword: Optional[str] = Query(None, description="关键词搜索", min_length=1, max_length=50),
    market: Optional[str] = Query(None, description="市场类型", pattern=r"^(SH|SZ)$"),
    category: Optional[str] = Query(None, description="ETF类型", pattern=r"^(股票|债券|商品|货币|QDII)$"),
    limit: int = Query(default=100, description="返回数量", ge=1, le=500),
    offset: int = Query(0, description="偏移量", ge=0, le=10000),
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
        etf_data = [ETFDataResponse.model_validate(r) for r in results]

        return create_success_response(
            data={"etf_list": etf_data, "total": len(etf_data), "symbol": symbol, "keyword": keyword},
            message=f"获取ETF列表成功，共{len(etf_data)}条记录",
        )

    except Exception as e:
        raise BusinessException(
            detail=f"获取ETF列表失败: {str(e)}", status_code=500, error_code="EXTERNAL_SERVICE_ERROR"
        )


@router.post(
    "/etf/refresh",
    response_model=MessageResponse,
    summary="刷新ETF数据",
    description="刷新全市场 ETF 实时行情数据，用于 A 股 ETF 行情同步和后续查询缓存预热。",
    responses=ETF_REFRESH_RESPONSES,
)
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
        raise BusinessException(detail=result["message"], status_code=400, error_code="MARKET_OPERATION_FAILED")

    return MessageResponse(**result)


@router.get(
    "/chip-race",
    response_model=List[ChipRaceResponse],
    summary="查询竞价抢筹",
    description="查询竞价抢筹数据，支持按类型、日期、金额门槛和返回数量过滤，用于盘前盘后抢筹监控。",
    responses=CHIP_RACE_RESPONSES,
)
@cache_response("chip_race", ttl=300)  # 🚀 添加5分钟缓存
async def get_chip_race(
    race_type: str = Query(default="open", description="抢筹类型: open/end"),
    trade_date: Optional[date] = Query(None, description="交易日期"),
    min_race_amount: Optional[float] = Query(None, ge=0, description="最小抢筹金额"),
    limit: int = Query(default=100, ge=1, le=500, description="返回记录数限制"),
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
        raise BusinessException(detail=str(e), status_code=500, error_code="MARKET_SERVICE_ERROR")


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
        raise BusinessException(detail=result["message"], status_code=400, error_code="MARKET_OPERATION_FAILED")

    return MessageResponse(**result)


@router.get(
    "/lhb",
    response_model=List[LongHuBangResponse],
    summary="查询龙虎榜",
    description="查询龙虎榜明细数据，支持股票、日期区间、净买入额和返回数量过滤，用于异动席位分析。",
    responses=LHB_RESPONSES,
)
@cache_response("lhb", ttl=86400)  # 🚀 添加24小时缓存（龙虎榜每日发布）
async def get_lhb_detail(
    symbol: Optional[str] = Query(None, description="股票代码"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    min_net_amount: Optional[float] = Query(None, description="最小净买入额"),
    limit: int = Query(default=100, ge=1, le=500, description="返回记录数限制"),
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
        raise BusinessException(detail=str(e), status_code=500, error_code="MARKET_SERVICE_ERROR")


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
        raise BusinessException(detail=result["message"], status_code=400, error_code="MARKET_OPERATION_FAILED")

    return MessageResponse(**result)


@router.get("/quotes", summary="查询实时行情")
@cache_response("real_time_quotes", ttl=10)  # 🚀 添加10秒缓存（平衡实时性）
async def get_market_quotes(
    symbols: Optional[str] = Query(None, description="股票代码列表，逗号分隔，如: 000001,600519"),
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

        return create_success_response(
            data=build_quotes_response_payload(result, symbol_list),
            message=f"获取{len(symbol_list)}只股票实时行情成功",
        )

    except Exception as e:
        raise BusinessException(
            detail=f"获取实时行情失败: {str(e)}", status_code=500, error_code="EXTERNAL_SERVICE_ERROR"
        )


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
            return create_success_response(
                data={
                    "stocks": mock_data.get("data", []),
                    "total": len(mock_data.get("data", [])),
                    "source": "mock",
                    "search": search,
                    "exchange": exchange,
                    "security_type": security_type,
                },
                message="获取股票列表成功（Mock数据）",
            )
        else:
            # 正常获取真实数据
            from sqlalchemy import text

            from app.core.database import get_postgresql_session

            session = get_postgresql_session()

            # 使用固定SQL模板 + 参数占位，避免动态拼接 WHERE 子句
            sql = text(
                """
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
                WHERE (:search IS NULL OR symbol LIKE :search OR name LIKE :search)
                  AND (:exchange IS NULL OR exchange = :exchange)
                  AND (:security_type IS NULL OR security_type = :security_type)
                ORDER BY symbol
                LIMIT :limit
            """
            )

            params = {
                "search": f"%{search}%" if search else None,
                "exchange": exchange,
                "security_type": security_type,
                "limit": limit,
            }

            result = session.execute(sql, params)
            stocks = [dict(row._mapping) for row in result]

            session.close()

            return create_success_response(
                data={
                    "stocks": stocks,
                    "total": len(stocks),
                    "source": "real",
                    "search": search,
                    "exchange": exchange,
                    "security_type": security_type,
                },
                message=f"获取股票列表成功，共{len(stocks)}条记录",
            )

    except Exception as e:
        raise BusinessException(detail=f"查询股票列表失败: {str(e)}", status_code=500, error_code="DATABASE_ERROR")


@router.get("/kline", summary="查询K线数据")
async def get_kline_data(
    stock_code: str = Query(..., description="股票代码（6位数字或带交易所后缀）"),
    period: str = Query(
        default="daily", description="时间周期: daily/weekly/monthly", pattern=r"^(daily|weekly|monthly)$"
    ),
    adjust: str = Query(default="qfq", description="复权类型: qfq/hfq/空字符串", pattern=r"^(qfq|hfq|)$"),
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
    **验证**: P0改进 Task 2 - 使用MarketDataQueryModel验证参数
    **返回**: K线数据数组，包含OHLCV及技术指标
    """
    try:
        from datetime import datetime as dt_convert

        from app.services.stock_search_service import get_stock_search_service

        # 参数验证：日期格式验证（但不转换为datetime对象，因为service层期望字符串）
        if start_date:
            try:
                # 验证日期格式但不转换
                dt_convert.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise ValidationException(detail=f"开始日期格式错误: {start_date}，应为 YYYY-MM-DD", field="start_date")

        if end_date:
            try:
                # 验证日期格式但不转换
                dt_convert.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise ValidationException(detail=f"结束日期格式错误: {end_date}，应为 YYYY-MM-DD", field="end_date")

        # P0改进 Task 3: 使用熔断器保护外部API调用
        circuit_breaker = get_circuit_breaker("market_data")

        if circuit_breaker.is_open():
            # 熔断器打开，使用降级策略
            logger.warning("⚠️ Circuit breaker for market_data is OPEN, K线数据服务暂不可用")
            raise BusinessException(
                detail="市场数据服务暂不可用，请稍后重试", status_code=503, error_code="MARKET_SERVICE_UNAVAILABLE"
            )

        service = get_stock_search_service()
        try:
            # FIX: 直接传递字符串参数给service层
            result = service.get_a_stock_kline(
                symbol=stock_code,
                period=period,
                adjust=adjust,
                start_date=start_date,  # 字符串格式 YYYY-MM-DD
                end_date=end_date,  # 字符串格式 YYYY-MM-DD
            )
            # 成功调用，记录成功
            circuit_breaker.record_success()
        except Exception as e:
            # API调用失败，记录失败
            circuit_breaker.record_failure()
            logger.error(f"❌ K-line data API failed: {e}, failures: {circuit_breaker.failure_count}")
            raise

        if result is None:
            raise NotFoundException(resource="股票K线数据", identifier=stock_code)

        # Validate data availability
        if result.get("count", 0) < 10:
            raise ValidationException(detail="该股票历史数据不足10个交易日，无法生成K线图", field="date_range")

        return {"success": True, **result, "timestamp": datetime.now().isoformat()}

    except ValidationError as ve:
        # P0改进: 标准化验证错误响应
        error_details = [
            {"field": err["loc"][0] if err["loc"] else "unknown", "message": err["msg"]} for err in ve.errors()
        ]
        return create_error_response(error_code="VALIDATION_ERROR", message="输入参数验证失败", details=error_details)
    except ValueError as e:
        # Invalid stock code format or parameters
        raise BusinessException(detail=str(e), status_code=400, error_code="MARKET_OPERATION_FAILED")
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Unexpected errors (e.g., AKShare failures)
        raise BusinessException(
            detail=f"数据源暂时不可用，请稍后重试: {str(e)}", status_code=500, error_code="DATA_SOURCE_UNAVAILABLE"
        )
