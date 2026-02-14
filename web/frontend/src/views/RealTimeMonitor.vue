<template>
    <div class="page-header">
      <div class="page-title">实时监控中心</div>
      <div class="page-subtitle">REALTIME MONITORING CENTER</div>
      <div class="page-decorative-line"></div>
      <p class="subtitle">基于SSE (Server-Sent Events) 的实时推送系统</p>
    </div>

    <div class="info-banner">
      <div class="banner-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="16" x2="12" y2="12"></line>
          <line x1="12" y1="8" x2="12.01" y2="8"></line>
        </svg>
      </div>
      <div class="banner-content">
        <div class="banner-title">实时推送功能说明</div>
        <p>本页面展示了基于SSE (Server-Sent Events) 协议的实时数据推送功能。所有数据通过长连接实时更新，无需手动刷新页面。</p>
        <div class="feature-tags">
          <span class="tag">模型训练进度</span>
          <span class="tag">回测执行进度</span>
          <span class="tag">风险告警通知</span>
          <span class="tag">实时指标更新</span>
        </div>
      </div>
    </div>

    <el-row :gutter="20" class="metrics-section">
      <el-col :xs="24" :lg="16">
        <div class="card-wrapper">
          <DashboardMetrics />
        </div>
      </el-col>
      <el-col :xs="24" :lg="8">
        <div class="card-wrapper">
          <RiskAlerts :max-alerts="50" :show-notification="true" />
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="progress-section">
      <el-col :xs="24" :lg="12">
        <div class="card-wrapper">
          <TrainingProgress />
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="card-wrapper">
          <BacktestProgress />
        </div>
      </el-col>
    </el-row>

    <div class="card sse-status-card">
      <div class="card-header">
        <div class="header-title">
          <div class="title-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
              <line x1="8" y1="21" x2="16" y2="21"></line>
              <line x1="12" y1="17" x2="12" y2="21"></line>
            </svg>
          </div>
          <span class="title-text">SSE 连接状态</span>
          <span class="title-sub">SSE CONNECTION STATUS</span>
        </div>
        <button class="button" @click="refreshSSEStatus">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6"></path>
            <path d="M1 20v-6h6"></path>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
          </svg>
          刷新状态
        </button>
      </div>
      <div class="card-body">
        <div v-if="sseStatus" class="sse-status-content">
          <div class="status-grid">
            <div class="status-item">
              <span class="status-label">服务状态</span>
              <span :class="['status-value', sseStatus.status === 'active' ? 'status-active' : 'status-inactive']">
                {{ sseStatus.status === 'active' ? '活跃' : '不可用' }}
              </span>
            </div>
            <div class="status-item">
              <span class="status-label">总连接数</span>
              <span class="status-value highlight">{{ sseStatus.total_connections || 0 }}</span>
            </div>
            <div v-if="sseStatus.channels?.training" class="status-item">
              <span class="status-label">训练通道</span>
              <span class="status-value">{{ sseStatus.channels.training.connection_count || 0 }} 个连接</span>
            </div>
            <div v-if="sseStatus.channels?.backtest" class="status-item">
              <span class="status-label">回测通道</span>
              <span class="status-value">{{ sseStatus.channels.backtest.connection_count || 0 }} 个连接</span>
            </div>
            <div v-if="sseStatus.channels?.alerts" class="status-item">
              <span class="status-label">告警通道</span>
              <span class="status-value">{{ sseStatus.channels.alerts.connection_count || 0 }} 个连接</span>
            </div>
            <div v-if="sseStatus.channels?.dashboard" class="status-item">
              <span class="status-label">仪表板通道</span>
              <span class="status-value">{{ sseStatus.channels.dashboard.connection_count || 0 }} 个连接</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <svg class="loading-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M12 2a10 10 0 0 1 10 10"></path>
          </svg>
          <p>加载SSE状态中...</p>
        </div>
      </div>
    </div>

    <div class="card test-tools-card">
      <div class="card-header">
        <div class="header-title">
          <div class="title-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
            </svg>
          </div>
          <span class="title-text">SSE 测试工具</span>
          <span class="title-sub">SSE TESTING TOOLS</span>
        </div>
      </div>
      <div class="card-body">
        <div class="test-notice">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
          <p>以下按钮用于测试SSE功能。点击后，后端会通过SSE推送相应的事件数据。<strong>注意：需要后端API支持才能正常工作。</strong></p>
        </div>
        <div class="test-buttons">
          <button class="button button-primary" :class="{ loading: testingTraining }" @click="testTrainingProgress">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
              <polyline points="17 6 23 6 23 12"></polyline>
            </svg>
            测试训练进度
          </button>
          <button class="button button-success" :class="{ loading: testingBacktest }" @click="testBacktestProgress">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="20" x2="18" y2="10"></line>
              <line x1="12" y1="20" x2="12" y2="4"></line>
              <line x1="6" y1="20" x2="6" y2="14"></line>
            </svg>
            测试回测进度
          </button>
          <button class="button button-danger" :class="{ loading: testingAlert }" @click="testRiskAlert">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
            </svg>
            测试风险告警
          </button>
          <button class="button button-info" :class="{ loading: testingDashboard }" @click="testDashboardUpdate">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            测试指标更新
          </button>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
// @ts-nocheck

import { ref, onMounted, type Ref } from 'vue'
import { ElMessage } from 'element-plus'
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
  } catch (error: unknown) {
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
    ElMessage.info('训练进度测试功能需要后端API支持')
  } catch (error: unknown) {
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
  } catch (error: unknown) {
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
  } catch (error: unknown) {
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
  } catch (error: unknown) {
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
@import "./styles/RealTimeMonitor.scss";
</style>
