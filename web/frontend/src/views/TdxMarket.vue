<template>
  <div class="tdx-market-container">
    <!-- 指数监控面板 -->
    <el-card class="index-monitor" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">指数行情监控</span>
          <el-button
            :icon="Refresh"
            circle
            size="small"
            @click="refreshIndexes"
            :loading="indexLoading"
          />
        </div>
      </template>
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
    </el-card>

    <el-row :gutter="20">
      <!-- 左侧: 股票搜索和实时行情 -->
      <el-col :span="8">
        <el-card shadow="never" class="quote-card">
          <template #header>
            <div class="card-header">
              <span class="title">实时行情</span>
            </div>
          </template>

          <!-- 股票搜索 -->
          <div class="stock-search">
            <el-input
              v-model="searchSymbol"
              placeholder="输入股票代码(如: 600519)"
              @keyup.enter="fetchQuote"
              clearable
            >
              <template #append>
                <el-button
                  :icon="Search"
                  @click="fetchQuote"
                  :loading="quoteLoading"
                />
              </template>
            </el-input>
          </div>

          <!-- 实时行情展示 -->
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
              <el-row :gutter="10">
                <el-col :span="12">
                  <div class="detail-item">
                    <span class="label">今开:</span>
                    <span class="value">{{ currentQuote.open?.toFixed(2) }}</span>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="detail-item">
                    <span class="label">昨收:</span>
                    <span class="value">{{ currentQuote.pre_close?.toFixed(2) }}</span>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="detail-item">
                    <span class="label">最高:</span>
                    <span class="value">{{ currentQuote.high?.toFixed(2) }}</span>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="detail-item">
                    <span class="label">最低:</span>
                    <span class="value">{{ currentQuote.low?.toFixed(2) }}</span>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="detail-item">
                    <span class="label">成交量:</span>
                    <span class="value">{{ formatVolume(currentQuote.volume) }}</span>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="detail-item">
                    <span class="label">成交额:</span>
                    <span class="value">{{ formatAmount(currentQuote.amount) }}</span>
                  </div>
                </el-col>
              </el-row>
            </div>

            <!-- 五档行情 -->
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

            <!-- 自动刷新控制 -->
            <div class="auto-refresh-control">
              <el-switch
                v-model="autoRefresh"
                active-text="自动刷新"
                @change="handleAutoRefreshChange"
              />
              <span class="refresh-time" v-if="lastRefreshTime">
                更新: {{ lastRefreshTime }}
              </span>
            </div>
          </div>

          <el-empty
            v-else
            description="请输入股票代码查询行情"
            :image-size="100"
          />
        </el-card>
      </el-col>

      <!-- 右侧: K线图表 -->
      <el-col :span="16">
        <el-card shadow="never" class="kline-card">
          <template #header>
            <div class="card-header">
              <span class="title">K线图表</span>
              <div class="period-selector">
                <el-radio-group
                  v-model="selectedPeriod"
                  size="small"
                  @change="fetchKline"
                >
                  <el-radio-button label="1m">1分钟</el-radio-button>
                  <el-radio-button label="5m">5分钟</el-radio-button>
                  <el-radio-button label="15m">15分钟</el-radio-button>
                  <el-radio-button label="30m">30分钟</el-radio-button>
                  <el-radio-button label="1h">1小时</el-radio-button>
                  <el-radio-button label="1d">日线</el-radio-button>
                </el-radio-group>
              </div>
            </div>
          </template>

          <div class="kline-chart-container">
            <div
              ref="klineChart"
              class="kline-chart"
              v-loading="klineLoading"
            ></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { init, dispose } from 'klinecharts'
import axios from 'axios'

// API基础URL
const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

// 状态
const searchSymbol = ref('600519')
const currentQuote = ref(null)
const quoteLoading = ref(false)
const klineLoading = ref(false)
const selectedPeriod = ref('1d')
const autoRefresh = ref(false)
const lastRefreshTime = ref('')
const indexLoading = ref(false)

// 指数列表
const indexes = ref([
  { code: '000001', name: '上证指数', price: 0, change: 0, change_pct: 0 },
  { code: '399001', name: '深证成指', price: 0, change: 0, change_pct: 0 },
  { code: '399006', name: '创业板指', price: 0, change: 0, change_pct: 0 }
])

// K线图表实例
const klineChart = ref(null)
let chartInstance = null
let refreshTimer = null

// 获取认证令牌
const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

// 获取股票实时行情
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

    // 自动加载K线
    await fetchKline()
  } catch (error) {
    console.error('获取行情失败:', error)
    ElMessage.error(error.response?.data?.detail || '获取行情失败')
  } finally {
    quoteLoading.value = false
  }
}

