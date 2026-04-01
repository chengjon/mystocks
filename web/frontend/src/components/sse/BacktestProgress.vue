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
          <el-icon :size="emptyIconSize" class="backtest-progress-icon--info"><Timer /></el-icon>
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
          :stroke-width="progressStrokeWidth"
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
        <el-row :gutter="resultsGutter">
          <el-col :span="8" v-for="(value, key) in results" :key="key">
            <el-card shadow="never" class="result-card">
              <el-statistic
                :title="getResultLabel(key)"
                :value="value"
                :precision="getResultPrecision(key)"
                :class="['result-statistic', getResultStateClass(key, value)]"
              >
                <template #prefix>
                  <el-icon :class="getResultStateClass(key, value)">
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
        <el-row :gutter="performanceGutter" class="performance-cards">
          <el-col :span="8">
            <div class="metric-card return-card">
              <div class="metric-icon">
                <el-icon :size="metricCardIconSize"><TrendCharts /></el-icon>
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
                <el-icon :size="metricCardIconSize"><Histogram /></el-icon>
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
                <el-icon :size="metricCardIconSize"><Sort /></el-icon>
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
  TrendCharts, _SuccessFilled, _CircleClose, Sort, _Warning
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

const progressStrokeWidth = 20
const resultsGutter = 16
const performanceGutter = 12
const emptyIconSize = 'var(--artdeco-spacing-20)'
const metricCardIconSize = 24

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

