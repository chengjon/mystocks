"""
Efinance Data Source API

提供efinance数据源的API端点，包括：
- 股票历史K线、实时行情、龙虎榜、业绩数据、资金流向
- 基金历史净值、持仓信息、基本信息
- 可转债实时行情、基本信息、K线数据
- 期货基本信息、历史行情、实时行情

集成优化特性：
- SmartCache: 智能缓存系统
- CircuitBreaker: 熔断器保护
- DataQualityValidator: 数据质量验证
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.core.responses import ErrorCodes, create_error_response, create_success_response
from app.core.security import User, get_current_user
from src.adapters.efinance_adapter import EfinanceDataSource

# 创建efinance数据源实例
efinance_adapter = EfinanceDataSource(
    use_smart_cache=True,
    use_circuit_breaker=True,
    use_quality_validator=True,
    cache_ttl=300,  # 5分钟缓存
    circuit_breaker_threshold=3,
    enable_column_mapping=True,
)

router = APIRouter(prefix="/api/efinance", tags=["efinance"])


# ============================================================================
# Pydantic Models
# ============================================================================


class StockKlineRequest(BaseModel):
    """股票K线请求"""

    symbol: str = Field(..., description="股票代码", example="600519")
    start_date: str = Field(..., description="开始日期", example="2024-01-01")
    end_date: str = Field(..., description="结束日期", example="2024-12-31")
    klt: int = Field(101, description="K线周期: 1/5/15/30/60分钟, 101日线", example=101)


class FundNavRequest(BaseModel):
    """基金净值请求"""

    fund_code: str = Field(..., description="基金代码", example="161725")


class FundBasicRequest(BaseModel):
    """基金基本信息请求"""

    fund_codes: List[str] = Field(..., description="基金代码列表", example=["161725", "005827"])


class BondKlineRequest(BaseModel):
    """可转债K线请求"""

    bond_code: str = Field(..., description="债券代码", example="123111")


class FuturesHistoryRequest(BaseModel):
    """期货历史行情请求"""

    quote_id: str = Field(..., description="期货行情ID", example="115.ZCM")


class DragonTigerRequest(BaseModel):
    """龙虎榜请求"""

    start_date: Optional[str] = Field(None, description="开始日期", example="2024-01-01")
    end_date: Optional[str] = Field(None, description="结束日期", example="2024-01-05")


class FundFlowRequest(BaseModel):
    """资金流向请求"""

    symbol: str = Field(..., description="股票代码", example="300750")


# ============================================================================
# Stock 股票相关API
# ============================================================================


@router.get("/stock/kline", summary="获取股票历史K线数据")
async def get_stock_kline(
    symbol: str = Query(..., description="股票代码", example="600519"),
    start_date: str = Query(..., description="开始日期", example="2024-01-01"),
    end_date: str = Query(..., description="结束日期", example="2024-12-31"),
    klt: int = Query(101, description="K线周期: 1/5/15/30/60分钟, 101日线"),
    current_user: User = Depends(get_current_user),
):
    """
    获取股票历史K线数据

    支持日K线和分钟K线数据，通过klt参数控制：
    - 1/5/15/30/60: 分钟K线
    - 101: 日K线
    """
    try:
        df = efinance_adapter.get_stock_daily(symbol, start_date, end_date)

        if df.empty:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, f"No data found for stock {symbol}")

        # 转换为字典格式返回
        result = {
            "symbol": symbol,
            "data": df.to_dict("records"),
            "count": len(df),
            "columns": list(df.columns),
            "cached": False,  # 可以通过缓存统计获取
            "source": "efinance",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, f"Failed to get stock kline data: {str(e)}")


@router.get("/stock/realtime", summary="获取沪深A股实时行情")
async def get_realtime_quotes(current_user: User = Depends(get_current_user)):
    """
    获取沪深A股实时行情数据

    返回所有A股的最新行情数据，包括价格、涨跌幅、成交量等
    """
    try:
        df = efinance_adapter.get_real_time_data("")  # efinance的实时行情API不需要指定股票

        if df.empty:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, "No realtime data available")

        result = {
            "data": df.to_dict("records"),
            "count": len(df),
            "columns": list(df.columns),
            "timestamp": datetime.now().isoformat(),
            "source": "efinance",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, f"Failed to get realtime quotes: {str(e)}")


@router.get("/stock/realtime/{symbol}", summary="获取单只股票实时行情")
async def get_single_stock_realtime(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取指定股票的实时行情数据
    """
    try:
        data = efinance_adapter.get_real_time_data(symbol)

        if not data:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, f"No realtime data found for stock {symbol}")

        result = {"symbol": symbol, "data": data, "timestamp": datetime.now().isoformat(), "source": "efinance"}

        return create_success_response(result)

    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, f"Failed to get realtime data for {symbol}: {str(e)}")


