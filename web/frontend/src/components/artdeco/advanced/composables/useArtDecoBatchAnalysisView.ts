import { ref, computed, onMounted, watch, type Ref } from 'vue'
import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
import _ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'
import ArtDecoSelect from '@/components/artdeco/base/ArtDecoSelect.vue'
import ArtDecoSwitch from '@/components/artdeco/base/ArtDecoSwitch.vue'
import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'

interface AnalysisResult {
    id?: string
    symbolName?: string
    signal: 'buy' | 'sell' | 'hold'
    confidence: number
    analysisType: string
    symbol: string
    completedAt: string
    [key: string]: unknown
}

interface ProgressData {
    total?: number
    completed?: number
    running?: number
    pending?: number
    failed?: number
    [key: string]: unknown
}

interface ReportInsight {
    id: string
    type: 'success' | 'warning' | 'error' | 'info'
    title: string
    description: string
}

interface ReportData {
    dataQuality?: number
    analysisDepth?: number
    insights?: ReportInsight[]
    [key: string]: unknown
}

interface BatchData {
    progress?: ProgressData
    results?: AnalysisResult[]
    report?: ReportData
    startTime?: string
    endTime?: string
    totalDataSize?: number
    [key: string]: unknown
}

interface PropsData {
    batch?: BatchData
    [key: string]: unknown
}

interface UseArtDecoBatchAnalysisViewOptions {
    data: Ref<PropsData>
    loading?: Ref<boolean>
}

export function useArtDecoBatchAnalysisView(options?: Partial<UseArtDecoBatchAnalysisViewOptions>) {
    const data = options?.data ?? ref<PropsData>({})
    const loading = options?.loading ?? ref(false)

    // 响应式数据
    const autoRefresh = ref(true)
    const resultsFilter = ref('all')
    const resultsSort = ref('time')

    // 计算属性
    const batchData = computed(() => data.value?.batch || {})
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
        const total = resultsData.value.reduce((sum: number, r: AnalysisResult) => sum + r.confidence, 0)
        return total / resultsData.value.length
    })

    const signalCoverage = computed(() => {
        if (!resultsData.value.length) return 0
        const signaled = resultsData.value.filter((r: AnalysisResult) => r.signal !== 'hold').length
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
    const buySignals = computed(() => resultsData.value.filter((r: AnalysisResult) => r.signal === 'buy').length)
    const sellSignals = computed(() => resultsData.value.filter((r: AnalysisResult) => r.signal === 'sell').length)
    const holdSignals = computed(() => resultsData.value.filter((r: AnalysisResult) => r.signal === 'hold').length)
    const highConfidenceSignals = computed(() => resultsData.value.filter((r: AnalysisResult) => r.confidence >= 80).length)

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
        resultsData.value.forEach((r: AnalysisResult) => {
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
                filtered = filtered.filter((r: AnalysisResult) => r.signal === 'buy')
            } else if (resultsFilter.value === 'sell') {
                filtered = filtered.filter((r: AnalysisResult) => r.signal === 'sell')
            } else if (resultsFilter.value === 'high-confidence') {
                filtered = filtered.filter((r: AnalysisResult) => r.confidence >= 80)
            }
        }

        // 排序
        if (resultsSort.value === 'time') {
            filtered.sort((a: AnalysisResult, b: AnalysisResult) => new Date(b.completedAt).getTime() - new Date(a.completedAt).getTime())
        } else if (resultsSort.value === 'confidence') {
            filtered.sort((a: AnalysisResult, b: AnalysisResult) => b.confidence - a.confidence)
        } else if (resultsSort.value === 'symbol') {
            filtered.sort((a: AnalysisResult, b: AnalysisResult) => a.symbol.localeCompare(b.symbol))
        }

        return filtered
    })

    const reportInsights = computed((): ReportInsight[] => reportData.value?.insights || [])

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

    const getResultClass = (result: AnalysisResult): string => {
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

  return {
    loading,
    autoRefresh,
    resultsFilter,
    resultsSort,
    batchData,
    progressData,
    resultsData,
    reportData,
    totalTasks,
    completedTasks,
    runningTasks,
    pendingTasks,
    failedTasks,
    overallProgress,
    avgConfidence,
    signalCoverage,
    dataQuality,
    analysisDepth,
    batchStartTime,
    batchEndTime,
    totalDuration,
    avgTaskDuration,
    buySignals,
    sellSignals,
    holdSignals,
    highConfidenceSignals,
    taskStatusData,
    analysisTypeData,
    filteredResults,
    reportInsights,
    filterOptions,
    sortOptions,
    getTotalTasks,
    getAvgProcessingTime,
    getSuccessRate,
    getTotalDataSize,
    getProgressClass,
    getResultClass,
    getSignalClass,
    getSignalText,
    getAnalysisTypeText,
    getQualityClass,
    formatTime,
    formatDuration,
    refreshProgress,
    exportReport,
    generateReport,
    saveReport,
    shareReport,
    scheduleReport,
    refreshTimer,
    startAutoRefresh,
    stopAutoRefresh,
  }
}
