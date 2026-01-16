<template>
    <div class="capital-flow-container">
        <!-- Page Header -->
        <div class="page-header">
            <div class="header-title-section">
                <h1 class="page-title">
                    <el-icon><Money /></el-icon>
                    CAPITAL FLOW ANALYSIS
                </h1>
                <p class="page-subtitle">MARKET CAPITAL FLOW MONITORING & ANALYSIS</p>
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

        <!-- Market Overview Cards -->
        <div class="overview-cards">
            <el-card class="overview-card">
                <div class="card-content">
                    <div class="card-icon">📈</div>
                    <div class="card-data">
                        <div class="card-value">{{ formatCurrency(marketOverview.totalFlow) }}</div>
                        <div class="card-label">TOTAL FLOW</div>
                    </div>
                </div>
            </el-card>

            <el-card class="overview-card">
                <div class="card-content">
                    <div class="card-icon">📊</div>
                    <div class="card-data">
                        <div class="card-value">{{ formatCurrency(marketOverview.mainFlow) }}</div>
                        <div class="card-label">MAIN FORCE</div>
                    </div>
                </div>
            </el-card>

            <el-card class="overview-card">
                <div class="card-content">
                    <div class="card-icon">🔄</div>
                    <div class="card-data">
                        <div class="card-value">{{ formatCurrency(marketOverview.retailFlow) }}</div>
                        <div class="card-label">RETAIL FLOW</div>
                    </div>
                </div>
            </el-card>

            <el-card class="overview-card">
                <div class="card-content">
                    <div class="card-icon">⚡</div>
                    <div class="card-data">
                        <div class="card-value">{{ formatCurrency(marketOverview.fastMoney) }}</div>
                        <div class="card-label">FAST MONEY</div>
                    </div>
                </div>
            </el-card>
        </div>

        <!-- Fund Flow Analysis Section -->
        <div class="analysis-section">
            <el-card class="analysis-card">
                <template #header>
                    <div class="card-header">
                        <span class="card-title">DETAILED FUND FLOW ANALYSIS</span>
                        <div class="header-info">
                            <el-tag type="info" size="small">实时更新</el-tag>
                            <span class="update-time">最后更新: {{ lastUpdate }}</span>
                        </div>
                    </div>
                </template>

                <!-- Fund Flow Panel Integration -->
                <FundFlowPanel
                    ref="fundFlowPanelRef"
                    @data-loaded="handleFundFlowData"
                    @refresh="handleFundFlowRefresh"
                />
            </el-card>
        </div>

        <!-- Top Gainers/Losers Section -->
        <div class="top-movers-section">
            <div class="movers-grid">
                <el-card class="movers-card">
                    <template #header>
                        <div class="card-header">
                            <span class="card-title">TOP GAINERS</span>
                            <span class="card-subtitle">资金流入最多</span>
                        </div>
                    </template>

                    <el-table :data="topGainers" :show-header="false" class="movers-table" size="small">
                        <el-table-column width="60">
                            <template #default="{ $index }">
                                <span class="rank-number">{{ $index + 1 }}</span>
                            </template>
                        </el-table-column>

                        <el-table-column>
                            <template #default="{ row }">
                                <div class="stock-info">
                                    <span class="stock-symbol">{{ row.symbol }}</span>
                                    <span class="stock-name">{{ row.name }}</span>
                                </div>
                            </template>
                        </el-table-column>

                        <el-table-column align="right">
                            <template #default="{ row }">
                                <span class="flow-amount positive">{{ formatCurrency(row.flowAmount) }}</span>
                            </template>
                        </el-table-column>
                    </el-table>
                </el-card>

                <el-card class="movers-card">
                    <template #header>
                        <div class="card-header">
                            <span class="card-title">TOP SELLERS</span>
                            <span class="card-subtitle">资金流出最多</span>
                        </div>
                    </template>

                    <el-table :data="topSellers" :show-header="false" class="movers-table" size="small">
                        <el-table-column width="60">
                            <template #default="{ $index }">
                                <span class="rank-number">{{ $index + 1 }}</span>
                            </template>
                        </el-table-column>

                        <el-table-column>
                            <template #default="{ row }">
                                <div class="stock-info">
                                    <span class="stock-symbol">{{ row.symbol }}</span>
                                    <span class="stock-name">{{ row.name }}</span>
                                </div>
                            </template>
                        </el-table-column>

                        <el-table-column align="right">
                            <template #default="{ row }">
                                <span class="flow-amount negative">{{ formatCurrency(row.flowAmount) }}</span>
                            </template>
                        </el-table-column>
                    </el-table>
                </el-card>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, onMounted, reactive } from 'vue'
    import { ElCard, ElButton, ElTable, ElTableColumn, ElTag, ElMessage } from 'element-plus'
    import { Money, RefreshRight } from '@element-plus/icons-vue'
    import FundFlowPanel from '@/components/market/FundFlowPanel.vue'

    interface MarketOverview {
        totalFlow: number
        mainFlow: number
        retailFlow: number
        fastMoney: number
    }

    interface StockFlow {
        symbol: string
        name: string
        flowAmount: number
    }

    const loading = ref(false)
    const lastUpdate = ref('')
    const fundFlowPanelRef = ref()

    const marketOverview = reactive<MarketOverview>({
        totalFlow: 1250000000, // 12.5亿
        mainFlow: 850000000, // 8.5亿
        retailFlow: 320000000, // 3.2亿
        fastMoney: 80000000 // 0.8亿
    })

    const topGainers = ref<StockFlow[]>([
        { symbol: '000001', name: '平安银行', flowAmount: 125000000 },
        { symbol: '600036', name: '招商银行', flowAmount: 98000000 },
        { symbol: '000002', name: '万科A', flowAmount: 87000000 },
        { symbol: '600000', name: '浦发银行', flowAmount: 76000000 },
        { symbol: '002142', name: '宁波银行', flowAmount: 65000000 }
    ])

    const topSellers = ref<StockFlow[]>([
        { symbol: '600276', name: '恒瑞医药', flowAmount: -95000000 },
        { symbol: '000858', name: '五粮液', flowAmount: -87000000 },
        { symbol: '300750', name: '宁德时代', flowAmount: -78000000 },
        { symbol: '000568', name: '泸州老窖', flowAmount: -65000000 },
        { symbol: '600519', name: '贵州茅台', flowAmount: -58000000 }
    ])

    const formatCurrency = (amount: number): string => {
        if (Math.abs(amount) >= 100000000) {
            return `${(amount / 100000000).toFixed(2)}亿`
        } else if (Math.abs(amount) >= 10000) {
            return `${(amount / 10000).toFixed(1)}万`
        }
        return amount.toString()
    }

    const refreshAllData = async (): Promise<void> => {
        loading.value = true
        try {
            // Refresh market overview data
            await loadMarketOverview()

            // Refresh fund flow data through the panel
            if (fundFlowPanelRef.value) {
                await fundFlowPanelRef.value.refreshData()
            }

            // Refresh top movers data
            await loadTopMovers()

            updateLastUpdateTime()
            ElMessage.success('所有数据已刷新')
        } catch (error) {
            console.error('Failed to refresh all data:', error)
            ElMessage.error('刷新数据失败')
        } finally {
            loading.value = false
        }
    }

    const loadMarketOverview = async (): Promise<void> => {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 300))

        // Update with random changes
        const change = (Math.random() - 0.5) * 0.1
        marketOverview.totalFlow = Math.round(marketOverview.totalFlow * (1 + change))
        marketOverview.mainFlow = Math.round(marketOverview.mainFlow * (1 + change * 0.8))
        marketOverview.retailFlow = Math.round(marketOverview.retailFlow * (1 + change * 0.6))
        marketOverview.fastMoney = Math.round(marketOverview.fastMoney * (1 + change * 0.4))
    }

    const loadTopMovers = async (): Promise<void> => {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 200))

        // Update with random changes
        topGainers.value.forEach(stock => {
            const change = (Math.random() - 0.3) * 0.2
            stock.flowAmount = Math.round(stock.flowAmount * (1 + change))
        })

        topSellers.value.forEach(stock => {
            const change = (Math.random() - 0.3) * 0.2
            stock.flowAmount = Math.round(stock.flowAmount * (1 + change))
        })
    }

    const updateLastUpdateTime = (): void => {
        const now = new Date()
        lastUpdate.value = now.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        })
    }

    const handleFundFlowData = (data: any): void => {
        console.log('Fund flow data loaded:', data)
        // Handle data loaded event from FundFlowPanel
    }

    const handleFundFlowRefresh = (): void => {
        console.log('Fund flow refresh requested')
        // Handle refresh event from FundFlowPanel
    }

    onMounted(() => {
        updateLastUpdateTime()
    })
