<template>
  <div class="artdeco-risk-center">
    <!-- Risk Metrics -->
    <div class="artdeco-grid-4">
      <div class="artdeco-card">
        <div class="artdeco-stat-value" style="color: var(--artdeco-success);">低</div>
        <div class="artdeco-stat-label">风险等级</div>
      </div>
      <div class="artdeco-card">
        <div class="artdeco-stat-value artdeco-data-fall">{{ riskMetrics.currentDrawdown }}%</div>
        <div class="artdeco-stat-label">当前回撤</div>
      </div>
      <div class="artdeco-card">
        <div class="artdeco-stat-value" style="color: var(--artdeco-gold-primary);">{{ riskMetrics.positionRatio }}%</div>
        <div class="artdeco-stat-label">仓位比例</div>
      </div>
      <div class="artdeco-card">
        <div class="artdeco-stat-value">{{ riskMetrics.concentration }}</div>
        <div class="artdeco-stat-label">集中度</div>
      </div>
    </div>

    <!-- Risk Charts -->
    <div class="artdeco-grid-2">
      <div class="artdeco-card">
        <h3>回撤分析</h3>
        <div ref="drawdownChartRef" class="artdeco-chart-container"></div>
      </div>
      <div class="artdeco-card">
        <h3>仓位分布</h3>
        <div ref="positionChartRef" class="artdeco-chart-container"></div>
      </div>
    </div>

    <!-- Risk Alerts -->
    <div class="artdeco-card">
      <h3>风险预警</h3>
      <table class="artdeco-table">
        <thead>
          <tr>
            <th>预警时间</th>
            <th>预警类型</th>
            <th>预警内容</th>
            <th>风险等级</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="alert in riskAlerts" :key="alert.time">
            <td style="font-family: var(--artdeco-font-mono);">{{ alert.time }}</td>
            <td>{{ alert.type }}</td>
            <td>{{ alert.content }}</td>
            <td>
              <span
                class="artdeco-badge"
                :class="alert.level === 'danger' ? 'artdeco-badge-danger' : alert.level === 'warning' ? 'artdeco-badge-warning' : 'artdeco-badge-success'"
              >
                {{ alert.level === 'danger' ? '高危' : alert.level === 'warning' ? '警告' : '提示' }}
              </span>
            </td>
            <td>
              <span
                class="artdeco-badge"
                :class="alert.status === 'pending' ? 'artdeco-badge-warning' : 'artdeco-badge-success'"
              >
                {{ alert.status === 'pending' ? '待处理' : '已处理' }}
              </span>
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
interface RiskMetrics {
  riskLevel: string
  currentDrawdown: number
  positionRatio: number
  concentration: number
}

interface RiskAlert {
  time: string
  type: string
  content: string
  level: 'danger' | 'warning' | 'info'
  status: 'pending' | 'resolved'
}

// State
const riskMetrics = ref<RiskMetrics>({
  riskLevel: '低',
  currentDrawdown: -8.2,
  positionRatio: 65.8,
  concentration: 5.2
})

const riskAlerts = ref<RiskAlert[]>([
  { time: '2024-01-15 09:35:22', type: '仓位预警', content: '单只股票仓位超过20%', level: 'warning', status: 'pending' },
  { time: '2024-01-15 10:12:45', type: '回撤预警', content: '组合回撤接近风控线-8%', level: 'danger', status: 'resolved' },
  { time: '2024-01-15 13:45:08', type: '波动率预警', content: '市场波动率异常上升', level: 'warning', status: 'pending' },
  { time: '2024-01-15 14:20:15', type: '集中度预警', content: '行业集中度过高', level: 'info', status: 'resolved' }
])

// Chart refs
const drawdownChartRef = ref<HTMLElement>()
const positionChartRef = ref<HTMLElement>()
let drawdownChart: echarts.ECharts | null = null
let positionChart: echarts.ECharts | null = null

// Methods
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
      data: [0, -3.2, -6.5, -8.2, -5.8, -4.1],
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

function initPositionChart() {
  if (!positionChartRef.value) return

  positionChart = echarts.init(positionChartRef.value)

  const option: EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}% ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: { color: '#E5E4E2' }
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['35%', '50%'],
      data: [
        { value: 25, name: '消费', itemStyle: { color: '#D4AF37' } },
        { value: 20, name: '金融', itemStyle: { color: '#C94042' } },
        { value: 15, name: '科技', itemStyle: { color: '#3D9970' } },
        { value: 18, name: '医药', itemStyle: { color: '#4A90E2' } },
        { value: 12, name: '新能源', itemStyle: { color: '#E67E22' } },
        { value: 10, name: '现金', itemStyle: { color: '#8B9BB4' } }
      ],
      label: {
        color: '#E5E4E2',
        formatter: '{b}\n{c}%'
      },
      labelLine: {
        lineStyle: { color: '#D4AF37' }
      }
    }]
  }

  positionChart.setOption(option)
}

// Lifecycle
onMounted(() => {
  initDrawdownChart()
  initPositionChart()

  window.addEventListener('resize', () => {
    drawdownChart?.resize()
    positionChart?.resize()
  })
})

onUnmounted(() => {
  drawdownChart?.dispose()
  positionChart?.dispose()
})
</script>

<style scoped>
@import '@/styles/artdeco/artdeco-theme.css';

.artdeco-risk-center {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-space-lg);
}

.artdeco-grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--artdeco-space-lg);
}

.artdeco-grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
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
  font-size: 2rem;
  font-family: var(--artdeco-font-mono);
  font-weight: 700;
  margin-bottom: var(--artdeco-space-xs);
}

.artdeco-stat-label {
  font-size: 0.875rem;
  color: var(--artdeco-silver-dim);
}

.artdeco-chart-container {
  width: 100%;
  height: 350px;
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

.artdeco-badge {
  display: inline-block;
  padding: 4px 12px;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 2px;
}

.artdeco-badge-success {
  background: var(--artdeco-success);
  color: white;
}

.artdeco-badge-warning {
  background: var(--artdeco-warning);
  color: white;
}

.artdeco-badge-danger {
  background: var(--artdeco-danger);
  color: white;
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
