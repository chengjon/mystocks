<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { apiClient } from '@/api/apiClient'
import { ArtDecoButton, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import { buildConceptRequest, extractConceptRows, type ConceptRow } from './marketConceptData'

const { loading, lastRequestId, exec } = useArtDecoApi()
const concepts = ref<ConceptRow[]>([])

const positiveConcepts = computed(() => concepts.value.filter((concept) => concept.change_pct >= 0).length)
const negativeConcepts = computed(() => concepts.value.filter((concept) => concept.change_pct < 0).length)
const topLeader = computed(() => concepts.value[0]?.leader || 'N/A')
const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  return positiveConcepts.value >= negativeConcepts.value ? '概念偏强' : '概念承压'
})
const pageStatusType = computed(() => (positiveConcepts.value >= negativeConcepts.value ? 'success' : 'warning'))

const fetchConcepts = async () => {
  const request = buildConceptRequest()
  const data = await exec(() => apiClient.get(request.path, { params: request.params }), {
    silent: true
  })

  concepts.value = extractConceptRows(data)
}

onMounted(() => {
  void fetchConcepts()
})
</script>

<template>
  <div class="market-concept-tab page-enter">
    <section class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">concept sector desk</span>
          <div class="hero-meta">
            <span v-if="lastRequestId">REQ: {{ lastRequestId }}</span>
            <span>SECTORS: {{ concepts.length }}</span>
            <span>LEADER: {{ topLeader }}</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="概念板块工作台"
        subtitle="统一观察概念板块涨跌、主力净流入和龙头股，形成板块动向入口"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" @click="fetchConcepts">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新板块
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="概念总数" :value="concepts.length" variant="gold" />
      <ArtDecoStatCard label="上涨概念" :value="positiveConcepts" variant="rise" />
      <ArtDecoStatCard label="下跌概念" :value="negativeConcepts" variant="fall" />
      <ArtDecoStatCard label="龙头股" :value="topLeader" variant="gold" />
    </section>

    <section class="content-shell artdeco-card-shell">
      <div class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">sector breadth route</span>
          <h3 class="content-shell-title">概念强弱与龙头面板</h3>
          <p class="content-shell-subtitle">按概念板块审查涨跌幅、主力净流入和龙头股，快速识别最强板块与承压板块。</p>
        </div>
        <div class="content-shell-meta">
          <span>POSITIVE: {{ positiveConcepts }}</span>
          <span>NEGATIVE: {{ negativeConcepts }}</span>
        </div>
      </div>

      <div class="concept-table-container artdeco-card" v-loading="loading">
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
                  <div
                    :class="['trend-bar', c.change_pct >= 0 ? 'trend-bar--rise' : 'trend-bar--down']"
                    :style="{ height: `${Math.abs(c.change_pct) * 5}px` }"
                  ></div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
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

.trend-bar--rise {
  background: var(--artdeco-rise);
}

.trend-bar--down {
  background: var(--artdeco-down);
}

@media (width <= 75rem) {
  .stats-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (width <= 48rem) {
  .stats-strip {
    grid-template-columns: 1fr;
  }

  .hero-meta,
  .content-shell-meta {
    width: 100%;
  }
}
</style>
