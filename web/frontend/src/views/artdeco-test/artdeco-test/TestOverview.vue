<template>
  <div class="test-overview-container">
    <!-- 测试概览主容器 -->
    <div class="test-overview-header">
      <h2 class="test-overview-title">测试概览</h2>
      <div class="test-overview-actions">
        <button class="btn-primary" @click="refreshOverview">刷新概览</button>
        <button class="btn-secondary" @click="exportOverview">导出报告</button>
        <button class="btn-secondary" @click="toggleDashboardMode" :class="{ active: dashboardMode }">
          仪表盘模式 {{ dashboardMode ? '开启' : '关闭' }}
        </button>
      </div>
    </div>

    <!-- 测试状态卡片 -->
    <div class="test-stats-grid">
      <div class="card test-stat-card">
        <div class="card-header">
          <span class="stat-title">测试统计</span>
          <span class="stat-period">总体</span>
        </div>
        <div class="card-body">
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">总测试用例</span>
              <span class="stat-value">{{ totalTestCases }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">已执行</span>
              <span class="stat-value">{{ executedTestCases }}</span>
            </div>
          </div>
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">成功率</span>
              <span class="stat-value" :class="getSuccessRateClass(successRate)">
                {{ successRate }}%
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">失败率</span>
              <span class="stat-value" :class="getFailRateClass(failRate)">
                {{ failRate }}%
              </span>
            </div>
          </div>
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">覆盖率</span>
              <span class="stat-value">{{ coverageRate }}%</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">平均执行时间</span>
              <span class="stat-value">{{ avgExecutionTime }}ms</span>
            </div>
          </div>
        </div>
      </div>

      <div class="card test-status-card">
        <div class="card-header">
          <span class="stat-title">测试状态</span>
          <span class="stat-status" :class="getStatusClass(status)">
            {{ status }}
          </span>
        </div>
        <div class="card-body">
          <div class="status-list">
            <div class="status-item" :class="getCategoryStatusClass(category.status)" v-for="category in testCategories" :key="category.name">
              <span class="category-name">{{ category.name }}</span>
              <span class="category-stat">
                <span class="category-pass">{{ category.passed }}</span>/
                <span class="category-total">{{ category.total }}</span>
              </span>
              <span class="category-rate">{{ category.rate }}%</span>
              <span class="status-badge" :class="getCategoryStatusClass(category.status)">
                {{ category.status }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="card test-trend-card">
        <div class="card-header">
          <span class="stat-title">测试趋势</span>
          <select v-model="trendPeriod" class="period-select">
            <option value="day">日</option>
            <option value="week">周</option>
            <option value="month">月</option>
          </select>
        </div>
        <div class="card-body">
          <canvas id="testTrendChart" :height="300"></canvas>
          <div class="trend-summary">
            <div class="trend-metric">
              <span class="metric-label">测试次数</span>
              <span class="metric-value">{{ trendData.totalTests }}</span>
            </div>
            <div class="trend-metric">
              <span class="metric-label">通过率</span>
              <span class="metric-value" :class="getSuccessRateClass(trendData.passRate)">
                {{ trendData.passRate }}%
              </span>
            </div>
            <div class="trend-metric">
              <span class="metric-label">平均耗时</span>
              <span class="metric-value">{{ trendData.avgTime }}ms</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 测试结果列表 -->
    <div class="test-results-section" v-if="dashboardMode">
      <div class="card results-card">
        <div class="card-header">
          <h3>最新测试结果</h3>
          <div class="results-actions">
            <select v-model="resultFilter" class="filter-select">
              <option value="all">全部结果</option>
              <option value="passed">通过</option>
              <option value="failed">失败</option>
              <option value="warning">警告</option>
            </select>
            <button class="btn-secondary" @click="exportResults">导出结果</button>
          </div>
        </div>
        <div class="card-body">
          <table class="results-table">
            <thead>
              <tr>
                <th>测试用例</th>
                <th>模块</th>
                <th>执行时间</th>
                <th>状态</th>
                <th>覆盖率</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(result, index) in paginatedResults" :key="index">
                <td>{{ result.testCase }}</td>
                <td>{{ result.module }}</td>
                <td>{{ result.executionTime }}ms</td>
                <td :class="getStatusClass(result.status)">{{ result.status }}</td>
                <td>{{ result.coverage }}%</td>
              </tr>
            </tbody>
          </table>
          <div class="pagination">
            <button class="page-btn" :disabled="currentPage <= 1" @click="prevPage">
              上一页
            </button>
            <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
            <button class="page-btn" :disabled="currentPage >= totalPages" @click="nextPage">
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 测试配置 -->
    <div class="test-config-section">
      <div class="card config-card">
        <div class="card-header">
          <h3>测试配置</h3>
        </div>
        <div class="card-body">
          <div class="config-group">
            <div class="config-item">
              <span class="config-label">测试环境</span>
              <select v-model="testConfig.environment" class="config-select">
                <option value="development">开发</option>
                <option value="staging">测试</option>
                <option value="production">生产</option>
              </select>
            </div>
            <div class="config-item">
              <span class="config-label">超时设置</span>
              <input type="number" v-model="testConfig.timeout" class="config-input">
            </div>
            <div class="config-item">
              <span class="config-label">重试次数</span>
              <input type="number" v-model="testConfig.retries" class="config-input">
            </div>
          </div>
          <div class="config-actions">
            <button class="btn-primary" @click="applyConfig">应用配置</button>
            <button class="btn-secondary" @click="resetConfig">重置配置</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="quick-actions-section">
      <div class="card actions-card">
        <div class="card-header">
          <h3>快捷操作</h3>
        </div>
        <div class="card-body">
          <div class="actions-grid">
            <div class="action-item" @click="runAllTests">
              <span class="action-icon">▶️</span>
              <span class="action-label">运行所有测试</span>
            </div>
            <div class="action-item" @click="runFailedTests">
              <span class="action-icon">❌</span>
              <span class="action-label">运行失败测试</span>
            </div>
            <div class="action-item" @click="viewTestReport">
              <span class="action-icon">📊</span>
              <span class="action-label">查看测试报告</span>
            </div>
            <div class="action-item" @click="viewCoverageReport">
              <span class="action-icon">📈</span>
              <span class="action-label">查看覆盖率报告</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在加载测试概览...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useTestStore } from '@/stores/test'
import { useRouter } from 'vue-router'
import type { TestCase, TestStats, TestResult, TestTrend, TestConfig } from '@/types/test'
import { getTestOverview, getTestResults, runAllTests, getTestConfig, updateTestConfig } from '@/api/test'
import { formatValue } from '@/utils/format'

const router = useRouter()
const testStore = useTestStore()

const totalTestCases = ref<number>(0)
const executedTestCases = ref<number>(0)
const successRate = ref<number>(0)
const failRate = ref<number>(0)
const coverageRate = ref<number>(0)
const avgExecutionTime = ref<number>(0)
const status = ref<string>('未运行')

const testCategories = ref<TestCase[]>([])
const trendData = ref<TestTrend>({
  totalTests: 0,
  passRate: 0,
  avgTime: 0
})

const testResults = ref<TestResult[]>([])
const filteredResults = ref<TestResult[]>([])
const dashboardMode = ref<boolean>(false)
const resultFilter = ref<'all' | 'passed' | 'failed' | 'warning'>('all')
const trendPeriod = ref<'day' | 'week' | 'month'>('week')

const testConfig = reactive<TestConfig>({
  environment: 'development',
  timeout: 30,
  retries: 3
})

const currentPage = ref<number>(1)
const totalPages = ref<number>(1)
const pageSize = 20
const isLoading = ref<boolean>(false)

const paginatedResults = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return filteredResults.value.slice(start, end)
})

