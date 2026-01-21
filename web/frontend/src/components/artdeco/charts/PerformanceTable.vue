<template>
    <div class="artdeco-performance-table">
        <ArtDecoCard class="table-card">
            <template #header>
                <div class="table-header">
                    <div class="header-title">
                        <span class="title-icon">📊</span>
                        <div class="title-text">
                            <div class="title-main">{{ title }}</div>
                            <div class="title-sub">{{ subtitle }}</div>
                        </div>
                    </div>
                    <div class="header-controls">
                        <ArtDecoSelect
                            v-if="periodOptions.length > 0"
                            v-model="selectedPeriod"
                            :options="periodOptions"
                            placeholder="选择周期"
                            class="period-select"
                        />
                        <ArtDecoButton @click="handleRefresh" :loading="loading" variant="secondary" size="sm">
                            ↻ 刷新
                        </ArtDecoButton>
                    </div>
                </div>
            </template>

            <div class="table-container" :class="{ loading: loading }">
                <ArtDecoLoader v-if="loading" :text="'加载中...'" />

                <div v-else class="table-content">
                    <!-- Empty State -->
                    <div v-if="!data || data.length === 0" class="empty-state">
                        <div class="empty-icon">📈</div>
                        <div class="empty-text">暂无绩效数据</div>
                        <div class="empty-hint">NO PERFORMANCE DATA AVAILABLE</div>
                    </div>

                    <!-- Performance Table -->
                    <div v-else class="performance-table-wrapper">
                        <el-table
                            :data="paginatedData"
                            stripe
                            border
                            class="artdeco-performance-table"
                            :default-sort="{ prop: 'totalReturn', order: 'descending' }"
                            @row-click="handleRowClick"
                        >
                            <!-- Strategy Name -->
                            <el-table-column prop="strategyName" label="策略名称" width="180" fixed>
                                <template #default="{ row }">
                                    <div class="strategy-name-cell">
                                        <span class="strategy-icon">{{ getStrategyIcon(row.strategyType) }}</span>
                                        <div class="strategy-info">
                                            <div class="strategy-name">{{ row.strategyName }}</div>
                                            <div class="strategy-code">{{ row.strategyCode }}</div>
                                        </div>
                                    </div>
                                </template>
                            </el-table-column>

                            <!-- Performance Metrics -->
                            <el-table-column prop="totalReturn" label="总收益率" width="120" sortable align="right">
                                <template #default="{ row }">
                                    <span :class="getValueClass(row.totalReturn)">
                                        {{ formatPercent(row.totalReturn) }}
                                    </span>
                                </template>
                            </el-table-column>

                            <el-table-column
                                prop="annualizedReturn"
                                label="年化收益"
                                width="120"
                                sortable
                                align="right"
                            >
                                <template #default="{ row }">
                                    <span :class="getValueClass(row.annualizedReturn)">
                                        {{ formatPercent(row.annualizedReturn) }}
                                    </span>
                                </template>
                            </el-table-column>

                            <el-table-column prop="sharpeRatio" label="夏普比率" width="110" sortable align="right">
                                <template #default="{ row }">
                                    <span :class="getSharpeClass(row.sharpeRatio)">
                                        {{ row.sharpeRatio.toFixed(2) }}
                                    </span>
                                </template>
                            </el-table-column>

                            <el-table-column prop="maxDrawdown" label="最大回撤" width="110" sortable align="right">
                                <template #default="{ row }">
                                    <span :class="getDrawdownClass(row.maxDrawdown)">
                                        {{ formatPercent(row.maxDrawdown) }}
                                    </span>
                                </template>
                            </el-table-column>

                            <el-table-column prop="winRate" label="胜率" width="100" sortable align="right">
                                <template #default="{ row }">
                                    <span :class="getWinRateClass(row.winRate)">
                                        {{ formatPercent(row.winRate) }}
                                    </span>
                                </template>
                            </el-table-column>

                            <el-table-column prop="profitFactor" label="盈亏比" width="100" sortable align="right">
                                <template #default="{ row }">
                                    <span class="metric-value">{{ row.profitFactor.toFixed(2) }}</span>
                                </template>
                            </el-table-column>

                            <el-table-column prop="volatility" label="波动率" width="100" sortable align="right">
                                <template #default="{ row }">
                                    <span class="metric-value">{{ formatPercent(row.volatility) }}</span>
                                </template>
                            </el-table-column>

                            <el-table-column prop="totalTrades" label="交易次数" width="100" sortable align="right">
                                <template #default="{ row }">
                                    <span class="metric-value">{{ row.totalTrades }}</span>
                                </template>
                            </el-table-column>

                            <el-table-column prop="avgHoldDays" label="平均持仓" width="100" sortable align="right">
                                <template #default="{ row }">
                                    <span class="metric-value">{{ row.avgHoldDays }} 天</span>
                                </template>
                            </el-table-column>

                            <!-- Actions -->
                            <el-table-column label="操作" width="180" fixed="right">
                                <template #default="{ row }">
                                    <div class="action-buttons">
                                        <ArtDecoButton @click.stop="handleViewDetails(row)" variant="outline" size="sm">
                                            详情
                                        </ArtDecoButton>
                                        <ArtDecoButton @click.stop="handleCompare(row)" variant="secondary" size="sm">
                                            对比
                                        </ArtDecoButton>
                                    </div>
                                </template>
                            </el-table-column>
                        </el-table>

                        <!-- Pagination -->
                        <div v-if="data.length > pageSize" class="pagination-wrapper">
                            <el-pagination
                                v-model:current-page="currentPage"
                                v-model:page-size="pageSize"
                                :page-sizes="[10, 20, 50, 100]"
                                :total="data.length"
                                layout="total, sizes, prev, pager, next, jumper"
                                @size-change="handleSizeChange"
                                @current-change="handlePageChange"
                            />
                        </div>
                    </div>
                </div>
            </div>

            <!-- Summary Footer -->
            <div v-if="summary && data.length > 0" class="table-footer">
                <div class="summary-stats">
                    <div class="stat-item">
                        <span class="stat-label">平均收益</span>
                        <span class="stat-value" :class="getValueClass(summary.avgReturn)">
                            {{ formatPercent(summary.avgReturn) }}
                        </span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">最佳策略</span>
                        <span class="stat-value">{{ summary.bestStrategy }}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">胜率最高</span>
                        <span class="stat-value">{{ summary.highestWinRate }}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">总交易数</span>
                        <span class="stat-value">{{ summary.totalTrades }}</span>
                    </div>
                </div>
            </div>
        </ArtDecoCard>
    </div>
