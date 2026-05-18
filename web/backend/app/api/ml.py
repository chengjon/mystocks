"""
机器学习 API 端点
提供模型训练、预测、评估等功能
"""

import os
from typing import List

from fastapi import APIRouter, Body, Depends, Path

from app.core.exceptions import BusinessException
from app.api._ml_responses import (
    ML_FEATURE_GENERATION_REQUEST_EXAMPLE,
    ML_FEATURE_GENERATION_RESPONSES,
    ML_HYPERPARAMETER_SEARCH_REQUEST_EXAMPLE,
    ML_HYPERPARAMETER_SEARCH_RESPONSES,
    ML_MARKET_PATH_DESCRIPTION,
    ML_MODEL_DETAIL_RESPONSES,
    ML_MODEL_EVALUATION_REQUEST_EXAMPLE,
    ML_MODEL_EVALUATION_RESPONSES,
    ML_MODEL_LIST_RESPONSES,
    ML_MODEL_PREDICT_REQUEST_EXAMPLE,
    ML_MODEL_PREDICT_RESPONSES,
    ML_MODEL_TRAIN_REQUEST_EXAMPLE,
    ML_MODEL_TRAIN_RESPONSES,
    ML_TDX_DATA_REQUEST_EXAMPLE,
    ML_TDX_DATA_RESPONSES,
    ML_TDX_STOCKS_RESPONSES,
)

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


def _build_ml_service() -> "MLPredictionService":
    if MLPredictionService is None:
        raise BusinessException(
            status_code=503,
            detail=f"ML prediction service unavailable: {_ML_PREDICTION_IMPORT_ERROR}",
        )
    return MLPredictionService(model_dir=MODEL_DIR)


# ==================== 通达信数据相关 ====================


@router.post(
    "/tdx/data",
    response_model=TdxDataResponse,
    summary="获取通达信行情数据",
    description="按股票代码和市场代码读取通达信原始行情数据，返回 OHLCV 记录列表和总记录数。",
    responses=ML_TDX_DATA_RESPONSES,
)
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
            raise BusinessException(
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
        raise BusinessException(status_code=500, detail=str(e))


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
        raise BusinessException(status_code=500, detail=str(e))


# ==================== 特征工程相关 ====================


@router.post(
    "/features/generate",
    response_model=FeatureGenerationResponse,
    summary="生成机器学习特征",
    description="基于指定股票历史行情生成训练特征，返回样本量、特征维度和特征列清单。",
    responses=ML_FEATURE_GENERATION_RESPONSES,
)
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
            raise BusinessException(
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
        raise BusinessException(status_code=500, detail=str(e))


# ==================== 模型训练相关 ====================


@router.post(
    "/models/train",
    response_model=ModelTrainResponse,
    summary="训练机器学习模型",
    description="使用指定股票历史行情训练模型，并返回训练完成后的模型名称和评估指标。",
    responses=ML_MODEL_TRAIN_RESPONSES,
)
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
            raise BusinessException(
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
        raise BusinessException(status_code=500, detail=str(e))


# ==================== 模型预测相关 ====================


@router.post(
    "/models/predict",
    response_model=ModelPredictResponse,
    summary="使用模型执行预测",
    description="加载指定模型并对目标股票执行下一交易日价格预测，返回预测价格列表。",
    responses=ML_MODEL_PREDICT_RESPONSES,
)
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
            raise BusinessException(status_code=404, detail=f"模型不存在: {request.model_name}")

        # 获取数据
        df = tdx_service.get_stock_data(request.stock_code, request.market)

        if df is None or df.empty:
            raise BusinessException(
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
            raise BusinessException(status_code=400, detail="数据不足，无法进行预测")

    except BusinessException:
        raise
    except Exception as e:
        raise BusinessException(status_code=500, detail=str(e))


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
        raise BusinessException(status_code=500, detail=str(e))


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
            raise BusinessException(status_code=404, detail=f"模型不存在: {model_name}")

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

    except BusinessException:
        raise
    except Exception as e:
        raise BusinessException(status_code=500, detail=str(e))


# ==================== 超参数搜索 ====================


@router.post(
    "/models/hyperparameter-search",
    response_model=HyperparameterSearchResponse,
    summary="执行超参数搜索",
    description="对指定股票数据执行模型超参数搜索，并返回最佳参数组合与交叉验证结果。",
    responses=ML_HYPERPARAMETER_SEARCH_RESPONSES,
)
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
            raise BusinessException(
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
        raise BusinessException(status_code=500, detail=str(e))


# ==================== 模型评估 ====================


@router.post(
    "/models/evaluate",
    response_model=ModelEvaluationResponse,
    summary="评估模型表现",
    description="使用指定股票数据评估已保存模型的效果，返回 RMSE、MAE、R2 等评估指标。",
    responses=ML_MODEL_EVALUATION_RESPONSES,
)
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
            raise BusinessException(status_code=404, detail=f"模型不存在: {request.model_name}")

        # 获取数据
        df = tdx_service.get_stock_data(request.stock_code, request.market)

        if df is None or df.empty:
            raise BusinessException(
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

    except BusinessException:
        raise
    except Exception as e:
        raise BusinessException(status_code=500, detail=str(e))
