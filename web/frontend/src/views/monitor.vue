<template>
    <!-- 页面头部 -->
    <PageHeader
      title="系统监控"
      subtitle="SYSTEM MONITORING"
    >
      <template #actions>
        <div v-if="isLoading" class="loading-indicator">
          <svg class="loading-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M12 2a10 10 0 0 1 10 10"></path>
          </svg>
          <span>加载中...</span>
        </div>
        <button class="button" @click="refreshData" :disabled="isLoading" :class="{ loading: isLoading }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6"></path>
            <path d="M1 20v-6h6"></path>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
          </svg>
          刷新
        </button>
        <button class="button" :class="{ active: autoRefresh, 'button-primary': autoRefresh }" @click="toggleAutoRefresh">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="6" y="4" width="4" height="16"></rect>
            <rect x="14" y="4" width="4" height="16"></rect>
          </svg>
          {{ autoRefresh ? '暂停自动刷新' : '启动自动刷新' }}
        </button>
      </template>
    </PageHeader>

    <div v-if="error" class="error-message">
      <svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
      {{ error }}
    </div>

    <div class="monitor-summary">
      <div :class="['card summary-card', isSystemHealthy ? 'status-normal' : 'status-warning']">
        <div class="card-body">
          <div class="summary-content">
            <div class="summary-icon">
              <svg v-if="isSystemHealthy" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
            </div>
            <div class="summary-info">
              <div class="summary-title">{{ isSystemHealthy ? '系统运行正常' : '系统存在警告' }}</div>
              <div class="summary-description">{{ systemStatusMessage }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="summary-details">
        <div class="card detail-card">
          <div class="card-body">
            <div class="detail-content">
              <div class="detail-label">前端服务</div>
              <div :class="['detail-value', services.frontend === 'normal' ? 'status-normal' : 'status-warning']">
                {{ getServiceStatusText(services.frontend) }}
              </div>
            </div>
          </div>
        </div>
        <div class="card detail-card">
          <div class="card-body">
            <div class="detail-content">
              <div class="detail-label">API服务</div>
              <div :class="['detail-value', services.api === 'normal' ? 'status-normal' : 'status-warning']">
                {{ getServiceStatusText(services.api) }}
              </div>
            </div>
          </div>
        </div>
        <div class="card detail-card">
          <div class="card-body">
            <div class="detail-content">
              <div class="detail-label">PostgreSQL</div>
              <div :class="['detail-value', services.postgresql === 'normal' ? 'status-normal' : 'status-warning']">
                {{ getServiceStatusText(services.postgresql) }}
              </div>
            </div>
          </div>
        </div>
        <div class="card detail-card">
          <div class="card-body">
            <div class="detail-content">
              <div class="detail-label">TDengine</div>
              <div :class="['detail-value', services.tdengine === 'normal' ? 'status-normal' : 'status-warning']">
                {{ getServiceStatusText(services.tdengine) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="services-section">
      <div class="section-title">
        <span>服务详情</span>
        <span class="subtitle">SERVICE DETAILS</span>
      </div>
      <div class="services-grid">
        <div class="card service-card">
          <div class="card-header">
            <div class="header-title">
              <span class="title-text">前端服务</span>
              <span :class="['service-status', services.frontend === 'normal' ? 'status-normal' : 'status-warning']">
                {{ getServiceStatusText(services.frontend) }}
              </span>
            </div>
          </div>
          <div class="card-body">
            <div class="service-content">
              <div class="service-info">
                <div class="info-item">
                  <span class="info-label">状态:</span>
                  <span class="info-value">{{ services.frontend === 'normal' ? '正常' : '异常' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">URL:</span>
                  <span class="info-value mono">{{ FRONTEND_URL }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">响应时间:</span>
                  <span class="info-value mono">{{ servicesData.frontend?.responseTime || '未知' }} ms</span>
                </div>
              </div>
              <div class="service-actions">
                <button @click="checkService('frontend')" class="button button-sm">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                  </svg>
                  检查
                </button>
                <a :href="FRONTEND_URL" target="_blank" class="button button-sm">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                    <polyline points="15 3 21 3 21 9"></polyline>
                    <line x1="10" y1="14" x2="21" y2="3"></line>
                  </svg>
                  访问
                </a>
              </div>
            </div>
          </div>
        </div>

        <div class="card service-card">
          <div class="card-header">
            <div class="header-title">
              <span class="title-text">API服务</span>
              <span :class="['service-status', services.api === 'normal' ? 'status-normal' : 'status-warning']">
                {{ getServiceStatusText(services.api) }}
              </span>
            </div>
          </div>
          <div class="card-body">
            <div class="service-content">
              <div class="service-info">
                <div class="info-item">
                  <span class="info-label">状态:</span>
                  <span class="info-value">{{ services.api === 'normal' ? '正常' : '异常' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">URL:</span>
                  <span class="info-value mono">{{ API_BASE_URL }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">健康检查端点:</span>
                  <span class="info-value mono">/api/health</span>
                </div>
              </div>
              <div class="service-actions">
                <button @click="checkService('api')" class="button button-sm">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                  </svg>
                  检查
                </button>
                <a :href="`${API_BASE_URL}/api/docs`" target="_blank" class="button button-sm">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                  </svg>
                  API文档
                </a>
              </div>
            </div>
          </div>
        </div>

        <div class="card service-card">
          <div class="card-header">
            <div class="header-title">
              <span class="title-text">PostgreSQL</span>
              <span :class="['service-status', services.postgresql === 'normal' ? 'status-normal' : 'status-warning']">
                {{ getServiceStatusText(services.postgresql) }}
              </span>
            </div>
          </div>
          <div class="card-body">
            <div class="service-content">
              <div class="service-info">
                <div class="info-item">
                  <span class="info-label">状态:</span>
                  <span class="info-value">{{ servicesData.postgresql?.status || '未知' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">主机:</span>
                  <span class="info-value mono">localhost:5438</span>
                </div>
                <div class="info-item">
                  <span class="info-label">数据库:</span>
                  <span class="info-value mono">mystocks</span>
                </div>
              </div>
              <div class="service-actions">
                <button @click="checkService('postgresql')" class="button button-sm">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                  </svg>
                  检查
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="card service-card">
          <div class="card-header">
            <div class="header-title">
              <span class="title-text">TDengine</span>
              <span :class="['service-status', services.tdengine === 'normal' ? 'status-normal' : 'status-warning']">
                {{ getServiceStatusText(services.tdengine) }}
              </span>
            </div>
          </div>
          <div class="card-body">
            <div class="service-content">
              <div class="service-info">
                <div class="info-item">
                  <span class="info-label">状态:</span>
                  <span class="info-value">{{ servicesData.tdengine?.status || '未知' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">主机:</span>
                  <span class="info-value mono">localhost:6030</span>
                </div>
                <div class="info-item">
                  <span class="info-label">数据库:</span>
                  <span class="info-value mono">mystocks</span>
                </div>
              </div>
              <div class="service-actions">
                <button @click="checkService('tdengine')" class="button button-sm">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                  </svg>
                  检查
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="history-section">
      <div class="section-title">
        <span>监控历史</span>
        <span class="subtitle">MONITORING HISTORY</span>
      </div>
      <div class="card history-table-card">
        <div class="card-body">
          <StockListTable
            :columns="historyColumns"
            :data="historyData"
            :loading="isLoading"
            :row-clickable="false"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useApiService } from '@/composables/useApiService'
import { PageHeader, StockListTable } from '@/components/shared'
import type { TableColumn } from '@/components/shared'

const { getHealthData } = useApiService()

const autoRefresh = ref(false)
const refreshInterval = ref(60000)
const isLoading = ref(false)
const error = ref<string | null>(null)

const services = ref({
  frontend: 'normal' as 'normal' | 'warning',
  api: 'normal' as 'normal' | 'warning',
  postgresql: 'normal' as 'normal' | 'warning',
  tdengine: 'warning' as 'normal' | 'warning'
})

const servicesData = ref<{
  frontend: { responseTime: number } | null
  api: { status: string } | null
  postgresql: { status: string } | null
  tdengine: { status: string } | null
}>({
  frontend: null,
  api: null,
  postgresql: null,
  tdengine: null
})

const historyData = ref<any[]>([])

const FRONTEND_URL = 'http://localhost:3000'
const API_BASE_URL = 'http://localhost:8000'

// 历史表格列配置
const historyColumns = computed((): TableColumn[] => [
  {
    prop: 'timestamp',
    label: '时间',
    width: 180,
    formatter: (value: number) => formatDateTime(value)
  },
  {
    prop: 'frontend',
    label: '前端',
    width: 80,
    align: 'center',
    formatter: (value: number) => getStatusText(value)
  },
  {
    prop: 'api',
    label: 'API',
    width: 80,
    align: 'center',
    formatter: (value: number) => getStatusText(value)
  },
  {
    prop: 'postgresql',
    label: 'PostgreSQL',
    width: 100,
    align: 'center',
    formatter: (value: string) => getStatusText(value)
  },
  {
    prop: 'tdengine',
    label: 'TDengine',
    width: 100,
    align: 'center',
    formatter: (value: string) => getStatusText(value)
  },
  {
    prop: 'overallStatus',
    label: '整体状态',
    width: 100,
    align: 'center',
    colorClass: (_value: any, row: any) => row.overallStatus === 'normal' ? 'status-normal' : 'status-warning',
    formatter: (value: string) => value === 'normal' ? '正常' : '异常'
  }
])

const isSystemHealthy = computed(() => {
  return Object.values(services.value).every(status => status === 'normal')
})

const systemStatusMessage = computed(() => {
  if (isSystemHealthy.value) {
    return '所有服务运行正常，没有检测到问题'
  } else {
    const issues = Object.entries(services.value)
      .filter(([_, value]) => value !== 'normal')
      .map(([key]) => {
        switch(key) {
          case 'frontend': return '前端服务'
          case 'api': return 'API服务'
          case 'postgresql': return 'PostgreSQL'
          case 'tdengine': return 'TDengine'
          default: return key
        }
      })
      .join('、')

    return `检测到问题: ${issues}`
  }
})

const formatDateTime = (timestamp: number): string => {
  const date = new Date(timestamp)
  return date.toLocaleString()
}

const getStatusText = (status: number | string): string => {
  if (typeof status === 'number') {
    return status === 200 ? '✓' : '⚠'
  }
  return status === 'normal' ? '✓' : '⚠'
}

const getServiceStatusText = (status: 'normal' | 'warning'): string => {
  return status === 'normal' ? '正常' : '警告'
}

const checkService = async (serviceName: 'frontend' | 'api' | 'postgresql' | 'tdengine') => {
  try {
    isLoading.value = true
    error.value = null

    const healthData = await getHealthData()

    if (serviceName === 'frontend') {
      services.value.frontend = healthData.frontend === 200 ? 'normal' : 'warning'
      servicesData.value.frontend = {
        responseTime: healthData.frontendResponseTime
      }
    } else if (serviceName === 'api') {
      services.value.api = healthData.api === 200 ? 'normal' : 'warning'
      servicesData.value.api = {
        status: healthData.api === 200 ? '正常' : '异常'
      }
    } else if (serviceName === 'postgresql') {
      services.value.postgresql = healthData.postgresql === '正常' ? 'normal' : 'warning'
      servicesData.value.postgresql = {
        status: healthData.postgresql
      }
    } else if (serviceName === 'tdengine') {
      services.value.tdengine = healthData.tdengine === '可访问' ? 'normal' : 'warning'
      servicesData.value.tdengine = {
        status: healthData.tdengine
      }
    }

    addToHistory(healthData)
  } catch (err: any) {
    console.error(`检查服务 ${serviceName} 失败:`, err)
    error.value = `检查服务 ${serviceName} 失败: ${err.message}`
  } finally {
    isLoading.value = false
  }
}

const refreshData = async () => {
  try {
    isLoading.value = true
    error.value = null

    const healthData = await getHealthData()

    services.value.frontend = healthData.frontend === 200 ? 'normal' : 'warning'
    services.value.api = healthData.api === 200 ? 'normal' : 'warning'
    services.value.postgresql = healthData.postgresql === '正常' ? 'normal' : 'warning'
    services.value.tdengine = healthData.tdengine === '可访问' ? 'normal' : 'warning'

    servicesData.value.frontend = {
      responseTime: healthData.frontendResponseTime
    }
    servicesData.value.api = {
      status: healthData.api === 200 ? '正常' : '异常'
    }
    servicesData.value.postgresql = {
      status: healthData.postgresql
    }
    servicesData.value.tdengine = {
      status: healthData.tdengine
    }

    addToHistory(healthData)
  } catch (err: any) {
    console.error('刷新数据失败:', err)
    error.value = `刷新数据失败: ${err.message}`
  } finally {
    isLoading.value = false
  }
}

const addToHistory = (healthData: any) => {
  historyData.value.unshift({
    timestamp: healthData.timestamp,
    frontend: healthData.frontend,
    api: healthData.api,
    postgresql: healthData.postgresql,
    tdengine: healthData.tdengine,
    overallStatus: healthData.overallStatus
  })

  if (historyData.value.length > 10) {
    historyData.value.pop()
  }
}

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value

  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

let refreshTimer: number | null = null

const startAutoRefresh = () => {
  stopAutoRefresh()
  refreshTimer = window.setInterval(() => {
    refreshData()
  }, refreshInterval.value)
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

onMounted(() => {
  refreshData()

  for (let i = 1; i <= 3; i++) {
    const timestamp = Date.now() - (i * 3600000)
    const healthData = {
      timestamp,
      frontend: 200,
      api: 200,
      postgresql: '正常',
      tdengine: '不可访问'
    }
    addToHistory(healthData)
  }
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped lang="scss">

  padding: 24px;
  background: var(--bg-primary);
  background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(212, 175, 55, 0.02) 10px, rgba(212, 175, 55, 0.02) 11px);
  min-height: 100vh;

  .page-header {
    margin-bottom: 32px;
  }

  .error-message {
    background: rgba(255, 82, 82, 0.1);
    border: 1px solid var(--rise);
    color: var(--rise);
    padding: 16px;
    border-left: 4px solid var(--rise);
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 12px;

    .error-icon {
      width: 24px;
      height: 24px;
      flex-shrink: 0;
    }
  }

  .loading-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--gold-primary);
    font-family: var(--font-body);
    font-size: 14px;
    font-weight: 600;

    .loading-icon {
      width: 20px;
      height: 20px;
      animation: spin 2s linear infinite;
    }
  }

  .monitor-summary {
    margin-bottom: 32px;

    .summary-card {
      margin-bottom: 24px;

      &.status-normal {
        border-color: var(--fall);
      }

      &.status-warning {
        border-color: #e6a23c;
      }

      .summary-content {
        display: flex;
        align-items: center;
        gap: 20px;

        .summary-icon {
          width: 64px;
          height: 64px;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;

          svg {
            width: 100%;
            height: 100%;
          }
        }

        &.status-normal .summary-icon svg {
          color: var(--fall);
        }

        &.status-warning .summary-icon svg {
          color: #e6a23c;
        }

        .summary-info {
          flex: 1;

          .summary-title {
            font-family: var(--font-display);
            font-size: 24px;
            font-weight: 700;
            color: var(--gold-primary);
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 8px;
          }

          .summary-description {
            font-family: var(--font-body);
            font-size: 14px;
            color: var(--text-secondary);
          }
        }
      }
    }

    .summary-details {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;

      .detail-card {
        .detail-content {
          text-align: center;
          padding: 20px;

          .detail-label {
            font-family: var(--font-body);
            font-size: 12px;
            color: var(--gold-muted);
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 12px;
          }

          .detail-value {
            font-family: var(--font-mono);
            font-size: 28px;
            font-weight: 700;

            &.status-normal {
              color: var(--fall);
            }

            &.status-warning {
              color: #e6a23c;
            }
          }
        }
      }
    }
  }

  .section-title {
    text-align: center;
    margin-bottom: 24px;

    span {
      font-family: var(--font-display);
      font-size: 28px;
      font-weight: 700;
      color: var(--gold-primary);
      text-transform: uppercase;
      letter-spacing: 3px;
      display: block;
    }

    .subtitle {
      font-family: var(--font-body);
      font-size: 11px;
      color: var(--artde-gold-muted);
      letter-spacing: 6px;
      text-transform: uppercase;
      margin-top: 4px;
    }
  }

  .services-section {
    margin-bottom: 32px;

    .services-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
      gap: 20px;

      .service-card {
        .card-header {
          .service-status {
            font-family: var(--font-body);
            font-size: 11px;
            padding: 6px 16px;
            text-transform: uppercase;
            letter-spacing: 1px;

            &.status-normal {
              background: rgba(0, 230, 118, 0.1);
              color: var(--fall);
              border: 1px solid var(--fall);
            }

            &.status-warning {
              background: rgba(230, 162, 60, 0.1);
              color: #e6a23c;
              border: 1px solid #e6a23c;
            }
          }
        }

        .service-content {
          display: flex;
          justify-content: space-between;
          gap: 20px;

          .service-info {
            flex: 1;

            .info-item {
              margin-bottom: 12px;
              display: flex;
              align-items: center;
              gap: 8px;

              .info-label {
                font-family: var(--font-body);
                font-size: 12px;
                color: var(--gold-muted);
                text-transform: uppercase;
                letter-spacing: 1px;
                flex-shrink: 0;
              }

              .info-value {
                font-family: var(--font-body);
                font-size: 14px;
                color: var(--artde-text-primary);
                word-break: break-all;

                &.mono {
                  font-family: var(--font-mono);
                }
              }
            }
          }

          .service-actions {
            display: flex;
            flex-direction: column;
            gap: 12px;

            .button,
            a.button {
              text-decoration: none;
            }
          }
        }
      }
    }
  }

  .history-section {
    .history-table-card {
      .card-body {
        min-height: 200px;
      }
    }
  }

  .card {
    background: var(--bg-card);
    border: 1px solid var(--gold-dim);
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

      .header-title {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;

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
    text-decoration: none;

    svg {
      width: 18px;
      height: 18px;
    }

    &:hover:not(:disabled) {
      background: var(--gold-primary);
      color: var(--bg-primary);
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    &.loading {
      opacity: 0.6;
      cursor: not-allowed;
    }

    &.active {
      background: var(--gold-primary);
      color: var(--bg-primary);
    }

    &.button-primary {
      border-color: var(--rise);
      color: var(--rise);

      &.active {
        background: var(--rise);
        color: var(--bg-primary);
      }
    }

    &.button-sm {
      padding: 8px 16px;
      font-size: 12px;
      letter-spacing: 1px;

      svg {
        width: 16px;
        height: 16px;
      }
    }

    &::before {
      content: '';
      position: absolute;
      top: 4px;
      left: 4px;
      width: 8px;
      height: 8px;
      border-left: 1px solid currentColor;
      border-top: 1px solid currentColor;
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
    padding: 16px;

    .services-section {
      .services-grid {
        grid-template-columns: 1fr;

        .service-card {
          .service-content {
            flex-direction: column;
          }

          .service-actions {
            width: 100%;

            .button {
              width: 100%;
            }
          }
        }
      }
    }
  }
}
</style>
