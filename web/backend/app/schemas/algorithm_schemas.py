"""
量化交易算法 API 数据模型

定义所有算法API的Pydantic模型，包括：
- 请求模型：算法训练、预测、配置等
- 响应模型：算法结果、状态信息等
- 配置模型：算法参数和选项
- 枚举模型：算法类型、状态等

遵循项目统一响应格式和验证规范。
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator


# ==================== 枚举定义 ====================


class AlgorithmType(str, Enum):
    """算法类型枚举"""

    SVM = "svm"
    DECISION_TREE = "decision_tree"
    NAIVE_BAYES = "naive_bayes"
    BRUTE_FORCE = "brute_force"
    KNUTH_MORRIS_PRATT = "knuth_morris_pratt"
    BOYER_MOORE_HORSPOOL = "boyer_moore_horspool"
    AHO_CORASICK = "aho_corasick"
    HIDDEN_MARKOV_MODEL = "hidden_markov_model"
    BAYESIAN_NETWORK = "bayesian_network"
    N_GRAM = "n_gram"
    NEURAL_NETWORK = "neural_network"


class AlgorithmStatus(str, Enum):
    """算法执行状态"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PredictionLabel(str, Enum):
    """预测标签枚举"""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


# ==================== 基础模型 ====================


class AlgorithmMetadata(BaseModel):
    """算法元数据"""

    algorithm_type: AlgorithmType = Field(..., description="算法类型")
    algorithm_name: str = Field(..., min_length=1, max_length=100, description="算法名称")
    version: str = Field(default="1.0.0", pattern=r"^\d+\.\d+\.\d+$", description="算法版本")
    description: Optional[str] = Field(None, max_length=500, description="算法描述")


class AlgorithmConfig(BaseModel):
    """算法配置基础模型"""

    enable_gpu: bool = Field(default=True, description="是否启用GPU加速")
    gpu_memory_limit_mb: Optional[int] = Field(None, gt=0, description="GPU内存限制(MB)")
    enable_validation: bool = Field(default=True, description="是否启用数据验证")
    random_seed: Optional[int] = Field(None, ge=0, le=2**32 - 1, description="随机种子")


# ==================== 请求模型 ====================


class AlgorithmTrainRequest(BaseModel):
    """算法训练请求"""

    algorithm_type: AlgorithmType = Field(..., description="算法类型")
    symbol: str = Field(..., min_length=1, max_length=20, description="股票代码")
    features: List[str] = Field(..., min_items=1, description="特征列表")
    labels: Optional[List[str]] = Field(None, description="标签列表（分类算法）")
    config: AlgorithmConfig = Field(default_factory=AlgorithmConfig, description="算法配置")
    training_data: Optional[Dict[str, Any]] = Field(None, description="训练数据（可选，直接提供）")


class AlgorithmPredictRequest(BaseModel):
    """算法预测请求"""

    model_id: str = Field(..., min_length=1, description="模型ID")
    features_data: Union[List[float], List[List[float]]] = Field(..., description="特征数据")
    prediction_config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="预测配置")


class AlgorithmInfoRequest(BaseModel):
    """算法信息请求"""

    algorithm_type: AlgorithmType = Field(..., description="算法类型")


# ==================== SVM专用模型 ====================


class SVMConfig(AlgorithmConfig):
    """SVM算法配置"""

    kernel: str = Field(default="rbf", pattern="^(linear|rbf|poly|sigmoid)$", description="核函数类型")
    C: float = Field(default=1.0, gt=0, description="正则化参数")
    gamma: Union[str, float] = Field(default="scale", description="核函数系数")
    max_iter: int = Field(default=-1, ge=-1, description="最大迭代次数")

    @field_validator("gamma")
    @classmethod
    def validate_gamma(cls, v):
        if isinstance(v, str) and v not in ["scale", "auto"]:
            raise ValueError("gamma must be 'scale', 'auto', or a positive float")
        if isinstance(v, (int, float)) and v <= 0:
            raise ValueError("gamma must be positive when numeric")
        return v


class SVMTrainRequest(AlgorithmTrainRequest):
    """SVM训练请求"""

    svm_config: SVMConfig = Field(default_factory=SVMConfig, description="SVM专用配置")


# ==================== 决策树专用模型 ====================


class DecisionTreeConfig(AlgorithmConfig):
    """决策树算法配置"""

    max_depth: Optional[int] = Field(None, ge=1, description="最大深度")
    min_samples_split: int = Field(default=2, ge=2, description="最小分割样本数")
    criterion: str = Field(default="gini", pattern="^(gini|entropy|log_loss)$", description="分割标准")


class DecisionTreeTrainRequest(AlgorithmTrainRequest):
    """决策树训练请求"""

    tree_config: DecisionTreeConfig = Field(default_factory=DecisionTreeConfig, description="决策树专用配置")


# ==================== 朴素贝叶斯专用模型 ====================


