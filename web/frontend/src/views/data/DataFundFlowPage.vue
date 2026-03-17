<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import { fundFlowPageService, type FundFlowBigDealRow, type FundFlowPageSnapshot, type FundFlowTimeframe } from '@/api/services/fundFlowPageService'
import { ArtDecoCard, ArtDecoSelect } from '@/components/artdeco'
import ArtDecoChart from '@/components/artdeco/charts/ArtDecoChart.vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'

type RankingSortKey = 'bigDealNetInflow' | 'bigDealAmount' | 'bigDealBuyAmount'
type RankingMetricKey = RankingSortKey | 'bigDealSellAmount'

interface TimeFilterOption {
  key: FundFlowTimeframe
  label: string
}

const { loading, error, lastProcessTime, lastRequestId, exec } = useArtDecoApi()

const timeFilters: TimeFilterOption[] = [
  { key: 'today', label: '今日' },
  { key: '3day', label: '3日' },
  { key: '5day', label: '5日' },
  { key: '10day', label: '10日' }
]

const rankingOptions = [
  { label: '净流入额', value: 'bigDealNetInflow' },
  { label: '成交额', value: 'bigDealAmount' },
  { label: '买入额', value: 'bigDealBuyAmount' }
]

const activeTimeFilter = ref<FundFlowTimeframe>('today')
const rankingSort = ref<RankingSortKey>('bigDealNetInflow')
const snapshot = ref<FundFlowPageSnapshot>({
  timeframe: 'today',
  summaryRows: [],
  rankingRows: []
})

const displayProcessTime = computed(() => {
  if (!lastProcessTime.value) {
    return 'N/A'
  }

  return lastProcessTime.value
})

const timeframeLabel = computed(() => {
  return timeFilters.find((filter) => filter.key === activeTimeFilter.value)?.label ?? '今日'
})

const summary = computed(() => {
  const northNet = snapshot.value.summaryRows.reduce((sum, row) => sum + row.northMoney, 0)
  const southNet = snapshot.value.summaryRows.reduce((sum, row) => sum + row.southMoney, 0)
  const totalBigDealAmount = snapshot.value.rankingRows.reduce((sum, row) => sum + row.bigDealAmount, 0)
  const totalBigDealNetInflow = snapshot.value.rankingRows.reduce((sum, row) => sum + row.bigDealNetInflow, 0)

  return {
    northNet,
    southNet,
    totalBigDealAmount,
    totalBigDealNetInflow
  }
})

const sortedRanking = computed(() => {
  return snapshot.value.rankingRows
    .slice()
    .sort((left, right) => right[rankingSort.value] - left[rankingSort.value])
    .slice(0, 20)
})

const trendChartOption = computed(() => {
  if (snapshot.value.summaryRows.length === 0) {
    return {}
  }

  return {
    tooltip: { trigger: 'axis' },
    legend: {
      data: ['北向资金', '南向资金'],
      textStyle: { color: 'var(--artdeco-fg-muted)' }
    },
    xAxis: {
      type: 'category',
      data: snapshot.value.summaryRows.map((row) => row.date)
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: '北向资金',
        type: 'line',
        smooth: true,
        data: snapshot.value.summaryRows.map((row) => row.northMoney),
        lineStyle: { color: 'var(--artdeco-gold-primary)' },
        itemStyle: { color: 'var(--artdeco-gold-primary)' }
      },
      {
        name: '南向资金',
        type: 'line',
        smooth: true,
        data: snapshot.value.summaryRows.map((row) => row.southMoney),
        lineStyle: { color: 'var(--artdeco-rise)' },
        itemStyle: { color: 'var(--artdeco-rise)' }
      }
    ]
  }
})

const isEmpty = computed(() => {
  return snapshot.value.summaryRows.length === 0 && snapshot.value.rankingRows.length === 0
})

