<template>
    <div class="artdeco-market-quotes">
        <section class="hero-shell artdeco-card-shell">
            <div class="hero-rail">
                <div class="hero-copy">
                    <span class="hero-eyebrow">live market observatory</span>
                    <div class="hero-meta">
                        <span>REQ_ID: {{ requestTraceId }}</span>
                        <span>SYNC: {{ syncLabel }}</span>
                        <span>FOCUS: {{ activeTabMeta.label }}</span>
                    </div>
                </div>
            </div>

            <ArtDecoHeader
                title="市场行情中心"
                subtitle="全方位实时行情监控与技术分析平台"
                :show-status="true"
                :status-text="marketStatusLabel"
            >
                <template #actions>
                    <div class="hero-actions">
                        <div class="time-display">
                            <span class="time-label">当前市场</span>
                            <span class="time-value">{{ selectedMarketLabel }}</span>
                        </div>
                        <ArtDecoButton variant="outline" size="sm" @click="refreshData">刷新行情</ArtDecoButton>
                    </div>
                </template>
            </ArtDecoHeader>
        </section>

        <section class="stats-strip artdeco-card-shell">
            <ArtDecoStatCard label="行情条目" :value="quoteCountLabel" variant="gold" />
            <ArtDecoStatCard label="上涨家数" :value="risingCountLabel" variant="rise" />
            <ArtDecoStatCard label="下跌家数" :value="fallingCountLabel" variant="fall" />
            <ArtDecoStatCard label="接口端点" :value="apiStatusLabel" variant="gold" />
        </section>

        <section class="tabs-shell artdeco-card-shell">
            <div class="tabs-shell-header">
                <div class="tabs-shell-copy">
                    <span class="tabs-shell-eyebrow">market route</span>
                    <h2 class="tabs-shell-title">行情与技术工作流</h2>
                    <p class="tabs-shell-subtitle">{{ activeTabMeta.description }}</p>
                </div>
                <div class="tabs-shell-trace">
                    <span>TABS: {{ mainTabs.length }}</span>
                    <span>CHANNEL: {{ wsChannelLabel }}</span>
                </div>
            </div>

            <nav class="main-tabs">
                <button
                    v-for="(tab, _idx) in mainTabs"
                    :key="tab.key"
                    class="main-tab"
                    :class="{ active: activeTab === tab.key }"
                    @click="switchTab(tab.key)"
                >
                    <ArtDecoIcon :name="tab.icon" size="sm" class="tab-icon" />
                    <span class="tab-label">{{ tab.label }}</span>
                </button>
            </nav>
        </section>

        <section class="content-shell artdeco-card-shell">
            <div class="content-shell-header">
                <div class="content-shell-copy">
                    <span class="content-shell-kicker">{{ activeTabMeta.eyebrow }}</span>
                    <h3 class="content-shell-title">{{ activeTabMeta.label }}</h3>
                </div>
                <div class="content-shell-meta">
                    <span>SORT: {{ activeSortLabel }}</span>
                    <span>API: {{ apiStatusLabel }}</span>
                </div>
            </div>

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
                            <template v-else-if="displayQuotes.length > 0">
                                <div
                                    class="table-row"
                                    v-for="(stock, _idx) in displayQuotes"
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
        </section>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
    ArtDecoCard, ArtDecoButton, ArtDecoHeader, ArtDecoIcon,
    ArtDecoSelect, ArtDecoInput, ArtDecoStatCard
} from '@/components/artdeco'
import ArtDecoSkeleton from '@/components/artdeco/core/ArtDecoSkeleton.vue'
import { marketService } from '@/api/services/marketService'
import { getPageConfig, isRouteName } from '@/config/pageConfig'

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
    eyebrow?: string
    description?: string
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

    const endpoint = (config as { apiEndpoint?: unknown }).apiEndpoint
    return typeof endpoint === 'string' ? endpoint : ''
})

