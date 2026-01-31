<template>
  <div class="test-report-container">
    <!-- 测试报告主容器 -->
    <div class="test-report-header">
      <h2 class="test-report-title">测试报告</h2>
      <div class="test-report-actions">
        <button class="btn-primary" @click="generateReport">生成报告</button>
        <button class="btn-secondary" @click="exportReport">导出报告</button>
        <button class="btn-secondary" @click="exportHistory">导出历史</button>
      </div>
    </div>

    <!-- 报告生成面板 -->
    <div class="report-generation-section" v-if="showReportGenerator">
      <div class="card generator-card">
        <div class="card-header">
          <h3>生成测试报告</h3>
          <button class="close-btn" @click="toggleReportGenerator">×</button>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label class="form-label">报告名称</label>
            <input type="text" v-model="reportForm.name" placeholder="输入报告名称" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">报告类型</label>
            <select v-model="reportForm.type" class="form-select">
              <option value="summary">摘要报告</option>
              <option value="detailed">详细报告</option>
              <option value="performance">性能报告</option>
              <option value="coverage">覆盖率报告</option>
              <option value="trend">趋势报告</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">时间范围</label>
            <select v-model="reportForm.timeRange" class="form-select">
              <option value="day">今天</option>
              <option value="week">最近一周</option>
              <option value="month">最近一月</option>
              <option value="quarter">最近三月</option>
              <option value="year">最近一年</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">测试模块</label>
            <select v-model="reportForm.module" class="form-select">
              <option value="all">全部模块</option>
              <option value="market">市场数据</option>
              <option value="trading">交易</option>
              <option value="risk">风险管理</option>
              <option value="portfolio">投资组合</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">报告格式</label>
            <select v-model="reportForm.format" class="form-select">
              <option value="html">HTML</option>
              <option value="pdf">PDF</option>
              <option value="word">Word</option>
              <option value="excel">Excel</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">包含图表</label>
            <div class="checkbox-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="reportForm.includeCharts.summary"> 摘要图表
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="reportForm.includeCharts.performance"> 性能图表
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="reportForm.includeCharts.coverage"> 覆盖率图表
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="reportForm.includeCharts.trend"> 趋势图表
              </label>
            </div>
          </div>
          <div class="form-actions">
            <button class="btn-primary" @click="generateAndDownload">生成并下载</button>
            <button class="btn-secondary" @click="resetReportForm">重置</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 报告列表 -->
    <div class="report-list-section">
      <div class="card reports-card">
        <div class="card-header">
          <h3>历史报告</h3>
          <div class="reports-actions">
            <select v-model="reportTypeFilter" class="filter-select">
              <option value="all">全部类型</option>
              <option value="summary">摘要报告</option>
              <option value="detailed">详细报告</option>
              <option value="performance">性能报告</option>
              <option value="coverage">覆盖率报告</option>
              <option value="trend">趋势报告</option>
            </select>
            <button class="btn-secondary" @click="refreshReports">刷新</button>
          </div>
        </div>
        <div class="card-body">
          <table class="reports-table">
            <thead>
              <tr>
                <th>报告名称</th>
                <th>报告类型</th>
                <th>生成时间</th>
                <th>测试数量</th>
                <th>通过率</th>
                <th>文件大小</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="report in paginatedReports" :key="report.id">
                <td class="report-name">{{ report.name }}</td>
                <td class="report-type">{{ report.type }}</td>
                <td class="report-time">{{ formatTime(report.generatedAt) }}</td>
                <td class="report-count">{{ report.testCount }}</td>
                <td class="report-rate" :class="getSuccessRateClass(report.passRate)">
                  {{ report.passRate }}%
                </td>
                <td class="report-size">{{ formatFileSize(report.fileSize) }}</td>
                <td class="report-actions">
                  <button class="btn-view" @click="viewReport(report)">查看</button>
                  <button class="btn-download" @click="downloadReport(report)">下载</button>
                  <button class="btn-delete" @click="deleteReport(report)">删除</button>
                </td>
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
            <div class="page-size-selector">
              <label class="page-size-label">每页显示:</label>
              <select v-model="pageSize" @change="changePageSize" class="page-size-select">
                <option :value="10">10</option>
                <option :value="20">20</option>
                <option :value="50">50</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 报告预览 -->
    <div class="report-preview-section" v-if="showReportPreview">
      <div class="card preview-card">
        <div class="card-header">
          <h3>报告预览</h3>
          <button class="close-btn" @click="toggleReportPreview">×</button>
        </div>
        <div class="card-body">
          <div class="preview-content">
            <div class="preview-header">
              <h4>{{ previewReport.name }}</h4>
              <span class="preview-type">{{ previewReport.type }}</span>
            </div>
            <div class="preview-summary">
              <div class="summary-item">
                <span class="summary-label">生成时间</span>
                <span class="summary-value">{{ formatTime(previewReport.generatedAt) }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">测试数量</span>
                <span class="summary-value">{{ previewReport.testCount }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">通过数量</span>
                <span class="summary-value">{{ previewReport.passedCount }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">通过率</span>
                <span class="summary-value" :class="getSuccessRateClass(previewReport.passRate)">
                  {{ previewReport.passRate }}%
                </span>
              </div>
            </div>
            <div class="preview-charts">
              <div class="chart-section">
                <h5>测试结果分布</h5>
                <canvas id="testDistributionChart" :height="200"></canvas>
              </div>
              <div class="chart-section">
                <h5>测试趋势</h5>
                <canvas id="testTrendChart" :height="200"></canvas>
              </div>
            </div>
          </div>
          <div class="preview-actions">
            <button class="btn-primary" @click="downloadCurrentReport">下载报告</button>
            <button class="btn-secondary" @click="editReport">编辑报告</button>
            <button class="btn-secondary" @click="closePreview">关闭预览</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在加载测试报告...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useTestStore } from '@/stores/test'
import { useRouter } from 'vue-router'
import type { TestReport, ReportForm, ReportFilters } from '@/types/test'
import { getTestReports, generateTestReport, deleteTestReport, getTestReportDetail } from '@/api/test'
import { formatTime, formatFileSize } from '@/utils/format'

const router = useRouter()
const testStore = useTestStore()

const reports = ref<TestReport[]>([])
const previewReport = ref<TestReport>({})
const showReportGenerator = ref<boolean>(false)
const showReportPreview = ref<boolean>(false)
const reportTypeFilter = ref<'all' | 'summary' | 'detailed' | 'performance' | 'coverage' | 'trend'>('all')
const isLoading = ref<boolean>(false)

const reportForm = reactive<ReportForm>({
  name: '',
  type: 'summary',
  timeRange: 'week',
  module: 'all',
  format: 'html',
  includeCharts: {
    summary: true,
    performance: true,
    coverage: true,
    trend: true
  }
})

const currentPage = ref<number>(1)
const totalPages = ref<number>(1)
const pageSize = ref<number>(20)

const paginatedReports = computed(() => {
  let filtered = reports.value
  
  if (reportTypeFilter.value !== 'all') {
    filtered = filtered.filter(report => report.type === reportTypeFilter.value)
  }
  
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filtered.slice(start, end)
})

const refreshReports = async () => {
  try {
    isLoading.value = true
    await loadReports()
  } catch (error) {
    console.error('Error refreshing reports:', error)
  } finally {
    isLoading.value = false
  }
}

const loadReports = async () => {
  try {
    const response = await getTestReports()
    
    if (response.code === 200 && response.data) {
      reports.value = response.data.data
      currentPage.value = 1
      totalPages.value = Math.ceil(response.data.data.length / pageSize.value)
    } else {
      console.error('Failed to load reports:', response.message)
    }
  } catch (error) {
    console.error('Error loading reports:', error)
    throw error
  }
}

const generateReport = () => {
  showReportGenerator.value = true
}

const toggleReportGenerator = () => {
  showReportGenerator.value = !showReportGenerator.value
}

const generateAndDownload = async () => {
  try {
    const response = await generateTestReport(reportForm)
    
    if (response.code === 200) {
      console.log('Test report generated successfully')
      await downloadReportFile(response.data.fileUrl, response.data.fileName)
      await loadReports()
      toggleReportGenerator()
    } else {
      console.error('Failed to generate report:', response.message)
    }
  } catch (error) {
    console.error('Error generating report:', error)
  }
}

const downloadReportFile = async (fileUrl: string, fileName: string) => {
  try {
    const link = document.createElement('a')
    link.href = imageUrl
    link.download = fileName
    link.click()
    console.log('Report file downloaded')
  } catch (error) {
    console.error('Error downloading report file:', error)
  }
}

const resetReportForm = () => {
  reportForm.name = ''
  reportForm.type = 'summary'
  reportForm.timeRange = 'week'
  reportForm.module = 'all'
  reportForm.format = 'html'
  reportForm.includeCharts = {
    summary: true,
    performance: true,
    coverage: true,
    trend: true
  }
}

const exportReport = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      filters: {
        reportType: reportTypeFilter.value
      },
      reports: paginatedReports.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `test_reports_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Test reports exported')
  } catch (error) {
    console.error('Error exporting reports:', error)
  }
}

const exportHistory = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      data: reports.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `test_reports_history_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Test reports history exported')
  } catch (error) {
    console.error('Error exporting history:', error)
  }
}

