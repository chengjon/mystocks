<template>
    <div class="realtime-container">
        <!-- Header -->
        <div class="realtime-header">
            <div class="header-title-section">
                <h1 class="realtime-title">
                    <el-icon><Monitor /></el-icon>
                    REALTIME QUOTES
                </h1>
                <p class="realtime-subtitle">LIVE STOCK & INDEX MARKET DATA MONITORING</p>
            </div>
            <div class="header-actions">
                <el-button
                    type="primary"
                    size="default"
                    @click="handleRefresh"
                    :loading="loading"
                    class="refresh-button"
                >
                    <template #icon>
                        <RefreshRight />
                    </template>
                    REFRESH
                </el-button>
                <el-switch
                    v-model="autoRefresh"
                    active-text="AUTO REFRESH"
                    inactive-text="MANUAL"
                    @change="toggleAutoRefresh"
                    class="auto-refresh-switch"
                />
                <span v-if="lastUpdate" class="last-update">Last: {{ lastUpdate }}</span>
            </div>
        </div>

        <!-- Market Indices Overview -->
        <div class="indices-grid">
            <el-card
                v-for="index in marketIndices"
                :key="index.code"
                class="index-card"
                :class="{ rising: index.change >= 0, falling: index.change < 0 }"
            >
                <div class="index-content">
                    <div class="index-name">{{ index.name }}</div>
                    <div class="index-value">{{ index.value.toFixed(2) }}</div>
                    <div class="index-change">
                        <span class="change-value">
                            {{ index.change >= 0 ? '+' : '' }}{{ index.change.toFixed(2) }}
                        </span>
                        <span class="change-percent">
                            ({{ index.changePercent >= 0 ? '+' : '' }}{{ index.changePercent.toFixed(2) }}%)
                        </span>
                    </div>
                </div>
            </el-card>
        </div>

        <!-- Stock Quotes Section -->
        <el-card class="stock-quotes-card">
            <template #header>
                <div class="card-header">
                    <span class="card-title">STOCK QUOTES</span>
                    <div class="header-controls">
                        <el-input
                            v-model="searchSymbol"
                            placeholder="Search symbol..."
                            size="small"
                            clearable
                            class="search-input"
                            @input="filterStocks"
                        >
                            <template #prefix>
                                <Search />
                            </template>
                        </el-input>
                    </div>
                </div>
            </template>

            <el-table :data="filteredStocks" :loading="loading" class="stock-table" stripe border height="500">
                <el-table-column prop="symbol" label="CODE" width="100" fixed>
                    <template #default="{ row }">
                        <span class="symbol-code">{{ row.symbol }}</span>
                    </template>
                </el-table-column>

                <el-table-column prop="name" label="NAME" width="150">
                    <template #default="{ row }">
                        <span class="stock-name">{{ row.name }}</span>
                    </template>
                </el-table-column>

                <el-table-column prop="price" label="PRICE" width="120" align="right">
                    <template #default="{ row }">
                        <span class="price-value">{{ row.price.toFixed(2) }}</span>
                    </template>
                </el-table-column>

                <el-table-column prop="change" label="CHANGE" width="120" align="right">
                    <template #default="{ row }">
                        <span class="change-value" :class="{ positive: row.change >= 0, negative: row.change < 0 }">
                            {{ row.change >= 0 ? '+' : '' }}{{ row.change.toFixed(2) }}
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

                <el-table-column prop="high" label="HIGH" width="120" align="right">
                    <template #default="{ row }">
                        <span class="high-value">{{ row.high.toFixed(2) }}</span>
                    </template>
                </el-table-column>

                <el-table-column prop="low" label="LOW" width="120" align="right">
                    <template #default="{ row }">
                        <span class="low-value">{{ row.low.toFixed(2) }}</span>
                    </template>
                </el-table-column>

                <el-table-column label="STATUS" width="100" align="center">
                    <template #default="{ row }">
                        <el-tag :type="row.status === 'trading' ? 'success' : 'warning'" size="small">
                            {{ row.status === 'trading' ? 'TRADING' : 'CLOSED' }}
                        </el-tag>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>
    </div>
</template>

