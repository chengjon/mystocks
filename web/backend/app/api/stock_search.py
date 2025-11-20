"""
股票搜索 API
提供统一的股票搜索、报价和新闻接口
支持 A 股和 H 股（港股）
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.services.stock_search_service import (
    get_stock_search_service,
    StockSearchService,
)
from app.api.auth import get_current_user, User

router = APIRouter()


class StockSearchResult(BaseModel):
    """股票搜索结果"""

    symbol: str = Field(..., description="股票代码")
    description: str = Field(..., description="股票名称")
    displaySymbol: str = Field(..., description="显示代码")
    type: str = Field(..., description="类型")
    exchange: str = Field(..., description="交易所")
    market: Optional[str] = Field(None, description="市场")


class StockQuote(BaseModel):
    """股票报价"""

    symbol: Optional[str] = None
    name: Optional[str] = None
    current: float = Field(..., description="当前价格")
    change: float = Field(..., description="涨跌额")
    percent_change: float = Field(..., description="涨跌幅")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    open: float = Field(..., description="开盘价")
    previous_close: float = Field(..., description="昨收")
    volume: Optional[float] = Field(None, description="成交量")
    amount: Optional[float] = Field(None, description="成交额")
    timestamp: float = Field(..., description="时间戳")


class NewsItem(BaseModel):
    """新闻条目"""

    headline: str = Field(..., description="标题")
    summary: str = Field(..., description="摘要")
    source: str = Field(..., description="来源")
    datetime: float = Field(..., description="时间戳")
    url: str = Field(..., description="链接")
    image: Optional[str] = Field(None, description="图片")
    category: Optional[str] = Field(None, description="分类")


@router.get("/search", response_model=List[StockSearchResult])
async def search_stocks(
    q: str = Query(..., description="搜索关键词", min_length=1),
    market: str = Query("auto", description="市场类型: auto, cn, hk"),
    current_user: User = Depends(get_current_user),
) -> List[Dict]:
    """
    搜索股票

    支持：
    - A 股：股票代码或名称
    - H 股（港股）：股票代码或名称
    """
    try:
        # 检查是否使用Mock数据
        use_mock = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'
        
        if use_mock:
            # 使用Mock数据
            from app.mock.unified_mock_data import get_mock_data_manager
            mock_manager = get_mock_data_manager()
            mock_data = mock_manager.get_data("stock_search", keyword=q, market=market)
            return mock_data.get("data", [])
        else:
            # 正常获取真实数据
            service = get_stock_search_service()
            results = service.unified_search(q, market=market)
            return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/quote/{symbol}", response_model=StockQuote)
async def get_stock_quote(
    symbol: str,
    market: str = Query("cn", description="市场类型: cn, hk"),
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    获取股票实时报价

    Args:
        symbol: 股票代码
        market: 市场类型（cn=A股, hk=港股）
    """
    try:
        # 检查是否使用Mock数据
        use_mock = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'
        
        if use_mock:
            # 使用Mock数据
            from app.mock.unified_mock_data import get_mock_data_manager
            mock_manager = get_mock_data_manager()
            mock_data = mock_manager.get_data("stock_quote", symbol=symbol, market=market)
            return mock_data.get("data", {})
        else:
            # 正常获取真实数据
            service = get_stock_search_service()

            if market.lower() == "cn":
                quote = service.get_a_stock_realtime(symbol)
            elif market.lower() == "hk":
                quote = service.get_hk_stock_realtime(symbol)
            else:
                raise HTTPException(
                    status_code=400, detail="不支持的市场类型，仅支持: cn, hk"
                )

            if not quote:
                raise HTTPException(status_code=404, detail="未找到股票报价")

            return quote
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取报价失败: {str(e)}")


