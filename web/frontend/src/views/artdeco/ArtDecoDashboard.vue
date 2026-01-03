<template>
  <div class="artdeco-dashboard">
    <!-- Market Statistics Cards -->
    <div class="artdeco-stats-grid artdeco-stagger">
      <div class="artdeco-stat-card">
        <div class="artdeco-stat-label">上证综指</div>
        <div class="artdeco-stat-value">{{ formatNumber(marketData.shIndex) }}</div>
        <div class="artdeco-stat-change" :class="getChangeClass(marketData.shChange)">
          <span>{{ marketData.shChange >= 0 ? '▲' : '▼' }}</span>
          <span>{{ marketData.shChange >= 0 ? '+' : '' }}{{ marketData.shChange }}%</span>
        </div>
      </div>

      <div class="artdeco-stat-card">
        <div class="artdeco-stat-label">深证成指</div>
        <div class="artdeco-stat-value">{{ formatNumber(marketData.szIndex) }}</div>
        <div class="artdeco-stat-change" :class="getChangeClass(marketData.szChange)">
          <span>{{ marketData.szChange >= 0 ? '▲' : '▼' }}</span>
          <span>{{ marketData.szChange >= 0 ? '+' : '' }}{{ marketData.szChange }}%</span>
        </div>
      </div>

      <div class="artdeco-stat-card">
        <div class="artdeco-stat-label">创业板指</div>
        <div class="artdeco-stat-value">{{ formatNumber(marketData.cybIndex) }}</div>
        <div class="artdeco-stat-change" :class="getChangeClass(marketData.cybChange)">
          <span>{{ marketData.cybChange >= 0 ? '▲' : '▼' }}</span>
          <span>{{ marketData.cybChange >= 0 ? '+' : '' }}{{ marketData.cybChange }}%</span>
        </div>
      </div>

      <div class="artdeco-stat-card">
        <div class="artdeco-stat-label">北向资金</div>
        <div class="artdeco-stat-value">{{ marketData.northFlow >= 0 ? '+' : '' }}{{ marketData.northFlow }}亿</div>
        <div class="artdeco-stat-change" :class="marketData.northFlow >= 0 ? 'data-rise' : 'data-fall'">
          <span>{{ marketData.northFlow >= 0 ? '▲' : '▼' }}</span>
          <span>{{ marketData.northFlow >= 0 ? '净流入' : '净流出' }}</span>
        </div>
      </div>
    </div>

    <!-- Two Column Layout -->
    <div class="artdeco-two-column">
      <!-- Main Chart -->
      <div class="artdeco-card artdeco-fade-in">
        <div class="artdeco-card-header">
          <h3>三大指数分时走势</h3>
          <div class="artdeco-btn-group">
            <button
              v-for="index in indexTypes"
              :key="index.key"
              class="artdeco-btn artdeco-btn-secondary"
              :class="{ active: activeIndex === index.key }"
              @click="activeIndex = index.key"
            >
              {{ index.label }}
            </button>
          </div>
        </div>
        <div ref="mainChartRef" class="artdeco-chart"></div>
      </div>

      <!-- Market Heatmap -->
      <div class="artdeco-card artdeco-fade-in" style="animation-delay: 0.2s;">
        <h3>板块热度</h3>
        <div ref="heatmapChartRef" class="artdeco-chart"></div>
      </div>
    </div>

    <!-- Bottom Row -->
    <div class="artdeco-bottom-row">
      <!-- Limit Up/Down Stats -->
      <div class="artdeco-card artdeco-fade-in" style="animation-delay: 0.3s;">
        <h3>涨跌停统计</h3>
        <div class="artdeco-stats-triple">
          <div>
            <div class="artdeco-stat-label">涨停</div>
            <div class="artdeco-stat-value data-rise" style="font-size: 1.5rem;">{{ limitStats.limitUp }}</div>
          </div>
          <div>
            <div class="artdeco-stat-label">跌停</div>
            <div class="artdeco-stat-value data-fall" style="font-size: 1.5rem;">{{ limitStats.limitDown }}</div>
          </div>
          <div>
            <div class="artdeco-stat-label">平盘</div>
            <div class="artdeco-stat-value data-flat" style="font-size: 1.5rem;">{{ limitStats.flat }}</div>
          </div>
        </div>
      </div>

      <!-- Data Source Status -->
      <div class="artdeco-card artdeco-fade-in" style="animation-delay: 0.4s;">
        <h3>数据源状态</h3>
        <table class="artdeco-table">
          <thead>
            <tr>
              <th>数据源</th>
              <th>状态</th>
              <th>延迟</th>
              <th>最后更新</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="source in dataSources" :key="source.name">
              <td>{{ source.name }}</td>
              <td>
                <span class="artdeco-badge" :class="source.status === 'online' ? 'artdeco-badge-gold' : 'artdeco-badge-silver'">
                  {{ source.status === 'online' ? '在线' : '离线' }}
                </span>
              </td>
              <td class="text-mono">{{ source.latency }}</td>
              <td class="text-mono text-dim">{{ source.lastUpdate }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'

// Types
interface MarketData {
  shIndex: number
  shChange: number
  szIndex: number
  szChange: number
  cybIndex: number
  cybChange: number
  northFlow: number
}

interface LimitStats {
  limitUp: number
  limitDown: number
  flat: number
}

interface DataSource {
  name: string
  status: 'online' | 'offline'
  latency: string
  lastUpdate: string
}

// State
const marketData = ref<MarketData>({
  shIndex: 3245.67,
  shChange: 1.23,
  szIndex: 10892.45,
  szChange: -0.56,
  cybIndex: 2156.78,
  cybChange: 2.15,
  northFlow: 89.5
})

const limitStats = ref<LimitStats>({
  limitUp: 47,
  limitDown: 12,
  flat: 8
})

const dataSources = ref<DataSource[]>([
  { name: 'AKShare', status: 'online', latency: '23ms', lastUpdate: '刚刚' },
  { name: 'Tushare', status: 'online', latency: '45ms', lastUpdate: '5秒前' },
  { name: '通达信', status: 'online', latency: '12ms', lastUpdate: '刚刚' },
  { name: '北向资金', status: 'online', latency: '67ms', lastUpdate: '10秒前' }
])

const activeIndex = ref('sh')
const indexTypes = [
  { key: 'sh', label: '上证' },
  { key: 'sz', label: '深证' },
  { key: 'cyb', label: '创业板' }
]

// Chart refs
const mainChartRef = ref<HTMLElement>()
const heatmapChartRef = ref<HTMLElement>()
let mainChart: echarts.ECharts | null = null
let heatmapChart: echarts.ECharts | null = null
let refreshInterval: number | null = null

// Methods
function formatNumber(num: number): string {
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function getChangeClass(change: number): string {
  if (change > 0) return 'data-rise'
  if (change < 0) return 'data-fall'
  return 'data-flat'
}

function initMainChart() {
  if (!mainChartRef.value) return

  mainChart = echarts.init(mainChartRef.value)

  const option: EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(20, 20, 20, 0.95)', /* Rich Charcoal */
      borderColor: '#D4AF37',
      borderWidth: 2, /* Thicker border */
      textStyle: {
        color: '#F2F0E4', /* Champagne Cream */
        fontFamily: 'JetBrains Mono'
      }
    },
    legend: {
      data: ['上证综指', '深证成指', '创业板指'],
      textStyle: {
        color: '#888888', /* Pewter */
        fontFamily: 'Marcellus', /* Art Deco display font */
        fontSize: 14
      },
      top: 10,
      itemGap: 20
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
      data: ['9:30', '10:00', '10:30', '11:00', '11:30', '13:00', '13:30', '14:00', '14:30', '15:00'],
      axisLine: {
        lineStyle: { color: '#5C6B7F', width: 2 }
      },
      axisLabel: {
        color: '#888888', /* Pewter */
        fontFamily: 'JetBrains Mono',
        fontSize: 12
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: { color: '#5C6B7F', width: 2 }
      },
      axisLabel: {
        color: '#888888', /* Pewter */
        fontFamily: 'JetBrains Mono',
        fontSize: 12
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(212, 175, 55, 0.15)', /* More visible gold */
          type: 'dashed',
          width: 1
        }
      }
    },
    series: [
      {
        name: '上证综指',
        type: 'line',
        smooth: true,
        data: [3220, 3235, 3240, 3238, 3242, 3245, 3248, 3246, 3244, 3245.67],
        lineStyle: {
          color: '#D4AF37',
          width: 2
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(212, 175, 55, 0.3)' },
              { offset: 1, color: 'rgba(212, 175, 55, 0)' }
            ]
          }
        }
      },
      {
        name: '深证成指',
        type: 'line',
        smooth: true,
        data: [10850, 10870, 10880, 10875, 10885, 10890, 10892, 10890, 10891, 10892.45],
        lineStyle: {
          color: '#4A90E2',
          width: 2
        }
      },
      {
        name: '创业板指',
        type: 'line',
        smooth: true,
        data: [2140, 2145, 2150, 2148, 2152, 2154, 2156, 2155, 2157, 2156.78],
        lineStyle: {
          color: '#27AE60',
          width: 2
        }
      }
    ]
  }

  mainChart.setOption(option)
}