<script setup lang="ts">
    import { ref, onMounted, onUnmounted, computed } from 'vue'
    import { ElCard, ElButton, ElTable, ElTableColumn, ElInput, ElSwitch, ElTag, ElMessage } from 'element-plus'
    import { Monitor, RefreshRight, Search } from '@element-plus/icons-vue'
    import axios from 'axios'

    interface MarketIndex {
        code: string
        name: string
        value: number
        change: number
        changePercent: number
    }

    interface StockQuote {
        symbol: string
        name: string
        price: number
        change: number
        changePercent: number
        volume: number
        amount: number
        high: number
        low: number
        status: 'trading' | 'closed'
    }

    const loading = ref(false)
    const autoRefresh = ref(false)
    const lastUpdate = ref('')
    const searchSymbol = ref('')
    const refreshInterval = ref<NodeJS.Timeout | null>(null)

    const marketIndices = ref<MarketIndex[]>([
        {
            code: '000001',
            name: '上证指数',
            value: 3200.5,
            change: 25.3,
            changePercent: 0.8
        },
        {
            code: '399001',
            name: '深证成指',
            value: 10500.8,
            change: -45.2,
            changePercent: -0.43
        },
        {
            code: '399006',
            name: '创业板指',
            value: 2100.3,
            change: 12.5,
            changePercent: 0.6
        }
    ])

    const stockQuotes = ref<StockQuote[]>([
        {
            symbol: '000001',
            name: '平安银行',
            price: 12.85,
            change: 0.15,
            changePercent: 1.18,
            volume: 1250000,
            amount: 16062500,
            high: 12.9,
            low: 12.7,
            status: 'trading'
        },
        {
            symbol: '000002',
            name: '万科A',
            price: 18.95,
            change: -0.25,
            changePercent: -1.3,
            volume: 980000,
            amount: 18591000,
            high: 19.2,
            low: 18.9,
            status: 'trading'
        },
        {
            symbol: '600000',
            name: '浦发银行',
            price: 8.45,
            change: 0.08,
            changePercent: 0.96,
            volume: 2100000,
            amount: 17745000,
            high: 8.48,
            low: 8.4,
            status: 'trading'
        }
    ])

    const filteredStocks = computed(() => {
        if (!searchSymbol.value) {
            return stockQuotes.value
        }
        return stockQuotes.value.filter(
            stock =>
                stock.symbol.toLowerCase().includes(searchSymbol.value.toLowerCase()) ||
                stock.name.toLowerCase().includes(searchSymbol.value.toLowerCase())
        )
    })

    const formatVolume = (volume: number): string => {
        if (volume >= 100000000) {
            return `${(volume / 100000000).toFixed(1)}亿`
        } else if (volume >= 10000) {
            return `${(volume / 10000).toFixed(1)}万`
        }
        return volume.toString()
    }

    const formatAmount = (amount: number): string => {
        if (amount >= 100000000) {
            return `${(amount / 100000000).toFixed(2)}亿`
        } else if (amount >= 10000) {
            return `${(amount / 10000).toFixed(2)}万`
        }
        return amount.toString()
    }

    const loadMarketData = async (): Promise<void> => {
        loading.value = true
        try {
            // TODO: Replace with actual API calls
            // const indicesResponse = await axios.get('/api/market/indices')
            // const stocksResponse = await axios.get('/api/market/stocks')

            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 500))

            // Update market indices with random changes
            marketIndices.value.forEach(index => {
                const change = (Math.random() - 0.5) * 2
                index.change = parseFloat((index.change + change).toFixed(2))
                index.changePercent = parseFloat(((index.change / index.value) * 100).toFixed(2))
            })

            // Update stock quotes with random changes
            stockQuotes.value.forEach(stock => {
                const priceChange = (Math.random() - 0.5) * 0.5
                stock.price = parseFloat((stock.price + priceChange).toFixed(2))
                stock.change = parseFloat((stock.price - stock.low).toFixed(2)) // Simplified
                stock.changePercent = parseFloat(((stock.change / (stock.price - stock.change)) * 100).toFixed(2))
                stock.volume = Math.floor(stock.volume * (0.9 + Math.random() * 0.2))
                stock.amount = stock.price * stock.volume
            })

            updateLastUpdateTime()
        } catch (error) {
            console.error('Failed to load market data:', error)
            ElMessage.error('加载市场数据失败')
        } finally {
            loading.value = false
        }
    }

    const updateLastUpdateTime = (): void => {
        const now = new Date()
        lastUpdate.value = now.toLocaleString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        })
    }

    const handleRefresh = async (): Promise<void> => {
        await loadMarketData()
        ElMessage.success('数据已刷新')
    }

    const toggleAutoRefresh = (): void => {
        if (autoRefresh.value) {
            refreshInterval.value = setInterval(loadMarketData, 5000) // 5 seconds
            ElMessage.success('已开启自动刷新')
        } else {
            if (refreshInterval.value) {
                clearInterval(refreshInterval.value)
                refreshInterval.value = null
            }
            ElMessage.info('已关闭自动刷新')
        }
    }

    const filterStocks = (): void => {
        // Filtering is handled by computed property
    }

    onMounted(() => {
        loadMarketData()
    })

    onUnmounted(() => {
        if (refreshInterval.value) {
            clearInterval(refreshInterval.value)
        }
    })
