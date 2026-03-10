from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tests.pipeline.test_data_pipeline import PipelineConfig, TestDataPipeline


class PipelineFactory:
    """管道工厂类"""

    @staticmethod
    def create_market_data_pipeline(
        pipeline_cls: type["TestDataPipeline"], config_cls: type["PipelineConfig"]
    ) -> "TestDataPipeline":
        """创建市场数据管道"""
        config = config_cls(
            name="market_data_pipeline",
            description="市场数据处理管道",
            max_workers=8,
            batch_size=5000,
            quality_threshold=0.85,
            enable_monitoring=True,
        )
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
        return pipeline_cls(config)

    @staticmethod
    def create_trading_data_pipeline(
        pipeline_cls: type["TestDataPipeline"], config_cls: type["PipelineConfig"]
    ) -> "TestDataPipeline":
        """创建交易数据管道"""
        config = config_cls(
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
        return pipeline_cls(config)

    @staticmethod
    def create_performance_data_pipeline(
        pipeline_cls: type["TestDataPipeline"], config_cls: type["PipelineConfig"]
    ) -> "TestDataPipeline":
        """创建性能数据管道"""
        config = config_cls(
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
        return pipeline_cls(config)


async def demo_data_pipeline(
    pipeline_factory: type[PipelineFactory],
    pipeline_cls: type["TestDataPipeline"],
    config_cls: type["PipelineConfig"],
):
    """演示数据管道功能"""
    print("🚀 演示测试数据管道功能")

    market_pipeline = pipeline_factory.create_market_data_pipeline(pipeline_cls, config_cls)

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

    batch_id = await market_pipeline.ingest_data("market_data", test_data)
    print(f"✓ 数据摄入完成: {batch_id}")

    processed_batches = await market_pipeline.process_pipeline()
    print(f"✓ 处理完成 {len(processed_batches)} 个批次")

    metrics = market_pipeline.get_metrics()
    print(f"📊 管道指标: {metrics.to_dict()}")

    await market_pipeline.export_data(processed_batches, "exported_market_data.json", "json")
    print("✓ 数据导出完成")

    await market_pipeline.clear_cache()
