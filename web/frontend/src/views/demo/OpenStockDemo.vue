<template>

    <div class="page-header">
      <h1 class="page-title">OPENSTOCK</h1>
      <p class="page-subtitle">FEATURE DEMONSTRATION | INTEGRATION TESTING | MODULE SHOWCASE</p>
      <div class="decorative-line"></div>
    </div>

    <!-- 认证状态提示 -->
    <div class="card alert-card" v-if="!isAuthenticated">
      <div class="alert-content">
        <div class="alert-icon">⚠️</div>
        <div class="alert-text">
          <div class="alert-title">NOT LOGGED IN</div>
          <div class="alert-desc">Please login before using search features</div>
        </div>
          GO TO LOGIN
        </button>
      </div>
    </div>

    <!-- 功能导航 -->
    <div class="function-nav tabs-nav">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="btn"
        @click="activeTab = tab.key"
      >
        <span class="tab-icon">{{ tab.icon }}</span>
        <span class="tab-label">{{ tab.label }}</span>
      </button>
    </div>

    <!-- 组件内容 -->
    <div class="content-area">
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
import { TABS, DEFAULT_API_STATUS, type ApiStatus } from './openstock/config'
import {
  StockSearch,
  StockQuote,
  StockNews,
  WatchlistManagement,
  KlineChart,
  HeatmapChart,
  FeatureStatus
} from './openstock/components'
import axios from 'axios'

const router = useRouter()

const API_BASE = '/api'

const getToken = () => {
  return localStorage.getItem('token') || ''
}

const isAuthenticated = computed<boolean>(() => {
  const token = getToken()
  return !!(token && token.length > 0)
})

const goToLogin = () => {
  router.push('/login')
}

const activeTab = ref('search')
const tabs = TABS

const apiStatus = ref<ApiStatus>({ ...DEFAULT_API_STATUS })

const stockQuoteRef: Ref<any> = ref(null)
const stockNewsRef: Ref<any> = ref(null)
const featureStatusRef: Ref<any> = ref(null)

const groups = ref<any[]>([])

const fetchGroups = async () => {
  try {
    const response = await axios.get(`${API_BASE}/watchlist/groups`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    groups.value = response.data
  } catch (error) {
    console.error('Failed to fetch groups:', error)
  }
}

const handleApiTest = (feature: keyof ApiStatus) => {
  apiStatus.value[feature] = true
  if (featureStatusRef.value) {
    featureStatusRef.value.updateStatus(feature, true)
  }
}

const handleGetQuote = (stock: any) => {
  activeTab.value = 'quote'
  if (stockQuoteRef.value) {
    stockQuoteRef.value.setQuote(stock.symbol, stock.market === 'CN' ? 'cn' : 'hk')
    stockQuoteRef.value.fetchQuote()
  }
}

const handleGetNews = (stock: any) => {
  activeTab.value = 'news'
  if (stockNewsRef.value) {
    stockNewsRef.value.setNews(stock.symbol, stock.market === 'CN' ? 'cn' : 'hk')
    stockNewsRef.value.fetchNews()
  }
}

onMounted(() => {
  fetchGroups()
})
</script>

<style scoped lang="scss">

.openstock-demo {
  min-height: 100vh;
  padding: var(--spacing-6);
  background: var(--bg-primary);
  position: relative;
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
    repeating-linear-gradient(45deg, var(--accent-gold) 0px, var(--accent-gold) 1px, transparent 1px, transparent 10px),
    repeating-linear-gradient(-45deg, var(--accent-gold) 0px, var(--accent-gold) 1px, transparent 1px, transparent 10px);
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

  .decorative-line {
    width: 200px;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-gold), transparent);
    margin: var(--spacing-5) auto 0;
    position: relative;

    &::after {
      content: '';
      position: absolute;
      bottom: -8px;
      left: 50%;
      transform: translateX(-50%);
      width: 60px;
      height: 1px;
      background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.5), transparent);
    }
  }
}

.alert-card {
  position: relative;
  z-index: 1;
  margin-bottom: var(--spacing-6);
  background: rgba(230, 126, 34, 0.1);
  border: 1px solid rgba(230, 126, 34, 0.4);
}

.alert-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-4);
}

.alert-icon {
  font-size: 24px;
}

.alert-text {
  flex: 1;
}

.alert-title {
  font-family: var(--font-display);
  font-size: var(--font-size-body);
  color: #E67E22;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: var(--spacing-1);
}

.alert-desc {
  font-family: var(--font-body);
  font-size: var(--font-size-small);
  color: var(--fg-secondary);
}

.function-nav {
  display: flex;
  gap: var(--spacing-2);
  margin-bottom: var(--spacing-6);
  flex-wrap: wrap;
  position: relative;
  z-index: 1;
}

.content-area {
  position: relative;
  z-index: 1;
}

  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  padding: var(--spacing-3) var(--spacing-5);
  font-family: var(--font-display);
  font-size: var(--font-size-small);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  border: 2px solid var(--accent-gold);
  border-radius: 0;
  cursor: pointer;
  transition: all var(--transition-base);
}

  background: var(--accent-gold);
  color: var(--bg-primary);

  &:hover {
    background: var(--accent-gold-light);
    box-shadow: var(--glow-medium);
  }
}

  background: transparent;
  color: var(--accent-gold);

  &:hover {
    background: rgba(212, 175, 55, 0.1);
    box-shadow: var(--glow-subtle);
  }
}

.tab-icon {
  font-size: 14px;
}

.tab-label {
  font-size: var(--font-size-small);
}

@media (max-width: 768px) {
  .openstock-demo {
    padding: var(--spacing-4);
  }

  .function-nav {
    flex-direction: column;

      width: 100%;
    }
  }

  .alert-content {
    flex-direction: column;
    text-align: center;
  }
}
</style>
