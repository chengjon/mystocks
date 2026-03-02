import { ref, computed, onMounted, nextTick, watch } from 'vue'

interface SentimentDataType {
    overallIndex?: number
    bullish?: number
    bearish?: number
    neutral?: number
}

interface ResearchReport {
    id?: string | number
    broker?: string
    title?: string
    rating?: number
    targetPrice?: number
    upside?: number
    date?: string
}

interface NormalizedResearchReport {
    id: string | number
    broker: string
    title: string
    rating: number
    targetPrice: number
    upside: number
    date: string
}

interface ResearchDataType {
    total?: number
    avgRating?: number
    avgTargetPrice?: number
    avgUpside?: number
    recent?: ResearchReport[]
}

interface NewsSegment {
    type?: string
    startAngle?: number
    endAngle?: number
    percentage?: number
    count?: number
}

interface NormalizedNewsSegment {
    type: string
    startAngle: number
    endAngle: number
    percentage: number
    count: number
}

interface RecentNewsItem {
    id: string | number
    sentiment: string
    title: string
    source: string
    time: string
}

interface NewsDataType {
    segments?: NewsSegment[]
    total?: number
    recent?: Record<string, unknown>[]
    [key: string]: unknown
}

interface PopularityDataType {
    searchHeat?: number
    forum?: number
    social?: number
    news?: number
    consensus?: number
    volatility?: number
    attentionTrend?: string
    [key: string]: unknown
}

interface PropsData {
    sentiment?: SentimentDataType
    research?: ResearchDataType
    news?: NewsDataType
    popularity?: PopularityDataType
}

interface Props {
    data: PropsData | null
    symbol: string
    loading?: boolean
}

