<template>
    <div class="artdeco-stock-management">
        <!-- Page Header -->
        <div class="page-header">
            <div class="header-content">
                <h1 class="page-title">智能选股管理</h1>
                <p class="page-subtitle">自选股管理、策略选股、行业分析、批量操作</p>
                <div class="header-actions">
                    <div class="time-display">
                        <span class="time-label">最后更新</span>
                        <span class="time-value">{{ currentTime }}</span>
                    </div>
                    <ArtDecoButton variant="outline" size="sm" @click="refreshAllData">刷新数据</ArtDecoButton>
                    <ArtDecoButton variant="solid" size="sm" @click="showAddStockDialog = true">添加股票</ArtDecoButton>
                </div>
            </div>
        </div>

        <!-- Summary Stats -->
        <div class="stats-section">
            <div class="stats-grid">
                <ArtDecoStatCard label="自选股票" :value="watchlistStats.totalStocks" :change="strategyStats.changePercent" variant="gold" />
                <ArtDecoStatCard label="关注行业" :value="industryStats.totalIndustries" :change="industryStats.changePercent" variant="gold" />
                <ArtDecoStatCard label="概念板块" :value="conceptStats.totalConcepts" :change="conceptStats.changePercent" variant="gold" />
                <ArtDecoStatCard label="今日涨跌" :value="portfolioStats.dailyChange" :change="portfolioStats.changePercent" :variant="portfolioStats.changePercent >= 0 ? 'rise' : 'fall'" />
                <ArtDecoStatCard label="持仓收益" :value="portfolioStats.totalReturn" :change="portfolioStats.returnPercent" :variant="portfolioStats.returnPercent >= 0 ? 'rise' : 'fall'" />
                <ArtDecoStatCard label="策略配置" :value="strategyStats.totalSelected" :change="strategyStats.changePercent" variant="gold" />
            </div>
        </div>

        <!-- Main Navigation Tabs -->
        <nav class="main-tabs">
            <button
                v-for="tab in mainTabs"
                :key="tab.key"
                class="main-tab"
                :class="{ active: activeMainTab === tab.key }"
                @click="switchMainTab(tab.key)"
            >
                <span class="tab-icon">{{ tab.icon }}</span>
                <span class="tab-label">{{ tab.label }}</span>
            </button>
        </nav>

        <!-- Tab Content -->
        <div class="tab-content">
            <!-- ==================== WATCHLIST MANAGEMENT ==================== -->
            <div v-if="activeMainTab === 'watchlist'" class="tab-panel">
                <div class="watchlist-header">
                    <div class="watchlist-tabs">
                        <button
                            v-for="list in watchlists"
                            :key="list.id"
                            class="watchlist-tab"
                            :class="{ active: activeWatchlistId === list.id }"
                            @click="activeWatchlistId = list.id"
                        >
                            <span class="list-icon">{{ list.icon }}</span>
                            <span class="list-name">{{ list.name }}</span>
                            <span class="list-count">{{ list.stocks.length }}</span>
                        </button>
                    </div>
                    <div class="watchlist-actions">
                        <ArtDecoButton class="watchlist-tab add-list" @click="showCreateListDialog = true">+</span>
                        <ArtDecoButton variant="outline" size="sm" @click="exportWatchlist">导出CSV</ArtDecoButton>
                        <ArtDecoButton variant="outline" size="sm" @click="showImportDialog = true">导入股票</ArtDecoButton>
                        <ArtDecoButton variant="outline" size="sm" @click="toggleBatchMode">
                            {{ batchMode ? '退出批量' : '批量操作' }}
                        </ArtDecoButton>
                    </div>
                </div>

                <div class="stock-cards-grid">
                    <div v-for="stock in currentWatchlistStocks" :key="stock.symbol">
                        <div class="card-header">
                            <span class="stock-symbol">{{ stock.symbol }}</span>
                            <button class="remove-stock" @click="removeStock(stock)">×</button>
                        </div>
                        <div class="card-body">
                            <div class="stock-name">{{ stock.name }}</div>
                        </div>
                    </div>
                </div>
            </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, computed, onMounted, watch } from 'vue'
    import { useRoute } from 'vue-router'
    import { getPageConfig, getTabConfig, isRouteName, isMonolithicConfig, type PageConfig, type MonolithicPageConfig, type TabConfig } from '@/config/pageConfig'

    const route = useRoute()

    // 根据当前路由名称获取配置
    const currentRouteName = computed(() => {
        return route.name as string || 'stock-management'
    })

    // 当前页面配置
    const currentPageConfig = computed(() => {
        if (!isRouteName(currentRouteName.value)) {
            console.warn('未知路由名称:', currentRouteName.value)
            return null
        }
        return getPageConfig(currentRouteName.value)
    })

    // 验证是否为 monolithic 配置
    const isMonolithic = computed(() => {
        return currentPageConfig.value !== null && isMonolithicConfig(currentPageConfig.value)
    })

    // Tab 配置
    const mainTabs = computed(() => {
        if (!isMonolithic.value) return []
        const config = currentPageConfig.value as MonolithicPageConfig
        return config.tabs || []
    })

    // 当前 Tab 配置
    const currentTabConfig = computed((): TabConfig | undefined => {
        if (!isMonolithic.value) return undefined
        const config = currentPageConfig.value as MonolithicPageConfig
        return getTabConfig(currentRouteName.value, activeMainTab.value)
    })

    // API 端点
    const apiEndpoint = computed(() => {
        return currentTabConfig.value?.apiEndpoint || currentPageConfig.value?.apiEndpoint || ''
    })

    // WebSocket 频道
    const wsChannel = computed(() => {
        return currentTabConfig.value?.wsChannel || currentPageConfig.value?.wsChannel || ''
    })

    const activeMainTab = ref('watchlist')

    // 根据路由 meta.activeTab 设置初始 tab
    onMounted(() => {
        const metaTab = route.meta.activeTab
        if (metaTab) {
            activeMainTab.value = metaTab
        }
        console.log('ArtDecoStockManagement 已加载')
        console.log('当前路由:', currentRouteName.value)
        console.log('API端点:', apiEndpoint.value)
        console.log('WebSocket频道:', wsChannel.value)
    })

    // 监听路由变化
    watch(() => route.name, (newRoute) => {
        const metaTab = route.meta.activeTab
        if (metaTab) {
            activeMainTab.value = metaTab
        }
        console.log('路由切换到:', newRoute)
        console.log('API端点:', apiEndpoint.value)
        console.log('WebSocket频道:', wsChannel.value)
    })
const loading = ref({
    overview: false,
    watchlist: false,
    positions: false,
    attribution: false,
    history: false,
    strategy: false
})

// Error states
const error = ref({
    overview: null,
    watchlist: null,
    positions: null,
    attribution: null,
    history: null,
    strategy: null
})

function switchMainTab(tabKey: string) {
    activeMainTab.value = tabKey
}

const currentTime = computed(() => {
    const now = new Date()
    const options: Intl.DateTimeFormatOptions = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric'
    }
    return new Intl.DateTimeFormat('zh-CN', options).format(now)
})

async function refreshAllData() {
    if (!apiEndpoint.value) {
        console.warn('未配置的API端点:', currentRouteName.value)
        return
    }
    
    console.log('刷新数据 - API端点:', apiEndpoint.value)
    // TODO: 使用 apiEndpoint 调用 API
}

function showAddStockDialog() {
    console.log('显示添加股票对话框')
}

function showCreateListDialog() {
    console.log('显示创建自选列表对话框')
}

function showImportDialog() {
    console.log('显示导入股票对话框')
}
</script>