class NaiveBayesConfig(AlgorithmConfig):
    """朴素贝叶斯算法配置"""

    distribution_type: str = Field(
        default="gaussian", pattern="^(gaussian|multinomial|bernoulli)$", description="分布类型"
    )


class NaiveBayesTrainRequest(AlgorithmTrainRequest):
    """朴素贝叶斯训练请求"""

    nb_config: NaiveBayesConfig = Field(default_factory=NaiveBayesConfig, description="朴素贝叶斯专用配置")


# ==================== Aho-Corasick专用模型 ====================


class PatternDefinition(BaseModel):
    """模式定义"""

    name: str = Field(..., min_length=1, max_length=100, description="模式名称")
    sequence: List[float] = Field(..., min_items=2, description="价格序列模式")


class AhoCorasickTrainRequest(BaseModel):
    """Aho-Corasick训练请求"""

    patterns: List[PatternDefinition] = Field(..., min_items=1, description="模式列表")
    market: str = Field(default="cn", pattern="^(cn|us|hk)$", description="市场类型")


class AhoCorasickMatchRequest(BaseModel):
    """Aho-Corasick匹配请求"""

    automaton_id: str = Field(..., description="自动机ID")
    time_series: List[float] = Field(..., min_items=1, description="待匹配时间序列")
    threshold: float = Field(default=0.95, ge=0, le=1, description="匹配相似度阈值")


# ==================== HMM专用模型 ====================


class HMMConfig(AlgorithmConfig):
    """隐马尔可夫模型配置"""

    n_states: int = Field(default=3, ge=2, le=10, description="隐藏状态数量")
    n_features: int = Field(default=5, ge=1, description="特征维度")
    covariance_type: str = Field(default="full", pattern="^(full|tied|diag|spherical)$", description="协方差类型")


class HMMTrainRequest(BaseModel):
    """HMM训练请求"""

    symbol: str = Field(..., min_length=1, max_length=20, description="股票代码")
    observations: List[str] = Field(..., min_items=1, description="观测序列")
    hmm_config: HMMConfig = Field(default_factory=HMMConfig, description="HMM专用配置")


class HMMPredictRequest(BaseModel):
    """HMM预测请求"""

    model_id: str = Field(..., description="模型ID")
    current_observations: List[str] = Field(..., min_items=1, description="当前观测序列")


# ==================== 贝叶斯网络专用模型 ====================


class RelationshipDefinition(BaseModel):
    """关系定义"""

    from_symbol: str = Field(..., description="源股票代码")
    to_symbol: str = Field(..., description="目标股票代码")
    delay: int = Field(default=1, ge=0, description="延时（天数）")


class BayesianNetworkBuildRequest(BaseModel):
    """贝叶斯网络构建请求"""

    symbols: List[str] = Field(..., min_items=2, description="股票代码列表")
    relationships: List[RelationshipDefinition] = Field(..., description="关系定义列表")
    time_window: int = Field(default=30, ge=1, description="时间窗口（天）")


class BayesianNetworkInferRequest(BaseModel):
    """贝叶斯网络推理请求"""

    network_id: str = Field(..., description="网络ID")
    trigger_event: Dict[str, Any] = Field(..., description="触发事件")
    max_delay: int = Field(default=5, ge=1, description="最大延时")


# ==================== N-gram专用模型 ====================


class NGramTrainRequest(BaseModel):
    """N-gram训练请求"""

    symbol: str = Field(..., min_length=1, max_length=20, description="股票代码")
    n: int = Field(default=3, ge=2, le=10, description="N-gram的N值")
    sequence_type: str = Field(
        default="price_changes", pattern="^(price_changes|volume_changes)$", description="序列类型"
    )
    window_size: int = Field(default=1000, ge=100, description="历史数据窗口大小")


class NGramPredictRequest(BaseModel):
    """N-gram预测请求"""

    model_id: str = Field(..., description="模型ID")
    current_sequence: List[float] = Field(..., min_items=1, description="当前序列")
    n: int = Field(default=3, ge=2, le=10, description="N-gram的N值")


# ==================== 神经网络专用模型 ====================


class NeuralNetworkConfig(AlgorithmConfig):
    """神经网络配置"""

    architecture: str = Field(default="lstm", pattern="^(lstm|gru|cnn|transformer)$", description="网络架构")
    layers: int = Field(default=2, ge=1, le=10, description="网络层数")
    units: int = Field(default=64, ge=8, le=1024, description="每层单元数")
    dropout: float = Field(default=0.2, ge=0, le=0.5, description="dropout率")


class NeuralNetworkTrainRequest(BaseModel):
    """神经网络训练请求"""

    symbol: str = Field(..., min_length=1, max_length=20, description="股票代码")
    input_features: List[str] = Field(..., min_items=1, description="输入特征列表")
    prediction_horizon: int = Field(default=5, ge=1, le=30, description="预测周期")
    lookback_window: int = Field(default=60, ge=10, description="回溯窗口")
    nn_config: NeuralNetworkConfig = Field(default_factory=NeuralNetworkConfig, description="神经网络配置")


