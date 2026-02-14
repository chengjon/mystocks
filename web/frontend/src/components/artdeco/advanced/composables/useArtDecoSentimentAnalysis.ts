    import { ref, computed, onMounted, nextTick, watch } from 'vue'
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
    import _ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'
    import ArtDecoSelect from '@/components/artdeco/base/ArtDecoSelect.vue'
    import ArtDecoSwitch from '@/components/artdeco/base/ArtDecoSwitch.vue'
    interface Props {

export function useArtDecoSentimentAnalysis() {

        data: unknown
        symbol: string
        loading?: boolean
    }

    const props = defineProps<Props>()

    // 响应式数据
    const radarTimeframe = ref('1d')
    const showHistorical = ref(false)

    const radarCanvas = ref<HTMLCanvasElement>()

    // 计算属性
    const sentimentData = computed(() => props.data?.sentiment || {})
    const researchData = computed(() => props.data?.research || {})
    const newsData = computed(() => props.data?.news || {})
    const popularityData = computed(() => props.data?.popularity || {})

    // 情绪分析相关
    const overallSentimentIndex = computed(() => sentimentData.value?.overallIndex || 0)
    const bullishPercentage = computed(() => sentimentData.value?.bullish || 0)
    const bearishPercentage = computed(() => sentimentData.value?.bearish || 0)
    const neutralPercentage = computed(() => sentimentData.value?.neutral || 0)

    // 研报分析相关
    const totalReports = computed(() => researchData.value?.total || 0)
    const avgRating = computed(() => researchData.value?.avgRating || 0)
    const avgTargetPrice = computed(() => researchData.value?.avgTargetPrice || 0)
    const avgUpside = computed(() => researchData.value?.avgUpside || 0)
    const recentReports = computed(() => researchData.value?.recent || [])

    // 新闻分析相关
    const sentimentSegments = computed(() => newsData.value?.segments || [])
    const totalNews = computed(() => newsData.value?.total || 0)
    const recentNews = computed(() => newsData.value?.recent || [])

    // 人气指标相关
    const searchHeatIndex = computed(() => popularityData.value?.searchHeat || 0)
    const forumDiscussion = computed(() => popularityData.value?.forum || 0)
    const socialMedia = computed(() => popularityData.value?.social || 0)
    const newsCoverage = computed(() => popularityData.value?.news || 0)
    const consensusLevel = computed(() => popularityData.value?.consensus || 0)
    const sentimentVolatility = computed(() => popularityData.value?.volatility || 0)

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
        const trend = popularityData.value?.attentionTrend || '稳定'
        return trend
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
    colors,
    getSentimentTypeText,
    texts,
    getSentimentClass,
    getHeatClass,
    getAttentionTrend,
    trend,
    renderRadarChart,
    ctx,
    canvas,
    width,
    height,
    centerX,
    centerY,
    radius,
    axes,
    angle,
    x,
    y,
    sentimentValues,
    angle,
    x,
    y,
  }
}
