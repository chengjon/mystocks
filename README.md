# CLI-5 任务分配：Phase 6 GPU加速监控仪表板

**分配时间**: 2025-12-29
**预计工作量**: 8-10 工作日
**优先级**: Round 1 - 与CLI-1并行
**依赖**: 无 (GPU后端已在Phase 6.4完成)
**Worktree路径**: `/opt/claude/mystocks_phase6_monitoring`
**分支**: `phase6-gpu-monitoring`

---

## 📋 任务概览

### 核心目标
为**已实现的GPU加速引擎** (Phase 6.4完成, 68.58x性能提升) 构建**专业级监控仪表板**,提供实时GPU状态、性能指标、加速比分析和智能优化建议。

### 背景信息
**GPU加速引擎现状** (Phase 6.4已完成):
- ✅ 矩阵运算加速: **187.35x** (最大306.62x)
- ✅ 内存操作加速: **82.53x** (最大372.72x)
- ✅ 峰值性能: **662.52 GFLOPS**
- ✅ 长期稳定性: 83.3%成功率, 100%并发安全
- ✅ HAL层架构: 4层抽象,策略隔离,故障容灾
- ✅ 内存管理: 智能内存池,100%命中率

**监控需求**:
- 实时GPU状态 (利用率、显存、温度、功耗)
- 性能指标追踪 (GFLOPS、加速比、吞吐量)
- 历史数据分析 (趋势图、性能报告)
- 智能优化建议 (基于监控数据)

### 关键交付物
1. **GPU状态监控组件**: 实时显示GPU硬件状态
2. **性能仪表板**: 加速比、GFLOPS、吞吐量可视化
3. **历史数据分析**: 长期性能趋势和报告生成
4. **优化建议引擎**: AI驱动的性能优化建议
5. **告警系统**: GPU异常自动告警

### 技术栈
- **后端**: FastAPI (GPU监控API), psutil, pynvml (NVIDIA Management Library)
- **前端**: Vue 3 + TypeScript, ECharts (性能图表)
- **实时通信**: Server-Sent Events (SSE)
- **数据存储**: PostgreSQL (历史数据), Redis (实时缓存)

---

## 🎯 分阶段任务列表

### **阶段1: GPU监控后端 (Day 1-3)**

#### T5.1 GPU硬件监控服务
**目标**: 实时采集GPU硬件状态数据

**关键实现**:
```python
import pynvml
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime

class GPUMetrics(BaseModel):
    """GPU监控指标"""
    device_id: int
    device_name: str
    timestamp: datetime

    # 核心指标
    gpu_utilization: float      # GPU利用率 (%)
    memory_used: int            # 已使用显存 (MB)
    memory_total: int           # 总显存 (MB)
    memory_utilization: float   # 显存利用率 (%)
    temperature: float          # 温度 (°C)
    power_usage: float          # 功耗 (W)
    power_limit: float          # 功耗上限 (W)

    # 性能指标
    sm_clock: int               # SM时钟频率 (MHz)
    memory_clock: int           # 显存时钟频率 (MHz)
    pcie_throughput_tx: float   # PCIe发送吞吐量 (MB/s)
    pcie_throughput_rx: float   # PCIe接收吞吐量 (MB/s)

class GPUMonitoringService:
    """GPU监控服务"""

    def __init__(self):
        # 初始化NVML库
        pynvml.nvmlInit()
        self.device_count = pynvml.nvmlDeviceGetCount()
        self.handles = [
            pynvml.nvmlDeviceGetHandleByIndex(i)
            for i in range(self.device_count)
        ]

    def get_metrics(self, device_id: int = 0) -> GPUMetrics:
        """获取单个GPU的实时指标"""
        handle = self.handles[device_id]

        # 基本信息
        name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')

        # 利用率
        util = pynvml.nvmlDeviceGetUtilizationRates(handle)
        gpu_util = util.gpu
        memory_util = util.memory

        # 显存
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        mem_used = mem_info.used // (1024 ** 2)  # 转MB
        mem_total = mem_info.total // (1024 ** 2)

        # 温度
        temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)

        # 功耗
        power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # 转W
        power_limit = pynvml.nvmlDeviceGetPowerManagementLimit(handle) / 1000.0

        # 时钟频率
        sm_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_SM)
        mem_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM)

        # PCIe吞吐量
        pcie_tx = pynvml.nvmlDeviceGetPcieThroughput(handle, pynvml.NVML_PCIE_UTIL_TX_BYTES) / 1024  # KB/s → MB/s
        pcie_rx = pynvml.nvmlDeviceGetPcieThroughput(handle, pynvml.NVML_PCIE_UTIL_RX_BYTES) / 1024

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
            pcie_throughput_rx=float(pcie_rx)
        )

    def get_all_metrics(self) -> List[GPUMetrics]:
        """获取所有GPU的指标"""
        return [self.get_metrics(i) for i in range(self.device_count)]

    def get_process_info(self, device_id: int = 0) -> List[Dict]:
        """获取GPU上运行的进程信息"""
        handle = self.handles[device_id]
        processes = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)

        result = []
        for proc in processes:
            try:
                import psutil
                p = psutil.Process(proc.pid)
                result.append({
                    "pid": proc.pid,
                    "process_name": p.name(),
                    "memory_used_mb": proc.usedGpuMemory // (1024 ** 2),
                    "cmdline": " ".join(p.cmdline()[:3])  # 截取前3个参数
                })
            except psutil.NoSuchProcess:
                pass

        return result

    def __del__(self):
        """清理NVML"""
        try:
            pynvml.nvmlShutdown()
        except:
            pass
```

**API端点**:
```python
from fastapi import APIRouter
from typing import List

router = APIRouter(prefix="/api/gpu", tags=["GPU监控"])

gpu_monitor = GPUMonitoringService()

@router.get("/metrics", response_model=List[GPUMetrics])
async def get_gpu_metrics():
    """获取所有GPU的实时指标"""
    return gpu_monitor.get_all_metrics()

@router.get("/metrics/{device_id}", response_model=GPUMetrics)
async def get_gpu_metrics_by_id(device_id: int):
    """获取指定GPU的实时指标"""
    return gpu_monitor.get_metrics(device_id)

@router.get("/processes/{device_id}")
async def get_gpu_processes(device_id: int):
    """获取GPU上运行的进程"""
    return gpu_monitor.get_process_info(device_id)
```

