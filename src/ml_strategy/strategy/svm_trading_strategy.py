#!/usr/bin/env python3
"""
SVM增强交易策略 (SVM-Enhanced Trading Strategy)

功能说明:
- 基于SVM算法的价格模式识别策略
- 识别上涨、震荡、下跌三种市场状态
- 结合技术指标进行特征工程
- GPU加速的模式识别能力
- 自适应阈值和风险控制

策略逻辑:
1. 使用技术指标构建特征向量
2. SVM分类器识别价格模式
3. 基于置信度生成交易信号
4. 多重风险控制机制

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


class SVMTradingStrategy(MLTradingStrategy):
    """
    SVM增强交易策略

    使用支持向量机进行价格模式识别：
    - 识别上涨趋势 (Buy信号)
    - 识别震荡区间 (Hold信号)
    - 识别下跌趋势 (Sell信号)

    特征包括：
    - 移动平均线系统
    - 动量指标
    - 波动率指标
    - RSI相对强弱指数
    - MACD指标
    - 布林带指标
    """

    def __init__(self, **kwargs):
        # SVM特定的配置
        config = MLStrategyConfig(
            algorithm_type="svm",
            prediction_threshold=0.65,  # SVM需要更高的阈值
            confidence_threshold=0.75,
            algorithm_params={
                "C": 1.0,
                "kernel": "rbf",
                "gamma": "scale",
                "class_weight": "balanced",
            },
        )

        super().__init__(strategy_name="SVM_Pattern_Recognition", algorithm_type="svm", config=config, **kwargs)

        # SVM特定的参数
        self.pattern_lookback_periods = 20  # 模式识别回望周期
        self.signal_strength_threshold = 0.8  # 信号强度阈值

        logger.info("初始化SVM增强交易策略")

    async def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        准备SVM策略的特征工程

        构建适合SVM分类的特征向量
        """
        try:
            df = data.copy()

            # 基础价格特征
            df = self.feature_engineer.add_technical_features(df)

            # SVM特定的特征处理
            df = self._add_svm_specific_features(df)

            # 创建目标变量
            df = self.feature_engineer.create_target_variable(df, future_periods=5)

            # 清理数据
            df = df.dropna()

            logger.info("SVM特征工程完成，生成 {len(df)} 个样本，{len(df.columns) - 1} 个特征")
            return df

        except Exception:
            logger.error("SVM特征工程失败: %(e)s")
            raise

    def _add_svm_specific_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        添加SVM特定的特征

        SVM对特征缩放敏感，这里进行专门的预处理
        """
        df = data.copy()

        # 价格相对位置特征
        df["price_vs_ma5"] = (df["close"] - df["ma_5"]) / df["ma_5"]
        df["price_vs_ma10"] = (df["close"] - df["ma_10"]) / df["ma_10"]
        df["price_vs_ma20"] = (df["close"] - df["ma_20"]) / df["ma_20"]

        # 布林带位置
        df["bb_position"] = (df["close"] - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"])
        df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]

        # RSI信号
        df["rsi_overbought"] = (df["rsi_14"] > 70).astype(int)
        df["rsi_oversold"] = (df["rsi_14"] < 30).astype(int)
        df["rsi_neutral"] = ((df["rsi_14"] >= 30) & (df["rsi_14"] <= 70)).astype(int)

        # MACD信号强度
        df["macd_histogram"] = df["macd"] - df["macd_signal"]
        df["macd_crossover"] = np.sign(df["macd"] - df["macd_signal"])

        # 动量组合特征
        df["momentum_trend"] = np.sign(df["momentum_5"] + df["momentum_10"])
        df["momentum_strength"] = np.abs(df["momentum_5"]) + np.abs(df["momentum_10"])

        # 波动率趋势
        df["volatility_trend"] = df["volatility_10"] / df["volatility_5"] - 1

        # 成交量价格趋势 (如果有成交量数据)
        if "volume" in df.columns:
            df["volume_price_trend"] = df["volume"] * np.sign(df["close"] - df["open"])
            df["volume_ma_ratio"] = df["volume"] / df["volume"].rolling(window=10).mean()

        return df

    async def interpret_ml_signals(self, predictions: List[Dict[str, Any]], data: pd.DataFrame) -> pd.DataFrame:
        """
        解释SVM预测结果为交易信号

        SVM预测结果：
        - 0: 下跌趋势 (Sell信号)
        - 1: 震荡区间 (Hold信号)
        - 2: 上涨趋势 (Buy信号)
        """
        try:
            # 调试: 检查预测结果分布
            pred_classes = [p["prediction"] for p in predictions]
            pred_confidences = [p["confidence"] for p in predictions]
            unique_preds = set(pred_classes)
            logger.info(
                f"SVM预测结果分布: {dict(zip(unique_preds, [pred_classes.count(x) for x in unique_preds]))}"
            )
            logger.info("SVM置信度范围: {min(pred_confidences):.3f} - {max(pred_confidences):.3f")
            logger.info(
                f"SVM平均置信度: {sum(pred_confidences) / len(pred_confidences):.3f}"
            )
            signals = []

            signal_counts = {"buy": 0, "hold": 0, "sell": 0}

            for i, pred in enumerate(predictions):
                prediction_class = pred["prediction"]
                confidence = pred["confidence"]

                # SVM信号映射
                if prediction_class == 2 and confidence > self.config.confidence_threshold:
                    # 强上涨信号
                    signal = 1  # Buy
                    signal_strength = confidence
                    signal_counts["buy"] += 1
                elif prediction_class == 0 and confidence > self.config.confidence_threshold:
                    # 强下跌信号
                    signal = -1  # Sell
                    signal_strength = confidence
                    signal_counts["sell"] += 1
                elif prediction_class == 1:
                    # 震荡区间
                    signal = 0  # Hold
                    signal_strength = 0.5
                    signal_counts["hold"] += 1
                else:
                    # 不确定信号
                    signal = 0  # Hold
                    signal_strength = 0.3
                    signal_counts["hold"] += 1

                # 使用数据索引而不是时间戳，确保与输入数据对齐
                index_value = data.index[i] if i < len(data) else pd.Timestamp.now()

                signals.append(
                    {
                        "timestamp": index_value,  # 使用索引值作为时间戳
                        "signal": signal,
                        "confidence": confidence,
                        "signal_strength": signal_strength,
                        "prediction_class": prediction_class,
                        "ml_model": "svm",
                    }
                )

            logger.info(
                f"信号生成统计: 买入={signal_counts['buy']}, 持有={signal_counts['hold']}, 卖出={signal_counts['sell']}"
            )
            logger.info("置信度阈值: {self.config.confidence_threshold")

            signals_df = pd.DataFrame(signals)
            signals_df.set_index("timestamp", inplace=True)  # 使用timestamp作为索引

            # 应用额外的风险控制
            signals_df = self._apply_risk_controls(signals_df, data)

            logger.info("SVM策略生成 {len(signals_df)} 个交易信号")
            return signals_df

        except Exception:
            logger.error("SVM信号解释失败: %(e)s")
            raise

    def _apply_risk_controls(self, signals_df: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
        """
        应用风险控制机制

        防止在极端市场条件下产生错误信号
        """
        try:
            original_signal_counts = signals_df["signal"].value_counts().to_dict()
            logger.info("风险控制前信号分布: %(original_signal_counts)s")

            # 过滤低置信度信号
            high_confidence_mask = signals_df["confidence"] > self.config.confidence_threshold
            low_conf_signals = (~high_confidence_mask).sum()
            signals_df.loc[~high_confidence_mask, "signal"] = 0
            logger.info("低置信度过滤: %(low_conf_signals)s 个信号被过滤")

            # 防止在高波动期产生信号
            if "volatility_10" in data.columns:
                # 计算波动率分位数
                volatility_percentile = data["volatility_10"].rank(pct=True)
                high_volatility_mask = volatility_percentile > 0.8  # 最高20%波动率

                # 在高波动期降低信号强度
                signals_df.loc[high_volatility_mask, "signal_strength"] *= 0.7
                logger.info("高波动期调整: {high_volatility_mask.sum()} 个信号强度被降低")

            # 防止连续相同信号 (避免过度交易)
            signals_df["signal_change"] = signals_df["signal"].diff().fillna(0)
            consecutive_signals = signals_df["signal_change"] == 0
            signals_df.loc[consecutive_signals, "signal_strength"] *= 0.8

            # 基于RSI的额外过滤
            if "rsi_14" in data.columns:
                rsi_stats = data["rsi_14"].describe()
                logger.info(
                    f"RSI统计: 均值={rsi_stats['mean']:.1f}, 最小={rsi_stats['min']:.1f}, 最大={rsi_stats['max']:.1f}"
                )

                # 在超买区不产生买入信号
                overbought_mask = data["rsi_14"] > 75
                overbought_buy_signals = (overbought_mask & (signals_df["signal"] == 1)).sum()
                signals_df.loc[overbought_mask & (signals_df["signal"] == 1), "signal"] = 0
                logger.info("超买区过滤: %(overbought_buy_signals)s 个买入信号被过滤")

                # 在超卖区不产生卖出信号
                oversold_mask = data["rsi_14"] < 25
                oversold_sell_signals = (oversold_mask & (signals_df["signal"] == -1)).sum()
                signals_df.loc[oversold_mask & (signals_df["signal"] == -1), "signal"] = 0
                logger.info("超卖区过滤: %(oversold_sell_signals)s 个卖出信号被过滤")

            final_signal_counts = signals_df["signal"].value_counts().to_dict()
            logger.info("风险控制后信号分布: %(final_signal_counts)s")

            return signals_df

        except Exception:
            logger.warning("风险控制应用失败，使用原始信号: %(e)s")
            return signals_df

    def get_strategy_info(self) -> Dict[str, Any]:
        """获取SVM策略的详细信息"""
        base_info = super().get_strategy_info()
        base_info.update(
            {
                "pattern_lookback_periods": self.pattern_lookback_periods,
                "signal_strength_threshold": self.signal_strength_threshold,
                "feature_engineering": "svm_optimized",
                "risk_controls": ["confidence_filtering", "volatility_filter", "rsi_filter", "signal_diversity"],
            }
        )
        return base_info


class SVMConservativeStrategy(SVMTradingStrategy):
    """
    保守型SVM策略

    更严格的信号过滤，更高的置信度要求
    适合风险偏好较低的投资者
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 更保守的参数设置
        self.config.prediction_threshold = 0.75
        self.config.confidence_threshold = 0.85
        self.signal_strength_threshold = 0.9

        logger.info("初始化保守型SVM策略")


class SVMAggressiveStrategy(SVMTradingStrategy):
    """
    激进型SVM策略

    更宽松的信号标准，更早捕捉趋势
    适合风险偏好较高的投资者
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 更激进的参数设置
        self.config.prediction_threshold = 0.55
        self.config.confidence_threshold = 0.65
        self.signal_strength_threshold = 0.7

        logger.info("初始化激进型SVM策略")
