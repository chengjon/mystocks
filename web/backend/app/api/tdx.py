"""
TDX数据API路由

提供RESTful接口:
- GET /api/tdx/quote/{symbol} - 获取实时行情
- GET /api/tdx/kline - 获取历史K线(多周期)
- GET /api/tdx/index/quote/{symbol} - 获取指数行情
- GET /api/tdx/index/kline - 获取指数K线
- GET /api/tdx/health - 健康检查

所有接口均需JWT认证
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.core.security import User, get_current_active_user
from app.schemas.tdx_schemas import (
    IndexQuoteResponse,
    KlineResponse,
    RealTimeQuoteResponse,
    TdxHealthResponse,
)
from app.services.tdx_service import TdxService, get_tdx_service

router = APIRouter()


def _success_response_spec(status_code: int, description: str, example: object) -> dict[int, dict]:
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


TDX_INDEX_QUOTE_RESPONSES = {
    **_error_response_spec(
        400,
        "指数代码无效",
        {"detail": "无效的指数代码,必须为6位数字"},
    ),
    **_error_response_spec(
        500,
        "获取指数行情失败",
        {"detail": "获取指数行情失败: TDX 服务暂不可用"},
    ),
    **_success_response_spec(
        200,
        "指数实时行情",
        {
            "code": "000001",
            "name": "上证指数",
            "price": 3250.5,
            "pre_close": 3245.0,
            "open": 3246.0,
            "high": 3252.0,
            "low": 3244.0,
            "volume": 1234567890,
            "amount": 450000000000.0,
            "change": 5.5,
            "change_pct": 0.17,
            "timestamp": "2026-04-05 14:30:00",
        },
    ),
}

TDX_HEALTH_RESPONSES = {
    **_error_response_spec(
        500,
        "TDX 服务检查失败",
        {
            "status": "error",
            "tdx_connected": False,
            "timestamp": "2026-04-05 14:30:00",
            "server_info": {"error": "TDX 服务连接异常"},
        },
    ),
    **_success_response_spec(
        200,
        "TDX 服务健康状态",
        {
            "status": "healthy",
            "tdx_connected": True,
            "timestamp": "2026-04-05 14:30:00",
            "server_info": {"host": "127.0.0.1", "port": 7709},
        },
    ),
}

TDX_STOCK_QUOTE_RESPONSES = {
    **_error_response_spec(
        400,
        "股票代码无效",
        {"detail": "无效的股票代码,必须为6位数字"},
    ),
    **_error_response_spec(
        500,
        "获取股票实时行情失败",
        {"detail": "获取实时行情失败: TDX 服务暂不可用"},
    ),
    **_success_response_spec(
        200,
        "股票实时行情",
        {
            "code": "600519",
            "name": "贵州茅台",
            "price": 1850.5,
            "pre_close": 1845.0,
            "open": 1846.0,
            "high": 1852.0,
            "low": 1844.0,
            "volume": 123456,
            "amount": 228000000.0,
            "bid1": 1850.0,
            "bid1_volume": 100,
            "ask1": 1851.0,
            "ask1_volume": 150,
            "timestamp": "2026-04-07 14:30:00",
            "change": 5.5,
            "change_pct": 0.3,
        },
    ),
}

TDX_STOCK_KLINE_RESPONSES = {
    **_error_response_spec(
        400,
        "K线查询参数无效",
        {"detail": "无效的K线周期,支持的周期: 1m, 5m, 15m, 30m, 1h, 1d"},
    ),
    **_error_response_spec(
        500,
        "获取股票K线失败",
        {"detail": "获取K线数据失败: TDX 服务暂不可用"},
    ),
    **_success_response_spec(
        200,
        "股票历史K线数据",
        {
            "code": "600519",
            "period": "1d",
            "data": [
                {
                    "date": "2026-04-01 00:00:00",
                    "open": 1838.0,
                    "high": 1855.0,
                    "low": 1832.5,
                    "close": 1850.5,
                    "volume": 96543,
                    "amount": 178560000.0,
                },
                {
                    "date": "2026-04-02 00:00:00",
                    "open": 1851.0,
                    "high": 1862.0,
                    "low": 1846.0,
                    "close": 1858.6,
                    "volume": 88421,
                    "amount": 164230000.0,
                },
            ],
            "count": 2,
        },
    ),
}

TDX_INDEX_KLINE_RESPONSES = {
    **_error_response_spec(
        400,
        "指数K线查询参数无效",
        {"detail": "无效的指数代码,必须为6位数字"},
    ),
    **_error_response_spec(
        500,
        "获取指数K线失败",
        {"detail": "获取指数K线失败: TDX 服务暂不可用"},
    ),
    **_success_response_spec(
        200,
        "指数历史K线数据",
        {
            "code": "000300",
            "period": "1d",
            "data": [
                {
                    "date": "2026-04-01 00:00:00",
                    "open": 3650.2,
                    "high": 3678.4,
                    "low": 3642.8,
                    "close": 3670.1,
                    "volume": 245678901,
                    "amount": 356800000000.0,
                },
                {
                    "date": "2026-04-02 00:00:00",
                    "open": 3672.0,
                    "high": 3686.5,
                    "low": 3659.7,
                    "close": 3664.3,
                    "volume": 231234567,
                    "amount": 340500000000.0,
                },
            ],
            "count": 2,
        },
    ),
}


# ==================== 实时行情 ====================


@router.get(
    "/quote/{symbol}",
    response_model=RealTimeQuoteResponse,
    summary="获取股票实时行情",
    description="查询指定股票的实时行情数据,包括最新价、涨跌幅、成交量、五档行情等",
    responses=TDX_STOCK_QUOTE_RESPONSES,
)
async def get_stock_quote(
    symbol: str = Path(..., description="6 位数字股票代码，例如 600519。"),
    current_user: User = Depends(get_current_active_user),
    service: TdxService = Depends(get_tdx_service),
):
    """
    获取股票实时行情

    **参数:**
    - symbol: 6位数字股票代码(如: 600519)

    **返回:**
    - 实时行情数据,包含最新价、涨跌幅、五档行情等

    **示例:**
    ```
    GET /api/tdx/quote/600519
    ```

    **认证:** 需要JWT令牌
    """
    try:
        # 验证股票代码格式
        if not symbol or len(symbol) != 6 or not symbol.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的股票代码,必须为6位数字",
            )

        # 调用服务获取行情
        quote = service.get_real_time_quote(symbol)

        return RealTimeQuoteResponse(**quote)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取实时行情失败: {str(e)}",
        )


# ==================== 股票K线 ====================


@router.get(
    "/kline",
    response_model=KlineResponse,
    summary="获取股票K线数据",
    description="查询股票历史K线数据,支持多种周期(1m/5m/15m/30m/1h/1d)",
    responses=TDX_STOCK_KLINE_RESPONSES,
)
async def get_stock_kline(
    symbol: str = Query(..., description="股票代码(6位数字)"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    period: str = Query(default="1d", description="K线周期: 1m/5m/15m/30m/1h/1d"),
    current_user: User = Depends(get_current_active_user),
    service: TdxService = Depends(get_tdx_service),
):
    """
    获取股票K线数据

    **参数:**
    - symbol: 6位数字股票代码(如: 600519)
    - start_date: 开始日期(可选,默认为30天前)
    - end_date: 结束日期(可选,默认为今天)
    - period: K线周期
      - 1m: 1分钟
      - 5m: 5分钟
      - 15m: 15分钟
      - 30m: 30分钟
      - 1h: 1小时
      - 1d: 日线(默认)

    **返回:**
    - K线数据列表,包含开高低收成交量等

    **示例:**
    ```
    GET /api/tdx/kline?symbol=600519&period=5m&start_date=2025-10-01&end_date=2025-10-15
    ```

    **认证:** 需要JWT令牌
    """
    try:
        # 验证股票代码
        if not symbol or len(symbol) != 6 or not symbol.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的股票代码,必须为6位数字",
            )

        # 验证周期
        valid_periods = ["1m", "5m", "15m", "30m", "1h", "1d"]
        if period not in valid_periods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的K线周期,支持的周期: {', '.join(valid_periods)}",
            )

        # 默认日期范围
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            # 根据周期设置默认起始日期
            days_map = {
                "1m": 2,  # 1分钟: 2天
                "5m": 5,  # 5分钟: 5天
                "15m": 10,  # 15分钟: 10天
                "30m": 15,  # 30分钟: 15天
                "1h": 30,  # 1小时: 30天
                "1d": 90,  # 日线: 90天
            }
            days = days_map.get(period, 30)
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # 调用服务获取K线
        kline_data = service.get_stock_kline(symbol=symbol, start_date=start_date, end_date=end_date, period=period)

        return KlineResponse(**kline_data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取K线数据失败: {str(e)}",
        )


# ==================== 指数行情 ====================


@router.get(
    "/index/quote/{symbol}",
    response_model=IndexQuoteResponse,
    summary="获取指数实时行情",
    description="查询指定指数的实时点位、涨跌幅和成交额等行情字段，适用于指数监控看板。",
    responses=TDX_INDEX_QUOTE_RESPONSES,
)
async def get_index_quote(
    symbol: str = Path(..., description="6 位数字指数代码，例如 000001 或 399001。"),
    current_user: User = Depends(get_current_active_user),
    service: TdxService = Depends(get_tdx_service),
):
    """
    获取指数实时行情

    **参数:**
    - symbol: 6位数字指数代码
      - 000001: 上证指数
      - 399001: 深证成指
      - 399006: 创业板指

    **返回:**
    - 指数实时点位、涨跌幅等数据

    **示例:**
    ```
    GET /api/tdx/index/quote/000001
    ```

    **认证:** 需要JWT令牌
    """
    try:
        # 验证指数代码
        if not symbol or len(symbol) != 6 or not symbol.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的指数代码,必须为6位数字",
            )

        # 调用服务获取指数行情
        quote = service.get_index_quote(symbol)

        return IndexQuoteResponse(**quote)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取指数行情失败: {str(e)}",
        )


# ==================== 指数K线 ====================


@router.get(
    "/index/kline",
    response_model=KlineResponse,
    summary="获取指数K线数据",
    description="查询指数历史K线数据，支持分钟级到日线周期，并允许按日期区间筛选用于指数回溯分析。",
    responses=TDX_INDEX_KLINE_RESPONSES,
)
async def get_index_kline(
    symbol: str = Query(..., description="指数代码(6位数字)"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    period: str = Query(default="1d", description="K线周期: 1m/5m/15m/30m/1h/1d"),
    current_user: User = Depends(get_current_active_user),
    service: TdxService = Depends(get_tdx_service),
):
    """
    获取指数K线数据

    **参数:**
    - symbol: 6位数字指数代码
    - start_date: 开始日期(可选,默认为90天前)
    - end_date: 结束日期(可选,默认为今天)
    - period: K线周期(同股票K线)

    **返回:**
    - 指数K线数据列表

    **示例:**
    ```
    GET /api/tdx/index/kline?symbol=000001&period=1d&start_date=2025-01-01
    ```

    **认证:** 需要JWT令牌
    """
    try:
        # 验证指数代码
        if not symbol or len(symbol) != 6 or not symbol.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的指数代码,必须为6位数字",
            )

        # 验证周期
        valid_periods = ["1m", "5m", "15m", "30m", "1h", "1d"]
        if period not in valid_periods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的K线周期,支持的周期: {', '.join(valid_periods)}",
            )

        # 默认日期范围
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            days_map = {"1m": 2, "5m": 5, "15m": 10, "30m": 15, "1h": 30, "1d": 90}
            days = days_map.get(period, 90)
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # 调用服务获取指数K线
        kline_data = service.get_index_kline(symbol=symbol, start_date=start_date, end_date=end_date, period=period)

        return KlineResponse(**kline_data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取指数K线失败: {str(e)}",
        )


# ==================== 健康检查 ====================


@router.get(
    "/health",
    response_model=TdxHealthResponse,
    summary="TDX服务健康检查",
    description="检查 TDX 服务的连接状态和服务端信息，用于后端运行状态探活与排障。",
    responses=TDX_HEALTH_RESPONSES,
)
async def health_check(service: TdxService = Depends(get_tdx_service)):
    """
    TDX服务健康检查

    **返回:**
    - 服务状态和TDX连接信息

    **示例:**
    ```
    GET /api/tdx/health
    ```

    **注意:** 此接口不需要认证
    """
    try:
        health_info = service.check_connection()
        return TdxHealthResponse(**health_info)
    except Exception as e:
        return TdxHealthResponse(
            status="error",
            tdx_connected=False,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            server_info={"error": str(e)},
        )
