#!/usr/bin/env python3
"""
CPU回退版本模块
为GPU加速组件提供完全的CPU替代实现
确保在GPU不可用时，系统仍能正常工作
"""

import time
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split as sklearn_train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from datetime import datetime, timedelta

# 导入GPU模块中的数据类
from .price_predictor_gpu import PredictionResult, ModelPerformance


@dataclass
class ProcessingConfig:
    """CPU版本的处理配置"""

    remove_outliers: bool = True
    handle_missing: bool = True
    normalize_features: bool = True
    parallel_jobs: int = 1
    chunk_size: int = 10000


# CPU版本的价格预测器
class PricePredictorCPU:
    """CPU版本的价格预测器 - GPU版本的完整回退实现"""

    def __init__(self, gpu_enabled: bool = False):
        self.gpu_enabled = gpu_enabled
        self.models = {
            "linear": LinearRegression(),
            "ridge": Ridge(alpha=1.0),
            "lasso": Lasso(alpha=1.0),
            "random_forest": RandomForestRegressor(n_estimators=100, random_state=42),
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

    def _prepare_data_cpu(
        self, data: pd.DataFrame, target_col: str = "close"
    ) -> Tuple[np.ndarray, np.ndarray]:
        """准备CPU数据"""
        # 选择特征列（排除目标列）
        feature_cols = [col for col in data.columns if col != target_col]
        self.feature_columns = feature_cols

        # 提取特征和目标
        X = data[feature_cols].values
        y = data[target_col].values

        # 数据标准化
        X_scaled = self.scaler.fit_transform(X)

        return X_scaled, y

    def _create_lag_features(
        self, data: pd.DataFrame, lags: List[int] = [1, 2, 3, 5, 10]
    ) -> pd.DataFrame:
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

    def prepare_features(
        self, data: pd.DataFrame, prediction_horizon: int = 1
    ) -> pd.DataFrame:
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

    def train_models(
        self, data: pd.DataFrame, test_size: float = 0.2
    ) -> Dict[str, ModelPerformance]:
        """训练多个模型"""
        start_time = time.time()

        # 准备数据
        feature_data = self.prepare_features(data)

        # 分割训练和测试数据
        X, y = self._prepare_data_cpu(feature_data)
        X_train, X_test, y_train, y_test = sklearn_train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        training_results = {}

        for model_name, model in self.models.items():
            model_start_time = time.time()

            # 训练模型
            model.fit(X_train, y_train)

            # 预测
            y_pred = model.predict(X_test)

            # 计算性能指标
            training_time = time.time() - model_start_time

            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2_score_val = r2_score(y_test, y_pred)
            rmse = np.sqrt(mse)

            performance = ModelPerformance(
                training_time=training_time,
                prediction_time=0.001,
                mse=mse,
                mae=mae,
                r2_score=r2_score_val,
                rmse=rmse,
                is_gpu_enabled=self.gpu_enabled,
            )

            training_results[model_name] = performance
            self.performance_stats["model_scores"][model_name] = r2_score_val

            # 更新最佳模型
            if (
                self.performance_stats["best_model"] is None
                or r2_score_val > self.performance_stats["best_model"][1]
            ):
                self.performance_stats["best_model"] = (model_name, r2_score_val)

        self.is_fitted = True
        total_training_time = time.time() - start_time

        self.performance_stats["total_training_time"] = total_training_time

        self.logger.info(f"CPU模型训练完成，总耗时: {total_training_time:.2f}秒")
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

        # CPU预测
        predicted_price = float(model.predict(X)[0])

        prediction_time = time.time() - start_time

        # 计算置信度
        confidence_score = self._calculate_confidence_score(
            model_name, prediction_horizon
        )

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
                "mae": 0,
                "r2_score": self.performance_stats["model_scores"].get(model_name, 0),
            },
        )

        # 更新性能统计
        self.performance_stats["total_predictions"] += 1
        self.performance_stats["total_prediction_time"] += prediction_time

        return result

    def _calculate_confidence_score(
        self, model_name: str, prediction_horizon: int
    ) -> float:
        """计算预测置信度"""
        base_confidence = self.performance_stats["model_scores"].get(model_name, 0.5)

        # 根据预测时间调整置信度
        time_penalty = min(0.1 * prediction_horizon, 0.3)

        # 根据模型性能调整置信度
        model_adjustment = (
            0.1 if model_name == self.performance_stats["best_model"][0] else 0
        )

        confidence = max(
            0.0, min(1.0, base_confidence - time_penalty + model_adjustment)
        )
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
                self.logger.error(f"批量预测中发生错误: {e}")
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

    def optimize_hyperparameters(
        self, data: pd.DataFrame, model_type: str = "ridge"
    ) -> Dict:
        """优化超参数"""
        from sklearn.model_selection import GridSearchCV

        param_grid = {"alpha": [0.1, 1.0, 10.0, 100.0]}

        feature_data = self.prepare_features(data)
        X, y = self._prepare_data_cpu(feature_data)

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
        self.logger.info(f"CPU模型已保存到: {filepath}")

    def load_model(self, filepath: str):
        """加载模型"""
        import joblib

        model_data = joblib.load(filepath)

        self.models = model_data["models"]
        self.scaler = model_data["scaler"]
        self.feature_columns = model_data["feature_columns"]
        self.is_fitted = model_data["is_fitted"]
        self.performance_stats = model_data["performance_stats"]

        self.logger.info(f"CPU模型已从 {filepath} 加载")


