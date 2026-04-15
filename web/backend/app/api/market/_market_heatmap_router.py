"""Market heatmap routes."""

from datetime import datetime

from fastapi import APIRouter, Query

from app.core.cache_utils import cache_response
from app.core.config import settings
from app.core.exceptions import BusinessException

router = APIRouter()


def _is_market_heatmap_mock_enabled() -> bool:
    return settings.use_mock_apis


def _get_mock_market_heatmap(market: str, limit: int) -> dict:
    from app.mock.unified_mock_data import get_mock_data_manager

    mock_manager = get_mock_data_manager()
    return mock_manager.get_data("market_heatmap", market=market, limit=limit)


def _success_response_spec(description: str, example: dict) -> dict[int, dict]:
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


MARKET_HEATMAP_RESPONSES = {
    **_success_response_spec(
        "市场热力图数据",
        {
            "success": True,
            "data": [
                {
                    "symbol": "600519",
                    "name": "贵州茅台",
                    "price": 1688.0,
                    "change": 25.8,
                    "change_pct": 1.55,
                    "volume": 4589123,
                    "amount": 7742000000.0,
                    "market_cap": 2120000000000.0,
                }
            ],
            "total": 1,
            "timestamp": "2026-04-07T09:30:00",
            "source": "real",
        },
    ),
}


@router.get("/heatmap", summary="获取市场热力图数据", responses=MARKET_HEATMAP_RESPONSES)
@cache_response("market_heatmap", ttl=60)
async def get_market_heatmap(
    market: str = Query(default="cn", description="市场类型: cn(A股)/hk(港股)"),
    limit: int = Query(default=50, ge=10, le=200, description="返回股票数量"),
):
    """获取市场热力图数据，用于可视化展示各股票的涨跌情况。"""
    try:
        if _is_market_heatmap_mock_enabled():
            mock_data = _get_mock_market_heatmap(market=market, limit=limit)
            return {
                "success": True,
                "data": mock_data.get("data", []),
                "total": len(mock_data.get("data", [])),
                "timestamp": mock_data.get("timestamp"),
                "source": "mock",
            }

        import akshare as ak

        if market == "cn":
            dataframe = ak.stock_zh_a_spot_em().head(limit)
        elif market == "hk":
            dataframe = ak.stock_hk_spot_em().head(limit)
        else:
            raise BusinessException(
                detail=f"不支持的市场类型: {market}",
                status_code=400,
                error_code="UNSUPPORTED_MARKET_TYPE",
            )

        result = []
        for _, row in dataframe.iterrows():
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
                        "market_cap": float(row.get("总市值", 0)) if "总市值" in row else None,
                    }
                )
            except Exception:
                continue

        result = sorted(result, key=lambda item: item["change_pct"], reverse=True)
        return {
            "success": True,
            "data": result,
            "total": len(result),
            "timestamp": datetime.now().isoformat(),
            "source": "real",
        }

    except ImportError:
        raise BusinessException(detail="AKShare库未安装", status_code=500, error_code="LIBRARY_NOT_INSTALLED")
    except Exception as error:
        raise BusinessException(
            detail=f"获取热力图数据失败: {str(error)}",
            status_code=500,
            error_code="HEATMAP_DATA_FAILED",
        )
