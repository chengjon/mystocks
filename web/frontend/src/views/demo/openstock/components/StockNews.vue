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
import axios, { type AxiosError } from 'axios'

interface NewsItem {
  datetime: number
  headline: string
  summary: string
  source: string
  url?: string
}

const emit = defineEmits<{
  'api-tested': [feature: string]
}>()

const newsSymbol = ref('')
const newsMarket = ref('cn')
const newsDays = ref(7)
const newsList = ref<NewsItem[]>([])
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
  } catch (error: unknown) {
    const apiError = error as AxiosError<{ detail?: string }>
    ElMessage.error('获取新闻失败: ' + (apiError.response?.data?.detail || apiError.message))
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
@use '../../../../styles/artdeco-tokens.scss' as *;

.news-section {
  padding: var(--artdeco-spacing-3) 0;
}

.controls-row {
  display: flex;
  gap: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
  align-items: flex-end;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: calc(var(--artdeco-spacing-2) - (var(--artdeco-spacing-px) * 2));
  min-width: calc(var(--artdeco-spacing-20) + var(--artdeco-spacing-10) + var(--artdeco-spacing-5));

  .input-label {
    color: var(--artdeco-fg-muted);
    font-size: calc(var(--artdeco-text-sm) - var(--artdeco-spacing-px));
    font-weight: var(--artdeco-font-medium);
  }
}

.input,
.select {
  padding: calc(var(--artdeco-spacing-5) / 2) calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);
  background: var(--artdeco-bg-global);
  color: var(--artdeco-fg-primary);
  font-size: var(--artdeco-text-sm);
  transition: border-color var(--artdeco-transition-quick) var(--artdeco-ease-out);

  &:focus {
    outline: none;
    border-color: var(--artdeco-gold-primary);
  }
}

.input::placeholder {
  color: var(--artdeco-fg-muted);
}

.select {
  cursor: pointer;
}

.news-list {
  margin-top: var(--artdeco-spacing-5);
}

.timeline {
  position: relative;
  padding-left: calc(var(--artdeco-spacing-5) + var(--artdeco-spacing-2) + (var(--artdeco-spacing-px) * 2));

  &::before {
    content: '';
    position: absolute;
    top: 0;
    bottom: 0;
    left: calc(var(--artdeco-spacing-2) - (var(--artdeco-spacing-px) * 2));
    width: calc(var(--artdeco-spacing-px) * 2);
    background: color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  }
}

.timeline-item {
  position: relative;
  padding-bottom: var(--artdeco-spacing-6);

  &:last-child {
    padding-bottom: 0;
  }
}

.timeline-marker {
  position: absolute;
  top: 0;
  left: calc((var(--artdeco-spacing-5) + var(--artdeco-spacing-2) + (var(--artdeco-spacing-px) * 2)) * -1);
  width: calc(var(--artdeco-spacing-3) + (var(--artdeco-spacing-px) * 2));
  height: calc(var(--artdeco-spacing-3) + (var(--artdeco-spacing-px) * 2));
  background: var(--artdeco-gold-primary);
  border: calc(var(--artdeco-spacing-px) * 3) solid var(--artdeco-bg-global);
  border-radius: var(--artdeco-radius-full);
}

.timeline-content {
  padding-left: calc(var(--artdeco-spacing-2) + (var(--artdeco-spacing-px) * 2));
}

.timeline-time {
  margin-bottom: var(--artdeco-spacing-2);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-xs);
}

.news-card {
  padding: var(--artdeco-spacing-4);
  background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);

  h4 {
    margin: 0 0 calc(var(--artdeco-spacing-2) + (var(--artdeco-spacing-px) * 2)) 0;
    color: var(--artdeco-fg-primary);
    font-size: calc(var(--artdeco-text-sm) + var(--artdeco-spacing-px));
    font-weight: var(--artdeco-font-semibold);
    line-height: 1.4;
  }

  p {
    margin: 0 0 var(--artdeco-spacing-3) 0;
    color: var(--artdeco-fg-muted);
    font-size: calc(var(--artdeco-text-sm) - var(--artdeco-spacing-px));
    line-height: 1.6;
  }
}

.news-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.news-link {
  color: var(--artdeco-gold-primary);
  font-size: calc(var(--artdeco-text-sm) - var(--artdeco-spacing-px));
  font-weight: var(--artdeco-font-medium);
  text-decoration: none;

  &:hover {
    text-decoration: underline;
  }
}

.loading-spinner {
  display: inline-block;
  width: var(--artdeco-spacing-4);
  height: var(--artdeco-spacing-4);
  margin-right: var(--artdeco-spacing-2);
  border: calc(var(--artdeco-spacing-px) * 2) solid color-mix(in srgb, var(--artdeco-fg-primary) 30%, transparent);
  border-top-color: var(--artdeco-fg-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