</script>

<style scoped lang="scss">
    @import '@/styles/theme-tokens.scss';

    .realtime-container {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-lg);
        padding: var(--spacing-lg);
        background: var(--color-bg-primary);
        min-height: 100vh;
    }

    // Header
    .realtime-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: var(--spacing-lg);
        border-bottom: 2px solid var(--color-border);

        .header-title-section {
            flex: 1;
        }

        .realtime-title {
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

        .realtime-subtitle {
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

            .refresh-button {
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }

            .auto-refresh-switch {
                :deep(.el-switch__label) {
                    font-size: var(--font-size-xs);
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                }
            }

            .last-update {
                font-family: var(--font-family-mono);
                font-size: var(--font-size-sm);
                color: var(--color-text-tertiary);
            }
        }
    }

    // Market Indices
    .indices-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: var(--spacing-lg);

        @media (max-width: 1200px) {
            grid-template-columns: repeat(2, 1fr);
        }

        @media (max-width: 768px) {
            grid-template-columns: 1fr;
        }
    }

    .index-card {
        transition: all 0.3s ease;

        &.rising {
            :deep(.el-card__body) {
                border-left: 4px solid var(--color-stock-up);
            }
        }

        &.falling {
            :deep(.el-card__body) {
                border-left: 4px solid var(--color-stock-down);
            }
        }

        :deep(.el-card__body) {
            padding: var(--spacing-lg);
        }
    }

    .index-content {
        text-align: center;

        .index-name {
            font-family: var(--font-family-sans);
            font-size: var(--font-size-sm);
            font-weight: 600;
            color: var(--color-text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: var(--spacing-sm);
        }

        .index-value {
            font-family: var(--font-family-mono);
            font-size: var(--font-size-2xl);
            font-weight: 700;
            color: var(--color-text-primary);
            margin-bottom: var(--spacing-xs);
        }

        .index-change {
            display: flex;
            justify-content: center;
            gap: var(--spacing-sm);

            .change-value {
                font-family: var(--font-family-mono);
                font-size: var(--font-size-lg);
                font-weight: 600;
            }

            .change-percent {
                font-family: var(--font-family-sans);
                font-size: var(--font-size-sm);
                color: var(--color-text-tertiary);
            }
        }
    }

    // Stock Quotes Card
    .stock-quotes-card {
        background: linear-gradient(135deg, var(--color-bg-secondary) 0%, var(--color-bg-elevated) 100%);
        border: 1px solid var(--color-border);
        border-radius: var(--border-radius-md);

        :deep(.el-card__header) {
            background: transparent;
            border-bottom: 1px solid var(--color-border);
            padding: var(--spacing-md) var(--spacing-lg);
        }

        :deep(.el-card__body) {
            padding: 0;
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

            .header-controls {
                display: flex;
                align-items: center;
                gap: var(--spacing-md);

                .search-input {
                    width: 200px;
                }
            }
        }
    }

    // Stock Table
    .stock-table {
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

        .symbol-code {
            font-family: var(--font-family-mono);
            font-weight: 600;
            color: var(--color-accent);
        }

        .stock-name {
            font-family: var(--font-family-sans);
            font-weight: 500;
        }

        .price-value,
        .high-value,
        .low-value {
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
        .amount-value {
            font-family: var(--font-family-mono);
        }
    }

    // Responsive Design
    @media (max-width: 1200px) {
        .realtime-container {
            padding: var(--spacing-lg);
            gap: var(--spacing-lg);
        }

        .indices-grid {
            grid-template-columns: repeat(2, 1fr);
        }

        .realtime-header {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--spacing-md);

            .header-actions {
                width: 100%;
                justify-content: space-between;
            }
        }
    }

    @media (max-width: 768px) {
        .realtime-container {
            padding: var(--spacing-md);
            gap: var(--spacing-md);
        }

        .indices-grid {
            grid-template-columns: 1fr;
        }

        .realtime-header {
            .realtime-title {
                font-size: var(--font-size-xl);
            }

            .realtime-subtitle {
                font-size: var(--font-size-xs);
            }

            .header-actions {
                flex-direction: column;
                gap: var(--spacing-sm);

                .last-update {
                    order: -1;
                }
            }
        }

        .card-header {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--spacing-md);

            .header-controls {
                width: 100%;

                .search-input {
                    width: 100%;
                }
            }
        }
    }
</style>
