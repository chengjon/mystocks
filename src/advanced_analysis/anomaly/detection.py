"""异常追踪分析器子模块"""

import logging
from datetime import datetime
from typing import List

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

from .dataclasses import AnomalyEvent, AnomalyAlert, GPU_AVAILABLE, IsolationForest
from src.advanced_analysis import BaseAnalyzer, AnalysisResult, AnalysisType
class AnomalyTrackingAnalyzer(BaseAnalyzer):
    """
    异动跟踪分析器

    提供全面的异常检测和跟踪分析，包括：
    - 多维度异常检测（价格、成交量、技术指标）
    - 统计异常值识别和模式识别
    - 实时异常监控和告警
    - 异常聚类和趋势分析
    - 基于异常模式的综合风险评估
    """


def __init__(self, data_manager, gpu_manager=None):
    super().__init__(data_manager, gpu_manager)

    # 异常检测参数
    self.anomaly_params = {
        "zscore_threshold": 3.0,  # Z-score阈值
        "iqr_multiplier": 1.5,  # IQR倍数
        "moving_average_window": 20,  # 移动平均窗口
        "volatility_window": 10,  # 波动率窗口
        "min_anomaly_separation": 5,  # 最小异常间隔
    }

    # 告警配置
    self.alert_configs = {
        "price_spike": AnomalyAlert(
            alert_id="price_spike_alert",
            alert_type="price_anomaly",
            threshold=5.0,  # 5%价格异常
            time_window=5,
            cooldown_period=30,
            enabled=True,
        ),
        "volume_surge": AnomalyAlert(
            alert_id="volume_surge_alert",
            alert_type="volume_anomaly",
            threshold=3.0,  # 3倍成交量
            time_window=10,
            cooldown_period=60,
            enabled=True,
        ),
        "technical_divergence": AnomalyAlert(
            alert_id="technical_divergence_alert",
            alert_type="technical_anomaly",
            threshold=0.8,  # 0.8相关性
            time_window=15,
            cooldown_period=120,
            enabled=True,
        ),
    }

    # 机器学习模型参数
    self.ml_params = {
        "contamination": 0.1,  # 异常比例
        "random_state": 42,
        "n_estimators": 100,  # 孤立森林树数量
        "max_features": 1.0,
    }

    # 分析时间窗口
    self.analysis_windows = {
        "short_term": 1,  # 短期：1天
        "medium_term": 7,  # 中期：7天
        "long_term": 30,  # 长期：30天
    }


