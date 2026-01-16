<template>
    <div class="technical-analysis">
        <!-- Page Header -->
        <div class="page-header">
            <div class="header-title-section">
                <h1 class="page-title">
                    <el-icon><DataLine /></el-icon>
                    TECHNICAL INDICATORS
                </h1>
                <p class="page-subtitle">REAL-TIME TECHNICAL ANALYSIS & CHART INDICATORS</p>
            </div>
            <div class="header-actions">
                <el-button type="primary" @click="refreshData" :loading="loading">
                    <template #icon>
                        <RefreshRight />
                    </template>
                    REFRESH DATA
                </el-button>
                <el-button @click="showIndicatorPanel = true">
                    <template #icon>
                        <Setting />
                    </template>
                    INDICATORS
                </el-button>
            </div>
        </div>

        <!-- Toolbar Section -->
        <div class="toolbar-section">
            <div class="toolbar-content">
                <!-- Stock Search -->
                <div class="search-section">
                    <el-input
                        v-model="selectedSymbol"
                        placeholder="Enter stock symbol (e.g., 600519)"
                        clearable
                        class="symbol-input"
                        @change="handleSymbolChange"
                    >
                        <template #prefix>
                            <Search />
                        </template>
                    </el-input>
                </div>

                <!-- Date Range Picker -->
                <div class="date-section">
                    <el-date-picker
                        v-model="dateRange"
                        type="daterange"
                        range-separator="to"
                        start-placeholder="Start Date"
                        end-placeholder="End Date"
                        format="YYYY-MM-DD"
                        value-format="YYYY-MM-DD"
                        class="date-picker"
                        :shortcuts="dateShortcuts"
                        @change="handleDateRangeChange"
                    />
                </div>

                <!-- Time Period Selector -->
                <div class="period-section">
                    <el-radio-group
                        v-model="selectedPeriod"
                        size="small"
                        @change="handlePeriodChange"
                        class="period-selector"
                    >
                        <el-radio-button label="1d">1D</el-radio-button>
                        <el-radio-button label="5d">5D</el-radio-button>
                        <el-radio-button label="1M">1M</el-radio-button>
                        <el-radio-button label="3M">3M</el-radio-button>
                        <el-radio-button label="6M">6M</el-radio-button>
                        <el-radio-button label="1Y">1Y</el-radio-button>
                    </el-radio-group>
                </div>

                <!-- Chart Type Selector -->
                <div class="chart-type-section">
                    <el-select
                        v-model="chartType"
                        placeholder="Chart Type"
                        size="small"
                        class="chart-type-select"
                        @change="handleChartTypeChange"
                    >
                        <el-option label="Candlestick" value="candlestick" />
                        <el-option label="Line" value="line" />
                        <el-option label="Area" value="area" />
                    </el-select>
                </div>
            </div>
        </div>

        <!-- Main Chart Section -->
        <div class="chart-section">
            <el-card class="main-chart-card" shadow="never">
                <template #header>
                    <div class="chart-header">
                        <div class="chart-title">
                            <span class="symbol-display">{{ selectedSymbol || 'No Symbol Selected' }}</span>
                            <span class="symbol-name">{{ symbolName }}</span>
                        </div>
                        <div class="chart-info">
                            <el-tag type="info" size="small">{{ selectedPeriod.toUpperCase() }}</el-tag>
                            <span class="last-update" v-if="lastUpdate">Updated: {{ lastUpdate }}</span>
                        </div>
                    </div>
                </template>

                <!-- Chart Container -->
                <div class="chart-container" v-loading="loading">
                    <div v-if="!selectedSymbol" class="no-data-placeholder">
                        <el-empty description="Please enter a stock symbol to view technical analysis" :image-size="80">
                            <template #image>
                                <el-icon size="80" class="placeholder-icon"><DataLine /></el-icon>
                            </template>
                        </el-empty>
                    </div>

                    <div v-else-if="!chartData || !chartData.ohlcv" class="no-data-placeholder">
                        <el-empty description="No chart data available for this symbol" :image-size="80" />
                    </div>

                    <div v-else ref="chartContainer" class="kline-chart" :style="{ height: chartHeight }"></div>
                </div>
            </el-card>
        </div>

        <!-- Indicators Overview -->
        <div class="indicators-section" v-if="selectedIndicators.length > 0">
            <el-card class="indicators-card" shadow="never">
                <template #header>
                    <div class="card-header">
                        <span class="card-title">ACTIVE INDICATORS</span>
                        <span class="indicators-count">{{ selectedIndicators.length }} active</span>
                    </div>
                </template>

                <div class="indicators-grid">
                    <div v-for="indicator in selectedIndicators" :key="indicator.name" class="indicator-item">
                        <div class="indicator-info">
                            <span class="indicator-name">{{ indicator.displayName }}</span>
                            <span class="indicator-params" v-if="indicator.params">
                                ({{ formatParams(indicator.params) }})
                            </span>
                        </div>
                        <div class="indicator-actions">
                            <el-button type="danger" size="small" text @click="removeIndicator(indicator.name)">
                                Remove
                            </el-button>
                        </div>
                    </div>
                </div>
            </el-card>
        </div>

        <!-- Technical Summary -->
        <div class="summary-section" v-if="chartData && chartData.ohlcv">
            <el-card class="summary-card" shadow="never">
                <template #header>
                    <div class="card-header">
                        <span class="card-title">TECHNICAL SUMMARY</span>
                    </div>
                </template>

                <div class="summary-grid">
                    <div class="summary-item">
                        <span class="summary-label">Data Points</span>
                        <span class="summary-value">{{ chartData.ohlcv.dates?.length || 0 }}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Time Range</span>
                        <span class="summary-value">
                            {{ dateRange?.[0] || 'N/A' }} to {{ dateRange?.[1] || 'N/A' }}
                        </span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Indicators</span>
                        <span class="summary-value">{{ selectedIndicators.length }}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Last Price</span>
                        <span class="summary-value">
                            {{ chartData.ohlcv.close?.[chartData.ohlcv.close.length - 1]?.toFixed(2) || 'N/A' }}
                        </span>
                    </div>
                </div>
            </el-card>
        </div>

        <!-- Indicator Selection Panel -->
        <el-drawer v-model="showIndicatorPanel" title="Technical Indicators" size="400px" :close-on-click-modal="false">
            <div class="indicator-drawer">
                <div class="indicator-categories">
                    <div v-for="category in indicatorCategories" :key="category.key" class="category-section">
                        <h4 class="category-title">{{ category.name }}</h4>
                        <div class="indicators-list">
                            <el-checkbox
                                v-for="indicator in category.indicators"
                                :key="indicator.name"
                                v-model="indicator.selected"
                                @change="handleIndicatorToggle(indicator)"
                                class="indicator-checkbox"
                            >
                                <div class="indicator-info">
                                    <span class="indicator-name">{{ indicator.displayName }}</span>
                                    <span class="indicator-desc">{{ indicator.description }}</span>
                                </div>
                            </el-checkbox>
                        </div>
                    </div>
                </div>
            </div>
        </el-drawer>
    </div>
