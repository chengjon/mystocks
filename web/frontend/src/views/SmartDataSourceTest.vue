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

<style scoped lang="scss">
@use "./styles/SmartDataSourceTest.css";
</style>
