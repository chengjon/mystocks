<template>
  <div class="monitoring-stat-card fintech-card" :class="cardClass">
    <div class="stat-header" v-if="title || subtitle">
      <div class="stat-icon" v-if="icon">
        <component :is="icon" />
      </div>
      <div class="stat-info">
        <h3 class="fintech-text-primary stat-title" v-if="title">{{ title }}</h3>
        <p class="fintech-text-secondary stat-subtitle" v-if="subtitle">{{ subtitle }}</p>
      </div>
    </div>

    <div class="stat-content">
      <div class="stat-value-section">
        <div class="stat-value fintech-text-primary" :class="valueClass">
          {{ formattedValue }}
        </div>
        <div class="stat-unit fintech-text-secondary" v-if="unit">{{ unit }}</div>
      </div>

      <div class="stat-meta" v-if="change !== undefined || trend">
        <div class="stat-change" v-if="change !== undefined" :class="changeClass">
          <span class="change-icon">{{ change >= 0 ? '↗' : '↘' }}</span>
          <span class="change-value">{{ Math.abs(change) }}%</span>
        </div>
        <div class="stat-trend" v-if="trend">
          <span class="trend-text fintech-text-tertiary">{{ trend }}</span>
        </div>
      </div>
    </div>

    <div class="stat-visual" v-if="showProgress || showGauge">
      <div class="progress-container" v-if="showProgress">
        <div class="progress-track">
          <div class="progress-fill" :style="{ width: `${Math.min(100, Math.max(0, value))}%` }"></div>
        </div>
        <div class="progress-label fintech-text-tertiary">{{ Math.round(value) }}%</div>
      </div>

      <div class="gauge-container" v-if="showGauge">
        <div class="gauge-track">
          <div
            class="gauge-fill"
            :style="{ transform: `rotate(${Math.min(180, Math.max(0, (value / 100) * 180))}deg)` }"
          ></div>
          <div class="gauge-center"></div>
        </div>
        <div class="gauge-labels">
          <span class="gauge-min fintech-text-tertiary">0</span>
          <span class="gauge-max fintech-text-tertiary">100</span>
        </div>
      </div>
    </div>

    <div class="stat-actions" v-if="$slots.actions">
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  value: {
    type: [Number, String],
    required: true
  },
  unit: {
    type: String,
    default: ''
  },
  change: {
    type: Number,
    default: undefined
  },
  trend: {
    type: String,
    default: ''
  },
  icon: {
    type: Object,
    default: null
  },
  variant: {
    type: String,
    default: 'default', // 'default', 'success', 'warning', 'danger', 'info'
    validator: (value) => ['default', 'success', 'warning', 'danger', 'info'].includes(value)
  },
  size: {
    type: String,
    default: 'medium', // 'small', 'medium', 'large'
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  showProgress: {
    type: Boolean,
    default: false
  },
  showGauge: {
    type: Boolean,
    default: false
  }
})

const cardClass = computed(() => {
  return [`variant-${props.variant}`, `size-${props.size}`]
})

const valueClass = computed(() => {
  if (typeof props.value === 'number') {
    if (props.value >= 80) return 'fintech-text-up'
    if (props.value >= 60) return 'fintech-text-flat'
    return 'fintech-text-down'
  }
  return ''
})

const changeClass = computed(() => {
  if (props.change === undefined) return ''
  return props.change >= 0 ? 'positive' : 'negative'
})

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    // 格式化数字显示
    if (props.value >= 1000000) {
      return (props.value / 1000000).toFixed(1) + 'M'
    } else if (props.value >= 1000) {
      return (props.value / 1000).toFixed(1) + 'K'
    } else if (Number.isInteger(props.value)) {
      return props.value.toString()
    } else {
      return props.value.toFixed(2)
    }
  }
  return props.value
})
</script>

<style scoped>
.monitoring-stat-card {
  position: relative;
  transition: all var(--fintech-transition-base);
  overflow: hidden;
}

.monitoring-stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--fintech-shadow-md);
}

/* 卡片头部 */
.stat-header {
  display: flex;
  align-items: center;
  gap: var(--fintech-space-3);
  margin-bottom: var(--fintech-space-4);
}

