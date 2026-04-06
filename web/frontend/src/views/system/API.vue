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
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { monitoringApi } from '@/api/index'
import { ArtDecoButton, ArtDecoCard, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'

interface MonitoringHealthData {
  request_id?: string
  status?: string
  service?: string
  version?: string
  [key: string]: unknown
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
const health = ref<MonitoringHealthData | null>(null)
const requestId = ref('')
const middlewareCount = 3

const isEmbedded = computed(() => Boolean(props.functionKey))
const displayRequestId = computed(() => requestId.value || 'N/A')
const systemStatusLabel = computed(() => health.value?.status?.toUpperCase() || 'UNKNOWN')
const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  return health.value?.status === 'healthy' ? '探针在线' : '状态待确认'
})
const pageStatusType = computed(() => (health.value?.status === 'healthy' ? 'success' : 'warning'))
const contentShellDescription = computed(() => '查看服务健康状态、中间件链路和导出报告能力，作为系统治理链路中的可观测性节点。')

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

onMounted(fetchHealth)
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
