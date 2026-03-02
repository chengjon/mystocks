<template>
  <div class="watchlist-manager">
    <div class="overview-grid">
      <ArtDecoStatCard label="组合数量" :value="watchlists.length" variant="gold" />
      <ArtDecoStatCard label="当前股票数" :value="stocksCount" variant="gold" />
      <ArtDecoStatCard label="上涨家数" :value="upCount" variant="rise" />
      <ArtDecoStatCard label="下跌家数" :value="downCount" variant="fall" />
    </div>

    <div class="watchlist-header">
      <div class="watchlist-tabs">
        <button
          v-for="list in watchlists"
          :key="list.id"
          class="watchlist-tab"
          :class="{ active: activeWatchlistId === list.id }"
          @click="emit('select-list', list.id)"
        >
          {{ list.name }}
          <span class="count">{{ list.stocks.length }}</span>
        </button>
        <button class="add-list-btn" @click="emit('add-list')">+</button>
      </div>
      <div class="actions">
        <ArtDecoButton variant="outline" size="sm" @click="emit('import')">导入</ArtDecoButton>
        <ArtDecoButton variant="outline" size="sm" @click="emit('export')">导出</ArtDecoButton>
      </div>
    </div>

    <ArtDecoCard title="组合持仓明细" hoverable>
      <ArtDecoTable :columns="columns" :data="currentStocks">
        <template #action="{ row }">
          <ArtDecoButton variant="outline" size="sm" @click="emit('remove-stock', row)">删除</ArtDecoButton>
        </template>
      </ArtDecoTable>
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArtDecoButton, ArtDecoCard, ArtDecoStatCard, ArtDecoTable } from '@/components/artdeco'

interface StockRow {
  [key: string]: unknown
  change?: number | string
}

interface WatchlistItem {
  id: string
  name: string
  stocks: unknown[]
}

interface Props {
  watchlists: WatchlistItem[]
  activeWatchlistId: string
  currentStocks: StockRow[]
}

const props = withDefaults(defineProps<Props>(), {
  watchlists: () => [],
  activeWatchlistId: '',
  currentStocks: () => []
})
const emit = defineEmits(['select-list', 'add-list', 'import', 'export', 'remove-stock'])

const numericChanges = computed(() => props.currentStocks.map((row) => {
  const value = row.change
  if (typeof value === 'number') return value
  if (typeof value === 'string') return Number(value.replace('%', ''))
  return 0
}))

const stocksCount = computed(() => props.currentStocks.length)
const upCount = computed(() => numericChanges.value.filter((v) => v > 0).length)
const downCount = computed(() => numericChanges.value.filter((v) => v < 0).length)

const columns = [
  { key: 'symbol', label: '代码', width: '100px' },
  { key: 'name', label: '名称' },
  { key: 'price', label: '现价', align: 'right' },
  { key: 'change', label: '涨跌幅', variant: 'color', align: 'right' },
  { key: 'volume', label: '成交量', align: 'right' },
  { key: 'action', label: '操作', width: '90px' }
]
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.watchlist-manager {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-4);
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}

.watchlist-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.watchlist-tabs {
  display: flex;
  gap: var(--artdeco-spacing-2);
}

.watchlist-tab {
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-default);
  color: var(--artdeco-fg-muted);
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
  cursor: pointer;

  &.active {
    border-color: var(--artdeco-gold-primary);
    color: var(--artdeco-gold-primary);
    background: var(--artdeco-gold-opacity-10);
  }

  .count {
    margin-left: 8px;
    font-size: 12px;
    opacity: 60%;
  }
}

.add-list-btn {
  @extend .watchlist-tab;

  width: 40px;
  padding: 8px 0;
}

.actions {
  display: flex;
  gap: var(--artdeco-spacing-2);
}
</style>
