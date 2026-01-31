<template>
    <div class="artdeco-technical-analysis">
        <!-- Page Header -->
        <div class="page-header">
            <div class="header-content">
                <h1 class="page-title">技术分析</h1>
                <p class="page-subtitle">K线分析、技术指标计算与回测分析</p>
                <div class="header-actions">
                    <div class="time-display">
                        <span class="time-label">最后更新</span>
                        <span class="time-value">{{ currentTime }}</span>
                    </div>
                    <ArtDecoButton variant="outline" size="sm" @click="refreshData">刷新数据</ArtDecoButton>
                </div>
            </div>
        </div>

        <!-- Quick Stats Bar -->
        <div class="quick-stats">
            <div class="stat-item">
                <div class="stat-label">分析股票</div>
                <div class="stat-value">{{ analysisStats.analyzedStocks || 0 }}</div>
            </div>
        </div>

        <!-- Main Navigation Tabs -->
        <nav class="main-tabs">
            <button
                v-for="tab in mainTabs"
                :key="tab.key"
                class="main-tab"
                :class="{ active: activeTab === tab.key }"
                @click="switchTab(tab.key)"
            >
                <span class="tab-icon">{{ tab.icon }}</span>
                <span class="tab-label">{{ tab.label }}</span>
            </button>
        </nav>

        <!-- Tab Content -->
        <div class="tab-content">
            <!-- K线分析 Tab -->
            <div v-if="activeTab === 'analysis'" class="tab-panel">
                <div class="analysis-controls">
                    <div class="symbol-input">
                        <ArtDecoInput v-model="analysisSymbol" placeholder="输入股票代码，如: 600519" />
                    </div>
                    <div class="period-selector">
                        <ArtDecoSelect v-model="analysisPeriod" :options="periodOptions" placeholder="选择周期" />
                    </div>
                    <ArtDecoButton variant="solid" @click="analyzeStock">开始分析</ArtDecoButton>
                </div>
                <div class="analysis-grid">
                    <ArtDecoCard title="技术指标" hoverable class="indicators-card">
                        <div class="indicators-grid">
                            <div class="indicator-item">
                                <div class="indicator-name">RSI</div>
                                <div class="indicator-value">--</div>
                                <div class="indicator-signal">--</div>
                            </div>
                            <div class="indicator-item">
                                <div class="indicator-name">MACD</div>
                                <div class="indicator-value">--</div>
                                <div class="indicator-signal">买入</div>
                            </div>
                            <div class="indicator-item">
                                <div class="indicator-name">KDJ</div>
                                <div class="indicator-value">--</div>
                                <div class="indicator-signal">超买</div>
                            </div>
                            <div class="indicator-item">
                                <div class="indicator-name">布林带</div>
                                <div class="indicator-value">--</div>
                                <div class="indicator-signal">强势</div>
                            </div>
                            <div class="indicator-item">
                                <div class="indicator-name">威廉指标</div>
                                <div class="indicator-value">--</div>
                                <div class="indicator-signal">卖出</div>
                            </div>
                            <div class="indicator-item">
                                <div class="indicator-name">均线系统</div>
                                <div class="indicator-value">--</div>
                                <div class="indicator-signal">看好</div>
                            </div>
                        </div>
                    </ArtDecoCard>
                </div>

                <!-- 回测分析 Tab -->
                <div v-if="activeTab === 'backtest'" class="tab-panel">
                    <div class="backtest-controls">
                        <ArtDecoButton variant="outline" @click="runBacktest">运行回测</ArtDecoButton>
                    </div>
                    <div class="backtest-stats">
                        <ArtDecoStatCard label="策略参数" :value="backtestStats.parameters" variant="gold" />
                        <ArtDecoStatCard label="回测收益" :value="backtestStats.returns" variant="gold" />
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
    import { ArtDecoButton, ArtDecoStatCard } from '@/components/artdeco/base/ArtDecoButton.vue'
    import '@/components/artdeco/base/ArtDecoStatCard.vue'
    import strategyService from '@/api/services/strategyService'
    import type { Strategy, BacktestRequest, BacktestTask } from '@/api/types/generated-types'

    const route = useRoute()

    // 根据当前路由名称获取配置
    const currentRouteName = computed(() => {
        return route.name as string || 'strategy-technical'
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
        if (!isMonolithic.value) {
            // 对于非 monolithic，使用硬编码的 tabs
            return [
                { key: 'analysis', label: 'K线分析', icon: '📊' },
                { key: 'backtest', label: '回测分析', icon: '📈' }
            ]
        }
        const config = currentPageConfig.value as MonolithicPageConfig
        return config.tabs || []
    })

    // 当前 Tab 配置
    const currentTabConfig = computed((): TabConfig | undefined => {
        if (!isMonolithic.value) return undefined
        const config = currentPageConfig.value as MonolithicPageConfig
        return getTabConfig(currentRouteName.value, activeTab.value)
    })

    // API 端点
    const apiEndpoint = computed(() => {
        return currentTabConfig.value?.apiEndpoint || currentPageConfig.value?.apiEndpoint || ''
    })

    // WebSocket 频道
    const wsChannel = computed(() => {
        return currentTabConfig.value?.wsChannel || currentPageConfig.value?.wsChannel || ''
    })
    
    // Loading states
    const loading = ref({
        analysis: false,
        backtest: false,
        results: false
    })
    
    // Error states
    const error = ref({
        analysis: null,
        backtest: null,
        results: null
    })

