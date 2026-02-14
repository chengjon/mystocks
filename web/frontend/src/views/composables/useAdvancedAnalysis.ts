    import { ref, computed, onMounted, onUnmounted } from 'vue'
    import { ElMessage } from 'element-plus'
    import { advancedAnalysisApi } from '@/api/advancedAnalysis'
    import { PageHeader } from '@/components/shared'
    import FundamentalAnalysisView from './advanced-analysis/FundamentalAnalysisView.vue'
    import TechnicalAnalysisView from './advanced-analysis/TechnicalAnalysisView.vue'
    import RadarAnalysisView from './advanced-analysis/RadarAnalysisView.vue'
    import TradingSignalsView from './advanced-analysis/TradingSignalsView.vue'
    import TimeSeriesView from './advanced-analysis/TimeSeriesView.vue'
    import MarketPanoramaView from './advanced-analysis/MarketPanoramaView.vue'
    import CapitalFlowView from './advanced-analysis/CapitalFlowView.vue'
    import ChipDistributionView from './advanced-analysis/ChipDistributionView.vue'
    import AnomalyTrackingView from './advanced-analysis/AnomalyTrackingView.vue'
    import FinancialValuationView from './advanced-analysis/FinancialValuationView.vue'
    import SentimentAnalysisView from './advanced-analysis/SentimentAnalysisView.vue'
    import DecisionModelsView from './advanced-analysis/DecisionModelsView.vue'
    import BatchAnalysisView from './advanced-analysis/BatchAnalysisView.vue'
    interface AnalysisForm {
    interface AnalysisResult {
    interface HealthStatus {

export function useAdvancedAnalysis() {

    // 分析结果视图组件

        symbol: string
        analysisType: string
        includeRawData: boolean
        enableRealtime: boolean
    }

        overall_signal?: string
        fundamental?: unknown
        technical?: unknown
        trading_signals?: unknown
        time_series?: unknown
        market_panorama?: unknown
        capital_flow?: unknown
        chip_distribution?: unknown
        anomaly_tracking?: unknown
        financial_valuation?: unknown
        sentiment?: unknown
        decision_models?: unknown
        multidimensional_radar?: unknown
    }

        database: string
        api: string
        gpu: string
    }

    const loading = ref(false)
    const batchLoading = ref(false)
    const analysisResult = ref<AnalysisResult | null>(null)
    const batchResults = ref<unknown>(null)
    const realtimeInterval = ref<NodeJS.Timeout | null>(null)

    const form = ref<AnalysisForm>({
        symbol: '',
        analysisType: 'fundamental',
        includeRawData: false,
        enableRealtime: false
    })

    const healthStatus = ref<HealthStatus>({
        database: 'healthy',
        api: 'healthy',
        gpu: 'warning'
    })

    const overviewMetrics = computed(() => {
        if (!analysisResult.value) return []

        const metrics = []
        const result = analysisResult.value

        // 添加关键指标
        if (result.overall_signal) {
            metrics.push({
                key: 'signal',
                label: '总体信号',
                value: result.overall_signal,
                class: getSignalClass(result.overall_signal)
            })
        }

        return metrics
    })

    const getAnalysisTitle = (): string => {
        const titles: Record<string, string> = {
            fundamental: '基本面分析',
            technical: '技术面分析',
            'trading-signals': '交易信号分析',
            'time-series': '时序分析',
            'market-panorama': '市场全景分析',
            'capital-flow': '资金流向分析',
            'chip-distribution': '筹码分布分析',
            'anomaly-tracking': '异常追踪分析',
            'financial-valuation': '财务估值分析',
            sentiment: '情绪分析',
            'decision-models': '决策模型分析',
            'multidimensional-radar': '多维度雷达分析'
        }
        return titles[form.value.analysisType] || '高级分析'
    }

    const getOverallSignalType = (): 'success' | 'danger' | 'warning' | 'info' => {
        if (!analysisResult.value?.overall_signal) return 'info'
        const signal = analysisResult.value.overall_signal.toLowerCase()
        if (signal.includes('买') || signal.includes('强')) return 'success'
        if (signal.includes('卖') || signal.includes('弱')) return 'danger'
        return 'warning'
    }

    const getSignalClass = (signal: string): string => {
        if (!signal) return ''
        const signalLower = signal.toLowerCase()
        if (signalLower.includes('买') || signalLower.includes('强')) return 'positive'
        if (signalLower.includes('卖') || signalLower.includes('弱')) return 'negative'
        return 'neutral'
    }

    const runAnalysis = async (): Promise<void> => {
        if (!form.value.symbol) {
            ElMessage.warning('请输入股票代码')
            return
        }

        loading.value = true
        try {
            const params = {
                symbol: form.value.symbol,
                include_raw_data: form.value.includeRawData
            }

            const response = await (advancedAnalysisApi as unknown)[form.value.analysisType](params)

            if (response.data?.success) {
                analysisResult.value = response.data.data
                ElMessage.success('分析完成')

                // 如果启用了实时更新，设置定时器
                if (form.value.enableRealtime) {
                    startRealtimeUpdates()
                }
            } else {
                ElMessage.error(response.data?.message || '分析失败')
            }
        } catch (error: unknown) {
            console.error('分析失败:', error)
            ElMessage.error('分析失败: ' + (error.response?.data?.detail || error.message))
        } finally {
            loading.value = false
        }
    }

    const runBatchAnalysis = async (): Promise<void> => {
        if (!form.value.symbol) {
            ElMessage.warning('请输入股票代码')
            return
        }

        batchLoading.value = true
        try {
            const batchData = {
                analyses: ['fundamental', 'technical', 'trading-signals'],
                symbol: form.value.symbol,
                options: {
                    include_raw_data: form.value.includeRawData
                }
            }

            const response = await advancedAnalysisApi.batch(batchData)

            if (response.data?.success) {
                batchResults.value = response.data.data
                ElMessage.success('批量分析完成')
            } else {
                ElMessage.error(response.data?.message || '批量分析失败')
            }
        } catch (error: unknown) {
            console.error('批量分析失败:', error)
            ElMessage.error('批量分析失败: ' + (error.response?.data?.detail || error.message))
        } finally {
            batchLoading.value = false
        }
    }

    const startRealtimeUpdates = (): void => {
        if (realtimeInterval.value) {
            clearInterval(realtimeInterval.value)
        }

        realtimeInterval.value = setInterval(async () => {
            try {
                await runAnalysis()
            } catch (error) {
                console.error('实时更新失败:', error)
            }
        }, 30000) // 30秒更新一次
    }

    const stopRealtimeUpdates = (): void => {
        if (realtimeInterval.value) {
            clearInterval(realtimeInterval.value)
            realtimeInterval.value = null
        }
    }

    // WebSocket连接管理
    let websocket: WebSocket | null = null

    const connectWebSocket = () => {
        if (websocket) return

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const wsUrl = `${protocol}//${window.location.host}/ws/events?channels=analysis:all,analysis:${form.value.symbol}`

        websocket = new WebSocket(wsUrl)

        websocket.onopen = () => {
            console.log('WebSocket connected for advanced analysis')
        }

        websocket.onmessage = event => {
            try {
                const data = JSON.parse(event.data)
                handleWebSocketMessage(data)
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error)
            }
        }

        websocket.onclose = () => {
            console.log('WebSocket disconnected')
            websocket = null
        }

        websocket.onerror = error => {
            console.error('WebSocket error:', error)
        }
    }

    const disconnectWebSocket = () => {
        if (websocket) {
            websocket.close()
            websocket = null
        }
    }

    const handleWebSocketMessage = (data: unknown) => {
        if (data.type === 'analysis_progress') {
            // 处理分析进度更新
            updateAnalysisProgress(data)
        } else if (data.type === 'analysis_complete') {
            // 处理分析完成事件
            updateAnalysisResult(data)
        }
    }

    const updateAnalysisProgress = (data: unknown) => {
        // 更新UI显示分析进度
        console.log('Analysis progress:', data)

        // 可以在这里更新进度条或状态指示器
        if (data.status === 'completed') {
            // 分析完成，更新结果
            if (data.data) {
                analysisResult.value = {
                    ...analysisResult.value,
                    [data.analysis_type]: data.data
                }
            }
        }
    }

    const updateAnalysisResult = (data: unknown) => {
        // 更新分析结果
        console.log('Analysis complete:', data)

        if (data.result) {
            analysisResult.value = {
                ...analysisResult.value,
                [data.analysis_type]: data.result
            }
        }
    }

    // 生命周期
    onMounted(() => {
        // 检查系统健康状态
        checkSystemHealth()

        // 连接WebSocket用于实时更新
        connectWebSocket()
    })

    onUnmounted(() => {
        stopRealtimeUpdates()
        disconnectWebSocket()
    })

    const checkSystemHealth = async (): Promise<void> => {
        try {
            // 这里可以添加实际的健康检查逻辑
            // 暂时使用模拟状态
            healthStatus.value = {
                database: 'healthy',
                api: 'healthy',
                gpu: 'healthy'
            }
        } catch (error) {
            console.error('健康检查失败:', error)
        }
    }

  return {
    loading,
    batchLoading,
    analysisResult,
    batchResults,
    realtimeInterval,
    form,
    healthStatus,
    overviewMetrics,
    metrics,
    result,
    getAnalysisTitle,
    titles,
    getOverallSignalType,
    signal,
    getSignalClass,
    signalLower,
    runAnalysis,
    params,
    response,
    runBatchAnalysis,
    batchData,
    response,
    startRealtimeUpdates,
    stopRealtimeUpdates,
    websocket,
    connectWebSocket,
    protocol,
    wsUrl,
    data,
    disconnectWebSocket,
    handleWebSocketMessage,
    updateAnalysisProgress,
    updateAnalysisResult,
    checkSystemHealth,
  }
}
