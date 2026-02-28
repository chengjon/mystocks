<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi';
import { apiClient } from '@/api/apiClient';

const { loading, lastRequestId, exec } = useArtDecoApi();
const signals = ref<any[]>([]);

const fetchSignals = async () => {
  const data = await exec(() => apiClient.get('/v1/trade/signals', { params: { limit: 10 } }), {
    silent: true
  });
  
  if (data && data.items) {
    signals.value = data.items;
  } else {
    // 模拟信号数据
    signals.value = [
      { symbol: '600519', name: '贵州茅台', type: 'BUY', price: 1720.5, time: '14:25:01', strategy: 'TrendFollow' },
      { symbol: '300750', name: '宁德时代', type: 'SELL', price: 195.2, time: '14:20:15', strategy: 'MeanReversion' },
      { symbol: '000001', name: '平安银行', type: 'BUY', price: 10.45, time: '13:55:42', strategy: 'Alpha_V2' }
    ];
  }
};

onMounted(() => {
  fetchSignals();
});
</script>

<template>
  <div class="strategy-signals-tab page-enter">
    <div class="artdeco-header-bar">
      <h2 class="section-title">Live Strategy Signals</h2>
      <div class="trace-id" v-if="lastRequestId">ID: {{ lastRequestId }}</div>
    </div>

    <div class="signals-timeline" v-loading="loading">
      <div v-for="sig in signals" :key="sig.time" :class="['signal-item', sig.type.toLowerCase()]">
        <div class="signal-marker"></div>
        <div class="signal-content artdeco-card">
          <div class="sig-header">
            <span class="sig-type">{{ sig.type }}</span>
            <span class="sig-time">{{ sig.time }}</span>
          </div>
          <div class="sig-body">
            <div class="stock-info">
              <span class="name">{{ sig.name }}</span>
              <span class="symbol">{{ sig.symbol }}</span>
            </div>
            <div class="price-info">
              <label>PRICE</label>
              <span class="val">{{ sig.price }}</span>
            </div>
            <div class="strategy-info">
              <label>STRATEGY</label>
              <span class="val">{{ sig.strategy }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.strategy-signals-tab {
  padding: var(--artdeco-spacing-6);
}

.artdeco-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-10);
  border-bottom: 2px solid var(--artdeco-gold-primary);
  padding-bottom: var(--artdeco-spacing-2);

  .section-title {
    margin: 0;
    font-size: var(--artdeco-text-2xl);
    color: var(--artdeco-gold-primary);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
  }

  .trace-id {
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-xs);
    color: var(--artdeco-fg-muted);
    letter-spacing: var(--artdeco-tracking-wide);
  }
}

.signals-timeline {
  position: relative;
  padding-left: 30px;
  &::before {
    content: '';
    position: absolute;
    left: 4px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: var(--artdeco-border-default);
  }
}

.signal-item {
  position: relative;
  margin-bottom: var(--artdeco-spacing-6);

  .signal-marker {
    position: absolute;
    left: -30px;
    top: 15px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--artdeco-fg-muted);
    border: 2px solid var(--artdeco-bg-global);
    z-index: 2;
  }

  &.buy .signal-marker {
    background: var(--artdeco-rise);
    box-shadow: 0 0 10px var(--artdeco-rise);
  }
  &.sell .signal-marker {
    background: var(--artdeco-down);
    box-shadow: 0 0 10px var(--artdeco-down);
  }

  .signal-content {
    padding: var(--artdeco-spacing-4);

    @include artdeco-geometric-corners;
    
    .sig-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: var(--artdeco-spacing-3);
      border-bottom: 1px solid var(--artdeco-gold-opacity-10);
      padding-bottom: 4px;
      
      .sig-type {
        font-family: var(--artdeco-font-display);
        font-weight: bold;
      }
      .sig-time {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
      }
    }
  }

  &.buy .sig-type {
    color: var(--artdeco-rise);
  }
  &.sell .sig-type {
    color: var(--artdeco-down);
  }
}

.sig-body {
  display: flex;
  justify-content: space-between;

  .stock-info {
    display: flex;
    flex-direction: column;

    .name {
      font-weight: bold;
      color: var(--artdeco-gold-light);
    }

    .symbol {
      font-family: var(--artdeco-font-mono);
      font-size: 12px;
    }
  }

  label {
    display: block;
    font-size: 10px;
    color: var(--artdeco-fg-muted);
    margin-bottom: 2px;
  }

  .val {
    font-family: var(--artdeco-font-mono);
    font-weight: bold;
  }
}
</style>