# CPU版本的数据处理器
class DataProcessorCPU:
    """CPU版本的数据处理器 - GPU版本的完整回退实现"""

    def __init__(
        self, gpu_enabled: bool = False, n_jobs: int = 1, chunk_size: int = 10000
    ):
        self.gpu_enabled = gpu_enabled
        self.n_jobs = n_jobs
        self.chunk_size = chunk_size
        self.scaler = StandardScaler()
        self.logger = logging.getLogger(__name__)

        # 统计信息
        self.chunks_processed = 0
        self.total_data_processed = 0

    def preprocess(
        self, data: pd.DataFrame, config: Optional[ProcessingConfig] = None
    ) -> pd.DataFrame:
        """数据预处理"""
        config = config or ProcessingConfig()
        processed_data = data.copy()

        # 去除异常值
        if config.remove_outliers:
            processed_data = self._remove_outliers(processed_data)

        # 处理缺失值
        if config.handle_missing:
            processed_data = self._handle_missing_values(processed_data)

        # 添加技术指标
        processed_data = self._add_technical_indicators(processed_data)

        # 特征标准化
        if config.normalize_features:
            processed_data = self._normalize_features(processed_data)

        self.chunks_processed += 1
        self.total_data_processed += len(processed_data)

        return processed_data

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

    def _handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """处理缺失值"""
        # 数值列用前向填充，然后用后向填充
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            data[col] = data[col].fillna(method="ffill").fillna(method="bfill")

        # 分类列用众数填充
        categorical_columns = data.select_dtypes(include=["object"]).columns
        for col in categorical_columns:
            data[col] = data[col].fillna(data[col].mode()[0])

        return data

    def _add_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """添加技术指标"""
        # 移动平均
        data["sma_5"] = data["close"].rolling(window=5).mean()
        data["sma_20"] = data["close"].rolling(window=20).mean()
        data["sma_50"] = data["close"].rolling(window=50).mean()

        # RSI
        data["rsi"] = self._calculate_rsi(data["close"])

        # MACD
        data["macd"], data["macd_signal"] = self._calculate_macd(data["close"])

        # 布林带
        data["bb_middle"] = data["close"].rolling(window=20).mean()
        data["bb_upper"] = data["bb_middle"] + (
            data["close"].rolling(window=20).std() * 2
        )
        data["bb_lower"] = data["bb_middle"] - (
            data["close"].rolling(window=20).std() * 2
        )

        return data

    def _normalize_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """特征标准化"""
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        feature_data = data[numeric_columns]

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

    def parallel_process(self, data_list: List[pd.DataFrame]) -> List[pd.DataFrame]:
        """并行处理多个数据集"""
        results = []

        for i, data in enumerate(data_list):
            try:
                processed_data = self.preprocess(data)
                results.append(processed_data)

                if (i + 1) % 10 == 0:
                    self.logger.info(f"并行处理进度: {i + 1}/{len(data_list)}")

            except Exception as e:
                self.logger.error(f"处理第 {i + 1} 个数据时出错: {e}")
                results.append(data)  # 出错时返回原始数据

        return results

    def get_performance_summary(self) -> Dict:
        """获取性能总结"""
        return {
            "gpu_enabled": self.gpu_enabled,
            "n_jobs": self.n_jobs,
            "chunk_size": self.chunk_size,
            "chunks_processed": self.chunks_processed,
            "total_data_processed": self.total_data_processed,
        }


