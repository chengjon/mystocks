    import { ref, computed, onMounted, nextTick, watch } from 'vue'
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
    import _ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'
    import ArtDecoSelect from '@/components/artdeco/base/ArtDecoSelect.vue'
    import ArtDecoSwitch from '@/components/artdeco/base/ArtDecoSwitch.vue'
    interface Props {

export function useArtDecoChipDistribution() {

        data: unknown
        symbol: string
        loading?: boolean
    }

    const props = defineProps<Props>()

    // 响应式数据
    const distributionType = ref('cost')
    const timeRange = ref('1M')
    const showCurrentPrice = ref(true)

    const distributionCanvas = ref<HTMLCanvasElement>()

    // 计算属性
    const chipDistribution = computed(() => props.data?.chipDistribution || {})
    const costAnalysis = computed(() => props.data?.costAnalysis || {})
    const profitAnalysis = computed(() => props.data?.profitAnalysis || {})
    const stabilityAnalysis = computed(() => props.data?.stabilityAnalysis || {})

    const currentPrice = computed(() => chipDistribution.value?.currentPrice || 0)

    // 配置选项
    const distributionTypeOptions = [
        { label: '成本分布', value: 'cost' },
        { label: '盈利分布', value: 'profit' },
        { label: '时间分布', value: 'time' },
        { label: '持仓分布', value: 'position' }
    ]

    const timeRangeOptions = [
        { label: '1个月', value: '1M' },
        { label: '3个月', value: '3M' },
        { label: '6个月', value: '6M' },
        { label: '1年', value: '1Y' }
    ]

    // 计算辅助属性
    const costZones = computed(() => costAnalysis.value?.zones || [])
    const profitChipRatio = computed(() => profitAnalysis.value?.profitRatio || 0)
    const avgProfitMultiplier = computed(() => profitAnalysis.value?.avgMultiplier || 0)
    const profitMultiplier = computed(() => profitAnalysis.value?.profitMultiplier || 0)
    const profitDistributionZones = computed(() => profitAnalysis.value?.distributionZones || [])

    const stabilityIndex = computed(() => stabilityAnalysis.value?.stabilityIndex || 0)
    const turnoverStability = computed(() => stabilityAnalysis.value?.turnoverStability || 0)
    const positionConcentration = computed(() => stabilityAnalysis.value?.positionConcentration || 0)
    const chipLockPeriod = computed(() => stabilityAnalysis.value?.chipLockPeriod || 0)
    const stabilityTimeline = computed(() => stabilityAnalysis.value?.timeline || [])
    const maxStability = computed(() => {
        const stabilities = stabilityTimeline.value.map((s: unknown) => s.stability)
        return stabilities.length > 0 ? Math.max(...stabilities) : 1
    })

    const stabilityInsights = computed(() => stabilityAnalysis.value?.insights || [])

    // 格式化函数
    const getConcentrationIndex = (): string => {
        const index = chipDistribution.value?.concentrationIndex || 0
        return index.toFixed(2)
    }

    const getProfitChipRatio = (): string => {
        return `${profitChipRatio.value.toFixed(1)}%`
    }

    const getLossChipRatio = (): string => {
        const lossRatio = 100 - profitChipRatio.value
        return `${lossRatio.toFixed(1)}%`
    }

    const getAverageCost = (): string => {
        const avgCost = costAnalysis.value?.averageCost || 0
        return avgCost.toFixed(2)
    }

    const formatChipVolume = (volume: number): string => {
        if (volume >= 100000000) {
            return `${(volume / 100000000).toFixed(1)}亿`
        }
        if (volume >= 10000) {
            return `${(volume / 10000).toFixed(1)}万`
        }
        return volume.toString()
    }

    const getZoneClass = (zone: unknown): string => {
        if (zone.range.includes('成本')) return 'cost-zone'
        if (zone.range.includes('获利')) return 'profit-zone'
        if (zone.range.includes('套牢')) return 'loss-zone'
        return 'neutral-zone'
    }

    const getZoneBarClass = (zone: unknown): string => {
        if (zone.range.includes('成本')) return 'cost-fill'
        if (zone.range.includes('获利')) return 'profit-fill'
        if (zone.range.includes('套牢')) return 'loss-fill'
        return 'neutral-fill'
    }

    const getSupportLevel = (): string => {
        const support = costAnalysis.value?.supportLevel || 0
        return support.toFixed(2)
    }

    const getResistanceLevel = (): string => {
        const resistance = costAnalysis.value?.resistanceLevel || 0
        return resistance.toFixed(2)
    }

    const getProfitZoneClass = (zone: unknown): string => {
        if (zone.range.includes('亏损')) return 'loss-zone-fill'
        if (zone.range.includes('小盈')) return 'small-profit-fill'
        if (zone.range.includes('中盈')) return 'medium-profit-fill'
        if (zone.range.includes('大盈')) return 'large-profit-fill'
        return 'neutral-zone-fill'
    }

    const getCurrentPricePosition = (): number => {
        const distribution = chipDistribution.value?.priceRange || { min: 0, max: 100 }
        const current = currentPrice.value
        const range = distribution.max - distribution.min
        if (range === 0) return 50
        return ((current - distribution.min) / range) * 100
    }

    const getStabilityClass = (index: number): string => {
        if (index >= 80) return 'positive'
        if (index >= 60) return 'warning'
        return 'negative'
    }

    const getStabilityDesc = (index: number): string => {
        if (index >= 80) return '高度稳定'
        if (index >= 60) return '中等稳定'
        if (index >= 40) return '波动较大'
        return '极不稳定'
    }

    const getTurnoverStabilityClass = (stability: number): string => {
        if (stability >= 80) return 'positive'
        if (stability >= 60) return 'warning'
        return 'negative'
    }

    const getTurnoverStabilityDesc = (stability: number): string => {
        if (stability >= 80) return '换手稳定'
        if (stability >= 60) return '换手适中'
        return '换手频繁'
    }

    const formatDate = (date: string): string => {
        return new Date(date).toLocaleDateString('zh-CN', {
            month: '2-digit',
            day: '2-digit'
        })
    }

    // 图表渲染
    const renderDistributionChart = async () => {
        await nextTick()
        if (!distributionCanvas.value) return

        const ctx = distributionCanvas.value.getContext('2d')
        if (!ctx) return

        // 这里可以集成D3.js或其他图表库来绘制筹码分布图
        // 暂时绘制示例
        const canvas = distributionCanvas.value
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

        // 绘制示例筹码分布曲线
        const distribution = chipDistribution.value?.distribution || []
        if (distribution.length > 0) {
            ctx.strokeStyle = '#D4AF37'
            ctx.lineWidth = 3
            ctx.beginPath()

            distribution.forEach((point: unknown, index: unknown) => {
                const x = (width / (distribution.length - 1)) * index
                const y = height - (point.density / 100) * height * 0.8 - height * 0.1

                if (index === 0) {
                    ctx.moveTo(x, y)
                } else {
                    ctx.lineTo(x, y)
                }
            })

            ctx.stroke()

            // 填充区域
            ctx.fillStyle = 'rgb(212 175 55 / 10%)'
            ctx.beginPath()
            distribution.forEach((point: unknown, index: unknown) => {
                const x = (width / (distribution.length - 1)) * index
                const y = height - (point.density / 100) * height * 0.8 - height * 0.1

                if (index === 0) {
                    ctx.moveTo(x, height)
                    ctx.lineTo(x, y)
                } else {
                    ctx.lineTo(x, y)
                }
            })
            ctx.lineTo(width, height)
            ctx.closePath()
            ctx.fill()
        }
    }

    // 生命周期
    onMounted(() => {
        renderDistributionChart()
    })

    // 监听数据变化重新渲染
    watch(
        () => props.data,
        () => {
            renderDistributionChart()
        },
        { deep: true }
    )

  return {
    props,
    distributionType,
    timeRange,
    showCurrentPrice,
    distributionCanvas,
    chipDistribution,
    costAnalysis,
    profitAnalysis,
    stabilityAnalysis,
    currentPrice,
    distributionTypeOptions,
    timeRangeOptions,
    costZones,
    profitChipRatio,
    avgProfitMultiplier,
    profitMultiplier,
    profitDistributionZones,
    stabilityIndex,
    turnoverStability,
    positionConcentration,
    chipLockPeriod,
    stabilityTimeline,
    maxStability,
    stabilities,
    stabilityInsights,
    getConcentrationIndex,
    index,
    getProfitChipRatio,
    getLossChipRatio,
    lossRatio,
    getAverageCost,
    avgCost,
    formatChipVolume,
    getZoneClass,
    getZoneBarClass,
    getSupportLevel,
    support,
    getResistanceLevel,
    resistance,
    getProfitZoneClass,
    getCurrentPricePosition,
    distribution,
    current,
    range,
    getStabilityClass,
    getStabilityDesc,
    getTurnoverStabilityClass,
    getTurnoverStabilityDesc,
    formatDate,
    renderDistributionChart,
    ctx,
    canvas,
    width,
    height,
    y,
    x,
    distribution,
    x,
    y,
    x,
    y,
  }
}
