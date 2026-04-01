<template>
  <div class="card demo-card">
    <div class="card-header">
      <span class="card-title">📈 实时行情查询</span>
      <span class="badge badge-success">已迁移</span>
    </div>

    <div class="quote-section">
      <div class="controls-row">
        <div class="input-group">
          <span class="input-label">代码</span>
          <input v-model="quoteSymbol" type="text" class="input" placeholder="输入股票代码" />
        </div>
        <div class="input-group">
          <span class="input-label">市场</span>
          <select v-model="quoteMarket" class="select">
            <option value="cn">A股</option>
            <option value="hk">H股</option>
          </select>
        </div>
        <button class="btn btn-primary" @click="fetchQuote" :disabled="quoteLoading">
          <span v-if="quoteLoading" class="loading-spinner"></span>
          {{ quoteLoading ? '查询中...' : '查询行情' }}
        </button>
      </div>

      <div v-if="currentQuote" class="quote-display">
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">股票名称</span>
            <span class="info-value">{{ currentQuote.name || currentQuote.symbol }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">股票代码</span>
            <code class="info-value">{{ currentQuote.symbol }}</code>
          </div>
          <div class="info-item">
            <span class="info-label">当前价</span>
            <span :class="['info-value', 'price', (currentQuote.change ?? 0) >= 0 ? 'price-up' : 'price-down']">
              {{ currentQuote.current?.toFixed(2) }}
            </span>
          </div>
          <div class="info-item">
            <span class="info-label">涨跌幅</span>
            <span :class="['info-value', 'price', (currentQuote.percent_change ?? 0) >= 0 ? 'price-up' : 'price-down']">
              {{ currentQuote.percent_change?.toFixed(2) }}%
            </span>
          </div>
          <div class="info-item">
            <span class="info-label">涨跌额</span>
            <span :class="['info-value', 'price', (currentQuote.change ?? 0) >= 0 ? 'price-up' : 'price-down']">
              {{ currentQuote.change?.toFixed(2) }}
            </span>
          </div>
          <div class="info-item">
            <span class="info-label">开盘价</span>
            <span class="info-value">{{ currentQuote.open?.toFixed(2) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">最高价</span>
            <span class="info-value">{{ currentQuote.high?.toFixed(2) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">最低价</span>
            <span class="info-value">{{ currentQuote.low?.toFixed(2) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">昨收价</span>
            <span class="info-value">{{ currentQuote.previous_close?.toFixed(2) }}</span>
          </div>
          <div class="info-item" v-if="currentQuote.volume">
            <span class="info-label">成交量</span>
            <span class="info-value">{{ formatVolume(currentQuote.volume) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

interface StockQuote {
  name?: string
  symbol: string
  current?: number
  change?: number
  percent_change?: number
  open?: number
  high?: number
  low?: number
  previous_close?: number
  volume?: number
  [key: string]: unknown
}

interface ApiErrorResponse {
  response?: {
    data?: {
      detail?: string
    }
  }
  message?: string
}

const emit = defineEmits<{
  'api-tested': [feature: string]
}>()

const quoteSymbol = ref('')
const quoteMarket = ref('cn')
const currentQuote = ref<StockQuote | null>(null)
const quoteLoading = ref(false)

const fetchQuote = async () => {
  if (!quoteSymbol.value.trim()) {
    ElMessage.warning('请输入股票代码')
    return
  }

  quoteLoading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const API_BASE = '/api'

    const response = await axios.get(
      `${API_BASE}/stock-search/quote/${quoteSymbol.value}`,
      {
        params: { market: quoteMarket.value },
        headers: { Authorization: `Bearer ${token}` }
      }
    )
    currentQuote.value = response.data
    emit('api-tested', 'quote')
    ElMessage.success('行情获取成功')
  } catch (error: unknown) {
    const apiError = error as ApiErrorResponse
    ElMessage.error('获取行情失败: ' + (apiError.response?.data?.detail || apiError.message))
  } finally {
    quoteLoading.value = false
  }
}

const formatVolume = (volume: number) => {
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + '亿'
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万'
  }
  return volume.toString()
}

defineExpose({
  fetchQuote,
  setQuote: (symbol: string, market: string) => {
    quoteSymbol.value = symbol
    quoteMarket.value = market
  }
})
</script>

<style scoped lang="scss">
@use '../../../../styles/artdeco-tokens.scss' as *;

.quote-section {
  padding: var(--artdeco-spacing-3) 0;
}

.controls-row {
  display: flex;
  gap: var(--artdeco-spacing-4);
  align-items: flex-end;
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

.select {
  cursor: pointer;
}

.quote-display {
  margin-top: var(--artdeco-spacing-5);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0;
  background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);
  overflow: hidden;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px)) var(--artdeco-spacing-5);
  border-bottom: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 12%, transparent);
  border-right: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 12%, transparent);

  &:nth-child(2n) {
    border-right: none;
  }

  &:nth-last-child(1),
  &:nth-last-child(2) {
    border-bottom: none;
  }
}

.info-label {
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
}

.info-value {
  color: var(--artdeco-fg-primary);
  font-size: var(--artdeco-text-sm);
  font-weight: var(--artdeco-font-medium);

  code {
    padding: calc(var(--artdeco-spacing-px) * 2) var(--artdeco-spacing-2);
    background: var(--artdeco-bg-elevated);
    border-radius: var(--artdeco-radius-none);
    font-family: var(--artdeco-font-accent, var(--font-mono));
  }
}

.price {
  font-weight: var(--artdeco-font-bold);
}

.price-up {
  color: var(--artdeco-rise);
}

.price-down {
  color: var(--artdeco-down);
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
</style>
