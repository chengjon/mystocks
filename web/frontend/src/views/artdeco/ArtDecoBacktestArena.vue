<template>
  <div class="artdeco-backtest-arena">
    <!-- Key Metrics -->
    <div class="artdeco-grid-4">
      <div class="artdeco-card">
        <div class="artdeco-stat-value artdeco-data-rise">+{{ backtestMetrics.totalReturn }}%</div>
        <div class="artdeco-stat-label">累计收益率</div>
      </div>
      <div class="artdeco-card">
        <div class="artdeco-stat-value">{{ backtestMetrics.sharpe }}</div>
        <div class="artdeco-stat-label">夏普比率</div>
      </div>
      <div class="artdeco-card">
        <div class="artdeco-stat-value artdeco-data-fall">{{ backtestMetrics.maxDrawdown }}%</div>
        <div class="artdeco-stat-label">最大回撤</div>
      </div>
      <div class="artdeco-card">
        <div class="artdeco-stat-value">{{ backtestMetrics.winRate }}%</div>
        <div class="artdeco-stat-label">胜率</div>
      </div>
    </div>

    <!-- Charts -->
    <div class="artdeco-grid-2">
      <div class="artdeco-card">
        <h3>净值曲线</h3>
        <div ref="equityChartRef" class="artdeco-chart-container"></div>
      </div>
      <div class="artdeco-card">
        <h3>回撤分析</h3>
        <div ref="drawdownChartRef" class="artdeco-chart-container"></div>
      </div>
    </div>

    <!-- Trade History -->
    <div class="artdeco-card">
      <h3>交易记录</h3>
      <table class="artdeco-table">
        <thead>
          <tr>
            <th>日期</th>
            <th>股票代码</th>
            <th>股票名称</th>
            <th>操作</th>
            <th>价格</th>
            <th>数量</th>
            <th>盈亏</th>
            <th>盈亏比例</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="trade in trades" :key="trade.date + trade.code">
            <td>{{ trade.date }}</td>
            <td style="font-family: var(--artdeco-font-mono);">{{ trade.code }}</td>
            <td>{{ trade.name }}</td>
            <td>
              <span :style="{ color: trade.action === '买入' ? 'var(--artdeco-rise)' : 'var(--artdeco-fall)' }">
                {{ trade.action }}
              </span>
            </td>
            <td style="font-family: var(--artdeco-font-mono); text-align: right;">
              {{ trade.price.toFixed(2) }}
            </td>
            <td style="font-family: var(--artdeco-font-mono); text-align: right;">
              {{ trade.quantity }}
            </td>
            <td
              style="font-family: var(--artdeco-font-mono); text-align: right;"
              :class="trade.profit >= 0 ? 'artdeco-data-rise' : 'artdeco-data-fall'"
            >
              {{ trade.profit >= 0 ? '+' : '' }}{{ trade.profit.toFixed(2) }}
            </td>
            <td
              style="font-family: var(--artdeco-font-mono); text-align: right;"
              :class="trade.profitRatio >= 0 ? 'artdeco-data-rise' : 'artdeco-data-fall'"
            >
              {{ trade.profitRatio >= 0 ? '+' : '' }}{{ trade.profitRatio.toFixed(2) }}%
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'

// Types
interface BacktestMetrics {
  totalReturn: number
  sharpe: number
  maxDrawdown: number
  winRate: number
}

interface Trade {
  date: string
  code: string
  name: string
  action: '买入' | '卖出'
  price: number
  quantity: number
  profit: number
  profitRatio: number
}

// State
const backtestMetrics = ref<BacktestMetrics>({
  totalReturn: 23.5,
  sharpe: 1.85,
  maxDrawdown: -8.2,
  winRate: 67.8
})

const trades = ref<Trade[]>([
  { date: '2024-01-15', code: '600519.SH', name: '贵州茅台', action: '买入', price: 1678.50, quantity: 100, profit: 12560, profitRatio: 7.5 },
  { date: '2024-02-20', code: '000858.SZ', name: '五粮液', action: '买入', price: 156.78, quantity: 500, profit: -3240, profitRatio: -4.1 },
  { date: '2024-03-10', code: '600036.SH', name: '招商银行', action: '买入', price: 32.45, quantity: 2000, profit: 8920, profitRatio: 13.7 },
  { date: '2024-04-05', code: '600519.SH', name: '贵州茅台', action: '卖出', price: 1756.80, quantity: 100, profit: 7830, profitRatio: 4.7 },
  { date: '2024-05-12', code: '000001.SZ', name: '平安银行', action: '买入', price: 12.34, quantity: 5000, profit: 2340, profitRatio: 3.8 }
])