</template>

<script setup lang="ts">
    import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
    import {
        ElCard,
        ElButton,
        ElInput,
        ElDatePicker,
        ElRadioGroup,
        ElRadioButton,
        ElSelect,
        ElOption,
        ElTag,
        ElDrawer,
        ElCheckbox,
        ElEmpty,
        ElMessage
    } from 'element-plus'
    import { DataLine, RefreshRight, Setting, Search } from '@element-plus/icons-vue'

    interface Indicator {
        name: string
        displayName: string
        params: Record<string, any>
    }

    // Reactive data
    const loading = ref(false)
    const selectedSymbol = ref('600519')
    const symbolName = ref('')
    const dateRange = ref(['2024-01-01', new Date().toISOString().split('T')[0]])
    const selectedPeriod = ref('1d')
    const chartType = ref('candlestick')
    const chartHeight = ref('600px')
    const lastUpdate = ref('')
    const showIndicatorPanel = ref(false)

    // Chart data
    const chartData = reactive({
        symbol: '',
        symbolName: '',
        ohlcv: null as any,
        indicators: [] as any[]
    })

    // Selected indicators
    const selectedIndicators = ref<Indicator[]>([])

    // Indicator categories
    const indicatorCategories = [
        {
            key: 'trend',
            name: 'Trend Indicators',
            indicators: [
                {
                    name: 'sma',
                    displayName: 'SMA (Simple Moving Average)',
                    description: 'Simple moving average',
                    selected: false
                },
                {
                    name: 'ema',
                    displayName: 'EMA (Exponential Moving Average)',
                    description: 'Exponential moving average',
                    selected: false
                },
                {
                    name: 'wma',
                    displayName: 'WMA (Weighted Moving Average)',
                    description: 'Weighted moving average',
                    selected: false
                },
                {
                    name: 'macd',
                    displayName: 'MACD',
                    description: 'Moving Average Convergence Divergence',
                    selected: false
                }
            ]
        },
        {
            key: 'momentum',
            name: 'Momentum Indicators',
            indicators: [
                {
                    name: 'rsi',
                    displayName: 'RSI (Relative Strength Index)',
                    description: 'Relative strength index',
                    selected: false
                },
                {
                    name: 'stoch',
                    displayName: 'Stochastic Oscillator',
                    description: 'Stochastic oscillator',
                    selected: false
                },
                {
                    name: 'williams',
                    displayName: 'Williams %R',
                    description: 'Williams percentage range',
                    selected: false
                },
                {
                    name: 'cci',
                    displayName: 'CCI (Commodity Channel Index)',
                    description: 'Commodity channel index',
                    selected: false
                }
            ]
        },
        {
            key: 'volatility',
            name: 'Volatility Indicators',
            indicators: [
                { name: 'bbands', displayName: 'Bollinger Bands', description: 'Bollinger bands', selected: false },
                {
                    name: 'atr',
                    displayName: 'ATR (Average True Range)',
                    description: 'Average true range',
                    selected: false
                },
                { name: 'kc', displayName: 'Keltner Channel', description: 'Keltner channel', selected: false }
            ]
        },
        {
            key: 'volume',
            name: 'Volume Indicators',
            indicators: [
                { name: 'volume', displayName: 'Volume', description: 'Trading volume', selected: false },
                {
                    name: 'obv',
                    displayName: 'OBV (On Balance Volume)',
                    description: 'On balance volume',
                    selected: false
                },
                {
                    name: 'vwap',
                    displayName: 'VWAP (Volume Weighted Average Price)',
                    description: 'Volume weighted average price',
                    selected: false
                }
            ]
        }
    ]

    // Date shortcuts
    const dateShortcuts = [
        {
            text: 'Last 7 days',
            value: (() => {
                const end = new Date()
                const start = new Date()
                start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
                return [start, end]
            })()
        },
        {
            text: 'Last 30 days',
            value: (() => {
                const end = new Date()
                const start = new Date()
                start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
                return [start, end]
            })()
        },
        {
            text: 'Last 3 months',
            value: (() => {
                const end = new Date()
                const start = new Date()
                start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
                return [start, end]
            })()
        }
    ]

    // Methods
    const handleSymbolChange = async () => {
        if (selectedSymbol.value) {
            await fetchChartData()
        }
    }

    const handleDateRangeChange = () => {
        if (selectedSymbol.value) {
            fetchChartData()
        }
    }

    const handlePeriodChange = () => {
        if (selectedSymbol.value) {
            fetchChartData()
        }
    }

    const handleChartTypeChange = () => {
        // Chart type change logic
    }

    const refreshData = async () => {
        if (selectedSymbol.value) {
            await fetchChartData()
        }
    }

    const fetchChartData = async () => {
        loading.value = true
        try {
            // TODO: Replace with actual API call
            // const response = await axios.get(`/api/market/technical/${selectedSymbol.value}`, {
            //   params: {
            //     start_date: dateRange.value[0],
            //     end_date: dateRange.value[1],
            //     period: selectedPeriod.value
            //   }
            // })

            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 1000))

            // Mock data
            chartData.symbol = selectedSymbol.value
            chartData.symbolName = selectedSymbol.value === '600519' ? '贵州茅台' : 'Unknown Stock'
            chartData.ohlcv = generateMockOHLCV()
            chartData.indicators = []

            updateLastUpdateTime()
            ElMessage.success('Chart data updated')
        } catch (error) {
            console.error('Failed to fetch chart data:', error)
            ElMessage.error('Failed to load chart data')
        } finally {
            loading.value = false
        }
    }

    const generateMockOHLCV = () => {
        const dates = []
        const open = []
        const high = []
        const low = []
        const close = []
        const volume = []

        const startDate = new Date(dateRange.value[0])
        const endDate = new Date(dateRange.value[1])
        const currentDate = new Date(startDate)

        let basePrice = 1000 + Math.random() * 500 // Random base price

        while (currentDate <= endDate) {
            dates.push(currentDate.toISOString().split('T')[0])

            const dailyChange = (Math.random() - 0.5) * 0.1 // ±5% daily change
            const openPrice = basePrice * (1 + dailyChange)
            const volatility = Math.random() * 0.05 // 5% max volatility

            const highPrice = openPrice * (1 + Math.random() * volatility)
            const lowPrice = openPrice * (1 - Math.random() * volatility)
            const closePrice = lowPrice + Math.random() * (highPrice - lowPrice)

            open.push(parseFloat(openPrice.toFixed(2)))
            high.push(parseFloat(highPrice.toFixed(2)))
            low.push(parseFloat(lowPrice.toFixed(2)))
            close.push(parseFloat(closePrice.toFixed(2)))
            volume.push(Math.floor(Math.random() * 1000000 + 100000))

            basePrice = closePrice
            currentDate.setDate(currentDate.getDate() + 1)
        }

        return { dates, open, high, low, close, volume }
    }

    const updateLastUpdateTime = () => {
        const now = new Date()
        lastUpdate.value = now.toLocaleString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        })
    }

    const handleIndicatorToggle = (indicator: any) => {
        if (indicator.selected) {
            addIndicator(indicator)
        } else {
            removeIndicator(indicator.name)
        }
    }

    const addIndicator = (indicator: any) => {
        if (!selectedIndicators.value.find(i => i.name === indicator.name)) {
            selectedIndicators.value.push({
                name: indicator.name,
                displayName: indicator.displayName,
                params: getDefaultParams(indicator.name)
            })
            calculateIndicators()
        }
    }

    const removeIndicator = (indicatorName: string) => {
        const index = selectedIndicators.value.findIndex(i => i.name === indicatorName)
        if (index >= 0) {
            selectedIndicators.value.splice(index, 1)
            calculateIndicators()
        }
    }

    const getDefaultParams = (indicatorName: string) => {
        const defaultParams: { [key: string]: any } = {
            sma: { period: 20 },
            ema: { period: 20 },
            rsi: { period: 14 },
            macd: { fastPeriod: 12, slowPeriod: 26, signalPeriod: 9 },
            bbands: { period: 20, stdDev: 2 },
            stoch: { kPeriod: 14, dPeriod: 3 }
        }
        return defaultParams[indicatorName] || {}
    }

    const calculateIndicators = () => {
        // TODO: Implement indicator calculations
        // This would integrate with the backend API for technical calculations
    }

    const formatParams = (params: any) => {
        return Object.entries(params)
            .map(([key, value]) => `${key}=${value}`)
            .join(', ')
    }

    // Lifecycle
    onMounted(() => {
        if (selectedSymbol.value) {
            fetchChartData()
        }
    })