function initHeatmapChart() {
  if (!heatmapChartRef.value) return

  heatmapChart = echarts.init(heatmapChartRef.value)

  const data = [
    [0, 0, 3.45], [0, 1, 2.78], [1, 0, 2.12], [1, 1, 1.89],
    [2, 0, -0.45], [2, 1, -1.23], [3, 0, -2.15], [3, 1, 0.67]
  ]

  const option: EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      position: 'top',
      backgroundColor: 'rgba(20, 20, 20, 0.95)', /* Rich Charcoal */
      borderColor: '#D4AF37',
      borderWidth: 2,
      textStyle: {
        color: '#F2F0E4', /* Champagne Cream */
        fontFamily: 'JetBrains Mono'
      }
    },
    grid: {
      height: '70%',
      top: '5%'
    },
    xAxis: {
      type: 'category',
      data: ['科技', '消费', '金融', '周期'],
      splitArea: { show: true },
      axisLine: { lineStyle: { color: '#5C6B7F', width: 2 } },
      axisLabel: {
        color: '#888888', /* Pewter */
        fontFamily: 'Marcellus', /* Art Deco font */
        fontSize: 14
      }
    },
    yAxis: {
      type: 'category',
      data: ['强势', '弱势'],
      splitArea: { show: true },
      axisLine: { lineStyle: { color: '#5C6B7F', width: 2 } },
      axisLabel: {
        color: '#888888', /* Pewter */
        fontFamily: 'Marcellus', /* Art Deco font */
        fontSize: 14
      }
    },
    visualMap: {
      min: -3,
      max: 4,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0%',
      textStyle: {
        color: '#888888', /* Pewter */
        fontFamily: 'Marcellus', /* Art Deco font */
        fontSize: 12
      },
      inRange: {
        color: ['#3D9970', '#B8B8B8', '#C94042']
      }
    },
    series: [{
      name: '涨跌幅',
      type: 'heatmap',
      data: data,
      label: {
        show: true,
        formatter: '{c}%',
        fontFamily: 'JetBrains Mono',
        color: '#E5E4E2'
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(212, 175, 55, 0.5)'
        }
      }
    }]
  }

  heatmapChart.setOption(option)
}