const refreshOverview = async () => {
  try {
    isLoading.value = true
    await Promise.all([
      loadTestStats(),
      loadTestTrends(),
      loadTestResults()
    ])
  } catch (error) {
    console.error('Error refreshing test overview:', error)
  } finally {
    isLoading.value = false
  }
}

const loadTestStats = async () => {
  try {
    const response = await getTestOverview()
    
    if (response.code === 200 && response.data) {
      const stats = response.data.data
      
      totalTestCases.value = stats.totalTestCases
      executedTestCases.value = stats.executedTestCases
      successRate.value = stats.successRate
      failRate.value = stats.failRate
      coverageRate.value = stats.coverageRate
      avgExecutionTime.value = stats.avgExecutionTime
      status.value = stats.status
      
      testCategories.value = stats.categories || []
    } else {
      console.error('Failed to load test stats:', response.message)
    }
  } catch (error) {
    console.error('Error loading test stats:', error)
  }
}

const loadTestTrends = async () => {
  try {
    const response = await getTestOverview()
    
    if (response.code === 200 && response.data) {
      trendData.value = response.data.trend
      await renderTrendChart()
    } else {
      console.error('Failed to load test trends:', response.message)
    }
  } catch (error) {
    console.error('Error loading test trends:', error)
  }
}

