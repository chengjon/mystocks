<template>
  <div class="fund-flow-analysis">
    <div class="fund-overview">
      <ArtDecoStatCard
        label="沪股通净流入"
        :value="fundData.shanghai.amount"
        :change="fundData.shanghai.change"
        change-percent
        variant="gold"
      />
      <ArtDecoStatCard
        label="深股通净流入"
        :value="fundData.shenzhen.amount"
        :change="fundData.shenzhen.change"
        change-percent
        variant="gold"
      />
      <ArtDecoStatCard
        label="北向资金总额"
        :value="fundData.north.amount"
        :change="fundData.north.change"
        change-percent
        :variant="fundData.north.change > 0 ? 'rise' : 'fall'"
      />
      <ArtDecoStatCard
        label="主力净流入"
        :value="fundData.main.amount"
        :change="fundData.main.change"
        change-percent
        variant="gold"
      />
    </div>

    <ArtDecoCard title="近30日资金流向趋势" hoverable class="fund-chart-card">
      <div class="chart-container">
        <ArtDecoChart :option="trendChartOption" height="300px" />
      </div>
    </ArtDecoCard>

    <ArtDecoCard title="个股资金流向排行" hoverable class="fund-ranking-card">
      <div class="ranking-controls">
        <div class="time-filters">
          <button
            v-for="filter in timeFilters"
            :key="filter.key"
            class="filter-btn"
            :class="{ active: activeTimeFilter === filter.key }"
            @click="emit('filter-change', filter.key)"
          >
            {{ filter.label }}
          </button>
        </div>
        <ArtDecoSelect
          :model-value="rankingType"
          :options="rankingOptions"
          placeholder="选择排序方式"
          class="ranking-select"
          @update:model-value="emit('ranking-change', $event)"
        />
      </div>

      <ArtDecoTable :columns="columns" :data="stockRanking" />
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArtDecoStatCard, ArtDecoCard, ArtDecoSelect, ArtDecoTable } from '@/components/artdeco'
import ArtDecoChart from '@/components/artdeco/charts/ArtDecoChart.vue'

interface Props {
  fundData: any
  stockRanking: any[]
  trendData: any[]
  activeTimeFilter: string
  rankingType: string
}

const props = defineProps<Props>()
const emit = defineEmits(['filter-change', 'ranking-change'])

const timeFilters = [
  { key: 'today', label: '今日' },
  { key: '3day', label: '3日' },
  { key: '5day', label: '5日' },
  { key: '10day', label: '10日' }
]

const rankingOptions = [
  { label: '主力流入额', value: 'main_force' },
  { label: '超大单流入', value: 'huge_order' },
  { label: '净流入比例', value: 'ratio' }
]

const columns = [
  { key: 'rank', label: '排名', width: '80px' },
  { key: 'name', label: '股票名称' },
  { key: 'code', label: '代码' },
  { key: 'price', label: '最新价' },
  { key: 'change', label: '涨跌幅', variant: 'color' },
  { key: 'inflow', label: '资金流入' },
  { key: 'mainForce', label: '主力净额' }
]

const trendChartOption = computed(() => {
  if (!props.trendData || props.trendData.length === 0) return {}
  
  return {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: props.trendData.map((d: any) => d.date) },
    yAxis: { type: 'value' },
    series: [{
      data: props.trendData.map((d: any) => d.value),
      type: 'bar',
      itemStyle: {
        color: (params: any) => params.value >= 0 ? 'var(--artdeco-up)' : 'var(--artdeco-down)'
      }
    }]
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.fund-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-6);
}

.fund-chart-card {
  margin-bottom: var(--artdeco-spacing-6);
}

.ranking-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-4);
}

.time-filters {
  display: flex;
  gap: var(--artdeco-spacing-2);
}

.filter-btn {
  background: transparent;
  border: 1px solid var(--artdeco-border-gold-subtle);
  color: var(--artdeco-fg-muted);
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
  cursor: pointer;
  transition: all var(--artdeco-duration-base);

  &.active {
    border-color: var(--artdeco-accent-gold);
    color: var(--artdeco-accent-gold);
    background: rgba(212, 175, 55, 0.1);
  }
}

.ranking-select {
  width: 200px;
}
</style>
