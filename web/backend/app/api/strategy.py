"""
股票策略API端点
提供策略执行、查询、管理等RESTful接口
"""

import logging
import re
from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from app.openapi_config import COMMON_RESPONSES
from app.core.responses import ErrorCodes, ResponseMessages, create_error_response, create_success_response
from app.services.data_source_factory import DataSourceFactory
from app.services.strategy_service import get_strategy_service

logger = logging.getLogger(__name__)

STRATEGY_ROUTE_RESPONSES = {
    400: COMMON_RESPONSES[400],
    404: COMMON_RESPONSES[404],
    500: COMMON_RESPONSES[500],
}

router = APIRouter(responses=STRATEGY_ROUTE_RESPONSES)


def _strategy_success_response_spec(description: str, example: dict) -> dict[int, dict]:
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


STRATEGY_DEFINITIONS_RESPONSE_EXAMPLE = {
    "success": True,
    "data": {
        "definitions": [
            {
                "id": 1,
                "strategy_code": "volume_surge",
                "strategy_name_cn": "放量突破",
                "strategy_name_en": "Volume Surge Breakout",
                "description": "识别成交量显著放大且价格突破关键区间的股票。",
                "parameters": {"volume_ratio": 2.0, "lookback_days": 20},
                "is_active": True,
                "created_at": "2026-04-01T09:00:00",
                "updated_at": "2026-04-07T15:30:00",
            },
            {
                "id": 2,
                "strategy_code": "ma_crossover",
                "strategy_name_cn": "均线金叉",
                "strategy_name_en": "MA Crossover",
                "description": "识别短周期均线上穿长周期均线的趋势启动信号。",
                "parameters": {"fast_ma": 5, "slow_ma": 20},
                "is_active": True,
                "created_at": "2026-04-01T09:00:00",
                "updated_at": "2026-04-07T15:30:00",
            },
        ],
        "total": 2,
    },
    "message": "操作成功",
    "timestamp": "2026-04-08T04:20:00Z",
    "request_id": "req-strategy-definitions-001",
}

STRATEGY_RUN_SINGLE_RESPONSE_EXAMPLE = {
    "success": True,
    "data": {
        "strategy_result": {
            "success": True,
            "match_result": True,
            "message": "匹配策略条件",
        },
        "strategy_code": "volume_surge",
        "symbol": "600519.SH",
        "execution_success": True,
    },
    "message": "策略volume_surge执行完成",
    "timestamp": "2026-04-08T04:20:00Z",
    "request_id": "req-strategy-run-single-001",
}

STRATEGY_RUN_BATCH_RESPONSE_EXAMPLE = {
    "success": True,
    "data": {
        "batch_result": {
            "success": True,
            "total": 3,
            "matched": 1,
            "failed": 0,
            "message": "完成: 总计3, 匹配1, 失败0",
        },
        "strategy_code": "ma_crossover",
        "market": "A",
        "execution_success": True,
        "processed_symbols": "600519.SH,000001.SZ,510300.SH",
    },
    "message": "批量策略ma_crossover执行完成",
    "timestamp": "2026-04-08T04:20:00Z",
    "request_id": "req-strategy-run-batch-001",
}

STRATEGY_RESULTS_RESPONSE_EXAMPLE = {
    "success": True,
    "data": {
        "strategy_results": [
            {
                "id": 101,
                "strategy_code": "volume_surge",
                "symbol": "600519.SH",
                "stock_name": "贵州茅台",
                "check_date": "2026-04-07",
                "match_result": True,
                "match_score": 92,
                "match_details": {"volume_ratio": 2.4, "breakout_price": 1748.5},
                "latest_price": "1754.66",
                "change_percent": "1.24",
                "created_at": "2026-04-07T15:00:00",
            },
            {
                "id": 102,
                "strategy_code": "volume_surge",
                "symbol": "000001.SZ",
                "stock_name": "平安银行",
                "check_date": "2026-04-07",
                "match_result": False,
                "match_score": 48,
                "match_details": {"volume_ratio": 1.1, "breakout_price": None},
                "latest_price": "12.64",
                "change_percent": "0.32",
                "created_at": "2026-04-07T15:00:00",
            },
        ],
        "total": 2,
        "filters": {
            "strategy_code": "volume_surge",
            "symbol": None,
            "check_date": "2026-04-07",
            "match_result": None,
        },
    },
    "message": "查询策略结果成功，共2条记录",
    "timestamp": "2026-04-08T04:20:00Z",
    "request_id": "req-strategy-results-001",
}

