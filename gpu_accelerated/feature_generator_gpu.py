#!/usr/bin/env python3
"""
GPU加速的特征生成器
使用cuDF和cuPy实现高性能特征工程
支持大规模金融数据的并行特征计算
"""

import time
import numpy as np
import pandas as pd
import cupy as cp
import cudf
from cuml.feature_extraction import FeatureHasher
from cuml.preprocessing import StandardScaler, MinMaxScaler
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

@dataclass
class FeatureResult:
    """特征计算结果"""
    features: pd.DataFrame
    feature_names: List[str]
    calculation_time: float
    memory_usage: Dict[str, float]
    gpu_accelerated: bool
    feature_quality: Dict[str, float]

@dataclass
class BatchFeatureResult:
    """批量特征计算结果"""
    results: List[FeatureResult]
    total_time: float
    avg_features_per_stock: float
    gpu_memory_utilization: float

class GPUFeatureGenerator:
    """GPU加速的特征生成器"""

    def __init__(self, gpu_enabled: bool = True, n_jobs: int = 1):
        self.gpu_enabled = gpu_enabled
        self.n_jobs = n_jobs
        self.feature_cache = {}
        self.logger = logging.getLogger(__name__)

        # 预定义的特征配置
        self.feature_config = {
            'technical': {
                'indicators': ['sma', 'ema', 'rsi', 'macd', 'bollinger', 'stochastic'],
                'windows': [5, 10, 20]
            },
            'statistical': {
                'metrics': ['z_score', 'percentile', 'skewness', 'kurtosis'],
                'windows': [10, 20, 50]
            },
            'momentum': {
                'indicators': ['roc', 'momentum', 'trix', 'cci'],
                'windows': [5, 10, 15]
            },
            'volatility': {
                'indicators': ['atr', 'standard_deviation', 'volatility_ratio'],
                'windows': [10, 20, 30]
            }
        }

    def generate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成技术指标特征（GPU加速）"""
        start_time = time.time()

        # 转换为cuDF DataFrame
        df_gpu = cudf.DataFrame(data) if self.gpu_enabled else data.copy()

        # 基本价格数据
        prices = df_gpu['close']
        high = df_gpu['high']
        low = df_gpu['low']
        volume = df_gpu['volume']

        # 移动平均线
        for window in [5, 10, 20]:
            df_gpu[f'sma_{window}'] = prices.rolling(window=window).mean()
            df_gpu[f'ema_{window}'] = prices.ewm(span=window).mean()

        # RSI
        df_gpu['rsi'] = self._calculate_rsi_gpu(prices)

        # MACD
        ema_12 = prices.ewm(span=12).mean()
        ema_26 = prices.ewm(span=26).mean()
        df_gpu['macd'] = ema_12 - ema_26
        df_gpu['macd_signal'] = df_gpu['macd'].ewm(span=9).mean()
        df_gpu['macd_histogram'] = df_gpu['macd'] - df_gpu['macd_signal']

        # 布林带
        sma_20 = prices.rolling(window=20).mean()
        std_20 = prices.rolling(window=20).std()
        df_gpu['bb_upper'] = sma_20 + (std_20 * 2)
        df_gpu['bb_lower'] = sma_20 - (std_20 * 2)
        df_gpu['bb_width'] = df_gpu['bb_upper'] - df_gpu['bb_lower']
        df_gpu['bb_position'] = (prices - df_gpu['bb_lower']) / (df_gpu['bb_upper'] - df_gpu['bb_lower'])

        # Stochastic指标
        low_14 = low.rolling(window=14).min()
        high_14 = high.rolling(window=14).max()
        df_gpu['stochastic_k'] = 100 * ((prices - low_14) / (high_14 - low_14))
        df_gpu['stochastic_d'] = df_gpu['stochastic_k'].rolling(window=3).mean()

        # 成交量指标
        df_gpu['volume_sma'] = volume.rolling(window=20).mean()
        df_gpu['volume_ratio'] = volume / df_gpu['volume_sma']

        # 计算时间
        calculation_time = time.time() - start_time

        # 转换回Pandas（如果需要）
        result = df_gpu.to_pandas() if self.gpu_enabled else df_gpu

        self.logger.info(f"技术指标生成完成，耗时: {calculation_time:.2f}秒")

        return result

    def _calculate_rsi_gpu(self, prices: cudf.Series, period: int = 14) -> cudf.Series:
        """GPU加速的RSI计算"""
        delta = prices.diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def generate_statistical_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成统计特征（GPU加速）"""
        start_time = time.time()

        df_gpu = cudf.DataFrame(data) if self.gpu_enabled else data.copy()
        prices = df_gpu['close']

        # Z-Score标准化
        for window in [10, 20, 50]:
            rolling_mean = prices.rolling(window=window).mean()
            rolling_std = prices.rolling(window=window).std()
            df_gpu[f'z_score_{window}'] = (prices - rolling_mean) / rolling_std

        # 百分位排名
        for window in [20, 50]:
            df_gpu[f'percentile_{window}'] = prices.rolling(window=window).rank(pct=True)

        # 偏度和峰度
        for window in [20, 50]:
            df_gpu[f'skewness_{window}'] = prices.rolling(window=window).skew()
            df_gpu[f'kurtosis_{window}'] = prices.rolling(window=window).kurt()

        # 价格变化统计
        returns = prices.pct_change()
        df_gpu['returns_mean'] = returns.rolling(window=20).mean()
        df_gpu['returns_std'] = returns.rolling(window=20).std()
        df_gpu['returns_skew'] = returns.rolling(window=20).skew()
        df_gpu['returns_kurt'] = returns.rolling(window=20).kurt()

        calculation_time = time.time() - start_time

        result = df_gpu.to_pandas() if self.gpu_enabled else df_gpu

        self.logger.info(f"统计特征生成完成，耗时: {calculation_time:.2f}秒")

        return result

    def generate_momentum_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成动量特征（GPU加速）"""
        start_time = time.time()

        df_gpu = cudf.DataFrame(data) if self.gpu_enabled else data.copy()
        prices = df_gpu['close']

        # ROC (Rate of Change)
        for window in [5, 10, 15]:
            df_gpu[f'roc_{window}'] = prices.pct_change(window)

        # 动量指标
        for window in [5, 10, 15]:
            df_gpu[f'momentum_{window}'] = prices - prices.shift(window)

        # TRIX指标
        ema_1 = prices.ewm(span=3).mean()
        ema_2 = ema_1.ewm(span=3).mean()
        ema_3 = ema_2.ewm(span=3).mean()
        df_gpu['trix'] = ema_3.pct_change()

        # CCI指标
        tp = (df_gpu['high'] + df_gpu['low'] + df_gpu['close']) / 3
        sma_tp = tp.rolling(window=20).mean()
        mad = tp.rolling(window=20).apply(lambda x: np.abs(x - x.mean()).mean())
        df_gpu['cci'] = (tp - sma_tp) / (0.015 * mad)

        calculation_time = time.time() - start_time

        result = df_gpu.to_pandas() if self.gpu_enabled else df_gpu

        self.logger.info(f"动量特征生成完成，耗时: {calculation_time:.2f}秒")

        return result

    def generate_volatility_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成波动率特征（GPU加速）"""
        start_time = time.time()

        df_gpu = cudf.DataFrame(data) if self.gpu_enabled else data.copy()
        prices = df_gpu['close']
        high = df_gpu['high']
        low = df_gpu['low']

        # ATR (Average True Range)
        tr1 = high - low
        tr2 = abs(high - df_gpu['close'].shift(1))
        tr3 = abs(low - df_gpu['close'].shift(1))
        tr = cp.maximum([tr1, tr2, tr3], axis=0) if self.gpu_enabled else pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df_gpu['atr'] = cudf.Series(tr).rolling(window=14).mean() if self.gpu_enabled else pd.Series(tr).rolling(window=14).mean()

        # 标准差波动率
        for window in [10, 20, 30]:
            df_gpu[f'volatility_{window}'] = prices.pct_change().rolling(window=window).std()

        # 波动率比率
        df_gpu['volatility_ratio'] = df_gpu['volatility_10'] / df_gpu['volatility_20']

        # Parkinson波动率
        parkinson_vol = cp.sqrt((1/(4*cp.log(2))) * cp.sum(cp.square(cp.log(high/low)))) if self.gpu_enabled else np.sqrt((1/(4*np.log(2))) * np.sum(np.square(np.log(high/low))))
        df_gpu['parkinson_volatility'] = parkinson_vol.rolling(window=20).mean()

        calculation_time = time.time() - start_time

        result = df_gpu.to_pandas() if self.gpu_enabled else df_gpu

        self.logger.info(f"波动率特征生成完成，耗时: {calculation_time:.2f}秒")

        return result

    def generate_pattern_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成形态学特征（GPU加速）"""
        start_time = time.time()

        df_gpu = cudf.DataFrame(data) if self.gpu_enabled else data.copy()
        prices = df_gpu['close']
        high = df_gpu['high']
        low = df_gpu['low']

        # 支撑阻力位
        df_gpu['resistance'] = high.rolling(window=20).max()
        df_gpu['support'] = low.rolling(window=20).min()

        # 价格形态识别
        df_gpu['is_doji'] = self._detect_doji(prices, high, low)
        df_gpu['is_hammer'] = self._detect_hammer(prices, high, low)
        df_gpu['is_shooting_star'] = self._detect_shooting_star(prices, high, low)

        # 蜡烛图模式
        body_size = abs(prices - df_gpu['open'])
        total_range = high - low
        df_gpu['body_ratio'] = body_size / total_range
        df_gpu['upper_shadow'] = (high - cp.maximum(prices, df_gpu['open'])) if self.gpu_enabled else (high - np.maximum(prices, df_gpu['open']))
        df_gpu['lower_shadow'] = (cp.minimum(prices, df_gpu['open']) - low) if self.gpu_enabled else (np.minimum(prices, df_gpu['open']) - low)

        calculation_time = time.time() - start_time

        result = df_gpu.to_pandas() if self.gpu_enabled else df_gpu

        self.logger.info(f"形态学特征生成完成，耗时: {calculation_time:.2f}秒")

        return result

    def _detect_doji(self, prices: cudf.Series, high: cudf.Series, low: cudf.Series) -> cudf.Series:
        """识别十字星形态"""
        body_size = abs(prices - prices.shift(1))
        total_range = high - low
        return (body_size / total_range) < 0.1

    def _detect_hammer(self, prices: cudf.Series, high: cudf.Series, low: cudf.Series) -> cudf.Series:
        """识别锤子形态"""
        body_size = abs(prices - prices.shift(1))
        upper_shadow = high - prices
        lower_shadow = prices - low
        return (lower_shadow > 2 * body_size) & (upper_shadow < body_size)

    def _detect_shooting_star(self, prices: cudf.Series, high: cudf.Series, low: cudf.Series) -> cudf.Series:
        """识别射击之星形态"""
        body_size = abs(prices - prices.shift(1))
        upper_shadow = high - prices
        lower_shadow = prices - low
        return (upper_shadow > 2 * body_size) & (lower_shadow < body_size)

    def generate_all_features(self, data: pd.DataFrame) -> FeatureResult:
        """生成所有特征"""
        start_time = time.time()

        # 技术指标特征
        data_with_features = self.generate_technical_indicators(data)

        # 统计特征
        data_with_features = self.generate_statistical_features(data_with_features)

        # 动量特征
        data_with_features = self.generate_momentum_features(data_with_features)

        # 波动率特征
        data_with_features = self.generate_volatility_features(data_with_features)

        # 形态学特征
        data_with_features = self.generate_pattern_features(data_with_features)

        # 计算内存使用
        memory_usage = {
            'total_memory': data_with_features.memory_usage(deep=True).sum(),
            'feature_count': len(data_with_features.columns),
            'sample_count': len(data_with_features)
        }

        # 评估特征质量
        feature_quality = self._evaluate_feature_quality(data_with_features)

        calculation_time = time.time() - start_time

        return FeatureResult(
            features=data_with_features,
            feature_names=list(data_with_features.columns),
            calculation_time=calculation_time,
            memory_usage=memory_usage,
            gpu_accelerated=self.gpu_enabled,
            feature_quality=feature_quality
        )

    def _evaluate_feature_quality(self, data: pd.DataFrame) -> Dict[str, float]:
        """评估特征质量"""
        quality_metrics = {}

        # 计算特征的统计特性
        numeric_columns = data.select_dtypes(include=[np.number]).columns

        for col in numeric_columns:
            col_data = data[col].dropna()
            if len(col_data) > 0:
                # 计算特征的变化系数
                mean_val = col_data.mean()
                std_val = col_data.std()
                cv = std_val / mean_val if mean_val != 0 else 0

                # 计算特征的缺失率
                missing_rate = col_data.isnull().sum() / len(col_data)

                # 计算特征的波动性
                volatility = col_data.std()

                quality_metrics[col] = {
                    'coefficient_of_variation': cv,
                    'missing_rate': missing_rate,
                    'volatility': volatility,
                    'quality_score': 1.0 - missing_rate  # 简单的质量评分
                }

        return quality_metrics

    def batch_feature_generation(self, data_list: List[pd.DataFrame]) -> BatchFeatureResult:
        """批量特征生成"""
        start_time = time.time()

        results = []
        total_features = 0
        total_memory = 0

        for i, data in enumerate(data_list):
            try:
                result = self.generate_all_features(data)
                results.append(result)
                total_features += len(result.feature_names)
                total_memory += result.memory_usage['total_memory']

            except Exception as e:
                self.logger.error(f"批量特征生成第{i}个数据失败: {e}")
                continue

        total_time = time.time() - start_time
        avg_features_per_stock = total_features / len(results) if results else 0

        # 估算GPU内存利用率
        gpu_memory_utilization = total_memory / (8 * 1024 * 1024 * 1024) if self.gpu_enabled else 0  # 假设8GB GPU内存

        return BatchFeatureResult(
            results=results,
            total_time=total_time,
            avg_features_per_stock=avg_features_per_stock,
            gpu_memory_utilization=gpu_memory_utilization
        )

    def parallel_feature_generation(self, data_list: List[pdDataFrame], batch_size: int = 10) -> BatchFeatureResult:
        """并行特征生成"""
        if not self.gpu_enabled or self.n_jobs == 1:
            return self.batch_feature_generation(data_list)

        start_time = time.time()
        results = []

        # 使用多进程并行处理
        with ProcessPoolExecutor(max_workers=self.n_jobs) as executor:
            # 将数据分成批次
            batches = [data_list[i:i + batch_size] for i in range(0, len(data_list), batch_size)]

            # 并行处理每个批次
            future_to_batch = {
                executor.submit(self.batch_feature_generation, batch): batch_idx
                for batch_idx, batch in enumerate(batches)
            }

            for future in future_to_batch:
                try:
                    batch_result = future.result(timeout=300)  # 5分钟超时
                    results.extend(batch_result.results)
                except Exception as e:
                    self.logger.error(f"批次处理失败: {e}")

        total_time = time.time() - start_time

        return BatchFeatureResult(
            results=results,
            total_time=total_time,
            avg_features_per_stock=np.mean([len(r.feature_names) for r in results]) if results else 0,
            gpu_memory_utilization=0.0  # 简化处理
        )

    def select_features(self, data: pd.DataFrame, method: str = 'variance', top_k: int = 100) -> List[str]:
        """特征选择"""
        if method == 'variance':
            # 基于方差的特征选择
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            variances = data[numeric_columns].var()
            top_features = variances.nlargest(top_k).index.tolist()

        elif method == 'correlation':
            # 基于相关性的特征选择
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            correlations = data[numeric_columns].corrwith(data['close']).abs()
            top_features = correlations.nlargest(top_k).index.tolist()

        elif method == 'mutual_info':
            # 基于互信息的特征选择
            from cuml.feature_selection import mutual_info_regression

            X = data.select_dtypes(include=[np.number]).drop(columns=['close'], errors='ignore')
            y = data['close']

            if self.gpu_enabled:
                X_gpu = cudf.DataFrame(X)
                y_gpu = cudf.Series(y)
                mi_scores = mutual_info_regression(X_gpu, y_gpu)
            else:
                from sklearn.feature_selection import mutual_info_regression
                mi_scores = mutual_info_regression(X, y)

            # 选择top_k特征
            feature_scores = pd.Series(mi_scores, index=X.columns)
            top_features = feature_scores.nlargest(top_k).index.tolist()

        else:
            raise ValueError(f"不支持的特征选择方法: {method}")

        return top_features

    def normalize_features(self, data: pd.DataFrame, method: str = 'standard') -> pd.DataFrame:
        """特征标准化"""
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        feature_data = data[numeric_columns]

        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        else:
            raise ValueError(f"不支持的标准化方法: {method}")

        if self.gpu_enabled:
            feature_gpu = cudf.DataFrame(feature_data)
            normalized_features = scaler.fit_transform(feature_gpu)
            normalized_df = cudf.DataFrame(normalized_features, columns=feature_gpu.columns)
            result = data.copy()
            for col in normalized_df.columns:
                result[f'{col}_normalized'] = normalized_df[col].to_numpy()
        else:
            normalized_features = scaler.fit_transform(feature_data)
            normalized_df = pd.DataFrame(normalized_features, columns=feature_data.columns)
            result = data.copy()
            for col in normalized_df.columns:
                result[f'{col}_normalized'] = normalized_df[col].values

        return result

    def save_feature_cache(self, filepath: str):
        """保存特征缓存"""
        import joblib
        cache_data = {
            'feature_cache': self.feature_cache,
            'feature_config': self.feature_config,
            'gpu_enabled': self.gpu_enabled
        }
        joblib.dump(cache_data, filepath)

    def load_feature_cache(self, filepath: str):
        """加载特征缓存"""
        import joblib
        cache_data = joblib.load(filepath)
        self.feature_cache = cache_data['feature_cache']
        self.feature_config = cache_data['feature_config']
        self.gpu_enabled = cache_data['gpu_enabled']


class MultiStockFeatureGenerator:
    """多股票特征生成器"""

    def __init__(self, gpu_enabled: bool = True, max_stocks: int = 1000):
        self.gpu_enabled = gpu_enabled
        self.max_stocks = max_stocks
        self.base_generator = GPUFeatureGenerator(gpu_enabled)

    def generate_market_features(self, stock_data: Dict[str, pd.DataFrame]) -> Dict[str, FeatureResult]:
        """为多只股票生成特征"""
        results = {}

        # 按批次处理
        batch_size = 50 if self.gpu_enabled else 10
        stock_codes = list(stock_data.keys())

        for i in range(0, len(stock_codes), batch_size):
            batch_codes = stock_codes[i:i + batch_size]
            batch_data = [stock_data[code] for code in batch_codes]

            # 使用GPU批量处理
            batch_results = self.base_generator.batch_feature_generation(batch_data)

            # 存储结果
            for j, code in enumerate(batch_codes):
                if j < len(batch_results.results):
                    results[code] = batch_results.results[j]

        return results

    def generate_cross_sectional_features(self, market_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """生成横截面特征"""
        start_time = time.time()

        # 收集所有股票的最新数据
        latest_data = {}
        for stock_code, data in market_data.items():
            if not data.empty:
                latest_data[stock_code] = data.iloc[-1]

        # 转换为DataFrame
        cross_sectional_df = pd.DataFrame.from_dict(latest_data, orient='index')

        # 计算横截面特征
        features = {}

        # 市值排名
        if 'market_cap' in cross_sectional_df.columns:
            features['market_cap_rank'] = cross_sectional_df['market_cap'].rank(ascending=False)

        # 收益率排名
        return_columns = [col for col in cross_sectional_df.columns if 'return' in col.lower()]
        for col in return_columns:
            features[f'{col}_rank'] = cross_sectional_df[col].rank(ascending=False)

        # 波动率排名
        vol_columns = [col for col in cross_sectional_df.columns if 'volatility' in col.lower()]
        for col in vol_columns:
            features[f'{col}_rank'] = cross_sectional_df[col].rank(ascending=True)

        # 合并特征
        features_df = pd.DataFrame(features)

        calculation_time = time.time() - start_time

        self.logger.info(f"横截面特征生成完成，耗时: {calculation_time:.2f}秒")

        return features_df


def benchmark_feature_generation(data: pd.DataFrame, gpu_enabled: bool = True):
    """特征生成性能基准测试"""
    print("🔬 开始特征生成性能测试...")

    # GPU版本
    gpu_generator = GPUFeatureGenerator(gpu_enabled=True)
    gpu_start = time.time()
    gpu_result = gpu_generator.generate_all_features(data)
    gpu_time = time.time() - gpu_start

    # CPU版本
    cpu_generator = GPUFeatureGenerator(gpu_enabled=False)
    cpu_start = time.time()
    cpu_result = cpu_generator.generate_all_features(data)
    cpu_time = time.time() - cpu_start

    # 对比结果
    print(f"\n📊 特征生成性能对比:")
    print(f"GPU处理时间: {gpu_time:.2f}秒")
    print(f"CPU处理时间: {cpu_time:.2f}秒")
    print(f"加速比: {cpu_time/gpu_time:.2f}x")
    print(f"GPU生成特征数: {len(gpu_result.feature_names)}")
    print(f"CPU生成特征数: {len(cpu_result.feature_names)}")
    print(f"GPU内存使用: {gpu_result.memory_usage['total_memory']/1024/1024:.2f} MB")

    return {
        'gpu_time': gpu_time,
        'cpu_time': cpu_time,
        'speedup': cpu_time / gpu_time,
        'gpu_result': gpu_result,
        'cpu_result': cpu_result
    }


if __name__ == "__main__":
    # 示例使用
    import yfinance as yf

    # 获取多只股票数据
    stock_symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
    stock_data = {}

    for symbol in stock_symbols:
        data = yf.download(symbol, start='2023-01-01', end='2024-01-01')
        stock_data[symbol] = data

    # 创建特征生成器
    generator = GPUFeatureGenerator(gpu_enabled=True)

    # 批量生成特征
    batch_result = generator.batch_feature_generation(list(stock_data.values()))

    print(f"批量处理完成:")
    print(f"总处理时间: {batch_result.total_time:.2f}秒")
    print(f"平均特征数: {batch_result.avg_features_per_stock:.0f}")
    print(f"GPU内存利用率: {batch_result.gpu_memory_utilization:.2f}")

    # 基准测试
    benchmark_results = benchmark_feature_generation(list(stock_data.values())[0])
    print(f"\nGPU加速性能提升: {benchmark_results['speedup']:.2f}x")