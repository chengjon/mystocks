#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据管道

提供测试数据的ETL流程、数据转换、验证和优化功能，确保测试数据的高效流动和管理。
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    """管道处理阶段枚举"""

    INGESTION = "ingestion"  # 数据摄入
    VALIDATION = "validation"  # 数据验证
    TRANSFORMATION = "transformation"  # 数据转换
    AGGREGATION = "aggregation"  # 数据聚合
    OPTIMIZATION = "optimization"  # 数据优化
    EXPORT = "export"  # 数据导出


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

    # 基础配置
    name: str
    description: str

    # 性能配置
    max_workers: int = 4
    batch_size: int = 1000
    timeout_seconds: int = 300

    # 质量配置
    quality_threshold: float = 0.8
    validation_enabled: bool = True
    auto_repair: bool = True

    # 存储配置
    storage_path: str = "data/pipeline"
    cache_enabled: bool = True
    cache_ttl: int = 3600

    # 监控配置
    enable_monitoring: bool = True
    metrics_interval: int = 60

    # 错误处理配置
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


class TestDataValidator:
    """测试数据验证器"""

    def __init__(self):
        self.validation_rules = {
            "market_data": self._validate_market_data,
            "trading_data": self._validate_trading_data,
            "performance_data": self._validate_performance_data,
            "ai_data": self._validate_ai_data,
        }

    def validate_batch(self, batch: DataBatch) -> Tuple[bool, List[str]]:
        """验证数据批次"""
        errors = []

        # 基础结构验证
        if not batch.data:
            errors.append("数据为空")
            return False, errors

        # 数据类型验证
        for i, record in enumerate(batch.data[:100]):  # 只检查前100条记录
            if not isinstance(record, dict):
                errors.append(f"第{i}条记录不是字典类型")
                continue

            # 根据源类型应用特定验证规则
            validator = self.validation_rules.get(batch.source)
            if validator:
                record_errors = validator(record)
                errors.extend(record_errors)

        quality_score = self._calculate_quality_score(batch.data)
        batch.quality_score = quality_score

        passed = quality_score >= 0.7 and len(errors) == 0
        return passed, errors

    def _validate_market_data(self, record: Dict[str, Any]) -> List[str]:
        """验证市场数据格式"""
        errors = []

        # 必需字段检查
        required_fields = ["symbol", "date", "open", "high", "low", "close", "volume"]
        missing_fields = [f for f in required_fields if f not in record]
        if missing_fields:
            errors.append(f"缺少必需字段: {missing_fields}")

        # 数据类型检查
        if "symbol" in record and not isinstance(record["symbol"], str):
            errors.append("symbol 必须是字符串")

        if "volume" in record and not isinstance(record["volume"], (int, float)):
            errors.append("volume 必须是数字")

        # 数值范围检查
        numeric_fields = ["open", "high", "low", "close"]
        for field in numeric_fields:
            if field in record:
                value = record[field]
                if isinstance(value, (int, float)):
                    if value <= 0:
                        errors.append(f"{field} 必须大于0")
                    if value > 1000000:  # 异常高价检查
                        errors.append(f"{field} 数值异常高")

        return errors

    def _validate_trading_data(self, record: Dict[str, Any]) -> List[str]:
        """验证交易数据格式"""
        errors = []

        # 必需字段检查
        required_fields = ["symbol", "quantity", "price", "timestamp"]
        missing_fields = [f for f in required_fields if f not in record]
        if missing_fields:
            errors.append(f"缺少必需字段: {missing_fields}")

        # 数值范围检查
        if "quantity" in record and isinstance(record["quantity"], (int, float)):
            if record["quantity"] <= 0:
                errors.append("quantity 必须大于0")
            if record["quantity"] > 1000000:
                errors.append("quantity 数值异常大")

        if "price" in record and isinstance(record["price"], (int, float)):
            if record["price"] <= 0:
                errors.append("price 必须大于0")
            if record["price"] > 1000000:
                errors.append("price 数值异常高")

        return errors

    def _validate_performance_data(self, record: Dict[str, Any]) -> List[str]:
        """验证性能数据格式"""
        errors = []

        # 必需字段检查
        required_fields = ["test_name", "duration", "status"]
        missing_fields = [f for f in required_fields if f not in record]
        if missing_fields:
            errors.append(f"缺少必需字段: {missing_fields}")

        # 状态值检查
        if "status" in record and record["status"] not in [
            "passed",
            "failed",
            "skipped",
        ]:
            errors.append("status 必须是 passed/failed/skipped 之一")

        return errors

    def _validate_ai_data(self, record: Dict[str, Any]) -> List[str]:
        """验证AI数据格式"""
        errors = []

        # 必需字段检查
        required_fields = ["symbol", "timestamp", "prediction", "confidence"]
        missing_fields = [f for f in required_fields if f not in record]
        if missing_fields:
            errors.append(f"缺少必需字段: {missing_fields}")

        # 置信度范围检查
        if "confidence" in record and isinstance(record["confidence"], (int, float)):
            if not (0 <= record["confidence"] <= 1):
                errors.append("confidence 必须在0-1之间")

        return errors

    def _calculate_quality_score(self, data: List[Dict[str, Any]]) -> float:
        """计算数据质量分数"""
        if not data:
            return 0.0

        score = 100.0
        total_records = len(data)

        # 检查记录完整性
        for record in data[:100]:  # 只检查前100条记录
            if not isinstance(record, dict):
                score -= 5
                continue

            # 基础字段存在性检查
            if not record:
                score -= 10
                continue

            # 空值比例检查
            empty_fields = sum(1 for v in record.values() if v is None or v == "")
            if empty_fields > len(record) * 0.5:  # 空值超过50%
                score -= 20
                break

        # 检查重复记录
        if total_records > 1:
            seen = set()
            duplicates = 0
            for record in data:
                record_str = json.dumps(record, sort_keys=True)
                if record_str in seen:
                    duplicates += 1
                seen.add(record_str)

            duplicate_ratio = duplicates / total_records
            score -= duplicate_ratio * 30

        return max(0.0, min(100.0, score))


