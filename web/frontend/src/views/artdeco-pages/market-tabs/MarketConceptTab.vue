<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { marketService } from '@/api/services/marketService'
import { extractConceptFlowRows } from './marketConceptContract'
import { summarizeConceptRows, toConceptRows, type ConceptRow } from './marketConceptViewModel'

const loading = ref(false)
const lastRequestId = ref('')
const errorMessage = ref('')
const concepts = ref<ConceptRow[]>([])

const summary = computed(() => summarizeConceptRows(concepts.value))

const fetchConcepts = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await marketService.getConceptFundFlow({
      timeframe: '今日',
      limit: 8
    })

    if (response && typeof response === 'object') {
      lastRequestId.value = typeof response.request_id === 'string' ? response.request_id : ''
    }

    if (!response?.success) {
      errorMessage.value = '概念数据加载失败'
      concepts.value = []
      return
    }

    concepts.value = toConceptRows(extractConceptFlowRows(response))
  } catch {
    errorMessage.value = '概念数据加载失败'
    concepts.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchConcepts()
})
</script>

<template>
  <div class="market-concept-tab page-enter">
    <div class="artdeco-header-bar">
      <h2 class="section-title">Concept Sectors</h2>
      <div class="trace-info" v-if="lastRequestId">REQ: {{ lastRequestId }}</div>
    </div>

    <div class="concept-table-container artdeco-card" v-loading="loading">
      <div v-if="errorMessage" class="empty-state">
        <p class="empty-title">{{ errorMessage }}</p>
        <p class="empty-description">暂无概念资金流向数据</p>
      </div>
      <div v-else-if="concepts.length === 0" class="empty-state">
        <p class="empty-title">暂无概念资金流向数据</p>
        <p class="empty-description">等待真实概念板块资金流接口返回数据</p>
      </div>
      <table class="artdeco-table">
        <caption class="sr-only">
          概念板块资金流向，活跃概念 {{ summary.activeConcepts }} 个
        </caption>
        <thead>
          <tr>
            <th>SECTOR NAME</th>
            <th>CHANGE %</th>
            <th>NET INFLOW</th>
            <th>LEADING STOCK</th>
            <th>TREND</th>
          </tr>
        </thead>
        <tbody v-if="!errorMessage && concepts.length > 0">
          <tr v-for="c in concepts" :key="c.name">
            <td class="concept-name">{{ c.name }}</td>
            <td :class="['change', c.changePct >= 0 ? 'rise' : 'down']">
              {{ c.changePct >= 0 ? '+' : '' }}{{ c.changePct.toFixed(2) }}%
            </td>
            <td class="inflow">{{ c.mainInflow }}</td>
            <td class="leader">{{ c.leader }}</td>
            <td>
              <div class="mini-chart">
                <!-- 简易趋势示意图 -->
                <div class="trend-bar" :style="{ height: `${Math.abs(c.changePct) * 5}px`, background: c.changePct >= 0 ? 'var(--artdeco-rise)' : 'var(--artdeco-down)' }"></div>
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
  border-bottom: 2px solid var(--artdeco-gold-primary);
  padding-bottom: var(--artdeco-spacing-2);

  .section-title {
    margin: 0;
    font-size: var(--artdeco-text-2xl);
    color: var(--artdeco-gold-primary);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
  }
}

.concept-table-container {
  padding: var(--artdeco-spacing-4);
  background: var(--artdeco-bg-card);

  @include artdeco-stepped-corners(10px);
}

.empty-state {
  padding: var(--artdeco-spacing-6);
  text-align: center;
  color: var(--artdeco-fg-muted);
}

.empty-title {
  color: var(--artdeco-gold-light);
  font-family: var(--artdeco-font-display);
  margin-bottom: var(--artdeco-spacing-2);
}

.empty-description {
  margin: 0;
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
    border-bottom: 1px solid var(--artdeco-border-default);
  }

  td {
    padding: var(--artdeco-spacing-4);
    color: var(--artdeco-fg-primary);
    border-bottom: 1px solid var(--artdeco-gold-opacity-10);
    font-family: var(--artdeco-font-mono);
  }

  .concept-name {
    font-family: var(--artdeco-font-body);
    font-weight: bold;
    color: var(--artdeco-gold-light);
  }

  .change {
    &.rise {
      color: var(--artdeco-rise);
    }

    &.down {
      color: var(--artdeco-down);
    }
  }

  .leader {
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-sm);
  }
}

.mini-chart {
  display: flex;
  align-items: flex-end;
  height: 30px;
  width: 40px;
  .trend-bar {
    width: 100%;
    border-radius: 1px;
  }
}
</style>
