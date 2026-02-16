<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi';
import { apiClient } from '@/api/apiClient';

const { loading, lastRequestId, exec } = useArtDecoApi();
const etfList = ref<any[]>([]);

const fetchETFs = async () => {
  // 获取 ETF 实时数据 (调用 v1 标准接口)
  const data = await exec(() => apiClient.get('/v1/market/etf', { params: { limit: 15 } }), {
    silent: true
  });
  
  if (data && data.items) {
    etfList.value = data.items;
  } else {
    // 降级模拟数据 (仅用于演示，实际生产需后端支持该接口)
    etfList.value = [
      { symbol: '510300', name: '沪深300ETF', price: 3.842, change_pct: 1.25, volume: '4.2B' },
      { symbol: '159915', name: '创业板ETF', price: 2.156, change_pct: -0.85, volume: '2.1B' },
      { symbol: '510050', name: '上证50ETF', price: 2.678, change_pct: 0.42, volume: '1.5B' }
    ];
  }
};

onMounted(() => {
  fetchETFs();
});
</script>

<template>
  <div class="market-etf-tab page-enter">
    <div class="artdeco-header-bar">
      <h2 class="section-title">ETF Market Pulse</h2>
      <div class="trace-info" v-if="lastRequestId">ID: {{ lastRequestId }}</div>
    </div>

    <div class="etf-grid" v-loading="loading">
      <div v-for="etf in etfList" :key="etf.symbol" class="artdeco-card etf-card">
        <div class="card-inner">
          <div class="etf-info">
            <span class="symbol">{{ etf.symbol }}</span>
            <span class="name">{{ etf.name }}</span>
          </div>
          <div class="etf-price-row">
            <span class="price">{{ etf.price?.toFixed(3) }}</span>
            <span :class="['change', etf.change_pct >= 0 ? 'rise' : 'down']">
              {{ etf.change_pct >= 0 ? '+' : '' }}{{ etf.change_pct }}%
            </span>
          </div>
          <div class="etf-volume">
            <label>VOL:</label>
            <span>{{ etf.volume }}</span>
          </div>
        </div>
        <!-- 艺术装饰边角 -->
        <div class="corner-accents"></div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.market-etf-tab {
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
    letter-spacing: 0.1em;
  }
}

.etf-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--artdeco-spacing-6);
}

.etf-card {
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-default);
  position: relative;
  @include artdeco-hover-lift-glow;

  .card-inner {
    padding: var(--artdeco-spacing-4);
    z-index: 1;
    position: relative;
  }

  .etf-info {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--artdeco-spacing-4);
    .symbol { font-family: var(--font-mono); color: var(--artdeco-gold-primary); font-weight: bold; }
    .name { font-size: var(--artdeco-text-sm); color: var(--artdeco-fg-primary); }
  }

  .etf-price-row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: var(--artdeco-spacing-3);
    .price { font-family: var(--font-mono); font-size: var(--artdeco-text-xl); }
    .change { font-family: var(--font-mono); font-size: var(--artdeco-text-md); &.rise { color: var(--artdeco-rise); } &.down { color: var(--artdeco-down); } }
  }

  .etf-volume {
    font-size: 10px;
    color: var(--artdeco-fg-muted);
    font-family: var(--font-mono);
    label { margin-right: 4px; }
  }

  @include artdeco-geometric-corners(var(--artdeco-gold-dim), 12px, 1px);
}
</style>
