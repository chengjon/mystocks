<template>
  <div class="artdeco-data-analysis">
    <!-- Filter Panel -->
    <ArtDecoCard title="筛选条件" class="artdeco-filter-panel">
      <div class="artdeco-filter-row">
        <span class="artdeco-filter-label">分析维度:</span>
        <select v-model="selectedDimension" class="artdeco-filter-select">
          <option value="market">市场整体</option>
          <option value="sector">行业分析</option>
          <option value="indicator">技术指标</option>
        </select>
      </div>

      <div class="artdeco-filter-row">
        <span class="artdeco-filter-label">时间范围:</span>
        <select v-model="selectedTimeRange" class="artdeco-filter-select">
          <option value="1d">近1日</option>
          <option value="1w">近1周</option>
          <option value="1m">近1月</option>
          <option value="3m">近3月</option>
        </select>

        <ArtDecoButton variant="solid" @click="applyFilters">
          分析
        </ArtDecoButton>
      </div>
    </ArtDecoCard>

    <!-- Charts Grid -->
    <div class="artdeco-grid-3">
      <ArtDecoCard title="涨跌分布" :hoverable="false">
        <div ref="riseFallChartRef" class="artdeco-chart-container"></div>
      </ArtDecoCard>

      <ArtDecoCard title="行业资金流向" :hoverable="false">
        <div ref="sectorFlowChartRef" class="artdeco-chart-container"></div>
      </ArtDecoCard>

      <ArtDecoCard title="技术指标分布" :hoverable="false">
        <div ref="indicatorChartRef" class="artdeco-chart-container"></div>
      </ArtDecoCard>
    </div>

    <!-- Indicator Details Table -->
    <ArtDecoCard title="技术指标明细" :hoverable="false">
      <div class="artdeco-table-wrapper">
        <table class="artdeco-table">
          <thead>
            <tr>
              <th>指标名称</th>
              <th>超买数量</th>
              <th>超买比例</th>
              <th>超卖数量</th>
              <th>超卖比例</th>
              <th>中性区域</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="indicator in indicatorDetails" :key="indicator.name">
              <td>{{ indicator.name }}</td>
              <td class="text-mono">{{ indicator.overboughtCount }}</td>
              <td :class="indicator.overboughtRatio > 30 ? 'data-rise' : ''">
                {{ indicator.overboughtRatio }}%
              </td>
              <td class="text-mono">{{ indicator.oversoldCount }}</td>
              <td :class="indicator.oversoldRatio > 30 ? 'data-fall' : ''">
                {{ indicator.oversoldRatio }}%
              </td>
              <td class="text-mono">{{ indicator.neutralRatio }}%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'
import ArtDecoCard from '@/components/artdeco/ArtDecoCard.vue'
import ArtDecoButton from '@/components/artdeco/ArtDecoButton.vue'

// Types
interface IndicatorDetail {
  name: string
  overboughtCount: number
  overboughtRatio: number
  oversoldCount: number
  oversoldRatio: number
  neutralRatio: number
}

// State
const selectedDimension = ref('market')
const selectedTimeRange = ref('1w')

const indicatorDetails = ref<IndicatorDetail[]>([
  { name: 'MACD', overboughtCount: 245, overboughtRatio: 20.4, oversoldCount: 156, oversoldRatio: 13.0, neutralRatio: 66.6 },
  { name: 'KDJ', overboughtCount: 312, overboughtRatio: 26.0, oversoldCount: 189, oversoldRatio: 15.8, neutralRatio: 58.2 },
  { name: 'RSI', overboughtCount: 198, overboughtRatio: 16.5, oversoldCount: 223, oversoldRatio: 18.6, neutralRatio: 64.9 },
  { name: 'BOLL', overboughtCount: 267, overboughtRatio: 22.3, oversoldCount: 145, oversoldRatio: 12.1, neutralRatio: 65.6 }
])

// Chart refs
const riseFallChartRef = ref<HTMLElement>()
const sectorFlowChartRef = ref<HTMLElement>()
const indicatorChartRef = ref<HTMLElement>()
let riseFallChart: echarts.ECharts | null = null
let sectorFlowChart: echarts.ECharts | null = null
let indicatorChart: echarts.ECharts | null = null

// Methods
function applyFilters() {
  console.log('Applying filters:', { dimension: selectedDimension.value, timeRange: selectedTimeRange.value })
  // Refresh charts with new data
}

function initRiseFallChart() {
  if (!riseFallChartRef.value) return

  riseFallChart = echarts.init(riseFallChartRef.value)

  const option: EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 18, 21, 0.95)',
      borderColor: '#D4AF37',
      borderWidth: 1,
      textStyle: { color: '#E5E4E2' }
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: [
        { value: 1245, name: '上涨', itemStyle: { color: '#C94042' } },
        { value: 856, name: '下跌', itemStyle: { color: '#3D9970' } },
        { value: 156, name: '平盘', itemStyle: { color: '#B8B8B8' } }
      ],
      label: {
        color: '#E5E4E2',
        fontFamily: 'Cinzel',
        formatter: '{b}: {c} ({d}%)'
      }
    }]
  }

  riseFallChart.setOption(option)
}

