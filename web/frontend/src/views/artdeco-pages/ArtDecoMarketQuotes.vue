<template>
    <div class="artdeco-market-quotes">
        <!-- Page Header -->
        <div class="page-header">
            <button @click="fetchRealtimeQuotes" style="background: red; color: white; padding: 10px; position: fixed; top: 10px; right: 10px; z-index: 9999;">
                FORCE REFRESH DEBUG
            </button>
            <div class="header-content">
                <h1 class="page-title">市场行情中心</h1>
                <p class="page-subtitle">全方位实时行情监控与技术分析平台</p>
                <div class="header-actions">
                    <div class="time-display">
                        <span class="time-label">市场状态</span>
                        <span class="time-value">交易中</span>
                    </div>
                    <ArtDecoButton variant="outline" size="sm" @click="refreshData">刷新行情</ArtDecoButton>
                </div>
            </div>
        </div>

        <!-- Quick Stats Bar -->
        <div class="quick-stats">
            <div class="stat-item">
                <div class="stat-label">上证指数</div>
                <div class="stat-value">3128.45</div>
                <div class="stat-change rise">+0.85%</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">深证成指</div>
                <div class="stat-value">10245.67</div>
                <div class="stat-change rise">+1.23%</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">创业板指</div>
                <div class="stat-value">2156.89</div>
                <div class="stat-change fall">-0.45%</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">北向资金</div>
                <div class="stat-value">58.8亿</div>
                <div class="stat-change rise">+15.6%</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">成交金额</div>
                <div class="stat-value">8956亿</div>
                <div class="stat-change rise">+15.8%</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">涨跌家数</div>
                <div class="stat-value">2856↑/1689↓</div>
                <div class="stat-change neutral">净涨</div>
            </div>
        </div>

        <!-- Main Tabs -->
        <nav class="main-tabs">
            <button
                v-for="(tab, _idx) in mainTabs"
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
            <!-- 实时行情 -->
            <div v-if="activeTab === 'realtime'" class="tab-panel">
                <div class="realtime-controls">
                    <div class="market-selector">
                        <ArtDecoSelect v-model="selectedMarket" :options="marketOptions" placeholder="选择市场" />
                    </div>
                    <div class="sort-controls">
                        <button
                            v-for="(sort, _idx) in sortOptions"
                            :key="sort.key"
                            class="sort-btn"
                            :class="{ active: activeSort === sort.key }"
                            @click="activeSort = sort.key"
                        >
                            {{ sort.label }}
                        </button>
                    </div>
                </div>
                <ArtDecoCard title="实时行情列表" hoverable class="quotes-table-card">
                    <div class="quotes-table">
                        <div class="table-header">
                            <div class="col-code">代码</div>
                            <div class="col-name">名称</div>
                            <div class="col-price">最新价</div>
                            <div class="col-change">涨跌幅</div>
                            <div class="col-volume">成交量</div>
                            <div class="col-amount">成交额</div>
                            <div class="col-turnover">换手率</div>
                            <div class="col-pe">市盈率</div>
                        </div>
                        <div class="table-body">
                            <template v-if="loading">
                                <div class="table-row skeleton" v-for="i in 10" :key="i">
                                    <div class="col-code"><ArtDecoSkeleton variant="text" width="60px" /></div>
                                    <div class="col-name"><ArtDecoSkeleton variant="text" width="100px" /></div>
                                    <div class="col-price"><ArtDecoSkeleton variant="text" width="50px" /></div>
                                    <div class="col-change"><ArtDecoSkeleton variant="text" width="50px" /></div>
                                    <div class="col-volume"><ArtDecoSkeleton variant="text" width="80px" /></div>
                                    <div class="col-amount"><ArtDecoSkeleton variant="text" width="80px" /></div>
                                    <div class="col-turnover"><ArtDecoSkeleton variant="text" width="40px" /></div>
                                    <div class="col-pe"><ArtDecoSkeleton variant="text" width="40px" /></div>
                                </div>
                            </template>
                            <template v-else-if="realtimeQuotes.length > 0">
                                <div
                                    class="table-row"
                                    v-for="(stock, _idx) in realtimeQuotes"
                                    :key="stock.code"
                                    :class="{ 'price-up': stock.change > 0, 'price-down': stock.change < 0 }"
                                >
                                    <div class="col-code">{{ stock.code }}</div>
                                    <div class="col-name">{{ stock.name }}</div>
                                    <div class="col-price">{{ stock.price }}</div>
                                    <div class="col-change">{{ stock.change > 0 ? '+' : '' }}{{ stock.change }}%</div>
                                    <div class="col-volume">{{ stock.volume }}</div>
                                    <div class="col-amount">{{ stock.amount }}</div>
                                    <div class="col-turnover">{{ stock.turnover }}%</div>
                                    <div class="col-pe">{{ stock.pe }}</div>
                                </div>
                            </template>
                            <template v-else>
                                <div class="empty-state">
                                    <ArtDecoIcon name="search" size="xl" />
                                    <p>暂无行情数据，请刷新重试</p>
                                    <p v-if="errorMsg" class="error-detail">{{ errorMsg }}</p>
                                </div>
                            </template>
                        </div>
                    </div>
                </ArtDecoCard>
            </div>

            <!-- 技术分析 -->
            <div v-if="activeTab === 'technical'" class="tab-panel">
                <div class="technical-controls">
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
                                <div class="indicator-value">67.8</div>
                                <div class="indicator-signal">中性</div>
                            </div>
                            <div class="indicator-item">
                                <div class="indicator-name">MACD</div>
                                <div class="indicator-value">+0.45</div>
                                <div class="indicator-signal rise">买入</div>
                            </div>
                            <div class="indicator-item">
                                <div class="indicator-name">KDJ</div>
                                <div class="indicator-value">78.5</div>
                                <div class="indicator-signal">超买</div>
                            </div>
                            <div class="indicator-item">
                                <div class="indicator-name">布林带</div>
                                <div class="indicator-value">上轨</div>
                                <div class="indicator-signal">强势</div>
                            </div>
                            <div class="indicator-item">
                                <div class="indicator-name">威廉指标</div>
                                <div class="indicator-value">-23.4</div>
                                <div class="indicator-signal fall">卖出</div>
                            </div>
                            <div class="indicator-item">
                                <div class="indicator-name">均线系统</div>
                                <div class="indicator-value">多头排列</div>
                                <div class="indicator-signal rise">看好</div>
                            </div>
                        </div>
                    </ArtDecoCard>

                    <ArtDecoCard title="形态识别" hoverable class="patterns-card">
                        <div class="patterns-list">
                            <div class="pattern-item">
                                <div class="pattern-name">头肩顶形态</div>
                            </div>
                            <div class="pattern-item">
                                <div class="pattern-name">双顶形态</div>
                            </div>
                            <div class="pattern-item">
                                <div class="pattern-name">底部形态</div>
                            </div>
                            <div class="pattern-item">
                                <div class="pattern-name">三角形形态</div>
                            </div>
                        </div>
                    </ArtDecoCard>

                    <ArtDecoCard title="异动监控" hoverable class="abnormal-monitor-card">
                        <div class="abnormal-list">
                            <div class="abnormal-item" v-for="item in abnormalStocks" :key="item.code">
                                <div class="abnormal-type" :class="item.type">{{ item.typeText }}</div>
                                <div class="abnormal-stock">
                                    <div class="stock-name">{{ item.name }}</div>
                                    <div class="stock-code">{{ item.code }}</div>
                                </div>
                                <div class="abnormal-change" :class="item.change >= 0 ? 'rise' : 'fall'">
                                    {{ item.change >= 0 ? '+' : '' }}{{ item.change }}%
                                </div>
                            </div>
                        </div>
                    </ArtDecoCard>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
    ArtDecoStatCard, ArtDecoCard, ArtDecoButton, ArtDecoCollapsible,
    ArtDecoHeader, ArtDecoIcon, ArtDecoBadge, ArtDecoLoading,
    ArtDecoSelect, ArtDecoInput
} from '@/components/artdeco'
import ArtDecoSkeleton from '@/components/artdeco/core/ArtDecoSkeleton.vue'
import { marketService } from '@/api/services/marketService'

