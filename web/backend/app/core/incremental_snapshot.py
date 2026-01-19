"""
数据快照优化系统
集成测试使用增量数据而非全量导入，提升测试效率和稳定性
"""

import hashlib
import pickle
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

from prometheus_client import Counter, Gauge, Histogram

# ==================== 监控指标 ====================

SNAPSHOT_OPERATION_COUNT = Counter("snapshot_operations_total", "快照操作计数", ["operation_type", "result"])

SNAPSHOT_SIZE_BYTES = Gauge("snapshot_size_bytes", "快照文件大小(字节)", ["snapshot_type"])

SNAPSHOT_OPERATION_TIME = Histogram(
    "snapshot_operation_duration_seconds",
    "快照操作耗时(秒)",
    ["operation_type"],
    buckets=[0.1, 0.5, 1, 5, 10, 30],
)

INCREMENTAL_UPDATE_COUNT = Counter("incremental_updates_total", "增量更新计数", ["data_type"])

# ==================== 数据结构 ====================


class SnapshotMetadata:
    """快照元数据"""

    def __init__(self, snapshot_type: str, version: str, created_at: datetime):
        self.snapshot_type = snapshot_type
        self.version = version
        self.created_at = created_at
        self.last_modified = created_at
        self.data_hash = ""
        self.record_count = 0
        self.size_bytes = 0

    def update_hash(self, data: Any):
        """更新数据哈希"""
        if isinstance(data, pd.DataFrame):
            # DataFrame的哈希计算
            data_str = data.to_csv().encode("utf-8")
        elif isinstance(data, dict):
            # 字典的哈希计算
            data_str = str(sorted(data.items())).encode("utf-8")
        else:
            # 其他类型的哈希计算
            data_str = str(data).encode("utf-8")

        self.data_hash = hashlib.sha256(data_str).hexdigest()


