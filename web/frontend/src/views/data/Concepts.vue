<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { apiClient } from '@/api/apiClient'
import { ArtDecoButton, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import ArtDecoRouteHeader from '@/components/artdeco/route-shell/ArtDecoRouteHeader.vue'
import { buildConceptRequest, extractConceptRows, type ConceptRow } from './marketConceptData'

const { loading, error, lastRequestId, exec } = useArtDecoApi()
const concepts = ref<ConceptRow[]>([])
const hasLoaded = ref(false)
const refreshWarning = ref('')
const lastVerifiedRequestId = ref('')

const positiveConcepts = computed(() => concepts.value.filter((concept) => concept.change_pct >= 0).length)
const negativeConcepts = computed(() => concepts.value.filter((concept) => concept.change_pct < 0).length)
const topLeader = computed(() => concepts.value[0]?.leader || 'N/A')
const showSummaryPlaceholders = computed(() => !hasLoaded.value || (Boolean(error.value) && concepts.value.length === 0))
const displaySectorCount = computed(() => (showSummaryPlaceholders.value ? '--' : String(concepts.value.length)))
const displayPositiveConcepts = computed(() => (showSummaryPlaceholders.value ? '--' : String(positiveConcepts.value)))
const displayNegativeConcepts = computed(() => (showSummaryPlaceholders.value ? '--' : String(negativeConcepts.value)))
const displayTopLeader = computed(() => (showSummaryPlaceholders.value ? '--' : topLeader.value))
const displayRequestId = computed(() => {
  if (showSummaryPlaceholders.value) {
    return 'N/A'
  }

  return lastVerifiedRequestId.value || lastRequestId.value || 'N/A'
})
const showRefreshWarning = computed(() => !loading.value && refreshWarning.value.length > 0 && concepts.value.length > 0)
const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  if (showRefreshWarning.value) return '刷新异常'
  if (error.value) return '同步异常'
  if (hasLoaded.value && concepts.value.length === 0) return '暂无概念数据'
  return positiveConcepts.value >= negativeConcepts.value ? '概念偏强' : '概念承压'
})
const pageStatusType = computed(() => {
  if (showRefreshWarning.value) return 'warning'
  if (error.value) return 'danger'
  if (loading.value || (hasLoaded.value && concepts.value.length === 0)) return 'info'
  return positiveConcepts.value >= negativeConcepts.value ? 'success' : 'warning'
})
const showLoadingState = computed(() => loading.value && !hasLoaded.value)
const showErrorState = computed(() => !loading.value && Boolean(error.value) && concepts.value.length === 0)
const showEmptyState = computed(() => !loading.value && hasLoaded.value && !error.value && concepts.value.length === 0)

const fetchConcepts = async () => {
  const hadPreviousData = concepts.value.length > 0
  const request = buildConceptRequest()
  const data = await exec(() => apiClient.get(request.path, { params: request.params }), {
    silent: true,
    errorMsg: '概念板块数据加载失败'
  })

  if (data === null) {
    if (hadPreviousData) {
      refreshWarning.value = '当前仍展示上次成功同步的概念板块数据，请稍后重试刷新。'
    } else {
      refreshWarning.value = ''
      concepts.value = []
    }
    hasLoaded.value = true
    return
  }

  refreshWarning.value = ''
  concepts.value = extractConceptRows(data)
  lastVerifiedRequestId.value = lastRequestId.value || lastVerifiedRequestId.value
  hasLoaded.value = true
}

onMounted(() => {
  void fetchConcepts()
})
</script>

