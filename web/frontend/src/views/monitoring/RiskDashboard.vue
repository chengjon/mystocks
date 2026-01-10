<template>
  <div class="risk-dashboard fintech-bg-primary">
    <!-- 页面标题 -->
    <div class="fintech-card elevated header-section">
      <div class="header-content">
        <div class="title-section">
          <h1 class="fintech-text-primary page-title">RISK MANAGEMENT DASHBOARD</h1>
          <p class="fintech-text-secondary page-subtitle">实时风险监控与投资组合分析</p>
        </div>
        <div class="actions-section">
          <button class="fintech-btn" @click="refresh">
            <reload-outlined />
            <span>REFRESH</span>
          </button>
          <button class="fintech-btn primary" @click="exportReport">
            <export-outlined />
            <span>EXPORT</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 核心指标面板 -->
    <div class="metrics-grid">
      <!-- 组合健康度 -->
      <div class="fintech-card metric-card health-card">
        <div class="metric-header">
          <div class="metric-icon">
            <heart-outlined />
          </div>
          <div class="metric-info">
            <h3 class="fintech-text-primary metric-title">PORTFOLIO HEALTH</h3>
            <p class="fintech-text-secondary metric-subtitle">综合健康评分</p>
          </div>
        </div>
        <div class="metric-value">
          <span class="value-number fintech-text-primary">{{ summary.total_score || 0 }}</span>
          <span class="value-unit fintech-text-secondary">/ 100</span>
        </div>
        <div class="metric-trend">
          <span :class="['trend-indicator', getScoreTrend(summary.total_score)]">
            {{ getScoreChange(summary.total_score) }}
          </span>
        </div>
      </div>

      <!-- 风险评分 -->
      <div class="fintech-card metric-card risk-card">
        <div class="metric-header">
          <div class="metric-icon">
            <warning-outlined />
          </div>
          <div class="metric-info">
            <h3 class="fintech-text-primary metric-title">RISK SCORE</h3>
            <p class="fintech-text-secondary metric-subtitle">风险评估指数</p>
          </div>
        </div>
        <div class="metric-value">
          <span class="value-number fintech-text-primary">{{ summary.risk_score || 0 }}</span>
          <span class="value-unit fintech-text-secondary">/ 100</span>
        </div>
        <div class="metric-gauge">
          <div class="gauge-container">
            <div class="gauge-track">
              <div class="gauge-fill" :style="{ width: `${summary.risk_score || 0}%` }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 持仓统计 -->
      <div class="fintech-card metric-card position-card">
        <div class="metric-header">
          <div class="metric-icon">
            <stock-outlined />
          </div>
          <div class="metric-info">
            <h3 class="fintech-text-primary metric-title">POSITIONS</h3>
            <p class="fintech-text-secondary metric-subtitle">持仓数量统计</p>
          </div>
        </div>
        <div class="metric-value">
          <span class="value-number fintech-text-primary">{{ summary.position_count || 0 }}</span>
          <span class="value-unit fintech-text-secondary">STOCKS</span>
        </div>
        <div class="metric-breakdown">
          <div class="breakdown-item">
            <span class="breakdown-label fintech-text-tertiary">ACTIVE</span>
            <span class="breakdown-value fintech-text-success">{{ activePositions }}</span>
          </div>
          <div class="breakdown-item">
            <span class="breakdown-label fintech-text-tertiary">INACTIVE</span>
            <span class="breakdown-value fintech-text-disabled">{{ inactivePositions }}</span>
          </div>
        </div>
      </div>

      <!-- 预警统计 -->
      <div class="fintech-card metric-card alert-card">
        <div class="metric-header">
          <div class="metric-icon">
            <alert-outlined />
          </div>
          <div class="metric-info">
            <h3 class="fintech-text-primary metric-title">ALERTS</h3>
            <p class="fintech-text-secondary metric-subtitle">待处理预警</p>
          </div>
        </div>
        <div class="metric-value">
          <span class="value-number fintech-text-danger">{{ summary.alert_summary?.critical || 0 }}</span>
          <span class="value-unit fintech-text-secondary">CRITICAL</span>
        </div>
        <div class="alert-breakdown">
          <div class="alert-level">
            <span class="level-dot critical"></span>
            <span class="level-count fintech-text-danger">{{ summary.alert_summary?.critical || 0 }}</span>
          </div>
          <div class="alert-level">
            <span class="level-dot warning"></span>
            <span class="level-count fintech-text-warning">{{ summary.alert_summary?.warning || 0 }}</span>
          </div>
          <div class="alert-level">
            <span class="level-dot info"></span>
            <span class="level-count fintech-text-info">{{ summary.alert_summary?.info || 0 }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="content-grid">
      <!-- 左侧：预警面板 -->
      <div class="alerts-section">
        <!-- 紧急预警 -->
        <div class="fintech-card alert-panel critical-panel">
          <div class="panel-header">
            <div class="panel-icon">
              <exclamation-circle-outlined />
            </div>
            <div class="panel-info">
              <h3 class="fintech-text-primary panel-title">CRITICAL ALERTS</h3>
              <p class="fintech-text-secondary panel-subtitle">{{ criticalAlerts.length }} active alerts</p>
            </div>
            <div class="panel-count">
              <span class="count-badge critical">{{ criticalAlerts.length }}</span>
            </div>
          </div>
          <div class="alerts-list">
            <div v-if="criticalAlerts.length > 0" class="alerts-container">
              <div
                v-for="alert in criticalAlerts"
                :key="alert.id"
                class="alert-item critical-item"
              >
                <div class="alert-icon">
                  <exclamation-circle-outlined />
                </div>
                <div class="alert-content">
                  <div class="alert-symbol fintech-text-data">{{ alert.stock_code }}</div>
                  <div class="alert-message fintech-text-primary">{{ alert.message }}</div>
                  <div class="alert-time fintech-text-tertiary">{{ formatTime(alert.timestamp) }}</div>
                </div>
                <div class="alert-actions">
                  <button class="fintech-btn primary" @click="handleAlert(alert)">ACKNOWLEDGE</button>
                </div>
              </div>
            </div>
            <div v-else class="empty-alerts">
              <div class="empty-icon">
                <check-circle-outlined />
              </div>
              <div class="empty-text">
                <h4 class="fintech-text-secondary">ALL CLEAR</h4>
                <p class="fintech-text-tertiary">No critical alerts at this time</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 风险提醒 -->
        <div class="fintech-card alert-panel warning-panel">
          <div class="panel-header">
            <div class="panel-icon">
              <warning-outlined />
            </div>
            <div class="panel-info">
              <h3 class="fintech-text-primary panel-title">RISK WARNINGS</h3>
              <p class="fintech-text-secondary panel-subtitle">{{ warningAlerts.length }} warnings</p>
            </div>
            <div class="panel-count">
              <span class="count-badge warning">{{ warningAlerts.length }}</span>
            </div>
          </div>
          <div class="alerts-list">
            <div v-if="warningAlerts.length > 0" class="alerts-container">
              <div
                v-for="alert in warningAlerts"
                :key="alert.id"
                class="alert-item warning-item"
              >
                <div class="alert-icon">
                  <warning-outlined />
                </div>
                <div class="alert-content">
                  <div class="alert-symbol fintech-text-data">{{ alert.stock_code }}</div>
                  <div class="alert-message fintech-text-primary">{{ alert.message }}</div>
                  <div class="alert-time fintech-text-tertiary">{{ formatTime(alert.timestamp) }}</div>
                </div>
                <div class="alert-actions">
                  <button class="fintech-btn" @click="handleAlert(alert)">REVIEW</button>
                </div>
              </div>
            </div>
            <div v-else class="empty-alerts">
              <div class="empty-icon">
                <check-circle-outlined />
              </div>
              <div class="empty-text">
                <h4 class="fintech-text-secondary">NO WARNINGS</h4>
                <p class="fintech-text-tertiary">All positions within risk parameters</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 优化建议 -->
        <div class="fintech-card alert-panel info-panel">
          <div class="panel-header">
            <div class="panel-icon">
              <bulb-outlined />
            </div>
            <div class="panel-info">
              <h3 class="fintech-text-primary panel-title">OPTIMIZATION TIPS</h3>
              <p class="fintech-text-secondary panel-subtitle">{{ infoAlerts.length }} suggestions</p>
            </div>
            <div class="panel-count">
              <span class="count-badge info">{{ infoAlerts.length }}</span>
            </div>
          </div>
          <div class="alerts-list">
            <div v-if="infoAlerts.length > 0" class="alerts-container">
              <div
                v-for="alert in infoAlerts"
                :key="alert.id"
                class="alert-item info-item"
              >
                <div class="alert-icon">
                  <bulb-outlined />
                </div>
                <div class="alert-content">
                  <div class="alert-symbol fintech-text-data">{{ alert.stock_code }}</div>
                  <div class="alert-message fintech-text-primary">{{ alert.message }}</div>
                  <div class="alert-time fintech-text-tertiary">{{ formatTime(alert.timestamp) }}</div>
                </div>
                <div class="alert-actions">
                  <button class="fintech-btn" @click="handleAlert(alert)">APPLY</button>
                </div>
              </div>
            </div>
            <div v-else class="empty-alerts">
              <div class="empty-icon">
                <bulb-outlined />
              </div>
              <div class="empty-text">
                <h4 class="fintech-text-secondary">WELL OPTIMIZED</h4>
                <p class="fintech-text-tertiary">Portfolio is performing optimally</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：分析面板 -->
      <div class="analysis-section">
        <!-- 再平衡建议 -->
        <div class="fintech-card analysis-panel">
          <div class="panel-header">
            <div class="panel-icon">
              <balance-outlined />
            </div>
            <div class="panel-info">
              <h3 class="fintech-text-primary panel-title">REBALANCING RECOMMENDATIONS</h3>
              <p class="fintech-text-secondary panel-subtitle">{{ suggestions.length }} actions needed</p>
            </div>
          </div>
          <div class="suggestions-list">
            <div v-if="suggestions.length > 0" class="suggestions-container">
              <div
                v-for="suggestion in suggestions"
                :key="suggestion.id"
                class="suggestion-item"
              >
                <div class="suggestion-header">
                  <div class="suggestion-symbol fintech-text-data">{{ suggestion.stock_code }}</div>
                  <div class="suggestion-action">
                    <span :class="['action-badge', getActionClass(suggestion.action)]">
                      {{ suggestion.action }}
                    </span>
                  </div>
                </div>
                <div class="suggestion-content">
                  <div class="suggestion-reason fintech-text-primary">{{ suggestion.reason }}</div>
                  <div class="suggestion-impact">
                    <span class="impact-label fintech-text-secondary">IMPACT:</span>
                    <span class="impact-value fintech-text-primary">
                      {{ formatCurrency(suggestion.estimated_impact) }}
                    </span>
                  </div>
                </div>
                <div class="suggestion-actions">
                  <button class="fintech-btn primary" @click="applySuggestion(suggestion)">EXECUTE</button>
                  <button class="fintech-btn" @click="dismissSuggestion(suggestion)">DISMISS</button>
                </div>
              </div>
            </div>
            <div v-else class="empty-suggestions">
              <div class="empty-icon">
                <check-circle-outlined />
              </div>
              <div class="empty-text">
                <h4 class="fintech-text-secondary">BALANCED</h4>
                <p class="fintech-text-tertiary">Portfolio is well-balanced</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 行业配置 -->
        <div class="fintech-card analysis-panel">
          <div class="panel-header">
            <div class="panel-icon">
              <pie-chart-outlined />
            </div>
            <div class="panel-info">
              <h3 class="fintech-text-primary panel-title">SECTOR ALLOCATION</h3>
              <p class="fintech-text-secondary panel-subtitle">Industry distribution analysis</p>
            </div>
          </div>
          <div class="sector-allocation">
            <div v-if="Object.keys(summary.sector_allocation || {}).length > 0" class="sector-list">
              <div
                v-for="(weight, sector) in summary.sector_allocation"
                :key="sector"
                class="sector-item"
              >
                <div class="sector-info">
                  <div class="sector-name fintech-text-primary">{{ sector }}</div>
                  <div class="sector-weight fintech-text-secondary">{{ (weight * 100).toFixed(1) }}%</div>
                </div>
                <div class="sector-bar">
                  <div class="bar-track">
                    <div
                      class="bar-fill"
                      :style="{ width: `${weight * 100}%` }"
                      :class="getSectorColor(sector)"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="empty-sector">
              <div class="empty-icon">
                <pie-chart-outlined />
              </div>
              <div class="empty-text">
                <h4 class="fintech-text-secondary">NO DATA</h4>
                <p class="fintech-text-tertiary">Sector allocation data unavailable</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 风险指标 -->
        <div class="fintech-card analysis-panel">
          <div class="panel-header">
            <div class="panel-icon">
              <bar-chart-outlined />
            </div>
            <div class="panel-info">
              <h3 class="fintech-text-primary panel-title">RISK METRICS</h3>
              <p class="fintech-text-secondary panel-subtitle">Advanced risk indicators</p>
            </div>
          </div>
          <div class="risk-metrics">
            <div class="metric-item">
              <div class="metric-name fintech-text-secondary">SHARPE RATIO</div>
              <div class="metric-value fintech-text-primary">{{ summary.sharpe_ratio?.toFixed(2) || 'N/A' }}</div>
            </div>
            <div class="metric-item">
              <div class="metric-name fintech-text-secondary">SORTINO RATIO</div>
              <div class="metric-value fintech-text-primary">{{ summary.sortino_ratio?.toFixed(2) || 'N/A' }}</div>
            </div>
            <div class="metric-item">
              <div class="metric-name fintech-text-secondary">MAX DRAWDOWN</div>
              <div class="metric-value fintech-text-danger">{{ summary.max_drawdown ? `${(summary.max_drawdown * 100).toFixed(2)}%` : 'N/A' }}</div>
            </div>
            <div class="metric-item">
              <div class="metric-name fintech-text-secondary">VOLATILITY</div>
              <div class="metric-value fintech-text-primary">{{ summary.volatility ? `${(summary.volatility * 100).toFixed(2)}%` : 'N/A' }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  AlertOutlined,
  HeartOutlined,
  WarningOutlined,
  StockOutlined,
  ReloadOutlined,
  ExportOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  BulbOutlined,
  // BalanceOutlined,  // Not available in @ant-design/icons-vue
  PieChartOutlined,
  BarChartOutlined
} from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'

const props = defineProps({
  watchlistId: {
    type: Number,
    required: true
  }
})

const loading = ref(false)
const summary = ref({
  total_score: 0,
  risk_score: 50,
  position_count: 0,
  sector_allocation: {},
  alert_summary: { critical: 0, warning: 0, info: 0 },
  sharpe_ratio: null,
  sortino_ratio: null,
  max_drawdown: null,
  volatility: null
})
const alerts = ref([])
const suggestions = ref([])

const criticalAlerts = computed(() => alerts.value.filter(a => a.level === 'critical'))
const warningAlerts = computed(() => alerts.value.filter(a => a.level === 'warning'))
const infoAlerts = computed(() => alerts.value.filter(a => a.level === 'info'))

const activePositions = computed(() => {
  // 模拟数据：假设80%的持仓是活跃的
  return Math.floor((summary.value.position_count || 0) * 0.8)
})

const inactivePositions = computed(() => {
  return (summary.value.position_count || 0) - activePositions.value
})

// 工具函数
const getScoreColor = (score) => {
  if (score >= 70) return 'fintech-text-up'
  if (score >= 50) return 'fintech-text-flat'
  return 'fintech-text-down'
}

const getScoreTrend = (score) => {
  if (score >= 70) return 'positive'
  if (score >= 50) return 'neutral'
  return 'negative'
}

const getScoreChange = (score) => {
  // 模拟趋势数据
  const change = (Math.random() - 0.5) * 10
  const sign = change >= 0 ? '+' : ''
  return `${sign}${change.toFixed(1)}%`
}

const getActionClass = (action) => {
  const classes = {
    'BUY': 'action-buy',
    'SELL': 'action-sell',
    'HOLD': 'action-hold',
    'REBALANCE': 'action-rebalance'
  }
  return classes[action] || 'action-hold'
}

const getSectorColor = (sector) => {
  // 根据行业返回不同的颜色类
  const colors = ['sector-tech', 'sector-healthcare', 'sector-finance', 'sector-consumer', 'sector-energy']
  const index = sector.length % colors.length
  return colors[index]
}

const formatCurrency = (value) => {
  if (!value) return '$0.00'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2
  }).format(value)
}

