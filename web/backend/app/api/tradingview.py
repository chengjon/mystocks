"""
TradingView Widget API
提供 TradingView 图表和 widgets 配置
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Body, Depends, Query
from app.core.exceptions import BusinessException
from app.core.responses import UnifiedResponse, create_unified_success_response
from pydantic import BaseModel, Field

from app.api.auth import User, get_current_user
from app.core.config import settings
from app.services.tradingview_widget_service import TradingViewWidgetService, get_tradingview_service_dependency

router = APIRouter()


def _is_tradingview_mock_enabled() -> bool:
    return settings.use_mock_apis


def _get_mock_tradingview_config(data_type: str, **kwargs: Any) -> Dict[str, Any]:
    from app.mock.unified_mock_data import get_mock_data_manager

    mock_manager = get_mock_data_manager()
    mock_data = mock_manager.get_data(data_type, **kwargs)
    return mock_data.get("config", {})


def _get_mock_tradingview_symbol(symbol: str, market: str) -> str:
    from app.mock.unified_mock_data import get_mock_data_manager

    mock_manager = get_mock_data_manager()
    mock_data = mock_manager.get_data("tradingview_symbol_convert", symbol=symbol, market=market)
    return mock_data.get("tradingview_symbol", "")

TRADINGVIEW_ERROR_RESPONSE = {
    500: {
        "description": "TradingView widget configuration generation failed because symbol conversion or widget assembly was unsuccessful.",
        "content": {
            "application/json": {
                "example": {
                    "detail": "生成图表配置失败: invalid market symbol",
                }
            }
        },
    }
}


def _success_response_spec(description: str, example: Dict) -> Dict[int, Dict]:
    return {
        200: {
            "description": description,
            "content": {"application/json": {"example": example}},
        },
        **TRADINGVIEW_ERROR_RESPONSE,
    }


TRADINGVIEW_CHART_CONFIG_RESPONSES = _success_response_spec(
    "TradingView 标准图表嵌入配置，供前端加载 A 股或港股日线/分钟图。",
    {
        "success": True,
        "config": {
            "symbol": "SSE:600519",
            "interval": "D",
            "theme": "dark",
            "locale": "zh_CN",
            "container_id": "tradingview_chart",
            "autosize": True,
            "allow_symbol_change": True,
        },
    },
)

TRADINGVIEW_MINI_CHART_RESPONSES = _success_response_spec(
    "TradingView 迷你图嵌入配置，适合卡片或列表场景展示简版走势。",
    {
        "success": True,
        "config": {
            "symbol": "HKEX:0700",
            "theme": "dark",
            "locale": "zh_CN",
            "container_id": "tradingview_mini_chart",
            "width": 320,
            "height": 220,
        },
    },
)

TRADINGVIEW_TICKER_TAPE_RESPONSES = _success_response_spec(
    "TradingView ticker tape 嵌入配置，展示自选证券滚动行情条。",
    {
        "success": True,
        "config": {
            "symbols": [
                {"proName": "SSE:600519", "title": "贵州茅台"},
                {"proName": "HKEX:0700", "title": "腾讯控股"},
            ],
            "theme": "dark",
            "locale": "zh_CN",
            "container_id": "tradingview_ticker_tape",
            "displayMode": "regular",
        },
    },
)

TRADINGVIEW_MARKET_OVERVIEW_RESPONSES = _success_response_spec(
    "TradingView 市场概览组件配置，默认提供中国市场概览视图。",
    {
        "success": True,
        "config": {
            "container_id": "tradingview_market_overview",
            "theme": "dark",
            "locale": "zh_CN",
            "market": "china",
            "tabs": [
                {"title": "主要指数", "symbols": ["SSE:000001", "SZSE:399001"]},
                {"title": "港股观察", "symbols": ["HKEX:HSI", "HKEX:0700"]},
            ],
        },
    },
)

TRADINGVIEW_SCREENER_RESPONSES = _success_response_spec(
    "TradingView 筛选器组件配置，默认聚焦中国市场证券列表。",
    {
        "success": True,
        "config": {
            "container_id": "tradingview_screener",
            "theme": "dark",
            "locale": "zh_CN",
            "market": "china",
            "defaultColumn": "close",
            "defaultScreen": "most_capitalized",
        },
    },
)

TRADINGVIEW_SYMBOL_CONVERT_RESPONSES = _success_response_spec(
    "普通证券代码转换为 TradingView 使用的交易所前缀格式。",
    {
        "success": True,
        "original_symbol": "0700",
        "tradingview_symbol": "HKEX:0700",
        "market": "HK",
    },
)


class ChartConfigRequest(BaseModel):
    """图表配置请求"""

    symbol: str = Field(..., description="股票代码")
    market: str = Field("CN", description="市场类型: CN, US, HK")
    interval: str = Field("D", description="时间间隔: 1, 5, 15, 60, D, W, M")
    theme: str = Field("dark", description="主题: light, dark")
    locale: str = Field("zh_CN", description="语言: zh_CN, en")
    container_id: str = Field("tradingview_chart", description="容器ID")


class SymbolItem(BaseModel):
    """股票代码条目"""

    proName: str = Field(..., description="代码（如 NASDAQ:AAPL）")
    title: str = Field(..., description="显示名称")


class TickerTapeConfigRequest(BaseModel):
    """Ticker Tape 配置请求"""

    symbols: List[SymbolItem] = Field(None, description="股票列表")
    theme: str = Field("dark", description="主题")
    locale: str = Field("zh_CN", description="语言")
    container_id: str = Field("tradingview_ticker_tape", description="容器ID")


@router.post(
    "/chart/config",
    summary="获取 TradingView 图表配置",
    response_model=UnifiedResponse,
    responses=TRADINGVIEW_CHART_CONFIG_RESPONSES,
)
async def get_chart_config(
    request: ChartConfigRequest = Body(
        ...,
        openapi_examples={
            "cn_daily_chart": {
                "summary": "A 股日线图配置",
                "value": {
                    "symbol": "600519",
                    "market": "CN",
                    "interval": "D",
                    "theme": "dark",
                    "locale": "zh_CN",
                    "container_id": "tradingview_chart",
                },
            }
        },
    ),
    current_user: User = Depends(get_current_user),
    service: TradingViewWidgetService = Depends(get_tradingview_service_dependency),
) -> Dict:
    """
    获取 TradingView 图表配置

    返回用于前端嵌入的图表配置
    """
    try:
        if _is_tradingview_mock_enabled():
            config = _get_mock_tradingview_config(
                "tradingview_chart",
                symbol=request.symbol,
                market=request.market,
                interval=request.interval,
                theme=request.theme,
                locale=request.locale,
                container_id=request.container_id,
            )
            return create_unified_success_response(data={"config": config}, message="图表配置获取成功")

        tv_symbol = service.convert_symbol_to_tradingview_format(request.symbol, request.market)
        config = service.generate_chart_config(
            symbol=tv_symbol,
            container_id=request.container_id,
            interval=request.interval,
            theme=request.theme,
            locale=request.locale,
        )

        return create_unified_success_response(data={"config": config}, message="图表配置获取成功")
    except Exception as e:
        raise BusinessException(status_code=500, detail=f"生成图表配置失败: {str(e)}")


@router.post(
    "/mini-chart/config",
    summary="获取 TradingView 迷你图配置",
    response_model=UnifiedResponse,
    responses=TRADINGVIEW_MINI_CHART_RESPONSES,
)
async def get_mini_chart_config(
    symbol: str = Query(..., description="股票代码"),
    market: str = Query("CN", description="市场类型"),
    theme: str = Query("dark", description="主题"),
    locale: str = Query("zh_CN", description="语言"),
    container_id: str = Query("tradingview_mini_chart", description="容器ID"),
    current_user: User = Depends(get_current_user),
    service: TradingViewWidgetService = Depends(get_tradingview_service_dependency),
) -> Dict:
    """
    获取 TradingView 迷你图表配置
    """
    try:
        if _is_tradingview_mock_enabled():
            config = _get_mock_tradingview_config(
                "tradingview_mini_chart",
                symbol=symbol,
                market=market,
                theme=theme,
                locale=locale,
                container_id=container_id,
            )
            return create_unified_success_response(data={"config": config}, message="迷你图表配置获取成功")

        tv_symbol = service.convert_symbol_to_tradingview_format(symbol, market)
        config = service.generate_mini_chart_config(symbol=tv_symbol, container_id=container_id, theme=theme, locale=locale)

        return create_unified_success_response(data={"config": config}, message="迷你图表配置获取成功")
    except Exception as e:
        raise BusinessException(status_code=500, detail=f"生成迷你图表配置失败: {str(e)}")


@router.post(
    "/ticker-tape/config",
    summary="获取 TradingView Ticker Tape 配置",
    response_model=UnifiedResponse,
    responses=TRADINGVIEW_TICKER_TAPE_RESPONSES,
)
async def get_ticker_tape_config(
    request: TickerTapeConfigRequest = Body(
        ...,
        openapi_examples={
            "default_watchlist": {
                "summary": "默认自选股滚动条",
                "value": {
                    "symbols": [
                        {"proName": "SSE:600519", "title": "贵州茅台"},
                        {"proName": "SZSE:000001", "title": "平安银行"},
                    ],
                    "theme": "dark",
                    "locale": "zh_CN",
                    "container_id": "tradingview_ticker_tape",
                },
            }
        },
    ),
    current_user: User = Depends(get_current_user),
    service: TradingViewWidgetService = Depends(get_tradingview_service_dependency),
) -> Dict:
    """
    获取 TradingView Ticker Tape 配置
    """
    try:
        symbols = None
        if request.symbols:
            symbols = [item.dict() for item in request.symbols]

        if _is_tradingview_mock_enabled():
            config = _get_mock_tradingview_config(
                "tradingview_ticker_tape",
                symbols=symbols,
                theme=request.theme,
                locale=request.locale,
                container_id=request.container_id,
            )
            return create_unified_success_response(data={"config": config}, message="Ticker Tape 配置获取成功")

        config = service.generate_ticker_tape_config(
            symbols=symbols,
            container_id=request.container_id,
            theme=request.theme,
            locale=request.locale,
        )

        return create_unified_success_response(data={"config": config}, message="Ticker Tape 配置获取成功")
    except Exception as e:
        raise BusinessException(status_code=500, detail=f"生成 Ticker Tape 配置失败: {str(e)}")


@router.get(
    "/market-overview/config",
    summary="获取 TradingView 市场概览配置",
    response_model=UnifiedResponse,
    responses=TRADINGVIEW_MARKET_OVERVIEW_RESPONSES,
)
async def get_market_overview_config(
    market: str = Query("china", description="市场类型: china, us, crypto"),
    theme: str = Query("dark", description="主题"),
    locale: str = Query("zh_CN", description="语言"),
    container_id: str = Query("tradingview_market_overview", description="容器ID"),
    current_user: User = Depends(get_current_user),
    service: TradingViewWidgetService = Depends(get_tradingview_service_dependency),
) -> Dict:
    """
    获取 TradingView 市场概览配置
    """
    try:
        if _is_tradingview_mock_enabled():
            config = _get_mock_tradingview_config(
                "tradingview_market_overview", market=market, theme=theme, locale=locale, container_id=container_id
            )
            return create_unified_success_response(data={"config": config}, message="市场概览配置获取成功")

        config = service.generate_market_overview_config(
            container_id=container_id, theme=theme, locale=locale, market=market
        )

        return create_unified_success_response(data={"config": config}, message="市场概览配置获取成功")
    except Exception as e:
        raise BusinessException(status_code=500, detail=f"生成市场概览配置失败: {str(e)}")


@router.get(
    "/screener/config",
    summary="获取 TradingView 股票筛选器配置",
    response_model=UnifiedResponse,
    responses=TRADINGVIEW_SCREENER_RESPONSES,
)
async def get_screener_config(
    market: str = Query("china", description="市场类型: china, america, crypto"),
    theme: str = Query("dark", description="主题"),
    locale: str = Query("zh_CN", description="语言"),
    container_id: str = Query("tradingview_screener", description="容器ID"),
    current_user: User = Depends(get_current_user),
    service: TradingViewWidgetService = Depends(get_tradingview_service_dependency),
) -> Dict:
    """
    获取 TradingView 股票筛选器配置
    """
    try:
        if _is_tradingview_mock_enabled():
            config = _get_mock_tradingview_config(
                "tradingview_screener", market=market, theme=theme, locale=locale, container_id=container_id
            )
            return create_unified_success_response(data={"config": config}, message="筛选器配置获取成功")

        config = service.generate_screener_config(
            container_id=container_id, theme=theme, locale=locale, market=market
        )

        return create_unified_success_response(data={"config": config}, message="筛选器配置获取成功")
    except Exception as e:
        raise BusinessException(status_code=500, detail=f"生成筛选器配置失败: {str(e)}")


@router.get(
    "/symbol/convert",
    summary="转换 TradingView 证券代码",
    response_model=UnifiedResponse,
    responses=TRADINGVIEW_SYMBOL_CONVERT_RESPONSES,
)
async def convert_symbol(
    symbol: str = Query(..., description="股票代码"),
    market: str = Query("CN", description="市场类型"),
    current_user: User = Depends(get_current_user),
    service: TradingViewWidgetService = Depends(get_tradingview_service_dependency),
) -> Dict:
    """
    将股票代码转换为 TradingView 格式
    """
    try:
        if _is_tradingview_mock_enabled():
            return create_unified_success_response(
                data={
                    "original_symbol": symbol,
                    "tradingview_symbol": _get_mock_tradingview_symbol(symbol=symbol, market=market),
                    "market": market,
                },
                message="股票代码转换成功",
            )

        tv_symbol = service.convert_symbol_to_tradingview_format(symbol, market)

        return create_unified_success_response(
            data={
                "original_symbol": symbol,
                "tradingview_symbol": tv_symbol,
                "market": market,
            },
            message="股票代码转换成功",
        )
    except Exception as e:
        raise BusinessException(status_code=500, detail=f"转换股票代码失败: {str(e)}")
