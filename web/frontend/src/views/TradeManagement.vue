<template>
  <div class="trade-management">

    <div class="page-header">
      <h1 class="page-title">TRADE MANAGEMENT</h1>
      <p class="page-subtitle">POSITION TRACKING | ORDER MANAGEMENT | PERFORMANCE ANALYSIS</p>
    </div>

    <PortfolioOverview ref="portfolioOverviewRef" />

    <div class="main-card">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick" class="tabs">
        <el-tab-pane label="POSITIONS" name="positions">
          <PositionsTab
            v-if="activeTab === 'positions'"
            ref="positionsTabRef"
            @buy="openTradeDialog('buy')"
            @sell="openTradeDialog('sell')"
            @quick-sell="handleQuickSell"
          />
        </el-tab-pane>

        <el-tab-pane label="TRADE HISTORY" name="trades">
          <TradeHistoryTab v-if="activeTab === 'trades'" ref="tradeHistoryTabRef" />
        </el-tab-pane>

        <el-tab-pane label="STATISTICS" name="statistics">
          <StatisticsTab v-if="activeTab === 'statistics'" ref="statisticsTabRef" />
        </el-tab-pane>
      </el-tabs>
    </div>

    <TradeDialog
      v-model:visible="tradeDialogVisible"
      :trade-type="tradeType"
      @submitted="handleTradeSubmitted"
    />
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck
import { ref, nextTick, onMounted } from 'vue'
import { PortfolioOverview, PositionsTab, TradeHistoryTab, StatisticsTab, TradeDialog } from './trade-management/components'
import { tradeApi } from '@/api/trade'

const activeTab = ref('positions')
const tradeDialogVisible = ref(false)
const tradeType = ref<'buy' | 'sell'>('buy')

const portfolioOverviewRef = ref<InstanceType<typeof PortfolioOverview>>()
const positionsTabRef = ref<InstanceType<typeof PositionsTab>>()
const tradeHistoryTabRef = ref<InstanceType<typeof TradeHistoryTab>>()
const statisticsTabRef = ref<InstanceType<typeof StatisticsTab>>()

const initializeData = async () => {
  try {
    const portfolioData = await tradeApi.getAccountOverview()
    portfolioOverviewRef.value?.setPortfolio(portfolioData)
  } catch (error) {
    console.error('加载投资组合失败:', error)
  }
}

onMounted(() => {
  initializeData()
})

const handleTabClick = async (tab: any) => {
  if (tab.paneName === 'statistics') {
    await nextTick()
    statisticsTabRef.value?.renderCharts()
  }
}

const openTradeDialog = (type: 'buy' | 'sell') => {
  tradeType.value = type
  tradeDialogVisible.value = true
}

const handleQuickSell = (position: any) => {
  tradeType.value = 'sell'
  tradeDialogVisible.value = true
  // Pre-fill dialog with position data
  // The TradeDialog component will handle this through its setFormData method
}

const handleTradeSubmitted = async () => {
  await initializeData()
  positionsTabRef.value?.refresh()
  statisticsTabRef.value?.loadStatistics()
  tradeHistoryTabRef.value?.loadTrades()
}
</script>

<style scoped lang="scss">

  min-height: 100vh;
  padding: var(--spacing-6);
  position: relative;
  background: var(--bg-primary);

    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
    opacity: 0.04;
    background-image:
      repeating-linear-gradient(
        45deg,
        var(--accent-gold) 0px,
        var(--accent-gold) 1px,
        transparent 1px,
        transparent 10px
      ),
      repeating-linear-gradient(
        -45deg,
        var(--accent-gold) 0px,
        var(--accent-gold) 1px,
        transparent 1px,
        transparent 10px
      );
  }

  .page-header {
    text-align: center;
    margin-bottom: var(--spacing-8);
    position: relative;
    z-index: 1;

    .page-title {
      font-family: var(--font-display);
      font-size: var(--font-size-h2);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: var(--tracking-widest);
      color: var(--accent-gold);
      margin: 0 0 var(--spacing-2) 0;
    }

    .page-subtitle {
      font-family: var(--font-body);
      font-size: var(--font-size-small);
      color: var(--fg-muted);
      text-transform: uppercase;
      letter-spacing: var(--tracking-wider);
      margin: 0;
    }
  }

    background: var(--bg-card);
    border: 1px solid rgba(212, 175, 55, 0.3);
    border-radius: var(--radius-none);
    padding: var(--spacing-6);
    position: relative;
    z-index: 1;
  }

  .tabs {
    :deep(.el-tabs__nav-wrap) {
      &::after {
        background: rgba(212, 175, 55, 0.3);
      }
    }

    :deep(.el-tabs__item) {
      color: var(--fg-muted);
      font-family: var(--font-display);
      text-transform: uppercase;
      letter-spacing: var(--tracking-wider);
      font-weight: 600;

      &:hover {
        color: var(--accent-gold);
      }

      &.is-active {
        color: var(--accent-gold);
        border-bottom: 2px solid var(--accent-gold) !important;
      }
    }

    :deep(.el-tabs__active-bar) {
      background: var(--accent-gold);
    }
  }
}
</style>