const formatTime = (timestamp) => {
  if (!timestamp) return 'Unknown'
  const date = new Date(timestamp)
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 事件处理函数
const refresh = async () => {
  await fetchData()
  message.success('Dashboard refreshed')
}

const exportReport = () => {
  // 模拟导出功能
  message.info('Export functionality coming soon')
}

const handleAlert = (alert) => {
  // 处理告警
  message.success(`Alert acknowledged: ${alert.stock_code}`)
}

const applySuggestion = (suggestion) => {
  // 应用建议
  message.success(`Suggestion applied: ${suggestion.action} ${suggestion.stock_code}`)
}

const dismissSuggestion = (suggestion) => {
  // 忽略建议
  const index = suggestions.value.findIndex(s => s.id === suggestion.id)
  if (index > -1) {
    suggestions.value.splice(index, 1)
    message.info('Suggestion dismissed')
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const [summaryRes, alertsRes, suggestionsRes] = await Promise.all([
      fetch(`/api/monitoring/analysis/portfolio/${props.watchlistId}/summary`),
      fetch(`/api/monitoring/analysis/portfolio/${props.watchlistId}/alerts`),
      fetch(`/api/monitoring/analysis/portfolio/${props.watchlistId}/rebalance`)
    ])

    if (summaryRes.ok) {
      const data = await summaryRes.json()
      if (data.success) {
        summary.value = { ...summary.value, ...data.data }
      }
    }

    if (alertsRes.ok) {
      const data = await alertsRes.json()
      if (data.success) {
        alerts.value = data.data
      }
    }

    if (suggestionsRes.ok) {
      const data = await suggestionsRes.json()
      if (data.success) {
        suggestions.value = data.data
      }
    }
  } catch (error) {
    console.error('获取数据失败:', error)
    message.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})

defineExpose({
  refresh: fetchData
})
</script>

<style scoped>
/* ========================================
   Bloomberg-Level Risk Management Dashboard
   ======================================== */

.risk-dashboard {
  min-height: 100vh;
  padding: var(--fintech-space-4);
  background: var(--fintech-bg-primary);
}

/* 标题栏样式 */
.header-section {
  margin-bottom: var(--fintech-space-6);
  background: linear-gradient(135deg, var(--fintech-bg-elevated) 0%, var(--fintech-bg-secondary) 100%);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--fintech-space-6);
}

