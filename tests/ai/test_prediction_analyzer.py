"""
预测分析器

提供基于机器学习的测试结果预测、趋势分析和风险评估功能。
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, deque
import uuid

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestRegressor
pytest.importorskip("mlflow")
pytest.importorskip("tensorflow")
pytest.importorskip("xgboost")
import mlflow
import mlflow.sklearn
import mlflow.keras

from tests._prediction_analyzer_models import FeatureExtractor, TimeSeriesPredictor

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PredictionModel(Enum):
    """预测模型枚举"""

    LINEAR_REGRESSION = "linear_regression"
    RIDGE_REGRESSION = "ridge_regression"
    LASSO_REGRESSION = "lasso_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    XGBOOST = "xgboost"
    SVR = "svr"
    MLP = "mlp"
    LSTM = "lstm"
    ENSEMBLE = "ensemble"


class PredictionTask(Enum):
    """预测任务枚举"""

    TEST_DURATION = "test_duration"
    PASS_RATE = "pass_rate"
    FAILURE_RATE = "failure_rate"
    RESOURCE_USAGE = "resource_usage"
    COVERAGE_SCORE = "coverage_score"
    MAINTENANCE_BURDEN = "maintenance_burden"
    FLAKINESS_PREDICTION = "flakiness_prediction"


class PredictionConfidence(Enum):
    """预测置信度枚举"""

    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class PredictionRequest:
    """预测请求"""

    task: PredictionTask
    model_type: PredictionModel
    historical_data: List[Dict[str, Any]]
    future_horizon: int  # 预测时间步数
    confidence_threshold: float = 0.8
    features: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PredictionResult:
    """预测结果"""

    request: PredictionRequest
    predictions: List[float]
    confidence: PredictionConfidence
    prediction_interval: Tuple[float, float]
    feature_importance: Dict[str, float]
    model_performance: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)
    model_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    error_message: str = ""


from tests._prediction_analyzer_support import RiskAssessor, demo_prediction_analyzer


class PredictionAnalyzer:
    """预测分析器主类"""

    def __init__(self):
        self.predictors = {}
        self.feature_extractor = FeatureExtractor()
        self.risk_assessor = RiskAssessor()
        self.model_registry = {}
        self.prediction_history = deque(maxlen=1000)

        # MLflow跟踪
        try:
            mlflow.set_tracking_uri("http://localhost:5000")
            mlflow.set_experiment("test_prediction_analyzer")
        except Exception as e:
            logger.warning(f"MLflow连接失败: {e}")

    def register_model(self, model_id: str, model: Any, model_type: PredictionModel):
        """注册模型"""
        self.model_registry[model_id] = {
            "model": model,
            "type": model_type,
            "registered_at": datetime.now(),
            "usage_count": 0,
        }

    def make_prediction(self, request: PredictionRequest) -> PredictionResult:
        """执行预测"""
        logger.info(f"开始预测任务: {request.task.value} 使用模型: {request.model_type.value}")

        try:
            # 验证输入数据
            if not request.historical_data:
                raise ValueError("历史数据不能为空")

            # 提取特征
            features = self.feature_extractor.extract_features(request.historical_data)
            if len(features) == 0:
                raise ValueError("无法提取有效特征")

            # 选择预测器
            predictor_key = f"{request.task.value}_{request.model_type.value}"
            if predictor_key not in self.predictors:
                self.predictors[predictor_key] = TimeSeriesPredictor(request.model_type)

            predictor = self.predictors[predictor_key]

            # 准备目标变量
            target_values = self._extract_target_values(request.historical_data, request.task)
            if len(target_values) < 10:
                raise ValueError(f"用于{request.task.value}的数据不足")

            # 训练模型
            training_metrics = predictor.train(np.array(target_values))

            # 执行预测
            predictions = predictor.predict(request.future_horizon)

            # 计算置信度
            confidence = self._calculate_confidence(predictions, training_metrics)

            # 计算预测区间
            prediction_interval = self._calculate_prediction_interval(predictions, confidence)

            # 特征重要性分析
            feature_importance = self._analyze_feature_importance(features, target_values)

            # 评估模型性能
            model_performance = {
                "mse": training_metrics["mse"],
                "mae": training_metrics["mae"],
                "r2": training_metrics["r2"],
                "training_loss": training_metrics["training_loss"],
            }

            # 创建预测结果
            result = PredictionResult(
                request=request,
                predictions=predictions,
                confidence=confidence,
                prediction_interval=prediction_interval,
                feature_importance=feature_importance,
                model_performance=model_performance,
            )

            # 记录历史
            self.prediction_history.append(
                {
                    "timestamp": datetime.now(),
                    "result": result,
                    "model_type": request.model_type.value,
                    "task": request.task.value,
                }
            )

            # 记录到MLflow
            self._log_to_mlflow(result)

            logger.info(f"预测完成，置信度: {confidence.value}")
            return result

        except Exception as e:
            logger.error(f"预测失败: {e}")
            return PredictionResult(
                request=request,
                predictions=[],
                confidence=PredictionConfidence.VERY_LOW,
                prediction_interval=(0, 0),
                feature_importance={},
                model_performance={},
                error_message=str(e),
            )

    def _extract_target_values(self, historical_data: List[Dict[str, Any]], task: PredictionTask) -> List[float]:
        """提取目标值"""
        target_values = []

        for data_point in historical_data:
            if task == PredictionTask.TEST_DURATION:
                value = data_point.get("duration", 0)
            elif task == PredictionTask.PASS_RATE:
                value = data_point.get("pass_rate", 1.0)
            elif task == PredictionTask.FAILURE_RATE:
                value = data_point.get("failure_rate", 0.0)
            elif task == PredictionTask.RESOURCE_USAGE:
                value = data_point.get("memory_usage", 0) + data_point.get("cpu_usage", 0)
            elif task == PredictionTask.COVERAGE_SCORE:
                value = data_point.get("coverage_score", 0.0)
            elif task == PredictionTask.MAINTENANCE_BURDEN:
                # 维护负担的简化计算
                complexity = data_point.get("complexity_metrics", {}).get("cyclomatic_complexity", 1)
                dependencies = len(data_point.get("dependencies", []))
                value = complexity * 0.5 + dependencies * 0.3
            elif task == PredictionTask.FLAKINESS_PREDICTION:
                value = data_point.get("flakiness_score", 0.0)
            else:
                value = 0

            target_values.append(value)

        return target_values

    def _calculate_confidence(self, predictions: List[float], training_metrics: Dict) -> PredictionConfidence:
        """计算预测置信度"""
        # 基于多个因素计算置信度
        confidence_score = 0.5  # 基础分数

        # 基于R²分数
        if training_metrics["r2"] > 0.8:
            confidence_score += 0.2
        elif training_metrics["r2"] > 0.5:
            confidence_score += 0.1

        # 基于MAE
        if training_metrics["mae"] < 0.1:
            confidence_score += 0.1
        elif training_metrics["mae"] < 0.3:
            confidence_score += 0.05

        # 基于训练损失
        if training_metrics["training_loss"] < 0.1:
            confidence_score += 0.1
        elif training_metrics["training_loss"] < 0.5:
            confidence_score += 0.05

        # 确定置信度等级
        if confidence_score >= 0.8:
            return PredictionConfidence.VERY_HIGH
        elif confidence_score >= 0.65:
            return PredictionConfidence.HIGH
        elif confidence_score >= 0.4:
            return PredictionConfidence.MEDIUM
        elif confidence_score >= 0.2:
            return PredictionConfidence.LOW
        else:
            return PredictionConfidence.VERY_LOW

    def _calculate_prediction_interval(
        self, predictions: List[float], confidence: PredictionConfidence
    ) -> Tuple[float, float]:
        """计算预测区间"""
        if not predictions:
            return (0, 0)

        mean_pred = np.mean(predictions)
        std_pred = np.std(predictions)

        # 根据置信度调整区间宽度
        if confidence == PredictionConfidence.VERY_HIGH:
            interval_multiplier = 1.0
        elif confidence == PredictionConfidence.HIGH:
            interval_multiplier = 1.5
        elif confidence == PredictionConfidence.MEDIUM:
            interval_multiplier = 2.0
        elif confidence == PredictionConfidence.LOW:
            interval_multiplier = 3.0
        else:
            interval_multiplier = 4.0

        lower_bound = mean_pred - (std_pred * interval_multiplier)
        upper_bound = mean_pred + (std_pred * interval_multiplier)

        return (max(0, lower_bound), upper_bound)

    def _analyze_feature_importance(self, features: np.ndarray, target_values: List[float]) -> Dict[str, float]:
        """分析特征重要性"""
        if len(features) < 10:
            return {}

        try:
            # 使用随机森林分析特征重要性
            rf = RandomForestRegressor(n_estimators=100, random_state=42)
            rf.fit(features, target_values)

            feature_names = self.feature_extractor.get_feature_names()
            if feature_names:
                importance_dict = dict(zip(feature_names, rf.feature_importances_))
                return importance_dict
            else:
                # 如果没有特征名称，返回重要性指数
                return {f"feature_{i}": importance for i, importance in enumerate(rf.feature_importances_)}
        except Exception as e:
            logger.error(f"特征重要性分析失败: {e}")
            return {}

    def _log_to_mlflow(self, result: PredictionResult):
        """记录到MLflow"""
        try:
            with mlflow.start_run():
                # 记录参数
                mlflow.log_param("task", result.request.task.value)
                mlflow.log_param("model_type", result.request.model_type.value)
                mlflow.log_param("future_horizon", result.request.future_horizon)
                mlflow.log_param("confidence", result.confidence.value)

                # 记录指标
                mlflow.log_metric("mse", result.model_performance.get("mse", 0))
                mlflow.log_metric("mae", result.model_performance.get("mae", 0))
                mlflow.log_metric("r2", result.model_performance.get("r2", 0))

                # 记录预测结果
                for i, pred in enumerate(result.predictions):
                    mlflow.log_metric(f"prediction_{i}", pred)

                # 记录特征重要性
                for feature, importance in result.feature_importance.items():
                    mlflow.log_metric(f"feature_importance_{feature}", importance)

                # 保存模型（如果需要）
                if result.request.model_type in [
                    PredictionModel.RANDOM_FOREST,
                    PredictionModel.GRADIENT_BOOSTING,
                ]:
                    mlflow.sklearn.log_model(
                        self.predictors.get(f"{result.request.task.value}_{result.request.model_type.value}").model,
                        "prediction_model",
                    )

        except Exception as e:
            logger.warning(f"MLflow记录失败: {e}")

    def batch_predict(self, requests: List[PredictionRequest]) -> List[PredictionResult]:
        """批量预测"""
        results = []

        # 根据模型类型分组
        model_groups = defaultdict(list)
        for req in requests:
            model_key = req.model_type.value
            model_groups[model_key].append(req)

        # 并行处理
        with ThreadPoolExecutor() as executor:
            futures = []

            for model_type, req_list in model_groups.items():
                # 对同一模型类型的请求使用相同的预测器
                for req in req_list:
                    future = executor.submit(self.make_prediction, req)
                    futures.append(future)

            # 收集结果
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"批量预测失败: {e}")

        return results

    def generate_prediction_report(self, results: List[PredictionResult]) -> Dict[str, Any]:
        """生成预测报告"""
        if not results:
            return {}

        # 按任务分组
        task_groups = defaultdict(list)
        for result in results:
            task_groups[result.request.task].append(result)

        report = {
            "generated_at": datetime.now().isoformat(),
            "total_predictions": len(results),
            "by_task": {},
            "summary": {},
            "recommendations": [],
        }

        # 分析每个任务
        for task, task_results in task_groups.items():
            task_summary = {
                "predictions_count": len(task_results),
                "average_confidence": self._calculate_average_confidence(task_results),
                "success_rate": sum(1 for r in task_results if not r.error_message) / len(task_results),
                "average_prediction": np.mean([r.predictions[0] for r in task_results if r.predictions]),
                "trend": self._analyze_prediction_trend(task_results),
            }

            report["by_task"][task.value] = task_summary

        # 总体总结
        all_confidences = [r.confidence for r in results]
        confidence_distribution = {
            "very_high": sum(1 for c in all_confidences if c == PredictionConfidence.VERY_HIGH),
            "high": sum(1 for c in all_confidences if c == PredictionConfidence.HIGH),
            "medium": sum(1 for c in all_confidences if c == PredictionConfidence.MEDIUM),
            "low": sum(1 for c in all_confidences if c == PredictionConfidence.LOW),
            "very_low": sum(1 for c in all_confidences if c == PredictionConfidence.VERY_LOW),
        }

        report["summary"]["confidence_distribution"] = confidence_distribution
        report["summary"]["overall_success_rate"] = sum(1 for r in results if not r.error_message) / len(results)

        # 生成建议
        report["recommendations"] = self._generate_prediction_recommendations(results)

        return report

    def _calculate_average_confidence(self, results: List[PredictionResult]) -> float:
        """计算平均置信度"""
        confidence_scores = {
            PredictionConfidence.VERY_HIGH: 1.0,
            PredictionConfidence.HIGH: 0.8,
            PredictionConfidence.MEDIUM: 0.6,
            PredictionConfidence.LOW: 0.4,
            PredictionConfidence.VERY_LOW: 0.2,
        }

        scores = [confidence_scores[r.confidence] for r in results]
        return sum(scores) / len(scores) if scores else 0

    def _analyze_prediction_trend(self, results: List[PredictionResult]) -> str:
        """分析预测趋势"""
        if len(results) < 2:
            return "insufficient_data"

        # 获取第一个预测值
        first_pred = results[0].predictions[0] if results[0].predictions else 0
        last_pred = results[-1].predictions[0] if results[-1].predictions else 0

        change = (last_pred - first_pred) / first_pred if first_pred != 0 else 0

        if change > 0.1:
            return "increasing"
        elif change < -0.1:
            return "decreasing"
        else:
            return "stable"

    def _generate_prediction_recommendations(self, results: List[PredictionResult]) -> List[str]:
        """生成预测建议"""
        recommendations = []

        # 分析置信度
        low_confidence = [
            r for r in results if r.confidence in [PredictionConfidence.LOW, PredictionConfidence.VERY_LOW]
        ]
        if low_confidence:
            recommendations.append(f"有 {len(low_confidence)} 个预测置信度较低，建议增加历史数据或选择更合适的模型")

        # 分析错误
        error_predictions = [r for r in results if r.error_message]
        if error_predictions:
            recommendations.append(f"有 {len(error_predictions)} 个预测失败，请检查输入数据")

        # 模型建议
        model_usage = defaultdict(int)
        for r in results:
            model_usage[r.request.model_type.value] += 1

        best_model = max(model_usage.items(), key=lambda x: x[1])[0]
        recommendations.append(f"推荐模型 '{best_model}' 在类似任务中使用")

        return recommendations

    def export_predictions(self, results: List[PredictionResult], output_path: str, format: str = "json"):
        """导出预测结果"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == "json":
            data = {"export_timestamp": datetime.now().isoformat(), "predictions": []}

            for result in results:
                pred_data = {
                    "model_id": result.model_id,
                    "task": result.request.task.value,
                    "model_type": result.request.model_type.value,
                    "predictions": result.predictions,
                    "confidence": result.confidence.value,
                    "prediction_interval": result.prediction_interval,
                    "timestamp": result.timestamp.isoformat(),
                    "error_message": result.error_message,
                }

                if result.error_message:
                    pred_data["error"] = result.error_message

                data["predictions"].append(pred_data)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        elif format == "csv":
            # 创建CSV文件
            df_data = []
            for result in results:
                for i, pred in enumerate(result.predictions):
                    df_data.append(
                        {
                            "model_id": result.model_id,
                            "task": result.request.task.value,
                            "model_type": result.request.model_type.value,
                            "step": i + 1,
                            "prediction": pred,
                            "confidence": result.confidence.value,
                            "lower_bound": result.prediction_interval[0],
                            "upper_bound": result.prediction_interval[1],
                            "timestamp": result.timestamp.isoformat(),
                            "error": result.error_message or "",
                        }
                    )

            df = pd.DataFrame(df_data)
            df.to_csv(output_path, index=False)

        logger.info(f"预测结果已导出到: {output_path}")


if __name__ == "__main__":
    demo_prediction_analyzer()
