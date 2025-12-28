"""
Memory Management Fix for GPU Data Processing
解决DataFrame内存泄漏问题的修复方案
"""

import gc
import sys
import time
import weakref
import psutil
import logging
from typing import Dict, List, Any
from functools import wraps
import pandas as pd
import warnings

# 抑制pandas的内存警告
warnings.filterwarnings("ignore", category=ResourceWarning)

logger = logging.getLogger(__name__)


class MemoryManager:
    """内存管理器 - 解决DataFrame内存泄漏问题"""

    def __init__(self):
        self.tracked_objects = weakref.WeakSet()
        self.memory_threshold = 0.8  # 80%内存使用阈值
        self.cleanup_count = 0
        self.last_cleanup_time = None

    def track_dataframe(self, df: pd.DataFrame, name: str = "") -> None:
        """跟踪DataFrame对象以便清理"""
        try:
            self.tracked_objects.add((weakref.ref(df), name))
            logger.debug(
                "Tracking DataFrame: %s, shape: %s, memory: %sMB", name, df.shape, df.memory_usage().sum() / 1024**2
            )
        except Exception as e:
            logger.warning("Failed to track DataFrame: %s", e)

    def cleanup_memory(self, force: bool = False) -> Dict[str, Any]:
        """清理内存并返回清理统计"""
        stats = {
            "before_cleanup_mb": 0,
            "after_cleanup_mb": 0,
            "objects_cleaned": 0,
            "force_cleanup": force,
        }

        try:
            # 获取清理前的内存使用
            process = psutil.Process()
            stats["before_cleanup_mb"] = process.memory_info().rss / 1024**2

            # 强制垃圾回收
            collected = gc.collect()
            stats["objects_cleaned"] = collected

            # 清理pandas缓存
            self._cleanup_pandas_cache()

            # 清理被跟踪的DataFrame
            self._cleanup_tracked_objects()

            # 再次获取清理后的内存使用
            stats["after_cleanup_mb"] = process.memory_info().rss / 1024**2

            # 内存使用率检查
            memory_percent = process.memory_percent()
            if memory_percent > self.memory_threshold * 100:
                logger.warning("High memory usage: %s%", memory_percent)
                # 执行深度清理
                self._deep_cleanup()

            self.cleanup_count += 1
            self.last_cleanup_time = time.time()
            logger.info(
                "Memory cleanup #{self.cleanup_count}: "
                f"Before: {stats['before_cleanup_mb']:.1f}MB, "
                f"After: {stats['after_cleanup_mb']:.1f}MB, "
                f"Freed: {stats['before_cleanup_mb'] - stats['after_cleanup_mb']:.1f}MB"
            )

        except Exception as e:
            logger.error("Memory cleanup failed: %s", e)

        return stats

    def _cleanup_pandas_cache(self) -> None:
        """清理pandas内部缓存"""
        try:
            # 清理pandas的字符串缓存
            pd.core.strings.StringDtype._cache.clear()

            # 清理pandas的解析缓存
            if hasattr(pd, "_libs"):
                pd._libs.lib.clear_cached()

        except Exception as e:
            logger.debug("Pandas cache cleanup warning: %s", e)

    def _cleanup_tracked_objects(self) -> None:
        """清理被跟踪的弱引用对象"""
        to_remove = []
        for ref, name in self.tracked_objects:
            obj = ref()
            if obj is None:
                to_remove.append((ref, name))

        # 移除已销毁的对象
        for item in to_remove:
            self.tracked_objects.discard(item)

    def _deep_cleanup(self) -> None:
        """深度内存清理"""
        try:
            # 多次垃圾回收
            for i in range(3):
                gc.collect()

            # 清理模块缓存
            modules_to_clear = []
            for module_name, module in sys.modules.items():
                if "pandas" in module_name or "numpy" in module_name:
                    modules_to_clear.append(module_name)

            for module_name in modules_to_clear:
                if module_name in sys.modules:
                    del sys.modules[module_name]

        except Exception as e:
            logger.warning("Deep cleanup failed: %s", e)

    def get_memory_stats(self) -> Dict[str, Any]:
        """获取内存统计信息"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()

            gc.get_stats()

            return {
                "current": {
                    "process_memory_mb": memory_info.rss / 1024**2,
                    "virtual_memory_mb": memory_info.vms / 1024**2,
                    "process_memory_percent": psutil.virtual_memory().percent,
                    "total_objects": len(gc.get_objects()),
                    "leak_candidates": self._get_leak_candidates(),
                },
                "tracked_objects": len(self.tracked_objects),
                "cleanup_count": self.cleanup_count,
                "last_cleanup_time": self.last_cleanup_time,
            }
        except Exception as e:
            logger.warning("Failed to get memory stats: %s", e)
            return {
                "current": {
                    "process_memory_mb": 0,
                    "virtual_memory_mb": 0,
                    "process_memory_percent": 0,
                    "total_objects": 0,
                    "leak_candidates": [],
                },
                "tracked_objects": 0,
                "cleanup_count": 0,
                "last_cleanup_time": None,
            }

    def _get_leak_candidates(self) -> List[str]:
        """获取内存泄漏候选者"""
        try:
            gc.collect()
            obj_counts = {}
            for obj in gc.get_objects():
                obj_type = type(obj).__name__
                obj_counts[obj_type] = obj_counts.get(obj_type, 0) + 1

            # 识别可能的泄漏模式
            leak_candidates = []
            for obj_type, count in obj_counts.items():
                # 某些类型的对象过多可能是泄漏的迹象
                if count > 1000:  # 阈值可调整
                    leak_candidates.append(f"{obj_type}:{count}")

            return leak_candidates[:10]  # 限制返回数量
        except Exception:
            return []


# 全局内存管理器实例
memory_manager = MemoryManager()


def memory_cleanup_decorator(threshold_mb: int = 100):
    """内存清理装饰器"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 检查内存使用
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024**2

            if memory_mb > threshold_mb:
                logger.debug("Memory cleanup before %s: %sMB", func.__name__, memory_mb)
                memory_manager.cleanup_memory()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # 函数执行后检查内存
                post_memory_mb = process.memory_info().rss / 1024**2
                if post_memory_mb > threshold_mb:
                    logger.debug("Memory cleanup after %s: %sMB", func.__name__, post_memory_mb)
                    memory_manager.cleanup_memory()

        return wrapper

    return decorator


