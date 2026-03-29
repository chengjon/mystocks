<template>
  <div>
    <el-row :gutter="chartRowGutter">
      <el-col :span="12">
        <div class="subcard">
          <div class="subcard-header">
            <h4 class="subcard-title">ASSET TREND</h4>
          </div>
          <div ref="assetsChartRef" :style="{ height: chartHeight }"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="subcard">
          <div class="subcard-header">
            <h4 class="subcard-title">PROFIT DISTRIBUTION</h4>
          </div>
          <div ref="profitChartRef" :style="{ height: chartHeight }"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="chartRowGutter" :style="{ marginTop: chartSectionSpacing }">
      <el-col :span="24">
        <div class="subcard">
          <div class="subcard-header">
            <h4 class="subcard-title">TRADE STATISTICS</h4>
          </div>
          <el-descriptions :column="4" border class="descriptions">
            <el-descriptions-item label="TOTAL TRADES">{{ statistics.total_trades }}</el-descriptions-item>
            <el-descriptions-item label="BUY COUNT">{{ statistics.buy_count }}</el-descriptions-item>
            <el-descriptions-item label="SELL COUNT">{{ statistics.sell_count }}</el-descriptions-item>
            <el-descriptions-item label="POSITION COUNT">{{ statistics.position_count }}</el-descriptions-item>
            <el-descriptions-item label="TOTAL BUY AMOUNT">¥{{ statistics.total_buy_amount.toFixed(2) }}</el-descriptions-item>
            <el-descriptions-item label="TOTAL SELL AMOUNT">¥{{ statistics.total_sell_amount.toFixed(2) }}</el-descriptions-item>
            <el-descriptions-item label="TOTAL COMMISSION">¥{{ statistics.total_commission.toFixed(2) }}</el-descriptions-item>
            <el-descriptions-item label="REALIZED PROFIT">
              <span :class="getProfitClass(statistics.realized_profit)">
                ¥{{ statistics.realized_profit.toFixed(2) }}
              </span>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import echarts from '@/utils/echarts'
import type { EChartsType } from 'echarts/core'

import { artDecoTheme } from '@/utils/echarts'
import { tradeApi } from '@/api/trade'

interface Statistics {
  total_trades: number
  buy_count: number
  sell_count: number
  position_count: number
  total_buy_amount: number
  total_sell_amount: number
  total_commission: number
  realized_profit: number
}

const assetsChartRef = ref<HTMLElement>()
const profitChartRef = ref<HTMLElement>()

let assetsChartInstance: EChartsType | null = null
let profitChartInstance: EChartsType | null = null

const chartRowGutter = 24
const chartHeight = 'calc((var(--artdeco-spacing-20) * 3) + var(--artdeco-spacing-10) + var(--artdeco-spacing-5))'
const chartSectionSpacing = 'var(--artdeco-spacing-6)'

const getCssVar = (name: string, fallback: string): string => {
  if (typeof window === 'undefined') return fallback
  const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  return value || fallback
}

const statistics = reactive<Statistics>({
  total_trades: 2,
  buy_count: 2,
  sell_count: 0,
  position_count: 2,
  total_buy_amount: 25400,
  total_sell_amount: 0,
  total_commission: 10,
  realized_profit: 1050
})

const mockPositions = [
  { stock_name: '平安银行', profit: 700 },
  { stock_name: '万科A', profit: 350 }
]

