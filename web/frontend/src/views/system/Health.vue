<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ArtDecoButton, ArtDecoCard, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { apiClient } from '@/api/apiClient'

interface HealthRow {
  status?: string
  service?: string
  version?: string
}

const { loading, lastRequestId, exec } = useArtDecoApi()
const health = ref<HealthRow | null>(null)
const middlewareCount = 3

const systemStatusLabel = computed(() => health.value?.status?.toUpperCase() || 'UNKNOWN')
const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  return health.value?.status === 'healthy' ? '矩阵在线' : '状态待确认'
})
const pageStatusType = computed(() => (health.value?.status === 'healthy' ? 'success' : 'warning'))
const contentShellDescription = computed(() => '校验健康探针、服务版本与中间件层状态，作为系统治理链路中的健康矩阵节点。')

const fetchHealth = async () => {
  const data = await exec(() => apiClient.get('/health'), {
    errorMsg: '无法连接到后端服务'
  })
  if (data) {
    health.value = data as HealthRow
  }
}

onMounted(() => {
  void fetchHealth()
})
</script>

<template>
  <div class="system-health-tab page-enter">
    <section class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">health matrix deck</span>
          <div class="hero-meta">
            <span v-if="lastRequestId">REQ_ID: {{ lastRequestId }}</span>
            <span>STATUS: {{ systemStatusLabel }}</span>
            <span>FOCUS: health probes</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="系统健康矩阵"
        subtitle="从基础健康探针切入，观察服务状态、版本与中间件链路的可运行性"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" :loading="loading" @click="fetchHealth">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新矩阵
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="服务状态" :value="systemStatusLabel" :variant="health?.status === 'healthy' ? 'rise' : 'fall'" />
      <ArtDecoStatCard label="服务名称" :value="health?.service || 'N/A'" variant="gold" />
      <ArtDecoStatCard label="版本" :value="health?.version || 'N/A'" variant="gold" />
      <ArtDecoStatCard label="中间件项" :value="middlewareCount" variant="gold" />
    </section>

    <section class="content-shell artdeco-card-shell">
      <div class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">service viability route</span>
          <h3 class="content-shell-title">服务状态与中间件面板</h3>
          <p class="content-shell-subtitle">{{ contentShellDescription }}</p>
        </div>
        <div class="content-shell-meta">
          <span>STATUS: {{ systemStatusLabel }}</span>
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
              <span class="mw-name">Performance Tracing</span>
              <span class="mw-status active">ENABLED</span>
            </div>
            <div class="mw-item">
              <span class="mw-name">Unified Response</span>
              <span class="mw-status active">ENABLED</span>
            </div>
            <div class="mw-item">
              <span class="mw-name">Redis Caching</span>
              <span class="mw-status active">ACTIVE</span>
            </div>
          </div>
        </ArtDecoCard>
      </div>

      <ArtDecoCard class="observability-note" hoverable>
        <p>
          <strong class="gold-text">Note:</strong> All API interactions are tracked via UUID v4 Request IDs.
          Slow queries (&gt;300ms) are automatically flagged by the Performance Monitoring middleware
          and reported to the backend telemetry system.
        </p>
      </ArtDecoCard>
    </section>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.system-health-tab {
  padding: var(--artdeco-spacing-6);
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-6);
}

.hero-shell,
.stats-strip,
.content-shell {
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

  @include artdeco-stepped-corners(var(--artdeco-spacing-3));
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

  .content-shell-meta,
  .hero-meta {
    width: 100%;
  }
}
</style>