**验收标准**:
- [ ] 成功采集GPU利用率、显存、温度、功耗
- [ ] 进程信息准确显示
- [ ] API响应时间 < 100ms

**预估时间**: 1天

---

#### T5.2 性能指标采集 (GFLOPS/加速比)
**目标**: 采集GPU加速引擎的性能指标

**关键实现**:
```python
from typing import Dict, Optional
from datetime import datetime, timedelta
import asyncio

class PerformanceMetrics(BaseModel):
    """性能指标"""
    timestamp: datetime

    # 矩阵运算性能
    matrix_gflops: float            # 矩阵运算GFLOPS
    matrix_speedup: float           # 矩阵运算加速比
    matrix_throughput: float        # 矩阵运算吞吐量 (ops/s)

    # 内存操作性能
    memory_bandwidth_gbs: float     # 内存带宽 (GB/s)
    memory_speedup: float           # 内存操作加速比
    memory_throughput: float        # 内存操作吞吐量 (ops/s)

    # 综合指标
    overall_speedup: float          # 综合加速比
    cache_hit_rate: float           # 缓存命中率 (%)
    success_rate: float             # 任务成功率 (%)

class PerformanceCollector:
    """性能指标采集器"""

    def __init__(self):
        self.recent_benchmarks = []  # 最近100次基准测试结果
        self.cache_stats = {"hits": 0, "misses": 0}

    async def collect_performance_metrics(self) -> PerformanceMetrics:
        """采集当前性能指标"""

        # 运行轻量级基准测试 (每次采集时执行一次)
        benchmark_result = await self._run_lightweight_benchmark()

        # 计算加速比
        matrix_speedup = self._calculate_speedup(
            benchmark_result['gpu_matrix_time'],
            benchmark_result['cpu_matrix_time']
        )

        memory_speedup = self._calculate_speedup(
            benchmark_result['gpu_memory_time'],
            benchmark_result['cpu_memory_time']
        )

        overall_speedup = (matrix_speedup + memory_speedup) / 2

        # 计算GFLOPS
        matrix_gflops = self._calculate_gflops(
            benchmark_result['matrix_ops'],
            benchmark_result['gpu_matrix_time']
        )

        # 计算内存带宽
        memory_bandwidth = self._calculate_bandwidth(
            benchmark_result['memory_bytes'],
            benchmark_result['gpu_memory_time']
        )

        # 缓存命中率
        cache_hit_rate = self._calculate_cache_hit_rate()

        # 成功率 (最近100次任务)
        success_rate = self._calculate_success_rate()

        return PerformanceMetrics(
            timestamp=datetime.now(),
            matrix_gflops=matrix_gflops,
            matrix_speedup=matrix_speedup,
            matrix_throughput=benchmark_result['matrix_throughput'],
            memory_bandwidth_gbs=memory_bandwidth,
            memory_speedup=memory_speedup,
            memory_throughput=benchmark_result['memory_throughput'],
            overall_speedup=overall_speedup,
            cache_hit_rate=cache_hit_rate,
            success_rate=success_rate
        )

    async def _run_lightweight_benchmark(self) -> Dict:
        """运行轻量级基准测试 (512x512矩阵乘法)"""
        import cupy as cp
        import numpy as np
        import time

        # 矩阵大小
        N = 512

        # GPU基准测试
        A_gpu = cp.random.rand(N, N, dtype=cp.float32)
        B_gpu = cp.random.rand(N, N, dtype=cp.float32)

        start = time.perf_counter()
        C_gpu = cp.matmul(A_gpu, B_gpu)
        cp.cuda.Device().synchronize()
        gpu_matrix_time = time.perf_counter() - start

        # CPU基准测试
        A_cpu = np.random.rand(N, N).astype(np.float32)
        B_cpu = np.random.rand(N, N).astype(np.float32)

        start = time.perf_counter()
        C_cpu = np.matmul(A_cpu, B_cpu)
        cpu_matrix_time = time.perf_counter() - start

        # 计算FLOPS (矩阵乘法: 2*N^3 FLOPs)
        matrix_ops = 2 * (N ** 3)
        matrix_throughput = 1.0 / gpu_matrix_time  # 每秒矩阵运算次数

        # 内存操作基准测试
        memory_bytes = N * N * 4  # float32 = 4 bytes

        start = time.perf_counter()
        D_gpu = cp.copy(A_gpu)
        cp.cuda.Device().synchronize()
        gpu_memory_time = time.perf_counter() - start

        start = time.perf_counter()
        D_cpu = np.copy(A_cpu)
        cpu_memory_time = time.perf_counter() - start

        memory_throughput = 1.0 / gpu_memory_time

        return {
            'gpu_matrix_time': gpu_matrix_time,
            'cpu_matrix_time': cpu_matrix_time,
            'gpu_memory_time': gpu_memory_time,
            'cpu_memory_time': cpu_memory_time,
            'matrix_ops': matrix_ops,
            'memory_bytes': memory_bytes,
            'matrix_throughput': matrix_throughput,
            'memory_throughput': memory_throughput
        }

    def _calculate_speedup(self, gpu_time: float, cpu_time: float) -> float:
        """计算加速比"""
        if gpu_time == 0:
            return 0.0
        return cpu_time / gpu_time

    def _calculate_gflops(self, ops: int, time_sec: float) -> float:
        """计算GFLOPS"""
        if time_sec == 0:
            return 0.0
        flops = ops / time_sec
        return flops / 1e9  # 转GFLOPS

    def _calculate_bandwidth(self, bytes_transferred: int, time_sec: float) -> float:
        """计算内存带宽 (GB/s)"""
        if time_sec == 0:
            return 0.0
        bytes_per_sec = bytes_transferred / time_sec
        return bytes_per_sec / 1e9  # 转GB/s

    def _calculate_cache_hit_rate(self) -> float:
        """计算缓存命中率"""
        total = self.cache_stats["hits"] + self.cache_stats["misses"]
        if total == 0:
            return 0.0
        return (self.cache_stats["hits"] / total) * 100

    def _calculate_success_rate(self) -> float:
        """计算任务成功率 (最近100次)"""
        if not self.recent_benchmarks:
            return 0.0

        successful = sum(1 for b in self.recent_benchmarks if b['success'])
        return (successful / len(self.recent_benchmarks)) * 100

    def record_benchmark(self, result: Dict):
        """记录基准测试结果"""
        self.recent_benchmarks.append(result)
        if len(self.recent_benchmarks) > 100:
            self.recent_benchmarks.pop(0)

    def update_cache_stats(self, hit: bool):
        """更新缓存统计"""
        if hit:
            self.cache_stats["hits"] += 1
        else:
            self.cache_stats["misses"] += 1
```