const viewReport = async (report: TestReport) => {
  try {
    const response = await getTestReportDetail(report.id)
    
    if (response.code === 200 && response.data) {
      previewReport.value = response.data.data
      showReportPreview.value = true
      
      await renderPreviewCharts(previewReport.value)
    } else {
      console.error('Failed to load report detail:', response.message)
    }
  } catch (error) {
    console.error('Error loading report detail:', error)
  }
}

const downloadReport = (report: TestReport) => {
  try {
    downloadReportFile(report.fileUrl, report.fileName)
  } catch (error) {
    console.error('Error downloading report:', error)
  }
}

const deleteReport = async (report: TestReport) => {
  try {
    if (confirm('确定要删除这个测试报告吗？')) {
      const response = await deleteTestReport(report.id)
      
      if (response.code === 200) {
        await loadReports()
        console.log('Test report deleted successfully')
      } else {
        console.error('Failed to delete report:', response.message)
      }
    }
  } catch (error) {
    console.error('Error deleting report:', error)
  }
}

const toggleReportPreview = () => {
  showReportPreview.value = !showReportPreview.value
}

const closePreview = () => {
  showReportPreview.value = false
}

const editReport = () => {
  if (previewReport.value.id) {
    router.push(`/test/reports/edit/${previewReport.value.id}`)
  }
}

