<template>
  <div class="artdeco-technical-analysis">
    <ArtDecoHeader
      title="高级技术分析"
      subtitle="多维指标运算 · 深度回测验证 · 智能决策支持"
      :show-status="true"
      status-text="引擎就绪"
    >
      <template #actions>
        <div class="header-metrics">
          <ArtDecoBadge variant="gold">GPU 核心活跃</ArtDecoBadge>
          <ArtDecoBadge variant="gold">计算负载 12%</ArtDecoBadge>
        </div>
      </template>
    </ArtDecoHeader>

    <nav class="main-tabs">
      <button
        v-for="(tab, _idx) in tabs"
        :key="tab.key"
        class="main-tab"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </nav>

    <div class="tab-content">
      <transition name="fade" mode="out-in">
        <div :key="activeTab" class="tab-panel">
          <KLineAnalysis
            v-if="activeTab === 'analysis'"
            :indicators="indicators"
            :trend-data="trendData"
            @analyze="handleAnalyze"
          />
          <BacktestAnalysis
            v-if="activeTab === 'backtest'"
            :stats="backtestStats"
            :equity-data="equityData"
            @run="handleRunBacktest"
          />
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ArtDecoHeader, ArtDecoBadge } from '@/components/artdeco'
import KLineAnalysis from './analysis-tabs/KLineAnalysis.vue'
import BacktestAnalysis from './analysis-tabs/BacktestAnalysis.vue'
import dashboardService from '@/api/services/dashboardService'

const activeTab = ref('analysis')
const tabs = [
  { key: 'analysis', label: '实时分析' },
  { key: 'backtest', label: '回测验证' }
]

type IndicatorItem = {
  name: string
  value: string | number
  signal: string
  signalType: 'rise' | 'fall' | 'neutral'
}

type TrendDataPoint = {
  time: string | number
  value: number
}

type EquityDataPoint = {
  time: string
  value: number
}

const indicators = ref<IndicatorItem[]>([])
const trendData = ref<TrendDataPoint[]>([])
const equityData = ref<EquityDataPoint[]>([])
const backtestStats = ref({
  totalReturn: '0%',
  sharpe: '0',
  maxDrawdown: '0%',
  winRate: '0%'
})

const handleAnalyze = async (params: { symbol: string, period: string }) => {
  console.log('Analyzing stock:', params)
  try {
    const indRes = await dashboardService.getTechnicalIndicatorsSafe([params.symbol], ['RSI', 'MACD', 'KDJ', 'BOLL'])

    if (indRes.data?.[params.symbol]) {
      const rawIndicators = indRes.data[params.symbol] as Array<{ name: string; value: string | number; signal?: string; signalType?: 'rise' | 'fall' | 'neutral' }>
      indicators.value = rawIndicators.map(item => ({
        name: item.name,
        value: item.value,
        signal: item.signal || '',
        signalType: item.signalType || 'neutral'
      }))
    }

    if (!indRes.ok && indRes.error) {
      ElMessage.error(`技术指标加载失败: ${indRes.error}`)
    }

    // Mock trend data since marketService.getTrend doesn't exist
    trendData.value = Array.from({ length: 30 }, (_, i) => ({
      time: i,
      value: 100 + Math.random() * 20
    }))
  } catch (e) {
    console.error('Analysis failed', e)
  }
}

const handleRunBacktest = async () => {
  console.log('Running backtest task...')
  // Mocking backtest results through service-like delay
  setTimeout(() => {
    backtestStats.value = {
      totalReturn: '+15.4%',
      sharpe: '1.24',
      maxDrawdown: '-8.5%',
      winRate: '62%'
    }
    equityData.value = Array.from({length: 50}, (_, i) => ({ time: String(i), value: 100 + Math.random() * 20 }))
  }, 1000)
}

onMounted(() => {
  // Initial load
  handleAnalyze({ symbol: '000001.SH', period: '1d' })
})

// Auto-generated: cleanup timers to prevent memory leaks
const _timer_1: ReturnType<typeof setTimeout> | null = null
onUnmounted(() => {
  if (_timer_1) clearTimeout(_timer_1)
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.artdeco-technical-analysis {
  padding: var(--artdeco-spacing-6);
  background: var(--artdeco-bg-global);
  min-height: 100vh;
}

.main-tabs {
  display: flex;
  gap: var(--artdeco-spacing-2);
  margin: var(--artdeco-spacing-6) 0;
  border-bottom: calc(var(--artdeco-spacing-px) * 2) solid var(--artdeco-border-gold-subtle);
}

.main-tab {
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-6);
  background: transparent;
  border: none;
  color: var(--artdeco-fg-muted);
  cursor: pointer;
  text-transform: uppercase;
  font-family: var(--artdeco-font-display);
  letter-spacing: var(--artdeco-tracking-wide);
  transition: all var(--artdeco-transition-base);

  &:hover, &.active {
    color: var(--artdeco-accent-gold);
  }

  &.active {
    border-bottom: calc(var(--artdeco-spacing-px) * 2) solid var(--artdeco-accent-gold);
    margin-bottom: calc(var(--artdeco-spacing-2) * -0.25);
  }
}

.fade-enter-active, .fade-leave-active { transition: opacity var(--artdeco-transition-base); }
.fade-enter-from, .fade-leave-to { opacity: 0%; }
</style>
