<template>
  <div class="signals-view">
    <div class="view-header">
      <h3>交易信号监控中心</h3>
      <div class="header-actions">
        <span class="signals-count">当前 {{ filteredSignals.length }} 条信号</span>
      </div>
    </div>

    <ArtDecoSignalMonitoringOverview :metrics="overviewMetrics" />

    <ArtDecoTradingSignalsControls
      :signal-filters="signalFilters"
      v-model:activeSignalFilter="activeSignalFilter"
      @export-csv="exportSignals"
      @batch-execute="batchExecute"
    />

    <div class="signals-list-section">
      <ArtDecoTradingSignals :signals="filteredSignals" />
    </div>

    <ArtDecoSignalMonitoringMetrics :quality="qualityMetrics" :types="signalTypes" />

    <div class="execution-history-section">
      <ArtDecoSignalHistory :history="historySignals" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import ArtDecoTradingSignals from './ArtDecoTradingSignals.vue'
import ArtDecoSignalMonitoringOverview from '../components/ArtDecoSignalMonitoringOverview.vue'
import ArtDecoTradingSignalsControls from '../components/ArtDecoTradingSignalsControls.vue'
import ArtDecoSignalMonitoringMetrics from '../components/ArtDecoSignalMonitoringMetrics.vue'
import ArtDecoSignalHistory from '../components/ArtDecoSignalHistory.vue'

const activeSignalFilter = ref('all')

const signalFilters = [
  { key: 'all', label: '全部' },
  { key: 'buy', label: '买入' },
  { key: 'sell', label: '卖出' },
  { key: 'high', label: '高置信度' }
]

const signals = ref([
  { id: 1001, selected: false, time: '09:42:18', symbol: '600519', symbolName: '贵州茅台', type: 'buy', typeText: '买入', strength: 5, price: 1688.3, reason: '量价齐升+突破前高', confidence: 91 },
  { id: 1002, selected: false, time: '09:47:52', symbol: '300750', symbolName: '宁德时代', type: 'sell', typeText: '卖出', strength: 4, price: 197.6, reason: '短期顶背离', confidence: 82 },
  { id: 1003, selected: false, time: '10:03:09', symbol: '601318', symbolName: '中国平安', type: 'buy', typeText: '买入', strength: 3, price: 46.21, reason: '趋势回踩确认', confidence: 73 }
])

const historySignals = ref([
  { id: 1, time: '2026-02-28 09:15', type: 'buy', typeText: '买入', symbol: '600036', strength: 4, outcome: 'win', outcomeText: '盈利', pnl: 2680 },
  { id: 2, time: '2026-02-27 14:22', type: 'sell', typeText: '卖出', symbol: '000001', strength: 3, outcome: 'loss', outcomeText: '亏损', pnl: -940 },
  { id: 3, time: '2026-02-27 10:11', type: 'buy', typeText: '买入', symbol: '002594', strength: 5, outcome: 'win', outcomeText: '盈利', pnl: 4120 }
])

const overviewMetrics = {
  accuracy: 74.6,
  responseTime: 138,
  coverage: 86.4,
  qualityScore: 8.2
}

const qualityMetrics = {
  wins: 42,
  losses: 18,
  avgProfit: 1320,
  avgLoss: 640,
  profitLossRatio: '2.06',
  maxWinStreak: 7,
  maxLossStreak: 3
}

const signalTypes = [
  { name: '趋势突破', description: '顺势突破型信号', count: 28, accuracy: 76 },
  { name: '均值回归', description: '超跌反弹型信号', count: 17, accuracy: 69 },
  { name: '资金异动', description: '主力资金异常流入', count: 15, accuracy: 81 }
]

const filteredSignals = computed(() => {
  if (activeSignalFilter.value === 'all') return signals.value
  if (activeSignalFilter.value === 'high') return signals.value.filter((s) => s.confidence >= 85)
  return signals.value.filter((s) => s.type === activeSignalFilter.value)
})

function exportSignals() {
  // placeholder
}

function batchExecute() {
  // placeholder
}
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.signals-view {
  min-height: 900px;
  padding: var(--artdeco-spacing-4);

  .view-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--artdeco-spacing-6);

    h3 {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-text-xl);
      font-weight: 700;
      margin: 0;
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wider);
      color: var(--artdeco-gold-primary);
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-4);

      .signals-count {
        font-size: var(--artdeco-text-xs);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
      }
    }
  }

  .signals-list-section {
    margin-bottom: var(--artdeco-spacing-6);
  }

  .execution-history-section {
    margin-top: var(--artdeco-spacing-6);
  }
}
</style>
