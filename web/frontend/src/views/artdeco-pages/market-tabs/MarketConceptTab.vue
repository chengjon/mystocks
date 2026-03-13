<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { apiClient } from '@/api/apiClient'

interface ConceptRow {
  name: string
  change_pct: number
  stock_count: number
  leader: string
}

const { loading, error, lastRequestId, exec } = useArtDecoApi()
const concepts = ref<ConceptRow[]>([])

const showErrorState = computed(() => Boolean(error.value) && concepts.value.length === 0)
const showEmptyState = computed(() => !loading.value && !error.value && concepts.value.length === 0)

const fetchConcepts = async () => {
  const data = await exec(
    () => apiClient.get('/data/markets/hot-concepts', { params: { limit: 10 } }),
    { silent: true, errorMsg: '概念板块数据加载失败' }
  )

  const rows = Array.isArray((data as { data?: unknown[] } | null)?.data)
    ? (data as { data: Array<Record<string, unknown>> }).data
    : Array.isArray(data)
      ? (data as Array<Record<string, unknown>>)
      : []

  concepts.value = rows.map((row) => ({
    name: String(row.concept_name ?? row.name ?? '--'),
    change_pct: Number(row.avg_change ?? row.change_pct ?? 0),
    stock_count: Number(row.stock_count ?? 0),
    leader: '待补充'
  }))
}

onMounted(() => {
  void fetchConcepts()
})
</script>

<template>
  <div class="market-concept-tab page-enter">
    <div class="artdeco-header-bar">
      <h2 class="section-title">概念动向</h2>
      <div class="trace-info" v-if="lastRequestId">REQ: {{ lastRequestId }}</div>
    </div>

    <div v-if="showErrorState" class="error-state artdeco-card" role="alert">
      <p>概念板块数据加载失败</p>
      <span>{{ error }}</span>
    </div>

    <div v-else-if="showEmptyState" class="empty-state artdeco-card" role="status" aria-live="polite">
      <p>暂无概念板块数据</p>
      <span>当前保持真实接口模式，不再回退模拟榜单。</span>
    </div>

    <div v-else class="concept-table-container artdeco-card" v-loading="loading">
      <table class="artdeco-table">
        <thead>
          <tr>
            <th>CONCEPT NAME</th>
            <th>CHANGE %</th>
            <th>STOCK COUNT</th>
            <th>LEADING STOCK</th>
            <th>TREND</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="concept in concepts" :key="concept.name">
            <td class="concept-name">{{ concept.name }}</td>
            <td :class="['change', concept.change_pct >= 0 ? 'rise' : 'down']">
              {{ concept.change_pct >= 0 ? '+' : '' }}{{ concept.change_pct.toFixed(2) }}%
            </td>
            <td class="inflow">{{ concept.stock_count }} 只</td>
            <td class="leader">{{ concept.leader }}</td>
            <td>
              <div class="mini-chart">
                <div
                  class="trend-bar"
                  :style="{ height: `${Math.max(6, Math.abs(concept.change_pct) * 5)}px`, background: concept.change_pct >= 0 ? 'var(--artdeco-rise)' : 'var(--artdeco-down)' }"
                ></div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.market-concept-tab {
  padding: var(--artdeco-spacing-6);
}

.artdeco-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-8);
  border-bottom: calc(var(--artdeco-spacing-1) / 2) solid var(--artdeco-gold-primary);
  padding-bottom: var(--artdeco-spacing-2);

  .section-title {
    margin: 0;
    font-size: var(--artdeco-text-2xl);
    color: var(--artdeco-gold-primary);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
  }
}

.trace-info {
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
}

.error-state,
.empty-state {
  display: grid;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-5);
  margin-bottom: var(--artdeco-spacing-6);
  border: thin solid var(--artdeco-border-default);
  background: linear-gradient(145deg, var(--artdeco-gold-opacity-05), transparent 65%);

  p {
    margin: 0;
    color: var(--artdeco-fg-primary);
    font-family: var(--font-display);
    letter-spacing: var(--artdeco-tracking-wide);
  }

  span {
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-sm);
  }
}

.concept-table-container {
  padding: var(--artdeco-spacing-4);
  background: var(--artdeco-bg-card);
  @include artdeco-stepped-corners(var(--artdeco-spacing-3));
}

.artdeco-table {
  width: 100%;
  border-collapse: collapse;

  th {
    padding: var(--artdeco-spacing-4);
    text-align: left;
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-display);
    font-size: var(--artdeco-text-sm);
    border-bottom: thin solid var(--artdeco-border-default);
  }

  td {
    padding: var(--artdeco-spacing-4);
    color: var(--artdeco-fg-primary);
    border-bottom: thin solid var(--artdeco-gold-opacity-10);
    font-family: var(--artdeco-font-mono);
  }

  .concept-name {
    font-family: var(--artdeco-font-body);
    font-weight: bold;
    color: var(--artdeco-gold-light);
  }

  .change.rise {
    color: var(--artdeco-rise);
  }

  .change.down {
    color: var(--artdeco-down);
  }

  .leader {
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-sm);
  }
}

.mini-chart {
  display: flex;
  align-items: flex-end;
  height: 2rem;
  width: 2.5rem;

  .trend-bar {
    width: 100%;
    border-radius: 1px;
  }
}
</style>