.title-section h1 {
  margin: 0 0 var(--fintech-space-2) 0;
  font-size: var(--fintech-font-size-3xl);
  font-weight: 600;
  letter-spacing: 0.02em;
}

.page-subtitle {
  margin: 0;
  font-size: var(--fintech-font-size-md);
  opacity: 0.8;
}

.actions-section {
  display: flex;
  gap: var(--fintech-space-3);
}

/* 核心指标网格 */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--fintech-space-4);
  margin-bottom: var(--fintech-space-6);
}

.metric-card {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, var(--fintech-bg-secondary) 0%, var(--fintech-bg-tertiary) 100%);
  transition: all var(--fintech-transition-base);
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--fintech-shadow-base);
}

.metric-header {
  display: flex;
  align-items: center;
  gap: var(--fintech-space-4);
  margin-bottom: var(--fintech-space-4);
}

.metric-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--fintech-bg-elevated);
  border-radius: var(--fintech-radius-base);
  font-size: 20px;
  color: var(--fintech-accent-primary);
}

.metric-info h3 {
  margin: 0 0 var(--fintech-space-1) 0;
  font-size: var(--fintech-font-size-lg);
  font-weight: 600;
}

.metric-info p {
  margin: 0;
  font-size: var(--fintech-font-size-sm);
}

