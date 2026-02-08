<template>
  <div class="lhb-analysis">
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
            v-for="f in filters" 
            :key="f.key"
            class="filter-btn" 
            :class="{ active: activeFilter === f.key }"
            @click="emit('filter-change', f.key)"
          >
            {{ f.label }}
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
  lhbData: any[]
  lhbDate: string
  activeFilter: string
}

defineProps<Props>()
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
@import '@/styles/artdeco-tokens.scss';

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
</style>
