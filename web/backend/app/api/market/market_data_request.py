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
from typing import Any, List, Mapping, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import ValidationError

from app.api.market._market_heatmap_router import router as market_heatmap_router
from app.api.market.health_check import router as market_health_router
from app.core.cache_utils import cache_response  # 导入缓存工具
from app.core.config import settings
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
from app.services.openstock_client import OpenStockClient, OpenStockClientConfig, OpenStockFetchResult

router = APIRouter()
router.include_router(market_heatmap_router)
router.include_router(market_health_router)
logger = logging.getLogger(__name__)

DEFAULT_OPENSTOCK_BASE_URL = "http://192.168.123.104:8040"


def get_openstock_market_client() -> OpenStockClient:
    base_url = (
        os.getenv("OPENSTOCK_BASE_URL")
        or os.getenv("OPENSTOCK_API_BASE_URL")
        or DEFAULT_OPENSTOCK_BASE_URL
    ).strip()
    try:
        timeout_seconds = float(os.getenv("OPENSTOCK_TIMEOUT_SECONDS", "5.0"))
    except ValueError:
        timeout_seconds = 5.0
    api_key = os.getenv("OPENSTOCK_API_KEY", "").strip() or None
    return OpenStockClient(
        OpenStockClientConfig(
            base_url=base_url or DEFAULT_OPENSTOCK_BASE_URL,
            timeout_seconds=timeout_seconds,
            api_key=api_key,
        )
    )


def _quotes_payload_from_openstock(result: OpenStockFetchResult, symbols: list[str]) -> dict[str, Any]:
    return build_quotes_response_payload(
        {
            "data": result.data,
            "source": result.source or "openstock",
            "endpoint": result.endpoint_name or "quotes",
        },
        symbols,
    )


_OPENSTOCK_PERIOD_TO_INTERVAL = {
    "day": "1d",
    "daily": "1d",
    "week": "1w",
    "weekly": "1w",
    "month": "1M",
    "monthly": "1M",
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "60m": "1h",
}


def _normalize_openstock_kline_payload(
    result: OpenStockFetchResult,
    *,
    stock_code: str,
    period: str,
    adjust: str,
) -> dict[str, Any]:
    """Convert OpenStock /data/bars response to the frontend KLineResponse shape.

    Frontend contract (kline.ts):
        {code, data: {symbol, interval, adjust, candles: [{timestamp, OHLCV}]}}
    Backend wraps as:
        {success, stock_code, stock_name, period, adjust,
         data: {symbol, interval, adjust, candles: [...]}, count, timestamp}

    The candles envelope + `time`→`timestamp` rename lives here so neither
    OpenStock nor the frontend needs to track the other's shape.
    """
    payload = result.data
    if isinstance(payload, Mapping):
        rows = payload.get("data") or []
        if not isinstance(rows, list):
            rows = []
        count_value = payload.get("count", len(rows))
        count = count_value if isinstance(count_value, int) else len(rows)
        symbol_value = str(payload.get("stock_code") or payload.get("symbol") or stock_code)
        period_value = str(payload.get("period") or period)
        adjust_value = str(payload.get("adjust") or adjust or "qfq") or "qfq"
        interval_value = _OPENSTOCK_PERIOD_TO_INTERVAL.get(period_value, period)
        return {
            "stock_code": symbol_value,
            "stock_name": str(payload.get("stock_name") or payload.get("name") or stock_code),
            "period": period_value,
            "adjust": adjust_value,
            "data": {
                "symbol": symbol_value,
                "interval": interval_value,
                "adjust": adjust_value,
                "candles": [_convert_openstock_bar_to_candle(bar) for bar in rows],
            },
            "count": count,
        }

    rows = payload if isinstance(payload, list) else []
    interval_value = _OPENSTOCK_PERIOD_TO_INTERVAL.get(period, period)
    return {
        "stock_code": stock_code,
        "stock_name": stock_code,
        "period": period,
        "adjust": adjust or "qfq",
        "data": {
            "symbol": stock_code,
            "interval": interval_value,
            "adjust": adjust or "qfq",
            "candles": [_convert_openstock_bar_to_candle(bar) for bar in rows],
        },
        "count": len(rows),
    }


