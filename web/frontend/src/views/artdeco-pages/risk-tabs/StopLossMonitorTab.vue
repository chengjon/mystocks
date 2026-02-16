<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi';
import { apiClient } from '@/api/apiClient';

const { loading, lastRequestId, exec } = useArtDecoApi();
const stopLossItems = ref<any[]>([]);

const fetchStopLossData = async () => {
  const data = await exec(() => apiClient.get('/v1/monitoring/watchlists'), {
    silent: true
  });
  
  if (data && data.items) {
    stopLossItems.value = data.items.map((item: any) => ({
      ...item,
      current_price: (Math.random() * 100 + 10).toFixed(2),
      stop_price: (Math.random() * 100 + 5).toFixed(2),
      distance: (Math.random() * 5).toFixed(2)
    }));
  } else {
    stopLossItems.value = [
      { symbol: '600036', name: '招商银行', current_price: 35.20, stop_price: 33.50, distance: 4.8 },
      { symbol: '601318', name: '中国平安', current_price: 48.15, stop_price: 47.50, distance: 1.3 },
      { symbol: '000651', name: '格力电器', current_price: 42.05, stop_price: 42.50, distance: -1.0 }
    ];
  }
};

onMounted(() => {
  fetchStopLossData();
});
</script>

<template>
  <div class="stop-loss-monitor-tab page-enter">
    <div class="artdeco-header-bar">
      <h2 class="section-title">Stop-Loss Monitoring</h2>
      <div class="trace-id" v-if="lastRequestId">REQ: {{ lastRequestId }}</div>
    </div>

    <div class="monitor-grid" v-loading="loading">
      <div v-for="item in stopLossItems" :key="item.symbol" class="artdeco-card risk-card">
        <div class="risk-level-bar" :style="{ background: parseFloat(item.distance) < 2 ? 'var(--artdeco-rise)' : 'var(--artdeco-gold-dim)' }"></div>
        
        <div class="card-body">
          <div class="stock-id">
            <span class="symbol">{{ item.symbol }}</span>
            <span class="name">{{ item.name }}</span>
          </div>

          <div class="price-compare">
            <div class="price-box">
              <label>CURRENT</label>
              <div class="val">{{ item.current_price }}</div>
            </div>
            <div class="divider">VS</div>
            <div class="price-box">
              <label>STOP LOSS</label>
              <div class="val gold">{{ item.stop_price }}</div>
            </div>
          </div>

          <div class="risk-status">
            <div class="distance-label">Distance to Stop</div>
            <div :class="['distance-val', parseFloat(item.distance) < 2 ? 'critical' : '']">
              {{ item.distance }}%
            </div>
          </div>
        </div>

        <div class="warning-overlay" v-if="parseFloat(item.distance) < 0">
          <span>TRIGGERED</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.stop-loss-monitor-tab {
  padding: var(--artdeco-spacing-6);
}

.artdeco-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-8);
  border-bottom: 2px solid var(--artdeco-gold-primary);
  padding-bottom: var(--artdeco-spacing-2);

  .section-title { font-size: var(--artdeco-text-2xl); color: var(--artdeco-gold-primary); text-transform: uppercase; }
}

.monitor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--artdeco-spacing-6);
}

.risk-card {
  position: relative;
  background: var(--artdeco-bg-card);
  padding: 0;
  overflow: hidden;
  border: 1px solid var(--artdeco-border-default);
  @include artdeco-hover-lift-glow;

  .risk-level-bar { height: 4px; width: 100%; }

  .card-body { padding: var(--artdeco-spacing-5); }

  .stock-id {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--artdeco-spacing-5);
    .symbol { font-family: var(--font-mono); font-weight: bold; color: var(--artdeco-gold-primary); }
    .name { font-family: var(--font-display); }
  }
}

.price-compare {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-6);
  background: var(--artdeco-bg-elevated);
  padding: var(--artdeco-spacing-3);
  
  .price-box {
    text-align: center;
    label { font-size: 10px; color: var(--artdeco-fg-muted); display: block; }
    .val { font-family: var(--font-mono); font-size: var(--artdeco-text-lg); font-weight: bold; }
    .val.gold { color: var(--artdeco-gold-primary); }
  }
  .divider { font-family: var(--font-display); color: var(--artdeco-gold-dim); font-size: 12px; }
}

.risk-status {
  text-align: right;
  .distance-label { font-size: 10px; color: var(--artdeco-fg-muted); }
  .distance-val {
    font-family: var(--font-mono);
    font-size: var(--artdeco-text-2xl);
    &.critical { color: var(--artdeco-rise); text-shadow: 0 0 10px var(--artdeco-rise); }
  }
}

.warning-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255, 82, 82, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  span {
    background: var(--artdeco-rise);
    color: white;
    padding: 4px 12px;
    font-weight: bold;
    font-family: var(--font-display);
    transform: rotate(-15deg);
    box-shadow: 0 0 20px rgba(0,0,0,0.5);
  }
}
</style>
