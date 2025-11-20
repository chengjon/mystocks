<!-- 监控页面组件 -->
<template>
  <div class="monitor-page">
    <div class="page-header">
      <h1>系统监控</h1>
      <div class="actions">
        <div v-if="isLoading" class="loading-indicator">
          <span class="icon">⏳</span> 加载中...
        </div>
        <button @click="refreshData" class="btn-refresh" :disabled="isLoading">
          <span class="icon">⟳</span> 刷新
        </button>
        <button @click="toggleAutoRefresh" class="btn-toggle" :class="{ 'active': autoRefresh }">
          <span class="icon">{{ autoRefresh ? '⏸' : '▶' }}</span>
          {{ autoRefresh ? '暂停自动刷新' : '启动自动刷新' }}
        </button>
      </div>
    </div>
    
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <!-- 监控摘要 -->
    <div class="monitor-summary">
      <div class="summary-card" :class="{ 'status-normal': isSystemHealthy, 'status-warning': !isSystemHealthy }">
        <div class="summary-icon">{{ isSystemHealthy ? '✓' : '⚠' }}</div>
        <div class="summary-content">
          <div class="summary-title">{{ isSystemHealthy ? '系统运行正常' : '系统存在警告' }}</div>
          <div class="summary-description">{{ systemStatusMessage }}</div>
        </div>
      </div>
      
      <div class="summary-details">
        <div class="detail-card">
          <div class="detail-label">前端服务</div>
          <div class="detail-value" :class="{ 'status-normal': services.frontend === 'normal', 'status-warning': services.frontend === 'warning' }">
            {{ getServiceStatusText(services.frontend) }}
          </div>
        </div>
        <div class="detail-card">
          <div class="detail-label">API服务</div>
          <div class="detail-value" :class="{ 'status-normal': services.api === 'normal', 'status-warning': services.api === 'warning' }">
            {{ getServiceStatusText(services.api) }}
          </div>
        </div>
        <div class="detail-card">
          <div class="detail-label">PostgreSQL</div>
          <div class="detail-value" :class="{ 'status-normal': services.postgresql === 'normal', 'status-warning': services.postgresql === 'warning' }">
            {{ getServiceStatusText(services.postgresql) }}
          </div>
        </div>
        <div class="detail-card">
          <div class="detail-label">TDengine</div>
          <div class="detail-value" :class="{ 'status-normal': services.tdengine === 'normal', 'status-warning': services.tdengine === 'warning' }">
            {{ getServiceStatusText(services.tdengine) }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- 服务详情 -->
    <div class="services-section">
      <h2>服务详情</h2>
      <div class="services-grid">
        <div class="service-card">
          <div class="service-header">
            <h3>前端服务</h3>
            <div class="service-status" :class="{ 'status-normal': services.frontend === 'normal', 'status-warning': services.frontend === 'warning' }">
              {{ getServiceStatusText(services.frontend) }}
            </div>
          </div>
          <div class="service-content">
            <div class="service-info">
              <div class="info-item">
                <span class="info-label">状态:</span>
                <span class="info-value">{{ services.frontend === 'normal' ? '正常' : '异常' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">URL:</span>
                <span class="info-value">{{ FRONTEND_URL }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">响应时间:</span>
                <span class="info-value">{{ servicesData.frontend?.responseTime || '未知' }} ms</span>
              </div>
            </div>
            <div class="service-actions">
              <button @click="checkService('frontend')" class="btn-action">检查</button>
              <a :href="FRONTEND_URL" target="_blank" class="btn-action">访问</a>
            </div>
          </div>
        </div>
        
        <div class="service-card">
          <div class="service-header">
            <h3>API服务</h3>
            <div class="service-status" :class="{ 'status-normal': services.api === 'normal', 'status-warning': services.api === 'warning' }">
              {{ getServiceStatusText(services.api) }}
            </div>
          </div>
          <div class="service-content">
            <div class="service-info">
              <div class="info-item">
                <span class="info-label">状态:</span>
                <span class="info-value">{{ services.api === 'normal' ? '正常' : '异常' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">URL:</span>
                <span class="info-value">{{ API_BASE_URL }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">健康检查端点:</span>
                <span class="info-value">/api/health</span>
              </div>
            </div>
            <div class="service-actions">
              <button @click="checkService('api')" class="btn-action">检查</button>
              <a :href="`${API_BASE_URL}/api/docs`" target="_blank" class="btn-action">API文档</a>
            </div>
          </div>
        </div>
        
        <div class="service-card">
          <div class="service-header">
            <h3>PostgreSQL</h3>
            <div class="service-status" :class="{ 'status-normal': services.postgresql === 'normal', 'status-warning': services.postgresql === 'warning' }">
              {{ getServiceStatusText(services.postgresql) }}
            </div>
          </div>
          <div class="service-content">
            <div class="service-info">
              <div class="info-item">
                <span class="info-label">状态:</span>
                <span class="info-value">{{ servicesData.postgresql?.status || '未知' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">主机:</span>
                <span class="info-value">localhost:5438</span>
              </div>
              <div class="info-item">
                <span class="info-label">数据库:</span>
                <span class="info-value">mystocks</span>
              </div>
            </div>
            <div class="service-actions">
              <button @click="checkService('postgresql')" class="btn-action">检查</button>
            </div>
          </div>
        </div>
        
        <div class="service-card">
          <div class="service-header">
            <h3>TDengine</h3>
            <div class="service-status" :class="{ 'status-normal': services.tdengine === 'normal', 'status-warning': services.tdengine === 'warning' }">
              {{ getServiceStatusText(services.tdengine) }}
            </div>
          </div>
          <div class="service-content">
            <div class="service-info">
              <div class="info-item">
                <span class="info-label">状态:</span>
                <span class="info-value">{{ servicesData.tdengine?.status || '未知' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">主机:</span>
                <span class="info-value">localhost:6030</span>
              </div>
              <div class="info-item">
                <span class="info-label">数据库:</span>
                <span class="info-value">mystocks</span>
              </div>
            </div>
            <div class="service-actions">
              <button @click="checkService('tdengine')" class="btn-action">检查</button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 历史记录 -->
    <div class="history-section">
      <h2>监控历史</h2>
      <div class="history-table">
        <table>
          <thead>
            <tr>
              <th>时间</th>
              <th>前端</th>
              <th>API</th>
              <th>PostgreSQL</th>
              <th>TDengine</th>
              <th>整体状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(record, index) in historyData" :key="index" :class="record.overallStatus === 'normal' ? 'status-normal' : 'status-warning'">
              <td>{{ formatDateTime(record.timestamp) }}</td>
              <td>{{ getStatusText(record.frontend) }}</td>
              <td>{{ getStatusText(record.api) }}</td>
              <td>{{ getStatusText(record.postgresql) }}</td>
              <td>{{ getStatusText(record.tdengine) }}</td>
              <td>{{ record.overallStatus === 'normal' ? '正常' : '异常' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useApiService } from '@/composables/useApiService'

export default {
  name: 'SystemMonitor',
  setup() {
    const { getHealthData, getDetailedHealthData } = useApiService()
    
    // 监控状态
    const autoRefresh = ref(false)
    const refreshInterval = ref(60000) // 60秒
    const isLoading = ref(false)
    const error = ref(null)
    
    // 服务状态
    const services = ref({
      frontend: 'normal',
      api: 'normal',
      postgresql: 'normal',
      tdengine: 'warning' // TDengine默认警告状态，因为已知存在问题
    })
    
    // 服务数据
    const servicesData = ref({
      frontend: null,
      api: null,
      postgresql: null,
      tdengine: null
    })
    
    // 历史数据
    const historyData = ref([])
    
    // 常量
    const FRONTEND_URL = 'http://localhost:3000'
    const API_BASE_URL = 'http://localhost:8000'
    
    // 计算属性
    const isSystemHealthy = computed(() => {
      return Object.values(services.value).every(status => status === 'normal')
    })
    
    const systemStatusMessage = computed(() => {
      if (isSystemHealthy.value) {
        return '所有服务运行正常，没有检测到问题'
      } else {
        const issues = Object.entries(services.value)
          .filter(([key, value]) => value !== 'normal')
          .map(([key]) => {
            switch(key) {
              case 'frontend': return '前端服务'
              case 'api': return 'API服务'
              case 'postgresql': return 'PostgreSQL'
              case 'tdengine': return 'TDengine'
              default: return key
            }
          })
          .join('、')
        
        return `检测到问题: ${issues}`
      }
    })
    
    // 方法
    const formatDateTime = (timestamp) => {
      const date = new Date(timestamp)
      return date.toLocaleString()
    }
    
    const getStatusText = (status) => {
      return status === 'normal' ? '✓' : '⚠'
    }
    
    const getServiceStatusText = (status) => {
      return status === 'normal' ? '正常' : '警告'
    }
    
    const checkService = async (serviceName) => {
      try {
        isLoading.value = true
        error.value = null
        
        // 调用健康检查API
        const healthData = await getHealthData()
        
        if (serviceName === 'frontend') {
          services.value.frontend = healthData.frontend === 200 ? 'normal' : 'warning'
          servicesData.value.frontend = {
            responseTime: healthData.frontendResponseTime
          }
        } else if (serviceName === 'api') {
          services.value.api = healthData.api === 200 ? 'normal' : 'warning'
          servicesData.value.api = {
            status: healthData.api === 200 ? '正常' : '异常'
          }
        } else if (serviceName === 'postgresql') {
          services.value.postgresql = healthData.postgresql === '正常' ? 'normal' : 'warning'
          servicesData.value.postgresql = {
            status: healthData.postgresql
          }
        } else if (serviceName === 'tdengine') {
          services.value.tdengine = healthData.tdengine === '可访问' ? 'normal' : 'warning'
          servicesData.value.tdengine = {
            status: healthData.tdengine
          }
        }
        
        // 添加到历史记录
        addToHistory(healthData)
      } catch (error) {
        console.error(`检查服务 ${serviceName} 失败:`, error)
        error.value = `检查服务 ${serviceName} 失败: ${error.message}`
      } finally {
        isLoading.value = false
      }
    }
    
    const refreshData = async () => {
      try {
        isLoading.value = true
        error.value = null
        
        // 调用健康检查API
        const healthData = await getHealthData()
        
        // 更新服务状态
        services.value.frontend = healthData.frontend === 200 ? 'normal' : 'warning'
        services.value.api = healthData.api === 200 ? 'normal' : 'warning'
        services.value.postgresql = healthData.postgresql === '正常' ? 'normal' : 'warning'
        services.value.tdengine = healthData.tdengine === '可访问' ? 'normal' : 'warning'
        
        // 更新服务数据
        servicesData.value.frontend = {
          responseTime: healthData.frontendResponseTime
        }
        servicesData.value.api = {
          status: healthData.api === 200 ? '正常' : '异常'
        }
        servicesData.value.postgresql = {
          status: healthData.postgresql
        }
        servicesData.value.tdengine = {
          status: healthData.tdengine
        }
        
        // 添加到历史记录
        addToHistory(healthData)
      } catch (error) {
        console.error('刷新数据失败:', error)
        error.value = `刷新数据失败: ${error.message}`
      } finally {
        isLoading.value = false
      }
    }
    
    const addToHistory = (healthData) => {
      // 添加到历史记录的开头
      historyData.value.unshift({
        timestamp: healthData.timestamp,
        frontend: healthData.frontend,
        api: healthData.api,
        postgresql: healthData.postgresql,
        tdengine: healthData.tdengine,
        overallStatus: healthData.overallStatus
      })
      
      // 限制历史记录数量
      if (historyData.value.length > 10) {
        historyData.value.pop()
      }
    }
    
    const toggleAutoRefresh = () => {
      autoRefresh.value = !autoRefresh.value
      
      if (autoRefresh.value) {
        startAutoRefresh()
      } else {
        stopAutoRefresh()
      }
    }
    
    let refreshTimer = null
    
    const startAutoRefresh = () => {
      stopAutoRefresh()
      refreshTimer = setInterval(() => {
        refreshData()
      }, refreshInterval.value)
    }
    
    const stopAutoRefresh = () => {
      if (refreshTimer) {
        clearInterval(refreshTimer)
        refreshTimer = null
      }
    }
    
    // 生命周期钩子
    onMounted(() => {
      // 初始加载数据
      refreshData()
      
      // 添加一些示例历史数据
      for (let i = 1; i <= 3; i++) {
        const timestamp = Date.now() - (i * 3600000) // 每次间隔1小时
        const healthData = {
          timestamp,
          frontend: 200,
          api: 200,
          postgresql: '正常',
          tdengine: '不可访问'
        }
        addToHistory(healthData)
      }
    })
    
    onUnmounted(() => {
      // 清理定时器
      stopAutoRefresh()
    })
    
    return {
      // 状态
      autoRefresh,
      services,
      servicesData,
      historyData,
      isLoading,
      error,
      
      // 常量
      FRONTEND_URL,
      API_BASE_URL,
      
      // 计算属性
      isSystemHealthy,
      systemStatusMessage,
      
      // 方法
      formatDateTime,
      getStatusText,
      getServiceStatusText,
      checkService,
      refreshData,
      toggleAutoRefresh
    }
  }
}
</script>

<style scoped>
.monitor-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: bold;
  color: #333;
}

.actions {
  display: flex;
  gap: 1rem;
}

.btn-refresh {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f5f5f5;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-toggle {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f5f5f5;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-toggle.active {
  background-color: #e6f7ff;
  border-color: #1890ff;
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-right: 1rem;
  color: #1890ff;
  font-weight: bold;
}

.error-message {
  background-color: #fff1f0;
  color: #cf1322;
  padding: 1rem;
  border-left: 4px solid #cf1322;
  margin-bottom: 1rem;
  border-radius: 4px;
}

.icon {
  display: inline-block;
}

.monitor-summary {
  margin-bottom: 2rem;
}

.summary-card {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
}

.summary-card.status-normal {
  background-color: #f6ffed;
  border-left: 4px solid #52c41a;
}

.summary-card.status-warning {
  background-color: #fff7e6;
  border-left: 4px solid #faad14;
}

.summary-icon {
  font-size: 2rem;
  margin-right: 1rem;
}

.summary-card.status-normal .summary-icon {
  color: #52c41a;
}

.summary-card.status-warning .summary-icon {
  color: #faad14;
}

.summary-content {
  flex: 1;
}

.summary-title {
  font-size: 1.25rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.summary-description {
  color: #666;
}

.summary-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.detail-card {
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  background-color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.detail-label {
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: #333;
}

.detail-value {
  font-size: 1.5rem;
  font-weight: bold;
}

.detail-value.status-normal {
  color: #52c41a;
}

.detail-value.status-warning {
  color: #faad14;
}

.services-section {
  margin-bottom: 2rem;
}

.services-section h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #333;
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.service-card {
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  background-color: #fff;
  overflow: hidden;
}

.service-header {
  padding: 1rem;
  background-color: #fafafa;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.service-header h3 {
  font-size: 1.25rem;
  margin: 0;
}

.service-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: bold;
}

.service-status.status-normal {
  background-color: #f6ffed;
  color: #52c41a;
}

.service-status.status-warning {
  background-color: #fff7e6;
  color: #faad14;
}

.service-content {
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.service-info {
  flex: 1;
}

.info-item {
  margin-bottom: 0.5rem;
}

.info-label {
  font-weight: bold;
  margin-right: 0.5rem;
  color: #666;
}

.service-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  justify-content: center;
}

.btn-action {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f5f5f5;
  cursor: pointer;
  text-align: center;
  text-decoration: none;
  color: #333;
}

.btn-action:hover {
  background-color: #e9e9e9;
}

.history-section {
  margin-bottom: 2rem;
}

.history-section h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #333;
}

.history-table {
  overflow-x: auto;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  background-color: #fff;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background-color: #fafafa;
}

th {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
  font-weight: bold;
}

tbody td {
  padding: 0.75rem;
  border-bottom: 1px solid #f0f0f0;
}

.status-normal {
  background-color: #f6ffed;
}

.status-warning {
  background-color: #fff7e6;
}
</style>