@router.get("/profile/{symbol}")
async def get_company_profile(
    symbol: str,
    market: str = Query("cn", description="市场类型: cn, hk"),
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    获取公司基本信息

    Args:
        symbol: 股票代码
        market: 市场类型
    """
    try:
        # 检查是否使用Mock数据
        use_mock = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'
        
        if use_mock:
            # 使用Mock数据
            from app.mock.unified_mock_data import get_mock_data_manager
            mock_manager = get_mock_data_manager()
            mock_data = mock_manager.get_data("stock_profile", symbol=symbol, market=market)
            return mock_data.get("data", {})
        else:
            # 正常获取真实数据
            raise HTTPException(
                status_code=501,
                detail="公司基本信息功能暂不支持，本系统仅支持 A 股和 H 股（港股），不支持美股",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取公司信息失败: {str(e)}")


@router.get("/news/{symbol}", response_model=List[NewsItem])
async def get_stock_news(
    symbol: str,
    market: str = Query("cn", description="市场类型: cn, hk"),
    days: int = Query(7, description="获取最近几天的新闻", ge=1, le=30),
    current_user: User = Depends(get_current_user),
) -> List[Dict]:
    """
    获取股票新闻

    Args:
        symbol: 股票代码
        market: 市场类型（cn=A股, hk=港股）
        days: 获取最近几天的新闻
    """
    try:
        # 检查是否使用Mock数据
        use_mock = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'
        
        if use_mock:
            # 使用Mock数据
            from app.mock.unified_mock_data import get_mock_data_manager
            mock_manager = get_mock_data_manager()
            mock_data = mock_manager.get_data("stock_news", symbol=symbol, market=market, days=days)
            return mock_data.get("data", [])
        else:
            # 正常获取真实数据
            service = get_stock_search_service()

            if market.lower() == "cn":
                news = service.get_a_stock_news(symbol, days=days)
            elif market.lower() == "hk":
                news = service.get_hk_stock_news(symbol)
            else:
                raise HTTPException(
                    status_code=400, detail="不支持的市场类型，仅支持: cn, hk"
                )

            return news
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取新闻失败: {str(e)}")


@router.get("/news/market/{category}", response_model=List[NewsItem])
async def get_market_news(
    category: str = "general",
    market: str = Query("cn", description="市场类型: cn, hk"),
    current_user: User = Depends(get_current_user),
) -> List[Dict]:
    """
    获取市场新闻

    Args:
        category: 新闻类别
        market: 市场类型（cn=A股, hk=港股）
    """
    try:
        service = get_stock_search_service()

        if market.lower() == "cn":
            news = service.get_a_stock_news(days=7)
        elif market.lower() == "hk":
            news = service.get_hk_stock_news()
        else:
            raise HTTPException(
                status_code=400, detail="不支持的市场类型，仅支持: cn, hk"
            )

        return news
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取市场新闻失败: {str(e)}")


@router.get("/recommendation/{symbol}")
async def get_recommendation_trends(
    symbol: str, current_user: User = Depends(get_current_user)
) -> Dict:
    """
    获取分析师推荐趋势

    Args:
        symbol: 股票代码
    """
    try:
        # 检查是否使用Mock数据
        use_mock = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'
        
        if use_mock:
            # 使用Mock数据
            from app.mock.unified_mock_data import get_mock_data_manager
            mock_manager = get_mock_data_manager()
            mock_data = mock_manager.get_data("stock_recommendation", symbol=symbol)
            return mock_data.get("data", {})
        else:
            # 正常获取真实数据
            raise HTTPException(
                status_code=501,
                detail="分析师推荐功能暂不支持，本系统仅支持 A 股和 H 股（港股），不支持美股",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分析师推荐失败: {str(e)}")


@router.post("/cache/clear")
async def clear_search_cache(current_user: User = Depends(get_current_user)) -> Dict:
    """
    清除搜索缓存
    """
    try:
        service = get_stock_search_service()
        service.clear_cache()

        return {"success": True, "message": "搜索缓存已清除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除缓存失败: {str(e)}")
