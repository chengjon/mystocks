<template>
  <div class="lhb-analysis-page">
    <div class="page-header">
      <h2 class="section-title">龙虎榜分析</h2>
      <div class="trace-info">API STATUS: PENDING</div>
    </div>

    <div class="pending-state artdeco-card">
      <p>API 真值待复核</p>
      <span>当前保留页面壳层、日期筛选器和表格骨架；待后端路由口径确认后再接入真实数据。</span>
    </div>

    <ArtDecoCard title="龙虎榜数据" hoverable class="lhb-card">
      <div class="lhb-controls">
        <ArtDecoSelect
          :model-value="lhbDate"
          :options="dateOptions"
          placeholder="选择日期"
          @update:model-value="emit('date-change', $event)"
        />
        <div class="lhb-filters">
          <button
            v-for="filter in filters"
            :key="filter.key"
            class="filter-btn"
            :class="{ active: activeFilter === filter.key }"
            @click="emit('filter-change', filter.key)"
          >
            {{ filter.label }}
          </button>
        </div>
      </div>

      <ArtDecoTable :columns="columns" :data="lhbData" />
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { ArtDecoCard, ArtDecoSelect, ArtDecoTable } from '@/components/artdeco'

interface Props {
  lhbData: unknown[]
  lhbDate: string
  activeFilter: string
}

withDefaults(defineProps<Props>(), {
  lhbData: () => [],
  lhbDate: 'today',
  activeFilter: 'buy'
})

const emit = defineEmits(['date-change', 'filter-change'])

const dateOptions = [
  { label: '今日', value: 'today' },
  { label: '昨日', value: 'yesterday' },
  { label: '前日', value: 'dayBefore' }
]

const filters = [
  { key: 'buy', label: '买入榜' },
  { key: 'sell', label: '卖出榜' },
  { key: 'institution', label: '机构榜' }
]

const columns = [
  { key: 'rank', label: '排名', width: '60px' },
  { key: 'name', label: '股票信息' },
  { key: 'price', label: '收盘价', align: 'right' },
  { key: 'change', label: '涨跌幅', variant: 'color', align: 'right' },
  { key: 'buyAmount', label: '买入金额', align: 'right' },
  { key: 'sellAmount', label: '卖出金额', align: 'right' },
  { key: 'netBuy', label: '净买入', variant: 'color', align: 'right' }
]
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.lhb-analysis-page {
  display: grid;
  gap: var(--artdeco-spacing-4);
  padding: var(--artdeco-spacing-6);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: calc(var(--artdeco-spacing-1) / 2) solid var(--artdeco-gold-primary);
  padding-bottom: var(--artdeco-spacing-2);
}

.section-title {
  margin: 0;
  color: var(--artdeco-gold-primary);
  font-size: var(--artdeco-text-2xl);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
}

.trace-info {
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
}

.pending-state {
  display: grid;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-5);
  border: thin solid var(--artdeco-border-default);
  background: linear-gradient(145deg, var(--artdeco-gold-opacity-05), transparent 65%);

  p {
    margin: 0;
    color: var(--artdeco-fg-primary);
    font-family: var(--font-display);
    letter-spacing: var(--artdeco-tracking-wide);
  }

  span {
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-sm);
  }
}

.lhb-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-4);
}

.lhb-filters {
  display: flex;
  gap: var(--artdeco-spacing-2);
}

.filter-btn {
  background: transparent;
  border: thin solid var(--artdeco-border-default);
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
</style>
