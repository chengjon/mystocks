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
        <div class="stock-row" @click="handleRowClick(typedItem(item))">
          <div class="col symbol">{{ typedItem(item).symbol }}</div>
          <div class="col name">{{ typedItem(item).name }}</div>
          <div class="col price" :class="getPriceColor(typedItem(item).change)">
            {{ formatPrice(typedItem(item).price) }}
          </div>
          <div class="col change" :class="getPriceColor(typedItem(item).change)">
            {{ formatChange(typedItem(item).change) }}%
          </div>
          <div class="col volume">{{ formatVolume(typedItem(item).volume) }}</div>
          <div class="col actions">
            <button @click.stop="emit('trade', typedItem(item))">Trade</button>
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

const _props = defineProps({
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

// Type helper for VirtualList slot item
const typedItem = (item: unknown): StockItem => item as StockItem

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
@use '@/styles/artdeco-tokens.scss' as *;

.virtual-stock-list {
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-md);
  background: var(--artdeco-bg-card);
  overflow: hidden;
}

.list-header {
  display: flex;
  height: var(--artdeco-spacing-10);
  align-items: center;
  background: var(--artdeco-bg-elevated);
  border-bottom: 1px solid var(--artdeco-border-default);
  padding: 0 var(--artdeco-spacing-4);
  font-weight: 600;
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
  text-transform: uppercase;
}

.stock-row {
  display: flex;
  align-items: center;
  height: var(--artdeco-spacing-12); // Must match item-height prop
  padding: 0 var(--artdeco-spacing-4);
  border-bottom: 1px solid var(--artdeco-gold-opacity-10);
  cursor: pointer;
  transition: background-color var(--artdeco-transition-quick) var(--artdeco-ease-out);

  &:hover {
    background: var(--artdeco-gold-opacity-05);
  }
}

.col {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  
  &.symbol {
    flex: 0 0 var(--artdeco-spacing-20);
    font-weight: 600;
  }
  &.name { flex: 2; }
  &.price {
    flex: 0 0 calc(var(--artdeco-spacing-20) + var(--artdeco-spacing-5));
    text-align: right;
    font-family: var(--artdeco-font-mono);
  }
  &.change {
    flex: 0 0 var(--artdeco-spacing-20);
    text-align: right;
    font-family: var(--artdeco-font-mono);
  }
  &.volume {
    flex: 0 0 calc(var(--artdeco-spacing-20) + var(--artdeco-spacing-5));
    text-align: right;
    color: var(--artdeco-fg-muted);
  }
  &.actions {
    flex: 0 0 var(--artdeco-spacing-20);
    text-align: right;
  }
}

.text-up { color: var(--artdeco-up); }
.text-down { color: var(--artdeco-down); }
.text-neutral { color: var(--artdeco-fg-muted); }

button {
  background: var(--artdeco-bg-base);
  border: 1px solid var(--artdeco-border-default);
  color: var(--artdeco-fg-primary);
  padding: calc(var(--artdeco-spacing-px) * 2) var(--artdeco-spacing-2);
  border-radius: var(--artdeco-radius-sm);
  cursor: pointer;
  font-size: var(--artdeco-text-xs);
  
  &:hover {
    background: var(--artdeco-bg-elevated);
    border-color: var(--artdeco-gold-primary);
  }
}
</style>
