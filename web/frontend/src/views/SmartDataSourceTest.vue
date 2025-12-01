<template>
  <div class="smart-data-test">
    <div class="test-header">
      <h1>🧠 智能数据源测试页面</h1>
      <SmartDataIndicator ref="indicator" />
    </div>

    <div class="test-content">
      <!-- 控制面板 -->
      <div class="control-panel">
        <h3>🎛️ 控制面板</h3>

        <div class="control-buttons">
          <button @click="refreshStatus" class="btn btn-primary">
            🔄 刷新状态
          </button>
          <button @click="clearCache" class="btn btn-secondary">
            🗑️ 清理缓存
          </button>
          <button @click="forceMode('mock')" class="btn btn-warning">
            🎭️ 强制Mock
          </button>
          <button @click="testHealthCheck" class="btn btn-info">
            ❤️ 健康检查
          </button>
        </div>
      </div>

      <!-- 状态信息 -->
      <div class="status-panel">
        <h3>📊 状态信息</h3>
        <div class="status-grid">
          <div class="status-item">
            <label>服务状态:</label>
            <span :class="serviceStatusClass">{{ serviceStatus }}</span>
          </div>
          <div class="status-item">
            <label>数据源模式:</label>
            <span class="mode-badge mode-{{ currentMode }}">{{ modeText }}</span>
          </div>
          <div class="status-item">
            <label>降级启用:</label>
            <span>{{ fallbackEnabled ? '是' : '否' }}</span>
          </div>
          <div class="status-item">
            <label>最后更新:</label>
            <span>{{ formatTime(lastUpdate) }}</span>
          </div>
        </div>
      </div>

      <!-- 测试面板 -->
      <div class="test-panels">
        <!-- Dashboard测试 -->
        <div class="test-panel">
          <h3>📊 Dashboard 测试</h3>
          <div class="test-controls">
            <input v-model="dashboardUserId" type="number" placeholder="用户ID" min="1" />
            <button @click="testDashboard" class="btn btn-primary" :disabled="loading.dashboard">
              {{ loading.dashboard ? '测试中...' : '测试Dashboard' }}
            </button>
          </div>
          <div v-if="dashboardResult" class="test-result">
            <h4>测试结果:</h4>
            <pre>{{ JSON.stringify(dashboardResult, null, 2) }}</pre>
          </div>
        </div>

        <!-- Market测试 -->
        <div class="test-panel">
          <h3>📈 Market 测试</h3>
          <div class="test-controls">
            <input v-model="marketSymbols" type="text" placeholder="股票代码，逗号分隔" />
            <button @click="testMarketQuotes" class="btn btn-primary" :disabled="loading.market">
              {{ loading.market ? '测试中...' : '测试行情' }}
            </button>
          </div>
          <div v-if="marketResult" class="test-result">
            <h4>测试结果:</h4>
            <pre>{{ JSON.stringify(marketResult, null, 2) }}</pre>
          </div>
        </div>

        <!-- Data Quality测试 -->
        <div class="test-panel">
          <h3>🔍 Data Quality 测试</h3>
          <div class="test-controls">
            <button @click="testDataQualityHealth" class="btn btn-primary" :disabled="loading.quality">
              {{ loading.quality ? '检查中...' : '检查健康状态' }}
            </button>
            <button @click="testDataQualityMetrics" class="btn btn-secondary" :disabled="loading.metrics">
              {{ loading.metrics ? '获取中...' : '获取指标' }}
            </button>
          </div>
          <div v-if="qualityResult" class="test-result">
            <h4>测试结果:</h4>
            <pre>{{ JSON.stringify(qualityResult, null, 2) }}</pre>
          </div>
        </div>

        <!-- 批量测试 -->
        <div class="test-panel">
          <h3>🚀 批量测试</h3>
          <div class="test-controls">
            <button @click="testBatchRequests" class="btn btn-primary" :disabled="loading.batch">
              {{ loading.batch ? '批量测试中...' : '批量请求测试' }}
            </button>
            <span class="batch-info">同时测试多个API端点</span>
          </div>
          <div v-if="batchResults.length > 0" class="test-result">
            <h4>批量结果:</h4>
            <div class="batch-summary">
              <span>成功: {{ batchSuccess }}</span>
              <span>失败: {{ batchFailed }}</span>
              <span>总计: {{ batchTotal }}</span>
            </div>
            <div class="batch-details">
              <div v-for="(result, index) in batchResults" :key="index" class="batch-item">
                <span class="batch-index">#{{ index + 1 }}</span>
                <span class="batch-request">{{ result.request.endpoint }}</span>
                <span class="batch-status" :class="result.result ? 'success' : 'failed'">
                  {{ result.result ? '✅' : '❌' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SmartDataIndicator from '@/components/common/SmartDataIndicator.vue'
import { smartDataService } from '@/services/smartDataService.js'

export default {
  name: 'SmartDataSourceTest',

  components: {
    SmartDataIndicator
  },

  data() {
    return {
      // 测试参数
      dashboardUserId: 1,
      marketSymbols: '000001,600519',

      // 加载状态
      loading: {
        dashboard: false,
        market: false,
        quality: false,
        metrics: false,
        batch: false
      },

      // 测试结果
      dashboardResult: null,
      marketResult: null,
      qualityResult: null,
      batchResults: [],

      // 服务状态
      currentMode: 'unknown',
      fallbackEnabled: false,
      serviceStatus: 'initializing',
      lastUpdate: null
    }
  },

  computed: {
    modeText() {
      const modeTexts = {
        'mock': '模拟数据',
        'real': '真实数据',
        'hybrid': '混合模式',
        'unknown': '未知'
      }
      return modeTexts[this.currentMode] || '未知'
    },

    serviceStatusClass() {
      return `status-${this.serviceStatus}`
    },

    batchSuccess() {
      return this.batchResults.filter(r => r.result).length
    },

    batchFailed() {
      return this.batchResults.filter(r => !r.result).length
    },

    batchTotal() {
      return this.batchResults.length
    }
  },

  async mounted() {
    // 监听服务事件
    this.setupEventListeners()

    // 初始化状态
    await this.updateServiceStatus()

    // 开始定期更新
    this.startStatusUpdates()
  },

  methods: {
    setupEventListeners() {
      smartDataService.on('mode-change', (mode) => {
        this.currentMode = mode
        this.lastUpdate = new Date()
      })

      smartDataService.on('health-change', (isHealthy) => {
        this.serviceStatus = isHealthy ? 'healthy' : 'unhealthy'
        this.lastUpdate = new Date()
      })
    },

    async updateServiceStatus() {
      try {
        await smartDataService.initialize()
        const status = smartDataService.getStatus()
        const health = await smartDataService.healthCheck()

        this.currentMode = status.adapterStatus.mode
        this.fallbackEnabled = status.adapterStatus.fallbackEnabled
        this.serviceStatus = health.service
        this.lastUpdate = new Date()

        console.log('✅ Service status updated:', {
          mode: this.currentMode,
          health: this.serviceStatus
        })
      } catch (error) {
        console.error('❌ Failed to update service status:', error)
        this.serviceStatus = 'error'
        this.lastUpdate = new Date()
      }
    },

    startStatusUpdates() {
      // 每30秒更新一次状态
      this.statusTimer = setInterval(() => {
        this.updateServiceStatus()
      }, 30000)
    },

    // 控制方法
    async refreshStatus() {
      await this.updateServiceStatus()
      this.$refs.indicator?.refreshStatus()
    },

    clearCache() {
      smartDataService.clearCache()
      this.$message.success('缓存已清理')
    },

    async forceMode(mode) {
      try {
        await this.$refs.indicator?.forceMode(mode)
        await this.updateServiceStatus()
        this.$message.success(`已强制切换到${mode}模式`)
      } catch (error) {
        console.error('Force mode failed:', error)
        this.$message.error('强制模式切换失败')
      }
    },

    // 测试方法
    async testDashboard() {
      this.loading.dashboard = true
      try {
        this.dashboardResult = await smartDataService.getDashboardSummary(
          this.dashboardUserId,
          {
            include_market: true,
            include_watchlist: true,
            include_portfolio: true
          }
        )
        this.$message.success('Dashboard测试成功')
      } catch (error) {
        console.error('Dashboard test failed:', error)
        this.$message.error(`Dashboard测试失败: ${error.message}`)
        this.dashboardResult = { error: error.message }
      } finally {
        this.loading.dashboard = false
      }
    },

    async testMarketQuotes() {
      this.loading.market = true
      try {
        this.marketResult = await smartDataService.getMarketQuotes(this.marketSymbols)
        this.$message.success('市场行情测试成功')
      } catch (error) {
        console.error('Market quotes test failed:', error)
        this.$message.error(`行情测试失败: ${error.message}`)
        this.marketResult = { error: error.message }
      } finally {
        this.loading.market = false
      }
    },

    async testDataQualityHealth() {
      this.loading.quality = true
      try {
        this.qualityResult = await smartDataService.getDataQualityHealth()
        this.$message.success('数据质量健康检查完成')
      } catch (error) {
        console.error('Data quality health check failed:', error)
        this.$message.error(`健康检查失败: ${error.message}`)
        this.qualityResult = { error: error.message }
      } finally {
        this.loading.quality = false
      }
    },

    async testDataQualityMetrics() {
      this.loading.metrics = true
      try {
        this.qualityResult = await smartDataService.getDataQualityMetrics()
        this.$message.success('数据质量指标获取成功')
      } catch (error) {
        console.error('Data quality metrics failed:', error)
        this.$message.error(`指标获取失败: ${error.message}`)
        this.qualityResult = { error: error.message }
      } finally {
        this.loading.metrics = false
      }
    },

    async testBatchRequests() {
      this.loading.batch = true
      this.batchResults = []

      try {
        const requests = [
          { endpoint: '/api/dashboard/health' },
          { endpoint: '/api/data-quality/config/mode' },
          { endpoint: '/api/market/quotes?symbols=000001' },
          { endpoint: '/api/data-quality/health' }
        ]

        const results = await smartDataService.batchFetch(requests, { concurrent: 2 })
        this.batchResults = results

        this.$message.success(`批量测试完成: ${results.length}个请求`)
      } catch (error) {
        console.error('Batch test failed:', error)
        this.$message.error(`批量测试失败: ${error.message}`)
      } finally {
        this.loading.batch = false
      }
    },

    async testHealthCheck() {
      try {
        const health = await smartDataService.healthCheck()
        this.$message.success(`健康检查完成: ${health.service} - ${health.healthy}/${health.sources} sources healthy`)

        if (health.service === 'healthy') {
          this.$message.success('系统整体健康状态良好')
        } else {
          this.$message.warning('系统存在异常，需要关注')
        }
      } catch (error) {
        console.error('Health check failed:', error)
        this.$message.error('健康检查失败')
      }
    },

    // 工具方法
    formatTime(timestamp) {
      if (!timestamp) return '未知'
      return new Date(timestamp).toLocaleTimeString()
    }
  },

  beforeDestroy() {
    if (this.statusTimer) {
      clearInterval(this.statusTimer)
    }
  }
}
</script>

<style scoped>
.smart-data-test {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.test-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.test-header h1 {
  margin: 0;
  font-size: 24px;
  color: #111827;
}

.test-content {
  display: grid;
  gap: 30px;
}

.control-panel,
.status-panel {
  background: #f9fafb;
  border-radius: 8px;
  padding: 20px;
}

.control-panel h3,
.status-panel h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #374151;
}

.control-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
}

.btn-warning {
  background: #f59e0b;
  color: white;
}

.btn-warning:hover {
  background: #d97706;
}

.btn-info {
  background: #8b5cf6;
  color: white;
}

.btn-info:hover {
  background: #6d28d9;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.status-item label {
  font-weight: 500;
  color: #6b7280;
}

.mode-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.mode-badge.mode-mock {
  background: #f59e0b;
  color: white;
}

.mode-badge.mode-real {
  background: #10b981;
  color: white;
}

.mode-badge.mode-hybrid {
  background: #3b82f6;
  color: white;
}

.mode-badge.mode-unknown {
  background: #6b7280;
  color: white;
}

.status-healthy {
  color: #10b981;
  font-weight: 600;
}

.status-unhealthy {
  color: #ef4444;
  font-weight: 600;
}

.status-initializing {
  color: #f59e0b;
  font-weight: 600;
}

.status-error {
  color: #ef4444;
  font-weight: 600;
}

.test-panels {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 20px;
}

.test-panel {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
}

.test-panel h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #374151;
}