# CPU版本的特征生成器
class FeatureGeneratorCPU:
    """CPU版本的特征生成器 - GPU版本的完整回退实现"""

    def __init__(self, gpu_enabled: bool = False):
        self.gpu_enabled = gpu_enabled
        self.logger = logging.getLogger(__name__)
        self.features_generated = 0

    def generate_features(
        self, data: pd.DataFrame, feature_types: List[str] = None
    ) -> pd.DataFrame:
        """生成特征"""
        feature_types = feature_types or [
            "technical",
            "statistical",
            "momentum",
            "volatility",
        ]

        feature_data = data.copy()

        for feature_type in feature_types:
            if feature_type == "technical":
                feature_data = self._generate_technical_features(feature_data)
            elif feature_type == "statistical":
                feature_data = self._generate_statistical_features(feature_data)
            elif feature_type == "momentum":
                feature_data = self._generate_momentum_features(feature_data)
            elif feature_type == "volatility":
                feature_data = self._generate_volatility_features(feature_data)

        self.features_generated += len(feature_data.columns)
        return feature_data

    def _generate_technical_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成技术特征"""
        # 移动平均
        windows = [5, 10, 20, 50]
        for window in windows:
            data[f"sma_{window}"] = data["close"].rolling(window=window).mean()
            data[f"ema_{window}"] = data["close"].ewm(span=window).mean()

        # 布林带
        data["bb_middle"] = data["close"].rolling(window=20).mean()
        data["bb_upper"] = data["bb_middle"] + (
            data["close"].rolling(window=20).std() * 2
        )
        data["bb_lower"] = data["bb_middle"] - (
            data["close"].rolling(window=20).std() * 2
        )

        return data

    def _generate_statistical_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成统计特征"""
        # 价格统计
        data["price_mean"] = data["close"].expanding().mean()
        data["price_std"] = data["close"].expanding().std()
        data["price_skew"] = data["close"].expanding().skew()
        data["price_kurt"] = data["close"].expanding().kurt()

        # 成交量统计
        if "volume" in data.columns:
            data["volume_mean"] = data["volume"].expanding().mean()
            data["volume_std"] = data["volume"].expanding().std()

        return data

    def _generate_momentum_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成动量特征"""
        # 价格变化率
        periods = [1, 3, 5, 10, 20]
        for period in periods:
            data[f"return_{period}"] = data["close"].pct_change(period)

        # 价格动量
        for period in [5, 10, 20]:
            data[f"momentum_{period}"] = data["close"] / data["close"].shift(period) - 1

        return data

    def _generate_volatility_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成波动率特征"""
        # 波动率
        windows = [5, 10, 20]
        for window in windows:
            returns = data["close"].pct_change().rolling(window=window).std()
            data[f"volatility_{window}"] = returns * np.sqrt(252)  # 年化波动率

        # ATR (平均真实波幅)
        high_low = data["high"] - data["low"]
        high_close = np.abs(data["high"] - data["close"].shift())
        low_close = np.abs(data["low"] - data["close"].shift())
        true_range = np.maximum(high_low, high_close, low_close)
        data["atr"] = true_range.rolling(window=14).mean()

        return data

    def get_performance_summary(self) -> Dict:
        """获取性能总结"""
        return {
            "gpu_enabled": self.gpu_enabled,
            "features_generated": self.features_generated,
        }


