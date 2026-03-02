<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi';
import { dataApi } from '@/api/index';

interface KLineRow {
  datetime: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

const { loading, lastRequestId, exec } = useArtDecoApi();
const klineData = ref<KLineRow[]>([]);
const currentSymbol = ref('000001');

const fetchKLine = async () => {
  const data = await exec(() => dataApi.getKline({ 
    symbol: currentSymbol.value,
    period: 'daily',
    limit: 100
  }), { silent: true });
  
  if (data && Array.isArray((data as { data?: unknown }).data)) {
    const rows = (data as { data: Array<Record<string, unknown>> }).data
    klineData.value = rows.map((row, index) => ({
      datetime: String(row.datetime ?? row.time ?? index),
      open: Number(row.open ?? 0),
      high: Number(row.high ?? 0),
      low: Number(row.low ?? 0),
      close: Number(row.close ?? 0),
      volume: Number(row.volume ?? 0)
    }))
  }
};

onMounted(() => {
  fetchKLine();
});
</script>

<template>
  <div class="market-kline-tab page-enter">
    <div class="artdeco-header-bar">
      <div class="symbol-info">
        <h2 class="section-title">K-Line Analysis</h2>
        <span class="active-symbol">{{ currentSymbol }}</span>
      </div>
      <div class="trace-id" v-if="lastRequestId">REQ: {{ lastRequestId }}</div>
    </div>

    <!-- K线图占位符 (实际集成时会使用 Highcharts/ECharts) -->
    <div class="kline-container artdeco-card" v-loading="loading">
      <div class="chart-placeholder">
        <div class="placeholder-icon">📊</div>
        <p>Real-time K-Line Data Stream Active</p>
        <div class="data-summary" v-if="klineData.length > 0">
          Last Price: <span class="gold-text">{{ klineData[klineData.length-1].close }}</span>
          | Data Points: {{ klineData.length }}
        </div>
      </div>
      <!-- 阶梯角点缀 -->
      <div class="ziggurat-corners"></div>
    </div>

    <!-- 数据表格 -->
    <div class="data-table-section artdeco-card">
      <table class="artdeco-table">
        <thead>
          <tr>
            <th>DATE</th>
            <th>OPEN</th>
            <th>HIGH</th>
            <th>LOW</th>
            <th>CLOSE</th>
            <th>VOL</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="k in klineData.slice(-5).reverse()" :key="k.datetime">
            <td class="date">{{ k.datetime.split(' ')[0] }}</td>
            <td>{{ k.open }}</td>
            <td class="rise">{{ k.high }}</td>
            <td class="down">{{ k.low }}</td>
            <td :class="k.close >= k.open ? 'rise' : 'down'">{{ k.close }}</td>
            <td>{{ (k.volume / 10000).toFixed(1) }}万</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.market-kline-tab {
  padding: var(--artdeco-spacing-6);
}

.artdeco-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-8);
  border-bottom: 2px solid var(--artdeco-gold-primary);
  padding-bottom: var(--artdeco-spacing-2);

  .symbol-info {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-4);
    
    .section-title {
      margin: 0;
      font-size: var(--artdeco-text-2xl);
      color: var(--artdeco-gold-primary);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
    }
    .active-symbol { 
      background: var(--artdeco-gold-primary);
      color: var(--artdeco-bg-global);
      padding: 2px 8px;
      font-family: var(--artdeco-font-mono);
      font-weight: bold;
    }
  }
}

.kline-container {
  height: 400px;
  background: var(--artdeco-bg-elevated);
  margin-bottom: var(--artdeco-spacing-8);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  border: 1px solid var(--artdeco-border-default);

  @include artdeco-stepped-corners(15px);

  .chart-placeholder {
    text-align: center;
    .placeholder-icon {
      font-size: 48px;
      margin-bottom: 16px;
      opacity: 50%;
    }
    p {
      font-family: var(--artdeco-font-display);
      color: var(--artdeco-fg-muted);
      letter-spacing: 0.1em;
    }
    .gold-text {
      color: var(--artdeco-gold-primary);
      font-family: var(--artdeco-font-mono);
      font-weight: bold;
    }
  }
}

.artdeco-table {
  width: 100%;
  border-collapse: collapse;
  th {
    padding: 12px;
    text-align: left;
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-display);
    border-bottom: 1px solid var(--artdeco-border-default);
  }
  td {
    padding: 12px;
    font-family: var(--artdeco-font-mono);
    border-bottom: 1px solid var(--artdeco-gold-opacity-10);
  }
  .rise {
    color: var(--artdeco-rise);
  }
  .down {
    color: var(--artdeco-down);
  }
}
</style>
