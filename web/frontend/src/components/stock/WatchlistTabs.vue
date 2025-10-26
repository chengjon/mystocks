<template>
  <div class="watchlist-tabs">
    <el-tabs
      v-model="activeTab"
      type="card"
      @tab-change="handleTabChange"
      class="watchlist-tabs-container"
    >
      <el-tab-pane
        v-for="tab in tabs"
        :key="tab.name"
        :label="tab.label"
        :name="tab.name"
      >
        <template #label>
          <span class="tab-label">
            <el-icon v-if="tab.icon" style="margin-right: 4px">
              <component :is="tab.icon" />
            </el-icon>
            {{ tab.label }}
          </span>
        </template>

        <!-- Tab content: WatchlistTable for each group -->
        <WatchlistTable
          :group="tab.name"
          @view="handleViewStock"
          @remove="handleRemoveStock"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserPreferences } from '@/composables/useUserPreferences'
import WatchlistTable from './WatchlistTable.vue'
import { User, MagicStick, TrendCharts, Warning } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const { preferences, updatePreference } = useUserPreferences()

// Tab definitions (FR-026)
const tabs = [
  { name: 'user', label: '用户自选', icon: User },
  { name: 'system', label: '系统自选', icon: MagicStick },
  { name: 'strategy', label: '策略自选', icon: TrendCharts },
  { name: 'monitor', label: '监控列表', icon: Warning }
]

// Active tab state (default: 'user' per FR-027)
const activeTab = ref('user')

/**
 * Handle tab change (T020)
 * Updates URL query parameter and saves to LocalStorage
 */
const handleTabChange = (tabName) => {
  console.log('[WatchlistTabs] Tab changed to:', tabName)

  // Update URL query parameter
  router.push({ query: { tab: tabName } })

  // Save to LocalStorage (FR-030)
  updatePreference('lastWatchlistTab', tabName)
}

/**
 * Initialize tab from URL or LocalStorage (T020)
 */
const initializeTab = () => {
  // Priority 1: URL query parameter
  if (route.query.tab) {
    const queryTab = route.query.tab
    if (tabs.some(t => t.name === queryTab)) {
      activeTab.value = queryTab
      console.log('[WatchlistTabs] Initialized from URL:', queryTab)
      return
    }
  }

  // Priority 2: LocalStorage
  const lastTab = preferences.value.lastWatchlistTab
  if (lastTab && tabs.some(t => t.name === lastTab)) {
    activeTab.value = lastTab
    // Update URL to match LocalStorage
    router.replace({ query: { tab: lastTab } })
    console.log('[WatchlistTabs] Initialized from LocalStorage:', lastTab)
    return
  }

  // Default: 'user' (FR-027)
  activeTab.value = 'user'
  router.replace({ query: { tab: 'user' } })
  console.log('[WatchlistTabs] Initialized to default: user')
}

/**
 * Handle browser back/forward navigation (T020)
 * Watch route query changes
 */
const handleRouteChange = () => {
  const newTab = route.query.tab
  if (newTab && tabs.some(t => t.name === newTab) && activeTab.value !== newTab) {
    activeTab.value = newTab
    console.log('[WatchlistTabs] Route changed to:', newTab)
  }
}

// Event handlers
const handleViewStock = (stock) => {
  console.log('[WatchlistTabs] View stock:', stock)
  // In production: navigate to stock detail page
  // router.push({ name: 'stock-detail', params: { symbol: stock.symbol } })
}

const handleRemoveStock = (stock) => {
  console.log('[WatchlistTabs] Remove stock:', stock)
  // Stock removal is handled in WatchlistTable
}

// Lifecycle
onMounted(() => {
  initializeTab()

  // Watch for route changes (browser back/forward)
  router.afterEach((to) => {
    if (to.name === route.name) {
      handleRouteChange()
    }
  })

  console.log('[WatchlistTabs] Mounted with active tab:', activeTab.value)
})
</script>

<style scoped>
.watchlist-tabs {
  width: 100%;
  padding: 20px;
}

.watchlist-tabs-container {
  width: 100%;
}

.tab-label {
  display: flex;
  align-items: center;
  font-size: 14px;
  font-weight: 500;
}

/* Enhance tab appearance */
:deep(.el-tabs__item) {
  font-size: 14px;
  padding: 0 20px;
  height: 42px;
  line-height: 42px;
}

:deep(.el-tabs__item.is-active) {
  color: #409EFF;
  font-weight: 600;
}

:deep(.el-tabs__content) {
  padding-top: 20px;
}

/* Card-style tabs */
:deep(.el-tabs--card > .el-tabs__header) {
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 20px;
}

:deep(.el-tabs--card > .el-tabs__header .el-tabs__item) {
  border: 1px solid transparent;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
  transition: all 0.3s;
}

:deep(.el-tabs--card > .el-tabs__header .el-tabs__item.is-active) {
  background-color: #fff;
  border-color: #e4e7ed;
  border-bottom-color: #fff;
}

:deep(.el-tabs--card > .el-tabs__header .el-tabs__item:hover) {
  color: #409EFF;
}
</style>
