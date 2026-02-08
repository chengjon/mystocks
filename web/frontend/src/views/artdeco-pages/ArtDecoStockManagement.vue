<template>
  <div class="artdeco-stock-management">
    <ArtDecoHeader
      title="智能选股管理"
      subtitle="动态自选池 · 实时持仓监控 · 行业深度归因"
      :show-status="true"
      status-text="云同步完成"
    >
      <template #actions>
        <ArtDecoButton variant="solid" size="sm" @click="handleAddStock">
          <template #icon><ArtDecoIcon name="plus" /></template>
          添加股票
        </ArtDecoButton>
      </template>
    </ArtDecoHeader>

    <nav class="main-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="main-tab"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </nav>

    <div class="tab-content">
      <transition name="fade" mode="out-in">
        <div :key="activeTab" class="tab-panel">
          <WatchlistManager 
            v-if="activeTab === 'watchlist'" 
            :watchlists="watchlists"
            :active-watchlist-id="activeWatchlistId"
            :current-stocks="currentWatchlistStocks"
            @select-list="activeWatchlistId = $event"
          />
          <PortfolioMonitor 
            v-if="activeTab === 'portfolio'" 
            :positions="positions" 
          />
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ArtDecoHeader, ArtDecoButton, ArtDecoIcon } from '@/components/artdeco'
import WatchlistManager from './stock-management-tabs/WatchlistManager.vue'
import PortfolioMonitor from './stock-management-tabs/PortfolioMonitor.vue'
import apiClient from '@/api/apiClient'

const activeTab = ref('watchlist')
const tabs = [
  { key: 'watchlist', label: '自选管理' },
  { key: 'portfolio', label: '持仓监控' },
  { key: 'attribution', label: '行业归因' }
]

const activeWatchlistId = ref('')
const watchlists = ref([])
const positions = ref([])

const currentWatchlistStocks = computed(() => {
  return watchlists.value.find((l: any) => l.id === activeWatchlistId.value)?.stocks || []
})

const fetchData = async () => {
  try {
    const [wlRes, portRes] = await Promise.all([
      apiClient.get('/api/portfolio/v2/watchlist'),
      apiClient.get('/api/portfolio/v2/summary')
    ])
    
    if (wlRes.data?.success) {
      watchlists.value = wlRes.data.data
      if (watchlists.value.length > 0 && !activeWatchlistId.value) {
        activeWatchlistId.value = watchlists.value[0].id
      }
    }
    
    if (portRes.data?.success) {
      positions.value = portRes.data.data.positions
    }
  } catch (e) {
    console.error('Failed to fetch stock management data', e)
  }
}

const handleAddStock = () => {
  console.log('Opening add stock dialog...')
}

onMounted(fetchData)
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.artdeco-stock-management {
  padding: var(--artdeco-spacing-6);
  background: var(--artdeco-bg-global);
  min-height: 100vh;
}

.main-tabs {
  display: flex;
  gap: var(--artdeco-spacing-2);
  margin: var(--artdeco-spacing-6) 0;
  border-bottom: 2px solid var(--artdeco-border-gold-subtle);
}

.main-tab {
  padding: 12px 24px;
  background: transparent;
  border: none;
  color: var(--artdeco-fg-muted);
  cursor: pointer;
  text-transform: uppercase;
  font-family: var(--artdeco-font-display);
  letter-spacing: var(--artdeco-tracking-wide);
  transition: all 0.3s;

  &:hover, &.active {
    color: var(--artdeco-accent-gold);
  }

  &.active {
    border-bottom: 2px solid var(--artdeco-accent-gold);
    margin-bottom: -2px;
  }
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>