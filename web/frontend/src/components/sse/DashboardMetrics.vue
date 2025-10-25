<template>
  <el-card class="dashboard-metrics-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <span class="title">
          <el-icon><Odometer /></el-icon>
          实时指标
        </span>
        <div class="header-actions">
          <el-tag :type="isConnected ? 'success' : 'danger'" size="small" effect="dark">
            <el-icon v-if="isConnected"><Connection /></el-icon>
            <el-icon v-else><Close /></el-icon>
            {{ isConnected ? '已连接' : '未连接' }}
          </el-tag>
          <el-text v-if="lastUpdate" type="info" size="small">
            <el-icon><Clock /></el-icon>
            更新于 {{ formatTimestamp(lastUpdate) }}
          </el-text>
        </div>
      </div>
    </template>

    <!-- 无数据状态 -->
    <div v-if="Object.keys(metrics).length === 0 && isConnected" class="empty-state">
      <el-empty description="等待数据更新...">
        <template #image>
          <el-icon :size="80" color="#409eff"><Loading /></el-icon>
        </template>
      </el-empty>
    </div>

    <!-- 连接失败状态 -->
    <div v-else-if="error" class="error-state">
      <el-result icon="error" title="连接失败" :sub-title="error.message">
        <template #extra>
          <el-button type="primary" @click="reset">
            <el-icon><Refresh /></el-icon>
            重新连接
          </el-button>
        </template>
      </el-result>
    </div>

    <!-- 指标显示 -->
    <div v-else class="metrics-content">
      <!-- 核心指标卡片 -->
      <el-row :gutter="16" class="core-metrics">
        <el-col :xs="24" :sm="12" :md="6" v-if="metrics.total_value !== undefined">
          <div class="metric-card value-card">
            <div class="metric-icon">
              <el-icon :size="32"><Money /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">总资产价值</div>
              <div class="metric-value">
                {{ formatCurrency(metrics.total_value) }}
              </div>
              <div class="metric-change" v-if="metrics.value_change">
                <span :class="{ positive: metrics.value_change > 0, negative: metrics.value_change < 0 }">
                  <el-icon v-if="metrics.value_change > 0"><CaretTop /></el-icon>
                  <el-icon v-else><CaretBottom /></el-icon>
                  {{ formatPercentage(metrics.value_change) }}
                </span>
              </div>
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6" v-if="metrics.daily_return !== undefined">
          <div class="metric-card return-card">
            <div class="metric-icon">
              <el-icon :size="32"><TrendCharts /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">日收益率</div>
              <div
                class="metric-value"
                :class="{ positive: metrics.daily_return > 0, negative: metrics.daily_return < 0 }"
              >
                {{ formatPercentage(metrics.daily_return) }}
              </div>
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6" v-if="metrics.positions_count !== undefined">
          <div class="metric-card positions-card">
            <div class="metric-icon">
              <el-icon :size="32"><Grid /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">持仓数量</div>
              <div class="metric-value">{{ metrics.positions_count }}</div>
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6" v-if="metrics.open_orders !== undefined">
          <div class="metric-card orders-card">
            <div class="metric-icon">
              <el-icon :size="32"><Document /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">挂单数量</div>
              <div class="metric-value">{{ metrics.open_orders }}</div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 更多指标 -->
      <div v-if="hasMoreMetrics" class="more-metrics">
        <el-divider content-position="left">
          <el-icon><DataAnalysis /></el-icon>
          详细指标
        </el-divider>

        <el-row :gutter="16">
          <el-col
            :xs="24"
            :sm="12"
            :md="8"
            :lg="6"
            v-for="(value, key) in filteredMetrics"
            :key="key"
          >
            <el-statistic
              :title="getMetricLabel(key)"
              :value="value"
              :precision="getMetricPrecision(key)"
              class="metric-statistic"
            >
              <template #prefix>
                <el-icon :color="getMetricColor(key, value)">
                  <component :is="getMetricIcon(key)" />
                </el-icon>
              </template>
              <template #suffix v-if="isPercentageMetric(key)">
                %
              </template>
            </el-statistic>
          </el-col>
        </el-row>
      </div>

      <!-- 更新类型和连接统计 -->
      <div class="footer-info">
        <el-text type="info" size="small">
          <el-icon><Notification /></el-icon>
          更新类型: {{ updateType || 'N/A' }}
        </el-text>
        <el-text type="info" size="small">
          <el-icon><Connection /></el-icon>
          连接次数: {{ connectionCount }} | 重试次数: {{ retryCount }}
        </el-text>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import {
  Odometer, Connection, Close, Clock, Loading, Refresh,
  Money, TrendCharts, Grid, Document, DataAnalysis,
  CaretTop, CaretBottom, Notification, Histogram,
  SuccessFilled, Warning
} from '@element-plus/icons-vue'
import { useDashboardUpdates } from '@/composables/useSSE'

