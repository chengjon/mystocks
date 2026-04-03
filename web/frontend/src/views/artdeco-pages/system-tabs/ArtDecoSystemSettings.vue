<template>
  <div class="system-settings-page">
    <div class="page-header">
      <div>
        <h2 class="section-title">系统配置中心</h2>
        <div class="header-meta">
          <span>DATA: {{ monitorSource }}</span>
          <span>REQ_ID: {{ displayRequestId }}</span>
          <span>TIME: {{ displayProcessTime }}</span>
        </div>
      </div>
      <ArtDecoButton variant="solid" size="sm" @click="saveAll">保存本地设置</ArtDecoButton>
    </div>

    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="tab"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <div class="analysis-blocker" role="status" aria-live="polite">
      统一系统配置后端契约仍未建立，当前页面仅保留本地设置持久化与健康监控视图；
      数据源真实配置写回请前往“系统数据”页。
    </div>

    <template v-if="activeTab === 'sources'">
      <div class="stats-grid">
        <ArtDecoStatCard label="可用数据源" :value="4" variant="gold" />
        <ArtDecoStatCard label="健康状态" :value="'3/4'" variant="rise" />
        <ArtDecoStatCard label="今日调用" :value="'28,412'" variant="gold" />
        <ArtDecoStatCard label="异常告警" :value="2" variant="fall" />
      </div>
      <ArtDecoCard title="数据源优先级" hoverable>
        <ArtDecoTable :columns="sourceColumns" :data="sourceRows" />
      </ArtDecoCard>
    </template>

    <template v-if="activeTab === 'settings'">
      <ArtDecoCard title="核心参数" hoverable>
        <div class="form-grid">
          <div class="field">
            <label>后端地址</label>
            <ArtDecoInput v-model="form.backendUrl" />
          </div>
          <div class="field">
            <label>回测最大并发</label>
            <ArtDecoInput v-model="form.maxBacktestJobs" />
          </div>
          <div class="field">
            <label>默认滑点(%)</label>
            <ArtDecoInput v-model="form.slippage" />
          </div>
          <div class="field">
            <label>交易手续费(万分比)</label>
            <ArtDecoInput v-model="form.feeRate" />
          </div>
        </div>
      </ArtDecoCard>
    </template>

    <template v-if="activeTab === 'monitor'">
      <ArtDecoCard title="API性能监控" hoverable>
        <ArtDecoTable :columns="apiColumns" :data="apiRows" />
      </ArtDecoCard>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ArtDecoButton, ArtDecoCard, ArtDecoInput, ArtDecoStatCard, ArtDecoTable } from '@/components/artdeco'
import { monitoringApi } from '@/api'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { API_BASE_URL } from '@/config/runtime-endpoints'
import { normalizeSystemSettingsMonitorRows, type MonitorRow } from './systemSettingsMonitorData.ts'

const STORAGE_KEY = 'artdeco-system-settings'

const tabs = [
  { key: 'sources', label: '数据源' },
  { key: 'settings', label: '系统设置' },
  { key: 'monitor', label: '系统监控' }
]

const activeTab = ref('sources')

const form = reactive({
  backendUrl: API_BASE_URL,
  maxBacktestJobs: '4',
  slippage: '0.05',
  feeRate: '2.5'
})

const { lastRequestId, lastProcessTime, exec } = useArtDecoApi()
const monitorSource = ref<'REAL' | 'MOCK'>('REAL')

const sourceColumns = [
  { key: 'name', label: '数据源' },
  { key: 'priority', label: '优先级' },
  { key: 'status', label: '状态', variant: 'color' },
  { key: 'latency', label: '延迟(ms)' },
  { key: 'quota', label: '配额使用率' }
]

const sourceRows = [
  { name: 'AKShare', priority: 1, status: 'online', latency: 92, quota: '64%' },
  { name: 'Tushare', priority: 2, status: 'online', latency: 138, quota: '71%' },
  { name: 'TDX', priority: 3, status: 'degraded', latency: 218, quota: '82%' },
  { name: 'Wind', priority: 4, status: 'offline', latency: '-', quota: '0%' }
]