class DataTransformer:
    """数据转换器"""

    def __init__(self):
        self.transformers = {
            "normalize": self._normalize_data,
            "aggregate": self._aggregate_data,
            "filter": self._filter_data,
            "enrich": self._enrich_data,
            "optimize": self._optimize_data,
        }

    def transform(self, batch: DataBatch, transformations: List[str]) -> DataBatch:
        """应用数据转换"""
        transformed_data = batch.data.copy()

        for transform_name in transformations:
            transformer = self.transformers.get(transform_name)
            if transformer:
                try:
                    transformed_data = transformer(transformed_data, batch.metadata)
                    logger.info(f"应用转换: {transform_name}")
                except Exception as e:
                    logger.error(f"转换失败 {transform_name}: {str(e)}")
                    continue

        # 创建新的批次
        new_batch = DataBatch(
            id=f"{batch.id}_transformed",
            source=batch.source,
            data=transformed_data,
            metadata=batch.metadata.copy(),
            quality_score=batch.quality_score,
        )
        new_batch.processing_stage = PipelineStage.TRANSFORMATION

        return new_batch

    def _normalize_data(
        self, data: List[Dict[str, Any]], metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """标准化数据格式"""
        normalized = []

        for record in data:
            # 标准化时间戳格式
            if "date" in record:
                record["timestamp"] = record["date"]

            # 标准化价格字段
            price_fields = ["open", "high", "low", "close"]
            for field in price_fields:
                if field in record and isinstance(record[field], str):
                    try:
                        record[field] = float(record[field].replace(",", ""))
                    except:
                        pass

            # 标准化成交量
            if "volume" in record and isinstance(record["volume"], str):
                try:
                    record["volume"] = int(record["volume"].replace(",", ""))
                except:
                    pass

            normalized.append(record)

        return normalized

    def _aggregate_data(
        self, data: List[Dict[str, Any]], metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """聚合数据"""
        if not data:
            return []

        # 按股票代码分组聚合
        grouped = {}
        for record in data:
            symbol = record.get("symbol", "unknown")
            if symbol not in grouped:
                grouped[symbol] = []
            grouped[symbol].append(record)

        aggregated = []
        for symbol, records in grouped.items():
            if len(records) == 1:
                aggregated.append(records[0])
                continue

            # 计算聚合指标
            agg_record = {
                "symbol": symbol,
                "record_count": len(records),
                "timestamp": datetime.now().isoformat(),
                "aggregated": True,
            }

            # 计算价格聚合
            price_fields = ["open", "high", "low", "close"]
            for field in price_fields:
                values = [r.get(field) for r in records if r.get(field) is not None]
                if values:
                    agg_record[f"avg_{field}"] = sum(values) / len(values)
                    agg_record[f"max_{field}"] = max(values)
                    agg_record[f"min_{field}"] = min(values)

            # 计算成交量聚合
            volumes = [r.get("volume") for r in records if r.get("volume") is not None]
            if volumes:
                agg_record["total_volume"] = sum(volumes)
                agg_record["avg_volume"] = sum(volumes) / len(volumes)

            aggregated.append(agg_record)

        return aggregated

    def _filter_data(
        self, data: List[Dict[str, Any]], metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """过滤数据"""
        filtered = []

        for record in data:
            # 过滤无效数据
            if not record:
                continue

            # 过滤空记录
            if all(v is None or v == "" for v in record.values()):
                continue

            # 过滤异常价格（根据元数据中的范围配置）
            price_ranges = metadata.get("price_ranges", {})
            for field, range_config in price_ranges.items():
                if field in record and isinstance(record[field], (int, float)):
                    min_val, max_val = range_config
                    if not (min_val <= record[field] <= max_val):
                        break
            else:
                filtered.append(record)

        return filtered

    def _enrich_data(
        self, data: List[Dict[str, Any]], metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """丰富数据"""
        enriched = []

        for record in data:
            enriched_record = record.copy()

            # 添加处理时间戳
            enriched_record["processed_at"] = datetime.now().isoformat()

            # 添加数据来源
            enriched_record["source"] = metadata.get("source", "unknown")

            # 添加质量分数
            enriched_record["quality_score"] = metadata.get("quality_score", 0.0)

            enriched.append(enriched_record)

        return enriched

    def _optimize_data(
        self, data: List[Dict[str, Any]], metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """优化数据结构"""
        optimized = []

        for record in data:
            optimized_record = {}

            # 只保留必要字段
            essential_fields = metadata.get(
                "essential_fields", ["id", "symbol", "timestamp"]
            )
            for field in essential_fields:
                if field in record:
                    optimized_record[field] = record[field]

            # 压缩数值精度
            for key, value in optimized_record.items():
                if isinstance(value, float):
                    optimized_record[key] = round(value, 4)
                elif isinstance(value, str) and len(value) > 100:
                    # 截断过长的字符串
                    optimized_record[key] = value[:100] + "..."

            optimized.append(optimized_record)

        return optimized


class TestDataPipeline:
    """测试数据管道主类"""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.validator = TestDataValidator()
        self.transformer = DataTransformer()
        self.metrics = PipelineMetrics()
        self.batches: Dict[str, DataBatch] = {}
        self.processing_queue = asyncio.Queue()
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)

        # 创建存储目录
        self.storage_path = Path(config.storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"初始化测试数据管道: {config.name}")

    async def ingest_data(
        self,
        source: str,
        data: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """摄入数据"""
        batch_id = f"{source}_{int(time.time())}"
        batch_metadata = metadata or {}
        batch_metadata.update(
            {
                "source": source,
                "ingestion_time": datetime.now().isoformat(),
                "record_count": len(data),
            }
        )

        batch = DataBatch(
            id=batch_id, source=source, data=data, metadata=batch_metadata
        )

        # 将批次加入处理队列
        await self.processing_queue.put(batch)
        self.batches[batch_id] = batch

        logger.info(f"数据已摄入: {batch_id} ({len(data)} 条记录)")
        return batch_id

    async def process_pipeline(self) -> List[str]:
        """处理管道中的所有批次"""
        processed_batches = []

        while not self.processing_queue.empty():
            batch = await self.processing_queue.get()

            try:
                # 处理批次
                result_batch = await self._process_batch(batch)
                processed_batches.append(result_batch.id)

                # 更新指标
                self.metrics.batches_processed += 1
                self.metrics.processed_records += len(result_batch.data)

                logger.info(f"批次处理完成: {batch.id}")

            except Exception as e:
                logger.error(f"批次处理失败 {batch.id}: {str(e)}")
                self.metrics.failed_records += len(batch.data)
                if self.config.fail_fast:
                    break

        # 计算总体指标
        if self.metrics.batches_processed > 0:
            self.metrics.avg_processing_time = (
                self.metrics.total_duration / self.metrics.batches_processed
            )

        return processed_batches

    async def _process_batch(self, batch: DataBatch) -> DataBatch:
        """处理单个数据批次"""
        start_time = time.time()

        try:
            # 阶段1: 验证
            if self.config.validation_enabled:
                passed, errors = self.validator.validate_batch(batch)
                if not passed and self.config.auto_repair:
                    batch = self._auto_repair_batch(batch, errors)
                    # 重新验证
                    passed, errors = self.validator.validate_batch(batch)

                if not passed:
                    logger.warning(f"批次验证失败 {batch.id}: {errors}")
                    # 创建失败批次但继续处理
                    failed_batch = DataBatch(
                        id=f"{batch.id}_failed",
                        source=batch.source,
                        data=[],  # 失败批次为空
                        metadata=batch.metadata,
                        quality_score=batch.quality_score,
                    )
                    return failed_batch

            # 阶段2: 转换
            transformations = self.config.metadata.get("transformations", [])
            if transformations:
                batch = self.transformer.transform(batch, transformations)

            # 阶段3: 优化
            self._optimize_batch(batch)

            # 阶段4: 存储
            await self._store_batch(batch)

            # 更新处理状态
            batch.processing_stage = PipelineStage.EXPORT

            processing_time = time.time() - start_time
            self.metrics.total_duration += processing_time

            logger.info(f"批次处理成功 {batch.id}: {processing_time:.2f}秒")

            return batch

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"批次处理异常 {batch.id}: {str(e)}")

            # 创建错误批次
            error_batch = DataBatch(
                id=f"{batch.id}_error",
                source=batch.source,
                data=[],
                metadata=batch.metadata,
                quality_score=0.0,
            )
            return error_batch

    def _auto_repair_batch(self, batch: DataBatch, errors: List[str]) -> DataBatch:
        """自动修复批次数据"""
        repaired_data = []

        for record in batch.data:
            repaired_record = record.copy()

            # 修复常见问题
            if not isinstance(repaired_record, dict):
                continue

            # 修复缺失的必需字段
            essential_fields = ["symbol", "timestamp", "value"]
            for field in essential_fields:
                if field not in repaired_record:
                    repaired_record[field] = None

            # 修复数据类型
            if "volume" in repaired_record and isinstance(
                repaired_record["volume"], str
            ):
                try:
                    repaired_record["volume"] = int(
                        repaired_record["volume"].replace(",", "")
                    )
                except:
                    repaired_record["volume"] = 0

            repaired_data.append(repaired_record)

        repaired_batch = DataBatch(
            id=f"{batch.id}_repaired",
            source=batch.source,
            data=repaired_data,
            metadata=batch.metadata,
            quality_score=batch.quality_score,
        )

        logger.info(
            f"自动修复批次: {batch.id} ({len(batch.data)} -> {len(repaired_data)})"
        )
        return repaired_batch

    def _optimize_batch(self, batch: DataBatch):
        """优化批次数据"""
        # 去重
        unique_data = []
        seen = set()

        for record in batch.data:
            record_str = json.dumps(record, sort_keys=True)
            if record_str not in seen:
                seen.add(record_str)
                unique_data.append(record)

        batch.data = unique_data
        logger.info(f"批次数据去重: {batch.id} ({len(batch.data)} 条唯一记录)")

    async def _store_batch(self, batch: DataBatch):
        """存储批次数据"""
        try:
            # 创建存储文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{batch.source}_{batch.id}_{timestamp}.json"
            filepath = self.storage_path / filename

            # 序列化数据
            serialized = {"batch_info": batch.to_dict(), "data": batch.data}

            # 写入文件
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(serialized, f, indent=2, ensure_ascii=False)

            logger.info(f"批次已存储: {filepath}")

        except Exception as e:
            logger.error(f"批次存储失败 {batch.id}: {str(e)}")

    async def export_data(
        self, batch_ids: List[str], output_path: str, format: str = "json"
    ) -> bool:
        """导出数据"""
        try:
            export_data = []

            for batch_id in batch_ids:
                if batch_id in self.batches:
                    batch = self.batches[batch_id]
                    export_data.extend(batch.data)

            if not export_data:
                logger.warning("没有可导出的数据")
                return False

            # 根据格式导出
            output_file = Path(output_path)

            if format == "json":
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)

            elif format == "csv":
                df = pd.DataFrame(export_data)
                df.to_csv(output_file, index=False)

            elif format == "parquet":
                df = pd.DataFrame(export_data)
                df.to_parquet(output_file)

            else:
                logger.error(f"不支持的导出格式: {format}")
                return False

            logger.info(f"数据导出完成: {output_file} ({len(export_data)} 条记录)")
            return True

        except Exception as e:
            logger.error(f"数据导出失败: {str(e)}")
            return False

    def get_metrics(self) -> PipelineMetrics:
        """获取管道性能指标"""
        return self.metrics

    def get_batch_info(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """获取批次信息"""
        if batch_id in self.batches:
            return self.batches[batch_id].to_dict()
        return None

    def list_batches(self) -> List[Dict[str, Any]]:
        """列出所有批次"""
        return [batch.to_dict() for batch in self.batches.values()]

    async def clear_cache(self):
        """清理缓存"""
        self.batches.clear()
        self.processing_queue = asyncio.Queue()

        # 清理存储目录中的旧文件
        cutoff_time = datetime.now() - timedelta(days=7)
        for file_path in self.storage_path.glob("*.json"):
            if datetime.fromtimestamp(file_path.stat().st_mtime) < cutoff_time:
                file_path.unlink()
                logger.info(f"清理旧文件: {file_path}")

        logger.info("缓存清理完成")


# 管道工厂类
class PipelineFactory:
    """管道工厂类"""

    @staticmethod
    def create_market_data_pipeline() -> TestDataPipeline:
        """创建市场数据管道"""
        config = PipelineConfig(
            name="market_data_pipeline",
            description="市场数据处理管道",
            max_workers=8,
            batch_size=5000,
            quality_threshold=0.85,
            enable_monitoring=True,
        )

        # 市场数据特定的配置
        config.metadata = {
            "transformations": ["normalize", "aggregate"],
            "essential_fields": [
                "symbol",
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
            ],
            "price_ranges": {
                "open": (0, 1000000),
                "high": (0, 1000000),
                "low": (0, 1000000),
                "close": (0, 1000000),
            },
        }

        return TestDataPipeline(config)

    @staticmethod
    def create_trading_data_pipeline() -> TestDataPipeline:
        """创建交易数据管道"""
        config = PipelineConfig(
            name="trading_data_pipeline",
            description="交易数据处理管道",
            max_workers=6,
            batch_size=2000,
            quality_threshold=0.9,
            auto_repair=True,
        )

        config.metadata = {
            "transformations": ["normalize", "filter"],
            "essential_fields": ["symbol", "quantity", "price", "timestamp"],
            "volume_ranges": {"quantity": (0, 1000000), "price": (0, 100000)},
        }

        return TestDataPipeline(config)

    @staticmethod
    def create_performance_data_pipeline() -> TestDataPipeline:
        """创建性能数据管道"""
        config = PipelineConfig(
            name="performance_data_pipeline",
            description="性能数据处理管道",
            max_workers=4,
            batch_size=1000,
            quality_threshold=0.95,
            fail_fast=True,
        )

        config.metadata = {
            "transformations": ["normalize", "optimize"],
            "essential_fields": ["test_name", "duration", "status", "timestamp"],
        }

        return TestDataPipeline(config)


# 使用示例
async def demo_data_pipeline():
    """演示数据管道功能"""
    print("🚀 演示测试数据管道功能")

    # 创建市场数据管道
    market_pipeline = PipelineFactory.create_market_data_pipeline()

    # 生成测试数据
    test_data = [
        {
            "symbol": "AAPL",
            "date": "2024-12-12",
            "open": 150.0,
            "high": 155.0,
            "low": 149.0,
            "close": 152.0,
            "volume": 1000000,
        }
        for _ in range(100)
    ]

    # 摄入数据
    batch_id = await market_pipeline.ingest_data("market_data", test_data)
    print(f"✓ 数据摄入完成: {batch_id}")

    # 处理管道
    processed_batches = await market_pipeline.process_pipeline()
    print(f"✓ 处理完成 {len(processed_batches)} 个批次")

    # 获取指标
    metrics = market_pipeline.get_metrics()
    print(f"📊 管道指标: {metrics.to_dict()}")

    # 导出数据
    await market_pipeline.export_data(
        processed_batches, "exported_market_data.json", "json"
    )
    print("✓ 数据导出完成")

    # 清理
    await market_pipeline.clear_cache()


if __name__ == "__main__":
    # 运行演示
    asyncio.run(demo_data_pipeline())
