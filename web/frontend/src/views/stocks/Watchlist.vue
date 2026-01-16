<template>
    <div class="watchlist-container">
        <!-- Page Header -->
        <div class="page-header">
            <div class="header-title-section">
                <h1 class="page-title">
                    <el-icon><Star /></el-icon>
                    WATCHLIST MANAGEMENT
                </h1>
                <p class="page-subtitle">PERSONAL STOCK WATCHLIST AND PORTFOLIO TRACKING</p>
            </div>
            <div class="header-actions">
                <el-button type="primary" @click="refreshAllData" :loading="loading">
                    <template #icon>
                        <RefreshRight />
                    </template>
                    REFRESH ALL
                </el-button>
            </div>
        </div>

        <!-- Overview Section -->
        <div class="overview-section">
            <el-card class="overview-card">
                <div class="overview-grid">
                    <div class="overview-item">
                        <div class="overview-icon">📊</div>
                        <div class="overview-data">
                            <div class="overview-value">{{ watchlistStats.totalStocks }}</div>
                            <div class="overview-label">Total Stocks</div>
                        </div>
                    </div>
                    <div class="overview-item">
                        <div class="overview-icon">📈</div>
                        <div class="overview-data">
                            <div class="overview-value">{{ watchlistStats.gainers }}</div>
                            <div class="overview-label">Gainers</div>
                        </div>
                    </div>
                    <div class="overview-item">
                        <div class="overview-icon">📉</div>
                        <div class="overview-data">
                            <div class="overview-value">{{ watchlistStats.losers }}</div>
                            <div class="overview-label">Losers</div>
                        </div>
                    </div>
                    <div class="overview-item">
                        <div class="overview-icon">💰</div>
                        <div class="overview-data">
                            <div class="overview-value">¥{{ formatNumber(watchlistStats.totalValue) }}</div>
                            <div class="overview-label">Total Value</div>
                        </div>
                    </div>
                </div>
            </el-card>
        </div>

        <!-- Controls Section -->
        <div class="controls-section">
            <el-card class="controls-card">
                <div class="controls-content">
                    <div class="search-section">
                        <el-input v-model="searchQuery" placeholder="Search stocks..." class="search-input" clearable>
                            <template #prefix>
                                <el-icon><Search /></el-icon>
                            </template>
                        </el-input>
                    </div>
                    <div class="filter-section">
                        <el-select v-model="sortBy" class="sort-select" placeholder="Sort by">
                            <el-option label="Symbol" value="symbol" />
                            <el-option label="Name" value="name" />
                            <el-option label="Price" value="price" />
                            <el-option label="Change" value="change" />
                        </el-select>
                        <el-select v-model="filterBy" class="filter-select" placeholder="Filter">
                            <el-option label="All" value="all" />
                            <el-option label="Favorites" value="favorites" />
                            <el-option label="Gainers" value="gainers" />
                            <el-option label="Losers" value="losers" />
                        </el-select>
                    </div>
                    <div class="view-section">
                        <el-radio-group v-model="viewMode">
                            <el-radio-button label="table">Table</el-radio-button>
                            <el-radio-button label="cards">Cards</el-radio-button>
                        </el-radio-group>
                    </div>
                </div>
            </el-card>
        </div>

        <!-- Content Section -->
        <div class="content-section">
            <el-card class="table-card">
                <template #header>
                    <div class="table-header">
                        <span class="card-title">MY WATCHLIST</span>
                        <span class="stock-count">{{ filteredStocks.length }} stocks</span>
                    </div>
                </template>

                <!-- Table View -->
                <el-table
                    v-if="viewMode === 'table'"
                    :data="paginatedStocks"
                    class="watchlist-table"
                    style="width: 100%"
                >
                    <el-table-column prop="symbol" label="Symbol" width="120">
                        <template #default="{ row }">
                            <div class="symbol-cell">
                                <span class="stock-symbol">{{ row.symbol }}</span>
                                <el-button
                                    :icon="row.favorite ? Star : undefined"
                                    circle
                                    size="small"
                                    class="favorite-btn"
                                    :class="{ 'is-favorite': row.favorite }"
                                    @click="toggleFavorite(row)"
                                />
                            </div>
                        </template>
                    </el-table-column>
                    <el-table-column prop="name" label="Name" width="200">
                        <template #default="{ row }">
                            <span class="stock-name">{{ row.name }}</span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="price" label="Price" width="120" align="right">
                        <template #default="{ row }">
                            <span class="price-value">¥{{ row.price.toFixed(2) }}</span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="change" label="Change" width="100" align="right">
                        <template #default="{ row }">
                            <span class="change-value" :class="{ positive: row.change > 0, negative: row.change < 0 }">
                                {{ row.change > 0 ? '+' : '' }}{{ row.change.toFixed(2) }}
                            </span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="changePercent" label="Change %" width="120" align="right">
                        <template #default="{ row }">
                            <span
                                class="change-percent"
                                :class="{ positive: row.changePercent > 0, negative: row.changePercent < 0 }"
                            >
                                {{ row.changePercent > 0 ? '+' : '' }}{{ row.changePercent.toFixed(2) }}%
                            </span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="volume" label="Volume" width="120" align="right">
                        <template #default="{ row }">
                            <span class="volume-value">{{ formatNumber(row.volume) }}</span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="marketCap" label="Market Cap" width="120" align="right">
                        <template #default="{ row }">
                            <span class="market-cap-value">{{ formatNumber(row.marketCap) }}</span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="pe" label="P/E" width="100" align="right">
                        <template #default="{ row }">
                            <span class="pe-value">{{ row.pe.toFixed(2) }}</span>
                        </template>
                    </el-table-column>
                    <el-table-column label="Actions" width="100" align="center" fixed="right">
                        <template #default="{ row }">
                            <el-button type="danger" size="small" @click="removeFromWatchlist(row)">Remove</el-button>
                        </template>
                    </el-table-column>
                </el-table>

                <!-- Cards View -->
                <div v-else class="cards-container">
                    <div class="cards-grid">
                        <el-card
                            v-for="stock in paginatedStocks"
                            :key="stock.symbol"
                            class="stock-card"
                            @click="viewStockDetail(stock)"
                        >
                            <div class="card-header">
                                <div class="stock-basic">
                                    <span class="stock-symbol">{{ stock.symbol }}</span>
                                    <span class="stock-name">{{ stock.name }}</span>
                                </div>
                                <div class="stock-actions">
                                    <el-button
                                        :icon="stock.favorite ? Star : undefined"
                                        circle
                                        size="small"
                                        @click.stop="toggleFavorite(stock)"
                                    />
                                </div>
                            </div>
                            <div class="card-content">
                                <div class="price-section">
                                    <div class="current-price">¥{{ stock.price.toFixed(2) }}</div>
                                    <div class="price-change">
                                        <span
                                            class="change-value"
                                            :class="{ positive: stock.change > 0, negative: stock.change < 0 }"
                                        >
                                            {{ stock.change > 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}
                                        </span>
                                        <span
                                            class="change-percent"
                                            :class="{
                                                positive: stock.changePercent > 0,
                                                negative: stock.changePercent < 0
                                            }"
                                        >
                                            {{ stock.changePercent > 0 ? '+' : ''
                                            }}{{ stock.changePercent.toFixed(2) }}%
                                        </span>
                                    </div>
                                </div>
                                <div class="stock-metrics">
                                    <div class="metric-item">
                                        <span class="metric-label">Volume</span>
                                        <span class="metric-value">{{ formatNumber(stock.volume) }}</span>
                                    </div>
                                    <div class="metric-item">
                                        <span class="metric-label">Market Cap</span>
                                        <span class="metric-value">{{ formatNumber(stock.marketCap) }}</span>
                                    </div>
                                    <div class="metric-item">
                                        <span class="metric-label">P/E</span>
                                        <span class="metric-value">{{ stock.pe.toFixed(2) }}</span>
                                    </div>
                                </div>
                            </div>
                        </el-card>
                    </div>
                </div>

                <!-- Pagination -->
                <div class="pagination-section">
                    <el-pagination
                        v-model:current-page="currentPage"
                        v-model:page-size="pageSize"
                        :page-sizes="[10, 20, 50, 100]"
                        :total="filteredStocks.length"
                        layout="total, sizes, prev, pager, next, jumper"
                    />
                </div>
            </el-card>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, reactive, computed, onMounted } from 'vue'
    import {
        ElCard,
        ElButton,
        ElTable,
        ElTableColumn,
        ElInput,
        ElSelect,
        ElOption,
        ElRadioGroup,
        ElRadioButton,
        ElMessage
    } from 'element-plus'
    import { Star, RefreshRight, Search } from '@element-plus/icons-vue'

    interface Stock {
        symbol: string
        name: string
        price: number
        change: number
        changePercent: number
        volume: number
        marketCap: number
        pe: number
        favorite: boolean
        group: string
        lastUpdate: string
    }

    // State
    const loading = ref(false)
    const searchQuery = ref('')
    const sortBy = ref('symbol')
    const filterBy = ref('all')
    const viewMode = ref('table')
    const currentPage = ref(1)
    const pageSize = ref(20)

    const watchlistStats = reactive({
        totalStocks: 0,
        gainers: 0,
        losers: 0,
        totalValue: 0
    })

    // Mock watchlist data
    const watchlistStocks = ref<Stock[]>([
        {
            symbol: '000001',
            name: '平安银行',
            price: 12.85,
            change: 0.15,
            changePercent: 1.18,
            volume: 45000000,
            marketCap: 234567890000,
            pe: 8.5,
            favorite: true,
            group: 'favorites',
            lastUpdate: '2025-01-12 15:00:00'
        },
        {
            symbol: '000002',
            name: '万科A',
            price: 18.95,
            change: -0.25,
            changePercent: -1.3,
            volume: 32000000,
            marketCap: 189456789000,
            pe: 12.3,
            favorite: false,
            group: 'favorites',
            lastUpdate: '2025-01-12 15:00:00'
        },
        {
            symbol: '600036',
            name: '招商银行',
            price: 35.6,
            change: 0.8,
            changePercent: 2.3,
            volume: 58000000,
            marketCap: 789123456000,
            pe: 9.2,
            favorite: true,
            group: 'favorites',
            lastUpdate: '2025-01-12 15:00:00'
        }
    ])

    // Computed
    const filteredStocks = computed(() => {
        let stocks = [...watchlistStocks.value]

        // Filter by search query
        if (searchQuery.value) {
            const query = searchQuery.value.toLowerCase()
            stocks = stocks.filter(
                stock => stock.symbol.toLowerCase().includes(query) || stock.name.toLowerCase().includes(query)
            )
        }

        // Filter by category
        if (filterBy.value === 'favorites') {
            stocks = stocks.filter(stock => stock.favorite)
        } else if (filterBy.value === 'gainers') {
            stocks = stocks.filter(stock => stock.change > 0)
        } else if (filterBy.value === 'losers') {
            stocks = stocks.filter(stock => stock.change < 0)
        }

        // Sort
        stocks.sort((a, b) => {
            if (sortBy.value === 'symbol') return a.symbol.localeCompare(b.symbol)
            if (sortBy.value === 'name') return a.name.localeCompare(b.name)
            if (sortBy.value === 'price') return b.price - a.price
            if (sortBy.value === 'change') return b.change - a.change
            return 0
        })

        return stocks
    })

    const paginatedStocks = computed(() => {
        const start = (currentPage.value - 1) * pageSize.value
        const end = start + pageSize.value
        return filteredStocks.value.slice(start, end)
    })

    // Methods
    const refreshAllData = async () => {
        loading.value = true
        try {
            // TODO: Implement actual API call
            await new Promise(resolve => setTimeout(resolve, 1000))

            // Update stats
            watchlistStats.totalStocks = watchlistStocks.value.length
            watchlistStats.gainers = watchlistStocks.value.filter(s => s.change > 0).length
            watchlistStats.losers = watchlistStocks.value.filter(s => s.change < 0).length
            watchlistStats.totalValue = watchlistStocks.value.reduce(
                (sum, stock) => sum + stock.price * stock.volume,
                0
            )

            ElMessage.success('Data refreshed successfully')
        } catch (error) {
            ElMessage.error('Failed to refresh data')
        } finally {
            loading.value = false
        }
    }

    const toggleFavorite = (stock: Stock) => {
        stock.favorite = !stock.favorite
        ElMessage.success(`${stock.symbol} ${stock.favorite ? 'added to' : 'removed from'} favorites`)
    }

    const removeFromWatchlist = (stock: Stock) => {
        const index = watchlistStocks.value.findIndex(s => s.symbol === stock.symbol)
        if (index > -1) {
            watchlistStocks.value.splice(index, 1)
            ElMessage.success(`${stock.symbol} removed from watchlist`)
        }
    }

    const viewStockDetail = (stock: Stock) => {
        ElMessage.info(`View details for ${stock.symbol}`)
    }

    const formatNumber = (num: number): string => {
        if (num >= 100000000) {
            return (num / 100000000).toFixed(2) + 'B'
        } else if (num >= 10000) {
            return (num / 10000).toFixed(2) + 'W'
        }
        return num.toLocaleString()
    }

    // Lifecycle
    onMounted(() => {
        refreshAllData()
    })
