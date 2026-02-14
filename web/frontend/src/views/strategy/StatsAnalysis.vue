<template>
    <div class="page-header">
      <div class="page-title">策略统计分析</div>
      <div class="page-subtitle">STRATEGY STATISTICAL ANALYSIS</div>
      <div class="page-decorative-line"></div>
    </div>

    <div class="toolbar">
      <div class="date-selector">
        <label class="selector-label">统计日期</label>
        <input
          v-model="checkDate"
          type="date"
          class="input"
        />
        <button class="button button-primary" @click="loadStats" :class="{ loading: loading }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="11" x2="16.65" y2="16.65"></line>
          </svg>
          查询
        </button>
      </div>

      <div class="auto-refresh">
        <label class="switch-label">
          <input
            type="checkbox"
            v-model="autoRefreshEnabled"
            @change="toggleAutoRefresh"
            class="checkbox"
          />
          <span>自动刷新</span>
        </label>
        <select
          v-model="refreshInterval"
          class="select-sm"
          :disabled="!autoRefreshEnabled"
          @change="onIntervalChange"
        >
          <option :value="30">30秒</option>
          <option :value="60">1分钟</option>
          <option :value="300">5分钟</option>
          <option :value="600">10分钟</option>
        </select>
        <span v-if="autoRefreshEnabled && countdown > 0" class="countdown-tag">
          {{ countdown }}秒后刷新
        </span>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <svg class="loading-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <path d="M12 2a10 10 0 0 1 10 10"></path>
      </svg>
      <p>加载中...</p>
    </div>

    <div v-else-if="stats.length > 0" class="stats-content">
      <div class="stats-grid">
        <div v-for="stat in stats" :key="stat.strategy_code" class="card stat-card">
          <div class="card-body">
            <div class="stat-header">
              <div class="strategy-info">
                <h3>{{ stat.strategy_name_cn }}</h3>
                <span class="tag tag-sm">{{ stat.strategy_code }}</span>
              </div>
              <div class="match-count">
                <span class="count-number">{{ stat.matched_count }}</span>
                <span class="count-label">只匹配</span>
              </div>
            </div>
            <div class="stat-subtitle">
              {{ stat.strategy_name_en }}
            </div>
            <div class="stat-divider"></div>
            <div class="stat-actions">
              <button class="button button-sm" @click="viewMatchedStocks(stat)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <path d="M1 12s4-8 11.8-4-4.4-4-4-4 0 0 4 4 4-4-4 0 8-8 11.8 0 0 1-4.4 4-4-4-4 0 0 8-8 11.8z"></path>
                </svg>
                查看匹配股票
              </button>
              <button class="button button-primary button-sm" @click="runStrategy(stat)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polygon points="5 3 19 12 21 12 5 3 19 21 12 5 3" />
                </svg>
                运行策略
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="summary-section">
        <div class="section-title">汇总统计</div>
        <div class="summary-stats">
          <div class="card stat-summary-card">
            <div class="card-body">
              <div class="stat-label">策略总数</div>
              <div class="stat-value">{{ stats.length }}<span class="unit">个</span></div>
            </div>
          </div>
          <div class="card stat-summary-card">
            <div class="card-body">
              <div class="stat-label">总匹配数</div>
              <div class="stat-value">{{ totalMatched }}<span class="unit">只</span></div>
            </div>
          </div>
          <div class="card stat-summary-card">
            <div class="card-body">
              <div class="stat-label">平均匹配</div>
              <div class="stat-value">{{ averageMatched }}<span class="unit">只/策略</span></div>
            </div>
          </div>
          <div class="card stat-summary-card">
            <div class="card-body">
              <div class="stat-label">最多匹配</div>
              <div class="stat-value">{{ maxMatched }}<span class="unit">只</span></div>
            </div>
          </div>
        </div>

        <div class="ranking-section">
          <div class="section-title">匹配数量排行 TOP 5</div>
          <table class="table">
            <thead>
              <tr>
                <th>排名</th>
                <th>策略名称</th>
                <th>匹配数量</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in topStrategies" :key="item.strategy_code">
                <td class="mono rank-cell">{{ index + 1 }}</td>
                <td>{{ item.strategy_name_cn }}</td>
                <td>
                  <span class="tag tag-success">{{ item.matched_count }}</span>
                </td>
                <td>
                  <button class="action-button" @click="viewMatchedStocks(item)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="10"></circle>
                      <path d="M1 12s4-8 11.8-4-4.4-4-4-4-4 0 0 4 4 4-4-4-0 8-8 11.8z"></path>
                    </svg>
                    查看
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M18 8A6 6 0 0 0 6 2c0 7-3 9-3 9h18s-3-2-3-9"></path>
        <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
      </svg>
      <p>暂无统计数据</p>
    </div>

    <div v-if="stocksVisible" class="dialog-overlay" @click.self="stocksVisible = false">
      <div class="card dialog">
        <div class="card-header">
          <div class="header-title">
            <span class="title-text">{{ selectedStrategy?.strategy_name_cn }} - 匹配股票列表</span>
          </div>
        </div>
        <div class="card-body">
          <div v-if="stocksLoading" class="loading-state">
            <svg class="loading-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M12 2a10 10 0 0 1 10 10"></path>
            </svg>
            <p>加载中...</p>
          </div>
          <table v-else class="table">
            <thead>
              <tr>
                <th>股票代码</th>
                <th>股票名称</th>
                <th>最新价</th>
                <th>涨跌幅</th>
                <th>检查日期</th>
                <th>创建时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="stock in matchedStocks" :key="stock.symbol">
                <td class="mono">{{ stock.symbol }}</td>
                <td>{{ stock.stock_name }}</td>
                <td class="mono">{{ stock.latest_price }}</td>
                <td :class="stock.change_percent > 0 ? 'positive' : stock.change_percent < 0 ? 'negative' : ''">
                  {{ stock.change_percent ? stock.change_percent + '%' : '--' }}
                </td>
                <td class="mono">{{ stock.check_date }}</td>
                <td class="mono">{{ stock.created_at }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { strategyApi } from '@/api'

const loading = ref(false)
const stats = ref([])
const checkDate = ref('')
const stocksVisible = ref(false)
const stocksLoading = ref(false)
const matchedStocks = ref([])
const selectedStrategy = ref(null)

const autoRefreshEnabled = ref(false)
const refreshInterval = ref(60)
const countdown = ref(0)
let refreshTimer = null
let countdownTimer = null

const totalMatched = computed(() => {
  return stats.value.reduce((sum, stat) => sum + stat.matched_count, 0)
})

const averageMatched = computed(() => {
  if (stats.value.length === 0) return 0
  return totalMatched.value / stats.value.length
})

const maxMatched = computed(() => {
  if (stats.value.length === 0) return 0
  return Math.max(...stats.value.map(s => s.matched_count))
})

const topStrategies = computed(() => {
  return [...stats.value]
    .sort((a, b) => b.matched_count - a.matched_count)
    .slice(0, 5)
})

const loadStats = async () => {
  loading.value = true
  try {
    const params = {}
    if (checkDate.value) {
      params.check_date = checkDate.value
    }

    const response = await strategyApi.getStats(params)
    if (response.data.success) {
      stats.value = response.data.data
      ElMessage.success('加载统计数据成功')
    } else {
      ElMessage.error(response.data.message || '加载失败')
    }
  } catch (error) {
    console.error('加载统计失败:', error)
    ElMessage.error('加载统计失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const viewMatchedStocks = async (stat) => {
  selectedStrategy.value = stat
  stocksVisible.value = true
  stocksLoading.value = true

  try {
    const params = {
      strategy_code: stat.strategy_code,
      limit: 100
    }
    if (checkDate.value) {
      params.check_date = checkDate.value
    }

    const response = await strategyApi.getMatchedStocks(params)
    if (response.data.success) {
      matchedStocks.value = response.data.data
    } else {
      ElMessage.error(response.data.message || '查询失败')
    }
  } catch (error) {
    console.error('查询匹配股票失败:', error)
    ElMessage.error('查询失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    stocksLoading.value = false
  }
}

const runStrategy = (stat) => {
  ElMessage.info(`跳转到批量扫描：${stat.strategy_name_cn}`)
}

const toggleAutoRefresh = (enabled) => {
  if (enabled) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const onIntervalChange = () => {
  if (autoRefreshEnabled.value) {
    stopAutoRefresh()
    startAutoRefresh()
  }
}

const startAutoRefresh = () => {
  countdown.value = refreshInterval.value

  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      countdown.value = refreshInterval.value
      loadStats()
    }
  }, 1000)

  refreshTimer = setInterval(() => {
    loadStats()
  }, refreshInterval.value * 1000)

  ElMessage.success(`已启动自动刷新 (${refreshInterval.value}秒间隔)`)
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
  countdown.value = 0
}

onMounted(() => {
  loadStats()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped lang="scss">
@import "./styles/StatsAnalysis.scss";
</style>