// Lifecycle
onMounted(() => {
  initMainChart()
  initHeatmapChart()

  // Auto-refresh every 3 seconds
  refreshInterval = window.setInterval(() => {
    // Simulate data update
    marketData.value.shIndex += (Math.random() - 0.5) * 2
    marketData.value.shChange = +(Math.random() * 4 - 2).toFixed(2)
  }, 3000)

  // Handle window resize
  window.addEventListener('resize', () => {
    mainChart?.resize()
    heatmapChart?.resize()
  })
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
  mainChart?.dispose()
  heatmapChart?.dispose()
})
</script>

<style scoped>
@import '@/styles/artdeco/artdeco-theme.css';

.artdeco-dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-space-section); /* 128px - Generous section spacing */
}

/* Stats Grid */
.artdeco-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--artdeco-space-xl); /* 48px - Increased gap */
}

.artdeco-stat-card {
  background: var(--artdeco-bg-card);
  border: 2px solid var(--artdeco-gold-dim); /* Thicker border */
  padding: var(--artdeco-space-xl); /* 48px - Generous padding */
  position: relative;
  overflow: hidden;
  transition: all var(--artdeco-transition-slow); /* 500ms theatrical */
}

/* Double-frame effect */
.artdeco-stat-card::before {
  content: '';
  position: absolute;
  top: 6px;
  left: 6px;
  right: 6px;
  bottom: 6px;
  border: 1px solid var(--artdeco-gold-primary);
  opacity: 0.2;
  pointer-events: none;
}

