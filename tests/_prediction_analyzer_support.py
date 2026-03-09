"""Support utilities extracted from ``tests.ai.test_prediction_analyzer``."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
import random
from typing import Any, Dict, List

import numpy as np

logger = logging.getLogger(__name__)


class RiskAssessor:
    """风险评估器"""

    def __init__(self):
        self.risk_thresholds = {"critical": 0.8, "high": 0.6, "medium": 0.4, "low": 0.2}
        self.historical_risks = []

    def assess_test_risk(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """评估测试风险"""
        risk_score = 0
        risk_factors = []

        if "failure_history" in test_data:
            failure_rate = test_data["failure_history"].get("failure_rate", 0)
            risk_score += failure_rate * 0.3
            risk_factors.append(f"历史失败率: {failure_rate:.2%}")

        if "duration" in test_data:
            duration = test_data["duration"]
            if duration > 10:
                risk_score += 0.2
                risk_factors.append(f"执行时间过长: {duration:.2f}s")
            elif duration > 5:
                risk_score += 0.1
                risk_factors.append(f"执行时间较长: {duration:.2f}s")

        if "memory_usage" in test_data and "cpu_usage" in test_data:
            memory_score = min(test_data["memory_usage"] / 1000, 1.0)
            cpu_score = min(test_data["cpu_usage"] / 100, 1.0)
            resource_risk = (memory_score + cpu_score) / 2 * 0.2
            risk_score += resource_risk
            risk_factors.append(f"资源使用风险: {resource_risk:.2f}")

        if "complexity_metrics" in test_data:
            complexity = test_data["complexity_metrics"]
            if complexity.get("cyclomatic_complexity", 0) > 20:
                risk_score += 0.15
                risk_factors.append(f"圈复杂度过高: {complexity['cyclomatic_complexity']}")
            if complexity.get("cognitive_complexity", 0) > 15:
                risk_score += 0.15
                risk_factors.append(f"认知复杂度过高: {complexity['cognitive_complexity']}")

        if "dependencies" in test_data:
            deps = test_data["dependencies"]
            unstable_deps = sum(1 for dep in deps if dep.get("stability", 1.0) < 0.7)
            if unstable_deps > 0:
                risk_score += unstable_deps * 0.1
                risk_factors.append(f"不稳定依赖: {unstable_deps}")

        risk_level = "low"
        for level, threshold in self.risk_thresholds.items():
            if risk_score >= threshold:
                risk_level = level
                break

        return {
            "risk_score": min(risk_score, 1.0),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "timestamp": datetime.now(),
        }

    def predict_future_risks(self, historical_risks: List[Dict]) -> List[Dict[str, Any]]:
        """预测未来风险"""
        predictions = []
        if len(historical_risks) < 5:
            return predictions

        risk_scores = [risk["risk_score"] for risk in historical_risks]
        if len(risk_scores) >= 3:
            trend = np.polyfit(range(len(risk_scores)), risk_scores, 1)[0]
            for index in range(1, 4):
                predicted_score = max(0, min(1, risk_scores[-1] + trend * index + np.random.normal(0, 0.1)))
                risk_level = "low"
                for level, threshold in self.risk_thresholds.items():
                    if predicted_score >= threshold:
                        risk_level = level
                        break
                predictions.append(
                    {
                        "step": index,
                        "predicted_risk_score": predicted_score,
                        "risk_level": risk_level,
                        "confidence": "medium" if abs(trend) < 0.1 else ("low" if abs(trend) > 0.2 else "high"),
                        "timestamp": datetime.now() + timedelta(days=index),
                    }
                )

        return predictions

    def generate_risk_mitigation_plan(self, risk_assessment: Dict) -> List[str]:
        """生成风险缓解计划"""
        mitigation_plan = []
        risk_level = risk_assessment["risk_level"]
        risk_factors = risk_assessment["risk_factors"]

        if risk_level == "critical":
            mitigation_plan.extend(["立即暂停相关测试", "进行全面代码审查", "增加监控频率", "准备回滚计划"])

        for factor in risk_factors:
            if "失败率" in factor:
                mitigation_plan.append("分析失败原因并修复")
            elif "执行时间" in factor:
                mitigation_plan.append("优化测试性能或拆分测试")
            elif "资源使用" in factor:
                mitigation_plan.append("优化资源使用或增加资源")
            elif "复杂度" in factor:
                mitigation_plan.append("重构代码降低复杂度")
            elif "依赖" in factor:
                mitigation_plan.append("更新或替换不稳定依赖")

        mitigation_plan.extend(["增加测试覆盖率", "添加自动化监控", "建立预警机制", "定期风险评审"])
        return list(set(mitigation_plan))


def demo_prediction_analyzer():
    """演示预测分析器功能"""
    from tests.ai.test_prediction_analyzer import (
        PredictionAnalyzer,
        PredictionModel,
        PredictionRequest,
        PredictionTask,
    )

    logger.info("🚀 演示预测分析器功能")
    analyzer = PredictionAnalyzer()
    historical_data = []
    base_time = datetime.now() - timedelta(days=30)

    for index in range(30):
        timestamp = base_time + timedelta(days=index)
        historical_data.append(
            {
                "timestamp": timestamp.isoformat(),
                "duration": 5.0 + random.gauss(0, 1) + index * 0.1,
                "memory_usage": 50 + random.gauss(0, 10),
                "cpu_usage": 30 + random.gauss(0, 5),
                "pass_rate": 0.9 + random.gauss(0, 0.05),
                "coverage_score": 0.85 + random.gauss(0, 0.02),
            }
        )

    requests = [
        PredictionRequest(
            task=PredictionTask.TEST_DURATION,
            model_type=PredictionModel.RANDOM_FOREST,
            historical_data=historical_data,
            future_horizon=7,
            confidence_threshold=0.8,
        ),
        PredictionRequest(
            task=PredictionTask.PASS_RATE,
            model_type=PredictionModel.LSTM,
            historical_data=historical_data,
            future_horizon=5,
            confidence_threshold=0.7,
        ),
        PredictionRequest(
            task=PredictionTask.RESOURCE_USAGE,
            model_type=PredictionModel.XGBOOST,
            historical_data=historical_data,
            future_horizon=10,
            confidence_threshold=0.6,
        ),
    ]

    results = analyzer.batch_predict(requests)
    logger.info("📊 预测结果:")
    for index, result in enumerate(results):
        logger.info("预测 %s:", index + 1)
        logger.info("  任务: %s", result.request.task.value)
        logger.info("  模型: %s", result.request.model_type.value)
        logger.info("  置信度: %s", result.confidence.value)
        logger.info(
            "  预测区间: %.2f - %.2f",
            result.prediction_interval[0],
            result.prediction_interval[1],
        )
        logger.info("  未来7天预测: %s", result.predictions[:7])
        if result.error_message:
            logger.info("  错误: %s", result.error_message)

    report = analyzer.generate_prediction_report(results)
    logger.info("📈 预测报告:")
    logger.info("  总预测数: %s", report["summary"]["total_predictions"])
    logger.info("  成功率: %.2f%%", report["summary"]["overall_success_rate"] * 100)

    if "recommendations" in report:
        logger.info("💡 建议:")
        for recommendation in report["recommendations"]:
            logger.info("  - %s", recommendation)

    analyzer.export_predictions(results, "prediction_results.json", "json")
    analyzer.export_predictions(results, "prediction_results.csv", "csv")


__all__ = ["RiskAssessor", "demo_prediction_analyzer"]