</script>

<style scoped lang="scss">
    @import '@/styles/theme-tokens.scss';

    .watchlist-container {
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

    // Overview Section
    .overview-section {
        .overview-card {
            :deep(.el-card__body) {
                padding: var(--spacing-lg);
            }
        }

        .overview-grid {
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

        .overview-item {
            display: flex;
            align-items: center;
            gap: var(--spacing-md);
            padding: var(--spacing-md);
            background: var(--color-bg-secondary);
            border-radius: var(--border-radius-md);

            .overview-icon {
                font-size: var(--font-size-2xl);
                width: 48px;
                height: 48px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: var(--color-accent-alpha-90);
                border-radius: var(--border-radius-md);
            }

            .overview-data {
                flex: 1;

                .overview-value {
                    font-family: var(--font-family-mono);
                    font-size: var(--font-size-xl);
                    font-weight: 700;
                    color: var(--color-text-primary);
                    margin-bottom: var(--spacing-xs);
                }

                .overview-label {
                    font-family: var(--font-family-sans);
                    font-size: var(--font-size-xs);
                    color: var(--color-text-tertiary);
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                    font-weight: 600;
                }
            }
        }
    }

    // Controls Section
    .controls-section {
        .controls-card {
            :deep(.el-card__body) {
                padding: var(--spacing-lg);
            }
        }

        .controls-content {
            display: flex;
            align-items: center;
            gap: var(--spacing-lg);
            flex-wrap: wrap;

            .search-section {
                .search-input {
                    width: 250px;
                }
            }

            .filter-section {
                display: flex;
                gap: var(--spacing-md);

                .sort-select,
                .filter-select {
                    width: 140px;
                }
            }

            .view-section {
                .el-radio-group {
                    :deep(.el-radio-button__inner) {
                        border-radius: var(--border-radius-sm);
                    }
                }
            }
        }
    }

    // Content Section
    .content-section {
        .table-card {
            :deep(.el-card__header) {
                background: transparent;
                border-bottom: 1px solid var(--color-border);
                padding: var(--spacing-md) var(--spacing-lg);
            }

            :deep(.el-card__body) {
                padding: 0;
            }
        }

        .table-header {
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

            .stock-count {
                font-family: var(--font-family-mono);
                font-size: var(--font-size-xs);
                color: var(--color-text-tertiary);
            }
        }

        .pagination-section {
            display: flex;
            justify-content: center;
            padding: var(--spacing-lg);
            border-top: 1px solid var(--color-border);
        }
    }

    // Watchlist Table
    .watchlist-table {
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

        .symbol-cell {
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);

            .stock-symbol {
                font-family: var(--font-family-mono);
                font-weight: 600;
                color: var(--color-accent);
            }

            .favorite-btn {
                padding: 0;
                font-size: var(--font-size-sm);

                &.is-favorite {
                    color: #f5c71a;
                }
            }
        }

        .stock-name {
            font-family: var(--font-family-sans);
            font-weight: 500;
        }

        .price-value {
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

        .volume-value,
        .market-cap-value,
        .pe-value {
            font-family: var(--font-family-mono);
        }
    }

    // Cards View
    .cards-container {
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: var(--spacing-lg);
        }

        .stock-card {
            cursor: pointer;
            transition: all 0.2s ease;

            &:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px var(--color-accent-alpha-50);
            }

            :deep(.el-card__body) {
                padding: var(--spacing-lg);
            }
        }

        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: var(--spacing-md);

            .stock-basic {
                display: flex;
                flex-direction: column;
                gap: var(--spacing-xs);

                .stock-symbol {
                    font-family: var(--font-family-mono);
                    font-size: var(--font-size-lg);
                    font-weight: 600;
                    color: var(--color-accent);
                }

                .stock-name {
                    font-family: var(--font-family-sans);
                    font-size: var(--font-size-sm);
                    color: var(--color-text-primary);
                }
            }

            .stock-actions {
                display: flex;
                gap: var(--spacing-sm);
            }
        }

        .card-content {
            .price-section {
                margin-bottom: var(--spacing-lg);

                .current-price {
                    font-family: var(--font-family-mono);
                    font-size: var(--font-size-2xl);
                    font-weight: 700;
                    color: var(--color-text-primary);
                    margin-bottom: var(--spacing-xs);
                }

                .price-change {
                    display: flex;
                    gap: var(--spacing-sm);

                    .change-value,
                    .change-percent {
                        font-family: var(--font-family-mono);
                        font-size: var(--font-size-sm);
                        font-weight: 600;

                        &.positive {
                            color: var(--color-stock-up);
                        }

                        &.negative {
                            color: var(--color-stock-down);
                        }
                    }
                }
            }

            .stock-metrics {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: var(--spacing-md);

                .metric-item {
                    display: flex;
                    flex-direction: column;
                    gap: var(--spacing-xs);

                    .metric-label {
                        font-family: var(--font-family-sans);
                        font-size: var(--font-size-xs);
                        color: var(--color-text-tertiary);
                        text-transform: uppercase;
                        letter-spacing: 0.05em;
                    }

                    .metric-value {
                        font-family: var(--font-family-mono);
                        font-size: var(--font-size-sm);
                        font-weight: 600;
                        color: var(--color-text-primary);
                    }
                }
            }
        }
    }

    // Responsive Design
    @media (max-width: 1200px) {
        .watchlist-container {
            padding: var(--spacing-lg);
            gap: var(--spacing-lg);
        }

        .overview-grid {
            grid-template-columns: repeat(2, 1fr);
        }

        .controls-content {
            flex-direction: column;
            align-items: stretch;
            gap: var(--spacing-md);

            .search-section,
            .filter-section,
            .view-section {
                width: 100%;
            }
        }

        .cards-grid {
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        }
    }

    @media (max-width: 768px) {
        .watchlist-container {
            padding: var(--spacing-md);
            gap: var(--spacing-md);
        }

        .page-title {
            font-size: var(--font-size-xl);
        }

        .overview-grid {
            grid-template-columns: 1fr;
        }

        .cards-grid {
            grid-template-columns: 1fr;
        }

        .card-content .stock-metrics {
            grid-template-columns: 1fr;
        }
    }
</style>
