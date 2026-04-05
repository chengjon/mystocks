<template>
  <div class="card demo-card">
    <div class="card-header">
      <span class="card-title">🔥 股票热力图（ECharts）</span>
      <span class="badge badge-success">已集成</span>
    </div>

    <div class="heatmap-section">
      <div class="controls-row">
        <div class="radio-group">
          <label
            class="radio-btn"
            :class="{ active: heatmapMarket === 'cn' }"
            @click="heatmapMarket = 'cn'; loadHeatmapData()"
          >
            中国A股
          </label>
          <label
            class="radio-btn"
            :class="{ active: heatmapMarket === 'hk' }"
            @click="heatmapMarket = 'hk'; loadHeatmapData()"
          >
            港股
          </label>
        </div>
        <button class="btn btn-primary" @click="loadHeatmapData" :disabled="heatmapLoading">
          <span v-if="heatmapLoading" class="loading-spinner"></span>
          {{ heatmapLoading ? '加载中...' : '刷新数据' }}
        </button>
      </div>

      <div
        ref="heatmapContainerRef"
        class="echarts-heatmap-container"
        :class="{ loading: heatmapLoading }"
      >
        <div v-if="heatmapLoading" class="loading-overlay">
          <div class="loading-text">加载热力图中...</div>
        </div>
      </div>

      <div class="alert-info">
        <div class="alert-content">
          <strong>股票热力图说明</strong>
          <p>使用 ECharts 实现的股票市场热力图，实时展示各板块和个股的涨跌情况。</p>
          <ul class="info-list">
            <li>方块大小代表市值或成交额，颜色深浅代表涨跌幅度</li>
            <li>红色表示上涨，绿色表示下跌（符合中国股市习惯）</li>
            <li>支持中国A股和港股市场切换</li>
            <li>鼠标悬停可查看详细信息</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import echarts from '@/utils/echarts'

// Type definitions
interface HeatmapItem {
  name: string
  symbol: string
  price: number
  change: number
  change_pct: number
  volume: number
  market_cap?: number
}

interface ApiErrorResponse {
  response?: {
    status?: number
    data?: {
      detail?: string
    }
  }
  message?: string
}

const emit = defineEmits<{
  'api-tested': [feature: string]
}>()

const heatmapMarket = ref('cn')
const heatmapLoading = ref(false)
const heatmapContainerRef = ref<HTMLElement | null>(null)
let heatmapChart: echarts.ECharts | null = null
let heatmapResizeHandler: (() => void) | null = null

const initHeatmapChart = () => {
  if (!heatmapContainerRef.value) return
  if (heatmapChart) {
    heatmapChart.dispose()
  }
  heatmapChart = echarts.init(heatmapContainerRef.value)
  heatmapResizeHandler = () => {
    if (heatmapChart) heatmapChart.resize()
  }
  window.addEventListener('resize', heatmapResizeHandler)
}

const loadHeatmapData = async () => {
  heatmapLoading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const API_BASE = '/api'
    const response = await axios.get(`${API_BASE}/market/heatmap`, {
      params: { market: heatmapMarket.value },
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!response.data || response.data.length === 0) {
      ElMessage.warning('暂无热力图数据')
      return
    }
    renderHeatmap(response.data)
    emit('api-tested', 'heatmap')
    ElMessage.success('热力图加载成功')
  } catch (error: unknown) {
    console.error('加载热力图失败:', error)
    const apiError = error as ApiErrorResponse
    if (apiError.response?.status === 404) {
      ElMessage.warning('热力图API未实现，使用模拟数据展示')
      renderHeatmap(generateMockHeatmapData())
    } else {
      ElMessage.error('加载热力图失败: ' + (apiError.response?.data?.detail || apiError.message || '未知错误'))
    }
  } finally {
    heatmapLoading.value = false
  }
}

