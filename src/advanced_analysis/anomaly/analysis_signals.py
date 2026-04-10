"""异常追踪分析器子模块"""

import logging
from datetime import datetime
from typing import Any, Dict, List

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

from .dataclasses import AnomalyCluster, AnomalyEvent, AnomalyAlert, AnomalyPattern
from src.advanced_analysis import AnalysisResult, AnalysisType
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
