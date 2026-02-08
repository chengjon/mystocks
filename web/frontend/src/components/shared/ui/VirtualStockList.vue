<template>
  <div class="virtual-stock-list">
    <!-- Header -->
    <div class="list-header">
      <div class="col symbol">Symbol</div>
      <div class="col name">Name</div>
      <div class="col price">Price</div>
      <div class="col change">Change</div>
      <div class="col volume">Volume</div>
      <div class="col actions">Actions</div>
    </div>
    
    <!-- Virtual List -->
    <VirtualList
      :items="items"
      :item-height="48"
      :container-height="height"
      class="stock-list-container"
    >
      <template #default="{ item }">
        <div class="stock-row" @click="handleRowClick(item)">
          <div class="col symbol">{{ item.symbol }}</div>
          <div class="col name">{{ item.name }}</div>
          <div class="col price" :class="getPriceColor(item.change)">
            {{ formatPrice(item.price) }}
          </div>
          <div class="col change" :class="getPriceColor(item.change)">
            {{ formatChange(item.change) }}%
          </div>
          <div class="col volume">{{ formatVolume(item.volume) }}</div>
          <div class="col actions">
            <button @click.stop="emit('trade', item)">Trade</button>
          </div>
        </div>
      </template>
    </VirtualList>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'
import VirtualList from '@/components/common/VirtualList.vue'

interface StockItem {
  symbol: string
  name: string
  price: number
  change: number
  volume: number
}

const props = defineProps({
  items: {
    type: Array as () => StockItem[],
    required: true
  },
  height: {
    type: Number,
    default: 500
  }
})

const emit = defineEmits(['row-click', 'trade'])

const handleRowClick = (item: StockItem) => {
  emit('row-click', item)
}

const getPriceColor = (change: number) => {
  if (change > 0) return 'text-up'
  if (change < 0) return 'text-down'
  return 'text-neutral'
}

const formatPrice = (price: number) => {
  return price.toFixed(2)
}

const formatChange = (change: number) => {
  return (change > 0 ? '+' : '') + change.toFixed(2)
}

const formatVolume = (volume: number) => {
  if (volume >= 1000000) return (volume / 1000000).toFixed(2) + 'M'
  if (volume >= 1000) return (volume / 1000).toFixed(2) + 'K'
  return volume.toString()
}
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.virtual-stock-list {
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-md);
  background: var(--artdeco-bg-surface);
  overflow: hidden;
}

.list-header {
  display: flex;
  height: 40px;
  align-items: center;
  background: var(--artdeco-bg-elevated);
  border-bottom: 1px solid var(--artdeco-border-default);
  padding: 0 var(--artdeco-spacing-4);
  font-weight: 600;
  font-size: 12px;
  color: var(--artdeco-fg-muted);
  text-transform: uppercase;
}

.stock-row {
  display: flex;
  align-items: center;
  height: 48px; // Must match item-height prop
  padding: 0 var(--artdeco-spacing-4);
  border-bottom: 1px solid var(--artdeco-border-subtle);
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: var(--artdeco-bg-hover);
  }
}

.col {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  
  &.symbol { flex: 0 0 80px; font-weight: 600; }
  &.name { flex: 2; }
  &.price { flex: 0 0 100px; text-align: right; font-family: var(--artdeco-font-mono); }
  &.change { flex: 0 0 80px; text-align: right; font-family: var(--artdeco-font-mono); }
  &.volume { flex: 0 0 100px; text-align: right; color: var(--artdeco-fg-muted); }
  &.actions { flex: 0 0 80px; text-align: right; }
}

.text-up { color: var(--artdeco-up); }
.text-down { color: var(--artdeco-down); }
.text-neutral { color: var(--artdeco-fg-muted); }

button {
  background: var(--artdeco-bg-secondary);
  border: 1px solid var(--artdeco-border-default);
  color: var(--artdeco-fg-primary);
  padding: 2px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  
  &:hover {
    background: var(--artdeco-bg-hover);
    border-color: var(--artdeco-gold-primary);
  }
}
</style>