<template>
  <div class="market-concept-tab page-enter">
    <ArtDecoRouteHeader
      title="概念板块工作台"
      subtitle="统一观察概念板块涨跌、主力净流入和龙头股，形成板块动向入口"
      eyebrow="concept sector desk"
      :show-status="true"
      :status-text="pageStatusText"
      :status-type="pageStatusType"
      test-id="data-concept-header"
      shell-class="hero-shell artdeco-card-shell"
    >
      <template #meta>
        <span>REQ: {{ displayRequestId }}</span>
        <span>SECTORS: {{ displaySectorCount }}</span>
        <span>LEADER: {{ displayTopLeader }}</span>
      </template>

      <template #actions>
        <ArtDecoButton
          variant="outline"
          size="sm"
          :loading="loading"
          :disabled="loading"
          data-testid="data-concept-refresh"
          @click="fetchConcepts"
        >
          <template #icon>
            <ArtDecoIcon name="refresh" />
          </template>
          刷新板块
        </ArtDecoButton>
      </template>
    </ArtDecoRouteHeader>

    <section class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="概念总数" :value="displaySectorCount" :show-change="false" variant="gold" />
      <ArtDecoStatCard label="上涨概念" :value="displayPositiveConcepts" :show-change="false" variant="rise" />
      <ArtDecoStatCard label="下跌概念" :value="displayNegativeConcepts" :show-change="false" variant="fall" />
      <ArtDecoStatCard label="龙头股" :value="displayTopLeader" :show-change="false" variant="gold" />
    </section>

    <section class="content-shell artdeco-card-shell">
      <div class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">sector breadth route</span>
          <h2 class="content-shell-title">概念强弱与龙头面板</h2>
          <p class="content-shell-subtitle">按概念板块审查涨跌幅、主力净流入和龙头股，快速识别最强板块与承压板块。</p>
        </div>
        <div class="content-shell-meta">
          <span>POSITIVE: {{ displayPositiveConcepts }}</span>
          <span>NEGATIVE: {{ displayNegativeConcepts }}</span>
        </div>
      </div>

      <div v-if="showLoadingState" class="state-panel artdeco-card" role="status" aria-live="polite">
        <p>概念板块同步中</p>
        <span>正在刷新概念强弱与龙头股数据。</span>
      </div>

      <div v-if="showRefreshWarning" class="state-panel warning-panel artdeco-card" role="status" aria-live="polite">
        <p>部分刷新失败</p>
        <span>{{ refreshWarning }}</span>
      </div>

      <div v-if="showErrorState" class="state-panel artdeco-card" role="alert">
        <p>概念板块数据加载失败</p>
        <span>{{ error }}</span>
        <ArtDecoButton variant="outline" size="sm" @click="fetchConcepts">重试刷新</ArtDecoButton>
      </div>

      <div v-else-if="showEmptyState" class="state-panel artdeco-card" role="status" aria-live="polite">
        <p>暂无概念数据</p>
        <span>当前环境未返回概念板块排行，可稍后刷新重试。</span>
      </div>

      <div v-else class="concept-table-container artdeco-card" v-loading="loading">
        <div class="concept-table-scroll">
          <table class="artdeco-table">
            <thead>
              <tr>
                <th>SECTOR NAME</th>
                <th>CHANGE %</th>
                <th>NET INFLOW</th>
                <th>LEADING STOCK</th>
                <th>TREND</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in concepts" :key="c.name">
                <td class="concept-name">{{ c.name }}</td>
                <td :class="['change', c.change_pct >= 0 ? 'rise' : 'down']">
                  {{ c.change_pct >= 0 ? '+' : '' }}{{ c.change_pct }}%
                </td>
                <td class="inflow">{{ c.main_inflow }}</td>
                <td class="leader">{{ c.leader }}</td>
                <td>
                  <div class="mini-chart">
                    <div class="trend-bar" :style="{ height: `${Math.abs(c.change_pct) * 5}px`, background: c.change_pct >= 0 ? 'var(--artdeco-rise)' : 'var(--artdeco-down)' }"></div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.market-concept-tab {
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
  justify-content: space-between;
  align-items: flex-start;
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
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
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

.concept-table-container {
  padding: var(--artdeco-spacing-4);
  background: var(--artdeco-bg-card);

  @include artdeco-stepped-corners(calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) * 2));
}

.concept-table-scroll {
  overflow-x: auto;
}

.state-panel {
  display: grid;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-5);
  border: 1px solid var(--artdeco-border-default);
  background: linear-gradient(145deg, var(--artdeco-gold-opacity-05), transparent 65%);
}

.warning-panel {
  border-color: var(--artdeco-warning);
  background: linear-gradient(145deg, color-mix(in srgb, var(--artdeco-warning) 12%, transparent), transparent 70%);
}

.state-panel p {
  margin: 0;
  color: var(--artdeco-fg-primary);
  font-family: var(--artdeco-font-display);
}

.state-panel span {
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
}

.artdeco-table {
  width: 100%;
  border-collapse: collapse;
}

.artdeco-table th {
  padding: var(--artdeco-spacing-4);
  text-align: left;
  color: var(--artdeco-gold-primary);
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-sm);
  border-bottom: 1px solid var(--artdeco-border-default);
}

.artdeco-table td {
  padding: var(--artdeco-spacing-4);
  color: var(--artdeco-fg-primary);
  border-bottom: 1px solid var(--artdeco-gold-opacity-10);
  font-family: var(--artdeco-font-mono);
}

.artdeco-table .concept-name {
  font-family: var(--artdeco-font-body);
  font-weight: bold;
  color: var(--artdeco-gold-light);
}

.artdeco-table .change.rise {
  color: var(--artdeco-rise);
}

.artdeco-table .change.down {
  color: var(--artdeco-down);
}

.artdeco-table .leader {
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
}

.mini-chart {
  display: flex;
  align-items: flex-end;
  height: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1) + var(--artdeco-spacing-px) * 2);
  width: calc(var(--artdeco-spacing-8) + var(--artdeco-spacing-2));
}

.trend-bar {
  width: 100%;
  border-radius: 1px;
}

@media (width <= 75rem) {
  .stats-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
