<template>
  <div class="pro-kline-chart">
    <!-- Chart Toolbar -->
    <div class="chart-toolbar">
      <!-- Period Selector -->
      <el-select
        v-model="selectedPeriod"
        placeholder="周期"
        size="small"
        @change="handlePeriodChange"
      >
        <el-option
          v-for="(period, _idx) in periods"
          :key="period.value"
          :label="period.label"
          :value="period.value"
        />
      </el-select>

      <!-- Indicator Selector -->
      <el-select
        v-model="selectedIndicators"
        placeholder="技术指标"
        size="small"
        multiple
        collapse-tags
        collapse-tags-tooltip
        @change="handleIndicatorChange"
      >
        <el-option
          v-for="(indicator, _idx) in availableIndicators"
          :key="indicator.value"
          :label="indicator.label"
          :value="indicator.value"
        />
      </el-select>

      <!-- Refresh Button -->
      <el-button
        size="small"
        type="primary"
        :loading="loading"
        @click="handleRefresh"
      >
        <el-icon><RefreshRight /></el-icon>
        刷新
      </el-button>

      <!-- A股 Features Toggle -->
      <div class="a-share-features">
        <el-switch
          v-model="showPriceLimits"
          size="small"
          active-text="涨跌停"
          @change="handleTogglePriceLimits"
        />
        <el-switch
          v-model="useForwardAdjusted"
          size="small"
          active-text="前复权"
          @change="handleToggleAdjustment"
        />
      </div>
    </div>

    <!-- Chart Container -->
    <div
      ref="chartContainer"
      class="chart-container"
      v-loading="loading"
      element-loading-text="加载中..."
    />
  </div>
</template>

<script setup lang="ts">
import { RefreshRight } from '@element-plus/icons-vue'
import { useProKLineChart } from './composables/useProKLineChart'

const {
  props,
  emit,
  chartContainer,
  chartInstance,
  loading,
  selectedPeriod,
  selectedIndicators,
  showPriceLimits,
  useForwardAdjusted,
  currentKLineData,
  priceLimitMarkers,
  availableIndicators,
  initChart,
  loadHistoricalData,
  calculatePriceLimitMarkers,
  applyPriceLimitOverlay,
  handlePeriodChange,
  applyIndicators,
  applyMAIndicator,
  applyVolumeIndicator,
  applyMACDIndicator,
  applyRSIIndicator,
  applyKDJIndicator,
  handleIndicatorChange,
  handleRefresh,
  handleTogglePriceLimits,
  handleToggleAdjustment,
} = useProKLineChart()

// Expose periods from props for template usage
const periods = props.periods
</script>

<style scoped lang="scss">
.pro-kline-chart {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-primary);
  border-radius: 4px;
  overflow: hidden;

  .chart-toolbar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: var(--color-bg-secondary);
    border-bottom: 1px solid var(--color-border);

    .a-share-features {
      margin-left: auto;
      display: flex;
      gap: 12px;
    }
  }

  .chart-container {
    flex: 1;
    width: 100%;
    position: relative;
  }
}
</style>
