<template>
  <div class="watchlist-manager">
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

    <ArtDecoTable :columns="columns" :data="currentStocks">
      <template #action="{ row }">
        <ArtDecoButton variant="outline" size="xs" @click="emit('remove-stock', row)">删除</ArtDecoButton>
      </template>
    </ArtDecoTable>
  </div>
</template>

<script setup lang="ts">
import { ArtDecoButton, ArtDecoTable } from '@/components/artdeco'

interface Props {
  watchlists: any[]
  activeWatchlistId: string
  currentStocks: any[]
}

defineProps<Props>()
const emit = defineEmits(['select-list', 'add-list', 'import', 'export', 'remove-stock'])

const columns = [
  { key: 'symbol', label: '代码', width: '100px' },
  { key: 'name', label: '名称' },
  { key: 'price', label: '现价', align: 'right' },
  { key: 'change', label: '涨跌幅', variant: 'color', align: 'right' },
  { key: 'action', label: '操作', width: '80px' }
]
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.watchlist-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-4);
}

.watchlist-tabs {
  display: flex;
  gap: var(--artdeco-spacing-2);
}

.watchlist-tab {
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-gold-subtle);
  color: var(--artdeco-fg-muted);
  padding: 8px 16px;
  cursor: pointer;
  
  &.active {
    border-color: var(--artdeco-accent-gold);
    color: var(--artdeco-accent-gold);
  }

  .count {
    margin-left: 8px;
    font-size: 12px;
    opacity: 0.6;
  }
}

.add-list-btn {
  @extend .watchlist-tab;
  width: 40px;
  padding: 8px 0;
}
</style>
