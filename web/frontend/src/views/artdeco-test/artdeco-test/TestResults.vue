<template>
  <div class="test-results-container">
    <!-- 测试结果主容器 -->
    <div class="test-results-header">
      <h2 class="test-results-title">测试结果</h2>
      <div class="test-results-actions">
        <button class="btn-primary" @click="refreshResults">刷新结果</button>
        <button class="btn-secondary" @click="filterResults">筛选结果</button>
        <button class="btn-secondary" @click="exportResults">导出报告</button>
      </div>
    </div>

    <!-- 结果筛选面板 -->
    <div class="results-filter-section">
      <div class="filter-card">
        <div class="filter-header">
          <h3>结果筛选</h3>
          <button class="close-btn" @click="toggleFilter">×</button>
        </div>
        <div class="filter-body">
          <div class="filter-row">
            <div class="filter-item">
              <span class="filter-label">测试用例</span>
              <input type="text" v-model="filters.testCase" placeholder="输入测试用例名称" class="search-input">
            </div>
            <div class="filter-item">
              <span class="filter-label">状态</span>
              <select v-model="filters.status" class="filter-select">
                <option value="all">全部</option>
                <option value="passed">通过</option>
                <option value="failed">失败</option>
                <option value="warning">警告</option>
                <option value="timeout">超时</option>
              </select>
            </div>
          </div>
          <div class="filter-row">
            <div class="filter-item">
              <span class="filter-label">模块</span>
              <select v-model="filters.module" class="filter-select">
                <option value="all">全部</option>
                <option value="market">市场数据</option>
                <option value="trading">交易</option>
                <option value="risk">风险管理</option>
                <option value="portfolio">投资组合</option>
              </select>
            </div>
            <div class="filter-item">
              <span class="filter-label">执行时间</span>
              <select v-model="filters.executionTime" class="filter-select">
                <option value="all">全部</option>
                <option value="fast">< 10秒</option>
                <option value="medium">10-30秒</option>
                <option value="slow">> 30秒</option>
              </select>
            </div>
          </div>
          <div class="filter-actions">
            <button class="btn-primary" @click="applyFilters">应用筛选</button>
            <button class="btn-secondary" @click="resetFilters">重置</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 结果统计卡片 -->
    <div class="results-stats-grid">
      <div class="card stat-card">
        <div class="card-header">
          <span class="stat-title">结果统计</span>
          <span class="stat-period">总计</span>
        </div>
        <div class="card-body">
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">总测试数</span>
              <span class="stat-value">{{ totalTests }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">已执行</span>
              <span class="stat-value">{{ executedTests }}</span>
            </div>
          </div>
          <div class="stat-row">
            <div class="stat-item">
              <span class="stat-label">通过</span>
              <span class="stat-value passed">{{ passedTests }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">失败</span>
              <span class="stat-value failed">{{ failedTests }}</span>
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
              <span class="stat-label">平均时间</span>
              <span class="stat-value">{{ avgExecutionTime }}ms</span>
            </div>
          </div>
        </div>
      </div>

      <div class="card stat-card">
        <div class="card-header">
          <span class="stat-title">执行时间</span>
          <span class="stat-period">总计</span>
        </div>
        <div class="card-body">
          <div class="chart-container">
            <canvas id="executionTimeChart" :height="250"></canvas>
          </div>
          <div class="chart-legend">
            <div class="legend-item" v-for="item in executionTimeDistribution" :key="item.range">
              <div class="legend-color" :style="{ backgroundColor: item.color }"></div>
              <span class="legend-label">{{ item.range }}</span>
              <span class="legend-value">{{ item.count }}个</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 结果列表 -->
    <div class="results-list">
      <div class="card result-card" v-for="result in filteredResults" :key="result.id">
        <div class="card-header" :class="getStatusClass(result.status)">
          <span class="result-name">{{ result.testCaseName }}</span>
          <span class="result-code">{{ result.testCaseCode }}</span>
          <span class="result-status">{{ getStatusName(result.status) }}</span>
          <span class="result-time">{{ formatTime(result.executionTime) }}</span>
        </div>
        <div class="card-body">
          <div class="result-details">
            <div class="detail-row">
              <span class="detail-label">模块</span>
              <span class="detail-value">{{ result.module }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">执行时间</span>
              <span class="detail-time">{{ result.executionTime }}ms</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">状态</span>
              <span class="detail-status" :class="getStatusClass(result.status)">
                {{ getStatusName(result.status) }}
              </span>
            </div>
            <div class="detail-row">
              <span class="detail-label">覆盖率</span>
              <span class="detail-coverage">{{ result.coverage }}%</span>
            </div>
          </div>
          <div class="result-chart">
            <canvas :id="`result-chart-${result.id}`" :height="150"></canvas>
          </div>
          <div class="result-output">
            <div class="output-header">输出</div>
            <div class="output-content">
              <pre class="output-text">{{ result.output || '无输出' }}</pre>
            </div>
          </div>
          <div class="result-actions">
            <div class="action-buttons">
              <button class="btn-action" @click="viewResultDetail(result)">
                <span class="action-icon">📊</span>
                <span class="action-label">查看详情</span>
              </button>
              <button class="btn-action" @click="rerunTest(result)" :disabled="isRerunning">
                <span class="action-icon">🔄</span>
                <span class="action-label">{{ isRerunning ? '重试中...' : '重新执行' }}</span>
              </button>
              <button class="btn-action" @click="viewCoverage(result)">
                <span class="action-icon">📈</span>
                <span class="action-label">覆盖率</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="results-pagination">
      <button class="page-btn" :disabled="currentPage <= 1" @click="prevPage">
        上一页
      </button>
      <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
      <button class="page-btn" :disabled="currentPage >= totalPages" @click="nextPage">
        下一页
      </button>
      <div class="page-size-selector">
        <label class="page-size-label">每页显示:</label>
        <select v-model="pageSize" @change="changePageSize" class="page-size-select">
          <option :value="10">10</option>
          <option :value="20">20</option>
          <option :value="50">50</option>
        </select>
      </div>
    </div>

    <!-- 详情模态框 -->
    <div class="modal" v-if="showResultDetail" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>测试结果详情</h3>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-section">
            <div class="detail-section-title">基本信息</div>
            <div class="detail-section-body">
              <div class="detail-row">
                <span class="detail-label">测试用例</span>
                <span class="detail-value">{{ selectedResult.testCaseName }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">测试用例代码</span>
                <span class="detail-value">{{ selectedResult.testCaseCode }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">模块</span>
                <span class="detail-value">{{ selectedResult.module }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">执行时间</span>
                <span class="detail-value">{{ selectedResult.executionTime }}ms</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">状态</span>
                <span class="detail-value" :class="getStatusClass(selectedResult.status)">
                  {{ getStatusName(selectedResult.status) }}
                </span>
              </div>
            </div>
          </div>
          <div class="detail-section">
            <div class="detail-section-title">结果统计</div>
            <div class="detail-section-body">
              <div class="detail-row">
                <span class="detail-label">覆盖率</span>
                <span class="detail-value">{{ selectedResult.coverage }}%</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">断言数量</span>
                <span class="detail-value">{{ selectedResult.assertions }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">通过断言</span>
                <span class="detail-value passed">{{ selectedResult.passedAssertions }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">失败断言</span>
                <span class="detail-value failed">{{ selectedResult.failedAssertions }}</span>
              </div>
            </div>
          </div>
          <div class="detail-section">
            <div class="detail-section-title">性能指标</div>
            <div class="detail-section-body">
              <div class="detail-row">
                <span class="detail-label">开始时间</span>
                <span class="detail-value">{{ formatDateTime(selectedResult.startTime) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">结束时间</span>
                <span class="detail-value">{{ formatDateTime(selectedResult.endTime) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">持续时间</span>
                <span class="detail-value">{{ selectedResult.duration }}ms</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">CPU使用</span>
                <span class="detail-value">{{ selectedResult.cpuUsage }}%</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">内存使用</span>
                <span class="detail-value">{{ selectedResult.memoryUsage }}MB</span>
              </div>
            </div>
          </div>
          <div class="detail-section">
            <div class="detail-section-title">输出日志</div>
            <div class="detail-section-body">
              <pre class="output-text">{{ selectedResult.output }}</pre>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-primary" @click="rerunTestFromDetail">重新执行</button>
          <button class="btn-secondary" @click="viewCoverageFromDetail">查看覆盖率</button>
          <button class="btn-secondary" @click="closeModal">关闭</button>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在加载测试结果...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useTestStore } from '@/stores/test'
import { useRouter } from 'vue-router'
import type { TestResult, TestResultStats, ResultFilters, ExecutionTimeDistribution } from '@/types/test'
import { getTestResults, getTestResultsStats, rerunTest, getCoverageReport } from '@/api/test'
import { formatTime, formatDateTime, getStatusName } from '@/utils/format'

const router = useRouter()
const testStore = useTestStore()

const allResults = ref<TestResult[]>([])
const filteredResults = ref<TestResult[]>([])
const selectedResult = ref<TestResult>({})
const showResultDetail = ref<boolean>(false)
const showFilter = ref<boolean>(false)
const isRerunning = ref<boolean>(false)
const isLoading = ref<boolean>(false)

const totalTests = ref<number>(0)
const executedTests = ref<number>(0)
const passedTests = ref<number>(0)
const failedTests = ref<number>(0)
const successRate = ref<number>(0)
const avgExecutionTime = ref<number>(0)
const executionTimeDistribution = ref<ExecutionTimeDistribution[]>([])

const filters = reactive<ResultFilters>({
  testCase: '',
  status: 'all',
  module: 'all',
  executionTime: 'all'
})

const currentPage = ref<number>(1)
const totalPages = ref<number>(1)
const pageSize = ref<number>(20)

const refreshResults = async () => {
  try {
    isLoading.value = true
    await Promise.all([
      loadResults(),
      loadResultsStats()
    ])
  } catch (error) {
    console.error('Error refreshing results:', error)
  } finally {
    isLoading.value = false
  }
}

const loadResults = async () => {
  try {
    const response = await getTestResults(filters)
    
    if (response.code === 200 && response.data) {
      allResults.value = response.data.data
      applyFilters()
      await renderAllResultCharts(response.data.data)
    } else {
      console.error('Failed to load test results:', response.message)
    }
  } catch (error) {
    console.error('Error loading test results:', error)
    throw error
  }
}

const loadResultsStats = async () => {
  try {
    const response = await getTestResultsStats()
    
    if (response.code === 200 && response.data) {
      const stats = response.data.data
      
      totalTests.value = stats.totalTests
      executedTests.value = stats.executedTests
      passedTests.value = stats.passedTests
      failedTests.value = stats.failedTests
      successRate.value = stats.successRate
      avgExecutionTime.value = stats.avgExecutionTime
      executionTimeDistribution.value = stats.executionTimeDistribution || []
      
      await renderExecutionTimeChart()
    } else {
      console.error('Failed to load results stats:', response.message)
    }
  } catch (error) {
    console.error('Error loading results stats:', error)
  }
}

const renderAllResultCharts = async (results: TestResult[]) => {
  for (const result of results) {
    const canvas = document.getElementById(`result-chart-${result.id}`)
    if (canvas) {
      await renderResultChart(canvas, result)
    }
  }
}

const renderResultChart = async (canvas: HTMLCanvasElement, result: TestResult) => {
  try {
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 10
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    const values = result.executionTimeHistory || []
    
    if (values.length < 2) {
      return
    }
    
    const x = padding
    const y = padding
    
    const stepX = chartWidth / (values.length - 1)
    const max = Math.max(...values)
    const min = Math.min(...values)
    const range = max - min
    
    if (range === 0) {
      return
    }
    
    const stepY = chartHeight / range
    
    ctx.strokeStyle = '#2196f3'
    ctx.lineWidth = 2
    ctx.beginPath()
    
    for (let i = 0; i < values.length; i++) {
      const normalizedValue = (values[i] - min) / range * chartHeight
      
      ctx.moveTo(x + i * stepX, y + chartHeight / 2 - normalizedValue / 2)
      ctx.lineTo(x + i * stepX, y + chartHeight / 2 - normalizedValue / 2)
    }
    
    ctx.stroke()
  } catch (error) {
    console.error('Error rendering result chart:', error)
  }
}

const renderExecutionTimeChart = async () => {
  try {
    const canvas = document.getElementById('executionTimeChart')
    
    if (!canvas) {
      return
    }
    
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 40
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    const x = padding
    const y = padding
    
    const barWidth = chartWidth / executionTimeDistribution.value.length * 0.8
    const max = Math.max(...executionTimeDistribution.value.map(d => d.count))
    
    if (max === 0) {
      return
    }
    
    const stepY = chartHeight / max
    
    const colors = ['#4caf50', '#81c784', '#ffc107', '#ff9800', '#f44336']
    
    for (let i = 0; i < executionTimeDistribution.value.length; i++) {
      const item = executionTimeDistribution.value[i]
      const barHeight = (item.count / max) * stepY
      
      ctx.fillStyle = colors[i % colors.length]
      ctx.fillRect(x + i * barWidth, y + chartHeight - barHeight, barWidth, barHeight)
      
      ctx.fillStyle = '#333'
      ctx.font = '14px Arial'
      ctx.textAlign = 'center'
      ctx.fillText(item.range, x + barWidth / 2, y + chartHeight - barHeight - 10)
      ctx.fillText(item.count.toString(), x + barWidth / 2, y + chartHeight + 10)
    }
  } catch (error) {
    console.error('Error rendering execution time chart:', error)
  }
}

const toggleFilter = () => {
  showFilter.value = !showFilter.value
}

const applyFilters = async () => {
  let filtered = allResults.value
  
  if (filters.testCase.trim()) {
    filtered = filtered.filter(result => result.testCaseName.includes(filters.testCase.trim()))
  }
  
  if (filters.status !== 'all') {
    filtered = filtered.filter(result => result.status === filters.status)
  }
  
  if (filters.module !== 'all') {
    filtered = filtered.filter(result => result.module === filters.module)
  }
  
  if (filters.executionTime !== 'all') {
    if (filters.executionTime === 'fast') {
      filtered = filtered.filter(result => result.executionTime < 10)
    } else if (filters.executionTime === 'medium') {
      filtered = filtered.filter(result => result.executionTime >= 10 && result.executionTime <= 30)
    } else if (filters.executionTime === 'slow') {
      filtered = filtered.filter(result => result.executionTime > 30)
    }
  }
  
  filteredResults.value = filtered
  currentPage.value = 1
  totalPages.value = Math.ceil(filtered.length / pageSize.value)
}

const resetFilters = () => {
  filters.testCase = ''
  filters.status = 'all'
  filters.module = 'all'
  filters.executionTime = 'all'
  applyFilters()
  showFilter.value = false
}

const filterResults = () => {
  showFilter.value = true
}

const exportResults = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      filters: {
        testCase: filters.testCase,
        status: filters.status,
        module: filters.module,
        executionTime: filters.executionTime
      },
      data: filteredResults.value,
      stats: {
        totalTests: totalTests.value,
        executedTests: executedTests.value,
        passedTests: passedTests.value,
        failedTests: failedTests.value,
        successRate: successRate.value,
        avgExecutionTime: avgExecutionTime.value
      }
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `test_results_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Test results exported')
  } catch (error) {
    console.error('Error exporting results:', error)
  }
}

const viewResultDetail = (result: TestResult) => {
  selectedResult.value = result
  showResultDetail.value = true
}

const closeModal = () => {
  showResultDetail.value = false
}

const rerunTest = async (result: TestResult) => {
  try {
    isRerunning.value = true
    const response = await rerunTest(result.id)
    
    if (response.code === 200) {
      await refreshResults()
      console.log('Test rerun started successfully')
    } else {
      console.error('Failed to rerun test:', response.message)
    }
  } catch (error) {
    console.error('Error rerunning test:', error)
  } finally {
    isRerunning.value = false
  }
}

const rerunTestFromDetail = async () => {
  await rerunTest(selectedResult.value)
}

const viewCoverage = async (result: TestResult) => {
  try {
    router.push('/test/coverage', {
      state: {
        resultId: result.id,
        testCaseCode: result.testCaseCode
      }
    })
  } catch (error) {
    console.error('Error navigating to coverage:', error)
  }
}

const viewCoverageFromDetail = async () => {
  await viewCoverage(selectedResult.value)
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

const changePageSize = (newSize: number) => {
  pageSize.value = newSize
  currentPage.value = 1
  totalPages.value = Math.ceil(filteredResults.value.length / newPageSize)
}

const getStatusClass = (status: string) => {
  if (status === 'passed') return 'status-passed'
  if (status === 'failed') return 'status-failed'
  if (status === 'warning') return 'status-warning'
  if (status === 'timeout') return 'status-timeout'
  return 'status-unknown'
}

const getSuccessRateClass = (rate: number) => {
  if (rate >= 90) return 'rate-excellent'
  if (rate >= 70) return 'rate-good'
  if (rate >= 50) return 'rate-fair'
  return 'rate-poor'
}

const formatTime = (timestamp: string) => {
  if (!timestamp) return '-'
  
  const date = new Date(timestamp)
  return date.toLocaleTimeString()
}

const formatDateTime = (timestamp: string) => {
  if (!timestamp) return '-'
  
  const date = new Date(timestamp)
  return date.toLocaleString()
}

onMounted(async () => {
  await refreshResults()
  console.log('TestResults component mounted')
})
</script>

<style scoped lang="scss">
.test-results-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.test-results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.test-results-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.test-results-actions {
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
  background: #4caf50;
  color: white;
}

.btn-primary:hover {
  background: #45a049;
}

.btn-secondary {
  background: transparent;
  color: #4caf50;
  border: 1px solid #4caf50;
}

.btn-secondary:hover {
  background: #f0f0f0;
  border-color: #4caf50;
}

.results-filter-section {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  width: 400px;
  max-height: 80vh;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.filter-card {
  width: 100%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #4caf50 0%, #1b5e20 100%);
  color: white;
}

.filter-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
}

.close-btn {
  background: transparent;
  border: none;
  color: white;
  font-size: 24px;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  transition: all 0.3s;
}

.close-btn:hover {
  transform: scale(1.1);
}

.filter-body {
  padding: 20px;
  overflow-y: auto;
}

.filter-row {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.filter-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.search-input {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: #4caf50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
}

.filter-select {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: #4caf50;
}

.filter-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.results-stats-grid {
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

.stat-value.passed {
  color: #4caf50;
}

.stat-value.failed {
  color: #f44336;
}

.chart-container {
  margin-bottom: 15px;
}

.chart-legend {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
  margin-top: 15px;
}

.legend-item {
  display: flex;
  gap: 10px;
  align-items: center;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  flex-shrink: 0;
}

.legend-label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.legend-value {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.result-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.result-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.card-header.status-passed {
  background: linear-gradient(135deg, #4caf50 0%, #1b5e20 100%);
}

.card-header.status-failed {
  background: linear-gradient(135deg, #f44336 0%, #c62828 100%);
}

.card-header.status-warning {
  background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
}

.card-header.status-timeout {
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
}

.result-name {
  font-size: 18px;
  font-weight: bold;
  color: white;
  flex-grow: 1;
}

.result-code {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(0, 0, 0, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
  margin-left: 10px;
}

.result-status {
  font-size: 14px;
  color: white;
  font-weight: 500;
  margin-left: 10px;
}

.result-time {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  margin-left: 10px;
}

.result-details {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.detail-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
}

.detail-value {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.detail-time {
  font-size: 14px;
  color: #999;
}

.detail-status.status-passed {
  color: #4caf50;
  font-weight: bold;
}

.detail-status.status-failed {
  color: #f44336;
  font-weight: bold;
}

.detail-coverage {
  font-size: 16px;
  font-weight: 500;
  color: #4caf50;
}

.result-chart {
  margin-bottom: 15px;
}

.result-output {
  margin-bottom: 15px;
}

.output-header {
  font-size: 14px;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
}

.output-content {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
}

.output-text {
  font-size: 14px;
  color: #666;
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
  margin: 0;
}

.result-actions {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.btn-action {
  padding: 10px 20px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-action:hover {
  border-color: #4caf50;
  transform: translateY(-2px);
}

.action-icon {
  font-size: 20px;
}

.action-label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.results-pagination {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
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
  background: #f0f0f0;
}

.page-btn:disabled {
  background: #f5f5f5;
  color: #ccc;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.page-size-selector {
  display: flex;
  gap: 10px;
  align-items: center;
}

.page-size-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.page-size-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  width: 600px;
  max-height: 80vh;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 20px;
  background: linear-gradient(135deg, #4caf50 0%, #1b5e20 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
}

.close-btn {
  background: transparent;
  border: none;
  color: white;
  font-size: 24px;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  transition: all 0.3s;
}

.close-btn:hover {
  transform: scale(1.1);
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 30px;
}

.detail-section-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #4caf50;
}

.detail-section-body {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
}

.detail-section-body .detail-row {
  margin-bottom: 10px;
}

.modal-footer {
  padding: 20px;
  background: #f5f7fa;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
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
  border: 5px solid #4caf50;
  border-top-color: transparent;
  border-right-color: #4caf50;
  border-bottom-color: #4caf50;
  border-left-color: #4caf50;
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
  .results-stats-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-legend {
    grid-template-columns: 1fr;
  }
}
</style>