MATCHED_STOCKS_RESPONSE_EXAMPLE = {
    "success": True,
    "data": [
        {
            "id": 101,
            "strategy_code": "volume_surge",
            "symbol": "600519.SH",
            "stock_name": "贵州茅台",
            "check_date": "2026-04-07",
            "match_result": True,
            "match_score": 92,
            "match_details": {"volume_ratio": 2.4, "breakout_price": 1748.5},
            "latest_price": "1754.66",
            "change_percent": "1.24",
            "created_at": "2026-04-07T15:00:00",
        },
        {
            "id": 103,
            "strategy_code": "volume_surge",
            "symbol": "510300.SH",
            "stock_name": "沪深300ETF",
            "check_date": "2026-04-07",
            "match_result": True,
            "match_score": 88,
            "match_details": {"volume_ratio": 2.1, "breakout_price": 4.12},
            "latest_price": "4.18",
            "change_percent": "0.96",
            "created_at": "2026-04-07T15:00:00",
        },
    ],
    "total": 2,
    "message": "找到2只匹配股票",
}

STRATEGY_SUMMARY_RESPONSE_EXAMPLE = {
    "success": True,
    "data": {
        "strategy_summary": [
            {
                "strategy_code": "volume_surge",
                "strategy_name_cn": "放量突破",
                "strategy_name_en": "Volume Surge Breakout",
                "matched_count": 2,
                "check_date": "2026-04-07",
            },
            {
                "strategy_code": "ma_crossover",
                "strategy_name_cn": "均线金叉",
                "strategy_name_en": "MA Crossover",
                "matched_count": 5,
                "check_date": "2026-04-07",
            },
        ],
        "check_date": "2026-04-07",
    },
    "message": "获取策略统计摘要成功",
    "timestamp": "2026-04-08T04:20:00Z",
    "request_id": "req-strategy-summary-001",
}

STRATEGY_DEFINITIONS_RESPONSES = _strategy_success_response_spec(
    "策略定义列表查询成功。", STRATEGY_DEFINITIONS_RESPONSE_EXAMPLE
)
STRATEGY_RUN_SINGLE_RESPONSES = _strategy_success_response_spec("单只股票策略运行成功。", STRATEGY_RUN_SINGLE_RESPONSE_EXAMPLE)
STRATEGY_RUN_BATCH_RESPONSES = _strategy_success_response_spec("批量策略运行成功。", STRATEGY_RUN_BATCH_RESPONSE_EXAMPLE)
STRATEGY_RESULTS_RESPONSES = _strategy_success_response_spec("策略结果查询成功。", STRATEGY_RESULTS_RESPONSE_EXAMPLE)
MATCHED_STOCKS_RESPONSES = _strategy_success_response_spec("匹配股票列表查询成功。", MATCHED_STOCKS_RESPONSE_EXAMPLE)
STRATEGY_SUMMARY_RESPONSES = _strategy_success_response_spec("策略统计摘要查询成功。", STRATEGY_SUMMARY_RESPONSE_EXAMPLE)


# ==================== 请求/响应模型 ====================


