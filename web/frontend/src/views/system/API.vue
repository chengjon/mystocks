<template>
  <div class="monitoring-dashboard page-enter" :class="{ 'is-embedded': isEmbedded }">
    <section v-if="!isEmbedded" class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">observability control deck</span>
          <div class="hero-meta">
            <span>REQ_ID: {{ displayRequestId }}</span>
            <span>STATUS: {{ systemStatusLabel }}</span>
            <span>FOCUS: telemetry</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="系统监控工作台"
        subtitle="汇聚服务健康、中间件状态与遥测追踪，形成可观测性控制面板"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" :loading="loading" @click="fetchHealth">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新探针
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section v-if="!isEmbedded" class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="服务状态" :value="systemStatusLabel" :variant="health?.status === 'healthy' ? 'rise' : 'fall'" />
      <ArtDecoStatCard label="服务名称" :value="health?.service || 'N/A'" variant="gold" />
      <ArtDecoStatCard label="版本" :value="health?.version || 'N/A'" variant="gold" />
      <ArtDecoStatCard label="中间件项" :value="middlewareCount" variant="gold" />
    </section>

    <section :class="isEmbedded ? 'embedded-shell' : 'content-shell artdeco-card-shell'">
      <div v-if="!isEmbedded" class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">health and telemetry route</span>
          <h3 class="content-shell-title">系统健康与遥测面板</h3>
          <p class="content-shell-subtitle">{{ contentShellDescription }}</p>
        </div>
        <div class="content-shell-meta">
          <span>REQ_ID: {{ displayRequestId }}</span>
          <span>MIDDLEWARE: {{ middlewareCount }}</span>
        </div>
      </div>

      <div class="health-grid" v-loading="loading">
        <ArtDecoCard class="status-card" title="后端服务状态" hoverable>
          <div class="status-indicator">
            <div :class="['glow-dot', health?.status === 'healthy' ? 'online' : 'offline']"></div>
            <span class="status-text">{{ systemStatusLabel }}</span>
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
        <ArtDecoButton variant="outline" size="sm" @click="fetchHealth">刷新</ArtDecoButton>
        <ArtDecoButton variant="outline" size="sm" @click="exportReport">导出报告</ArtDecoButton>
      </div>

      <ArtDecoCard class="observability-note" hoverable>
        <p>
          <strong class="gold-text">说明：</strong> 所有 API 交互均通过 UUID v4 请求 ID 追踪。
          慢查询（&gt;300ms）由性能监控中间件自动标记并上报至后端遥测系统。
        </p>
      </ArtDecoCard>

      <ArtDecoCard v-if="showDeveloperInspector" class="governance-card" title="前端数据治理检查面板" hoverable>
        <div class="governance-meta">
          <span>Readiness: {{ readinessState }}</span>
          <span>Backend: {{ backendReady ? 'ready' : 'not-ready' }}</span>
          <span>Fallback: {{ usingMockFallback ? 'enabled' : 'disabled' }}</span>
          <span>Request ID: {{ readinessRequestId || displayRequestId }}</span>
        </div>
        <p class="governance-message">{{ readinessMessage }}</p>

        <div class="action-bar governance-actions">
          <ArtDecoButton variant="outline" size="sm" @click="checkBackendReadiness">刷新 Readiness</ArtDecoButton>
          <ArtDecoButton variant="outline" size="sm" @click="refreshInspectorStores">刷新试点 Store</ArtDecoButton>
        </div>

        <div class="governance-grid">
          <section class="governance-section">
            <h4>Capability Registry</h4>
            <div v-for="capability in capabilityRows" :key="capability.id" class="governance-row">
              <span>{{ capability.id }}</span>
              <span>{{ capability.sourceOfTruth }}</span>
              <span>{{ capability.endpoint }}</span>
              <span>{{ capability.cache }}</span>
            </div>
          </section>

          <section class="governance-section">
            <h4>Realtime Registry</h4>
            <div v-for="channel in realtimeRows" :key="channel.name" class="governance-row">
              <span>{{ channel.name }}</span>
              <span>{{ channel.consumer }}</span>
              <span>{{ channel.coalescing }}</span>
              <span>{{ channel.refresh }}</span>
            </div>
          </section>

          <section class="governance-section">
            <h4>Store Runtime</h4>
            <div v-for="store in storeSnapshots" :key="store.id" class="governance-row">
              <span>{{ store.id }}</span>
              <span>{{ store.loading }}</span>
              <span>{{ store.error }}</span>
              <span>{{ store.lastFetch }}</span>
            </div>
          </section>
        </div>
      </ArtDecoCard>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { useBackendReadiness } from '@/composables/useBackendReadiness'