// Props
const props = defineProps({
  clientId: {
    type: String,
    default: null
  },
  autoConnect: {
    type: Boolean,
    default: true
  }
})

// Use dashboard updates composable
const {
  isConnected,
  error,
  metrics,
  updateType,
  lastUpdate,
  connectionCount,
  retryCount,
  reset
} = useDashboardUpdates({
  clientId: props.clientId,
  autoConnect: props.autoConnect
})

// Computed properties
const coreMetricKeys = ['total_value', 'daily_return', 'positions_count', 'open_orders', 'value_change']

const filteredMetrics = computed(() => {
  const result = {}
  Object.keys(metrics.value).forEach(key => {
    if (!coreMetricKeys.includes(key)) {
      result[key] = metrics.value[key]
    }
  })
  return result
})

const hasMoreMetrics = computed(() => {
  return Object.keys(filteredMetrics.value).length > 0
})

// Helper functions
const formatCurrency = (value) => {
  if (value === undefined || value === null) return 'N/A'
  const num = parseFloat(value)
  if (isNaN(num)) return 'N/A'

  if (num >= 1000000) {
    return `¥${(num / 1000000).toFixed(2)}M`
  } else if (num >= 1000) {
    return `¥${(num / 1000).toFixed(2)}K`
  }
  return `¥${num.toFixed(2)}`
}

const formatPercentage = (value) => {
  if (value === undefined || value === null) return 'N/A'
  const num = parseFloat(value)
  if (isNaN(num)) return 'N/A'
  return `${num > 0 ? '+' : ''}${(num * 100).toFixed(2)}%`
}

const formatTimestamp = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date

  // Less than 1 minute
  if (diff < 60000) {
    return '刚刚'
  }
  // Less than 1 hour
  if (diff < 3600000) {
    return `${Math.floor(diff / 60000)} 分钟前`
  }
  // Full time
  return date.toLocaleTimeString('zh-CN')
}

const getMetricLabel = (key) => {
  const labelMap = {
    'total_pnl': '总盈亏',
    'unrealized_pnl': '浮动盈亏',
    'realized_pnl': '已实现盈亏',
    'available_cash': '可用资金',
    'margin_used': '已用保证金',
    'margin_rate': '保证金比率',
    'win_rate': '胜率',
    'sharpe_ratio': '夏普比率',
    'max_drawdown': '最大回撤',
    'total_trades': '总交易次数',
    'winning_trades': '盈利交易',
    'losing_trades': '亏损交易'
  }
  return labelMap[key] || key
}

const getMetricPrecision = (key) => {
  const precisionMap = {
    'margin_rate': 2,
    'win_rate': 2,
    'sharpe_ratio': 2,
    'max_drawdown': 2,
    'total_trades': 0,
    'winning_trades': 0,
    'losing_trades': 0
  }
  return precisionMap[key] !== undefined ? precisionMap[key] : 2
}

const getMetricIcon = (key) => {
  const iconMap = {
    'total_pnl': 'Money',
    'unrealized_pnl': 'TrendCharts',
    'realized_pnl': 'SuccessFilled',
    'available_cash': 'Money',
    'margin_used': 'Histogram',
    'margin_rate': 'DataAnalysis',
    'win_rate': 'SuccessFilled',
    'sharpe_ratio': 'TrendCharts',
    'max_drawdown': 'Warning',
    'total_trades': 'Document',
    'winning_trades': 'SuccessFilled',
    'losing_trades': 'Warning'
  }
  return iconMap[key] || 'DataLine'
}

