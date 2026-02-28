<template>
  <div class="backtest-analysis-page">
    <div class="page-header">
      <h2 class="section-title">策略回测引擎</h2>
      <div class="header-actions">
        <ArtDecoButton variant="outline" size="sm" @click="resetConfig">重置参数</ArtDecoButton>
        <ArtDecoButton variant="solid" size="sm" @click="runBacktest">启动回测</ArtDecoButton>
      </div>
    </div>

    <div class="stats-grid">
      <ArtDecoStatCard label="总回测次数" :value="summary.totalRuns" variant="gold" />
      <ArtDecoStatCard label="策略胜率" :value="`${summary.winRate}%`" variant="rise" />
      <ArtDecoStatCard label="年化收益" :value="`${summary.annualReturn}%`" variant="gold" />
      <ArtDecoStatCard label="最大回撤" :value="`${summary.maxDrawdown}%`" variant="fall" />
    </div>

    <ArtDecoCard title="回测参数配置" hoverable class="config-card">
      <div class="config-grid">
        <div class="field">
          <label>策略模板</label>
          <ArtDecoSelect v-model="config.strategy" :options="strategyOptions" placeholder="选择策略" />
        </div>
        <div class="field">
          <label>回测周期</label>
          <ArtDecoSelect v-model="config.period" :options="periodOptions" placeholder="选择周期" />
        </div>
        <div class="field">
          <label>初始资金</label>
          <ArtDecoInput v-model="config.capital" placeholder="例如 1000000" />
        </div>
        <div class="field">
          <label>对比基准</label>
          <ArtDecoSelect v-model="config.benchmark" :options="benchmarkOptions" placeholder="选择基准" />
        </div>
      </div>
    </ArtDecoCard>

    <div class="results-grid">
      <ArtDecoCard title="绩效曲线摘要" hoverable>
        <div class="curve-list">
          <div v-for="item in curveSummary" :key="item.label" class="curve-item">
            <span class="label">{{ item.label }}</span>
            <span class="value" :class="item.trend">{{ item.value }}</span>
          </div>
        </div>
      </ArtDecoCard>

      <ArtDecoCard title="交易统计" hoverable>
        <ArtDecoTable :columns="tradeColumns" :data="tradeStats" />
      </ArtDecoCard>
    </div>

    <ArtDecoCard title="回测历史记录" hoverable>
      <ArtDecoTable :columns="historyColumns" :data="historyRows" />
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { ArtDecoButton, ArtDecoCard, ArtDecoInput, ArtDecoSelect, ArtDecoStatCard, ArtDecoTable } from '@/components/artdeco'

const summary = reactive({
  totalRuns: 428,
  winRate: 63.4,
  annualReturn: 18.7,
  maxDrawdown: -9.2
})

const config = reactive({
  strategy: 'momentum',
  period: '1y',
  capital: '1000000',
  benchmark: 'csi300'
})

const strategyOptions = [
  { label: '动量轮动策略', value: 'momentum' },
  { label: '均值回归策略', value: 'mean-reversion' },
  { label: '多因子组合策略', value: 'multi-factor' }
]

const periodOptions = [
  { label: '近6个月', value: '6m' },
  { label: '近1年', value: '1y' },
  { label: '近3年', value: '3y' }
]

const benchmarkOptions = [
  { label: '沪深300', value: 'csi300' },
  { label: '中证500', value: 'csi500' },
  { label: '上证指数', value: 'shanghai' }
]

const curveSummary = [
  { label: '累计收益', value: '+34.6%', trend: 'rise' },
  { label: '超额收益', value: '+11.2%', trend: 'rise' },
  { label: '波动率', value: '14.8%', trend: 'neutral' },
  { label: '夏普比率', value: '1.42', trend: 'gold' }
]

const tradeColumns = [
  { key: 'metric', label: '指标' },
  { key: 'value', label: '结果' }
]

const tradeStats = [
  { metric: '总交易次数', value: 186 },
  { metric: '盈利次数', value: 118 },
  { metric: '亏损次数', value: 68 },
  { metric: '平均持仓天数', value: '6.4' }
]

const historyColumns = [
  { key: 'name', label: '任务名称' },
  { key: 'strategy', label: '策略' },
  { key: 'period', label: '周期' },
  { key: 'return', label: '收益率', variant: 'color' },
  { key: 'drawdown', label: '最大回撤', variant: 'color' },
  { key: 'updatedAt', label: '更新时间' }
]

const historyRows = [
  { name: '2026Q1_轮动增强', strategy: '动量轮动', period: '1年', return: '+22.3%', drawdown: '-8.4%', updatedAt: '2026-02-28 09:40' },
  { name: '稳健价值组合', strategy: '多因子', period: '3年', return: '+48.1%', drawdown: '-12.1%', updatedAt: '2026-02-27 20:11' },
  { name: '快速反转试验', strategy: '均值回归', period: '6个月', return: '+9.5%', drawdown: '-5.3%', updatedAt: '2026-02-27 14:06' }
]

function runBacktest() {
  summary.totalRuns += 1
}

function resetConfig() {
  config.strategy = 'momentum'
  config.period = '1y'
  config.capital = '1000000'
  config.benchmark = 'csi300'
}
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.backtest-analysis-page {
  padding: var(--artdeco-spacing-6);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-6);
}

.section-title {
  margin: 0;
  color: var(--artdeco-gold-primary);
}

.header-actions {
  display: flex;
  gap: var(--artdeco-spacing-3);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-6);
}

.config-card {
  margin-bottom: var(--artdeco-spacing-6);
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}

.field {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);

  label {
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-xs);
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }
}

.results-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-6);
}

.curve-list {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-3);
}

.curve-item {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid var(--artdeco-border-default);
  padding-bottom: var(--artdeco-spacing-2);

  .label {
    color: var(--artdeco-fg-muted);
  }

  .value {
    font-family: var(--artdeco-font-mono);
  }

  .value.rise {
    color: var(--artdeco-rise);
  }

  .value.neutral {
    color: var(--artdeco-fg-primary);
  }

  .value.gold {
    color: var(--artdeco-gold-primary);
  }
}
</style>
