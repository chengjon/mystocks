<template>
  <div class="tdx-market-page">
    <div class="page-header">
      <h1 class="page-title">TDX行情中心</h1>
      <p class="page-subtitle">REAL-TIME QUOTE | K-LINE CHART | INDEX MONITORING</p>
      <div class="decorative-line"></div>
    </div>

    <div class="card index-monitor">
      <div class="card-header">
        <span class="section-title">指数行情监控</span>
        <button class="button" @click="refreshIndexes" :disabled="indexLoading">
          <svg v-if="!indexLoading" width="16" height="16" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-primary)'" stroke-width="2">
            <path d="M23 4v6h-6"></path>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
          </svg>
          <svg v-else class="spinner" width="16" height="16" viewBox="0 0 50 50">
            <circle cx="25" cy="25" r="20" fill="none" :stroke="'var(--gold-primary)'" stroke-width="4"></circle>
          </svg>
        </button>
      </div>
      <div class="index-list">
        <div
          v-for="index in indexes"
          :key="index.code"
          class="index-item"
          @click="selectStock(index.code)"
        >
          <div class="index-name">{{ index.name || index.code }}</div>
          <div class="index-price" :class="getPriceClass(index.change_pct)">
            {{ index.price?.toFixed(2) || '--' }}
          </div>
          <div class="index-change" :class="getPriceClass(index.change_pct)">
            <span>{{ formatChange(index.change) }}</span>
            <span>{{ formatChangePct(index.change_pct) }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="content-row">
      <div class="quote-section">
        <div class="card quote-card">
          <div class="card-header">
            <span class="section-title">实时行情</span>
          </div>

          <div class="stock-search">
            <div class="input-wrapper">
              <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-dim)'" stroke-width="2">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
              <input
                v-model="searchSymbol"
                type="text"
                class="input"
                placeholder="输入股票代码(如: 600519)"
                @keyup.enter="fetchQuote"
              />
            </div>
            <button class="button" @click="fetchQuote" :disabled="quoteLoading">
              查询
            </button>
          </div>

          <div v-if="currentQuote" class="quote-display">
            <div class="quote-header">
              <span class="stock-code">{{ currentQuote.code }}</span>
              <span class="stock-name">{{ currentQuote.name || '暂无名称' }}</span>
            </div>

            <div class="quote-main">
              <div class="price-large" :class="getPriceClass(currentQuote.change_pct)">
                {{ currentQuote.price?.toFixed(2) || '--' }}
              </div>
              <div class="change-info" :class="getPriceClass(currentQuote.change_pct)">
                <span>{{ formatChange(currentQuote.change) }}</span>
                <span>{{ formatChangePct(currentQuote.change_pct) }}</span>
              </div>
            </div>

            <div class="quote-details">
              <div class="detail-row">
                <div class="detail-item">
                  <span class="label">今开:</span>
                  <span class="value">{{ currentQuote.open?.toFixed(2) }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">昨收:</span>
                  <span class="value">{{ currentQuote.pre_close?.toFixed(2) }}</span>
                </div>
              </div>
              <div class="detail-row">
                <div class="detail-item">
                  <span class="label">最高:</span>
                  <span class="value">{{ currentQuote.high?.toFixed(2) }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">最低:</span>
                  <span class="value">{{ currentQuote.low?.toFixed(2) }}</span>
                </div>
              </div>
              <div class="detail-row">
                <div class="detail-item">
                  <span class="label">成交量:</span>
                  <span class="value">{{ formatVolume(currentQuote.volume) }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">成交额:</span>
                  <span class="value">{{ formatAmount(currentQuote.amount) }}</span>
                </div>
              </div>
            </div>

            <div class="quote-bid-ask">
              <div class="bid-ask-item ask">
                <span class="label">卖一:</span>
                <span class="price">{{ currentQuote.ask1?.toFixed(2) }}</span>
                <span class="volume">{{ currentQuote.ask1_volume }}</span>
              </div>
              <div class="bid-ask-item bid">
                <span class="label">买一:</span>
                <span class="price">{{ currentQuote.bid1?.toFixed(2) }}</span>
                <span class="volume">{{ currentQuote.bid1_volume }}</span>
              </div>
            </div>

            <div class="auto-refresh-control">
              <label class="switch-label">
                <input type="checkbox" v-model="autoRefresh" @change="handleAutoRefreshChange" class="checkbox" />
                <span>自动刷新</span>
              </label>
              <span class="refresh-time" v-if="lastRefreshTime">
                更新: {{ lastRefreshTime }}
              </span>
            </div>
          </div>

          <div v-else class="empty-state">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-dim)'" stroke-width="1">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <p>请输入股票代码查询行情</p>
          </div>
        </div>
      </div>

      <div class="kline-section">
        <div class="card kline-card">
          <div class="card-header">
            <span class="section-title">K线图表</span>
            <div class="period-selector">
              <label class="radio-label">
                <input type="radio" v-model="selectedPeriod" value="1m" @change="fetchKline" class="radio" />
                <span>1分钟</span>
              </label>
              <label class="radio-label">
                <input type="radio" v-model="selectedPeriod" value="5m" @change="fetchKline" class="radio" />
                <span>5分钟</span>
              </label>
              <label class="radio-label">
                <input type="radio" v-model="selectedPeriod" value="15m" @change="fetchKline" class="radio" />
                <span>15分钟</span>
              </label>
              <label class="radio-label">
                <input type="radio" v-model="selectedPeriod" value="30m" @change="fetchKline" class="radio" />
                <span>30分钟</span>
              </label>
              <label class="radio-label">
                <input type="radio" v-model="selectedPeriod" value="1h" @change="fetchKline" class="radio" />
                <span>1小时</span>
              </label>
              <label class="radio-label">
                <input type="radio" v-model="selectedPeriod" value="1d" @change="fetchKline" class="radio" />
                <span>日线</span>
              </label>
            </div>
          </div>

          <div class="kline-chart-container" v-loading="klineLoading">
            <div ref="klineChart" class="kline-chart"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { init, dispose } from 'klinecharts'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

const searchSymbol = ref('600519')
const currentQuote = ref(null)
const quoteLoading = ref(false)
const klineLoading = ref(false)
const selectedPeriod = ref('1d')
const autoRefresh = ref(false)
const lastRefreshTime = ref('')
const indexLoading = ref(false)

const indexes = ref([
  { code: '000001', name: '上证指数', price: 0, change: 0, change_pct: 0 },
  { code: '399001', name: '深证成指', price: 0, change: 0, change_pct: 0 },
  { code: '399006', name: '创业板指', price: 0, change: 0, change_pct: 0 }
])

const klineChart = ref(null)
let chartInstance = null
let refreshTimer = null

const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

const fetchQuote = async () => {
  if (!searchSymbol.value || searchSymbol.value.length !== 6) {
    ElMessage.warning('请输入6位数字股票代码')
    return
  }

  quoteLoading.value = true
  try {
    const response = await axios.get(
      `${API_BASE}/api/tdx/quote/${searchSymbol.value}`,
      { headers: getAuthHeaders() }
    )
    currentQuote.value = response.data
    lastRefreshTime.value = new Date().toLocaleTimeString()

    await fetchKline()
  } catch (error) {
    console.error('获取行情失败:', error)
    ElMessage.error(error.response?.data?.detail || '获取行情失败')
  } finally {
    quoteLoading.value = false
  }
}

const fetchKline = async () => {
  if (!searchSymbol.value) return

  klineLoading.value = true
  try {
    const response = await axios.get(`${API_BASE}/api/tdx/kline`, {
      params: {
        symbol: searchSymbol.value,
        period: selectedPeriod.value
      },
      headers: getAuthHeaders()
    })

    const klineData = response.data
    if (klineData.data && klineData.data.length > 0) {
      updateChart(klineData.data)
    } else {
      ElMessage.warning('暂无K线数据')
    }
  } catch (error) {
    console.error('获取K线失败:', error)
    ElMessage.error(error.response?.data?.detail || '获取K线失败')
  } finally {
    klineLoading.value = false
  }
}

const updateChart = (data) => {
  if (!chartInstance) {
    initChart()
  }

  const formattedData = data.map(item => ({
    timestamp: new Date(item.date).getTime(),
    open: item.open,
    high: item.high,
    low: item.low,
    close: item.close,
    volume: item.volume
  }))

  chartInstance.applyNewData(formattedData)
}

const initChart = () => {
  if (!klineChart.value) return

  chartInstance = init(klineChart.value)

  chartInstance.setStyles({
    grid: {
      show: true,
      horizontal: {
        show: true,
        size: 1,
        color: 'rgba(212, 175, 55, 0.3)',
        style: 'dashed'
      },
      vertical: {
        show: true,
        size: 1,
        color: 'rgba(212, 175, 55, 0.3)',
        style: 'dashed'
      }
    },
    candle: {
      type: 'candle_solid',
      bar: {
        upColor: '#FF5252',
        downColor: '#00E676',
        noChangeColor: '#999999'
      },
      tooltip: {
        showRule: 'always',
        showType: 'standard',
        labels: ['时间:', '开:', '收:', '高:', '低:', '量:'],
        values: (kLineData) => {
          return [
            new Date(kLineData.timestamp).toLocaleString(),
            kLineData.open.toFixed(2),
            kLineData.close.toFixed(2),
            kLineData.high.toFixed(2),
            kLineData.low.toFixed(2),
            kLineData.volume
          ]
        }
      }
    }
  })
}

const fetchIndexQuote = async (code) => {
  try {
    const response = await axios.get(
      `${API_BASE}/api/tdx/index/quote/${code}`,
      { headers: getAuthHeaders() }
    )
    return response.data
  } catch (error) {
    console.error(`获取指数${code}失败:`, error)
    return null
  }
}

const refreshIndexes = async () => {
  indexLoading.value = true
  try {
    const promises = indexes.value.map(index => fetchIndexQuote(index.code))
    const results = await Promise.all(promises)

    results.forEach((data, i) => {
      if (data) {
        indexes.value[i] = {
          ...indexes.value[i],
          ...data
        }
      }
    })
  } catch (error) {
    console.error('刷新指数失败:', error)
  } finally {
    indexLoading.value = false
  }
}

const selectStock = (code) => {
  searchSymbol.value = code
  fetchQuote()
}

const handleAutoRefreshChange = (val) => {
  if (val) {
    refreshTimer = setInterval(() => {
      if (searchSymbol.value) {
        fetchQuote()
      }
      refreshIndexes()
    }, 5000)
    ElMessage.success('已开启自动刷新(每5秒)')
  } else {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
    ElMessage.info('已关闭自动刷新')
  }
}

const getPriceClass = (changePct) => {
  if (!changePct) return ''
  return changePct > 0 ? 'positive' : changePct < 0 ? 'negative' : ''
}

const formatChange = (change) => {
  if (!change) return '--'
  const sign = change > 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}`
}

const formatChangePct = (changePct) => {
  if (!changePct) return '--'
  const sign = changePct > 0 ? '+' : ''
  return `${sign}${changePct.toFixed(2)}%`
}

const formatVolume = (vol) => {
  if (!vol) return '--'
  if (vol >= 10000) return `${(vol / 10000).toFixed(2)}万手`
  return `${vol}手`
}

const formatAmount = (amt) => {
  if (!amt) return '--'
  if (amt >= 100000000) return `${(amt / 100000000).toFixed(2)}亿`
  if (amt >= 10000) return `${(amt / 10000).toFixed(2)}万`
  return `${amt.toFixed(2)}`
}

onMounted(async () => {
  await nextTick()
  initChart()
  refreshIndexes()
  if (searchSymbol.value) {
    fetchQuote()
  }
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  if (chartInstance) {
    dispose(klineChart.value)
  }
})
</script>

<style scoped lang="scss">

.tdx-market-page {
  padding: 20px;
  min-height: 100vh;
  background: var(--bg-primary);
  background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(212, 175, 55, 0.02) 10px, rgba(212, 175, 55, 0.02) 11px);
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 30px 0;

  .page-title {
    font-family: var(--font-display);
    font-size: 32px;
    color: var(--gold-primary);
    text-transform: uppercase;
    letter-spacing: 4px;
    margin: 0 0 8px 0;
  }

  .page-subtitle {
    font-family: var(--font-body);
    font-size: 12px;
    color: var(--gold-muted);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin: 0;
  }

  .decorative-line {
    width: 200px;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold-primary), transparent);
    margin: 20px auto 0;

    &::before {
      content: '';
      position: absolute;
      bottom: -6px;
      left: 50%;
      transform: translateX(-50%);
      width: 60px;
      height: 1px;
      background: linear-gradient(90deg, transparent, var(--gold-muted), transparent);
    }
  }
}

.card {
  background: var(--bg-secondary);
  border: 1px solid var(--gold-dim);
  padding: 20px;
  position: relative;
  border-radius: 0;

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: 16px;
    height: 16px;
    border: 2px solid var(--gold-primary);
  }

  &::before {
    top: 12px;
    left: 12px;
    border-right: none;
    border-bottom: none;
  }

  &::after {
    bottom: 12px;
    right: 12px;
    border-left: none;
    border-top: none;
  }

  &:hover {
    border-color: var(--gold-primary);
    box-shadow: 0 0 15px rgba(212, 175, 55, 0.3);
  }
}

.index-monitor {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid var(--gold-dim);
  }
}

.section-title {
  font-family: var(--font-display);
  font-size: 16px;
  color: var(--gold-primary);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin: 0;
}

.index-list {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.index-item {
  flex: 1;
  min-width: 200px;
  padding: 15px;
  background: var(--bg-primary);
  border: 1px solid var(--gold-dim);
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    border-color: var(--gold-primary);
    box-shadow: 0 0 12px rgba(212, 175, 55, 0.3);
    transform: translateY(-2px);
  }

  .index-name {
    font-size: 14px;
    color: var(--text-primary);
    margin-bottom: 8px;
    font-family: var(--font-body);
  }

  .index-price {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 5px;
    font-family: var(--font-display);
  }

  .index-change {
    font-size: 14px;
    display: flex;
    gap: 10px;
    font-family: var(--font-body);
  }
}

.content-row {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 20px;
}

.quote-section {
  .quote-card {
    .stock-search {
      display: flex;
      gap: 10px;
      margin-bottom: 20px;

      .input-wrapper {
        position: relative;
        flex: 1;

        .search-icon {
          position: absolute;
          left: 12px;
          top: 50%;
          transform: translateY(-50%);
          pointer-events: none;
        }

        .input {
          width: 100%;
          padding: 10px 12px 10px 40px;
          background: var(--bg-primary);
          border: 1px solid var(--gold-dim);
          color: var(--text-primary);
          font-family: var(--font-body);
          font-size: 14px;
          border-radius: 0;
          outline: none;
          transition: all 0.3s ease;

          &:focus {
            border-color: var(--gold-primary);
            box-shadow: 0 0 8px rgba(212, 175, 55, 0.3);
          }

          &::placeholder {
            color: var(--text-muted);
          }
        }
      }
    }

    .quote-display {
      .quote-header {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px solid var(--gold-dim);

        .stock-code {
          font-size: 18px;
          font-weight: 600;
          color: var(--gold-primary);
          font-family: var(--font-display);
        }

        .stock-name {
          font-size: 16px;
          color: var(--text-muted);
          font-family: var(--font-body);
        }
      }

      .quote-main {
        text-align: center;
        margin-bottom: 20px;

        .price-large {
          font-size: 48px;
          font-weight: 600;
          line-height: 1.2;
          font-family: var(--font-display);
        }

        .change-info {
          font-size: 18px;
          margin-top: 10px;
          display: flex;
          gap: 15px;
          justify-content: center;
          font-family: var(--font-body);
        }
      }

      .quote-details {
        margin: 20px 0;

        .detail-row {
          display: flex;
          gap: 20px;
          margin-bottom: 12px;
        }

        .detail-item {
          flex: 1;
          display: flex;
          justify-content: space-between;
          font-size: 14px;
          font-family: var(--font-body);

          .label {
            color: var(--text-muted);
          }

          .value {
            color: var(--text-primary);
            font-weight: 500;
          }
        }
      }

      .quote-bid-ask {
        margin: 20px 0;
        padding: 15px;
        background: var(--bg-primary);
        border: 1px solid var(--gold-dim);

        .bid-ask-item {
          display: flex;
          justify-content: space-between;
          padding: 8px 0;
          font-size: 14px;
          font-family: var(--font-body);

          .label {
            color: var(--text-muted);
          }

          .price {
            font-weight: 600;
          }

          .volume {
            color: var(--text-muted);
          }

          &.ask {
            color: var(--fall);
          }

          &.bid {
            color: var(--rise);
          }
        }
      }

      .auto-refresh-control {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 20px;
        padding-top: 15px;
        border-top: 1px solid var(--gold-dim);

        .switch-label {
          display: flex;
          align-items: center;
          gap: 8px;
          font-family: var(--font-body);
          font-size: 14px;
          color: var(--text-primary);
        }

        .refresh-time {
          font-size: 12px;
          color: var(--text-muted);
          font-family: var(--font-body);
        }
      }
    }

    .empty-state {
      text-align: center;
      padding: 60px 20px;

      svg {
        margin-bottom: 16px;
      }

      p {
        color: var(--text-muted);
        font-family: var(--font-body);
        font-size: 14px;
        margin: 0;
      }
    }
  }
}

.kline-section {
  .kline-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 15px;
      border-bottom: 1px solid var(--gold-dim);
      flex-wrap: wrap;
      gap: 10px;
    }
  }

  .period-selector {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }

  .radio-label {
    display: flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
    font-family: var(--font-body);
    font-size: 12px;
    color: var(--text-primary);

    &:hover {
      color: var(--gold-primary);
    }
  }

  .radio-input {
    width: 16px;
    height: 16px;
    accent-color: var(--gold-primary);
    cursor: pointer;
  }

  .kline-chart-container {
    height: 500px;
    background: var(--bg-primary);
    border: 1px solid var(--gold-dim);
    padding: 10px;

    .kline-chart {
      width: 100%;
      height: 100%;
    }
  }
}

.button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--gold-primary);
  color: var(--bg-primary);
  border: none;
  font-family: var(--font-display);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
  cursor: pointer;
  border-radius: 0;
  transition: all 0.3s ease;

  &:hover:not(:disabled) {
    background: var(--gold-muted);
    box-shadow: 0 0 12px rgba(212, 175, 55, 0.4);
  }

  &:disabled {
    background: var(--gold-dim);
    cursor: not-allowed;
    opacity: 0.5;
  }
}

.radio-input {
  width: 18px;
  height: 18px;
  accent-color: var(--gold-primary);
  cursor: pointer;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.positive {
  color: var(--rise);
}

.negative {
  color: var(--fall);
}

@media (max-width: 1200px) {
  .content-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .tdx-market-page {
    padding: 10px;
  }

  .page-header {
    padding: 20px 0;

    .page-title {
      font-size: 24px;
      letter-spacing: 2px;
    }

    .page-subtitle {
      font-size: 10px;
      letter-spacing: 2px;
    }
  }

  .index-list {
    flex-direction: column;
  }

  .period-selector {
    flex-direction: column;
  }
}
</style>