**API端点**:
```python
perf_collector = PerformanceCollector()

@router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_metrics():
    """获取当前性能指标"""
    return await perf_collector.collect_performance_metrics()
```

**验收标准**:
- [ ] 成功采集GFLOPS、加速比、吞吐量
- [ ] 缓存命中率计算准确
- [ ] 轻量级基准测试完成时间 < 500ms

**预估时间**: 1天

---

#### T5.3 历史数据持久化和查询
**目标**: 将监控数据持久化到PostgreSQL,支持历史查询

**数据库Schema**:
```sql
-- GPU监控历史数据表
CREATE TABLE IF NOT EXISTS gpu_monitoring_history (
    id SERIAL PRIMARY KEY,
    device_id INT NOT NULL,
    timestamp TIMESTAMP NOT NULL,

    -- GPU硬件指标
    gpu_utilization FLOAT,
    memory_used INT,
    memory_total INT,
    memory_utilization FLOAT,
    temperature FLOAT,
    power_usage FLOAT,
    sm_clock INT,
    memory_clock INT,

    -- 性能指标
    matrix_gflops FLOAT,
    matrix_speedup FLOAT,
    memory_bandwidth_gbs FLOAT,
    overall_speedup FLOAT,
    cache_hit_rate FLOAT,
    success_rate FLOAT,

    created_at TIMESTAMP DEFAULT NOW()
);

-- 索引优化
CREATE INDEX idx_gpu_monitoring_device_time ON gpu_monitoring_history(device_id, timestamp DESC);
CREATE INDEX idx_gpu_monitoring_timestamp ON gpu_monitoring_history(timestamp DESC);

-- 性能事件表 (异常事件记录)
CREATE TABLE IF NOT EXISTS gpu_performance_events (
    id SERIAL PRIMARY KEY,
    device_id INT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    event_type VARCHAR(50),  -- 'high_temp', 'low_utilization', 'memory_leak', 'performance_drop'
    severity VARCHAR(20),    -- 'info', 'warning', 'critical'
    message TEXT,
    metadata JSONB,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**历史数据服务**:
```python
from sqlalchemy import create_engine, Column, Integer, Float, DateTime, String, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
from datetime import datetime, timedelta

Base = declarative_base()

class GPUMonitoringHistory(Base):
    __tablename__ = "gpu_monitoring_history"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    gpu_utilization = Column(Float)
    memory_used = Column(Integer)
    memory_total = Column(Integer)
    temperature = Column(Float)
    power_usage = Column(Float)
    matrix_gflops = Column(Float)
    overall_speedup = Column(Float)
    cache_hit_rate = Column(Float)

class GPUPerformanceEvent(Base):
    __tablename__ = "gpu_performance_events"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    event_type = Column(String(50))
    severity = Column(String(20))
    message = Column(Text)
    resolved = Column(Boolean, default=False)

class HistoryDataService:
    """历史数据服务"""

    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def save_metrics(self, gpu_metrics: GPUMetrics, perf_metrics: PerformanceMetrics):
        """保存监控指标"""
        record = GPUMonitoringHistory(
            device_id=gpu_metrics.device_id,
            timestamp=gpu_metrics.timestamp,
            gpu_utilization=gpu_metrics.gpu_utilization,
            memory_used=gpu_metrics.memory_used,
            memory_total=gpu_metrics.memory_total,
            temperature=gpu_metrics.temperature,
            power_usage=gpu_metrics.power_usage,
            matrix_gflops=perf_metrics.matrix_gflops,
            overall_speedup=perf_metrics.overall_speedup,
            cache_hit_rate=perf_metrics.cache_hit_rate
        )
        self.session.add(record)
        self.session.commit()

    def query_history(
        self,
        device_id: int,
        start_time: datetime,
        end_time: datetime
    ) -> List[GPUMonitoringHistory]:
        """查询历史数据"""
        return self.session.query(GPUMonitoringHistory).filter(
            GPUMonitoringHistory.device_id == device_id,
            GPUMonitoringHistory.timestamp >= start_time,
            GPUMonitoringHistory.timestamp <= end_time
        ).order_by(GPUMonitoringHistory.timestamp.desc()).all()

    def get_aggregated_stats(
        self,
        device_id: int,
        hours: int = 24
    ) -> Dict:
        """获取聚合统计 (最近N小时)"""
        start_time = datetime.now() - timedelta(hours=hours)

        from sqlalchemy import func

        stats = self.session.query(
            func.avg(GPUMonitoringHistory.gpu_utilization).label('avg_utilization'),
            func.max(GPUMonitoringHistory.gpu_utilization).label('max_utilization'),
            func.avg(GPUMonitoringHistory.temperature).label('avg_temperature'),
            func.max(GPUMonitoringHistory.temperature).label('max_temperature'),
            func.avg(GPUMonitoringHistory.matrix_gflops).label('avg_gflops'),
            func.max(GPUMonitoringHistory.matrix_gflops).label('peak_gflops'),
            func.avg(GPUMonitoringHistory.overall_speedup).label('avg_speedup')
        ).filter(
            GPUMonitoringHistory.device_id == device_id,
            GPUMonitoringHistory.timestamp >= start_time
        ).first()

        return {
            "avg_utilization": float(stats.avg_utilization or 0),
            "max_utilization": float(stats.max_utilization or 0),
            "avg_temperature": float(stats.avg_temperature or 0),
            "max_temperature": float(stats.max_temperature or 0),
            "avg_gflops": float(stats.avg_gflops or 0),
            "peak_gflops": float(stats.peak_gflops or 0),
            "avg_speedup": float(stats.avg_speedup or 0)
        }

    def log_event(self, event: GPUPerformanceEvent):
        """记录性能事件"""
        self.session.add(event)
        self.session.commit()
