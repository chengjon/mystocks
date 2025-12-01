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

        console.debug('📊 Smart Data Indicator updated:', status)
      } catch (error) {
        console.error('❌ Failed to update status:', error)
      }
    },

    handleModeChange(mode) {
      console.log('🔄 Mode changed to:', mode)
      this.currentMode = mode
      this.$emit('mode-change', mode)
    },

    handleHealthChange(isHealthy) {
      console.log('💚 Health status changed:', isHealthy)
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
  gap: 12px;
  position: relative;
}

.mode-indicator,
.health-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mode-indicator.mode-mock {
  background: #f3f4f6;
  color: #6b7280;
}

.mode-indicator.mode-real {
  background: #10b981;
  color: white;
}

.mode-indicator.mode-hybrid {
  background: #3b82f6;
  color: white;
}

.mode-indicator.mode-unknown {
  background: #f59e0b;
  color: white;
}

.health-indicator {
  background: #f3f4f6;
  color: #6b7280;
}

.health-indicator.health-healthy {
  background: #10b981;
  color: white;
}

.health-indicator.health-unhealthy {
  background: #ef4444;
  color: white;
}

.health-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.health-dot.dot-healthy {
  background: #10b981;
}

.health-dot.dot-unhealthy {
  background: #ef4444;
}

.health-dot.dot-loading {
  background: #f59e0b;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.status-tooltip {
  position: absolute;
  top: 100%;
  left: 0;
  z-index: 1000;
  margin-top: 8px;
}

.tooltip-content {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  min-width: 280px;
  max-width: 400px;
}

.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
}

.tooltip-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  background: none;
  border: none;
  font-size: 16px;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.close-btn:hover {
  background: #f3f4f6;
}

.tooltip-body {
  padding: 16px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: 500;
  color: #6b7280;
  font-size: 13px;
}

.value {
  font-weight: 600;
  color: #111827;
  font-size: 13px;
}

.sources-details {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
}

.sources-details h5 {
  margin: 0 0 8px 0;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
}

.source-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  font-size: 12px;
}

.source-item.status-healthy {
  color: #10b981;
}

.source-item.status-degraded {
  color: #f59e0b;
}

.source-item.status-failed {
  color: #ef4444;
}

.source-name {
  flex: 1;
  font-weight: 500;
}

.source-status {
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  font-size: 10px;
}

.source-response {
  color: #6b7280;
  font-size: 11px;
  font-family: 'Monaco', 'Menlo', monospace;
}

/* 响应式 */
@media (max-width: 768px) {
  .smart-data-indicator {
    flex-direction: column;
    gap: 8px;
  }

  .tooltip-content {
    min-width: 240px;
    max-width: 90vw;
  }
}
</style>