const route = useRoute()

// 定义数据类型
interface Stock {
    code: string
    name: string
    price: number
    change: number
    volume: string
    amount: string
    turnover: number
    pe: number
}

interface AbnormalStock {
    code: string
    name: string
    type: string
    typeText: string
    change: number
}

interface TabOption {
    key: string
    label: string
    icon: string
}

interface SelectOption {
    label: string
    value: string
}

// 根据当前路由名称获取配置
const currentRouteName = computed(() => {
    return route.name as string || 'market-realtime'
})

// 当前页面配置
const currentPageConfig = computed(() => {
    if (!isRouteName(currentRouteName.value)) {
        console.warn('未知路由名称:', currentRouteName.value)
        return null
    }
    return getPageConfig(currentRouteName.value)
})

// API 端点
const apiEndpoint = computed(() => {
    const config = currentPageConfig.value
    if (!config) return ''
    if ('apiEndpoint' in config) {
        return (config as any).apiEndpoint
    }
    return ''
})

// WebSocket 频道
const wsChannel = computed(() => {
    const config = currentPageConfig.value
    if (!config) return ''
    if ('wsChannel' in config) {
        return (config as any).wsChannel
    }
    return ''
})

// 组件名称
const _componentName = computed(() => {
    return currentPageConfig.value?.component || ''
})

