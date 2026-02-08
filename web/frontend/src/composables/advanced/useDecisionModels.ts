import { ref, computed } from 'vue'

export function useDecisionModels() {
    const decisionModels = ref([
        { name: '巴菲特价值模型', description: '基于财务稳健性与盈利能力', signal: 'buy', confidence: 85, expectedReturn: 15, riskLevel: 'low' },
        { name: '欧内尔CANSLIM', description: '强劲成长与市场趋势', signal: 'hold', confidence: 72, expectedReturn: 22, riskLevel: 'medium' },
        { name: '林奇PEG模型', description: '成长性与估值匹配度', signal: 'buy', confidence: 78, expectedReturn: 18, riskLevel: 'low' },
        { name: '数据挖掘模型', description: '机器学习趋势预测', signal: 'sell', confidence: 65, expectedReturn: 12, riskLevel: 'high' }
    ])

    const buffettCriteria = ref([
        { name: '净资产收益率 (ROE)', score: 92, currentValue: '22.5%', standardValue: '>15%' },
        { name: '毛利率稳定性', score: 88, currentValue: '42.8%', standardValue: '稳定' },
        { name: '负债权益比', score: 95, currentValue: '0.32', standardValue: '<0.5' },
        { name: '自由现金流', score: 85, currentValue: '充足', standardValue: '正值' }
    ])

    const canslimFactors = ref([
        { letter: 'C', name: '当前季度业绩', score: 85, description: '季度盈余大幅增长' },
        { letter: 'A', name: '年度盈利增长', score: 92, description: '过去三年年度增长强劲' },
        { letter: 'N', name: '新产品/新管理', score: 75, description: '行业地位提升' },
        { letter: 'S', name: '供给与需求', score: 68, description: '成交量配合上涨' },
        { letter: 'L', name: '行业领头羊', score: 88, description: '处于行业领先地位' },
        { letter: 'I', name: '机构投资者', score: 82, description: '机构持仓稳定增加' },
        { letter: 'M', name: '市场方向', score: 65, description: '大盘趋势转强' }
    ])

    const pegRatio = ref(0.85)
    const peRatio = ref(15.2)
    const growthRate = ref(18.5)

    const miningAccuracy = ref(78.5)
    const predictionProbability = ref(62.4)
    const topFeature = ref('成交量放大')

    const buffettOverallScore = computed(() => {
        return Math.round(buffettCriteria.value.reduce((acc, c) => acc + c.score, 0) / buffettCriteria.value.length)
    })

    const oneilSignalStrength = computed(() => {
        return Math.round(canslimFactors.value.reduce((acc, f) => acc + f.score, 0) / canslimFactors.value.length)
    })

    // Methods
    const getBestModel = () => '巴菲特价值模型'
    const getDecisionConfidence = () => '85%'
    const getExpectedReturn = () => '15.8%'
    const getRiskAssessment = () => '低风险'

    return {
        decisionModels,
        buffettCriteria,
        canslimFactors,
        pegRatio,
        peRatio,
        growthRate,
        miningAccuracy,
        predictionProbability,
        topFeature,
        buffettOverallScore,
        oneilSignalStrength,
        getBestModel,
        getDecisionConfidence,
        getExpectedReturn,
        getRiskAssessment
    }
}
