"""
GPU工具模块
GPU Utility Module
"""

import importlib.util
import logging
import time
from typing import Any, Dict, List, Optional

try:
    import pynvml

    NVIDIA_AVAILABLE = True
except ImportError:
    NVIDIA_AVAILABLE = False
    logging.warning("NVIDIA ML library not available")

# 检查 CuPy 可用性
CUPY_AVAILABLE = bool(importlib.util.find_spec("cupy"))
if CUPY_AVAILABLE:
    logging.info("CuPy library available")
else:
    logging.warning("CuPy library not available")

# 检查 cuDF 可用性
CUDF_AVAILABLE = bool(importlib.util.find_spec("cudf"))
if CUDF_AVAILABLE:
    logging.info("cuDF library available")
else:
    logging.warning("cuDF library not available")

logger = logging.getLogger(__name__)


class GPUResourceManager:
    """GPU资源管理器"""

    def __init__(self, gpu_ids: List[int] = None):
        self.gpu_ids = gpu_ids or list(range(self.get_gpu_count()))
        self.gpu_states = {}
        self.reserved_memory = {}
        self.active_tasks = {}
        self.task_queue = []
        self.gpu_lock = {}

        # GPU优先级配置
        self.gpu_priority = {
            "high": [],  # 高优先级GPU
            "medium": [],  # 中优先级GPU
            "low": [],  # 低优先级GPU
        }

        logger.info("初始化GPU资源管理器，GPU数量: %s", len(self.gpu_ids))

    def initialize(self):
        """初始化GPU管理器"""
        if NVIDIA_AVAILABLE:
            try:
                pynvml.nvmlInit()
                logger.info("NVIDIA ML库初始化成功")
            except Exception as e:
                logger.error("NVIDIA ML库初始化失败: %s", e)

        # 初始化每个GPU的状态
        for gpu_id in self.gpu_ids:
            self.gpu_states[gpu_id] = {
                "utilization": 0,
                "memory_usage": 0,
                "memory_total": self.get_gpu_memory_total(gpu_id),
                "memory_free": self.get_gpu_memory_free(gpu_id),
                "temperature": self.get_gpu_temperature(gpu_id),
                "power_usage": self.get_gpu_power_usage(gpu_id),
                "fan_speed": self.get_gpu_fan_speed(gpu_id),
                "pcie_bandwidth": self.get_gpu_pcie_bandwidth(gpu_id),
                "ecc_memory_errors": self.get_gpu_ecc_memory_errors(gpu_id),
                "timestamp": time.time(),
            }

            # 初始化GPU锁
            self.gpu_lock[gpu_id] = False

            # 分类GPU优先级
            self.classify_gpu_priority(gpu_id)

            logger.info("GPU %s 初始化完成: %s", gpu_id, self.gpu_states[gpu_id])

    def get_gpu_count(self) -> int:
        """获取GPU数量"""
        if not NVIDIA_AVAILABLE:
            return 0
        try:
            return pynvml.nvmlDeviceGetCount()
        except pynvml.NVMLError as e:
            if hasattr(self, "logger"):
                self.logger.debug("NVIDIA GPU not available: %s", e)
            return 0
        except (ImportError, AttributeError) as e:
            if hasattr(self, "logger"):
                self.logger.warning("NVIDIA library not properly installed: %s", e)
            return 0

    def get_gpu_memory_total(self, gpu_id: int) -> int:
        """获取GPU总内存(MB)"""
        if not NVIDIA_AVAILABLE:
            return 0
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
            return pynvml.nvmlDeviceGetMemoryInfo(handle).total // (1024 * 1024)
        except Exception:
            return 0

    def get_gpu_memory_free(self, gpu_id: int) -> int:
        """获取GPU可用内存(MB)"""
        if not NVIDIA_AVAILABLE:
            return 0
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
            return pynvml.nvmlDeviceGetMemoryInfo(handle).free // (1024 * 1024)
        except Exception:
            return 0

    def get_gpu_memory_used(self, gpu_id: int) -> int:
        """获取GPU已用内存(MB)"""
        if not NVIDIA_AVAILABLE:
            return 0
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
            return pynvml.nvmlDeviceGetMemoryInfo(handle).used // (1024 * 1024)
        except Exception:
            return 0

    def get_gpu_utilization(self, gpu_id: int) -> float:
        """获取GPU利用率(%)"""
        if not NVIDIA_AVAILABLE:
            return 0
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
            return pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
        except Exception:
            return 0

    def get_gpu_temperature(self, gpu_id: int) -> int:
        """获取GPU温度(°C)"""
        if not NVIDIA_AVAILABLE:
            return 0
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
            return pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
        except Exception:
            return 0

    def get_gpu_power_usage(self, gpu_id: int) -> int:
        """获取GPU功耗(W)"""
        if not NVIDIA_AVAILABLE:
            return 0
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
            return pynvml.nvmlDeviceGetPowerUsage(handle) // 1000
        except Exception:
            return 0

    def get_gpu_fan_speed(self, gpu_id: int) -> int:
        """获取GPU风扇转速(RPM)"""
        if not NVIDIA_AVAILABLE:
            return 0
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
            return pynvml.nvmlDeviceGetFanSpeed(handle)
        except Exception:
            return 0

    def get_gpu_pcie_bandwidth(self, gpu_id: int) -> float:
        """获取GPU PCIE带宽(GB/s)"""
        if not NVIDIA_AVAILABLE:
            return 0
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
            # 获取当前PCIe带宽
            total = pynvml.nvmlDeviceGetPcieThroughput(handle, pynvml.NVML_PCIE_UTIL_COUNT)
            return total / 1024.0  # 转换为GB/s
        except Exception:
            return 0

    def get_gpu_ecc_memory_errors(self, gpu_id: int) -> int:
        """获取GPU内存错误计数"""
        if not NVIDIA_AVAILABLE:
            return 0
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
            return pynvml.nvmlDeviceGetTotalEccErrors(
                handle, pynvml.NVML_MEMORY_ERROR_TYPE_CORRECTED
            ).singleBitEccErrors
        except Exception:
            return 0

    def classify_gpu_priority(self, gpu_id: int):
        """根据GPU性能分类优先级"""
        memory = self.get_gpu_memory_total(gpu_id)
        temperature = self.get_gpu_temperature(gpu_id)

        if memory >= 16000 and temperature < 70:  # 大内存且低温
            self.gpu_priority["high"].append(gpu_id)
            logger.info("GPU %s 分类为高优先级", gpu_id)
        elif memory >= 8000 and temperature < 75:  # 中等内存温度
            self.gpu_priority["medium"].append(gpu_id)
            logger.info("GPU %s 分类为中优先级", gpu_id)
        else:
            self.gpu_priority["low"].append(gpu_id)
            logger.info("GPU %s 分类为低优先级", gpu_id)

    def get_gpu_stats(self) -> Dict[str, float]:
        """获取GPU统计信息"""
        if not self.gpu_states:
            return {}

        total_utilization = sum(state["utilization"] for state in self.gpu_states.values()) / len(self.gpu_states)
        total_memory_usage = sum(state["memory_usage"] for state in self.gpu_states.values()) / len(self.gpu_states)

        return {
            "utilization": total_utilization,
            "memory_usage": total_memory_usage,
            "gpu_count": len(self.gpu_states),
            "timestamp": time.time(),
        }

    def allocate_gpu(self, task_id: str, priority: str = "medium", memory_required: int = 0) -> Optional[int]:
        """分配GPU资源"""
        logger.info("为任务 %s 分配GPU，优先级: %s, 内存需求: %sMB", task_id, priority, memory_required)

        # 根据优先级选择GPU
        gpu_ids = self.gpu_priority.get(priority, [])
        if not gpu_ids and priority == "high":
            gpu_ids = self.gpu_priority.get("medium", [])
        if not gpu_ids and priority in ["high", "medium"]:
            gpu_ids = self.gpu_priority.get("low", [])
        if not gpu_ids:
            gpu_ids = self.gpu_ids

        # 检查GPU可用性
        for gpu_id in gpu_ids:
            if not self.gpu_lock[gpu_id]:
                # 检查内存是否足够
                available_memory = self.get_gpu_memory_free(gpu_id) - self.reserved_memory.get(gpu_id, 0)
                if memory_required == 0 or available_memory >= memory_required:
                    # 锁定GPU
                    self.gpu_lock[gpu_id] = True
                    self.reserved_memory[gpu_id] = self.reserved_memory.get(gpu_id, 0) + memory_required
                    self.active_tasks[gpu_id] = task_id

                    logger.info("已为任务 %s 分配GPU %s", task_id, gpu_id)
                    return gpu_id

        logger.warning("无法为任务 %s 分配GPU资源", task_id)
        return None

    def release_gpu(self, task_id: str, gpu_id: Optional[int] = None):
        """释放GPU资源"""
        if gpu_id is not None:
            if gpu_id in self.gpu_lock and self.gpu_lock[gpu_id]:
                self.gpu_lock[gpu_id] = False
                # 释放内存
                memory_released = self.reserved_memory.get(gpu_id, 0)
                self.reserved_memory[gpu_id] = 0
                del self.active_tasks[gpu_id]
                logger.info("已释放GPU %s，释放内存: %sMB", gpu_id, memory_released)
            else:
                logger.warning("GPU %s 未被锁定", gpu_id)
        else:
            # 通过任务ID查找GPU
            for gpu_id, task in self.active_tasks.items():
                if task == task_id:
                    self.gpu_lock[gpu_id] = False
                    memory_released = self.reserved_memory.get(gpu_id, 0)
                    self.reserved_memory[gpu_id] = 0
                    del self.active_tasks[gpu_id]
                    logger.info("已为任务 %s 释放GPU %s，释放内存: %sMB", task_id, gpu_id, memory_released)
                    break

    def update_gpu_status(self):
        """更新GPU状态"""
        for gpu_id in self.gpu_ids:
            if gpu_id in self.gpu_states:
                self.gpu_states[gpu_id].update(
                    {
                        "utilization": self.get_gpu_utilization(gpu_id),
                        "memory_usage": self.get_gpu_memory_used(gpu_id),
                        "memory_total": self.get_gpu_memory_total(gpu_id),
                        "memory_free": self.get_gpu_memory_free(gpu_id),
                        "temperature": self.get_gpu_temperature(gpu_id),
                        "power_usage": self.get_gpu_power_usage(gpu_id),
                        "fan_speed": self.get_gpu_fan_speed(gpu_id),
                        "pcie_bandwidth": self.get_gpu_pcie_bandwidth(gpu_id),
                        "ecc_memory_errors": self.get_gpu_ecc_memory_errors(gpu_id),
                        "timestamp": time.time(),
                    }
                )

    def get_available_gpu_count(self) -> int:
        """获取可用GPU数量"""
        return sum(1 for gpu_id in self.gpu_ids if not self.gpu_lock[gpu_id])

    def get_gpu_usage_summary(self) -> Dict[str, Any]:
        """获取GPU使用摘要"""
        total_gpus = len(self.gpu_ids)
        available_gpus = self.get_available_gpu_count()
        active_tasks = len(self.active_tasks)

        # 计算平均使用率
        total_utilization = sum(state["utilization"] for state in self.gpu_states.values())
        avg_utilization = total_utilization / len(self.gpu_states) if self.gpu_states else 0

        # 计算平均内存使用率
        total_memory_usage = sum(state["memory_usage"] for state in self.gpu_states.values())
        total_memory_total = sum(state["memory_total"] for state in self.gpu_states.values())
        avg_memory_usage = (total_memory_usage / total_memory_total * 100) if total_memory_total > 0 else 0

        return {
            "total_gpus": total_gpus,
            "available_gpus": available_gpus,
            "active_tasks": active_tasks,
            "average_utilization": avg_utilization,
            "average_memory_usage": avg_memory_usage,
            "gpu_states": self.gpu_states,
        }

    def cleanup(self):
        """清理资源"""
        # 释放所有GPU资源
        for gpu_id in self.gpu_ids:
            if self.gpu_lock[gpu_id]:
                self.release_gpu("cleanup", gpu_id)

        # 清理NVIDIA ML库
        if NVIDIA_AVAILABLE:
            try:
                pynvml.nvmlShutdown()
                logger.info("NVIDIA ML库已清理")
            except Exception as e:
                logger.error("NVIDIA ML库清理失败: %s", e)

        logger.info("GPU资源管理器已清理")


if __name__ == "__main__":
    # 测试GPU资源管理器
    gpu_manager = GPUResourceManager()
    gpu_manager.initialize()

    # 获取GPU状态摘要
    summary = gpu_manager.get_gpu_usage_summary()
    print(f"GPU状态摘要: {summary}")

    # 测试GPU分配
    gpu_id = gpu_manager.allocate_gpu("test_task_1", "medium", 2048)
    if gpu_id:
        print(f"分配GPU: {gpu_id}")

    # 释放GPU
    gpu_manager.release_gpu("test_task_1", gpu_id)
    print(f"释放GPU: {gpu_id}")

    # 清理
    gpu_manager.cleanup()
