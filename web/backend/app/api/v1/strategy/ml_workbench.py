"""Canonical ML training and prediction workbench routes."""

from __future__ import annotations

import importlib.util
import os
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.responses import UnifiedResponse

from .ml_runtime_helpers import _feature_snapshot, _load_price_frame
from .runtime_state import TrainedStrategyState, runtime_store

router = APIRouter(prefix="/ml")


class MLWorkbenchModelFamily(str, Enum):
    """Canonical first-batch ML workbench model families."""

    SVM = "svm"
    LIGHTGBM = "lightgbm"


class MLWorkbenchTrainingRequest(BaseModel):
    """Canonical ML workbench training request."""

    model_family: MLWorkbenchModelFamily = Field(MLWorkbenchModelFamily.SVM, description="Model backend family")
    symbol: str = Field(..., description="Training symbol")
    start_date: str = Field(..., description="Training start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Training end date (YYYY-MM-DD)")
    feature_window: int = Field(20, ge=5, le=120, description="Rolling feature window")
    prediction_horizon: int = Field(1, ge=1, le=30, description="Prediction horizon in trading periods")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Model parameters")


class MLWorkbenchPredictionRequest(BaseModel):
    """Canonical ML workbench prediction request."""

    model_id: str = Field(..., description="Trained model ID")
    symbol: str = Field(..., description="Prediction symbol")
    prediction_horizon: int = Field(1, ge=1, le=30, description="Prediction horizon in trading periods")


def _dependency_status(package_name: str) -> dict[str, Any]:
    available = importlib.util.find_spec(package_name) is not None
    return {"available": available, "package": package_name}


def _model_backend_dependency(model_family: str | MLWorkbenchModelFamily) -> str | None:
    family = getattr(model_family, "value", model_family)
    if family == MLWorkbenchModelFamily.LIGHTGBM.value:
        return "lightgbm"
    return None


def _ensure_model_backend_available(model_family: str | MLWorkbenchModelFamily) -> None:
    dependency = _model_backend_dependency(model_family)
    if dependency and not _dependency_status(dependency)["available"]:
        family = getattr(model_family, "value", model_family)
        raise HTTPException(
            status_code=503,
            detail={
                "error_code": "ml_backend_unavailable",
                "dependency": dependency,
                "model_family": family,
                "message": f"Optional ML dependency '{dependency}' is required for {family} models.",
            },
        )


def _ml_safety_payload() -> dict[str, Any]:
    return {
        "analytical_output_only": True,
        "disclaimer": "ML predictions are analytical outputs, not a trade instruction or execution fact.",
    }


def _runtime_model_items() -> list[TrainedStrategyState]:
    return [item for item in runtime_store.list(trained_only=True) if item.parameters.get("workbench_model") is True]


def _serialize_workbench_model(item: TrainedStrategyState) -> dict[str, Any]:
    feature_context = item.parameters.get("feature_context", {})
    return {
        "model_id": item.strategy_id,
        "model_family": item.strategy_type,
        "symbol": item.symbol,
        "artifact_status": item.parameters.get("artifact_status", "runtime_registered"),
        "feature_context": feature_context,
        "metrics": item.performance,
        "feature_importance": item.feature_importance,
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat(),
        "safety": _ml_safety_payload(),
    }


def _workbench_signal(frame: pd.DataFrame, horizon: int, validation_score: float) -> tuple[dict[str, Any], float]:
    returns = frame["close"].pct_change().dropna()
    if returns.empty:
        raise HTTPException(status_code=400, detail="Insufficient samples for ML prediction")
    resolved_horizon = max(1, horizon)
    expected_return = float(returns.tail(min(len(returns), resolved_horizon)).mean()) * resolved_horizon
    signal = "buy" if expected_return > 0.002 else "sell" if expected_return < -0.002 else "hold"
    confidence = round(min(0.95, 0.5 + abs(expected_return) * 20 + validation_score * 0.2), 4)
    return {
        "signal": signal,
        "expected_return": round(expected_return, 4),
        "prediction_horizon": resolved_horizon,
    }, confidence


@router.get(
    "/runtime-status",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="ML runtime status",
    description="返回 7.1 模型训练 / 预测推理 canonical runtime 的依赖、模型目录和能力状态。",
)
async def get_ml_runtime_status():
    model_dir = Path(os.getenv("ML_MODEL_DIR", "./models"))
    optional_dependencies = {
        "lightgbm": _dependency_status("lightgbm"),
        "sklearn": _dependency_status("sklearn"),
        "joblib": _dependency_status("joblib"),
    }
    warnings = []
    if not optional_dependencies["lightgbm"]["available"]:
        warnings.append("lightgbm_unavailable")

    data = {
        "service_available": True,
        "model_backend": "runtime_registry",
        "optional_dependencies": optional_dependencies,
        "model_dir": str(model_dir),
        "model_dir_writable": model_dir.exists() and os.access(model_dir, os.W_OK),
        "legacy_api_available": True,
        "supported_operations": ["train", "predict", "models:list", "models:detail"],
        "warnings": warnings,
        "safety": _ml_safety_payload(),
    }
    return UnifiedResponse(success=True, code=200, message="ML runtime status", data=data)