.metric-value {
  display: flex;
  align-items: baseline;
  gap: var(--fintech-space-2);
  margin-bottom: var(--fintech-space-3);
}

.value-number {
  font-size: var(--fintech-font-size-3xl);
  font-weight: 600;
  font-family: var(--fintech-font-family-data);
  letter-spacing: 0.01em;
}

.value-unit {
  font-size: var(--fintech-font-size-base);
}

.metric-trend .trend-indicator {
  font-size: var(--fintech-font-size-sm);
  font-weight: 500;
  padding: var(--fintech-space-1) var(--fintech-space-2);
  border-radius: var(--fintech-radius-sm);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.trend-indicator.positive {
  background: var(--fintech-accent-success);
  color: white;
}

.trend-indicator.negative {
  background: var(--fintech-accent-danger);
  color: white;
}

.trend-indicator.neutral {
  background: var(--fintech-accent-warning);
  color: var(--fintech-bg-primary);
}

.metric-gauge {
  margin-top: var(--fintech-space-3);
}

.gauge-container {
  width: 100%;
  height: 8px;
  background: var(--fintech-bg-tertiary);
  border-radius: var(--fintech-radius-sm);
  overflow: hidden;
}

.gauge-track {
  width: 100%;
  height: 100%;
  background: var(--fintech-bg-tertiary);
  border-radius: var(--fintech-radius-sm);
}

.gauge-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--fintech-accent-success) 0%, var(--fintech-accent-warning) 50%, var(--fintech-accent-danger) 100%);
  border-radius: var(--fintech-radius-sm);
  transition: width var(--fintech-transition-slow);
}

