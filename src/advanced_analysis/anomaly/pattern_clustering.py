"""异常追踪分析器子模块"""

import logging
from typing import Dict, List

import pandas as pd

logger = logging.getLogger(__name__)

from .dataclasses import AnomalyEvent, AnomalyCluster
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