const loadTestResults = async () => {
  try {
    const response = await getTestResults()
    
    if (response.code === 200 && response.data) {
      testResults.value = response.data.data
      applyResultFilter()
    } else {
      console.error('Failed to load test results:', response.message)
    }
  } catch (error) {
    console.error('Error loading test results:', error)
  }
}

const renderTrendChart = async () => {
  try {
    const canvas = document.getElementById('testTrendChart')
    
    if (!canvas) {
      return
    }
    
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 20
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    // 绘制测试趋势线
    ctx.strokeStyle = '#2196f3'
    ctx.lineWidth = 2
    ctx.beginPath()
    
    const dates = trendData.value.dates || []
    const passRates = trendData.value.passRates || []
    const totalTests = trendData.value.totalTests || []
    
    if (passRates.length < 2) {
      return
    }
    
    const stepX = chartWidth / (dates.length - 1)
    const stepY = chartHeight / 100
    
    for (let i = 0; i < dates.length; i++) {
      const x = padding + i * stepX
      const normalizedRate = passRates[i] / 100 * chartHeight
      
      ctx.moveTo(x, padding + chartHeight / 2 - normalizedRate)
      ctx.lineTo(x, padding + chartHeight / 2 - normalizedRate)
    }
    
    ctx.stroke()
    
    // 绘制填充区域
    ctx.fillStyle = 'rgba(33, 150, 243, 0.1)'
    ctx.fill()
    ctx.moveTo(padding, padding)
    ctx.lineTo(padding + chartWidth, padding)
    ctx.lineTo(padding + chartWidth, padding + chartHeight)
    ctx.lineTo(padding, padding + chartHeight)
    ctx.fill()
    
    // 绘制网格线
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.1)'
    ctx.lineWidth = 1
    
    for (let i = 0; i <= 5; i++) {
      const y = padding + i * (chartHeight / 5)
      ctx.beginPath()
      ctx.moveTo(padding, y)
      ctx.lineTo(padding + chartWidth, y)
      ctx.stroke()
    }
  } catch (error) {
    console.error('Error rendering trend chart:', error)
  }
}

const toggleDashboardMode = () => {
  dashboardMode.value = !dashboardMode.value
}

const applyResultFilter = () => {
  let filtered = testResults.value
  
  if (resultFilter.value !== 'all') {
    filtered = filtered.filter(result => result.status === resultFilter.value)
  }
  
  filteredResults.value = filtered
  currentPage.value = 1
  totalPages.value = Math.ceil(filtered.length / pageSize)
}

const exportOverview = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      stats: {
        totalTestCases: totalTestCases.value,
        executedTestCases: executedTestCases.value,
        successRate: successRate.value,
        failRate: failRate.value,
        coverageRate: coverageRate.value,
        avgExecutionTime: avgExecutionTime.value,
        status: status.value
      },
      categories: testCategories.value,
      trends: trendData.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `test_overview_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Test overview exported')
  } catch (error) {
    console.error('Error exporting overview:', error)
  }
}

const exportResults = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      filter: resultFilter.value,
      data: filteredResults.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `test_results_${resultFilter.value}_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Test results exported')
  } catch (error) {
    console.error('Error exporting results:', error)
  }
}

const applyConfig = async () => {
  try {
    const response = await updateTestConfig(testConfig)
    
    if (response.code === 200) {
      console.log('Test config updated successfully')
      refreshOverview()
    } else {
      console.error('Failed to update test config:', response.message)
    }
  } catch (error) {
    console.error('Error applying config:', error)
  }
}

const resetConfig = () => {
  testConfig.environment = 'development'
  testConfig.timeout = 30
  testConfig.retries = 3
}

const runAllTests = async () => {
  try {
    const response = await runAllTests()
    
    if (response.code === 200) {
      console.log('All tests started successfully')
      status.value = '正在运行'
      refreshOverview()
    } else {
      console.error('Failed to start tests:', response.message)
    }
  } catch (error) {
    console.error('Error running tests:', error)
  }
}

const runFailedTests = async () => {
  try {
    const response = await runAllTests({ filter: 'failed' })
    
    if (response.code === 200) {
      console.log('Failed tests started successfully')
    } else {
      console.error('Failed to start failed tests:', response.message)
    }
  } catch (error) {
    console.error('Error running failed tests:', error)
  }
}

const viewTestReport = () => {
  router.push('/test/reports')
}

