<template>
    <div class="portfolio-container">
        <!-- Page Header -->
        <div class="page-header">
            <div class="header-title-section">
                <h1 class="page-title">
                    <el-icon><Folder /></el-icon>
                    PORTFOLIO MANAGEMENT
                </h1>
                <p class="page-subtitle">INVESTMENT PORTFOLIO TRACKING AND PERFORMANCE ANALYSIS</p>
            </div>
            <div class="header-actions">
                <el-button type="primary" @click="refreshPortfolio">
                    <template #icon><RefreshRight /></template>
                    REFRESH
                </el-button>
                <el-button @click="addPosition">
                    <template #icon><Plus /></template>
                    ADD POSITION
                </el-button>
            </div>
        </div>

        <!-- Portfolio Overview -->
        <div class="overview-section">
            <div class="overview-cards">
                <el-card class="metric-card">
                    <div class="metric-content">
                        <div class="metric-icon">💰</div>
                        <div class="metric-data">
                            <div class="metric-value">¥{{ formatCurrency(portfolioMetrics.totalValue) }}</div>
                            <div class="metric-label">TOTAL VALUE</div>
                        </div>
                    </div>
                </el-card>

                <el-card class="metric-card">
                    <div class="metric-content">
                        <div class="metric-icon">📈</div>
                        <div class="metric-data">
                            <div
                                class="metric-value"
                                :class="{
                                    positive: portfolioMetrics.totalReturn >= 0,
                                    negative: portfolioMetrics.totalReturn < 0
                                }"
                            >
                                {{ portfolioMetrics.totalReturn >= 0 ? '+' : ''
                                }}{{ portfolioMetrics.totalReturn.toFixed(2) }}%
                            </div>
                            <div class="metric-label">TOTAL RETURN</div>
                        </div>
                    </div>
                </el-card>

                <el-card class="metric-card">
                    <div class="metric-content">
                        <div class="metric-icon">📊</div>
                        <div class="metric-data">
                            <div class="metric-value">¥{{ formatCurrency(portfolioMetrics.dailyPnL) }}</div>
                            <div class="metric-label">DAILY P&L</div>
                        </div>
                    </div>
                </el-card>

                <el-card class="metric-card">
                    <div class="metric-content">
                        <div class="metric-icon">🎯</div>
                        <div class="metric-data">
                            <div class="metric-value">{{ portfolioMetrics.sharpeRatio.toFixed(2) }}</div>
                            <div class="metric-label">SHARPE RATIO</div>
                        </div>
                    </div>
                </el-card>
            </div>
        </div>

        <!-- Portfolio Positions -->
        <div class="positions-section">
            <el-card class="positions-card">
                <template #header>
                    <div class="card-header">
                        <span class="card-title">PORTFOLIO POSITIONS</span>
                        <span class="position-count">({{ positions.length }} positions)</span>
                    </div>
                </template>

                <el-table :data="positions" class="positions-table" stripe border>
                    <el-table-column prop="symbol" label="SYMBOL" width="100" />
                    <el-table-column prop="name" label="NAME" width="150" />
                    <el-table-column prop="shares" label="SHARES" width="100" align="right" />
                    <el-table-column prop="avgCost" label="AVG COST" width="120" align="right">
                        <template #default="{ row }">¥{{ row.avgCost.toFixed(2) }}</template>
                    </el-table-column>
                    <el-table-column prop="currentPrice" label="CURRENT PRICE" width="140" align="right">
                        <template #default="{ row }">¥{{ row.currentPrice.toFixed(2) }}</template>
                    </el-table-column>
                    <el-table-column prop="marketValue" label="MARKET VALUE" width="140" align="right">
                        <template #default="{ row }">¥{{ formatCurrency(row.marketValue) }}</template>
                    </el-table-column>
                    <el-table-column prop="unrealizedPnL" label="UNREALIZED P&L" width="140" align="right">
                        <template #default="{ row }">
                            <span :class="{ positive: row.unrealizedPnL >= 0, negative: row.unrealizedPnL < 0 }">
                                {{ row.unrealizedPnL >= 0 ? '+' : '' }}¥{{ row.unrealizedPnL.toFixed(2) }}
                            </span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="returnPct" label="RETURN %" width="120" align="right">
                        <template #default="{ row }">
                            <span :class="{ positive: row.returnPct >= 0, negative: row.returnPct < 0 }">
                                {{ row.returnPct >= 0 ? '+' : '' }}{{ row.returnPct.toFixed(2) }}%
                            </span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="weight" label="WEIGHT %" width="120" align="right">
                        <template #default="{ row }">{{ row.weight.toFixed(2) }}%</template>
                    </el-table-column>
                </el-table>
            </el-card>
        </div>

        <!-- Performance Chart -->
        <div class="performance-section">
            <el-card class="performance-card">
                <template #header>
                    <div class="card-header">
                        <span class="card-title">PORTFOLIO PERFORMANCE</span>
                        <div class="chart-controls">
                            <el-select v-model="performancePeriod" size="small" @change="updatePerformanceChart">
                                <el-option label="1 Week" value="1w" />
                                <el-option label="1 Month" value="1m" />
                                <el-option label="3 Months" value="3m" />
                                <el-option label="6 Months" value="6m" />
                                <el-option label="1 Year" value="1y" />
                            </el-select>
                        </div>
                    </div>
                </template>

                <div class="chart-placeholder">
                    <el-empty description="Performance chart will be implemented with trading data integration" />
                </div>
            </el-card>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, reactive, onMounted } from 'vue'
    import { ElCard, ElButton, ElTable, ElTableColumn, ElSelect, ElOption, ElEmpty, ElMessage } from 'element-plus'
    import { Folder, RefreshRight, Plus } from '@element-plus/icons-vue'

    interface PortfolioMetrics {
        totalValue: number
        totalReturn: number
        dailyPnL: number
        sharpeRatio: number
    }

    interface Position {
        symbol: string
        name: string
        shares: number
        avgCost: number
        currentPrice: number
        marketValue: number
        unrealizedPnL: number
        returnPct: number
        weight: number
    }

    const performancePeriod = ref('1m')

    const portfolioMetrics = reactive<PortfolioMetrics>({
        totalValue: 1250000,
        totalReturn: 12.5,
        dailyPnL: 2500,
        sharpeRatio: 1.8
    })

    const positions = ref<Position[]>([
        {
            symbol: '000001',
            name: '平安银行',
            shares: 10000,
            avgCost: 12.5,
            currentPrice: 12.85,
            marketValue: 128500,
            unrealizedPnL: 3500,
            returnPct: 2.8,
            weight: 10.28
        },
        {
            symbol: '000002',
            name: '万科A',
            shares: 5000,
            avgCost: 18.2,
            currentPrice: 18.95,
            marketValue: 94750,
            unrealizedPnL: 3750,
            returnPct: 4.12,
            weight: 7.58
        },
        {
            symbol: '600036',
            name: '招商银行',
            shares: 2000,
            avgCost: 40.5,
            currentPrice: 42.8,
            marketValue: 85600,
            unrealizedPnL: 4600,
            returnPct: 5.68,
            weight: 6.85
        },
        {
            symbol: '000858',
            name: '五粮液',
            shares: 500,
            avgCost: 125.0,
            currentPrice: 128.5,
            marketValue: 64250,
            unrealizedPnL: 1750,
            returnPct: 2.8,
            weight: 5.14
        },
        {
            symbol: '300750',
            name: '宁德时代',
            shares: 1000,
            avgCost: 235.0,
            currentPrice: 245.8,
            marketValue: 245800,
            unrealizedPnL: 10800,
            returnPct: 4.6,
            weight: 19.66
        }
    ])

    const refreshPortfolio = async () => {
        // Simulate portfolio refresh
        await new Promise(resolve => setTimeout(resolve, 500))

        // Update positions with new prices
        positions.value.forEach(position => {
            const priceChange = (Math.random() - 0.5) * 2
            position.currentPrice = parseFloat((position.currentPrice + priceChange).toFixed(2))
            position.marketValue = position.shares * position.currentPrice
            position.unrealizedPnL = (position.currentPrice - position.avgCost) * position.shares
            position.returnPct = ((position.currentPrice - position.avgCost) / position.avgCost) * 100
        })

        // Recalculate portfolio metrics
        portfolioMetrics.totalValue = positions.value.reduce((sum, pos) => sum + pos.marketValue, 0)
        portfolioMetrics.dailyPnL = Math.random() * 10000 - 5000

        ElMessage.success('Portfolio refreshed')
    }

    const addPosition = () => {
        // TODO: Implement add position dialog
        ElMessage.info('Add position feature will be implemented')
    }

    const updatePerformanceChart = () => {
        // TODO: Update chart based on selected period
        console.log('Update performance chart for period:', performancePeriod.value)
    }

    const formatCurrency = (amount: number): string => {
        if (amount >= 100000000) {
            return (amount / 100000000).toFixed(2) + '亿'
        } else if (amount >= 10000) {
            return (amount / 10000).toFixed(1) + '万'
        }
        return amount.toString()
    }

    // Lifecycle
    onMounted(() => {
        // Initial load
    })
