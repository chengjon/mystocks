<template>
  <div class="gpu-monitoring-page">
    <el-page-header @back="goBack" title="GPU监控仪表板" class="page-header">
      <template #content>
        <div class="page-header-content">
          <span class="page-title">GPU监控仪表板</span>
          <el-button type="primary" size="small" @click="refreshAll" :loading="loading">
            刷新全部
          </el-button>
        </div>
      </template>
    </el-page-header>

    <el-row :gutter="16">
      <el-col :span="24">
        <GPUStatusCard :device-id="0" />
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px;">
      <el-col :span="16">
        <PerformanceChart />
      </el-col>
      <el-col :span="8">
        <OptimizationPanel />
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px;">
      <el-col :span="24">
        <PerformanceStatsCard />
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import GPUStatusCard from '@/components/GPUMonitoring/GPUStatusCard.vue';
import PerformanceChart from '@/components/GPUMonitoring/PerformanceChart.vue';
import OptimizationPanel from '@/components/GPUMonitoring/OptimizationPanel.vue';
import PerformanceStatsCard from '@/components/GPUMonitoring/PerformanceStatsCard.vue';

const router = useRouter();
const loading = ref(false);

const goBack = () => {
  router.back();
};

const refreshAll = async () => {
  loading.value = true;
  window.location.reload();
};
</script>

<style scoped>
.gpu-monitoring-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
}
</style>
