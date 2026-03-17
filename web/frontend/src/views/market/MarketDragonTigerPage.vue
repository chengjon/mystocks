<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import { dragonTigerService, type DragonTigerRecord } from '@/api/services/dragonTigerService'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import DragonTigerAnalysis from '@/views/artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue'

type DragonTigerFilter = 'buy' | 'sell' | 'institution'
type DragonTigerDatePreset = 'today' | 'yesterday' | 'dayBefore'

interface DragonTigerRow {
  id: number
  symbol: string
  name: string
  tradeDate: string
  reason: string
  buyAmount: string
  sellAmount: string
  netBuy: string
}

const { loading, error, lastProcessTime, lastRequestId, exec } = useArtDecoApi()

const activeFilter = ref<DragonTigerFilter>('buy')
const selectedDatePreset = ref<DragonTigerDatePreset>('today')
const dragonTigerRecords = ref<DragonTigerRecord[]>([])

const displayProcessTime = computed(() => {
  if (!lastProcessTime.value) {
    return 'N/A'
  }

  const value = Number.parseFloat(lastProcessTime.value)
  if (Number.isNaN(value)) {
    return lastProcessTime.value
  }

  return `${value.toFixed(2)}ms`
})

const filteredRecords = computed(() => {
  if (activeFilter.value === 'institution') {
    return dragonTigerRecords.value.filter((record) => {
      return record.institution_buy != null || record.institution_sell != null
    })
  }

  if (activeFilter.value === 'sell') {
    return dragonTigerRecords.value.filter((record) => record.net_amount < 0)
  }

  return dragonTigerRecords.value.filter((record) => record.net_amount >= 0)
})

const tableRows = computed<DragonTigerRow[]>(() => {
  return filteredRecords.value.map((record) => ({
    id: record.id,
    symbol: record.symbol,
    name: record.name,
    tradeDate: record.trade_date,
    reason: record.reason || '无上榜原因',
    buyAmount: formatAmount(record.buy_amount),
    sellAmount: formatAmount(record.sell_amount),
    netBuy: formatSignedAmount(record.net_amount)
  }))
})

const summary = computed(() => {
  const maxNetBuy = dragonTigerRecords.value.reduce((max, record) => {
    return Math.max(max, record.net_amount)
  }, 0)

  return {
    totalRecords: dragonTigerRecords.value.length,
    netBuyRecords: dragonTigerRecords.value.filter((record) => record.net_amount >= 0).length,
    institutionRecords: dragonTigerRecords.value.filter((record) => {
      return record.institution_buy != null || record.institution_sell != null
    }).length,
    maxNetBuy: formatAmount(maxNetBuy)
  }
})

function formatAmount(amount: number): string {
  return `${(amount / 10000).toFixed(2)}万`
}

function formatSignedAmount(amount: number): string {
  return `${amount >= 0 ? '+' : ''}${formatAmount(amount)}`
}

function resolveTradeDate(preset: DragonTigerDatePreset): string {
  const currentDate = new Date()
  const daysOffset = preset === 'today' ? 0 : preset === 'yesterday' ? 1 : 2
  currentDate.setDate(currentDate.getDate() - daysOffset)

  const year = currentDate.getFullYear()
  const month = `${currentDate.getMonth() + 1}`.padStart(2, '0')
  const day = `${currentDate.getDate()}`.padStart(2, '0')

  return `${year}-${month}-${day}`
}

async function fetchDragonTiger(): Promise<void> {
  const data = await exec(
    () =>
      dragonTigerService.listDragonTiger({
        tradeDate: resolveTradeDate(selectedDatePreset.value),
        limit: 20
      }),
    {
      silent: true,
      errorMsg: '龙虎榜数据加载失败'
    }
  )

  dragonTigerRecords.value = Array.isArray(data) ? data : []
}

function handleDateChange(value: string): void {
  if (value === 'today' || value === 'yesterday' || value === 'dayBefore') {
    selectedDatePreset.value = value
  }
}

function handleFilterChange(value: string): void {
  if (value === 'buy' || value === 'sell' || value === 'institution') {
    activeFilter.value = value
  }
}

watch(selectedDatePreset, () => {
  void fetchDragonTiger()
})

onMounted(() => {
  void fetchDragonTiger()
})
</script>

<template>
  <div class="market-lhb-page page-enter">
    <div class="artdeco-header-bar">
      <h2 class="section-title">Dragon Tiger Board</h2>
      <div class="header-meta">
        <span>DATA: REAL</span>
        <span>REQ: {{ lastRequestId || 'N/A' }}</span>
        <span>TIME: {{ displayProcessTime }}</span>
      </div>
    </div>

    <div class="stats-grid artdeco-card">
      <div class="stat-item">
        <span class="stat-label">上榜记录</span>
        <strong class="stat-value">{{ summary.totalRecords }}</strong>
      </div>
      <div class="stat-item">
        <span class="stat-label">净买入记录</span>
        <strong class="stat-value rise">{{ summary.netBuyRecords }}</strong>
      </div>
      <div class="stat-item">
        <span class="stat-label">机构席位</span>
        <strong class="stat-value gold">{{ summary.institutionRecords }}</strong>
      </div>
      <div class="stat-item">
        <span class="stat-label">最大净买入</span>
        <strong class="stat-value gold">{{ summary.maxNetBuy }}</strong>
      </div>
    </div>

    <div v-if="tableRows.length === 0" class="lhb-empty artdeco-card" v-loading="loading">
      <p v-if="error" class="empty-error">{{ error }}</p>
      <p class="empty-title">暂无龙虎榜数据</p>
      <p class="empty-hint">当前页面只展示真实生产链路返回的数据，不再使用本地 mock / fallback 伪成功。</p>
    </div>

    <DragonTigerAnalysis
      v-else
      :lhb-data="tableRows"
      :lhb-date="selectedDatePreset"
      :active-filter="activeFilter"
      @date-change="handleDateChange"
      @filter-change="handleFilterChange"
    />
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.market-lhb-page {
  padding: var(--artdeco-spacing-6);
}

.artdeco-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: var(--artdeco-spacing-8);
  border-bottom: 2px solid var(--artdeco-gold-primary);
  padding-bottom: var(--artdeco-spacing-2);

  .section-title {
    margin: 0;
    font-size: var(--artdeco-text-2xl);
    color: var(--artdeco-gold-primary);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
  }
}

.header-meta {
  display: flex;
  gap: var(--artdeco-spacing-3);
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-4);
  padding: var(--artdeco-spacing-4);
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.stat-label {
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-xs);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
}

.stat-value {
  color: var(--artdeco-fg-primary);
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xl);
}

.stat-value.rise {
  color: var(--artdeco-rise);
}

.stat-value.gold {
  color: var(--artdeco-gold-primary);
}

.lhb-empty {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-5);
}

.empty-error {
  margin: 0;
  color: var(--artdeco-down);
  font-family: var(--artdeco-font-mono);
}

.empty-title {
  margin: 0;
  color: var(--artdeco-gold-light);
  font-size: var(--artdeco-text-lg);
}

.empty-hint {
  margin: 0;
  color: var(--artdeco-fg-muted);
}
</style>
