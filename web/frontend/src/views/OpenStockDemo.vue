<template>
  <div class="openstock-demo">

    <div class="page-header">
      <h1 class="page-title">OPENSTOCK DEMO</h1>
      <p class="page-subtitle">COMPONENT DEMONSTRATION | SEARCH | QUOTES | NEWS</p>

      <el-alert v-if="!isAuthenticated" type="warning" :closable="false" show-icon>
        Please log in to use the search functionality
        <el-button type="primary" size="small" @click="goToLogin" style="margin-top: 10px;">
          GO TO LOGIN
        </el-button>
      </el-alert>
    </div>

    <div class="function-nav">
      <el-button
        v-for="tab in tabs"
        :key="tab.key"
        :type="activeTab === tab.key ? 'primary' : 'default'"
        @click="activeTab = tab.key"
      >
        {{ tab.icon }} {{ tab.label }}
      </el-button>
    </div>

    <div class="demo-content">
      <StockSearch
        v-if="activeTab === 'search'"
        :is-authenticated="isAuthenticated"
        :groups="groups"
        @get-quote="handleGetQuote"
        @get-news="handleGetNews"
        @api-tested="handleApiTest"
      />

      <StockQuote
        v-if="activeTab === 'quote'"
        ref="stockQuoteRef"
        @api-tested="handleApiTest"
      />

      <StockNews
        v-if="activeTab === 'news'"
        ref="stockNewsRef"
        @api-tested="handleApiTest"
      />

      <WatchlistManagement
        v-if="activeTab === 'watchlist'"
        :groups="groups"
        @get-quote="handleGetQuote"
        @groups-changed="fetchGroups"
        @api-tested="handleApiTest"
      />

      <KlineChart
        v-if="activeTab === 'klinechart'"
        @api-tested="handleApiTest"
      />

      <HeatmapChart
        v-if="activeTab === 'heatmap'"
        @api-tested="handleApiTest"
      />

      <FeatureStatus
        v-if="activeTab === 'status'"
        ref="featureStatusRef"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, type Ref } from 'vue'
import { useRouter } from 'vue-router'
import { TABS, DEFAULT_API_STATUS, type ApiStatus } from './demo/openstock/config'
import {
  StockSearch,
  StockQuote,
  StockNews,
  WatchlistManagement,
  KlineChart,
  HeatmapChart,
  FeatureStatus
} from './demo/openstock/components'
import axios from 'axios'

const router = useRouter()

// API 基础地址
const API_BASE = '/api'

// 获取 token
const getToken = () => {
  return localStorage.getItem('token') || ''
}

// 认证状态检查
const isAuthenticated = computed(() => {
  const token = getToken()
  return token && token.length > 0
})

// 跳转到登录页
const goToLogin = () => {
  router.push('/login')
}

// Tab 切换
const activeTab = ref('search')
const tabs = TABS

// API 测试状态
const apiStatus = ref<ApiStatus>({ ...DEFAULT_API_STATUS })

// 组件引用
const stockQuoteRef: Ref<any> = ref(null)
const stockNewsRef: Ref<any> = ref(null)
const featureStatusRef: Ref<any> = ref(null)

// 分组数据（用于搜索组件的自动完成）
const groups = ref<any[]>([])

// 获取分组列表
const fetchGroups = async () => {
  try {
    const response = await axios.get(`${API_BASE}/watchlist/groups`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    groups.value = response.data
  } catch (error) {
    console.error('获取分组失败:', error)
  }
}

// 处理API测试事件
const handleApiTest = (feature: keyof ApiStatus) => {
  apiStatus.value[feature] = true
  if (featureStatusRef.value) {
    featureStatusRef.value.updateStatus(feature, true)
  }
}

// 处理获取行情
const handleGetQuote = (stock: any) => {
  activeTab.value = 'quote'
  if (stockQuoteRef.value) {
    stockQuoteRef.value.setQuote(stock.symbol, stock.market === 'CN' ? 'cn' : 'hk')
    stockQuoteRef.value.fetchQuote()
  }
}

// 处理获取新闻
const handleGetNews = (stock: any) => {
  activeTab.value = 'news'
  if (stockNewsRef.value) {
    stockNewsRef.value.setNews(stock.symbol, stock.market === 'CN' ? 'cn' : 'hk')
    stockNewsRef.value.fetchNews()
  }
}

// 页面加载时获取分组列表
onMounted(() => {
  fetchGroups()
})
</script>

<style scoped lang="scss">

  padding: var(--spacing-6);
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
  position: relative;
  background: var(--bg-primary);
}

  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.04;
  background-image:
    repeating-linear-gradient(
      45deg,
      var(--accent-gold) 0px,
      var(--accent-gold) 1px,
      transparent 1px,
      transparent 10px
    ),
    repeating-linear-gradient(
      -45deg,
      var(--accent-gold) 0px,
      var(--accent-gold) 1px,
      transparent 1px,
      transparent 10px
    );
}

.page-header {
  text-align: center;
  margin-bottom: var(--spacing-8);
  position: relative;
  z-index: 1;

  .page-title {
    font-family: var(--font-display);
    font-size: var(--font-size-h2);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-widest);
    color: var(--accent-gold);
    margin: 0 0 var(--spacing-2) 0;
  }

  .page-subtitle {
    font-family: var(--font-body);
    font-size: var(--font-size-small);
    color: var(--fg-muted);
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    margin: 0;
  }
}

  display: flex;
  gap: var(--spacing-3);
  margin-bottom: var(--spacing-6);
  flex-wrap: wrap;
  position: relative;
  z-index: 1;
}

.demo-content {
  position: relative;
  z-index: 1;
}

.demo-card {
  margin-bottom: var(--spacing-6);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-family: var(--font-display);
  font-size: var(--font-size-h4);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  color: var(--accent-gold);
}
</style>
