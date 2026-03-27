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
        v-for="(alert, _idx) in alerts"
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

const _emit = defineEmits(['alert-click', 'alert-acknowledge', 'alert-dismiss'])

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

<style scoped lang="scss">
@use "./styles/MonitoringAlertPanel.css";
</style>
