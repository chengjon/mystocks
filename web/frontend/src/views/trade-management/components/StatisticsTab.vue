<template>
  <div>
    <el-row :gutter="24">
      <el-col :span="12">
        <div class="subcard">
          <div class="subcard-header">
            <h4 class="subcard-title">ASSET TREND</h4>
          </div>
          <div ref="assetsChartRef" style="height: 300px"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="subcard">
          <div class="subcard-header">
            <h4 class="subcard-title">PROFIT DISTRIBUTION</h4>
          </div>
          <div ref="profitChartRef" style="height: 300px"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="24" style="margin-top: 24px">
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
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
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

let assetsChartInstance: ECharts | null = null
let profitChartInstance: ECharts | null = null

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
      axisLine: { lineStyle: { color: '#D4AF37' } },
      axisLabel: { color: '#F2F0E4' }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#D4AF37' } },
      axisLabel: { color: '#F2F0E4', formatter: '¥{value}' },
      splitLine: { lineStyle: { color: 'rgba(212, 175, 55, 0.1)' } }
    },
    series: [
      {
        name: 'TOTAL ASSETS',
        type: 'line',
        data: values,
        smooth: true,
        itemStyle: { color: '#D4AF37' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(212, 175, 55, 0.3)' },
              { offset: 1, color: 'rgba(212, 175, 55, 0.1)' }
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

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: { color: '#F2F0E4' }
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
            shadowColor: 'rgba(212, 175, 55, 0.5)'
          }
        },
        itemStyle: {
          borderColor: '#141414',
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

.subcard {
  background: rgba(212, 175, 55, 0.05);
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: var(--radius-none);
  padding: var(--spacing-6);
  height: 100%;

  .subcard-header {
    margin-bottom: var(--spacing-4);
    padding-bottom: var(--spacing-3);
    border-bottom: 1px solid rgba(212, 175, 55, 0.2);

    .subcard-title {
      font-family: var(--font-display);
      font-size: var(--font-size-base);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: var(--tracking-widest);
      color: var(--accent-gold);
      margin: 0;
    }
  }

  :deep(.el-descriptions__label) {
    background: rgba(212, 175, 55, 0.1) !important;
    color: var(--fg-muted) !important;
    font-family: var(--font-display);
    font-size: var(--font-size-xs);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    border-color: rgba(212, 175, 55, 0.3) !important;
  }

  :deep(.el-descriptions__content) {
    background: transparent !important;
    color: var(--fg-primary) !important;
    font-family: var(--font-body);
    border-color: rgba(212, 175, 55, 0.3) !important;
  }
}

.profit-up {
  color: var(--color-up) !important;
}

.profit-down {
  color: var(--color-down) !important;
}
</style>