class StrategyRunRequest(BaseModel):
    """运行策略请求"""

    strategy_code: str = Field(..., description="策略代码", min_length=1, max_length=50, pattern=r"^[a-z0-9_]+$")
    symbol: Optional[str] = Field(
        None, description="单个股票代码", min_length=1, max_length=20, pattern=r"^[A-Z0-9.]+$"
    )
    symbols: Optional[List[str]] = Field(None, description="多个股票代码列表")
    check_date: Optional[str] = Field(None, description="检查日期 YYYY-MM-DD", pattern=r"^\d{4}-\d{2}-\d{2}$")
    limit: Optional[int] = Field(None, description="处理数量限制", ge=1, le=10000)

    @field_validator("symbols")
    @classmethod
    def validate_symbols(cls, v: Optional[List[str]], info) -> Optional[List[str]]:
        """验证股票代码列表"""
        if v is None:
            return v

        if not v:  # 空列表
            raise ValueError("股票代码列表不能为空")

        if len(v) > 1000:  # 限制列表长度
            raise ValueError("股票代码列表长度不能超过1000")

        # 验证每个股票代码格式
        for symbol in v:
            if not symbol:
                raise ValueError("股票代码不能为空")
            if len(symbol) > 20:
                raise ValueError(f'股票代码 "{symbol}" 长度超过限制')
            if not re.match(r"^[A-Z0-9.]+$", symbol):
                raise ValueError(f'股票代码 "{symbol}" 格式无效，只能包含大写字母、数字和点')

        # 去重并转换为大写
        return list(set(s.upper() for s in v))

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: Optional[str]) -> Optional[str]:
        """验证单个股票代码"""
        if v is None:
            return v
        return v.upper()

    @field_validator("check_date")
    @classmethod
    def validate_check_date(cls, v: Optional[str]) -> Optional[str]:
        """验证日期格式和范围"""
        if v is None:
            return v

        try:
            parsed_date = datetime.strptime(v, "%Y-%m-%d").date()
            today = date.today()

            # 检查日期不能是未来
            if parsed_date > today:
                raise ValueError("检查日期不能是未来日期")

            # 检查日期不能太久远（比如不能早于1990年）
            if parsed_date.year < 1990:
                raise ValueError("检查日期不能早于1990年")

            return v
        except ValueError as e:
            if "does not match format" in str(e):
                raise ValueError("日期格式错误，请使用 YYYY-MM-DD 格式")
            raise

    @field_validator("strategy_code")
    @classmethod
    def validate_strategy_code(cls, v: str) -> str:
        """验证策略代码"""
        # 预定义的策略代码列表（用于验证）
        valid_strategies = {
            "volume_surge",
            "price_breakout",
            "ma_crossover",
            "rsi_oversold",
            "rsi_overbought",
            "macd_bullish",
            "macd_bearish",
            "bollinger_squeeze",
            "atr_breakout",
            "stochastic_turn",
            "williams_r_oversold",
            "williams_r_overbought",
            "cci_extreme",
            "roc_momentum",
            "obv_divergence",
            "vwap_reversion",
            "gap_up",
            "gap_down",
            "doji_pattern",
            "hammer_pattern",
            "engulfing_pattern",
        }

        if v not in valid_strategies:
            raise ValueError(f'无效的策略代码 "{v}"，支持的策略: {", ".join(sorted(valid_strategies))}')

        return v


class StrategyResultResponse(BaseModel):
    """策略结果响应"""

    success: bool = Field(..., description="执行是否成功")
    data: Optional[dict] = Field(None, description="策略结果数据")
    message: str = Field(..., description="响应消息", min_length=1, max_length=500)


class StrategyQueryParams(BaseModel):
    """策略查询参数"""

    strategy_code: Optional[str] = Field(
        None, description="策略代码", min_length=1, max_length=50, pattern=r"^[a-z0-9_]+$"
    )
    symbol: Optional[str] = Field(None, description="股票代码", min_length=1, max_length=20, pattern=r"^[A-Z0-9.]+$")
    check_date: Optional[str] = Field(None, description="检查日期 YYYY-MM-DD", pattern=r"^\d{4}-\d{2}-\d{2}$")
    match_result: Optional[bool] = Field(None, description="是否匹配结果")
    limit: int = Field(100, description="返回数量", ge=1, le=1000)
    offset: int = Field(0, description="偏移量", ge=0, le=10000)

    @field_validator("check_date")
    @classmethod
    def validate_check_date(cls, v: Optional[str]) -> Optional[str]:
        """验证日期格式"""
        if v is None:
            return v

        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("日期格式错误，请使用 YYYY-MM-DD 格式")