function formatAmount(value: number): string {
  const absoluteValue = Math.abs(value)

  if (absoluteValue >= 100000000) {
    return `${(value / 100000000).toFixed(2)}亿`
  }

  return `${(value / 10000).toFixed(2)}万`
}

function rankingValue(row: FundFlowBigDealRow, key: RankingMetricKey): string {
  return formatAmount(row[key])
}

async function fetchSnapshot(): Promise<void> {
  const data = await exec(
    () =>
      fundFlowPageService.getFundFlowPageSnapshot({
        timeframe: activeTimeFilter.value
      }),
    {
      silent: true,
      errorMsg: '资金流向数据加载失败'
    }
  )

  snapshot.value = data ?? {
    timeframe: activeTimeFilter.value,
    summaryRows: [],
    rankingRows: []
  }
}

function handleTimeFilterChange(timeframe: FundFlowTimeframe): void {
  activeTimeFilter.value = timeframe
}

function handleRankingSortChange(value: string): void {
  if (value === 'bigDealNetInflow' || value === 'bigDealAmount' || value === 'bigDealBuyAmount') {
    rankingSort.value = value
  }
}

watch(activeTimeFilter, () => {
  void fetchSnapshot()
})

onMounted(() => {
  void fetchSnapshot()
})
</script>

<template>
  <div class="data-fund-flow-page page-enter">
    <div class="artdeco-header-bar">
      <h2 class="section-title">Capital Flow Monitor</h2>
      <div class="header-meta">
        <span>DATA: REAL</span>
        <span>REQ: {{ lastRequestId || 'N/A' }}</span>
        <span>TIME: {{ displayProcessTime }}</span>
        <span>RANGE: {{ timeframeLabel }}</span>
      </div>
    </div>

    <div class="fund-flow-toolbar artdeco-card">
      <div class="time-filters">
        <button
          v-for="filter in timeFilters"
          :key="filter.key"
          class="filter-btn"
          :class="{ active: activeTimeFilter === filter.key }"
          @click="handleTimeFilterChange(filter.key)"
        >
          {{ filter.label }}
        </button>
      </div>

      <ArtDecoSelect
        :model-value="rankingSort"
        :options="rankingOptions"
        class="ranking-select"
        placeholder="选择排序方式"
        @update:model-value="handleRankingSortChange"
      />
    </div>

    <div class="stats-grid artdeco-card">
      <div class="stat-item">
        <span class="stat-label">北向净流入</span>
        <strong class="stat-value gold">{{ formatAmount(summary.northNet) }}</strong>
      </div>
      <div class="stat-item">
        <span class="stat-label">南向净流入</span>
        <strong class="stat-value rise">{{ formatAmount(summary.southNet) }}</strong>
      </div>
      <div class="stat-item">
        <span class="stat-label">大单成交额</span>
        <strong class="stat-value">{{ formatAmount(summary.totalBigDealAmount) }}</strong>
      </div>
      <div class="stat-item">
        <span class="stat-label">大单净流入</span>
        <strong class="stat-value gold">{{ formatAmount(summary.totalBigDealNetInflow) }}</strong>
      </div>
    </div>

    <div v-if="isEmpty" class="fund-flow-empty artdeco-card" v-loading="loading">
      <p v-if="error" class="empty-error">{{ error }}</p>
      <p class="empty-title">暂无资金流向数据</p>
      <p class="empty-hint">当前页面只展示真实生产链路返回的数据，不再使用本地 mock / fallback 伪成功。</p>
    </div>

    <div v-else class="fund-flow-layout">
      <ArtDecoCard title="北向 / 南向资金趋势" hoverable class="fund-chart-card" v-loading="loading">
        <ArtDecoChart :option="trendChartOption" height="320px" />
      </ArtDecoCard>

      <ArtDecoCard title="大单成交排行" hoverable class="fund-table-card" v-loading="loading">
        <div class="table-shell">
          <table class="artdeco-table">
            <thead>
              <tr>
                <th>RANK</th>
                <th>NAME</th>
                <th>SYMBOL</th>
                <th>成交额</th>
                <th>买入额</th>
                <th>卖出额</th>
                <th>净流入</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in sortedRanking" :key="`${row.symbol}-${index}`">
                <td class="rank">{{ index + 1 }}</td>
                <td class="name">{{ row.name }}</td>
                <td>{{ row.symbol }}</td>
                <td>{{ rankingValue(row, 'bigDealAmount') }}</td>
                <td>{{ rankingValue(row, 'bigDealBuyAmount') }}</td>
                <td>{{ rankingValue(row, 'bigDealSellAmount') }}</td>
                <td :class="['net-flow', row.bigDealNetInflow >= 0 ? 'rise' : 'down']">
                  {{ rankingValue(row, 'bigDealNetInflow') }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </ArtDecoCard>
    </div>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.data-fund-flow-page {
  padding: var(--artdeco-spacing-6);
}

.artdeco-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: var(--artdeco-spacing-8);
  border-bottom: 2px solid var(--artdeco-gold-primary);
  padding-bottom: var(--artdeco-spacing-2);

  .section-title {
    margin: 0;
    font-size: var(--artdeco-text-2xl);
    color: var(--artdeco-gold-primary);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
  }
}

