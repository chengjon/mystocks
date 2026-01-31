"""
机器学习相关的数据模型定义
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# ==================== 通达信数据相关 ====================


class TdxDataRequest(BaseModel):
    """通达信数据请求"""

    stock_code: str = Field(..., description="股票代码", example="000001")
    market: str = Field(default="sh", description="市场代码（sh/sz）", example="sh")


class TdxDataResponse(BaseModel):
    """通达信数据响应"""

    code: str = Field(..., description="股票代码")
    market: str = Field(..., description="市场")
    data: List[Dict[str, Any]] = Field(..., description="OHLCV数据列表")
    total_records: int = Field(..., description="总记录数")


class TdxExportRequest(BaseModel):
    """通达信数据导出请求"""

    stock_code: str = Field(..., description="股票代码")
    market: str = Field(default="sh", description="市场代码")
    output_format: str = Field(default="csv", description="输出格式（csv/json）")


# ==================== 特征工程相关 ====================


class FeatureGenerationRequest(BaseModel):
    """特征生成请求"""

    stock_code: str = Field(..., description="股票代码")
    market: str = Field(default="sh", description="市场代码")
    step: int = Field(default=10, description="滚动窗口大小", ge=1, le=100)
    include_indicators: bool = Field(default=True, description="是否包含技术指标")


class FeatureGenerationResponse(BaseModel):
    """特征生成响应"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    total_samples: int = Field(..., description="样本总数")
    feature_dim: int = Field(..., description="特征维度")
    step: int = Field(..., description="窗口大小")
    feature_columns: List[str] = Field(..., description="特征列名")
    metadata: Dict[str, Any] = Field(..., description="元数据")


# ==================== 模型训练相关 ====================


class ModelTrainRequest(BaseModel):
    """模型训练请求"""

    stock_code: str = Field(..., description="股票代码")
    market: str = Field(default="sh", description="市场代码")
    step: int = Field(default=10, description="滚动窗口大小")
    test_size: float = Field(default=0.2, description="测试集比例", ge=0.1, le=0.5)
    model_name: str = Field(..., description="模型名称")
    model_params: Optional[Dict[str, Any]] = Field(None, description="模型参数")


class ModelTrainResponse(BaseModel):
    """模型训练响应"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    model_name: str = Field(..., description="模型名称")
    metrics: Dict[str, Any] = Field(..., description="评估指标")


# ==================== 模型预测相关 ====================


class ModelPredictRequest(BaseModel):
    """模型预测请求"""

    model_name: str = Field(..., description="模型名称")
    stock_code: str = Field(..., description="股票代码")
    market: str = Field(default="sh", description="市场代码")
    days: int = Field(default=1, description="预测天数", ge=1, le=30)


class PredictionResult(BaseModel):
    """单次预测结果"""

    date: str = Field(..., description="日期")
    predicted_price: float = Field(..., description="预测价格")
    confidence: Optional[float] = Field(None, description="置信度")


class ModelPredictResponse(BaseModel):
    """模型预测响应"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    model_name: str = Field(..., description="使用的模型名称")
    stock_code: str = Field(..., description="股票代码")
    predictions: List[PredictionResult] = Field(..., description="预测结果列表")


# ==================== 模型信息相关 ====================


class ModelInfo(BaseModel):
    """模型信息"""

    name: str = Field(..., description="模型名称")
    path: str = Field(..., description="模型路径")
    trained_at: str = Field(..., description="训练时间")
    test_rmse: float = Field(..., description="测试集RMSE")
    test_r2: float = Field(..., description="测试集R²")
    train_samples: Optional[int] = Field(None, description="训练样本数")
    test_samples: Optional[int] = Field(None, description="测试样本数")
    feature_dim: Optional[int] = Field(None, description="特征维度")


class ModelListResponse(BaseModel):
    """模型列表响应"""

    total: int = Field(..., description="模型总数")
    models: List[ModelInfo] = Field(..., description="模型列表")


class ModelDetailResponse(BaseModel):
    """模型详情响应"""

    name: str = Field(..., description="模型名称")
    metadata: Dict[str, Any] = Field(..., description="模型元数据")
    training_history: List[Dict[str, Any]] = Field(..., description="训练历史")
    feature_importance: Optional[List[Dict[str, Any]]] = Field(None, description="特征重要性")


# ==================== 超参数搜索相关 ====================


class HyperparameterSearchRequest(BaseModel):
    """超参数搜索请求"""

    stock_code: str = Field(..., description="股票代码")
    market: str = Field(default="sh", description="市场代码")
    step: int = Field(default=10, description="滚动窗口大小")
    cv: int = Field(default=5, description="交叉验证折数", ge=2, le=10)
    param_grid: Optional[Dict[str, List[Any]]] = Field(
        None,
        description="参数网格",
        example={
            "num_leaves": [5, 10, 15, 20, 25],
            "n_estimators": [10, 40, 70, 100],
            "learning_rate": [0.01, 0.1, 0.2],
        },
    )


class HyperparameterSearchResponse(BaseModel):
    """超参数搜索响应"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    best_params: Dict[str, Any] = Field(..., description="最佳参数")
    best_rmse: float = Field(..., description="最佳RMSE")
    best_mse: float = Field(..., description="最佳MSE")
    cv_results: Dict[str, Any] = Field(..., description="交叉验证结果")


# ==================== 评估相关 ====================


class ModelEvaluationRequest(BaseModel):
    """模型评估请求"""

    model_name: str = Field(..., description="模型名称")
    stock_code: str = Field(..., description="股票代码")
    market: str = Field(default="sh", description="市场代码")


class ModelEvaluationResponse(BaseModel):
    """模型评估响应"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    model_name: str = Field(..., description="模型名称")
    metrics: Dict[str, Any] = Field(..., description="评估指标")


# ==================== 通用响应 ====================


class MLResponse(BaseModel):
    """通用ML响应"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    data: Optional[Any] = Field(None, description="数据")


class ErrorResponse(BaseModel):
    """错误响应"""

    error: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(None, description="详细错误信息")