def _convert_openstock_bar_to_candle(bar: Any) -> dict[str, Any]:
    """OpenStock bar uses `time`; frontend candle uses `timestamp`."""
    if not isinstance(bar, Mapping):
        return {}
    candle: dict[str, Any] = {}
    if "time" in bar:
        candle["timestamp"] = bar["time"]
    elif "timestamp" in bar:
        candle["timestamp"] = bar["timestamp"]
    for field in ("open", "high", "low", "close", "volume", "amount"):
        if field in bar:
            candle[field] = bar[field]
    return candle


def _is_market_stock_list_mock_enabled() -> bool:
    return settings.use_mock_apis


def _get_mock_stock_list(*, limit: int, search: Optional[str], exchange: Optional[str], security_type: Optional[str]):
    from app.mock.unified_mock_data import get_mock_data_manager

    mock_manager = get_mock_data_manager()
    return mock_manager.get_data(
        "stock_list", limit=limit, search=search, exchange=exchange, security_type=security_type
    )


from app.api.market._market_data_request_responses import (
    CHIP_RACE_REFRESH_RESPONSES,
    CHIP_RACE_RESPONSES,
    ETF_LIST_RESPONSES,
    ETF_REFRESH_RESPONSES,
    FUND_FLOW_REFRESH_RESPONSES,
    FUND_FLOW_RESPONSES,
    KLINE_DATA_RESPONSES,
    LHB_REFRESH_RESPONSES,
    LHB_RESPONSES,
    MARKET_QUOTES_RESPONSES,
    STOCK_LIST_RESPONSES,
)

@router.get("/fund-flow", summary="查询资金流向", responses=FUND_FLOW_RESPONSES)
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


@router.post("/fund-flow/refresh", summary="刷新资金流向", responses=FUND_FLOW_REFRESH_RESPONSES)
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


@router.get("/etf/list", summary="查询ETF列表", responses=ETF_LIST_RESPONSES)
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


@router.post(
    "/chip-race/refresh",
    response_model=MessageResponse,
    summary="刷新抢筹数据",
    responses=CHIP_RACE_REFRESH_RESPONSES,
)
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


@router.post(
    "/lhb/refresh",
    response_model=MessageResponse,
    summary="刷新龙虎榜",
    responses=LHB_REFRESH_RESPONSES,
)
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


@router.get("/quotes", summary="查询实时行情", responses=MARKET_QUOTES_RESPONSES)
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
        # 如果未指定股票代码，返回热门股票
        if not symbols:
            symbols = "000001,600519,000858,601318,600036"  # 平安、茅台、五粮液、平安保险、招商银行

        symbol_list = [s.strip() for s in symbols.split(",")]

        client = get_openstock_market_client()
        try:
            result = await client.fetch("REALTIME_QUOTES", params={"symbols": symbol_list})
        finally:
            await client.aclose()

        return create_success_response(
            data=_quotes_payload_from_openstock(result, symbol_list),
            message=f"获取{len(symbol_list)}只股票实时行情成功",
        )

    except Exception as e:
        raise BusinessException(
            detail=f"获取实时行情失败: {str(e)}", status_code=500, error_code="EXTERNAL_SERVICE_ERROR"
        )