.header-meta {
  display: flex;
  gap: var(--artdeco-spacing-3);
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
}

.fund-flow-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-4);
  padding: var(--artdeco-spacing-4);
}

.time-filters {
  display: flex;
  gap: var(--artdeco-spacing-2);
}

.filter-btn {
  background: transparent;
  border: 1px solid var(--artdeco-border-default);
  color: var(--artdeco-fg-muted);
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
  cursor: pointer;
  transition: all var(--artdeco-duration-base);

  &.active {
    border-color: var(--artdeco-gold-primary);
    color: var(--artdeco-gold-primary);
    background: var(--artdeco-gold-opacity-10);
  }
}

.ranking-select {
  width: 220px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-4);
  padding: var(--artdeco-spacing-4);
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.stat-label {
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-xs);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
}

.stat-value {
  color: var(--artdeco-fg-primary);
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xl);
}

.stat-value.gold {
  color: var(--artdeco-gold-primary);
}

.stat-value.rise {
  color: var(--artdeco-rise);
}

.fund-flow-empty {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-5);
}

.empty-error {
  margin: 0;
  color: var(--artdeco-down);
  font-family: var(--artdeco-font-mono);
}

.empty-title {
  margin: 0;
  color: var(--artdeco-gold-light);
  font-size: var(--artdeco-text-lg);
}

.empty-hint {
  margin: 0;
  color: var(--artdeco-fg-muted);
}

.fund-flow-layout {
  display: grid;
  gap: var(--artdeco-spacing-4);
}

.table-shell {
  overflow-x: auto;
}

.artdeco-table {
  width: 100%;
  border-collapse: collapse;

  th {
    padding: var(--artdeco-spacing-4);
    text-align: left;
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-display);
    font-size: var(--artdeco-text-sm);
    border-bottom: 1px solid var(--artdeco-border-default);
  }

  td {
    padding: var(--artdeco-spacing-4);
    color: var(--artdeco-fg-primary);
    border-bottom: 1px solid var(--artdeco-gold-opacity-10);
    font-family: var(--artdeco-font-mono);
  }
}

.rank {
  color: var(--artdeco-gold-primary);
}

.name {
  color: var(--artdeco-gold-light);
  font-family: var(--artdeco-font-body);
  font-weight: bold;
}

.net-flow.rise {
  color: var(--artdeco-rise);
}

.net-flow.down {
  color: var(--artdeco-down);
}

@media (max-width: 1024px) {
  .artdeco-header-bar,
  .fund-flow-toolbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-meta {
    flex-wrap: wrap;
  }

  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .data-fund-flow-page {
    padding: var(--artdeco-spacing-4);
  }

  .time-filters {
    flex-wrap: wrap;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .ranking-select {
    width: 100%;
  }
}
</style>
