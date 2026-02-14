    import { ref, computed, onMounted, nextTick, watch } from 'vue'
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
    import _ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'
    import ArtDecoSelect from '@/components/artdeco/base/ArtDecoSelect.vue'
    import ArtDecoSwitch from '@/components/artdeco/base/ArtDecoSwitch.vue'
    interface Props {

export function useArtDecoTimeSeriesAnalysis() {

        data: unknown
        symbol: string
        loading?: boolean
    }

    const props = defineProps<Props>()

    // 响应式数据
    const chartType = ref('line')
    const analysisType = ref('trend')
    const showInflectionPoints = ref(true)
    const showTrend = ref(true)
    const predictionMethod = ref('arima')
    const predictionHorizon = ref('30d')

    const chartCanvas = ref<HTMLCanvasElement>()

    // 计算属性
    const timeSeriesData = computed(() => props.data?.timeSeries || [])
    const inflectionPoints = computed(() => props.data?.inflectionPoints || [])
    const periodicityData = computed(() => props.data?.periodicity || {})
    const predictionData = computed(() => props.data?.prediction || {})

    // 配置选项
    const chartTypeOptions = [
        { label: '线图', value: 'line' },
        { label: '面积图', value: 'area' },
        { label: '柱状图', value: 'bar' },
        { label: '散点图', value: 'scatter' }
    ]

    const analysisTypeOptions = [
        { label: '趋势分析', value: 'trend' },
        { label: '拐点检测', value: 'inflection' },
        { label: '周期分析', value: 'periodicity' },
        { label: '预测分析', value: 'prediction' }
    ]

    const predictionMethodOptions = [
        { label: 'ARIMA', value: 'arima' },
        { label: '指数平滑', value: 'exponential' },
        { label: '线性回归', value: 'linear' },
        { label: '神经网络', value: 'neural' }
    ]

    const predictionHorizonOptions = [
        { label: '7天', value: '7d' },
        { label: '30天', value: '30d' },
        { label: '90天', value: '90d' },
        { label: '180天', value: '180d' }
    ]

    // 计算辅助函数
    const getDataPointsCount = (): string => {
        return timeSeriesData.value.length.toString()
    }

    const getInflectionPointsCount = (): string => {
        return inflectionPoints.value.length.toString()
    }

    const getTrendStrength = (): string => {
        const trend = props.data?.trend
        if (!trend) return 'N/A'

        const strength = trend.strength || 0
        if (strength >= 80) return '极强'
        if (strength >= 60) return '强'
        if (strength >= 40) return '中等'
        if (strength >= 20) return '弱'
        return '极弱'
    }

    const getPeriodicityConfidence = (): string => {
        const periodicity = periodicityData.value
        if (!periodicity?.confidence) return 'N/A'

        return `${periodicity.confidence.toFixed(1)}%`
    }

    const getMaxChangeAmplitude = (): string => {
        if (!inflectionPoints.value.length) return 'N/A'

        const maxAmplitude = Math.max(...inflectionPoints.value.map((p: unknown) => Math.abs(p.changeAmplitude || 0)))
        return `${maxAmplitude.toFixed(2)}%`
    }

    const getAvgChangePeriod = (): string => {
        if (!inflectionPoints.value.length) return 'N/A'

        const timestamps = inflectionPoints.value.map((p: unknown) => new Date(p.timestamp).getTime())
        const intervals = []

        for (let i = 1; i < timestamps.length; i++) {
            intervals.push(timestamps[i] - timestamps[i - 1])
        }

        if (!intervals.length) return 'N/A'

        const avgInterval = intervals.reduce((sum: unknown, interval: unknown) => sum + interval, 0) / intervals.length
        const days = Math.round(avgInterval / (1000 * 60 * 60 * 24))

        return `${days}天`
    }

    const getInflectionType = (point: unknown): string => {
        if (point.type === 'peak') return 'peak'
        if (point.type === 'valley') return 'valley'
        return 'neutral'
    }

    const getPointTypeText = (type: string): string => {
        if (type === 'peak') return '波峰'
        if (type === 'valley') return '波谷'
        return '转折点'
    }

    const formatTime = (timestamp: string): string => {
        return new Date(timestamp).toLocaleString('zh-CN', {
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    const dominantPeriods = computed(() => {
        const periods = periodicityData.value?.dominantPeriods || []
        return periods.slice(0, 5).map((period: unknown) => ({
            frequency: period.frequency,
            strength: period.strength * 100
        }))
    })

    const getPeriodLabel = (frequency: string): string => {
        const labels: Record<string, string> = {
            daily: '日',
            weekly: '周',
            monthly: '月',
            quarterly: '季',
            yearly: '年'
        }
        return labels[frequency] || frequency
    }

    const spectrumData = computed(() => {
        // 生成频谱数据示例
        return [
            { frequency: 'daily', power: 30 },
            { frequency: 'weekly', power: 70 },
            { frequency: 'monthly', power: 45 },
            { frequency: 'quarterly', power: 25 },
            { frequency: 'yearly', power: 15 }
        ]
    })

    const getSpectrumColor = (frequency: string): string => {
        const colors: Record<string, string> = {
            daily: '#D4AF37',
            weekly: '#F59E0B',
            monthly: '#10B981',
            quarterly: '#3B82F6',
            yearly: '#8B5CF6'
        }
        return colors[frequency] || '#6B7280'
    }

    const getPredictionAccuracy = (): string => {
        const accuracy = predictionData.value?.accuracy
        return accuracy ? `${(accuracy * 100).toFixed(1)}%` : 'N/A'
    }

    const getPredictionInterval = (): string => {
        const interval = predictionData.value?.confidenceInterval
        return interval ? `±${interval.toFixed(2)}` : 'N/A'
    }

    const getModelConfidence = (): string => {
        const confidence = predictionData.value?.modelConfidence
        return confidence ? `${(confidence * 100).toFixed(1)}%` : 'N/A'
    }

    const predictionInsights = computed(() => {
        return (
            predictionData.value?.insights || [
                {
                    id: 1,
                    type: 'bullish',
                    text: '短期内可能出现上涨趋势',
                    confidence: 75
                },
                {
                    id: 2,
                    type: 'neutral',
                    text: '中期走势相对稳定',
                    confidence: 60
                },
                {
                    id: 3,
                    type: 'bearish',
                    text: '长期存在调整风险',
                    confidence: 45
                }
            ]
        )
    })

    // 图表渲染
    const renderChart = async () => {
        await nextTick()
        if (!chartCanvas.value) return

        const ctx = chartCanvas.value.getContext('2d')
        if (!ctx) return

        // 这里可以集成Chart.js或其他图表库
        // 暂时绘制简单的示例图表
        const canvas = chartCanvas.value
        const width = (canvas.width = canvas.offsetWidth)
        const height = (canvas.height = canvas.offsetHeight)

        ctx.clearRect(0, 0, width, height)

        // 绘制网格
        ctx.strokeStyle = 'rgb(212 175 55 / 10%)'
        ctx.lineWidth = 1

        // 水平网格线
        for (let i = 0; i <= 5; i++) {
            const y = (height / 5) * i
            ctx.beginPath()
            ctx.moveTo(0, y)
            ctx.lineTo(width, y)
            ctx.stroke()
        }

        // 垂直网格线
        for (let i = 0; i <= 10; i++) {
            const x = (width / 10) * i
            ctx.beginPath()
            ctx.moveTo(x, 0)
            ctx.lineTo(x, height)
            ctx.stroke()
        }

        // 绘制示例数据线
        if (timeSeriesData.value.length > 0) {
            ctx.strokeStyle = '#D4AF37'
            ctx.lineWidth = 2
            ctx.beginPath()

            const data = timeSeriesData.value
            const maxValue = Math.max(...data.map((d: unknown) => d.value))
            const minValue = Math.min(...data.map((d: unknown) => d.value))
            const valueRange = maxValue - minValue

            data.forEach((point: unknown, index: unknown) => {
                const x = (width / (data.length - 1)) * index
                const y = height - ((point.value - minValue) / valueRange) * height * 0.8 - height * 0.1

                if (index === 0) {
                    ctx.moveTo(x, y)
                } else {
                    ctx.lineTo(x, y)
                }
            })

            ctx.stroke()
        }
    }

    // 生命周期
    onMounted(() => {
        renderChart()
    })

    // 监听数据变化重新渲染
    watch(
        () => props.data,
        () => {
            renderChart()
        },
        { deep: true }
    )

  return {
    props,
    chartType,
    analysisType,
    showInflectionPoints,
    showTrend,
    predictionMethod,
    predictionHorizon,
    chartCanvas,
    timeSeriesData,
    inflectionPoints,
    periodicityData,
    predictionData,
    chartTypeOptions,
    analysisTypeOptions,
    predictionMethodOptions,
    predictionHorizonOptions,
    getDataPointsCount,
    getInflectionPointsCount,
    getTrendStrength,
    trend,
    strength,
    getPeriodicityConfidence,
    periodicity,
    getMaxChangeAmplitude,
    maxAmplitude,
    getAvgChangePeriod,
    timestamps,
    intervals,
    avgInterval,
    days,
    getInflectionType,
    getPointTypeText,
    formatTime,
    dominantPeriods,
    periods,
    getPeriodLabel,
    labels,
    spectrumData,
    getSpectrumColor,
    colors,
    getPredictionAccuracy,
    accuracy,
    getPredictionInterval,
    interval,
    getModelConfidence,
    confidence,
    predictionInsights,
    renderChart,
    ctx,
    canvas,
    width,
    height,
    y,
    x,
    data,
    maxValue,
    minValue,
    valueRange,
    x,
    y,
  }
}
