<template>
  <div class="monitor-page">
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
import { PageHeader, StockListTable } from '@/components/shared'
import { usemonitor } from './composables/usemonitor'

const {
  autoRefresh,
  isLoading,
  error,
  services,
  servicesData,
  historyData,
  FRONTEND_URL,
  API_BASE_URL,
  historyColumns,
  isSystemHealthy,
  systemStatusMessage,
  getServiceStatusText,
  checkService,
  refreshData,
  toggleAutoRefresh
} = usemonitor()
</script>

<style scoped lang="scss">
@use './styles/monitor.scss' as *;
</style>