def analyze(self, stock_code: str, **kwargs) -> AnalysisResult:
    """
    执行异动跟踪分析

    Args:
        stock_code: 股票代码
        **kwargs: 分析参数
            - analysis_period: 分析周期 (默认: 30天)
            - detection_methods: 检测方法列表 (默认: ['statistical', 'ml', 'pattern'])
            - include_clustering: 是否包含异常聚类 (默认: True)
            - include_alerts: 是否包含告警分析 (默认: True)
            - real_time_monitoring: 是否开启实时监控 (默认: False)

    Returns:
        AnalysisResult: 分析结果
    """
    analysis_period = kwargs.get("analysis_period", 30)
    detection_methods = kwargs.get("detection_methods", ["statistical", "ml", "pattern"])
    include_clustering = kwargs.get("include_clustering", True)
    include_alerts = kwargs.get("include_alerts", True)
    real_time_monitoring = kwargs.get("real_time_monitoring", False)

    try:
        # 获取历史数据
        data = self._get_historical_data(stock_code, days=analysis_period, data_type="1d")
        if data.empty:
            return self._create_error_result(stock_code, "No historical data available for anomaly tracking analysis")

        # 多维度异常检测
        anomalies = []
        for method in detection_methods:
            try:
                if method == "statistical":
                    method_anomalies = self._statistical_anomaly_detection(data)
                elif method == "ml":
                    method_anomalies = self._ml_anomaly_detection(data)
                elif method == "pattern":
                    method_anomalies = self._pattern_anomaly_detection(data)
                else:
                    continue

                anomalies.extend(method_anomalies)
            except Exception as e:
                print(f"Error in {method} anomaly detection: {e}")
                continue

        # 异常去重和排序
        unique_anomalies = self._deduplicate_anomalies(anomalies)
        unique_anomalies.sort(key=lambda x: x.timestamp, reverse=True)

        # 异常聚类分析
        anomaly_clusters = []
        if include_clustering and unique_anomalies:
            anomaly_clusters = self._cluster_anomalies(unique_anomalies)

        # 异常模式分析
        anomaly_patterns = self._analyze_anomaly_patterns(unique_anomalies, data)

        # 告警分析
        active_alerts = []
        if include_alerts:
            active_alerts = self._analyze_active_alerts(unique_anomalies)

        # 计算综合得分
        scores = self._calculate_anomaly_scores(unique_anomalies, anomaly_clusters, anomaly_patterns)

        # 生成信号
        signals = self._generate_anomaly_signals(unique_anomalies, anomaly_clusters, anomaly_patterns, active_alerts)

        # 投资建议
        recommendations = self._generate_anomaly_recommendations(unique_anomalies, anomaly_clusters, anomaly_patterns)

        # 风险评估
        risk_assessment = self._assess_anomaly_risk(unique_anomalies, anomaly_clusters, anomaly_patterns)

        # 元数据
        metadata = {
            "analysis_period_days": analysis_period,
            "detection_methods_used": detection_methods,
            "total_anomalies_detected": len(unique_anomalies),
            "anomalies_last_24h": len([a for a in unique_anomalies if (datetime.now() - a.timestamp).days < 1]),
            "anomalies_last_7d": len([a for a in unique_anomalies if (datetime.now() - a.timestamp).days < 7]),
            "clusters_identified": len(anomaly_clusters),
            "active_alerts": len(active_alerts),
            "real_time_monitoring": real_time_monitoring,
            "analysis_timestamp": datetime.now(),
        }

        return AnalysisResult(
            analysis_type=AnalysisType.ANOMALY_TRACKING,
            stock_code=stock_code,
            timestamp=datetime.now(),
            scores=scores,
            signals=signals,
            recommendations=recommendations,
            risk_assessment=risk_assessment,
            metadata=metadata,
            raw_data=data if kwargs.get("include_raw_data", False) else None,
        )

    except Exception as e:
        return self._create_error_result(stock_code, str(e))


def _statistical_anomaly_detection(self, data: pd.DataFrame) -> List[AnomalyEvent]:
    """统计异常检测"""
    anomalies = []

    try:
        # 价格异常检测
        price_anomalies = self._detect_price_anomalies(data)
        anomalies.extend(price_anomalies)

        # 成交量异常检测
        volume_anomalies = self._detect_volume_anomalies(data)
        anomalies.extend(volume_anomalies)

        # 技术指标异常检测
        technical_anomalies = self._detect_technical_anomalies(data)
        anomalies.extend(technical_anomalies)

        # 价格-成交量背离检测
        divergence_anomalies = self._detect_price_volume_divergence(data)
        anomalies.extend(divergence_anomalies)

    except Exception as e:
        print(f"Error in statistical anomaly detection: {e}")

    return anomalies


def _detect_price_anomalies(self, data: pd.DataFrame) -> List[AnomalyEvent]:
    """检测价格异常"""
    anomalies = []

    try:
        prices = data["close"].values
        timestamps = data.index

        # Z-score异常检测
        z_scores = (prices - np.mean(prices)) / np.std(prices)
        zscore_anomalies = np.abs(z_scores) > self.anomaly_params["zscore_threshold"]

        # IQR异常检测
        Q1 = np.percentile(prices, 25)
        Q3 = np.percentile(prices, 75)
        IQR = Q3 - Q1
        iqr_threshold_upper = Q3 + self.anomaly_params["iqr_multiplier"] * IQR
        iqr_threshold_lower = Q1 - self.anomaly_params["iqr_multiplier"] * IQR

        iqr_anomalies = (prices > iqr_threshold_upper) | (prices < iqr_threshold_lower)

        # 合并异常检测结果
        all_anomalies = zscore_anomalies | iqr_anomalies

        for i, is_anomaly in enumerate(all_anomalies):
            if is_anomaly:
                deviation = abs(z_scores[i])
                severity = "critical" if deviation > 4 else "major" if deviation > 3 else "minor"

                anomaly = AnomalyEvent(
                    event_id=f"price_anomaly_{timestamps[i].strftime('%Y%m%d_%H%M%S')}",
                    timestamp=timestamps[i].to_pydatetime(),
                    anomaly_type="price_anomaly",
                    severity=severity,
                    confidence=min(deviation / 5, 1.0),
                    value=prices[i],
                    expected_value=np.mean(prices),
                    deviation=deviation,
                    description=f"价格异常: {prices[i]:.2f} (期望: {np.mean(prices):.2f})",
                    impact_assessment=self._assess_price_anomaly_impact(deviation),
                    recommended_action=self._get_price_anomaly_action(severity),
                )
                anomalies.append(anomaly)

    except Exception as e:
        print(f"Error detecting price anomalies: {e}")

    return anomalies