class NeuralNetworkPredictRequest(BaseModel):
    """神经网络预测请求"""

    model_id: str = Field(..., description="模型ID")
    current_data: Dict[str, List[float]] = Field(..., description="当前市场数据")


# ==================== 响应模型 ====================


class AlgorithmResult(BaseModel):
    """算法执行结果"""

    algorithm_id: str = Field(..., description="算法实例ID")
    algorithm_type: str = Field(..., description="算法类型")
    execution_timestamp: datetime = Field(default_factory=datetime.utcnow, description="执行时间戳")
    status: AlgorithmStatus = Field(..., description="执行状态")
    success: bool = Field(True, description="是否成功")
    message: Optional[str] = Field(None, description="结果消息")
    data: Optional[Dict[str, Any]] = Field(None, description="结果数据")


class AlgorithmMetrics(BaseModel):
    """算法性能指标"""

    accuracy: Optional[float] = Field(None, ge=0, le=1, description="准确率")
    precision: Optional[float] = Field(None, ge=0, le=1, description="精确率")
    recall: Optional[float] = Field(None, ge=0, le=1, description="召回率")
    f1_score: Optional[float] = Field(None, ge=0, le=1, description="F1分数")
    training_time: Optional[float] = Field(None, ge=0, description="训练时间(秒)")
    prediction_time: Optional[float] = Field(None, ge=0, description="预测时间(秒)")


class AlgorithmInfo(BaseModel):
    """算法信息"""

    type: str = Field(..., description="算法类型")
    category: str = Field(..., description="算法分类")
    description: str = Field(..., description="算法描述")
    parameters: Dict[str, Any] = Field(..., description="参数规格")
    use_cases: List[str] = Field(..., description="应用场景")
    performance: Dict[str, Any] = Field(..., description="性能特征")


class ModelInfo(BaseModel):
    """模型信息"""

    model_id: str = Field(..., description="模型ID")
    algorithm_type: str = Field(..., description="算法类型")
    symbol: str = Field(..., description="股票代码")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    metrics: Optional[AlgorithmMetrics] = Field(None, description="性能指标")
    config: Dict[str, Any] = Field(..., description="模型配置")
    status: str = Field(default="active", description="模型状态")


class PredictionResult(BaseModel):
    """预测结果"""

    prediction: Union[str, float, List[float]] = Field(..., description="预测值")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="置信度")
    probabilities: Optional[Dict[str, float]] = Field(None, description="各类别概率")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")


# ==================== 批量操作模型 ====================


class BatchOperationRequest(BaseModel):
    """批量操作请求"""

    operations: List[Dict[str, Any]] = Field(..., min_items=1, description="操作列表")
    parallel_execution: bool = Field(default=True, description="是否并行执行")
    max_concurrent: Optional[int] = Field(None, ge=1, le=10, description="最大并发数")


class BatchOperationResult(BaseModel):
    """批量操作结果"""

    total_operations: int = Field(..., description="总操作数")
    successful_operations: int = Field(..., description="成功操作数")
    failed_operations: int = Field(..., description="失败操作数")
    results: List[AlgorithmResult] = Field(..., description="详细结果列表")
    execution_time: float = Field(..., description="总执行时间")


# ==================== 健康检查模型 ====================


class AlgorithmHealthStatus(BaseModel):
    """算法服务健康状态"""

    service: str = Field(default="algorithms-api", description="服务名称")
    status: str = Field(..., description="服务状态")
    algorithms_loaded: bool = Field(..., description="算法是否已加载")
    gpu_available: bool = Field(..., description="GPU是否可用")
    supported_algorithms: int = Field(..., description="支持的算法数量")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="检查时间戳")


# ==================== 导出配置 ====================

__all__ = [
    # 枚举
    "AlgorithmType",
    "AlgorithmStatus",
    "PredictionLabel",
    # 基础模型
    "AlgorithmMetadata",
    "AlgorithmConfig",
    # 请求模型
    "AlgorithmTrainRequest",
    "AlgorithmPredictRequest",
    "AlgorithmInfoRequest",
    # 算法专用模型
    "SVMConfig",
    "SVMTrainRequest",
    "DecisionTreeConfig",
    "DecisionTreeTrainRequest",
    "NaiveBayesConfig",
    "NaiveBayesTrainRequest",
    "AhoCorasickTrainRequest",
    "AhoCorasickMatchRequest",
    "HMMConfig",
    "HMMTrainRequest",
    "HMMPredictRequest",
    "BayesianNetworkBuildRequest",
    "BayesianNetworkInferRequest",
    "NGramTrainRequest",
    "NGramPredictRequest",
    "NeuralNetworkConfig",
    "NeuralNetworkTrainRequest",
    "NeuralNetworkPredictRequest",
    # 响应模型
    "AlgorithmResult",
    "AlgorithmMetrics",
    "AlgorithmInfo",
    "ModelInfo",
    "PredictionResult",
    # 批量操作
    "BatchOperationRequest",
    "BatchOperationResult",
    # 健康检查
    "AlgorithmHealthStatus",
]