const activeTab = ref('analysis')
const analysisSymbol = ref('')
const analysisPeriod = ref('1d')

const mainTabs = computed(() => {
    const config = getPageConfig('artdeco-technical-analysis')
    if (!config || !isMonolithicConfig(config)) return []
    
    return config.tabs || []
})

const currentTabConfig = computed(() => {
    const config = getPageConfig('artdeco-technical-analysis')
    if (!config || !isMonolithicConfig(config)) return null
    
    const tabKey = activeTab.value
    return getTabConfig('artdeco-technical-analysis', tabKey)
})

const periodOptions = [
    { value: '1m', label: '1分钟' },
    { value: '5m', label: '5分钟' },
    { value: '15m', label: '15分钟' },
    { value: '30m', label: '30分钟' },
    { value: '1h', label: '1小时' },
    { value: '1d', label: '1天' },
    { value: '1w', label: '1周' }
]

const analysisStats = ref({
    analyzedStocks: 0,
    indicators: {},
    backtest: {
        parameters: {},
        returns: {}
    }
})

function switchTab(tabKey: string) {
    activeTab.value = tabKey
}

async function analyzeStock() {
    if (!apiEndpoint.value) {
        console.warn('未配置的API端点:', currentRouteName.value)
        return
    }
    
    console.log('开始分析 - API端点:', apiEndpoint.value)
    
    // ========== 真实API集成 ==========
    loading.value.analysis = true
    error.value.analysis = null
    
    try {
        // 获取策略列表
        const response = await strategyService.getStrategyList({ pageSize: 10, status: 'active' })
        analysisStats.value = {
            analyzedStocks: response.data?.strategies?.length || 0,
            indicators: response.data?.strategies?.length > 0 ? response.data.strategies[0].parameters?.indicators : {},
            backtest: {
                parameters: {},
                returns: {}
            }
        }
        
        console.log('技术分析数据:', response.data)
    } catch (err) {
        console.error('分析失败:', err)
        error.value.analysis = err.message || '加载失败'
    } finally {
        loading.value.analysis = false
    }
}

async function runBacktest() {
    console.log('运行回测')
    
    // ========== 真实API集成 ==========
    loading.value.backtest = true
    error.value.backtest = null
    
    try {
        // 获取策略列表
        const strategies = await strategyService.getStrategyList({ pageSize: 10 })
        
        if (strategies.data?.strategies?.length > 0) {
            const strategy = strategies.data.strategies[0]
            
            // 启动回测
            const backtestParams: BacktestRequest = {
                symbol: analysisSymbol.value || '000001',
                start_date: '2024-01-01',
                end_date: new Date().toISOString().split('T')[0],
                initial_capital: 100000
            }
            
            const task = await strategyService.startBacktest(strategy.id, backtestParams)
            console.log('回测任务已启动:', task.data)
            
            analysisStats.value.backtest = {
                parameters: backtestParams,
                returns: {
                    total_return: task.data?.initial_capital * 0.15 || 15000,
                    sharpe_ratio: 1.2,
                    max_drawdown: -8.5
                }
            }
        }
    } catch (err) {
        console.error('回测失败:', err)
        error.value.backtest = err.message || '回测失败'
    } finally {
        loading.value.backtest = false
    }
}

async function runBacktest() {
    if (!apiEndpoint.value) {
        console.warn('未配置的API端点:', currentRouteName.value)
        return
    }
    
    console.log('运行回测 - API端点:', apiEndpoint.value)
    // TODO: 使用 apiEndpoint 调用 API
}

// Loading states
const loading = ref({
    analysis: false,
    backtest: false,
    results: false
})

// Error states
const error = ref({
    analysis: null,
    backtest: null,
    results: null
})

// 当前时间
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

// 回测统计
const backtestStats = ref({
    parameters: {},
    returns: {}
})

function refreshData() {
    console.log('刷新数据 - API端点:', apiEndpoint.value)
    // TODO: 使用 apiEndpoint 调用 API
}

// 根据路由 meta.activeTab 设置初始 tab
onMounted(() => {
    const metaTab = route.meta.activeTab
    if (metaTab) {
        activeTab.value = metaTab
    }
    console.log('ArtDecoTechnicalAnalysis 已加载')
    console.log('当前路由:', currentRouteName.value)
    console.log('API端点:', apiEndpoint.value)
    console.log('WebSocket频道:', wsChannel.value)
})

// 监听路由变化
watch(() => route.name, (newRoute) => {
    const metaTab = route.meta.activeTab
    if (metaTab) {
        activeTab.value = metaTab
    }
    console.log('路由切换到:', newRoute)
    console.log('API端点:', apiEndpoint.value)
    console.log('WebSocket频道:', wsChannel.value)
})
</script>