```

**API端点**:
```python
history_service = HistoryDataService(db_url="postgresql://user:pass@localhost/mystocks")

@router.get("/history/{device_id}")
async def get_gpu_history(
    device_id: int,
    hours: int = 24
):
    """获取历史数据"""
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    return history_service.query_history(device_id, start_time, end_time)

@router.get("/stats/{device_id}")
async def get_aggregated_stats(device_id: int, hours: int = 24):
    """获取聚合统计"""
    return history_service.get_aggregated_stats(device_id, hours)
```

**验收标准**:
- [ ] 数据成功持久化到PostgreSQL
- [ ] 历史查询速度 < 500ms (24小时数据)
- [ ] 聚合统计计算准确

**预估时间**: 1天

---

### **阶段2: 前端仪表板 (Day 4-6)**

#### T5.4 GPU状态卡片组件
**目标**: 实时显示GPU硬件状态

**核心组件**:
```typescript
// web/frontend/src/components/GPUMonitoring/GPUStatusCard.vue
<template>
  <el-card class="gpu-status-card">
    <template #header>
      <div class="card-header">
        <span>GPU {{ deviceId }}: {{ deviceName }}</span>
        <el-tag :type="getStatusTagType(status)" size="small">
          {{ status }}
        </el-tag>
      </div>
    </template>

    <div class="metrics-grid">
      <!-- GPU利用率 -->
      <div class="metric-item">
        <div class="metric-label">GPU利用率</div>
        <el-progress
          type="dashboard"
          :percentage="metrics.gpu_utilization"
          :color="getUtilizationColor(metrics.gpu_utilization)"
        >
          <template #default="{ percentage }">
            <span class="percentage-value">{{ percentage }}%</span>
          </template>
        </el-progress>
      </div>

      <!-- 显存使用 -->
      <div class="metric-item">
        <div class="metric-label">显存使用</div>
        <el-progress
          type="dashboard"
          :percentage="metrics.memory_utilization"
          :color="getMemoryColor(metrics.memory_utilization)"
        >
          <template #default>
            <span class="percentage-value">
              {{ formatMemory(metrics.memory_used) }} / {{ formatMemory(metrics.memory_total) }}
            </span>
          </template>
        </el-progress>
      </div>

      <!-- 温度 -->
      <div class="metric-item">
        <div class="metric-label">温度</div>
        <div class="metric-value" :class="getTemperatureClass(metrics.temperature)">
          {{ metrics.temperature.toFixed(1) }}°C
        </div>
        <el-progress
          :percentage="(metrics.temperature / 100) * 100"
          :show-text="false"
          :color="getTemperatureColor(metrics.temperature)"
        />
      </div>

      <!-- 功耗 -->
      <div class="metric-item">
        <div class="metric-label">功耗</div>
        <div class="metric-value">
          {{ metrics.power_usage.toFixed(1) }} W / {{ metrics.power_limit.toFixed(0) }} W
        </div>
        <el-progress
          :percentage="(metrics.power_usage / metrics.power_limit) * 100"
          :show-text="false"
        />
      </div>

      <!-- 时钟频率 -->
      <div class="metric-item">
        <div class="metric-label">SM频率</div>
        <div class="metric-value">{{ metrics.sm_clock }} MHz</div>
      </div>

      <div class="metric-item">
        <div class="metric-label">显存频率</div>
        <div class="metric-value">{{ metrics.memory_clock }} MHz</div>
      </div>

      <!-- PCIe吞吐量 -->
      <div class="metric-item">
        <div class="metric-label">PCIe吞吐量</div>
        <div class="metric-value">
          ↑ {{ metrics.pcie_throughput_tx.toFixed(2) }} MB/s<br>
          ↓ {{ metrics.pcie_throughput_rx.toFixed(2) }} MB/s
        </div>
      </div>
    </div>

    <!-- 运行进程 -->
    <el-divider />
    <div class="processes-section">
      <div class="section-title">运行进程 ({{ processes.length }})</div>
      <el-table :data="processes" size="small" max-height="200">
        <el-table-column prop="pid" label="PID" width="80" />
        <el-table-column prop="process_name" label="进程名" width="150" />
        <el-table-column label="显存占用" width="120">
          <template #default="{ row }">
            {{ formatMemory(row.memory_used_mb) }}
          </template>
        </el-table-column>
        <el-table-column prop="cmdline" label="命令行" show-overflow-tooltip />
      </el-table>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';

const props = defineProps<{
  deviceId: number;
}>();

const deviceName = ref('');
const status = ref('正常');
const metrics = ref({
  gpu_utilization: 0,
  memory_used: 0,
  memory_total: 0,
  memory_utilization: 0,
  temperature: 0,
  power_usage: 0,
  power_limit: 0,
  sm_clock: 0,
  memory_clock: 0,
  pcie_throughput_tx: 0,
  pcie_throughput_rx: 0
});
const processes = ref([]);

let updateInterval: number;

