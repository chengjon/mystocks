<template>
  <div class="openstock-demo">

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
        <button class="btn btn-primary" @click="_goToLogin">
          GO TO LOGIN
        </button>
      </div>
    </div>

    <!-- 功能导航 -->
    <div class="function-nav tabs-nav">
      <button
        v-for="(tab, _idx) in tabs"
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

const _goToLogin = () => {
  router.push('/login')
}

const activeTab = ref('search')
const tabs = TABS

const apiStatus = ref<ApiStatus>({ ...DEFAULT_API_STATUS })

interface StockRef {
  setQuote?: (symbol: string, market: string) => void
  fetchQuote?: () => void
  setNews?: (symbol: string, market: string) => void
  fetchNews?: () => void
  updateStatus?: (feature: string, status: boolean) => void
}

interface StockInfo {
  symbol: string
  market: string
}

const stockQuoteRef: Ref<StockRef | null> = ref(null)
const stockNewsRef: Ref<StockRef | null> = ref(null)
const featureStatusRef: Ref<StockRef | null> = ref(null)

const groups = ref<unknown[]>([])

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
    featureStatusRef.value.updateStatus?.(feature, true)
  }
}

const handleGetQuote = (stock: StockInfo) => {
  activeTab.value = 'quote'
  if (stockQuoteRef.value) {
    stockQuoteRef.value.setQuote?.(stock.symbol, stock.market === 'CN' ? 'cn' : 'hk')
    stockQuoteRef.value.fetchQuote?.()
  }
}

const handleGetNews = (stock: StockInfo) => {
  activeTab.value = 'news'
  if (stockNewsRef.value) {
    stockNewsRef.value.setNews?.(stock.symbol, stock.market === 'CN' ? 'cn' : 'hk')
    stockNewsRef.value.fetchNews?.()
  }
}

onMounted(() => {
  fetchGroups()
})
</script>

<style scoped lang="scss">
@use '../../styles/artdeco-tokens.scss' as *;

.openstock-demo {
  min-height: 100vh;
  padding: var(--artdeco-spacing-6);
  position: relative;
  background: var(--artdeco-bg-global);
  background-image:
    linear-gradient(180deg, color-mix(in srgb, var(--artdeco-gold-primary) 6%, transparent), transparent 40%),
    repeating-linear-gradient(
      45deg,
      transparent,
      transparent var(--artdeco-spacing-5),
      var(--artdeco-gold-opacity-05) var(--artdeco-spacing-5),
      var(--artdeco-gold-opacity-05) calc(var(--artdeco-spacing-5) + var(--artdeco-spacing-px))
    );
}

.page-header,
.alert-card,
.function-nav,
.content-area {
  position: relative;
  z-index: 1;
}

.page-header {
  text-align: center;
  margin-bottom: var(--artdeco-spacing-8);
}

.page-title {
  margin: 0 0 var(--artdeco-spacing-2) 0;
  color: var(--artdeco-gold-primary);
  font-family: var(--artdeco-font-heading, var(--font-display));
  font-size: var(--artdeco-text-3xl);
  font-weight: var(--artdeco-font-semibold);
  letter-spacing: var(--artdeco-tracking-widest);
  text-transform: uppercase;
}

.page-subtitle {
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-body, var(--font-body));
  font-size: var(--artdeco-text-xs);
  letter-spacing: var(--artdeco-tracking-wider);
  text-transform: uppercase;
}

.decorative-line {
  width: calc(var(--artdeco-spacing-20) * 2);
  height: calc(var(--artdeco-spacing-px) * 2);
  margin: var(--artdeco-spacing-5) auto 0;
  position: relative;
  background: linear-gradient(90deg, transparent, var(--artdeco-gold-primary), transparent);

  &::after {
    content: '';
    position: absolute;
    bottom: calc(var(--artdeco-spacing-2) * -1);
    left: 50%;
    transform: translateX(-50%);
    width: calc(var(--artdeco-spacing-20) - var(--artdeco-spacing-5));
    height: var(--artdeco-spacing-px);
    background: linear-gradient(90deg, transparent, color-mix(in srgb, var(--artdeco-gold-primary) 50%, transparent), transparent);
  }
}

.alert-card {
  margin-bottom: var(--artdeco-spacing-6);
  background: color-mix(in srgb, var(--artdeco-warning) 10%, var(--artdeco-bg-card));
  border: 1px solid color-mix(in srgb, var(--artdeco-warning) 40%, transparent);
}

.alert-content {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-4);
  padding: var(--artdeco-spacing-4);
}

.alert-icon {
  font-size: var(--artdeco-text-xl);
}

.alert-text {
  flex: 1;
}

.alert-title {
  margin-bottom: var(--artdeco-spacing-1);
  color: var(--artdeco-warning);
  font-family: var(--artdeco-font-heading, var(--font-display));
  font-size: var(--artdeco-text-base);
  font-weight: var(--artdeco-font-semibold);
  text-transform: uppercase;
}

.alert-desc {
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-body, var(--font-body));
  font-size: var(--artdeco-text-sm);
}

.function-nav {
  display: flex;
  gap: var(--artdeco-spacing-2);
  margin-bottom: var(--artdeco-spacing-6);
  flex-wrap: wrap;
}

.content-area {
  position: relative;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-5);
  background: transparent;
  border: calc(var(--artdeco-spacing-px) * 2) solid var(--artdeco-gold-primary);
  color: var(--artdeco-gold-primary);
  font-family: var(--artdeco-font-heading, var(--font-display));
  font-size: var(--artdeco-text-sm);
  font-weight: var(--artdeco-font-semibold);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wider);
  border-radius: var(--artdeco-radius-none);
  cursor: pointer;
  transition:
    background var(--artdeco-transition-quick) var(--artdeco-ease-out),
    color var(--artdeco-transition-quick) var(--artdeco-ease-out),
    box-shadow var(--artdeco-transition-quick) var(--artdeco-ease-out);

  &:hover {
    background: color-mix(in srgb, var(--artdeco-gold-primary) 10%, transparent);
    box-shadow: var(--artdeco-glow-subtle);
  }
}

.btn-primary {
  background: var(--artdeco-gold-primary);
  color: var(--artdeco-bg-global);

  &:hover {
    background: var(--artdeco-gold-light);
  }
}

.tab-icon {
  font-size: var(--artdeco-text-sm);
}

.tab-label {
  font-size: var(--artdeco-text-sm);
}

@media (width <= 48rem) {
  .openstock-demo {
    padding: var(--artdeco-spacing-4);
  }

  .function-nav {
    flex-direction: column;
    width: 100%;
  }

  .alert-content {
    flex-direction: column;
    text-align: center;
  }

  .btn {
    width: 100%;
  }
}
</style>
