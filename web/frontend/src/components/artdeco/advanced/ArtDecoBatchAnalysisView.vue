<template>
    <div class="artdeco-batch-analysis-view">
        <!-- 批量分析概览 -->
        <div class="batch-overview">
            <ArtDecoStatCard
                label="分析任务总数"
                :value="getTotalTasks()"
                description="已完成的批量分析任务"
                variant="default"
            />

            <ArtDecoStatCard
                label="平均处理时间"
                :value="getAvgProcessingTime()"
                description="单个任务平均处理时长"
                variant="default"
            />

            <ArtDecoStatCard
                label="成功率"
                :value="getSuccessRate()"
                description="批量分析任务成功率"
                variant="rise"
            />

            <ArtDecoStatCard
                label="总数据量"
                :value="getTotalDataSize()"
                description="批量分析处理的总数据量"
                variant="default"
            />
        </div>

        <!-- 批量分析进度 -->
        <ArtDecoCard class="batch-progress">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M12 2v6m0 0l4-4m-4 4L8 4m4 4v10m0 0l4-4m-4 4l-4-4"></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>批量分析进度</h4>
                        <p>BATCH ANALYSIS PROGRESS</p>
                    </div>
                    <div class="progress-controls">
                        <ArtDecoSwitch v-model="autoRefresh" label="自动刷新" />
                        <ArtDecoButton size="sm" variant="outline" @click="refreshProgress">刷新</ArtDecoButton>
                    </div>
                </div>
            </template>

            <div class="progress-dashboard">
                <div class="overall-progress">
                    <div class="progress-gauge">
                        <div class="gauge-container">
                            <div class="gauge-background">
                                <div
                                    class="gauge-fill"
                                    :style="{ transform: `rotate(${(overallProgress / 100) * 180 - 90}deg)` }"
                                    :class="getProgressClass(overallProgress)"
                                ></div>
                            </div>
                            <div class="gauge-center">
                                <div class="gauge-value">{{ overallProgress }}%</div>
                                <div class="gauge-label">完成进度</div>
                            </div>
                        </div>
                    </div>

                    <div class="progress-details">
                        <div class="detail-item">
                            <span class="label">已完成:</span>
                            <span class="value">{{ completedTasks }}/{{ totalTasks }}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">进行中:</span>
                            <span class="value">{{ runningTasks }}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">待处理:</span>
                            <span class="value">{{ pendingTasks }}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">失败:</span>
                            <span class="value">{{ failedTasks }}</span>
                        </div>
                    </div>
                </div>

                <div class="task-breakdown">
                    <div class="breakdown-charts">
                        <div class="chart-item">
                            <div class="chart-title">任务状态分布</div>
                            <div class="status-pie">
                                <!-- 任务状态饼图 -->
                                <div class="pie-chart">
                                    <div
                                        v-for="status in taskStatusData"
                                        :key="status.name"
                                        class="pie-segment"
                                        :style="{
                                            background: status.color,
                                            transform: `rotate(${status.startAngle}deg)`,
                                            clipPath: `polygon(50% 50%, 50% 0%, ${status.endAngle > 180 ? '100%' : Math.cos(((status.endAngle - 90) * Math.PI) / 180) * 50 + 50 + '%'} ${Math.sin(((status.endAngle - 90) * Math.PI) / 180) * 50 + 50 + '%'})`
                                        }"
                                    ></div>
                                    <div class="pie-center">
                                        <div class="center-text">{{ totalTasks }}</div>
                                        <div class="center-label">总任务</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="chart-item">
                            <div class="chart-title">分析类型分布</div>
                            <div class="type-bars">
                                <div v-for="type in analysisTypeData" :key="type.name" class="type-bar">
                                    <div class="bar-label">{{ type.name }}</div>
                                    <div class="bar-container">
                                        <div class="bar-fill" :style="{ width: type.percentage + '%' }"></div>
                                    </div>
                                    <div class="bar-value">{{ type.count }}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 批量分析结果 -->
        <ArtDecoCard class="batch-results">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>批量分析结果</h4>
                        <p>BATCH ANALYSIS RESULTS</p>
                    </div>
                    <div class="results-controls">
                        <ArtDecoSelect v-model="resultsFilter" :options="filterOptions" size="sm" />
                        <ArtDecoSelect v-model="resultsSort" :options="sortOptions" size="sm" />
                    </div>
                </div>
            </template>

            <div class="results-content">
                <div class="results-summary">
                    <div class="summary-stats">
                        <div class="stat-item">
                            <div class="stat-label">平均置信度</div>
                            <div class="stat-value">{{ avgConfidence.toFixed(1) }}%</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">信号覆盖率</div>
                            <div class="stat-value">{{ signalCoverage.toFixed(1) }}%</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">数据质量评分</div>
                            <div class="stat-value" :class="getQualityClass(dataQuality)">{{ dataQuality }}/100</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">分析深度</div>
                            <div class="stat-value">{{ analysisDepth }}/10</div>
                        </div>
                    </div>
                </div>

                <div class="results-list">
                    <div class="results-table">
                        <div class="table-header">
                            <div class="col-symbol">股票代码</div>
                            <div class="col-analysis">分析类型</div>
                            <div class="col-signal">信号</div>
                            <div class="col-confidence">置信度</div>
                            <div class="col-time">完成时间</div>
                        </div>
                        <div class="table-body">
                            <div
                                v-for="result in filteredResults"
                                :key="result.id"
                                class="table-row"
                                :class="getResultClass(result)"
                            >
                                <div class="col-symbol">
                                    <div class="symbol-code">{{ result.symbol }}</div>
                                    <div class="symbol-name">{{ result.symbolName }}</div>
                                </div>
                                <div class="col-analysis">
                                    <span class="analysis-type">{{ getAnalysisTypeText(result.analysisType) }}</span>
                                </div>
                                <div class="col-signal">
                                    <span :class="getSignalClass(result.signal)">
                                        {{ getSignalText(result.signal) }}
                                    </span>
                                </div>
                                <div class="col-confidence">
                                    <div class="confidence-bar">
                                        <div class="confidence-fill" :style="{ width: result.confidence + '%' }"></div>
                                    </div>
                                    <div class="confidence-text">{{ result.confidence }}%</div>
                                </div>
                                <div class="col-time">
                                    {{ formatTime(result.completedAt) }}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 批量分析报告 -->
        <ArtDecoCard class="batch-report">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path
                                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                            ></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>批量分析报告</h4>
                        <p>BATCH ANALYSIS REPORT</p>
                    </div>
                    <div class="report-controls">
                        <ArtDecoButton size="sm" @click="exportReport">导出报告</ArtDecoButton>
                        <ArtDecoButton size="sm" variant="outline" @click="generateReport">生成报告</ArtDecoButton>
                    </div>
                </div>
            </template>

            <div class="report-content">
                <div class="report-summary">
                    <div class="summary-section">
                        <h5>执行概况</h5>
                        <div class="summary-grid">
                            <div class="summary-item">
                                <div class="item-label">开始时间</div>
                                <div class="item-value">{{ formatTime(batchStartTime) }}</div>
                            </div>
                            <div class="summary-item">
                                <div class="item-label">结束时间</div>
                                <div class="item-value">{{ formatTime(batchEndTime) }}</div>
                            </div>
                            <div class="summary-item">
                                <div class="item-label">总耗时</div>
                                <div class="item-value">{{ formatDuration(totalDuration) }}</div>
                            </div>
                            <div class="summary-item">
                                <div class="item-label">平均耗时</div>
                                <div class="item-value">{{ formatDuration(avgTaskDuration) }}</div>
                            </div>
                        </div>
                    </div>

                    <div class="summary-section">
                        <h5>结果统计</h5>
                        <div class="summary-grid">
                            <div class="summary-item">
                                <div class="item-label">买入信号</div>
                                <div class="item-value">{{ buySignals }}</div>
                            </div>
                            <div class="summary-item">
                                <div class="item-label">卖出信号</div>
                                <div class="item-value">{{ sellSignals }}</div>
                            </div>
                            <div class="summary-item">
                                <div class="item-label">持有信号</div>
                                <div class="item-value">{{ holdSignals }}</div>
                            </div>
                            <div class="summary-item">
                                <div class="item-label">高置信度信号</div>
                                <div class="item-value">{{ highConfidenceSignals }}</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="report-insights">
                    <h5>关键洞察</h5>
                    <div class="insights-list">
                        <div
                            v-for="insight in reportInsights"
                            :key="insight.id"
                            class="insight-item"
                            :class="insight.type"
                        >
                            <div class="insight-icon">
                                <svg
                                    v-if="insight.type === 'success'"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                >
                                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                                <svg
                                    v-else-if="insight.type === 'warning'"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                >
                                    <path d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                                </svg>
                            </div>
                            <div class="insight-content">
                                <div class="insight-title">{{ insight.title }}</div>
                                <div class="insight-description">{{ insight.description }}</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="report-actions">
                    <div class="action-buttons">
                        <ArtDecoButton @click="saveReport" variant="outline">保存报告</ArtDecoButton>
                        <ArtDecoButton @click="shareReport" variant="outline">分享报告</ArtDecoButton>
                        <ArtDecoButton @click="scheduleReport" variant="outline">定时报告</ArtDecoButton>
                    </div>
                </div>
            </div>
        </ArtDecoCard>
    </div>
