<script setup lang="ts">
import { ArtDecoBadge, ArtDecoButton, ArtDecoCard, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'

import { DEFAULT_WINDOW_MINUTES, useSystemResourcesPage } from './composables/useSystemResourcesPage'

const {
  contentShellDescription,
  criticalCount,
  dependencySnapshots,
  dependencyTrackedLabel,
  displayRequestId,
  formatMemoryMb,
  formatMetricValue,
  formatPercent,
  formatTimestamp,
  hasVerifiedSnapshot,
  hostMetrics,
  loading,
  metricMetaSummary,
  overallStatusLabel,
  pageStatusText,
  pageStatusType,
  pollingButtonLabel,
  processSnapshots,
  processTrackedLabel,
  resourceSnapshot,
  runtimeMessage,
  sparklinePoints,
  statsCriticalCount,
  statsDependencyCount,
  statsProcessCount,
  statusVariant,
  togglePolling,
} = useSystemResourcesPage()
</script>

<template>
  <div class="resource-usage-page page-enter">
    <section class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">single-node resource observatory</span>
          <div class="hero-meta">
            <span>REQ_ID: {{ displayRequestId }}</span>
            <span>STATUS: {{ overallStatusLabel }}</span>
            <span>NODE: {{ resourceSnapshot?.node.node_id || 'N/A' }}</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="资源使用工作台"
        subtitle="分离 host、process 与 dependency 资源视角，形成独立的系统资源观察面"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton class="polling-toggle" variant="outline" size="sm" @click="togglePolling">
            <template #icon>
              <ArtDecoIcon name="pause" />
            </template>
            {{ pollingButtonLabel }}
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="整体状态" :value="overallStatusLabel" :variant="statusVariant(resourceSnapshot?.node.overall_status || 'warning')" :show-change="false" />
      <ArtDecoStatCard label="监控节点" :value="resourceSnapshot?.node.node_id || 'N/A'" variant="gold" :show-change="false" />
      <ArtDecoStatCard label="运行进程" :value="statsProcessCount" variant="gold" :show-change="false" />
      <ArtDecoStatCard label="关键告警" :value="statsCriticalCount" :variant="!hasVerifiedSnapshot ? 'gold' : criticalCount > 0 ? 'fall' : 'rise'" :show-change="false" />
      <ArtDecoStatCard label="依赖摘要" :value="statsDependencyCount" variant="gold" :show-change="false" />
    </section>

    <section class="content-shell artdeco-card-shell">
      <div class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">host + process + dependency views</span>
          <h2 class="content-shell-title">单节点资源快照与短窗口趋势</h2>
          <p class="content-shell-subtitle">{{ contentShellDescription }}</p>
        </div>
        <div class="content-shell-meta">
          <span>WINDOW: {{ resourceSnapshot?.node.window_minutes || DEFAULT_WINDOW_MINUTES }}m</span>
          <span>POLL: {{ resourceSnapshot?.node.polling_interval_seconds || 15 }}s</span>
          <span>UPDATED: {{ formatTimestamp(resourceSnapshot?.node.sampled_at) }}</span>
        </div>
      </div>

      <p v-if="runtimeMessage" class="runtime-message" aria-live="polite">{{ runtimeMessage }}</p>

      <div class="host-grid" v-loading="loading">
        <ArtDecoCard v-for="metric in hostMetrics" :key="metric.metric_key" class="metric-card" hoverable>
          <div class="metric-card-header">
            <div>
              <p class="metric-label">{{ metric.label }}</p>
              <h3 class="metric-value">{{ formatMetricValue(metric) }}</h3>
            </div>
            <ArtDecoBadge :text="metric.status.toUpperCase()" :variant="statusVariant(metric.status)" />
          </div>
          <div class="metric-meta">
            <span>Warn {{ metric.warning_threshold }}{{ metric.unit }}</span>
            <span>Critical {{ metric.critical_threshold }}{{ metric.unit }}</span>
            <span>{{ metricMetaSummary(metric) }}</span>
          </div>
          <svg class="sparkline" viewBox="0 0 120 40" preserveAspectRatio="none" aria-hidden="true">
            <polyline :points="sparklinePoints(metric.series)" />
          </svg>
        </ArtDecoCard>
      </div>

      <div class="resource-lower-grid">
        <ArtDecoCard class="resource-section" hoverable>
          <div class="section-header">
            <h3>运行进程</h3>
            <span>{{ processTrackedLabel }}</span>
          </div>
          <div v-if="processSnapshots.length" class="entity-list">
            <div v-for="process in processSnapshots" :key="process.process_key" class="entity-row">
              <div class="entity-copy">
                <strong>{{ process.display_name }}</strong>
                <span>{{ process.summary }}</span>
                <span>PID {{ process.pid ?? 'N/A' }} · Started {{ formatTimestamp(process.started_at) }}</span>
              </div>
              <div class="entity-metrics">
                <ArtDecoBadge :text="process.status.toUpperCase()" :variant="statusVariant(process.status)" />
                <span>{{ formatPercent(process.cpu_percent) }}</span>
                <span>{{ formatMemoryMb(process.memory_mb) }}</span>
              </div>
            </div>
          </div>
          <p v-else class="empty-state">当前没有可展示的进程快照。</p>
        </ArtDecoCard>

        <ArtDecoCard class="resource-section" hoverable>
          <div class="section-header">
            <h3>依赖摘要</h3>
            <span>{{ dependencyTrackedLabel }}</span>
          </div>
          <div v-if="dependencySnapshots.length" class="entity-list">
            <div v-for="dependency in dependencySnapshots" :key="dependency.dependency_key" class="entity-row">
              <div class="entity-copy">
                <strong>{{ dependency.display_name }}</strong>
                <span>{{ dependency.summary }}</span>
                <span>{{ JSON.stringify(dependency.metrics) }}</span>
              </div>
              <div class="entity-metrics">
                <ArtDecoBadge :text="dependency.status.toUpperCase()" :variant="statusVariant(dependency.status)" />
              </div>
            </div>
          </div>
          <p v-else class="empty-state">当前没有可展示的依赖摘要。</p>
        </ArtDecoCard>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss" src="./styles/Resources.scss"></style>
