"""
Anomaly Tracking Analysis Module for MyStocks Advanced Quantitative Analysis
A股量化分析平台异动跟踪分析功能

This module provides comprehensive anomaly detection and tracking including:
- Multi-dimensional anomaly detection (price, volume, technical indicators)
- Statistical outlier identification and pattern recognition
- Real-time anomaly monitoring and alerting
- Anomaly clustering and trend analysis
- Risk assessment based on anomaly patterns
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import warnings

from src.advanced_analysis import BaseAnalyzer, AnalysisResult, AnalysisType

# GPU acceleration support
try:
    import cudf
    import cuml
    from cuml import IsolationForest, OneClassSVM

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    try:
        from sklearn.ensemble import IsolationForest
        from sklearn.svm import OneClassSVM
        from sklearn.preprocessing import StandardScaler
        from scipy.stats import zscore
    except ImportError:
        warnings.warn("Neither GPU nor CPU ML libraries available. Some anomaly detection features will be limited.")


@dataclass
class AnomalyEvent:
    """异常事件数据结构"""

    event_id: str
    timestamp: datetime
    anomaly_type: str  # price_anomaly, volume_anomaly, technical_anomaly, pattern_anomaly
    severity: str  # critical, major, minor, warning
    confidence: float  # 检测置信度 (0-1)
    value: float  # 异常值
    expected_value: float  # 期望值
    deviation: float  # 偏差程度
    description: str  # 异常描述
    impact_assessment: str  # 影响评估
    recommended_action: str  # 建议行动


@dataclass
class AnomalyCluster:
    """异常聚类结果"""

    cluster_id: int
    anomaly_count: int
    cluster_type: str  # price_cluster, volume_cluster, mixed_cluster
    time_span: Tuple[datetime, datetime]  # 异常时间跨度
    severity_distribution: Dict[str, int]  # 严重程度分布
    common_characteristics: List[str]  # 共同特征
    cluster_risk_level: str  # 聚类风险等级


@dataclass
class AnomalyPattern:
    """异常模式分析"""

    pattern_type: str  # sudden_spike, gradual_drift, cyclical_anomaly, clustered_events
    pattern_strength: float  # 模式强度 (0-1)
    pattern_duration: int  # 模式持续时间（天）
    recurrence_probability: float  # 复发概率 (0-1)
    trend_direction: str  # 模式发展趋势
    predictive_value: float  # 预测价值 (0-1)


@dataclass
class AnomalyAlert:
    """异常告警配置"""

    alert_id: str
    alert_type: str
    threshold: float
    time_window: int  # 时间窗口（分钟）
    cooldown_period: int  # 冷却期（分钟）
    enabled: bool
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0


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


def _pattern_anomaly_detection(self, data: pd.DataFrame) -> List[AnomalyEvent]:
    """模式异常检测"""
    anomalies = []

    try:
        # 检测价格跳空
        price_gaps = self._detect_price_gaps(data)
        anomalies.extend(price_gaps)

        # 检测成交量峰值
        volume_spikes = self._detect_volume_spikes(data)
        anomalies.extend(volume_spikes)

        # 检测异常波动率
        volatility_anomalies = self._detect_volatility_anomalies(data)
        anomalies.extend(volatility_anomalies)

    except Exception as e:
        print(f"Error in pattern anomaly detection: {e}")

    return anomalies


def _detect_price_gaps(self, data: pd.DataFrame) -> List[AnomalyEvent]:
    """检测价格跳空"""
    anomalies = []

    try:
        if len(data) < 2:
            return anomalies

        # 计算每日价格区间重叠
        current_high = data["high"]
        current_low = data["low"]
        prev_close = data["close"].shift(1)

        # 上跳空
        gap_up = current_low > prev_close * 1.02  # 跳空幅度>2%
        # 下跳空
        gap_down = current_high < prev_close * 0.98  # 跳空幅度>2%

        gaps = gap_up | gap_down

        for i, is_gap in enumerate(gaps):
            if is_gap:
                timestamp = data.index[i]
                prev_price = prev_close.iloc[i] if i > 0 else data["close"].iloc[i]

                gap_type = "向上跳空" if gap_up.iloc[i] else "向下跳空"
                gap_size = abs(data["close"].iloc[i] - prev_price) / prev_price

                anomaly = AnomalyEvent(
                    event_id=f"gap_anomaly_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                    timestamp=timestamp.to_pydatetime(),
                    anomaly_type="pattern_anomaly",
                    severity="major" if gap_size > 0.05 else "minor",
                    confidence=min(gap_size * 20, 1.0),
                    value=data["close"].iloc[i],
                    expected_value=prev_price,
                    deviation=gap_size,
                    description=f"{gap_type}: {gap_size:.1%} ({data['close'].iloc[i]:.2f} vs {prev_price:.2f})",
                    impact_assessment="价格出现跳空，可能预示重要趋势变化",
                    recommended_action="关注跳空方向的支撑阻力",
                )
                anomalies.append(anomaly)

    except Exception as e:
        print(f"Error detecting price gaps: {e}")

    return anomalies


def _detect_volume_spikes(self, data: pd.DataFrame) -> List[AnomalyEvent]:
    """检测成交量峰值"""
    # 这个方法已经在_detect_volume_anomalies中实现了，这里返回空列表
    return []


def _detect_volatility_anomalies(self, data: pd.DataFrame) -> List[AnomalyEvent]:
    """检测波动率异常"""
    anomalies = []

    try:
        # 计算波动率
        returns = data["close"].pct_change()
        volatility = returns.rolling(window=self.anomaly_params["volatility_window"]).std()

        # 计算波动率Z-score
        vol_mean = volatility.mean()
        vol_std = volatility.std()

        if vol_std > 0:
            vol_zscores = (volatility - vol_mean) / vol_std

            for i, zscore in enumerate(vol_zscores):
                if pd.notna(zscore) and abs(zscore) > 2.0:
                    timestamp = data.index[i]

                    anomaly = AnomalyEvent(
                        event_id=f"volatility_anomaly_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                        timestamp=timestamp.to_pydatetime(),
                        anomaly_type="pattern_anomaly",
                        severity="major" if abs(zscore) > 3 else "minor",
                        confidence=min(abs(zscore) / 4, 1.0),
                        value=volatility.iloc[i],
                        expected_value=vol_mean,
                        deviation=abs(zscore),
                        description=f"波动率异常: {volatility.iloc[i]:.3f} (Z-score: {zscore:.2f})",
                        impact_assessment="波动率显著偏离正常水平",
                        recommended_action="谨慎操作，注意风险控制",
                    )
                    anomalies.append(anomaly)

    except Exception as e:
        print(f"Error detecting volatility anomalies: {e}")

    return anomalies


def _deduplicate_anomalies(self, anomalies: List[AnomalyEvent]) -> List[AnomalyEvent]:
    """异常去重"""
    seen_events = set()
    unique_anomalies = []

    for anomaly in anomalies:
        # 创建唯一标识符
        event_key = (anomaly.timestamp.strftime("%Y%m%d%H%M"), anomaly.anomaly_type)

        if event_key not in seen_events:
            seen_events.add(event_key)
            unique_anomalies.append(anomaly)

    return unique_anomalies


def _cluster_anomalies(self, anomalies: List[AnomalyEvent]) -> List[AnomalyCluster]:
    """异常聚类"""
    if len(anomalies) < 3:
        return []

    try:
        # 按时间和类型聚类
        clusters = []

        # 简单的时间聚类
        sorted_anomalies = sorted(anomalies, key=lambda x: x.timestamp)

        current_cluster = [sorted_anomalies[0]]
        for anomaly in sorted_anomalies[1:]:
            # 如果时间间隔小于1小时，归为同一聚类
            time_diff = (anomaly.timestamp - current_cluster[-1].timestamp).total_seconds() / 3600

            if time_diff < 1:  # 1小时内
                current_cluster.append(anomaly)
            else:
                if len(current_cluster) >= 2:
                    cluster = self._create_anomaly_cluster(current_cluster)
                    clusters.append(cluster)
                current_cluster = [anomaly]

        # 处理最后一个聚类
        if len(current_cluster) >= 2:
            cluster = self._create_anomaly_cluster(current_cluster)
            clusters.append(cluster)

        return clusters

    except Exception as e:
        print(f"Error clustering anomalies: {e}")
        return []


def _create_anomaly_cluster(self, cluster_anomalies: List[AnomalyEvent]) -> AnomalyCluster:
    """创建异常聚类"""
    cluster_id = f"cluster_{cluster_anomalies[0].timestamp.strftime('%Y%m%d%H%M')}"

    # 统计聚类信息
    anomaly_types = [a.anomaly_type for a in cluster_anomalies]
    severities = [a.severity for a in cluster_anomalies]

    # 确定主要类型
    type_counts = {}
    for atype in anomaly_types:
        type_counts[atype] = type_counts.get(atype, 0) + 1

    cluster_type = max(type_counts.keys(), key=lambda x: type_counts[x])

    # 时间跨度
    start_time = min(a.timestamp for a in cluster_anomalies)
    end_time = max(a.timestamp for a in cluster_anomalies)

    # 严重程度分布
    severity_distribution = {}
    for severity in severities:
        severity_distribution[severity] = severity_distribution.get(severity, 0) + 1

    # 共同特征
    common_characteristics = self._extract_common_characteristics(cluster_anomalies)

    # 风险等级
    risk_level = self._assess_cluster_risk(severity_distribution, len(cluster_anomalies))

    return AnomalyCluster(
        cluster_id=int(cluster_id.split("_")[1]),
        anomaly_count=len(cluster_anomalies),
        cluster_type=cluster_type,
        time_span=(start_time, end_time),
        severity_distribution=severity_distribution,
        common_characteristics=common_characteristics,
        cluster_risk_level=risk_level,
    )


def _extract_common_characteristics(self, anomalies: List[AnomalyEvent]) -> List[str]:
    """提取共同特征"""
    characteristics = []

    # 检查是否都是价格异常
    if all(a.anomaly_type == "price_anomaly" for a in anomalies):
        characteristics.append("集中价格异常")

    # 检查是否都是成交量异常
    if all(a.anomaly_type == "volume_anomaly" for a in anomalies):
        characteristics.append("集中成交量异常")

    # 检查严重程度
    high_severity_count = sum(1 for a in anomalies if a.severity in ["critical", "major"])
    if high_severity_count > len(anomalies) * 0.5:
        characteristics.append("高严重程度异常集中")

    return characteristics


def _assess_cluster_risk(self, severity_distribution: Dict[str, int], count: int) -> str:
    """评估聚类风险"""
    critical_count = severity_distribution.get("critical", 0)
    major_count = severity_distribution.get("major", 0)

    high_risk_count = critical_count + major_count

    if high_risk_count > count * 0.5 or critical_count > 0:
        return "high"
    elif high_risk_count > count * 0.3:
        return "medium"
    else:
        return "low"


def _analyze_anomaly_patterns(self, anomalies: List[AnomalyEvent], data: pd.DataFrame) -> List[AnomalyPattern]:
    """分析异常模式"""
    patterns = []

    try:
        if len(anomalies) < 3:
            return patterns

        # 分析异常的时间分布
        timestamps = [a.timestamp for a in anomalies]

        # 计算时间间隔
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i - 1]).total_seconds() / 3600  # 小时
            intervals.append(interval)

        if intervals:
            # 分析间隔模式
            avg_interval = np.mean(intervals)
            interval_std = np.std(intervals)

            # 判断模式类型
            if interval_std < avg_interval * 0.3:
                pattern_type = "regular_intervals"  # 规律间隔
                pattern_strength = 0.8
            elif len([i for i in intervals if i < 24]) > len(intervals) * 0.7:
                pattern_type = "clustered_events"  # 聚集事件
                pattern_strength = 0.9
            else:
                pattern_type = "random_distribution"  # 随机分布
                pattern_strength = 0.3

            # 计算持续时间
            duration = (max(timestamps) - min(timestamps)).total_seconds() / 86400  # 天

            # 趋势方向（基于严重程度的变化）
            severities = [a.confidence for a in anomalies]
            severity_trend = np.polyfit(range(len(severities)), severities, 1)[0]
            trend_direction = "increasing" if severity_trend > 0 else "decreasing" if severity_trend < 0 else "stable"

            # 复发概率（基于历史模式）
            recurrence_probability = min(len(anomalies) / duration * 7, 1.0) if duration > 0 else 0.5

            # 预测价值
            predictive_value = pattern_strength * recurrence_probability

            pattern = AnomalyPattern(
                pattern_type=pattern_type,
                pattern_strength=pattern_strength,
                pattern_duration=int(duration),
                recurrence_probability=recurrence_probability,
                trend_direction=trend_direction,
                predictive_value=predictive_value,
            )
            patterns.append(pattern)

    except Exception as e:
        print(f"Error analyzing anomaly patterns: {e}")

    return patterns


def _analyze_active_alerts(self, anomalies: List[AnomalyEvent]) -> List[AnomalyAlert]:
    """分析活跃告警"""
    active_alerts = []

    try:
        current_time = datetime.now()

        for alert_config in self.alert_configs.values():
            if not alert_config.enabled:
                continue

            # 检查是否在冷却期
            if alert_config.last_triggered:
                cooldown_remaining = (current_time - alert_config.last_triggered).total_seconds() / 60
                if cooldown_remaining < alert_config.cooldown_period:
                    continue

            # 检查是否触发告警条件
            recent_anomalies = [
                a
                for a in anomalies
                if (current_time - a.timestamp).total_seconds() / 60 <= alert_config.time_window
                and a.anomaly_type == alert_config.alert_type
            ]

            if recent_anomalies:
                # 检查阈值条件
                should_trigger = False

                if alert_config.alert_type == "price_anomaly":
                    max_deviation = max(a.deviation for a in recent_anomalies)
                    should_trigger = max_deviation >= alert_config.threshold
                elif alert_config.alert_type == "volume_anomaly":
                    max_deviation = max(a.deviation for a in recent_anomalies)
                    should_trigger = max_deviation >= alert_config.threshold
                elif alert_config.alert_type == "technical_anomaly":
                    # 技术指标告警逻辑
                    should_trigger = len(recent_anomalies) >= 2

                if should_trigger:
                    alert_config.last_triggered = current_time
                    alert_config.trigger_count += 1
                    active_alerts.append(alert_config)

    except Exception as e:
        print(f"Error analyzing active alerts: {e}")

    return active_alerts


def _calculate_anomaly_scores(
    self, anomalies: List[AnomalyEvent], clusters: List[AnomalyCluster], patterns: List[AnomalyPattern]
) -> Dict[str, float]:
    """计算异常分析得分"""
    scores = {}

    try:
        # 异常频率得分
        if anomalies:
            anomaly_frequency = len(anomalies) / 30  # 每月异常次数
            scores["anomaly_frequency"] = min(anomaly_frequency / 10, 1.0)  # 标准化到0-1
        else:
            scores["anomaly_frequency"] = 0.0

        # 异常严重程度得分
        if anomalies:
            severity_scores = {"critical": 1.0, "major": 0.7, "minor": 0.4, "warning": 0.2}
            avg_severity = np.mean([severity_scores.get(a.severity, 0.0) for a in anomalies])
            scores["avg_severity_score"] = avg_severity
        else:
            scores["avg_severity_score"] = 0.0

        # 聚类集中度得分
        if clusters:
            total_anomalies = sum(c.anomaly_count for c in clusters)
            max_cluster_size = max(c.anomaly_count for c in clusters)
            concentration_score = max_cluster_size / total_anomalies if total_anomalies > 0 else 0
            scores["cluster_concentration"] = concentration_score
        else:
            scores["cluster_concentration"] = 0.0

        # 模式识别得分
        if patterns:
            avg_pattern_strength = np.mean([p.pattern_strength for p in patterns])
            scores["pattern_recognition"] = avg_pattern_strength
        else:
            scores["pattern_recognition"] = 0.0

        # 综合风险得分
        weights = {
            "anomaly_frequency": 0.3,
            "avg_severity_score": 0.4,
            "cluster_concentration": 0.2,
            "pattern_recognition": 0.1,
        }

        overall_score = sum(scores.get(key, 0) * weight for key, weight in weights.items())
        scores["overall_risk_score"] = overall_score

    except Exception as e:
        print(f"Error calculating anomaly scores: {e}")
        scores = {"overall_risk_score": 0.0, "error": True}

    return scores


def _generate_anomaly_signals(
    self,
    anomalies: List[AnomalyEvent],
    clusters: List[AnomalyCluster],
    patterns: List[AnomalyPattern],
    alerts: List[AnomalyAlert],
) -> List[Dict[str, Any]]:
    """生成异常信号"""
    signals = []

    # 最新异常信号
    if anomalies:
        latest_anomaly = anomalies[0]  # 已经按时间排序

        severity_map = {"critical": "high", "major": "high", "minor": "medium", "warning": "low"}
        signals.append(
            {
                "type": f"{latest_anomaly.anomaly_type}_detected",
                "severity": severity_map.get(latest_anomaly.severity, "medium"),
                "message": f"检测到{latest_anomaly.anomaly_type}: {latest_anomaly.description}",
                "details": {
                    "anomaly_type": latest_anomaly.anomaly_type,
                    "severity": latest_anomaly.severity,
                    "confidence": latest_anomaly.confidence,
                    "deviation": latest_anomaly.deviation,
                    "impact_assessment": latest_anomaly.impact_assessment,
                    "recommended_action": latest_anomaly.recommended_action,
                },
            }
        )

    # 异常聚类信号
    for cluster in clusters:
        if cluster.cluster_risk_level == "high":
            signals.append(
                {
                    "type": "anomaly_cluster_high_risk",
                    "severity": "high",
                    "message": f"高风险异常聚类: {cluster.cluster_type} ({cluster.anomaly_count}个异常)",
                    "details": {
                        "cluster_type": cluster.cluster_type,
                        "anomaly_count": cluster.anomaly_count,
                        "risk_level": cluster.cluster_risk_level,
                        "time_span": f"{cluster.time_span[0].strftime('%Y-%m-%d')} 至 {cluster.time_span[1].strftime('%Y-%m-%d')}",
                    },
                }
            )

    # 告警信号
    for alert in alerts:
        signals.append(
            {
                "type": f"alert_triggered_{alert.alert_type}",
                "severity": "high",
                "message": f"异常告警触发: {alert.alert_type} (阈值: {alert.threshold})",
                "details": {
                    "alert_type": alert.alert_type,
                    "threshold": alert.threshold,
                    "trigger_count": alert.trigger_count,
                    "last_triggered": alert.last_triggered.isoformat() if alert.last_triggered else None,
                },
            }
        )

    return signals


def _generate_anomaly_recommendations(
    self, anomalies: List[AnomalyEvent], clusters: List[AnomalyCluster], patterns: List[AnomalyPattern]
) -> Dict[str, Any]:
    """生成异常分析建议"""
    recommendations = {}

    try:
        # 评估整体风险水平
        risk_level = "low"
        if anomalies:
            critical_count = sum(1 for a in anomalies if a.severity == "critical")
            major_count = sum(1 for a in anomalies if a.severity == "major")

            if critical_count > 0 or major_count > len(anomalies) * 0.3:
                risk_level = "high"
            elif major_count > 0 or len(anomalies) > 10:
                risk_level = "medium"

        # 生成建议
        if risk_level == "high":
            primary_signal = "high_risk"
            action = "发现多个高风险异常，建议立即停止交易并等待市场稳定"
            confidence = "high"
        elif risk_level == "medium":
            primary_signal = "medium_risk"
            action = "检测到较多异常，建议谨慎操作并加强风险控制"
            confidence = "medium"
        else:
            primary_signal = "low_risk"
            action = "异常情况正常，可按常规策略操作"
            confidence = "low"

        # 模式相关建议
        pattern_insights = []
        if patterns:
            strong_patterns = [p for p in patterns if p.pattern_strength > 0.7]
            if strong_patterns:
                pattern_insights.append("发现强异常模式，建议持续监控")

            recurring_patterns = [p for p in patterns if p.recurrence_probability > 0.7]
            if recurring_patterns:
                pattern_insights.append("异常模式具有复发倾向，需警惕")

        # 聚类相关建议
        cluster_insights = []
        if clusters:
            high_risk_clusters = [c for c in clusters if c.cluster_risk_level == "high"]
            if high_risk_clusters:
                cluster_insights.append(f"发现{len(high_risk_clusters)}个高风险异常聚类")

        recommendations.update(
            {
                "primary_signal": primary_signal,
                "recommended_action": action,
                "confidence_level": confidence,
                "risk_level": risk_level,
                "anomaly_summary": {
                    "total_anomalies": len(anomalies),
                    "critical_count": sum(1 for a in anomalies if a.severity == "critical"),
                    "clusters_count": len(clusters),
                    "patterns_count": len(patterns),
                },
                "key_insights": pattern_insights + cluster_insights,
                "monitoring_suggestions": (
                    [
                        "持续监控新异常的发生频率",
                        "关注异常模式的演变趋势",
                        "及时调整风险控制参数",
                    ]
                    if risk_level in ["medium", "high"]
                    else []
                ),
            }
        )

    except Exception as e:
        print(f"Error generating anomaly recommendations: {e}")
        recommendations = {
            "primary_signal": "unknown",
            "recommended_action": "分析过程中出现错误，建议观望",
            "confidence_level": "low",
        }

    return recommendations


def _assess_anomaly_risk(
    self, anomalies: List[AnomalyEvent], clusters: List[AnomalyCluster], patterns: List[AnomalyPattern]
) -> Dict[str, Any]:
    """评估异常风险"""
    risk_assessment = {}

    try:
        # 计算异常密度
        if anomalies:
            # 假设30天分析周期
            anomaly_density = len(anomalies) / 30
            density_risk = "high" if anomaly_density > 1 else "medium" if anomaly_density > 0.5 else "low"
        else:
            density_risk = "low"

        # 异常严重程度分布
        severity_distribution = {}
        if anomalies:
            for anomaly in anomalies:
                severity_distribution[anomaly.severity] = severity_distribution.get(anomaly.severity, 0) + 1

        # 聚类风险
        cluster_risk = "low"
        if clusters:
            high_risk_clusters = sum(1 for c in clusters if c.cluster_risk_level == "high")
            if high_risk_clusters > len(clusters) * 0.5:
                cluster_risk = "high"
            elif high_risk_clusters > 0:
                cluster_risk = "medium"

        # 模式风险
        pattern_risk = "low"
        if patterns:
            strong_patterns = sum(1 for p in patterns if p.pattern_strength > 0.8)
            if strong_patterns > 0:
                pattern_risk = "medium"
                if any(p.recurrence_probability > 0.8 for p in patterns):
                    pattern_risk = "high"

        # 综合风险等级
        risk_scores = {"high": 3, "medium": 2, "low": 1}
        avg_risk_score = np.mean(
            [risk_scores.get(density_risk, 1), risk_scores.get(cluster_risk, 1), risk_scores.get(pattern_risk, 1)]
        )

        overall_risk = "high" if avg_risk_score > 2.5 else "medium" if avg_risk_score > 1.5 else "low"

        risk_assessment.update(
            {
                "overall_risk_level": overall_risk,
                "anomaly_density_risk": density_risk,
                "cluster_risk": cluster_risk,
                "pattern_risk": pattern_risk,
                "severity_distribution": severity_distribution,
                "risk_factors": [
                    "异常发生频率过高" if density_risk == "high" else None,
                    "异常聚类风险显著" if cluster_risk == "high" else None,
                    "异常模式反复出现" if pattern_risk == "high" else None,
                ],
                "risk_factors": [
                    f
                    for f in [
                        "异常发生频率过高" if density_risk == "high" else None,
                        "异常聚类风险显著" if cluster_risk == "high" else None,
                        "异常模式反复出现" if pattern_risk == "high" else None,
                    ]
                    if f is not None
                ],
            }
        )

    except Exception as e:
        print(f"Error assessing anomaly risk: {e}")
        risk_assessment = {"overall_risk_level": "unknown", "error": str(e)}

    return risk_assessment


def _assess_price_anomaly_impact(self, deviation: float) -> str:
    """评估价格异常影响"""
    if deviation > 4:
        return "极度异常，可能预示重大市场事件"
    elif deviation > 3:
        return "严重异常，需要密切关注"
    else:
        return "一般异常，可结合其他指标判断"


def _get_price_anomaly_action(self, severity: str) -> str:
    """获取价格异常建议行动"""
    actions = {
        "critical": "立即检查市场新闻，考虑调整仓位",
        "major": "密切关注价格走势，准备应对措施",
        "minor": "记录异常情况，继续正常监控",
    }
    return actions.get(severity, "继续观察")


def _assess_volume_anomaly_impact(self, ratio: float) -> str:
    """评估成交量异常影响"""
    if ratio > 5:
        return "成交量极度放大，可能伴随重要市场动向"
    elif ratio > 3:
        return "成交量显著放大，值得关注"
    else:
        return "成交量 moderately 放大，正常波动范围"


def _get_volume_anomaly_action(self, severity: str) -> str:
    """获取成交量异常建议行动"""
    actions = {
        "critical": "重点关注价格走势，成交量异常可能是重要信号",
        "major": "结合技术指标分析成交量变化原因",
        "minor": "记录成交量变化，继续常规分析",
    }
    return actions.get(severity, "继续观察")


def _create_error_result(self, stock_code: str, error_msg: str) -> AnalysisResult:
    """创建错误结果"""
    return AnalysisResult(
        analysis_type=AnalysisType.ANOMALY_TRACKING,
        stock_code=stock_code,
        timestamp=datetime.now(),
        scores={"error": True},
        signals=[{"type": "analysis_error", "severity": "high", "message": f"异动跟踪分析失败: {error_msg}"}],
        recommendations={"error": error_msg},
        risk_assessment={"error": True},
        metadata={"error": True, "error_message": error_msg},
    )