const fetchMetrics = async () => {
  try {
    const [metricsResp, processesResp] = await Promise.all([
      axios.get(`/api/gpu/metrics/${props.deviceId}`),
      axios.get(`/api/gpu/processes/${props.deviceId}`)
    ]);

    deviceName.value = metricsResp.data.device_name;
    metrics.value = metricsResp.data;
    processes.value = processesResp.data;

    // 判断状态
    if (metrics.value.temperature > 85) {
      status.value = '高温';
    } else if (metrics.value.gpu_utilization > 95) {
      status.value = '繁忙';
    } else if (metrics.value.gpu_utilization < 10) {
      status.value = '空闲';
    } else {
      status.value = '正常';
    }
  } catch (error) {
    console.error('获取GPU指标失败:', error);
  }
};

const getUtilizationColor = (value: number) => {
  if (value < 30) return '#909399';  // 灰色 (空闲)
  if (value < 70) return '#67C23A';  // 绿色 (正常)
  if (value < 90) return '#E6A23C';  // 橙色 (繁忙)
  return '#F56C6C';  // 红色 (满载)
};

const getMemoryColor = (value: number) => {
  if (value < 60) return '#67C23A';
  if (value < 80) return '#E6A23C';
  return '#F56C6C';
};

const getTemperatureColor = (temp: number) => {
  if (temp < 60) return '#67C23A';
  if (temp < 80) return '#E6A23C';
  return '#F56C6C';
};

const getTemperatureClass = (temp: number) => {
  if (temp > 85) return 'temp-critical';
  if (temp > 75) return 'temp-warning';
  return 'temp-normal';
};

const getStatusTagType = (status: string) => {
  const map: Record<string, any> = {
    '正常': 'success',
    '繁忙': 'warning',
    '高温': 'danger',
    '空闲': 'info'
  };
  return map[status] || 'info';
};

const formatMemory = (mb: number) => {
  if (mb >= 1024) {
    return `${(mb / 1024).toFixed(2)} GB`;
  }
  return `${mb.toFixed(0)} MB`;
};

onMounted(() => {
  fetchMetrics();
  updateInterval = window.setInterval(fetchMetrics, 2000);  // 每2秒更新
});

onUnmounted(() => {
  clearInterval(updateInterval);
});
</script>

<style scoped>
.gpu-status-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.metric-item {
  text-align: center;
}

.metric-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 18px;
  font-weight: bold;
  margin: 8px 0;
}

.temp-critical {
  color: #F56C6C;
}

.temp-warning {
  color: #E6A23C;
}

.temp-normal {
  color: #67C23A;
}

.processes-section {
  margin-top: 16px;
}

.section-title {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 8px;
}
</style>
```

**验收标准**:
- [ ] GPU状态实时更新 (2秒刷新)
- [ ] 进度条颜色根据阈值变化
- [ ] 进程信息正确显示

**预估时间**: 1天

---

#### T5.5 性能图表组件 (GFLOPS/加速比趋势)
**目标**: 可视化性能趋势

**核心组件**:
```typescript
// web/frontend/src/components/GPUMonitoring/PerformanceChart.vue
<template>
  <el-card>
    <template #header>
      <div class="header">
        <span>性能趋势</span>
        <el-radio-group v-model="timeRange" size="small" @change="fetchData">
          <el-radio-button label="1h">1小时</el-radio-button>
          <el-radio-button label="6h">6小时</el-radio-button>
          <el-radio-button label="24h">24小时</el-radio-button>
        </el-radio-group>
      </div>
    </template>

    <div ref="chartRef" style="width: 100%; height: 400px;"></div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';

const timeRange = ref('1h');
const chartRef = ref<HTMLElement>();
let chartInstance: echarts.ECharts;

const fetchData = async () => {
  const hours = parseInt(timeRange.value);
  const response = await axios.get(`/api/gpu/history/0?hours=${hours}`);
  const data = response.data;

  // 提取时间序列
  const timestamps = data.map((d: any) => new Date(d.timestamp).toLocaleTimeString());
  const gflops = data.map((d: any) => d.matrix_gflops);
  const speedup = data.map((d: any) => d.overall_speedup);
  const temperature = data.map((d: any) => d.temperature);
  const utilization = data.map((d: any) => d.gpu_utilization);

  const option = {
    title: {
      text: 'GPU性能趋势'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['GFLOPS', '加速比', '温度', 'GPU利用率']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: timestamps
    },
    yAxis: [
      {
        type: 'value',
        name: 'GFLOPS / 加速比',
        position: 'left'
      },
      {
        type: 'value',
        name: '温度 / 利用率',
        position: 'right'
      }
    ],
    series: [
      {
        name: 'GFLOPS',
        type: 'line',
        smooth: true,
        data: gflops,
        yAxisIndex: 0,
        itemStyle: { color: '#5470C6' }
      },
      {
        name: '加速比',
        type: 'line',
        smooth: true,
        data: speedup,
        yAxisIndex: 0,
        itemStyle: { color: '#91CC75' }
      },
      {
        name: '温度',
        type: 'line',
        smooth: true,
        data: temperature,
        yAxisIndex: 1,
        itemStyle: { color: '#EE6666' }
      },
      {
        name: 'GPU利用率',
        type: 'line',
        smooth: true,
        data: utilization,
        yAxisIndex: 1,
        itemStyle: { color: '#FAC858' }
      }
    ]
  };

  chartInstance.setOption(option);
};

onMounted(() => {
  chartInstance = echarts.init(chartRef.value!);
  fetchData();
});

watch(timeRange, fetchData);
</script>
```

**验收标准**:
- [ ] 图表实时更新
- [ ] 支持1h/6h/24h时间范围切换
- [ ] 四条曲线正常显示

**预估时间**: 1天

---

#### T5.6 智能优化建议组件
**目标**: 基于监控数据生成优化建议

**关键实现**:
```python
from typing import List
from pydantic import BaseModel

class OptimizationRecommendation(BaseModel):
    """优化建议"""
    title: str
    category: str  # 'performance', 'temperature', 'memory', 'efficiency'
    severity: str  # 'info', 'warning', 'critical'
    description: str
    expected_improvement: str
    action_steps: List[str]

