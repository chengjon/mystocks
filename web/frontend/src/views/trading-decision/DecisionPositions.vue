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

const handleQuickBuy = (_stock: { code: string }): void => {
}

const handleQuickSell = (_stock: { code: string }): void => {
}

const handleRefreshPositions = (): void => {
}
</script>
