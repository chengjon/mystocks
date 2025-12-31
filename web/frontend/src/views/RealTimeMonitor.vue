<template>
  <div class="realtime-monitor">
    <div class="page-header">
      <h1>📡 实时监控中心</h1>
      <p class="subtitle">基于SSE (Server-Sent Events) 的实时推送系统 - Week 2 Day 3</p>
    </div>

    <!-- 功能说明 -->
    <el-alert
      title="实时推送功能说明"
      type="info"
      :closable="false"
      show-icon
      class="info-banner"
    >
      <template #default>
        <p>
          本页面展示了基于SSE (Server-Sent Events) 协议的实时数据推送功能。
          所有数据通过长连接实时更新，无需手动刷新页面。
        </p>
        <el-space wrap>
          <el-tag>模型训练进度</el-tag>
          <el-tag>回测执行进度</el-tag>
          <el-tag>风险告警通知</el-tag>
          <el-tag>实时指标更新</el-tag>
        </el-space>
      </template>
    </el-alert>

    <!-- 实时指标和风险告警 -->
    <el-row :gutter="20">
      <el-col :xs="24" :lg="16">
        <DashboardMetrics />
      </el-col>
      <el-col :xs="24" :lg="8">
        <RiskAlerts :max-alerts="50" :show-notification="true" />
      </el-col>
    </el-row>

    <!-- 训练进度和回测进度 -->
    <el-row :gutter="20">
      <el-col :xs="24" :lg="12">
        <TrainingProgress />
      </el-col>
      <el-col :xs="24" :lg="12">
        <BacktestProgress />
      </el-col>
    </el-row>

    <!-- SSE 状态监控 -->
    <el-card class="sse-status-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Monitor /></el-icon>
            SSE 连接状态
          </span>
          <el-button size="small" @click="refreshSSEStatus">
            <el-icon><Refresh /></el-icon>
            刷新状态
          </el-button>
        </div>
      </template>

      <el-descriptions v-if="sseStatus" :column="2" border>
        <el-descriptions-item label="服务状态">
          <el-tag :type="sseStatus.status === 'active' ? 'success' : 'danger'">
            {{ sseStatus.status === 'active' ? '活跃' : '不可用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="总连接数">
          <el-text type="primary" size="large">
            <strong>{{ sseStatus.total_connections || 0 }}</strong>
          </el-text>
        </el-descriptions-item>

        <el-descriptions-item label="训练通道" v-if="sseStatus.channels?.training">
          {{ sseStatus.channels.training.connection_count || 0 }} 个连接
        </el-descriptions-item>
        <el-descriptions-item label="回测通道" v-if="sseStatus.channels?.backtest">
          {{ sseStatus.channels.backtest.connection_count || 0 }} 个连接
        </el-descriptions-item>
        <el-descriptions-item label="告警通道" v-if="sseStatus.channels?.alerts">
          {{ sseStatus.channels.alerts.connection_count || 0 }} 个连接
        </el-descriptions-item>
        <el-descriptions-item label="仪表板通道" v-if="sseStatus.channels?.dashboard">
          {{ sseStatus.channels.dashboard.connection_count || 0 }} 个连接
        </el-descriptions-item>
      </el-descriptions>

      <el-empty v-else description="加载SSE状态中..." />
    </el-card>

    <!-- API测试工具 -->
    <el-card class="test-tools-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Tools /></el-icon>
            SSE 测试工具
          </span>
        </div>
      </template>

      <el-space direction="vertical" :fill="true" style="width: 100%">
        <el-alert
          title="测试说明"
          type="warning"
          :closable="false"
          show-icon
        >
          <p>
            以下按钮用于测试SSE功能。点击后，后端会通过SSE推送相应的事件数据。
            <strong>注意：需要后端API支持才能正常工作。</strong>
          </p>
        </el-alert>

        <el-row :gutter="16">
          <el-col :xs="24" :sm="12" :md="6">
            <el-button
              type="primary"
              :icon="TrendCharts"
              :loading="testingTraining"
              @click="testTrainingProgress"
              style="width: 100%"
            >
              测试训练进度
            </el-button>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-button
              type="success"
              :icon="Histogram"
              :loading="testingBacktest"
              @click="testBacktestProgress"
              style="width: 100%"
            >
              测试回测进度
            </el-button>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-button
              type="danger"
              :icon="Bell"
              :loading="testingAlert"
              @click="testRiskAlert"
              style="width: 100%"
            >
              测试风险告警
            </el-button>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-button
              type="info"
              :icon="Odometer"
              :loading="testingDashboard"
              @click="testDashboardUpdate"
              style="width: 100%"
            >
              测试指标更新
            </el-button>
          </el-col>
        </el-row>
      </el-space>
    </el-card>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck

import { ref, onMounted, type Ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Monitor, Refresh, Tools, TrendCharts,
  Histogram, Bell, Odometer
} from '@element-plus/icons-vue'
import axios from 'axios'

// Import SSE components
import TrainingProgress from '@/components/sse/TrainingProgress.vue'
import BacktestProgress from '@/components/sse/BacktestProgress.vue'
import RiskAlerts from '@/components/sse/RiskAlerts.vue'
import DashboardMetrics from '@/components/sse/DashboardMetrics.vue'

// ============================================
// 类型定义
// ============================================

/**
 * SSE通道连接数
 */
interface ChannelConnectionCount {
  connection_count: number
}

/**
 * SSE通道状态
 */
interface SSEChannels {
  training?: ChannelConnectionCount
  backtest?: ChannelConnectionCount
  alerts?: ChannelConnectionCount
  dashboard?: ChannelConnectionCount
}

/**
 * SSE状态响应
 */
interface SSEStatus {
  status: 'active' | 'inactive'
  total_connections: number
  channels?: SSEChannels
}

// ============================================
// 状态管理
// ============================================

const sseStatus: Ref<SSEStatus | null> = ref(null)
const testingTraining: Ref<boolean> = ref(false)
const testingBacktest: Ref<boolean> = ref(false)
const testingAlert: Ref<boolean> = ref(false)
const testingDashboard: Ref<boolean> = ref(false)

// Get API base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// ============================================
// 方法定义
// ============================================

/**
 * Fetch SSE status from backend
 */
const refreshSSEStatus = async (): Promise<void> => {
  try {
    const response = await axios.get<SSEStatus>(`${API_BASE_URL}/api/v1/sse/status`)
    sseStatus.value = response.data
    ElMessage.success('SSE状态已更新')
  } catch (error: any) {
    console.error('Failed to fetch SSE status:', error)
    ElMessage.error('获取SSE状态失败')
  }
}

/**
 * Test training progress SSE
 */
const testTrainingProgress = async (): Promise<void> => {
  testingTraining.value = true
  try {
    // This would call a backend API that triggers training progress events
    ElMessage.info('训练进度测试功能需要后端API支持')
    // await axios.post(`${API_BASE_URL}/api/test/training-progress`)
  } catch (error: any) {
    console.error('Test training progress failed:', error)
    ElMessage.error('测试训练进度失败')
  } finally {
    testingTraining.value = false
  }
}

/**
 * Test backtest progress SSE
 */
const testBacktestProgress = async (): Promise<void> => {
  testingBacktest.value = true
  try {
    ElMessage.info('回测进度测试功能需要后端API支持')
    // await axios.post(`${API_BASE_URL}/api/test/backtest-progress`)
  } catch (error: any) {
    console.error('Test backtest progress failed:', error)
    ElMessage.error('测试回测进度失败')
  } finally {
    testingBacktest.value = false
  }
}

/**
 * Test risk alert SSE
 */
const testRiskAlert = async (): Promise<void> => {
  testingAlert.value = true
  try {
    ElMessage.info('风险告警测试功能需要后端API支持')
    // await axios.post(`${API_BASE_URL}/api/test/risk-alert`)
  } catch (error: any) {
    console.error('Test risk alert failed:', error)
    ElMessage.error('测试风险告警失败')
  } finally {
    testingAlert.value = false
  }
}

/**
 * Test dashboard update SSE
 */
const testDashboardUpdate = async (): Promise<void> => {
  testingDashboard.value = true
  try {
    ElMessage.info('指标更新测试功能需要后端API支持')
    // await axios.post(`${API_BASE_URL}/api/test/dashboard-update`)
  } catch (error: any) {
    console.error('Test dashboard update failed:', error)
    ElMessage.error('测试指标更新失败')
  } finally {
    testingDashboard.value = false
  }
}

// ============================================
// 生命周期
// ============================================

/**
 * Load SSE status on mount
 */
onMounted((): void => {
  refreshSSEStatus()
})
</script>

<style scoped lang="scss">
.realtime-monitor {
  padding: 20px;

  .page-header {
    margin-bottom: 20px;

    h1 {
      font-size: 28px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 8px 0;
    }

    .subtitle {
      font-size: 14px;
      color: #909399;
      margin: 0;
    }
  }

  .info-banner {
    margin-bottom: 20px;

    p {
      margin: 0 0 12px 0;
      line-height: 1.6;
    }
  }

  .sse-status-card {
    margin-bottom: 20px;

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;

      .title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        font-weight: 600;
        color: #303133;

        .el-icon {
          font-size: 18px;
        }
      }
    }
  }

  .test-tools-card {
    margin-bottom: 20px;

    .card-header {
      .title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        font-weight: 600;
        color: #303133;

        .el-icon {
          font-size: 18px;
        }
      }
    }

    .el-alert {
      p {
        margin: 0;
        line-height: 1.6;
      }
    }

    .el-button {
      margin-bottom: 8px;

      @media (min-width: 768px) {
        margin-bottom: 0;
      }
    }
  }
}
</style>
