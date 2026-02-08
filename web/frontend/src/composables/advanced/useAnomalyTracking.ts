import { ref, computed } from 'vue'

export function useAnomalyTracking() {
    const activeAlerts = ref([
        { id: 1, symbol: '600519.SH', symbolName: '贵州茅台', type: 'volume_surge', severity: 'critical', timestamp: new Date(), status: 'pending', description: '成交量异常放大 500%', anomalyScore: 8.5, confidence: 92, impactLevel: 'high' },
        { id: 2, symbol: '000001.SZ', symbolName: '平安银行', type: 'price_flash_crash', severity: 'warning', timestamp: new Date(), status: 'investigating', description: '股价快速下跌 2%', anomalyScore: 4.2, confidence: 75, impactLevel: 'medium' }
    ])

    const patterns = ref([
        { name: '老鼠仓嫌疑', confidence: 82, count: 3, description: '特定时间点大单成交' },
        { name: '主力吸筹', confidence: 75, count: 12, description: '底部缩量上涨' },
        { name: '游资对倒', confidence: 68, count: 5, description: '高换手率但价格震荡' }
    ])

    const stats = ref({
        totalAnomalies: 42,
        highRisk: 5,
        detectionAccuracy: 94.2,
        avgResponseTime: '1.2s'
    })

    const monitoringMode = ref('comprehensive')
    const autoAlert = ref(true)

    // Methods
    const getAnomalyCount = () => stats.value.totalAnomalies
    const getHighRiskCount = () => stats.value.highRisk
    const getDetectionAccuracy = () => stats.value.detectionAccuracy + '%'
    const getAvgResponseTime = () => stats.value.avgResponseTime

    return {
        activeAlerts,
        patterns,
        stats,
        monitoringMode,
        autoAlert,
        getAnomalyCount,
        getHighRiskCount,
        getDetectionAccuracy,
        getAvgResponseTime
    }
}
