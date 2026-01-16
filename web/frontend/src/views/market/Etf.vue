<template>
    <div class="etf-market-container">
        <!-- Page Header -->
        <div class="page-header">
            <div class="header-title-section">
                <h1 class="page-title">
                    <el-icon><TrendCharts /></el-icon>
                    ETF MARKET DATA
                </h1>
                <p class="page-subtitle">EXCHANGE TRADED FUNDS REAL-TIME QUOTES AND ANALYSIS</p>
            </div>
            <div class="header-actions">
                <el-button type="primary" @click="refreshAllData" :loading="loading">
                    <template #icon>
                        <RefreshRight />
                    </template>
                    REFRESH ALL
                </el-button>
                <el-switch
                    v-model="autoRefresh"
                    active-text="AUTO"
                    inactive-text="MANUAL"
                    @change="toggleAutoRefresh"
                />
            </div>
        </div>

        <!-- Market Overview Cards -->
        <div class="overview-cards">
            <el-card class="overview-card">
                <div class="card-content">
                    <div class="card-icon">📈</div>
                    <div class="card-data">
                        <div class="card-value">{{ formatCurrency(etfMarketOverview.totalAssets) }}</div>
                        <div class="card-label">TOTAL ETF ASSETS</div>
                    </div>
                </div>
            </el-card>

            <el-card class="overview-card">
                <div class="card-content">
                    <div class="card-icon">📊</div>
                    <div class="card-data">
                        <div class="card-value">{{ etfMarketOverview.totalProducts }}</div>
                        <div class="card-label">TOTAL PRODUCTS</div>
                    </div>
                </div>
            </el-card>

            <el-card class="overview-card">
                <div class="card-content">
                    <div class="card-icon">💰</div>
                    <div class="card-data">
                        <div class="card-value">{{ formatCurrency(etfMarketOverview.dailyVolume) }}</div>
                        <div class="card-label">DAILY VOLUME</div>
                    </div>
                </div>
            </el-card>

            <el-card class="overview-card">
                <div class="card-content">
                    <div class="card-icon">📈</div>
                    <div class="card-data">
                        <div class="card-value">{{ etfMarketOverview.avgChange.toFixed(2) }}%</div>
                        <div class="card-label">AVG CHANGE</div>
                    </div>
                </div>
            </el-card>
        </div>

        <!-- ETF Categories Tabs -->
        <div class="categories-section">
            <el-tabs v-model="activeCategory" @tab-click="changeCategory">
                <el-tab-pane
                    v-for="category in etfCategories"
                    :key="category.key"
                    :label="category.name"
                    :name="category.key"
                >
                    <div class="category-content">
                        <div class="category-header">
                            <div class="category-info">
                                <h3 class="category-title">{{ category.name }}</h3>
                                <p class="category-description">{{ category.description }}</p>
                                <div class="category-stats">
                                    <span class="stat-item">Products: {{ category.count }}</span>
                                    <span class="stat-item">Avg Volume: {{ formatVolume(category.avgVolume) }}</span>
                                </div>
                            </div>
                            <div class="category-controls">
                                <el-input
                                    v-model="searchQuery"
                                    placeholder="Search ETF..."
                                    size="small"
                                    clearable
                                    class="search-input"
                                    @input="filterETFs"
                                >
                                    <template #prefix>
                                        <Search />
                                    </template>
                                </el-input>
                                <el-select
                                    v-model="sortBy"
                                    placeholder="Sort by"
                                    size="small"
                                    class="sort-select"
                                    @change="sortETFs"
                                >
                                    <el-option label="Name" value="name" />
                                    <el-option label="Price" value="price" />
                                    <el-option label="Change %" value="changePercent" />
                                    <el-option label="Volume" value="volume" />
                                </el-select>
                            </div>
                        </div>

                        <!-- ETF Table -->
                        <el-table :data="filteredETFs" :loading="loading" class="etf-table" stripe border height="600">
                            <el-table-column prop="code" label="CODE" width="100" fixed>
                                <template #default="{ row }">
                                    <span class="etf-code">{{ row.code }}</span>
                                </template>
                            </el-table-column>

                            <el-table-column prop="name" label="NAME" width="200">
                                <template #default="{ row }">
                                    <div class="etf-name-info">
                                        <span class="etf-name">{{ row.name }}</span>
                                        <span class="etf-type">{{ row.type }}</span>
                                    </div>
                                </template>
                            </el-table-column>

                            <el-table-column prop="price" label="PRICE" width="120" align="right">
                                <template #default="{ row }">
                                    <span class="price-value">{{ row.price.toFixed(3) }}</span>
                                </template>
                            </el-table-column>

                            <el-table-column prop="change" label="CHANGE" width="120" align="right">
                                <template #default="{ row }">
                                    <span
                                        class="change-value"
                                        :class="{ positive: row.change >= 0, negative: row.change < 0 }"
                                    >
                                        {{ row.change >= 0 ? '+' : '' }}{{ row.change.toFixed(3) }}
                                    </span>
                                </template>
                            </el-table-column>

                            <el-table-column prop="changePercent" label="CHANGE %" width="120" align="right">
                                <template #default="{ row }">
                                    <span
                                        class="change-percent"
                                        :class="{ positive: row.changePercent >= 0, negative: row.changePercent < 0 }"
                                    >
                                        {{ row.changePercent >= 0 ? '+' : '' }}{{ row.changePercent.toFixed(2) }}%
                                    </span>
                                </template>
                            </el-table-column>

                            <el-table-column prop="volume" label="VOLUME" width="140" align="right">
                                <template #default="{ row }">
                                    <span class="volume-value">{{ formatVolume(row.volume) }}</span>
                                </template>
                            </el-table-column>

                            <el-table-column prop="amount" label="AMOUNT" width="160" align="right">
                                <template #default="{ row }">
                                    <span class="amount-value">{{ formatAmount(row.amount) }}</span>
                                </template>
                            </el-table-column>

                            <el-table-column prop="premium" label="PREMIUM" width="120" align="right">
                                <template #default="{ row }">
                                    <span
                                        class="premium-value"
                                        :class="{ discount: row.premium < 0, premium: row.premium > 0 }"
                                    >
                                        {{ row.premium >= 0 ? '+' : '' }}{{ row.premium.toFixed(2) }}%
                                    </span>
                                </template>
                            </el-table-column>

                            <el-table-column prop="nav" label="NAV" width="120" align="right">
                                <template #default="{ row }">
                                    <span class="nav-value">{{ row.nav.toFixed(4) }}</span>
                                </template>
                            </el-table-column>

                            <el-table-column label="STATUS" width="100" align="center">
                                <template #default="{ row }">
                                    <el-tag :type="row.status === 'trading' ? 'success' : 'warning'" size="small">
                                        {{ row.status === 'trading' ? 'TRADING' : 'SUSPENDED' }}
                                    </el-tag>
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>
                </el-tab-pane>
            </el-tabs>
        </div>

        <!-- Top Performers Section -->
        <div class="performers-section">
            <div class="performers-grid">
                <el-card class="performer-card">
                    <template #header>
                        <div class="card-header">
                            <span class="card-title">TOP GAINERS</span>
                            <span class="timeframe">Last 24h</span>
                        </div>
                    </template>

                    <el-table :data="topGainers" :show-header="false" class="performer-table" size="small">
                        <el-table-column width="50">
                            <template #default="{ $index }">
                                <span class="rank-badge">{{ $index + 1 }}</span>
                            </template>
                        </el-table-column>

                        <el-table-column>
                            <template #default="{ row }">
                                <div class="etf-info">
                                    <span class="etf-code">{{ row.code }}</span>
                                    <span class="etf-short-name">{{ row.name }}</span>
                                </div>
                            </template>
                        </el-table-column>

                        <el-table-column align="right">
                            <template #default="{ row }">
                                <span class="change-percent positive">+{{ row.changePercent.toFixed(2) }}%</span>
                            </template>
                        </el-table-column>
                    </el-table>
                </el-card>

                <el-card class="performer-card">
                    <template #header>
                        <div class="card-header">
                            <span class="card-title">TOP VOLUME</span>
                            <span class="timeframe">Last 24h</span>
                        </div>
                    </template>

                    <el-table :data="topVolume" :show-header="false" class="performer-table" size="small">
                        <el-table-column width="50">
                            <template #default="{ $index }">
                                <span class="rank-badge">{{ $index + 1 }}</span>
                            </template>
                        </el-table-column>

                        <el-table-column>
                            <template #default="{ row }">
                                <div class="etf-info">
                                    <span class="etf-code">{{ row.code }}</span>
                                    <span class="etf-short-name">{{ row.name }}</span>
                                </div>
                            </template>
                        </el-table-column>

                        <el-table-column align="right">
                            <template #default="{ row }">
                                <span class="volume-amount">{{ formatVolume(row.volume) }}</span>
                            </template>
                        </el-table-column>
                    </el-table>
                </el-card>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
    import {
        ElCard,
        ElButton,
        ElTable,
        ElTableColumn,
        ElTabs,
        ElTabPane,
        ElInput,
        ElSelect,
        ElOption,
        ElTag,
        ElSwitch,
        ElMessage
    } from 'element-plus'
    import { TrendCharts, RefreshRight, Search } from '@element-plus/icons-vue'

    // Reactive data
    const loading = ref(false)
    const autoRefresh = ref(false)
    const activeCategory = ref('broad-market')
    const searchQuery = ref('')
    const sortBy = ref('changePercent')
    const refreshInterval = ref<NodeJS.Timeout | null>(null)

    // ETF Market Overview
    const etfMarketOverview = reactive({
        totalAssets: 2500000000000, // 2.5万亿
        totalProducts: 678,
        dailyVolume: 125000000000, // 1250亿
        avgChange: 0.85
    })

    // ETF Categories
    const etfCategories = [
        {
            key: 'broad-market',
            name: 'Broad Market ETFs',
            description: '跟踪主要市场指数的ETF产品',
            count: 156,
            avgVolume: 500000000
        },
        {
            key: 'sector-etfs',
            name: 'Sector ETFs',
            description: '跟踪特定行业板块的ETF产品',
            count: 234,
            avgVolume: 300000000
        },
        {
            key: 'bond-etfs',
            name: 'Bond ETFs',
            description: '跟踪债券市场的ETF产品',
            count: 98,
            avgVolume: 200000000
        },
        {
            key: 'international',
            name: 'International ETFs',
            description: '跟踪海外市场的ETF产品',
            count: 145,
            avgVolume: 150000000
        },
        {
            key: 'commodity-etfs',
            name: 'Commodity ETFs',
            description: '跟踪大宗商品的ETF产品',
            count: 45,
            avgVolume: 100000000
        }
    ]

    // ETF Data by Category
    const etfDataByCategory: Record<string, any[]> = {
        'broad-market': [
            {
                code: '159919',
                name: '沪深300ETF',
                type: 'Stock Index',
                price: 3.245,
                change: 0.025,
                changePercent: 0.78,
                volume: 125000000,
                amount: 405625000,
                premium: 0.12,
                nav: 3.241,
                status: 'trading'
            },
            {
                code: '159941',
                name: '纳指ETF',
                type: 'International',
                price: 2.856,
                change: -0.034,
                changePercent: -1.17,
                volume: 98000000,
                amount: 279888000,
                premium: -0.08,
                nav: 2.858,
                status: 'trading'
            },
            {
                code: '159915',
                name: '创业板ETF',
                type: 'Stock Index',
                price: 2.145,
                change: 0.018,
                changePercent: 0.85,
                volume: 156000000,
                amount: 334620000,
                premium: 0.15,
                nav: 2.142,
                status: 'trading'
            },
            {
                code: '159920',
                name: '恒生ETF',
                type: 'International',
                price: 2.967,
                change: 0.023,
                changePercent: 0.78,
                volume: 67000000,
                amount: 198789000,
                premium: 0.05,
                nav: 2.965,
                status: 'trading'
            },
            {
                code: '159922',
                name: '中证500ETF',
                type: 'Stock Index',
                price: 4.123,
                change: -0.012,
                changePercent: -0.29,
                volume: 89000000,
                amount: 366747000,
                premium: -0.03,
                nav: 4.124,
                status: 'trading'
            }
        ],
        'sector-etfs': [
            {
                code: '159915',
                name: '创业板ETF',
                type: 'Technology',
                price: 2.145,
                change: 0.018,
                changePercent: 0.85,
                volume: 156000000,
                amount: 334620000,
                premium: 0.15,
                nav: 2.142,
                status: 'trading'
            },
            {
                code: '159941',
                name: '新能源ETF',
                type: 'Energy',
                price: 0.856,
                change: -0.014,
                changePercent: -1.61,
                volume: 234000000,
                amount: 200504000,
                premium: -0.12,
                nav: 0.857,
                status: 'trading'
            },
            {
                code: '159919',
                name: '医药ETF',
                type: 'Healthcare',
                price: 0.945,
                change: 0.008,
                changePercent: 0.85,
                volume: 187000000,
                amount: 176715000,
                premium: 0.18,
                nav: 0.943,
                status: 'trading'
            },
            {
                code: '159920',
                name: '银行ETF',
                type: 'Financial',
                price: 0.967,
                change: 0.003,
                changePercent: 0.31,
                volume: 145000000,
                amount: 140215000,
                premium: 0.07,
                nav: 0.966,
                status: 'trading'
            },
            {
                code: '159922',
                name: '消费ETF',
                type: 'Consumer',
                price: 1.123,
                change: -0.005,
                changePercent: -0.44,
                volume: 98000000,
                amount: 110054000,
                premium: -0.02,
                nav: 1.123,
                status: 'trading'
            }
        ],
        'bond-etfs': [
            {
                code: '159901',
                name: '10年国债ETF',
                type: 'Government Bond',
                price: 1.056,
                change: 0.001,
                changePercent: 0.09,
                volume: 45000000,
                amount: 47520000,
                premium: 0.02,
                nav: 1.056,
                status: 'trading'
            },
            {
                code: '159902',
                name: '5年国债ETF',
                type: 'Government Bond',
                price: 1.034,
                change: 0.0,
                changePercent: 0.0,
                volume: 32000000,
                amount: 33088000,
                premium: 0.01,
                nav: 1.034,
                status: 'trading'
            },
            {
                code: '159903',
                name: '企业债ETF',
                type: 'Corporate Bond',
                price: 1.078,
                change: -0.001,
                changePercent: -0.09,
                volume: 28000000,
                amount: 30184000,
                premium: -0.03,
                nav: 1.078,
                status: 'trading'
            }
        ],
        international: [
            {
                code: '159941',
                name: '纳指ETF',
                type: 'US Market',
                price: 2.856,
                change: -0.034,
                changePercent: -1.17,
                volume: 98000000,
                amount: 279888000,
                premium: -0.08,
                nav: 2.858,
                status: 'trading'
            },
            {
                code: '159920',
                name: '恒生ETF',
                type: 'HK Market',
                price: 2.967,
                change: 0.023,
                changePercent: 0.78,
                volume: 67000000,
                amount: 198789000,
                premium: 0.05,
                nav: 2.965,
                status: 'trading'
            },
            {
                code: '159922',
                name: '日经ETF',
                type: 'Japan Market',
                price: 1.845,
                change: 0.015,
                changePercent: 0.82,
                volume: 45000000,
                amount: 82927500,
                premium: 0.12,
                nav: 1.843,
                status: 'trading'
            }
        ],
        'commodity-etfs': [
            {
                code: '159941',
                name: '黄金ETF',
                type: 'Gold',
                price: 3.456,
                change: 0.034,
                changePercent: 0.99,
                volume: 12000000,
                amount: 41472000,
                premium: 0.08,
                nav: 3.453,
                status: 'trading'
            },
            {
                code: '159915',
                name: '原油ETF',
                type: 'Oil',
                price: 2.145,
                change: -0.028,
                changePercent: -1.29,
                volume: 8500000,
                amount: 18232500,
                premium: -0.15,
                nav: 2.148,
                status: 'trading'
            }
        ]
    }

    // Top Performers
    const topGainers = ref([
        { code: '159941', name: '黄金ETF', changePercent: 2.34 },
        { code: '159915', name: '医药ETF', changePercent: 1.87 },
        { code: '159920', name: '新能源ETF', changePercent: 1.65 },
        { code: '159922', name: '消费ETF', changePercent: 1.43 },
        { code: '159919', name: '创业板ETF', changePercent: 1.21 }
    ])

    const topVolume = ref([
        { code: '159919', name: '沪深300ETF', volume: 125000000 },
        { code: '159915', name: '创业板ETF', volume: 98000000 },
        { code: '159941', name: '新能源ETF', volume: 87000000 },
        { code: '159920', name: '医药ETF', volume: 76000000 },
        { code: '159922', name: '消费ETF', volume: 65000000 }
    ])

    // Computed properties
    const currentETFs = computed(() => {
        return etfDataByCategory[activeCategory.value] || []
    })

    const filteredETFs = computed(() => {
        let etfs = [...currentETFs.value]

        // Apply search filter
        if (searchQuery.value) {
            etfs = etfs.filter(
                etf =>
                    etf.code.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                    etf.name.toLowerCase().includes(searchQuery.value.toLowerCase())
            )
        }

        // Apply sorting
        etfs.sort((a, b) => {
            switch (sortBy.value) {
                case 'name':
                    return a.name.localeCompare(b.name)
                case 'price':
                    return b.price - a.price
                case 'changePercent':
                    return b.changePercent - a.changePercent
                case 'volume':
                    return b.volume - a.volume
                default:
                    return 0
            }
        })

        return etfs
    })

    // Methods
    const refreshAllData = async (): Promise<void> => {
        loading.value = true
        try {
            await loadETFData()
            await loadTopPerformers()
            ElMessage.success('ETF data refreshed')
        } catch (error) {
            console.error('Failed to refresh ETF data:', error)
            ElMessage.error('Failed to refresh ETF data')
        } finally {
            loading.value = false
        }
    }

    const loadETFData = async (): Promise<void> => {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500))

        // Update ETF data with random changes
        Object.keys(etfDataByCategory).forEach((category: string) => {
            etfDataByCategory[category].forEach((etf: any) => {
                const priceChange = (Math.random() - 0.5) * 0.1
                etf.price = parseFloat((etf.price + priceChange).toFixed(3))
                etf.change = parseFloat((etf.price - etf.nav).toFixed(3))
                etf.changePercent = parseFloat(((etf.change / etf.nav) * 100).toFixed(2))
                etf.premium = parseFloat(((etf.price / etf.nav - 1) * 100).toFixed(2))
            })
        })
    }

    const loadTopPerformers = async (): Promise<void> => {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 300))

        // Update top performers
        topGainers.value.forEach(item => {
            const change = (Math.random() - 0.3) * 0.5
            item.changePercent = parseFloat((item.changePercent + change).toFixed(2))
        })

        topVolume.value.forEach(item => {
            const change = (Math.random() - 0.5) * 0.2
            item.volume = Math.round(item.volume * (1 + change))
        })
    }

    const changeCategory = (): void => {
        searchQuery.value = ''
        loadETFData()
    }

    const filterETFs = (): void => {
        // Filtering is handled by computed property
    }

    const sortETFs = (): void => {
        // Sorting is handled by computed property
    }

    const toggleAutoRefresh = (): void => {
        if (autoRefresh.value) {
            refreshInterval.value = setInterval(refreshAllData, 30000) // 30 seconds
            ElMessage.success('Auto refresh enabled')
        } else {
            if (refreshInterval.value) {
                clearInterval(refreshInterval.value)
                refreshInterval.value = null
            }
            ElMessage.info('Auto refresh disabled')
        }
    }

    const formatCurrency = (amount: number): string => {
        if (amount >= 1000000000000) {
            return (amount / 1000000000000).toFixed(2) + '万亿'
        } else if (amount >= 100000000) {
            return (amount / 100000000).toFixed(1) + '亿'
        } else if (amount >= 10000) {
            return (amount / 10000).toFixed(1) + '万'
        }
        return amount.toString()
    }

    const formatVolume = (volume: number): string => {
        if (volume >= 100000000) {
            return (volume / 100000000).toFixed(1) + '亿'
        } else if (volume >= 10000) {
            return (volume / 10000).toFixed(1) + '万'
        }
        return volume.toString()
    }

    const formatAmount = (amount: number): string => {
        if (amount >= 100000000) {
            return (amount / 100000000).toFixed(2) + '亿'
        } else if (amount >= 10000) {
            return (amount / 10000).toFixed(2) + '万'
        }
        return amount.toString()
    }

    // Lifecycle
    onMounted(async () => {
        await loadETFData()
        await loadTopPerformers()
    })

    onUnmounted(() => {
        if (refreshInterval.value) {
            clearInterval(refreshInterval.value)
        }
    })