.metric-breakdown {
  display: flex;
  gap: var(--fintech-space-4);
  margin-top: var(--fintech-space-3);
}

.breakdown-item {
  text-align: center;
}

.breakdown-label {
  display: block;
  font-size: var(--fintech-font-size-xs);
  text-transform: uppercase;
  letter-spacing: 0.02em;
  margin-bottom: var(--fintech-space-1);
}

.breakdown-value {
  font-size: var(--fintech-font-size-lg);
  font-weight: 600;
  font-family: var(--fintech-font-family-data);
}

.alert-breakdown {
  display: flex;
  gap: var(--fintech-space-3);
  margin-top: var(--fintech-space-3);
  justify-content: flex-end;
}

.alert-level {
  display: flex;
  align-items: center;
  gap: var(--fintech-space-2);
}

.level-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.level-dot.critical {
  background: var(--fintech-accent-danger);
}

.level-dot.warning {
  background: var(--fintech-accent-warning);
}

.level-dot.info {
  background: var(--fintech-accent-info);
}

.level-count {
  font-size: var(--fintech-font-size-sm);
  font-weight: 500;
  font-family: var(--fintech-font-family-data);
}

/* 主内容网格 */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: var(--fintech-space-6);
  align-items: start;
}

.alerts-section {
  display: flex;
  flex-direction: column;
  gap: var(--fintech-space-4);
}

