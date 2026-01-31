#!/usr/bin/env python3
"""
GPU加速的价格预测器
基于cuML机器学习库实现高性能价格预测
支持RTX 2080 GPU加速，提供实时预测能力
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import cudf
import cupy as cp
import numpy as np
import pandas as pd
from cuml.ensemble import RandomForestRegressor
from cuml.linear_model import Lasso, LinearRegression, Ridge
from cuml.model_selection import train_test_split as gpu_train_test_split
from cuml.preprocessing import StandardScaler


@dataclass
class PredictionResult:
    """预测结果"""

    predicted_price: float
    confidence_score: float
    prediction_date: datetime
    model_used: str
    features_used: List[str]
    prediction_horizon: int  # 预测天数
    error_metrics: Dict[str, float]


@dataclass
class ModelPerformance:
    """模型性能指标"""

    training_time: float
    prediction_time: float
    mse: float
    mae: float
    r2_score: float
    rmse: float
    is_gpu_enabled: bool


class GPUPricePredictor:
    """GPU加速的价格预测器"""

    def __init__(self, gpu_enabled: bool = True):
        self.gpu_enabled = gpu_enabled
        self.models = {
            "linear": LinearRegression(),
            "ridge": Ridge(alpha=1.0),
            "lasso": Lasso(alpha=1.0),
            "random_forest": RandomForestRegressor(n_estimators=100),
        }
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.feature_columns = []
        self.target_column = "close"
        self.logger = logging.getLogger(__name__)

        # 性能统计
        self.performance_stats = {
            "total_predictions": 0,
            "total_training_time": 0,
            "total_prediction_time": 0,
            "best_model": None,
            "model_scores": {},
        }

    def _prepare_data_gpu(self, data: pd.DataFrame, target_col: str = "close") -> Tuple[cp.ndarray, cp.ndarray]:
        """准备GPU数据"""
        # 转换为cuDF DataFrame
        df_gpu = cudf.DataFrame(data) if self.gpu_enabled else data

        # 选择特征列（排除目标列）
        feature_cols = [col for col in df_gpu.columns if col != target_col]
        self.feature_columns = feature_cols

        # 提取特征和目标
        X = df_gpu[feature_cols]
        y = df_gpu[target_col]

        # 数据标准化
        X_scaled = self.scaler.fit_transform(X) if self.gpu_enabled else StandardScaler().fit_transform(X)

        return X_scaled, y

    def _create_lag_features(self, data: pd.DataFrame, lags: List[int] = [1, 2, 3, 5, 10]) -> pd.DataFrame:
        """创建滞后特征"""
        df = data.copy()

        for lag in lags:
            df[f"close_lag_{lag}"] = df["close"].shift(lag)

        # 创建技术指标特征
        df["sma_5"] = df["close"].rolling(window=5).mean()
        df["sma_10"] = df["close"].rolling(window=10).mean()
        df["sma_20"] = df["close"].rolling(window=20).mean()

        df["rsi"] = self._calculate_rsi(data["close"])
        df["macd"], df["macd_signal"] = self._calculate_macd(data["close"])

        # 价格变化特征
        df["price_change"] = df["close"].pct_change()
        df["volatility"] = df["price_change"].rolling(window=10).std()

        return df

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(
        self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Tuple[pd.Series, pd.Series]:
        """计算MACD指标"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        return macd, macd_signal

    def prepare_features(self, data: pd.DataFrame, prediction_horizon: int = 1) -> pd.DataFrame:
        """准备特征数据"""
        # 创建滞后特征
        feature_data = self._create_lag_features(data)

        # 删除NaN值
        feature_data = feature_data.dropna()

        # 添加预测目标
        feature_data["target"] = feature_data["close"].shift(-prediction_horizon)

        # 删除最后的prediction_horizon行（没有目标值）
        feature_data = feature_data.iloc[:-prediction_horizon]

        return feature_data

    def train_models(self, data: pd.DataFrame, test_size: float = 0.2) -> Dict[str, ModelPerformance]:
        """训练多个模型"""
        start_time = time.time()

        # 准备数据
        feature_data = self.prepare_features(data)

        # 分割训练和测试数据
        X, y = self._prepare_data_gpu(feature_data)
        X_train, X_test, y_train, y_test = gpu_train_test_split(X, y, test_size=test_size, random_state=42)

        training_results = {}

        for model_name, model in self.models.items():
            model_start_time = time.time()

            # 训练模型
            model.fit(X_train, y_train)

            # 预测
            y_pred = model.predict(X_test)

            # 计算性能指标
            training_time = time.time() - model_start_time

            if self.gpu_enabled:
                y_pred_cpu = y_pred.to_numpy()
                y_test_cpu = y_test.to_numpy()
            else:
                y_pred_cpu = y_pred
                y_test_cpu = y_test

            mse = np.mean((y_pred_cpu - y_test_cpu) ** 2)
            mae = np.mean(np.abs(y_pred_cpu - y_test_cpu))
            r2_score = 1 - (np.sum((y_test_cpu - y_pred_cpu) ** 2) / np.sum((y_test_cpu - np.mean(y_test_cpu)) ** 2))
            rmse = np.sqrt(mse)

            performance = ModelPerformance(
                training_time=training_time,
                prediction_time=0.001,  # 预测时间很短
                mse=mse,
                mae=mae,
                r2_score=r2_score,
                rmse=rmse,
                is_gpu_enabled=self.gpu_enabled,
            )

            training_results[model_name] = performance
            self.performance_stats["model_scores"][model_name] = r2_score

            # 更新最佳模型
            if self.performance_stats["best_model"] is None or r2_score > self.performance_stats["best_model"][1]:
                self.performance_stats["best_model"] = (model_name, r2_score)

        self.is_fitted = True
        total_training_time = time.time() - start_time

        self.performance_stats["total_training_time"] = total_training_time

        self.logger.info("模型训练完成，总耗时: %s秒", total_training_time)
        return training_results

    def predict_price(
        self, data: pd.DataFrame, model_name: str = None, prediction_horizon: int = 1
    ) -> PredictionResult:
        """预测价格"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练，请先调用train_models方法")

        start_time = time.time()

        # 选择模型
        if model_name is None:
            model_name = self.performance_stats["best_model"][0]

        model = self.models[model_name]

        # 准备数据
        feature_data = self.prepare_features(data, prediction_horizon)

        # 获取最后一行数据作为预测输入
        last_row = feature_data.iloc[-1:].copy()

        # 移除目标列
        if "target" in last_row.columns:
            last_row = last_row.drop("target", axis=1)

        # 数据标准化
        X = self.scaler.transform(last_row)

        # GPU预测
        if self.gpu_enabled:
            X_gpu = cp.array(X)
            predicted_gpu = model.predict(X_gpu)
            predicted_price = float(predicted_gpu.to_numpy()[0])
        else:
            predicted_price = float(model.predict(X)[0])

        prediction_time = time.time() - start_time

        # 计算置信度
        confidence_score = self._calculate_confidence_score(model_name, prediction_horizon)

        # 创建预测结果
        result = PredictionResult(
            predicted_price=predicted_price,
            confidence_score=confidence_score,
            prediction_date=datetime.now() + timedelta(days=prediction_horizon),
            model_used=model_name,
            features_used=self.feature_columns,
            prediction_horizon=prediction_horizon,
            error_metrics={
                "mse": self.performance_stats["model_scores"].get(model_name, 0),
                "mae": 0,  # 这里可以添加更多计算
                "r2_score": self.performance_stats["model_scores"].get(model_name, 0),
            },
        )

        # 更新性能统计
        self.performance_stats["total_predictions"] += 1
        self.performance_stats["total_prediction_time"] += prediction_time

        return result

    def _calculate_confidence_score(self, model_name: str, prediction_horizon: int) -> float:
        """计算预测置信度"""
        base_confidence = self.performance_stats["model_scores"].get(model_name, 0.5)

        # 根据预测时间调整置信度
        time_penalty = min(0.1 * prediction_horizon, 0.3)

        # 根据模型性能调整置信度
        model_adjustment = 0.1 if model_name == self.performance_stats["best_model"][0] else 0

        confidence = max(0.0, min(1.0, base_confidence - time_penalty + model_adjustment))
        return confidence

    def batch_predict(
        self,
        data_list: List[pd.DataFrame],
        model_name: str = None,
        prediction_horizon: int = 1,
    ) -> List[PredictionResult]:
        """批量预测"""
        results = []

        for data in data_list:
            try:
                result = self.predict_price(data, model_name, prediction_horizon)
                results.append(result)
            except Exception as e:
                self.logger.error("批量预测中发生错误: %s", e)
                continue

        return results

    def get_performance_summary(self) -> Dict:
        """获取性能总结"""
        avg_prediction_time = self.performance_stats["total_prediction_time"] / max(
            1, self.performance_stats["total_predictions"]
        )

        return {
            "gpu_enabled": self.gpu_enabled,
            "total_predictions": self.performance_stats["total_predictions"],
            "total_training_time": self.performance_stats["total_training_time"],
            "avg_prediction_time": avg_prediction_time,
            "best_model": self.performance_stats["best_model"],
            "model_scores": self.performance_stats["model_scores"],
            "is_fitted": self.is_fitted,
        }

    def optimize_hyperparameters(self, data: pd.DataFrame, model_type: str = "ridge") -> Dict:
        """优化超参数"""
        if self.gpu_enabled:
            from cuml.linear_model import Ridge
            from cuml.model_selection import GridSearchCV

            # 定义参数网格
            param_grid = {"alpha": [0.1, 1.0, 10.0, 100.0]}

            # 准备数据
            feature_data = self.prepare_features(data)
            X, y = self._prepare_data_gpu(feature_data)

            # 创建网格搜索
            grid_search = GridSearchCV(
                Ridge(),
                param_grid,
                cv=5,
                scoring="r2",
                n_jobs=-1 if not self.gpu_enabled else 1,  # GPU时不需要多进程
            )

            grid_search.fit(X, y)

            return {
                "best_params": grid_search.best_params_,
                "best_score": grid_search.best_score_,
                "model_type": model_type,
            }
        else:
            # CPU版本的超参数优化
            from sklearn.model_selection import GridSearchCV

            param_grid = {"alpha": [0.1, 1.0, 10.0, 100.0]}

            feature_data = self.prepare_features(data)
            X, y = self._prepare_data_gpu(feature_data)

            grid_search = GridSearchCV(Ridge(), param_grid, cv=5, scoring="r2", n_jobs=-1)

            grid_search.fit(X, y)

            return {
                "best_params": grid_search.best_params_,
                "best_score": grid_search.best_score_,
                "model_type": model_type,
            }

    def save_model(self, filepath: str):
        """保存模型"""
        import joblib

        model_data = {
            "models": self.models,
            "scaler": self.scaler,
            "feature_columns": self.feature_columns,
            "is_fitted": self.is_fitted,
            "performance_stats": self.performance_stats,
        }

        joblib.dump(model_data, filepath)
        self.logger.info("模型已保存到: %s", filepath)

    def load_model(self, filepath: str):
        """加载模型"""
        import joblib

        model_data = joblib.load(filepath)

        self.models = model_data["models"]
        self.scaler = model_data["scaler"]
        self.feature_columns = model_data["feature_columns"]
        self.is_fitted = model_data["is_fitted"]
        self.performance_stats = model_data["performance_stats"]

        self.logger.info("模型已从 %s 加载", filepath)


class GPUPredictionPipeline:
    """GPU预测流水线"""

    def __init__(self, gpu_enabled: bool = True):
        self.predictor = GPUPricePredictor(gpu_enabled)
        self.data_preprocessor = DataPreprocessorGPU(gpu_enabled)

    def run_full_pipeline(self, raw_data: pd.DataFrame, prediction_horizon: int = 1) -> Dict:
        """运行完整的预测流水线"""
        # 数据预处理
        processed_data = self.data_preprocessor.preprocess(raw_data)

        # 训练模型
        training_results = self.predictor.train_models(processed_data)

        # 进行预测
        prediction_result = self.predictor.predict_price(processed_data, prediction_horizon=prediction_horizon)

        # 获取性能总结
        performance_summary = self.predictor.get_performance_summary()

        return {
            "training_results": training_results,
            "prediction": prediction_result,
            "performance": performance_summary,
            "data_shape": processed_data.shape,
        }


class DataPreprocessorGPU:
    """GPU数据预处理器"""

    def __init__(self, gpu_enabled: bool = True):
        self.gpu_enabled = gpu_enabled
        self.scaler = StandardScaler()

    def preprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        """数据预处理"""
        # 去除异常值
        data = self._remove_outliers(data)

        # 添加技术指标
        data = self._add_technical_indicators(data)

        # 特征标准化
        data = self._normalize_features(data)

        return data

    def _remove_outliers(self, data: pd.DataFrame) -> pd.DataFrame:
        """去除异常值"""
        numeric_columns = data.select_dtypes(include=[np.number]).columns

        for col in numeric_columns:
            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            data = data[(data[col] >= lower_bound) & (data[col] <= upper_bound)]

        return data

    def _add_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """添加技术指标"""
        # 移动平均
        data["sma_5"] = data["close"].rolling(window=5).mean()
        data["sma_20"] = data["close"].rolling(window=20).mean()

        # RSI
        data["rsi"] = self._calculate_rsi(data["close"])

        # MACD
        data["macd"], data["macd_signal"] = self._calculate_macd(data["close"])

        return data

    def _normalize_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """特征标准化"""
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        feature_data = data[numeric_columns]

        if self.gpu_enabled:
            feature_gpu = cudf.DataFrame(feature_data)
            normalized_features = self.scaler.fit_transform(feature_gpu)
            normalized_df = cudf.DataFrame(normalized_features, columns=feature_gpu.columns)
        else:
            normalized_features = self.scaler.fit_transform(feature_data)
            normalized_df = pd.DataFrame(normalized_features, columns=feature_data.columns)

        # 合并回原始数据
        result = data.copy()
        for col in normalized_df.columns:
            result[f"{col}_normalized"] = normalized_df[col].values

        return result

    def _calculate_rsi(self, prices: pd.Series) -> pd.Series:
        """计算RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(self, prices: pd.Series) -> Tuple[pd.Series, pd.Series]:
        """计算MACD"""
        ema_fast = prices.ewm(span=12).mean()
        ema_slow = prices.ewm(span=26).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=9).mean()
        return macd, macd_signal