const downloadCurrentReport = () => {
  if (previewReport.value.fileUrl) {
    downloadReportFile(previewReport.value.fileUrl, previewReport.value.fileName)
  }
}

const renderPreviewCharts = async (report: TestReport) => {
  try {
    await renderTestDistributionChart(report)
    await renderTestTrendChart(report)
  } catch (error) {
    console.error('Error rendering preview charts:', error)
  }
}

const renderTestDistributionChart = async (report: TestReport) => {
  try {
    const canvas = document.getElementById('testDistributionChart')
    
    if (!canvas || !report.distributionData) {
      return
    }
    
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 20
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    const data = report.distributionData
    const max = Math.max(...data.values)
    const total = data.values.reduce((sum, val) => sum + val, 0)
    
    if (max === 0) {
      return
    }
    
    const barWidth = chartWidth / data.values.length
    const barHeight = chartHeight / max
    
    const colors = ['#4caf50', '#f44336', '#ffc107', '#2196f3', '#9c27b0']
    
    for (let i = 0; i < data.values.length; i++) {
      const x = padding + i * barWidth
      const barHeightActual = data.values[i] / max * barHeight
      
      ctx.fillStyle = colors[i % colors.length]
      ctx.fillRect(x, padding + chartHeight - barHeightActual, barWidth * 0.8, barHeightActual)
      
      ctx.fillStyle = '#333'
      ctx.font = '12px Arial'
      ctx.textAlign = 'center'
      ctx.fillText(data.labels[i], x + barWidth * 0.4, padding + chartHeight - barHeightActual - 10)
      ctx.fillText(data.values[i].toString(), x + barWidth * 0.4, padding + chartHeight - barHeightActual + 20)
    }
  } catch (error) {
    console.error('Error rendering test distribution chart:', error)
  }
}

const renderTestTrendChart = async (report: TestReport) => {
  try {
    const canvas = document.getElementById('testTrendChart')
    
    if (!canvas || !report.trendData) {
      return
    }
    
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 20
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    const dates = report.trendData.dates || []
    const passRates = report.trendData.passRates || []
    const counts = report.trendData.counts || []
    
    if (dates.length < 2) {
      return
    }
    
    const x = padding
    const y = padding
    
    const stepX = chartWidth / (dates.length - 1)
    const stepY = chartHeight / 100
    
    ctx.strokeStyle = '#2196f3'
    ctx.lineWidth = 2
    ctx.beginPath()
    
    for (let i = 0; i < passRates.length; i++) {
      const normalizedValue = passRates[i] / 100
      const chartY = y + chartHeight / 2 - (normalizedValue * stepY)
      
      ctx.moveTo(x + i * stepX, chartY)
      ctx.lineTo(x + i * stepX, chartY)
    }
    
    ctx.stroke()
    
    ctx.fillStyle = 'rgba(33, 150, 243, 0.1)'
    ctx.fill()
    ctx.moveTo(x, y)
    ctx.lineTo(x + chartWidth, y)
    ctx.lineTo(x + chartWidth, y + chartHeight)
    ctx.lineTo(x, y + chartHeight)
    ctx.fill()
    
    // 绘制网格线
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.1)'
    ctx.lineWidth = 1
    
    for (let i = 0; i <= 5; i++) {
      const gridY = y + i * (chartHeight / 5)
      ctx.beginPath()
      ctx.moveTo(x, gridY)
      ctx.lineTo(x + chartWidth, gridY)
      ctx.stroke()
    }
  } catch (error) {
    console.error('Error rendering test trend chart:', error)
  }
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
}