def optimize_dataframe_memory(df: pd.DataFrame, inplace: bool = False) -> pd.DataFrame:
    """优化DataFrame内存使用"""
    if not inplace:
        df = df.copy()

    original_memory = df.memory_usage(deep=True).sum() / 1024**2

    # 优化数值类型
    for col in df.select_dtypes(include=["int64"]).columns:
        col_min = df[col].min()
        col_max = df[col].max()

        if col_min >= 0:
            if col_max < 255:
                df[col] = df[col].astype("uint8")
            elif col_max < 65535:
                df[col] = df[col].astype("uint16")
            elif col_max < 4294967295:
                df[col] = df[col].astype("uint32")
        else:
            if col_min >= -128 and col_max < 128:
                df[col] = df[col].astype("int8")
            elif col_min >= -32768 and col_max < 32768:
                df[col] = df[col].astype("int16")
            elif col_min >= -2147483648 and col_max < 2147483648:
                df[col] = df[col].astype("int32")

    # 优化浮点类型
    for col in df.select_dtypes(include=["float64"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="float")

    # 优化对象类型
    for col in df.select_dtypes(include=["object"]).columns:
        if df[col].nunique() / len(df[col]) < 0.5:  # 如果唯一值比例小于50%
            df[col] = df[col].astype("category")

    optimized_memory = df.memory_usage(deep=True).sum() / 1024**2
    compression_ratio = original_memory / optimized_memory if optimized_memory > 0 else 1.0

    logger.info(
        "DataFrame memory optimization: {original_memory:.1f}MB -> {optimized_memory:.1f}MB "
        f"(ratio: {compression_ratio:.1f}x)"
    )

    return df


def safe_dataframe_operation(func):
    """安全的DataFrame操作装饰器，确保内存清理"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            # 跟踪结果DataFrame
            if isinstance(result, pd.DataFrame):
                memory_manager.track_dataframe(result, func.__name__)
            return result
        except MemoryError as e:
            logger.error("Memory error in %s: %s", func.__name__, e)
            memory_manager.cleanup_memory(force=True)
            raise
        except Exception as e:
            logger.error("Error in %s: %s", func.__name__, e)
            raise

    return wrapper


# 使用示例和修复指南
class MemoryUsageGuide:
    """内存使用最佳实践指南"""

    @staticmethod
    def get_optimization_tips() -> List[str]:
        """获取内存优化技巧"""
        return [
            "1. 使用 .copy() 时谨慎，考虑使用 .loc[] 或 .iloc[] 进行选择性复制",
            "2. 及时删除不再需要的DataFrame: del df",
            "3. 使用 memory_cleanup_decorator 装饰器自动管理内存",
            "4. 优先使用 optimize_dataframe_memory 减少内存占用",
            "5. 避免在循环中创建大量临时DataFrame",
            "6. 使用 category 类型减少字符串内存使用",
            "7. 定期调用 memory_manager.cleanup_memory() 手动清理",
            "8. 监控内存使用情况，避免内存泄漏",
        ]

    @staticmethod
    def apply_memory_safe_patterns(df: pd.DataFrame) -> pd.DataFrame:
        """应用内存安全模式到DataFrame"""
        # 1. 内存优化
        df = optimize_dataframe_memory(df)

        # 2. 跟踪对象
        memory_manager.track_dataframe(df, "memory_safe_df")

        # 3. 设置适当的索引
        if df.index.name is None:
            df.index.name = "index"

        return df


# 导出主要组件
__all__ = [
    "MemoryManager",
    "memory_cleanup_decorator",
    "optimize_dataframe_memory",
    "safe_dataframe_operation",
    "MemoryUsageGuide",
    "memory_manager",
]
