import pynvml
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GPUMetrics(BaseModel):
    device_id: int
    device_name: str
    timestamp: datetime

    gpu_utilization: float
    memory_used: int
    memory_total: int
    memory_utilization: float
    temperature: float
    power_usage: float
    power_limit: float

    sm_clock: int
    memory_clock: int
    pcie_throughput_tx: float
    pcie_throughput_rx: float


class GPUMonitoringService:
    def __init__(self):
        self.initialized = False
        self.device_count = 0
        self.handles = []
        try:
            pynvml.nvmlInit()
            self.device_count = pynvml.nvmlDeviceGetCount()
            self.handles = [pynvml.nvmlDeviceGetHandleByIndex(i) for i in range(self.device_count)]
            self.initialized = True
            logger.info(f"GPU monitoring initialized with {self.device_count} device(s)")
        except Exception as e:
            logger.warning(f"Failed to initialize NVML: {e}. Running in mock mode.")
            self.initialized = False

    def get_metrics(self, device_id: int = 0) -> GPUMetrics:
        if self.initialized and device_id < len(self.handles):
            return self._get_real_metrics(device_id)
        return self._get_mock_metrics(device_id)

    def _get_real_metrics(self, device_id: int) -> GPUMetrics:
        handle = self.handles[device_id]

        name = pynvml.nvmlDeviceGetName(handle)
        if isinstance(name, bytes):
            name = name.decode("utf-8")

        util = pynvml.nvmlDeviceGetUtilizationRates(handle)
        gpu_util = util.gpu
        memory_util = util.memory

        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        mem_used = mem_info.used // (1024**2)
        mem_total = mem_info.total // (1024**2)

        temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)

        try:
            power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
            power_limit = pynvml.nvmlDeviceGetPowerManagementLimit(handle) / 1000.0
        except pynvml.NVMLError:
            power = 0.0
            power_limit = 0.0

        try:
            sm_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_SM)
            mem_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM)
        except pynvml.NVMLError:
            sm_clock = 0
            mem_clock = 0

        try:
            pcie_tx = pynvml.nvmlDeviceGetPcieThroughput(handle, pynvml.NVML_PCIE_UTIL_TX_BYTES) / 1024
            pcie_rx = pynvml.nvmlDeviceGetPcieThroughput(handle, pynvml.NVML_PCIE_UTIL_RX_BYTES) / 1024
        except pynvml.NVMLError:
            pcie_tx = 0.0
            pcie_rx = 0.0

        return GPUMetrics(
            device_id=device_id,
            device_name=name,
            timestamp=datetime.now(),
            gpu_utilization=float(gpu_util),
            memory_used=int(mem_used),
            memory_total=int(mem_total),
            memory_utilization=float(memory_util),
            temperature=float(temp),
            power_usage=float(power),
            power_limit=float(power_limit),
            sm_clock=int(sm_clock),
            memory_clock=int(mem_clock),
            pcie_throughput_tx=float(pcie_tx),
            pcie_throughput_rx=float(pcie_rx),
        )

    def _get_mock_metrics(self, device_id: int = 0) -> GPUMetrics:
        return GPUMetrics(
            device_id=device_id,
            device_name="Mock GPU Device",
            timestamp=datetime.now(),
            gpu_utilization=0.0,
            memory_used=0,
            memory_total=0,
            memory_utilization=0.0,
            temperature=0.0,
            power_usage=0.0,
            power_limit=0.0,
            sm_clock=0,
            memory_clock=0,
            pcie_throughput_tx=0.0,
            pcie_throughput_rx=0.0,
        )

    def get_all_metrics(self) -> List[GPUMetrics]:
        if not self.initialized:
            return [self._get_mock_metrics(0)]
        return [self.get_metrics(i) for i in range(self.device_count)]

    def get_process_info(self, device_id: int = 0) -> List[Dict]:
        if not self.initialized or device_id >= len(self.handles):
            return []

        handle = self.handles[device_id]
        try:
            processes = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
        except pynvml.NVMLError:
            return []

        result = []
        import psutil

        for proc in processes:
            try:
                p = psutil.Process(proc.pid)
                result.append(
                    {
                        "pid": proc.pid,
                        "process_name": p.name(),
                        "memory_used_mb": proc.usedGpuMemory // (1024**2) if proc.usedGpuMemory else 0,
                        "cmdline": " ".join(p.cmdline()[:3]) if p.cmdline() else "",
                    }
                )
            except psutil.NoSuchProcess:
                pass

        return result

    def __del__(self):
        if self.initialized:
            try:
                pynvml.nvmlShutdown()
            except Exception:
                pass