const getMetricColor = (key, value) => {
  if (['total_pnl', 'unrealized_pnl', 'realized_pnl'].includes(key)) {
    return value > 0 ? '#67c23a' : value < 0 ? '#f56c6c' : '#909399'
  }
  if (key === 'max_drawdown') {
    return '#f56c6c'
  }
  if (key === 'win_rate' || key === 'sharpe_ratio') {
    return '#67c23a'
  }
  return '#409eff'
}

const isPercentageMetric = (key) => {
  return ['margin_rate', 'win_rate', 'max_drawdown'].includes(key)
}
</script>

<style scoped lang="scss">
.dashboard-metrics-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;

    .title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 600;
      color: #303133;

      .el-icon {
        font-size: 18px;
      }
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 12px;

      .el-tag {
        display: flex;
        align-items: center;
        gap: 4px;
      }

      .el-text {
        display: inline-flex;
        align-items: center;
        gap: 4px;
      }
    }
  }

  .empty-state {
    padding: 40px 20px;
    text-align: center;

    :deep(.el-empty__image) {
      .el-icon {
        animation: spin 2s linear infinite;
      }
    }
  }

  .error-state {
    padding: 20px;
  }

  .metrics-content {
    .core-metrics {
      margin-bottom: 20px;

      .metric-card {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 20px;
        border-radius: 12px;
        background: linear-gradient(135deg, #f5f7fa 0%, #fff 100%);
        border: 2px solid #ebeef5;
        transition: all 0.3s;
        min-height: 120px;

        &:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        }

        .metric-icon {
          width: 64px;
          height: 64px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          flex-shrink: 0;
        }

        .metric-info {
          flex: 1;

          .metric-label {
            font-size: 13px;
            color: #909399;
            margin-bottom: 8px;
          }

          .metric-value {
            font-size: 24px;
            font-weight: 700;
            color: #303133;
            margin-bottom: 4px;

            &.positive {
              color: #67c23a;
            }

            &.negative {
              color: #f56c6c;
            }
          }

          .metric-change {
            font-size: 14px;

            span {
              display: inline-flex;
              align-items: center;
              gap: 2px;
              font-weight: 600;

              &.positive {
                color: #67c23a;
              }

              &.negative {
                color: #f56c6c;
              }
            }
          }
        }

        &.value-card .metric-icon {
          background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
        }

        &.return-card .metric-icon {
          background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
        }

        &.positions-card .metric-icon {
          background: linear-gradient(135deg, #e6a23c 0%, #f0c78a 100%);
        }

        &.orders-card .metric-icon {
          background: linear-gradient(135deg, #909399 0%, #b1b3b8 100%);
        }
      }
    }

    .more-metrics {
      margin-top: 24px;

      .el-divider {
        margin: 16px 0 20px;

        :deep(.el-divider__text) {
          display: flex;
          align-items: center;
          gap: 6px;
          font-weight: 600;
          color: #303133;
        }
      }

      .metric-statistic {
        margin-bottom: 16px;
        padding: 16px;
        background: #f5f7fa;
        border-radius: 8px;

        :deep(.el-statistic__head) {
          font-size: 12px;
          color: #606266;
          margin-bottom: 8px;
        }

        :deep(.el-statistic__content) {
          font-size: 20px;
          font-weight: 600;
        }
      }
    }

    .footer-info {
      margin-top: 20px;
      padding-top: 16px;
      border-top: 1px solid #ebeef5;
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;

      .el-text {
        display: inline-flex;
        align-items: center;
        gap: 4px;
      }
    }
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

// Responsive adjustments
@media (max-width: 768px) {
  .dashboard-metrics-card {
    .core-metrics .metric-card {
      min-height: 100px;
      padding: 16px;

      .metric-icon {
        width: 48px;
        height: 48px;

        .el-icon {
          font-size: 24px !important;
        }
      }

      .metric-info {
        .metric-value {
          font-size: 20px;
        }
      }
    }
  }
}
</style>