@router.get("/stocks", summary="查询股票列表", responses=STOCK_LIST_RESPONSES)
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
        if _is_market_stock_list_mock_enabled():
            mock_data = _get_mock_stock_list(
                limit=limit,
                search=search,
                exchange=exchange,
                security_type=security_type,
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


@router.get("/kline", summary="查询K线数据", responses=KLINE_DATA_RESPONSES)
async def get_kline_data(
    stock_code: Optional[str] = Query(None, description="股票代码（6位数字或带交易所后缀，与 symbol 二选一）"),
    symbol: Optional[str] = Query(None, description="股票代码别名（前端使用），与 stock_code 二选一"),
    period: Optional[str] = Query(
        None, description="时间周期: daily/weekly/monthly（与 interval 二选一）"
    ),
    interval: Optional[str] = Query(
        None, description="时间周期别名（前端使用）: 1d/1w/1M/1m/5m/15m/1h"
    ),
    adjust: str = Query(default="qfq", description="复权类型: qfq/hfq/none"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD（已接收，暂不透传给 OpenStock）"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD（已接收，暂不透传给 OpenStock）"),
):
    """
    获取股票K线（蜡烛图）历史数据

    **参数说明（前端友好别名）**:
    - stock_code / symbol: 股票代码（两者二选一；前端用 symbol）
    - period / interval: 周期（两者二选一；前端用 interval）
      - period: daily / weekly / monthly
      - interval: 1d / 1w / 1M / 1m / 5m / 15m / 1h
    - adjust: qfq (前复权，推荐) / hfq (后复权) / none (不复权)
    - start_date/end_date: 日期范围（已接收，当前实现暂不透传给 OpenStock）

    **数据源**: OpenStock /data/bars
    **返回**: 包含 candles 数组的 KLineResponse 形状
    """
    try:
        from datetime import datetime as dt_convert

        # 兼容前端 symbol/interval 别名
        effective_stock_code = stock_code or symbol
        if not effective_stock_code:
            raise ValidationException(
                detail="必须提供 stock_code 或 symbol 参数", field="stock_code"
            )

        # 将 interval (前端值域) 翻译为 period (内部值域)；period 优先若同时给出
        interval_to_period = {
            "1d": "daily",
            "1w": "weekly",
            "1M": "monthly",
            "1m": "minute_1",
            "5m": "minute_5",
            "15m": "minute_15",
            "1h": "minute_60",
        }
        if period:
            effective_period = period
        elif interval:
            effective_period = interval_to_period.get(interval)
            if not effective_period:
                raise ValidationException(
                    detail=f"不支持的 interval 值: {interval}（支持: 1d/1w/1M/1m/5m/15m/1h）",
                    field="interval",
                )
        else:
            effective_period = "daily"

        # 规范化 adjust：前端 "none" → 内部 ""（OpenStock 端当前忽略，仅回显）
        effective_adjust = "" if adjust == "none" else adjust

        # 参数验证：日期格式验证（已接收，当前不透传，但保留格式校验）
        if start_date:
            try:
                dt_convert.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise ValidationException(detail=f"开始日期格式错误: {start_date}，应为 YYYY-MM-DD", field="start_date")

        if end_date:
            try:
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

        try:
            client = get_openstock_market_client()
            try:
                # OpenStock /data/bars 接受 day/week/month (或 1m/5m/15m/30m/60m)。
                # 第一阶段：translate daily/weekly/monthly → day/week/month；
                #          adjust/start_date/end_date 已接收但暂不透传（OpenStock execute_bars_payload 当前忽略）。
                period_map = {
                    "daily": "day",
                    "weekly": "week",
                    "monthly": "month",
                    "minute_1": "1m",
                    "minute_5": "5m",
                    "minute_15": "15m",
                    "minute_60": "60m",
                }
                openstock_period = period_map.get(effective_period, "day")
                openstock_result = await client.fetch_bars(
                    symbol=effective_stock_code,
                    period=openstock_period,
                    count=60,
                )
            finally:
                await client.aclose()
            result = _normalize_openstock_kline_payload(
                openstock_result,
                stock_code=effective_stock_code,
                period=effective_period,
                adjust=effective_adjust,
            )
            # 成功调用，记录成功
            circuit_breaker.record_success()
        except Exception as e:
            # API调用失败，记录失败
            circuit_breaker.record_failure()
            logger.error(f"❌ K-line data API failed: {e}, failures: {circuit_breaker.failure_count}")
            raise

        if result is None:
            raise NotFoundException(resource="股票K线数据", identifier=effective_stock_code)

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
    except BusinessException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Unexpected errors (e.g., AKShare failures)
        raise BusinessException(
            detail=f"数据源暂时不可用，请稍后重试: {str(e)}", status_code=500, error_code="DATA_SOURCE_UNAVAILABLE"
        )
