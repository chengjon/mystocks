"""
机器学习策略 (Machine Learning Strategy)

功能说明:
- 基于机器学习的量化策略
- 自动特征工程
- 多种ML模型支持
- 模型训练和预测

支持的模型:
- Random Forest
- Gradient Boosting
- XGBoost / LightGBM
- Neural Networks

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import pickle

# Scikit-learn支持
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("警告: scikit-learn未安装，ML功能不可用")
    print("安装: pip install scikit-learn")

# 尝试导入BaseStrategy
try:
    from strategy.base_strategy import BaseStrategy

    BASE_STRATEGY_AVAILABLE = True
except ImportError:
    BASE_STRATEGY_AVAILABLE = False

    # 如果无法导入，创建一个简化版本
    class BaseStrategy:
        pass


class FeatureEngineering:
    """
    特征工程

    自动生成技术指标特征
    """

    @staticmethod
    def create_features(data: pd.DataFrame) -> pd.DataFrame:
        """
        创建特征

        参数:
            data: 价格数据（OHLCV）

        返回:
            DataFrame: 包含特征的数据
        """
        df = data.copy()

        # 1. 价格特征
        df["returns"] = df["close"].pct_change()
        df["log_returns"] = np.log(df["close"] / df["close"].shift(1))

        # 2. 移动平均
        for period in [5, 10, 20, 60]:
            df[f"ma_{period}"] = df["close"].rolling(period).mean()
            df[f"price_to_ma_{period}"] = df["close"] / df[f"ma_{period}"]

        # 3. 波动率
        for period in [5, 20]:
            df[f"volatility_{period}"] = df["returns"].rolling(period).std()

        # 4. 动量指标
        for period in [5, 10, 20]:
            df[f"momentum_{period}"] = df["close"] / df["close"].shift(period) - 1

        # 5. RSI
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["rsi_14"] = 100 - (100 / (1 + rs))

        # 6. 布林带
        df["bb_middle"] = df["close"].rolling(20).mean()
        bb_std = df["close"].rolling(20).std()
        df["bb_upper"] = df["bb_middle"] + 2 * bb_std
        df["bb_lower"] = df["bb_middle"] - 2 * bb_std
        df["bb_position"] = (df["close"] - df["bb_lower"]) / (
            df["bb_upper"] - df["bb_lower"]
        )

        # 7. 成交量特征
        df["volume_ma_20"] = df["volume"].rolling(20).mean()
        df["volume_ratio"] = df["volume"] / df["volume_ma_20"]

        # 8. 价格区间
        df["high_low_ratio"] = df["high"] / df["low"]
        df["close_open_ratio"] = df["close"] / df["open"]

        # 删除NaN
        df = df.dropna()

        return df

    @staticmethod
    def create_target(
        data: pd.DataFrame, forward_days: int = 1, threshold: float = 0.0
    ) -> pd.Series:
        """
        创建目标变量（分类）

        参数:
            data: 价格数据
            forward_days: 前瞻天数
            threshold: 涨跌阈值

        返回:
            Series: 目标变量 (1=涨, 0=跌)
        """
        future_returns = data["close"].shift(-forward_days) / data["close"] - 1
        target = (future_returns > threshold).astype(int)
        return target


class MLStrategy(BaseStrategy if BASE_STRATEGY_AVAILABLE else object):
    """
    机器学习策略

    使用机器学习模型预测股票涨跌
    """

    def __init__(
        self,
        model_type: str = "random_forest",
        forward_days: int = 1,
        threshold: float = 0.01,
        **kwargs,
    ):
        """
        初始化ML策略

        参数:
            model_type: 模型类型 ('random_forest', 'gradient_boosting')
            forward_days: 预测天数
            threshold: 涨跌阈值（默认1%）
            kwargs: 其他参数
        """
        if BASE_STRATEGY_AVAILABLE:
            super().__init__(
                name=f"ML_{model_type}",
                version="1.0.0",
                parameters={"model_type": model_type, "forward_days": forward_days},
            )

        self.logger = logging.getLogger(f"{__name__}.MLStrategy")

        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn未安装")

        self.model_type = model_type
        self.forward_days = forward_days
        self.threshold = threshold

        # 特征工程
        self.feature_engineer = FeatureEngineering()

        # 模型
        self.model = self._create_model()
        self.scaler = StandardScaler()

        # 特征列表
        self.feature_columns: List[str] = []

        # 训练状态
        self.is_trained = False

    def _create_model(self):
        """创建ML模型"""
        if self.model_type == "random_forest":
            return RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=20,
                min_samples_leaf=10,
                random_state=42,
            )
        elif self.model_type == "gradient_boosting":
            return GradientBoostingClassifier(
                n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42
            )
        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")

    def train(
        self, data: pd.DataFrame, test_size: float = 0.2, cross_validate: bool = True
    ) -> Dict:
        """
        训练模型

        参数:
            data: 训练数据（OHLCV）
            test_size: 测试集比例
            cross_validate: 是否交叉验证

        返回:
            Dict: 训练结果
        """
        self.logger.info("=" * 70)
        self.logger.info("开始训练ML模型")
        self.logger.info("=" * 70)

        # 1. 特征工程
        self.logger.info("1. 特征工程")
        df = self.feature_engineer.create_features(data)

        # 2. 创建目标变量
        target = self.feature_engineer.create_target(
            df, forward_days=self.forward_days, threshold=self.threshold
        )

        # 对齐数据
        df = df.iloc[: -self.forward_days]
        target = target.iloc[: -self.forward_days]

        # 3. 选择特征
        exclude_columns = ["open", "high", "low", "close", "volume", "amount"]
        self.feature_columns = [col for col in df.columns if col not in exclude_columns]

        X = df[self.feature_columns].values
        y = target.values

        self.logger.info(f"  特征数量: {len(self.feature_columns)}")
        self.logger.info(f"  样本数量: {len(X)}")
        self.logger.info(f"  正样本比例: {y.mean()*100:.2f}%")

        # 4. 数据标准化
        self.logger.info("\n2. 数据标准化")
        X_scaled = self.scaler.fit_transform(X)

        # 5. 划分训练集和测试集
        self.logger.info("\n3. 划分训练集和测试集")
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=test_size, random_state=42, stratify=y
        )

        self.logger.info(f"  训练集: {len(X_train)}")
        self.logger.info(f"  测试集: {len(X_test)}")

        # 6. 训练模型
        self.logger.info("\n4. 训练模型")
        self.model.fit(X_train, y_train)

        # 7. 评估模型
        self.logger.info("\n5. 评估模型")

        y_train_pred = self.model.predict(X_train)
        y_test_pred = self.model.predict(X_test)

        train_metrics = self._calculate_metrics(y_train, y_train_pred)
        test_metrics = self._calculate_metrics(y_test, y_test_pred)

        self.logger.info("\n训练集指标:")
        for key, value in train_metrics.items():
            self.logger.info(f"  {key}: {value:.4f}")

        self.logger.info("\n测试集指标:")
        for key, value in test_metrics.items():
            self.logger.info(f"  {key}: {value:.4f}")

        # 8. 交叉验证
        cv_score = None
        if cross_validate:
            self.logger.info("\n6. 交叉验证")
            cv_scores = cross_val_score(
                self.model, X_scaled, y, cv=5, scoring="accuracy"
            )
            cv_score = cv_scores.mean()
            self.logger.info(f"  CV准确率: {cv_score:.4f} (+/- {cv_scores.std():.4f})")

        # 9. 特征重要性
        if hasattr(self.model, "feature_importances_"):
            self.logger.info("\n7. Top 10 重要特征:")
            importances = self.model.feature_importances_
            indices = np.argsort(importances)[::-1][:10]

            for i, idx in enumerate(indices):
                self.logger.info(
                    f"  {i+1}. {self.feature_columns[idx]}: {importances[idx]:.4f}"
                )

        self.is_trained = True

        self.logger.info("\n" + "=" * 70)
        self.logger.info("✓ 模型训练完成")
        self.logger.info("=" * 70)

        return {
            "train_metrics": train_metrics,
            "test_metrics": test_metrics,
            "cv_score": cv_score,
            "feature_count": len(self.feature_columns),
            "sample_count": len(X),
        }

    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        预测

        参数:
            data: 预测数据

        返回:
            DataFrame: 预测结果
        """
        if not self.is_trained:
            raise RuntimeError("模型尚未训练")

        # 特征工程
        df = self.feature_engineer.create_features(data)

        # 提取特征
        X = df[self.feature_columns].values

        # 标准化
        X_scaled = self.scaler.transform(X)

        # 预测
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)[:, 1]

        # 构建结果
        result = df[["close"]].copy()
        result["prediction"] = predictions
        result["probability"] = probabilities

        return result

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信号

        参数:
            data: 价格数据

        返回:
            DataFrame: 信号数据
        """
        predictions = self.predict(data)

        signals = pd.DataFrame(index=predictions.index)
        signals["signal"] = "hold"

        # 基于预测生成信号
        signals.loc[predictions["prediction"] == 1, "signal"] = "buy"
        signals.loc[predictions["prediction"] == 0, "signal"] = "sell"

        # 添加概率阈值过滤
        prob_threshold = 0.6
        low_confidence = (predictions["probability"] > (1 - prob_threshold)) & (
            predictions["probability"] < prob_threshold
        )
        signals.loc[low_confidence, "signal"] = "hold"

        # 添加价格信息
        signals["price"] = predictions["close"]
        signals["probability"] = predictions["probability"]

        return signals

    def save_model(self, path: str):
        """保存模型"""
        if not self.is_trained:
            raise RuntimeError("模型尚未训练")

        model_data = {
            "model": self.model,
            "scaler": self.scaler,
            "feature_columns": self.feature_columns,
            "model_type": self.model_type,
            "forward_days": self.forward_days,
            "threshold": self.threshold,
        }

        with open(path, "wb") as f:
            pickle.dump(model_data, f)

        self.logger.info(f"✓ 模型已保存: {path}")

    def load_model(self, path: str):
        """加载模型"""
        with open(path, "rb") as f:
            model_data = pickle.load(f)

        self.model = model_data["model"]
        self.scaler = model_data["scaler"]
        self.feature_columns = model_data["feature_columns"]
        self.model_type = model_data["model_type"]
        self.forward_days = model_data["forward_days"]
        self.threshold = model_data["threshold"]

        self.is_trained = True

        self.logger.info(f"✓ 模型已加载: {path}")

    def _calculate_metrics(self, y_true, y_pred) -> Dict:
        """计算评估指标"""
        return {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall": recall_score(y_true, y_pred, zero_division=0),
            "f1_score": f1_score(y_true, y_pred, zero_division=0),
        }


if __name__ == "__main__":
    # 测试代码
    print("机器学习策略测试")
    print("=" * 70)

    if not SKLEARN_AVAILABLE:
        print("✗ scikit-learn未安装，无法测试")
        exit(1)

    # 设置日志
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # 生成测试数据
    print("\n生成测试数据...")
    np.random.seed(42)
    n = 500

    dates = pd.date_range("2023-01-01", periods=n, freq="D")
    price = 100 + np.cumsum(np.random.randn(n) * 2)

    test_data = pd.DataFrame(
        {
            "open": price + np.random.randn(n) * 0.5,
            "high": price + np.abs(np.random.randn(n)),
            "low": price - np.abs(np.random.randn(n)),
            "close": price,
            "volume": np.random.uniform(1000000, 10000000, n),
        },
        index=dates,
    )

    print(f"  数据量: {len(test_data)}")
    print(f"  日期范围: {test_data.index[0]} 至 {test_data.index[-1]}")

    # 创建ML策略
    print("\n创建ML策略...")
    strategy = MLStrategy(model_type="random_forest", forward_days=1, threshold=0.01)

    # 训练模型
    print("\n训练模型...")
    train_result = strategy.train(test_data, test_size=0.2)

    print("\n训练结果摘要:")
    print(f"  特征数量: {train_result['feature_count']}")
    print(f"  样本数量: {train_result['sample_count']}")
    print(f"  测试集准确率: {train_result['test_metrics']['accuracy']:.4f}")
    print(f"  测试集F1分数: {train_result['test_metrics']['f1_score']:.4f}")

    # 生成信号
    print("\n生成交易信号...")
    # 使用最后100天数据生成信号（确保有足够数据计算特征）
    signals = strategy.generate_signals(test_data.tail(100))

    print("\n最近10天信号:")
    print(signals[["signal", "price", "probability"]].tail(10))

    print("\n" + "=" * 70)
    print("测试完成")
