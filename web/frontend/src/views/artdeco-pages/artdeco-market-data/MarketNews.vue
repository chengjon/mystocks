<template>
  <div class="market-news-container">
    <!-- 市场新闻主容器 -->
    <div class="market-news-header">
      <h2 class="market-news-title">市场新闻</h2>
      <div class="market-news-actions">
        <button class="btn-primary" @click="refreshNews">刷新新闻</button>
        <button class="btn-secondary" @click="toggleFilter" :class="{ active: showFilter }">
          筛选 {{ showFilter ? '收起' : '展开' }}
        </button>
        <button class="btn-secondary" @click="exportNews">导出新闻</button>
      </div>
    </div>

    <!-- 新闻筛选面板 -->
    <div class="news-filter-panel" v-if="showFilter">
      <div class="filter-card">
        <div class="filter-header">
          <h3>新闻筛选</h3>
          <button class="close-btn" @click="toggleFilter">×</button>
        </div>
        <div class="filter-body">
          <div class="filter-row">
            <div class="filter-item">
              <span class="filter-label">新闻类型</span>
              <select v-model="filters.newsType" class="filter-select">
                <option value="all">全部</option>
                <option value="market">市场</option>
                <option value="policy">政策</option>
                <option value="company">公司</option>
                <option value="sector">行业</option>
              </select>
            </div>
            <div class="filter-item">
              <span class="filter-label">时间范围</span>
              <select v-model="filters.timeRange" class="filter-select">
                <option value="today">今天</option>
                <option value="week">最近一周</option>
                <option value="month">最近一月</option>
                <option value="quarter">最近三月</option>
              </select>
            </div>
          </div>
          <div class="filter-row">
            <div class="filter-item">
              <span class="filter-label">关键词</span>
              <input type="text" v-model="filters.keyword" placeholder="输入关键词" class="search-input">
            </div>
            <div class="filter-item">
              <span class="filter-label">来源</span>
              <select v-model="filters.source" class="filter-select">
                <option value="all">全部</option>
                <option value="cs">中财网</option>
                <option value="wallstreet">华尔街</option>
                <option value="bloomberg">彭博</option>
                <option value="reuters">路透</option>
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

    <!-- 新闻列表 -->
    <div class="news-list">
      <div class="card news-card" v-for="news in filteredNews" :key="news.id">
        <div class="card-header">
          <span class="news-type" :class="getNewsTypeClass(news.type)">
            {{ getNewsTypeName(news.type) }}
          </span>
          <span class="news-source">{{ news.source }}</span>
          <span class="news-date">{{ formatNewsDate(news.date) }}</span>
        </div>
        <div class="card-body">
          <div class="news-title" @click="viewNewsDetail(news)">
            <span class="title-text">{{ news.title }}</span>
            <span class="title-tag" v-if="news.tag">{{ news.tag }}</span>
          </div>
          <div class="news-summary">
            <p class="summary-text">{{ news.summary }}</p>
          </div>
          <div class="news-content">
            <p class="content-text" v-if="news.content">{{ news.content }}</p>
            <p class="content-text" v-else>
              {{ news.summary }}... <span class="read-more" @click="viewNewsDetail(news)">点击查看详情</span>
            </p>
          </div>
          <div class="news-footer">
            <div class="news-actions">
              <button class="action-btn" @click="shareNews(news)" :class="{ shared: news.shared }">
                <span class="action-icon">{{ news.shared ? '🔗' : '📤' }}</span>
                <span class="action-label">{{ news.shared ? '已分享' : '分享' }}</span>
              </button>
              <button class="action-btn" @click="bookmarkNews(news)" :class="{ bookmarked: news.bookmarked }">
                <span class="action-icon">{{ news.bookmarked ? '⭐' : '☆' }}</span>
                <span class="action-label">{{ news.bookmarked ? '已收藏' : '收藏' }}</span>
              </button>
              <button class="action-btn" @click="likeNews(news)">
                <span class="action-icon">👍</span>
                <span class="action-label">{{ news.likes || 0 }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="news-pagination">
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

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在加载新闻...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useMarketStore } from '@/stores/market'
import { useRouter } from 'vue-router'
import type { MarketNews, NewsFilter } from '@/types/market'
import { getMarketNews, getNewsDetail } from '@/api/market'
import { formatNewsDate } from '@/utils/format'

