#!/usr/bin/env python3
"""
Decision Tree增强交易策略 (Decision Tree-Enhanced Trading Strategy)

功能说明:
- 基于Decision Tree算法的规则-based交易策略
- 使用随机森林进行模式识别和决策制定
- 结合技术指标构建决策规则
- 提供可解释的交易决策逻辑
- 支持特征重要性分析

策略逻辑:
1. 使用技术指标构建特征空间
2. Decision Tree分类器识别市场状态
3. 基于树模型规则生成交易信号
4. 结合特征重要性进行信号验证

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


class DecisionTreeTradingStrategy(MLTradingStrategy):
    """
    Decision Tree增强交易策略

    使用决策树算法进行规则-based交易决策：
    - 识别上涨趋势 (Buy信号)
    - 识别震荡区间 (Hold信号)
    - 识别下跌趋势 (Sell信号)

    优势：
    - 可解释性强：可以查看决策规则
    - 处理非线性关系：无需特征变换
    - 特征重要性：识别关键交易因子
    - 鲁棒性好：对异常值不敏感
    """

    def __init__(self, **kwargs):
        # Decision Tree特定的配置
        config = MLStrategyConfig(
            algorithm_type="decision_tree",
            prediction_threshold=0.55,  # Decision Tree可能需要更灵活的阈值
            confidence_threshold=0.65,
            algorithm_params={
                "max_depth": 10,
                "min_samples_split": 20,
                "min_samples_leaf": 10,
                "max_features": "sqrt",
                "random_state": 42,
            },
        )

        super().__init__(strategy_name="DecisionTree_Rule_Based", algorithm_type="decision_tree", config=config, **kwargs)

        # Decision Tree特定的参数
        self.feature_importance_threshold = 0.05  # 特征重要性阈值
        self.max_rules_display = 10  # 最大显示规则数
        self.rule_complexity_limit = 5  # 规则复杂度限制

        logger.info("初始化Decision Tree增强交易策略")

    async def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        准备Decision Tree策略的特征工程

        Decision Tree对特征工程要求相对宽松，但仍需要合理的数据预处理
        """
        try:
            df = data.copy()

            # 基础技术指标特征
            df = self.feature_engineer.add_technical_features(df)

            # Decision Tree特定的特征处理
            df = self._add_decision_tree_features(df)

            # 创建目标变量
            df = self.feature_engineer.create_target_variable(df, future_periods=3)  # 较短预测期

            # 清理数据 - Decision Tree对缺失值敏感
            df = df.dropna()

            logger.info(
                f"Decision Tree特征工程完成，生成 {len(df)} 个样本，{len(df.columns) - 1} 个特征"
            )
            return df

        except Exception:
            logger.error("Decision Tree特征工程失败: %(e)s")
            raise

    def _add_decision_tree_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        添加Decision Tree特定的特征

        Decision Tree可以处理非线性特征和交互特征
        """
        df = data.copy()

        # 趋势强度特征
        df["trend_strength"] = abs(df["close"] - df["close"].shift(20)) / df["close"].shift(20)

        # 动量组合特征
        df["momentum_divergence"] = df["momentum_5"] - df["momentum_10"]

        # 波动率趋势
        df["volatility_acceleration"] = df["volatility_10"].diff(5)

        # RSI动量
        df["rsi_momentum"] = df["rsi_14"].diff(3)

        # MACD信号强度
        df["macd_trend"] = np.sign(df["macd"]).diff().fillna(0)

        # 布林带位置 (计算价格在布林带中的位置)
        df["bb_position"] = (df["close"] - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"])

        # 布林带位置动量
        df["bb_position_trend"] = df["bb_position"].diff(3)

        # 成交量比率特征
        if "volume" in df.columns:
            df["volume_ratio"] = df["volume"] / df["volume"].rolling(window=20).mean()
            df["volume_trend"] = df["volume_ratio"].diff(5)

        # 价格区间特征
        df["price_range_ratio"] = (df["high"] - df["low"]) / df["close"]
        df["body_size_ratio"] = abs(df["close"] - df["open"]) / (df["high"] - df["low"])

        # 时间序列特征
        df["day_of_week"] = pd.to_datetime(df.index).dayofweek
        df["month"] = pd.to_datetime(df.index).month

        # 移除可能导致数据泄漏的未来信息
        future_columns = [col for col in df.columns if "future" in col.lower() or "target" in col.lower()]
        for col in future_columns:
            if col in df.columns:
                df = df.drop(columns=[col])

        return df

    async def interpret_ml_signals(self, predictions: List[Dict[str, Any]], data: pd.DataFrame) -> pd.DataFrame:
        """
        解释Decision Tree预测结果为交易信号

        Decision Tree预测结果：
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
                f"Decision Tree预测结果分布: {dict(zip(unique_preds, [pred_classes.count(x) for x in unique_preds]))}"
            )
            logger.info(
                f"Decision Tree置信度范围: {min(pred_confidences):.3f} - {max(pred_confidences):.3f}"
            )
            logger.info(
                f"Decision Tree平均置信度: {sum(pred_confidences) / len(pred_confidences):.3f}"
            )

            signals = []
            signal_counts = {"buy": 0, "hold": 0, "sell": 0}

            for i, pred in enumerate(predictions):
                prediction_class = pred["prediction"]
                confidence = pred["confidence"]

                # Decision Tree信号映射 - 更保守的阈值
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
                else:
                    # 震荡或其他情况
                    signal = 0  # Hold
                    signal_strength = max(0.3, confidence * 0.8)  # 降低持有信号强度
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
                        "ml_model": "decision_tree",
                    }
                )

            logger.info(
                f"信号生成统计: 买入={signal_counts['buy']}, 持有={signal_counts['hold']}, 卖出={signal_counts['sell']}"
            )
            logger.info("置信度阈值: {self.config.confidence_threshold")

            signals_df = pd.DataFrame(signals)
            signals_df.set_index("timestamp", inplace=True)

            # 应用Decision Tree特定的风险控制
            signals_df = self._apply_decision_tree_risk_controls(signals_df, data)

            logger.info("Decision Tree策略生成 {len(signals_df)} 个交易信号")
            return signals_df

        except Exception:
            logger.error("Decision Tree信号解释失败: %(e)s")
            raise

    def _apply_decision_tree_risk_controls(self, signals_df: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
        """
        应用Decision Tree特定的风险控制

        Decision Tree可能对某些市场条件更敏感
        """
        try:
            df = signals_df.copy()

            # 获取基础风险控制
            # pylint: disable=no-member
            df = self._apply_risk_controls(df, data)
            # pylint: enable=no-member

            # Decision Tree特定的额外控制

            # 1. 基于趋势强度的过滤
            if "trend_strength" in data.columns:
                # 在弱趋势市场减少信号
                weak_trend = data["trend_strength"] < data["trend_strength"].quantile(0.3)
                df.loc[weak_trend, "signal_strength"] *= 0.9

                # 在强趋势市场增加信号强度
                strong_trend = data["trend_strength"] > data["trend_strength"].quantile(0.7)
                df.loc[strong_trend & (df["signal"] != 0), "signal_strength"] *= 1.1

            # 2. 基于波动率加速的过滤
            if "volatility_acceleration" in data.columns:
                # 波动率突然增加时减少信号
                vol_acceleration = data["volatility_acceleration"] > data["volatility_acceleration"].quantile(0.8)
                df.loc[vol_acceleration, "signal_strength"] *= 0.8

            # 3. 基于价格区间比例的过滤
            if "price_range_ratio" in data.columns:
                # 高波动日减少信号
                high_volatility_day = data["price_range_ratio"] > data["price_range_ratio"].quantile(0.8)
                df.loc[high_volatility_day, "signal_strength"] *= 0.85

            logger.info("Decision Tree特定风险控制已应用")
            return df

        except Exception:
            logger.warning("Decision Tree风险控制应用失败，使用基础风险控制: %(e)s")
            # pylint: disable=no-member
            return self._apply_risk_controls(signals_df, data)
            # pylint: enable=no-member

    def get_decision_rules(self, max_depth: int = 3) -> Dict[str, Any]:
        """
        提取决策树的决策规则

        这有助于理解模型的决策逻辑
        """
        try:
            # 获取训练好的模型
            if not self.trained_model_key or self.trained_model_key not in self.algorithm_manager.trained_models:
                return {"error": "模型未训练"}

            model_info = self.algorithm_manager.trained_models[self.trained_model_key]
            model = model_info["model"]

            # 这里简化版 - 实际实现需要解析树结构
            rules = {
                "model_type": "Random Forest (Decision Tree Ensemble)",
                "n_estimators": getattr(model, "n_estimators", "Unknown"),
                "max_depth": getattr(model, "max_depth", "Unknown"),
                "feature_importance_available": True,
                "rules_extractable": False,  # 随机森林规则提取复杂
                "interpretation": "Decision Tree提供了特征重要性和规则-based决策，但具体规则需要专业工具提取",
            }

            return rules

        except Exception as e:
            logger.error("决策规则提取失败: %(e)s")
            return {"error": str(e)}

    def get_feature_importance(self) -> Dict[str, Any]:
        """
        获取特征重要性分析
        """
        try:
            if not self.trained_model_key or self.trained_model_key not in self.algorithm_manager.trained_models:
                return {"error": "模型未训练"}

            model_info = self.algorithm_manager.trained_models[self.trained_model_key]
            model = model_info["model"]
            feature_names = model_info["feature_columns"]

            # 获取特征重要性
            if hasattr(model, "feature_importances_"):
                importance_scores = model.feature_importances_
                feature_importance = dict(zip(feature_names, importance_scores))

                # 排序并过滤重要特征
                sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
                top_features = dict(sorted_features[:10])  # Top 10

                return {
                    "feature_importance": feature_importance,
                    "top_features": top_features,
                    "most_important_feature": sorted_features[0][0] if sorted_features else None,
                    "importance_threshold": self.feature_importance_threshold,
                }
            else:
                return {"error": "模型不支持特征重要性分析"}

        except Exception as e:
            logger.error("特征重要性获取失败: %(e)s")
            return {"error": str(e)}

    def get_strategy_info(self) -> Dict[str, Any]:
        """获取Decision Tree策略的详细信息"""
        base_info = super().get_strategy_info()

        # 添加Decision Tree特定信息
        feature_importance = self.get_feature_importance()
        decision_rules = self.get_decision_rules()

        base_info.update(
            {
                "feature_importance_threshold": self.feature_importance_threshold,
                "max_rules_display": self.max_rules_display,
                "rule_complexity_limit": self.rule_complexity_limit,
                "model_interpretability": "high",  # Decision Tree可解释性强
                "feature_importance": feature_importance,
                "decision_rules": decision_rules,
                "algorithm_characteristics": {
                    "handles_nonlinear": True,
                    "feature_scaling_required": False,
                    "outlier_robust": True,
                    "categorical_support": True,
                    "missing_value_handling": "built-in",
                },
            }
        )

        return base_info


class DecisionTreeConservativeStrategy(DecisionTreeTradingStrategy):
    """
    保守型Decision Tree策略

    更严格的参数设置，适合风险偏好较低的投资者
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 更保守的参数
        self.config.prediction_threshold = 0.65
        self.config.confidence_threshold = 0.75
        self.config.algorithm_params.update(
            {
                "max_depth": 5,  # 更浅的树
                "min_samples_split": 30,  # 更高的分割要求
                "min_samples_leaf": 15,  # 更大的叶子节点
            }
        )

        logger.info("初始化保守型Decision Tree策略")


class DecisionTreeAggressiveStrategy(DecisionTreeTradingStrategy):
    """
    激进型Decision Tree策略

    更灵活的参数设置，更早捕捉市场变化
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 更激进的参数
        self.config.prediction_threshold = 0.45
        self.config.confidence_threshold = 0.55
        self.config.algorithm_params.update(
            {
                "max_depth": 15,  # 更深的树
                "min_samples_split": 10,  # 更低的分割要求
                "min_samples_leaf": 5,  # 更小的叶子节点
            }
        )

        logger.info("初始化激进型Decision Tree策略")