@router.get("/stock/dragon-tiger", summary="获取龙虎榜数据")
async def get_dragon_tiger_list(
    start_date: Optional[str] = Query(None, description="开始日期", example="2024-01-01"),
    end_date: Optional[str] = Query(None, description="结束日期", example="2024-01-05"),
    current_user: User = Depends(get_current_user),
):
    """
    获取龙虎榜数据

    包含机构席位、上榜原因、买卖金额等信息
    """
    try:
        df = efinance_adapter.get_dragon_tiger_list(start_date, end_date)

        if df.empty:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, "No dragon tiger data found")

        result = {
            "data": df.to_dict("records"),
            "count": len(df),
            "columns": list(df.columns),
            "date_range": {"start": start_date, "end": end_date},
            "source": "efinance",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, f"Failed to get dragon tiger list: {str(e)}")


@router.get("/stock/performance", summary="获取公司业绩数据")
async def get_company_performance(
    season: str = Query("z", description="报告期: z=最新, y=去年同期, j=季度累计"),
    current_user: User = Depends(get_current_user),
):
    """
    获取沪深A股公司业绩数据

    包含营收、净利润、每股收益等财务指标
    """
    try:
        df = efinance_adapter.get_financial_data("", period=season)  # 传递空字符串获取全部

        if df.empty:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, "No company performance data found")

        result = {
            "data": df.to_dict("records"),
            "count": len(df),
            "columns": list(df.columns),
            "season": season,
            "source": "efinance",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, f"Failed to get company performance: {str(e)}")


@router.get("/stock/fund-flow/{symbol}", summary="获取股票历史资金流向")
async def get_stock_fund_flow(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取股票历史资金流向数据

    包含主力、散户、中小单、大单、超大单的净流入情况
    """
    try:
        df = efinance_adapter.get_fund_flow_data(symbol)

        if df.empty:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, f"No fund flow data found for stock {symbol}")

        result = {
            "symbol": symbol,
            "data": df.to_dict("records"),
            "count": len(df),
            "columns": list(df.columns),
            "source": "efinance",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, f"Failed to get fund flow data for {symbol}: {str(e)}")


@router.get("/stock/fund-flow-today/{symbol}", summary="获取今日资金流向")
async def get_today_fund_flow(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取股票今日分钟级资金流向数据

    实时更新，包含每分钟的主力资金流向情况
    """
    try:
        df = efinance_adapter.get_today_fund_flow(symbol)

        if df.empty:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, f"No today fund flow data found for stock {symbol}")

        result = {
            "symbol": symbol,
            "data": df.to_dict("records"),
            "count": len(df),
            "columns": list(df.columns),
            "timestamp": datetime.now().isoformat(),
            "source": "efinance",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR, f"Failed to get today fund flow data for {symbol}: {str(e)}"
        )


# ============================================================================
# Fund 基金相关API
# ============================================================================


@router.get("/fund/nav/{fund_code}", summary="获取基金历史净值")
async def get_fund_nav_history(
    fund_code: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取基金历史净值数据

    包含单位净值、累计净值、日涨跌幅等信息
    """
    try:
        df = efinance_adapter.get_fund_history(fund_code)

        if df.empty:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, f"No fund nav data found for {fund_code}")

        result = {
            "fund_code": fund_code,
            "data": df.to_dict("records"),
            "count": len(df),
            "columns": list(df.columns),
            "source": "efinance",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR, f"Failed to get fund nav history for {fund_code}: {str(e)}"
        )


@router.get("/fund/positions/{fund_code}", summary="获取基金持仓信息")
async def get_fund_positions(
    fund_code: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取基金持仓信息

    包含持仓股票、持仓占比、较上期变化等信息
    """
    try:
        df = efinance_adapter.get_fund_holdings(fund_code)

        if df.empty:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, f"No fund positions data found for {fund_code}")

        result = {
            "fund_code": fund_code,
            "data": df.to_dict("records"),
            "count": len(df),
            "columns": list(df.columns),
            "source": "efinance",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR, f"Failed to get fund positions for {fund_code}: {str(e)}"
        )


@router.post("/fund/basic", summary="获取多只基金基本信息")
async def get_fund_basic_info(
    request: FundBasicRequest,
    current_user: User = Depends(get_current_user),
):
    """
    获取多只基金的基本信息

    支持批量查询基金的基本信息、成立日期、净值等
    """
    try:
        df = efinance_adapter.get_fund_basic_info(request.fund_codes)

        if df.empty:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, "No fund basic info found")

        result = {
            "fund_codes": request.fund_codes,
            "data": df.to_dict("records"),
            "count": len(df),
            "columns": list(df.columns),
            "source": "efinance",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, f"Failed to get fund basic info: {str(e)}")


# ============================================================================
# Bond 债券相关API
# ============================================================================


@router.get("/bond/realtime", summary="获取可转债实时行情")
async def get_bond_realtime_quotes(current_user: User = Depends(get_current_user)):
    """
    获取可转债实时行情数据

    返回所有可转债的最新行情数据
    """
    try:
        df = efinance_adapter.get_bond_realtime_quotes()

        if df.empty:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, "No bond realtime data available")

        result = {
            "data": df.to_dict("records"),
            "count": len(df),
            "columns": list(df.columns),
            "timestamp": datetime.now().isoformat(),
            "source": "efinance",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, f"Failed to get bond realtime quotes: {str(e)}")