const router = useRouter()
const marketStore = useMarketStore()

const allNews = ref<MarketNews[]>([])
const filteredNews = ref<MarketNews[]>([])
const showFilter = ref<boolean>(false)
const currentPage = ref<number>(1)
const totalPages = ref<number>(10)
const pageSize = ref<number>(20)
const isLoading = ref<boolean>(false)

const filters = reactive<NewsFilter>({
  newsType: 'all',
  timeRange: 'today',
  keyword: '',
  source: 'all'
})

const refreshNews = async () => {
  try {
    isLoading.value = true
    await loadNews()
  } catch (error) {
    console.error('Error refreshing news:', error)
  } finally {
    isLoading.value = false
  }
}

const loadNews = async () => {
  try {
    const response = await getMarketNews(filters)
    
    if (response.code === 200 && response.data) {
      allNews.value = response.data.data
      applyFilters()
    } else {
      console.error('Failed to load news:', response.message)
    }
  } catch (error) {
    console.error('Error loading news:', error)
    throw error
  }
}

const toggleFilter = () => {
  showFilter.value = !showFilter.value
}

const applyFilters = () => {
  let filtered = allNews.value
  
  if (filters.newsType !== 'all') {
    filtered = filtered.filter(news => news.type === filters.newsType)
  }
  
  if (filters.timeRange !== 'all') {
    const now = new Date()
    
    if (filters.timeRange === 'today') {
      filtered = filtered.filter(news => {
        const newsDate = new Date(news.date)
        return newsDate.toDateString() === now.toDateString()
      })
    } else if (filters.timeRange === 'week') {
      filtered = filtered.filter(news => {
        const newsDate = new Date(news.date)
        const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
        return newsDate >= weekAgo
      })
    } else if (filters.timeRange === 'month') {
      filtered = filtered.filter(news => {
        const newsDate = new Date(news.date)
        const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
        return newsDate >= monthAgo
      })
    }
  }
  
  if (filters.keyword.trim()) {
    const keyword = filters.keyword.toLowerCase()
    filtered = filtered.filter(news => 
      news.title.toLowerCase().includes(keyword) ||
      news.summary.toLowerCase().includes(keyword) ||
      news.content.toLowerCase().includes(keyword)
    )
  }
  
  if (filters.source !== 'all') {
    filtered = filtered.filter(news => news.source === filters.source)
  }
  
  filteredNews.value = filtered
  currentPage.value = 1
  totalPages.value = Math.ceil(filteredNews.value.length / pageSize.value)
}

const resetFilters = () => {
  filters.newsType = 'all'
  filters.timeRange = 'today'
  filters.keyword = ''
  filters.source = 'all'
  applyFilters()
  showFilter.value = false
}