function initSectorFlowChart() {
  if (!sectorFlowChartRef.value) return

  sectorFlowChart = echarts.init(sectorFlowChartRef.value)

  const option: EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(15, 18, 21, 0.95)',
      borderColor: '#D4AF37',
      borderWidth: 1
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['科技', '医药', '消费', '金融', '地产', '能源'],
      axisLine: { lineStyle: { color: '#5C6B7F' } },
      axisLabel: {
        color: '#8B9BB4',
        fontFamily: 'Cinzel',
        interval: 0,
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#5C6B7F' } },
      axisLabel: {
        color: '#8B9BB4',
        formatter: '{value}亿'
      },
      splitLine: {
        lineStyle: { color: 'rgba(212, 175, 55, 0.1)' }
      }
    },
    series: [{
      type: 'bar',
      data: [
        { value: 125.6, itemStyle: { color: '#C94042' } },
        { value: 89.3, itemStyle: { color: '#3D9970' } },
        { value: 56.8, itemStyle: { color: '#C94042' } },
        { value: -34.5, itemStyle: { color: '#C94042' } },
        { value: -45.2, itemStyle: { color: '#C94042' } },
        { value: 67.9, itemStyle: { color: '#3D9970' } }
      ]
    }]
  }

  sectorFlowChart.setOption(option)
}

function initIndicatorChart() {
  if (!indicatorChartRef.value) return

  indicatorChart = echarts.init(indicatorChartRef.value)

  const option: EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 18, 21, 0.95)',
      borderColor: '#D4AF37',
      borderWidth: 1
    },
    legend: {
      data: ['PE分布', 'PB分布', '换手率分布'],
      textStyle: { color: '#8B9BB4' },
      top: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['<10', '10-20', '20-30', '30-50', '>50'],
      axisLine: { lineStyle: { color: '#5C6B7F' } },
      axisLabel: { color: '#8B9BB4' }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#5C6B7F' } },
      axisLabel: { color: '#8B9BB4' },
      splitLine: {
        lineStyle: { color: 'rgba(212, 175, 55, 0.1)' }
      }
    },
    series: [
      {
        name: 'PE分布',
        type: 'line',
        data: [120, 245, 389, 256, 145],
        smooth: true,
        lineStyle: { color: '#D4AF37' }
      },
      {
        name: 'PB分布',
        type: 'line',
        data: [234, 189, 156, 123, 89],
        smooth: true,
        lineStyle: { color: '#4A90E2' }
      },
      {
        name: '换手率分布',
        type: 'line',
        data: [456, 312, 234, 178, 95],
        smooth: true,
        lineStyle: { color: '#27AE60' }
      }
    ]
  }

  indicatorChart.setOption(option)
}

// Lifecycle
onMounted(() => {
  initRiseFallChart()
  initSectorFlowChart()
  initIndicatorChart()

  window.addEventListener('resize', () => {
    riseFallChart?.resize()
    sectorFlowChart?.resize()
    indicatorChart?.resize()
  })
})

onUnmounted(() => {
  riseFallChart?.dispose()
  sectorFlowChart?.dispose()
  indicatorChart?.dispose()
})
</script>

<style scoped>
@import '@/styles/artdeco/artdeco-theme.css';

.artdeco-data-analysis {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-space-section); /* 128px - Generous section spacing */
}

/* Filter Panel */
.artdeco-filter-panel {
  padding: var(--artdeco-space-xl);
}

.artdeco-filter-row {
  display: flex;
  gap: var(--artdeco-space-md);
  margin-bottom: var(--artdeco-space-md);
  align-items: center;
}

.artdeco-filter-row:last-child {
  margin-bottom: 0;
}

.artdeco-filter-label {
  font-family: var(--artdeco-font-display);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--artdeco-gold-primary);
  min-width: 100px;
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-tight);
}

.artdeco-filter-select {
  flex: 1;
  padding: 8px 12px;
  font-family: var(--artdeco-font-body);
  font-size: 0.875rem;
  color: var(--artdeco-text-primary);
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-gold-dim);
  border-radius: var(--artdeco-radius-none);
  transition: all var(--artdeco-transition-base);
}

.artdeco-filter-select:focus {
  outline: none;
  border-color: var(--artdeco-gold-primary);
  box-shadow: var(--artdeco-glow-subtle);
}

/* Charts Grid */
.artdeco-grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--artdeco-space-xl);
}

.artdeco-chart-container {
  width: 100%;
  height: 350px;
}

/* Table */
.artdeco-table-wrapper {
  overflow-x: auto;
}

.artdeco-table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--artdeco-font-mono);
  font-size: 0.875rem;
}

.artdeco-table thead th {
  position: sticky;
  top: 0;
  background: var(--artdeco-bg-header);
  color: var(--artdeco-gold-primary);
  font-family: var(--artdeco-font-display);
  font-weight: 600;
  text-align: left;
  padding: var(--artdeco-space-md);
  border-bottom: 2px solid var(--artdeco-gold-primary);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-tight);
  white-space: nowrap;
}

.artdeco-table tbody td {
  padding: var(--artdeco-space-md);
  border-bottom: 1px solid var(--artdeco-gold-dim);
  color: var(--artdeco-silver-text);
}

.artdeco-table tbody tr:hover td {
  background: var(--artdeco-bg-hover);
}

.text-mono {
  font-family: var(--artdeco-font-mono);
}

.data-rise {
  color: var(--artdeco-rise);
}

.data-fall {
  color: var(--artdeco-fall);
}

/* Responsive */
@media (max-width: 1440px) {
  .artdeco-grid-3 {
    grid-template-columns: repeat(2, 1fr);
  }

  .artdeco-data-analysis {
    gap: var(--artdeco-space-2xl); /* 64px on smaller screens */
  }
}

@media (max-width: 1080px) {
  .artdeco-data-analysis {
    gap: var(--artdeco-space-2xl); /* 64px */
  }
}

@media (max-width: 768px) {
  .artdeco-grid-3 {
    grid-template-columns: 1fr;
  }

  .artdeco-filter-row {
    flex-direction: column;
    align-items: stretch;
  }

  .artdeco-filter-label {
    min-width: auto;
  }

  .artdeco-chart-container {
    height: 280px;
  }
}
</style>
