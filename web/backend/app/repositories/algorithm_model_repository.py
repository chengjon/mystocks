"""
Algorithm Model Repository Layer

提供算法模型数据的数据库访问接口，使用SQLAlchemy ORM操作PostgreSQL
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    TIMESTAMP,
    Boolean,
    Column,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
Base = declarative_base()


# ============================================================
# SQLAlchemy ORM Models
# ============================================================


class AlgorithmModel(Base):
    """算法模型表ORM模型"""

    __tablename__ = "algorithm_models"

    model_id = Column(String(100), primary_key=True, comment="模型唯一ID")
    algorithm_type = Column(String(50), nullable=False, comment="算法类型")
    model_name = Column(String(200), nullable=False, comment="模型名称")
    model_version = Column(String(20), default="1.0.0", comment="模型版本")
    model_data = Column(JSON, comment="模型参数和权重数据")
    model_metadata = Column(JSON, comment="模型元数据")
    training_metrics = Column(JSON, comment="训练指标")
    symbol = Column(String(20), comment="关联股票代码")
    features = Column(JSON, comment="使用的特征列表")
    is_active = Column(Boolean, default=True, comment="是否激活")
    gpu_trained = Column(Boolean, default=False, comment="是否使用GPU训练")
    created_at = Column(TIMESTAMP, default=datetime.now, comment="创建时间")
    updated_at = Column(TIMESTAMP, default=datetime.now, comment="更新时间")

    # 索引
    __table_args__ = (
        Index("idx_algorithm_models_type", "algorithm_type"),
        Index("idx_algorithm_models_symbol", "symbol"),
        Index("idx_algorithm_models_active", "is_active"),
        Index("idx_algorithm_models_created", "created_at"),
    )


class TrainingHistoryModel(Base):
    """训练历史表ORM模型"""

    __tablename__ = "training_history"

    training_id = Column(String(100), primary_key=True, comment="训练记录唯一ID")
    model_id = Column(String(100), nullable=False, comment="关联模型ID")
    algorithm_type = Column(String(50), nullable=False, comment="算法类型")
    training_start_time = Column(TIMESTAMP, nullable=False, comment="训练开始时间")
    training_end_time = Column(TIMESTAMP, comment="训练结束时间")
    training_duration_ms = Column(Integer, comment="训练耗时(毫秒)")
    status = Column(String(20), nullable=False, comment="训练状态")
    symbol = Column(String(20), comment="训练股票代码")
    features = Column(JSON, comment="使用的特征列表")
    training_config = Column(JSON, comment="训练配置参数")
    training_metrics = Column(JSON, comment="训练指标结果")
    validation_metrics = Column(JSON, comment="验证指标结果")
    error_message = Column(Text, comment="错误信息")
    gpu_used = Column(Boolean, default=False, comment="是否使用GPU")
    data_sample_count = Column(Integer, comment="训练样本数量")
    created_at = Column(TIMESTAMP, default=datetime.now, comment="记录创建时间")

    # 索引
    __table_args__ = (
        Index("idx_training_history_model", "model_id"),
        Index("idx_training_history_type", "algorithm_type"),
        Index("idx_training_history_status", "status"),
        Index("idx_training_history_symbol", "symbol"),
        Index("idx_training_history_time", "training_start_time"),
    )


class PredictionHistoryModel(Base):
    """预测历史表ORM模型"""

    __tablename__ = "prediction_history"

    prediction_id = Column(String(100), primary_key=True, comment="预测记录唯一ID")
    model_id = Column(String(100), nullable=False, comment="使用的模型ID")
    algorithm_type = Column(String(50), nullable=False, comment="算法类型")
    prediction_time = Column(TIMESTAMP, nullable=False, comment="预测执行时间")
    processing_time_ms = Column(Integer, comment="预测处理耗时(毫秒)")
    status = Column(String(20), nullable=False, comment="预测状态")
    input_data = Column(JSON, comment="输入数据")
    prediction_result = Column(JSON, comment="预测结果")
    confidence_score = Column(Numeric(5, 4), comment="置信度分数")
    error_message = Column(Text, comment="错误信息")
    gpu_used = Column(Boolean, default=False, comment="是否使用GPU")
    batch_size = Column(Integer, comment="批量预测大小")
    created_at = Column(TIMESTAMP, default=datetime.now, comment="记录创建时间")

    # 索引
    __table_args__ = (
        Index("idx_prediction_history_model", "model_id"),
        Index("idx_prediction_history_type", "algorithm_type"),
        Index("idx_prediction_history_status", "status"),
        Index("idx_prediction_history_time", "prediction_time"),
    )


# ============================================================
# Repository Classes
# ============================================================


class AlgorithmModelRepository:
    """
    算法模型数据访问仓库

    提供算法模型、训练历史、预测历史的数据库操作接口
    """

    def __init__(self, session: Session):
        self.session = session

    # ==================== 模型管理方法 ====================

    async def save_model(self, model_data: Dict[str, Any]) -> bool:
        """
        保存算法模型到数据库

        Args:
            model_data: 模型数据字典

        Returns:
            保存是否成功
        """
        try:
            model = AlgorithmModel(**model_data)
            model.updated_at = datetime.now()

            self.session.add(model)
            self.session.commit()

            logger.info("Saved algorithm model: {model.model_id}")
            return True

        except SQLAlchemyError:
            self.session.rollback()
            logger.error("Failed to save algorithm model: %(e)s")
            return False

    async def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取算法模型

        Args:
            model_id: 模型ID

        Returns:
            模型数据字典或None
        """
        try:
            model = self.session.query(AlgorithmModel).filter_by(model_id=model_id).first()
            if model:
                return {
                    "model_id": model.model_id,
                    "algorithm_type": model.algorithm_type,
                    "model_name": model.model_name,
                    "model_version": model.model_version,
                    "model_data": model.model_data,
                    "metadata": model.model_metadata,
                    "training_metrics": model.training_metrics,
                    "symbol": model.symbol,
                    "features": model.features,
                    "is_active": model.is_active,
                    "gpu_trained": model.gpu_trained,
                    "created_at": model.created_at,
                    "updated_at": model.updated_at,
                }
            return None

        except SQLAlchemyError:
            logger.error("Failed to get algorithm model %(model_id)s: %(e)s")
            return None

    async def update_model(self, model_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新算法模型信息

        Args:
            model_id: 模型ID
            updates: 更新数据

        Returns:
            更新是否成功
        """
        try:
            updates["updated_at"] = datetime.now()

            result = self.session.query(AlgorithmModel).filter_by(model_id=model_id).update(updates)
            self.session.commit()

            if result > 0:
                logger.info("Updated algorithm model: %(model_id)s")
                return True
            return False

        except SQLAlchemyError:
            self.session.rollback()
            logger.error("Failed to update algorithm model %(model_id)s: %(e)s")
            return False

    async def delete_model(self, model_id: str) -> bool:
        """
        删除算法模型

        Args:
            model_id: 模型ID

        Returns:
            删除是否成功
        """
        try:
            result = self.session.query(AlgorithmModel).filter_by(model_id=model_id).delete()
            self.session.commit()

            if result > 0:
                logger.info("Deleted algorithm model: %(model_id)s")
                return True
            return False

        except SQLAlchemyError:
            self.session.rollback()
            logger.error("Failed to delete algorithm model %(model_id)s: %(e)s")
            return False

    async def list_models(
        self, algorithm_type: Optional[str] = None, symbol: Optional[str] = None, is_active: bool = True
    ) -> List[Dict[str, Any]]:
        """
        列出算法模型

        Args:
            algorithm_type: 算法类型过滤
            symbol: 股票代码过滤
            is_active: 是否只返回激活的模型

        Returns:
            模型列表
        """
        try:
            query = self.session.query(AlgorithmModel)

            if algorithm_type:
                query = query.filter_by(algorithm_type=algorithm_type)
            if symbol:
                query = query.filter_by(symbol=symbol)
            if is_active is not None:
                query = query.filter_by(is_active=is_active)

            query = query.order_by(AlgorithmModel.created_at.desc())

            models = query.all()
            return [
                {
                    "model_id": model.model_id,
                    "algorithm_type": model.algorithm_type,
                    "model_name": model.model_name,
                    "model_version": model.model_version,
                    "symbol": model.symbol,
                    "is_active": model.is_active,
                    "gpu_trained": model.gpu_trained,
                    "created_at": model.created_at,
                    "updated_at": model.updated_at,
                }
                for model in models
            ]

        except SQLAlchemyError:
            logger.error("Failed to list algorithm models: %(e)s")
            return []

    # ==================== 训练历史管理方法 ====================

    async def save_training_history(self, history_data: Dict[str, Any]) -> bool:
        """
        保存训练历史记录

        Args:
            history_data: 训练历史数据

        Returns:
            保存是否成功
        """
        try:
            history = TrainingHistoryModel(**history_data)
            self.session.add(history)
            self.session.commit()

            logger.info("Saved training history: {history.training_id}")
            return True

        except SQLAlchemyError:
            self.session.rollback()
            logger.error("Failed to save training history: %(e)s")
            return False

    async def get_training_history(self, training_id: str) -> Optional[Dict[str, Any]]:
        """
        获取训练历史记录

        Args:
            training_id: 训练记录ID

        Returns:
            训练历史数据或None
        """
        try:
            history = self.session.query(TrainingHistoryModel).filter_by(training_id=training_id).first()
            if history:
                return {
                    "training_id": history.training_id,
                    "model_id": history.model_id,
                    "algorithm_type": history.algorithm_type,
                    "training_start_time": history.training_start_time,
                    "training_end_time": history.training_end_time,
                    "training_duration_ms": history.training_duration_ms,
                    "status": history.status,
                    "symbol": history.symbol,
                    "features": history.features,
                    "training_config": history.training_config,
                    "training_metrics": history.training_metrics,
                    "validation_metrics": history.validation_metrics,
                    "error_message": history.error_message,
                    "gpu_used": history.gpu_used,
                    "data_sample_count": history.data_sample_count,
                    "created_at": history.created_at,
                }
            return None

        except SQLAlchemyError:
            logger.error("Failed to get training history %(training_id)s: %(e)s")
            return None

    async def list_training_history(
        self, model_id: Optional[str] = None, algorithm_type: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        列出训练历史记录

        Args:
            model_id: 模型ID过滤
            algorithm_type: 算法类型过滤
            limit: 返回记录数量限制

        Returns:
            训练历史列表
        """
        try:
            query = self.session.query(TrainingHistoryModel)

            if model_id:
                query = query.filter_by(model_id=model_id)
            if algorithm_type:
                query = query.filter_by(algorithm_type=algorithm_type)

            query = query.order_by(TrainingHistoryModel.training_start_time.desc()).limit(limit)

            histories = query.all()
            return [
                {
                    "training_id": history.training_id,
                    "model_id": history.model_id,
                    "algorithm_type": history.algorithm_type,
                    "training_start_time": history.training_start_time,
                    "status": history.status,
                    "training_duration_ms": history.training_duration_ms,
                    "gpu_used": history.gpu_used,
                    "data_sample_count": history.data_sample_count,
                }
                for history in histories
            ]

        except SQLAlchemyError:
            logger.error("Failed to list training history: %(e)s")
            return []

    # ==================== 预测历史管理方法 ====================

    async def save_prediction_history(self, history_data: Dict[str, Any]) -> bool:
        """
        保存预测历史记录

        Args:
            history_data: 预测历史数据

        Returns:
            保存是否成功
        """
        try:
            history = PredictionHistoryModel(**history_data)
            self.session.add(history)
            self.session.commit()

            logger.info("Saved prediction history: {history.prediction_id}")
            return True

        except SQLAlchemyError:
            self.session.rollback()
            logger.error("Failed to save prediction history: %(e)s")
            return False

    async def get_prediction_history(self, prediction_id: str) -> Optional[Dict[str, Any]]:
        """
        获取预测历史记录

        Args:
            prediction_id: 预测记录ID

        Returns:
            预测历史数据或None
        """
        try:
            history = self.session.query(PredictionHistoryModel).filter_by(prediction_id=prediction_id).first()
            if history:
                return {
                    "prediction_id": history.prediction_id,
                    "model_id": history.model_id,
                    "algorithm_type": history.algorithm_type,
                    "prediction_time": history.prediction_time,
                    "processing_time_ms": history.processing_time_ms,
                    "status": history.status,
                    "input_data": history.input_data,
                    "prediction_result": history.prediction_result,
                    "confidence_score": history.confidence_score,
                    "error_message": history.error_message,
                    "gpu_used": history.gpu_used,
                    "batch_size": history.batch_size,
                    "created_at": history.created_at,
                }
            return None

        except SQLAlchemyError:
            logger.error("Failed to get prediction history %(prediction_id)s: %(e)s")
            return None

    async def list_prediction_history(
        self, model_id: Optional[str] = None, algorithm_type: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        列出预测历史记录

        Args:
            model_id: 模型ID过滤
            algorithm_type: 算法类型过滤
            limit: 返回记录数量限制

        Returns:
            预测历史列表
        """
        try:
            query = self.session.query(PredictionHistoryModel)

            if model_id:
                query = query.filter_by(model_id=model_id)
            if algorithm_type:
                query = query.filter_by(algorithm_type=algorithm_type)

            query = query.order_by(PredictionHistoryModel.prediction_time.desc()).limit(limit)

            histories = query.all()
            return [
                {
                    "prediction_id": history.prediction_id,
                    "model_id": history.model_id,
                    "algorithm_type": history.algorithm_type,
                    "prediction_time": history.prediction_time,
                    "status": history.status,
                    "processing_time_ms": history.processing_time_ms,
                    "confidence_score": history.confidence_score,
                    "gpu_used": history.gpu_used,
                }
                for history in histories
            ]

        except SQLAlchemyError:
            logger.error("Failed to list prediction history: %(e)s")
            return []

    # ==================== 统计和监控方法 ====================

    async def get_model_statistics(self) -> Dict[str, Any]:
        """
        获取模型统计信息

        Returns:
            统计数据字典
        """
        try:
            # 模型总数
            total_models = self.session.query(AlgorithmModel).count()

            # 激活模型数
            active_models = self.session.query(AlgorithmModel).filter_by(is_active=True).count()

            # GPU训练模型数
            gpu_trained_models = self.session.query(AlgorithmModel).filter_by(gpu_trained=True).count()

            # 算法类型分布
            from sqlalchemy import func

            algorithm_counts = (
                self.session.query(AlgorithmModel.algorithm_type, func.count(AlgorithmModel.model_id).label("count"))
                .group_by(AlgorithmModel.algorithm_type)
                .all()
            )

            # 训练历史统计
            total_trainings = self.session.query(TrainingHistoryModel).count()
            successful_trainings = self.session.query(TrainingHistoryModel).filter_by(status="success").count()

            # 预测历史统计
            total_predictions = self.session.query(PredictionHistoryModel).count()
            successful_predictions = self.session.query(PredictionHistoryModel).filter_by(status="success").count()

            return {
                "total_models": total_models,
                "active_models": active_models,
                "gpu_trained_models": gpu_trained_models,
                "algorithm_distribution": {item.algorithm_type: item.count for item in algorithm_counts},
                "training_stats": {
                    "total_trainings": total_trainings,
                    "successful_trainings": successful_trainings,
                    "success_rate": successful_trainings / total_trainings if total_trainings > 0 else 0,
                },
                "prediction_stats": {
                    "total_predictions": total_predictions,
                    "successful_predictions": successful_predictions,
                    "success_rate": successful_predictions / total_predictions if total_predictions > 0 else 0,
                },
            }

        except SQLAlchemyError:
            logger.error("Failed to get model statistics: %(e)s")
            return {}

    async def cleanup_old_history(self, days_to_keep: int = 90) -> int:
        """
        清理旧的历史记录

        Args:
            days_to_keep: 保留天数

        Returns:
            删除的记录数量
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            # 删除旧的训练历史
            deleted_trainings = (
                self.session.query(TrainingHistoryModel).filter(TrainingHistoryModel.created_at < cutoff_date).delete()
            )

            # 删除旧的预测历史
            deleted_predictions = (
                self.session.query(PredictionHistoryModel)
                .filter(PredictionHistoryModel.created_at < cutoff_date)
                .delete()
            )

            self.session.commit()

            total_deleted = deleted_trainings + deleted_predictions
            logger.info("Cleaned up %(total_deleted)s old history records (keeping %(days_to_keep)s days)")

            return total_deleted

        except SQLAlchemyError:
            self.session.rollback()
            logger.error("Failed to cleanup old history: %(e)s")
            return 0

    # ==================== 数据验证和清理方法 ====================

    async def validate_model_data(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证模型数据的完整性和一致性

        Args:
            model_data: 模型数据字典

        Returns:
            验证结果 {"valid": bool, "errors": list, "warnings": list}
        """
        errors = []
        warnings = []

        # 必填字段检查
        required_fields = ["model_id", "algorithm_type", "model_name"]
        for field in required_fields:
            if field not in model_data or not model_data[field]:
                errors.append(f"Missing required field: {field}")

        # 算法类型验证
        valid_algorithm_types = ["svm", "decision_tree", "naive_bayes", "hmm", "neural_network"]
        if "algorithm_type" in model_data:
            if model_data["algorithm_type"] not in valid_algorithm_types:
                errors.append(f"Invalid algorithm_type: {model_data['algorithm_type']}")

        # 模型ID格式验证
        if "model_id" in model_data:
            model_id = model_data["model_id"]
            if not isinstance(model_id, str) or len(model_id) > 100:
                errors.append("model_id must be a string with max length 100")

        # JSON字段验证
        json_fields = ["model_data", "metadata", "training_metrics"]
        for field in json_fields:
            if field in model_data and model_data[field] is not None:
                if not isinstance(model_data[field], dict):
                    errors.append(f"{field} must be a valid JSON object")

        # 布尔字段验证
        bool_fields = ["is_active", "gpu_trained"]
        for field in bool_fields:
            if field in model_data and model_data[field] is not None:
                if not isinstance(model_data[field], bool):
                    warnings.append(f"{field} should be a boolean value")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    async def validate_history_data(self, history_data: Dict[str, Any], history_type: str) -> Dict[str, Any]:
        """
        验证历史记录数据的完整性和一致性

        Args:
            history_data: 历史数据字典
            history_type: 历史类型 ("training" 或 "prediction")

        Returns:
            验证结果 {"valid": bool, "errors": list, "warnings": list}
        """
        errors = []
        warnings = []

        # 必填字段检查
        if history_type == "training":
            required_fields = ["training_id", "model_id", "algorithm_type", "training_start_time", "status"]
        else:  # prediction
            required_fields = ["prediction_id", "model_id", "algorithm_type", "prediction_time", "status"]

        for field in required_fields:
            if field not in history_data or history_data[field] is None:
                errors.append(f"Missing required field: {field}")

        # ID格式验证
        id_field = "training_id" if history_type == "training" else "prediction_id"
        if id_field in history_data:
            record_id = history_data[id_field]
            if not isinstance(record_id, str) or len(record_id) > 100:
                errors.append(f"{id_field} must be a string with max length 100")

        # 时间戳验证
        time_field = "training_start_time" if history_type == "training" else "prediction_time"
        if time_field in history_data:
            try:
                datetime.fromisoformat(str(history_data[time_field]).replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                errors.append(f"Invalid timestamp format for {time_field}")

        # 状态验证
        if "status" in history_data:
            valid_statuses = ["success", "failed", "interrupted", "timeout"]
            if history_data["status"] not in valid_statuses:
                errors.append(f"Invalid status: {history_data['status']}")

        # 持续时间验证
        if "training_duration_ms" in history_data and history_data["training_duration_ms"] is not None:
            if (
                not isinstance(history_data["training_duration_ms"], (int, float))
                or history_data["training_duration_ms"] < 0
            ):
                errors.append("training_duration_ms must be a non-negative number")

        # 置信度验证
        if "confidence_score" in history_data and history_data["confidence_score"] is not None:
            confidence = history_data["confidence_score"]
            if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
                errors.append("confidence_score must be a number between 0 and 1")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    async def repair_model_data(self, model_id: str) -> Dict[str, Any]:
        """
        修复模型数据的完整性和一致性

        Args:
            model_id: 模型ID

        Returns:
            修复结果 {"repaired": bool, "changes": list}
        """
        try:
            model = self.session.query(AlgorithmModel).filter_by(model_id=model_id).first()
            if not model:
                return {"repaired": False, "changes": [], "error": "Model not found"}

            changes = []

            # 修复缺失的默认值
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

            # 修复JSON字段
            json_fields = ["model_data", "metadata", "training_metrics"]
            for field_name in json_fields:
                field_value = getattr(model, field_name)
                if field_value is not None and not isinstance(field_value, dict):
                    try:
                        # 尝试解析字符串为JSON
                        if isinstance(field_value, str):
                            import json

                            parsed_value = json.loads(field_value)
                            setattr(model, field_name, parsed_value)
                            changes.append(f"Repaired {field_name} JSON format")
                    except (json.JSONDecodeError, TypeError):
                        # 如果无法解析，设置为空对象
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
        """
        清理孤立的历史记录（关联模型不存在的记录）

        Returns:
            清理结果 {"training_deleted": int, "prediction_deleted": int}
        """
        try:
            # 查找孤立的训练历史
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

            # 查找孤立的预测历史
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

    async def validate_data_integrity(self) -> Dict[str, Any]:
        """
        执行完整的数据完整性验证

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