const exportNews = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      filters: {
        newsType: filters.newsType,
        timeRange: filters.timeRange,
        keyword: filters.keyword,
        source: filters.source
      },
      data: filteredNews.value,
      totalCount: filteredNews.value.length
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `market_news_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('News report exported')
  } catch (error) {
    console.error('Error exporting news:', error)
  }
}

const viewNewsDetail = async (news: MarketNews) => {
  try {
    router.push(`/news/${news.id}`)
  } catch (error) {
    console.error('Error navigating to news detail:', error)
  }
}

const shareNews = (news: MarketNews) => {
  try {
    if (news.shared) {
      return
    }
    
    // 实现分享功能
    if (navigator.share) {
      navigator.share({
        title: news.title,
        text: news.summary,
        url: window.location.href
      })
    } else {
      console.log('Web Share API not supported')
    }
  } catch (error) {
    console.error('Error sharing news:', error)
  }
}

const bookmarkNews = (news: MarketNews) => {
  try {
    news.bookmarked = !news.bookmarked
    
    // 保存收藏到本地存储
    const bookmarks = JSON.parse(localStorage.getItem('news_bookmarks') || '[]')
    
    if (!news.bookmarked) {
      bookmarks.push(news.id)
    } else {
      const index = bookmarks.indexOf(news.id)
      if (index > -1) {
        bookmarks.splice(index, 1)
      }
    }
    
    localStorage.setItem('news_bookmarks', JSON.stringify(bookmarks))
    
  } catch (error) {
    console.error('Error bookmarking news:', error)
  }
}

const likeNews = (news: MarketNews) => {
  try {
    news.likes = (news.likes || 0) + 1
  } catch (error) {
    console.error('Error liking news:', error)
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
  totalPages.value = Math.ceil(filteredNews.value.length / newPageSize)
}

const getPaginatedNews = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredNews.value.slice(start, end)
})

const getNewsTypeClass = (type: string) => {
  if (type === 'market') return 'type-market'
  if (type === 'policy') return 'type-policy'
  if (type === 'company') return 'type-company'
  if (type === 'sector') return 'type-sector'
  return 'type-other'
}

const getNewsTypeName = (type: string) => {
  const names = {
    market: '市场',
    policy: '政策',
    company: '公司',
    sector: '行业'
    other: '其他'
  }
  return names[type] || '其他'
}

onMounted(async () => {
  await loadNews()
  console.log('MarketNews component mounted')
})
</script>

<style scoped lang="scss">
.market-news-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.market-news-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.market-news-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.market-news-actions {
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
  background: #1a1a1a;
  color: white;
}

.btn-primary:hover {
  background: #333;
}

.btn-secondary {
  background: transparent;
  color: #1a1a1a;
  border: 1px solid #1a1a1a;
}

.btn-secondary:hover {
  background: #f0f0f0;
  border-color: #333;
}

.btn-secondary.active {
  background: #1a1a1a;
  color: white;
}

.news-filter-panel {
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.filter-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: bold;
  color: white;
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
  gap: 20px;
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
  font-weight: 500;
  color: #666;
}

.filter-select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
}

.filter-select:focus {
  outline: none;
  border-color: #1a1a1a;
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
  border-color: #1a1a1a;
  box-shadow: 0 0 3px rgba(26, 26, 26, 0.2);
}

.filter-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.news-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.news-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card-header {
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.news-type {
  font-size: 14px;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.2);
}

.news-type.type-market {
  background: rgba(76, 175, 80, 0.2);
}

.news-type.type-policy {
  background: rgba(248, 113, 113, 0.2);
}

.news-type.type-company {
  background: rgba(38, 198, 218, 0.2);
}

.news-type.type-sector {
  background: rgba(251, 146, 60, 0.2);
}

.news-type.type-other {
  background: rgba(153, 102, 255, 0.2);
}

.news-source {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(0, 0, 0, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
}

.news-date {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
}

.card-body {
  padding: 20px;
}

.news-title {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.title-text {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  line-height: 1.4;
}

.title-tag {
  font-size: 12px;
  color: white;
  background: #ff5722;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.news-summary {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.summary-text {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
}

.news-content {
  margin-bottom: 20px;
}

.content-text {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
}

.read-more {
  color: #1a1a1a;
  font-weight: 500;
  cursor: pointer;
}

.news-footer {
  display: flex;
  gap: 10px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.news-actions {
  display: flex;
  gap: 10px;
  flex-grow: 1;
}

.action-btn {
  padding: 8px 16px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.action-btn:hover {
  border-color: #1a1a1a;
}

.action-btn.shared {
  background: #e8f5e9;
  border-color: #c51162;
}

.action-btn.bookmarked {
  background: #fff3cd;
  border-color: #fbbf24;
}

.action-icon {
  font-size: 18px;
}

.action-label {
  font-size: 14px;
  font-weight: 500;
  color: #666;
}

.news-pagination {
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
  border-color: #1a1a1a;
}

.page-btn:disabled {
  background: #f5f5f5;
  color: #ccc;
  cursor: not-allowed;
}

.page-info {
  font-size: 16px;
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
  border: 5px solid #1a1a1a;
  border-top-color: transparent;
  border-right-color: #1a1a1a;
  border-bottom-color: #1a1a1a;
  border-left-color: #1a1a1a;
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
  .news-list {
    grid-template-columns: 1fr;
  }
  
  .news-actions {
    flex-wrap: wrap;
  }
  
  .filter-row {
    flex-direction: column;
  }
}
</style>
