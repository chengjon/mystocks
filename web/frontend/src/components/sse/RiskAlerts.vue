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
          <el-icon :size="80" color="#67c23a"><CircleCheck /></el-icon>
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
          v-for="alert in alerts"
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
                <el-icon :size="18" :color="getSeverityColor(alert.severity)">
                  <component :is="getSeverityIcon(alert.severity)" />
                </el-icon>
                <span>{{ alert.alert_type || '风险告警' }}</span>
                <el-tag :type="getSeverityTagType(alert.severity)" size="small" effect="dark">
                  {{ getSeverityText(alert.severity) }}
                </el-tag>
              </div>
              <el-icon
                v-if="!alert.read"
                :size="10"
                color="#409eff"
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
import { computed } from 'vue'
import {
  Bell, Connection, Close, Select, Delete, CircleCheck,
  Refresh, CircleFilled, Warning, CircleClose, InfoFilled
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
  latestAlert,
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
    'low': '#909399',
    'medium': '#e6a23c',
    'high': '#f56c6c',
    'critical': '#c41e3a'
  }
  return colorMap[severity] || '#909399'
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
.risk-alerts-card {
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
      position: relative;

      .el-icon {
        font-size: 18px;
      }

      .alert-badge {
        margin-left: 4px;
      }
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 8px;

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

    .empty-desc {
      color: #67c23a;
      font-weight: 500;
      margin-top: 12px;
    }
  }

  .error-state {
    padding: 20px;
  }

  .alerts-content {
    max-height: 600px;
    overflow-y: auto;

    .el-timeline {
      padding-left: 0;

      .alert-item {
        cursor: pointer;
        transition: all 0.3s;
        border-left: 4px solid transparent;

        &.unread {
          background: #f0f9ff;
          border-left-color: #409eff;
        }

        &:hover {
          transform: translateX(4px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
        }

        &.severity-low {
          border-left-color: #909399;
        }

        &.severity-medium {
          border-left-color: #e6a23c;
        }

        &.severity-high {
          border-left-color: #f56c6c;
        }

        &.severity-critical {
          border-left-color: #c41e3a;
          background: #fef0f0;
        }

        :deep(.el-card__body) {
          padding: 12px;
        }

        .alert-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 12px;

          .alert-title {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
            color: #303133;
          }

          .unread-dot {
            animation: pulse 2s ease-in-out infinite;
          }
        }

        .alert-body {
          .alert-message {
            margin: 0 0 12px 0;
            color: #606266;
            font-size: 14px;
            line-height: 1.6;
          }

          .alert-details {
            :deep(.el-descriptions__label) {
              width: 70px;
              font-size: 12px;
            }

            :deep(.el-descriptions__content) {
              font-size: 12px;
            }

            .value-exceeded {
              color: #f56c6c;
              font-weight: 600;
            }

            .value-normal {
              color: #67c23a;
              font-weight: 600;
            }
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

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
}
</style>
