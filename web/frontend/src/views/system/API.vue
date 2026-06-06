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
      <ArtDecoStatCard label="服务状态" :value="systemStatusLabel" :variant="health?.status === 'healthy' ? 'rise' : 'fall'" :show-change="false" />
      <ArtDecoStatCard label="服务名称" :value="displayServiceLabel" variant="gold" :show-change="false" />
      <ArtDecoStatCard label="版本" :value="displayVersionLabel" variant="gold" :show-change="false" />
      <ArtDecoStatCard label="中间件项" :value="displayMiddlewareCount" variant="gold" :show-change="false" />
    </section>

    <section :class="isEmbedded ? 'embedded-shell' : 'content-shell artdeco-card-shell'">
      <div v-if="!isEmbedded" class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">health and telemetry route</span>
          <h2 class="content-shell-title">系统健康与遥测面板</h2>
          <p class="content-shell-subtitle">{{ contentShellDescription }}</p>
        </div>
        <div class="content-shell-meta">
          <span>REQ_ID: {{ displayRequestId }}</span>
          <span>MIDDLEWARE: {{ displayMiddlewareCount }}</span>
        </div>
      </div>

      <p v-if="runtimeMessage" class="runtime-message" aria-live="polite">{{ runtimeMessage }}</p>

      <div class="health-grid" v-loading="loading">
        <ArtDecoCard class="status-card" title="后端服务状态" hoverable>
          <div class="status-indicator">
            <div :class="['glow-dot', health?.status === 'healthy' ? 'online' : 'offline']"></div>
            <span class="status-text">{{ systemStatusLabel }}</span>
          </div>
          <div class="info-row">
            <span>Service:</span>
            <span>{{ displayServiceLabel }}</span>
          </div>
          <div class="info-row">
            <span>Version:</span>
            <span>{{ displayVersionLabel }}</span>
          </div>
        </ArtDecoCard>

        <ArtDecoCard class="status-card" title="中间件层" hoverable>
          <div class="middleware-list">
            <div v-for="row in middlewareRows" :key="row.name" class="mw-item">
              <span class="mw-name">{{ row.name }}</span>
              <span :class="['mw-status', row.statusClass]">{{ row.statusLabel }}</span>
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

      <ContractImpactPanel />

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
              <span>{{ store.requestCount }}</span>
              <span>{{ store.lastDurationMs }}</span>
              <span>{{ store.averageDurationMs }}</span>
            </div>
          </section>
        </div>
      </ArtDecoCard>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { useBackendReadiness } from '@/composables/useBackendReadiness'
import { monitoringApi } from '@/api/index'
import { useRiskAlertsStore, useTechnicalIndicatorsStore, useTradingSignalsStore, useWatchlistsStore } from '@/stores/apiStores'
import { frontendStorePolicies } from '@/stores/storePolicies'
import { ArtDecoButton, ArtDecoCard, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import ContractImpactPanel from './components/ContractImpactPanel.vue'
import { normalizeSystemHealthProbeResponse } from './healthProbeContract'

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
  requestCount?: number
  lastDurationMs?: number | null
  averageDurationMs?: number | null
}

