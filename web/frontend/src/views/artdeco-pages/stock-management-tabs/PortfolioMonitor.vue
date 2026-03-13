<template>
  <div class="portfolio-monitor">
    <div class="portfolio-monitor__meta" v-if="lastRequestId">REQ: {{ lastRequestId }}</div>

    <div class="portfolio-stats" v-loading="loading">
      <ArtDecoStatCard label="总资产" :value="formatCurrency(totalAssets)" variant="gold" />
      <ArtDecoStatCard
        label="浮动盈亏"
        :value="formatSignedCurrency(totalPnl)"
        :variant="totalPnl >= 0 ? 'rise' : 'fall'"
      />
      <ArtDecoStatCard label="持仓仓位" :value="`${portfolioExposure}%`" variant="gold" />
      <ArtDecoStatCard label="持仓标的" :value="String(displayRows.length)" variant="gold" />
    </div>

    <div v-if="showErrorState" class="portfolio-monitor__state portfolio-monitor__state--error" role="alert">
      持仓监控接口加载失败：{{ error }}
    </div>

    <div v-else-if="showEmptyState" class="portfolio-monitor__state" role="status" aria-live="polite">
      暂无持仓监控数据。
    </div>

    <ArtDecoCard v-else title="持仓明细" class="positions-card">
      <ArtDecoTable :columns="columns" :data="tableRows" />
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { apiClient } from '@/api/apiClient'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { ArtDecoStatCard, ArtDecoCard, ArtDecoTable } from '@/components/artdeco'
import { extractPositionsPayload, toTradingPositionRows } from '../trading-tabs/tradingDataTransform'

interface PortfolioMonitorRow {
  symbol: string
  name: string
  quantity: number
  cost: number
  price: number
  marketValue: number
  pnl: number
  positionPercent: number
}

const props = defineProps<{
  positions?: unknown[]
}>()

const columns = [
  { key: 'symbol', label: '代码' },
  { key: 'name', label: '名称' },
  { key: 'quantity', label: '持仓', align: 'right' },
  { key: 'cost', label: '成本', align: 'right' },
  { key: 'price', label: '现价', align: 'right' },
  { key: 'marketValue', label: '市值', align: 'right' },
  { key: 'pnl', label: '盈亏', variant: 'color', align: 'right' }
]

const internalRows = ref<PortfolioMonitorRow[]>([])
const { loading, error, lastRequestId, exec } = useArtDecoApi()

function parseNumber(value: unknown): number {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value
  }

  if (typeof value === 'string' && value.trim().length > 0) {
    const parsed = Number.parseFloat(value)
    return Number.isFinite(parsed) ? parsed : 0
  }

  return 0
}

function parseString(value: unknown, fallback: string): string {
  return typeof value === 'string' && value.trim().length > 0 ? value : fallback
}

function normalizeInputRows(items: unknown[]): PortfolioMonitorRow[] {
  return items.map((item, index) => {
    const row = (item ?? {}) as Record<string, unknown>
    const symbol = parseString(row.symbol, `UNKNOWN-${index + 1}`)
    const quantity = parseNumber(row.quantity ?? row.shares)
    const cost = parseNumber(row.cost ?? row.avgCost ?? row.cost_price)
    const price = parseNumber(row.price ?? row.currentPrice ?? row.current_price)
    const marketValue = parseNumber(row.marketValue ?? row.market_value) || Number((quantity * price).toFixed(2))
    const pnl = parseNumber(row.pnl ?? row.profit_loss)
    const positionPercent = parseNumber(row.positionPercent ?? row.position_percent)

    return {
      symbol,
      name: parseString(row.name ?? row.symbol_name, symbol),
      quantity,
      cost,
      price,
      marketValue,
      pnl,
      positionPercent,
    }
  })
}

const displayRows = computed(() => {
  if (Array.isArray(props.positions) && props.positions.length > 0) {
    return normalizeInputRows(props.positions)
  }
  return internalRows.value
})

const totalAssets = computed(() => displayRows.value.reduce((sum, row) => sum + row.marketValue, 0))
const totalPnl = computed(() => displayRows.value.reduce((sum, row) => sum + row.pnl, 0))
const portfolioExposure = computed(() => {
  if (displayRows.value.length === 0) {
    return 0
  }

  const fromPayload = displayRows.value.reduce((sum, row) => sum + row.positionPercent, 0)
  if (fromPayload > 0) {
    return Number(Math.min(100, fromPayload).toFixed(2))
  }

  return 100
})

const tableRows = computed(() =>
  displayRows.value.map((row) => ({
    symbol: row.symbol,
    name: row.name,
    quantity: row.quantity.toLocaleString('zh-CN'),
    cost: row.cost.toFixed(2),
    price: row.price.toFixed(2),
    marketValue: row.marketValue.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
    pnl: `${row.pnl >= 0 ? '+' : ''}${row.pnl.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
  }))
)

const showErrorState = computed(() => Boolean(error.value) && displayRows.value.length === 0)
const showEmptyState = computed(() => !loading.value && !error.value && displayRows.value.length === 0)

function formatCurrency(value: number): string {
  return `¥${value.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`
}

function formatSignedCurrency(value: number): string {
  return `${value >= 0 ? '+' : ''}${formatCurrency(value)}`
}

async function loadPositions() {
  const responseData = await exec(() => apiClient.get('/v1/trade/positions'), {
    silent: true,
    errorMsg: '获取持仓监控数据失败',
  })
  internalRows.value = toTradingPositionRows(extractPositionsPayload(responseData)).map((row) => ({
    symbol: row.symbol,
    name: row.name,
    quantity: row.shares,
    cost: row.avgCost,
    price: row.currentPrice,
    marketValue: row.marketValue,
    pnl: row.pnl,
    positionPercent: row.positionPercent,
  }))
}

onMounted(() => {
  if (!Array.isArray(props.positions) || props.positions.length === 0) {
    void loadPositions()
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.portfolio-monitor {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-4);
}

.portfolio-monitor__meta {
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
}

.portfolio-monitor__state {
  padding: var(--artdeco-spacing-5);
  border: 1px solid var(--artdeco-border-default);
  background: linear-gradient(145deg, var(--artdeco-gold-opacity-05), transparent 65%);
  color: var(--artdeco-fg-primary);

  &--error {
    color: var(--artdeco-down);
  }
}

.portfolio-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}

.positions-card {
  margin-top: 0;
}

@media (width <= 960px) {
  .portfolio-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (width <= 640px) {
  .portfolio-stats {
    grid-template-columns: 1fr;
  }
}
</style>
