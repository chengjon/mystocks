<template>
  <div class="card demo-card">
    <div class="card-header">
      <span class="card-title">📊 K线图表（klinecharts）</span>
      <span class="badge badge-success">已集成</span>
    </div>

    <div class="klinechart-section">
      <div class="controls-row">
        <div class="input-group">
          <span class="input-label">代码</span>
          <input v-model="chartSymbol" type="text" class="input" placeholder="输入股票代码" />
        </div>
        <div class="input-group">
          <span class="input-label">市场</span>
          <select v-model="chartMarket" class="select">
            <option value="CN">A股</option>
            <option value="HK">H股</option>
          </select>
        </div>
        <button class="btn btn-primary" @click="loadKlineChart" :disabled="chartLoading">
          <span v-if="chartLoading" class="loading-spinner"></span>
          {{ chartLoading ? '加载中...' : '加载图表' }}
        </button>
      </div>

      <div id="kline-chart" class="klinechart-container" :class="{ loading: chartLoading }">
        <div v-if="chartLoading" class="loading-overlay">
          <div class="loading-text">加载图表中...</div>
        </div>
      </div>

      <div class="alert-info">
        <div class="alert-content">
          <strong>K线图表说明</strong>
          <p>使用 klinecharts 实现的专业K线图表，支持多种技术指标和图表类型。</p>
          <p class="tip">💡 图表支持鼠标缩放、拖动等交互操作。如需更多技术指标，可通过图表工具栏添加。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios, { type AxiosError } from 'axios'
import { init, dispose, type Chart, type KLineData } from 'klinecharts'

const emit = defineEmits<{
  'api-tested': [feature: string]
}>()

const chartSymbol = ref('600000')
const chartMarket = ref('CN')
const chartLoading = ref(false)
let chart: Chart | null = null

const loadKlineChart = async () => {
  if (!chartSymbol.value.trim()) {
    ElMessage.warning('请输入股票代码')
    return
  }

  chartLoading.value = true

  try {
    if (chart) {
      try {
        dispose(chart)
        const container = document.getElementById('kline-chart')
        if (container) {
          container.textContent = ''
        }
        chart = null
      } catch (e) {
        console.warn('清除旧图表时出错:', e)
      }
    }

    const token = localStorage.getItem('token') || ''
    const API_BASE = '/api'

    const response = await axios.get(`${API_BASE}/market/kline`, {
      params: { symbol: chartSymbol.value, market: chartMarket.value },
      headers: { Authorization: `Bearer ${token}` }
    })

    const container = document.getElementById('kline-chart')
    if (!container) {
      ElMessage.error('图表容器未找到')
      return
    }

    chart = init('kline-chart')
    if (!chart) {
      ElMessage.error('图表初始化失败')
      return
    }

    if (response.data && response.data.length > 0) {
      chart.applyNewData(response.data as KLineData[])
      emit('api-tested', 'klinechart')
      ElMessage.success(`成功加载 ${response.data.length} 条K线数据`)
    } else {
      ElMessage.warning('没有获取到K线数据')
    }
  } catch (error: unknown) {
    const apiError = error as AxiosError<{ detail?: string }>
    if (apiError.response?.status === 404) {
      ElMessage.error('K线数据接口未实现，请先实现后端接口: GET /api/market/kline')
    } else {
      ElMessage.error('加载图表失败: ' + (apiError.response?.data?.detail || apiError.message))
    }
    console.error('klinecharts Error:', apiError)
  } finally {
    chartLoading.value = false
  }
}
</script>

<style scoped lang="scss">
@use '../../../../styles/artdeco-tokens.scss' as *;

.klinechart-section {
  padding: var(--artdeco-spacing-3) 0;
}

.controls-row {
  display: flex;
  gap: var(--artdeco-spacing-4);
  align-items: flex-end;
  margin-bottom: var(--artdeco-spacing-5);
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
  min-width: calc(var(--artdeco-spacing-20) + var(--artdeco-spacing-10));

  .input-label {
    color: var(--artdeco-fg-muted);
    font-size: calc(var(--artdeco-text-sm) - var(--artdeco-spacing-px));
    font-weight: var(--artdeco-font-medium);
  }
}

.input,
.select {
  padding: calc(var(--artdeco-spacing-5) / 2) calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);
  font-size: var(--artdeco-text-sm);
  color: var(--artdeco-fg-primary);
  background: var(--artdeco-bg-global);
  transition: border-color var(--artdeco-transition-quick) var(--artdeco-ease-out);

  &:focus {
    outline: none;
    border-color: var(--artdeco-gold-primary);
  }
}

.input::placeholder {
  color: var(--artdeco-fg-muted);
}

.select {
  cursor: pointer;
}

.klinechart-container {
  position: relative;
  width: 100%;
  height: 37.5rem;
  overflow: hidden;
  background: var(--artdeco-bg-global);
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);

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
    margin: 0;
    color: var(--artdeco-fg-muted);
  }

  .tip {
    margin-top: var(--artdeco-spacing-2);
    font-size: var(--artdeco-text-xs);
    color: var(--artdeco-fg-muted);
  }
}
</style>
