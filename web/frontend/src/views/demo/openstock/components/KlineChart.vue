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
import axios from 'axios'
import { init, _dispose } from 'klinecharts'

const emit = defineEmits<{
  'api-tested': [feature: string]
}>()

const chartSymbol = ref('600000')
const chartMarket = ref('CN')
const chartLoading = ref(false)
let chart: unknown = null

const loadKlineChart = async () => {
  if (!chartSymbol.value.trim()) {
    ElMessage.warning('请输入股票代码')
    return
  }

  chartLoading.value = true

  try {
    if (chart) {
      try {
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
    chart.setSymbol({ ticker: chartSymbol.value })
    chart.setPeriod({ span: 1, type: 'day' })

    if (response.data && response.data.length > 0) {
      chart.applyNewData(response.data)
      emit('api-tested', 'klinechart')
      ElMessage.success(`成功加载 ${response.data.length} 条K线数据`)
    } else {
      ElMessage.warning('没有获取到K线数据')
    }
  } catch (error: unknown) {
    if (error.response?.status === 404) {
      ElMessage.error('K线数据接口未实现，请先实现后端接口: GET /api/market/kline')
    } else {
      ElMessage.error('加载图表失败: ' + (error.response?.data?.detail || error.message))
    }
    console.error('klinecharts Error:', error)
  } finally {
    chartLoading.value = false
  }
}
</script>

<style scoped lang="scss">

.klinechart-section {
  padding: 10px 0;
}

.controls-row {
  display: flex;
  gap: 15px;
  align-items: flex-end;
  margin-bottom: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 150px;

  .input-label {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-secondary);
  }
}

.input {
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-primary);
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: var(--primary);
  }

  &::placeholder {
    color: var(--text-muted);
  }
}

.select {
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-primary);
  cursor: pointer;
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: var(--primary);
  }
}

.klinechart-container {
  width: 100%;
  height: 600px;
  background: var(--bg-primary);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  position: relative;
  overflow: hidden;

  &.loading {
    opacity: 70%;
  }

  .loading-overlay {
    position: absolute;
    inset: 0 0 0 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgb(255 255 255 / 80%);
    z-index: 10;

    .loading-text {
      font-size: 16px;
      color: var(--text-secondary);
    }
  }
}

.loading-spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgb(255 255 255 / 30%);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.alert-content {
  strong {
    display: block;
    margin-bottom: 8px;
    color: var(--text-primary);
  }

  p {
    margin: 0;
    color: var(--text-secondary);
  }

  .tip {
    margin-top: 8px;
    font-size: 12px;
    color: var(--text-muted);
  }
}
</style>
