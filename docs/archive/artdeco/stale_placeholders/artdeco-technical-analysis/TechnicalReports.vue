<template>
  <div class="technical-reports-container">
    <!-- 技术报告主容器 -->
    <div class="technical-reports-header">
      <h2 class="technical-reports-title">技术报告</h2>
      <div class="technical-reports-actions">
        <button class="btn-primary" @click="refreshReports">刷新报告</button>
        <button class="btn-secondary" @click="generateReport">生成报告</button>
        <button class="btn-secondary" @click="exportReports">导出报告</button>
      </div>
    </div>

    <!-- 报告列表 -->
    <div class="reports-list">
      <div class="card report-card" v-for="report in reports" :key="report.id">
        <div class="card-header" :class="getReportTypeClass(report.type)">
          <span class="report-name">{{ report.name }}</span>
          <span class="report-type">{{ report.type }}</span>
          <span class="report-date">{{ formatTime(report.generatedAt) }}</span>
        </div>
        <div class="card-body">
          <div class="report-summary">
            <div class="summary-item">
              <span class="summary-label">报告类型</span>
              <span class="summary-value">{{ report.type }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">生成时间</span>
              <span class="summary-value">{{ formatTime(report.generatedAt) }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">股票代码</span>
              <span class="summary-value">{{ report.stockCode }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">时间周期</span>
              <span class="summary-value">{{ report.timePeriod }}</span>
            </div>
          </div>
          <div class="report-content">
            <canvas :id="`report-chart-${report.id}`" :height="200"></canvas>
          </div>
          <div class="report-actions">
            <button class="btn-action" @click="viewReportDetail(report)">
              <span class="action-icon">📊</span>
              <span class="action-label">查看详情</span>
            </button>
            <button class="btn-action" @click="downloadReport(report)">
              <span class="action-icon">📥</span>
              <span class="action-label">下载</span>
            </button>
            <button class="btn-action" @click="deleteReport(report)">
              <span class="action-icon">🗑️</span>
              <span class="action-label">删除</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 生成报告面板 -->
    <div class="generate-report-panel" v-if="showGenerateReport">
      <div class="card generator-card">
        <div class="card-header">
          <h3>生成技术报告</h3>
          <button class="close-btn" @click="toggleGenerateReport">×</button>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label class="form-label">报告类型</label>
            <select v-model="reportForm.type" class="form-select">
              <option value="indicator">指标分析</option>
              <option value="signal">信号分析</option>
              <option value="trend">趋势分析</option>
              <option value="comprehensive">综合分析</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">股票代码</label>
            <input type="text" v-model="reportForm.stockCode" placeholder="输入股票代码" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">时间周期</label>
            <select v-model="reportForm.timePeriod" class="form-select">
              <option value="day">日</option>
              <option value="week">周</option>
              <option value="month">月</option>
              <option value="quarter">季</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">分析指标</label>
            <div class="indicator-checkboxes">
              <label class="checkbox-label">
                <input type="checkbox" v-model="reportForm.indicators.MA" checked>
                MA 移动平均
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="reportForm.indicators.EMA">
                EMA 指数平均
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="reportForm.indicators.MACD">
                MACD 指标
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="reportForm.indicators.RSI">
                RSI 相对强弱指标
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="reportForm.indicators.BOLLINGER">
                BOLLINGER 布林带
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="reportForm.indicators.KDJ">
                KDJ 随机指标
              </label>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">包含图表</label>
            <div class="chart-checkboxes">
              <label class="checkbox-label">
                <input type="checkbox" v-model="reportForm.charts.price"> 价格走势
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="reportForm.charts.volume"> 成交量
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="reportForm.charts.indicator"> 指标叠加
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="reportForm.charts.signal"> 信号标记
              </label>
            </div>
          </div>
          <div class="form-actions">
            <button class="btn-primary" @click="generateAndSave">生成报告</button>
            <button class="btn-secondary" @click="resetReportForm">重置</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 报告详情模态框 -->
    <div class="modal" v-if="showReportDetail" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>技术报告详情</h3>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-section">
            <div class="detail-section-title">基本信息</div>
            <div class="detail-section-body">
              <div class="detail-row">
                <span class="detail-label">报告名称</span>
                <span class="detail-value">{{ selectedReport.name }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">报告类型</span>
                <span class="detail-value">{{ selectedReport.type }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">股票代码</span>
                <span class="detail-value">{{ selectedReport.stockCode }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">时间周期</span>
                <span class="detail-value">{{ selectedReport.timePeriod }}</span>
              </div>
            </div>
          </div>
          <div class="detail-section">
            <div class="detail-section-title">指标分析</div>
            <div class="detail-section-body">
              <div class="detail-row" v-for="(indicator, index) in selectedReport.indicators" :key="index">
                <span class="detail-label">{{ indicator.name }}</span>
                <span class="detail-value" :class="getIndicatorValueClass(indicator.value)">
                  {{ formatValue(indicator.value) }}
                </span>
                <span class="detail-trend" :class="getIndicatorTrendClass(indicator.trend)">
                  {{ indicator.trend }}
                </span>
                <span class="detail-signal" :class="getIndicatorSignalClass(indicator.signal)">
                  {{ indicator.signal }}
                </span>
              </div>
            </div>
          </div>
          <div class="detail-section">
            <div class="detail-section-title">图表分析</div>
            <div class="detail-section-body">
              <canvas id="detailChart" :height="300"></canvas>
            </div>
          </div>
          <div class="detail-section">
            <div class="detail-section-title">投资建议</div>
            <div class="detail-section-body">
              <div class="recommendation">
                <span class="recommendation-label">操作建议</span>
                <span class="recommendation-value" :class="getRecommendationClass(selectedReport.recommendation)">
                  {{ selectedReport.recommendation }}
                </span>
              </div>
              <div class="recommendation">
                <span class="recommendation-label">风险评估</span>
                <span class="recommendation-value" :class="getRiskClass(selectedReport.risk)">
                  {{ selectedReport.risk }}
                </span>
              </div>
              <div class="recommendation">
                <span class="recommendation-label">预期收益</span>
                <span class="recommendation-value">{{ selectedReport.expectedReturn }}</span>
              </div>
              <div class="recommendation">
                <span class="recommendation-label">建议周期</span>
                <span class="recommendation-value">{{ selectedReport.holdingPeriod }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-primary" @click="downloadCurrentReport">下载报告</button>
          <button class="btn-secondary" @click="closeModal">关闭</button>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在加载技术报告...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useMarketStore } from '@/stores/market'
import { useRouter } from 'vue-router'
import type { TechnicalReport, ReportForm, IndicatorAnalysis } from '@/types/market'
import { getTechnicalReports, generateTechnicalReport, deleteTechnicalReport, getTechnicalReportDetail } from '@/api/market'
import { formatTime, formatValue } from '@/utils/format'

const router = useRouter()
const marketStore = useMarketStore()

const reports = ref<TechnicalReport[]>([])
const selectedReport = ref<TechnicalReport>({})
const showGenerateReport = ref<boolean>(false)
const showReportDetail = ref<boolean>(false)
const isLoading = ref<boolean>(false)

const reportForm = reactive<ReportForm>({
  type: 'comprehensive',
  stockCode: '',
  timePeriod: 'day',
  indicators: {
    MA: true,
    EMA: false,
    MACD: true,
    RSI: true,
    BOLLINGER: true,
    KDJ: false
  },
  charts: {
    price: true,
    volume: true,
    indicator: true,
    signal: true
  }
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
    const response = await getTechnicalReports()
    
    if (response.code === 200 && response.data) {
      reports.value = response.data.data
      await renderAllReportCharts(response.data.data)
    } else {
      console.error('Failed to load reports:', response.message)
    }
  } catch (error) {
    console.error('Error loading reports:', error)
    throw error
  }
}

const renderAllReportCharts = async (reports: TechnicalReport[]) => {
  for (const report of reports) {
    const canvas = document.getElementById(`report-chart-${report.id}`)
    if (canvas) {
      await renderReportChart(canvas, report)
    }
  }
}

const renderReportChart = async (canvas: HTMLCanvasElement, report: TechnicalReport) => {
  try {
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 10
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    const prices = report.chartData.prices || []
    const volumes = report.chartData.volumes || []
    
    if (prices.length < 2) {
      return
    }
    
    const max = Math.max(...prices)
    const min = Math.min(...prices)
    const range = max - min
    
    if (range === 0) {
      return
    }
    
    const stepX = chartWidth / (prices.length - 1)
    const stepY = chartHeight / range
    
    ctx.strokeStyle = '#ef4444'
    ctx.lineWidth = 2
    ctx.beginPath()
    
    for (let i = 0; i < prices.length; i++) {
      const x = padding + i * stepX
      const normalizedValue = (prices[i] - min) / range * chartHeight
      const y = padding + chartHeight - normalizedValue
      
      ctx.moveTo(x, y)
      ctx.lineTo(x, y)
    }
    
    ctx.stroke()
    
    ctx.fillStyle = 'rgba(239, 68, 68, 0.1)'
    ctx.fill()
    ctx.moveTo(padding, padding)
    ctx.lineTo(padding + chartWidth, padding)
    ctx.lineTo(padding + chartWidth, padding + chartHeight)
    ctx.lineTo(padding, padding + chartHeight)
    ctx.fill()
  } catch (error) {
    console.error('Error rendering report chart:', error)
  }
}

const generateReport = () => {
  showGenerateReport.value = true
}

const toggleGenerateReport = () => {
  showGenerateReport.value = !showGenerateReport.value
}

const generateAndSave = async () => {
  try {
    const response = await generateTechnicalReport(reportForm)
    
    if (response.code === 200) {
      await loadReports()
      toggleGenerateReport()
      console.log('Technical report generated successfully')
    } else {
      console.error('Failed to generate report:', response.message)
    }
  } catch (error) {
    console.error('Error generating report:', error)
  }
}

const resetReportForm = () => {
  reportForm.type = 'comprehensive'
  reportForm.stockCode = ''
  reportForm.timePeriod = 'day'
  reportForm.indicators = {
    MA: true,
    EMA: false,
    MACD: true,
    RSI: true,
    BOLLINGER: true,
    KDJ: false
  }
  reportForm.charts = {
    price: true,
    volume: true,
    indicator: true,
    signal: true
  }
}

const exportReports = () => {
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
    link.download = `technical_reports_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Technical reports exported')
  } catch (error) {
    console.error('Error exporting reports:', error)
  }
}

const viewReportDetail = async (report: TechnicalReport) => {
  try {
    const response = await getTechnicalReportDetail(report.id)
    
    if (response.code === 200 && response.data) {
      selectedReport.value = response.data.data
      showReportDetail.value = true
      await renderDetailChart(response.data.data)
    } else {
      console.error('Failed to load report detail:', response.message)
    }
  } catch (error) {
    console.error('Error loading report detail:', error)
  }
}

const closeModal = () => {
  showReportDetail.value = false
}

const renderDetailChart = async (report: TechnicalReport) => {
  try {
    const canvas = document.getElementById('detailChart')
    
    if (!canvas) {
      return
    }
    
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 20
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    const prices = report.chartData.prices || []
    const volumes = report.chartData.volumes || []
    
    if (prices.length < 2) {
      return
    }
    
    const max = Math.max(...prices)
    const min = Math.min(...prices)
    const range = max - min
    
    if (range === 0) {
      return
    }
    
    const stepX = chartWidth / (prices.length - 1)
    const stepY = chartHeight / range
    
    ctx.strokeStyle = '#2196f3'
    ctx.lineWidth = 2
    ctx.beginPath()
    
    for (let i = 0; i < prices.length; i++) {
      const x = padding + i * stepX
      const normalizedValue = (prices[i] - min) / range * chartHeight
      const y = padding + chartHeight - normalizedValue
      
      ctx.moveTo(x, y)
      ctx.lineTo(x, y)
    }
    
    ctx.stroke()
    
    ctx.fillStyle = 'rgba(33, 150, 243, 0.1)'
    ctx.fill()
    ctx.moveTo(padding, padding)
    ctx.lineTo(padding + chartWidth, padding)
    ctx.lineTo(padding + chartWidth, padding + chartHeight)
    ctx.lineTo(padding, padding + chartHeight)
    ctx.fill()
  } catch (error) {
    console.error('Error rendering detail chart:', error)
  }
}

const downloadReport = (report: TechnicalReport) => {
  try {
    const link = document.createElement('a')
    link.href = report.fileUrl
    link.download = report.fileName
    link.click()
    
    console.log('Report downloaded')
  } catch (error) {
    console.error('Error downloading report:', error)
  }
}

const downloadCurrentReport = () => {
  downloadReport(selectedReport.value)
}

const deleteReport = async (report: TechnicalReport) => {
  try {
    if (confirm('确定要删除这个技术报告吗？')) {
      const response = await deleteTechnicalReport(report.id)
      
      if (response.code === 200) {
        await loadReports()
        console.log('Report deleted successfully')
      } else {
        console.error('Failed to delete report:', response.message)
      }
    }
  } catch (error) {
    console.error('Error deleting report:', error)
  }
}

const getReportTypeClass = (type: string) => {
  if (type === 'indicator') return 'type-indicator'
  if (type === 'signal') return 'type-signal'
  if (type === 'trend') return 'type-trend'
  if (type === 'comprehensive') return 'type-comprehensive'
  return 'type-unknown'
}

const getIndicatorValueClass = (value: number) => {
  if (value > 0) return 'value-up'
  if (value < 0) return 'value-down'
  return 'value-neutral'
}

const getIndicatorTrendClass = (trend: string) => {
  if (trend === 'up') return 'trend-up'
  if (trend === 'down') return 'trend-down'
  if (trend === 'sideways') return 'trend-sideways'
  return 'trend-unknown'
}

const getIndicatorSignalClass = (signal: string) => {
  if (signal === 'buy') return 'signal-buy'
  if (signal === 'sell') return 'signal-sell'
  if (signal === 'hold') return 'signal-hold'
  return 'signal-unknown'
}

const getRecommendationClass = (recommendation: string) => {
  if (recommendation === 'buy') return 'recommendation-buy'
  if (recommendation === 'sell') return 'recommendation-sell'
  if (recommendation === 'hold') return 'recommendation-hold'
  return 'recommendation-unknown'
}

const getRiskClass = (risk: string) => {
  if (risk === 'low') return 'risk-low'
  if (risk === 'medium') return 'risk-medium'
  if (risk === 'high') return 'risk-high'
  return 'risk-unknown'
}

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  return date.toLocaleString()
}

const formatValue = (value: number) => {
  if (value >= 1000) return (value / 1000).toFixed(2)
  return value.toFixed(2)
}

onMounted(async () => {
  await loadReports()
  console.log('TechnicalReports component mounted')
})
</script>

<style scoped lang="scss">
.technical-reports-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.technical-reports-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.technical-reports-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.technical-reports-actions {
  display: flex;
  gap: 10px;
}

.btn-primary,
.btn-secondary,
.btn-action {
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

.reports-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.report-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.report-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.card-header {
  padding: 15px 20px;
  background: linear-gradient(135deg, #2196f3 0%, #374151 100%);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header.type-indicator {
  background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
}

.card-header.type-signal {
  background: linear-gradient(135deg, #ef4444 0%, #dc3545 100%);
}

.card-header.type-trend {
  background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
}

.card-header.type-comprehensive {
  background: linear-gradient(135deg, #4caf50 0%, #1b5e20 100%);
}

.card-header.type-unknown {
  background: linear-gradient(135deg, #e0e0e0 0%, #9e9e9e 100%);
}

.report-name {
  font-size: 18px;
  font-weight: bold;
  color: white;
  flex: 1;
}

.report-type {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(0, 0, 0, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
  margin-left: 10px;
}

.report-date {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  margin-left: 10px;
}

.card-body {
  padding: 20px;
}

.report-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.summary-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
}

.summary-value {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.report-content {
  margin-bottom: 20px;
}

.report-actions {
  display: flex;
  gap: 10px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
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
  border-color: #2196f3;
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

.generate-report-panel {
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
  display: block;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 3px rgba(33, 150, 243, 0.2);
}

.form-select {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.form-select:focus {
  outline: none;
  border-color: #2196f3;
}

.indicator-checkboxes {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.chart-checkboxes {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
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
  width: 800px;
  max-height: 80vh;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 20px;
  background: linear-gradient(135deg, #2196f3 0%, #374151 100%);
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

.modal-header .close-btn {
  background: transparent;
  border: none;
  color: white;
  font-size: 24px;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  transition: all 0.3s;
}

.modal-header .close-btn:hover {
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
  border-bottom: 2px solid #2196f3;
}

.detail-section-body {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.detail-row {
  display: flex;
  flex-direction: column;
  gap: 5px;
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

.detail-value.value-up {
  color: #ef4444;
}

.detail-value.value-down {
  color: #22c55e;
}

.detail-value.value-neutral {
  color: #666;
}

.detail-trend.trend-up {
  color: #ef4444;
}

.detail-trend.trend-down {
  color: #22c55e;
}

.detail-trend.trend-sideways {
  color: #ffc107;
}

.detail-trend.trend-unknown {
  color: #999;
}

.detail-signal.signal-buy {
  color: #ef4444;
}

.detail-signal.signal-sell {
  color: #22c55e;
}

.detail-signal.signal-hold {
  color: #ffc107;
}

.detail-signal.signal-unknown {
  color: #999;
}

.recommendation {
  padding: 10px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.recommendation-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  display: block;
  margin-bottom: 8px;
}

.recommendation-value {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.recommendation-value.recommendation-buy {
  color: #ef4444;
}

.recommendation-value.recommendation-sell {
  color: #22c55e;
}

.recommendation-value.recommendation-hold {
  color: #ffc107;
}

.recommendation-value.recommendation-unknown {
  color: #999;
}

.recommendation-value.risk-low {
  color: #4caf50;
}

.recommendation-value.risk-medium {
  color: #ffc107;
}

.recommendation-value.risk-high {
  color: #ff9800;
}

.recommendation-value.risk-unknown {
  color: #999;
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
  .reports-list {
    grid-template-columns: 1fr;
  }
  
  .indicator-checkboxes,
  .chart-checkboxes {
    grid-template-columns: 1fr;
  }
  
  .detail-section-body {
    grid-template-columns: 1fr;
  }
}
</style>