</script>

<style scoped lang="scss">
    @import '@/styles/theme-tokens.scss';

    .technical-analysis {
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
            gap: var(--spacing-md);
        }
    }

    // Toolbar
    .toolbar-section {
        background: var(--color-bg-secondary);
        border: 1px solid var(--color-border);
        border-radius: var(--border-radius-md);
        padding: var(--spacing-lg);

        .toolbar-content {
            display: flex;
            align-items: center;
            gap: var(--spacing-lg);
            flex-wrap: wrap;

            .search-section {
                .symbol-input {
                    width: 200px;
                }
            }

            .date-section {
                .date-picker {
                    width: 280px;
                }
            }

            .period-section {
                .period-selector {
                    :deep(.el-radio-button__inner) {
                        border-radius: var(--border-radius-sm);
                    }
                }
            }

            .chart-type-section {
                .chart-type-select {
                    width: 140px;
                }
            }
        }
    }

    // Chart Section
    .chart-section {
        .main-chart-card {
            :deep(.el-card__header) {
                background: transparent;
                border-bottom: 1px solid var(--color-border);
                padding: var(--spacing-md) var(--spacing-lg);
            }

            :deep(.el-card__body) {
                padding: 0;
            }
        }

        .chart-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: var(--spacing-lg);

            .chart-title {
                display: flex;
                flex-direction: column;
                gap: var(--spacing-xs);

                .symbol-display {
                    font-family: var(--font-family-mono);
                    font-size: var(--font-size-lg);
                    font-weight: 600;
                    color: var(--color-accent);
                }

                .symbol-name {
                    font-family: var(--font-family-sans);
                    font-size: var(--font-size-sm);
                    color: var(--color-text-secondary);
                }
            }

            .chart-info {
                display: flex;
                align-items: center;
                gap: var(--spacing-md);

                .last-update {
                    font-family: var(--font-family-mono);
                    font-size: var(--font-size-xs);
                    color: var(--color-text-tertiary);
                }
            }
        }

        .chart-container {
            position: relative;
            min-height: 400px;

            .no-data-placeholder {
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 400px;

                .placeholder-icon {
                    color: var(--color-text-tertiary);
                }
            }

            .kline-chart {
                width: 100%;
                border-radius: var(--border-radius-sm);
            }
        }
    }

    // Indicators Section
    .indicators-section {
        .indicators-card {
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

            .indicators-count {
                font-family: var(--font-family-sans);
                font-size: var(--font-size-xs);
                color: var(--color-text-tertiary);
            }
        }

        .indicators-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: var(--spacing-md);
        }

        .indicator-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: var(--spacing-md);
            background: var(--color-bg-primary);
            border: 1px solid var(--color-border);
            border-radius: var(--border-radius-sm);

            .indicator-info {
                display: flex;
                flex-direction: column;
                gap: var(--spacing-xs);

                .indicator-name {
                    font-family: var(--font-family-sans);
                    font-weight: 600;
                    color: var(--color-text-primary);
                }

                .indicator-params {
                    font-family: var(--font-family-mono);
                    font-size: var(--font-size-xs);
                    color: var(--color-text-tertiary);
                }
            }

            .indicator-actions {
                flex-shrink: 0;
            }
        }
    }

    // Summary Section
    .summary-section {
        .summary-card {
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
            .card-title {
                font-family: var(--font-family-sans);
                font-size: var(--font-size-sm);
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                color: var(--color-accent);
            }
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--spacing-lg);
        }

        .summary-item {
            display: flex;
            flex-direction: column;
            gap: var(--spacing-xs);

            .summary-label {
                font-family: var(--font-family-sans);
                font-size: var(--font-size-xs);
                color: var(--color-text-tertiary);
                text-transform: uppercase;
                letter-spacing: 0.1em;
            }

            .summary-value {
                font-family: var(--font-family-mono);
                font-size: var(--font-size-lg);
                font-weight: 600;
                color: var(--color-text-primary);
            }
        }
    }

    // Indicator Drawer
    .indicator-drawer {
        .indicator-categories {
            .category-section {
                margin-bottom: var(--spacing-xl);

                &:last-child {
                    margin-bottom: 0;
                }

                .category-title {
                    font-family: var(--font-family-sans);
                    font-size: var(--font-size-sm);
                    font-weight: 600;
                    color: var(--color-accent);
                    margin: 0 0 var(--spacing-md) 0;
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                }

                .indicators-list {
                    display: flex;
                    flex-direction: column;
                    gap: var(--spacing-sm);

                    .indicator-checkbox {
                        :deep(.el-checkbox__label) {
                            display: flex;
                            flex-direction: column;
                            align-items: flex-start;
                            gap: var(--spacing-xs);
                            line-height: 1.4;
                        }

                        .indicator-info {
                            .indicator-name {
                                font-family: var(--font-family-sans);
                                font-weight: 500;
                                color: var(--color-text-primary);
                            }

                            .indicator-desc {
                                font-family: var(--font-family-sans);
                                font-size: var(--font-size-xs);
                                color: var(--color-text-tertiary);
                            }
                        }
                    }
                }
            }
        }
    }

    // Responsive Design
    @media (max-width: 1200px) {
        .toolbar-content {
            flex-direction: column;
            align-items: stretch;
            gap: var(--spacing-md);

            .search-section,
            .date-section,
            .period-section,
            .chart-type-section {
                width: 100%;

                .symbol-input,
                .date-picker,
                .period-selector,
                .chart-type-select {
                    width: 100%;
                }
            }
        }

        .indicators-grid {
            grid-template-columns: 1fr;
        }

        .summary-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    @media (max-width: 768px) {
        .technical-analysis {
            padding: var(--spacing-md);
            gap: var(--spacing-md);
        }

        .page-title {
            font-size: var(--font-size-xl);
        }

        .summary-grid {
            grid-template-columns: 1fr;
        }

        .chart-header {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--spacing-md);

            .chart-info {
                width: 100%;
                justify-content: space-between;
            }
        }
    }
</style>
