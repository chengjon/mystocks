<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi';
import { apiClient } from '@/api/apiClient';

interface ConceptRow {
  name: string
  change_pct: number
  main_inflow: string
  leader: string
}

const { loading, lastRequestId, exec } = useArtDecoApi();
const concepts = ref<ConceptRow[]>([]);

const fetchConcepts = async () => {
  // 调用 v1 概念板块接口
  const data = await exec(() => apiClient.get('/v1/market/concept', { params: { sort: 'change_pct', order: 'desc' } }), {
    silent: true
  });
  
  if (data && (data as Record<string, unknown>).items) {
    concepts.value = (data as Record<string, unknown>).items as ConceptRow[];
  } else {
    // 降级模拟
    concepts.value = [
      { name: '人工智能', change_pct: 3.42, main_inflow: '12.5B', leader: '科大讯飞' },
      { name: '半导体', change_pct: 2.15, main_inflow: '8.2B', leader: '中芯国际' },
      { name: '新能源车', change_pct: -1.05, main_inflow: '-3.1B', leader: '比亚迪' },
      { name: '低空经济', change_pct: 5.67, main_inflow: '5.4B', leader: '万丰奥威' }
    ];
  }
};

onMounted(() => {
  fetchConcepts();
});
</script>

<template>
  <div class="market-concept-tab page-enter">
    <div class="artdeco-header-bar">
      <h2 class="section-title">Concept Sectors</h2>
      <div class="trace-info" v-if="lastRequestId">REQ: {{ lastRequestId }}</div>
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
                <!-- 简易趋势示意图 -->
                <div class="trend-bar" :style="{ height: `${Math.abs(c.change_pct) * 5}px`, background: c.change_pct >= 0 ? 'var(--artdeco-rise)' : 'var(--artdeco-down)' }"></div>
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
