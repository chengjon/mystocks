<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi';
import { dataApi } from '@/api/index';
import type { StockListResponse } from '@/api/types/common';

const { loading, lastRequestId, exec } = useArtDecoApi();
const scannerResults = ref<any[]>([]);

const fetchScannerData = async () => {
  // 获取基础股票列表作为扫描展示（实际生产中会调用专门的筛选接口）
  const response = await exec(() => dataApi.getStocksBasic({ limit: 20 }), {
    silent: true
  });

  const items = (response as Record<string, unknown>)?.data as unknown[] | undefined;
  if (response && items) {
    // 模拟添加一些技术指标评分数据
    scannerResults.value = items.map((stock: unknown) => ({
      ...(stock as Record<string, unknown>),
      rsi: (Math.random() * 40 + 30).toFixed(2),
      macd_signal: Math.random() > 0.5 ? 'BULL' : 'BEAR',
      trend_score: (Math.random() * 10).toFixed(1)
    }));
  }
};

onMounted(() => {
  fetchScannerData();
});
</script>

<template>
  <div class="technical-scanner-tab page-enter">
    <div class="artdeco-header-bar">
      <h2 class="section-title">Technical Scanner</h2>
      <div class="trace-info" v-if="lastRequestId">ID: {{ lastRequestId }}</div>
    </div>

    <div class="scanner-grid" v-loading="loading">
      <div v-for="stock in scannerResults" :key="stock.symbol" class="artdeco-card stock-scan-card">
        <div class="stock-header">
          <span class="symbol">{{ stock.symbol }}</span>
          <span class="name">{{ stock.name }}</span>
        </div>
        
        <div class="indicators">
          <div class="indicator">
            <span class="label">RSI(14)</span>
            <span :class="['value', parseFloat(stock.rsi) > 70 ? 'overbought' : (parseFloat(stock.rsi) < 30 ? 'oversold' : '')]">
              {{ stock.rsi }}
            </span>
          </div>
          <div class="indicator">
            <span class="label">MACD</span>
            <span :class="['value', stock.macd_signal === 'BULL' ? 'rise' : 'down']">
              {{ stock.macd_signal }}
            </span>
          </div>
        </div>

        <div class="trend-gauge">
          <div class="gauge-label">Trend Strength</div>
          <div class="gauge-bar">
            <div class="gauge-fill" :style="{ width: `${stock.trend_score * 10}%`, background: stock.macd_signal === 'BULL' ? 'var(--artdeco-rise)' : 'var(--artdeco-down)' }"></div>
          </div>
          <div class="gauge-value">{{ stock.trend_score }}/10</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.technical-scanner-tab {
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
  }
  
  .trace-info {
    font-family: var(--font-mono);
    font-size: var(--artdeco-text-xs);
    color: var(--artdeco-fg-muted);
  }
}

.scanner-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--artdeco-spacing-6);
}

.stock-scan-card {
  padding: var(--artdeco-spacing-4);
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-default);
  @include artdeco-hover-lift-glow;

  .stock-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--artdeco-spacing-4);
    border-bottom: 1px solid rgb(212 175 55 / 20%);
    padding-bottom: var(--artdeco-spacing-2);

    .symbol { font-family: var(--font-mono); font-weight: bold; color: var(--artdeco-gold-primary); }
    .name { font-size: var(--artdeco-text-sm); }
  }
}

.indicators {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
  margin-bottom: var(--artdeco-spacing-4);

  .indicator {
    display: flex;
    justify-content: space-between;
    font-size: var(--artdeco-text-xs);
    
    .label { color: var(--artdeco-fg-muted); }
    .value {
      font-family: var(--font-mono);
      &.overbought { color: var(--artdeco-rise); }
      &.oversold { color: var(--artdeco-down); }
      &.rise { color: var(--artdeco-rise); }
      &.down { color: var(--artdeco-down); }
    }
  }
}

.trend-gauge {
  .gauge-label { font-size: 10px; color: var(--artdeco-fg-muted); text-transform: uppercase; margin-bottom: 4px; }
  .gauge-bar {
    height: 4px;
    background: var(--artdeco-bg-elevated);
    margin-bottom: 4px;
    .gauge-fill { height: 100%; transition: width 0.5s ease; }
  }
  .gauge-value { font-family: var(--font-mono); font-size: 10px; text-align: right; }
}
</style>
