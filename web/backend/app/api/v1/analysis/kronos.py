"""Kronos-backed analysis API."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body
from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.responses import (
    ErrorDetail,
    UnifiedResponse,
    create_unified_error_response,
)
from app.core.database import db_service
from app.openapi_config import COMMON_RESPONSES
from app.services.external import KronosClientError, KronosServiceUnavailableError, get_kronos_client

MAX_CANDLES = 2048
MAX_PRED_LEN = 120
MAX_SAMPLE_COUNT = 10
DEFAULT_LOOKBACK = 120


class KronosModel(str, Enum):
    """Supported external Kronos models."""

    MINI = "mini"
    SMALL = "small"
    BASE = "base"


class KronosCandle(BaseModel):
    """Canonical OHLCV candle payload sent to Kronos."""

    timestamp: datetime = Field(..., description="ISO 8601 timestamp for the candle")
    open: float = Field(..., description="Open price")
    high: float = Field(..., description="High price")
    low: float = Field(..., description="Low price")
    close: float = Field(..., description="Close price")
    volume: Optional[float] = Field(None, description="Volume, defaults to 0 when omitted")
    amount: Optional[float] = Field(None, description="Turnover amount, estimated when omitted")


class KronosRequestBase(BaseModel):
    """Shared request parameters for Kronos-backed endpoints."""

    request_id: Optional[str] = Field(None, description="Optional client-provided request id")
    model: KronosModel = Field(KronosModel.SMALL, description="Target Kronos model")
    candles: Optional[List[KronosCandle]] = Field(
        None, min_length=1, max_length=MAX_CANDLES, description="Historical candles"
    )
    symbol: Optional[str] = Field(None, description="Symbol used for local K-line lookup when candles are omitted")
    period: str = Field("day", description="K-line period for local lookup; only day/daily is supported")
    lookback: int = Field(
        DEFAULT_LOOKBACK,
        ge=1,
        le=MAX_CANDLES,
        description="Number of local candles to load when symbol-based lookup is used",
    )
    start_date: Optional[date] = Field(None, description="Start date for local lookup when using explicit date range")
    end_date: Optional[date] = Field(None, description="End date for local lookup, defaults to current date")

    @field_validator("candles")
    @classmethod
    def _validate_candles(cls, candles: Optional[List[KronosCandle]]) -> Optional[List[KronosCandle]]:
        if candles is None:
            return candles
        if len(candles) > MAX_CANDLES:
            raise ValueError(f"candles length must not exceed {MAX_CANDLES}")
        return candles

    @field_validator("symbol")
    @classmethod
    def _normalize_symbol(cls, symbol: Optional[str]) -> Optional[str]:
        if symbol is None:
            return None
        normalized = symbol.strip()
        return normalized or None

    @field_validator("period")
    @classmethod
    def _normalize_period(cls, period: str) -> str:
        normalized = period.strip().lower()
        if normalized not in {"day", "daily"}:
            raise ValueError("period must be 'day' or 'daily'")
        return normalized

    @model_validator(mode="after")
    def _validate_data_source(self) -> "KronosRequestBase":
        if self.candles:
            return self
        if self.symbol:
            if self.start_date and self.end_date and self.start_date > self.end_date:
                raise ValueError("start_date must be earlier than or equal to end_date")
            if self.start_date and self.lookback != DEFAULT_LOOKBACK:
                raise ValueError("lookback cannot be customized when start_date/end_date range is provided")
            if self.start_date and self.end_date is None:
                raise ValueError("end_date is required when start_date is provided")
            return self
        raise ValueError("Either candles or symbol must be provided")


class KronosPredictRequest(KronosRequestBase):
    """Forecast request for external Kronos service."""

    pred_len: int = Field(..., ge=1, le=MAX_PRED_LEN, description="Prediction horizon")
    sample_count: int = Field(1, ge=1, le=MAX_SAMPLE_COUNT, description="Parallel sample count")
    top_p: float = Field(0.9, gt=0, le=1.0, description="Nucleus sampling probability")
    temperature: float = Field(1.0, gt=0, le=5.0, description="Sampling temperature")


class KronosEncodeRequest(KronosRequestBase):
    """Encoding request for external Kronos service."""


def _success_response_spec(description: str, example: dict[str, Any]) -> dict[int, dict[str, Any]]:
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


def _error_response_spec(description: str, example: dict[str, Any]) -> dict[str, Any]:
    return {
        "description": description,
        "content": {
            "application/json": {
                "example": example,
            }
        },
    }


KRONOS_PREDICT_REQUEST_EXAMPLES = {
    "direct_candles": {
        "summary": "直接上传标准化 K 线",
        "description": "由调用方直接提供标准化后的 OHLCV candles，适合脚本、服务直连或已有本地预处理结果的场景。",
        "value": {
            "request_id": "predict-direct-001",
            "model": "small",
            "candles": [
                {
                    "timestamp": "2026-04-17T09:30:00+00:00",
                    "open": 10.1,
                    "high": 10.5,
                    "low": 10.0,
                    "close": 10.3,
                    "volume": 123456,
                    "amount": 1260000,
                },
                {
                    "timestamp": "2026-04-18T09:30:00+00:00",
                    "open": 10.3,
                    "high": 10.6,
                    "low": 10.2,
                    "close": 10.4,
                    "volume": 120000,
                    "amount": 1248000,
                },
            ],
            "pred_len": 5,
            "sample_count": 2,
            "top_p": 0.9,
            "temperature": 1.0,
        },
    },
    "local_symbol_range": {
        "summary": "按本地股票与日期区间取数",
        "description": "由 MyStocks 先按 symbol 和日期区间查询本地日线，再统一转发给 Kronos。",
        "value": {
            "request_id": "predict-range-001",
            "model": "small",
            "symbol": "600519",
            "period": "day",
            "start_date": "2026-04-01",
            "end_date": "2026-04-17",
            "pred_len": 10,
            "sample_count": 1,
            "top_p": 0.9,
            "temperature": 1.0,
        },
    },
}

KRONOS_ENCODE_REQUEST_EXAMPLES = {
    "encode_direct_candles": {
        "summary": "编码标准化 K 线",
        "description": "把历史 K 线序列编码成 Kronos token 序列，适合后续模式检索或上游 AI 工具消费。",
        "value": {
            "request_id": "encode-direct-001",
            "model": "small",
            "candles": [
                {
                    "timestamp": "2026-04-17T09:30:00+00:00",
                    "open": 10.1,
                    "high": 10.5,
                    "low": 10.0,
                    "close": 10.3,
                    "volume": 123456,
                    "amount": 1260000,
                }
            ],
        },
    },
    "encode_local_symbol": {
        "summary": "按本地 symbol 与 lookback 编码",
        "description": "由 MyStocks 先读取本地日线数据，再调用 Kronos 编码。",
        "value": {
            "request_id": "encode-symbol-001",
            "model": "small",
            "symbol": "000001",
            "period": "day",
            "lookback": 120,
            "end_date": "2026-04-17",
        },
    },
}

KRONOS_404_LOCAL_DATA_NOT_FOUND_EXAMPLE = {
    "success": False,
    "code": 404,
    "message": "No local daily K-line data found for symbol 688999",
    "data": None,
    "request_id": "predict-missing-001",
    "errors": [
        {
            "field": None,
            "code": "KRONOS_LOCAL_DATA_NOT_FOUND",
            "message": "No local daily K-line data found for symbol 688999",
        }
    ],
}

KRONOS_422_VALIDATION_EXAMPLE = {
    "success": False,
    "code": 422,
    "message": "lookback cannot be customized when start_date/end_date range is provided",
    "data": None,
    "request_id": "predict-invalid-001",
    "errors": [
        {
            "field": None,
            "code": "VALIDATION_ERROR",
            "message": "lookback cannot be customized when start_date/end_date range is provided",
        }
    ],
}

KRONOS_503_UNAVAILABLE_EXAMPLE = {
    "success": False,
    "code": 503,
    "message": "Kronos service request failed after 3 attempts: timeout",
    "data": None,
    "request_id": "predict-timeout-001",
    "errors": [
        {
            "field": None,
            "code": "TIMEOUT",
            "message": "Kronos service request failed after 3 attempts: timeout",
        }
    ],
}


KRONOS_ROUTE_RESPONSES = {
    400: COMMON_RESPONSES[400],
    404: _error_response_spec("Local K-line data required by MyStocks was not found.", KRONOS_404_LOCAL_DATA_NOT_FOUND_EXAMPLE),
    422: _error_response_spec("MyStocks validation failed before or after calling Kronos.", KRONOS_422_VALIDATION_EXAMPLE),
    500: COMMON_RESPONSES[500],
    503: _error_response_spec("External Kronos service unavailable.", KRONOS_503_UNAVAILABLE_EXAMPLE),
}

router = APIRouter(
    prefix="/kronos",
    tags=["Kronos Analysis"],
    responses=KRONOS_ROUTE_RESPONSES,
)

KRONOS_PREDICT_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Kronos forecast completed",
    "data": {
        "predictions": [
            {
                "timestamp": "2026-04-17T10:00:00+00:00",
                "open": 10.4,
                "high": 10.6,
                "low": 10.2,
                "close": 10.5,
                "volume": 120000.0,
                "amount": 1250000.0,
            }
        ],
        "confidence": 0.78,
        "meta": {
            "model": "small",
            "device": "cuda:0",
            "degraded": False,
            "cached": False,
            "latency_ms": 420,
            "queue_wait_ms": 18,
        },
    },
}

KRONOS_ENCODE_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Kronos encoding completed",
    "data": {
        "s1_tokens": [1, 2, 3],
        "s2_tokens": [18, 19, 20],
        "reconstruction_error": 0.0132,
        "meta": {
            "model": "small",
            "device": "cuda:0",
            "degraded": False,
            "cached": False,
            "latency_ms": 35,
            "queue_wait_ms": 0,
        },
    },
}

KRONOS_STATUS_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Kronos status retrieved",
    "data": {
        "health": "healthy",
        "active_model": "small",
        "loaded_models": ["small"],
        "device": "cuda:0",
        "queue_depth": 0,
        "requests_inflight": 0,
        "version": "1.0.0",
        "meta": {
            "model": "small",
            "device": "cuda:0",
            "degraded": False,
            "cached": False,
            "latency_ms": 3,
            "queue_wait_ms": 0,
        },
    },
}

KRONOS_PREDICT_RESPONSES = _success_response_spec("Kronos forecast result normalized for MyStocks.", KRONOS_PREDICT_SUCCESS_EXAMPLE)
KRONOS_ENCODE_RESPONSES = _success_response_spec("Kronos encoding result normalized for MyStocks.", KRONOS_ENCODE_SUCCESS_EXAMPLE)
KRONOS_STATUS_RESPONSES = _success_response_spec("Kronos runtime status normalized for MyStocks.", KRONOS_STATUS_SUCCESS_EXAMPLE)


def _normalize_candles(candles: List[KronosCandle]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for candle in candles:
        avg_price = (candle.open + candle.high + candle.low + candle.close) / 4.0
        volume = float(candle.volume or 0.0)
        amount = float(candle.amount if candle.amount is not None else volume * avg_price)
        normalized.append(
            {
                "timestamp": candle.timestamp.astimezone(timezone.utc).isoformat(),
                "open": float(candle.open),
                "high": float(candle.high),
                "low": float(candle.low),
                "close": float(candle.close),
                "volume": volume,
                "amount": amount,
            }
        )
    return normalized


def _load_local_daily_candles(symbol: str, lookback: int, end_date: Optional[date]) -> List[KronosCandle]:
    normalized_end = end_date or datetime.now(timezone.utc).date()
    start_date = normalized_end - timedelta(days=max(lookback * 3, 30))
    df = db_service.query_daily_kline(symbol, start_date.isoformat(), normalized_end.isoformat())
    if df.empty:
        raise KronosClientError(
            f"No local daily K-line data found for symbol {symbol}",
            code="KRONOS_LOCAL_DATA_NOT_FOUND",
            status_code=404,
        )

    date_col = "trade_date" if "trade_date" in df.columns else "date"
    df = df.sort_values(date_col).tail(lookback)
    candles: List[KronosCandle] = []
    for row in df.to_dict("records"):
        row_date = row.get(date_col)
        timestamp = pd_to_datetime_iso(row_date)
        candles.append(
            KronosCandle(
                timestamp=timestamp,
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row.get("volume", 0) or 0),
                amount=float(row.get("amount")) if row.get("amount") is not None else None,
            )
        )
    return candles


def _load_local_daily_candles_by_range(symbol: str, start_date: date, end_date: date) -> List[KronosCandle]:
    df = db_service.query_daily_kline(symbol, start_date.isoformat(), end_date.isoformat())
    if df.empty:
        raise KronosClientError(
            f"No local daily K-line data found for symbol {symbol}",
            code="KRONOS_LOCAL_DATA_NOT_FOUND",
            status_code=404,
        )

    date_col = "trade_date" if "trade_date" in df.columns else "date"
    df = df.sort_values(date_col)
    candles: List[KronosCandle] = []
    for row in df.to_dict("records"):
        row_date = row.get(date_col)
        timestamp = pd_to_datetime_iso(row_date)
        candles.append(
            KronosCandle(
                timestamp=timestamp,
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row.get("volume", 0) or 0),
                amount=float(row.get("amount")) if row.get("amount") is not None else None,
            )
        )
    return candles


def pd_to_datetime_iso(value: Any) -> datetime:
    if isinstance(value, datetime):
        dt_value = value
    elif isinstance(value, date):
        dt_value = datetime.combine(value, datetime.min.time())
    else:
        dt_value = datetime.fromisoformat(str(value))
    if dt_value.tzinfo is None:
        dt_value = dt_value.replace(tzinfo=timezone.utc)
    return dt_value.astimezone(timezone.utc)


def _resolve_candles(request: KronosRequestBase) -> List[KronosCandle]:
    if request.candles:
        return request.candles
    assert request.symbol is not None
    if request.start_date is not None:
        end_date = request.end_date or datetime.now(timezone.utc).date()
        return _load_local_daily_candles_by_range(request.symbol, request.start_date, end_date)
    return _load_local_daily_candles(request.symbol, request.lookback, request.end_date)


def _build_predict_payload(request: KronosPredictRequest) -> Dict[str, Any]:
    candles = _resolve_candles(request)
    return {
        "request_id": request.request_id,
        "model": request.model.value,
        "candles": _normalize_candles(candles),
        "pred_len": request.pred_len,
        "sample_count": request.sample_count,
        "top_p": request.top_p,
        "temperature": request.temperature,
    }


def _build_encode_payload(request: KronosEncodeRequest) -> Dict[str, Any]:
    candles = _resolve_candles(request)
    return {
        "request_id": request.request_id,
        "model": request.model.value,
        "candles": _normalize_candles(candles),
    }


def _normalize_result(result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        **result.get("data", {}),
        "meta": {
            "model": result.get("meta", {}).get("model"),
            "device": result.get("meta", {}).get("device"),
            "degraded": bool(result.get("meta", {}).get("degraded", False)),
            "cached": bool(result.get("meta", {}).get("cached", False)),
            "latency_ms": result.get("meta", {}).get("latency_ms"),
            "queue_wait_ms": result.get("meta", {}).get("queue_wait_ms"),
            "batch_size": result.get("meta", {}).get("batch_size"),
        },
    }


def _service_unavailable_response(request_id: Optional[str], exc: KronosServiceUnavailableError) -> UnifiedResponse[Dict[str, Any]]:
    return create_unified_error_response(
        503,
        str(exc),
        errors=_error_detail(exc.code, str(exc)),
        request_id=request_id,
    )


def _error_detail(code: str, message: str) -> List[ErrorDetail]:
    return [ErrorDetail(field=None, code=code, message=message)]


@router.post(
    "/predict",
    response_model=UnifiedResponse[Dict[str, Any]],
    responses=KRONOS_PREDICT_RESPONSES,
    summary="Run Kronos OHLCV forecast through external service",
    description=(
        "支持两种输入模式：直接提交标准化 candles，或提交 symbol + lookback / start_date + end_date，"
        "由 MyStocks 先查询本地日线再转发给 Kronos。"
    ),
)
async def predict_with_kronos(
    request: KronosPredictRequest = Body(
        ...,
        description="Canonical Kronos forecast request",
        openapi_examples=KRONOS_PREDICT_REQUEST_EXAMPLES,
    ),
) -> UnifiedResponse[Dict[str, Any]]:
    client = get_kronos_client()
    try:
        result = await client.predict_ohlcv(_build_predict_payload(request))
        return UnifiedResponse(
            success=True,
            code=200,
            message="Kronos forecast completed",
            data=_normalize_result(result),
            request_id=result.get("request_id") or request.request_id,
        )
    except KronosClientError as exc:
        code = 404 if exc.status_code == 404 else 422
        return create_unified_error_response(
            code,
            str(exc),
            errors=_error_detail(exc.code, str(exc)),
            request_id=request.request_id,
        )
    except KronosServiceUnavailableError as exc:
        return _service_unavailable_response(request.request_id, exc)


@router.post(
    "/encode",
    response_model=UnifiedResponse[Dict[str, Any]],
    responses=KRONOS_ENCODE_RESPONSES,
    summary="Run Kronos candle encoding through external service",
    description="支持直接 candles 或本地 symbol 取数模式，返回 Kronos token 编码结果和状态元信息。",
)
async def encode_with_kronos(
    request: KronosEncodeRequest = Body(
        ...,
        description="Canonical Kronos encoding request",
        openapi_examples=KRONOS_ENCODE_REQUEST_EXAMPLES,
    ),
) -> UnifiedResponse[Dict[str, Any]]:
    client = get_kronos_client()
    try:
        result = await client.encode_kline(_build_encode_payload(request))
        return UnifiedResponse(
            success=True,
            code=200,
            message="Kronos encoding completed",
            data=_normalize_result(result),
            request_id=result.get("request_id") or request.request_id,
        )
    except KronosClientError as exc:
        code = 404 if exc.status_code == 404 else 422
        return create_unified_error_response(
            code,
            str(exc),
            errors=_error_detail(exc.code, str(exc)),
            request_id=request.request_id,
        )
    except KronosServiceUnavailableError as exc:
        return _service_unavailable_response(request.request_id, exc)


@router.get(
    "/status",
    response_model=UnifiedResponse[Dict[str, Any]],
    responses=KRONOS_STATUS_RESPONSES,
    summary="Get external Kronos runtime status through MyStocks",
    description="返回外部 Kronos 服务的可用性、当前模型、队列深度与延迟元信息，供前端或运维侧观测。",
)
async def get_kronos_status() -> UnifiedResponse[Dict[str, Any]]:
    client = get_kronos_client()
    try:
        result = await client.get_status()
        return UnifiedResponse(
            success=True,
            code=200,
            message="Kronos status retrieved",
            data=_normalize_result(result),
            request_id=result.get("request_id"),
        )
    except KronosServiceUnavailableError as exc:
        return _service_unavailable_response(None, exc)
