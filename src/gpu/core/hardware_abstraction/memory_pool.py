"""
GPU内存池管理器
提供高效的GPU内存分配、回收和管理功能
"""

import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import threading

try:
    import cupy as cp

    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False
    cp = None

logger = logging.getLogger(__name__)


class MemoryBlockState(Enum):
    """内存块状态"""

    FREE = "free"
    ALLOCATED = "allocated"
    RESERVED = "reserved"


@dataclass
class MemoryBlock:
    """内存块"""

    id: str
    size_bytes: int
    ptr: Optional[Any] = None
    state: MemoryBlockState = MemoryBlockState.FREE
    allocation_time: float = 0.0
    last_access_time: float = 0.0
    access_count: int = 0
    pool_id: Optional[str] = None


class MemoryPool:
    """GPU内存池"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.is_initialized = False

        # 内存块管理
        self.memory_blocks: Dict[str, MemoryBlock] = {}
        self.free_blocks: List[str] = []
        self.allocated_blocks: List[str] = []

        # 性能统计
        self.stats = {
            "total_allocations": 0,
            "total_deallocations": 0,
            "peak_memory_usage": 0,
            "current_memory_usage": 0,
            "pool_hits": 0,
            "pool_misses": 0,
            "allocation_time_total": 0.0,
            "deallocation_time_total": 0.0,
        }

        # 配置参数
        self.max_pool_size = self.config.get("max_pool_size", 1024 * 1024 * 1024)  # 1GB
        self.min_block_size = self.config.get("min_block_size", 1024)  # 1KB
        self.max_block_size = self.config.get("max_block_size", 100 * 1024 * 1024)  # 100MB
        self.cleanup_threshold = self.config.get("cleanup_threshold", 0.8)  # 80%使用率触发清理

        # 线程安全
        self._lock = threading.RLock()

    async def initialize(self) -> bool:
        """初始化内存池"""
        try:
            if not CUPY_AVAILABLE:
                logger.warning("CuPy not available, memory pool disabled")
                return False

            # 预分配一些常用大小的内存块
            common_sizes = [1024, 4096, 16384, 65536, 262144, 1048576]  # 1KB到1MB

            for size in common_sizes:
                if self._get_current_memory_usage() + size <= self.max_pool_size:
                    block_id = f"prealloc_{size}"
                    block = MemoryBlock(
                        id=block_id,
                        size_bytes=size,
                        ptr=cp.zeros(size, dtype=cp.float32),
                        state=MemoryBlockState.FREE,
                        allocation_time=time.time(),
                    )
                    self.memory_blocks[block_id] = block
                    self.free_blocks.append(block_id)

            self.is_initialized = True
            logger.info("Memory pool initialized with %s preallocated blocks", len(self.free_blocks))
            return True

        except Exception as e:
            logger.error("Failed to initialize memory pool: %s", e)
            return False

    async def allocate(self, size_bytes: int) -> Optional[str]:
        """分配内存块"""
        start_time = time.time()

        try:
            if not self.is_initialized:
                await self.initialize()

            with self._lock:
                # 查找合适大小的空闲块
                block_id = self._find_free_block(size_bytes)

                if block_id:
                    # 重用现有块
                    block = self.memory_blocks[block_id]
                    block.state = MemoryBlockState.ALLOCATED
                    block.last_access_time = time.time()
                    block.access_count += 1

                    self.free_blocks.remove(block_id)
                    self.allocated_blocks.append(block_id)

                    self.stats["pool_hits"] += 1
                else:
                    # 创建新块
                    if self._can_allocate_new_block(size_bytes):
                        block_id = f"alloc_{int(time.time() * 1000000)}_{len(self.memory_blocks)}"
                        block = MemoryBlock(
                            id=block_id,
                            size_bytes=size_bytes,
                            ptr=cp.zeros(size_bytes, dtype=cp.float32),
                            state=MemoryBlockState.ALLOCATED,
                            allocation_time=time.time(),
                            last_access_time=time.time(),
                        )
                        self.memory_blocks[block_id] = block
                        self.allocated_blocks.append(block_id)

                        self.stats["pool_misses"] += 1
                    else:
                        # 尝试清理未使用的块
                        await self._cleanup_unused_blocks()
                        block_id = self._find_free_block(size_bytes)

                        if block_id:
                            block = self.memory_blocks[block_id]
                            block.state = MemoryBlockState.ALLOCATED
                            block.last_access_time = time.time()
                            block.access_count += 1

                            self.free_blocks.remove(block_id)
                            self.allocated_blocks.append(block_id)
                            self.stats["pool_hits"] += 1
                        else:
                            # 内存不足
                            logger.warning("Cannot allocate %s bytes: memory pool exhausted", size_bytes)
                            return None

                # 更新统计信息
                self.stats["total_allocations"] += 1
                self.stats["current_memory_usage"] = self._get_current_memory_usage()
                self.stats["peak_memory_usage"] = max(
                    self.stats["peak_memory_usage"], self.stats["current_memory_usage"]
                )

                allocation_time = (time.time() - start_time) * 1000
                self.stats["allocation_time_total"] += allocation_time

                return block_id

        except Exception as e:
            logger.error("Memory allocation failed: %s", e)
            return None

    async def deallocate(self, block_id: str) -> bool:
        """释放内存块"""
        start_time = time.time()

        try:
            with self._lock:
                if block_id not in self.memory_blocks:
                    logger.warning("Block %s not found in memory pool", block_id)
                    return False

                block = self.memory_blocks[block_id]

                if block.state != MemoryBlockState.ALLOCATED:
                    logger.warning("Block %s is not allocated", block_id)
                    return False

                # 清理GPU内存内容
                if block.ptr is not None and CUPY_AVAILABLE:
                    block.ptr.fill(0)  # 清零释放

                block.state = MemoryBlockState.FREE
                block.last_access_time = time.time()

                if block_id in self.allocated_blocks:
                    self.allocated_blocks.remove(block_id)
                if block_id not in self.free_blocks:
                    self.free_blocks.append(block_id)

                # 更新统计信息
                self.stats["total_deallocations"] += 1
                self.stats["current_memory_usage"] = self._get_current_memory_usage()

                deallocation_time = (time.time() - start_time) * 1000
                self.stats["deallocation_time_total"] += deallocation_time

                return True

        except Exception as e:
            logger.error("Memory deallocation failed: %s", e)
            return False

    def get_memory_ptr(self, block_id: str) -> Optional[Any]:
        """获取内存指针"""
        with self._lock:
            if block_id not in self.memory_blocks:
                return None

            block = self.memory_blocks[block_id]
            if block.state != MemoryBlockState.ALLOCATED:
                return None

            block.last_access_time = time.time()
            block.access_count += 1
            return block.ptr

    def _find_free_block(self, size_bytes: int) -> Optional[str]:
        """查找合适的空闲块"""
        best_block_id = None
        best_size_diff = float("inf")

        for block_id in self.free_blocks:
            block = self.memory_blocks[block_id]
            size_diff = block.size_bytes - size_bytes

            if 0 <= size_diff < best_size_diff:
                best_size_diff = size_diff
                best_block_id = block_id

        return best_block_id

    def _can_allocate_new_block(self, size_bytes: int) -> bool:
        """检查是否可以分配新块"""
        current_usage = self._get_current_memory_usage()
        return (current_usage + size_bytes) <= self.max_pool_size

    def _get_current_memory_usage(self) -> int:
        """获取当前内存使用量"""
        return sum(block.size_bytes for block in self.memory_blocks.values())

    async def _cleanup_unused_blocks(self) -> int:
        """清理未使用的内存块"""
        if not self.allocated_blocks:
            return 0

        # 找出长时间未使用的块
        current_time = time.time()
        cleanup_threshold_time = 300.0  # 5分钟未使用
        blocks_to_cleanup = []

        for block_id in self.allocated_blocks:
            block = self.memory_blocks[block_id]
            if (current_time - block.last_access_time) > cleanup_threshold_time:
                blocks_to_cleanup.append(block_id)

        # 清理块
        cleaned_count = 0
        for block_id in blocks_to_cleanup:
            if await self.deallocate(block_id):
                cleaned_count += 1

        if cleaned_count > 0:
            logger.info("Cleaned up %s unused memory blocks", cleaned_count)

        return cleaned_count

    def get_stats(self) -> Dict[str, Any]:
        """获取内存池统计信息"""
        with self._lock:
            return {
                **self.stats,
                "total_blocks": len(self.memory_blocks),
                "free_blocks": len(self.free_blocks),
                "allocated_blocks": len(self.allocated_blocks),
                "pool_efficiency": self.stats["pool_hits"] / max(1, self.stats["total_allocations"]),
                "average_allocation_time_ms": (
                    self.stats["allocation_time_total"] / max(1, self.stats["total_allocations"])
                ),
                "average_deallocation_time_ms": (
                    self.stats["deallocation_time_total"] / max(1, self.stats["total_deallocations"])
                ),
            }

    async def shutdown(self):
        """关闭内存池"""
        with self._lock:
            for block_id in list(self.memory_blocks.keys()):
                block = self.memory_blocks[block_id]
                if block.ptr is not None:
                    del block.ptr
                del self.memory_blocks[block_id]

            self.free_blocks.clear()
            self.allocated_blocks.clear()
            self.is_initialized = False

            logger.info("Memory pool shutdown completed")


# 内存池管理器单例
_memory_pool_instance: Optional[MemoryPool] = None


def get_memory_pool() -> MemoryPool:
    """获取内存池单例实例"""
    global _memory_pool_instance
    if _memory_pool_instance is None:
        _memory_pool_instance = MemoryPool()
    return _memory_pool_instance