# 智能选择器 - 自动选择GPU或CPU版本
class ComponentSelector:
    """智能组件选择器 - 根据环境自动选择GPU或CPU版本"""

    def __init__(self):
        self.gpu_available = self._check_gpu_availability()
        self.logger = logging.getLogger(__name__)

    def _check_gpu_availability(self) -> bool:
        """检查GPU是否可用"""
        try:
            import cupy as cp

            # 检查是否有GPU设备
            cp.cuda.Device(0)
            return True
        except:
            return False

    def get_price_predictor(self, gpu_enabled: Optional[bool] = None):
        """获取价格预测器"""
        if gpu_enabled is True:
            # 强制使用GPU
            from .price_predictor_gpu import GPUPricePredictor

            return GPUPricePredictor(gpu_enabled=True)
        elif gpu_enabled is False:
            # 强制使用CPU
            return PricePredictorCPU(gpu_enabled=False)
        else:
            # 自动选择
            if self.gpu_available:
                from .price_predictor_gpu import GPUPricePredictor

                return GPUPricePredictor(gpu_enabled=True)
            else:
                self.logger.info("GPU不可用，使用CPU版本")
                return PricePredictorCPU(gpu_enabled=False)

    def get_data_processor(self, gpu_enabled: Optional[bool] = None):
        """获取数据处理器"""
        if gpu_enabled is True:
            from .data_processor_gpu import GPUDataProcessor

            return GPUDataProcessor(gpu_enabled=True)
        elif gpu_enabled is False:
            return DataProcessorCPU(gpu_enabled=False)
        else:
            if self.gpu_available:
                from .data_processor_gpu import GPUDataProcessor

                return GPUDataProcessor(gpu_enabled=True)
            else:
                self.logger.info("GPU不可用，使用CPU版本")
                return DataProcessorCPU(gpu_enabled=False)

    def get_feature_generator(self, gpu_enabled: Optional[bool] = None):
        """获取特征生成器"""
        if gpu_enabled is True:
            from .feature_generator_gpu import GPUFeatureGenerator

            return GPUFeatureGenerator(gpu_enabled=True)
        elif gpu_enabled is False:
            return FeatureGeneratorCPU(gpu_enabled=False)
        else:
            if self.gpu_available:
                from .feature_generator_gpu import GPUFeatureGenerator

                return GPUFeatureGenerator(gpu_enabled=True)
            else:
                self.logger.info("GPU不可用，使用CPU版本")
                return FeatureGeneratorCPU(gpu_enabled=False)

    def get_environment_info(self) -> Dict[str, any]:
        """获取环境信息"""
        return {
            "gpu_available": self.gpu_available,
            "cpu_fallback_available": True,
            "selected_mode": "GPU" if self.gpu_available else "CPU",
        }


# 全局智能选择器实例
_component_selector = ComponentSelector()


def get_component_selector() -> ComponentSelector:
    """获取全局组件选择器"""
    return _component_selector


def auto_select_component(component_type: str, gpu_enabled: Optional[bool] = None):
    """自动选择组件"""
    selector = get_component_selector()

    if component_type == "price_predictor":
        return selector.get_price_predictor(gpu_enabled)
    elif component_type == "data_processor":
        return selector.get_data_processor(gpu_enabled)
    elif component_type == "feature_generator":
        return selector.get_feature_generator(gpu_enabled)
    else:
        raise ValueError(f"不支持的组件类型: {component_type}")


def main():
    """主函数 - CPU版本测试"""
    print("🔄 CPU回退版本测试")
    print("=" * 40)

    # 创建组件选择器
    selector = ComponentSelector()
    print(f"GPU可用性: {selector.gpu_available}")

    # 测试价格预测器
    print("\n1. 价格预测器测试:")
    predictor = auto_select_component("price_predictor")
    print(f"使用版本: {'GPU' if selector.gpu_available else 'CPU'}")

    # 获取测试数据
    import yfinance as yf

    test_data = yf.download("AAPL", start="2023-01-01", end="2024-01-01")

    # 训练模型
    print("训练模型...")
    training_results = predictor.train_models(test_data[:200])  # 使用小样本
    print(f"训练完成，最佳模型: {predictor.performance_stats['best_model'][0]}")

    # 进行预测
    print("进行预测...")
    prediction = predictor.predict_price(test_data)
    print(f"预测价格: {prediction.predicted_price:.2f}")
    print(f"置信度: {prediction.confidence_score:.2f}")

    # 测试数据处理器
    print("\n2. 数据处理器测试:")
    processor = auto_select_component("data_processor")
    processed_data = processor.preprocess(test_data[:50])
    print(f"处理完成，数据形状: {processed_data.shape}")

    # 测试特征生成器
    print("\n3. 特征生成器测试:")
    feature_generator = auto_select_component("feature_generator")
    features = feature_generator.generate_features(test_data[:50])
    print(f"特征生成完成，特征数量: {len(features.columns)}")

    # 显示环境信息
    print("\n4. 环境信息:")
    env_info = selector.get_environment_info()
    for key, value in env_info.items():
        print(f"  {key}: {value}")

    print("\n✅ CPU回退版本测试完成")


if __name__ == "__main__":
    main()
