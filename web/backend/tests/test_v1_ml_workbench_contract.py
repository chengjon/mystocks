from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.v1.strategy.machine_learning", None)
    return importlib.import_module("app.api.v1.strategy.machine_learning")


def _load_workbench_module():
    _load_module()
    return importlib.import_module("app.api.v1.strategy.ml_workbench")


def _reset_runtime_state() -> None:
    state = importlib.import_module("app.api.v1.strategy.runtime_state")
    state.runtime_store.reset()


def test_v1_ml_workbench_registers_canonical_routes():
    module = _load_module()
    route_methods = {(route.path, tuple(sorted(route.methods or []))) for route in module.router.routes}

    assert ("/strategies/ml/runtime-status", ("GET",)) in route_methods
    assert ("/strategies/ml/train", ("POST",)) in route_methods
    assert ("/strategies/ml/predict", ("POST",)) in route_methods
    assert ("/strategies/ml/models", ("GET",)) in route_methods
    assert ("/strategies/ml/models/{model_id}", ("GET",)) in route_methods


async def test_v1_ml_runtime_status_is_machine_readable():
    module = _load_module()

    payload = await module.get_ml_runtime_status()

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["service_available"] is True
    assert "lightgbm" in payload.data["optional_dependencies"]
    assert payload.data["legacy_api_available"] is True
    assert {"train", "predict", "models:list", "models:detail"}.issubset(
        set(payload.data["supported_operations"])
    )


async def test_v1_ml_runtime_status_reports_missing_optional_dependency(monkeypatch):
    module = _load_module()
    workbench_module = _load_workbench_module()

    real_find_spec = workbench_module.importlib.util.find_spec

    def fake_find_spec(package_name: str):
        if package_name == "lightgbm":
            return None
        return real_find_spec(package_name)

    monkeypatch.setattr(workbench_module.importlib.util, "find_spec", fake_find_spec)

    payload = await module.get_ml_runtime_status()

    assert payload.success is True
    assert payload.data["optional_dependencies"]["lightgbm"]["available"] is False
    assert "lightgbm_unavailable" in payload.data["warnings"]


async def test_v1_ml_training_rejects_unavailable_lightgbm_dependency(monkeypatch):
    module = _load_module()
    workbench_module = _load_workbench_module()

    real_find_spec = workbench_module.importlib.util.find_spec

    def fake_find_spec(package_name: str):
        if package_name == "lightgbm":
            return None
        return real_find_spec(package_name)

    monkeypatch.setattr(workbench_module.importlib.util, "find_spec", fake_find_spec)

    with pytest.raises(module.HTTPException) as excinfo:
        await module.train_ml_workbench_model(
            module.MLWorkbenchTrainingRequest(
                model_family=module.MLWorkbenchModelFamily.LIGHTGBM,
                symbol="600519.SH",
                start_date="2024-01-01",
                end_date="2024-12-31",
                feature_window=20,
                prediction_horizon=5,
            )
        )

    assert excinfo.value.status_code == 503
    assert excinfo.value.detail["error_code"] == "ml_backend_unavailable"
    assert excinfo.value.detail["dependency"] == "lightgbm"


async def test_v1_ml_training_rejects_insufficient_samples(monkeypatch):
    module = _load_module()
    workbench_module = _load_workbench_module()
    short_frame = pd.DataFrame(
        {
            "trade_date": pd.date_range("2024-01-01", periods=6, freq="B"),
            "open": [1, 2, 3, 4, 5, 6],
            "high": [2, 3, 4, 5, 6, 7],
            "low": [1, 1, 2, 3, 4, 5],
            "close": [1, 2, 3, 4, 5, 6],
            "volume": [100] * 6,
        }
    )
    monkeypatch.setattr(workbench_module, "_load_price_frame", lambda *args, **kwargs: short_frame)

    with pytest.raises(module.HTTPException) as excinfo:
        await module.train_ml_workbench_model(
            module.MLWorkbenchTrainingRequest(
                model_family=module.MLWorkbenchModelFamily.SVM,
                symbol="600519.SH",
                start_date="2024-01-01",
                end_date="2024-01-31",
                feature_window=5,
                prediction_horizon=5,
            )
        )

    assert excinfo.value.status_code == 400
    assert "Insufficient samples" in excinfo.value.detail


async def test_v1_ml_training_prediction_and_model_registry_are_canonical():
    _reset_runtime_state()
    module = _load_module()

    train_payload = await module.train_ml_workbench_model(
        module.MLWorkbenchTrainingRequest(
            model_family=module.MLWorkbenchModelFamily.SVM,
            symbol="600519.SH",
            start_date="2024-01-01",
            end_date="2024-12-31",
            feature_window=20,
            prediction_horizon=5,
        )
    )

    assert train_payload.success is True
    assert train_payload.code == 200
    assert train_payload.data["model_id"].startswith("svm_600519_")
    assert train_payload.data["artifact_status"] == "runtime_registered"
    assert train_payload.data["feature_context"]["feature_window"] == 20
    assert train_payload.data["safety"]["analytical_output_only"] is True
    assert "not a trade instruction" in train_payload.data["safety"]["disclaimer"]

    list_payload = await module.list_ml_workbench_models()
    assert list_payload.success is True
    assert list_payload.data["total"] == 1
    model_id = list_payload.data["models"][0]["model_id"]

    detail_payload = await module.get_ml_workbench_model_detail(model_id)
    assert detail_payload.success is True
    assert detail_payload.data["model_id"] == model_id
    assert detail_payload.data["feature_context"]["feature_window"] == 20

    predict_payload = await module.predict_ml_workbench_model(
        module.MLWorkbenchPredictionRequest(
            model_id=model_id,
            symbol="600519.SH",
            prediction_horizon=5,
        )
    )

    assert predict_payload.success is True
    assert predict_payload.code == 200
    assert predict_payload.data["model_id"] == model_id
    assert predict_payload.data["symbol"] == "600519.SH"
    assert predict_payload.data["prediction_horizon"] == 5
    assert predict_payload.data["prediction"]["signal"] in {"buy", "sell", "hold"}
    assert predict_payload.data["safety"]["analytical_output_only"] is True