</script>

<style scoped lang="scss">
    @import '@/styles/theme-tokens.scss';

    .etf-market-container {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-lg);
        padding: var(--spacing-lg);
        background: var(--color-bg-primary);
        min-height: 100vh;
    }

    // Header
    .page-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: var(--spacing-lg);
        border-bottom: 2px solid var(--color-border);

        .header-title-section {
            flex: 1;
        }

        .page-title {
            display: flex;
            align-items: center;
            gap: var(--spacing-md);
            font-family: var(--font-family-sans);
            font-size: var(--font-size-2xl);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            color: var(--color-accent);
            margin: 0 0 var(--spacing-sm) 0;
            line-height: 1.2;

            .el-icon {
                font-size: var(--font-size-3xl);
                color: var(--color-accent);
            }
        }

        .page-subtitle {
            font-family: var(--font-family-sans);
            font-size: var(--font-size-xs);
            color: var(--color-text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.2em;
            margin: 0;
            line-height: 1.4;
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: var(--spacing-md);
        }
    }

    // Overview Cards
    .overview-cards {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: var(--spacing-lg);

        @media (max-width: 1200px) {
            grid-template-columns: repeat(2, 1fr);
        }

        @media (max-width: 768px) {
            grid-template-columns: 1fr;
        }
    }

    .overview-card {
        :deep(.el-card__body) {
            padding: var(--spacing-lg);
        }
    }

    .card-content {
        display: flex;
        align-items: center;
        gap: var(--spacing-md);

        .card-icon {
            font-size: var(--font-size-2xl);
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--color-accent-alpha-90);
            border-radius: var(--border-radius-md);
        }

        .card-data {
            flex: 1;

            .card-value {
                font-family: var(--font-family-mono);
                font-size: var(--font-size-xl);
                font-weight: 700;
                color: var(--color-text-primary);
                margin-bottom: var(--spacing-xs);
            }

            .card-label {
                font-family: var(--font-family-sans);
                font-size: var(--font-size-xs);
                color: var(--color-text-tertiary);
                text-transform: uppercase;
                letter-spacing: 0.1em;
                font-weight: 600;
            }
        }
    }

    // Categories Section
    .categories-section {
        :deep(.el-tabs__header) {
            margin: 0 0 var(--spacing-lg) 0;

            .el-tabs__nav-wrap::after {
                display: none;
            }

            .el-tabs__item {
                font-family: var(--font-family-sans);
                font-size: var(--font-size-sm);
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                color: var(--color-text-secondary);
                padding: var(--spacing-md) var(--spacing-lg);

                &.is-active {
                    color: var(--color-accent);
                }

                &:hover {
                    color: var(--color-accent);
                }
            }
        }

        :deep(.el-tabs__content) {
            padding: 0;
        }

        .category-content {
            .category-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: var(--spacing-lg);
                padding-bottom: var(--spacing-md);
                border-bottom: 1px solid var(--color-border);

                .category-info {
                    flex: 1;

                    .category-title {
                        font-family: var(--font-family-sans);
                        font-size: var(--font-size-lg);
                        font-weight: 600;
                        color: var(--color-accent);
                        margin: 0 0 var(--spacing-xs) 0;
                    }

                    .category-description {
                        font-family: var(--font-family-sans);
                        font-size: var(--font-size-sm);
                        color: var(--color-text-secondary);
                        margin: 0 0 var(--spacing-sm) 0;
                    }

                    .category-stats {
                        display: flex;
                        gap: var(--spacing-lg);

                        .stat-item {
                            font-family: var(--font-family-mono);
                            font-size: var(--font-size-xs);
                            color: var(--color-text-tertiary);
                            text-transform: uppercase;
                            letter-spacing: 0.05em;
                        }
                    }
                }

                .category-controls {
                    display: flex;
                    align-items: center;
                    gap: var(--spacing-md);

                    .search-input {
                        width: 200px;
                    }

                    .sort-select {
                        width: 120px;
                    }
                }
            }
        }
    }

    // ETF Table
    .etf-table {
        :deep(.el-table__header-wrapper) {
            background: var(--color-bg-secondary);

            th {
                background: var(--color-bg-secondary) !important;
                border-bottom: 2px solid var(--color-border);
                color: var(--color-text-secondary);
                font-family: var(--font-family-sans);
                font-size: var(--font-size-xs);
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                padding: var(--spacing-md) 0;
            }
        }

        :deep(.el-table__body-wrapper) {
            tr {
                transition: background 0.2s ease;

                &:hover {
                    background: var(--color-accent-alpha-90) !important;
                }

                td {
                    border-bottom: 1px solid var(--color-border);
                    color: var(--color-text-primary);
                    font-family: var(--font-family-mono);
                    font-size: var(--font-size-sm);
                    padding: var(--spacing-md) 0;
                }
            }
        }

        .etf-code {
            font-family: var(--font-family-mono);
            font-weight: 600;
            color: var(--color-accent);
        }

        .etf-name-info {
            display: flex;
            flex-direction: column;
            gap: var(--spacing-xs);

            .etf-name {
                font-family: var(--font-family-sans);
                font-weight: 500;
                color: var(--color-text-primary);
            }

            .etf-type {
                font-family: var(--font-family-sans);
                font-size: var(--font-size-xs);
                color: var(--color-text-tertiary);
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
        }

        .price-value,
        .nav-value {
            font-family: var(--font-family-mono);
            font-weight: 600;
        }

        .change-value,
        .change-percent {
            font-family: var(--font-family-mono);
            font-weight: 600;

            &.positive {
                color: var(--color-stock-up);
            }

            &.negative {
                color: var(--color-stock-down);
            }
        }

        .premium-value {
            font-family: var(--font-family-mono);
            font-weight: 600;

            &.premium {
                color: var(--color-stock-up);
            }

            &.discount {
                color: var(--color-stock-down);
            }
        }

        .volume-value,
        .amount-value {
            font-family: var(--font-family-mono);
        }
    }

    // Performers Section
    .performers-section {
        .performers-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: var(--spacing-lg);

            @media (max-width: 1200px) {
                grid-template-columns: 1fr;
            }
        }

        .performer-card {
            :deep(.el-card__header) {
                background: transparent;
                border-bottom: 1px solid var(--color-border);
                padding: var(--spacing-md) var(--spacing-lg);
            }

            :deep(.el-card__body) {
                padding: 0;
            }
        }

        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: var(--spacing-lg);

            .card-title {
                font-family: var(--font-family-sans);
                font-size: var(--font-size-sm);
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                color: var(--color-accent);
            }

            .timeframe {
                font-family: var(--font-family-mono);
                font-size: var(--font-size-xs);
                color: var(--color-text-tertiary);
            }
        }

        .performer-table {
            :deep(.el-table__body-wrapper) {
                tr {
                    &:hover {
                        background: var(--color-accent-alpha-90) !important;
                    }

                    td {
                        border-bottom: 1px solid var(--color-border);
                        padding: var(--spacing-md) 0;
                    }
                }
            }

            .rank-badge {
                font-family: var(--font-family-mono);
                font-weight: 700;
                color: var(--color-accent);
                font-size: var(--font-size-lg);
                width: 32px;
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: var(--color-accent-alpha-90);
                border-radius: 50%;
            }

            .etf-info {
                display: flex;
                flex-direction: column;
                gap: var(--spacing-xs);

                .etf-code {
                    font-family: var(--font-family-mono);
                    font-weight: 600;
                    color: var(--color-accent);
                    font-size: var(--font-size-sm);
                }

                .etf-short-name {
                    font-family: var(--font-family-sans);
                    font-weight: 500;
                    color: var(--color-text-primary);
                    font-size: var(--font-size-xs);
                }
            }

            .change-percent {
                font-family: var(--font-family-mono);
                font-weight: 600;
                font-size: var(--font-size-sm);

                &.positive {
                    color: var(--color-stock-up);
                }

                &.negative {
                    color: var(--color-stock-down);
                }
            }

            .volume-amount {
                font-family: var(--font-family-mono);
                font-weight: 600;
                font-size: var(--font-size-sm);
                color: var(--color-text-primary);
            }
        }
    }

    // Responsive Design
    @media (max-width: 1200px) {
        .etf-market-container {
            padding: var(--spacing-lg);
            gap: var(--spacing-lg);
        }

        .category-header {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--spacing-md);

            .category-controls {
                width: 100%;

                .search-input,
                .sort-select {
                    width: 100%;
                }
            }
        }

        .performers-grid {
            grid-template-columns: 1fr;
        }
    }

    @media (max-width: 768px) {
        .etf-market-container {
            padding: var(--spacing-md);
            gap: var(--spacing-md);
        }

        .page-title {
            font-size: var(--font-size-xl);
        }

        .overview-cards {
            grid-template-columns: 1fr;
        }

        .category-stats {
            flex-direction: column;
            gap: var(--spacing-xs);
        }
    }
</style>
