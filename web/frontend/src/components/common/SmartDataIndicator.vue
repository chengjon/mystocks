<template>
  <div class="smart-data-indicator">
    <!-- 数据源模式指示器 -->
    <div class="mode-indicator" :class="modeClass">
      <div class="mode-icon">
        <svg v-if="currentMode === 'mock'" width="16" height="16" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
          <path d="M12 6v6l4 2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <svg v-else-if="currentMode === 'real'" width="16" height="16" viewBox="0 0 24 24" fill="none">
          <path d="M13 2L3 14h9l-1 8 10-12z" fill="currentColor"/>
          <path d="M13 2L3 14h9l-1 8 10-12z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
        </svg>
        <svg v-else-if="currentMode === 'hybrid'" width="16" height="16" viewBox="0 0 24 24" fill="none">
          <rect x="2" y="2" width="7" height="7" fill="currentColor" opacity="0.5"/>
          <rect x="15" y="15" width="7" height="7" fill="currentColor"/>
          <path d="M9 15l6-6" stroke="currentColor" stroke-width="2"/>
        </svg>
      </div>
      <span class="mode-text">{{ modeText }}</span>
    </div>

    <!-- 健康状态指示器 -->
    <div class="health-indicator" :class="healthClass">
      <div class="health-dot" :class="healthDotClass"></div>
      <span class="health-text">{{ healthText }}</span>
    </div>

    <!-- 详细信息弹出框 -->
    <div class="status-tooltip" v-if="showTooltip" @mouseenter="showTooltip = true" @mouseleave="showTooltip = false">
      <div class="tooltip-content">
        <div class="tooltip-header">
          <h4>数据源状态</h4>
          <button class="close-btn" @click="showTooltip = false">✕</button>
        </div>

        <div class="tooltip-body">
          <div class="info-row">
            <span class="label">当前模式:</span>
            <span class="value">{{ modeText }}</span>
          </div>
          <div class="info-row">
            <span class="label">健康状态:</span>
            <span class="value" :class="healthClass">{{ healthText }}</span>
          </div>
          <div class="info-row">
            <span class="label">降级启用:</span>
            <span class="value">{{ fallbackEnabled ? '是' : '否' }}</span>
          </div>
          <div class="info-row" v-if="lastHealthCheck">
            <span class="label">最后检查:</span>
            <span class="value">{{ formatTime(lastHealthCheck.timestamp) }}</span>
          </div>

          <!-- 数据源详情 -->
          <div class="sources-details" v-if="healthDetails && healthDetails.sources">
            <h5>数据源详情</h5>
            <div class="source-item" v-for="(source, name) in healthDetails.sources" :key="name" :class="getStatusClass(source.status)">
              <span class="source-name">{{ name }}</span>
              <span class="source-status">{{ source.status }}</span>
              <span class="source-response">{{ Math.round(source.response_time) }}ms</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { intelligentDataSourceAdapter } from '@/services/intelligentDataSourceAdapter.js'

