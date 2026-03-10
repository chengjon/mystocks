from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List


class PipelineStage(Enum):
    """管道处理阶段枚举"""

    INGESTION = "ingestion"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    AGGREGATION = "aggregation"
    OPTIMIZATION = "optimization"
    EXPORT = "export"


class DataQuality(Enum):
    """数据质量级别枚举"""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    INVALID = "invalid"


@dataclass
class PipelineConfig:
    """管道配置类"""

    name: str
    description: str
    max_workers: int = 4
    batch_size: int = 1000
    timeout_seconds: int = 300
    quality_threshold: float = 0.8
    validation_enabled: bool = True
    auto_repair: bool = True
    storage_path: str = "data/pipeline"
    cache_enabled: bool = True
    cache_ttl: int = 3600
    enable_monitoring: bool = True
    metrics_interval: int = 60
    fail_fast: bool = False
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class DataBatch:
    """数据批次类"""

    id: str
    source: str
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    quality_score: float = 0.0
    processing_stage: PipelineStage = PipelineStage.INGESTION

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "source": self.source,
            "data": self.data,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "quality_score": self.quality_score,
            "processing_stage": self.processing_stage.value,
        }


@dataclass
class PipelineMetrics:
    """管道性能指标"""

    total_records: int = 0
    processed_records: int = 0
    failed_records: int = 0
    batches_processed: int = 0
    total_duration: float = 0.0
    avg_processing_time: float = 0.0
    quality_score: float = 0.0
    throughput_records_per_second: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_records": self.total_records,
            "processed_records": self.processed_records,
            "failed_records": self.failed_records,
            "batches_processed": self.batches_processed,
            "total_duration": self.total_duration,
            "avg_processing_time": self.avg_processing_time,
            "quality_score": self.quality_score,
            "throughput_records_per_second": self.throughput_records_per_second,
        }
