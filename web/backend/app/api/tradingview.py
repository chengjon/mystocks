"""
TradingView Widget API
提供 TradingView 图表和 widgets 配置
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel, Field

from app.services.tradingview_widget_service import get_tradingview_service
from app.api.auth import get_current_user, User

router = APIRouter()


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


@router.post("/chart/config")
async def get_chart_config(
    request: ChartConfigRequest, current_user: User = Depends(get_current_user)
) -> Dict:
    """
    获取 TradingView 图表配置

    返回用于前端嵌入的图表配置
    """
    try:
        # 检查是否使用Mock数据
        use_mock = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'
        
        if use_mock:
            # 使用Mock数据
            from app.mock.unified_mock_data import get_mock_data_manager
            mock_manager = get_mock_data_manager()
            mock_data = mock_manager.get_data("tradingview_chart", 
                                             symbol=request.symbol, 
                                             market=request.market,
                                             interval=request.interval,
                                             theme=request.theme,
                                             locale=request.locale,
                                             container_id=request.container_id)
            return {"success": True, "config": mock_data.get("config", {})}
        else:
            # 正常获取真实数据
            service = get_tradingview_service()

            # 转换股票代码为 TradingView 格式
            tv_symbol = service.convert_symbol_to_tradingview_format(
                request.symbol, request.market
            )

            # 生成图表配置
            config = service.generate_chart_config(
                symbol=tv_symbol,
                container_id=request.container_id,
                interval=request.interval,
                theme=request.theme,
                locale=request.locale,
            )

            return {"success": True, "config": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成图表配置失败: {str(e)}")


@router.post("/mini-chart/config")
async def get_mini_chart_config(
    symbol: str = Query(..., description="股票代码"),
    market: str = Query("CN", description="市场类型"),
    theme: str = Query("dark", description="主题"),
    locale: str = Query("zh_CN", description="语言"),
    container_id: str = Query("tradingview_mini_chart", description="容器ID"),
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    获取 TradingView 迷你图表配置
    """
    try:
        # 检查是否使用Mock数据
        use_mock = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'
        
        if use_mock:
            # 使用Mock数据
            from app.mock.unified_mock_data import get_mock_data_manager
            mock_manager = get_mock_data_manager()
            mock_data = mock_manager.get_data("tradingview_mini_chart",
                                             symbol=symbol,
                                             market=market,
                                             theme=theme,
                                             locale=locale,
                                             container_id=container_id)
            return {"success": True, "config": mock_data.get("config", {})}
        else:
            # 正常获取真实数据
            service = get_tradingview_service()

            # 转换股票代码
            tv_symbol = service.convert_symbol_to_tradingview_format(symbol, market)

            # 生成迷你图表配置
            config = service.generate_mini_chart_config(
                symbol=tv_symbol, container_id=container_id, theme=theme, locale=locale
            )

            return {"success": True, "config": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成迷你图表配置失败: {str(e)}")


@router.post("/ticker-tape/config")
async def get_ticker_tape_config(
    request: TickerTapeConfigRequest, current_user: User = Depends(get_current_user)
) -> Dict:
    """
    获取 TradingView Ticker Tape 配置
    """
    try:
        # 检查是否使用Mock数据
        use_mock = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'
        
        if use_mock:
            # 使用Mock数据
            from app.mock.unified_mock_data import get_mock_data_manager
            mock_manager = get_mock_data_manager()
            symbols = None
            if request.symbols:
                symbols = [item.dict() for item in request.symbols]
            mock_data = mock_manager.get_data("tradingview_ticker_tape",
                                             symbols=symbols,
                                             theme=request.theme,
                                             locale=request.locale,
                                             container_id=request.container_id)
            return {"success": True, "config": mock_data.get("config", {})}
        else:
            # 正常获取真实数据
            service = get_tradingview_service()

            # 转换 symbols 为字典列表
            symbols = None
            if request.symbols:
                symbols = [item.dict() for item in request.symbols]

            # 生成 Ticker Tape 配置
            config = service.generate_ticker_tape_config(
                symbols=symbols,
                container_id=request.container_id,
                theme=request.theme,
                locale=request.locale,
            )

            return {"success": True, "config": config}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"生成 Ticker Tape 配置失败: {str(e)}"
        )


@router.get("/market-overview/config")
async def get_market_overview_config(
    market: str = Query("china", description="市场类型: china, us, crypto"),
    theme: str = Query("dark", description="主题"),
    locale: str = Query("zh_CN", description="语言"),
    container_id: str = Query("tradingview_market_overview", description="容器ID"),
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    获取 TradingView 市场概览配置
    """
    try:
        # 检查是否使用Mock数据
        use_mock = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'
        
        if use_mock:
            # 使用Mock数据
            from app.mock.unified_mock_data import get_mock_data_manager
            mock_manager = get_mock_data_manager()
            mock_data = mock_manager.get_data("tradingview_market_overview",
                                             market=market,
                                             theme=theme,
                                             locale=locale,
                                             container_id=container_id)
            return {"success": True, "config": mock_data.get("config", {})}
        else:
            # 正常获取真实数据
            service = get_tradingview_service()

            # 生成市场概览配置
            config = service.generate_market_overview_config(
                container_id=container_id, theme=theme, locale=locale, market=market
            )

            return {"success": True, "config": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成市场概览配置失败: {str(e)}")


@router.get("/screener/config")
async def get_screener_config(
    market: str = Query("china", description="市场类型: china, america, crypto"),
    theme: str = Query("dark", description="主题"),
    locale: str = Query("zh_CN", description="语言"),
    container_id: str = Query("tradingview_screener", description="容器ID"),
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    获取 TradingView 股票筛选器配置
    """
    try:
        # 检查是否使用Mock数据
        use_mock = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'
        
        if use_mock:
            # 使用Mock数据
            from app.mock.unified_mock_data import get_mock_data_manager
            mock_manager = get_mock_data_manager()
            mock_data = mock_manager.get_data("tradingview_screener",
                                             market=market,
                                             theme=theme,
                                             locale=locale,
                                             container_id=container_id)
            return {"success": True, "config": mock_data.get("config", {})}
        else:
            # 正常获取真实数据
            service = get_tradingview_service()

            # 生成筛选器配置
            config = service.generate_screener_config(
                container_id=container_id, theme=theme, locale=locale, market=market
            )

            return {"success": True, "config": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成筛选器配置失败: {str(e)}")


@router.get("/symbol/convert")
async def convert_symbol(
    symbol: str = Query(..., description="股票代码"),
    market: str = Query("CN", description="市场类型"),
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    将股票代码转换为 TradingView 格式
    """
    try:
        # 检查是否使用Mock数据
        use_mock = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'
        
        if use_mock:
            # 使用Mock数据
            from app.mock.unified_mock_data import get_mock_data_manager
            mock_manager = get_mock_data_manager()
            mock_data = mock_manager.get_data("tradingview_symbol_convert",
                                             symbol=symbol,
                                             market=market)
            return {
                "success": True,
                "original_symbol": symbol,
                "tradingview_symbol": mock_data.get("tradingview_symbol", ""),
                "market": market,
            }
        else:
            # 正常获取真实数据
            service = get_tradingview_service()
            tv_symbol = service.convert_symbol_to_tradingview_format(symbol, market)

            return {
                "success": True,
                "original_symbol": symbol,
                "tradingview_symbol": tv_symbol,
                "market": market,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转换股票代码失败: {str(e)}")
