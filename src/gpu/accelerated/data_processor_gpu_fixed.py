"""
GPU Data Processor with Memory Management Fix
修复内存泄漏问题的GPU数据处理器
"""

import logging
import os
import sys
import time

import pandas as pd
import psutil

# 延迟导入GPU模块，只有在需要时才导入
try:
    import cudf
    import cupy as cp

    CUML_AVAILABLE = True
except ImportError:
    CUML_AVAILABLE = False
    cp = None
    cudf = None

try:
    from cuml.decomposition import PCA
    from cuml.feature_selection import SelectKBest
    from cuml.preprocessing import StandardScaler

    CUML_FULL_AVAILABLE = True
except ImportError:
    CUML_FULL_AVAILABLE = False
    StandardScaler = None
    SelectKBest = None
    PCA = None

# 添加内存管理模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import Any, Dict, List

from src.gpu.accelerated.memory_management_fix import (
    memory_cleanup_decorator,
    memory_manager,
    optimize_dataframe_memory,
)
from src.gpu.data_processing_interfaces import IDataProcessor

logger = logging.getLogger(__name__)


class GPUDataProcessorFixed(IDataProcessor):
    """
    GPU加速的数据处理器实现 - 内存安全版本
    修复DataFrame内存泄漏问题，提供完整的内存管理
    """

    def __init__(self, gpu_enabled: bool = True, memory_threshold_mb: int = 500):
        self.memory_threshold = memory_threshold_mb
        self.logger = logging.getLogger(__name__)
        self.scalers = {}
        self.preprocessing_pipeline = {}
        self.processing_stats = {
            "total_processed": 0,
            "total_memory_freed": 0,
            "cleanup_count": 0,
            "mode": "unknown",
        }

        # 自动检测GPU可用性
        if gpu_enabled:
            self.gpu_enabled = self._check_gpu_availability()
        else:
            self.gpu_enabled = False

        if self.gpu_enabled:
            try:
                cp.cuda.set_allocator(cp.cuda.MemoryPool())
                self.processing_stats["mode"] = "gpu"
                self.logger.info(
                    "GPUDataProcessorFixed initialized with GPU enabled, " f"memory_threshold={memory_threshold_mb}MB"
                )
            except Exception as e:
                self.logger.warning("GPU initialization failed, falling back to CPU: %s", e)
                self.gpu_enabled = False
                self.processing_stats["mode"] = "cpu"
        else:
            self.processing_stats["mode"] = "cpu"
            self.logger.info(
                "GPUDataProcessorFixed initialized with CPU mode, " f"memory_threshold={memory_threshold_mb}MB"
            )

    def _check_gpu_availability(self) -> bool:
        """检查GPU是否可用"""
        if not CUML_AVAILABLE:
            self.logger.info("CuML not available, using CPU")
            return False

        if not CUML_FULL_AVAILABLE:
            self.logger.info("Full CuML not available, using CPU")
            return False

        try:
            # 尝试创建简单的GPU数组
            import cupy as cp

            x = cp.array([1, 2, 3])
            del x
            self.logger.info("GPU available and working")
            return True
        except Exception as e:
            self.logger.warning("GPU not available: %s", e)
            return False

    @memory_cleanup_decorator(threshold_mb=500)
    def load_and_preprocess(self, data: pd.DataFrame) -> Dict[str, Any]:
        """加载和预处理数据 (GPU实现) - 带内存管理"""
        if data is None or data.empty:
            raise ValueError("Input data cannot be None or empty")

        start_time = time.time()

        # 内存优化输入数据
        data = optimize_dataframe_memory(data)
        memory_manager.track_dataframe(data, "input_data")

        try:
            if self.gpu_enabled:
                # 转换为cuDF DataFrame
                df_gpu = cudf.DataFrame(data)

                # 数据质量检查
                quality_metrics = self._check_data_quality(df_gpu)

                # 处理缺失值
                cleaned_data = self._handle_missing_values(df_gpu)

                # 数据类型优化
                optimized_data = self._optimize_dtypes(cleaned_data)

                # 异常值处理
                final_data = self._handle_outliers(optimized_data)

                # 特征标准化
                processed_data = self._normalize_features(final_data)

                # 转换回pandas以返回
                result_df = processed_data.to_pandas()
            else:
                # CPU fallback
                result_df = self._cpu_preprocess(data)
                quality_metrics = self._check_cpu_data_quality(data)

            processing_time = time.time() - start_time

            # 计算内存使用
            memory_usage = self._calculate_memory_usage(data, result_df)

            # 更新统计信息
            self.processing_stats["total_processed"] += 1
            if "original_memory_cpu" in memory_usage:
                freed_memory = memory_usage["original_memory_cpu"] - memory_usage["processed_memory_cpu"]
                self.processing_stats["total_memory_freed"] += freed_memory

            # 清理临时变量
            del data
            if "df_gpu" in locals():
                del df_gpu

            memory_manager.cleanup_memory()

            return {
                "processed_data": result_df,
                "processing_time": processing_time,
                "memory_usage": memory_usage,
                "gpu_accelerated": self.gpu_enabled,
                "quality_metrics": quality_metrics,
                "data_shape": result_df.shape,
                "processing_stats": self.processing_stats.copy(),
            }

        except Exception as e:
            self.logger.error("Data preprocessing failed: %s", e)
            memory_manager.cleanup_memory(force=True)
            raise

    @memory_cleanup_decorator(threshold_mb=300)
    def process_batch(self, batch_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        GPU批量处理数据 - 带内存管理
        """
        if not batch_data:
            return []

        try:
            if self.gpu_enabled:
                # 转换为cuDF DataFrame
                df = cudf.DataFrame(batch_data)

                # GPU计算
                df["price_change"] = df["price"].pct_change()

                # 简化版: 假设volume_ma可以直接在当前批次内计算
                if "volume" in df.columns and len(df) >= 20:
                    df["volume_ma"] = df["volume"].rolling(window=20, min_periods=1).mean()
                else:
                    df["volume_ma"] = 0.0

                # 转回CPU并转换为字典列表
                result_df_pandas = df.to_pandas()
                processed_results = []
                for _, row in result_df_pandas.iterrows():
                    processed_results.append(
                        {
                            "stock_code": row.get("stock_code"),
                            "price": row.get("price"),
                            "volume": row.get("volume"),
                            "timestamp": row.get("timestamp"),
                            "price_change": row["price_change"] if pd.notna(row["price_change"]) else 0.0,
                            "volume_ma": row["volume_ma"] if pd.notna(row["volume_ma"]) else 0.0,
                        }
                    )

                # 清理GPU内存
                cp.cuda.Stream.null.synchronize()

            else:
                # CPU fallback
                df = pd.DataFrame(batch_data)
                df["price_change"] = df["price"].pct_change()
                if "volume" in df.columns and len(df) >= 20:
                    df["volume_ma"] = df["volume"].rolling(window=20, min_periods=1).mean()
                else:
                    df["volume_ma"] = 0.0

                processed_results = df.to_dict("records")

            return processed_results

        except Exception as e:
            self.logger.error("Batch processing failed: %s", e)
            raise
        finally:
            # 清理临时变量
            if "df" in locals():
                del df

    @memory_cleanup_decorator(threshold_mb=400)
    def compute_features(self, historical_data: List[Dict], feature_types: List[str]) -> Dict[str, float]:
        """
        GPU计算技术特征 - 带内存管理
        """
        if not historical_data:
            return {}

        try:
            df = pd.DataFrame(historical_data)
            if df.empty or "price" not in df.columns or len(df) < 20:
                self.logger.warning("Historical data is insufficient or empty for feature calculation.")
                return {}

            # 内存优化
            df = optimize_dataframe_memory(df)
            memory_manager.track_dataframe(df, "historical_data")

            features = {}

            if self.gpu_enabled:
                df_gpu = cudf.DataFrame(df)
                prices = df_gpu["price"]
                volumes = df_gpu["volume"] if "volume" in df_gpu.columns else cudf.Series(0, index=df_gpu.index)

                for feature_type in feature_types:
                    if feature_type == "sma_20":
                        features["sma_20"] = float(prices.rolling(window=20).mean().iloc[-1])
                    elif feature_type == "sma_50":
                        if len(df_gpu) >= 50:
                            features["sma_50"] = float(prices.rolling(window=50).mean().iloc[-1])
                        else:
                            features["sma_50"] = 0.0
                    elif feature_type == "rsi":
                        features["rsi"] = self._calculate_rsi_gpu(prices)
                    elif feature_type == "macd":
                        macd_values = self._calculate_macd_gpu(prices)
                        features.update(macd_values)
                    elif feature_type == "bollinger":
                        bb_values = self._calculate_bollinger_gpu(prices)
                        features.update(bb_values)
                    elif feature_type == "volume_ratio":
                        volume_ma = volumes.rolling(window=20).mean().iloc[-1]
                        current_volume = volumes.iloc[-1]
                        features["volume_ratio"] = float(current_volume / volume_ma) if volume_ma > 0 else 0.0
            else:
                # CPU fallback
                features = self._compute_features_cpu(df, feature_types)

            # 清理
            del df
            if "df_gpu" in locals():
                del df_gpu

            return features

        except Exception as e:
            self.logger.error("Feature computation failed: %s", e)
            raise

    def get_memory_stats(self) -> Dict[str, Any]:
        """获取内存统计信息"""
        process = psutil.Process()
        memory_info = process.memory_info()

        return {
            "rss_mb": memory_info.rss / 1024**2,
            "vms_mb": memory_info.vms / 1024**2,
            "percent": process.memory_percent(),
            "gpu_memory_mb": self._get_gpu_memory_usage() if self.gpu_enabled else 0,
            "total_processed": self.processing_stats["total_processed"],
            "total_memory_freed": self.processing_stats["total_memory_freed"],
            "cleanup_count": self.processing_stats["cleanup_count"],
        }

    def force_cleanup(self) -> Dict[str, Any]:
        """强制内存清理"""
        stats = memory_manager.cleanup_memory(force=True)
        self.processing_stats["cleanup_count"] = memory_manager.cleanup_count
        return stats

    # --- 辅助方法 ---

    def _calculate_memory_usage(self, original: pd.DataFrame, processed: pd.DataFrame) -> Dict[str, Any]:
        """计算内存使用情况"""
        return {
            "original_memory_cpu": original.memory_usage(deep=True).sum() / 1024**2,
            "processed_memory_cpu": processed.memory_usage(deep=True).sum() / 1024**2,
            "compression_ratio": (
                original.memory_usage(deep=True).sum() / processed.memory_usage(deep=True).sum()
                if processed.memory_usage(deep=True).sum() > 0
                else 1.0
            ),
        }

    def _get_gpu_memory_usage(self) -> float:
        """获取GPU内存使用情况"""
        try:
            if cp.cuda.is_available():
                return cp.cuda.mem_get_info()[1] / 1024**2  # 总内存
            return 0.0
        except Exception:
            return 0.0

    def _cpu_preprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        """CPU预处理回退方案"""
        # 基本的CPU数据预处理
        result = data.copy()

        # 处理缺失值
        result = result.fillna(method="ffill").fillna(method="bfill")

        # 数据类型优化
        result = optimize_dataframe_memory(result)

        return result

    def _check_cpu_data_quality(self, data: pd.DataFrame) -> Dict[str, float]:
        """CPU数据质量检查"""
        quality_metrics = {}

        missing_values = data.isnull().sum()
        total_cells = data.shape[0] * data.shape[1]
        missing_ratio = missing_values.sum() / total_cells
        quality_metrics["missing_ratio"] = missing_ratio

        duplicate_ratio = data.duplicated().sum() / len(data)
        quality_metrics["duplicate_ratio"] = duplicate_ratio

        return quality_metrics

    # 保持原有的GPU辅助方法
    def _check_data_quality(self, data: cudf.DataFrame) -> Dict[str, float]:
        """检查数据质量"""
        quality_metrics = {}

        missing_values = data.isnull().sum()
        total_cells = data.shape[0] * data.shape[1]
        missing_ratio = missing_values.sum() / total_cells
        quality_metrics["missing_ratio"] = missing_ratio.item() if hasattr(missing_ratio, "item") else missing_ratio

        duplicate_ratio = data.duplicated().sum() / len(data)
        quality_metrics["duplicate_ratio"] = (
            duplicate_ratio.item() if hasattr(duplicate_ratio, "item") else duplicate_ratio
        )

        numeric_columns = data.select_dtypes(include=["float", "int"]).columns
        if len(numeric_columns) > 0:
            inf_count = data[numeric_columns].applymap(lambda x: x == cp.inf or x == -cp.inf).sum().sum()
            inf_ratio = inf_count / total_cells
            quality_metrics["inf_ratio"] = inf_ratio.item() if hasattr(inf_ratio, "item") else inf_ratio

        dtype_counts = data.dtypes.value_counts()
        quality_metrics["dtype_distribution"] = {str(k): int(v) for k, v in dtype_counts.items()}

        return quality_metrics

    def _handle_missing_values(self, data: cudf.DataFrame) -> cudf.DataFrame:
        """处理缺失值"""
        df_gpu = data.copy()

        # 使用前向填充，后向填充
        for col in df_gpu.columns:
            if df_gpu[col].dtype in ["float32", "float64", "int32", "int64"]:
                df_gpu[col] = df_gpu[col].fillna(method="ffill").fillna(method="bfill")
            else:
                df_gpu[col] = df_gpu[col].fillna("")

        return df_gpu

    def _optimize_dtypes(self, data: cudf.DataFrame) -> cudf.DataFrame:
        """优化数据类型"""
        df = data.copy()

        # 数值类型优化
        for col in df.select_dtypes(include=["int64"]).columns:
            col_min = df[col].min()
            col_max = df[col].max()

            if col_min >= 0:
                if col_max < 255:
                    df[col] = df[col].astype("int8")
                elif col_max < 65535:
                    df[col] = df[col].astype("int16")
                elif col_max < 2147483647:
                    df[col] = df[col].astype("int32")
            else:
                if col_min >= -128 and col_max < 128:
                    df[col] = df[col].astype("int8")
                elif col_min >= -32768 and col_max < 32768:
                    df[col] = df[col].astype("int16")
                elif col_min >= -2147483648 and col_max < 2147483648:
                    df[col] = df[col].astype("int32")

        # 浮点类型优化
        for col in df.select_dtypes(include=["float64"]).columns:
            df[col] = df[col].astype("float32")

        return df

    def _handle_outliers(self, data: cudf.DataFrame) -> cudf.DataFrame:
        """处理异常值"""
        df = data.copy()

        # 使用IQR方法检测和处理异常值
        numeric_cols = df.select_dtypes(include=["float32", "float64"]).columns

        for col in numeric_cols:
            if len(df) > 10:  # 只有足够的数据点才处理异常值
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1

                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                # 将异常值钳制到边界内
                df[col] = df[col].clip(lower_bound, upper_bound)

        return df

    def _normalize_features(self, data: cudf.DataFrame) -> cudf.DataFrame:
        """特征标准化"""
        df = data.copy()

        # 数值列标准化
        numeric_cols = df.select_dtypes(include=["float32", "float64", "int32", "int64"]).columns

        for col in numeric_cols:
            if df[col].std() > 0:  # 只有标准差大于0才进行标准化
                mean = df[col].mean()
                std = df[col].std()
                df[col] = (df[col] - mean) / std

        return df

    # GPU特定计算方法
    def _calculate_rsi_gpu(self, prices: cudf.Series, period: int = 14) -> float:
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1])

    def _calculate_macd_gpu(
        self, prices: cudf.Series, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Dict[str, float]:
        """计算MACD指标"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line

        return {
            "macd": float(macd_line.iloc[-1]),
            "macd_signal": float(signal_line.iloc[-1]),
            "macd_histogram": float(histogram.iloc[-1]),
        }

    def _calculate_bollinger_gpu(self, prices: cudf.Series, period: int = 20, std_dev: int = 2) -> Dict[str, float]:
        """计算布林带指标"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)

        return {
            "bb_upper": float(upper_band.iloc[-1]),
            "bb_middle": float(sma.iloc[-1]),
            "bb_lower": float(lower_band.iloc[-1]),
        }

    def _compute_features_cpu(self, df: pd.DataFrame, feature_types: List[str]) -> Dict[str, float]:
        """CPU特征计算回退方案"""
        features = {}

        if "price" not in df.columns:
            return features

        prices = df["price"]
        volumes = df.get("volume", pd.Series(0, index=df.index))

        for feature_type in feature_types:
            if feature_type == "sma_20":
                if len(df) >= 20:
                    features["sma_20"] = prices.rolling(window=20).mean().iloc[-1]
                else:
                    features["sma_20"] = 0.0
            elif feature_type == "sma_50":
                if len(df) >= 50:
                    features["sma_50"] = prices.rolling(window=50).mean().iloc[-1]
                else:
                    features["sma_50"] = 0.0
            elif feature_type == "volume_ratio":
                if len(df) >= 20:
                    volume_ma = volumes.rolling(window=20).mean().iloc[-1]
                    current_volume = volumes.iloc[-1]
                    features["volume_ratio"] = float(current_volume / volume_ma) if volume_ma > 0 else 0.0
                else:
                    features["volume_ratio"] = 0.0

        return features
