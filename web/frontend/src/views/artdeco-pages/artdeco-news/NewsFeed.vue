<template>
  <div class="news-feed-container">
    <!-- 新闻流主容器 -->
    <div class="news-feed-header">
      <h2 class="news-feed-title">新闻流</h2>
      <div class="news-feed-actions">
        <button class="btn-primary" @click="refreshFeed">刷新新闻</button>
        <button class="btn-secondary" @click="toggleFilter">筛选</button>
        <button class="btn-secondary" @click="exportFeed">导出</button>
      </div>
    </div>

    <!-- 新闻筛选面板 -->
    <div class="news-filter-section" v-if="showFilter">
      <div class="filter-card">
        <div class="filter-header">
          <h3>新闻筛选</h3>
          <button class="close-btn" @click="toggleFilter">×</button>
        </div>
        <div class="filter-body">
          <div class="filter-row">
            <div class="filter-item">
              <span class="filter-label">关键词</span>
              <input type="text" v-model="filters.keyword" placeholder="输入关键词" class="search-input">
            </div>
            <div class="filter-item">
              <span class="filter-label">分类</span>
              <select v-model="filters.category" class="filter-select">
                <option value="all">全部</option>
                <option value="market">市场</option>
                <option value="policy">政策</option>
                <option value="industry">行业</option>
                <option value="company">公司</option>
                <option value="international">国际</option>
              </select>
            </div>
          </div>
          <div class="filter-row">
            <div class="filter-item">
              <span class="filter-label">来源</span>
              <select v-model="filters.source" class="filter-select">
                <option value="all">全部</option>
                <option value="official">官方</option>
                <option value="media">媒体</option>
                <option value="social">社交</option>
              </select>
            </div>
            <div class="filter-item">
              <span class="filter-label">重要级别</span>
              <select v-model="filters.priority" class="filter-select">
                <option value="all">全部</option>
                <option value="high">重要</option>
                <option value="normal">一般</option>
                <option value="low">低</option>
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
    <div class="news-feed-list">
      <div class="card news-card" v-for="news in filteredNews" :key="news.id">
        <div class="card-header">
          <span class="news-category" :class="getCategoryClass(news.category)">
            {{ getCategoryName(news.category) }}
          </span>
          <span class="news-source" :class="getSourceClass(news.source)">
            {{ getSourceName(news.source) }}
          </span>
          <span class="news-priority" :class="getPriorityClass(news.priority)">
            {{ getPriorityName(news.priority) }}
          </span>
          <span class="news-time">{{ formatTime(news.publishTime) }}</span>
        </div>
        <div class="card-body">
          <div class="news-title">{{ news.title }}</div>
          <div class="news-summary">{{ news.summary }}</div>
          <div class="news-content">
            <div class="news-image" v-if="news.imageUrl">
              <img :src="news.imageUrl" :alt="news.title" class="news-image-img">
            </div>
            <div class="news-text">{{ news.content }}</div>
          </div>
          <div class="news-meta">
            <div class="meta-item">
              <span class="meta-label">阅读量</span>
              <span class="meta-value">{{ news.readCount }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">点赞数</span>
              <span class="meta-value">{{ news.likeCount }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">评论数</span>
              <span class="meta-value">{{ news.commentCount }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">分享数</span>
              <span class="meta-value">{{ news.shareCount }}</span>
            </div>
          </div>
          <div class="news-actions">
            <div class="action-buttons">
              <button class="btn-action" @click="readNews(news)">
                <span class="action-icon">👁</span>
                <span class="action-label">阅读</span>
              </button>
              <button class="btn-action" @click="likeNews(news)" :class="{ liked: news.isLiked }">
                <span class="action-icon">{{ news.isLiked ? '👍' : '👍' }}</span>
                <span class="action-label">{{ news.isLiked ? '已赞' : '赞' }}</span>
              </button>
              <button class="btn-action" @click="commentNews(news)">
                <span class="action-icon">💬</span>
                <span class="action-label">评论</span>
              </button>
              <button class="btn-action" @click="shareNews(news)">
                <span class="action-icon">🔗</span>
                <span class="action-label">分享</span>
              </button>
              <button class="btn-action" @click="bookmarkNews(news)" :class="{ bookmarked: news.isBookmarked }">
                <span class="action-icon">{{ news.isBookmarked ? '🔖' : '📌' }}</span>
                <span class="action-label">{{ news.isBookmarked ? '已收藏' : '收藏' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="feed-pagination">
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
import { useNewsStore } from '@/stores/news'
import { useRouter } from 'vue-router'
import type { News, NewsFilters } from '@/types/news'
import { getNewsFeed, likeNews, commentNews, shareNews, bookmarkNews } from '@/api/news'
import { formatTime, getCategoryName, getSourceName, getPriorityName } from '@/utils/format'

const router = useRouter()
const newsStore = useNewsStore()

const allNews = ref<News[]>([])
const showFilter = ref<boolean>(false)
const currentPage = ref<number>(1)
const totalPages = ref<number>(1)
const pageSize = ref<number>(20)
const isLoading = ref<boolean>(false)

const filters = reactive<NewsFilters>({
  keyword: '',
  category: 'all',
  source: 'all',
  priority: 'all'
})

const paginatedNews = computed(() => {
  return allNews.value
})

const refreshFeed = async () => {
  try {
    isLoading.value = true
    await loadNewsFeed()
  } catch (error) {
    console.error('Error refreshing feed:', error)
  } finally {
    isLoading.value = false
  }
}

const loadNewsFeed = async () => {
  try {
    const response = await getNewsFeed(filters)
    
    if (response.code === 200 && response.data) {
      allNews.value = response.data.data
      currentPage.value = 1
      totalPages.value = Math.ceil(response.data.total / pageSize.value)
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

const applyFilters = async () => {
  await loadNewsFeed()
  showFilter.value = false
}

const resetFilters = () => {
  filters.keyword = ''
  filters.category = 'all'
  filters.source = 'all'
  filters.priority = 'all'
  applyFilters()
}

const exportFeed = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      filters: {
        keyword: filters.keyword,
        category: filters.category,
        source: filters.source,
        priority: filters.priority
      },
      data: allNews.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `news_feed_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('News feed exported')
  } catch (error) {
    console.error('Error exporting news:', error)
  }
}

const readNews = (news: News) => {
  router.push(`/news/${news.id}`)
}

const likeNews = async (news: News) => {
  try {
    const response = await likeNews(news.id)
    
    if (response.code === 200) {
      news.isLiked = !news.isLiked
      news.likeCount += news.isLiked ? 1 : -1
      console.log('News liked successfully')
    } else {
      console.error('Failed to like news:', response.message)
    }
  } catch (error) {
    console.error('Error liking news:', error)
  }
}

const commentNews = (news: News) => {
  router.push(`/news/${news.id}#comments`)
}

const shareNews = async (news: News) => {
  try {
    const response = await shareNews(news.id)
    
    if (response.code === 200) {
      news.shareCount++
      console.log('News shared successfully')
      alert('分享链接已复制！')
    } else {
      console.error('Failed to share news:', response.message)
    }
  } catch (error) {
    console.error('Error sharing news:', error)
    alert('分享失败：' + error)
  }
}

const bookmarkNews = async (news: News) => {
  try {
    const response = await bookmarkNews(news.id)
    
    if (response.code === 200) {
      news.isBookmarked = !news.isBookmarked
      console.log('News bookmarked successfully')
    } else {
      console.error('Failed to bookmark news:', response.message)
    }
  } catch (error) {
    console.error('Error bookmarking news:', error)
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    loadNewsFeed()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadNewsFeed()
  }
}

const changePageSize = (newSize: number) => {
  pageSize.value = newSize
  currentPage.value = 1
  loadNewsFeed()
}

const getCategoryClass = (category: string) => {
  if (category === 'market') return 'category-market'
  if (category === 'policy') return 'category-policy'
  if (category === 'industry') return 'category-industry'
  if (category === 'company') return 'category-company'
  if (category === 'international') return 'category-international'
  return 'category-unknown'
}

const getSourceClass = (source: string) => {
  if (source === 'official') return 'source-official'
  if (source === 'media') return 'source-media'
  if (source === 'social') return 'source-social'
  return 'source-unknown'
}

const getPriorityClass = (priority: string) => {
  if (priority === 'high') return 'priority-high'
  if (priority === 'normal') return 'priority-normal'
  if (priority === 'low') return 'priority-low'
  return 'priority-unknown'
}

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  return date.toLocaleString()
}

onMounted(async () => {
  await loadNewsFeed()
  console.log('NewsFeed component mounted')
})
</script>

<style scoped lang="scss">
.news-feed-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.news-feed-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.news-feed-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.news-feed-actions {
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

.news-filter-section {
  position: fixed;
  top: 0;
  left: 0;
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
  background: linear-gradient(135deg, #2196f3 0%, #374151 100%);
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
  border-color: #2196f3;
  box-shadow: 0 0 3px rgba(33, 150, 243, 0.2);
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
  border-color: #2196f3;
}

.filter-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.news-feed-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
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
}

.news-category {
  font-size: 14px;
  color: white;
  background: #2196f3;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.news-category.category-market {
  background: #4caf50;
}

.news-category.category-policy {
  background: #ff9800;
}

.news-category.category-industry {
  background: #9c27b0;
}

.news-category.category-company {
  background: #f44336;
}

.news-category.category-international {
  background: #3f51b5;
}

.news-source {
  font-size: 14px;
  color: #666;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 4px;
  margin-left: 10px;
  font-weight: 500;
}

.news-source.source-official {
  color: #2196f3;
}

.news-source.source-media {
  color: #4caf50;
}

.news-source.source-social {
  color: #ff9800;
}

.news-priority {
  font-size: 14px;
  color: white;
  background: #e0e0e0;
  padding: 4px 8px;
  border-radius: 4px;
  margin-left: 10px;
  font-weight: 500;
}

.news-priority.priority-high {
  background: #f44336;
}

.news-priority.priority-normal {
  background: #2196f3;
}

.news-priority.priority-low {
  background: #9e9e9e;
}

.news-time {
  font-size: 14px;
  color: #999;
  margin-left: 10px;
  font-weight: 500;
}

.card-body {
  padding: 20px;
}

.news-title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
}

.news-summary {
  font-size: 16px;
  color: #666;
  margin-bottom: 15px;
  line-height: 1.5;
}

.news-content {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.news-image {
  width: 200px;
  flex-shrink: 0;
}

.news-image-img {
  width: 100%;
  height: auto;
  border-radius: 8px;
  object-fit: cover;
}

.news-text {
  flex: 1;
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
  margin-bottom: 20px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.meta-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
}

.meta-value {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.news-actions {
  margin-top: 20px;
  padding-top: 20px;
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
  border-color: #2196f3;
  transform: translateY(-2px);
}

.btn-action.liked {
  background: #e3f2fd;
  border-color: #2196f3;
}

.btn-action.bookmarked {
  background: #fff7e6;
  border-color: #ffc107;
}

.action-icon {
  font-size: 20px;
}

.action-label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.feed-pagination {
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
  .news-content {
    flex-direction: column;
  }
  
  .news-image {
    width: 100%;
  }
  
  .news-meta {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .action-buttons {
    flex-wrap: wrap;
  }
}
</style>