class OptimizationAdvisor:
    """优化建议引擎"""

    def analyze_and_recommend(
        self,
        gpu_metrics: GPUMetrics,
        perf_metrics: PerformanceMetrics,
        stats_24h: Dict
    ) -> List[OptimizationRecommendation]:
        """分析并生成优化建议"""

        recommendations = []

        # 规则1: GPU利用率过低
        if stats_24h['avg_utilization'] < 30:
            recommendations.append(OptimizationRecommendation(
                title="GPU利用率过低",
                category="efficiency",
                severity="warning",
                description=f"过去24小时平均GPU利用率仅{stats_24h['avg_utilization']:.1f}%,存在资源浪费",
                expected_improvement="提升利用率可降低每GFLOP成本",
                action_steps=[
                    "增加批处理大小 (batch_size)",
                    "并行执行多个回测任务",
                    "检查是否有CPU瓶颈限制GPU性能"
                ]
            ))

        # 规则2: 温度过高
        if stats_24h['max_temperature'] > 85:
            recommendations.append(OptimizationRecommendation(
                title="温度过高警告",
                category="temperature",
                severity="critical",
                description=f"GPU最高温度达到{stats_24h['max_temperature']:.1f}°C,可能影响性能和寿命",
                expected_improvement="降温可提升3-5%性能并延长硬件寿命",
                action_steps=[
                    "检查机箱风扇运行状态",
                    "清理GPU散热器灰尘",
                    "降低GPU功耗限制 (power_limit)",
                    "考虑增加机箱散热风扇"
                ]
            ))

        # 规则3: 显存利用率低
        if gpu_metrics.memory_utilization < 50:
            recommendations.append(OptimizationRecommendation(
                title="显存利用率较低",
                category="memory",
                severity="info",
                description=f"当前显存利用率{gpu_metrics.memory_utilization:.1f}%,可增加数据批处理大小",
                expected_improvement="提升显存利用率可提高10-20%吞吐量",
                action_steps=[
                    "增加batch_size (当前可能偏小)",
                    "减少内存池预留空间",
                    "预加载更多数据到显存"
                ]
            ))

        # 规则4: 加速比低于预期
        if perf_metrics.overall_speedup < 50:
            recommendations.append(OptimizationRecommendation(
                title="加速比低于预期",
                category="performance",
                severity="warning",
                description=f"当前综合加速比{perf_metrics.overall_speedup:.2f}x,远低于目标68.58x",
                expected_improvement="优化算法可达到目标加速比",
                action_steps=[
                    "检查是否使用Strassen算法 (O(n^2.807))",
                    "启用CUDA流并行",
                    "使用分块矩阵乘法优化大矩阵",
                    "检查GPU驱动版本是否最新"
                ]
            ))

        # 规则5: 缓存命中率低
        if perf_metrics.cache_hit_rate < 80:
            recommendations.append(OptimizationRecommendation(
                title="缓存命中率偏低",
                category="performance",
                severity="info",
                description=f"内存池缓存命中率{perf_metrics.cache_hit_rate:.1f}%,存在优化空间",
                expected_improvement="提升缓存命中率可减少30%内存分配开销",
                action_steps=[
                    "增加内存池大小",
                    "优化内存块重用策略",
                    "预分配常用尺寸内存块"
                ]
            ))

        return recommendations

# API端点
advisor = OptimizationAdvisor()

@router.get("/recommendations", response_model=List[OptimizationRecommendation])
async def get_optimization_recommendations(device_id: int = 0):
    """获取优化建议"""
    gpu_metrics = gpu_monitor.get_metrics(device_id)
    perf_metrics = await perf_collector.collect_performance_metrics()
    stats_24h = history_service.get_aggregated_stats(device_id, hours=24)

    return advisor.analyze_and_recommend(gpu_metrics, perf_metrics, stats_24h)
```

**前端组件**:
```typescript
// web/frontend/src/components/GPUMonitoring/OptimizationPanel.vue
<template>
  <el-card>
    <template #header>
      <span>智能优化建议</span>
      <el-button size="small" @click="fetchRecommendations">刷新</el-button>
    </template>

    <el-alert
      v-for="rec in recommendations"
      :key="rec.title"
      :title="rec.title"
      :type="getSeverityType(rec.severity)"
      :closable="false"
      class="recommendation-alert"
    >
      <template #default>
        <p><strong>问题描述:</strong> {{ rec.description }}</p>
        <p><strong>预期改善:</strong> {{ rec.expected_improvement }}</p>
        <div class="action-steps">
          <strong>建议操作:</strong>
          <ol>
            <li v-for="step in rec.action_steps" :key="step">{{ step }}</li>
          </ol>
        </div>
      </template>
    </el-alert>

    <el-empty v-if="recommendations.length === 0" description="暂无优化建议,系统运行良好" />
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

const recommendations = ref([]);

const fetchRecommendations = async () => {
  const response = await axios.get('/api/gpu/recommendations?device_id=0');
  recommendations.value = response.data;
};

const getSeverityType = (severity: string) => {
  const map: Record<string, any> = {
    'info': 'info',
    'warning': 'warning',
    'critical': 'error'
  };
  return map[severity] || 'info';
};

onMounted(fetchRecommendations);
</script>
```

**验收标准**:
- [ ] 优化建议准确 (规则覆盖5大类)
- [ ] 前端显示清晰易懂
- [ ] 刷新功能正常

**预估时间**: 1天

---

### **阶段3: 实时推送和告警 (Day 7-8)**

#### T5.7 SSE实时推送GPU指标
**目标**: 使用Server-Sent Events推送实时数据

**后端实现**:
```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import json

router = APIRouter(prefix="/api/gpu/stream", tags=["GPU实时推送"])

@router.get("/{device_id}")
async def gpu_metrics_stream(device_id: int):
    """GPU指标实时推送 (SSE)"""

    async def event_generator():
        try:
            while True:
                # 获取最新指标
                gpu_metrics = gpu_monitor.get_metrics(device_id)
                perf_metrics = await perf_collector.collect_performance_metrics()

                # 合并数据
                data = {
                    **gpu_metrics.dict(),
                    **perf_metrics.dict()
                }

                # 推送SSE事件
                yield f"data: {json.dumps(data)}\n\n"

                await asyncio.sleep(2)  # 每2秒推送一次

        except asyncio.CancelledError:
            pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )
