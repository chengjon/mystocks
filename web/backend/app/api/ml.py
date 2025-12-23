"""
机器学习 API 端点
提供模型训练、预测、评估等功能
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
import os

from app.schemas.ml_schemas import (
    TdxDataRequest,
    TdxDataResponse,
    FeatureGenerationRequest,
    FeatureGenerationResponse,
    ModelTrainRequest,
    ModelTrainResponse,
    ModelPredictRequest,
    ModelPredictResponse,
    ModelListResponse,
    ModelDetailResponse,
    ModelInfo,
    HyperparameterSearchRequest,
    HyperparameterSearchResponse,
    ModelEvaluationRequest,
    ModelEvaluationResponse,
)
from app.services.tdx_parser_service import TdxDataService
from app.services.feature_engineering_service import FeatureEngineeringService
from app.services.ml_prediction_service import MLPredictionService
from app.core.security import get_current_user, User

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

# 初始化服务
tdx_service = TdxDataService()
feature_service = FeatureEngineeringService()

# 模型存储目录
MODEL_DIR = os.getenv("ML_MODEL_DIR", "./models")


# ==================== 通达信数据相关 ====================


@router.post("/tdx/data", response_model=TdxDataResponse)
async def get_tdx_data(
    request: TdxDataRequest, current_user: User = Depends(get_current_user)
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


@router.get("/tdx/stocks/{market}", response_model=List[str])
async def list_tdx_stocks(market: str, current_user: User = Depends(get_current_user)):
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
    request: FeatureGenerationRequest, current_user: User = Depends(get_current_user)
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
    request: ModelTrainRequest, current_user: User = Depends(get_current_user)
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
        ml_service = MLPredictionService(model_dir=MODEL_DIR)

        # 训练模型
        metrics = ml_service.train(
            X, y, test_size=request.test_size, model_params=request.model_params
        )

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
    request: ModelPredictRequest, current_user: User = Depends(get_current_user)
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
        ml_service = MLPredictionService(model_dir=MODEL_DIR)
        loaded = ml_service.load_model(request.model_name)

        if not loaded:
            raise HTTPException(
                status_code=404, detail=f"模型不存在: {request.model_name}"
            )

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


@router.get("/models", response_model=ModelListResponse)
async def list_models(current_user: User = Depends(get_current_user)):
    """列出所有已保存的模型"""
    try:
        ml_service = MLPredictionService(model_dir=MODEL_DIR)
        models = ml_service.list_saved_models()

        return ModelListResponse(
            total=len(models), models=[ModelInfo(**model) for model in models]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_name}", response_model=ModelDetailResponse)
async def get_model_detail(
    model_name: str, current_user: User = Depends(get_current_user)
):
    """获取模型详情"""
    try:
        ml_service = MLPredictionService(model_dir=MODEL_DIR)
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


@router.post(
    "/models/hyperparameter-search", response_model=HyperparameterSearchResponse
)
async def hyperparameter_search(
    request: HyperparameterSearchRequest, current_user: User = Depends(get_current_user)
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
        ml_service = MLPredictionService(model_dir=MODEL_DIR)

        # 执行超参数搜索
        result = ml_service.hyperparameter_search(
            X, y, param_grid=request.param_grid, cv=request.cv
        )

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
    request: ModelEvaluationRequest, current_user: User = Depends(get_current_user)
):
    """
    评估模型性能

    - **model_name**: 模型名称
    - **stock_code**: 股票代码
    - **market**: 市场代码
    """
    try:
        # 加载模型
        ml_service = MLPredictionService(model_dir=MODEL_DIR)
        loaded = ml_service.load_model(request.model_name)

        if not loaded:
            raise HTTPException(
                status_code=404, detail=f"模型不存在: {request.model_name}"
            )

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
