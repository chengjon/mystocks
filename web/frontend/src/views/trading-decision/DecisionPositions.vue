<template>
  <div>
    <div v-if="isVisible" class="tab-content positions-tab">
      <div class="positions-toolbar">
        <el-button size="small" plain @click="handleRefreshPositions">刷新持仓</el-button>
      </div>

      <div v-if="positions.length > 0" class="positions-grid">
        <ArtDecoPositionCard
          v-for="position in positions"
          :key="position.symbol"
          :position="position"
          @sell="handleQuickSell"
        />
      </div>

      <el-empty v-else description="暂无持仓数据" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import ArtDecoPositionCard from '@/components/artdeco/trading/ArtDecoPositionCard.vue'
import { tradeApi } from '@/api/trade.ts'

const AUTO_REFRESH_EVENT = 'trading-decision:auto-refresh'

const props = defineProps<{
  activeTab?: string
}>()

interface PositionCardItem {
  symbol: string
  stock_name: string
  quantity: number
  cost_price: number
  current_price: number
  profit: number
  profit_rate: number
  update_time: string
}

const positions = ref<PositionCardItem[]>([])
const isVisible = computed(() => !props.activeTab || props.activeTab === 'positions')

const loadPositions = async (): Promise<void> => {
  const data = await tradeApi.getPositions()
  positions.value = data.map((position) => ({
    symbol: position.symbol,
    stock_name: position.name,
    quantity: position.quantity,
    cost_price: position.avgPrice,
    current_price: position.currentPrice,
    profit: position.positionPnL,
    profit_rate: Number.parseFloat(position.positionPnLPercent) || 0,
    update_time: position.lastUpdate
  }))
}

const handleQuickSell = (stock: { symbol: string; stock_name: string }): void => {
  ElMessage.info(`卖出入口已准备：${stock.stock_name} (${stock.symbol})`)
}

const handleRefreshPositions = async (showSuccess = true): Promise<void> => {
  try {
    await loadPositions()
    if (showSuccess) {
      ElMessage.success('持仓数据已刷新')
    }
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '持仓数据刷新失败')
  }
}

const handleAutoRefresh = (): void => {
  void handleRefreshPositions(false)
}

onMounted(() => {
  window.addEventListener(AUTO_REFRESH_EVENT, handleAutoRefresh)
  void handleRefreshPositions(false)
})

onBeforeUnmount(() => {
  window.removeEventListener(AUTO_REFRESH_EVENT, handleAutoRefresh)
})
</script>

<style scoped>
.positions-tab {
  display: grid;
  gap: 16px;
}

.positions-toolbar {
  display: flex;
  justify-content: flex-end;
}

.positions-grid {
  display: grid;
  gap: 16px;
}
</style>