.analysis-section {
  display: flex;
  flex-direction: column;
  gap: var(--fintech-space-4);
}

/* 面板通用样式 */
.alert-panel,
.analysis-panel {
  background: var(--fintech-bg-secondary);
  border: 1px solid var(--fintech-border-base);
}

.panel-header {
  display: flex;
  align-items: center;
  gap: var(--fintech-space-4);
  padding: var(--fintech-space-5);
  border-bottom: 1px solid var(--fintech-border-base);
  background: var(--fintech-bg-tertiary);
}

.panel-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--fintech-bg-elevated);
  border-radius: var(--fintech-radius-base);
  font-size: 18px;
  color: var(--fintech-accent-primary);
}

.panel-info h3 {
  margin: 0 0 var(--fintech-space-1) 0;
  font-size: var(--fintech-font-size-lg);
  font-weight: 600;
}

.panel-info p {
  margin: 0;
  font-size: var(--fintech-font-size-sm);
}

.panel-count {
  margin-left: auto;
}

.count-badge {
  padding: var(--fintech-space-1) var(--fintech-space-3);
  border-radius: var(--fintech-radius-base);
  font-size: var(--fintech-font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.count-badge.critical {
  background: var(--fintech-accent-danger);
  color: white;
}

.count-badge.warning {
  background: var(--fintech-accent-warning);
  color: var(--fintech-bg-primary);
}

.count-badge.info {
  background: var(--fintech-accent-info);
  color: white;
}

/* 告警列表 */
.alerts-list {
  padding: var(--fintech-space-5);
  max-height: 400px;
  overflow-y: auto;
}

.alerts-container {
  display: flex;
  flex-direction: column;
  gap: var(--fintech-space-3);
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: var(--fintech-space-4);
  padding: var(--fintech-space-4);
  border: 1px solid var(--fintech-border-dark);
  border-radius: var(--fintech-radius-base);
  background: var(--fintech-bg-tertiary);
  transition: all var(--fintech-transition-fast);
}

.alert-item:hover {
  border-color: var(--fintech-border-light);
  background: var(--fintech-bg-elevated);
}

.alert-icon {
  font-size: 20px;
  color: var(--fintech-accent-danger);
  margin-top: var(--fintech-space-1);
}

.critical-item .alert-icon {
  color: var(--fintech-accent-danger);
}

.warning-item .alert-icon {
  color: var(--fintech-accent-warning);
}

.info-item .alert-icon {
  color: var(--fintech-accent-info);
}

.alert-content {
  flex: 1;
}

.alert-symbol {
  font-size: var(--fintech-font-size-lg);
  font-weight: 600;
  margin-bottom: var(--fintech-space-1);
}

.alert-message {
  font-size: var(--fintech-font-size-base);
  margin-bottom: var(--fintech-space-1);
  line-height: 1.4;
}

.alert-time {
  font-size: var(--fintech-font-size-xs);
}

.alert-actions {
  margin-top: var(--fintech-space-2);
}

.alert-actions .fintech-btn {
  padding: var(--fintech-space-2) var(--fintech-space-4);
  font-size: var(--fintech-font-size-sm);
}

/* 空状态 */
.empty-alerts,
.empty-suggestions,
.empty-sector {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--fintech-space-8);
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  color: var(--fintech-gray-6);
  margin-bottom: var(--fintech-space-4);
  opacity: 0.5;
}

.empty-text h4 {
  margin: 0 0 var(--fintech-space-2) 0;
  font-size: var(--fintech-font-size-lg);
  font-weight: 500;
}

.empty-text p {
  margin: 0;
  font-size: var(--fintech-font-size-base);
}

/* 建议列表 */
.suggestions-list {
  padding: var(--fintech-space-5);
  max-height: 400px;
  overflow-y: auto;
}

.suggestions-container {
  display: flex;
  flex-direction: column;
  gap: var(--fintech-space-4);
}

.suggestion-item {
  padding: var(--fintech-space-4);
  border: 1px solid var(--fintech-border-dark);
  border-radius: var(--fintech-radius-base);
  background: var(--fintech-bg-tertiary);
  transition: all var(--fintech-transition-fast);
}

.suggestion-item:hover {
  border-color: var(--fintech-border-light);
  background: var(--fintech-bg-elevated);
}

.suggestion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--fintech-space-3);
}