@router.post(
    "/train",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Train canonical ML workbench model",
    description="训练 7.1 canonical 模型工作台运行时模型，并返回模型指标与特征上下文。",
)
async def train_ml_workbench_model(request: MLWorkbenchTrainingRequest):
    _ensure_model_backend_available(request.model_family)
    frame = _load_price_frame(request.symbol, request.start_date, request.end_date)
    if len(frame) <= request.feature_window + request.prediction_horizon:
        raise HTTPException(status_code=400, detail="Insufficient samples for ML training")

    feature_importance, training_accuracy, validation_score = _feature_snapshot(frame, request.feature_window)
    model_id = f"{request.model_family.value}_{request.symbol.split('.')[0]}_{uuid4().hex[:12]}"
    feature_context = {
        "feature_window": request.feature_window,
        "prediction_horizon": request.prediction_horizon,
        "feature_columns": ["momentum_5", "volatility_20", "return_mean"],
        "target_name": f"future_{request.prediction_horizon}d_return",
        "sample_count": int(len(frame)),
        "date_range": {"start": request.start_date, "end": request.end_date},
    }
    state = runtime_store.upsert(
        TrainedStrategyState(
            strategy_id=model_id,
            strategy_type=request.model_family.value,
            symbol=request.symbol,
            parameters={
                **dict(request.parameters or {}),
                "workbench_model": True,
                "artifact_status": "runtime_registered",
                "feature_context": feature_context,
            },
            trained=True,
            performance={
                "training_accuracy": training_accuracy,
                "validation_score": validation_score,
            },
            feature_importance=feature_importance,
        )
    )
    data = {
        "model_id": state.strategy_id,
        "model_family": state.strategy_type,
        "symbol": state.symbol,
        "artifact_status": "runtime_registered",
        "feature_context": feature_context,
        "metrics": state.performance,
        "feature_importance": state.feature_importance,
        "trained_at": state.updated_at.isoformat(),
        "warnings": [],
        "safety": _ml_safety_payload(),
    }
    return UnifiedResponse(success=True, code=200, message="ML workbench model trained", data=data)


@router.post(
    "/predict",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Predict with canonical ML workbench model",
    description="使用已注册的 7.1 canonical 运行时模型执行预测推理。",
)
async def predict_ml_workbench_model(request: MLWorkbenchPredictionRequest):
    state = runtime_store.get(request.model_id)
    if state is None or state.parameters.get("workbench_model") is not True:
        raise HTTPException(status_code=404, detail=f"Unknown model_id: {request.model_id}")

    _ensure_model_backend_available(state.strategy_type)
    feature_context = state.parameters.get("feature_context", {})
    if not feature_context.get("feature_window"):
        raise HTTPException(status_code=409, detail=f"Model metadata incompatible: {request.model_id}")
    if request.symbol != state.symbol:
        raise HTTPException(
            status_code=409,
            detail=f"Model symbol scope mismatch: {request.symbol} is not {state.symbol}",
        )
    trained_horizon = feature_context.get("prediction_horizon")
    if trained_horizon and request.prediction_horizon != trained_horizon:
        raise HTTPException(
            status_code=409,
            detail=f"Model horizon scope mismatch: {request.prediction_horizon} is not {trained_horizon}",
        )

    frame = _load_price_frame(request.symbol, "2024-01-01", datetime.now(timezone.utc).date().isoformat())
    prediction, confidence = _workbench_signal(
        frame,
        request.prediction_horizon,
        state.performance.get("validation_score", 0.5),
    )
    data = {
        "model_id": request.model_id,
        "model_family": state.strategy_type,
        "symbol": request.symbol,
        "prediction_horizon": request.prediction_horizon,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "feature_context": feature_context,
        "prediction": prediction,
        "confidence": confidence,
        "warnings": [],
        "safety": _ml_safety_payload(),
    }
    return UnifiedResponse(success=True, code=200, message="ML workbench prediction generated", data=data)


@router.get(
    "/models",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="List canonical ML workbench models",
    description="列出 7.1 canonical ML 工作台已注册的运行时模型。",
)
async def list_ml_workbench_models():
    models = [_serialize_workbench_model(item) for item in _runtime_model_items()]
    return UnifiedResponse(
        success=True,
        code=200,
        message="ML workbench models listed",
        data={"models": models, "total": len(models)},
    )


@router.get(
    "/models/{model_id}",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Get canonical ML workbench model detail",
    description="读取 7.1 canonical ML 工作台运行时模型详情。",
)
async def get_ml_workbench_model_detail(model_id: str):
    state = runtime_store.get(model_id)
    if state is None or state.parameters.get("workbench_model") is not True:
        raise HTTPException(status_code=404, detail=f"Unknown model_id: {model_id}")
    return UnifiedResponse(
        success=True,
        code=200,
        message="ML workbench model detail",
        data=_serialize_workbench_model(state),
    )
