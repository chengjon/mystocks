<template>
  <div class="news-analysis-container">
    <!-- 新闻分析主容器 -->
    <div class="news-analysis-header">
      <h2 class="news-analysis-title">新闻分析</h2>
      <div class="news-analysis-actions">
        <button class="btn-primary" @click="refreshAnalysis">刷新分析</button>
        <button class="btn-secondary" @click="generateReport">生成报告</button>
        <button class="btn-secondary" @click="exportAnalysis">导出数据</button>
      </div>
    </div>

    <!-- 分析概览 -->
    <div class="analysis-overview-section">
      <div class="card overview-card">
        <div class="card-header">
          <span class="overview-title">分析概览</span>
          <span class="overview-period">今日</span>
        </div>
        <div class="card-body">
          <div class="overview-stats-grid">
            <div class="overview-stat-item">
              <span class="stat-label">总新闻</span>
              <span class="stat-value">{{ totalNews }}</span>
            </div>
            <div class="overview-stat-item">
              <span class="stat-label">已分析</span>
              <span class="stat-value">{{ analyzedNews }}</span>
            </div>
            <div class="overview-stat-item">
              <span class="stat-label">待分析</span>
              <span class="stat-value">{{ pendingAnalysis }}</span>
            </div>
            <div class="overview-stat-item">
              <span class="stat-label">分析进度</span>
              <span class="stat-value" :class="getProgressClass(analysisProgress)">
                {{ analysisProgress }}%
              </span>
            </div>
          </div>
          <div class="overview-progress-bar">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: analysisProgress + '%' }"></div>
            </div>
            <div class="progress-text">{{ analysisProgress }}% 完成</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新闻分类分析 -->
    <div class="news-category-analysis-section">
      <div class="card category-analysis-card">
        <div class="card-header">
          <h3>新闻分类分析</h3>
          <div class="chart-actions">
            <select v-model="categoryPeriod" class="period-select">
              <option value="day">日</option>
              <option value="week">周</option>
              <option value="month">月</option>
            </select>
            <button class="btn-secondary" @click="exportCategoryAnalysis">导出</button>
          </div>
        </div>
        <div class="card-body">
          <div class="category-analysis-grid">
            <div class="category-analysis-item" v-for="category in categoryAnalysis" :key="category.name">
              <div class="category-name">{{ category.name }}</div>
              <div class="category-stats">
                <div class="category-stat">
                  <span class="category-stat-label">新闻数</span>
                  <span class="category-stat-value">{{ category.newsCount }}</span>
                </div>
                <div class="category-stat">
                  <span class="category-stat-label">占比</span>
                  <span class="category-stat-value" :class="getPercentClass(category.percent)">
                    {{ category.percent }}%
                  </span>
                </div>
                <div class="category-stat">
                  <span class="category-stat-label">趋势</span>
                  <span class="category-stat-value" :class="getTrendClass(category.trend)">
                    {{ getTrendName(category.trend) }}
                  </span>
                </div>
              </div>
              <div class="category-chart">
                <canvas :id="`category-chart-${category.code}`" :height="150"></canvas>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 情感分析 -->
    <div class="sentiment-analysis-section">
      <div class="card sentiment-analysis-card">
        <div class="card-header">
          <h3>情感分析</h3>
        </div>
        <div class="card-body">
          <div class="sentiment-overview">
            <div class="sentiment-gauge">
              <canvas id="sentimentGauge" :height="200"></canvas>
              <div class="sentiment-label">整体情感</div>
              <div class="sentiment-score" :class="getSentimentClass(overallSentiment.score)">
                {{ overallSentiment.score }}
              </div>
              <div class="sentiment-label">{{ getSentimentLabel(overallSentiment.label) }}</div>
            </div>
          </div>
          <div class="sentiment-details">
            <div class="sentiment-item" v-for="sentiment in sentimentAnalysis" :key="sentiment.type">
              <div class="sentiment-type" :class="getSentimentTypeClass(sentiment.type)">
                {{ getSentimentTypeName(sentiment.type) }}
              </div>
              <div class="sentiment-stats">
                <div class="sentiment-stat">
                  <span class="stat-label">数量</span>
                  <span class="stat-value">{{ sentiment.count }}</span>
                </div>
                <div class="sentiment-stat">
                  <span class="stat-label">占比</span>
                  <span class="stat-value" :class="getPercentClass(sentiment.percent)">
                    {{ sentiment.percent }}%
                  </span>
                </div>
                <div class="sentiment-stat">
                  <span class="stat-label">强度</span>
                  <span class="stat-value" :class="getIntensityClass(sentiment.intensity)">
                    {{ sentiment.intensity }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 关键词分析 -->
    <div class="keywords-analysis-section">
      <div class="card keywords-analysis-card">
        <div class="card-header">
          <h3>关键词分析</h3>
        </div>
        <div class="card-body">
          <div class="keywords-list">
            <div class="keyword-item" v-for="keyword in keywords" :key="keyword.word">
              <div class="keyword-word">{{ keyword.word }}</div>
              <div class="keyword-stats">
                <div class="keyword-stat">
                  <span class="stat-label">出现次数</span>
                  <span class="stat-value">{{ keyword.count }}</span>
                </div>
                <div class="keyword-stat">
                  <span class="stat-label">占比</span>
                  <span class="stat-value" :class="getPercentClass(keyword.percent)">
                    {{ keyword.percent }}%
                  </span>
                </div>
                <div class="keyword-stat">
                  <span class="stat-label">趋势</span>
                  <span class="stat-value" :class="getTrendClass(keyword.trend)">
                    {{ getTrendName(keyword.trend) }}
                  </span>
                </div>
              </div>
              <div class="keyword-chart">
                <canvas :id="`keyword-chart-${keyword.word}`" :height="50"></canvas>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 热点分析 -->
    <div class="hot-topics-section">
      <div class="card hot-topics-card">
        <div class="card-header">
          <h3>热点话题</h3>
          <div class="topics-actions">
            <select v-model="topicsPeriod" class="period-select">
              <option value="day">日</option>
              <option value="week">周</option>
              <option value="month">月</option>
            </select>
            <button class="btn-secondary" @click="exportHotTopics">导出</button>
          </div>
        </div>
        <div class="card-body">
          <div class="topics-list">
            <div class="topic-item" v-for="topic in hotTopics" :key="topic.id">
              <div class="topic-rank">{{ topic.rank }}</div>
              <div class="topic-info">
                <div class="topic-name">{{ topic.name }}</div>
                <div class="topic-keywords">{{ topic.keywords.join('、') }}</div>
                <div class="topic-meta">
                  <span class="topic-count">{{ topic.newsCount }}条新闻</span>
                  <span class="topic-reads">{{ topic.readCount }}阅读</span>
                </div>
              </div>
              <div class="topic-trend" :class="getTrendClass(topic.trend)">
                {{ getTrendIcon(topic.trend) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在加载新闻分析...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useNewsStore } from '@/stores/news'
import { useRouter } from 'vue-router'
import type { NewsAnalysis, CategoryAnalysis, SentimentAnalysis, Keyword, HotTopic } from '@/types/news'
import { getNewsAnalysis, generateNewsAnalysisReport, exportNewsAnalysisData } from '@/api/news'
import { formatTime, getTrendName, getTrendIcon } from '@/utils/format'

const router = useRouter()
const newsStore = useNewsStore()

const totalNews = ref<number>(0)
const analyzedNews = ref<number>(0)
const pendingAnalysis = ref<number>(0)
const analysisProgress = ref<number>(0)

const categoryAnalysis = ref<CategoryAnalysis[]>([])
const sentimentAnalysis = ref<SentimentAnalysis[]>([])
const overallSentiment = ref({ score: 0, label: '' })
const keywords = ref<Keyword[]>([])
const hotTopics = ref<HotTopic[]>([])

const categoryPeriod = ref<'day' | 'week' | 'month'>('day')
const topicsPeriod = ref<'day' | 'week' | 'month'>('day')

const isLoading = ref<boolean>(false)

const refreshAnalysis = async () => {
  try {
    isLoading.value = true
    await Promise.all([
      loadAnalysisOverview(),
      loadCategoryAnalysis(),
      loadSentimentAnalysis(),
      loadKeywordsAnalysis(),
      loadHotTopicsAnalysis()
    ])
  } catch (error) {
    console.error('Error refreshing analysis:', error)
  } finally {
    isLoading.value = false
  }
}

const loadAnalysisOverview = async () => {
  try {
    const response = await getNewsAnalysis()
    
    if (response.code === 200 && response.data) {
      const overview = response.data.data
      
      totalNews.value = overview.totalNews
      analyzedNews.value = overview.analyzedNews
      pendingAnalysis.value = overview.pendingAnalysis
      analysisProgress.value = overview.analysisProgress
      
      await renderSentimentGauge(overview.overallSentiment)
    } else {
      console.error('Failed to load analysis overview:', response.message)
    }
  } catch (error) {
    console.error('Error loading analysis overview:', error)
    throw error
  }
}

const loadCategoryAnalysis = async () => {
  try {
    const response = await getNewsAnalysis({ type: 'category', period: categoryPeriod.value })
    
    if (response.code === 200 && response.data) {
      categoryAnalysis.value = response.data.data
      await renderAllCategoryCharts(response.data.data)
    } else {
      console.error('Failed to load category analysis:', response.message)
    }
  } catch (error) {
    console.error('Error loading category analysis:', error)
    throw error
  }
}

const loadSentimentAnalysis = async () => {
  try {
    const response = await getNewsAnalysis({ type: 'sentiment' })
    
    if (response.code === 200 && response.data) {
      sentimentAnalysis.value = response.data.data
    } else {
      console.error('Failed to load sentiment analysis:', response.message)
    }
  } catch (error) {
    console.error('Error loading sentiment analysis:', error)
    throw error
  }
}

const loadKeywordsAnalysis = async () => {
  try {
    const response = await getNewsAnalysis({ type: 'keywords' })
    
    if (response.code === 200 && response.data) {
      keywords.value = response.data.data
      await renderAllKeywordCharts(response.data.data)
    } else {
      console.error('Failed to load keywords analysis:', response.message)
    }
  } catch (error) {
    console.error('Error loading keywords analysis:', error)
    throw error
  }
}

const loadHotTopicsAnalysis = async () => {
  try {
    const response = await getNewsAnalysis({ type: 'hotTopics', period: topicsPeriod.value })
    
    if (response.code === 200 && response.data) {
      hotTopics.value = response.data.data
    } else {
      console.error('Failed to load hot topics analysis:', response.message)
    }
  } catch (error) {
    console.error('Error loading hot topics analysis:', error)
    throw error
  }
}

const renderSentimentGauge = async (sentiment: any) => {
  try {
    const canvas = document.getElementById('sentimentGauge')
    
    if (!canvas) {
      return
    }
    
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 30
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    const centerX = padding + chartWidth / 2
    const centerY = padding + chartHeight / 2
    const radius = Math.min(chartWidth, chartHeight) / 2
    
    const score = sentiment.score || 0
    const startAngle = -Math.PI / 2
    const endAngle = startAngle + (score / 100) * Math.PI
    
    ctx.beginPath()
    ctx.arc(centerX, centerY, radius, startAngle, endAngle)
    ctx.lineWidth = 20
    ctx.strokeStyle = getSentimentColor(score)
    ctx.stroke()
    
    ctx.font = 'bold 24px Arial'
    ctx.fillStyle = '#333'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(score.toFixed(0), centerX, centerY)
  } catch (error) {
    console.error('Error rendering sentiment gauge:', error)
  }
}

const renderAllCategoryCharts = async (categories: CategoryAnalysis[]) => {
  for (const category of categories) {
    const canvas = document.getElementById(`category-chart-${category.code}`)
    if (canvas) {
      await renderCategoryChart(canvas, category)
    }
  }
}

const renderCategoryChart = async (canvas: HTMLCanvasElement, category: CategoryAnalysis) => {
  try {
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 10
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    const values = category.trendValues || []
    
    if (values.length < 2) {
      return
    }
    
    const max = Math.max(...values)
    const min = Math.min(...values)
    const range = max - min
    
    if (range === 0) {
      return
    }
    
    const stepX = chartWidth / (values.length - 1)
    const stepY = chartHeight / range
    
    ctx.strokeStyle = category.trend === 'up' ? '#4caf50' : category.trend === 'down' ? '#f44336' : '#999'
    ctx.lineWidth = 2
    ctx.beginPath()
    
    for (let i = 0; i < values.length; i++) {
      const x = padding + i * stepX
      const normalizedValue = (values[i] - min) / range * chartHeight
      const y = padding + chartHeight / 2 - (normalizedValue * stepY)
      
      ctx.moveTo(x, y)
      ctx.lineTo(x, y)
    }
    
    ctx.stroke()
  } catch (error) {
    console.error('Error rendering category chart:', error)
  }
}

const renderAllKeywordCharts = async (keywords: Keyword[]) => {
  for (const keyword of keywords) {
    const canvas = document.getElementById(`keyword-chart-${keyword.word}`)
    if (canvas) {
      await renderKeywordChart(canvas, keyword)
    }
  }
}

const renderKeywordChart = async (canvas: HTMLCanvasElement, keyword: Keyword) => {
  try {
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const padding = 5
    const chartWidth = canvas.width - padding * 2
    const chartHeight = canvas.height - padding * 2
    
    const values = keyword.trendValues || []
    
    if (values.length < 2) {
      return
    }
    
    const max = Math.max(...values)
    const min = Math.min(...values)
    const range = max - min
    
    if (range === 0) {
      return
    }
    
    const stepX = chartWidth / (values.length - 1)
    const stepY = chartHeight / range
    
    ctx.strokeStyle = keyword.trend === 'up' ? '#ef4444' : keyword.trend === 'down' ? '#22c55e' : '#999'
    ctx.lineWidth = 2
    ctx.beginPath()
    
    for (let i = 0; i < values.length; i++) {
      const x = padding + i * stepX
      const normalizedValue = (values[i] - min) / range * chartHeight
      const y = padding + chartHeight / 2 - (normalizedValue * stepY)
      
      ctx.moveTo(x, y)
      ctx.lineTo(x, y)
    }
    
    ctx.stroke()
  } catch (error) {
    console.error('Error rendering keyword chart:', error)
  }
}

const generateReport = async () => {
  try {
    const response = await generateNewsAnalysisReport()
    
    if (response.code === 200) {
      console.log('News analysis report generated successfully')
      alert('新闻分析报告已生成！')
    } else {
      console.error('Failed to generate report:', response.message)
      alert('生成报告失败：' + response.message)
    }
  } catch (error) {
    console.error('Error generating report:', error)
    alert('生成报告失败：' + error)
  }
}

const exportAnalysis = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      overview: {
        totalNews: totalNews.value,
        analyzedNews: analyzedNews.value,
        pendingAnalysis: pendingAnalysis.value,
        analysisProgress: analysisProgress.value
      },
      categoryAnalysis: categoryAnalysis.value,
      sentimentAnalysis: sentimentAnalysis.value,
      keywords: keywords.value,
      hotTopics: hotTopics.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `news_analysis_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('News analysis data exported')
  } catch (error) {
    console.error('Error exporting analysis:', error)
  }
}

const exportCategoryAnalysis = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      period: categoryPeriod.value,
      data: categoryAnalysis.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `category_analysis_${categoryPeriod.value}_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Category analysis exported')
  } catch (error) {
    console.error('Error exporting category analysis:', error)
  }
}

