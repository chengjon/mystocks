#!/usr/bin/env python3
"""
机器学习增强交易策略基类 (ML-Enhanced Trading Strategy Base Class)

功能说明:
- 提供机器学习算法与交易策略的集成框架
- 支持SVM、Decision Tree、Naive Bayes算法
- 自动特征工程和数据预处理
- 集成Phase 1.5算法实现
- 支持训练和预测模式的无缝切换

作者: MyStocks量化交易团队
创建时间: 2026-01-12
版本: 1.0.0
"""

from src.algorithms.metadata import AlgorithmFingerprint
from src.algorithms.classification.naive_bayes_algorithm import NaiveBayesAlgorithm
from src.algorithms.classification.decision_tree_algorithm import DecisionTreeAlgorithm
from src.algorithms.classification.svm_algorithm import SVMAlgorithm
from src.ml_strategy.strategy.base_strategy import BaseStrategy
import pandas as pd
import numpy as np
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import sys
import os

# 添加项目根目录到路径
project_root = "/opt/claude/mystocks_spec"
sys.path.insert(0, project_root)


logger = logging.getLogger(__name__)


class MLStrategyConfig:
    """ML策略配置类"""


def __init__(
    self,
    algorithm_type: str = "svm",
    feature_columns: List[str] = None,
    target_column: str = "target",
    train_window_days: int = 252,  # 约1年交易日
    min_train_samples: int = 100,
    prediction_threshold: float = 0.6,
    confidence_threshold: float = 0.7,
    retrain_frequency_days: int = 30,
    algorithm_params: Dict[str, Any] = None,
    feature_engineering: bool = True,
):
    self.algorithm_type = algorithm_type
    self.feature_columns = feature_columns or []
    self.target_column = target_column
    self.train_window_days = train_window_days
    self.min_train_samples = min_train_samples
    self.prediction_threshold = prediction_threshold
    self.confidence_threshold = confidence_threshold
    self.retrain_frequency_days = retrain_frequency_days
    self.algorithm_params = algorithm_params or {}
    self.feature_engineering = feature_engineering