// WebSocket 频道
const wsChannel = computed(() => {
    const config = currentPageConfig.value
    if (!config) return ''

    const channel = (config as { wsChannel?: unknown }).wsChannel
    return typeof channel === 'string' ? channel : ''
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
    {
        key: 'realtime',
        label: '实时行情',
        icon: 'Realtime',
        eyebrow: 'live tape',
        description: '监控实时行情、成交结构与市场横截面的最新变化。'
    },
    {
        key: 'technical',
        label: '技术分析',
        icon: 'TechnicalAnalysis',
        eyebrow: 'signal study',
        description: '围绕指标、形态与异动样本做快速技术研判。'
    }
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

const activeTabMeta = computed(() => mainTabs.find((tab) => tab.key === activeTab.value) || mainTabs[0])
const requestTraceId = computed(() => 'N/A')
const syncLabel = computed(() => loading.value ? '行情同步中' : '实时快照')
const marketStatusLabel = computed(() => loading.value ? '同步中' : '交易中')
const selectedMarketLabel = computed(() => marketOptions.find((item) => item.value === selectedMarket.value)?.label || '上海')
const quoteCountLabel = computed(() => `${realtimeQuotes.value.length}`)
const risingCountLabel = computed(() => `${realtimeQuotes.value.filter((item) => item.change > 0).length}`)
const fallingCountLabel = computed(() => `${realtimeQuotes.value.filter((item) => item.change < 0).length}`)
const apiStatusLabel = computed(() => apiEndpoint.value || 'N/A')
const wsChannelLabel = computed(() => wsChannel.value || 'N/A')
const activeSortLabel = computed(() => sortOptions.find((item) => item.key === activeSort.value)?.label || '代码')
const displayQuotes = computed(() => {
    const rows = [...realtimeQuotes.value]

    switch (activeSort.value) {
        case 'change':
            return rows.sort((a, b) => b.change - a.change)
        default:
            return rows.sort((a, b) => String(a.code).localeCompare(String(b.code)))
    }
})

// 根据路由 meta.activeTab 设置初始 tab
onMounted(() => {
    const metaTab = route.meta.activeTab as string | undefined
    if (metaTab) {
        activeTab.value = metaTab
    }
    fetchRealtimeQuotes()
})

// 监听排序或市场变化
watch([selectedMarket, activeSort], () => {
    if (activeTab.value === 'realtime') {
        void fetchRealtimeQuotes()
    }
})

async function fetchRealtimeQuotes() {
    loading.value = true
    errorMsg.value = ''
    try {
        // 调用标准化的 getQuotes
        const quotes = await marketService.getQuotes()
        
        // 数据转换逻辑
        realtimeQuotes.value = quotes.map((item: Record<string, unknown>) => ({
            code: String(item.symbol ?? item.code ?? ''),
            name: String(item.name ?? ''),
            price: Number(item.latest_price ?? item.price ?? 0),
            change: Number(item.change_percent ?? item.change ?? 0),
            volume: formatLargeNumber(item.volume as number | string),
            amount: formatLargeNumber(item.amount as number | string),
            turnover: Number(item.turnover_ratio ?? item.turnover ?? 0),
            pe: Number(item.pe_ratio ?? item.pe ?? 0)
        }))
    } catch (e: unknown) {
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
    void fetchRealtimeQuotes()
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

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.artdeco-market-quotes {
    background: var(--artdeco-bg-global);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    gap: var(--artdeco-spacing-5);
    position: relative;

    &::before {
        content: '';
        position: absolute;
        inset: 0;
        pointer-events: none;
        background:
            radial-gradient(circle at 18% 10%, color-mix(in srgb, var(--artdeco-gold-primary) 5%, transparent) 0%, transparent 34%),
            radial-gradient(circle at 84% 14%, color-mix(in srgb, var(--artdeco-bronze) 4%, transparent) 0%, transparent 28%);
        z-index: 0;
    }
}

.hero-shell,
.stats-strip,
.tabs-shell,
.content-shell {
    position: relative;
    z-index: 1;
}

.artdeco-card-shell {
    border: 1px solid var(--artdeco-border-default);
    background: linear-gradient(
        145deg,
        var(--artdeco-gold-opacity-05),
        color-mix(in srgb, var(--artdeco-bg-global) 92%, transparent)
    );
    box-shadow:
        inset 0 1px 0 color-mix(in srgb, var(--artdeco-fg-primary) 3%, transparent),
        0 var(--artdeco-spacing-2) var(--artdeco-spacing-6) color-mix(in srgb, var(--artdeco-bg-global) 82%, transparent);
}

.hero-shell {
    padding: var(--artdeco-spacing-5);

    &::after {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: calc(var(--artdeco-spacing-20) * 2 + var(--artdeco-spacing-10));
        height: calc(var(--artdeco-spacing-1) / 2);
        background: linear-gradient(
            90deg,
            transparent,
            var(--artdeco-gold-primary),
            var(--artdeco-bronze),
            var(--artdeco-gold-primary),
            transparent
        );
        box-shadow: 0 0 var(--artdeco-spacing-5) color-mix(in srgb, var(--artdeco-gold-primary) 45%, transparent);
    }
}

.hero-rail,
.tabs-shell-header,
.content-shell-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: var(--artdeco-spacing-4);
    flex-wrap: wrap;
}

.hero-copy,
.tabs-shell-copy,
.content-shell-copy,
.header-content {
    display: flex;
    flex-direction: column;
    gap: var(--artdeco-spacing-2);
}

.hero-eyebrow,
.tabs-shell-eyebrow,
.content-shell-kicker {
    font-size: var(--artdeco-text-xs);
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--artdeco-fg-muted);
    font-family: var(--artdeco-font-mono);
}

.hero-meta,
.tabs-shell-trace,
.content-shell-meta {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-3);
    flex-wrap: wrap;
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-xs);
    color: var(--artdeco-fg-muted);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
}

.hero-actions {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-3);
}

.time-display {
    display: flex;
    flex-direction: column;
    gap: var(--artdeco-spacing-1);
}

.time-label {
    font-size: var(--artdeco-text-xs);
    text-transform: uppercase;
    color: var(--artdeco-fg-muted);
    letter-spacing: var(--artdeco-tracking-wide);
}

.time-value {
    font-family: var(--artdeco-font-mono);
    color: var(--artdeco-gold-primary);
}

