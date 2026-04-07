"""
机器学习 API 端点
提供模型训练、预测、评估等功能
"""

import os
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, Path

from app.core.security import User, get_current_user
from app.schemas.ml_schemas import (
    FeatureGenerationRequest,
    FeatureGenerationResponse,
    HyperparameterSearchRequest,
    HyperparameterSearchResponse,
    ModelDetailResponse,
    ModelEvaluationRequest,
    ModelEvaluationResponse,
    ModelInfo,
    ModelListResponse,
    ModelPredictRequest,
    ModelPredictResponse,
    ModelTrainRequest,
    ModelTrainResponse,
    TdxDataRequest,
    TdxDataResponse,
)
from app.services.feature_engineering_service import FeatureEngineeringService
from app.services.tdx_parser_service import TdxDataService

try:
    from app.services.ml_prediction_service import MLPredictionService
except ModuleNotFoundError as exc:
    MLPredictionService = None
    _ML_PREDICTION_IMPORT_ERROR: ModuleNotFoundError | None = exc
else:
    _ML_PREDICTION_IMPORT_ERROR = None

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

# 初始化服务
tdx_service = TdxDataService()
feature_service = FeatureEngineeringService()

# 模型存储目录
MODEL_DIR = os.getenv("ML_MODEL_DIR", "./models")

ML_MARKET_PATH_DESCRIPTION = "市场代码，支持 sh（上交所）或 sz（深交所）。"

ML_TDX_DATA_REQUEST_EXAMPLE = {"stock_code": "000001", "market": "sh"}

ML_FEATURE_GENERATION_REQUEST_EXAMPLE = {
    "stock_code": "000001",
    "market": "sh",
    "step": 10,
    "include_indicators": True,
}

ML_MODEL_TRAIN_REQUEST_EXAMPLE = {
    "stock_code": "000001",
    "market": "sh",
    "step": 10,
    "test_size": 0.2,
    "model_name": "a_share_lgbm_v1",
    "model_params": {"n_estimators": 100, "learning_rate": 0.1},
}

ML_MODEL_PREDICT_REQUEST_EXAMPLE = {
    "model_name": "a_share_lgbm_v1",
    "stock_code": "000001",
    "market": "sh",
    "days": 1,
}

ML_HYPERPARAMETER_SEARCH_REQUEST_EXAMPLE = {
    "stock_code": "000001",
    "market": "sh",
    "step": 10,
    "cv": 5,
    "param_grid": {
        "num_leaves": [15, 31],
        "n_estimators": [50, 100],
        "learning_rate": [0.05, 0.1],
    },
}

ML_MODEL_EVALUATION_REQUEST_EXAMPLE = {
    "model_name": "a_share_lgbm_v1",
    "stock_code": "000001",
    "market": "sh",
}


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


ML_MODEL_LIST_RESPONSES = {
    **_success_response_spec(
        200,
        "已保存模型列表",
        {
            "total": 2,
            "models": [
                {
                    "name": "a_share_lgbm_v1",
                    "path": "./models/a_share_lgbm_v1.pkl",
                    "trained_at": "2026-04-05T09:30:00",
                    "test_rmse": 1.82,
                    "test_r2": 0.78,
                    "train_samples": 2400,
                    "test_samples": 600,
                    "feature_dim": 32,
                },
                {
                    "name": "hs300_xgboost_v2",
                    "path": "./models/hs300_xgboost_v2.pkl",
                    "trained_at": "2026-04-04T15:00:00",
                    "test_rmse": 2.11,
                    "test_r2": 0.73,
                    "train_samples": 1800,
                    "test_samples": 450,
                    "feature_dim": 28,
                },
            ],
        },
    ),
    **_error_response_spec(
        500,
        "模型列表查询失败",
        {"detail": "读取模型目录失败: [Errno 2] No such file or directory: './models'"},
    ),
}

ML_MODEL_DETAIL_RESPONSES = {
    **_success_response_spec(
        200,
        "模型详情",
        {
            "name": "a_share_lgbm_v1",
            "metadata": {
                "model_type": "lightgbm",
                "trained_at": "2026-04-05T09:30:00",
                "stock_scope": "A-share",
                "market": "sh",
                "metrics": {
                    "rmse": 1.82,
                    "r2": 0.78,
                    "step": 10,
                },
            },
            "training_history": [
                {"epoch": 1, "train_loss": 0.043, "val_loss": 0.051},
                {"epoch": 2, "train_loss": 0.039, "val_loss": 0.047},
            ],
            "feature_importance": [
                {"feature": "close", "importance": 0.31},
                {"feature": "volume", "importance": 0.18},
            ],
        },
    ),
    **_error_response_spec(
        404,
        "指定模型不存在",
        {"detail": "模型不存在: a_share_lgbm_v9"},
    ),
    **_error_response_spec(
        503,
        "模型服务当前不可用",
        {"detail": "ML prediction service unavailable: missing optional dependency"},
    ),
    **_error_response_spec(
        500,
        "模型详情查询失败",
        {"detail": "加载模型详情失败: metadata.json is corrupted"},
    ),
}