.test-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.test-controls input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
}

.test-result {
  background: #f9fafb;
  border-radius: 6px;
  padding: 16px;
  max-height: 300px;
  overflow-y: auto;
}

.test-result h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #374151;
}

.test-result pre {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  padding: 12px;
  font-size: 12px;
  overflow-x: auto;
  max-height: 250px;
  overflow-y: auto;
  margin: 0;
}

.batch-summary {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  font-size: 14px;
}

.batch-summary span {
  padding: 2px 8px;
  border-radius: 4px;
}

.batch-summary span:first-child {
  background: #10b981;
  color: white;
}

.batch-summary span:nth-child(2) {
  background: #ef4444;
  color: white;
}

.batch-summary span:last-child {
  background: #3b82f6;
  color: white;
}

.batch-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.batch-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  background: white;
  border-radius: 4px;
  font-size: 12px;
}

.batch-index {
  font-weight: 600;
  color: #6b7280;
  min-width: 30px;
}

.batch-request {
  flex: 1;
  font-family: monospace;
  color: #374151;
}

.batch-status.success {
  color: #10b981;
}

.batch-status.failed {
  color: #ef4444;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .smart-data-test {
    padding: 10px;
  }

  .test-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .test-content {
    grid-template-columns: 1fr;
  }

  .control-buttons {
    justify-content: flex-start;
  }

  .status-grid {
    grid-template-columns: 1fr;
  }

  .test-panels {
    grid-template-columns: 1fr;
  }
}
</style>
