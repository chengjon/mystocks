import { ref, computed } from 'vue'

export function useFinancialValuation() {
    const keyMetrics = ref([
        { key: 'roe', name: '净资产收益率', current: '22.5%', unit: '', trend: 'up', industryAvg: '15.2%', historicalAvg: '18.5%' },
        { key: 'margin', name: '毛利率', current: '42.8%', unit: '', trend: 'stable', industryAvg: '35.6%', historicalAvg: '41.2%' },
        { key: 'debt', name: '资产负债率', current: '32.1%', unit: '', trend: 'down', industryAvg: '45.8%', historicalAvg: '38.5%' }
    ])

    const valuationStatus = ref('合理区间')
    const financialHealthScore = ref(85)
    
    const profitabilityScore = ref(92)
    const solvencyScore = ref(78)
    const efficiencyScore = ref(85)

    const dupontData = ref({
        roe: 22.5,
        netProfitMargin: 15.2,
        assetTurnover: 0.85,
        equityMultiplier: 1.75
    })

    // Methods
    const getCurrentValuation = () => '¥1,245.00'
    const getPERatio = () => '15.2x'
    const getPBRatio = () => '2.8x'
    const getPSRatio = () => '3.5x'
    const getDividendYield = () => '3.2%'
    const getValuationStatus = () => valuationStatus.value

    return {
        keyMetrics,
        financialHealthScore,
        profitabilityScore,
        solvencyScore,
        efficiencyScore,
        dupontData,
        getCurrentValuation,
        getPERatio,
        getPBRatio,
        getPSRatio,
        getDividendYield,
        getValuationStatus
    }
}
