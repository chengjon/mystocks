"""
特征工程服务
用于生成股票预测的滚动窗口特征
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional
from queue import Queue


class FeatureEngineeringService:
    """
    特征工程服务

    主要功能：
    1. 滚动窗口特征生成
    2. 目标变量生成（下一日收盘价）
    3. 特征数据集保存和加载
    """

    @staticmethod
    def generate_rolling_features(
        df: pd.DataFrame, step: int = 10, feature_columns: list = None
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        生成滚动窗口特征

        Args:
            df: 包含 OHLCV 数据的 DataFrame
            step: 滚动窗口大小（默认10个交易日）
            feature_columns: 用于生成特征的列名列表

        Returns:
            Tuple[pd.DataFrame, pd.Series]: (特征矩阵 X, 目标变量 y)
        """
        if feature_columns is None:
            feature_columns = ["open", "high", "low", "close", "amount", "volume"]

        # 确保所有特征列都存在
        missing_cols = [col for col in feature_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"缺少特征列: {missing_cols}")

        # 生成目标变量：下一日收盘价
        df = df.copy()
        df["nextClose"] = df["close"].shift(-1)

        # 删除最后一行（没有目标变量）
        df = df[:-1]

        # 初始化特征矩阵
        feature_list = []
        feature_num = len(feature_columns)

        # 使用队列实现滚动窗口
        q = Queue(maxsize=step)

        for idx, row in df.iterrows():
            # 提取当前行的特征
            current_features = [row[col] for col in feature_columns]

            # 添加到队列
            if q.full():
                q.get()  # 移除最旧的数据
            q.put(current_features)

            # 当队列满时，生成特征向量
            if q.qsize() == step:
                # 将队列中的所有特征展平成一维向量
                feature_vector = []
                for item in list(q.queue):
                    feature_vector.extend(item)

                feature_list.append(feature_vector)
            else:
                # 队列未满，使用 NaN 填充
                feature_list.append([np.nan] * (step * feature_num))

        # 创建特征 DataFrame
        feature_columns_names = []
        for i in range(step):
            for col in feature_columns:
                feature_columns_names.append(f"{col}_t{i}")

        X = pd.DataFrame(feature_list, columns=feature_columns_names)

        # 删除包含 NaN 的行
        valid_indices = X.dropna().index
        X = X.loc[valid_indices]
        y = df.iloc[valid_indices]["nextClose"]

        # 重置索引
        X = X.reset_index(drop=True)
        y = y.reset_index(drop=True)

        return X, y

    @staticmethod
    def save_features_to_csv(X: pd.DataFrame, y: pd.Series, output_file: str) -> str:
        """
        保存特征和目标变量到 CSV 文件

        Args:
            X: 特征矩阵
            y: 目标变量
            output_file: 输出文件路径

        Returns:
            str: 输出文件路径
        """
        # 合并特征和目标变量
        data = X.copy()
        data["nextClose"] = y

        # 保存到 CSV
        data.to_csv(output_file, index=False, encoding="utf-8")

        return output_file

    @staticmethod
    def load_features_from_csv(file_path: str) -> Tuple[pd.DataFrame, pd.Series]:
        """
        从 CSV 文件加载特征和目标变量

        Args:
            file_path: CSV 文件路径

        Returns:
            Tuple[pd.DataFrame, pd.Series]: (特征矩阵 X, 目标变量 y)
        """
        data = pd.read_csv(file_path)

        # 分离特征和目标变量
        y = data["nextClose"]
        X = data.drop(columns=["nextClose"])

        return X, y

    @staticmethod
    def generate_features_from_file(
        input_file: str, output_file: str, step: int = 10, feature_columns: list = None
    ) -> Tuple[str, dict]:
        """
        从 CSV 文件读取数据并生成特征

        Args:
            input_file: 输入的 CSV 文件路径
            output_file: 输出的特征文件路径
            step: 滚动窗口大小
            feature_columns: 特征列名列表

        Returns:
            Tuple[str, dict]: (输出文件路径, 统计信息)
        """
        # 读取数据
        df = pd.read_csv(input_file)

        # 生成特征
        X, y = FeatureEngineeringService.generate_rolling_features(
            df, step, feature_columns
        )

        # 保存特征
        output_path = FeatureEngineeringService.save_features_to_csv(X, y, output_file)

        # 统计信息
        stats = {
            "total_samples": len(X),
            "feature_dim": X.shape[1],
            "step": step,
            "feature_columns": feature_columns
            or ["open", "high", "low", "close", "amount", "volume"],
            "target_mean": float(y.mean()),
            "target_std": float(y.std()),
            "target_min": float(y.min()),
            "target_max": float(y.max()),
        }

        return output_path, stats

    @staticmethod
    def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        计算技术指标特征

        Args:
            df: 包含 OHLCV 数据的 DataFrame

        Returns:
            pd.DataFrame: 添加了技术指标的 DataFrame
        """
        df = df.copy()

        # 移动平均线
        df["MA5"] = df["close"].rolling(window=5).mean()
        df["MA10"] = df["close"].rolling(window=10).mean()
        df["MA20"] = df["close"].rolling(window=20).mean()

        # 涨跌幅
        df["pct_change"] = df["close"].pct_change()

        # 价格波动率（标准差）
        df["volatility"] = df["close"].rolling(window=10).std()

        # 相对强弱指标（简化版）
        df["price_position"] = (df["close"] - df["low"]) / (
            df["high"] - df["low"] + 1e-6
        )

        # 成交量变化
        df["volume_change"] = df["volume"].pct_change()

        return df

    @staticmethod
    def prepare_model_data(
        df: pd.DataFrame, step: int = 10, include_indicators: bool = True
    ) -> Tuple[pd.DataFrame, pd.Series, dict]:
        """
        准备用于模型训练的数据

        Args:
            df: 原始 OHLCV 数据
            step: 滚动窗口大小
            include_indicators: 是否包含技术指标

        Returns:
            Tuple[pd.DataFrame, pd.Series, dict]: (特征矩阵, 目标变量, 元数据)
        """
        # 计算技术指标
        if include_indicators:
            df = FeatureEngineeringService.calculate_technical_indicators(df)
            feature_columns = [
                "open",
                "high",
                "low",
                "close",
                "amount",
                "volume",
                "MA5",
                "MA10",
                "MA20",
                "pct_change",
                "volatility",
                "price_position",
                "volume_change",
            ]
        else:
            feature_columns = ["open", "high", "low", "close", "amount", "volume"]

        # 删除 NaN 行
        df = df.dropna()

        # 生成滚动窗口特征
        X, y = FeatureEngineeringService.generate_rolling_features(
            df, step, feature_columns
        )

        # 元数据
        metadata = {
            "step": step,
            "feature_columns": feature_columns,
            "total_samples": len(X),
            "feature_dim": X.shape[1],
            "include_indicators": include_indicators,
            "date_range": {
                "start": (
                    df.iloc[0]["tradeDate"] if "tradeDate" in df.columns else "unknown"
                ),
                "end": (
                    df.iloc[-1]["tradeDate"] if "tradeDate" in df.columns else "unknown"
                ),
            },
        }

        return X, y, metadata