class MarketFilterParams(BaseModel):
    """市场过滤参数"""

    market: str = Field("A", description="市场类型", pattern=r"^(A|SH|SZ|CYB|KCB)$")
    limit: Optional[int] = Field(None, description="处理数量限制", ge=1, le=5000)

    @field_validator("market")
    @classmethod
    def validate_market(cls, v: str) -> str:
        """验证市场类型"""
        market_mapping = {"A": "全部A股", "SH": "上海主板", "SZ": "深圳主板", "CYB": "创业板", "KCB": "科创板"}
        return market_mapping.get(v, v)


# ==================== 策略定义相关 ====================


@router.get(
    "/definitions",
    tags=["strategy"],
    summary="获取策略定义列表",
    responses=STRATEGY_DEFINITIONS_RESPONSES,
)
async def get_strategy_definitions():
    """
    获取所有策略定义

    Returns:
        所有可用策略的定义列表
    """
    try:
        # 使用数据源工厂
        data_source_factory = DataSourceFactory()
        strategy_adapter = await data_source_factory.get_data_source("strategy")

        result = await strategy_adapter.get_data("definitions")

        if "error" in result:
            raise HTTPException(
                status_code=500,
                detail=create_error_response(ErrorCodes.EXTERNAL_SERVICE_ERROR, result["error"]).model_dump(),
            )

        definitions_data = result.get("data", [])

        return create_success_response(
            data={"definitions": definitions_data, "total": len(definitions_data)}, message=ResponseMessages.SUCCESS
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("获取策略定义失败: %(e)s")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 策略执行相关 ====================


@router.post(
    "/run/single",
    tags=["strategy"],
    summary="运行单股策略",
    responses=STRATEGY_RUN_SINGLE_RESPONSES,
)
async def run_strategy_single(
    strategy_code: str = Query(..., description="策略代码", min_length=1, max_length=50, pattern=r"^[a-z0-9_]+$"),
    symbol: str = Query(..., description="股票代码", min_length=1, max_length=20, pattern=r"^[A-Z0-9.]+$"),
    stock_name: Optional[str] = Query(None, description="股票名称", max_length=100),
    check_date: Optional[str] = Query(None, description="检查日期 YYYY-MM-DD", pattern=r"^\d{4}-\d{2}-\d{2}$"),
):
    """
    对单只股票运行策略

    Args:
        strategy_code: 策略代码 (如: volume_surge)
        symbol: 股票代码 (如: 600519)
        stock_name: 股票名称 (可选)
        check_date: 检查日期 (可选，默认今天)

    Returns:
        策略执行结果
    """
    try:
        # 使用数据源工厂
        data_source_factory = DataSourceFactory()
        strategy_adapter = await data_source_factory.get_data_source("strategy")

        params = {"strategy_code": strategy_code, "symbol": symbol, "stock_name": stock_name, "check_date": check_date}

        result = await strategy_adapter.get_data("run_single", params)

        if "error" in result:
            raise HTTPException(
                status_code=500,
                detail=create_error_response(ErrorCodes.EXTERNAL_SERVICE_ERROR, result["error"]).model_dump(),
            )

        return create_success_response(
            data={
                "strategy_result": result.get("data", {}),
                "strategy_code": strategy_code,
                "symbol": symbol,
                "execution_success": result.get("success", False),
            },
            message=result.get("message", f"策略{strategy_code}执行完成"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("运行单只股票策略失败: %(e)s")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(ErrorCodes.INTERNAL_SERVER_ERROR, f"运行策略失败: {str(e)}").model_dump(),
        )


@router.post(
    "/run/batch",
    tags=["strategy"],
    summary="批量运行策略",
    responses=STRATEGY_RUN_BATCH_RESPONSES,
)
async def run_strategy_batch(
    strategy_code: str = Query(..., description="策略代码", min_length=1, max_length=50, pattern=r"^[a-z0-9_]+$"),
    symbols: Optional[str] = Query(
        None, description="股票代码列表，逗号分隔", max_length=20000  # 1000个股票代码 * 20字符 + 999个逗号
    ),
    market: Optional[str] = Query("A", description="市场类型 (A/SH/SZ/CYB/KCB)", pattern=r"^(A|SH|SZ|CYB|KCB)$"),
    limit: Optional[int] = Query(None, description="限制处理数量", ge=1, le=5000),
    check_date: Optional[str] = Query(None, description="检查日期 YYYY-MM-DD", pattern=r"^\d{4}-\d{2}-\d{2}$"),
):
    """
    批量运行策略

    Args:
        strategy_code: 策略代码
        symbols: 股票代码列表，逗号分隔 (如: 600519,000001)
        market: 市场类型 (A=全部, SH=上证, SZ=深证, CYB=创业板, KCB=科创板)
        limit: 限制处理数量
        check_date: 检查日期 (可选)

    Returns:
        批量执行结果统计
    """
    try:
        # 使用数据源工厂
        data_source_factory = DataSourceFactory()
        strategy_adapter = await data_source_factory.get_data_source("strategy")

        params = {
            "strategy_code": strategy_code,
            "symbols": symbols,
            "market": market,
            "limit": limit,
            "check_date": check_date,
        }

        result = await strategy_adapter.get_data("run_batch", params)

        if "error" in result:
            raise HTTPException(
                status_code=500,
                detail=create_error_response(ErrorCodes.EXTERNAL_SERVICE_ERROR, result["error"]).model_dump(),
            )

        return create_success_response(
            data={
                "batch_result": result.get("data", {}),
                "strategy_code": strategy_code,
                "market": market,
                "execution_success": result.get("success", False),
                "processed_symbols": symbols,
            },
            message=result.get("message", f"批量策略{strategy_code}执行完成"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("批量运行策略失败: %(e)s")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(ErrorCodes.INTERNAL_SERVER_ERROR, f"批量运行策略失败: {str(e)}").model_dump(),
        )


# ==================== 策略结果查询 ====================


@router.get(
    "/results",
    tags=["strategy"],
    summary="查询策略运行结果",
    responses=STRATEGY_RESULTS_RESPONSES,
)
async def query_strategy_results(
    strategy_code: Optional[str] = Query(
        None, description="策略代码", min_length=1, max_length=50, pattern=r"^[a-z0-9_]+$"
    ),
    symbol: Optional[str] = Query(None, description="股票代码", min_length=1, max_length=20, pattern=r"^[A-Z0-9.]+$"),
    check_date: Optional[str] = Query(None, description="检查日期 YYYY-MM-DD", pattern=r"^\d{4}-\d{2}-\d{2}$"),
    match_result: Optional[bool] = Query(None, description="是否匹配"),
    limit: int = Query(100, description="返回数量", ge=1, le=1000),
    offset: int = Query(0, description="偏移量", ge=0, le=10000),
):
    """
    查询策略结果

    Args:
        strategy_code: 策略代码 (可选)
        symbol: 股票代码 (可选)
        check_date: 检查日期 (可选)
        match_result: 是否匹配 (可选)
        limit: 返回数量 (默认100)
        offset: 偏移量 (默认0)

    Returns:
        策略结果列表
    """
    try:
        service = get_strategy_service()

        # 解析日期
        check_date_obj = None
        if check_date:
            check_date_obj = datetime.strptime(check_date, "%Y-%m-%d").date()

        results = service.query_strategy_results(
            strategy_code=strategy_code,
            symbol=symbol,
            check_date=check_date_obj,
            match_result=match_result,
            limit=limit,
            offset=offset,
        )

        return create_success_response(
            data={
                "strategy_results": results,
                "total": len(results),
                "filters": {
                    "strategy_code": strategy_code,
                    "symbol": symbol,
                    "check_date": check_date,
                    "match_result": match_result,
                },
            },
            message=f"查询策略结果成功，共{len(results)}条记录",
        )

    except Exception as e:
        logger.error("查询策略结果失败: %(e)s")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(ErrorCodes.DATABASE_ERROR, f"查询策略结果失败: {str(e)}").model_dump(),
        )


@router.get(
    "/matched-stocks",
    tags=["strategy"],
    summary="获取匹配股票列表",
    responses=MATCHED_STOCKS_RESPONSES,
)
async def get_matched_stocks(
    strategy_code: str = Query(..., description="策略代码", min_length=1, max_length=50, pattern=r"^[a-z0-9_]+$"),
    check_date: Optional[str] = Query(None, description="检查日期 YYYY-MM-DD", pattern=r"^\d{4}-\d{2}-\d{2}$"),
    limit: int = Query(100, description="返回数量", ge=1, le=1000),
):
    """
    获取匹配指定策略的股票列表

    Args:
        strategy_code: 策略代码
        check_date: 检查日期 (可选，默认最新)
        limit: 返回数量 (默认100)

    Returns:
        匹配的股票列表
    """
    try:
        service = get_strategy_service()

        # 解析日期
        check_date_obj = None
        if check_date:
            check_date_obj = datetime.strptime(check_date, "%Y-%m-%d").date()

        stocks = service.get_matched_stocks(strategy_code=strategy_code, check_date=check_date_obj, limit=limit)

        return {
            "success": True,
            "data": stocks,
            "total": len(stocks),
            "message": f"找到{len(stocks)}只匹配股票",
        }

    except Exception as e:
        logger.error("获取匹配股票失败: %(e)s")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 统计分析相关 ====================


@router.get(
    "/stats/summary",
    tags=["strategy"],
    summary="获取策略统计摘要",
    responses=STRATEGY_SUMMARY_RESPONSES,
)
async def get_strategy_summary(
    check_date: Optional[str] = Query(None, description="检查日期 YYYY-MM-DD", pattern=r"^\d{4}-\d{2}-\d{2}$")
):
    """
    获取策略统计摘要

    Args:
        check_date: 检查日期 (可选，默认今天)

    Returns:
        各策略的匹配数量统计
    """
    try:
        service = get_strategy_service()

        # 解析日期
        check_date_obj = None
        if check_date:
            check_date_obj = datetime.strptime(check_date, "%Y-%m-%d").date()
        else:
            check_date_obj = datetime.now().date()

        # 获取所有策略
        strategies = service.get_strategy_definitions()

        # 统计每个策略的匹配数量
        summary = []
        for strategy in strategies:
            matched_stocks = service.get_matched_stocks(
                strategy_code=strategy["strategy_code"],
                check_date=check_date_obj,
                limit=10000,  # 大数以获取全部
            )

            summary.append(
                {
                    "strategy_code": strategy["strategy_code"],
                    "strategy_name_cn": strategy["strategy_name_cn"],
                    "strategy_name_en": strategy["strategy_name_en"],
                    "matched_count": len(matched_stocks),
                    "check_date": check_date or datetime.now().strftime("%Y-%m-%d"),
                }
            )

        return create_success_response(
            data={
                "strategy_summary": summary,
                "check_date": (
                    check_date_obj.strftime("%Y-%m-%d") if check_date_obj else datetime.now().strftime("%Y-%m-%d")
                ),
            },
            message="获取策略统计摘要成功",
        )

    except Exception as e:
        logger.error("获取策略统计失败: %(e)s")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(ErrorCodes.DATABASE_ERROR, f"获取策略统计失败: {str(e)}").model_dump(),
        )