const getResultStateClass = (key, value) => {
  if (key === 'total_return' || key === 'annual_return') {
    return value > 0 ? 'backtest-progress-icon--success' : 'backtest-progress-icon--danger'
  }
  if (key === 'max_drawdown') {
    return 'backtest-progress-icon--danger'
  }
  if (key === 'sharpe_ratio') {
    return value > 1
      ? 'backtest-progress-icon--success'
      : value > 0
        ? 'backtest-progress-icon--warning'
        : 'backtest-progress-icon--danger'
  }
  return 'backtest-progress-icon--info'
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
@use '@/styles/artdeco-tokens.scss' as *;

.backtest-progress-card {
  .backtest-progress-icon--info {
    color: var(--artdeco-info);
  }

  .backtest-progress-icon--success {
    color: var(--artdeco-rise);
  }

  .backtest-progress-icon--warning {
    color: var(--artdeco-warning);
  }

  .backtest-progress-icon--danger {
    color: var(--artdeco-down);
  }

  margin-bottom: var(--artdeco-spacing-5);
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-none);
  background: var(--artdeco-bg-card);

  :deep(.el-card__header) {
    padding: var(--artdeco-spacing-4);
    border-bottom: 1px solid var(--artdeco-border-default);
    background: linear-gradient(
      180deg,
      color-mix(in srgb, var(--artdeco-gold-primary) 6%, var(--artdeco-bg-card)) 0%,
      var(--artdeco-bg-card) 100%
    );
  }

  :deep(.el-card__body) {
    padding: var(--artdeco-spacing-4);
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    .title {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-2);
      font-family: var(--artdeco-font-heading, var(--font-display));
      font-size: var(--artdeco-text-base);
      font-weight: var(--artdeco-font-semibold);
      color: var(--artdeco-gold-primary);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);

      .el-icon {
        font-size: var(--artdeco-text-lg);
      }
    }

    .connection-status .el-tag {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-1);
    }
  }

  .empty-state {
    padding: var(--artdeco-spacing-10) var(--artdeco-spacing-5);
    text-align: center;
  }

  .error-state {
    padding: var(--artdeco-spacing-5);
  }

  .backtest-content {
    .progress-section {
      margin-bottom: var(--artdeco-spacing-5);

      :deep(.el-progress-bar__outer) {
        border-radius: var(--artdeco-radius-none);
        background: color-mix(in srgb, var(--artdeco-gold-primary) 8%, var(--artdeco-bg-elevated));
      }

      :deep(.el-progress-bar__inner) {
        border-radius: var(--artdeco-radius-none);
      }

      .percentage-text {
        color: var(--artdeco-fg-primary);
        font-family: var(--artdeco-font-accent, var(--font-mono));
        font-weight: var(--artdeco-font-semibold);
        font-size: var(--artdeco-text-compact-base);
      }
    }

    .status-section {
      margin-bottom: var(--artdeco-spacing-5);

      :deep(.el-descriptions__label) {
        width: calc(var(--artdeco-spacing-20) + var(--artdeco-spacing-2) + (var(--artdeco-spacing-px) * 2));
      }
    }

    .results-section {
      margin-top: var(--artdeco-spacing-5);

      .el-divider {
        margin: var(--artdeco-spacing-4) 0;

        :deep(.el-divider__text) {
          display: flex;
          align-items: center;
          gap: calc(var(--artdeco-spacing-3) / 2);
          font-family: var(--artdeco-font-heading, var(--font-display));
          font-weight: var(--artdeco-font-semibold);
          color: var(--artdeco-gold-primary);
          letter-spacing: var(--artdeco-tracking-wide);
          text-transform: uppercase;
        }
      }

      .result-card {
        background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
        border: 1px solid var(--artdeco-border-default);
        border-radius: var(--artdeco-radius-none);

        :deep(.el-card__body) {
          padding: var(--artdeco-spacing-3);
        }

        .el-statistic {
          :deep(.el-statistic__head) {
            font-family: var(--artdeco-font-body, var(--font-body));
            font-size: var(--artdeco-text-compact-sm);
            color: var(--artdeco-fg-muted);
            margin-bottom: calc(var(--artdeco-spacing-3) / 2);
          }

          :deep(.el-statistic__content) {
            font-family: var(--artdeco-font-accent, var(--font-mono));
            font-size: var(--artdeco-text-lg);
            font-weight: var(--artdeco-font-semibold);
            color: var(--artdeco-fg-primary);
          }
        }
      }
    }

    .performance-section {
      margin-top: var(--artdeco-spacing-5);

      .performance-cards {
        .metric-card {
          display: flex;
          align-items: center;
          gap: var(--artdeco-spacing-3);
          padding: var(--artdeco-spacing-4);
          border-radius: var(--artdeco-radius-none);
          background: linear-gradient(
            135deg,
            color-mix(in srgb, var(--artdeco-gold-primary) 5%, var(--artdeco-bg-card)) 0%,
            var(--artdeco-bg-card) 100%
          );
          border: 1px solid var(--artdeco-border-default);
          transition:
            transform var(--artdeco-transition-quick) var(--artdeco-ease-out),
            box-shadow var(--artdeco-transition-quick) var(--artdeco-ease-out),
            border-color var(--artdeco-transition-quick) var(--artdeco-ease-out);

          &:hover {
            transform: translateY(calc(var(--artdeco-spacing-px) * -2));
            border-color: var(--artdeco-border-hover);
            box-shadow: var(--artdeco-glow-subtle);
          }

          .metric-icon {
            width: var(--artdeco-spacing-12);
            height: var(--artdeco-spacing-12);
            border-radius: var(--artdeco-radius-none);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--artdeco-fg-primary);
          }

          .metric-info {
            flex: 1;

            .metric-label {
              font-family: var(--artdeco-font-body, var(--font-body));
              font-size: var(--artdeco-text-compact-sm);
              color: var(--artdeco-fg-muted);
              margin-bottom: var(--artdeco-spacing-1);
            }

            .metric-value {
              font-family: var(--artdeco-font-accent, var(--font-mono));
              font-size: var(--artdeco-text-xl);
              font-weight: var(--artdeco-font-bold);
              color: var(--artdeco-fg-primary);

              &.positive {
                color: var(--artdeco-rise);
              }

              &.negative {
                color: var(--artdeco-down);
              }
            }
          }

          &.return-card .metric-icon {
            background: linear-gradient(
              135deg,
              color-mix(in srgb, var(--artdeco-rise) 80%, var(--artdeco-bg-card)) 0%,
              var(--artdeco-rise) 100%
            );
          }

          &.sharpe-card .metric-icon {
            background: linear-gradient(
              135deg,
              color-mix(in srgb, var(--artdeco-warning) 80%, var(--artdeco-bg-card)) 0%,
              var(--artdeco-gold-primary) 100%
            );
          }

          &.drawdown-card .metric-icon {
            background: linear-gradient(
              135deg,
              color-mix(in srgb, var(--artdeco-down) 80%, var(--artdeco-bg-card)) 0%,
              var(--artdeco-down) 100%
            );
          }
        }
      }
    }

    .connection-info {
      margin-top: var(--artdeco-spacing-4);
      padding-top: var(--artdeco-spacing-3);
      border-top: 1px solid var(--artdeco-border-default);
      text-align: center;

      .el-text {
        display: inline-flex;
        align-items: center;
        gap: var(--artdeco-spacing-1);
      }
    }
  }
}
</style>