// 获取K线数据
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

// 更新K线图表
const updateChart = (data) => {
  if (!chartInstance) {
    initChart()
  }

  // 转换数据格式
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

// 初始化K线图表
const initChart = () => {
  if (!klineChart.value) return

  chartInstance = init(klineChart.value)

  // 配置图表
  chartInstance.setStyles({
    grid: {
      show: true,
      horizontal: {
        show: true,
        size: 1,
        color: '#f0f0f0',
        style: 'dashed'
      },
      vertical: {
        show: true,
        size: 1,
        color: '#f0f0f0',
        style: 'dashed'
      }
    },
    candle: {
      type: 'candle_solid',
      bar: {
        upColor: '#ef5350',
        downColor: '#26a69a',
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

// 获取指数行情
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

// 刷新所有指数
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

// 选择股票
const selectStock = (code) => {
  searchSymbol.value = code
  fetchQuote()
}

// 自动刷新处理
const handleAutoRefreshChange = (val) => {
  if (val) {
    // 开启自动刷新(每5秒)
    refreshTimer = setInterval(() => {
      if (searchSymbol.value) {
        fetchQuote()
      }
      refreshIndexes()
    }, 5000)
    ElMessage.success('已开启自动刷新(每5秒)')
  } else {
    // 关闭自动刷新
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
    ElMessage.info('已关闭自动刷新')
  }
}

// 格式化函数
const getPriceClass = (changePct) => {
  if (!changePct) return ''
  return changePct > 0 ? 'price-up' : changePct < 0 ? 'price-down' : ''
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

// 生命周期
onMounted(async () => {
  await nextTick()
  initChart()
  refreshIndexes()
  // 默认加载一个股票
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
.tdx-market-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .title {
    font-weight: 600;
    font-size: 16px;
  }

  .period-selector {
    display: flex;
    gap: 10px;
  }
}

// 指数监控面板
.index-monitor {
  margin-bottom: 20px;

  .index-list {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
  }

  .index-item {
    flex: 1;
    min-width: 200px;
    padding: 15px;
    border: 1px solid #e8e8e8;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      border-color: #409eff;
      box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
    }

    .index-name {
      font-size: 14px;
      color: #666;
      margin-bottom: 8px;
    }

    .index-price {
      font-size: 24px;
      font-weight: 600;
      margin-bottom: 5px;
    }

    .index-change {
      font-size: 14px;
      display: flex;
      gap: 10px;
    }
  }
}

// 实时行情卡片
.quote-card {
  height: calc(100vh - 280px);
  overflow-y: auto;

  .stock-search {
    margin-bottom: 20px;
  }

  .quote-display {
    .quote-header {
      display: flex;
      gap: 10px;
      margin-bottom: 20px;
      padding-bottom: 10px;
      border-bottom: 1px solid #e8e8e8;

      .stock-code {
        font-size: 18px;
        font-weight: 600;
      }

      .stock-name {
        font-size: 16px;
        color: #666;
      }
    }

    .quote-main {
      text-align: center;
      margin-bottom: 20px;

      .price-large {
        font-size: 48px;
        font-weight: 600;
        line-height: 1.2;
      }

      .change-info {
        font-size: 18px;
        margin-top: 10px;
        display: flex;
        gap: 15px;
        justify-content: center;
      }
    }

    .quote-details {
      margin: 20px 0;

      .detail-item {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        font-size: 14px;

        .label {
          color: #666;
        }

        .value {
          font-weight: 500;
        }
      }
    }

    .quote-bid-ask {
      margin: 20px 0;
      padding: 15px;
      background: #f5f7fa;
      border-radius: 8px;

      .bid-ask-item {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        font-size: 14px;

        .label {
          color: #666;
        }

        .price {
          font-weight: 600;
        }

        .volume {
          color: #999;
        }

        &.ask {
          color: #26a69a;
        }

        &.bid {
          color: #ef5350;
        }
      }
    }

    .auto-refresh-control {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 20px;
      padding-top: 15px;
      border-top: 1px solid #e8e8e8;

      .refresh-time {
        font-size: 12px;
        color: #999;
      }
    }
  }
}

// K线图表卡片
.kline-card {
  height: calc(100vh - 280px);

  .kline-chart-container {
    height: calc(100vh - 360px);

    .kline-chart {
      width: 100%;
      height: 100%;
    }
  }
}

// 涨跌颜色
.price-up {
  color: #ef5350 !important;
}

.price-down {
  color: #26a69a !important;
}
</style>