.stats-strip {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: var(--artdeco-spacing-3);
    padding: var(--artdeco-spacing-4);
}

.tabs-shell {
    padding: var(--artdeco-spacing-4);
}

.tabs-shell-title,
.content-shell-title {
    margin: 0;
    color: var(--artdeco-gold-primary);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
}

.tabs-shell-title {
    font-family: var(--artdeco-font-display);
    font-size: var(--artdeco-text-2xl);
}

.tabs-shell-subtitle {
    margin: 0;
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-sm);
    max-width: calc(var(--artdeco-spacing-32) * 3 + var(--artdeco-spacing-20));
    line-height: var(--artdeco-leading-relaxed);
}

.main-tabs {
    display: flex;
    gap: var(--artdeco-spacing-2);
    margin-top: var(--artdeco-spacing-4);
    border-bottom: calc(var(--artdeco-spacing-px) * 2) solid var(--artdeco-gold-opacity-10);
    padding-bottom: var(--artdeco-spacing-2);
    flex-wrap: wrap;
}

.main-tab {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-2);
    padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
    background: var(--artdeco-bg-card);
    border: 1px solid var(--artdeco-border-default);
    color: var(--artdeco-fg-primary);
    cursor: pointer;
    transition:
        border-color var(--artdeco-transition-base),
        background-color var(--artdeco-transition-base),
        color var(--artdeco-transition-base),
        box-shadow var(--artdeco-transition-base),
        transform var(--artdeco-transition-base);

    .tab-icon {
        flex-shrink: 0;
    }

    &:hover {
        color: var(--artdeco-gold-light);
        border-color: var(--artdeco-gold-primary);
        background: var(--artdeco-gold-opacity-05);
        transform: translateY(calc(var(--artdeco-spacing-1) / -2));
    }

    &:focus-visible {
        outline: none;
        border-color: var(--artdeco-border-hover);
        box-shadow: 0 0 0 1px var(--artdeco-border-hover);
    }

    &.active {
        color: var(--artdeco-gold-primary);
        border-color: var(--artdeco-border-accent);
        background: var(--artdeco-gold-opacity-08);
        box-shadow: var(--artdeco-glow-subtle);
    }
}

.content-shell {
    padding: var(--artdeco-spacing-5);
}

.content-shell-title {
    font-family: var(--artdeco-font-display);
    font-size: var(--artdeco-text-xl);
}

.tab-content {
    margin-top: var(--artdeco-spacing-4);
}

.tab-panel {
    min-height: calc(var(--artdeco-spacing-px) * 520);
}

.realtime-controls,
.technical-controls {
    display: flex;
    gap: var(--artdeco-spacing-4);
    align-items: flex-end;
    margin-bottom: var(--artdeco-spacing-6);
    background: var(--artdeco-bg-card);
    padding: var(--artdeco-spacing-4);
    border: 1px solid var(--artdeco-border-gold-subtle);
}

.sort-controls {
    display: flex;
    gap: var(--artdeco-spacing-2);
    flex-wrap: wrap;
}

.sort-btn {
    padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
    background: var(--artdeco-bg-base);
    border: 1px solid var(--artdeco-border-default);
    color: var(--artdeco-fg-muted);
    cursor: pointer;
    transition: all var(--artdeco-transition-base);

    &.active,
    &:hover {
        color: var(--artdeco-gold-primary);
        border-color: var(--artdeco-gold-primary);
    }
}

.analysis-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: var(--artdeco-spacing-4);
}

.indicators-grid,
.patterns-list,
.abnormal-list {
    display: flex;
    flex-direction: column;
    gap: var(--artdeco-spacing-3);
}

.indicator-item,
.pattern-item,
.abnormal-item {
    padding: var(--artdeco-spacing-3);
    border: 1px solid var(--artdeco-gold-opacity-10);
    background: var(--artdeco-bg-card);
}

.indicator-name,
.pattern-name,
.stock-name {
    color: var(--artdeco-fg-primary);
}

.indicator-value,
.stock-code {
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-mono);
}

.indicator-signal.rise,
.abnormal-change.rise {
    color: var(--artdeco-rise);
}

.indicator-signal.fall,
.abnormal-change.fall {
    color: var(--artdeco-down);
}

.empty-state {
    min-height: calc(var(--artdeco-spacing-px) * 280);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--artdeco-spacing-3);
    color: var(--artdeco-fg-muted);
}

.error-detail {
    color: var(--artdeco-down);
}

.fade-enter-active,
.fade-leave-active {
    transition: opacity var(--artdeco-transition-base);
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0%;
}

@media (width <= var(--artdeco-breakpoint-lg)) {
    .stats-strip {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .analysis-grid {
        grid-template-columns: minmax(0, 1fr);
    }
}

@media (width <= var(--artdeco-breakpoint-md)) {
    .stats-strip {
        grid-template-columns: minmax(0, 1fr);
    }

    .main-tab {
        width: 100%;
        justify-content: flex-start;
    }

    .realtime-controls,
    .technical-controls {
        flex-direction: column;
        align-items: stretch;
    }
}
</style>