def _detect_volume_anomalies(self, data: pd.DataFrame) -> List[AnomalyEvent]:
    """检测成交量异常"""
    anomalies = []

    try:
        volumes = data["volume"].values
        timestamps = data.index

        # 计算移动平均成交量
        volume_ma = pd.Series(volumes).rolling(window=self.anomaly_params["moving_average_window"]).mean()

        # 计算成交量比率
        volume_ratios = volumes / volume_ma.values

        # 识别异常成交量
        for i, ratio in enumerate(volume_ratios):
            if pd.notna(ratio) and ratio > 3.0:  # 成交量超过均值3倍
                severity = "critical" if ratio > 5 else "major" if ratio > 4 else "minor"

                anomaly = AnomalyEvent(
                    event_id=f"volume_anomaly_{timestamps[i].strftime('%Y%m%d_%H%M%S')}",
                    timestamp=timestamps[i].to_pydatetime(),
                    anomaly_type="volume_anomaly",
                    severity=severity,
                    confidence=min(ratio / 10, 1.0),
                    value=volumes[i],
                    expected_value=volume_ma.iloc[i],
                    deviation=ratio,
                    description=f"成交量异常放大: {volumes[i]:.0f} ({ratio:.1f}倍均值)",
                    impact_assessment=self._assess_volume_anomaly_impact(ratio),
                    recommended_action=self._get_volume_anomaly_action(severity),
                )
                anomalies.append(anomaly)

    except Exception as e:
        print(f"Error detecting volume anomalies: {e}")

    return anomalies


def _detect_technical_anomalies(self, data: pd.DataFrame) -> List[AnomalyEvent]:
    """检测技术指标异常"""
    anomalies = []

    try:
        # 计算技术指标
        from src.indicators.indicator_factory import IndicatorFactory

        indicator_factory = IndicatorFactory()

        # RSI异常
        try:
            rsi_calculator = indicator_factory.get_calculator("RSI_14", streaming=False)
            if rsi_calculator:
                rsi_result = rsi_calculator.calculate(data)
                if isinstance(rsi_result, pd.Series):
                    rsi_values = rsi_result.values
                    timestamps = data.index

                    for i, rsi in enumerate(rsi_values):
                        if pd.notna(rsi) and (rsi > 80 or rsi < 20):
                            severity = "minor"
                            description = f"RSI极端值: {rsi:.1f}"

                            anomaly = AnomalyEvent(
                                event_id=f"rsi_anomaly_{timestamps[i].strftime('%Y%m%d_%H%M%S')}",
                                timestamp=timestamps[i].to_pydatetime(),
                                anomaly_type="technical_anomaly",
                                severity=severity,
                                confidence=0.7,
                                value=rsi,
                                expected_value=50,
                                deviation=abs(rsi - 50),
                                description=description,
                                impact_assessment="技术指标显示超买或超卖状态",
                                recommended_action="结合其他指标确认买卖信号",
                            )
                            anomalies.append(anomaly)
        except Exception as e:
            print(f"Error detecting RSI anomalies: {e}")

    except Exception as e:
        print(f"Error detecting technical anomalies: {e}")

    return anomalies


