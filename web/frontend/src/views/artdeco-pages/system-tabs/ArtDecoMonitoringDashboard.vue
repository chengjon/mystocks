<template>
  <div class="monitoring-dashboard page-enter">
    <div class="artdeco-header-bar">
      <h2 class="section-title">系统监控面板</h2>
      <div class="trace-id" v-if="requestId">REQ_ID: {{ requestId }}</div>
    </div>

    <div class="health-grid" v-loading="loading">
      <ArtDecoCard class="status-card" title="后端服务状态" hoverable>
        <div class="status-indicator">
          <div :class="['glow-dot', health?.status === 'healthy' ? 'online' : 'offline']"></div>
          <span class="status-text">{{ health?.status?.toUpperCase() || 'UNKNOWN' }}</span>
        </div>
        <div class="info-row">
          <span>Service:</span>
          <span>{{ health?.service || 'N/A' }}</span>
        </div>
        <div class="info-row">
          <span>Version:</span>
          <span>{{ health?.version || 'N/A' }}</span>
        </div>
      </ArtDecoCard>

      <ArtDecoCard class="status-card" title="中间件层" hoverable>
        <div class="middleware-list">
          <div class="mw-item">
            <span class="mw-name">性能追踪</span>
            <span class="mw-status active">启用</span>
          </div>
          <div class="mw-item">
            <span class="mw-name">统一响应</span>
            <span class="mw-status active">启用</span>
          </div>
          <div class="mw-item">
            <span class="mw-name">Redis 缓存</span>
            <span class="mw-status active">活跃</span>
          </div>
        </div>
      </ArtDecoCard>
    </div>

    <div class="action-bar">
      <ArtDecoButton variant="outline" size="sm" @click="fetchDashboard">刷新</ArtDecoButton>
      <ArtDecoButton variant="outline" size="sm" @click="exportReport">导出报告</ArtDecoButton>
    </div>

    <ArtDecoCard class="metrics-card" title="API 指标" hoverable>
      <div v-if="showMetricsErrorState" class="monitoring-dashboard__state monitoring-dashboard__state--error" role="alert">
        {{ error }}
      </div>
      <div v-else-if="showMetricsEmptyState" class="monitoring-dashboard__state" role="status" aria-live="polite">
        暂无接口监控数据。
      </div>
      <div v-else class="metrics-list">
        <div v-for="metric in metrics" :key="metric.endpoint" class="metric-row">
          <span class="metric-endpoint">{{ metric.endpoint }}</span>
          <span>QPS {{ metric.qps }}</span>
          <span>P95 {{ metric.p95 }} ms</span>
          <span>错误率 {{ metric.errorRate }}</span>
        </div>
      </div>
    </ArtDecoCard>

    <ArtDecoCard class="observability-note" hoverable>
      <p>
        <strong class="gold-text">说明：</strong> 所有 API 交互均通过 UUID v4 请求 ID 追踪。
        慢查询（&gt;300ms）由性能监控中间件自动标记并上报至后端遥测系统。
      </p>
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { monitoringApi } from '@/api/index'
import { ArtDecoCard, ArtDecoButton } from '@/components/artdeco'

interface MonitoringHealthData {
  request_id?: string
  status?: string
  service?: string
  version?: string
  [key: string]: unknown
}

interface MonitoringMetricRow {
  endpoint: string
  qps: string
  p95: string
  errorRate: string
}

const { loading, error, exec } = useArtDecoApi()
const health = ref<MonitoringHealthData | null>(null)
const requestId = ref('')
const metrics = ref<MonitoringMetricRow[]>([])

const showMetricsErrorState = computed(() => Boolean(error.value) && metrics.value.length === 0)
const showMetricsEmptyState = computed(() => !loading.value && !error.value && metrics.value.length === 0)

function toMetricRows(payload: unknown): MonitoringMetricRow[] {
  const container = (payload ?? {}) as Record<string, unknown>
  const candidate =
    (Array.isArray(payload) ? payload : null) ??
    (Array.isArray(container.data) ? container.data : null) ??
    (Array.isArray(container.apis) ? container.apis : null) ??
    (Array.isArray(container.metrics) ? container.metrics : null)

  if (!candidate) {
    return []
  }

  return candidate.map((item, index) => {
    const row = (item ?? {}) as Record<string, unknown>
    return {
      endpoint: typeof row.endpoint === 'string'
        ? row.endpoint
        : typeof row.name === 'string'
          ? row.name
          : `API-${index + 1}`,
      qps: String(row.qps ?? row.avg_qps ?? '-'),
      p95: String(row.p95 ?? row.p95_ms ?? row.latency ?? row.avg_latency_ms ?? '-'),
      errorRate: String(row.errorRate ?? row.error_rate ?? '0.00%'),
    }
  })
}

