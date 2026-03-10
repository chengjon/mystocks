"""AlgorithmModelRepository 维护类方法集。"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from sqlalchemy.exc import SQLAlchemyError

from .part1 import AlgorithmModel, PredictionHistoryModel, TrainingHistoryModel, logger


class AlgorithmModelRepositoryMaintenanceMixin:
    """模型修复与历史清理方法。"""

    async def repair_model_data(self, model_id: str) -> Dict[str, Any]:
        """修复模型数据的完整性和一致性。"""
        try:
            model = self.session.query(AlgorithmModel).filter_by(model_id=model_id).first()
            if not model:
                return {"repaired": False, "changes": [], "error": "Model not found"}

            changes = []

            if model.model_version is None:
                model.model_version = "1.0.0"
                changes.append("Set default model_version")
            if model.is_active is None:
                model.is_active = True
                changes.append("Set default is_active")
            if model.gpu_trained is None:
                model.gpu_trained = False
                changes.append("Set default gpu_trained")
            if model.created_at is None:
                model.created_at = datetime.now()
                changes.append("Set default created_at")
            if model.updated_at is None:
                model.updated_at = datetime.now()
                changes.append("Set default updated_at")

            for field_name in ["model_data", "metadata", "training_metrics"]:
                field_value = getattr(model, field_name)
                if field_value is not None and not isinstance(field_value, dict):
                    try:
                        if isinstance(field_value, str):
                            import json

                            setattr(model, field_name, json.loads(field_value))
                            changes.append(f"Repaired {field_name} JSON format")
                    except (json.JSONDecodeError, TypeError):
                        setattr(model, field_name, {})
                        changes.append(f"Reset invalid {field_name} to empty object")

            if changes:
                model.updated_at = datetime.now()
                self.session.commit()
                logger.info("Repaired model %(model_id)s: %(changes)s")

            return {"repaired": len(changes) > 0, "changes": changes}

        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error("Failed to repair model %(model_id)s: %(e)s")
            return {"repaired": False, "changes": [], "error": str(e)}

    async def cleanup_orphaned_history(self) -> Dict[str, int]:
        """清理关联模型不存在的历史记录。"""
        try:
            orphaned_trainings = (
                self.session.query(TrainingHistoryModel.training_id)
                .filter(~TrainingHistoryModel.model_id.in_(self.session.query(AlgorithmModel.model_id)))
                .subquery()
            )
            deleted_trainings = (
                self.session.query(TrainingHistoryModel)
                .filter(TrainingHistoryModel.training_id.in_(orphaned_trainings))
                .delete(synchronize_session=False)
            )

            orphaned_predictions = (
                self.session.query(PredictionHistoryModel.prediction_id)
                .filter(~PredictionHistoryModel.model_id.in_(self.session.query(AlgorithmModel.model_id)))
                .subquery()
            )
            deleted_predictions = (
                self.session.query(PredictionHistoryModel)
                .filter(PredictionHistoryModel.prediction_id.in_(orphaned_predictions))
                .delete(synchronize_session=False)
            )

            self.session.commit()
            result = {"training_deleted": deleted_trainings, "prediction_deleted": deleted_predictions}
            logger.info("Cleaned up orphaned history records: %(result)s")
            return result

        except SQLAlchemyError:
            self.session.rollback()
            logger.error("Failed to cleanup orphaned history: %(e)s")
            return {"training_deleted": 0, "prediction_deleted": 0}
