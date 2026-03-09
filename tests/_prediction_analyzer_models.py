"""Model helpers extracted from `tests.ai.test_prediction_analyzer`."""

from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.svm import SVR

try:
    import xgboost as xgb
except ImportError:  # pragma: no cover - optional dependency
    xgb = None

try:
    from tensorflow.keras.callbacks import EarlyStopping
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.optimizers import Adam
except ImportError:  # pragma: no cover - optional dependency
    EarlyStopping = None
    LSTM = Dense = Dropout = Sequential = Adam = None


class FeatureExtractor:
    """特征提取器"""

    def __init__(self):
        self.feature_names = []
        self.scaler = StandardScaler()

    def extract_features(self, historical_data: List[Dict[str, Any]]) -> np.ndarray:
        """提取特征"""
        if not historical_data:
            return np.array([])

        feature_matrix = []

        for data_point in historical_data:
            features = []

            if "duration" in data_point:
                features.extend(
                    [
                        data_point["duration"],
                        data_point["duration"] ** 2,
                        math.sqrt(data_point["duration"]),
                        math.log(data_point["duration"] + 1),
                    ]
                )

            if "memory_usage" in data_point:
                features.extend([data_point["memory_usage"], data_point["memory_usage"] ** 2])

            if "cpu_usage" in data_point:
                features.extend([data_point["cpu_usage"], data_point["cpu_usage"] ** 2])

            if "timestamp" in data_point:
                timestamp = pd.to_datetime(data_point["timestamp"])
                features.extend(
                    [
                        timestamp.hour,
                        timestamp.dayofweek,
                        timestamp.day,
                        timestamp.month,
                        math.sin(2 * math.pi * timestamp.hour / 24),
                        math.cos(2 * math.pi * timestamp.hour / 24),
                        math.sin(2 * math.pi * timestamp.dayofweek / 7),
                        math.cos(2 * math.pi * timestamp.dayofweek / 7),
                    ]
                )

            if feature_matrix:
                previous_features = feature_matrix[-1]
                features.extend(
                    [
                        np.mean(previous_features[-4:]),
                        np.std(previous_features[-4:]),
                        previous_features[0],
                    ]
                )

            feature_matrix.append(features)

        if not feature_matrix:
            return np.array([])

        feature_array = np.array(feature_matrix)
        if not self.feature_names:
            self.feature_names = [f"feature_{index}" for index in range(feature_array.shape[1])]
            self.scaler.fit(feature_array)

        return self.scaler.transform(feature_array)

    def get_feature_names(self) -> List[str]:
        """获取特征名称"""
        return self.feature_names


class TimeSeriesPredictor:
    """时间序列预测器"""

    def __init__(self, model_type: Any):
        self.model_type = model_type
        self.model = None
        self.scaler = MinMaxScaler()
        self.is_trained = False
        self.training_history = []

    def train(self, time_series: np.ndarray) -> Dict[str, float]:
        """训练模型"""
        if len(time_series) < 10:
            raise ValueError("时间序列数据不足，至少需要10个数据点")

        features, targets = self._prepare_time_series_data(time_series)
        model_name = self._model_name

        if model_name == "linear_regression":
            self.model = LinearRegression()
        elif model_name == "ridge_regression":
            self.model = Ridge(alpha=1.0)
        elif model_name == "lasso_regression":
            self.model = Lasso(alpha=1.0)
        elif model_name == "random_forest":
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_name == "gradient_boosting":
            self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        elif model_name == "xgboost":
            if xgb is None:
                raise ImportError("xgboost 未安装")
            self.model = xgb.XGBRegressor(n_estimators=100, random_state=42)
        elif model_name == "svr":
            self.model = SVR(kernel="rbf", C=100, gamma=0.1, epsilon=0.1)
        elif model_name == "mlp":
            self.model = MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42)
        elif model_name == "lstm":
            if Sequential is None or EarlyStopping is None:
                raise ImportError("tensorflow 未安装")
            self.model = self._create_lstm_model(features.shape[1])
        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")

        if model_name == "lstm":
            history = self.model.fit(
                features,
                targets,
                epochs=100,
                batch_size=32,
                verbose=0,
                callbacks=[EarlyStopping(patience=10, restore_best_weights=True)],
            )
            training_loss = history.history["loss"][-1] if history.history["loss"] else float("inf")
        else:
            self.model.fit(features, targets)
            training_loss = 0

        predictions = self.model.predict(features)
        mse = mean_squared_error(targets, predictions)
        mae = mean_absolute_error(targets, predictions)
        r2 = r2_score(targets, predictions)

        self.is_trained = True
        self.training_history.append(
            {
                "timestamp": datetime.now(),
                "model_type": model_name,
                "mse": mse,
                "mae": mae,
                "r2": r2,
                "training_loss": training_loss,
            }
        )

        return {"mse": mse, "mae": mae, "r2": r2, "training_loss": training_loss}

    def predict(self, steps: int) -> List[float]:
        """预测未来值"""
        if not self.is_trained:
            raise ValueError("模型未训练")

        predictions = []
        current_sequence = self._get_initial_sequence()

        for _ in range(steps):
            if self._model_name == "lstm":
                input_data = current_sequence.reshape(1, -1, 1)
                prediction = self.model.predict(input_data, verbose=0)[0, 0]
            else:
                prediction = self.model.predict(current_sequence.reshape(1, -1))[0]

            current_sequence = np.roll(current_sequence, -1)
            current_sequence[-1] = prediction
            predictions.append(prediction)

        return predictions

    @property
    def _model_name(self) -> str:
        return getattr(self.model_type, "value", str(self.model_type))

    def _prepare_time_series_data(self, time_series: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """准备时间序列数据"""
        window_size = 5
        features, targets = [], []

        for index in range(len(time_series) - window_size):
            features.append(time_series[index : index + window_size])
            targets.append(time_series[index + window_size])

        return np.array(features), np.array(targets)

    def _create_lstm_model(self, input_shape: int):
        """创建LSTM模型"""
        model = Sequential(
            [
                LSTM(50, return_sequences=True, input_shape=(input_shape, 1)),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25),
                Dense(1),
            ]
        )
        model.compile(optimizer=Adam(learning_rate=0.001), loss="mse")
        return model

    def _get_initial_sequence(self) -> np.ndarray:
        """获取初始序列"""
        return np.random.randn(5)


__all__ = ["FeatureExtractor", "TimeSeriesPredictor"]
