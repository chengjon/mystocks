<template>
    <div class="tdx-interface-container">
        <!-- Page Header -->
        <div class="page-header">
            <div class="header-title-section">
                <h1 class="page-title">
                    <el-icon><Connection /></el-icon>
                    TDX DATA INTERFACE
                </h1>
                <p class="page-subtitle">TONGDA XIN PROFESSIONAL MARKET DATA SOURCE INTEGRATION</p>
            </div>
            <div class="header-actions">
                <el-button type="primary" @click="refreshAllData" :loading="loading">
                    <template #icon>
                        <RefreshRight />
                    </template>
                    REFRESH ALL
                </el-button>
                <el-tag :type="connectionStatus === 'connected' ? 'success' : 'warning'" size="small">
                    TDX {{ connectionStatus === 'connected' ? 'CONNECTED' : 'CONNECTING' }}
                </el-tag>
            </div>
        </div>

        <!-- Connection Status -->
        <div class="status-section">
            <el-card class="status-card" shadow="never">
                <div class="status-content">
                    <div class="status-item">
                        <div class="status-icon">
                            <el-icon :class="{ connected: connectionStatus === 'connected' }">
                                <Connection />
                            </el-icon>
                        </div>
                        <div class="status-info">
                            <span class="status-label">Connection Status</span>
                            <span class="status-value" :class="{ connected: connectionStatus === 'connected' }">
                                {{
                                    connectionStatus === 'connected'
                                        ? 'Connected to TDX Server'
                                        : 'Attempting to Connect...'
                                }}
                            </span>
                        </div>
                    </div>

                    <div class="status-item">
                        <div class="status-icon">
                            <el-icon>
                                <Timer />
                            </el-icon>
                        </div>
                        <div class="status-info">
                            <span class="status-label">Response Time</span>
                            <span class="status-value">{{ responseTime }}ms</span>
                        </div>
                    </div>

                    <div class="status-item">
                        <div class="status-icon">
                            <el-icon>
                                <DataLine />
                            </el-icon>
                        </div>
                        <div class="status-info">
                            <span class="status-label">Active Sessions</span>
                            <span class="status-value">{{ activeSessions }}</span>
                        </div>
                    </div>
                </div>
            </el-card>
        </div>

        <!-- Main Content Grid -->
        <div class="content-grid">
            <!-- Real-time Quotes Section -->
            <el-card class="quotes-card" shadow="never">
                <template #header>
                    <div class="card-header">
                        <span class="card-title">REAL-TIME QUOTES</span>
                        <div class="header-controls">
                            <el-input
                                v-model="searchSymbol"
                                placeholder="Enter symbol (e.g., 600519)"
                                size="small"
                                clearable
                                class="symbol-input"
                                @keyup.enter="fetchQuote"
                            >
                                <template #prefix>
                                    <Search />
                                </template>
                            </el-input>
                            <el-button type="primary" size="small" @click="fetchQuote" :loading="quoteLoading">
                                QUERY
                            </el-button>
                        </div>
                    </div>
                </template>

                <!-- Current Quote Display -->
                <div v-if="currentQuote" class="quote-display">
                    <div class="quote-header">
                        <div class="stock-info">
                            <span class="stock-code">{{ currentQuote.code }}</span>
                            <span class="stock-name">{{ currentQuote.name || 'Unknown' }}</span>
                            <el-tag :type="currentQuote.status === 'trading' ? 'success' : 'warning'" size="small">
                                {{ currentQuote.status === 'trading' ? 'TRADING' : 'CLOSED' }}
                            </el-tag>
                        </div>
                    </div>

                    <div class="quote-main">
                        <div class="price-section">
                            <div class="current-price" :class="getPriceClass(currentQuote.change_pct)">
                                {{ currentQuote.price?.toFixed(2) || '--' }}
                            </div>
                            <div class="price-change" :class="getPriceClass(currentQuote.change_pct)">
                                <span class="change-value">{{ formatChange(currentQuote.change) }}</span>
                                <span class="change-percent">({{ formatChangePct(currentQuote.change_pct) }})</span>
                            </div>
                        </div>
                    </div>

                    <div class="quote-details">
                        <div class="detail-grid">
                            <div class="detail-item">
                                <span class="label">Open:</span>
                                <span class="value">{{ currentQuote.open?.toFixed(2) || '--' }}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">Prev Close:</span>
                                <span class="value">{{ currentQuote.pre_close?.toFixed(2) || '--' }}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">High:</span>
                                <span class="value">{{ currentQuote.high?.toFixed(2) || '--' }}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">Low:</span>
                                <span class="value">{{ currentQuote.low?.toFixed(2) || '--' }}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">Volume:</span>
                                <span class="value">{{ formatVolume(currentQuote.volume) }}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">Amount:</span>
                                <span class="value">{{ formatAmount(currentQuote.amount) }}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Bid/Ask Spread -->
                    <div class="bid-ask-section">
                        <h4 class="section-title">Bid/Ask Spread</h4>
                        <div class="bid-ask-grid">
                            <div class="bid-ask-item ask">
                                <span class="level">Sell 1</span>
                                <span class="price">{{ currentQuote.ask1?.toFixed(2) || '--' }}</span>
                                <span class="volume">{{ formatVolume(currentQuote.ask1_volume, true) }}</span>
                            </div>
                            <div class="bid-ask-item bid">
                                <span class="level">Buy 1</span>
                                <span class="price">{{ currentQuote.bid1?.toFixed(2) || '--' }}</span>
                                <span class="volume">{{ formatVolume(currentQuote.bid1_volume, true) }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Empty State -->
                <div v-else class="empty-state">
                    <el-empty description="Enter a stock symbol to view real-time quotes" :image-size="80">
                        <template #image>
                            <el-icon size="80" class="placeholder-icon">
                                <Connection />
                            </el-icon>
                        </template>
                    </el-empty>
                </div>
            </el-card>

            <!-- K-Line Chart Section -->
            <el-card class="kline-card" shadow="never">
                <template #header>
                    <div class="card-header">
                        <span class="card-title">K-LINE CHART</span>
                        <div class="header-controls">
                            <el-select
                                v-model="selectedPeriod"
                                placeholder="Period"
                                size="small"
                                class="period-select"
                                @change="changePeriod"
                            >
                                <el-option label="1 Minute" value="1m" />
                                <el-option label="5 Minutes" value="5m" />
                                <el-option label="15 Minutes" value="15m" />
                                <el-option label="30 Minutes" value="30m" />
                                <el-option label="1 Hour" value="1h" />
                                <el-option label="Daily" value="1d" />
                            </el-select>
                            <el-date-picker
                                v-model="chartDateRange"
                                type="daterange"
                                range-separator="to"
                                start-placeholder="Start Date"
                                end-placeholder="End Date"
                                size="small"
                                class="date-picker"
                                @change="changeDateRange"
                            />
                        </div>
                    </div>
                </template>

                <div class="chart-container" v-loading="chartLoading">
                    <div v-if="!searchSymbol" class="no-chart-placeholder">
                        <el-empty description="Select a symbol and period to view K-line chart" :image-size="60" />
                    </div>

                    <div v-else ref="chartContainer" class="kline-chart" :style="{ height: chartHeight }"></div>
                </div>
            </el-card>
        </div>

        <!-- Server Information -->
        <div class="server-info-section">
            <el-card class="server-info-card" shadow="never">
                <template #header>
                    <div class="card-header">
                        <span class="card-title">TDX SERVER INFORMATION</span>
                    </div>
                </template>

                <div class="server-grid">
                    <div class="server-item">
                        <span class="server-label">Primary Server</span>
                        <span class="server-value">{{ primaryServer }}</span>
                        <el-tag type="success" size="small">Active</el-tag>
                    </div>

                    <div class="server-item">
                        <span class="server-label">Backup Servers</span>
                        <span class="server-value">{{ backupServers.length }} configured</span>
                        <el-tag type="info" size="small">Ready</el-tag>
                    </div>

                    <div class="server-item">
                        <span class="server-label">Data Types</span>
                        <span class="server-value">Stocks, Futures, Options</span>
                        <el-tag type="warning" size="small">Multiple</el-tag>
                    </div>

                    <div class="server-item">
                        <span class="server-label">Update Frequency</span>
                        <span class="server-value">Real-time</span>
                        <el-tag type="success" size="small">High</el-tag>
                    </div>
                </div>
            </el-card>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, reactive, onMounted, onUnmounted } from 'vue'
    import {
        ElCard,
        ElButton,
        ElInput,
        ElSelect,
        ElOption,
        ElDatePicker,
        ElTag,
        ElEmpty,
        ElMessage
    } from 'element-plus'
    import { Connection, RefreshRight, Timer, DataLine, Search } from '@element-plus/icons-vue'

    interface TdxQuote {
        code: string
        name: string
        price: number
        change: number
        change_pct: number
        open: number
        pre_close: number
        high: number
        low: number
        volume: number
        amount: number
        ask1: number
        ask1_volume: number
        bid1: number
        bid1_volume: number
        status: 'trading' | 'closed'
    }

    // Reactive data
    const loading = ref(false)
    const quoteLoading = ref(false)
    const chartLoading = ref(false)
    const searchSymbol = ref('600519')
    const selectedPeriod = ref('1d')
    const chartHeight = ref('400px')
    const lastUpdate = ref('')

    // Connection status
    const connectionStatus = ref<'connecting' | 'connected' | 'disconnected'>('connecting')
    const responseTime = ref(0)
    const activeSessions = ref(0)

    // Server information
    const primaryServer = ref('202.108.253.132:7709')
    const backupServers = ref(['202.108.253.133:7709', '202.108.253.134:7709', '61.152.107.141:7709'])

    // Current quote data
    const currentQuote = ref<TdxQuote | null>(null)

    // Chart date range
    const chartDateRange = ref([
        new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 days ago
        new Date().toISOString().split('T')[0]
    ])

    // Methods
    const refreshAllData = async (): Promise<void> => {
        loading.value = true
        try {
            await Promise.all([checkConnectionStatus(), fetchQuote()])
            updateLastUpdateTime()
            ElMessage.success('All data refreshed')
        } catch (error) {
            console.error('Failed to refresh all data:', error)
            ElMessage.error('Failed to refresh data')
        } finally {
            loading.value = false
        }
    }

    const checkConnectionStatus = async (): Promise<void> => {
        try {
            // TODO: Replace with actual TDX connection check API
            // const response = await axios.get('/api/tdx/health')

            // Simulate connection check
            await new Promise(resolve => setTimeout(resolve, 500))

            connectionStatus.value = 'connected'
            responseTime.value = Math.floor(Math.random() * 100) + 50 // 50-150ms
            activeSessions.value = Math.floor(Math.random() * 10) + 1 // 1-10 sessions
        } catch (error) {
            connectionStatus.value = 'disconnected'
            console.error('Connection check failed:', error)
        }
    }

    const fetchQuote = async (): Promise<void> => {
        if (!searchSymbol.value) {
            ElMessage.warning('Please enter a stock symbol')
            return
        }

        quoteLoading.value = true
        try {
            // TODO: Replace with actual TDX quote API
            // const response = await axios.get(`/api/tdx/quote/${searchSymbol.value}`)

            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 300))

            // Mock quote data
            currentQuote.value = {
                code: searchSymbol.value,
                name: searchSymbol.value === '600519' ? '贵州茅台' : 'Sample Stock',
                price: 1850 + Math.random() * 100,
                change: (Math.random() - 0.5) * 20,
                change_pct: (Math.random() - 0.5) * 2,
                open: 1830 + Math.random() * 20,
                pre_close: 1840 + Math.random() * 20,
                high: 1860 + Math.random() * 40,
                low: 1820 + Math.random() * 20,
                volume: Math.floor(Math.random() * 1000000) + 100000,
                amount: Math.floor(Math.random() * 100000000) + 10000000,
                ask1: 1850 + Math.random() * 100 + 0.01,
                ask1_volume: Math.floor(Math.random() * 1000) + 100,
                bid1: 1850 + Math.random() * 100 - 0.01,
                bid1_volume: Math.floor(Math.random() * 1000) + 100,
                status: 'trading'
            }

            updateLastUpdateTime()
        } catch (error) {
            console.error('Failed to fetch quote:', error)
            ElMessage.error('Failed to fetch quote data')
        } finally {
            quoteLoading.value = false
        }
    }

    const changePeriod = (): void => {
        // TODO: Update chart with new period
        loadChartData()
    }

    const changeDateRange = (): void => {
        // TODO: Update chart with new date range
        loadChartData()
    }

    const loadChartData = async (): Promise<void> => {
        if (!searchSymbol.value) return

        chartLoading.value = true
        try {
            // TODO: Implement chart data loading
            // const response = await axios.get('/api/tdx/kline', {
            //   params: {
            //     symbol: searchSymbol.value,
            //     period: selectedPeriod.value,
            //     start_date: chartDateRange.value[0],
            //     end_date: chartDateRange.value[1]
            //   }
            // })

            await new Promise(resolve => setTimeout(resolve, 500))
            // Mock chart loading
        } catch (error) {
            console.error('Failed to load chart data:', error)
        } finally {
            chartLoading.value = false
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

    const getPriceClass = (changePct: number): string => {
        if (changePct > 0) return 'positive'
        if (changePct < 0) return 'negative'
        return 'neutral'
    }

    const formatChange = (change: number): string => {
        if (!change) return '--'
        return (change > 0 ? '+' : '') + change.toFixed(2)
    }

    const formatChangePct = (changePct: number): string => {
        if (!changePct) return '--'
        return (changePct > 0 ? '+' : '') + changePct.toFixed(2) + '%'
    }

    const formatVolume = (volume: number, compact: boolean = false): string => {
        if (!volume) return '--'

        if (compact) {
            if (volume >= 10000) {
                return (volume / 10000).toFixed(1) + '万'
            }
            return volume.toString()
        }

        if (volume >= 100000000) {
            return (volume / 100000000).toFixed(1) + '亿'
        } else if (volume >= 10000) {
            return (volume / 10000).toFixed(1) + '万'
        }
        return volume.toString()
    }

    const formatAmount = (amount: number): string => {
        if (!amount) return '--'

        if (amount >= 100000000) {
            return (amount / 100000000).toFixed(2) + '亿'
        } else if (amount >= 10000) {
            return (amount / 10000).toFixed(2) + '万'
        }
        return amount.toString()
    }

    // Lifecycle
    onMounted(async () => {
        await checkConnectionStatus()
        if (searchSymbol.value) {
            await fetchQuote()
        }
    })
</script>

<style scoped lang="scss">
    @import '@/styles/theme-tokens.scss';

    .tdx-interface-container {
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

    // Status Section
    .status-section {
        .status-card {
            :deep(.el-card__body) {
                padding: var(--spacing-lg);
            }
        }

        .status-content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: var(--spacing-lg);
        }

        .status-item {
            display: flex;
            align-items: center;
            gap: var(--spacing-md);
            padding: var(--spacing-md);
            background: var(--color-bg-secondary);
            border-radius: var(--border-radius-md);

            .status-icon {
                flex-shrink: 0;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: var(--color-accent-alpha-90);
                border-radius: 50%;

                .el-icon {
                    font-size: var(--font-size-xl);
                    color: var(--color-accent);

                    &.connected {
                        color: var(--color-stock-up);
                    }
                }
            }

            .status-info {
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: var(--spacing-xs);

                .status-label {
                    font-family: var(--font-family-sans);
                    font-size: var(--font-size-xs);
                    color: var(--color-text-tertiary);
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                    font-weight: 600;
                }

                .status-value {
                    font-family: var(--font-family-mono);
                    font-size: var(--font-size-lg);
                    font-weight: 600;
                    color: var(--color-text-primary);

                    &.connected {
                        color: var(--color-stock-up);
                    }
                }
            }
        }
    }

    // Content Grid
    .content-grid {
        display: grid;
        grid-template-columns: 1fr 2fr;
        gap: var(--spacing-lg);

        @media (max-width: 1200px) {
            grid-template-columns: 1fr;
        }
    }

    // Cards
    .quotes-card,
    .kline-card {
        :deep(.el-card__header) {
            background: transparent;
            border-bottom: 1px solid var(--color-border);
            padding: var(--spacing-md) var(--spacing-lg);
        }

        :deep(.el-card__body) {
            padding: var(--spacing-lg);
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

        .header-controls {
            display: flex;
            align-items: center;
            gap: var(--spacing-md);

            .symbol-input {
                width: 200px;
            }

            .period-select,
            .date-picker {
                width: 120px;
            }
        }
    }

    // Quote Display
    .quote-display {
        .quote-header {
            margin-bottom: var(--spacing-lg);

            .stock-info {
                display: flex;
                align-items: center;
                gap: var(--spacing-md);
                margin-bottom: var(--spacing-sm);

                .stock-code {
                    font-family: var(--font-family-mono);
                    font-size: var(--font-size-xl);
                    font-weight: 700;
                    color: var(--color-accent);
                }

                .stock-name {
                    font-family: var(--font-family-sans);
                    font-size: var(--font-size-lg);
                    color: var(--color-text-primary);
                }
            }
        }

        .quote-main {
            margin-bottom: var(--spacing-lg);

            .price-section {
                .current-price {
                    font-family: var(--font-family-mono);
                    font-size: var(--font-size-4xl);
                    font-weight: 700;
                    margin-bottom: var(--spacing-xs);

                    &.positive {
                        color: var(--color-stock-up);
                    }

                    &.negative {
                        color: var(--color-stock-down);
                    }

                    &.neutral {
                        color: var(--color-text-primary);
                    }
                }

                .price-change {
                    display: flex;
                    gap: var(--spacing-sm);

                    .change-value,
                    .change-percent {
                        font-family: var(--font-family-mono);
                        font-size: var(--font-size-lg);
                        font-weight: 600;

                        &.positive {
                            color: var(--color-stock-up);
                        }

                        &.negative {
                            color: var(--color-stock-down);
                        }

                        &.neutral {
                            color: var(--color-text-primary);
                        }
                    }
                }
            }
        }

        .quote-details {
            margin-bottom: var(--spacing-lg);

            .detail-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: var(--spacing-md);
            }

            .detail-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: var(--spacing-sm) var(--spacing-md);
                background: var(--color-bg-secondary);
                border-radius: var(--border-radius-sm);

                .label {
                    font-family: var(--font-family-sans);
                    font-size: var(--font-size-sm);
                    color: var(--color-text-tertiary);
                    font-weight: 500;
                }

                .value {
                    font-family: var(--font-family-mono);
                    font-size: var(--font-size-sm);
                    color: var(--color-text-primary);
                    font-weight: 600;
                }
            }
        }

        .bid-ask-section {
            .section-title {
                font-family: var(--font-family-sans);
                font-size: var(--font-size-sm);
                font-weight: 600;
                color: var(--color-accent);
                text-transform: uppercase;
                letter-spacing: 0.1em;
                margin: 0 0 var(--spacing-md) 0;
            }

            .bid-ask-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: var(--spacing-md);
            }

            .bid-ask-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: var(--spacing-md);
                border-radius: var(--border-radius-sm);

                &.ask {
                    background: rgba(239, 68, 68, 0.1);
                    border: 1px solid rgba(239, 68, 68, 0.2);
                }

                &.bid {
                    background: rgba(34, 197, 94, 0.1);
                    border: 1px solid rgba(34, 197, 94, 0.2);
                }

                .level {
                    font-family: var(--font-family-sans);
                    font-size: var(--font-size-sm);
                    font-weight: 600;
                    color: var(--color-text-primary);
                }

                .price {
                    font-family: var(--font-family-mono);
                    font-size: var(--font-size-lg);
                    font-weight: 600;
                    color: var(--color-text-primary);
                }

                .volume {
                    font-family: var(--font-family-mono);
                    font-size: var(--font-size-sm);
                    color: var(--color-text-tertiary);
                }
            }
        }
    }

    // Chart Container
    .chart-container {
        position: relative;
        min-height: 300px;

        .no-chart-placeholder {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 300px;
        }

        .kline-chart {
            width: 100%;
            border-radius: var(--border-radius-sm);
        }
    }

    // Empty State
    .empty-state {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 300px;

        .placeholder-icon {
            color: var(--color-text-tertiary);
        }
    }

    // Server Info Section
    .server-info-section {
        .server-info-card {
            :deep(.el-card__header) {
                background: transparent;
                border-bottom: 1px solid var(--color-border);
                padding: var(--spacing-md) var(--spacing-lg);
            }

            :deep(.el-card__body) {
                padding: var(--spacing-lg);
            }
        }

        .server-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: var(--spacing-lg);
        }

        .server-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: var(--spacing-md);
            background: var(--color-bg-secondary);
            border-radius: var(--border-radius-md);

            .server-label {
                font-family: var(--font-family-sans);
                font-size: var(--font-size-sm);
                color: var(--color-text-tertiary);
                font-weight: 500;
            }

            .server-value {
                font-family: var(--font-family-mono);
                font-size: var(--font-size-sm);
                color: var(--color-text-primary);
                font-weight: 600;
            }
        }
    }

    // Responsive Design
    @media (max-width: 1200px) {
        .tdx-interface-container {
            padding: var(--spacing-lg);
            gap: var(--spacing-lg);
        }

        .content-grid {
            grid-template-columns: 1fr;
        }

        .status-content {
            grid-template-columns: 1fr;
        }

        .server-grid {
            grid-template-columns: 1fr;
        }
    }

    @media (max-width: 768px) {
        .tdx-interface-container {
            padding: var(--spacing-md);
            gap: var(--spacing-md);
        }

        .page-title {
            font-size: var(--font-size-xl);
        }

        .quote-details .detail-grid {
            grid-template-columns: 1fr;
        }

        .bid-ask-grid {
            grid-template-columns: 1fr;
        }

        .card-header {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--spacing-md);

            .header-controls {
                width: 100%;

                .symbol-input,
                .period-select,
                .date-picker {
                    width: 100%;
                }
            }
        }
    }
</style>
