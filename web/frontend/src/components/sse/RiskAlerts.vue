<template>
  <el-card class="risk-alerts-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <span class="title">
          <el-icon><Bell /></el-icon>
          风险告警
          <el-badge v-if="unreadCount > 0" :value="unreadCount" :max="99" class="alert-badge" />
        </span>
        <div class="header-actions">
          <el-tag :type="isConnected ? 'success' : 'danger'" size="small" effect="dark">
            <el-icon v-if="isConnected"><Connection /></el-icon>
            <el-icon v-else><Close /></el-icon>
            {{ isConnected ? '已连接' : '未连接' }}
          </el-tag>
          <el-button
            v-if="alerts.length > 0"
            size="small"
            text
            @click="markAllAsRead"
            :disabled="unreadCount === 0"
          >
            <el-icon><Select /></el-icon>
            全部已读
          </el-button>
          <el-button
            v-if="alerts.length > 0"
            size="small"
            text
            type="danger"
            @click="clearAlerts"
          >
            <el-icon><Delete /></el-icon>
            清空
          </el-button>
        </div>
      </div>
    </template>

    <!-- 无告警状态 -->
    <div v-if="alerts.length === 0 && isConnected" class="empty-state">
      <el-empty description="暂无风险告警">
        <template #image>
          <el-icon :size="emptyIconSize" :color="emptyIconColor"><CircleCheck /></el-icon>
        </template>
        <template #description>
          <p class="empty-desc">系统运行正常，暂无风险告警</p>
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

    <!-- 告警列表 -->
    <div v-else class="alerts-content">
      <el-timeline>
        <el-timeline-item
          v-for="(alert, _idx) in alerts"
          :key="alert.id"
          :timestamp="formatTimestamp(alert.timestamp)"
          :type="getTimelineType(alert.severity)"
          :hollow="alert.read"
          placement="top"
        >
          <el-card
            :class="[
              'alert-item',
              `severity-${alert.severity}`,
              { unread: !alert.read }
            ]"
            shadow="hover"
            @click="markAsRead(alert.id)"
          >
            <div class="alert-header">
              <div class="alert-title">
                <el-icon :size="severityIconSize" :color="getSeverityColor(alert.severity)">
                  <component :is="getSeverityIcon(alert.severity)" />
                </el-icon>
                <span>{{ alert.alert_type || '风险告警' }}</span>
                <el-tag :type="getSeverityTagType(alert.severity)" size="small" effect="dark">
                  {{ getSeverityText(alert.severity) }}
                </el-tag>
              </div>
              <el-icon
                v-if="!alert.read"
                :size="unreadDotSize"
                :color="unreadDotColor"
                class="unread-dot"
              >
                <CircleFilled />
              </el-icon>
            </div>

            <div class="alert-body">
              <p class="alert-message">{{ alert.message }}</p>

              <el-descriptions :column="2" size="small" border class="alert-details">
                <el-descriptions-item label="指标">
                  {{ alert.metric_name || 'N/A' }}
                </el-descriptions-item>
                <el-descriptions-item label="当前值">
                  <span :class="getValueClass(alert.metric_value, alert.threshold)">
                    {{ formatValue(alert.metric_value) }}
                  </span>
                </el-descriptions-item>
                <el-descriptions-item label="阈值">
                  {{ formatValue(alert.threshold) }}
                </el-descriptions-item>
                <el-descriptions-item label="实体类型" v-if="alert.entity_type">
                  {{ alert.entity_type }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>

      <!-- 连接统计 -->
      <div class="connection-info">
        <el-text type="info" size="small">
          <el-icon><Connection /></el-icon>
          连接次数: {{ connectionCount }} | 重试次数: {{ retryCount }} | 告警总数: {{ alerts.length }}
        </el-text>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import {
  Bell, Connection, Close, Select, Delete, CircleCheck,
  Refresh, _Warning, _InfoFilled
} from '@element-plus/icons-vue'
import { ElNotification } from 'element-plus'
import { useRiskAlerts } from '@/composables/useSSE'

// Props
const props = defineProps({
  clientId: {
    type: String,
    default: null
  },
  autoConnect: {
    type: Boolean,
    default: true
  },
  maxAlerts: {
    type: Number,
    default: 100
  },
  showNotification: {
    type: Boolean,
    default: true
  }
})

// Use risk alerts composable
const {
  isConnected,
  error,
  alerts,
  _latestAlert,
  unreadCount,
  connectionCount,
  retryCount,
  markAsRead,
  markAllAsRead,
  clearAlerts,
  reset,
  addEventListener
} = useRiskAlerts({
  clientId: props.clientId,
  autoConnect: props.autoConnect,
  maxAlerts: props.maxAlerts
})

const emptyIconSize = 'var(--artdeco-spacing-20)'
const emptyIconColor = 'var(--artdeco-down)'
const severityIconSize = 18
const unreadDotSize = 10
const unreadDotColor = 'var(--artdeco-info)'
const severityLowColor = 'var(--artdeco-fg-muted)'
const severityMediumColor = 'var(--artdeco-warning)'
const severityHighColor = 'var(--artdeco-rise)'
const severityCriticalColor = 'var(--artdeco-rise)'

// Watch for new alerts and show notifications
if (props.showNotification) {
  addEventListener('risk_alert', (data) => {
    const alert = data.data || data
    ElNotification({
      title: `${getSeverityText(alert.severity)} - ${alert.alert_type}`,
      message: alert.message,
      type: getSeverityNotificationType(alert.severity),
      duration: 0,  // Don't auto-close
      position: 'top-right'
    })
  })
}

// Helper functions
const getSeverityText = (severity) => {
  const textMap = {
    'low': '低风险',
    'medium': '中风险',
    'high': '高风险',
    'critical': '严重风险'
  }
  return textMap[severity] || severity
}

const getSeverityTagType = (severity) => {
  const typeMap = {
    'low': 'info',
    'medium': 'warning',
    'high': 'danger',
    'critical': 'danger'
  }
  return typeMap[severity] || 'info'
}

const getSeverityColor = (severity) => {
  const colorMap = {
    'low': severityLowColor,
    'medium': severityMediumColor,
    'high': severityHighColor,
    'critical': severityCriticalColor
  }
  return colorMap[severity] || severityLowColor
}

const getSeverityIcon = (severity) => {
  const iconMap = {
    'low': 'InfoFilled',
    'medium': 'Warning',
    'high': 'Warning',
    'critical': 'CircleClose'
  }
  return iconMap[severity] || 'InfoFilled'
}

const getSeverityNotificationType = (severity) => {
  const typeMap = {
    'low': 'info',
    'medium': 'warning',
    'high': 'error',
    'critical': 'error'
  }
  return typeMap[severity] || 'info'
}

const getTimelineType = (severity) => {
  const typeMap = {
    'low': 'info',
    'medium': 'warning',
    'high': 'danger',
    'critical': 'danger'
  }
  return typeMap[severity] || 'primary'
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
  // Less than 1 day
  if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)} 小时前`
  }
  // Full date
  return date.toLocaleString('zh-CN')
}

const formatValue = (value) => {
  if (value === undefined || value === null) return 'N/A'
  if (typeof value === 'number') {
    return value.toFixed(4)
  }
  return value.toString()
}

const getValueClass = (value, threshold) => {
  if (value === undefined || value === null || threshold === undefined || threshold === null) {
    return ''
  }
  return value > threshold ? 'value-exceeded' : 'value-normal'
}
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.risk-alerts-card {
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
      position: relative;
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);

      .el-icon {
        font-size: var(--artdeco-text-lg);
      }

      .alert-badge {
        margin-left: var(--artdeco-spacing-1);
      }
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-2);

      .el-tag {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-1);
      }
    }
  }

  .empty-state {
    padding: var(--artdeco-spacing-10) var(--artdeco-spacing-5);
    text-align: center;

    .empty-desc {
      color: var(--artdeco-down);
      font-weight: var(--artdeco-font-medium);
      margin-top: var(--artdeco-spacing-3);
    }
  }

  .error-state {
    padding: var(--artdeco-spacing-5);
  }

  .alerts-content {
    max-height: calc((var(--artdeco-spacing-24) * 6) + var(--artdeco-spacing-6));
    overflow-y: auto;

    .el-timeline {
      padding-left: 0;

      .alert-item {
        cursor: pointer;
        transition:
          transform var(--artdeco-transition-quick) var(--artdeco-ease-out),
          box-shadow var(--artdeco-transition-quick) var(--artdeco-ease-out),
          border-color var(--artdeco-transition-quick) var(--artdeco-ease-out),
          background var(--artdeco-transition-quick) var(--artdeco-ease-out);
        border-left: var(--artdeco-spacing-1) solid transparent;
        border-radius: var(--artdeco-radius-none);
        background: color-mix(in srgb, var(--artdeco-bg-elevated) 35%, var(--artdeco-bg-card));
        border-color: transparent;

        &.unread {
          background: color-mix(in srgb, var(--artdeco-info) 8%, var(--artdeco-bg-card));
          border-left-color: var(--artdeco-info);
        }

        &:hover {
          transform: translateX(var(--artdeco-spacing-1));
          box-shadow: var(--artdeco-glow-subtle);
        }

        &.severity-low {
          border-left-color: var(--artdeco-fg-muted);
        }

        &.severity-medium {
          border-left-color: var(--artdeco-warning);
        }

        &.severity-high {
          border-left-color: var(--artdeco-rise);
        }

        &.severity-critical {
          border-left-color: var(--artdeco-rise);
          background: color-mix(in srgb, var(--artdeco-rise) 10%, var(--artdeco-bg-card));
        }

        :deep(.el-card__body) {
          padding: var(--artdeco-spacing-3);
        }

        .alert-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: var(--artdeco-spacing-3);

          .alert-title {
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-2);
            font-family: var(--artdeco-font-heading, var(--font-display));
            font-weight: var(--artdeco-font-semibold);
            color: var(--artdeco-gold-primary);
            letter-spacing: var(--artdeco-tracking-wide);
            text-transform: uppercase;
          }

          .unread-dot {
            animation: pulse 2s ease-in-out infinite;
          }
        }

        .alert-body {
          .alert-message {
            margin: 0 0 var(--artdeco-spacing-3) 0;
            color: var(--artdeco-fg-muted);
            font-size: var(--artdeco-text-compact-base);
            line-height: 1.6;
          }

          .alert-details {
            :deep(.el-descriptions__label) {
              width: calc(var(--artdeco-spacing-16) + var(--artdeco-spacing-1) + (var(--artdeco-spacing-px) * 2));
              font-size: var(--artdeco-text-compact-sm);
            }

            :deep(.el-descriptions__content) {
              font-size: var(--artdeco-text-compact-sm);
            }

            .value-exceeded {
              color: var(--artdeco-rise);
              font-weight: var(--artdeco-font-semibold);
            }

            .value-normal {
              color: var(--artdeco-down);
              font-weight: var(--artdeco-font-semibold);
            }
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

@keyframes pulse {
  0%, 100% {
    opacity: 100%;
  }
  50% {
    opacity: 30%;
  }
}
</style>