class MLFeatureEngineer:
    """特征工程工具类"""

    @staticmethod
    def add_technical_features(data: pd.DataFrame) -> pd.DataFrame:
        """添加技术分析特征"""
        df = data.copy()

        # 移动平均线
        df["ma_5"] = df["close"].rolling(window=5).mean()
        df["ma_10"] = df["close"].rolling(window=10).mean()
        df["ma_20"] = df["close"].rolling(window=20).mean()

        # 价格动量
        df["momentum_5"] = (df["close"] - df["close"].shift(5)) / df["close"].shift(5)
        df["momentum_10"] = (df["close"] - df["close"].shift(10)) / df["close"].shift(10)

        # 波动率
        df["volatility_5"] = df["close"].rolling(window=5).std()
        df["volatility_10"] = df["close"].rolling(window=10).std()

        # 相对强弱指数 (RSI)
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["rsi_14"] = 100 - (100 / (1 + rs))

        # MACD
        ema_12 = df["close"].ewm(span=12).mean()
        ema_26 = df["close"].ewm(span=26).mean()
        df["macd"] = ema_12 - ema_26
        df["macd_signal"] = df["macd"].ewm(span=9).mean()

        # 布林带
        sma_20 = df["close"].rolling(window=20).mean()
        std_20 = df["close"].rolling(window=20).std()
        df["bb_upper"] = sma_20 + (std_20 * 2)
        df["bb_lower"] = sma_20 - (std_20 * 2)
        df["bb_middle"] = sma_20

        return df

    @staticmethod
    def create_target_variable(data: pd.DataFrame, future_periods: int = 5) -> pd.DataFrame:
        """创建目标变量（未来价格走势）"""
        df = data.copy()

        # 计算未来收益率
        future_returns = df["close"].shift(-future_periods) / df["close"] - 1

        # 分类标签：上涨(2)、震荡(1)、下跌(0)
        conditions = [
            (future_returns > 0.02),  # 上涨 > 2%
            (future_returns < -0.02),  # 下跌 < -2%
        ]
        choices = [2, 0]  # 2=上涨, 0=下跌
        df["target"] = np.select(conditions, choices, default=1)  # 1=震荡

        return df

    @staticmethod
    def prepare_ml_features(data: pd.DataFrame, feature_columns: List[str] = None) -> Tuple[pd.DataFrame, List[str]]:
        """准备ML特征数据"""
        df = data.copy()

        # 移除NaN值
        df = df.dropna()

        if not feature_columns:
            # 自动选择数值型特征（排除目标变量）
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            feature_columns = [col for col in numeric_cols if col not in ["target", "close", "open", "high", "low"]]

        # 确保所有特征列都存在
        missing_cols = [col for col in feature_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing feature columns: {missing_cols}")

        return df, feature_columns


class MLAlgorithmManager:
    """ML算法管理器"""

    def __init__(self):
        self.algorithms = {}
        self.trained_models = {}

    async def get_algorithm(self, algorithm_type: str, config: MLStrategyConfig) -> Any:
        """获取或创建算法实例"""
        if algorithm_type not in self.algorithms:
            metadata = AlgorithmFingerprint.from_config(
                {
                    "name": f"ML_Strategy_{algorithm_type}",
                    "description": f"ML-enhanced trading strategy using {algorithm_type}",
                    "algorithm_type": "classification",
                    "gpu_enabled": True,
                }
            )

            if algorithm_type == "svm":
                algorithm = SVMAlgorithm(metadata)
            elif algorithm_type == "decision_tree":
                algorithm = DecisionTreeAlgorithm(metadata)
            elif algorithm_type == "naive_bayes":
                algorithm = NaiveBayesAlgorithm(metadata)
            else:
                raise ValueError(f"Unsupported algorithm type: {algorithm_type}")

            self.algorithms[algorithm_type] = algorithm

        return self.algorithms[algorithm_type]

    async def train_model(self, algorithm_type: str, data: pd.DataFrame, config: MLStrategyConfig) -> Dict[str, Any]:
        """训练ML模型"""
        algorithm = await self.get_algorithm(algorithm_type, config)

        # 准备训练数据
        train_data, feature_cols = MLFeatureEngineer.prepare_ml_features(data, config.feature_columns)

        if len(train_data) < config.min_train_samples:
            raise ValueError(
                f"Insufficient training samples: {
                    len(train_data)} < {
                    config.min_train_samples}"
            )

        # 训练配置
        train_config = {
            "feature_columns": feature_cols,
            "target_column": config.target_column,
            f"{algorithm_type}_params": config.algorithm_params,
        }

        # 训练模型
        model = await algorithm.train(train_data, train_config)

        # 存储训练的模型
        model_key = f"{algorithm_type}_{
            hash(str(train_data.values.tobytes()))}"
        self.trained_models[model_key] = {
            "model": model,
            "algorithm": algorithm,
            "config": config,
            "feature_columns": feature_cols,
            "trained_at": datetime.now(),
        }

        return model_key

    async def predict(self, model_key: str, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """使用训练好的模型进行预测"""
        if model_key not in self.trained_models:
            raise ValueError(f"Model {model_key} not found")

        model_info = self.trained_models[model_key]
        algorithm = model_info["algorithm"]
        feature_columns = model_info["feature_columns"]

        # 准备预测数据
        pred_data, _ = MLFeatureEngineer.prepare_ml_features(data, feature_columns)

        # 进行预测
        predictions = await algorithm.predict(pred_data, model_info["model"])

        return predictions["predictions"]


class MLTradingStrategy(BaseStrategy):
    """
    机器学习增强交易策略基类

    提供机器学习算法与传统交易策略的集成框架，支持：
    - SVM算法：模式识别和分类
    - Decision Tree算法：规则-based决策
    - Naive Bayes算法：概率-based信号

    子类需要实现：
    - prepare_features(): 准备策略特定的特征
    - interpret_ml_signals(): 解释ML预测结果为交易信号
    """

    def __init__(
        self,
        strategy_name: str,
        algorithm_type: str = "svm",
        config: MLStrategyConfig = None,
        **kwargs,
    ):
        super().__init__(
            name=strategy_name,
            version="1.0.0",
            parameters={},
            description=f"ML-enhanced trading strategy using {algorithm_type}",
            **kwargs,
        )

        self.algorithm_type = algorithm_type
        self.config = config or MLStrategyConfig(algorithm_type=algorithm_type)
        self.algorithm_manager = MLAlgorithmManager()
        self.trained_model_key = None
        self.last_trained = None

        # ML特定的属性
        self.feature_engineer = MLFeatureEngineer()

        logger.info(f"初始化ML交易策略: {strategy_name} (算法: {algorithm_type})")

    async def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        准备策略特定的特征

        子类可以重写此方法来添加自定义特征工程
        """
        # 默认特征工程
        df = self.feature_engineer.add_technical_features(data)
        df = self.feature_engineer.create_target_variable(df)

        return df

    async def train_ml_model(self, data: pd.DataFrame) -> str:
        """训练ML模型"""
        logger.info(f"开始训练{self.algorithm_type}模型...")

        # 准备特征
        prepared_data = await self.prepare_features(data)

        # 训练模型
        model_key = await self.algorithm_manager.train_model(self.algorithm_type, prepared_data, self.config)

        self.trained_model_key = model_key
        self.last_trained = datetime.now()

        logger.info(f"ML模型训练完成: {model_key}")
        return model_key

    async def should_retrain_model(self, current_date: datetime) -> bool:
        """检查是否需要重新训练模型"""
        if not self.last_trained:
            return True

        days_since_training = (current_date - self.last_trained).days
        return days_since_training >= self.config.retrain_frequency_days

    async def get_ml_prediction(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """获取ML预测结果"""
        if not self.trained_model_key:
            raise ValueError("ML model not trained. Call train_ml_model() first.")

        # 准备预测数据的特征（使用与训练相同的特征工程）
        prediction_data = await self.prepare_features(data)

        predictions = await self.algorithm_manager.predict(self.trained_model_key, prediction_data)
        return predictions

    @abstractmethod
    async def interpret_ml_signals(self, predictions: List[Dict[str, Any]], data: pd.DataFrame) -> pd.DataFrame:
        """
        解释ML预测结果为交易信号

        参数:
            predictions: ML预测结果列表
            data: 原始数据

        返回:
            包含交易信号的DataFrame
        """
        pass

    async def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信号 - 集成ML预测和传统策略逻辑
        """
        try:
            # 检查是否需要重新训练模型
            if await self.should_retrain_model(datetime.now()):
                await self.train_ml_model(data)

            # 获取ML预测
            ml_predictions = await self.get_ml_prediction(data)

            # 解释ML信号为交易信号
            signals_df = await self.interpret_ml_signals(ml_predictions, data)

            logger.info(f"生成 {len(signals_df)} 个交易信号")
            return signals_df

        except Exception as e:
            logger.error(f"ML策略信号生成失败: {e}")
            # 返回空信号DataFrame
            return pd.DataFrame(columns=["signal", "confidence", "timestamp"])

    def validate_parameters(self) -> bool:
        """验证ML策略参数"""
        try:
            # 验证算法类型
            supported_algorithms = ["svm", "decision_tree", "naive_bayes"]
            if self.algorithm_type not in supported_algorithms:
                logger.error(f"不支持的算法类型: {self.algorithm_type}")
                return False

            # 验证配置参数
            if self.config.prediction_threshold < 0 or self.config.prediction_threshold > 1:
                logger.error("预测阈值必须在[0,1]范围内")
                return False

            if self.config.confidence_threshold < 0 or self.config.confidence_threshold > 1:
                logger.error("置信度阈值必须在[0,1]范围内")
                return False

            return True

        except Exception as e:
            logger.error(f"参数验证失败: {e}")
            return False

    def get_strategy_info(self) -> Dict[str, Any]:
        """获取策略信息"""
        return {
            "strategy_name": self.name,  # Use self.name from BaseStrategy
            "algorithm_type": self.algorithm_type,
            "config": self.config.__dict__,
            "trained_model": self.trained_model_key,
            "last_trained": self.last_trained.isoformat() if self.last_trained else None,
            "strategy_type": "ml_enhanced",
        }