ML_TDX_STOCKS_RESPONSES = {
    **_success_response_spec(
        200,
        "指定市场可用股票代码列表",
        ["000001", "000002", "600519", "601318"],
    ),
    **_error_response_spec(
        500,
        "股票代码列表查询失败",
        {"detail": "读取通达信股票目录失败: market index unavailable"},
    ),
}


def _build_ml_service() -> "MLPredictionService":
    if MLPredictionService is None:
        raise HTTPException(
            status_code=503,
            detail=f"ML prediction service unavailable: {_ML_PREDICTION_IMPORT_ERROR}",
        )
    return MLPredictionService(model_dir=MODEL_DIR)


# ==================== 通达信数据相关 ====================


@router.post("/tdx/data", response_model=TdxDataResponse)
async def get_tdx_data(
    request: TdxDataRequest = Body(..., example=ML_TDX_DATA_REQUEST_EXAMPLE),
    current_user: User = Depends(get_current_user),
):
    """
    获取通达信股票数据

    - **stock_code**: 股票代码（如：000001）
    - **market**: 市场代码（sh/sz）
    """
    try:
        df = tdx_service.get_stock_data(request.stock_code, request.market)

        if df is None or df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"未找到股票数据: {request.market}{request.stock_code}",
            )

        # 转换为字典列表
        data_list = df.to_dict("records")

        return TdxDataResponse(
            code=request.stock_code,
            market=request.market,
            data=data_list,
            total_records=len(data_list),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/tdx/stocks/{market}",
    response_model=List[str],
    summary="列出可用股票代码",
    responses=ML_TDX_STOCKS_RESPONSES,
)
async def list_tdx_stocks(
    market: str = Path(..., description=ML_MARKET_PATH_DESCRIPTION),
    current_user: User = Depends(get_current_user),
):
    """
    列出可用的股票代码

    - **market**: 市场代码（sh/sz）
    """
    try:
        stocks = tdx_service.list_available_stocks(market)
        return stocks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 特征工程相关 ====================


@router.post("/features/generate", response_model=FeatureGenerationResponse)
async def generate_features(
    request: FeatureGenerationRequest = Body(..., example=ML_FEATURE_GENERATION_REQUEST_EXAMPLE),
    current_user: User = Depends(get_current_user),
):
    """
    生成特征数据

    - **stock_code**: 股票代码
    - **market**: 市场代码
    - **step**: 滚动窗口大小（默认10）
    - **include_indicators**: 是否包含技术指标（默认True）
    """
    try:
        # 获取通达信数据
        df = tdx_service.get_stock_data(request.stock_code, request.market)

        if df is None or df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"未找到股票数据: {request.market}{request.stock_code}",
            )

        # 生成特征
        X, y, metadata = feature_service.prepare_model_data(
            df, step=request.step, include_indicators=request.include_indicators
        )

        return FeatureGenerationResponse(
            success=True,
            message="特征生成成功",
            total_samples=metadata["total_samples"],
            feature_dim=metadata["feature_dim"],
            step=metadata["step"],
            feature_columns=metadata["feature_columns"],
            metadata=metadata,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 模型训练相关 ====================


@router.post("/models/train", response_model=ModelTrainResponse)
async def train_model(
    request: ModelTrainRequest = Body(..., example=ML_MODEL_TRAIN_REQUEST_EXAMPLE),
    current_user: User = Depends(get_current_user),
):
    """
    训练预测模型

    - **stock_code**: 股票代码
    - **market**: 市场代码
    - **step**: 滚动窗口大小
    - **test_size**: 测试集比例（0.1-0.5）
    - **model_name**: 模型名称
    - **model_params**: 模型参数（可选）
    """
    try:
        # 获取通达信数据
        df = tdx_service.get_stock_data(request.stock_code, request.market)

        if df is None or df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"未找到股票数据: {request.market}{request.stock_code}",
            )

        # 生成特征
        X, y, metadata = feature_service.prepare_model_data(df, step=request.step)

        # 创建ML服务
        ml_service = _build_ml_service()

        # 训练模型
        metrics = ml_service.train(X, y, test_size=request.test_size, model_params=request.model_params)

        # 保存模型
        ml_service.save_model(request.model_name)

        return ModelTrainResponse(
            success=True,
            message=f"模型 {request.model_name} 训练成功",
            model_name=request.model_name,
            metrics=metrics,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 模型预测相关 ====================


@router.post("/models/predict", response_model=ModelPredictResponse)
async def predict_with_model(
    request: ModelPredictRequest = Body(..., example=ML_MODEL_PREDICT_REQUEST_EXAMPLE),
    current_user: User = Depends(get_current_user),
):
    """
    使用模型进行预测

    - **model_name**: 模型名称
    - **stock_code**: 股票代码
    - **market**: 市场代码
    - **days**: 预测天数（1-30）
    """
    try:
        # 加载模型
        ml_service = _build_ml_service()
        loaded = ml_service.load_model(request.model_name)

        if not loaded:
            raise HTTPException(status_code=404, detail=f"模型不存在: {request.model_name}")

        # 获取数据
        df = tdx_service.get_stock_data(request.stock_code, request.market)

        if df is None or df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"未找到股票数据: {request.market}{request.stock_code}",
            )

        # 获取模型元数据
        metadata = ml_service.model_metadata
        step = metadata.get("metrics", {}).get("step", 10)

        # 生成特征（使用最新数据）
        X, y, _ = feature_service.prepare_model_data(df, step=step)

        # 使用最后一条数据进行预测
        if len(X) > 0:
            last_X = X.tail(1)
            prediction = ml_service.predict(last_X)[0]

            predictions = [
                {
                    "date": "T+1",
                    "predicted_price": float(prediction),
                    "confidence": None,
                }
            ]

            return ModelPredictResponse(
                success=True,
                message="预测成功",
                model_name=request.model_name,
                stock_code=request.stock_code,
                predictions=predictions,
            )
        else:
            raise HTTPException(status_code=400, detail="数据不足，无法进行预测")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 模型管理相关 ====================