</script>

<style scoped lang="scss">
    @import '@/styles/theme-tokens.scss';

    .capital-flow-container {
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

    // Analysis Section
    .analysis-section {
        .analysis-card {
            :deep(.el-card__header) {
                background: transparent;
                border-bottom: 1px solid var(--color-border);
                padding: var(--spacing-md) var(--spacing-lg);
            }

            :deep(.el-card__body) {
                padding: 0;
            }
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

        .header-info {
            display: flex;
            align-items: center;
            gap: var(--spacing-md);

            .update-time {
                font-family: var(--font-family-mono);
                font-size: var(--font-size-xs);
                color: var(--color-text-tertiary);
            }
        }
    }

    // Top Movers Section
    .top-movers-section {
        .movers-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: var(--spacing-lg);

            @media (max-width: 1200px) {
                grid-template-columns: 1fr;
            }
        }

        .movers-card {
            :deep(.el-card__header) {
                background: transparent;
                border-bottom: 1px solid var(--color-border);
                padding: var(--spacing-md) var(--spacing-lg);
            }

            :deep(.el-card__body) {
                padding: 0;
            }
        }
    }

    .movers-table {
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

        .rank-number {
            font-family: var(--font-family-mono);
            font-weight: 700;
            color: var(--color-accent);
            font-size: var(--font-size-lg);
        }

        .stock-info {
            display: flex;
            flex-direction: column;
            gap: var(--spacing-xs);

            .stock-symbol {
                font-family: var(--font-family-mono);
                font-weight: 600;
                color: var(--color-accent);
                font-size: var(--font-size-sm);
            }

            .stock-name {
                font-family: var(--font-family-sans);
                font-weight: 500;
                color: var(--color-text-primary);
                font-size: var(--font-size-xs);
            }
        }

        .flow-amount {
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
    }

    // Responsive Design
    @media (max-width: 1200px) {
        .capital-flow-container {
            padding: var(--spacing-lg);
            gap: var(--spacing-lg);
        }

        .page-header {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--spacing-md);

            .header-actions {
                width: 100%;
                justify-content: flex-end;
            }
        }

        .movers-grid {
            grid-template-columns: 1fr;
        }
    }

    @media (max-width: 768px) {
        .capital-flow-container {
            padding: var(--spacing-md);
            gap: var(--spacing-md);
        }

        .page-title {
            font-size: var(--font-size-xl);
        }

        .overview-cards {
            grid-template-columns: 1fr;
        }
    }
</style>
