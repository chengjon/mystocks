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
            <span :class="['info-value', 'price', currentQuote.change >= 0 ? 'price-up' : 'price-down']">
              {{ currentQuote.current?.toFixed(2) }}
            </span>
          </div>
          <div class="info-item">
            <span class="info-label">涨跌幅</span>
            <span :class="['info-value', 'price', currentQuote.percent_change >= 0 ? 'price-up' : 'price-down']">
              {{ currentQuote.percent_change?.toFixed(2) }}%
            </span>
          </div>
          <div class="info-item">
            <span class="info-label">涨跌额</span>
            <span :class="['info-value', 'price', currentQuote.change >= 0 ? 'price-up' : 'price-down']">
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

const emit = defineEmits<{
  'api-tested': [feature: string]
}>()

const quoteSymbol = ref('')
const quoteMarket = ref('cn')
const currentQuote = ref<any>(null)
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
  } catch (error: any) {
    ElMessage.error('获取行情失败: ' + (error.response?.data?.detail || error.message))
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

.quote-section {
  padding: 10px 0;
}

.controls-row {
  display: flex;
  gap: 15px;
  align-items: flex-end;
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

.quote-display {
  margin-top: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0;
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border-light);
  border-right: 1px solid var(--border-light);

  &:nth-child(2n) {
    border-right: none;
  }

  &:nth-last-child(1),
  &:nth-last-child(2) {
    border-bottom: none;
  }
}

.info-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.info-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);

  code {
    padding: 2px 8px;
    background: var(--bg-dark);
    border-radius: var(--radius-sm);
    font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
  }
}

.price {
  font-weight: 700;
}

.price-up {
  color: var(--up);
}

.price-down {
  color: var(--down);
}

.loading-spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