// Chart refs
const equityChartRef = ref<HTMLElement>()
const drawdownChartRef = ref<HTMLElement>()
let equityChart: echarts.ECharts | null = null
let drawdownChart: echarts.ECharts | null = null

// Methods
function initEquityChart() {
  if (!equityChartRef.value) return

  equityChart = echarts.init(equityChartRef.value)

  const option: EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月'],
      axisLine: { lineStyle: { color: '#D4AF37' } },
      axisLabel: { color: '#8B9BB4' }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#D4AF37' } },
      axisLabel: {
        color: '#8B9BB4',
        formatter: '{value}%'
      },
      splitLine: { lineStyle: { color: 'rgba(212, 175, 55, 0.1)' } }
    },
    series: [{
      type: 'line',
      data: [0, 5.6, 12.3, 18.9, 15.6, 23.5],
      smooth: true,
      lineStyle: { color: '#D4AF37', width: 3 },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(212, 175, 55, 0.3)' },
            { offset: 1, color: 'rgba(212, 175, 55, 0.05)' }
          ]
        }
      }
    }]
  }

  equityChart.setOption(option)
}

function initDrawdownChart() {
  if (!drawdownChartRef.value) return

  drawdownChart = echarts.init(drawdownChartRef.value)

  const option: EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月'],
      axisLine: { lineStyle: { color: '#D4AF37' } },
      axisLabel: { color: '#8B9BB4' }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#D4AF37' } },
      axisLabel: {
        color: '#8B9BB4',
        formatter: '{value}%'
      },
      splitLine: { lineStyle: { color: 'rgba(212, 175, 55, 0.1)' } }
    },
    series: [{
      type: 'line',
      data: [0, -2.3, -5.6, -8.2, -6.4, -4.1],
      smooth: true,
      lineStyle: { color: '#C94042', width: 2 },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(201, 64, 66, 0.3)' },
            { offset: 1, color: 'rgba(201, 64, 66, 0.05)' }
          ]
        }
      }
    }]
  }

  drawdownChart.setOption(option)
}

// Lifecycle
onMounted(() => {
  initEquityChart()
  initDrawdownChart()

  window.addEventListener('resize', () => {
    equityChart?.resize()
    drawdownChart?.resize()
  })
})

onUnmounted(() => {
  equityChart?.dispose()
  drawdownChart?.dispose()
})
</script>

<style scoped>
@import '@/styles/artdeco/artdeco-theme.css';

.artdeco-backtest-arena {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-space-lg);
}

.artdeco-grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--artdeco-space-lg);
}

.artdeco-grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--artdeco-space-lg);
}

.artdeco-card {
  background: var(--artdeco-bg-card);
  border: 2px solid var(--artdeco-gold-primary);
  padding: var(--artdeco-space-lg);
  position: relative;
}

.artdeco-card::before {
  content: '';
  position: absolute;
  top: 4px;
  left: 4px;
  right: 4px;
  bottom: 4px;
  border: 1px solid rgba(212, 175, 55, 0.3);
  pointer-events: none;
}

.artdeco-card h3 {
  font-family: var(--artdeco-font-display);
  font-size: 1rem;
  font-weight: 600;
  color: var(--artdeco-gold-primary);
  margin-bottom: var(--artdeco-space-md);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.artdeco-stat-value {
  font-size: 2.5rem;
  font-family: var(--artdeco-font-mono);
  font-weight: 700;
  color: var(--artdeco-gold-primary);
  margin-bottom: var(--artdeco-space-xs);
}

.artdeco-stat-label {
  font-size: 0.875rem;
  color: var(--artdeco-silver-dim);
}

.artdeco-chart-container {
  width: 100%;
  height: 400px;
}

.artdeco-table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--artdeco-font-mono);
  font-size: 0.875rem;
}

.artdeco-table th {
  background: var(--artdeco-bg-header);
  color: var(--artdeco-gold-primary);
  font-family: var(--artdeco-font-display);
  font-weight: 600;
  text-align: left;
  padding: 12px var(--artdeco-space-md);
  border-bottom: 2px solid var(--artdeco-gold-primary);
}

.artdeco-table td {
  padding: 12px var(--artdeco-space-md);
  border-bottom: 1px solid var(--artdeco-gold-dim);
  color: var(--artdeco-silver-text);
}

.artdeco-table tr:hover td {
  background: var(--artdeco-bg-hover);
}

.artdeco-data-rise {
  color: var(--artdeco-rise);
}

.artdeco-data-fall {
  color: var(--artdeco-fall);
}

@media (max-width: 1440px) {
  .artdeco-grid-4 {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .artdeco-grid-2,
  .artdeco-grid-4 {
    grid-template-columns: 1fr;
  }
}
</style>
