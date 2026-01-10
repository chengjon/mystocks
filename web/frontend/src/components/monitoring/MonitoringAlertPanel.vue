<template>
  <div class="monitoring-alert-panel fintech-card" :class="panelClass">
    <div class="panel-header">
      <div class="panel-icon" :class="iconClass">
        <component :is="icon" />
      </div>
      <div class="panel-info">
        <h3 class="fintech-text-primary panel-title">{{ title }}</h3>
        <p class="fintech-text-secondary panel-subtitle">{{ subtitle }}</p>
      </div>
      <div class="panel-count" v-if="count !== undefined">
        <span class="count-badge" :class="badgeClass">{{ count }}</span>
      </div>
    </div>

    <div class="alerts-container">
      <div
        v-for="alert in alerts"
        :key="alert.id"
        class="alert-item"
        :class="getAlertClass(alert)"
        @click="$emit('alert-click', alert)"
      >
        <div class="alert-icon">
          <component :is="getAlertIcon(alert)" />
        </div>

        <div class="alert-content">
          <div class="alert-title fintech-text-primary">{{ alert.title || alert.symbol }}</div>
          <div class="alert-message fintech-text-primary">{{ alert.message }}</div>
          <div class="alert-meta">
            <span class="alert-time fintech-text-tertiary">{{ formatTime(alert.timestamp) }}</span>
            <span class="alert-priority" :class="getPriorityClass(alert.priority)" v-if="alert.priority">
              {{ alert.priority }}
            </span>
          </div>
        </div>

        <div class="alert-actions" v-if="$slots.actions || showDefaultActions">
          <slot name="actions" :alert="alert">
            <div class="default-actions">
              <button class="fintech-btn" @click.stop="$emit('alert-acknowledge', alert)">
                ACKNOWLEDGE
              </button>
              <button class="fintech-btn danger" @click.stop="$emit('alert-dismiss', alert)">
                DISMISS
              </button>
            </div>
          </slot>
        </div>
      </div>

      <div v-if="alerts.length === 0" class="empty-state">
        <div class="empty-icon">
          <component :is="emptyIcon" />
        </div>
        <div class="empty-content">
          <h4 class="fintech-text-secondary">{{ emptyTitle }}</h4>
          <p class="fintech-text-tertiary">{{ emptyMessage }}</p>
        </div>
      </div>
    </div>

    <div class="panel-footer" v-if="$slots.footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  ExclamationCircleOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined,
  BulbOutlined
} from '@ant-design/icons-vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  alerts: {
    type: Array,
    default: () => []
  },
  count: {
    type: Number,
    default: undefined
  },
  variant: {
    type: String,
    default: 'default', // 'default', 'critical', 'warning', 'info', 'success'
    validator: (value) => ['default', 'critical', 'warning', 'info', 'success'].includes(value)
  },
  maxHeight: {
    type: String,
    default: '400px'
  },
  showDefaultActions: {
    type: Boolean,
    default: true
  },
  emptyTitle: {
    type: String,
    default: 'ALL CLEAR'
  },
  emptyMessage: {
    type: String,
    default: 'No alerts at this time'
  }
})

const emit = defineEmits(['alert-click', 'alert-acknowledge', 'alert-dismiss'])

const panelClass = computed(() => {
  return [`variant-${props.variant}`]
})

const iconClass = computed(() => {
  return `icon-${props.variant}`
})

const badgeClass = computed(() => {
  return `badge-${props.variant}`
})

const icon = computed(() => {
  const icons = {
    critical: ExclamationCircleOutlined,
    warning: WarningOutlined,
    info: InfoCircleOutlined,
    success: CheckCircleOutlined,
    default: InfoCircleOutlined
  }
  return icons[props.variant] || InfoCircleOutlined
})

const emptyIcon = computed(() => {
  return CheckCircleOutlined
})

const getAlertClass = (alert) => {
  const baseClass = 'alert-item'
  const levelClass = `level-${alert.level || 'info'}`
  const priorityClass = alert.priority ? `priority-${alert.priority.toLowerCase()}` : ''
  return `${baseClass} ${levelClass} ${priorityClass}`
}

const getAlertIcon = (alert) => {
  const icons = {
    critical: ExclamationCircleOutlined,
    warning: WarningOutlined,
    info: InfoCircleOutlined,
    success: CheckCircleOutlined,
    tip: BulbOutlined
  }
  return icons[alert.level] || InfoCircleOutlined
}

const getPriorityClass = (priority) => {
  const classes = {
    high: 'priority-high',
    medium: 'priority-medium',
    low: 'priority-low'
  }
  return classes[priority?.toLowerCase()] || 'priority-medium'
}