def _detect_price_volume_divergence(self, data: pd.DataFrame) -> List[AnomalyEvent]:
    """检测价格-成交量背离"""
    anomalies = []

    try:
        prices = data["close"].pct_change()
        volumes = data["volume"]

        # 计算相关性
        correlation_window = 10
        correlations = []

        for i in range(correlation_window, len(data)):
            price_window = prices.iloc[i - correlation_window : i]
            volume_window = volumes.iloc[i - correlation_window : i]

            if len(price_window.dropna()) > 5 and len(volume_window.dropna()) > 5:
                corr = price_window.corr(volume_window)
                correlations.append(corr)

        # 检测异常相关性
        if correlations:
            corr_mean = np.mean(correlations)
            corr_std = np.std(correlations)

            for i, corr in enumerate(correlations):
                if abs(corr - corr_mean) > 2 * corr_std:
                    timestamp = data.index[i + correlation_window - 1]

                    anomaly = AnomalyEvent(
                        event_id=f"divergence_anomaly_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                        timestamp=timestamp.to_pydatetime(),
                        anomaly_type="pattern_anomaly",
                        severity="major",
                        confidence=0.8,
                        value=corr,
                        expected_value=corr_mean,
                        deviation=abs(corr - corr_mean),
                        description=f"价格-成交量背离: 相关性 {corr:.2f} (均值: {corr_mean:.2f})",
                        impact_assessment="价格与成交量走势出现背离，可能预示趋势变化",
                        recommended_action="密切关注价格走势确认",
                    )
                    anomalies.append(anomaly)

    except Exception as e:
        print(f"Error detecting price-volume divergence: {e}")

    return anomalies


def _ml_anomaly_detection(self, data: pd.DataFrame) -> List[AnomalyEvent]:
    """机器学习异常检测"""
    anomalies = []

    try:
        if not GPU_AVAILABLE:
            # 使用CPU版本的孤立森林
            features = self._extract_ml_features(data)

            if features.shape[0] > 10:  # 至少需要10个样本
                iso_forest = IsolationForest(
                    contamination=self.ml_params["contamination"],
                    random_state=self.ml_params["random_state"],
                    n_estimators=self.ml_params["n_estimators"],
                )

                # 训练模型
                iso_forest.fit(features)

                # 预测异常
                anomaly_scores = iso_forest.decision_function(features)
                predictions = iso_forest.predict(features)

                # 识别异常点
                for i, (score, prediction) in enumerate(zip(anomaly_scores, predictions)):
                    if prediction == -1:  # 异常点
                        timestamp = data.index[i]

                        anomaly = AnomalyEvent(
                            event_id=f"ml_anomaly_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                            timestamp=timestamp.to_pydatetime(),
                            anomaly_type="ml_anomaly",
                            severity="major" if score < -0.5 else "minor",
                            confidence=min(abs(score), 1.0),
                            value=score,
                            expected_value=0,
                            deviation=abs(score),
                            description=f"机器学习检测异常: 异常分数 {score:.3f}",
                            impact_assessment="算法识别出异常数据点，可能需要人工验证",
                            recommended_action="结合其他指标进行验证",
                        )
                        anomalies.append(anomaly)

    except Exception as e:
        print(f"Error in ML anomaly detection: {e}")

    return anomalies


def _extract_ml_features(self, data: pd.DataFrame) -> np.ndarray:
    """提取机器学习特征"""
    features = []

    # 价格特征
    if "close" in data.columns:
        prices = data["close"].values
        features.extend(
            [
                prices,  # 收盘价
                np.diff(prices, prepend=prices[0]),  # 价格变化
                pd.Series(prices).rolling(window=5).mean().values,  # 5日均线
                pd.Series(prices).rolling(window=20).mean().values,  # 20日均线
            ]
        )

    # 成交量特征
    if "volume" in data.columns:
        volumes = data["volume"].values
        features.extend(
            [
                volumes,  # 成交量
                pd.Series(volumes).rolling(window=5).mean().values,  # 成交量均线
            ]
        )

    # 组合特征
    features_array = np.column_stack([f for f in features if len(f) == len(data)])
    features_array = features_array[~np.isnan(features_array).any(axis=1)]  # 移除NaN

    return features_array