</script>

<style scoped lang="scss">
    @import '@/styles/theme-tokens.scss';

    .portfolio-container {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-lg);
      padding: var(--spacing-lg);
      background: var(--color-bg-primary);
      min-height: 100vh);
    }

    // Header
    .page-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-bottom: var(--spacing-lg);
      border-bottom: 2px solid var(--color-border);

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

        .el-icon { font-size: var(--font-size-3xl); color: var(--color-accent); }
      }

      .page-subtitle {
        font-family: var(--font-family-sans);
        font-size: var(--font-size-xs);
        color: var(--color-text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.2em;
        margin: var(--spacing-sm) 0 0 0;
      }
    }

    // Overview Cards
    .overview-section {
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

      .metric-card {
        :deep(.el-card__body) {
          padding: var(--spacing-lg);
        }
      }

      .metric-content {
        display: flex;
        align-items: center;
        gap: var(--spacing-md);

        .metric-icon {
          font-size: var(--font-size-2xl);
          width: 48px;
          height: 48px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--color-accent-alpha-90);
          border-radius: var(--border-radius-md);
        }

        .metric-data {
          flex: 1;

          .metric-value {
            font-family: var(--font-family-mono);
            font-size: var(--font-size-xl);
            font-weight: 700;
            color: var(--color-text-primary);
            margin-bottom: var(--spacing-xs);

            &.positive { color: var(--color-stock-up); }
            &.negative { color: var(--color-stock-down); }
          }

          .metric-label {
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

    // Positions Section
    .positions-section {
      .positions-card {
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

        .position-count {
          font-family: var(--font-family-mono);
          font-size: var(--font-size-xs);
          color: var(--color-text-tertiary);
        }
      }
    }

    // Positions Table
    .positions-table {
      :deep(.el-table__header th) {
        background: var(--color-bg-secondary);
        border-bottom: 2px solid var(--color-border);
        color: var(--color-text-secondary);
        font-family: var(--font-family-sans);
        font-size: var(--font-size-xs);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
      }

      :deep(.el-table__body td) {
        border-bottom: 1px solid var(--color-border);
        color: var(--color-text-primary);
        font-family: var(--font-family-mono);
        font-size: var(--font-size-sm);
      }

      .positive { color: var(--color-stock-up); }
      .negative { color: var(--color-stock-down); }
    }

    // Performance Section
    .performance-section {
      .performance-card {
        :deep(.el-card__header) {
          background: transparent;
          border-bottom: 1px solid var(--color-border);
          padding: var(--spacing-md) var(--spacing-lg);
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        :deep(.el-card__body) {
          padding: var(--spacing-lg);
        }
      }

      .card-header {
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: space-between;

        .card-title {
          font-family: var(--font-family-sans);
          font-size: var(--font-size-sm);
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.1em;
          color: var(--color-accent);
        }

        .chart-controls {
          display: flex;
          gap: var(--spacing-md);
        }
      }

      .chart-placeholder {
        min-height: 300px;
        display: flex;
        align-items: center;
        justify-content: center;
      }
    }

    // Responsive Design
    @media (max-width: 1200px) {
      .portfolio-container {
        padding: var(--spacing-lg);
        gap: var(--spacing-lg);
      }

      .overview-cards {
        grid-template-columns: repeat(2, 1fr);
      }
    }

    @media (max-width: 768px) {
      .portfolio-container {
        padding: var(--spacing-md);
        gap: var(--spacing-md);
      }

      .page-title {
        font-size: var(--font-size-xl);
      }

      .overview-cards {
        grid-template-columns: 1fr;
      }

      .page-header {
        flex-direction: column;
        align-items: flex-start;
        gap: var(--spacing-md);
      }
    }
</style>