class IncrementalDataManager:
    """增量数据管理器"""

    def __init__(self, base_dir: str = "data/snapshots"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # 快照缓存
        self.snapshots: Dict[str, Any] = {}
        self.metadata: Dict[str, SnapshotMetadata] = {}

        # 已处理的记录ID集合（用于增量更新）
        self.processed_ids: Dict[str, Set[str]] = {}

    def create_base_snapshot(self, snapshot_type: str, data: Any, version: str = "1.0.0") -> bool:
        """创建基础快照"""
        start_time = datetime.now()

        try:
            # 创建元数据
            metadata = SnapshotMetadata(snapshot_type, version, datetime.now())
            metadata.update_hash(data)

            # 估算记录数
            if isinstance(data, pd.DataFrame):
                metadata.record_count = len(data)
            elif isinstance(data, (list, dict)):
                metadata.record_count = len(data) if hasattr(data, "__len__") else 1

            # 保存快照
            snapshot_path = self.base_dir / f"{snapshot_type}_base.pkl"
            with open(snapshot_path, "wb") as f:
                pickle.dump({"data": data, "metadata": metadata, "type": "base"}, f)

            # 更新文件大小
            metadata.size_bytes = snapshot_path.stat().st_size

            # 缓存快照
            self.snapshots[snapshot_type] = data
            self.metadata[snapshot_type] = metadata

            # 初始化已处理ID集合
            self.processed_ids[snapshot_type] = self._extract_ids(data)

            # 更新监控指标
            SNAPSHOT_OPERATION_COUNT.labels(operation_type="create_base", result="success").inc()
            SNAPSHOT_SIZE_BYTES.labels(snapshot_type=snapshot_type).set(metadata.size_bytes)
            SNAPSHOT_OPERATION_TIME.labels(operation_type="create_base").observe(
                (datetime.now() - start_time).total_seconds()
            )

            return True

        except Exception as e:
            SNAPSHOT_OPERATION_COUNT.labels(operation_type="create_base", result="error").inc()
            print(f"Failed to create base snapshot for {snapshot_type}: {e}")
            return False

    def update_incremental(self, snapshot_type: str, new_data: Any) -> Dict[str, Any]:
        """增量更新快照"""
        start_time = datetime.now()

        try:
            # 获取现有快照
            if snapshot_type not in self.snapshots:
                if not self.load_snapshot(snapshot_type):
                    raise ValueError(f"Base snapshot for {snapshot_type} not found")

            existing_data = self.snapshots[snapshot_type]
            existing_ids = self.processed_ids.get(snapshot_type, set())

            # 提取新数据的ID
            new_ids = self._extract_ids(new_data)

            # 找出新增和更新的数据
            new_records = []
            updated_records = []
            new_ids_set = set(new_ids)

            if isinstance(new_data, pd.DataFrame) and isinstance(existing_data, pd.DataFrame):
                # DataFrame增量更新
                existing_ids_set = set(existing_ids)

                # 新的记录
                new_mask = ~new_ids_set.issubset(existing_ids_set)
                if new_mask:
                    new_records_df = new_data[~new_data.index.isin(existing_ids)]
                    new_records = new_records_df.to_dict("records") if not new_records_df.empty else []

                # 更新的记录（暂时简化处理，实际可根据时间戳判断）
                updated_records = new_data[new_data.index.isin(existing_ids)].to_dict("records")

                # 合并数据
                updated_data = pd.concat([existing_data, new_records_df]) if not new_records_df.empty else existing_data
                # 去重（保留最新的）
                updated_data = updated_data[~updated_data.index.duplicated(keep="last")]

            else:
                # 简单的数据合并（适用于列表或字典）
                if isinstance(new_data, list) and isinstance(existing_data, list):
                    # 合并列表，保留新数据
                    updated_data = existing_data + [item for item in new_data if item not in existing_data]
                    new_records = [item for item in new_data if item not in existing_data]
                else:
                    # 字典更新
                    updated_data = {**existing_data, **new_data}
                    new_records = list(new_data.keys())
                    updated_records = [k for k in new_data.keys() if k in existing_data]

            # 更新快照
            self.snapshots[snapshot_type] = updated_data

            # 更新已处理ID
            self.processed_ids[snapshot_type].update(new_ids)

            # 更新元数据
            if snapshot_type in self.metadata:
                metadata = self.metadata[snapshot_type]
                metadata.last_modified = datetime.now()
                metadata.update_hash(updated_data)

                if isinstance(updated_data, pd.DataFrame):
                    metadata.record_count = len(updated_data)
                elif isinstance(updated_data, (list, dict)):
                    metadata.record_count = len(updated_data) if hasattr(updated_data, "__len__") else 1

                # 保存更新后的快照
                snapshot_path = self.base_dir / f"{snapshot_type}_incremental.pkl"
                with open(snapshot_path, "wb") as f:
                    pickle.dump(
                        {
                            "data": updated_data,
                            "metadata": metadata,
                            "type": "incremental",
                        },
                        f,
                    )

                metadata.size_bytes = snapshot_path.stat().st_size
                SNAPSHOT_SIZE_BYTES.labels(snapshot_type=snapshot_type).set(metadata.size_bytes)

            # 更新监控指标
            INCREMENTAL_UPDATE_COUNT.labels(data_type=snapshot_type).inc()
            SNAPSHOT_OPERATION_COUNT.labels(operation_type="incremental_update", result="success").inc()
            SNAPSHOT_OPERATION_TIME.labels(operation_type="incremental_update").observe(
                (datetime.now() - start_time).total_seconds()
            )

            return {
                "success": True,
                "new_records_count": len(new_records),
                "updated_records_count": len(updated_records),
                "total_records": metadata.record_count if snapshot_type in self.metadata else 0,
            }

        except Exception as e:
            SNAPSHOT_OPERATION_COUNT.labels(operation_type="incremental_update", result="error").inc()
            print(f"Failed to update snapshot incrementally for {snapshot_type}: {e}")
            return {"success": False, "error": str(e)}

    def load_snapshot(self, snapshot_type: str) -> bool:
        """加载快照"""
        try:
            # 优先加载增量快照
            incremental_path = self.base_dir / f"{snapshot_type}_incremental.pkl"
            base_path = self.base_dir / f"{snapshot_type}_base.pkl"

            snapshot_path = incremental_path if incremental_path.exists() else base_path

            if not snapshot_path.exists():
                return False

            with open(snapshot_path, "rb") as f:
                snapshot_data = pickle.load(f)

            self.snapshots[snapshot_type] = snapshot_data["data"]
            self.metadata[snapshot_type] = snapshot_data["metadata"]

            # 重新构建已处理ID集合
            self.processed_ids[snapshot_type] = self._extract_ids(snapshot_data["data"])

            SNAPSHOT_OPERATION_COUNT.labels(operation_type="load", result="success").inc()
            return True

        except Exception as e:
            SNAPSHOT_OPERATION_COUNT.labels(operation_type="load", result="error").inc()
            print(f"Failed to load snapshot for {snapshot_type}: {e}")
            return False

    def get_snapshot_data(self, snapshot_type: str) -> Optional[Any]:
        """获取快照数据"""
        # 如果不在缓存中，尝试加载
        if snapshot_type not in self.snapshots:
            if not self.load_snapshot(snapshot_type):
                return None

        return self.snapshots.get(snapshot_type)

    def get_snapshot_metadata(self, snapshot_type: str) -> Optional[SnapshotMetadata]:
        """获取快照元数据"""
        return self.metadata.get(snapshot_type)

    def list_snapshots(self) -> List[Dict[str, Any]]:
        """列出所有快照"""
        snapshots = []
        for snapshot_type in self.snapshots.keys():
            metadata = self.metadata.get(snapshot_type)
            if metadata:
                snapshots.append(
                    {
                        "type": snapshot_type,
                        "version": metadata.version,
                        "created_at": metadata.created_at.isoformat(),
                        "last_modified": metadata.last_modified.isoformat(),
                        "record_count": metadata.record_count,
                        "size_bytes": metadata.size_bytes,
                        "data_hash": metadata.data_hash,
                    }
                )

        return snapshots

    def cleanup_old_snapshots(self, max_age_days: int = 30) -> int:
        """清理旧快照文件"""
        cleaned_count = 0
        cutoff_date = datetime.now() - timedelta(days=max_age_days)

        try:
            for snapshot_file in self.base_dir.glob("*.pkl"):
                if snapshot_file.stat().st_mtime < cutoff_date.timestamp():
                    snapshot_file.unlink()
                    cleaned_count += 1

            SNAPSHOT_OPERATION_COUNT.labels(operation_type="cleanup", result="success").inc()

        except Exception as e:
            SNAPSHOT_OPERATION_COUNT.labels(operation_type="cleanup", result="error").inc()
            print(f"Failed to cleanup old snapshots: {e}")

        return cleaned_count

    def _extract_ids(self, data: Any) -> Set[str]:
        """从数据中提取ID集合"""
        ids = set()

        try:
            if isinstance(data, pd.DataFrame):
                # DataFrame的索引作为ID
                ids = set(data.index.astype(str))
            elif isinstance(data, list):
                # 列表中的字典ID
                for item in data:
                    if isinstance(item, dict) and "id" in item:
                        ids.add(str(item["id"]))
                    else:
                        # 使用内容哈希作为ID
                        ids.add(hashlib.md5(str(item).encode()).hexdigest()[:8])
            elif isinstance(data, dict):
                # 字典的键作为ID
                ids = set(data.keys())

        except Exception as e:
            print(f"Warning: Failed to extract IDs from data: {e}")

        return ids


# ==================== 全局实例 ====================

incremental_manager = IncrementalDataManager()

# ==================== 便捷函数 ====================


def create_test_snapshot(snapshot_type: str, data: Any, version: str = "1.0.0") -> bool:
    """便捷函数：创建测试快照"""
    return incremental_manager.create_base_snapshot(snapshot_type, data, version)


def update_test_data_incremental(snapshot_type: str, new_data: Any) -> Dict[str, Any]:
    """便捷函数：增量更新测试数据"""
    return incremental_manager.update_incremental(snapshot_type, new_data)


def get_test_data(snapshot_type: str) -> Optional[Any]:
    """便捷函数：获取测试数据"""
    return incremental_manager.get_snapshot_data(snapshot_type)


def list_available_snapshots() -> List[Dict[str, Any]]:
    """便捷函数：列出可用快照"""
    return incremental_manager.list_snapshots()