</template>

<script setup lang="ts">
    import { ref, computed, onMounted, watch } from 'vue'
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
    import ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'
    import ArtDecoSelect from '@/components/artdeco/base/ArtDecoSelect.vue'
    import ArtDecoSwitch from '@/components/artdeco/base/ArtDecoSwitch.vue'
    import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'

    interface Props {
        data: any
        loading?: boolean
    }

    const props = defineProps<Props>()

    // 响应式数据
    const autoRefresh = ref(true)
    const resultsFilter = ref('all')
    const resultsSort = ref('time')

    // 计算属性
    const batchData = computed(() => props.data?.batch || {})
    const progressData = computed(() => batchData.value?.progress || {})
    const resultsData = computed(() => batchData.value?.results || [])
    const reportData = computed(() => batchData.value?.report || {})

    // 进度相关计算属性
    const totalTasks = computed(() => progressData.value?.total || 0)
    const completedTasks = computed(() => progressData.value?.completed || 0)
    const runningTasks = computed(() => progressData.value?.running || 0)
    const pendingTasks = computed(() => progressData.value?.pending || 0)
    const failedTasks = computed(() => progressData.value?.failed || 0)

    const overallProgress = computed(() => {
        if (totalTasks.value === 0) return 0
        return Math.round((completedTasks.value / totalTasks.value) * 100)
    })

    // 结果相关计算属性
    const avgConfidence = computed(() => {
        if (!resultsData.value.length) return 0
        const total = resultsData.value.reduce((sum: number, r: any) => sum + r.confidence, 0)
        return total / resultsData.value.length
    })

    const signalCoverage = computed(() => {
        if (!resultsData.value.length) return 0
        const signaled = resultsData.value.filter((r: any) => r.signal !== 'hold').length
        return (signaled / resultsData.value.length) * 100
    })

    const dataQuality = computed(() => reportData.value?.dataQuality || 0)
    const analysisDepth = computed(() => reportData.value?.analysisDepth || 0)

    // 时间相关计算属性
    const batchStartTime = computed(() => batchData.value?.startTime || new Date().toISOString())
    const batchEndTime = computed(() => batchData.value?.endTime || new Date().toISOString())
    const totalDuration = computed(() => {
        const start = new Date(batchStartTime.value).getTime()
        const end = new Date(batchEndTime.value).getTime()
        return end - start
    })

    const avgTaskDuration = computed(() => {
        if (completedTasks.value === 0) return 0
        return totalDuration.value / completedTasks.value
    })

    // 信号统计
    const buySignals = computed(() => resultsData.value.filter((r: any) => r.signal === 'buy').length)
    const sellSignals = computed(() => resultsData.value.filter((r: any) => r.signal === 'sell').length)
    const holdSignals = computed(() => resultsData.value.filter((r: any) => r.signal === 'hold').length)
    const highConfidenceSignals = computed(() => resultsData.value.filter((r: any) => r.confidence >= 80).length)

    // 图表数据
    const taskStatusData = computed(() => [
        {
            name: 'completed',
            count: completedTasks.value,
            color: '#22c55e',
            startAngle: 0,
            endAngle: (completedTasks.value / totalTasks.value) * 360
        },
        {
            name: 'running',
            count: runningTasks.value,
            color: '#3b82f6',
            startAngle: (completedTasks.value / totalTasks.value) * 360,
            endAngle: ((completedTasks.value + runningTasks.value) / totalTasks.value) * 360
        },
        {
            name: 'pending',
            count: pendingTasks.value,
            color: '#f59e0b',
            startAngle: ((completedTasks.value + runningTasks.value) / totalTasks.value) * 360,
            endAngle: ((completedTasks.value + runningTasks.value + pendingTasks.value) / totalTasks.value) * 360
        },
        {
            name: 'failed',
            count: failedTasks.value,
            color: '#ef4444',
            startAngle: ((completedTasks.value + runningTasks.value + pendingTasks.value) / totalTasks.value) * 360,
            endAngle: 360
        }
    ])

    const analysisTypeData = computed(() => {
        const types: Record<string, number> = {}
        resultsData.value.forEach((r: any) => {
            types[r.analysisType] = (types[r.analysisType] || 0) + 1
        })

        return Object.entries(types).map(([name, count]) => ({
            name: getAnalysisTypeText(name),
            count,
            percentage: (count / resultsData.value.length) * 100
        }))
    })

    const filteredResults = computed(() => {
        let filtered = [...resultsData.value]

        // 过滤
        if (resultsFilter.value !== 'all') {
            if (resultsFilter.value === 'buy') {
                filtered = filtered.filter(r => r.signal === 'buy')
            } else if (resultsFilter.value === 'sell') {
                filtered = filtered.filter(r => r.signal === 'sell')
            } else if (resultsFilter.value === 'high-confidence') {
                filtered = filtered.filter(r => r.confidence >= 80)
            }
        }

        // 排序
        if (resultsSort.value === 'time') {
            filtered.sort((a: any, b: any) => new Date(b.completedAt).getTime() - new Date(a.completedAt).getTime())
        } else if (resultsSort.value === 'confidence') {
            filtered.sort((a: any, b: any) => b.confidence - a.confidence)
        } else if (resultsSort.value === 'symbol') {
            filtered.sort((a: any, b: any) => a.symbol.localeCompare(b.symbol))
        }

        return filtered
    })

    const reportInsights = computed(() => reportData.value?.insights || [])

    // 配置选项
    const filterOptions = [
        { label: '全部结果', value: 'all' },
        { label: '买入信号', value: 'buy' },
        { label: '卖出信号', value: 'sell' },
        { label: '高置信度', value: 'high-confidence' }
    ]

    const sortOptions = [
        { label: '完成时间', value: 'time' },
        { label: '置信度', value: 'confidence' },
        { label: '股票代码', value: 'symbol' }
    ]

    // 格式化函数
    const getTotalTasks = (): string => {
        return totalTasks.value.toString()
    }

    const getAvgProcessingTime = (): string => {
        const duration = avgTaskDuration.value
        if (duration < 1000) return `${duration.toFixed(0)}ms`
        if (duration < 60000) return `${(duration / 1000).toFixed(1)}s`
        if (duration < 3600000) return `${(duration / 60000).toFixed(1)}m`
        return `${(duration / 3600000).toFixed(1)}h`
    }

    const getSuccessRate = (): string => {
        if (totalTasks.value === 0) return '0%'
        const successRate = ((completedTasks.value - failedTasks.value) / totalTasks.value) * 100
        return `${successRate.toFixed(1)}%`
    }

    const getTotalDataSize = (): string => {
        const size = batchData.value?.totalDataSize || 0
        if (size < 1024) return `${size}B`
        if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)}KB`
        if (size < 1024 * 1024 * 1024) return `${(size / (1024 * 1024)).toFixed(1)}MB`
        return `${(size / (1024 * 1024 * 1024)).toFixed(1)}GB`
    }

    const getProgressClass = (progress: number): string => {
        if (progress >= 80) return 'completed'
        if (progress >= 50) return 'in-progress'
        return 'starting'
    }

    const getResultClass = (result: any): string => {
        if (result.signal === 'buy') return 'buy-signal'
        if (result.signal === 'sell') return 'sell-signal'
        return 'hold-signal'
    }

    const getSignalClass = (signal: string): string => {
        if (signal === 'buy') return 'buy'
        if (signal === 'sell') return 'sell'
        return 'hold'
    }

    const getSignalText = (signal: string): string => {
        const texts: Record<string, string> = {
            buy: '买入',
            sell: '卖出',
            hold: '持有'
        }
        return texts[signal] || signal
    }

    const getAnalysisTypeText = (type: string): string => {
        const texts: Record<string, string> = {
            technical: '技术分析',
            fundamental: '基本面分析',
            sentiment: '情绪分析',
            valuation: '估值分析',
            comprehensive: '综合分析'
        }
        return texts[type] || type
    }

    const getQualityClass = (quality: number): string => {
        if (quality >= 80) return 'excellent'
        if (quality >= 60) return 'good'
        return 'poor'
    }

    const formatTime = (timestamp: string): string => {
        return new Date(timestamp).toLocaleString('zh-CN', {
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    const formatDuration = (duration: number): string => {
        if (duration < 1000) return `${duration.toFixed(0)}ms`
        if (duration < 60000) return `${(duration / 1000).toFixed(1)}s`
        if (duration < 3600000) return `${(duration / 60000).toFixed(1)}m`
        return `${(duration / 3600000).toFixed(1)}h`
    }

    // 事件处理
    const refreshProgress = () => {
        console.log('Refreshing batch progress...')
        // 这里可以调用API刷新进度
    }

    const exportReport = () => {
        console.log('Exporting batch report...')
        // 这里可以调用API导出报告
    }

    const generateReport = () => {
        console.log('Generating batch report...')
        // 这里可以调用API生成报告
    }

    const saveReport = () => {
        console.log('Saving batch report...')
        // 这里可以调用API保存报告
    }

    const shareReport = () => {
        console.log('Sharing batch report...')
        // 这里可以调用API分享报告
    }

    const scheduleReport = () => {
        console.log('Scheduling batch report...')
        // 这里可以调用API设置定时报告
    }

    // 自动刷新
    let refreshTimer: number | null = null

    const startAutoRefresh = () => {
        if (autoRefresh.value && !refreshTimer) {
            refreshTimer = setInterval(() => {
                refreshProgress()
            }, 5000) as unknown as number
        }
    }

    const stopAutoRefresh = () => {
        if (refreshTimer) {
            clearInterval(refreshTimer)
            refreshTimer = null
        }
    }

    // 生命周期
    onMounted(() => {
        startAutoRefresh()
    })

    // 监听自动刷新变化
    watch(autoRefresh, newValue => {
        if (newValue) {
            startAutoRefresh()
        } else {
            stopAutoRefresh()
        }
    })
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-batch-analysis-view {
        display: grid;
        gap: var(--artdeco-spacing-6);
    }

    // ============================================
    //   BATCH OVERVIEW - 批量概览
    // ============================================

    .batch-overview {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    // ============================================
    //   BATCH PROGRESS - 批量进度
    // ============================================

    .batch-progress {
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-4);

            .header-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, var(--artdeco-gold-primary), var(--artdeco-gold-secondary));
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--artdeco-bg-dark);

                svg {
                    width: 24px;
                    height: 24px;
                }
            }

            .header-content {
                flex: 1;
                margin-left: var(--artdeco-spacing-4);

                h4 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-lg);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-1) 0;
                }

                p {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-font-size-xs);
                    color: var(--artdeco-fg-muted);
                    margin: 0;
                    letter-spacing: var(--artdeco-tracking-normal);
                }
            }

            .progress-controls {
                display: flex;
                gap: var(--artdeco-spacing-3);
                align-items: center;
            }
        }

        .progress-dashboard {
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: var(--artdeco-spacing-5);

            .overall-progress {
                display: grid;
                grid-template-columns: 150px 1fr;
                gap: var(--artdeco-spacing-4);

                .progress-gauge {
                    .gauge-container {
                        position: relative;
                        width: 120px;
                        height: 120px;
                        margin: 0 auto;

                        .gauge-background {
                            position: relative;
                            width: 100%;
                            height: 100%;
                            border-radius: 50%;
                            background: conic-gradient(
                                from 0deg,
                                rgba(239, 68, 68, 0.2) 0deg,
                                rgba(245, 158, 11, 0.4) 45deg,
                                rgba(34, 197, 94, 0.6) 90deg,
                                rgba(34, 197, 94, 0.6) 180deg,
                                rgba(34, 197, 94, 0.6) 180deg
                            );

                            .gauge-fill {
                                position: absolute;
                                top: 0;
                                left: 0;
                                width: 100%;
                                height: 100%;
                                border-radius: 50%;
                                background: conic-gradient(
                                    from 0deg,
                                    transparent 0deg,
                                    transparent 180deg,
                                    rgba(34, 197, 94, 0.9) 180deg,
                                    rgba(34, 197, 94, 0.9) 360deg
                                );
                                clip-path: polygon(50% 50%, 50% 50%, 50% 0%, 100% 0%, 100% 100%, 50% 100%);
                                transition: transform var(--artdeco-transition-base);

                                &.completed {
                                    background: conic-gradient(
                                        from 0deg,
                                        transparent 0deg,
                                        transparent 180deg,
                                        rgba(34, 197, 94, 0.9) 180deg,
                                        rgba(34, 197, 94, 0.9) 360deg
                                    );
                                }

                                &.in-progress {
                                    background: conic-gradient(
                                        from 0deg,
                                        transparent 0deg,
                                        transparent 180deg,
                                        rgba(245, 158, 11, 0.9) 180deg,
                                        rgba(245, 158, 11, 0.9) 360deg
                                    );
                                }

                                &.starting {
                                    background: conic-gradient(
                                        from 0deg,
                                        transparent 0deg,
                                        transparent 180deg,
                                        rgba(239, 68, 68, 0.9) 180deg,
                                        rgba(239, 68, 68, 0.9) 360deg
                                    );
                                }
                            }
                        }

                        .gauge-center {
                            position: absolute;
                            top: 50%;
                            left: 50%;
                            transform: translate(-50%, -50%);
                            text-align: center;

                            .gauge-value {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-xl);
                                font-weight: 600;
                                color: var(--artdeco-up);
                                display: block;
                                margin-bottom: var(--artdeco-spacing-1);
                            }

                            .gauge-label {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-xs);
                                color: var(--artdeco-fg-muted);
                                text-transform: uppercase;
                                letter-spacing: var(--artdeco-tracking-wide);
                            }
                        }
                    }
                }

                .progress-details {
                    display: flex;
                    flex-direction: column;
                    gap: var(--artdeco-spacing-2);

                    .detail-item {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding: var(--artdeco-spacing-2);
                        background: var(--artdeco-bg-muted);
                        border-radius: 4px;

                        .label {
                            font-family: var(--artdeco-font-body);
                            font-size: var(--artdeco-font-size-sm);
                            color: var(--artdeco-fg-muted);
                            font-weight: 600;
                        }

                        .value {
                            font-family: var(--artdeco-font-mono);
                            font-size: var(--artdeco-font-size-sm);
                            color: var(--artdeco-fg-primary);
                            font-weight: 600;
                        }
                    }
                }
            }

            .task-breakdown {
                .breakdown-charts {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: var(--artdeco-spacing-4);

                    .chart-item {
                        .chart-title {
                            font-family: var(--artdeco-font-display);
                            font-size: var(--artdeco-font-size-md);
                            font-weight: 600;
                            color: var(--artdeco-gold-primary);
                            text-transform: uppercase;
                            letter-spacing: var(--artdeco-tracking-wide);
                            margin: 0 0 var(--artdeco-spacing-3) 0;
                        }

                        .status-pie {
                            height: 200px;
                            position: relative;

                            .pie-chart {
                                position: relative;
                                width: 150px;
                                height: 150px;
                                margin: 0 auto;
                                border-radius: 50%;

                                .pie-segment {
                                    position: absolute;
                                    width: 100%;
                                    height: 100%;
                                    border-radius: 50%;
                                    clip-path: polygon(50% 50%, 50% 0%, 100% 0%, 100% 100%, 0% 100%, 0% 0%);
                                }

                                .pie-center {
                                    position: absolute;
                                    top: 50%;
                                    left: 50%;
                                    transform: translate(-50%, -50%);
                                    text-align: center;

                                    .center-text {
                                        font-family: var(--artdeco-font-mono);
                                        font-size: var(--artdeco-font-size-lg);
                                        font-weight: 600;
                                        color: var(--artdeco-gold-primary);
                                        display: block;
                                        margin-bottom: var(--artdeco-spacing-1);
                                    }

                                    .center-label {
                                        font-family: var(--artdeco-font-body);
                                        font-size: var(--artdeco-font-size-xs);
                                        color: var(--artdeco-fg-muted);
                                        text-transform: uppercase;
                                        letter-spacing: var(--artdeco-tracking-wide);
                                    }
                                }
                            }
                        }

                        .type-bars {
                            display: flex;
                            flex-direction: column;
                            gap: var(--artdeco-spacing-2);

                            .type-bar {
                                display: flex;
                                align-items: center;
                                gap: var(--artdeco-spacing-3);

                                .bar-label {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-sm);
                                    color: var(--artdeco-fg-primary);
                                    font-weight: 600;
                                    min-width: 80px;
                                }

                                .bar-container {
                                    flex: 1;
                                    height: 12px;
                                    background: var(--artdeco-bg-muted);
                                    border-radius: 6px;
                                    overflow: hidden;

                                    .bar-fill {
                                        height: 100%;
                                        background: linear-gradient(
                                            90deg,
                                            var(--artdeco-gold-primary),
                                            var(--artdeco-gold-secondary)
                                        );
                                        border-radius: 6px;
                                        transition: width var(--artdeco-transition-base);
                                    }
                                }

                                .bar-value {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-sm);
                                    color: var(--artdeco-fg-muted);
                                    font-weight: 600;
                                    min-width: 40px;
                                    text-align: right;
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // ============================================
    //   BATCH RESULTS - 批量结果
    // ============================================

    .batch-results {
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-4);

            .header-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, var(--artdeco-gold-primary), var(--artdeco-gold-secondary));
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--artdeco-bg-dark);

                svg {
                    width: 24px;
                    height: 24px;
                }
            }

            .header-content {
                flex: 1;
                margin-left: var(--artdeco-spacing-4);

                h4 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-lg);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-1) 0;
                }

                p {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-font-size-xs);
                    color: var(--artdeco-fg-muted);
                    margin: 0;
                    letter-spacing: var(--artdeco-tracking-normal);
                }
            }

            .results-controls {
                display: flex;
                gap: var(--artdeco-spacing-3);
                align-items: center;
            }
        }

        .results-content {
            .results-summary {
                margin-bottom: var(--artdeco-spacing-5);

                .summary-stats {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: var(--artdeco-spacing-4);

                    .stat-item {
                        text-align: center;
                        padding: var(--artdeco-spacing-3);
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;

                        .stat-label {
                            font-family: var(--artdeco-font-body);
                            font-size: var(--artdeco-font-size-sm);
                            color: var(--artdeco-fg-muted);
                            text-transform: uppercase;
                            letter-spacing: var(--artdeco-tracking-wide);
                            margin-bottom: var(--artdeco-spacing-2);
                        }

                        .stat-value {
                            font-family: var(--artdeco-font-mono);
                            font-size: var(--artdeco-font-size-xl);
                            font-weight: 600;

                            &.excellent {
                                color: var(--artdeco-up);
                            }

                            &.good {
                                color: var(--artdeco-gold-primary);
                            }

                            &.poor {
                                color: var(--artdeco-down);
                            }
                        }
                    }
                }
            }

            .results-list {
                .results-table {
                    .table-header {
                        display: grid;
                        grid-template-columns: 1.5fr 1fr 1fr 1fr 1fr;
                        gap: var(--artdeco-spacing-4);
                        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
                        background: linear-gradient(135deg, var(--artdeco-bg-muted), rgba(212, 175, 55, 0.05));
                        border-bottom: 1px solid var(--artdeco-border-default);
                        font-family: var(--artdeco-font-body);
                        font-size: var(--artdeco-font-size-sm);
                        font-weight: 600;
                        color: var(--artdeco-fg-muted);
                        text-transform: uppercase;
                        letter-spacing: var(--artdeco-tracking-wide);
                    }

                    .table-body {
                        .table-row {
                            display: grid;
                            grid-template-columns: 1.5fr 1fr 1fr 1fr 1fr;
                            gap: var(--artdeco-spacing-4);
                            padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
                            border-bottom: 1px solid rgba(212, 175, 55, 0.1);
                            transition: all var(--artdeco-transition-base);

                            &:hover {
                                background: rgba(212, 175, 55, 0.02);
                            }

                            &.buy-signal {
                                border-left: 3px solid var(--artdeco-up);
                            }

                            &.sell-signal {
                                border-left: 3px solid var(--artdeco-down);
                            }

                            &.hold-signal {
                                border-left: 3px solid var(--artdeco-gold-primary);
                            }

                            .col-symbol {
                                .symbol-code {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-md);
                                    font-weight: 600;
                                    color: var(--artdeco-fg-primary);
                                    display: block;
                                    margin-bottom: var(--artdeco-spacing-1);
                                }

                                .symbol-name {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-sm);
                                    color: var(--artdeco-fg-muted);
                                }
                            }

                            .col-analysis {
                                .analysis-type {
                                    padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
                                    background: var(--artdeco-gold-primary);
                                    color: var(--artdeco-bg-dark);
                                    border-radius: 4px;
                                    font-size: var(--artdeco-font-size-xs);
                                    font-weight: 600;
                                    text-transform: uppercase;
                                    letter-spacing: var(--artdeco-tracking-wide);
                                }
                            }

                            .col-signal {
                                span {
                                    padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
                                    border-radius: 4px;
                                    font-size: var(--artdeco-font-size-sm);
                                    font-weight: 600;
                                    text-transform: uppercase;
                                    letter-spacing: var(--artdeco-tracking-wide);

                                    &.buy {
                                        background: var(--artdeco-up);
                                        color: white;
                                    }

                                    &.sell {
                                        background: var(--artdeco-down);
                                        color: white;
                                    }

                                    &.hold {
                                        background: var(--artdeco-gold-primary);
                                        color: var(--artdeco-bg-dark);
                                    }
                                }
                            }

                            .col-confidence {
                                .confidence-bar {
                                    width: 60px;
                                    height: 6px;
                                    background: var(--artdeco-bg-muted);
                                    border-radius: 3px;
                                    overflow: hidden;
                                    margin-bottom: var(--artdeco-spacing-1);

                                    .confidence-fill {
                                        height: 100%;
                                        background: linear-gradient(
                                            90deg,
                                            var(--artdeco-gold-primary),
                                            var(--artdeco-gold-secondary)
                                        );
                                        border-radius: 3px;
                                        transition: width var(--artdeco-transition-base);
                                    }
                                }

                                .confidence-text {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);
                                    font-weight: 600;
                                }
                            }

                            .col-time {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-xs);
                                color: var(--artdeco-fg-muted);
                            }
                        }
                    }
                }
            }
        }
    }

    // ============================================
    //   BATCH REPORT - 批量报告
    // ============================================

    .batch-report {
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-4);

            .header-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, var(--artdeco-gold-primary), var(--artdeco-gold-secondary));
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--artdeco-bg-dark);

                svg {
                    width: 24px;
                    height: 24px;
                }
            }

            .header-content {
                flex: 1;
                margin-left: var(--artdeco-spacing-4);

                h4 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-lg);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-1) 0;
                }

                p {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-font-size-xs);
                    color: var(--artdeco-fg-muted);
                    margin: 0;
                    letter-spacing: var(--artdeco-tracking-normal);
                }
            }

            .report-controls {
                display: flex;
                gap: var(--artdeco-spacing-3);
                align-items: center;
            }
        }

        .report-content {
            .report-summary {
                margin-bottom: var(--artdeco-spacing-5);

                .summary-section {
                    margin-bottom: var(--artdeco-spacing-4);

                    &:last-child {
                        margin-bottom: 0;
                    }

                    h5 {
                        font-family: var(--artdeco-font-display);
                        font-size: var(--artdeco-font-size-md);
                        font-weight: 600;
                        color: var(--artdeco-gold-primary);
                        text-transform: uppercase;
                        letter-spacing: var(--artdeco-tracking-wide);
                        margin: 0 0 var(--artdeco-spacing-3) 0;
                    }

                    .summary-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: var(--artdeco-spacing-4);

                        .summary-item {
                            padding: var(--artdeco-spacing-3);
                            background: var(--artdeco-bg-card);
                            border: 1px solid var(--artdeco-border-default);
                            border-radius: 6px;
                            text-align: center;

                            .item-label {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-sm);
                                color: var(--artdeco-fg-muted);
                                text-transform: uppercase;
                                letter-spacing: var(--artdeco-tracking-wide);
                                margin-bottom: var(--artdeco-spacing-2);
                            }

                            .item-value {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-md);
                                font-weight: 600;
                                color: var(--artdeco-gold-primary);
                            }
                        }
                    }
                }
            }

            .report-insights {
                margin-bottom: var(--artdeco-spacing-5);

                h5 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-md);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-4) 0;
                }

                .insights-list {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: var(--artdeco-spacing-4);

                    .insight-item {
                        display: flex;
                        gap: var(--artdeco-spacing-3);
                        padding: var(--artdeco-spacing-4);
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;
                        transition: all var(--artdeco-transition-base);

                        &:hover {
                            border-color: var(--artdeco-gold-primary);
                            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                        }

                        &.success {
                            border-left: 3px solid var(--artdeco-up);
                        }

                        &.warning {
                            border-left: 3px solid #f59e0b;
                        }

                        &.info {
                            border-left: 3px solid var(--artdeco-gold-primary);
                        }

                        .insight-icon {
                            flex-shrink: 0;
                            width: 24px;
                            height: 24px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: var(--artdeco-fg-primary);
                        }

                        .insight-content {
                            flex: 1;

                            .insight-title {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-md);
                                font-weight: 600;
                                color: var(--artdeco-fg-primary);
                                margin-bottom: var(--artdeco-spacing-1);
                            }

                            .insight-description {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-sm);
                                color: var(--artdeco-fg-secondary);
                                line-height: 1.5;
                            }
                        }
                    }
                }
            }

            .report-actions {
                .action-buttons {
                    display: flex;
                    gap: var(--artdeco-spacing-3);
                    justify-content: center;
                    flex-wrap: wrap;
                }
            }
        }
    }

    // ============================================
    //   RESPONSIVE DESIGN - 响应式设计
    // ============================================

    @media (max-width: 768px) {
        .artdeco-batch-analysis-view {
            gap: var(--artdeco-spacing-4);
        }

        .batch-overview {
            grid-template-columns: 1fr;
        }

        .batch-progress {
            .section-header {
                flex-direction: column;
                align-items: flex-start;
                gap: var(--artdeco-spacing-3);

                .header-content {
                    margin-left: 0;
                }

                .progress-controls {
                    width: 100%;
                    justify-content: space-between;
                    flex-wrap: wrap;
                }
            }

            .progress-dashboard {
                grid-template-columns: 1fr;
            }
        }

        .batch-results {
            .section-header {
                flex-direction: column;
                align-items: flex-start;
                gap: var(--artdeco-spacing-3);

                .header-content {
                    margin-left: 0;
                }

                .results-controls {
                    width: 100%;
                    justify-content: space-between;
                    flex-wrap: wrap;
                }
            }

            .results-content {
                .results-summary {
                    .summary-stats {
                        grid-template-columns: 1fr;
                    }
                }

                .results-list {
                    .results-table {
                        .table-header,
                        .table-row {
                            grid-template-columns: 1fr;
                            gap: var(--artdeco-spacing-2);
                        }
                    }
                }
            }
        }

        .batch-report {
            .section-header {
                flex-direction: column;
                align-items: flex-start;
                gap: var(--artdeco-spacing-3);

                .header-content {
                    margin-left: 0;
                }

                .report-controls {
                    width: 100%;
                    justify-content: space-between;
                    flex-wrap: wrap;
                }
            }

            .report-content {
                .report-summary {
                    .summary-section {
                        .summary-grid {
                            grid-template-columns: 1fr;
                        }
                    }
                }

                .report-insights {
                    .insights-list {
                        grid-template-columns: 1fr;
                    }
                }

                .report-actions {
                    .action-buttons {
                        justify-content: center;
                    }
                }
            }
        }
    }
</style>
