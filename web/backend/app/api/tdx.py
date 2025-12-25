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

from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import Optional
from datetime import date, datetime, timedelta

from app.schemas.tdx_schemas import (
    RealTimeQuoteResponse,
    KlineResponse,
    IndexQuoteResponse,
    ErrorResponse,
    TdxHealthResponse,
)
from app.services.tdx_service import get_tdx_service, TdxService
from app.core.security import get_current_active_user, User

router = APIRouter(prefix="/api/tdx", tags=["TDX行情数据"])


# ==================== 实时行情 ====================


@router.get(
    "/quote/{symbol}",
    response_model=RealTimeQuoteResponse,
    summary="获取股票实时行情",
    description="查询指定股票的实时行情数据,包括最新价、涨跌幅、成交量、五档行情等",
)
async def get_stock_quote(
    symbol: str,
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
        kline_data = service.get_stock_kline(
            symbol=symbol, start_date=start_date, end_date=end_date, period=period
        )

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
    description="查询指定指数的实时点位和涨跌幅",
)
async def get_index_quote(
    symbol: str,
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
    description="查询指数历史K线数据,支持多种周期",
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
        kline_data = service.get_index_kline(
            symbol=symbol, start_date=start_date, end_date=end_date, period=period
        )

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
    description="检查TDX服务器连接状态",
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