export function useArtDecoSentimentAnalysis() {
    const props = defineProps<Props>()

    // 响应式数据
    const radarTimeframe = ref('1d')
    const showHistorical = ref(false)

    const radarCanvas = ref<HTMLCanvasElement>()

    // 计算属性
    const sentimentData = computed<SentimentDataType>(() => props.data?.sentiment ?? {})
    const researchData = computed<ResearchDataType>(() => props.data?.research ?? {})
    const newsData = computed<NewsDataType>(() => props.data?.news ?? {})
    const popularityData = computed<PopularityDataType>(() => props.data?.popularity ?? {})

    // 情绪分析相关
    const overallSentimentIndex = computed<number>(() => Number(sentimentData.value.overallIndex ?? 0))
    const bullishPercentage = computed<number>(() => Number(sentimentData.value.bullish ?? 0))
    const bearishPercentage = computed<number>(() => Number(sentimentData.value.bearish ?? 0))
    const neutralPercentage = computed<number>(() => Number(sentimentData.value.neutral ?? 0))

    // 研报分析相关
    const totalReports = computed<number>(() => Number(researchData.value.total ?? 0))
    const avgRating = computed<number>(() => Number(researchData.value.avgRating ?? 0))
    const avgTargetPrice = computed<number>(() => Number(researchData.value.avgTargetPrice ?? 0))
    const avgUpside = computed<number>(() => Number(researchData.value.avgUpside ?? 0))
    const recentReports = computed<NormalizedResearchReport[]>(() => {
        const reports = researchData.value.recent ?? []

        return reports.map((report, index) => ({
            id: report.id ?? index,
            broker: report.broker ?? '--',
            title: report.title ?? '--',
            rating: Number(report.rating ?? 0),
            targetPrice: Number(report.targetPrice ?? 0),
            upside: Number(report.upside ?? 0),
            date: report.date ?? ''
        }))
    })

    // 新闻分析相关
    const sentimentSegments = computed<NormalizedNewsSegment[]>(() => {
        const segments = newsData.value.segments ?? []

        return segments.map((segment) => ({
            type: segment.type ?? 'neutral',
            startAngle: Number(segment.startAngle ?? 0),
            endAngle: Number(segment.endAngle ?? 0),
            percentage: Number(segment.percentage ?? 0),
            count: Number(segment.count ?? 0)
        }))
    })

    const totalNews = computed<number>(() => Number(newsData.value.total ?? 0))
    const recentNews = computed<RecentNewsItem[]>(() => {
        const newsList = newsData.value.recent ?? []

        return newsList.map((item, index) => {
            const news = item as Record<string, unknown>

            return {
                id:
                    typeof news.id === 'string' || typeof news.id === 'number'
                        ? news.id
                        : index,
                sentiment: typeof news.sentiment === 'string' ? news.sentiment : 'neutral',
                title: typeof news.title === 'string' ? news.title : '--',
                source: typeof news.source === 'string' ? news.source : '--',
                time: typeof news.time === 'string' ? news.time : ''
            }
        })
    })

    // 人气指标相关
    const searchHeatIndex = computed<number>(() => Number(popularityData.value.searchHeat ?? 0))
    const forumDiscussion = computed<number>(() => Number(popularityData.value.forum ?? 0))
    const socialMedia = computed<number>(() => Number(popularityData.value.social ?? 0))
    const newsCoverage = computed<number>(() => Number(popularityData.value.news ?? 0))
    const consensusLevel = computed<number>(() => Number(popularityData.value.consensus ?? 0))
    const sentimentVolatility = computed<number>(() => Number(popularityData.value.volatility ?? 0))

    // 配置选项
    const timeframeOptions = [
        { label: '今日', value: '1d' },
        { label: '3日', value: '3d' },
        { label: '1周', value: '1w' },
        { label: '1月', value: '1M' }
    ]

    // 格式化函数
    const getOverallSentimentIndex = (): string => {
        return overallSentimentIndex.value.toFixed(1)
    }

    const getBullishPercentage = (): string => {
        return `${bullishPercentage.value.toFixed(1)}%`
    }

    const getBearishPercentage = (): string => {
        return `${bearishPercentage.value.toFixed(1)}%`
    }

    const getNeutralPercentage = (): string => {
        return `${neutralPercentage.value.toFixed(1)}%`
    }

    const getRatingClass = (rating: number): string => {
        if (rating >= 4) return 'buy'
        if (rating >= 3) return 'hold'
        return 'sell'
    }

    const getRatingText = (rating: number): string => {
        if (rating >= 4.5) return '强烈推荐'
        if (rating >= 4) return '推荐'
        if (rating >= 3.5) return '谨慎推荐'
        if (rating >= 3) return '中性'
        if (rating >= 2.5) return '谨慎减持'
        if (rating >= 2) return '减持'
        return '卖出'
    }

    const getUpsideClass = (upside: number): string => {
        if (upside >= 20) return 'strong-positive'
        if (upside >= 10) return 'positive'
        if (upside >= 0) return 'neutral'
        return 'negative'
    }

    const formatPrice = (price: number): string => {
        return price.toFixed(2)
    }

    const formatDate = (date: string): string => {
        return new Date(date).toLocaleDateString('zh-CN', {
            month: '2-digit',
            day: '2-digit'
        })
    }

    const formatTime = (timestamp: string): string => {
        return new Date(timestamp).toLocaleString('zh-CN', {
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    const getSentimentColor = (type: string): string => {
        const colors: Record<string, string> = {
            positive: '#22c55e',
            negative: '#ef4444',
            neutral: '#6b7280'
        }
        return colors[type] || '#6b7280'
    }

    const getSentimentTypeText = (type: string): string => {
        const texts: Record<string, string> = {
            positive: '积极',
            negative: '消极',
            neutral: '中性'
        }
        return texts[type] || type
    }

    const getSentimentClass = (sentiment: string): string => {
        return sentiment
    }

    const getHeatClass = (heat: number): string => {
        if (heat >= 80) return 'high'
        if (heat >= 60) return 'medium'
        return 'low'
    }

    const getAttentionTrend = (): string => {
        const trend = popularityData.value?.attentionTrend
        return typeof trend === 'string' ? trend : '稳定'
    }

    // 雷达图渲染
    const renderRadarChart = async () => {
        await nextTick()
        if (!radarCanvas.value) return

        const ctx = radarCanvas.value.getContext('2d')
        if (!ctx) return

        // 这里可以集成Chart.js或其他雷达图库
        // 暂时绘制示例雷达图
        const canvas = radarCanvas.value
        const width = (canvas.width = canvas.offsetWidth)
        const height = (canvas.height = canvas.offsetHeight)

        ctx.clearRect(0, 0, width, height)

        const centerX = width / 2
        const centerY = height / 2
        const radius = (Math.min(width, height) / 2) * 0.8

        // 绘制背景圆圈
        ctx.strokeStyle = 'rgb(212 175 55 / 10%)'
        ctx.lineWidth = 1

        for (let i = 1; i <= 5; i++) {
            ctx.beginPath()
            ctx.arc(centerX, centerY, (radius * i) / 5, 0, 2 * Math.PI)
            ctx.stroke()
        }

        // 绘制轴线
        const axes = 6
        for (let i = 0; i < axes; i++) {
            const angle = (i * 2 * Math.PI) / axes - Math.PI / 2
            const x = centerX + Math.cos(angle) * radius
            const y = centerY + Math.sin(angle) * radius

            ctx.beginPath()
            ctx.moveTo(centerX, centerY)
            ctx.lineTo(x, y)
            ctx.stroke()
        }

        // 绘制情绪雷达图
        const sentimentValues = [
            bullishPercentage.value / 100,
            neutralPercentage.value / 100,
            bearishPercentage.value / 100,
            0.5, // 示例值
            0.3, // 示例值
            0.7 // 示例值
        ]

        ctx.strokeStyle = '#D4AF37'
        ctx.lineWidth = 2
        ctx.fillStyle = 'rgb(212 175 55 / 10%)'
        ctx.beginPath()

        sentimentValues.forEach((value, index) => {
            const angle = (index * 2 * Math.PI) / axes - Math.PI / 2
            const x = centerX + Math.cos(angle) * radius * value
            const y = centerY + Math.sin(angle) * radius * value

            if (index === 0) {
                ctx.moveTo(x, y)
            } else {
                ctx.lineTo(x, y)
            }
        })

        ctx.closePath()
        ctx.fill()
        ctx.stroke()
    }

    // 生命周期
    onMounted(() => {
        renderRadarChart()
    })

    // 监听数据变化重新渲染
    watch(
        () => props.data,
        () => {
            renderRadarChart()
        },
        { deep: true }
    )

  return {
    props,
    radarTimeframe,
    showHistorical,
    radarCanvas,
    sentimentData,
    researchData,
    newsData,
    popularityData,
    overallSentimentIndex,
    bullishPercentage,
    bearishPercentage,
    neutralPercentage,
    totalReports,
    avgRating,
    avgTargetPrice,
    avgUpside,
    recentReports,
    sentimentSegments,
    totalNews,
    recentNews,
    searchHeatIndex,
    forumDiscussion,
    socialMedia,
    newsCoverage,
    consensusLevel,
    sentimentVolatility,
    timeframeOptions,
    getOverallSentimentIndex,
    getBullishPercentage,
    getBearishPercentage,
    getNeutralPercentage,
    getRatingClass,
    getRatingText,
    getUpsideClass,
    formatPrice,
    formatDate,
    formatTime,
    getSentimentColor,
    getSentimentTypeText,
    getSentimentClass,
    getHeatClass,
    getAttentionTrend,
    renderRadarChart,
  }
}
