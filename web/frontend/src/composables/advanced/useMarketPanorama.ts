import { ref, computed } from 'vue'

export function useMarketPanorama() {
    const marketIndices = ref([
        { code: '000001.SH', name: '上证指数', value: 3245.85, changePercent: 1.25, volume: 352000000 },
        { code: '399001.SZ', name: '深证成指', value: 11025.42, changePercent: 0.85, volume: 425000000 },
        { code: '399006.SZ', name: '创业板指', value: 2245.15, changePercent: 1.58, volume: 125000000 }
    ])

    const northboundFlow = ref(45.8)
    const southboundFlow = ref(-12.5)
    const mainForceFlow = ref(85.2)

    const sectorFlows = ref([
        { name: '非银金融', flow: 12.5 },
        { name: '计算机', flow: 8.4 },
        { name: '食品饮料', flow: -5.2 },
        { name: '电力设备', flow: -10.8 }
    ])

    const stats = ref({
        totalMarketCap: '85.2万亿',
        totalTurnover: '9,850亿',
        upCount: 3245,
        downCount: 1520,
        limitUpCount: 85,
        limitDownCount: 12
    })

    // Methods
    const getTotalMarketCap = () => stats.value.totalMarketCap
    const getTotalTurnover = () => stats.value.totalTurnover
    const getUpCount = () => stats.value.upCount
    const getDownCount = () => stats.value.downCount
    const getLimitUpCount = () => stats.value.limitUpCount
    const getLimitDownCount = () => stats.value.limitDownCount

    return {
        marketIndices,
        northboundFlow,
        southboundFlow,
        mainForceFlow,
        sectorFlows,
        getTotalMarketCap,
        getTotalTurnover,
        getUpCount,
        getDownCount,
        getLimitUpCount,
        getLimitDownCount
    }
}
