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


