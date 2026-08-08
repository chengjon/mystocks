#!/usr/bin/env python3
"""
GPU加速的数据处理器
使用cuDF和cuPy实现高性能数据处理
支持大规模金融数据的并行处理和实时分析
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

import cudf
import cupy as cp
import numpy as np
import pandas as pd

from ._data_processor_gpu_batch import create_batch_processing_bindings

# 尝试导入 cuML 库
try:
    from cuml.decomposition import PCA
    from cuml.feature_selection import SelectKBest
    from cuml.preprocessing import StandardScaler

    CUML_AVAILABLE = True
except ImportError:
    CUML_AVAILABLE = False
    # 使用 None 作为占位符
    StandardScaler = None
    SelectKBest = None
    PCA = None


@dataclass
class ProcessingResult:
    """数据处理结果"""

    processed_data: pd.DataFrame
    processing_time: float
    memory_usage: Dict[str, float]
    gpu_accelerated: bool
    quality_metrics: Dict[str, float]
    data_shape: Tuple[int, int]


@dataclass
class BatchProcessingResult:
    """批量数据处理结果"""

    results: List[ProcessingResult]
    total_time: float
    avg_processing_time: float
    total_records_processed: int
    gpu_utilization: float


class GPUDataProcessor:
    """GPU加速的数据处理器"""

    def __init__(self, gpu_enabled: bool = True, n_jobs: int = 1, chunk_size: int = 10000):
        self.gpu_enabled = gpu_enabled
        self.n_jobs = n_jobs
        self.chunk_size = chunk_size
        self.logger = logging.getLogger(__name__)
        self.scalers = {}
        self.preprocessing_pipeline = {}

        # 初始化GPU内存池
        if self.gpu_enabled:
            cp.cuda.set_allocator(cp.cuda.MemoryPool())

    def load_and_preprocess(self, data: pd.DataFrame) -> ProcessingResult:
        """加载和预处理数据"""
        start_time = time.time()

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

        processing_time = time.time() - start_time

        # 计算内存使用
        memory_usage = {
            "original_memory": data.memory_usage(deep=True).sum(),
            "processed_memory": processed_data.memory_usage(deep=True).sum(),
            "compression_ratio": data.memory_usage(deep=True).sum() / processed_data.memory_usage(deep=True).sum(),
        }

        return ProcessingResult(
            processed_data=processed_data,
            processing_time=processing_time,
            memory_usage=memory_usage,
            gpu_accelerated=self.gpu_enabled,
            quality_metrics=quality_metrics,
            data_shape=processed_data.shape,
        )

    def _check_data_quality(self, data: pd.DataFrame) -> Dict[str, float]:
        """检查数据质量"""
        quality_metrics = {}

        # 检查缺失值
        missing_values = data.isnull().sum()
        total_cells = data.shape[0] * data.shape[1]
        missing_ratio = missing_values.sum() / total_cells
        quality_metrics["missing_ratio"] = missing_ratio

        # 检查重复值
        duplicate_ratio = data.duplicated().sum() / len(data)
        quality_metrics["duplicate_ratio"] = duplicate_ratio

        # 检查数据一致性
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            # 检查是否有无穷大值
            inf_count = np.isinf(data[numeric_columns]).sum().sum()
            inf_ratio = inf_count / total_cells
            quality_metrics["inf_ratio"] = inf_ratio

        # 检查数据类型分布
        dtype_counts = data.dtypes.value_counts()
        quality_metrics["dtype_distribution"] = dict(dtype_counts)

        return quality_metrics

    def _handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """处理缺失值"""
        if self.gpu_enabled:
            df_gpu = cudf.DataFrame(data)

            # 数值列：用中位数填充
            numeric_columns = df_gpu.select_dtypes(include=["float64", "int64"]).columns
            for col in numeric_columns:
                median_val = df_gpu[col].median()
                df_gpu[col] = df_gpu[col].fillna(median_val)

            # 分类列：用众数填充
            categorical_columns = df_gpu.select_dtypes(include=["object"]).columns
            for col in categorical_columns:
                mode_val = df_gpu[col].mode()
                if len(mode_val) > 0:
                    df_gpu[col] = df_gpu[col].fillna(mode_val[0])

            return df_gpu.to_pandas()
        else:
            data = data.copy()
            # 数值列：用中位数填充
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                median_val = data[col].median()
                data[col] = data[col].fillna(median_val)

            # 分类列：用众数填充
            categorical_columns = data.select_dtypes(include=["object"]).columns
            for col in categorical_columns:
                mode_val = data[col].mode()
                if len(mode_val) > 0:
                    data[col] = data[col].fillna(mode_val[0])

            return data

    def _optimize_dtypes(self, data: pd.DataFrame) -> pd.DataFrame:
        """优化数据类型"""
        if self.gpu_enabled:
            df_gpu = cudf.DataFrame(data)

            # 数值列类型优化
            for col in df_gpu.select_dtypes(include=["float64"]).columns:
                df_gpu[col] = df_gpu[col].astype("float32")

            for col in df_gpu.select_dtypes(include=["int64"]).columns:
                df_gpu[col] = df_gpu[col].astype("int32")

            return df_gpu.to_pandas()
        else:
            data = data.copy()
            # 数值列类型优化
            for col in data.select_dtypes(include=[np.float64]).columns:
                data[col] = pd.to_numeric(data[col], downcast="float")

            for col in data.select_dtypes(include=[np.int64]).columns:
                data[col] = pd.to_numeric(data[col], downcast="integer")

            return data

    def _handle_outliers(self, data: pd.DataFrame, method: str = "iqr") -> pd.DataFrame:
        """处理异常值"""
        if self.gpu_enabled:
            df_gpu = cudf.DataFrame(data)

            numeric_columns = df_gpu.select_dtypes(include=["float32", "int32"]).columns

            for col in numeric_columns:
                if method == "iqr":
                    Q1 = df_gpu[col].quantile(0.25)
                    Q3 = df_gpu[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR

                    df_gpu[col] = df_gpu[col].clip(lower_bound, upper_bound)

                elif method == "zscore":
                    mean_val = df_gpu[col].mean()
                    std_val = df_gpu[col].std()
                    (df_gpu[col] - mean_val) / std_val
                    df_gpu[col] = df_gpu[col].abs().clip(3, upper=None)  # 限制z-score在3以内

            return df_gpu.to_pandas()
        else:
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
                    (data[col] - mean_val) / std_val
                    data[col] = data[col].clip(mean_val - 3 * std_val, mean_val + 3 * std_val)

            return data

    def _normalize_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """特征标准化"""
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        feature_data = data[numeric_columns]

        if self.gpu_enabled:
            df_gpu = cudf.DataFrame(feature_data)
            scaler = StandardScaler()
            normalized_features = scaler.fit_transform(df_gpu)
            normalized_df = cudf.DataFrame(normalized_features, columns=df_gpu.columns)

            # 存储scaler用于后续使用
            self.scalers["standard_scaler"] = scaler

            result = data.copy()
            for col in normalized_df.columns:
                result[f"{col}_normalized"] = normalized_df[col].to_numpy()
        else:
            scaler = StandardScaler()
            normalized_features = scaler.fit_transform(feature_data)
            normalized_df = pd.DataFrame(normalized_features, columns=feature_data.columns)

            # 存储scaler用于后续使用
            self.scalers["standard_scaler"] = scaler

            result = data.copy()
            for col in normalized_df.columns:
                result[f"{col}_normalized"] = normalized_df[col].values

        return result

    def parallel_processing(self, data_list: List[pd.DataFrame]) -> BatchProcessingResult:
        """并行数据处理"""
        start_time = time.time()
        results = []

        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=self.n_jobs) as executor:
            futures = [executor.submit(self.load_and_preprocess, data) for data in data_list]

            for future in as_completed(futures):
                try:
                    result = future.result(timeout=300)
                    results.append(result)
                except Exception as e:
                    self.logger.error("并行处理失败: %s", e)

        total_time = time.time() - start_time
        avg_processing_time = total_time / len(results) if results else 0
        total_records_processed = sum(result.data_shape[0] for result in results)

        return BatchProcessingResult(
            results=results,
            total_time=total_time,
            avg_processing_time=avg_processing_time,
            total_records_processed=total_records_processed,
            gpu_utilization=self._estimate_gpu_utilization(),
        )

    def _estimate_gpu_utilization(self) -> float:
        """估算GPU利用率"""
        if self.gpu_enabled:
            try:
                # 获取GPU内存使用情况
                memory_info = cp.cuda.mem_get_info()
                used_memory = memory_info[1] - memory_info[0]
                total_memory = memory_info[1]
                return used_memory / total_memory
            except Exception:
                return 0.0
        else:
            return 0.0

    def real_time_data_streaming(
        self, data_stream: Callable[[], pd.DataFrame], window_size: int = 1000
    ) -> ProcessingResult:
        """实时数据流处理"""
        window_data = []
        processing_times = []

        for _ in range(window_size):
            try:
                # 获取新的数据点
                new_data = data_stream()
                window_data.append(new_data)

                # 每处理一定数量数据点后进行批量处理
                if len(window_data) >= 100:
                    batch_result = self.process_real_time_batch(window_data)
                    processing_times.append(batch_result.processing_time)

                    # 清空窗口
                    window_data = []

            except Exception as e:
                self.logger.error("实时数据处理错误: %s", e)
                continue

        # 处理剩余数据
        if window_data:
            batch_result = self.process_real_time_batch(window_data)
            processing_times.append(batch_result.processing_time)

        # 计算平均处理时间
        avg_processing_time = np.mean(processing_times) if processing_times else 0

        return ProcessingResult(
            processed_data=pd.DataFrame(),  # 简化处理
            processing_time=avg_processing_time,
            memory_usage={},
            gpu_accelerated=self.gpu_enabled,
            quality_metrics={},
            data_shape=(0, 0),
        )

    def process_real_time_batch(self, batch_data: List[pd.DataFrame]) -> ProcessingResult:
        """处理实时数据批次"""
        start_time = time.time()

        # 合并批次数据
        combined_data = pd.concat(batch_data, ignore_index=True)

        # 使用GPU处理
        result = self.load_and_preprocess(combined_data)

        processing_time = time.time() - start_time
        result.processing_time = processing_time

        return result

    def feature_engineering_pipeline(self, data: pd.DataFrame) -> ProcessingResult:
        """特征工程流水线"""
        start_time = time.time()

        # 1. 基础预处理
        preprocessed_data = self.load_and_preprocess(data).processed_data

        # 2. 特征选择
        selected_features = self.feature_selection(preprocessed_data)

        # 3. 降维处理
        reduced_data = self.dimensionality_reduction(preprocessed_data[selected_features])

        # 4. 特征重要性分析
        importance_scores = self.feature_importance_analysis(preprocessed_data[selected_features])

        processing_time = time.time() - start_time

        return ProcessingResult(
            processed_data=reduced_data,
            processing_time=processing_time,
            memory_usage={},
            gpu_accelerated=self.gpu_enabled,
            quality_metrics=importance_scores,
            data_shape=reduced_data.shape,
        )

    def feature_selection(self, data: pd.DataFrame, k: int = 50) -> List[str]:
        """特征选择"""
        feature_columns = [col for col in data.columns if col != "target" and "normalized" in col]

        if len(feature_columns) == 0:
            return []

        X = data[feature_columns]
        y = data["target"] if "target" in data.columns else data["close"]  # 默认使用收盘价作为目标

        if self.gpu_enabled and CUML_AVAILABLE and SelectKBest is not None:
            X_gpu = cudf.DataFrame(X)
            y_gpu = cudf.Series(y)

            # 使用互信息进行特征选择
            selector = SelectKBest(k=k)
            selector.fit_transform(X_gpu, y_gpu)

            # 获取选中的特征索引
            selected_indices = selector.get_support(indices=True)
            selected_features = [feature_columns[i] for i in selected_indices]
        else:
            from sklearn.feature_selection import SelectKBest as SklearnSelectKBest

            selector = SklearnSelectKBest(k=k)
            selector.fit_transform(X, y)
            selected_indices = selector.get_support(indices=True)
            selected_features = [feature_columns[i] for i in selected_indices]

        return selected_features

    def dimensionality_reduction(self, data: pd.DataFrame, n_components: int = 20) -> pd.DataFrame:
        """降维处理"""
        if self.gpu_enabled and CUML_AVAILABLE and PCA is not None:
            df_gpu = cudf.DataFrame(data)

            # 使用PCA进行降维
            pca = PCA(n_components=min(n_components, len(data.columns)))
            reduced_features = pca.fit_transform(df_gpu)

            # 创建降维后的DataFrame
            reduced_df = cudf.DataFrame(
                reduced_features,
                columns=[f"pca_{i}" for i in range(reduced_features.shape[1])],
            )

            return reduced_df.to_pandas()
        else:
            from sklearn.decomposition import PCA as SklearnPCA

            pca = SklearnPCA(n_components=min(n_components, len(data.columns)))
            reduced_features = pca.fit_transform(data)

            reduced_df = pd.DataFrame(
                reduced_features,
                columns=[f"pca_{i}" for i in range(reduced_features.shape[1])],
            )

            return reduced_df

    def feature_importance_analysis(self, data: pd.DataFrame) -> Dict[str, float]:
        """特征重要性分析"""
        feature_columns = [col for col in data.columns if col != "target"]
        if len(feature_columns) == 0:
            return {}

        X = data[feature_columns]
        y = data["target"] if "target" in data.columns else data["close"]

        if self.gpu_enabled:
            from cuml.ensemble import RandomForestRegressor

            X_gpu = cudf.DataFrame(X)
            y_gpu = cudf.Series(y)

            model = RandomForestRegressor(n_estimators=100)
            model.fit(X_gpu, y_gpu)

            # 获取特征重要性
            importances = model.feature_importances_
            importance_dict = dict(zip(feature_columns, importances))
        else:
            from sklearn.ensemble import RandomForestRegressor

            model = RandomForestRegressor(n_estimators=100)
            model.fit(X, y)

            importances = model.feature_importances_
            importance_dict = dict(zip(feature_columns, importances))

        return importance_dict

    def time_series_processing(self, data: pd.DataFrame, frequency: str = "D") -> ProcessingResult:
        """时间序列数据处理"""
        start_time = time.time()

        # 转换时间索引
        if "date" not in data.columns:
            data["date"] = pd.to_datetime(data.index)

        data = data.set_index("date")

        # 重采样
        if self.gpu_enabled:
            df_gpu = cudf.DataFrame(data)
            resampled_data = df_gpu.resample(frequency).agg(
                {
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum",
                }
            )
        else:
            resampled_data = data.resample(frequency).agg(
                {
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum",
                }
            )

        # 处理缺失值
        resampled_data = resampled_data.fillna(method="ffill")

        processing_time = time.time() - start_time

        return ProcessingResult(
            processed_data=resampled_data,
            processing_time=processing_time,
            memory_usage={},
            gpu_accelerated=self.gpu_enabled,
            quality_metrics={},
            data_shape=resampled_data.shape,
        )

    def anomaly_detection(self, data: pd.DataFrame, method: str = "isolation_forest") -> pd.DataFrame:
        """异常检测"""
        if self.gpu_enabled:
            from cuml.ensemble import IsolationForest

            feature_columns = [col for col in data.columns if col not in ["date", "target"]]
            if len(feature_columns) == 0:
                return data

            df_gpu = cudf.DataFrame(data[feature_columns])

            # 使用Isolation Forest进行异常检测
            iso_forest = IsolationForest(contamination=0.1)
            anomaly_labels = iso_forest.fit_predict(df_gpu)

            # 标记异常
            result_data = data.copy()
            result_data["anomaly"] = anomaly_labels

            return result_data
        else:
            from sklearn.ensemble import IsolationForest

            feature_columns = [col for col in data.columns if col not in ["date", "target"]]
            if len(feature_columns) == 0:
                return data

            iso_forest = IsolationForest(contamination=0.1)
            anomaly_labels = iso_forest.fit_predict(data[feature_columns])

            result_data = data.copy()
            result_data["anomaly"] = anomaly_labels

            return result_data

    def market_regime_detection(self, data: pd.DataFrame) -> pd.DataFrame:
        """市场状态检测"""
        if self.gpu_enabled:
            from cuml.cluster import KMeans

            # 使用收益率和波动率作为特征
            returns = data["close"].pct_change()
            volatility = returns.rolling(window=20).std()

            features = cudf.DataFrame({"return": returns, "volatility": volatility}).dropna()

            # 使用K-means聚类检测市场状态
            kmeans = KMeans(n_clusters=3)
            cluster_labels = kmeans.fit_predict(features)

            result_data = data.copy()
            result_data["market_regime"] = cluster_labels.reindex(data.index)

            return result_data
        else:
            from sklearn.cluster import KMeans

            returns = data["close"].pct_change()
            volatility = returns.rolling(window=20).std()

            features = pd.DataFrame({"return": returns, "volatility": volatility}).dropna()

            kmeans = KMeans(n_clusters=3)
            cluster_labels = kmeans.fit_predict(features)

            result_data = data.copy()
            result_data["market_regime"] = cluster_labels.reindex(data.index)

            return result_data

    def save_processing_pipeline(self, filepath: str):
        """保存处理流水线"""
        import joblib

        pipeline_data = {
            "scalers": self.scalers,
            "preprocessing_pipeline": self.preprocessing_pipeline,
            "gpu_enabled": self.gpu_enabled,
            "n_jobs": self.n_jobs,
            "chunk_size": self.chunk_size,
        }
        joblib.dump(pipeline_data, filepath)

    def load_processing_pipeline(self, filepath: str):
        """加载处理流水线"""
        import joblib

        pipeline_data = joblib.load(filepath)
        self.scalers = pipeline_data["scalers"]
        self.preprocessing_pipeline = pipeline_data["preprocessing_pipeline"]
        self.gpu_enabled = pipeline_data["gpu_enabled"]
        self.n_jobs = pipeline_data["n_jobs"]
        self.chunk_size = pipeline_data["chunk_size"]


BatchDataProcessor, benchmark_data_processing = create_batch_processing_bindings(GPUDataProcessor)


if __name__ == "__main__":
    # 示例使用
    import yfinance as yf

    # 获取示例数据
    data = yf.download("AAPL", start="2023-01-01", end="2024-01-01")

    # 创建数据处理器
    processor = GPUDataProcessor(gpu_enabled=True)

    # 数据处理
    result = processor.load_and_preprocess(data)

    print("数据处理完成:")
    print(f"处理时间: {result.processing_time:.2f}秒")
    print(f"数据形状: {result.data_shape}")
    print(f"内存压缩比: {result.memory_usage['compression_ratio']:.2f}x")

    # 基准测试
    benchmark_results = benchmark_data_processing(data)
    print(f"\nGPU加速性能提升: {benchmark_results['speedup']:.2f}x")
