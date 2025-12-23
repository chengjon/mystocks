import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Tuple
from src.gpu.data_processing_interfaces import IDataProcessor
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """数据处理结果"""

    processed_data: pd.DataFrame
    processing_time: float
    memory_usage: Dict[str, float]
    gpu_accelerated: bool
    quality_metrics: Dict[str, float]
    data_shape: Tuple[int, int]


class CPUDataProcessor(IDataProcessor):
    """
    CPU数据处理器
    实现IDataProcessor接口，使用Pandas/Numpy进行数据处理
    """

    def __init__(self):
        self.scalers = {}
        self.preprocessing_pipeline = {}
        logger.info("CPUDataProcessor initialized.")

    def load_and_preprocess(self, data: pd.DataFrame) -> Dict[str, Any]:
        """加载和预处理数据 (CPU实现)"""
        start_time = pd.Timestamp.now()

        # 数据质量检查
        quality_metrics = self._check_data_quality(data)

        # 处理缺失值
        cleaned_data = self._handle_missing_values(data)

        # 数据类型优化
        optimized_data = self._optimize_dtypes(cleaned_data)

        # 异常值处理
        cleaned_data = self._handle_outliers(optimized_data)

        # 特征标准化
        processed_data = self._normalize_features(cleaned_data)

        processing_time = (pd.Timestamp.now() - start_time).total_seconds()

        # 计算内存使用
        memory_usage = {
            "original_memory": data.memory_usage(deep=True).sum(),
            "processed_memory": processed_data.memory_usage(deep=True).sum(),
            "compression_ratio": (
                data.memory_usage(deep=True).sum()
                / processed_data.memory_usage(deep=True).sum()
                if processed_data.memory_usage(deep=True).sum() > 0
                else 1.0
            ),
        }

        return {
            "processed_data": processed_data,
            "processing_time": processing_time,
            "memory_usage": memory_usage,
            "gpu_accelerated": False,
            "quality_metrics": quality_metrics,
            "data_shape": processed_data.shape,
        }

    def process_batch(self, batch_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        CPU批量处理数据
        Args:
            batch_data: 包含数据点（字典）的列表，每个字典应包含 'stock_code', 'price', 'volume', 'timestamp' 等键
        Returns:
            处理后的数据字典列表，包含 'price_change', 'volume_ma' 等
        """
        processed_results = []
        for item in batch_data:
            # 在CPU实现中，我们暂时只返回原始数据加上占位符
            # 更复杂的CPU逻辑（例如计算历史数据）将需要额外的设计
            processed_results.append(
                {
                    "stock_code": item.get("stock_code"),
                    "price": item.get("price"),
                    "volume": item.get("volume"),
                    "timestamp": item.get("timestamp"),
                    "price_change": 0.0,  # 需历史数据计算
                    "volume_ma": 0.0,  # 需历史数据计算
                }
            )
        return processed_results

    def compute_features(
        self, historical_data: List[Dict], feature_types: List[str]
    ) -> Dict[str, float]:
        """
        CPU计算技术特征
        """
        df = pd.DataFrame(historical_data)
        features = {}

        if df.empty or "price" not in df.columns or len(df) < 20:  # 至少20个数据点
            logger.warning(
                "Historical data is insufficient or empty for feature calculation."
            )
            return features

        prices = df["price"]
        volumes = (
            df["volume"] if "volume" in df.columns else pd.Series(0, index=df.index)
        )

        for feature_type in feature_types:
            if feature_type == "sma_20":
                features["sma_20"] = float(prices.rolling(window=20).mean().iloc[-1])
            elif feature_type == "sma_50":
                if len(df) >= 50:
                    features["sma_50"] = float(
                        prices.rolling(window=50).mean().iloc[-1]
                    )
                else:
                    features["sma_50"] = 0.0
            elif feature_type == "rsi":
                features["rsi"] = self._calculate_rsi_cpu(prices)
            elif feature_type == "macd":
                macd_values = self._calculate_macd_cpu(prices)
                features.update(macd_values)
            elif feature_type == "bollinger":
                bb_values = self._calculate_bollinger_cpu(prices)
                features.update(bb_values)
            elif feature_type == "volume_ratio":
                volume_ma = volumes.rolling(window=20).mean().iloc[-1]
                current_volume = volumes.iloc[-1]
                features["volume_ratio"] = (
                    float(current_volume / volume_ma) if volume_ma > 0 else 0.0
                )
        return features

    # --- 辅助方法 (从原 GPUDataProcessor 移植，并去除GPU相关逻辑) ---

    def _check_data_quality(self, data: pd.DataFrame) -> Dict[str, float]:
        """检查数据质量"""
        quality_metrics = {}

        missing_values = data.isnull().sum()
        total_cells = data.shape[0] * data.shape[1]
        missing_ratio = missing_values.sum() / total_cells
        quality_metrics["missing_ratio"] = missing_ratio

        duplicate_ratio = data.duplicated().sum() / len(data)
        quality_metrics["duplicate_ratio"] = duplicate_ratio

        numeric_columns = data.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            inf_count = np.isinf(data[numeric_columns]).sum().sum()
            inf_ratio = inf_count / total_cells
            quality_metrics["inf_ratio"] = inf_ratio

        dtype_counts = data.dtypes.value_counts()
        quality_metrics["dtype_distribution"] = dict(dtype_counts)
        return quality_metrics

    def _handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """处理缺失值"""
        data = data.copy()
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            median_val = data[col].median()
            data[col] = data[col].fillna(median_val)

        categorical_columns = data.select_dtypes(include=["object"]).columns
        for col in categorical_columns:
            mode_val = data[col].mode()
            if len(mode_val) > 0:
                data[col] = data[col].fillna(mode_val[0])
        return data

    def _optimize_dtypes(self, data: pd.DataFrame) -> pd.DataFrame:
        """优化数据类型"""
        data = data.copy()
        for col in data.select_dtypes(include=[np.float64]).columns:
            data[col] = pd.to_numeric(data[col], downcast="float")
        for col in data.select_dtypes(include=[np.int64]).columns:
            data[col] = pd.to_numeric(data[col], downcast="integer")
        return data

    def _handle_outliers(self, data: pd.DataFrame, method: str = "iqr") -> pd.DataFrame:
        """处理异常值"""
        data = data.copy()
        numeric_columns = data.select_dtypes(include=[np.number]).columns

        for col in numeric_columns:
            if method == "iqr":
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                data[col] = data[col].clip(lower_bound, upper_bound)
            elif method == "zscore":
                mean_val = data[col].mean()
                std_val = data[col].std()
                data[col] = data[col].clip(
                    mean_val - 3 * std_val, mean_val + 3 * std_val
                )
        return data

    def _normalize_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """特征标准化"""
        from sklearn.preprocessing import StandardScaler  # 从CPU版本导入

        numeric_columns = data.select_dtypes(include=[np.number]).columns
        feature_data = data[numeric_columns]

        if feature_data.empty:
            return data

        scaler = StandardScaler()
        normalized_features = scaler.fit_transform(feature_data)
        normalized_df = pd.DataFrame(
            normalized_features, columns=feature_data.columns, index=data.index
        )

        self.scalers["standard_scaler"] = scaler

        result = data.copy()
        for col in normalized_df.columns:
            result[f"{col}_normalized"] = normalized_df[col].values
        return result

    def _calculate_rsi_cpu(self, prices: pd.Series) -> float:
        """CPU计算RSI"""
        delta = prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = (
            gain.rolling(window=14, min_periods=1).mean().iloc[-1]
        )  # Ensure min_periods
        avg_loss = (
            loss.rolling(window=14, min_periods=1).mean().iloc[-1]
        )  # Ensure min_periods

        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi)

    def _calculate_macd_cpu(self, prices: pd.Series) -> Dict[str, float]:
        """CPU计算MACD"""
        ema_12 = prices.ewm(span=12, adjust=False).mean()
        ema_26 = prices.ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()

        return {
            "macd": float(macd_line.iloc[-1]),
            "macd_signal": float(signal_line.iloc[-1]),
            "macd_histogram": float(macd_line.iloc[-1] - signal_line.iloc[-1]),
        }

    def _calculate_bollinger_cpu(self, prices: pd.Series) -> Dict[str, float]:
        """CPU计算布林带"""
        sma = prices.rolling(window=20).mean()
        std = prices.rolling(window=20).std()

        upper_band = sma + (2 * std)
        lower_band = sma - (2 * std)

        return {
            "bb_upper": float(upper_band.iloc[-1]),
            "bb_middle": float(sma.iloc[-1]),
            "bb_lower": float(lower_band.iloc[-1]),
        }