```

**前端接收**:
```typescript
// web/frontend/src/composables/useGPUStream.ts
import { ref, onMounted, onUnmounted } from 'vue';

export function useGPUStream(deviceId: number) {
  const metrics = ref<any>({});
  let eventSource: EventSource | null = null;

  const connect = () => {
    eventSource = new EventSource(`/api/gpu/stream/${deviceId}`);

    eventSource.onmessage = (event) => {
      metrics.value = JSON.parse(event.data);
    };

    eventSource.onerror = () => {
      console.error('SSE连接断开,5秒后重连');
      setTimeout(connect, 5000);
    };
  };

  onMounted(connect);
  onUnmounted(() => eventSource?.close());

  return { metrics };
}
```

**验收标准**:
- [ ] SSE连接稳定 (2秒刷新)
- [ ] 断线自动重连
- [ ] 数据实时更新前端

**预估时间**: 1天

---

#### T5.8 GPU异常告警系统
**目标**: 检测异常并发送告警

**告警规则**:
```python
class GPUAlertRule:
    """GPU告警规则"""

    @staticmethod
    def check_alerts(gpu_metrics: GPUMetrics, perf_metrics: PerformanceMetrics) -> List[GPUPerformanceEvent]:
        """检查是否触发告警"""
        events = []

        # 规则1: 高温告警
        if gpu_metrics.temperature > 85:
            events.append(GPUPerformanceEvent(
                device_id=gpu_metrics.device_id,
                timestamp=datetime.now(),
                event_type='high_temp',
                severity='critical',
                message=f"GPU温度过高: {gpu_metrics.temperature:.1f}°C (阈值: 85°C)",
                metadata={"temperature": gpu_metrics.temperature}
            ))

        # 规则2: 显存泄漏
        if gpu_metrics.memory_utilization > 95:
            events.append(GPUPerformanceEvent(
                device_id=gpu_metrics.device_id,
                timestamp=datetime.now(),
                event_type='memory_leak',
                severity='warning',
                message=f"显存使用率过高: {gpu_metrics.memory_utilization:.1f}% (阈值: 95%)",
                metadata={"memory_utilization": gpu_metrics.memory_utilization}
            ))

        # 规则3: 性能下降
        if perf_metrics.overall_speedup < 30:
            events.append(GPUPerformanceEvent(
                device_id=gpu_metrics.device_id,
                timestamp=datetime.now(),
                event_type='performance_drop',
                severity='warning',
                message=f"加速比异常下降: {perf_metrics.overall_speedup:.2f}x (预期: >50x)",
                metadata={"speedup": perf_metrics.overall_speedup}
            ))

        # 规则4: 低利用率 (24小时平均)
        stats_24h = history_service.get_aggregated_stats(gpu_metrics.device_id, 24)
        if stats_24h['avg_utilization'] < 20:
            events.append(GPUPerformanceEvent(
                device_id=gpu_metrics.device_id,
                timestamp=datetime.now(),
                event_type='low_utilization',
                severity='info',
                message=f"GPU利用率过低: 24小时平均{stats_24h['avg_utilization']:.1f}%",
                metadata={"avg_utilization": stats_24h['avg_utilization']}
            ))

        return events

# 后台任务: 定期检查告警
async def alert_checker_loop():
    """告警检查循环 (每30秒)"""
    while True:
        try:
            gpu_metrics = gpu_monitor.get_metrics(0)
            perf_metrics = await perf_collector.collect_performance_metrics()

            events = GPUAlertRule.check_alerts(gpu_metrics, perf_metrics)

            for event in events:
                # 记录到数据库
                history_service.log_event(event)

                # 推送到前端 (通过SSE)
                await sse_manager.broadcast({
                    "type": "gpu_alert",
                    "data": event.dict()
                })

        except Exception as e:
            logger.error(f"告警检查失败: {e}")

        await asyncio.sleep(30)
```

**验收标准**:
- [ ] 4种告警规则正常触发
- [ ] 告警推送到前端
- [ ] 告警记录到数据库

**预估时间**: 1天

---

### **阶段4: 集成测试与文档 (Day 9-10)**

#### T5.9 端到端测试
**目标**: 验证完整监控流程

**测试用例**:
```python
import pytest

def test_gpu_metrics_api():
    """测试GPU指标API"""
    response = client.get("/api/gpu/metrics/0")
    assert response.status_code == 200
    data = response.json()
    assert 'gpu_utilization' in data
    assert 'temperature' in data

def test_performance_metrics_api():
    """测试性能指标API"""
    response = client.get("/api/gpu/performance")
    assert response.status_code == 200
    data = response.json()
    assert 'matrix_gflops' in data
    assert 'overall_speedup' in data

def test_history_data_persistence():
    """测试历史数据持久化"""
    # 保存数据
    gpu_metrics = gpu_monitor.get_metrics(0)
    perf_metrics = await perf_collector.collect_performance_metrics()
    history_service.save_metrics(gpu_metrics, perf_metrics)

    # 查询数据
    data = history_service.query_history(0, datetime.now() - timedelta(hours=1), datetime.now())
    assert len(data) > 0

def test_alert_triggering():
    """测试告警触发"""
    # 模拟高温场景
    mock_metrics = GPUMetrics(
        device_id=0,
        device_name="Test GPU",
        timestamp=datetime.now(),
        temperature=90.0,  # 高于阈值85°C
        gpu_utilization=50.0,
        memory_used=8000,
        memory_total=12000,
        memory_utilization=66.7,
        power_usage=250.0,
        power_limit=300.0,
        sm_clock=1500,
        memory_clock=7000,
        pcie_throughput_tx=10.0,
        pcie_throughput_rx=10.0
    )

    events = GPUAlertRule.check_alerts(mock_metrics, perf_metrics)
    assert len(events) > 0
    assert any(e.event_type == 'high_temp' for e in events)