const loadStatistics = async () => {
  try {
    const data = await tradeApi.getTradeStatistics()
    Object.assign(statistics, {
      total_trades: data.totalTrades,
      buy_count: data.winningTrades,
      sell_count: data.losingTrades,
      position_count: 2,
      total_buy_amount: 25400,
      total_sell_amount: 0,
      total_commission: data.totalCommission,
      realized_profit: data.avgWin - data.avgLoss
    })
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const renderAssetsChart = () => {
  if (!assetsChartRef.value) return

  if (!assetsChartInstance) {
    assetsChartInstance = echarts.init(assetsChartRef.value, artDecoTheme)
  }

  const dates: string[] = []
  const values: number[] = []
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - 29)

  for (let i = 0; i < 30; i++) {
    const date = new Date(startDate)
    date.setDate(date.getDate() + i)
    dates.push(date.toISOString().slice(5, 10))
    values.push(1000000 + Math.random() * 100000)
  }

  const artDecoGold = getCssVar('--artdeco-gold-primary', '#D4AF37')
  const artDecoFgPrimary = getCssVar('--artdeco-fg-primary', '#F2F0E4')
  const artDecoGoldOpacity10 = getCssVar('--artdeco-gold-opacity-10', 'rgb(212 175 55 / 10%)')
  const artDecoGoldOpacity30 = getCssVar('--artdeco-gold-opacity-30', 'rgb(212 175 55 / 30%)')

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>TOTAL ASSETS: ¥{c}'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLine: { lineStyle: { color: artDecoGold } },
      axisLabel: { color: artDecoFgPrimary }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: artDecoGold } },
      axisLabel: { color: artDecoFgPrimary, formatter: '¥{value}' },
      splitLine: { lineStyle: { color: artDecoGoldOpacity10 } }
    },
    series: [
      {
        name: 'TOTAL ASSETS',
        type: 'line',
        data: values,
        smooth: true,
        itemStyle: { color: artDecoGold },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: artDecoGoldOpacity30 },
              { offset: 1, color: artDecoGoldOpacity10 }
            ]
          }
        }
      }
    ]
  }

  assetsChartInstance.setOption(option)
}

const renderProfitChart = () => {
  if (!profitChartRef.value) return

  if (!profitChartInstance) {
    profitChartInstance = echarts.init(profitChartRef.value, artDecoTheme)
  }

  const artDecoFgPrimary = getCssVar('--artdeco-fg-primary', '#F2F0E4')
  const artDecoGoldOpacityShadow = getCssVar('--artdeco-gold-opacity-shadow', 'rgb(212 175 55 / 30%)')
  const artDecoBgCard = getCssVar('--artdeco-bg-card', '#141414')

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: { color: artDecoFgPrimary }
    },
    series: [
      {
        name: 'POSITION PROFIT',
        type: 'pie',
        radius: '60%',
        data: mockPositions.map(p => ({
          name: p.stock_name,
          value: p.profit
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: artDecoGoldOpacityShadow
          }
        },
        itemStyle: {
          borderColor: artDecoBgCard,
          borderWidth: 2
        }
      }
    ]
  }

  profitChartInstance.setOption(option)
}

const handleResize = () => {
  if (assetsChartInstance) {
    assetsChartInstance.resize()
  }
  if (profitChartInstance) {
    profitChartInstance.resize()
  }
}

const getProfitClass = (value: number) => {
  return value >= 0 ? 'profit-up' : 'profit-down'
}

onMounted(async () => {
  window.addEventListener('resize', handleResize)
  await loadStatistics()
  await nextTick()
  renderAssetsChart()
  renderProfitChart()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (assetsChartInstance) {
    assetsChartInstance.dispose()
  }
  if (profitChartInstance) {
    profitChartInstance.dispose()
  }
})

defineExpose({
  loadStatistics,
  renderCharts: () => {
    renderAssetsChart()
    renderProfitChart()
  }
})
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.subcard {
  background: color-mix(in srgb, var(--artdeco-gold-primary) 5%, var(--artdeco-bg-card));
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-none);
  padding: var(--artdeco-spacing-6);
  height: 100%;

  .subcard-header {
    margin-bottom: var(--artdeco-spacing-4);
    padding-bottom: var(--artdeco-spacing-3);
    border-bottom: 1px solid var(--artdeco-border-default);

    .subcard-title {
      font-family: var(--artdeco-font-heading, var(--font-display));
      font-size: var(--artdeco-text-base);
      font-weight: var(--artdeco-font-semibold);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-widest);
      color: var(--artdeco-gold-primary);
      margin: 0;
    }
  }

  :deep(.el-descriptions__label) {
    background: color-mix(in srgb, var(--artdeco-gold-primary) 10%, var(--artdeco-bg-card)) !important;
    color: var(--artdeco-fg-muted) !important;
    font-family: var(--artdeco-font-heading, var(--font-display));
    font-size: var(--artdeco-text-xs);
    font-weight: var(--artdeco-font-semibold);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wider);
    border-color: var(--artdeco-border-default) !important;
  }

  :deep(.el-descriptions__content) {
    background: transparent !important;
    color: var(--artdeco-fg-primary) !important;
    font-family: var(--artdeco-font-body, var(--font-body));
    border-color: var(--artdeco-border-default) !important;
  }
}

.profit-up {
  color: var(--artdeco-rise) !important;
}

.profit-down {
  color: var(--artdeco-down) !important;
}
</style>