interface MiddlewareRow {
  name: string
  activeLabel: string
  inactiveLabel: string
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

const { loading, error, exec, lastRequestId } = useArtDecoApi()
const {
  readinessState,
  readinessMessage,
  requestId: readinessRequestId,
  backendReady,
  usingMockFallback,
  checkBackendReadiness,
} = useBackendReadiness()
const health = ref<MonitoringHealthData | null>(null)
const staleError = ref<string | null>(null)
const hasVerifiedHealthSnapshot = ref(false)
const lastVerifiedRequestId = ref('')
const middlewareCount = 3
const middlewareRegistry: MiddlewareRow[] = [
  {
    name: '性能追踪',
    activeLabel: '启用',
    inactiveLabel: '未校验',
  },
  {
    name: '统一响应',
    activeLabel: '启用',
    inactiveLabel: '未校验',
  },
  {
    name: 'Redis 缓存',
    activeLabel: '活跃',
    inactiveLabel: '未校验',
  },
]
const tradingSignalsStore = useTradingSignalsStore()
const riskAlertsStore = useRiskAlertsStore()
const watchlistsStore = useWatchlistsStore()
const technicalIndicatorsStore = useTechnicalIndicatorsStore()

const isEmbedded = computed(() => Boolean(props.functionKey))
const displayRequestId = computed(() => (hasVerifiedHealthSnapshot.value ? (lastVerifiedRequestId.value || 'N/A') : 'N/A'))
const systemStatusLabel = computed(() => health.value?.status?.toUpperCase() || 'UNKNOWN')
const displayServiceLabel = computed(() => (hasVerifiedHealthSnapshot.value ? health.value?.service || 'N/A' : '--'))
const displayVersionLabel = computed(() => (hasVerifiedHealthSnapshot.value ? health.value?.version || 'N/A' : '--'))
const displayMiddlewareCount = computed(() => (hasVerifiedHealthSnapshot.value ? `${middlewareCount}` : '--'))
const runtimeVerified = computed(() => health.value?.status === 'healthy')
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
  if (staleError.value) return '刷新异常'
  if (error.value) return hasVerifiedHealthSnapshot.value ? '刷新异常' : '探针异常'
  if (loading.value) return hasVerifiedHealthSnapshot.value ? '刷新中' : '同步中'
  if (!health.value) return '等待探针'
  return health.value?.status === 'healthy' ? '探针在线' : '状态待确认'
})
const pageStatusType = computed(() => {
  if (staleError.value || error.value) return 'warning'
  if (!health.value) return 'info'
  return health.value?.status === 'healthy' ? 'success' : 'warning'
})
const contentShellDescription = computed(() => '查看服务健康状态、中间件链路和导出报告能力，作为系统治理链路中的可观测性节点。')
const runtimeMessage = computed(() => {
  if (staleError.value) return `${staleError.value}，当前仍显示上次成功同步的系统探针快照。`
  if (error.value) {
    return hasVerifiedHealthSnapshot.value ? `${error.value}，当前仍显示上次成功同步的系统探针快照。` : `${error.value}，当前暂无已验证系统探针快照。`
  }
  if (loading.value) return hasVerifiedHealthSnapshot.value ? '系统遥测探针刷新中...' : '系统遥测探针同步中...'
  if (!health.value) return '当前没有可展示的系统健康探针数据。'
  return ''
})
const middlewareRows = computed(() =>
  middlewareRegistry.map((row) => ({
    name: row.name,
    statusLabel: runtimeVerified.value ? row.activeLabel : row.inactiveLabel,
    statusClass: runtimeVerified.value ? 'active' : 'pending',
  }))
)
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
    endpoint: '/v1/trade/signals',
    cache: `${frontendStorePolicies.tradingSignals.cache.strategy}:${frontendStorePolicies.tradingSignals.cache.ttl}ms`,
  },
  {
    id: frontendStorePolicies.riskAlerts.capability,
    sourceOfTruth: frontendStorePolicies.riskAlerts.sourceOfTruth,
    endpoint: '/api/risk/alerts',
    cache: `${frontendStorePolicies.riskAlerts.cache.strategy}:${frontendStorePolicies.riskAlerts.cache.ttl}ms`,
  },
  {
    id: frontendStorePolicies.monitoringWatchlists.capability,
    sourceOfTruth: frontendStorePolicies.monitoringWatchlists.sourceOfTruth,
    endpoint: '/v1/monitoring/watchlists',
    cache: `${frontendStorePolicies.monitoringWatchlists.cache.strategy}:${frontendStorePolicies.monitoringWatchlists.cache.ttl}ms`,
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
  requestCount: String(store.requestCount ?? 0),
  lastDurationMs: store.lastDurationMs !== null && store.lastDurationMs !== undefined ? `${store.lastDurationMs}ms` : 'n/a',
  averageDurationMs: store.averageDurationMs !== null && store.averageDurationMs !== undefined ? `${store.averageDurationMs}ms` : 'n/a',
})

const storeSnapshots = computed(() => [
  toInspectorSnapshot(frontendStorePolicies.tradingSignals.capability, tradingSignalsStore as unknown as InspectorStoreState),
  toInspectorSnapshot(frontendStorePolicies.riskAlerts.capability, riskAlertsStore as unknown as InspectorStoreState),
  toInspectorSnapshot(frontendStorePolicies.monitoringWatchlists.capability, watchlistsStore as unknown as InspectorStoreState),
  toInspectorSnapshot(frontendStorePolicies.technicalIndicators.capability, technicalIndicatorsStore as unknown as InspectorStoreState),
])

const fetchHealth = async () => {
  staleError.value = null
  const data = await exec(async () => normalizeSystemHealthProbeResponse(await monitoringApi.getSystemHealth()), {
    errorMsg: '无法连接到后端服务'
  })
  if (data) {
    health.value = data as MonitoringHealthData
    hasVerifiedHealthSnapshot.value = true
    lastVerifiedRequestId.value = lastRequestId.value || lastVerifiedRequestId.value
    return
  }

  if (hasVerifiedHealthSnapshot.value && error.value) {
    staleError.value = error.value
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
  ElMessage.success('试点 Store 已触发刷新。')
}

onMounted(async () => {
  await Promise.allSettled([fetchHealth(), checkBackendReadiness()])
})
</script>
<style scoped lang="scss" src="./styles/API.scss"></style>
