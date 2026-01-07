<template>
  <div class="smart-data-test">

    <div class="page-header">
      <h1 class="page-title">SMART DATA SOURCE TEST</h1>
      <p class="page-subtitle">DATA SOURCE TESTING | HEALTH CHECK | FALLBACK MODE</p>
      <SmartDataIndicator ref="indicator" />
    </div>

    <div class="test-content">
      <el-card class="control-panel">
        <template #header>
          <h3>CONTROL PANEL</h3>
        </template>

        <div class="control-buttons">
          <el-button type="primary" @click="refreshStatus">
            🔄 REFRESH STATUS
          </el-button>
          <el-button type="info" @click="clearCache">
            🗑️ CLEAR CACHE
          </el-button>
          <el-button type="warning" @click="forceMode('mock')">
            🎭️ FORCE MOCK
          </el-button>
          <el-button type="info" @click="testHealthCheck">
            ❤️ HEALTH CHECK
          </el-button>
        </div>
      </el-card>

      <el-card class="status-panel">
        <template #header>
          <h3>STATUS INFORMATION</h3>
        </template>
        <div class="status-grid">
          <div class="status-item">
            <label>SERVICE STATUS:</label>
            <span :class="serviceStatusClass">{{ serviceStatus }}</span>
          </div>
          <div class="status-item">
            <label>DATA SOURCE MODE:</label>
            <span class="mode-badge mode-{{ currentMode }}">{{ modeText }}</span>
          </div>
          <div class="status-item">
            <label>FALLBACK ENABLED:</label>
            <span>{{ fallbackEnabled ? 'YES' : 'NO' }}</span>
          </div>
          <div class="status-item">
            <label>LAST UPDATE:</label>
            <span>{{ formatTime(lastUpdate) }}</span>
          </div>
        </div>
      </el-card>

      <div class="test-panels">
        <el-card class="test-panel">
          <template #header>
            <h3>DASHBOARD TEST</h3>
          </template>
          <div class="test-controls">
            <el-input v-model="dashboardUserId" type="number" placeholder="USER ID" min="1" />
            <el-button type="primary" @click="testDashboard" :disabled="loading.dashboard">
              {{ loading.dashboard ? 'TESTING...' : 'TEST DASHBOARD' }}
            </el-button>
          </div>
          <div v-if="dashboardResult" class="test-result">
            <h4>TEST RESULT:</h4>
            <pre>{{ JSON.stringify(dashboardResult, null, 2) }}</pre>
          </div>
        </el-card>

        <el-card class="test-panel">
          <template #header>
            <h3>MARKET TEST</h3>
          </template>
          <div class="test-controls">
            <el-input v-model="marketSymbols" type="text" placeholder="STOCK CODES (COMMA SEPARATED)" />
            <el-button type="primary" @click="testMarketQuotes" :disabled="loading.market">
              {{ loading.market ? 'TESTING...' : 'TEST QUOTES' }}
            </el-button>
          </div>
          <div v-if="marketResult" class="test-result">
            <h4>TEST RESULT:</h4>
            <pre>{{ JSON.stringify(marketResult, null, 2) }}</pre>
          </div>
        </el-card>

        <el-card class="test-panel">
          <template #header>
            <h3>DATA QUALITY TEST</h3>
          </template>
          <div class="test-controls">
            <el-button type="primary" @click="testDataQualityHealth" :disabled="loading.quality">
              {{ loading.quality ? 'CHECKING...' : 'CHECK HEALTH' }}
            </el-button>
            <el-button type="info" @click="testDataQualityMetrics" :disabled="loading.metrics">
              {{ loading.metrics ? 'FETCHING...' : 'GET METRICS' }}
            </el-button>
          </div>
          <div v-if="qualityResult" class="test-result">
            <h4>TEST RESULT:</h4>
            <pre>{{ JSON.stringify(qualityResult, null, 2) }}</pre>
          </div>
        </el-card>

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

.smart-data-source-test {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-6);
  min-height: 100vh;
  position: relative;
  background: var(--bg-primary);
}

.background-pattern {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.04;
  background-image:
    repeating-linear-gradient(
      45deg,
      var(--accent-gold) 0px,
      var(--accent-gold) 1px,
      transparent 1px,
      transparent 10px
    ),
    repeating-linear-gradient(
      -45deg,
      var(--accent-gold) 0px,
      var(--accent-gold) 1px,
      transparent 1px,
      transparent 10px
    );
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-8);
  padding-bottom: var(--spacing-5);
  border-bottom: 1px solid rgba(212, 175, 55, 0.2);
  position: relative;
  z-index: 1;

  .page-title {
    font-family: var(--font-display);
    font-size: var(--font-size-h2);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-widest);
    color: var(--accent-gold);
    margin: 0;
  }

  .page-subtitle {
    font-family: var(--font-body);
    font-size: var(--font-size-small);
    color: var(--fg-muted);
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    margin: 0;
  }
}

.test-content {
  display: grid;
  gap: var(--spacing-6);
  position: relative;
  z-index: 1;
}

.control-panel,
.status-panel {
  background: var(--bg-card);
  border: 1px solid rgba(212, 175, 55, 0.3);
  border-radius: var(--radius-none);
  padding: var(--spacing-6);
}

.control-panel h3,
.status-panel h3 {
  margin: 0 0 var(--spacing-4) 0;
  font-family: var(--font-display);
  font-size: var(--font-size-h4);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  color: var(--accent-gold);
}

.control-buttons {
  display: flex;
  gap: var(--spacing-3);
  flex-wrap: wrap;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-3);

  .status-item {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-2);

    label {
      font-family: var(--font-display);
      font-size: var(--font-size-xs);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: var(--tracking-wider);
      color: var(--fg-muted);
    }

    span {
      font-family: var(--font-mono);
      font-size: var(--font-size-body);
      color: var(--fg-primary);
    }
  }
}

.test-panels {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: var(--spacing-6);
}

.test-panel {
  background: var(--bg-card);
  border: 1px solid rgba(212, 175, 55, 0.3);
  border-radius: var(--radius-none);
  padding: var(--spacing-6);

  h3 {
    font-family: var(--font-display);
    font-size: var(--font-size-h4);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    color: var(--accent-gold);
    margin: 0 0 var(--spacing-4) 0;
  }
}

.test-controls {
  display: flex;
  gap: var(--spacing-3);
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: var(--spacing-4);
}

.test-result {
  background: rgba(212, 175, 55, 0.05);
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: var(--radius-none);
  padding: var(--spacing-4);

  h4 {
    font-family: var(--font-display);
    font-size: var(--font-size-small);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    color: var(--accent-gold);
    margin: 0 0 var(--spacing-3) 0;
  }

  pre {
    font-family: var(--font-mono);
    font-size: var(--font-size-small);
    color: var(--fg-primary);
    margin: 0;
    white-space: pre-wrap;
    word-break: break-all;
  }
}

input {
  padding: var(--spacing-3) var(--spacing-4);
  font-family: var(--font-mono);
  font-size: var(--font-size-body);
  background: transparent;
  border: 1px solid rgba(212, 175, 55, 0.3);
  border-radius: var(--radius-none);
  color: var(--fg-primary);

  &:focus {
    outline: none;
    border-color: var(--accent-gold);
    box-shadow: var(--glow-subtle);
  }

  &::placeholder {
    color: var(--fg-muted);
  }
}

@media (max-width: 768px) {
  .smart-data-source-test {
    padding: var(--spacing-4);
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-4);
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
