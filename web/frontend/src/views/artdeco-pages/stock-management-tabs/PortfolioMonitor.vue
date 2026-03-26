<template>
  <div class="portfolio-monitor">
    <div class="portfolio-stats">
      <ArtDecoStatCard label="总资产" :value="stats.totalAssets" :change="stats.totalAssetsChange" change-percent variant="rise" />
      <ArtDecoStatCard label="今日盈亏" :value="stats.todayPnl" :change="stats.todayPnlChange" change-percent variant="rise" />
      <ArtDecoStatCard label="持仓数量" :value="stats.positionCountLabel" variant="gold" />
      <ArtDecoStatCard label="持仓市值" :value="stats.totalMarketValue" variant="gold" />
    </div>

    <ArtDecoCard title="持仓明细" class="positions-card">
      <ArtDecoTable :columns="columns" :data="displayPositions" />
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ArtDecoStatCard, ArtDecoCard, ArtDecoTable } from '@/components/artdeco'
import { apiClient } from '@/api/apiClient'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import {
  extractPortfolioMonitorRows,
  extractPortfolioMonitorStats,
} from './stockManagementRouteData'

interface Props {
  positions: unknown[]
}

const props = withDefaults(defineProps<Props>(), {
  positions: () => []
})

const { exec } = useArtDecoApi()
const internalPositions = ref<unknown[]>([])
const rawPayload = ref<unknown>(null)

const displayPositions = computed(() => {
  if (Array.isArray(props.positions) && props.positions.length > 0) {
    return props.positions
  }
  return internalPositions.value
})

const stats = computed(() => extractPortfolioMonitorStats(rawPayload.value))

async function loadPositions() {
  const responseData = await exec(() => apiClient.get('/v1/trade/positions'), { silent: true })
  rawPayload.value = responseData
  internalPositions.value = extractPortfolioMonitorRows(responseData)
}

onMounted(() => {
  if (!Array.isArray(props.positions) || props.positions.length === 0) {
    void loadPositions()
  }
})

const columns = [
  { key: 'symbol', label: '代码' },
  { key: 'name', label: '名称' },
  { key: 'quantity', label: '持仓', align: 'right' },
  { key: 'cost', label: '成本', align: 'right' },
  { key: 'price', label: '现价', align: 'right' },
  { key: 'pnl', label: '盈亏', variant: 'color', align: 'right' }
]
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.portfolio-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--artdeco-spacing-4);
}

.positions-card {
  margin-top: var(--artdeco-spacing-6);
}

@media (width <= 48rem) {
  .portfolio-stats {
    grid-template-columns: 1fr;
  }
}
</style>