def benchmark_gpu_vs_cpu(data: pd.DataFrame, prediction_horizon: int = 1):
    """GPU vs CPU性能对比"""
    print("🔬 开始GPU vs CPU性能对比测试...")

    # GPU版本
    gpu_pipeline = GPUPredictionPipeline(gpu_enabled=True)
    gpu_start = time.time()
    gpu_results = gpu_pipeline.run_full_pipeline(data, prediction_horizon)
    gpu_time = time.time() - gpu_start

    # CPU版本
    cpu_pipeline = GPUPredictionPipeline(gpu_enabled=False)
    cpu_start = time.time()
    cpu_results = cpu_pipeline.run_full_pipeline(data, prediction_horizon)
    cpu_time = time.time() - cpu_start

    # 对比结果
    print("\n📊 性能对比结果:")
    print(f"GPU训练时间: {gpu_time:.2f}秒")
    print(f"CPU训练时间: {cpu_time:.2f}秒")
    print(f"加速比: {cpu_time / gpu_time:.2f}x")
    print(f"GPU预测结果: {gpu_results['prediction'].predicted_price:.2f}")
    print(f"CPU预测结果: {cpu_results['prediction'].predicted_price:.2f}")
    print(f"预测差异: {abs(gpu_results['prediction'].predicted_price - cpu_results['prediction'].predicted_price):.2f}")

    return {
        "gpu_time": gpu_time,
        "cpu_time": cpu_time,
        "speedup": cpu_time / gpu_time,
        "gpu_results": gpu_results,
        "cpu_results": cpu_results,
    }


if __name__ == "__main__":
    # 示例使用
    import yfinance as yf

    # 获取示例数据
    data = yf.download("AAPL", start="2023-01-01", end="2024-01-01")

    # 创建预测器
    predictor = GPUPricePredictor(gpu_enabled=True)

    # 训练模型
    training_results = predictor.train_models(data)

    # 进行预测
    prediction = predictor.predict_price(data)

    # 显示结果
    print(f"预测价格: {prediction.predicted_price:.2f}")
    print(f"置信度: {prediction.confidence_score:.2f}")
    print(f"使用的模型: {prediction.model_used}")

    # 性能总结
    performance = predictor.get_performance_summary()
    print("\n性能总结:")
    print(f"GPU加速: {performance['gpu_enabled']}")
    print(f"总预测次数: {performance['total_predictions']}")
    print(f"平均预测时间: {performance['avg_prediction_time']:.4f}秒")

    # 运行性能对比
    benchmark_results = benchmark_gpu_vs_cpu(data)
    print(f"\nGPU加速性能提升: {benchmark_results['speedup']:.2f}x")