const getSuccessRateClass = (rate: number) => {
  if (rate >= 80) return 'rate-excellent'
  if (rate >= 60) return 'rate-good'
  if (rate >= 40) return 'rate-fair'
  return 'rate-poor'
}

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  return date.toLocaleString()
}

const formatFileSize = (size: number) => {
  if (size >= 1024 * 1024) return (size / (1024 * 1024)).toFixed(2) + 'MB'
  if (size >= 1024) return (size / 1024).toFixed(2) + 'KB'
  return size + 'B'
}

onMounted(async () => {
  await loadReports()
  console.log('TestReport component mounted')
})
</script>

<style scoped lang="scss">
.test-report-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.test-report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.test-report-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.test-report-actions {
  display: flex;
  gap: 10px;
}

.btn-primary,
.btn-secondary,
.btn-view,
.btn-download,
.btn-delete {
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
  border-color: #2196f3;
}

.report-generation-section {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  width: 500px;
  max-height: 80vh;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.generator-card {
  width: 100%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.card-header {
  padding: 15px 20px;
  background: linear-gradient(135deg, #2196f3 0%, #374151 100%);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
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

.card-body {
  padding: 20px;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  margin-bottom: 8px;
  display: block;
}

.form-input,
.form-select {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 3px rgba(33, 150, 243, 0.2);
}

.checkbox-group {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: #333;
  font-weight: 500;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.report-list-section {
  margin-bottom: 20px;
}

.reports-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.reports-card .card-header {
  background: linear-gradient(135deg, #2196f3 0%, #374151 100%);
  color: white;
}

.reports-card .card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
}

.reports-card .card-header .reports-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 4px;
  font-size: 14px;
  background: rgba(0, 0, 0, 0.1);
  color: white;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: white;
}

.reports-card .card-header .btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.5);
  color: white;
}

.reports-card .card-header .btn-secondary:hover {
  background: rgba(255, 255, 255, 0.3);
}

.reports-table {
  width: 100%;
  border-collapse: collapse;
}

.reports-table th {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
  font-weight: bold;
  color: #333;
  font-size: 14px;
  background: #f9f9f9;
}

.reports-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.reports-table tbody tr:hover {
  background: #f5f7fa;
}

.report-name {
  font-weight: bold;
  color: #333;
}

.report-type {
  font-weight: 500;
  color: #666;
}

.report-time {
  color: #666;
  font-size: 14px;
}

.report-count {
  font-weight: 500;
  color: #333;
}

.report-rate {
  font-weight: bold;
}

.report-rate.rate-excellent {
  color: #4caf50;
}

.report-rate.rate-good {
  color: #81c784;
}

.report-rate.rate-fair {
  color: #ffc107;
}

.report-rate.rate-poor {
  color: #f44336;
}

.report-size {
  color: #666;
  font-size: 14px;
}

.report-actions {
  display: flex;
  gap: 5px;
}

.btn-view,
.btn-download,
.btn-delete {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-view {
  background: #2196f3;
  color: white;
}

.btn-view:hover {
  background: #1976d2;
}

.btn-download {
  background: #4caf50;
  color: white;
}

.btn-download:hover {
  background: #45a049;
}

.btn-delete {
  background: #f44336;
  color: white;
}

.btn-delete:hover {
  background: #da190b;
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

.report-preview-section {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  width: 80%;
  height: 100%;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.preview-card {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.preview-card .card-header {
  padding: 20px;
  background: linear-gradient(135deg, #2196f3 0%, #374151 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-card .card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
}

.preview-card .card-header .close-btn {
  background: transparent;
  border: none;
  color: white;
  font-size: 24px;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  transition: all 0.3s;
}

.preview-card .card-header .close-btn:hover {
  transform: scale(1.1);
}

.preview-card .card-body {
  padding: 20px;
  overflow-y: auto;
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.preview-header h4 {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.preview-type {
  font-size: 14px;
  color: #999;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 4px;
}

.preview-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.summary-item {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
  text-align: center;
}

.summary-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
  display: block;
  margin-bottom: 10px;
}

.summary-value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.summary-value.rate-excellent {
  color: #4caf50;
}

.summary-value.rate-good {
  color: #81c784;
}

.summary-value.rate-fair {
  color: #ffc107;
}

.summary-value.rate-poor {
  color: #f44336;
}

.preview-charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.chart-section {
  background: white;
  border: 1px solid #f0f0f0;
  border-radius: 4px;
  padding: 15px;
}

.chart-section h5 {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin: 0 0 15px 0;
}

.preview-actions {
  display: flex;
  gap: 10px;
  padding: 20px;
  background: #f5f7fa;
}

.preview-actions .btn-secondary {
  background: white;
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
  .report-list-section {
    overflow-x: auto;
  }
  
  .reports-table {
    font-size: 12px;
  }
  
  .report-actions {
    flex-wrap: wrap;
  }
}
</style>
