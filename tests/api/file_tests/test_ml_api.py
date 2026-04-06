"""
File-level route contract tests for ml.py.

这里对齐当前真实的机器学习路由面与响应模型，
替换掉生成式占位断言。
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def ml_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "password")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("BACKEND_PORT", "8020")
    monkeypatch.setenv("BACKEND_BACKUP_PORT", "8021")
    return importlib.import_module("app.api.ml")


class TestMLAPIFile:
    @pytest.mark.file_test
    def test_router_registers_expected_ml_routes(self, ml_module):
        route_methods = {(route.path, tuple(sorted(route.methods or []))) for route in ml_module.router.routes}

        assert ml_module.router.prefix == "/ml"
        assert ml_module.router.tags == ["Machine Learning"]
        assert ("/ml/tdx/data", ("POST",)) in route_methods
        assert ("/ml/tdx/stocks/{market}", ("GET",)) in route_methods
        assert ("/ml/features/generate", ("POST",)) in route_methods
        assert ("/ml/models/train", ("POST",)) in route_methods
        assert ("/ml/models/predict", ("POST",)) in route_methods
        assert ("/ml/models", ("GET",)) in route_methods
        assert ("/ml/models/{model_name}", ("GET",)) in route_methods
        assert ("/ml/models/hyperparameter-search", ("POST",)) in route_methods
        assert ("/ml/models/evaluate", ("POST",)) in route_methods

    @pytest.mark.file_test
    def test_router_contains_expected_number_of_route_method_pairs(self, ml_module):
        route_pairs = [(route.path, tuple(sorted(route.methods or []))) for route in ml_module.router.routes]

        assert len(route_pairs) == 9
        assert len(route_pairs) == len(set(route_pairs))

    @pytest.mark.file_test
    def test_response_models_remain_stable(self, ml_module):
        response_models = {(route.path, tuple(sorted(route.methods or []))): route.response_model for route in ml_module.router.routes}

        assert response_models[("/ml/tdx/data", ("POST",))] is ml_module.TdxDataResponse
        assert response_models[("/ml/tdx/stocks/{market}", ("GET",))] == ml_module.List[str]
        assert response_models[("/ml/features/generate", ("POST",))] is ml_module.FeatureGenerationResponse
        assert response_models[("/ml/models/train", ("POST",))] is ml_module.ModelTrainResponse
        assert response_models[("/ml/models/predict", ("POST",))] is ml_module.ModelPredictResponse
        assert response_models[("/ml/models", ("GET",))] is ml_module.ModelListResponse
        assert response_models[("/ml/models/{model_name}", ("GET",))] is ml_module.ModelDetailResponse
        assert response_models[("/ml/models/hyperparameter-search", ("POST",))] is ml_module.HyperparameterSearchResponse
        assert response_models[("/ml/models/evaluate", ("POST",))] is ml_module.ModelEvaluationResponse

    @pytest.mark.file_test
    def test_route_names_remain_stable_for_core_operations(self, ml_module):
        route_names = {(route.path, tuple(sorted(route.methods or []))): route.name for route in ml_module.router.routes}

        assert route_names[("/ml/models/train", ("POST",))] == "train_model"
        assert route_names[("/ml/models/predict", ("POST",))] == "predict_with_model"
        assert route_names[("/ml/models", ("GET",))] == "list_models"
        assert route_names[("/ml/models/evaluate", ("POST",))] == "evaluate_model"

    @pytest.mark.file_test
    def test_router_contains_five_model_lifecycle_routes(self, ml_module):
        model_paths = {route.path for route in ml_module.router.routes if "/ml/models" in route.path}

        assert "/ml/models/train" in model_paths
        assert "/ml/models/predict" in model_paths
        assert "/ml/models" in model_paths
        assert "/ml/models/{model_name}" in model_paths
        assert "/ml/models/hyperparameter-search" in model_paths
        assert "/ml/models/evaluate" in model_paths

    @pytest.mark.file_test
    def test_mlprediction_service_builder_exposes_service_unavailable_path(self, ml_module, monkeypatch):
        monkeypatch.setattr(ml_module, "MLPredictionService", None)
        monkeypatch.setattr(ml_module, "_ML_PREDICTION_IMPORT_ERROR", ModuleNotFoundError("missing"))

        with pytest.raises(ml_module.HTTPException) as excinfo:
            ml_module._build_ml_service()

        assert excinfo.value.status_code == 503
        assert "ML prediction service unavailable" in excinfo.value.detail

    @pytest.mark.file_test
    def test_module_docstring_mentions_training_prediction_and_evaluation(self, ml_module):
        doc = ml_module.__doc__ or ""

        assert "模型训练" in doc
        assert "预测" in doc
        assert "评估" in doc

    @pytest.mark.file_test
    def test_feature_and_tdx_route_docstrings_are_descriptive(self, ml_module):
        assert "生成特征数据" in (ml_module.generate_features.__doc__ or "")
        assert "获取通达信股票数据" in (ml_module.get_tdx_data.__doc__ or "")

    @pytest.mark.file_test
    def test_model_dir_defaults_to_models_directory(self, ml_module):
        assert ml_module.MODEL_DIR == "./models"

    @pytest.mark.file_test
    def test_router_only_exposes_get_and_post_methods(self, ml_module):
        methods = {method for route in ml_module.router.routes for method in route.methods or []}

        assert methods == {"GET", "POST"}
