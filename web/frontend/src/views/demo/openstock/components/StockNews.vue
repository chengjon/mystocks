<template>
  <div class="card demo-card">
    <div class="card-header">
      <span class="card-title">📰 股票新闻</span>
      <span class="badge badge-success">已迁移</span>
    </div>

    <div class="news-section">
      <div class="controls-row">
        <div class="input-group">
          <span class="input-label">代码</span>
          <input v-model="newsSymbol" type="text" class="input" placeholder="输入股票代码" />
        </div>
        <div class="input-group">
          <span class="input-label">市场</span>
          <select v-model="newsMarket" class="select">
            <option value="cn">A股</option>
            <option value="hk">H股</option>
          </select>
        </div>
        <div class="input-group">
          <span class="input-label">时间范围</span>
          <select v-model="newsDays" class="select">
            <option :value="3">最近3天</option>
            <option :value="7">最近7天</option>
            <option :value="15">最近15天</option>
          </select>
        </div>
        <button class="btn btn-primary" @click="fetchNews" :disabled="newsLoading">
          <span v-if="newsLoading" class="loading-spinner"></span>
          {{ newsLoading ? '查询中...' : '查询新闻' }}
        </button>
      </div>

      <div v-if="newsList.length > 0" class="news-list">
        <div class="timeline">
          <div v-for="(news, index) in newsList" :key="index" class="timeline-item">
            <div class="timeline-marker"></div>
            <div class="timeline-content">
              <div class="timeline-time">{{ formatTime(news.datetime) }}</div>
              <div class="news-card">
                <h4>{{ news.headline }}</h4>
                <p>{{ news.summary }}</p>
                <div class="news-footer">
                  <span class="badge badge-info">{{ news.source }}</span>
                  <a v-if="news.url" :href="news.url" target="_blank" class="news-link">
                    阅读原文 →
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const emit = defineEmits<{
  'api-tested': [feature: string]
}>()

const newsSymbol = ref('')
const newsMarket = ref('cn')
const newsDays = ref(7)
const newsList = ref<any[]>([])
const newsLoading = ref(false)

const fetchNews = async () => {
  if (!newsSymbol.value.trim()) {
    ElMessage.warning('请输入股票代码')
    return
  }

  newsLoading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const API_BASE = '/api'

    const response = await axios.get(
      `${API_BASE}/stock-search/news/${newsSymbol.value}`,
      {
        params: { market: newsMarket.value, days: newsDays.value },
        headers: { Authorization: `Bearer ${token}` }
      }
    )
    newsList.value = response.data
    emit('api-tested', 'news')
    ElMessage.success(`获取到 ${response.data.length} 条新闻`)
  } catch (error: any) {
    ElMessage.error('获取新闻失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    newsLoading.value = false
  }
}

const formatTime = (timestamp: number) => {
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN')
}

defineExpose({
  fetchNews,
  setNews: (symbol: string, market: string) => {
    newsSymbol.value = symbol
    newsMarket.value = market
  }
})
</script>

<style scoped lang="scss">

.news-section {
  padding: 10px 0;
}

.controls-row {
  display: flex;
  gap: 15px;
  align-items: flex-end;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 140px;

  .input-label {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-secondary);
  }
}

.input {
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-primary);
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: var(--primary);
  }
}

.select {
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-primary);
  cursor: pointer;
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: var(--primary);
  }
}

.news-list {
  margin-top: 20px;
}

.timeline {
  position: relative;
  padding-left: 30px;

  &::before {
    content: '';
    position: absolute;
    left: 6px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: var(--border-light);
  }
}

.timeline-item {
  position: relative;
  padding-bottom: 24px;

  &:last-child {
    padding-bottom: 0;
  }
}

.timeline-marker {
  position: absolute;
  left: -30px;
  top: 0;
  width: 14px;
  height: 14px;
  background: var(--primary);
  border-radius: 50%;
  border: 3px solid var(--bg-primary);
}

.timeline-content {
  padding-left: 10px;
}

.timeline-time {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.news-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 16px;

  h4 {
    margin: 0 0 10px 0;
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
    line-height: 1.4;
  }

  p {
    margin: 0 0 12px 0;
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.6;
  }
}

.news-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.news-link {
  font-size: 13px;
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;

  &:hover {
    text-decoration: underline;
  }
}

.loading-spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