import { monitoringApi } from '@/api/index'
import { useRiskAlertsStore, useTechnicalIndicatorsStore, useTradingSignalsStore, useWatchlistsStore } from '@/stores/apiStores'
import { frontendStorePolicies } from '@/stores/storePolicies'
import { ArtDecoButton, ArtDecoCard, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'

interface MonitoringHealthData {
  request_id?: string
  status?: string
  service?: string
  version?: string
  [key: string]: unknown
}

interface InspectorStoreState {
  loading?: boolean
  error?: string | null
  lastFetch?: number | null
}

interface Props {
  functionKey?: string
  userPermissions?: string[]
  systemConfig?: unknown
}

const props = withDefaults(defineProps<Props>(), {
  functionKey: '',
  userPermissions: () => [],
  systemConfig: undefined
})

const { loading, exec } = useArtDecoApi()
const {
  readinessState,
  readinessMessage,
  requestId: readinessRequestId,
  backendReady,
  usingMockFallback,
  checkBackendReadiness,
} = useBackendReadiness()
const health = ref<MonitoringHealthData | null>(null)
const requestId = ref('')
const middlewareCount = 3
const tradingSignalsStore = useTradingSignalsStore()
const riskAlertsStore = useRiskAlertsStore()
const watchlistsStore = useWatchlistsStore()
const technicalIndicatorsStore = useTechnicalIndicatorsStore()

const isEmbedded = computed(() => Boolean(props.functionKey))
const displayRequestId = computed(() => requestId.value || 'N/A')
const systemStatusLabel = computed(() => health.value?.status?.toUpperCase() || 'UNKNOWN')
const showDeveloperInspector = computed(() => {
  if (import.meta.env.DEV) {
    return true
  }

  if (typeof window === 'undefined') {
    return false
  }

  return window.localStorage.getItem('mystocks:developer-mode') === 'true'
})
const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  return health.value?.status === 'healthy' ? '探针在线' : '状态待确认'
})
const pageStatusType = computed(() => (health.value?.status === 'healthy' ? 'success' : 'warning'))
const contentShellDescription = computed(() => '查看服务健康状态、中间件链路和导出报告能力，作为系统治理链路中的可观测性节点。')
const capabilityRows = computed(() => [
  {
    id: frontendStorePolicies.technicalIndicators.capability,
    sourceOfTruth: frontendStorePolicies.technicalIndicators.sourceOfTruth,
    endpoint: '/v1/technical-indicators',
    cache: `${frontendStorePolicies.technicalIndicators.cache.strategy}:${frontendStorePolicies.technicalIndicators.cache.ttl}ms`,
  },
  {
    id: frontendStorePolicies.tradingSignals.capability,
    sourceOfTruth: frontendStorePolicies.tradingSignals.sourceOfTruth,
    endpoint: '/api/trading/signals',
    cache: `${frontendStorePolicies.tradingSignals.cache.strategy}:${frontendStorePolicies.tradingSignals.cache.ttl}ms`,
  },
  {
    id: frontendStorePolicies.riskAlerts.capability,
    sourceOfTruth: frontendStorePolicies.riskAlerts.sourceOfTruth,
    endpoint: '/api/risk/alerts',
    cache: `${frontendStorePolicies.riskAlerts.cache.strategy}:${frontendStorePolicies.riskAlerts.cache.ttl}ms`,
  },
  {
    id: frontendStorePolicies.userWatchlists.capability,
    sourceOfTruth: frontendStorePolicies.userWatchlists.sourceOfTruth,
    endpoint: '/api/user/watchlists',
    cache: `${frontendStorePolicies.userWatchlists.cache.strategy}:${frontendStorePolicies.userWatchlists.cache.ttl}ms`,
  },
])
const realtimeRows = computed(() => [
  {
    name: 'market:realtime:{symbol}',
    consumer: 'useRealtimeMarket.subscribeStock',
    coalescing: 'latest-only / 200ms',
    refresh: 'unsubscribe -> resubscribe',
  },
  {
    name: 'market:summary',
    consumer: 'useRealtimeMarket.subscribeMarketSummary',
    coalescing: 'latest-only / 200ms',
    refresh: 'unsubscribe -> resubscribe',
  },
  {
    name: frontendStorePolicies.tradingSignals.realtime?.channel || 'trading-signals',
    consumer: 'useTradingSignalsStore',
    coalescing: 'store-level update',
    refresh: 'refresh()',
  },
  {
    name: frontendStorePolicies.riskAlerts.realtime?.channel || 'risk-alerts',
    consumer: 'useRiskAlertsStore',
    coalescing: 'store-level update',
    refresh: 'refresh()',
  },
])

const toInspectorSnapshot = (id: string, store: InspectorStoreState) => ({
  id,
  loading: String(store.loading ?? false),
  error: store.error || 'none',
  lastFetch: store.lastFetch ? new Date(store.lastFetch).toISOString() : 'never',
})

