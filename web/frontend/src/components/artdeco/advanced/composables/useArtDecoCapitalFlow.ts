    import { ref, computed } from 'vue'
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
    import ArtDecoSelect from '@/components/artdeco/base/ArtDecoSelect.vue'
    import ArtDecoSwitch from '@/components/artdeco/base/ArtDecoSwitch.vue'
    interface Props {

export function useArtDecoCapitalFlow() {

        data: unknown
        symbol?: string
        loading?: boolean
    }

    const props = defineProps<Props>()

    // 响应式数据
    const heatmapPeriod = ref('1d')
    const flowType = ref('net')
    const showLabels = ref(true)

    // 计算属性
    const capitalFlows = computed(() => props.data?.capitalFlows || {})
    const clusteringData = computed(() => props.data?.clustering || {})
    const mainForceData = computed(() => props.data?.mainForce || {})
    const opportunityData = computed(() => props.data?.opportunity || {})

    // 资金流向相关计算属性
    const northboundFlow = computed(() => capitalFlows.value?.northbound || 0)
    const southboundFlow = computed(() => capitalFlows.value?.southbound || 0)
    const mainForceFlow = computed(() => capitalFlows.value?.mainForce || 0)
    const retailFlow = computed(() => capitalFlows.value?.retail || 0)

    const sectorFlows = computed(() => capitalFlows.value?.sectorFlows || [])
    const minFlow = computed(() => {
        const flows = sectorFlows.value.map((s: unknown) => s.flow)
        return flows.length > 0 ? Math.min(...flows) : 0
    })
    const maxFlow = computed(() => {
        const flows = sectorFlows.value.map((s: unknown) => s.flow)
        return flows.length > 0 ? Math.max(...flows) : 0
    })

    // 聚类分析相关计算属性
    const clusters = computed(() => clusteringData.value?.clusters || [])
    const clusteredStocks = computed(() => clusteringData.value?.stocks || [])

    // 主力控盘相关计算属性
    const mainForceControl = computed(() => mainForceData.value?.controlLevel || 0)
    const top5Concentration = computed(() => mainForceData.value?.top5Concentration || 0)
    const top10Concentration = computed(() => mainForceData.value?.top10Concentration || 0)
    const mainForceRanking = computed(() => mainForceData.value?.ranking || [])

    // 风口诊断相关计算属性
    const marketSentiment = computed(() => opportunityData.value?.marketSentiment || '中性')
    const fundAttention = computed(() => opportunityData.value?.fundAttention || '一般')
    const sectorRotation = computed(() => opportunityData.value?.sectorRotation || '稳定')
    const opportunityWindow = computed(() => opportunityData.value?.opportunityWindow || '关闭')

    const hotSectors = computed(() => opportunityData.value?.hotSectors || [])
    const investmentInsights = computed(() => opportunityData.value?.insights || [])

    // 配置选项
    const periodOptions = [
        { label: '今日', value: '1d' },
        { label: '3日', value: '3d' },
        { label: '5日', value: '5d' },
        { label: '10日', value: '10d' }
    ]

    const flowTypeOptions = [
        { label: '净流入', value: 'net' },
        { label: '流入量', value: 'inflow' },
        { label: '流出量', value: 'outflow' }
    ]

    // 格式化函数
    const getNorthboundFlow = (): string => {
        return formatFlow(northboundFlow.value)
    }

    const getSouthboundFlow = (): string => {
        return formatFlow(southboundFlow.value)
    }

    const getMainForceFlow = (): string => {
        return formatFlow(mainForceFlow.value)
    }

    const getRetailFlow = (): string => {
        return formatFlow(retailFlow.value)
    }

    const formatFlow = (flow: number): string => {
        const sign = flow > 0 ? '+' : ''
        const absFlow = Math.abs(flow)
        if (absFlow >= 100000000) {
            return `${sign}${(absFlow / 100000000).toFixed(2)}亿`
        }
        if (absFlow >= 10000) {
            return `${sign}${(absFlow / 10000).toFixed(1)}万`
        }
        return `${sign}${absFlow.toFixed(0)}`
    }

    const formatVolume = (volume: number): string => {
        if (volume >= 100000000) {
            return `${(volume / 100000000).toFixed(1)}亿`
        }
        if (volume >= 10000) {
            return `${(volume / 10000).toFixed(1)}万`
        }
        return volume.toString()
    }

    const getHeatmapColor = (flow: number): string => {
        if (flow > 0) {
            // 绿色渐变表示资金流入
            const intensity = Math.min(Math.abs(flow) / Math.max(Math.abs(maxFlow.value), 1), 1)
            const green = Math.floor(197 * intensity + 34 * (1 - intensity))
            const alpha = 0.3 + 0.7 * intensity
            return `rgba(${34}, ${green}, ${94}, ${alpha})`
        } else if (flow < 0) {
            // 红色渐变表示资金流出
            const intensity = Math.min(Math.abs(flow) / Math.max(Math.abs(minFlow.value), 1), 1)
            const red = Math.floor(239 * intensity + 68 * (1 - intensity))
            const alpha = 0.3 + 0.7 * intensity
            return `rgba(${red}, ${68}, ${68}, ${alpha})`
        }
        return 'rgb(156 163 175 / 30%)'
    }

    const getHeatmapOpacity = (flow: number): number => {
        const maxAbsFlow = Math.max(Math.abs(minFlow.value), Math.abs(maxFlow.value))
        if (maxAbsFlow === 0) return 0.3
        return 0.3 + 0.7 * (Math.abs(flow) / maxAbsFlow)
    }

    const getSectorCode = (name: string): string => {
        const codes: Record<string, string> = {
            科技: 'T',
            医药: 'Y',
            金融: 'J',
            地产: 'D',
            能源: 'N',
            消费: 'X',
            制造: 'Z',
            其他: 'Q'
        }
        return codes[name] || name.charAt(0)
    }

    // 聚类分析辅助函数
    const getMaxClusterSize = (): number => {
        if (!clusters.value.length) return 0
        return Math.max(...clusters.value.map((c: unknown) => c.stocks?.length || 0))
    }

    const getClusteringDensity = (): number => {
        if (!clusters.value.length || !clusteredStocks.value.length) return 0
        const avgClusterSize = clusteredStocks.value.length / clusters.value.length
        const maxClusterSize = getMaxClusterSize()
        return avgClusterSize / maxClusterSize
    }

    const getDispersionIndex = (): number => {
        if (!clusteredStocks.value.length) return 0
        const volumes = clusteredStocks.value.map((s: unknown) => s.volume)
        const flows = clusteredStocks.value.map((s: unknown) => s.flow)

        const volumeMean = volumes.reduce((sum: unknown, v: unknown) => sum + v, 0) / volumes.length
        const flowMean = flows.reduce((sum: unknown, f: unknown) => sum + f, 0) / flows.length

        const volumeVariance =
            volumes.reduce((sum: unknown, v: unknown) => sum + Math.pow(v - volumeMean, 2), 0) / volumes.length
        const flowVariance = flows.reduce((sum: unknown, f: unknown) => sum + Math.pow(f - flowMean, 2), 0) / flows.length

        return Math.sqrt(volumeVariance + flowVariance)
    }

    const getClusterColor = (clusterId: number): string => {
        const colors = ['#D4AF37', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#EC4899', '#EF4444', '#F97316']
        return colors[clusterId % colors.length]
    }

    const getXPosition = (volume: number): number => {
        const volumes = clusteredStocks.value.map((s: unknown) => s.volume)
        const minVol = Math.min(...volumes)
        const maxVol = Math.max(...volumes)
        const range = maxVol - minVol
        if (range === 0) return 50
        return ((volume - minVol) / range) * 80 + 10 // 10%到90%的范围
    }

    const getYPosition = (flow: number): number => {
        const flows = clusteredStocks.value.map((s: unknown) => s.flow)
        const minFlow = Math.min(...flows)
        const maxFlow = Math.max(...flows)
        const range = maxFlow - minFlow
        if (range === 0) return 50
        return ((flow - minFlow) / range) * 80 + 10 // 10%到90%的范围
    }

    // 风口诊断辅助函数
    const getSentimentClass = (sentiment: string): string => {
        if (sentiment === '乐观') return 'positive'
        if (sentiment === '悲观') return 'negative'
        return 'neutral'
    }

    const getAttentionClass = (attention: string): string => {
        if (attention === '高关注') return 'positive'
        if (attention === '低关注') return 'negative'
        return 'neutral'
    }

    const getRotationClass = (rotation: string): string => {
        if (rotation === '快速轮动') return 'warning'
        if (rotation === '稳定') return 'positive'
        return 'neutral'
    }

    const getWindowClass = (window: string): string => {
        if (window === '开放') return 'positive'
        if (window === '关闭') return 'negative'
        return 'neutral'
    }

  return {
    props,
    heatmapPeriod,
    flowType,
    showLabels,
    capitalFlows,
    clusteringData,
    mainForceData,
    opportunityData,
    northboundFlow,
    southboundFlow,
    mainForceFlow,
    retailFlow,
    sectorFlows,
    minFlow,
    flows,
    maxFlow,
    flows,
    clusters,
    clusteredStocks,
    mainForceControl,
    top5Concentration,
    top10Concentration,
    mainForceRanking,
    marketSentiment,
    fundAttention,
    sectorRotation,
    opportunityWindow,
    hotSectors,
    investmentInsights,
    periodOptions,
    flowTypeOptions,
    getNorthboundFlow,
    getSouthboundFlow,
    getMainForceFlow,
    getRetailFlow,
    formatFlow,
    sign,
    absFlow,
    formatVolume,
    getHeatmapColor,
    intensity,
    green,
    alpha,
    intensity,
    red,
    alpha,
    getHeatmapOpacity,
    maxAbsFlow,
    getSectorCode,
    codes,
    getMaxClusterSize,
    getClusteringDensity,
    avgClusterSize,
    maxClusterSize,
    getDispersionIndex,
    volumes,
    flows,
    volumeMean,
    flowMean,
    volumeVariance,
    flowVariance,
    getClusterColor,
    colors,
    getXPosition,
    volumes,
    minVol,
    maxVol,
    range,
    getYPosition,
    flows,
    minFlow,
    maxFlow,
    range,
    getSentimentClass,
    getAttentionClass,
    getRotationClass,
    getWindowClass,
  }
}
