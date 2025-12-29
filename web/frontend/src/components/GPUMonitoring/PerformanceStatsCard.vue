<template>
  <el-card>
    <template #header>
      <div class="header">
        <span>性能统计汇总</span>
        <el-radio-group v-model="timeRange" size="small" @change="fetchStats">
          <el-radio-button label="1h">1小时</el-radio-button>
          <el-radio-button label="6h">6小时</el-radio-button>
          <el-radio-button label="24h">24小时</el-radio-button>
        </el-radio-group>
      </div>
    </template>

    <el-row :gutter="16">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-label">平均GPU利用率</div>
          <div class="stat-value">{{ stats.avg_utilization.toFixed(1) }}%</div>
          <div class="stat-sub">峰值: {{ stats.max_utilization.toFixed(1) }}%</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-label">平均GFLOPS</div>
          <div class="stat-value">{{ stats.avg_gflops.toFixed(2) }}</div>
          <div class="stat-sub">峰值: {{ stats.peak_gflops.toFixed(2) }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-label">平均温度</div>
          <div class="stat-value">{{ stats.avg_temperature.toFixed(1) }}°C</div>
          <div class="stat-sub">最高: {{ stats.max_temperature.toFixed(1) }}°C</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-label">平均加速比</div>
          <div class="stat-value">{{ stats.avg_speedup.toFixed(2) }}x</div>
          <div class="stat-sub">峰值: {{ stats.peak_speedup.toFixed(2) }}x</div>
        </div>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

interface PerformanceStats {
  avg_utilization: number;
  max_utilization: number;
  avg_temperature: number;
  max_temperature: number;
  avg_gflops: number;
  peak_gflops: number;
  avg_speedup: number;
  peak_speedup: number;
}

const timeRange = ref('24h');
const stats = ref<PerformanceStats>({
  avg_utilization: 0,
  max_utilization: 0,
  avg_temperature: 0,
  max_temperature: 0,
  avg_gflops: 0,
  peak_gflops: 0,
  avg_speedup: 0,
  peak_speedup: 0
});

const fetchStats = async () => {
  try {
    const hours = parseInt(timeRange.value);
    const response = await axios.get(`/api/gpu/stats/0?hours=${hours}`);
    stats.value = response.data;
  } catch (error) {
    console.error('获取性能统计失败:', error);
  }
};

onMounted(fetchStats);
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  padding: 20px;
  color: white;
  text-align: center;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 4px;
}

.stat-sub {
  font-size: 12px;
  opacity: 0.8;
}
</style>
