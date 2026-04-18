import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { advancedAnalysisApi, type AnalysisRequest, type AnalysisResponse } from '@/api/advancedAnalysis'
import { kronosApi, type KronosPredictResult, type KronosStatusResult } from '@/api/kronos'

type HealthTone = 'healthy' | 'warning' | 'error'

interface AnalysisForm {
    symbol: string
    analysisType: string
    includeRawData: boolean
    enableRealtime: boolean
}

interface KronosPredictForm {
    startDate: string
    endDate: string
    predLen: number
}

interface AnalysisResult {
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

interface HealthStatus {
    database: HealthTone
    api: HealthTone
    gpu: HealthTone
}

interface KronosRuntimeStatus {
    health: string
    activeModel: string
    queueDepth: number | null
    device: string | null
    gpuMemoryUsedMb: number | null
    latencyMs: number | null
    degraded: boolean
    requestId: string | null
}

interface KronosPredictionPreview {
    predictions: Array<{
        timestamp?: string
        open?: number
        high?: number
        low?: number
        close?: number
        volume?: number | null
    }>
    confidence: number | null
    requestId: string | null
}

interface ApiResponse<T = unknown> {
    success?: boolean
    data?: T
    message?: string
}

interface ApiErrorResponse {
    response?: {
        data?: {
            detail?: string
        }
    }
    message?: string
}

interface WebSocketMessage {
    type: string
    status?: string
    data?: unknown
    result?: unknown
    analysis_type?: string
}

interface BatchAnalysisData {
    overall_score?: number
    overall_signal?: string
    score?: number
    [key: string]: unknown
}

interface BatchAnalysisResult {
    success: boolean
    data?: BatchAnalysisData
    error?: string
}

export function useAdvancedAnalysis() {

    const loading = ref(false)
    const batchLoading = ref(false)
    const kronosPredictLoading = ref(false)
    const analysisResult = ref<AnalysisResult | null>(null)
    const batchResults = ref<Record<string, BatchAnalysisResult> | null>(null)
    const kronosPrediction = ref<KronosPredictionPreview | null>(null)
    const realtimeInterval = ref<NodeJS.Timeout | null>(null)

    const form = ref<AnalysisForm>({
        symbol: '',
        analysisType: 'fundamental',
        includeRawData: false,
        enableRealtime: false
    })
    const kronosPredictForm = ref<KronosPredictForm>({
        startDate: '',
        endDate: '',
        predLen: 5
    })

    const healthStatus = ref<HealthStatus>({
        database: 'warning',
        api: 'warning',
        gpu: 'warning'
    })
    const kronosStatus = ref<KronosRuntimeStatus | null>(null)

    const normalizeHealthTone = (value: unknown): HealthTone => {
        const text = String(value || '').toLowerCase()
        if (!text) return 'warning'
        if (text.includes('healthy') || text.includes('ok') || text.includes('normal') || text.includes('ready')) {
            return 'healthy'
        }
        if (text.includes('degraded') || text.includes('warning') || text.includes('busy')) {
            return 'warning'
        }
        return 'error'
    }

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
            const params: AnalysisRequest = {
                symbol: form.value.symbol,
                include_raw_data: form.value.includeRawData
            }

            const analysisApiMap: Record<string, (request: AnalysisRequest) => Promise<AnalysisResponse>> = {
                fundamental: advancedAnalysisApi.fundamental,
                technical: advancedAnalysisApi.technical,
                'trading-signals': advancedAnalysisApi['trading-signals'],
                'time-series': advancedAnalysisApi['time-series'],
                'market-panorama': advancedAnalysisApi['market-panorama'],
                'capital-flow': advancedAnalysisApi['capital-flow'],
                'chip-distribution': advancedAnalysisApi['chip-distribution'],
                'anomaly-tracking': advancedAnalysisApi['anomaly-tracking'],
                'financial-valuation': advancedAnalysisApi['financial-valuation'],
                sentiment: advancedAnalysisApi.sentiment,
                'decision-models': advancedAnalysisApi['decision-models'],
                'multidimensional-radar': advancedAnalysisApi['multidimensional-radar']
            }

            const requestHandler = analysisApiMap[form.value.analysisType]
            if (!requestHandler) {
                ElMessage.error('不支持的分析类型')
                return
            }

            const response = await requestHandler(params)
            const payload = (response as { data?: AnalysisResponse }).data ?? response

            if (payload.success) {
                analysisResult.value = (payload.data as AnalysisResult) ?? null
                ElMessage.success('分析完成')

                // 如果启用了实时更新，设置定时器
                if (form.value.enableRealtime) {
                    startRealtimeUpdates()
                }
            } else {
                ElMessage.error(payload.message || '分析失败')
            }
        } catch (error: unknown) {
            console.error('分析失败:', error)
            const apiError = error as ApiErrorResponse
            ElMessage.error('分析失败: ' + (apiError.response?.data?.detail || apiError.message))
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

            const response = await advancedAnalysisApi.batch(batchData) as ApiResponse

            if (response.success) {
                batchResults.value = response.data as Record<string, BatchAnalysisResult> | null
                ElMessage.success('批量分析完成')
            } else {
                ElMessage.error(response.message || '批量分析失败')
            }
        } catch (error: unknown) {
            console.error('批量分析失败:', error)
            const apiError = error as ApiErrorResponse
            ElMessage.error('批量分析失败: ' + (apiError.response?.data?.detail || apiError.message))
        } finally {
            batchLoading.value = false
        }
    }

    const runKronosPrediction = async (): Promise<void> => {
        if (!form.value.symbol) {
            ElMessage.warning('请输入股票代码')
            return
        }
        if (!kronosPredictForm.value.startDate || !kronosPredictForm.value.endDate) {
            ElMessage.warning('请选择预测使用的开始和结束日期')
            return
        }
        if (kronosPredictForm.value.startDate > kronosPredictForm.value.endDate) {
            ElMessage.warning('开始日期不能晚于结束日期')
            return
        }

        kronosPredictLoading.value = true
        try {
            const response = await kronosApi.predict({
                model: 'small',
                symbol: form.value.symbol,
                period: 'day',
                start_date: kronosPredictForm.value.startDate,
                end_date: kronosPredictForm.value.endDate,
                pred_len: kronosPredictForm.value.predLen,
                sample_count: 1,
                top_p: 0.9,
                temperature: 1.0,
            })

            if (response.success) {
                const data = (response.data || {}) as KronosPredictResult
                kronosPrediction.value = {
                    predictions: data.predictions || [],
                    confidence: typeof data.confidence === 'number' ? data.confidence : null,
                    requestId: response.request_id || null,
                }
                ElMessage.success('Kronos 预测完成')
                await checkSystemHealth()
            } else {
                ElMessage.error(response.message || 'Kronos 预测失败')
            }
        } catch (error: unknown) {
            console.error('Kronos 预测失败:', error)
            const apiError = error as ApiErrorResponse
            ElMessage.error('Kronos 预测失败: ' + (apiError.response?.data?.detail || apiError.message))
        } finally {
            kronosPredictLoading.value = false
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
        const msg = data as WebSocketMessage
        if (msg.type === 'analysis_progress') {
            // 处理分析进度更新
            updateAnalysisProgress(msg)
        } else if (msg.type === 'analysis_complete') {
            // 处理分析完成事件
            updateAnalysisResult(msg)
        }
    }

    const updateAnalysisProgress = (data: WebSocketMessage) => {
        // 更新UI显示分析进度
        console.log('Analysis progress:', data)

        // 可以在这里更新进度条或状态指示器
        if (data.status === 'completed') {
            // 分析完成，更新结果
            if (data.data) {
                analysisResult.value = {
                    ...analysisResult.value,
                    [data.analysis_type ?? 'unknown']: data.data
                }
            }
        }
    }

    const updateAnalysisResult = (data: WebSocketMessage) => {
        // 更新分析结果
        console.log('Analysis complete:', data)

        if (data.result) {
            analysisResult.value = {
                ...analysisResult.value,
                [data.analysis_type ?? 'unknown']: data.result
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
        let nextDatabase: HealthTone = 'warning'
        let nextApi: HealthTone = 'warning'
        let nextGpu: HealthTone = 'warning'

        try {
            const [analysisHealthResult, kronosHealthResult] = await Promise.allSettled([
                advancedAnalysisApi.health(),
                kronosApi.getStatus(),
            ])

            if (analysisHealthResult.status === 'fulfilled') {
                const payload = analysisHealthResult.value
                if (payload.success) {
                    const healthData = (payload.data || {}) as Record<string, unknown>
                    nextDatabase = normalizeHealthTone(healthData.database ?? healthData.status ?? 'healthy')
                }
            }

            if (kronosHealthResult.status === 'fulfilled') {
                const payload = kronosHealthResult.value
                if (payload.success) {
                    const data = (payload.data || {}) as KronosStatusResult
                    const meta = data.meta || {}
                    const degraded = Boolean(meta.degraded)
                    nextApi = normalizeHealthTone(data.health ?? 'healthy')
                    nextGpu = degraded ? 'warning' : (data.device || meta.device ? 'healthy' : nextApi)
                    kronosStatus.value = {
                        health: data.health || 'unknown',
                        activeModel: data.active_model || 'N/A',
                        queueDepth: typeof data.queue_depth === 'number' ? data.queue_depth : null,
                        device: data.device || meta.device || null,
                        gpuMemoryUsedMb: typeof data.gpu_memory_used_mb === 'number' ? data.gpu_memory_used_mb : null,
                        latencyMs: typeof data.inference_latency_ms_avg === 'number'
                            ? data.inference_latency_ms_avg
                            : (typeof meta.latency_ms === 'number' ? meta.latency_ms : null),
                        degraded,
                        requestId: payload.request_id || null,
                    }
                } else {
                    nextApi = 'error'
                    nextGpu = 'warning'
                    kronosStatus.value = null
                }
            } else {
                nextApi = 'error'
                nextGpu = 'warning'
                kronosStatus.value = null
            }

            healthStatus.value = {
                database: nextDatabase,
                api: nextApi,
                gpu: nextGpu
            }
        } catch (error) {
            console.error('健康检查失败:', error)
            healthStatus.value = {
                database: nextDatabase,
                api: 'error',
                gpu: 'warning'
            }
            kronosStatus.value = null
        }
    }

  return {
    loading,
    batchLoading,
    kronosPredictLoading,
    analysisResult,
    batchResults,
    kronosPrediction,
    realtimeInterval,
    form,
    kronosPredictForm,
    healthStatus,
    kronosStatus,
    overviewMetrics,
    getAnalysisTitle,
    getOverallSignalType,
    getSignalClass,
    runAnalysis,
    runBatchAnalysis,
    runKronosPrediction,
    startRealtimeUpdates,
    stopRealtimeUpdates,
    connectWebSocket,
    disconnectWebSocket,
    handleWebSocketMessage,
    updateAnalysisProgress,
    updateAnalysisResult,
    checkSystemHealth,
  }
}
