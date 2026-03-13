<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi';
import { apiClient } from '@/api/apiClient';

interface StopLossRow {
  symbol: string
  name: string
  current_price: number | string
  stop_price: number | string
  distance: number | string
}

const { loading, error, lastRequestId, exec } = useArtDecoApi();
const stopLossItems = ref<StopLossRow[]>([]);
const showErrorState = computed(() => Boolean(error.value) && stopLossItems.value.length === 0)
const showEmptyState = computed(() => !loading.value && !error.value && stopLossItems.value.length === 0)

function toFiniteNumber(value: unknown): number | null {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === 'string') {
    const normalized = Number.parseFloat(value);
    if (Number.isFinite(normalized)) {
      return normalized;
    }
  }
  return null;
}

function calculateDistancePercent(currentPrice: number | null, stopPrice: number | null): number | null {
  if (currentPrice === null || stopPrice === null || stopPrice <= 0) {
    return null;
  }
  return ((currentPrice - stopPrice) / stopPrice) * 100;
}

const fetchStopLossData = async () => {
  const data = await exec(() => apiClient.get('/v1/monitoring/watchlists'), {
    silent: true,
    errorMsg: '止损监控数据加载失败'
  });
  
  const payload = data as { items?: unknown[] } | null
  if (payload?.items) {
    stopLossItems.value = payload.items.map((item: unknown) => {
      const row = item as Partial<StopLossRow>
      const currentPrice = toFiniteNumber((row as Record<string, unknown>).current_price ?? (row as Record<string, unknown>).price);
      const stopPrice = toFiniteNumber(
        (row as Record<string, unknown>).stop_price ??
        (row as Record<string, unknown>).stop_loss_price ??
        (row as Record<string, unknown>).stoploss_price
      );
      const distance = calculateDistancePercent(currentPrice, stopPrice);

      return {
        symbol: String(row.symbol ?? ''),
        name: String(row.name ?? ''),
        current_price: currentPrice !== null ? currentPrice.toFixed(2) : '--',
        stop_price: stopPrice !== null ? stopPrice.toFixed(2) : '--',
        distance: distance !== null ? distance.toFixed(2) : '--'
      }
    });
  } else {
    stopLossItems.value = [];
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

    <div v-if="showErrorState" class="state-panel state-panel--error" role="alert">
      止损监控数据加载失败：{{ error }}
    </div>

    <div v-else-if="showEmptyState" class="state-panel" role="status" aria-live="polite">
      暂无止损监控数据。
    </div>

    <div v-else class="monitor-grid" v-loading="loading">
      <div v-for="item in stopLossItems" :key="item.symbol" class="artdeco-card risk-card">
        <div class="risk-level-bar" :style="{ background: Number(item.distance) < 2 ? 'var(--artdeco-rise)' : 'var(--artdeco-gold-dim)' }"></div>
        
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
            <div :class="['distance-val', Number(item.distance) < 2 ? 'critical' : '']">
              {{ item.distance }}%
            </div>
          </div>
        </div>

        <div class="warning-overlay" v-if="Number(item.distance) < 0">
          <span>TRIGGERED</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

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

  .section-title {
    font-size: var(--artdeco-text-2xl);
    color: var(--artdeco-gold-primary);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
  }
}

.monitor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--artdeco-spacing-6);
}

.state-panel {
  padding: var(--artdeco-spacing-5);
  margin-bottom: var(--artdeco-spacing-6);
  border: thin solid var(--artdeco-border-default);
  background: linear-gradient(145deg, var(--artdeco-gold-opacity-05), transparent 65%);
  color: var(--artdeco-fg-primary);

  &--error {
    color: var(--artdeco-rise);
  }
}

.risk-card {
  position: relative;
  background: var(--artdeco-bg-card);
  padding: 0;
  overflow: hidden;
  border: 1px solid var(--artdeco-border-default);

  @include artdeco-hover-lift-glow;

  .risk-level-bar {
    height: 4px;
    width: 100%;
  }

  .card-body {
    padding: var(--artdeco-spacing-5);
  }

  .stock-id {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--artdeco-spacing-5);
    .symbol {
      font-family: var(--artdeco-font-mono);
      font-weight: bold;
      color: var(--artdeco-gold-primary);
    }
    .name {
      font-family: var(--artdeco-font-display);
    }
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
    label {
      font-size: 10px;
      color: var(--artdeco-fg-muted);
      display: block;
    }
    .val {
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-text-lg);
      font-weight: bold;
    }
    .val.gold {
      color: var(--artdeco-gold-primary);
    }
  }
  .divider {
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-gold-dim);
    font-size: 12px;
  }
}

.risk-status {
  text-align: right;
  .distance-label {
    font-size: 10px;
    color: var(--artdeco-fg-muted);
  }
  .distance-val {
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-2xl);
    &.critical {
      color: var(--artdeco-rise);
      text-shadow: 0 0 10px var(--artdeco-rise);
    }
  }
}

.warning-overlay {
  position: absolute;
  inset: 0 0 0 0;
  background: color-mix(in srgb, var(--artdeco-rise) 20%, transparent);
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  span {
    background: var(--artdeco-rise);
    color: white;
    padding: 4px 12px;
    font-weight: bold;
    font-family: var(--artdeco-font-display);
    transform: rotate(-15deg);
    box-shadow: 0 0 20px color-mix(in srgb, var(--artdeco-bg-global) 50%, transparent);
  }
}
</style>