// Tab 配置（如果有）
const _tabConfig = computed(() => {
    const config = currentPageConfig.value
    if (config && 'tabs' in config) {
        return (config as Record<string, unknown>).tabs || []
    }
    return []
})

const activeTab = ref('realtime')
const selectedMarket = ref('sh')
const analysisSymbol = ref('')
const analysisPeriod = ref('1d')
const activeSort = ref('code')
const loading = ref(false)
const errorMsg = ref('')

const realtimeQuotes = ref<Stock[]>([])
const _hotSectors = ref([])
const abnormalStocks = ref<AbnormalStock[]>([])

// 主标签配置
const mainTabs: TabOption[] = [
    { key: 'realtime', label: '实时行情', icon: '📊' },
    { key: 'technical', label: '技术分析', icon: '📈' }
]

// 市场选项
const marketOptions: SelectOption[] = [
    { label: '上海', value: 'sh' },
    { label: '深圳', value: 'sz' },
    { label: '创业板', value: 'cyb' },
    { label: '科创板', value: 'kcb' }
]

// 排序选项
const sortOptions: TabOption[] = [
    { key: 'code', label: '代码', icon: '' },
    { key: 'change', label: '涨跌幅', icon: '' },
    { key: 'volume', label: '成交量', icon: '' },
    { key: 'amount', label: '成交额', icon: '' }
]

// 周期选项
const periodOptions: SelectOption[] = [
    { label: '日线', value: '1d' },
    { label: '周线', value: '1w' },
    { label: '月线', value: '1m' },
    { label: '5分钟', value: '5m' },
    { label: '15分钟', value: '15m' },
    { label: '30分钟', value: '30m' },
    { label: '60分钟', value: '60m' }
]

// 根据路由 meta.activeTab 设置初始 tab
onMounted(() => {
    const metaTab = route.meta.activeTab
    if (metaTab) {
        activeTab.value = metaTab
    }
    fetchRealtimeQuotes()
})

// 监听排序或市场变化
watch([selectedMarket, activeSort], () => {
    fetchRealtimeQuotes()
})

async function fetchRealtimeQuotes() {
    loading.value = true
    errorMsg.value = ''
    try {
        // 调用标准化的 getQuotes
        const quotes = await marketService.getQuotes()
        
        // 数据转换逻辑
        realtimeQuotes.value = quotes.map((item: any) => ({
            code: item.symbol || item.code,
            name: item.name,
            price: item.latest_price || item.price || 0,
            change: item.change_percent || item.change || 0,
            volume: formatLargeNumber(item.volume),
            amount: formatLargeNumber(item.amount),
            turnover: item.turnover_ratio || item.turnover || 0,
            pe: item.pe_ratio || item.pe || 0
        }))
    } catch (e: any) {
        console.error('Failed to fetch quotes:', e)
        errorMsg.value = '行情数据加载失败，请重试'
    } finally {
        loading.value = false
    }
}

function formatLargeNumber(num: number | string) {
    const n = Number(num)
    if (isNaN(n)) return '--'
    if (n >= 100000000) return (n / 100000000).toFixed(2) + '亿'
    if (n >= 10000) return (n / 10000).toFixed(2) + '万'
    return n.toString()
}

function switchTab(tabKey: string) {
    activeTab.value = tabKey
}

function refreshData() {
    fetchRealtimeQuotes()
}

function analyzeStock() {
    if (!apiEndpoint.value) {
        console.warn('未配置的API端点:', currentRouteName.value)
        return
    }
    console.log('开始分析 - API端点:', apiEndpoint.value)
    // TODO: 使用 apiEndpoint 调用 API
}

// 观察者模式 - 订阅 WebSocket
const _subscribeWebSocket = () => {
    if (!wsChannel.value) {
        console.warn('未配置的WebSocket频道:', currentRouteName.value)
        return
    }
    console.log('订阅WebSocket频道:', wsChannel.value)
    // TODO: 使用 wsChannel 订阅 WebSocket
}
</script>