const storeSnapshots = computed(() => [
  toInspectorSnapshot(frontendStorePolicies.tradingSignals.capability, tradingSignalsStore as unknown as InspectorStoreState),
  toInspectorSnapshot(frontendStorePolicies.riskAlerts.capability, riskAlertsStore as unknown as InspectorStoreState),
  toInspectorSnapshot(frontendStorePolicies.userWatchlists.capability, watchlistsStore as unknown as InspectorStoreState),
  toInspectorSnapshot(frontendStorePolicies.technicalIndicators.capability, technicalIndicatorsStore as unknown as InspectorStoreState),
])

const fetchHealth = async () => {
  const data = await exec(() => monitoringApi.getSystemHealth(), {
    errorMsg: '无法连接到后端服务'
  })
  if (data) {
    health.value = data as MonitoringHealthData
    requestId.value = health.value.request_id || `sys-${Date.now()}`
  }
}

const exportReport = async () => {
  try {
    const data = await exec(() => monitoringApi.getDetailedSystemHealth(), {
      errorMsg: '导出报告失败'
    })
    if (data) {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `system-health-${new Date().toISOString()}.json`
      link.click()
      URL.revokeObjectURL(url)
    }
  } catch (err) {
    console.error('Export failed:', err)
  }
}

const refreshInspectorStores = async () => {
  await Promise.allSettled([
    tradingSignalsStore.refresh(),
    riskAlertsStore.refresh(),
    watchlistsStore.refresh(),
  ])
}

onMounted(async () => {
  await Promise.allSettled([fetchHealth(), checkBackendReadiness()])
})
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.monitoring-dashboard {
  padding: var(--artdeco-spacing-6);
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-6);
}

.monitoring-dashboard.is-embedded {
  padding: 0;
}

.hero-shell,
.stats-strip,
.content-shell,
.embedded-shell {
  width: 100%;
}

.hero-shell,
.content-shell {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-5);
}

.hero-rail,
.content-shell-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--artdeco-spacing-4);
  flex-wrap: wrap;
}

.hero-copy,
.content-shell-copy {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.hero-eyebrow,
.content-shell-kicker {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-gold-dim);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
}

.hero-meta,
.content-shell-meta {
  display: flex;
  gap: var(--artdeco-spacing-3);
  flex-wrap: wrap;
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
}

.content-shell-title {
  margin: 0;
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-xl);
  color: var(--artdeco-fg-primary);
}

.content-shell-subtitle {
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
}

.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}

.health-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(calc(var(--artdeco-spacing-20) * 4 + var(--artdeco-spacing-20)), 1fr));
  gap: var(--artdeco-spacing-8);
  margin-bottom: var(--artdeco-spacing-8);
}

.status-card {
  padding: var(--artdeco-spacing-6);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-6);
}

.glow-dot {
  width: var(--artdeco-spacing-3);
  height: var(--artdeco-spacing-3);
  border-radius: 50%;
}

.glow-dot.online {
  background: var(--artdeco-rise);
  box-shadow: 0 0 calc(var(--artdeco-spacing-3) + var(--artdeco-spacing-px) * 3) var(--artdeco-rise);
}

.glow-dot.offline {
  background: var(--artdeco-down);
  box-shadow: 0 0 calc(var(--artdeco-spacing-3) + var(--artdeco-spacing-px) * 3) var(--artdeco-down);
}

.status-text {
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-xl);
  letter-spacing: 0.1em;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--artdeco-spacing-2);
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-sm);
  color: var(--artdeco-fg-muted);
}

.middleware-list .mw-item {
  display: flex;
  justify-content: space-between;
  padding: var(--artdeco-spacing-2) 0;
  border-bottom: 1px solid var(--artdeco-gold-opacity-10);
}

.mw-name {
  font-size: var(--artdeco-text-sm);
}

.mw-status.active {
  color: var(--artdeco-rise);
  font-weight: bold;
}

.action-bar {
  display: flex;
  justify-content: flex-end;
  gap: var(--artdeco-spacing-3);
  margin-bottom: var(--artdeco-spacing-6);
}

.observability-note {
  padding: var(--artdeco-spacing-6);
  font-style: italic;
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
  color: var(--artdeco-fg-muted);
}

.observability-note p {
  margin: 0;
}

.governance-card {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-4);
}

.governance-meta,
.governance-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-3);
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
}

.governance-message {
  margin: 0;
  color: var(--artdeco-fg-muted);
}

.governance-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(18rem, 1fr));
  gap: var(--artdeco-spacing-4);
}

.governance-section {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.governance-section h4 {
  margin: 0 0 var(--artdeco-spacing-2);
  color: var(--artdeco-fg-primary);
}

.gold-text {
  color: var(--artdeco-gold-primary);
}

@media (width <= 75rem) {
  .stats-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .health-grid {
    grid-template-columns: 1fr;
  }

  .governance-meta,
  .governance-row {
    grid-template-columns: 1fr;
  }
}

@media (width <= 48rem) {
  .stats-strip {
    grid-template-columns: 1fr;
  }

  .action-bar,
  .content-shell-meta,
  .hero-meta {
    width: 100%;
  }

  .action-bar {
    justify-content: stretch;
  }
}
</style>
