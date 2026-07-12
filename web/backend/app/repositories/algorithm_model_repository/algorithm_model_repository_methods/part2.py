"""Algorithm Model Repository Layer

提供算法模型数据的数据库访问接口，使用SQLAlchemy ORM操作PostgreSQL
"""

import logging
from datetime import datetime
from typing import Any, Dict

from sqlalchemy.ext.declarative import declarative_base


logger = logging.getLogger(__name__)
Base = declarative_base()


class AlgorithmModelRepositoryValidateDataIntegrityMixin:
    """AlgorithmModelRepository 方法集 Part 2"""

    async def validate_data_integrity(self) -> Dict[str, Any]:
        """执行完整的数据完整性验证

        Returns:
            验证结果报告

        """
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "models": {"total": 0, "valid": 0, "invalid": 0, "errors": []},
                "training_history": {"total": 0, "valid": 0, "invalid": 0, "errors": []},
                "prediction_history": {"total": 0, "valid": 0, "invalid": 0, "errors": []},
                "orphaned_records": {"training": 0, "prediction": 0},
                "overall_status": "unknown",
            }

            # 验证模型数据
            models = self.session.query(AlgorithmModel).all()
            report["models"]["total"] = len(models)

            for model in models:
                model_dict = {
                    "model_id": model.model_id,
                    "algorithm_type": model.algorithm_type,
                    "model_name": model.model_name,
                    "model_version": model.model_version,
                    "model_data": model.model_data,
                    "metadata": model.model_metadata,
                    "training_metrics": model.training_metrics,
                    "is_active": model.is_active,
                    "gpu_trained": model.gpu_trained,
                }

                validation = await self.validate_model_data(model_dict)
                if validation["valid"]:
                    report["models"]["valid"] += 1
                else:
                    report["models"]["invalid"] += 1
                    report["models"]["errors"].extend(validation["errors"])

            # 验证训练历史
            trainings = self.session.query(TrainingHistoryModel).limit(1000).all()
            report["training_history"]["total"] = len(trainings)

            for training in trainings:
                training_dict = {
                    "training_id": training.training_id,
                    "model_id": training.model_id,
                    "algorithm_type": training.algorithm_type,
                    "training_start_time": training.training_start_time,
                    "status": training.status,
                }

                validation = await self.validate_history_data(training_dict, "training")
                if validation["valid"]:
                    report["training_history"]["valid"] += 1
                else:
                    report["training_history"]["invalid"] += 1
                    report["training_history"]["errors"].extend(validation["errors"])

            # 验证预测历史
            predictions = self.session.query(PredictionHistoryModel).limit(1000).all()
            report["prediction_history"]["total"] = len(predictions)

            for prediction in predictions:
                prediction_dict = {
                    "prediction_id": prediction.prediction_id,
                    "model_id": prediction.model_id,
                    "algorithm_type": prediction.algorithm_type,
                    "prediction_time": prediction.prediction_time,
                    "status": prediction.status,
                }

                validation = await self.validate_history_data(prediction_dict, "prediction")
                if validation["valid"]:
                    report["prediction_history"]["valid"] += 1
                else:
                    report["prediction_history"]["invalid"] += 1
                    report["prediction_history"]["errors"].extend(validation["errors"])

            # 检查孤立记录
            orphaned = await self.cleanup_orphaned_history()
            report["orphaned_records"] = orphaned

            # 计算整体状态
            total_valid = (
                report["models"]["valid"] + report["training_history"]["valid"] + report["prediction_history"]["valid"]
            )
            total_invalid = (
                report["models"]["invalid"]
                + report["training_history"]["invalid"]
                + report["prediction_history"]["invalid"]
            )

            if total_invalid == 0:
                report["overall_status"] = "healthy"
            elif total_invalid / (total_valid + total_invalid) < 0.1:
                report["overall_status"] = "warning"
            else:
                report["overall_status"] = "critical"

            logger.info("Data integrity validation completed: {report['overall_status']}")
            return report

        except Exception as e:
            logger.error("Failed to validate data integrity: %(e)s")
            return {"timestamp": datetime.now().isoformat(), "overall_status": "error", "error": str(e)}