</template>

<script setup lang="ts">
    import { ref, computed } from 'vue'
    import ArtDecoCard from '../base/ArtDecoCard.vue'
    import ArtDecoButton from '../base/ArtDecoButton.vue'
    import ArtDecoSelect from '../base/ArtDecoSelect.vue'
    import ArtDecoLoader from './ArtDecoLoader.vue'

    // ============================================
    //   类型定义
    // ============================================

    interface PerformanceData {
        strategyCode: string
        strategyName: string
        strategyType: string
        totalReturn: number
        annualizedReturn: number
        sharpeRatio: number
        maxDrawdown: number
        winRate: number
        profitFactor: number
        volatility: number
        totalTrades: number
        avgHoldDays: number
    }

    interface PeriodOption {
        label: string
        value: string
    }

    interface Summary {
        avgReturn: number
        bestStrategy: string
        highestWinRate: string
        totalTrades: number
    }

    interface Props {
        title?: string
        subtitle?: string
        data: PerformanceData[]
        loading?: boolean
        periodOptions?: PeriodOption[]
    }

    // ============================================
    //   Props & Emits
    // ============================================

    const props = withDefaults(defineProps<Props>(), {
        title: '策略绩效表',
        subtitle: 'PERFORMANCE TABLE',
        loading: false,
        periodOptions: () => [
            { label: '近一月', value: '1m' },
            { label: '近三月', value: '3m' },
            { label: '近半年', value: '6m' },
            { label: '近一年', value: '1y' },
            { label: '全部', value: 'all' }
        ]
    })

    const emit = defineEmits<{
        refresh: []
        rowClick: [row: PerformanceData]
        viewDetails: [row: PerformanceData]
        compare: [row: PerformanceData]
        periodChange: [period: string]
    }>()

    // ============================================
    //   响应式数据
    // ============================================

    const currentPage = ref(1)
    const pageSize = ref(20)
    const selectedPeriod = ref('all')

    // Paginated data
    const paginatedData = computed(() => {
        const start = (currentPage.value - 1) * pageSize.value
        const end = start + pageSize.value
        return props.data.slice(start, end)
    })

    // Summary statistics
    const summary = computed<Summary | null>(() => {
        if (!props.data || props.data.length === 0) return null

        const returns = props.data.map(d => d.totalReturn)
        const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length

        const bestStrategy = props.data.reduce((best, current) =>
            current.totalReturn > best.totalReturn ? current : best
        )

        const highestWinRate = props.data.reduce((best, current) => (current.winRate > best.winRate ? current : best))

        const totalTrades = props.data.reduce((sum, d) => sum + d.totalTrades, 0)

        return {
            avgReturn,
            bestStrategy: bestStrategy.strategyName,
            highestWinRate: highestWinRate.strategyName,
            totalTrades
        }
    })

    // ============================================
    //   工具函数
    // ============================================

    const formatPercent = (value: number) => {
        return (value * 100).toFixed(2) + '%'
    }

    const getValueClass = (value: number) => {
        if (value > 0) return 'rise'
        if (value < 0) return 'fall'
        return 'neutral'
    }

    const getSharpeClass = (value: number) => {
        if (value > 2) return 'excellent'
        if (value > 1) return 'good'
        if (value > 0) return 'fair'
        return 'poor'
    }

    const getDrawdownClass = (value: number) => {
        if (value < -0.2) return 'severe'
        if (value < -0.1) return 'high'
        if (value < -0.05) return 'moderate'
        return 'mild'
    }

    const getWinRateClass = (value: number) => {
        if (value > 0.6) return 'excellent'
        if (value > 0.5) return 'good'
        if (value > 0.4) return 'fair'
        return 'poor'
    }

    const getStrategyIcon = (type: string) => {
        const iconMap: Record<string, string> = {
            trend: '📈',
            momentum: '⚡',
            mean_reversion: '🔄',
            arbitrage: '⚖️',
            custom: '🎯'
        }
        return iconMap[type] || '📊'
    }

    // ============================================
    //   事件处理
    // ============================================

    const handleRowClick = (row: PerformanceData) => {
        emit('rowClick', row)
    }

    const handleViewDetails = (row: PerformanceData) => {
        emit('viewDetails', row)
    }

    const handleCompare = (row: PerformanceData) => {
        emit('compare', row)
    }

    const handleRefresh = () => {
        emit('refresh')
    }

    const handlePageChange = (page: number) => {
        currentPage.value = page
    }

    const handleSizeChange = (size: number) => {
        pageSize.value = size
        currentPage.value = 1
    }

    // Watch period changes
    import { watch } from 'vue'
    watch(selectedPeriod, newPeriod => {
        emit('periodChange', newPeriod)
    })
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    // ============================================
    //   ART DECO PERFORMANCE TABLE
    // ============================================

    .artdeco-performance-table {
        width: 100%;
    }

    .table-card {
        :deep(.card-header) {
            padding: 0;
        }
    }

    // ============================================
    //   TABLE HEADER
    // ============================================

    .table-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: var(--artdeco-spacing-6);
        padding: var(--artdeco-spacing-4) var(--artdeco-spacing-6);

        .header-title {
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-4);

            .title-icon {
                font-size: var(--artdeco-text-2xl);
                opacity: 0.8;
            }

            .title-text {
                .title-main {
                    font-family: var(--artdeco-font-heading);
                    font-size: var(--artdeco-text-lg);
                    font-weight: 700;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    line-height: var(--artdeco-leading-tight);
                }

                .title-sub {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-text-xs);
                    font-weight: 600;
                    color: var(--artdeco-fg-muted);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin-top: var(--artdeco-spacing-1);
                }
            }
        }

        .header-controls {
            display: flex;
            gap: var(--artdeco-spacing-3);

            .period-select {
                width: 120px;
            }
        }
    }

    // ============================================
    //   TABLE CONTAINER
    // ============================================

    .table-container {
        position: relative;
        min-height: 400px;
        padding: var(--artdeco-spacing-4);

        &.loading {
            display: flex;
            align-items: center;
            justify-content: center;
        }
    }

    .table-content {
        width: 100%;
    }

    // ============================================
    //   EMPTY STATE
    // ============================================

    .empty-state {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;

        .empty-icon {
            font-size: var(--artdeco-text-5xl);
            margin-bottom: var(--artdeco-spacing-4);
            opacity: 0.3;
        }

        .empty-text {
            font-family: var(--artdeco-font-heading);
            font-size: var(--artdeco-text-lg);
            font-weight: 600;
            color: var(--artdeco-fg-muted);
            margin-bottom: var(--artdeco-spacing-2);
        }

        .empty-hint {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-xs);
            font-weight: 600;
            color: var(--artdeco-fg-dim);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
        }
    }

    // ============================================
    //   PERFORMANCE TABLE
    // ============================================

    .performance-table-wrapper {
        width: 100%;
    }

    .artdeco-performance-table {
        width: 100%;

        :deep(.el-table__header-wrapper) {
            background: rgba(212, 175, 55, 0.05);

            th {
                background: transparent;
                font-family: var(--artdeco-font-heading);
                font-size: var(--artdeco-text-xs);
                font-weight: 700;
                color: var(--artdeco-gold-primary);
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
                border-color: var(--artdeco-gold-dim);
            }
        }

        :deep(.el-table__body-wrapper) {
            td {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-primary);
                border-color: var(--artdeco-gold-dim);
            }

            tr:hover > td {
                background: rgba(212, 175, 55, 0.1) !important;
            }

            tr.current-row > td {
                background: rgba(212, 175, 55, 0.15) !important;
            }
        }

        // Strategy name cell
        .strategy-name-cell {
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-3);

            .strategy-icon {
                font-size: var(--artdeco-text-xl);
            }

            .strategy-info {
                display: flex;
                flex-direction: column;
                gap: var(--artdeco-spacing-1);

                .strategy-name {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-text-sm);
                    font-weight: 600;
                    color: var(--artdeco-fg-primary);
                }

                .strategy-code {
                    font-family: var(--artdeco-font-mono);
                    font-size: var(--artdeco-text-xs);
                    color: var(--artdeco-fg-muted);
                }
            }
        }

        // Metric values
        .metric-value {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-sm);
            font-weight: 600;
        }

        // Value colors
        .rise {
            color: var(--artdeco-rise);
        }

        .fall {
            color: var(--artdeco-fall);
        }

        .neutral {
            color: var(--artdeco-fg-muted);
        }

        // Sharpe ratio classes
        .excellent {
            color: var(--artdeco-rise);
            font-weight: 700;
        }

        .good {
            color: #66bb6a;
            font-weight: 600;
        }

        .fair {
            color: var(--artdeco-fg-muted);
        }

        .poor {
            color: var(--artdeco-fall);
        }

        // Drawdown classes
        .severe {
            color: #d32f2f;
            font-weight: 700;
        }

        .high {
            color: #f57c00;
            font-weight: 600;
        }

        .moderate {
            color: #fbc02d;
        }

        .mild {
            color: var(--artdeco-fg-muted);
        }

        // Action buttons
        .action-buttons {
            display: flex;
            gap: var(--artdeco-spacing-2);
        }
    }

    // ============================================
    //   PAGINATION
    // ============================================

    .pagination-wrapper {
        display: flex;
        justify-content: center;
        padding: var(--artdeco-spacing-6) 0;

        :deep(.el-pagination) {
            .el-pager li,
            .btn-prev,
            .btn-next {
                background: var(--artdeco-bg-card);
                border: 1px solid var(--artdeco-gold-dim);
                color: var(--artdeco-fg-primary);

                &:hover {
                    border-color: var(--artdeco-gold-primary);
                    color: var(--artdeco-gold-primary);
                }

                &.active {
                    background: var(--artdeco-gold-primary);
                    border-color: var(--artdeco-gold-primary);
                    color: var(--artdeco-bg-card);
                }
            }

            .el-pagination__sizes .el-select .el-input__wrapper {
                background: var(--artdeco-bg-card);
                border-color: var(--artdeco-gold-dim);
            }
        }
    }

    // ============================================
    //   TABLE FOOTER
    // ============================================

    .table-footer {
        padding: var(--artdeco-spacing-4) var(--artdeco-spacing-6);
        border-top: 1px solid var(--artdeco-gold-dim);

        .summary-stats {
            display: flex;
            justify-content: space-around;
            gap: var(--artdeco-spacing-6);

            .stat-item {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: var(--artdeco-spacing-2);

                .stat-label {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-text-xs);
                    font-weight: 600;
                    color: var(--artdeco-fg-muted);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                }

                .stat-value {
                    font-family: var(--artdeco-font-mono);
                    font-size: var(--artdeco-text-base);
                    font-weight: 700;

                    &.rise {
                        color: var(--artdeco-rise);
                    }

                    &.fall {
                        color: var(--artdeco-fall);
                    }
                }
            }
        }
    }
</style>