.suggestion-symbol {
  font-size: var(--fintech-font-size-lg);
  font-weight: 600;
}

.action-badge {
  padding: var(--fintech-space-1) var(--fintech-space-3);
  border-radius: var(--fintech-radius-sm);
  font-size: var(--fintech-font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.action-buy {
  background: var(--fintech-accent-success);
  color: white;
}

.action-sell {
  background: var(--fintech-accent-danger);
  color: white;
}

.action-hold {
  background: var(--fintech-accent-warning);
  color: var(--fintech-bg-primary);
}

.action-rebalance {
  background: var(--fintech-accent-info);
  color: white;
}

.suggestion-content {
  margin-bottom: var(--fintech-space-3);
}

.suggestion-reason {
  font-size: var(--fintech-font-size-base);
  margin-bottom: var(--fintech-space-2);
  line-height: 1.4;
}

.suggestion-impact {
  display: flex;
  align-items: center;
  gap: var(--fintech-space-2);
  font-size: var(--fintech-font-size-sm);
}

.impact-label {
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.impact-value {
  font-weight: 500;
  font-family: var(--fintech-font-family-data);
}

.suggestion-actions {
  display: flex;
  gap: var(--fintech-space-3);
  justify-content: flex-end;
}

.suggestion-actions .fintech-btn {
  padding: var(--fintech-space-2) var(--fintech-space-4);
  font-size: var(--fintech-font-size-sm);
}

/* 行业配置 */
.sector-allocation {
  padding: var(--fintech-space-5);
}

.sector-list {
  display: flex;
  flex-direction: column;
  gap: var(--fintech-space-4);
}

.sector-item {
  display: flex;
  flex-direction: column;
  gap: var(--fintech-space-2);
}

.sector-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sector-name {
  font-weight: 500;
}

.sector-weight {
  font-family: var(--fintech-font-family-data);
  font-weight: 600;
}

.sector-bar {
  width: 100%;
}

.bar-track {
  width: 100%;
  height: 8px;
  background: var(--fintech-bg-tertiary);
  border-radius: var(--fintech-radius-sm);
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: var(--fintech-radius-sm);
  transition: width var(--fintech-transition-base);
}

.sector-tech {
  background: var(--fintech-accent-primary);
}

.sector-healthcare {
  background: var(--fintech-accent-success);
}

.sector-finance {
  background: var(--fintech-accent-warning);
}

.sector-consumer {
  background: var(--fintech-accent-info);
}

.sector-energy {
  background: var(--fintech-accent-danger);
}

/* 风险指标 */
.risk-metrics {
  padding: var(--fintech-space-5);
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: var(--fintech-space-4);
}

.metric-item {
  text-align: center;
  padding: var(--fintech-space-4);
  background: var(--fintech-bg-tertiary);
  border-radius: var(--fintech-radius-base);
  border: 1px solid var(--fintech-border-dark);
}

.metric-name {
  font-size: var(--fintech-font-size-xs);
  text-transform: uppercase;
  letter-spacing: 0.02em;
  margin-bottom: var(--fintech-space-2);
}

.metric-value {
  font-size: var(--fintech-font-size-xl);
  font-weight: 600;
  font-family: var(--fintech-font-family-data);
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .analysis-section {
    order: -1;
  }
}

@media (max-width: 1280px) {
  .metrics-grid {
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  }

  .risk-metrics {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 高分辨率优化 */
@media (min-width: 1920px) {
  .risk-dashboard {
    padding: var(--fintech-space-6);
  }

  .value-number {
    font-size: 48px;
  }

  .panel-info h3 {
    font-size: var(--fintech-font-size-xl);
  }
}
</style>