/* Hover effect - Theatrical */
.artdeco-stat-card:hover {
  border-color: var(--artdeco-gold-primary);
  box-shadow: var(--artdeco-glow-subtle);
  transform: translateY(-2px);
}

.artdeco-stat-label {
  font-family: var(--artdeco-font-display); /* Marcellus */
  font-size: 0.875rem; /* Increased from 0.75rem */
  font-weight: 600;
  color: var(--artdeco-text-dim); /* Pewter */
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-display); /* 0.2em - Wide tracking */
  margin-bottom: var(--artdeco-space-md); /* 16px */
}

.artdeco-stat-value {
  font-family: var(--artdeco-font-mono); /* JetBrains Mono */
  font-size: 2.5rem; /* Increased from 2rem */
  font-weight: 600;
  color: var(--artdeco-gold-primary);
  line-height: 1;
  margin-bottom: var(--artdeco-space-sm);
}

.artdeco-stat-change {
  font-family: var(--artdeco-font-mono);
  font-size: 1rem; /* Increased from 0.875rem */
  display: flex;
  align-items: center;
  gap: var(--artdeco-space-sm);
}

.artdeco-stats-triple {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--artdeco-space-lg); /* 32px */
  text-align: center;
}

/* Two Column Layout */
.artdeco-two-column {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--artdeco-space-xl); /* 48px */
}

.artdeco-bottom-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--artdeco-space-xl); /* 48px */
}

/* Card */
.artdeco-card {
  background: var(--artdeco-bg-card);
  border: 2px solid var(--artdeco-gold-dim); /* Thicker border */
  padding: var(--artdeco-space-xl); /* 48px - Generous padding */
  position: relative;
  transition: all var(--artdeco-transition-slow);
}

/* Double-frame effect for cards */
.artdeco-card::before {
  content: '';
  position: absolute;
  top: 6px;
  left: 6px;
  right: 6px;
  bottom: 6px;
  border: 1px solid var(--artdeco-gold-primary);
  opacity: 0.2;
  pointer-events: none;
}

.artdeco-card:hover {
  border-color: var(--artdeco-gold-primary);
  box-shadow: var(--artdeco-glow-subtle);
}

.artdeco-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-space-xl); /* 48px - More breathing room */
  position: relative;
  z-index: 1;
}

/* Decorative divider after header */
.artdeco-card-header::after {
  content: '';
  position: absolute;
  bottom: -24px;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(
    to right,
    transparent,
    var(--artdeco-gold-primary) 30%,
    var(--artdeco-gold-primary) 70%,
    transparent
  );
  opacity: 0.3;
}

.artdeco-card-header h3 {
  margin: 0;
  font-family: var(--artdeco-font-display); /* Marcellus */
  font-size: 1.25rem; /* Increased from 1rem */
  color: var(--artdeco-gold-primary);
  letter-spacing: var(--artdeco-tracking-display); /* 0.2em */
  text-transform: uppercase;
}

.artdeco-btn-group {
  display: flex;
  gap: var(--artdeco-space-md); /* 16px */
}

.artdeco-chart {
  height: 400px; /* Increased from 320px */
}

/* Responsive */
@media (max-width: 1440px) {
  .artdeco-stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1080px) {
  .artdeco-two-column {
    grid-template-columns: 1fr;
  }

  .artdeco-bottom-row {
    grid-template-columns: 1fr;
  }

  .artdeco-dashboard {
    gap: var(--artdeco-space-2xl); /* 64px on smaller screens */
  }
}

@media (max-width: 768px) {
  .artdeco-stats-grid {
    grid-template-columns: 1fr;
  }

  .artdeco-chart {
    height: 320px;
  }
}
</style>