async def test_v1_ml_prediction_rejects_missing_model():
    _reset_runtime_state()
    module = _load_module()

    with pytest.raises(module.HTTPException) as excinfo:
        await module.predict_ml_workbench_model(
            module.MLWorkbenchPredictionRequest(
                model_id="missing_model",
                symbol="600519.SH",
                prediction_horizon=5,
            )
        )

    assert excinfo.value.status_code == 404
    assert "Unknown model_id" in excinfo.value.detail


async def test_v1_ml_prediction_rejects_incompatible_model_metadata():
    _reset_runtime_state()
    module = _load_module()
    module.runtime_store.upsert(
        module.TrainedStrategyState(
            strategy_id="broken_model",
            strategy_type="svm",
            symbol="600519.SH",
            parameters={"workbench_model": True},
            trained=True,
            performance={"validation_score": 0.5},
            feature_importance={},
        )
    )

    with pytest.raises(module.HTTPException) as excinfo:
        await module.predict_ml_workbench_model(
            module.MLWorkbenchPredictionRequest(
                model_id="broken_model",
                symbol="600519.SH",
                prediction_horizon=5,
            )
        )

    assert excinfo.value.status_code == 409
    assert "Model metadata incompatible" in excinfo.value.detail


async def test_v1_ml_prediction_rejects_unavailable_model_backend(monkeypatch):
    _reset_runtime_state()
    module = _load_module()
    workbench_module = _load_workbench_module()
    module.runtime_store.upsert(
        module.TrainedStrategyState(
            strategy_id="lightgbm_model",
            strategy_type="lightgbm",
            symbol="600519.SH",
            parameters={
                "workbench_model": True,
                "feature_context": {
                    "feature_window": 20,
                    "prediction_horizon": 5,
                },
            },
            trained=True,
            performance={"validation_score": 0.5},
            feature_importance={},
        )
    )
    real_find_spec = workbench_module.importlib.util.find_spec

    def fake_find_spec(package_name: str):
        if package_name == "lightgbm":
            return None
        return real_find_spec(package_name)

    monkeypatch.setattr(workbench_module.importlib.util, "find_spec", fake_find_spec)

    with pytest.raises(module.HTTPException) as excinfo:
        await module.predict_ml_workbench_model(
            module.MLWorkbenchPredictionRequest(
                model_id="lightgbm_model",
                symbol="600519.SH",
                prediction_horizon=5,
            )
        )

    assert excinfo.value.status_code == 503
    assert excinfo.value.detail["error_code"] == "ml_backend_unavailable"
    assert excinfo.value.detail["dependency"] == "lightgbm"


async def test_v1_ml_prediction_rejects_symbol_scope_mismatch():
    _reset_runtime_state()
    module = _load_module()
    train_payload = await module.train_ml_workbench_model(
        module.MLWorkbenchTrainingRequest(
            model_family=module.MLWorkbenchModelFamily.SVM,
            symbol="600519.SH",
            start_date="2024-01-01",
            end_date="2024-12-31",
            feature_window=20,
            prediction_horizon=5,
        )
    )

    with pytest.raises(module.HTTPException) as excinfo:
        await module.predict_ml_workbench_model(
            module.MLWorkbenchPredictionRequest(
                model_id=train_payload.data["model_id"],
                symbol="000001.SZ",
                prediction_horizon=5,
            )
        )

    assert excinfo.value.status_code == 409
    assert "Model symbol scope mismatch" in excinfo.value.detail


async def test_v1_ml_prediction_rejects_horizon_scope_mismatch():
    _reset_runtime_state()
    module = _load_module()
    train_payload = await module.train_ml_workbench_model(
        module.MLWorkbenchTrainingRequest(
            model_family=module.MLWorkbenchModelFamily.SVM,
            symbol="600519.SH",
            start_date="2024-01-01",
            end_date="2024-12-31",
            feature_window=20,
            prediction_horizon=5,
        )
    )

    with pytest.raises(module.HTTPException) as excinfo:
        await module.predict_ml_workbench_model(
            module.MLWorkbenchPredictionRequest(
                model_id=train_payload.data["model_id"],
                symbol="600519.SH",
                prediction_horizon=10,
            )
        )

    assert excinfo.value.status_code == 409
    assert "Model horizon scope mismatch" in excinfo.value.detail
