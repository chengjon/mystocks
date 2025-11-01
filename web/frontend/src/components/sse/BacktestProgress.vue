<template>
  <el-card class="backtest-progress-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <span class="title">
          <el-icon><Histogram /></el-icon>
          回测执行进度
        </span>
        <div class="connection-status">
          <el-tag :type="isConnected ? 'success' : 'danger'" size="small" effect="dark">
            <el-icon v-if="isConnected"><Connection /></el-icon>
            <el-icon v-else><Close /></el-icon>
            {{ isConnected ? '已连接' : '未连接' }}
          </el-tag>
        </div>
      </div>
    </template>

    <!-- 无任务状态 -->
    <div v-if="!backtestId && isConnected" class="empty-state">
      <el-empty description="等待回测任务...">
        <template #image>
          <el-icon :size="80" color="#67c23a"><Timer /></el-icon>
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

    <!-- 回测中状态 -->
    <div v-else-if="backtestId" class="backtest-content">
      <!-- 进度条 -->
      <div class="progress-section">
        <el-progress
          :percentage="progress"
          :status="getProgressStatus"
          :stroke-width="20"
          :text-inside="true"
        >
          <template #default="{ percentage }">
            <span class="percentage-text">{{ percentage }}%</span>
          </template>
        </el-progress>
      </div>

      <!-- 状态信息 -->
      <div class="status-section">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="回测ID">
            <el-text type="info" size="small">{{ backtestId }}</el-text>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType" size="small">{{ getStatusText }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="当前日期" v-if="currentDate">
            <el-text type="primary" size="small">
              <el-icon><Calendar /></el-icon>
              {{ currentDate }}
            </el-text>
          </el-descriptions-item>
          <el-descriptions-item label="消息" :span="currentDate ? 1 : 2">
            {{ message || '正在回测中...' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 回测结果 -->
      <div v-if="Object.keys(results).length > 0" class="results-section">
        <el-divider content-position="left">
          <el-icon><TrendCharts /></el-icon>
          实时结果
        </el-divider>
        <el-row :gutter="16">
          <el-col :span="8" v-for="(value, key) in results" :key="key">
            <el-card shadow="never" class="result-card">
              <el-statistic
                :title="getResultLabel(key)"
                :value="value"
                :precision="getResultPrecision(key)"
              >
                <template #prefix>
                  <el-icon :color="getResultColor(key, value)">
                    <component :is="getResultIcon(key)" />
                  </el-icon>
                </template>
                <template #suffix>
                  <span v-if="isPercentageMetric(key)">%</span>
                </template>
              </el-statistic>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 性能指标卡片 -->
      <div v-if="hasPerformanceMetrics" class="performance-section">
        <el-row :gutter="12" class="performance-cards">
          <el-col :span="8">
            <div class="metric-card return-card">
              <div class="metric-icon">
                <el-icon :size="24"><TrendCharts /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-label">总收益率</div>
                <div class="metric-value" :class="{ positive: results.total_return > 0, negative: results.total_return < 0 }">
                  {{ formatPercentage(results.total_return) }}
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="metric-card sharpe-card">
              <div class="metric-icon">
                <el-icon :size="24"><Histogram /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-label">夏普比率</div>
                <div class="metric-value">{{ results.sharpe_ratio?.toFixed(2) || 'N/A' }}</div>
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="metric-card drawdown-card">
              <div class="metric-icon">
                <el-icon :size="24"><Sort /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-label">最大回撤</div>
                <div class="metric-value negative">
                  {{ formatPercentage(results.max_drawdown) }}
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 连接统计 -->
      <div class="connection-info">
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
  Histogram, Connection, Close, Timer, Refresh, Calendar,
  TrendCharts, SuccessFilled, CircleClose, Sort, Warning
} from '@element-plus/icons-vue'
import { useBacktestProgress } from '@/composables/useSSE'

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

// Use backtest progress composable
const {
  isConnected,
  error,
  backtestId,
  progress,
  status,
  message,
  currentDate,
  results,
  connectionCount,
  retryCount,
  reset
} = useBacktestProgress({
  clientId: props.clientId,
  autoConnect: props.autoConnect
})

// Computed properties
const getProgressStatus = computed(() => {
  if (status.value === 'completed') return 'success'
  if (status.value === 'failed') return 'exception'
  if (progress.value >= 100) return 'success'
  return undefined
})

const getStatusType = computed(() => {
  const statusMap = {
    'running': 'primary',
    'completed': 'success',
    'failed': 'danger',
    'pending': 'warning'
  }
  return statusMap[status.value] || 'info'
})

const getStatusText = computed(() => {
  const statusMap = {
    'running': '运行中',
    'completed': '已完成',
    'failed': '失败',
    'pending': '等待中',
    'started': '已启动'
  }
  return statusMap[status.value] || status.value
})

const hasPerformanceMetrics = computed(() => {
  return results.value.total_return !== undefined ||
         results.value.sharpe_ratio !== undefined ||
         results.value.max_drawdown !== undefined
})

// Helper functions
const getResultLabel = (key) => {
  const labelMap = {
    'total_return': '总收益率',
    'sharpe_ratio': '夏普比率',
    'max_drawdown': '最大回撤',
    'win_rate': '胜率',
    'profit_factor': '盈亏比',
    'total_trades': '总交易次数',
    'annual_return': '年化收益',
    'volatility': '波动率'
  }
  return labelMap[key] || key
}

const getResultPrecision = (key) => {
  const precisionMap = {
    'total_return': 2,
    'sharpe_ratio': 2,
    'max_drawdown': 2,
    'win_rate': 2,
    'profit_factor': 2,
    'annual_return': 2,
    'volatility': 2,
    'total_trades': 0
  }
  return precisionMap[key] !== undefined ? precisionMap[key] : 2
}

const getResultIcon = (key) => {
  const iconMap = {
    'total_return': 'TrendCharts',
    'sharpe_ratio': 'Histogram',
    'max_drawdown': 'Sort',
    'win_rate': 'SuccessFilled',
    'profit_factor': 'TrendCharts',
    'total_trades': 'Document'
  }
  return iconMap[key] || 'DataLine'
}

const getResultColor = (key, value) => {
  if (key === 'total_return' || key === 'annual_return') {
    return value > 0 ? '#67c23a' : '#f56c6c'
  }
  if (key === 'max_drawdown') {
    return '#f56c6c'
  }
  if (key === 'sharpe_ratio') {
    return value > 1 ? '#67c23a' : value > 0 ? '#e6a23c' : '#f56c6c'
  }
  return '#409eff'
}

const isPercentageMetric = (key) => {
  return ['total_return', 'max_drawdown', 'win_rate', 'annual_return', 'volatility'].includes(key)
}

const formatPercentage = (value) => {
  if (value === undefined || value === null) return 'N/A'
  const num = parseFloat(value)
  if (isNaN(num)) return 'N/A'
  return `${num > 0 ? '+' : ''}${(num * 100).toFixed(2)}%`
}
</script>

<style scoped lang="scss">
.backtest-progress-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

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

    .connection-status {
      .el-tag {
        display: flex;
        align-items: center;
        gap: 4px;
      }
    }
  }

  .empty-state {
    padding: 40px 20px;
    text-align: center;
  }

  .error-state {
    padding: 20px;
  }

  .backtest-content {
    .progress-section {
      margin-bottom: 20px;

      .percentage-text {
        color: #fff;
        font-weight: 600;
        font-size: 14px;
      }
    }

    .status-section {
      margin-bottom: 20px;

      :deep(.el-descriptions__label) {
        width: 90px;
      }
    }

    .results-section {
      margin-top: 20px;

      .el-divider {
        margin: 16px 0;

        :deep(.el-divider__text) {
          display: flex;
          align-items: center;
          gap: 6px;
          font-weight: 600;
          color: #303133;
        }
      }

      .result-card {
        background: #f5f7fa;
        border: none;

        :deep(.el-card__body) {
          padding: 12px;
        }

        .el-statistic {
          :deep(.el-statistic__head) {
            font-size: 12px;
            color: #606266;
            margin-bottom: 6px;
          }

          :deep(.el-statistic__content) {
            font-size: 18px;
            font-weight: 600;
          }
        }
      }
    }

    .performance-section {
      margin-top: 20px;

      .performance-cards {
        .metric-card {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 16px;
          border-radius: 8px;
          background: linear-gradient(135deg, #f5f7fa 0%, #fff 100%);
          border: 1px solid #ebeef5;
          transition: all 0.3s;

          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          }

          .metric-icon {
            width: 48px;
            height: 48px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
          }

          .metric-info {
            flex: 1;

            .metric-label {
              font-size: 12px;
              color: #909399;
              margin-bottom: 4px;
            }

            .metric-value {
              font-size: 22px;
              font-weight: 700;
              color: #303133;

              &.positive {
                color: #67c23a;
              }

              &.negative {
                color: #f56c6c;
              }
            }
          }

          &.return-card .metric-icon {
            background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
          }

          &.sharpe-card .metric-icon {
            background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
          }

          &.drawdown-card .metric-icon {
            background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%);
          }
        }
      }
    }

    .connection-info {
      margin-top: 16px;
      padding-top: 12px;
      border-top: 1px solid #ebeef5;
      text-align: center;

      .el-text {
        display: inline-flex;
        align-items: center;
        gap: 4px;
      }
    }
  }
}
</style>
