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

      <div class="metric-item">
        <div class="metric-label">功耗</div>
        <div class="metric-value">
          {{ metrics.power_usage.toFixed(1) }} W / {{ metrics.power_limit.toFixed(0) }} W
        </div>
        <el-progress
          :percentage="metrics.power_limit > 0 ? (metrics.power_usage / metrics.power_limit) * 100 : 0"
          :show-text="false"
        />
      </div>

      <div class="metric-item">
        <div class="metric-label">SM频率</div>
        <div class="metric-value">{{ metrics.sm_clock }} MHz</div>
      </div>

      <div class="metric-item">
        <div class="metric-label">显存频率</div>
        <div class="metric-value">{{ metrics.memory_clock }} MHz</div>
      </div>

      <div class="metric-item">
        <div class="metric-label">PCIe吞吐量</div>
        <div class="metric-value">
          ↑ {{ metrics.pcie_throughput_tx.toFixed(2) }} MB/s<br>
          ↓ {{ metrics.pcie_throughput_rx.toFixed(2) }} MB/s
        </div>
      </div>
    </div>

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

interface GPUMetrics {
  device_id: number;
  device_name: string;
  timestamp: string;
  gpu_utilization: number;
  memory_used: number;
  memory_total: number;
  memory_utilization: number;
  temperature: number;
  power_usage: number;
  power_limit: number;
  sm_clock: number;
  memory_clock: number;
  pcie_throughput_tx: number;
  pcie_throughput_rx: number;
}

interface ProcessInfo {
  pid: number;
  process_name: string;
  memory_used_mb: number;
  cmdline: string;
}

const props = defineProps<{
  deviceId: number;
}>();

const deviceName = ref('');
const status = ref('正常');
const metrics = ref<GPUMetrics>({
  device_id: props.deviceId,
  device_name: '',
  timestamp: '',
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
const processes = ref<ProcessInfo[]>([]);

let updateInterval: number;

const fetchMetrics = async () => {
  try {
    const [metricsResp, processesResp] = await Promise.all([
      axios.get<GPUMetrics>(`/api/gpu/metrics/${props.deviceId}`),
      axios.get<ProcessInfo[]>(`/api/gpu/processes/${props.deviceId}`)
    ]);

    deviceName.value = metricsResp.data.device_name;
    metrics.value = metricsResp.data;
    processes.value = processesResp.data;

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
  if (value < 30) return '#909399';
  if (value < 70) return '#67C23A';
  if (value < 90) return '#E6A23C';
  return '#F56C6C';
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
  updateInterval = window.setInterval(fetchMetrics, 2000);
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