export default {
  name: 'SmartDataIndicator',

  data() {
    return {
      currentMode: 'unknown',
      healthStatus: null,
      fallbackEnabled: false,
      lastHealthCheck: null,
      healthDetails: null,
      showTooltip: false
    }
  },

  computed: {
    modeClass() {
      return `mode-${this.currentMode}`
    },

    modeText() {
      const modeTexts = {
        'mock': '模拟数据',
        'real': '真实数据',
        'hybrid': '混合模式',
        'unknown': '检测中'
      }
      return modeTexts[this.currentMode] || '未知'
    },

    healthClass() {
      return `health-${this.healthStatus?.overall ? 'healthy' : 'unhealthy'}`
    },

    healthText() {
      if (!this.healthStatus) return '检测中'
      return this.healthStatus.overall ? '健康' : '异常'
    },

    healthDotClass() {
      return {
        'dot-healthy': this.healthStatus?.overall,
        'dot-unhealthy': !this.healthStatus?.overall,
        'dot-loading': !this.healthStatus
      }
    },

    healthDetails() {
      return this.healthStatus?.details || null
    }
  },

  async mounted() {
    // 初始化状态
    await this.updateStatus()

    // 监听模式变更
    intelligentDataSourceAdapter.onModeChange(this.handleModeChange)

    // 监听健康状态变更
    intelligentDataSourceAdapter.onHealthChange(this.handleHealthChange)

    // 定期更新状态
    this.startStatusUpdates()
  },

  beforeUnmount() {
    // 清理定时器
    if (this.statusTimer) {
      clearInterval(this.statusTimer)
    }
  },

  methods: {
    async updateStatus() {
      try {
        const status = intelligentDataSourceAdapter.getStatus()
        this.currentMode = status.mode
        this.healthStatus = status.health
        this.fallbackEnabled = status.fallbackEnabled
        this.lastHealthCheck = status.lastHealthCheck

      } catch (error) {
        console.error('❌ Failed to update status:', error)
      }
    },

    handleModeChange(mode) {
      this.currentMode = mode
      this.$emit('mode-change', mode)
    },

    handleHealthChange(isHealthy) {
      this.updateStatus()
      this.$emit('health-change', isHealthy)
    },

    startStatusUpdates() {
      // 每30秒更新一次状态
      this.statusTimer = setInterval(() => {
        this.updateStatus()
      }, 30000)
    },

    getStatusClass(status) {
      return `status-${status}`
    },

    formatTime(timestamp) {
      if (!timestamp) return '未知'

      const date = new Date(timestamp)
      const now = new Date()
      const diff = now - date

      if (diff < 60000) {
        return `${Math.floor(diff / 1000)}秒前`
      } else if (diff < 3600000) {
        return `${Math.floor(diff / 60000)}分钟前`
      } else {
        return date.toLocaleTimeString()
      }
    },

    toggleTooltip() {
      this.showTooltip = !this.showTooltip
    },

    // 手动刷新状态
    async refreshStatus() {
      await intelligentDataSourceAdapter.checkHealthStatus()
      this.updateStatus()
    },

    // 手动清除缓存
    clearCache() {
      intelligentDataSourceAdapter.clearCache()
    },

    // 强制模式切换（仅用于测试）
    async forceMode(mode) {
      await intelligentDataSourceAdapter.forceMode(mode)
    }
  }
}
</script>

<style scoped>
.smart-data-indicator {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-3);
  position: relative;
}

.mode-indicator,
.health-indicator {
  display: flex;
  align-items: center;
  gap: calc(var(--artdeco-spacing-1) + var(--artdeco-spacing-px) * 2);
  padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
  border-radius: var(--artdeco-radius-full);
  font-size: var(--artdeco-text-xs);
  font-weight: 500;
  cursor: pointer;
  transition:
    background-color var(--artdeco-transition-quick) var(--artdeco-ease-out),
    color var(--artdeco-transition-quick) var(--artdeco-ease-out),
    box-shadow var(--artdeco-transition-quick) var(--artdeco-ease-out);
}

.mode-indicator.mode-mock {
  background: color-mix(in srgb, var(--artdeco-fg-muted) 12%, transparent);
  color: var(--artdeco-fg-muted);
}

.mode-indicator.mode-real {
  background: var(--artdeco-quality-excellent);
  color: var(--artdeco-bg-global);
}

.mode-indicator.mode-hybrid {
  background: var(--artdeco-info);
  color: var(--artdeco-bg-global);
}

.mode-indicator.mode-unknown {
  background: var(--artdeco-warning);
  color: var(--artdeco-bg-global);
}

.health-indicator {
  background: color-mix(in srgb, var(--artdeco-fg-muted) 12%, transparent);
  color: var(--artdeco-fg-muted);
}

.health-indicator.health-healthy {
  background: var(--artdeco-quality-excellent);
  color: var(--artdeco-bg-global);
}