const viewCoverageReport = () => {
  router.push('/test/coverage')
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const getStatusClass = (status: string) => {
  if (status === '通过') return 'status-passed'
  if (status === '失败') return 'status-failed'
  if (status === '警告') return 'status-warning'
  return 'status-unknown'
}

const getSuccessRateClass = (rate: number) => {
  if (rate >= 90) return 'rate-excellent'
  if (rate >= 70) return 'rate-good'
  if (rate >= 50) return 'rate-fair'
  return 'rate-poor'
}

const getFailRateClass = (rate: number) => {
  if (rate <= 10) return 'rate-excellent'
  if (rate <= 30) return 'rate-good'
  if (rate <= 50) return 'rate-fair'
  return 'rate-poor'
}

const getCategoryStatusClass = (status: string) => {
  if (status === '通过') return 'category-passed'
  if (status === '失败') return 'category-failed'
  if (status === '警告') return 'category-warning'
  return 'category-unknown'
}

onMounted(async () => {
  await loadTestConfig()
  await refreshOverview()
  console.log('TestOverview component mounted')
})
</script>

<style scoped lang="scss">
.test-overview-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.test-overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.test-overview-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.test-overview-actions {
  display: flex;
  gap: 10px;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background: #2196f3;
  color: white;
}

.btn-primary:hover {
  background: #1976d2;
}

.btn-secondary {
  background: transparent;
  color: #2196f3;
  border: 1px solid #2196f3;
}

.btn-secondary:hover {
  background: #f0f0f0;
}

.btn-secondary.active {
  background: #2196f3;
  color: white;
}

.test-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.stat-period {
  font-size: 14px;
  color: #999;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 4px;
}

.stat-status {
  font-size: 14px;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 4px;
  background: #f5f7fa;
}

.status-running {
  color: #2196f3;
}

.status-completed {
  color: #4caf50;
}

.status-failed {
  color: #f44336;
}

.card-body {
  padding: 20px;
}

.stat-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 15px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.stat-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.rate-excellent {
  color: #4caf50;
}

.rate-good {
  color: #81c784;
}

.rate-fair {
  color: #ffc107;
}

.rate-poor {
  color: #f44336;
}

.test-status-card {
  background: white;
  border-radius: 8px;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.status-item {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  padding: 10px;
  border-radius: 4px;
  background: #f9f9f9;
}

.category-name {
  font-weight: bold;
  color: #333;
}

.category-stat {
  font-weight: 500;
  color: #666;
}

.category-pass {
  color: #4caf50;
}

.category-total {
  color: #999;
}

.category-rate {
  font-weight: bold;
  color: #333;
}

.category-passed {
  background: rgba(76, 175, 80, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
  color: #4caf50;
}

.category-failed {
  background: rgba(248, 113, 113, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
  color: #f44336;
}

.category-warning {
  background: rgba(255, 193, 7, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
  color: #ffc107;
}

.category-unknown {
  background: rgba(153, 153, 153, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
  color: #999;
}

.status-badge {
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 4px;
}

.test-trend-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.card-header .period-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
}

.trend-chart {
  margin-bottom: 20px;
}

.trend-summary {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
}

.trend-metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.trend-metric:last-child {
  border-bottom: none;
}

.metric-label {
  color: white;
  font-size: 14px;
  font-weight: 500;
}

.metric-value {
  color: white;
  font-size: 20px;
  font-weight: bold;
}

.test-results-section {
  margin-bottom: 20px;
}

.results-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.results-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
}

.results-table th {
  padding: 12px;
  text-align: left;
  border-bottom: 2px solid #2196f3;
  font-weight: bold;
  color: #333;
  background: #f9f9f9;
}

.results-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.results-table tbody tr:hover {
  background: #f5f7fa;
}

.results-table .status-passed {
  color: #4caf50;
  font-weight: bold;
}

.results-table .status-failed {
  color: #f44336;
  font-weight: bold;
}

.pagination {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 20px;
}

.page-btn {
  padding: 10px 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  background: #2196f3;
  color: white;
}

.page-btn:disabled {
  background: #f0f0f0;
  color: #ccc;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.test-config-section {
  margin-bottom: 20px;
}

.config-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.config-card .card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.config-body {
  padding: 20px;
}

.config-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.config-input {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.config-input:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.2);
}

.config-select {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.config-select:focus {
  outline: none;
  border-color: #2196f3;
}

.config-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.quick-actions-section {
  margin-bottom: 20px;
}

.actions-card {
  background: white;
  border-radius: 8px;
}

.actions-card .card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.action-item {
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.action-item:hover {
  background: #f5f7fa;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.action-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.action-label {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #2196f3;
  border-top-color: transparent;
  border-right-color: #2196f3;
  border-bottom-color: #2196f3;
  border-left-color: #2196f3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: white;
  font-size: 16px;
  font-weight: 500;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .test-stats-grid {
    grid-template-columns: 1fr;
  }
  
  .config-group {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
}
</style>