.stat-icon {
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

.stat-info h3 {
  margin: 0 0 var(--fintech-space-1) 0;
  font-size: var(--fintech-font-size-base);
  font-weight: 600;
}

.stat-info p {
  margin: 0;
  font-size: var(--fintech-font-size-sm);
}

/* 统计内容 */
.stat-content {
  margin-bottom: var(--fintech-space-4);
}

.stat-value-section {
  display: flex;
  align-items: baseline;
  gap: var(--fintech-space-2);
  margin-bottom: var(--fintech-space-2);
}

.stat-value {
  font-size: var(--fintech-font-size-3xl);
  font-weight: 700;
  font-family: var(--fintech-font-family-data);
  letter-spacing: 0.01em;
}

.stat-unit {
  font-size: var(--fintech-font-size-base);
  opacity: 0.8;
}

.stat-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-change {
  display: flex;
  align-items: center;
  gap: var(--fintech-space-1);
  font-size: var(--fintech-font-size-sm);
  font-weight: 500;
  padding: var(--fintech-space-1) var(--fintech-space-2);
  border-radius: var(--fintech-radius-sm);
}

.stat-change.positive {
  background: var(--fintech-accent-success);
  color: white;
}

.stat-change.negative {
  background: var(--fintech-accent-danger);
  color: white;
}

.stat-trend {
  font-size: var(--fintech-font-size-xs);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

/* 视觉元素 */
.stat-visual {
  margin-top: var(--fintech-space-4);
}

.progress-container {
  display: flex;
  align-items: center;
  gap: var(--fintech-space-3);
}

.progress-track {
  flex: 1;
  height: 8px;
  background: var(--fintech-bg-tertiary);
  border-radius: var(--fintech-radius-sm);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--fintech-accent-success) 0%, var(--fintech-accent-warning) 50%, var(--fintech-accent-danger) 100%);
  border-radius: var(--fintech-radius-sm);
  transition: width var(--fintech-transition-slow);
}

.progress-label {
  font-size: var(--fintech-font-size-sm);
  font-family: var(--fintech-font-family-data);
  min-width: 40px;
  text-align: right;
}

.gauge-container {
  position: relative;
  width: 80px;
  height: 40px;
  margin: 0 auto;
}

.gauge-track {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 40px 40px 0 0;
  background: var(--fintech-bg-tertiary);
  overflow: hidden;
}

.gauge-fill {
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, var(--fintech-accent-success) 0%, var(--fintech-accent-warning) 50%, var(--fintech-accent-danger) 100%);
  transform-origin: bottom left;
  transition: transform var(--fintech-transition-slow);
}

.gauge-center {
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 4px;
  height: 4px;
  background: var(--fintech-text-primary);
  border-radius: 50%;
  transform: translateX(-50%);
}

.gauge-labels {
  display: flex;
  justify-content: space-between;
  margin-top: var(--fintech-space-2);
  font-size: var(--fintech-font-size-xs);
  font-family: var(--fintech-font-family-data);
}

/* 卡片动作 */
.stat-actions {
  margin-top: var(--fintech-space-4);
  padding-top: var(--fintech-space-4);
  border-top: 1px solid var(--fintech-border-dark);
}

/* 变体样式 */
.variant-success .stat-icon {
  color: var(--fintech-accent-success);
}

.variant-warning .stat-icon {
  color: var(--fintech-accent-warning);
}

.variant-danger .stat-icon {
  color: var(--fintech-accent-danger);
}

.variant-info .stat-icon {
  color: var(--fintech-accent-info);
}

/* 尺寸变体 */
.size-small .stat-value {
  font-size: var(--fintech-font-size-2xl);
}

.size-small .stat-icon {
  width: 32px;
  height: 32px;
  font-size: 16px;
}

.size-large .stat-value {
  font-size: 48px;
}

.size-large .stat-icon {
  width: 48px;
  height: 48px;
  font-size: 20px;
}

/* 响应式 */
@media (max-width: 768px) {
  .stat-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--fintech-space-2);
  }

  .stat-value {
    font-size: var(--fintech-font-size-2xl);
  }

  .stat-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--fintech-space-2);
  }
}
</style>