```

**验收标准**:
- [ ] 所有测试用例通过
- [ ] 测试覆盖率 > 80%

**预估时间**: 1天

---

#### T5.10 文档和交付
**目标**: 完整文档和部署指南

**文档清单**:
1. `GPU_MONITORING_ARCHITECTURE.md` - 架构设计文档
2. `GPU_MONITORING_API_REFERENCE.md` - API参考文档
3. `GPU_MONITORING_DEPLOYMENT_GUIDE.md` - 部署指南
4. `README_CLI5.md` - CLI-5完成报告

**验收标准**:
- [ ] 文档完整无遗漏
- [ ] 部署指南可操作性强

**预估时间**: 1天

---

## 📊 进度跟踪与验收

### 里程碑检查点

| 里程碑 | 时间节点 | 验收标准 |
|--------|---------|---------|
| M1: GPU监控后端完成 | Day 3 | API正常,数据持久化成功 |
| M2: 前端仪表板上线 | Day 6 | 状态卡片+图表正常显示 |
| M3: 实时推送和告警可用 | Day 8 | SSE稳定,告警正常触发 |
| M4: 集成测试通过 | Day 10 | 测试覆盖率>80%,文档完整 |

---

## 🔗 依赖关系

### 上游依赖
- **GPU加速引擎 (Phase 6.4)**: ✅ 已完成 (68.58x性能提升)

### 下游影响
- **CLI-4 (AI筛选)**: 提供GPU性能数据用于优化建议
- **CLI-6 (质量保证)**: 需要GPU监控API的测试用例

---

## 📝 交付清单

### 代码交付
- [ ] `src/gpu_monitoring/` - 后端GPU监控模块
  - `gpu_monitor_service.py` - GPU硬件监控
  - `performance_collector.py` - 性能指标采集
  - `history_service.py` - 历史数据服务
  - `optimization_advisor.py` - 优化建议引擎
- [ ] `web/frontend/src/views/GPUMonitoring/` - 前端页面
  - `GPUStatusCard.vue` - GPU状态卡片
  - `PerformanceChart.vue` - 性能图表
  - `OptimizationPanel.vue` - 优化建议面板
  - `AlertCenter.vue` - 告警中心

---

## 🎯 成功标准

### 功能完整性
- [x] 实时采集GPU硬件指标 (每2秒刷新)
- [x] 性能指标准确 (GFLOPS/加速比/吞吐量)
- [x] 历史数据持久化和查询
- [x] 智能优化建议生成
- [x] 异常告警及时触发

### 性能指标
- [x] 指标采集延迟 < 100ms
- [x] SSE推送延迟 < 2秒
- [x] 历史查询速度 < 500ms (24小时数据)
- [x] 前端图表渲染 < 1秒

### 质量标准
- [x] 测试覆盖率 > 80%
- [x] 代码Review通过
- [x] 文档完整无遗漏

---

## 工作流程与Git提交规范

### 📚 完整工作流程指南

详细的Worker CLI工作流程请参考:
📖 **[CLI工作流程指南](../../mystocks_spec/docs/guides/multi-cli-tasks/CLI_WORKFLOW_GUIDE.md)**

### ⚡ 快速参考

#### 每日工作流程

```bash
# 1. 拉取最新代码
cd /opt/claude/mystocks_phase6_monitoring
git pull

# 2. 查看今日任务
vim README.md

# 3. 开发实现
vim src/gpu_monitoring/gpu_monitor_service.py

# 4. 测试代码
pytest tests/test_gpu_monitoring.py -xvs

# 5. 代码质量检查
ruff check . --fix
black .
pylint src/

# 6. Git提交
git add .
git commit -m "feat(monitoring): add GPU metrics collection service

- Implement GPUMonitoringService with pynvml wrapper
- Add real-time GPU utilization tracking
- Include temperature and power monitoring

Task: T5.1
Acceptance: [x] GPU metrics [x] Temperature [x] Power usage"

# 7. 更新README进度
vim README.md
git add README.md
git commit -m "docs(readme): update progress to T+24h"

# 8. 推送到远程
git push
```

#### Git提交消息规范

```bash
# 格式: <type>(<scope>): <subject>

# 示例:
git commit -m "feat(advisor): implement optimization recommendation engine

- Analyze GPU utilization patterns
- Generate actionable optimization suggestions
- Include cost-benefit analysis

Task: T5.4
Acceptance: [x] Analysis [x] Recommendations [x] Cost estimation"
```

#### 完成标准检查清单

- [ ] 所有验收标准通过
- [ ] 代码已提交到Git（频繁提交）
- [ ] 测试覆盖率>80%
- [ ] 代码质量检查通过（Pylint>8.0）
- [ ] README已更新（进度+任务状态）

#### 进度更新格式

```markdown
## 进度更新

### T+0h (2025-12-29 15:00)
- ✅ 任务启动
- 📝 当前任务: T5.1 GPU监控服务实现
- ⏳ 预计完成: 2025-12-30

### T+24h (2025-12-30 15:00)
- ✅ T5.1 GPU监控服务完成
  - Git提交: abc1234
  - 验收标准: [x] 全部通过
- 📝 当前任务: T5.2 性能数据收集器
- 🚧 阻塞问题: 无
```

### 🎯 关键注意事项

1. **GPU资源监控**: 利用现有68.58x GPU加速基础设施
2. **频繁提交**: 每完成一个服务模块就提交
3. **性能优化**: 确保监控开销<5% GPU资源
4. **及时更新README**: 每天至少更新一次进度

### 📞 需要帮助？

- 📖 [完整工作流程](../../mystocks_spec/docs/guides/multi-cli-tasks/CLI_WORKFLOW_GUIDE.md)
- 📚 [GPU开发经验](../../mystocks_spec/docs/api/GPU开发经验总结.md)
- 🚧 遇到阻塞: 在README中记录

---

**最后更新**: 2025-12-29
**责任人**: CLI-5 Worker (Phase 6 GPU Monitoring)
**预计完成**: 2025-01-08 (8-10工作日)
