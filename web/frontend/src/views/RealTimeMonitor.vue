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
    ElMessage.info('训练进度测试功能需要后端API支持')
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
  padding: 24px;
  background: var(--bg-primary);
  background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(212, 175, 55, 0.02) 10px, rgba(212, 175, 55, 0.02) 11px);
  min-height: 100vh;

  .page-header {
    text-align: center;
    margin-bottom: 32px;
    padding: 32px 0;
    border-bottom: 1px solid var(--gold-dim);
    position: relative;

    .page-title {
      font-family: var(--font-display);
      font-size: 36px;
      font-weight: 700;
      color: var(--gold-primary);
      text-transform: uppercase;
      letter-spacing: 4px;
      margin-bottom: 4px;
    }

    .page-subtitle {
      font-family: var(--font-body);
      font-size: 11px;
      color: var(--gold-muted);
      letter-spacing: 6px;
      text-transform: uppercase;
    }

    .page-decorative-line {
      width: 200px;
      height: 2px;
      background: linear-gradient(90deg, transparent, var(--gold-primary), transparent);
      margin: 16px auto;
    }

    .subtitle {
      font-family: var(--font-body);
      font-size: 14px;
      color: var(--text-muted);
      margin: 8px 0 0 0;
    }
  }

  .info-banner {
    background: var(--bg-card);
    border: 1px solid var(--gold-dim);
    padding: 20px;
    margin-bottom: 24px;
    display: flex;
    gap: 16px;
    position: relative;

    &::before,
    &::after {
      content: '';
      position: absolute;
      width: 12px;
      height: 12px;
      border: 2px solid var(--gold-primary);
    }

    &::before {
      top: 8px;
      left: 8px;
      border-right: none;
      border-bottom: none;
    }

    &::after {
      bottom: 8px;
      right: 8px;
      border-left: none;
      border-top: none;
    }

    .banner-icon {
      flex-shrink: 0;
      width: 48px;
      height: 48px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--gold-primary);
    }

    .banner-content {
      flex: 1;

      .banner-title {
        font-family: var(--font-body);
        font-size: 16px;
        font-weight: 600;
        color: var(--gold-primary);
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 2px;
      }

      p {
        font-family: var(--font-body);
        font-size: 14px;
        color: var(--text-secondary);
        line-height: 1.6;
        margin: 0 0 12px 0;

        strong {
          color: var(--gold-primary);
        }
      }

      .feature-tags {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;

        .tag {
          font-family: var(--font-body);
          font-size: 12px;
          padding: 4px 12px;
          background: rgba(212, 175, 55, 0.1);
          border: 1px solid var(--gold-dim);
          color: var(--gold-primary);
          text-transform: uppercase;
          letter-spacing: 1px;
        }
      }
    }
  }

  .metrics-section {
    margin-bottom: 24px;
  }

  .progress-section {
    margin-bottom: 24px;
  }

  .card-wrapper {
    margin-bottom: 20px;

    :deep(.el-card) {
      background: var(--bg-card);
      border: 1px solid var(--gold-dim);
      box-shadow: none;

      .el-card__header {
        background: rgba(212, 175, 55, 0.05);
        border-bottom: 1px solid var(--gold-dim);
        font-family: var(--font-body);
      }

      .el-card__body {
        background: var(--bg-card);
      }
    }
  }

  .card {
    background: var(--bg-card);
    border: 1px solid var(--gold-dim);
    margin-bottom: 24px;
    position: relative;

    &::before,
    &::after {
      content: '';
      position: absolute;
      width: 16px;
      height: 16px;
      border: 2px solid var(--gold-primary);
      z-index: 1;
    }

    &::before {
      top: 12px;
      left: 12px;
      border-right: none;
      border-bottom: none;
    }

    &::after {
      bottom: 12px;
      right: 12px;
      border-left: none;
      border-top: none;
    }

    .card-header {
      padding: 16px 24px;
      border-bottom: 1px solid var(--gold-dim);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;

      .header-title {
        display: flex;
        align-items: center;
        gap: 12px;

        .title-icon {
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--gold-primary);
          flex-shrink: 0;
        }

        .title-text {
          font-family: var(--font-body);
          font-size: 16px;
          font-weight: 600;
          color: var(--gold-primary);
          text-transform: uppercase;
          letter-spacing: 2px;
        }

        .title-sub {
          font-family: var(--font-body);
          font-size: 10px;
          color: var(--gold-muted);
          text-transform: uppercase;
          letter-spacing: 3px;
          display: block;
          margin-top: 2px;
        }
      }
    }

    .card-body {
      padding: 24px;
    }
  }

  .sse-status-card {
    .sse-status-content {
      .status-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;

        .status-item {
          background: rgba(212, 175, 55, 0.05);
          border: 1px solid var(--gold-dim);
          padding: 16px;
          position: relative;

          &::before {
            content: '';
            position: absolute;
            top: 8px;
            left: 8px;
            width: 6px;
            height: 6px;
            background: var(--gold-primary);
          }

          .status-label {
            font-family: var(--font-body);
            font-size: 11px;
            color: var(--gold-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            display: block;
            margin-bottom: 8px;
          }

          .status-value {
            font-family: var(--font-mono);
            font-size: 20px;
            font-weight: 700;
            color: var(--text-primary);
            display: block;

            &.highlight {
              color: var(--gold-primary);
            }

            &.status-active {
              color: var(--rise);
            }

            &.status-inactive {
              color: var(--fall);
            }
          }
        }
      }
    }

    .empty-state {
      text-align: center;
      padding: 40px 20px;

      .loading-icon {
        width: 60px;
        height: 60px;
        margin: 0 auto 16px;
        color: var(--gold-primary);
        animation: spin 2s linear infinite;
      }

      p {
        font-family: var(--font-body);
        font-size: 14px;
        color: var(--text-secondary);
        margin: 0;
      }
    }
  }
}

  .test-tools-card {
    .test-notice {
      display: flex;
      gap: 12px;
      background: rgba(212, 175, 55, 0.05);
      border: 1px solid var(--gold-dim);
      padding: 16px;
      margin-bottom: 20px;

      svg {
        flex-shrink: 0;
        width: 24px;
        height: 24px;
        color: var(--gold-primary);
      }

      p {
        font-family: var(--font-body);
        font-size: 14px;
        color: var(--text-secondary);
        line-height: 1.6;
        margin: 0;

        strong {
          color: var(--gold-primary);
        }
      }
    }

    .test-buttons {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
    }

    .button {
      padding: 12px 24px;
      font-family: var(--font-body);
      font-size: 14px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 2px;
      border: 2px solid var(--gold-primary);
      background: transparent;
      color: var(--gold-primary);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: all 0.3s ease;
      position: relative;

      svg {
        width: 18px;
        height: 18px;
      }

      &:hover:not(.loading) {
        background: var(--gold-primary);
        color: var(--bg-primary);
      }

      &.loading {
        opacity: 0.6;
        cursor: not-allowed;
      }

      &::before {
        content: '';
        position: absolute;
        top: 4px;
        left: 4px;
        width: 8px;
        height: 8px;
        border-left: 1px solid var(--gold-primary);
        border-top: 1px solid var(--gold-primary);
      }

      &.button-primary {
        border-color: var(--rise);
        color: var(--rise);

        &::before {
          border-color: var(--rise);
        }

        &:hover:not(.loading) {
          background: var(--rise);
          color: var(--bg-primary);
        }
      }

      &.button-success {
        border-color: var(--fall);
        color: var(--fall);

        &::before {
          border-color: var(--fall);
        }

        &:hover:not(.loading) {
          background: var(--fall);
          color: var(--bg-primary);
        }
      }

      &.button-danger {
        border-color: #f56c6c;
        color: #f56c6c;

        &::before {
          border-color: #f56c6c;
        }

        &:hover:not(.loading) {
          background: #f56c6c;
          color: var(--bg-primary);
        }
      }

      &.button-info {
        border-color: var(--gold-primary);
        color: var(--gold-primary);

        &::before {
          border-color: var(--gold-primary);
        }

        &:hover:not(.loading) {
          background: var(--gold-primary);
          color: var(--bg-primary);
        }
      }
    }
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  @media (max-width: 768px) {
  .realtime-monitor {
    padding: 16px;

    .page-header {
      padding: 24px 0;
      margin-bottom: 24px;

      .page-title {
        font-size: 24px;
        letter-spacing: 2px;
      }

      .page-subtitle {
        font-size: 9px;
        letter-spacing: 3px;
      }
    }

    .info-banner {
      flex-direction: column;
      text-align: center;

      .banner-icon {
        margin: 0 auto;
      }

      .feature-tags {
        justify-content: center;
      }
    }

    .card {
      .card-header {
        flex-direction: column;
        text-align: center;
      }

      .card-body {
        padding: 16px;
      }
    }

    .test-tools-card {
      .test-notice {
        flex-direction: column;
        text-align: center;

        svg {
          margin: 0 auto;
        }
      }

      .test-buttons {
        grid-template-columns: 1fr;
      }
    }
  }
}
</style>
