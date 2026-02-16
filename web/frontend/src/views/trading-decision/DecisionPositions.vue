<template>
  <div>
        <div v-if="activeTab === 'positions'" class="tab-content">
          <!-- Position Management -->
          <PositionsPanel 
            @buy="handleQuickBuy"
            @sell="handleQuickSell"
            @refresh="handleRefreshPositions"
          />
        </div>

     <!-- Orders Tab -->
  </div>
</template>

<script setup lang="ts">
import PositionsPanel from './components/PositionsPanel.vue'

defineProps<{
  activeTab?: string
}>()

const handleQuickBuy = (stock: { code: string }): void => {
  console.log('Quick buy:', stock.code)
}

const handleQuickSell = (stock: { code: string }): void => {
  console.log('Quick sell:', stock.code)
}

const handleRefreshPositions = (): void => {
  console.log('Refresh positions')
}
</script>
