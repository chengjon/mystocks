<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { dataApi } from '@/api/index'
import { ArtDecoAlert, ArtDecoButton } from '@/components/artdeco'

interface KLineRow {
  datetime: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

const { loading, error, lastRequestId, exec } = useArtDecoApi()
const klineData = ref<KLineRow[]>([])
const currentSymbol = ref('000001.SZ')

const normalizeKlineRows = (payload: unknown): KLineRow[] => {
  const rows = Array.isArray(payload)
    ? payload
    : Array.isArray((payload as { data?: unknown[] } | null)?.data)
      ? ((payload as { data: unknown[] }).data)
      : []

  return rows.map((row, index) => {
    const current = row as Record<string, unknown>
    return {
      datetime: String(current.datetime ?? current.date ?? current.time ?? index),
      open: Number(current.open ?? 0),
      high: Number(current.high ?? 0),
      low: Number(current.low ?? 0),
      close: Number(current.close ?? 0),
      volume: Number(current.volume ?? 0)
    }
  })
}

const fetchKLine = async () => {
  const data = await exec(() => dataApi.getKline({
    symbol: currentSymbol.value,
    period: 'daily',
    limit: 100
  }), { silent: true, errorMsg: 'K线接口暂不可用' })

  klineData.value = normalizeKlineRows(data)
}

const showErrorState = computed(() => Boolean(error.value) && klineData.value.length === 0)
const showEmptyState = computed(() => !loading.value && !error.value && klineData.value.length === 0)

onMounted(() => {
  fetchKLine()
})
</script>

<template>
  <div class="market-kline-tab page-enter">
    <div class="artdeco-header-bar">
      <div class="symbol-info">
        <h2 class="section-title">K线分析</h2>
        <span class="active-symbol">{{ currentSymbol }}</span>
      </div>
      <div class="trace-id" v-if="lastRequestId">REQ: {{ lastRequestId }}</div>
    </div>

    <div class="toolbar artdeco-card">
      <div class="toolbar-copy">
        <strong>周期</strong>
        <span>日线 / 最近 100 根</span>
      </div>
      <ArtDecoButton variant="outline" size="sm" @click="fetchKLine">刷新K线</ArtDecoButton>
    </div>

    <div v-if="showErrorState" class="error-state artdeco-card" role="alert">
      <ArtDecoAlert type="error" title="K线接口暂不可用" :message="error || '请稍后重试。'" :dismissible="false" />
    </div>

    <div v-else-if="showEmptyState" class="empty-state artdeco-card" role="status" aria-live="polite">
      <p>暂无 K 线数据</p>
      <span>请确认当前标的和环境后重试。</span>
    </div>

    <template v-else>
      <div class="kline-container artdeco-card" v-loading="loading">
        <div class="chart-placeholder">
          <div class="placeholder-icon">📊</div>
          <p>实时 K 线数据已接入</p>
          <div class="data-summary" v-if="klineData.length > 0">
            Last Price: <span class="gold-text">{{ klineData[klineData.length-1].close }}</span>
            | Data Points: {{ klineData.length }}
          </div>
        </div>
        <div class="ziggurat-corners"></div>
      </div>

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
    </template>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.market-kline-tab {
  padding: var(--artdeco-spacing-6);
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-6);
  border: thin solid var(--artdeco-border-default);
  background: var(--artdeco-gold-opacity-05);
}

.toolbar-copy {
  display: grid;
  gap: var(--artdeco-spacing-1);
  color: var(--artdeco-fg-muted);

  strong {
    color: var(--artdeco-fg-primary);
    font-size: var(--artdeco-text-sm);
    letter-spacing: var(--artdeco-tracking-wide);
  }

  span {
    font-size: var(--artdeco-text-xs);
  }
}

.artdeco-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-8);
  border-bottom: calc(var(--artdeco-spacing-1) / 2) solid var(--artdeco-gold-primary);
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
      padding: var(--artdeco-spacing-1) var(--artdeco-spacing-3);
      font-family: var(--artdeco-font-mono);
      font-weight: bold;
    }
  }
}

.error-state,
.empty-state {
  display: grid;
  gap: var(--artdeco-spacing-3);
  padding: var(--artdeco-spacing-5);
  margin-bottom: var(--artdeco-spacing-6);
  border: thin solid var(--artdeco-border-default);
}

.empty-state {
  color: var(--artdeco-fg-muted);

  p {
    margin: 0;
    color: var(--artdeco-fg-primary);
    font-family: var(--font-display);
    letter-spacing: var(--artdeco-tracking-wide);
  }
}

.kline-container {
  height: 25rem;
  background: var(--artdeco-bg-elevated);
  margin-bottom: var(--artdeco-spacing-8);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  border: thin solid var(--artdeco-border-default);

  @include artdeco-stepped-corners(var(--artdeco-spacing-4));

  .chart-placeholder {
    text-align: center;
    .placeholder-icon {
      font-size: var(--artdeco-text-5xl);
      margin-bottom: var(--artdeco-spacing-4);
      opacity: 50%;
    }
    p {
      font-family: var(--artdeco-font-display);
      color: var(--artdeco-fg-muted);
      letter-spacing: var(--artdeco-tracking-widest);
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
    padding: var(--artdeco-spacing-3);
    text-align: left;
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-display);
    border-bottom: thin solid var(--artdeco-border-default);
  }
  td {
    padding: var(--artdeco-spacing-3);
    font-family: var(--artdeco-font-mono);
    border-bottom: thin solid var(--artdeco-gold-opacity-10);
  }
  .rise {
    color: var(--artdeco-rise);
  }
  .down {
    color: var(--artdeco-down);
  }
}
</style>