.health-indicator.health-unhealthy {
  background: var(--artdeco-quality-poor);
  color: var(--artdeco-bg-global);
}

.health-dot {
  width: var(--artdeco-spacing-2);
  height: var(--artdeco-spacing-2);
  border-radius: var(--artdeco-radius-full);
  animation: pulse 2s infinite;
}

.health-dot.dot-healthy {
  background: var(--artdeco-quality-excellent);
}

.health-dot.dot-unhealthy {
  background: var(--artdeco-quality-poor);
}

.health-dot.dot-loading {
  background: var(--artdeco-warning);
}

@keyframes pulse {
  0% { opacity: 100%; }
  50% { opacity: 50%; }
  100% { opacity: 100%; }
}

.status-tooltip {
  position: absolute;
  top: 100%;
  left: 0;
  z-index: calc(var(--artdeco-z-fixed) + 10);
  margin-top: var(--artdeco-spacing-2);
}

.tooltip-content {
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-md);
  box-shadow: var(--artdeco-shadow-xl);
  min-width: calc(var(--artdeco-spacing-32) * 2 + var(--artdeco-spacing-6));
  max-width: calc(var(--artdeco-spacing-32) * 3 + var(--artdeco-spacing-4));
}

.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
  border-bottom: 1px solid var(--artdeco-border-default);
}

.tooltip-header h4 {
  margin: 0;
  font-size: var(--artdeco-text-sm);
  font-weight: 600;
  color: var(--artdeco-fg-primary);
}

.close-btn {
  background: none;
  border: none;
  font-size: var(--artdeco-text-base);
  color: var(--artdeco-fg-muted);
  cursor: pointer;
  padding: 0;
  width: var(--artdeco-spacing-5);
  height: var(--artdeco-spacing-5);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--artdeco-radius-sm);
}

.close-btn:hover {
  background: color-mix(in srgb, var(--artdeco-fg-muted) 12%, transparent);
}

.tooltip-body {
  padding: var(--artdeco-spacing-4);
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-2);
}

.info-row:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: 500;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
}

.value {
  font-weight: 600;
  color: var(--artdeco-fg-primary);
  font-size: var(--artdeco-text-sm);
}

.sources-details {
  margin-top: var(--artdeco-spacing-4);
  padding-top: var(--artdeco-spacing-3);
  border-top: 1px solid var(--artdeco-border-default);
}

.sources-details h5 {
  margin: 0 0 var(--artdeco-spacing-2) 0;
  font-size: var(--artdeco-text-sm);
  font-weight: 600;
  color: var(--artdeco-fg-primary);
}

.source-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--artdeco-spacing-1) 0;
  font-size: var(--artdeco-text-xs);
}

.source-item.status-healthy {
  color: var(--artdeco-quality-excellent);
}

.source-item.status-degraded {
  color: var(--artdeco-quality-fair);
}

.source-item.status-failed {
  color: var(--artdeco-quality-poor);
}

.source-name {
  flex: 1;
  font-weight: 500;
}

.source-status {
  padding: calc(var(--artdeco-spacing-px) * 2) var(--artdeco-spacing-2);
  border-radius: var(--artdeco-radius-sm);
  background: color-mix(in srgb, var(--artdeco-quality-excellent) 10%, transparent);
  color: var(--artdeco-quality-excellent);
  font-size: calc(var(--artdeco-text-xs) - var(--artdeco-spacing-px) * 2);
}

.source-response {
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-xs);
  font-family: var(--font-mono);
}

/* 响应式 */
@media (width <= var(--artdeco-breakpoint-md)) {
  .smart-data-indicator {
    flex-direction: column;
    gap: var(--artdeco-spacing-2);
  }

  .tooltip-content {
    min-width: calc(var(--artdeco-spacing-32) * 2 - var(--artdeco-spacing-4));
    max-width: 90vw;
  }
}
</style>
