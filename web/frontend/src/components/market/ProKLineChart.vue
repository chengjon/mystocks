<template>
  <div class="pro-kline-chart">
    <!-- Chart Toolbar -->
    <div class="chart-toolbar">
      <!-- Period Selector -->
      <el-select
        v-if="!usesExternalData"
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
        v-if="!usesExternalData"
        size="small"
        type="primary"
        :loading="effectiveLoading"
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
          v-if="!usesExternalData"
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
      v-loading="effectiveLoading"
      element-loading-text="加载中..."
    />
  </div>
</template>

<script setup lang="ts">
import { RefreshRight } from '@element-plus/icons-vue'
import { computed } from 'vue'
import { useProKLineChart } from './composables/useProKLineChart'
import { defaultProKLineChartProps, type ProKLineChartProps } from './composables/useProKLineChart.types'

const props = withDefaults(defineProps<ProKLineChartProps>(), defaultProKLineChartProps)

const emit = defineEmits<{
  (e: 'period-change', period: string): void
  (e: 'indicator-change', indicators: string[]): void
  (e: 'data-loaded', data: unknown[]): void
  (e: 'error', error: Error): void
  (e: 'request-refresh'): void
}>()

const {
  chartContainer,
  loading,
  selectedPeriod,
  selectedIndicators,
  showPriceLimits,
  useForwardAdjusted,
  availableIndicators,
  handlePeriodChange,
  handleIndicatorChange,
  handleRefresh,
  handleTogglePriceLimits,
  handleToggleAdjustment,
} = useProKLineChart(props, emit)

// Expose periods from props for template usage
const periods = props.periods
const usesExternalData = computed(() => Array.isArray(props.externalData))
const effectiveLoading = computed(() => (usesExternalData.value ? Boolean(props.loading) : loading.value))
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.pro-kline-chart {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-primary);
  border-radius: var(--artdeco-spacing-1);
  overflow: hidden;

  .chart-toolbar {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-3);
    padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
    background: var(--color-bg-secondary);
    border-bottom: 1px solid var(--color-border);

    .a-share-features {
      margin-left: auto;
      display: flex;
      gap: var(--artdeco-spacing-3);
    }
  }

  .chart-container {
    flex: 1;
    width: 100%;
    position: relative;
  }
}
</style>
