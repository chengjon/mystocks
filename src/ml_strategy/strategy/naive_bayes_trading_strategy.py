#!/usr/bin/env python3
"""
Naive Bayes增强交易策略 (Naive Bayes-Enhanced Trading Strategy)

功能说明:
- 基于Naive Bayes算法的概率-based交易策略
- 使用高斯朴素贝叶斯进行市场状态分类
- 提供概率-based的信号强度评估
- 快速训练和预测，适合高频应用
- 基于条件概率的决策制定

策略逻辑:
1. 使用技术指标构建概率特征空间
2. Naive Bayes分类器计算条件概率
3. 基于概率分布生成交易信号
4. 结合概率置信度进行风险控制

作者: MyStocks量化交易团队
创建时间: 2026-01-12
版本: 1.0.0
"""

import logging
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from src.ml_strategy.strategy.ml_strategy_base import MLStrategyConfig, MLTradingStrategy

logger = logging.getLogger(__name__)


class NaiveBayesTradingStrategy(MLTradingStrategy):
    """
    Naive Bayes增强交易策略

    使用朴素贝叶斯算法进行概率-based交易决策：
    - 识别上涨趋势 (Buy信号)
    - 识别震荡区间 (Hold信号)
    - 识别下跌趋势 (Sell信号)

    优势：
    - 训练速度极快，适合实时更新
    - 提供概率输出，可量化不确定性
    - 对特征独立性假设简化计算
    - 对小数据集鲁棒性好
    """

    def __init__(self, **kwargs):
        # Naive Bayes特定的配置
        config = MLStrategyConfig(
            algorithm_type="naive_bayes",
            prediction_threshold=0.55,  # Naive Bayes可能需要调整阈值
            confidence_threshold=0.60,
            algorithm_params={
                "var_smoothing": 1e-9,  # 方差平滑参数
            },
        )

        super().__init__(
            strategy_name="NaiveBayes_Probability_Based", algorithm_type="naive_bayes", config=config, **kwargs
        )

        # Naive Bayes特定的参数
        self.probability_threshold = 0.6  # 概率阈值
        self.confidence_weight = 0.7  # 置信度权重
        self.probability_smoothing = 0.01  # 概率平滑

        logger.info("初始化Naive Bayes增强交易策略")


    async def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        准备Naive Bayes策略的特征工程

        Naive Bayes对特征分布敏感，需要合理的特征变换
        """
        try:
            df = data.copy()

            # 基础技术指标特征
            df = self.feature_engineer.add_technical_features(df)

            # Naive Bayes特定的特征处理
            df = self._add_naive_bayes_features(df)

            # 创建目标变量 - Naive Bayes对类别平衡敏感
            df = self.feature_engineer.create_target_variable(df, future_periods=3)  # 较短预测期

            # 清理数据 - Naive Bayes对NaN敏感
            df = df.dropna()

            logger.info(
                "Naive Bayes特征工程完成，生成 %d 个样本，%d 个特征",
                len(df), len(df.columns) - 1
            )
            return df

        except Exception as e:
            logger.error("Naive Bayes特征工程失败: %s", str(e))
            raise


def _add_naive_bayes_features(self, data: pd.DataFrame) -> pd.DataFrame:
    """
    添加Naive Bayes特定的特征

    Naive Bayes假设特征独立，需要特征变换以满足假设
    """
    df = data.copy()

    # 标准化特征 - Naive Bayes对尺度敏感
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if col != "target" and not col.startswith("target"):
            # Z-score标准化
            mean_val = df[col].mean()
            std_val = df[col].std()
            if std_val > 0:
                df[f"{col}_zscore"] = (df[col] - mean_val) / std_val

    # 概率分布特征
    df["price_change_prob"] = self._calculate_probability_features(df["close"])

    # 波动率概率特征
    if "volatility_10" in df.columns:
        df["volatility_prob"] = self._calculate_probability_features(df["volatility_10"])

    # RSI概率分布
    if "rsi_14" in df.columns:
        df["rsi_prob"] = self._calculate_probability_features(df["rsi_14"])

    # 动量概率特征
    if "momentum_5" in df.columns:
        df["momentum_prob"] = self._calculate_probability_features(df["momentum_5"])

    # 成交量概率特征 (如果有)
    if "volume" in df.columns:
        df["volume_prob"] = self._calculate_probability_features(df["volume"])

    # 技术指标组合概率
    if all(col in df.columns for col in ["rsi_14", "macd", "bb_position"]):
        df["technical_score"] = (
            (df["rsi_14"] - 50) / 50  # RSI围绕50为中心
            + df["macd"] / df["macd"].std()  # MACD标准化
            + (df["bb_position"] - 0.5) * 2  # 布林带位置标准化
        ) / 3  # 平均组合

        df["technical_prob"] = self._calculate_probability_features(df["technical_score"])

    return df


def _calculate_probability_features(self, series: pd.Series, bins: int = 10) -> pd.Series:
    """
    计算概率分布特征

    将连续值转换为概率分布，更适合Naive Bayes
    """
    try:
        # 创建分位数bins
        quantiles = np.linspace(0, 1, bins + 1)
        bin_edges = series.quantile(quantiles)

        # 计算每个值在分布中的概率位置
        ranks = series.rank(pct=True)

        # 添加小噪声避免完全确定性
        noise = np.random.normal(0, self.probability_smoothing, len(ranks))
        prob_features = ranks + noise

        # 确保在[0,1]范围内
        prob_features = np.clip(prob_features, 0, 1)

        return prob_features

    except Exception as e:
        logger.warning("概率特征计算失败: %s", str(e))
        return pd.Series([0.5] * len(series), index=series.index)


    async def interpret_ml_signals(self, predictions: List[Dict[str, Any]], data: pd.DataFrame) -> pd.DataFrame:
        """
        解释Naive Bayes预测结果为交易信号

        Naive Bayes预测结果：
        - 0: 下跌趋势 (Sell信号)
        - 1: 震荡区间 (Hold信号)
        - 2: 上涨趋势 (Buy信号)
        """
        try:
            # 调试: 检查预测结果分布
            pred_classes = [p["prediction"] for p in predictions]
            pred_confidences = [p["confidence"] for p in predictions]
            unique_preds = list(set(pred_classes))
            logger.info(
                f"Naive Bayes预测结果分布: {
                dict(zip(unique_preds, [pred_classes.count(x) for x in unique_preds]))}"
            )
            logger.info(
                f"Naive Bayes置信度范围: {
                        min(pred_confidences):.3f} - {max(pred_confidences):.3f}"
            )
            logger.info(
                f"Naive Bayes平均置信度: {
                    sum(pred_confidences) /
                    len(pred_confidences):.3f}"
            )

            signals = []
            signal_counts = {"buy": 0, "hold": 0, "sell": 0}

            for i, pred in enumerate(predictions):
                prediction_class = pred["prediction"]
                confidence = pred["confidence"]

                # Naive Bayes信号映射 - 概率导向
                if prediction_class == 2 and confidence > self.config.confidence_threshold:
                    # 强上涨概率
                    signal = 1  # Buy
                    signal_strength = confidence * self.confidence_weight
                    signal_counts["buy"] += 1
                elif prediction_class == 0 and confidence > self.config.confidence_threshold:
                    # 强下跌概率
                    signal = -1  # Sell
                    signal_strength = confidence * self.confidence_weight
                    signal_counts["sell"] += 1
                else:
                    # 概率不确定或震荡
                    signal = 0  # Hold
                    signal_strength = max(0.2, confidence * 0.5)  # 降低持有信号强度
                    signal_counts["hold"] += 1

                # 使用数据索引而不是时间戳，确保与输入数据对齐
                index_value = data.index[i] if i < len(data) else pd.Timestamp.now()

                signals.append(
                    {
                        "timestamp": index_value,
                        "signal": signal,
                        "confidence": confidence,
                        "signal_strength": signal_strength,
                        "prediction_class": prediction_class,
                        "ml_model": "naive_bayes",
                    }
                )

            logger.info(
                f"信号生成统计: 买入={
                    signal_counts['buy']}, 持有={
                    signal_counts['hold']}, 卖出={
                    signal_counts['sell']}"
            )
            logger.info("置信度阈值: %s", self.config.confidence_threshold)

            signals_df = pd.DataFrame(signals)
            signals_df.set_index("timestamp", inplace=True)

            # 应用Naive Bayes特定的风险控制
            signals_df = self._apply_naive_bayes_risk_controls(signals_df, data)

            logger.info("Naive Bayes策略生成 %d 个交易信号", len(signals_df))
            return signals_df

        except Exception as e:
            logger.error("Naive Bayes信号解释失败: %s", str(e))
            


def _apply_naive_bayes_risk_controls(self, signals_df: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
    """
    应用Naive Bayes特定的风险控制

    基于概率分布的风险管理
    """
    try:
        df = signals_df.copy()

        # 获取基础风险控制
        df = self._apply_risk_controls(df, data)

        # Naive Bayes特定的额外控制

        # 1. 基于预测概率分布的过滤
        # 如果预测概率过于集中，可能表示过拟合
        prob_std = df["confidence"].std()
        if prob_std < 0.1:  # 概率过于集中
            logger.warning("预测概率分布过于集中，可能存在过拟合风险")
            df["signal_strength"] *= 0.8

        # 2. 基于置信度分布的动态阈值调整
        confidence_median = df["confidence"].median()
        if confidence_median < 0.5:  # 整体置信度较低
            logger.info("整体预测置信度较低，调整信号强度")
            df.loc[df["signal"] != 0, "signal_strength"] *= 0.9

        # 3. 连续低概率信号的过滤
        # 如果连续多个信号的置信度都很低，可能表示模型不确定性
        low_confidence_streak = (df["confidence"] < self.config.confidence_threshold).rolling(window=5).sum()
        high_streak_signals = low_confidence_streak >= 3
        df.loc[high_streak_signals, "signal"] = 0

        logger.info("Naive Bayes特定风险控制已应用")
        return df

    except Exception as e:
        logger.warning("Naive Bayes风险控制应用失败，使用基础风险控制: %s", str(e))
        return self._apply_risk_controls(signals_df, data)


    def get_probability_distribution(self) -> Dict[str, Any]:
        """
        获取预测概率分布分析
        """
        try:
            if not self.trained_model_key or self.trained_model_key not in self.algorithm_manager.trained_models:
                return {"error": "模型未训练"}

            # 这里简化版 - 实际实现需要从模型中提取概率信息
            prob_info = {
                "model_type": "Gaussian Naive Bayes",
                "assumption": "特征条件独立",
                "strengths": ["快速训练", "概率输出", "对小数据集有效"],
                "limitations": ["特征独立性假设", "对相关特征敏感"],
                "best_for": "概率评估、快速原型、小数据集",
            }

            return prob_info

        except Exception as e:
            logger.error("概率分布获取失败: %s", str(e))
            return {"error": str(e)}


    def get_strategy_info(self) -> Dict[str, Any]:
        """获取Naive Bayes策略的详细信息"""
        base_info = super().get_strategy_info()

        # 添加Naive Bayes特定信息
        prob_dist = self.get_probability_distribution()

        base_info.update({
            "probability_threshold": self.probability_threshold,
            "confidence_weight": self.confidence_weight,
            "probability_smoothing": self.probability_smoothing,
            "model_interpretability": "moderate",  # 概率可解释但假设简化
            "probability_distribution": prob_dist,
            "algorithm_characteristics": {
                "fast_training": True,
                "probability_output": True,
                "feature_independence_assumption": True,
                "good_for_small_datasets": True,
                "sensitive_to_feature_correlation": True,
            },
        })

        return base_info


class NaiveBayesConservativeStrategy(NaiveBayesTradingStrategy):
    """
    保守型Naive Bayes策略

    更严格的概率阈值，更高的置信度要求
    适合风险偏好较低，对概率要求严格的投资者
    """


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 更保守的参数
        self.config.prediction_threshold = 0.65
        self.config.confidence_threshold = 0.75
        self.probability_threshold = 0.7
        self.confidence_weight = 0.8

        logger.info("初始化保守型Naive Bayes策略")


class NaiveBayesAggressiveStrategy(NaiveBayesTradingStrategy):
    """
    激进型Naive Bayes策略

    更宽松的概率标准，更早捕捉概率信号
    适合风险偏好较高，重视概率信息的投资者
    """


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 更激进的参数
        self.config.prediction_threshold = 0.45
        self.config.confidence_threshold = 0.50
        self.probability_threshold = 0.5
        self.confidence_weight = 0.6

        logger.info("初始化激进型Naive Bayes策略")