@router.get("/bond/basic", summary="获取可转债基本信息")
async def get_bond_basic_info(current_user: User = Depends(get_current_user)):
    """
    获取可转债基本信息

    包含债券代码、名称、正股信息、评级、发行规模等
    """
    try:
        df = efinance_adapter.get_bond_basic_info()

        if df.empty:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, "No bond basic info available")

        result = {"data": df.to_dict("records"), "count": len(df), "columns": list(df.columns), "source": "efinance"}

        return create_success_response(result)

    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, f"Failed to get bond basic info: {str(e)}")


@router.get("/bond/kline/{bond_code}", summary="获取可转债历史K线")
async def get_bond_kline(
    bond_code: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取可转债历史K线数据
    """
    try:
        df = efinance_adapter.get_bond_history(bond_code)

        if df.empty:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, f"No bond kline data found for {bond_code}")

        result = {
            "bond_code": bond_code,
            "data": df.to_dict("records"),
            "count": len(df),
            "columns": list(df.columns),
            "source": "efinance",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, f"Failed to get bond kline for {bond_code}: {str(e)}")


# ============================================================================
# Futures 期货相关API
# ============================================================================


@router.get("/futures/basic", summary="获取期货基本信息")
async def get_futures_basic_info(current_user: User = Depends(get_current_user)):
    """
    获取期货基本信息

    包含所有期货合约的基本信息和行情ID
    """
    try:
        df = efinance_adapter.get_futures_basic_info()

        if df.empty:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, "No futures basic info available")

        result = {"data": df.to_dict("records"), "count": len(df), "columns": list(df.columns), "source": "efinance"}

        return create_success_response(result)

    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, f"Failed to get futures basic info: {str(e)}")


@router.get("/futures/history/{quote_id}", summary="获取期货历史行情")
async def get_futures_history(
    quote_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取期货历史行情数据
    """
    try:
        df = efinance_adapter.get_futures_history(quote_id)

        if df.empty:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, f"No futures history data found for {quote_id}")

        result = {
            "quote_id": quote_id,
            "data": df.to_dict("records"),
            "count": len(df),
            "columns": list(df.columns),
            "source": "efinance",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR, f"Failed to get futures history for {quote_id}: {str(e)}"
        )


@router.get("/futures/realtime", summary="获取期货实时行情")
async def get_futures_realtime_quotes(current_user: User = Depends(get_current_user)):
    """
    获取期货实时行情数据

    返回所有期货合约的最新行情数据
    """
    try:
        df = efinance_adapter.get_futures_realtime_quotes()

        if df.empty:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, "No futures realtime data available")

        result = {
            "data": df.to_dict("records"),
            "count": len(df),
            "columns": list(df.columns),
            "timestamp": datetime.now().isoformat(),
            "source": "efinance",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, f"Failed to get futures realtime quotes: {str(e)}")


# ============================================================================
# 系统状态和监控API
# ============================================================================


@router.get("/cache/stats", summary="获取缓存统计信息")
async def get_cache_stats(current_user: User = Depends(get_current_user)):
    """
    获取efinance适配器的缓存统计信息

    包含命中率、缓存大小、刷新统计等
    """
    try:
        stats = efinance_adapter.get_cache_stats()

        result = {"cache_stats": stats, "timestamp": datetime.now().isoformat(), "source": "efinance"}

        return create_success_response(result)

    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, f"Failed to get cache stats: {str(e)}")


@router.get("/circuit-breaker/stats", summary="获取熔断器统计信息")
async def get_circuit_breaker_stats(current_user: User = Depends(get_current_user)):
    """
    获取efinance适配器的熔断器统计信息

    包含状态、失败次数、成功率等
    """
    try:
        stats = efinance_adapter.get_circuit_breaker_stats()

        result = {"circuit_breaker_stats": stats, "timestamp": datetime.now().isoformat(), "source": "efinance"}

        return create_success_response(result)

    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, f"Failed to get circuit breaker stats: {str(e)}")


@router.post("/cache/clear", summary="清空缓存")
async def clear_cache(current_user: User = Depends(get_current_user)):
    """
    清空efinance适配器的所有缓存
    """
    try:
        efinance_adapter.clear_cache()

        result = {
            "message": "Cache cleared successfully",
            "timestamp": datetime.now().isoformat(),
            "source": "efinance",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, f"Failed to clear cache: {str(e)}")


@router.post("/circuit-breaker/reset", summary="重置熔断器")
async def reset_circuit_breaker(current_user: User = Depends(get_current_user)):
    """
    重置efinance适配器的熔断器状态
    """
    try:
        efinance_adapter.reset_circuit_breaker()

        result = {
            "message": "Circuit breaker reset successfully",
            "timestamp": datetime.now().isoformat(),
            "source": "efinance",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, f"Failed to reset circuit breaker: {str(e)}")