async function fetchDashboard() {
  const healthData = await exec(() => monitoringApi.getSystemHealth(), {
    errorMsg: '无法连接到后端服务',
    silent: true,
  })

  if (healthData) {
    health.value = healthData as MonitoringHealthData
    requestId.value =
      (healthData as MonitoringHealthData).request_id ||
      requestId.value ||
      `sys-${Date.now()}`
  } else {
    health.value = null
  }

  const detailData = await exec(() => monitoringApi.getDetailedSystemHealth(), {
    errorMsg: '获取接口监控数据失败',
    silent: true,
  })

  metrics.value = detailData ? toMetricRows(detailData) : []
}

async function exportReport() {
  const data = await exec(() => monitoringApi.getDetailedSystemHealth(), {
    errorMsg: '导出报告失败',
    silent: true,
  })

  if (!data) {
    return
  }

  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `system-health-${new Date().toISOString()}.json`
  link.click()
  URL.revokeObjectURL(url)
}

onMounted(() => {
  void fetchDashboard()
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.monitoring-dashboard {
  padding: var(--artdeco-spacing-6);

  .artdeco-header-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--artdeco-spacing-8);
    border-bottom: 2px solid var(--artdeco-gold-primary);
    padding-bottom: var(--artdeco-spacing-2);

    .section-title {
      margin: 0;
      font-size: var(--artdeco-text-2xl);
      color: var(--artdeco-gold-primary);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
    }

    .trace-id {
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-text-xs);
      color: var(--artdeco-fg-muted);
      letter-spacing: var(--artdeco-tracking-wide);
    }
  }

  .health-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--artdeco-spacing-8);
    margin-bottom: var(--artdeco-spacing-8);

    .status-card {
      padding: var(--artdeco-spacing-6);

      .status-indicator {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-4);
        margin-bottom: var(--artdeco-spacing-6);

        .glow-dot {
          width: 12px;
          height: 12px;
          border-radius: 50%;

          &.online {
            background: var(--artdeco-rise);
            box-shadow: 0 0 15px var(--artdeco-rise);
          }

          &.offline {
            background: var(--artdeco-down);
            box-shadow: 0 0 15px var(--artdeco-down);
          }
        }

        .status-text {
          font-family: var(--artdeco-font-display);
          font-size: var(--artdeco-text-xl);
          letter-spacing: 0.1em;
        }
      }
    }
  }

  .info-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--artdeco-spacing-2);
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-sm);
    color: var(--artdeco-fg-muted);
  }

  .middleware-list {
    .mw-item {
      display: flex;
      justify-content: space-between;
      padding: var(--artdeco-spacing-2) 0;
      border-bottom: 1px solid var(--artdeco-gold-opacity-10);

      .mw-name {
        font-size: var(--artdeco-text-sm);
      }

      .mw-status.active {
        color: var(--artdeco-rise);
        font-weight: bold;
      }
    }
  }

  .action-bar {
    display: flex;
    gap: var(--artdeco-spacing-4);
    margin-bottom: var(--artdeco-spacing-8);
  }

  .metrics-card {
    margin-bottom: var(--artdeco-spacing-8);
  }

  .monitoring-dashboard__state {
    padding: var(--artdeco-spacing-5);
    border: 1px solid var(--artdeco-border-default);
    background: linear-gradient(145deg, var(--artdeco-gold-opacity-05), transparent 65%);
    color: var(--artdeco-fg-primary);

    &--error {
      color: var(--artdeco-down);
    }
  }

  .metrics-list {
    display: flex;
    flex-direction: column;
    gap: var(--artdeco-spacing-3);
  }

  .metric-row {
    display: grid;
    grid-template-columns: minmax(220px, 2fr) repeat(3, minmax(0, 1fr));
    gap: var(--artdeco-spacing-3);
    padding: var(--artdeco-spacing-3);
    border: 1px solid var(--artdeco-border-default);
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-sm);
    color: var(--artdeco-fg-secondary);
  }

  .metric-endpoint {
    color: var(--artdeco-gold-primary);
  }

  .observability-note {
    padding: var(--artdeco-spacing-6);
    font-style: italic;
    font-size: var(--artdeco-text-sm);
    line-height: var(--artdeco-leading-relaxed);
    color: var(--artdeco-fg-muted);

    p {
      margin: 0;
    }

    .gold-text {
      color: var(--artdeco-gold-primary);
    }
  }
}

@media (width <= 1200px) {
  .monitoring-dashboard {
    .health-grid {
      grid-template-columns: 1fr;
    }

    .metric-row {
      grid-template-columns: 1fr;
    }
  }
}
</style>