const apiColumns = [
  { key: 'endpoint', label: '接口' },
  { key: 'qps', label: 'QPS' },
  { key: 'p95', label: 'P95 延迟(ms)' },
  { key: 'errorRate', label: '错误率' }
]

const defaultApiRows: MonitorRow[] = [
  { endpoint: '/api/v1/market/quotes', qps: 53, p95: 128, errorRate: '0.18%' },
  { endpoint: '/api/v1/auth/login', qps: 7, p95: 164, errorRate: '0.02%' },
  { endpoint: '/api/v1/strategy/backtest', qps: 3, p95: 342, errorRate: '0.64%' }
]

const apiRows = ref<MonitorRow[]>([...defaultApiRows])

const displayRequestId = computed(() => lastRequestId.value || 'N/A')
const displayProcessTime = computed(() => {
  if (!lastProcessTime.value) {
    return 'N/A'
  }

  const value = Number.parseFloat(lastProcessTime.value)
  if (Number.isNaN(value)) {
    return lastProcessTime.value
  }

  return `${value.toFixed(2)}ms`
})

async function loadMonitorRows() {
  const detailed = await exec(() => monitoringApi.getDetailedSystemHealth(), {
    silent: true,
    errorMsg: '系统监控数据加载失败'
  })

  if (detailed !== null) {
    const fromDetailed = normalizeSystemSettingsMonitorRows(detailed)

    if (fromDetailed.length > 0) {
      monitorSource.value = 'REAL'
      apiRows.value = fromDetailed
      return
    }
  }

  const health = await exec(() => monitoringApi.getSystemHealth(), {
    silent: true,
    errorMsg: '系统健康状态加载失败'
  })

  if (health !== null) {
    const fromHealth = normalizeSystemSettingsMonitorRows(health)

    if (fromHealth.length > 0) {
      monitorSource.value = 'REAL'
      apiRows.value = fromHealth
      return
    }
  }

  monitorSource.value = 'MOCK'
  apiRows.value = [...defaultApiRows]
}

function restoreSettings() {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) {
    return
  }

  try {
    const saved = JSON.parse(raw) as Partial<typeof form>
    if (typeof saved.backendUrl === 'string') form.backendUrl = saved.backendUrl
    if (typeof saved.maxBacktestJobs === 'string') form.maxBacktestJobs = saved.maxBacktestJobs
    if (typeof saved.slippage === 'string') form.slippage = saved.slippage
    if (typeof saved.feeRate === 'string') form.feeRate = saved.feeRate
  } catch {
    localStorage.removeItem(STORAGE_KEY)
  }
}

function saveAll() {
  if (!form.backendUrl.trim() || !form.maxBacktestJobs.trim() || !form.slippage.trim() || !form.feeRate.trim()) {
    return
  }

  localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...form }))
}

onMounted(() => {
  restoreSettings()
  void loadMonitorRows()
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.system-settings-page {
  padding: var(--artdeco-spacing-6);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-5);
}

.section-title {
  margin: 0;
  font-size: var(--artdeco-text-2xl);
  color: var(--artdeco-gold-primary);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
}

.header-meta {
  margin-top: var(--artdeco-spacing-2);
  display: flex;
  gap: var(--artdeco-spacing-3);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-xs);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
}

.tabs {
  display: flex;
  gap: var(--artdeco-spacing-2);
  margin-bottom: var(--artdeco-spacing-5);
}

.analysis-blocker {
  margin-bottom: var(--artdeco-spacing-5);
  padding: var(--artdeco-spacing-4);
  border: 1px solid var(--artdeco-warning);
  background: color-mix(in srgb, var(--artdeco-warning) 14%, transparent);
  color: var(--artdeco-fg-primary);
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
}

.tab {
  background: transparent;
  border: 1px solid var(--artdeco-border-default);
  color: var(--artdeco-fg-muted);
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
  cursor: pointer;

  &.active {
    color: var(--artdeco-gold-primary);
    border-color: var(--artdeco-gold-primary);
    background: var(--artdeco-gold-opacity-10);
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-5);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}

.field {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);

  label {
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-xs);
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }
}
</style>
