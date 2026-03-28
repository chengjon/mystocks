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
                v-for="(alert, _idx) in criticalAlerts"
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
                v-for="(alert, _idx) in warningAlerts"
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
                v-for="(alert, _idx) in infoAlerts"
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
                v-for="(suggestion, _idx) in suggestions"
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
import { useRiskDashboard } from './composables/useRiskDashboard'

const {
  summary,
  suggestions,
  criticalAlerts,
  warningAlerts,
  infoAlerts,
  activePositions,
  inactivePositions,
  getScoreTrend,
  getScoreChange,
  getActionClass,
  getSectorColor,
  formatCurrency,
  formatTime,
  refresh,
  exportReport,
  handleAlert,
  applySuggestion,
  dismissSuggestion
} = useRiskDashboard()
</script>

<style scoped lang="scss">
@use './styles/RiskDashboard.scss' as *;
</style>
