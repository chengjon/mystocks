<template>
  <div class="trade-management-container">

    <!-- Bloomberg-style Header -->
    <div class="trade-header">
      <div class="header-title-section">
        <h1 class="page-title">TRADE MANAGEMENT</h1>
        <p class="page-subtitle">POSITION TRACKING | ORDER MANAGEMENT | PERFORMANCE ANALYSIS</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openTradeDialog('buy')">
          NEW TRADE
        </el-button>
      </div>
    </div>

    <!-- Portfolio Overview Section -->
    <div class="portfolio-section">
      <PortfolioOverview ref="portfolioOverviewRef" />
    </div>

    <!-- Main Card with Tabs -->
    <div class="main-card">
      <!-- Bloomberg-style Custom Tabs -->
      <div class="bloomberg-tabs-wrapper">
        <button
          v-for="tab in tabs"
          :key="tab.name"
          :class="['bloomberg-tab', { active: activeTab === tab.name }]"
          @click="activeTab = tab.name"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        <PositionsTab
          v-if="activeTab === 'positions'"
          ref="positionsTabRef"
          @buy="openTradeDialog('buy')"
          @sell="openTradeDialog('sell')"
          @quick-sell="handleQuickSell"
        />

        <TradeHistoryTab v-if="activeTab === 'trades'" ref="tradeHistoryTabRef" />

        <StatisticsTab v-if="activeTab === 'statistics'" ref="statisticsTabRef" />
      </div>
    </div>

    <!-- Trade Dialog -->
    <TradeDialog
      v-model:visible="tradeDialogVisible"
      :trade-type="tradeType"
      @submitted="handleTradeSubmitted"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, watch } from 'vue'
import { ElButton } from 'element-plus'
import { PortfolioOverview, PositionsTab, TradeHistoryTab, StatisticsTab, TradeDialog } from './trade-management/components'
import { tradeApi } from '@/api/trade'
import type { AccountOverviewVM } from '@/utils/trade-adapters'

const activeTab = ref('positions')
const tradeDialogVisible = ref(false)
const tradeType = ref<'buy' | 'sell'>('buy')

const tabs = [
  { name: 'positions', label: 'POSITIONS' },
  { name: 'trades', label: 'TRADE HISTORY' },
  { name: 'statistics', label: 'STATISTICS' }
]

const portfolioOverviewRef = ref<InstanceType<typeof PortfolioOverview>>()
const positionsTabRef = ref<InstanceType<typeof PositionsTab>>()
const tradeHistoryTabRef = ref<InstanceType<typeof TradeHistoryTab>>()
const statisticsTabRef = ref<InstanceType<typeof StatisticsTab>>()

// Type adapter: Convert AccountOverviewVM to Portfolio format
const adaptToPortfolio = (accountOverview: AccountOverviewVM) => ({
  total_assets: accountOverview.totalAssets,
  available_cash: accountOverview.availableCash,
  position_value: accountOverview.totalPositionValue,
  total_profit: accountOverview.totalPnL,
  profit_rate: parseFloat(accountOverview.totalPnLPercent)
})

const initializeData = async () => {
  try {
    const accountOverview = await tradeApi.getAccountOverview()
    const portfolioData = adaptToPortfolio(accountOverview)
    portfolioOverviewRef.value?.setPortfolio(portfolioData)
  } catch (error) {
    console.error('Failed to load portfolio:', error)
  }
}

onMounted(() => {
  initializeData()
})

const handleTabClick = async (tabName: string) => {
  if (tabName === 'statistics') {
    await nextTick()
    statisticsTabRef.value?.renderCharts()
  }
}

// Watch for tab changes
watch(activeTab, async (newTab) => {
  await handleTabClick(newTab)
})

const openTradeDialog = (type: 'buy' | 'sell') => {
  tradeType.value = type
  tradeDialogVisible.value = true
}

const handleQuickSell = (position: any) => {
  tradeType.value = 'sell'
  tradeDialogVisible.value = true
}

const handleTradeSubmitted = async () => {
  await initializeData()
  positionsTabRef.value?.refresh()
  statisticsTabRef.value?.loadStatistics()
  tradeHistoryTabRef.value?.loadTrades()
}
</script>

<style scoped lang="scss">
// Phase 3.3: Design Token Migration
@use 'sass:color';
@import '@/styles/theme-tokens.scss';

// ============================================
//   Bloomberg Terminal Style Trade Management
// ============================================

.trade-management-container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  padding: var(--spacing-lg);
  background: var(--color-bg-primary);
  min-height: 100vh;
}

// Bloomberg-style Header
.trade-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: var(--spacing-lg);
  border-bottom: 2px solid var(--color-border);

  .header-title-section {
    flex: 1;
  }

  .page-title {
    font-family: var(--font-family-sans);
    font-size: var(--font-size-2xl);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--color-accent);
    margin: 0 0 var(--spacing-sm) 0;
    line-height: 1.2;
  }

  .page-subtitle {
    font-family: var(--font-family-sans);
    font-size: var(--font-size-xs);
    color: var(--color-text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.2em;
    margin: 0;
    line-height: 1.4;
  }

  .header-actions {
    display: flex;
    gap: var(--spacing-md);
  }
}

// Portfolio Section
.portfolio-section {
  margin-bottom: var(--spacing-sm);
}

// Main Card
.main-card {
  background: linear-gradient(135deg, var(--color-bg-secondary) 0%, var(--color-bg-elevated) 100%);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-lg);

  // Bloomberg-style Tabs Wrapper
  .bloomberg-tabs-wrapper {
    display: flex;
    gap: 2px;
    border-bottom: 2px solid var(--color-border);
    margin-bottom: var(--spacing-lg);
  }

  .bloomberg-tab {
    display: flex;
    align-items: center;
    padding: var(--spacing-md) var(--spacing-lg);
    background: transparent;
    border: none;
    border-bottom: 3px solid transparent;
    color: var(--color-text-secondary);
    font-family: var(--font-family-sans);
    font-size: var(--font-size-xs);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      color: var(--color-accent);
      background: var(--color-accent-alpha-90);
    }

    &.active {
      color: var(--color-accent);
      border-bottom-color: var(--color-accent);
      background: var(--color-accent-alpha-90);
    }
  }

  // Tab Content
  .tab-content {
    min-height: 500px;
  }
}

// Responsive Design
@media (max-width: 1440px) {
  .trade-management-container {
    padding: var(--spacing-lg);
    gap: var(--spacing-lg);
  }

  .trade-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);

    .header-actions {
      width: 100%;
      justify-content: flex-end;
    }
  }
}

@media (max-width: 768px) {
  .trade-management-container {
    padding: var(--spacing-md);
    gap: var(--spacing-md);
  }

  .trade-header {
    .page-title {
      font-size: var(--font-size-xl);
    }

    .page-subtitle {
      font-size: var(--font-size-xs);
    }
  }

  .main-card {
    padding: var(--spacing-md);

    .bloomberg-tabs-wrapper {
      flex-wrap: wrap;

      .bloomberg-tab {
        padding: 10px var(--spacing-md);
        font-size: var(--font-size-xs);
      }
    }
  }
}
</style>