const formatTime = (timestamp) => {
  if (!timestamp) return 'Unknown'

  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`

  return date.toLocaleDateString()
}
</script>

<style scoped>
.monitoring-alert-panel {
  display: flex;
  flex-direction: column;
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
  border-radius: var(--fintech-radius-base);
  font-size: 18px;
}

.icon-critical {
  background: var(--fintech-accent-danger);
  color: white;
}

.icon-warning {
  background: var(--fintech-accent-warning);
  color: white;
}

.icon-info {
  background: var(--fintech-accent-info);
  color: white;
}

.icon-success {
  background: var(--fintech-accent-success);
  color: white;
}

.icon-default {
  background: var(--fintech-accent-primary);
  color: white;
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

.badge-critical {
  background: var(--fintech-accent-danger);
  color: white;
}

.badge-warning {
  background: var(--fintech-accent-warning);
  color: var(--fintech-bg-primary);
}

.badge-info {
  background: var(--fintech-accent-info);
  color: white;
}

.badge-success {
  background: var(--fintech-accent-success);
  color: white;
}

.badge-default {
  background: var(--fintech-accent-primary);
  color: white;
}

/* 告警容器 */
.alerts-container {
  flex: 1;
  max-height: v-bind(maxHeight);
  overflow-y: auto;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: var(--fintech-space-4);
  padding: var(--fintech-space-4);
  border-bottom: 1px solid var(--fintech-border-dark);
  cursor: pointer;
  transition: all var(--fintech-transition-fast);
}

.alert-item:hover {
  background: var(--fintech-bg-tertiary);
}

.alert-item:last-child {
  border-bottom: none;
}

.alert-icon {
  font-size: 20px;
  margin-top: var(--fintech-space-1);
  flex-shrink: 0;
}

.level-critical .alert-icon {
  color: var(--fintech-accent-danger);
}

.level-warning .alert-icon {
  color: var(--fintech-accent-warning);
}

.level-info .alert-icon {
  color: var(--fintech-accent-info);
}

.level-success .alert-icon {
  color: var(--fintech-accent-success);
}

.level-tip .alert-icon {
  color: var(--fintech-accent-warning);
}

.alert-content {
  flex: 1;
  min-width: 0;
}

.alert-title {
  font-size: var(--fintech-font-size-base);
  font-weight: 600;
  margin-bottom: var(--fintech-space-1);
  word-break: break-word;
}

.alert-message {
  font-size: var(--fintech-font-size-sm);
  line-height: 1.5;
  margin-bottom: var(--fintech-space-2);
  word-break: break-word;
}

.alert-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--fintech-space-3);
}

.alert-time {
  font-size: var(--fintech-font-size-xs);
  font-family: var(--fintech-font-family-data);
}

.alert-priority {
  padding: 2px 8px;
  border-radius: var(--fintech-radius-sm);
  font-size: var(--fintech-font-size-xs);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.priority-high {
  background: var(--fintech-accent-danger);
  color: white;
}

.priority-medium {
  background: var(--fintech-accent-warning);
  color: var(--fintech-bg-primary);
}

.priority-low {
  background: var(--fintech-gray-6);
  color: var(--fintech-text-secondary);
}

.alert-actions {
  flex-shrink: 0;
}

.default-actions {
  display: flex;
  gap: var(--fintech-space-2);
}

.default-actions .fintech-btn {
  padding: var(--fintech-space-2) var(--fintech-space-3);
  font-size: var(--fintech-font-size-xs);
}

/* 空状态 */
.empty-state {
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

.empty-content h4 {
  margin: 0 0 var(--fintech-space-2) 0;
  font-size: var(--fintech-font-size-lg);
  font-weight: 500;
}

.empty-content p {
  margin: 0;
  font-size: var(--fintech-font-size-base);
}

/* 面板底部 */
.panel-footer {
  padding: var(--fintech-space-4) var(--fintech-space-5);
  border-top: 1px solid var(--fintech-border-base);
  background: var(--fintech-bg-tertiary);
}

/* 变体样式覆盖 */
.variant-critical .panel-header {
  border-left: 3px solid var(--fintech-accent-danger);
}

.variant-warning .panel-header {
  border-left: 3px solid var(--fintech-accent-warning);
}

.variant-info .panel-header {
  border-left: 3px solid var(--fintech-accent-info);
}

.variant-success .panel-header {
  border-left: 3px solid var(--fintech-accent-success);
}

/* 优先级动画 */
.alert-item.priority-high {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.8; }
  100% { opacity: 1; }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .alert-item {
    flex-direction: column;
    gap: var(--fintech-space-3);
  }

  .alert-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--fintech-space-2);
  }

  .default-actions {
    flex-direction: column;
    width: 100%;
  }

  .default-actions .fintech-btn {
    flex: 1;
    text-align: center;
  }
}

/* 高分辨率优化 */
@media (min-width: 1920px) {
  .panel-info h3 {
    font-size: var(--fintech-font-size-xl);
  }

  .alert-title {
    font-size: var(--fintech-font-size-lg);
  }
}
</style>