@router.get(
    "/models",
    response_model=ModelListResponse,
    summary="获取已保存模型列表",
    description="返回当前模型目录中可用的机器学习模型清单，供模型运维、评估和预测调用前选择。",
    responses=ML_MODEL_LIST_RESPONSES,
)
async def list_models(current_user: User = Depends(get_current_user)):
    """返回当前模型目录中可用的机器学习模型清单。"""
    try:
        ml_service = _build_ml_service()
        models = ml_service.list_saved_models()

        return ModelListResponse(total=len(models), models=[ModelInfo(**model) for model in models])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/models/{model_name}",
    response_model=ModelDetailResponse,
    summary="获取单个模型详情",
    description="按模型名称读取训练元数据、训练历史和特征重要性，供排障、复盘和上线前核验使用。",
    responses=ML_MODEL_DETAIL_RESPONSES,
)
async def get_model_detail(
    model_name: str = Path(..., description="已保存模型的名称，用于定位需要查看详情的模型。"),
    current_user: User = Depends(get_current_user),
):
    """按模型名称读取训练元数据、训练历史和特征重要性。"""
    try:
        ml_service = _build_ml_service()
        loaded = ml_service.load_model(model_name)

        if not loaded:
            raise HTTPException(status_code=404, detail=f"模型不存在: {model_name}")

        # 获取特征重要性
        try:
            feature_importance = ml_service.get_feature_importance(top_k=20)
        except Exception:
            feature_importance = None

        return ModelDetailResponse(
            name=model_name,
            metadata=ml_service.model_metadata,
            training_history=ml_service.training_history,
            feature_importance=feature_importance,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 超参数搜索 ====================


@router.post("/models/hyperparameter-search", response_model=HyperparameterSearchResponse)
async def hyperparameter_search(
    request: HyperparameterSearchRequest = Body(..., example=ML_HYPERPARAMETER_SEARCH_REQUEST_EXAMPLE),
    current_user: User = Depends(get_current_user),
):
    """
    超参数搜索

    - **stock_code**: 股票代码
    - **market**: 市场代码
    - **step**: 滚动窗口大小
    - **cv**: 交叉验证折数
    - **param_grid**: 参数网格（可选）
    """
    try:
        # 获取数据
        df = tdx_service.get_stock_data(request.stock_code, request.market)

        if df is None or df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"未找到股票数据: {request.market}{request.stock_code}",
            )

        # 生成特征
        X, y, _ = feature_service.prepare_model_data(df, step=request.step)

        # 创建ML服务
        ml_service = _build_ml_service()

        # 执行超参数搜索
        result = ml_service.hyperparameter_search(X, y, param_grid=request.param_grid, cv=request.cv)

        return HyperparameterSearchResponse(
            success=True,
            message="超参数搜索完成",
            best_params=result["best_params"],
            best_rmse=result["best_rmse"],
            best_mse=result["best_mse"],
            cv_results=result["cv_results"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 模型评估 ====================


@router.post("/models/evaluate", response_model=ModelEvaluationResponse)
async def evaluate_model(
    request: ModelEvaluationRequest = Body(..., example=ML_MODEL_EVALUATION_REQUEST_EXAMPLE),
    current_user: User = Depends(get_current_user),
):
    """
    评估模型性能

    - **model_name**: 模型名称
    - **stock_code**: 股票代码
    - **market**: 市场代码
    """
    try:
        # 加载模型
        ml_service = _build_ml_service()
        loaded = ml_service.load_model(request.model_name)

        if not loaded:
            raise HTTPException(status_code=404, detail=f"模型不存在: {request.model_name}")

        # 获取数据
        df = tdx_service.get_stock_data(request.stock_code, request.market)

        if df is None or df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"未找到股票数据: {request.market}{request.stock_code}",
            )

        # 生成特征
        metadata = ml_service.model_metadata
        step = metadata.get("metrics", {}).get("step", 10)
        X, y, _ = feature_service.prepare_model_data(df, step=step)

        # 评估模型
        metrics = ml_service.evaluate_model(X, y)

        return ModelEvaluationResponse(
            success=True,
            message="评估完成",
            model_name=request.model_name,
            metrics=metrics,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
