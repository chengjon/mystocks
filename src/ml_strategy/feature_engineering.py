"""
特征工程模块 - 滚动窗口特征生成

基于 PyProf 项目的特征工程方法，扩展为更完整的特征生成系统。
支持滚动窗口特征、技术指标特征和自定义特征。

作者: MyStocks Development Team
创建日期: 2025-10-19
版本: 1.0.0
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Tuple, List, Dict, Any, Optional
import pandas as pd
import numpy as np
import logging
from queue import Queue


class RollingFeatureGenerator:
    """
    滚动窗口特征生成器

    生成基于历史数据的滚动窗口特征,用于机器学习预测。

    主要功能:
    - 滚动窗口特征提取
    - 技术指标计算
    - 特征矩阵构建

    示例:
        >>> generator = RollingFeatureGenerator(window_size=10)
        >>> X, y = generator.prepare_ml_data(df, target_col='close', forecast_horizon=1)
    """

    def __init__(self, window_size: int = 10):
        """
        初始化特征生成器

        Args:
            window_size: 滚动窗口大小（天数）
        """
        self.window_size = window_size
        self.logger = logging.getLogger(__name__)

    def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        生成滚动窗口特征

        Args:
            df: 包含 OHLCV 数据的 DataFrame
                必需列: open, high, low, close, vol

        Returns:
            DataFrame: 包含滚动窗口特征的数据
        """
        if df.empty:
            self.logger.warning("输入数据为空")
            return pd.DataFrame()

        # 验证必需列
        required_cols = ["open", "high", "low", "close", "vol"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"缺少必需列: {missing_cols}")

        features = []

        # 使用滑动窗口生成特征
        for i in range(len(df) - self.window_size + 1):
            window = df.iloc[i : i + self.window_size]
            feature_row = self._extract_window_features(window)
            features.append(feature_row)

        if not features:
            self.logger.warning("没有足够的数据生成特征")
            return pd.DataFrame()

        df_features = pd.DataFrame(features)

        self.logger.info(
            f"生成特征成功: {len(df_features)}条记录, {len(df_features.columns)}个特征"
        )

        return df_features

    def _extract_window_features(self, window: pd.DataFrame) -> Dict[str, float]:
        """
        从单个窗口提取特征

        Args:
            window: 窗口数据

        Returns:
            特征字典
        """
        features = {}

        # 1. 基础价格特征
        features["close_mean"] = window["close"].mean()
        features["close_std"] = window["close"].std()
        features["close_min"] = window["close"].min()
        features["close_max"] = window["close"].max()

        # 2. 价格比率特征
        features["high_low_ratio"] = window["high"].mean() / max(
            window["low"].mean(), 1e-6
        )
        features["close_open_ratio"] = window["close"].mean() / max(
            window["open"].mean(), 1e-6
        )

        # 3. 价格动量特征
        if len(window) >= 2:
            features["price_momentum"] = (
                window["close"].iloc[-1] / max(window["close"].iloc[0], 1e-6)
            ) - 1
            features["price_change_rate"] = window["close"].pct_change().mean()
        else:
            features["price_momentum"] = 0
            features["price_change_rate"] = 0

        # 4. 成交量特征
        features["volume_mean"] = window["vol"].mean()
        features["volume_std"] = window["vol"].std()

        if len(window) >= 6:
            recent_vol = window["vol"].iloc[-3:].mean()
            old_vol = window["vol"].iloc[:3].mean()
            features["volume_trend"] = recent_vol / max(old_vol, 1)
        else:
            features["volume_trend"] = 1

        # 5. 波动率特征
        if len(window) >= 2:
            returns = window["close"].pct_change().dropna()
            features["volatility"] = returns.std()
            features["skewness"] = returns.skew() if len(returns) > 2 else 0
        else:
            features["volatility"] = 0
            features["skewness"] = 0

        # 6. 趋势特征
        if len(window) >= 2:
            x = np.arange(len(window))
            y = window["close"].values
            if len(x) > 0 and len(y) > 0:
                slope = np.polyfit(x, y, 1)[0]
                features["price_trend"] = slope
            else:
                features["price_trend"] = 0
        else:
            features["price_trend"] = 0

        # 7. 振幅特征
        features["amplitude_mean"] = (
            (window["high"] - window["low"]) / window["close"]
        ).mean()

        return features

    def generate_rolling_raw_features(
        self, df: pd.DataFrame, feature_cols: List[str] = None
    ) -> pd.DataFrame:
        """
        生成滚动原始特征（PyProf 原始方法）

        将过去 N 天的原始数据展平为特征向量。
        例如: window_size=3 时, 生成 3×feature_num 个特征列

        Args:
            df: 原始数据
            feature_cols: 要使用的特征列（默认: open, high, low, close, vol, amount）

        Returns:
            DataFrame: 包含展平特征的数据
        """
        if feature_cols is None:
            feature_cols = ["open", "high", "low", "close", "vol", "amount"]

        # 验证列存在
        missing_cols = [col for col in feature_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"缺少特征列: {missing_cols}")

        feature_queue = Queue(maxsize=self.window_size)
        feature_list = []

        for index, row in df.iterrows():
            # 选择特征列
            feature_values = row[feature_cols]
            feature_queue.put(feature_values)

            # 当队列满了开始生成特征
            if feature_queue.full():
                # 提取队列中的所有特征
                row_features = []
                temp_queue = Queue(maxsize=self.window_size)

                for _ in range(self.window_size):
                    feat = feature_queue.get()
                    row_features.extend(feat.values.tolist())
                    temp_queue.put(feat)

                feature_queue = temp_queue
                feature_list.append(row_features)

        # 生成列名
        column_names = []
        for i in range(self.window_size):
            for col in feature_cols:
                column_names.append(f"{col}_t{i}")

        df_features = pd.DataFrame(feature_list, columns=column_names)

        self.logger.info(
            f"生成滚动原始特征: {len(df_features)}条, {len(column_names)}列"
        )

        return df_features

    def prepare_ml_data(
        self,
        df: pd.DataFrame,
        target_col: str = "close",
        forecast_horizon: int = 1,
        feature_type: str = "aggregate",
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        准备机器学习数据

        Args:
            df: 原始数据
            target_col: 目标列名
            forecast_horizon: 预测步长（天数）
            feature_type: 特征类型
                - 'aggregate': 聚合特征（均值、标准差等）
                - 'raw': 原始滚动特征（展平）

        Returns:
            (X, y): 特征矩阵和目标变量
        """
        if df.empty:
            raise ValueError("输入数据为空")

        if target_col not in df.columns:
            raise ValueError(f"目标列 {target_col} 不存在")

        # 生成特征
        if feature_type == "aggregate":
            X = self.generate_features(df)
        elif feature_type == "raw":
            X = self.generate_rolling_raw_features(df)
        else:
            raise ValueError(f"不支持的特征类型: {feature_type}")

        if X.empty:
            raise ValueError("特征生成失败")

        # 生成目标变量 (未来 forecast_horizon 天的价格)
        y_values = df[target_col].shift(-forecast_horizon).values

        # 对齐 X 和 y
        if feature_type == "aggregate":
            # aggregate 特征从 window_size-1 索引开始
            start_idx = self.window_size - 1
        else:
            # raw 特征从 window_size-1 索引开始
            start_idx = self.window_size - 1

        end_idx = len(df) - forecast_horizon

        # 切片对齐
        y = pd.Series(y_values[start_idx:end_idx], name=target_col)
        X = X.iloc[: len(y)].reset_index(drop=True)
        y = y.reset_index(drop=True)

        # 验证
        if len(X) != len(y):
            raise ValueError(f"X 和 y 长度不匹配: {len(X)} vs {len(y)}")

        # 移除缺失值
        mask = ~y.isna()
        X = X[mask].reset_index(drop=True)
        y = y[mask].reset_index(drop=True)

        self.logger.info(f"准备 ML 数据完成: X={X.shape}, y={y.shape}")

        return X, y

    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        添加技术指标特征

        Args:
            df: 原始OHLCV数据

        Returns:
            DataFrame: 添加技术指标后的数据
        """
        df = df.copy()

        # 1. 移动平均线
        for period in [5, 10, 20]:
            df[f"ma_{period}"] = df["close"].rolling(period).mean()
            df[f"price_to_ma_{period}"] = df["close"] / df[f"ma_{period}"]

        # 2. RSI
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-10)
        df["rsi_14"] = 100 - (100 / (1 + rs))

        # 3. MACD
        ema12 = df["close"].ewm(span=12, adjust=False).mean()
        ema26 = df["close"].ewm(span=26, adjust=False).mean()
        df["macd"] = ema12 - ema26
        df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
        df["macd_hist"] = df["macd"] - df["macd_signal"]

        # 4. 布林带
        df["bb_middle"] = df["close"].rolling(20).mean()
        bb_std = df["close"].rolling(20).std()
        df["bb_upper"] = df["bb_middle"] + 2 * bb_std
        df["bb_lower"] = df["bb_middle"] - 2 * bb_std
        df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]

        self.logger.info(f"添加技术指标: 新增 {len(df.columns) - len(df.columns)} 列")

        return df


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    # 创建测试数据
    test_data = pd.DataFrame(
        {
            "open": np.random.rand(100) * 100 + 3000,
            "high": np.random.rand(100) * 100 + 3100,
            "low": np.random.rand(100) * 100 + 2900,
            "close": np.random.rand(100) * 100 + 3000,
            "vol": np.random.rand(100) * 1e8,
        }
    )

    # 测试聚合特征
    print("\n=== 测试聚合特征 ===")
    generator = RollingFeatureGenerator(window_size=10)
    X, y = generator.prepare_ml_data(test_data, feature_type="aggregate")
    print(f"X.shape: {X.shape}")
    print(f"y.shape: {y.shape}")
    print(f"特征列: {list(X.columns)}")

    # 测试原始滚动特征
    print("\n=== 测试原始滚动特征 ===")
    # 添加 amount 列
    test_data["amount"] = test_data["vol"] * test_data["close"]
    X_raw, y_raw = generator.prepare_ml_data(test_data, feature_type="raw")
    print(f"X_raw.shape: {X_raw.shape}")
    print(f"y_raw.shape: {y_raw.shape}")
    print(f"前5个特征列: {list(X_raw.columns)[:5]}")

    print("\n✅ 特征工程模块测试完成")