const renderHeatmap = (data: HeatmapItem[]) => {
  if (!heatmapChart || !data || data.length === 0) return
  const treeData = {
    name: heatmapMarket.value === 'cn' ? 'A股市场' : '港股市场',
    children: data.map(item => ({
      name: item.name,
      value: item.change_pct,
      symbol: item.symbol,
      price: item.price,
      change: item.change,
      volume: item.volume,
      market_cap: item.market_cap
    }))
  }
  const option = {
    title: {
      text: heatmapMarket.value === 'cn' ? '中国A股市场热力图' : '港股市场热力图',
      left: 'center',
      textStyle: { color: '#333', fontSize: 18 }
    },
    tooltip: {
      formatter: (info: { data: { name: string; symbol?: string; value?: number; price?: number; change?: number; market_cap?: number } }) => {
        const data = info.data
        if (!data) return ''
        return [
          `<div style="font-weight: bold; margin-bottom: 5px;">${data.name} (${data.symbol || '-'})</div>`,
          `涨跌幅: <span style="color: ${data.value && data.value >= 0 ? '#ef5350' : '#26a69a'};">${data.value && data.value >= 0 ? '+' : ''}${data.value?.toFixed(2) || 0}%</span>`,
          `当前价: ${data.price?.toFixed(2) || '-'}`,
          `涨跌额: ${data.change && data.change >= 0 ? '+' : ''}${data.change?.toFixed(2) || '-'}`,
          data.market_cap ? `市值: ${(data.market_cap / 100000000).toFixed(2)}亿` : ''
        ].filter(Boolean).join('<br/>')
      }
    },
    series: [{
      type: 'treemap',
      data: treeData.children,
      width: '100%',
      height: '100%',
      label: { show: true, formatter: '{b}\n{c}%', fontSize: 12 },
      upperLabel: { show: true, height: 30, color: '#fff' },
      itemStyle: { borderColor: '#fff', borderWidth: 2, gapWidth: 2 },
      visualDimension: 'value',
      visualMin: -10,
      visualMax: 10,
      colorMappingBy: 'value',
      colorAlpha: [0.8, 1],
      colorSaturation: [0.3, 0.7],
      color: (params: { value?: number }) => {
        const value = params.value || 0
        if (value > 5) return '#d32f2f'
        if (value > 2) return '#ef5350'
        if (value > 0) return '#ffcdd2'
        if (value === 0) return '#e0e0e0'
        if (value > -2) return '#a5d6a7'
        if (value > -5) return '#66bb6a'
        return '#2e7d32'
      }
    }]
  }
  heatmapChart.setOption(option)
}

const generateMockHeatmapData = (): HeatmapItem[] => {
  const sectors = ['金融', '科技', '医药', '消费', '能源', '制造', '房地产', '通信']
  const data: HeatmapItem[] = []
  for (let i = 0; i < 30; i++) {
    const sector = sectors[Math.floor(Math.random() * sectors.length)]
    const changePct = (Math.random() - 0.5) * 20
    data.push({
      name: `${sector}${i + 1}`,
      symbol: `${(600000 + i).toString().padStart(6, '0')}`,
      price: 10 + Math.random() * 90,
      change: changePct * 0.1,
      change_pct: changePct,
      volume: Math.floor(Math.random() * 1000000),
      market_cap: Math.floor(Math.random() * 10000000000)
    })
  }
  return data
}

onMounted(() => {
  setTimeout(() => {
    initHeatmapChart()
    loadHeatmapData()
  }, 500)
})

onUnmounted(() => {
  if (heatmapChart) {
    if (heatmapResizeHandler) {
      window.removeEventListener('resize', heatmapResizeHandler)
      heatmapResizeHandler = null
    }
    heatmapChart.dispose()
    heatmapChart = null
  }
})
</script>

<style scoped lang="scss">
@use '../../../../styles/artdeco-tokens.scss' as *;

.heatmap-section {
  padding: var(--artdeco-spacing-3) 0;
}

.controls-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-5);
}

.radio-group {
  display: flex;
  background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);
  overflow: hidden;

  .radio-btn {
    padding: var(--artdeco-spacing-2) var(--artdeco-spacing-5);
    font-size: var(--artdeco-text-sm);
    color: var(--artdeco-fg-muted);
    cursor: pointer;
    transition:
      background var(--artdeco-transition-quick) var(--artdeco-ease-out),
      color var(--artdeco-transition-quick) var(--artdeco-ease-out);
    border-right: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);

    &:last-child {
      border-right: none;
    }

    &:hover {
      background: color-mix(in srgb, var(--artdeco-gold-primary) 5%, transparent);
    }

    &.active {
      background: var(--artdeco-gold-primary);
      color: var(--artdeco-bg-global);
    }
  }
}

.echarts-heatmap-container {
  width: 100%;
  height: 37.5rem;
  background: var(--artdeco-bg-global);
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);
  position: relative;
  overflow: hidden;

  &.loading {
    opacity: 70%;
  }

  .loading-overlay {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: color-mix(in srgb, var(--artdeco-bg-global) 80%, transparent);
    z-index: 10;

    .loading-text {
      font-size: var(--artdeco-text-base);
      color: var(--artdeco-fg-muted);
    }
  }
}

.loading-spinner {
  display: inline-block;
  width: var(--artdeco-spacing-4);
  height: var(--artdeco-spacing-4);
  margin-right: var(--artdeco-spacing-2);
  border: calc(var(--artdeco-spacing-px) * 2) solid color-mix(in srgb, var(--artdeco-fg-primary) 30%, transparent);
  border-top-color: var(--artdeco-fg-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.alert-content {
  strong {
    display: block;
    margin-bottom: var(--artdeco-spacing-2);
    color: var(--artdeco-fg-primary);
  }

  p {
    margin: 0 0 var(--artdeco-spacing-3) 0;
    color: var(--artdeco-fg-muted);
  }

  .info-list {
    margin: var(--artdeco-spacing-3) 0 0 0;
    padding-left: var(--artdeco-spacing-5);
    font-size: var(--artdeco-text-xs);
    color: var(--artdeco-fg-muted);
    line-height: 1.8;

    li {
      margin-bottom: var(--artdeco-spacing-1);
    }
  }
}
</style>
