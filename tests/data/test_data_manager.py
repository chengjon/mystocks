"""
测试数据管理器

提供智能测试数据生成、管理和优化功能。
"""

import json
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

import pandas as pd


class DataQuality(Enum):
    """数据质量枚举"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INVALID = "invalid"


@dataclass
class DataSource:
    """数据源定义"""

    name: str
    type: str  # "mock", "real", "api", "database"
    priority: int = 1
    data_format: str = "json"
    quality: DataQuality = DataQuality.HIGH
    refresh_interval: int = 3600  # 秒
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class TestDataset:
    """测试数据集"""

    name: str
    description: str
    size: int
    data: List[Dict[str, Any]]
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    source: str = "test_data_manager"
    quality_score: float = 0.0
    tags: List[str] = field(default_factory=list)


class TestDataOptimizer:
    """测试数据优化器"""

    def __init__(self, max_datasets: int = 100):
        self.max_datasets = max_datasets
        self.datasets: Dict[str, TestDataset] = {}
        self.data_sources: Dict[str, DataSource] = {}
        self.cache = {}
        self.stats = {
            "total_datasets": 0,
            "active_datasets": 0,
            "optimized_datasets": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

    def add_data_source(self, source: DataSource):
        """添加数据源"""
        self.data_sources[source.name] = source
        print(f"✓ 添加数据源: {source.name}")

    def get_best_data_source(self, data_type: str) -> Optional[DataSource]:
        """获取最佳数据源"""
        candidates = [s for s in self.data_sources.values() if s.type == data_type]
        if not candidates:
            return None

        # 按优先级和质量排序
        candidates.sort(key=lambda x: (x.priority, x.quality.value), reverse=True)
        return candidates[0]

    def generate_market_data(
        self, symbol: str, start_date: str, end_date: str, frequency: str = "daily"
    ) -> TestDataset:
        """生成市场测试数据"""
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        data = []
        current = start

        while current <= end:
            if frequency == "daily":
                # 生成日线数据
                data.append(
                    {
                        "symbol": symbol,
                        "date": current.strftime("%Y-%m-%d"),
                        "open": round(random.uniform(50, 200), 2),
                        "high": round(random.uniform(50, 200), 2),
                        "low": round(random.uniform(50, 200), 2),
                        "close": round(random.uniform(50, 200), 2),
                        "volume": random.randint(1000000, 10000000),
                        "created_at": current.isoformat(),
                    }
                )
                current += timedelta(days=1)
            elif frequency == "minute":
                # 生成分钟线数据
                for hour in range(9, 16):  # 交易时间 9:00-15:00
                    for minute in range(0, 60):
                        data.append(
                            {
                                "symbol": symbol,
                                "timestamp": current.replace(
                                    hour=hour, minute=minute, second=0
                                ).isoformat(),
                                "price": round(random.uniform(50, 200), 2),
                                "volume": random.randint(1000, 10000),
                                "created_at": current.isoformat(),
                            }
                        )
                current += timedelta(days=1)

        dataset = TestDataset(
            name=f"market_data_{symbol}_{start_date}_{end_date}",
            description=f"Market data for {symbol} from {start_date} to {end_date}",
            size=len(data),
            data=data,
            quality_score=self._calculate_quality_score(data),
        )

        self.datasets[dataset.name] = dataset
        return dataset

    def generate_trading_portfolio(
        self, initial_value: float = 1000000.0, position_count: int = 10
    ) -> TestDataset:
        """生成交易组合数据"""
        symbols = [
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "TSLA",
            "META",
            "NVDA",
            "JPM",
            "V",
            "WMT",
        ]

        # 生成初始现金和股票
        cash = initial_value
        positions = []
        total_value = cash

        for i in range(position_count):
            symbol = symbols[i % len(symbols)]
            quantity = random.randint(100, 1000)
            price = round(random.uniform(50, 300), 2)
            value = quantity * price

            # 确保总价值不超过初始值
            if value <= total_value:
                positions.append(
                    {
                        "symbol": symbol,
                        "quantity": quantity,
                        "avg_price": price,
                        "current_price": price * random.uniform(0.95, 1.05),
                        "pnl": 0.0,
                    }
                )
                cash -= value
                total_value -= value

        data = {
            "cash": cash,
            "total_value": initial_value
            - cash
            + sum(p["current_price"] * p["quantity"] for p in positions),
            "positions": positions,
            "created_at": datetime.now().isoformat(),
        }

        dataset = TestDataset(
            name="trading_portfolio",
            description="Sample trading portfolio data",
            size=len(positions),
            data=[data],
            quality_score=self._calculate_quality_score([data]),
        )

        self.datasets[dataset.name] = dataset
        return dataset

    def generate_ai_prediction_data(
        self, symbol: str, prediction_type: str = "price", data_points: int = 100
    ) -> TestDataset:
        """生成AI预测测试数据"""
        predictions = []

        for i in range(data_points):
            timestamp = datetime.now() - timedelta(hours=data_points - i)
            predictions.append(
                {
                    "symbol": symbol,
                    "timestamp": timestamp.isoformat(),
                    "prediction_type": prediction_type,
                    "actual_value": round(random.uniform(50, 200), 2),
                    "predicted_value": round(random.uniform(50, 200), 2),
                    "confidence": round(random.uniform(0.6, 0.99), 2),
                    "error": round(random.uniform(-5, 5), 2),
                }
            )

        dataset = TestDataset(
            name=f"ai_prediction_{symbol}_{prediction_type}",
            description=f"AI prediction data for {symbol}",
            size=len(predictions),
            data=predictions,
            quality_score=self._calculate_quality_score(predictions),
        )

        self.datasets[dataset.name] = dataset
        return dataset

    def generate_performance_test_data(
        self, scenario: str, data_size: int = 10000
    ) -> TestDataset:
        """生成性能测试数据"""
        if scenario == "large_dataset":
            # 大数据集测试
            data = []
            for i in range(data_size):
                data.append(
                    {
                        "id": i,
                        "name": f"item_{i}",
                        "value": random.uniform(0, 1000),
                        "category": random.choice(["A", "B", "C"]),
                        "created_at": datetime.now().isoformat(),
                    }
                )
        elif scenario == "time_series":
            # 时间序列测试
            data = []
            start_time = datetime.now() - timedelta(days=365)
            for i in range(data_size):
                timestamp = start_time + timedelta(days=i)
                data.append(
                    {
                        "timestamp": timestamp.isoformat(),
                        "value": random.random(),
                        "category": random.choice("ABC"),
                    }
                )
        else:
            # 默认测试数据
            data = [{"id": i, "value": random.random()} for i in range(data_size)]

        dataset = TestDataset(
            name=f"performance_test_{scenario}",
            description=f"Performance test data for {scenario}",
            size=len(data),
            data=data,
            quality_score=self._calculate_quality_score(data),
        )

        self.datasets[dataset.name] = dataset
        return dataset

    def _calculate_quality_score(self, data: List[Dict[str, Any]]) -> float:
        """计算数据质量分数"""
        if not data:
            return 0.0

        score = 100.0
        sample = data[0] if data else {}

        # 检查必需字段
        required_fields = {"id", "timestamp", "created_at"}
        missing_fields = required_fields - set(sample.keys())
        score -= len(missing_fields) * 10

        # 检查数据类型一致性
        if "value" in sample and not isinstance(sample["value"], (int, float)):
            score -= 20

        # 检查数据完整性
        total_fields = len(sample.keys()) if sample else 0
        if total_fields < 3:
            score -= 30

        # 检查重复数据
        if len(data) > 1:
            duplicates = len(data) - len(set(json.dumps(d) for d in data))
            score -= duplicates * 0.5

        return max(0.0, min(100.0, score))

    def optimize_dataset(self, dataset_name: str) -> bool:
        """优化数据集"""
        if dataset_name not in self.datasets:
            return False

        dataset = self.datasets[dataset_name]

        # 移除重复数据
        unique_data = []
        seen = set()
        for item in dataset.data:
            item_str = json.dumps(item, sort_keys=True)
            if item_str not in seen:
                seen.add(item_str)
                unique_data.append(item)

        dataset.data = unique_data

        # 压缩数据（去除空字段）
        for item in dataset.data:
            keys_to_remove = [k for k, v in item.items() if v is None or v == ""]
            for key in keys_to_remove:
                del item[key]

        dataset.size = len(dataset.data)
        dataset.updated_at = datetime.now()
        dataset.quality_score = self._calculate_quality_score(dataset.data)

        self.stats["optimized_datasets"] += 1
        print(f"✓ 优化数据集: {dataset_name} (大小: {dataset.size})")

        return True

    def cache_dataset(self, dataset_name: str) -> bool:
        """缓存数据集"""
        if dataset_name not in self.datasets:
            return False

        dataset = self.datasets[dataset_name]
        cache_key = f"dataset_{dataset_name}"

        if cache_key in self.cache:
            self.stats["cache_hits"] += 1
            return True

        # 序列化数据集
        cache_data = {
            "name": dataset.name,
            "description": dataset.description,
            "size": dataset.size,
            "data": dataset.data[:1000],  # 只缓存部分数据以节省内存
            "quality_score": dataset.quality_score,
        }

        self.cache[cache_key] = cache_data
        self.stats["cache_misses"] += 1

        print(f"✓ 缓存数据集: {dataset_name}")
        return True

    def get_cached_dataset(self, dataset_name: str) -> Optional[TestDataset]:
        """获取缓存的数据集"""
        cache_key = f"dataset_{dataset_name}"

        if cache_key in self.cache:
            self.stats["cache_hits"] += 1
            cache_data = self.cache[cache_key]

            return TestDataset(
                name=cache_data["name"],
                description=cache_data["description"],
                size=cache_data["size"],
                data=cache_data["data"],
                quality_score=cache_data["quality_score"],
            )

        self.stats["cache_misses"] += 1
        return None

    def cleanup_expired_datasets(self, max_age_days: int = 7):
        """清理过期数据集"""
        cutoff_time = datetime.now() - timedelta(days=max_age_days)
        expired_datasets = []

        for name, dataset in self.datasets.items():
            if dataset.updated_at < cutoff_time:
                expired_datasets.append(name)

        for name in expired_datasets:
            del self.datasets[name]
            print(f"🗑️  清理过期数据集: {name}")

        self.stats["total_datasets"] = len(self.datasets)

        # 清理过期缓存
        expired_cache = [
            k
            for k, v in self.cache.items()
            if "updated_at" in v and v["updated_at"] < cutoff_time
        ]
        for key in expired_cache:
            del self.cache[key]

    def get_dataset_statistics(self) -> Dict[str, Any]:
        """获取数据集统计信息"""
        total_size = sum(d.size for d in self.datasets.values())
        avg_quality = (
            sum(d.quality_score for d in self.datasets.values()) / len(self.datasets)
            if self.datasets
            else 0
        )

        return {
            "total_datasets": len(self.datasets),
            "active_datasets": len(
                [d for d in self.datasets.values() if d.quality_score > 50]
            ),
            "total_data_size": total_size,
            "average_quality_score": avg_quality,
            "cache_hits": self.stats["cache_hits"],
            "cache_misses": self.stats["cache_misses"],
            "cache_hit_rate": self.stats["cache_hits"]
            / (self.stats["cache_hits"] + self.stats["cache_misses"])
            if (self.stats["cache_hits"] + self.stats["cache_misses"]) > 0
            else 0,
        }

    def export_dataset(self, dataset_name: str, output_path: str, format: str = "json"):
        """导出数据集"""
        if dataset_name not in self.datasets:
            return False

        dataset = self.datasets[dataset_name]
        output_path = Path(output_path)

        if format == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(dataset.data, f, indent=2, ensure_ascii=False)
        elif format == "csv":
            df = pd.DataFrame(dataset.data)
            df.to_csv(output_path, index=False)
        elif format == "parquet":
            df = pd.DataFrame(dataset.data)
            df.to_parquet(output_path)
        else:
            return False

        print(f"✓ 导出数据集: {dataset_name} -> {output_path}")
        return True

    def load_dataset(
        self, file_path: str, dataset_name: Optional[str] = None
    ) -> Optional[TestDataset]:
        """从文件加载数据集"""
        file_path = Path(file_path)
        if not file_path.exists():
            return None

        try:
            # 根据文件扩展名选择解析方式
            if file_path.suffix.lower() == ".json":
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            elif file_path.suffix.lower() in [".csv", ".parquet"]:
                df = (
                    pd.read_csv(file_path)
                    if file_path.suffix.lower() == ".csv"
                    else pd.read_parquet(file_path)
                )
                data = df.to_dict("records")
            else:
                return None

            if not dataset_name:
                dataset_name = f"loaded_{file_path.stem}_{int(time.time())}"

            dataset = TestDataset(
                name=dataset_name,
                description=f"Loaded from {file_path.name}",
                size=len(data),
                data=data,
                quality_score=self._calculate_quality_score(data),
            )

            self.datasets[dataset.name] = dataset
            print(f"✓ 加载数据集: {dataset_name} (大小: {dataset.size})")
            return dataset

        except Exception as e:
            print(f"❌ 加载数据集失败: {e}")
            return None


class TestDataLifecycleManager:
    """测试数据生命周期管理器"""

    def __init__(self, optimizer: TestDataOptimizer):
        self.optimizer = optimizer
        self.lifecycle_rules = {
            "market_data": {
                "retention_days": 30,
                "compression_enabled": True,
                "backup_enabled": True,
            },
            "trading_data": {
                "retention_days": 90,
                "compression_enabled": True,
                "backup_enabled": True,
            },
            "ai_data": {
                "retention_days": 7,
                "compression_enabled": False,
                "backup_enabled": False,
            },
            "performance_data": {
                "retention_days": 1,
                "compression_enabled": False,
                "backup_enabled": False,
            },
        }

    def manage_dataset_lifecycle(self, dataset: TestDataset):
        """管理数据集生命周期"""
        dataset_type = self._classify_dataset(dataset)
        rules = self.lifecycle_rules.get(dataset_type, {})

        # 应用压缩规则
        if rules.get("compression_enabled", False):
            self._compress_dataset(dataset)

        # 应用备份规则
        if rules.get("backup_enabled", False):
            self._backup_dataset(dataset)

        # 检查保留期限
        retention_days = rules.get("retention_days", 7)
        if retention_days > 0:
            self._check_retention(dataset, retention_days)

    def _classify_dataset(self, dataset: TestDataset) -> str:
        """分类数据集类型"""
        dataset_name = dataset.name.lower()

        if "market" in dataset_name or "trading" in dataset_name:
            return "market_data"
        elif "ai" in dataset_name or "prediction" in dataset_name:
            return "ai_data"
        elif "performance" in dataset_name:
            return "performance_data"
        else:
            return "trading_data"

    def _compress_dataset(self, dataset: TestDataset):
        """压缩数据集"""
        # 移除不必要的字段
        compressed_data = []
        for item in dataset.data:
            # 保留核心字段
            compressed_item = {}
            for field in [
                "id",
                "symbol",
                "date",
                "timestamp",
                "value",
                "price",
                "quantity",
            ]:
                if field in item:
                    compressed_item[field] = item[field]
            compressed_data.append(compressed_item)

        dataset.data = compressed_data
        dataset.size = len(compressed_data)
        dataset.updated_at = datetime.now()

    def _backup_dataset(self, dataset: TestDataset):
        """备份数据集"""
        backup_dir = Path("backups/test_data")
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_path = backup_dir / f"{dataset.name}_{int(time.time())}.json"
        self.optimizer.export_dataset(dataset.name, str(backup_path), "json")

        print(f"📁 备份数据集: {dataset.name} -> {backup_path}")

    def _check_retention(self, dataset: TestDataset, retention_days: int):
        """检查数据保留期限"""
        age_days = (datetime.now() - dataset.created_at).days
        if age_days > retention_days:
            print(
                f"⚠️  数据集 {dataset.name} 已过期 {age_days} 天，超过保留期限 {retention_days} 天"
            )


# 使用示例
def demo_test_data_manager():
    """演示测试数据管理器功能"""
    print("🚀 演示测试数据管理器功能")

    # 创建优化器
    optimizer = TestDataOptimizer(max_datasets=50)

    # 创建生命周期管理器
    lifecycle_manager = TestDataLifecycleManager(optimizer)

    # 添加数据源
    market_source = DataSource(
        name="market_api", type="api", priority=1, quality=DataQuality.HIGH
    )
    optimizer.add_data_source(market_source)

    # 生成测试数据
    market_data = optimizer.generate_market_data(
        symbol="AAPL", start_date="2024-01-01", end_date="2024-12-31", frequency="daily"
    )

    portfolio_data = optimizer.generate_trading_portfolio()
    ai_prediction = optimizer.generate_ai_prediction_data("AAPL", "price")
    performance_data = optimizer.generate_performance_test_data("large_dataset")

    # 优化数据集
    optimizer.optimize_dataset(market_data.name)
    optimizer.cache_dataset(market_data.name)

    # 管理生命周期
    lifecycle_manager.manage_dataset_lifecycle(market_data)
    lifecycle_manager.manage_dataset_lifecycle(portfolio_data)

    # 获取统计信息
    stats = optimizer.get_dataset_statistics()
    print(f"\n📊 数据集统计: {stats}")

    # 导出数据
    optimizer.export_dataset(market_data.name, "market_data.json", "json")
    optimizer.export_dataset(portfolio_data.name, "portfolio_data.csv", "csv")


if __name__ == "__main__":
    demo_test_data_manager()