const exportHotTopics = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      period: topicsPeriod.value,
      data: hotTopics.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `hot_topics_${topicsPeriod.value}_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Hot topics exported')
  } catch (error) {
    console.error('Error exporting hot topics:', error)
  }
}

const getSentimentColor = (score: number) => {
  if (score >= 60) return '#4caf50'
  if (score >= 40) return '#ff9800'
  if (score >= 20) return '#f44336'
  return '#9e9e9e'
}

const getSentimentClass = (score: number) => {
  if (score >= 60) return 'sentiment-positive'
  if (score >= 40) return 'sentiment-neutral'
  if (score >= 20) return 'sentiment-negative'
  return 'sentiment-unknown'
}

const getSentimentLabel = (label: string) => {
  const labels = {
    positive: '正面',
    neutral: '中性',
    negative: '负面',
    unknown: '未知'
  }
  return labels[label] || '未知'
}

const getSentimentTypeClass = (type: string) => {
  if (type === 'positive') return 'type-positive'
  if (type === 'neutral') return 'type-neutral'
  if (type === 'negative') return 'type-negative'
  return 'type-unknown'
}

const getSentimentTypeName = (type: string) => {
  const names = {
    positive: '正面',
    neutral: '中性',
    negative: '负面',
    unknown: '未知'
  }
  return names[type] || '未知'
}

const getIntensityClass = (intensity: string) => {
  if (intensity === 'high') return 'intensity-high'
  if (intensity === 'medium') return 'intensity-medium'
  if (intensity === 'low') return 'intensity-low'
  return 'intensity-unknown'
}

const getPercentClass = (percent: number) => {
  if (percent >= 50) return 'percent-high'
  if (percent >= 30) return 'percent-medium'
  if (percent >= 10) return 'percent-low'
  return 'percent-unknown'
}

const getTrendClass = (trend: string) => {
  if (trend === 'up') return 'trend-up'
  if (trend === 'down') return 'trend-down'
  return 'trend-unknown'
}

const getTrendName = (trend: string) => {
  const names = {
    up: '上升',
    down: '下降',
    unknown: '未知'
  }
  return names[trend] || '未知'
}

const getTrendIcon = (trend: string) => {
  const icons = {
    up: '📈',
    down: '📉',
    unknown: '➖'
  }
  return icons[trend] || '➖'
}

const getProgressClass = (progress: number) => {
  if (progress >= 80) return 'progress-excellent'
  if (progress >= 60) return 'progress-good'
  if (progress >= 40) return 'progress-fair'
  return 'progress-poor'
}

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  return date.toLocaleString()
}

onMounted(async () => {
  await refreshAnalysis()
  console.log('NewsAnalysis component mounted')
})
</script>

<style scoped lang="scss">
.news-analysis-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.news-analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.news-analysis-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.news-analysis-actions {
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
  border-color: #2196f3;
}

.analysis-overview-section {
  margin-bottom: 20px;
}

.overview-card {
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

.overview-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.overview-period {
  font-size: 14px;
  color: #999;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 4px;
}

.card-body {
  padding: 20px;
}

.overview-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.overview-stat-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.stat-value.progress-excellent {
  color: #4caf50;
}

.stat-value.progress-good {
  color: #81c784;
}

.stat-value.progress-fair {
  color: #ffc107;
}

.stat-value.progress-poor {
  color: #f44336;
}

.overview-progress-bar {
  margin-top: 20px;
}

.progress-bar {
  width: 100%;
  height: 10px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #2196f3 0%, #374151 100%);
  transition: width 0.3s;
}

.progress-text {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  text-align: center;
}

.news-category-analysis-section,
.sentiment-analysis-section,
.keywords-analysis-section,
.hot-topics-section {
  margin-bottom: 20px;
}

.category-analysis-card,
.sentiment-analysis-card,
.keywords-analysis-card,
.hot-topics-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.chart-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.period-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.category-analysis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.category-analysis-item {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 15px;
}

.category-name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
}

.category-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 10px;
}

.category-stat {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.category-stat-label {
  font-size: 12px;
  color: #999;
  font-weight: 500;
}

.category-stat-value {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.category-stat-value.percent-high {
  color: #4caf50;
}

.category-stat-value.percent-medium {
  color: #81c784;
}

.category-stat-value.percent-low {
  color: #ffc107;
}

.category-stat-value.trend-up {
  color: #4caf50;
}

.category-stat-value.trend-down {
  color: #f44336;
}

.category-chart {
  margin-top: 10px;
}

.sentiment-overview {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.sentiment-gauge {
  position: relative;
  width: 200px;
  height: 200px;
  margin-bottom: 15px;
}

.sentiment-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  text-align: center;
}

.sentiment-score {
  font-size: 36px;
  font-weight: bold;
  color: #333;
  text-align: center;
}

.sentiment-score.sentiment-positive {
  color: #4caf50;
}

.sentiment-score.sentiment-negative {
  color: #f44336;
}

.sentiment-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.sentiment-item {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sentiment-type {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.sentiment-type.type-positive {
  color: #4caf50;
}

.sentiment-type.type-neutral {
  color: #999;
}

.sentiment-type.type-negative {
  color: #f44336;
}

.sentiment-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.sentiment-stat {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.sentiment-stat .stat-label {
  font-size: 12px;
  color: #999;
  font-weight: 500;
}

.sentiment-stat .stat-value {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.sentiment-stat .stat-value.percent-high {
  color: #4caf50;
}

.sentiment-stat .stat-value.percent-medium {
  color: #81c784;
}

.sentiment-stat .stat-value.percent-low {
  color: #ffc107;
}

.sentiment-stat .stat-value.trend-up {
  color: #4caf50;
}

.sentiment-stat .stat-value.trend-down {
  color: #f44336;
}

.sentiment-stat .stat-value.intensity-high {
  color: #ef4444;
}

.sentiment-stat .stat-value.intensity-medium {
  color: #ffc107;
}

.sentiment-stat .stat-value.intensity-low {
  color: #22c55e;
}

.keywords-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.keyword-item {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 15px;
}

.keyword-word {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
}

.keyword-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 10px;
}

.keyword-stat {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.keyword-stat .stat-label {
  font-size: 12px;
  color: #999;
  font-weight: 500;
}

.keyword-stat .stat-value {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.keyword-stat .stat-value.percent-high {
  color: #4caf50;
}

.keyword-stat .stat-value.trend-up {
  color: #ef4444;
}

.keyword-stat .stat-value.trend-down {
  color: #22c55e;
}

.keyword-chart {
  margin-top: 10px;
}

.topics-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.topic-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.topic-rank {
  font-size: 24px;
  font-weight: bold;
  color: #2196f3;
  width: 40px;
  text-align: center;
  flex-shrink: 0;
}

.topic-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.topic-name {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.topic-keywords {
  font-size: 14px;
  color: #666;
}

.topic-meta {
  display: flex;
  gap: 15px;
}

.topic-count,
.topic-reads {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.topic-trend {
  font-size: 32px;
  width: 40px;
  text-align: center;
  flex-shrink: 0;
}

.topic-trend.trend-up {
  color: #4caf50;
}

.topic-trend.trend-down {
  color: #f44336;
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
  .category-analysis-grid,
  .sentiment-details,
  .keywords-list {
    grid-template-columns: 1fr;
  }
}
</style>
