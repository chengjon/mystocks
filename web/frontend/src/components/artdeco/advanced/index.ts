// ============================================
//   ARTDECO ADVANCED ANALYSIS COMPONENTS
//   高级分析组件库
//
//   Design System: Art Deco (The "Gatsby" Aesthetic)
//   - 几何装饰与金色强调
//   - 戏剧性对比与平衡
//   - 奢华的视觉体验
// ============================================

// 核心组件
export { default as ArtDecoAnalysisDashboard } from '../core/ArtDecoAnalysisDashboard.vue'
export { default as ArtDecoFundamentalAnalysis } from '../core/ArtDecoFundamentalAnalysis.vue'
export { default as ArtDecoTechnicalAnalysis } from '../core/ArtDecoTechnicalAnalysis.vue'
export { default as ArtDecoRadarAnalysis } from '../core/ArtDecoRadarAnalysis.vue'

// 高级分析组件
export { default as ArtDecoTradingSignals } from './ArtDecoTradingSignals.vue'
export { default as ArtDecoTimeSeriesAnalysis } from './ArtDecoTimeSeriesAnalysis.vue'
export { default as ArtDecoMarketPanorama } from './ArtDecoMarketPanorama.vue'
export { default as ArtDecoCapitalFlow } from './ArtDecoCapitalFlow.vue'
export { default as ArtDecoChipDistribution } from './ArtDecoChipDistribution.vue'
export { default as ArtDecoAnomalyTracking } from './ArtDecoAnomalyTracking.vue'
export { default as ArtDecoFinancialValuation } from './ArtDecoFinancialValuation.vue'
export { default as ArtDecoSentimentAnalysis } from './ArtDecoSentimentAnalysis.vue'
export { default as ArtDecoDecisionModels } from './ArtDecoDecisionModels.vue'

// 批量分析组件
export { default as ArtDecoBatchAnalysisView } from './ArtDecoBatchAnalysisView.vue'

// 基础UI组件
export { default as ArtDecoCard } from '../base/ArtDecoCard.vue'
export { default as ArtDecoStatCard } from '../base/ArtDecoStatCard.vue'
export { default as ArtDecoButton } from '../base/ArtDecoButton.vue'
export { default as ArtDecoBadge } from '../base/ArtDecoBadge.vue'
export { default as ArtDecoInput } from '../base/ArtDecoInput.vue'
export { default as ArtDecoSelect } from '../base/ArtDecoSelect.vue'
export { default as ArtDecoSwitch } from '../base/ArtDecoSwitch.vue'
export { default as ArtDecoProgress } from '../base/ArtDecoProgress.vue'

// 类型定义
export interface AnalysisComponent {
    name: string
    title: string
    description: string
    icon: string
    component: any
}

export interface AnalysisData {
    fundamental?: any
    technical?: any
    'trading-signals'?: any
    'time-series'?: any
    'market-panorama'?: any
    'capital-flow'?: any
    'chip-distribution'?: any
    'anomaly-tracking'?: any
    'financial-valuation'?: any
    sentiment?: any
    'decision-models'?: any
    'multidimensional-radar'?: any
}

// 组件映射表
export const ANALYSIS_COMPONENTS: Record<string, AnalysisComponent> = {
    fundamental: {
        name: 'fundamental',
        title: '基本面分析',
        description: '财务比率分析、偿债能力、盈利能力、杜邦分析',
        icon: 'trending-up',
        component: () => import('../core/ArtDecoFundamentalAnalysis.vue')
    },
    technical: {
        name: 'technical',
        title: '技术面分析',
        description: '自定义技术分析方法、26个技术指标、趋势分析',
        icon: 'bar-chart',
        component: () => import('../core/ArtDecoTechnicalAnalysis.vue')
    },
    'trading-signals': {
        name: 'trading-signals',
        title: '交易信号分析',
        description: '长短线买卖点计算、实时监控、自定义条件判断',
        icon: 'zap',
        component: () => import('./ArtDecoTradingSignals.vue')
    },
    'time-series': {
        name: 'time-series',
        title: '时序分析',
        description: '特征表示、拐点检测、历史数据分段、预测方法',
        icon: 'clock',
        component: () => import('./ArtDecoTimeSeriesAnalysis.vue')
    },
    'market-panorama': {
        name: 'market-panorama',
        title: '市场全景分析',
        description: '资金流向全景、交易活跃度、趋势变化、市值分布、动态估值',
        icon: 'globe',
        component: () => import('./ArtDecoMarketPanorama.vue')
    },
    'capital-flow': {
        name: 'capital-flow',
        title: '资金流向分析',
        description: '聚类分析、主力控盘能力计算、风口位置诊断',
        icon: 'dollar-sign',
        component: () => import('./ArtDecoCapitalFlow.vue')
    },
    'chip-distribution': {
        name: 'chip-distribution',
        title: '筹码分布分析',
        description: '基于成本转换原理的筹码分析',
        icon: 'grid',
        component: () => import('./ArtDecoChipDistribution.vue')
    },
    'anomaly-tracking': {
        name: 'anomaly-tracking',
        title: '异动跟踪分析',
        description: '基于涨跌幅排序的异动检测',
        icon: 'alert-triangle',
        component: () => import('./ArtDecoAnomalyTracking.vue')
    },
    'financial-valuation': {
        name: 'financial-valuation',
        title: '财务估值分析',
        description: '财务指标、杜邦分析、定价方法、历史相似收益估值',
        icon: 'file-text',
        component: () => import('./ArtDecoFinancialValuation.vue')
    },
    sentiment: {
        name: 'sentiment',
        title: '情绪分析',
        description: '研报分析、新闻情绪、人气指标',
        icon: 'smile',
        component: () => import('./ArtDecoSentimentAnalysis.vue')
    },
    'decision-models': {
        name: 'decision-models',
        title: '决策模型分析',
        description: '巴菲特模型、欧内尔模型、林奇模型、数据挖掘模型',
        icon: 'brain',
        component: () => import('./ArtDecoDecisionModels.vue')
    },
    'multidimensional-radar': {
        name: 'multidimensional-radar',
        title: '多维度雷达分析',
        description: '技术面/消息面/基本面/资金面/行业面/估值面等多维度综合分析',
        icon: 'radar',
        component: () => import('../core/ArtDecoRadarAnalysis.vue')
    }
}

// 组件工具函数
export const getAnalysisComponent = (analysisType: string) => {
    return ANALYSIS_COMPONENTS[analysisType]?.component
}

export const getAnalysisInfo = (analysisType: string) => {
    return ANALYSIS_COMPONENTS[analysisType]
}

export const getAllAnalysisTypes = () => {
    return Object.keys(ANALYSIS_COMPONENTS)
}

// 样式常量
export const ARTDECO_ANALYSIS_STYLES = {
    // 主色调
    primary: '#D4AF37',
    secondary: '#1E3D59',
    accent: '#F2E8C4',

    // 功能色
    success: '#67C23A',
    warning: '#E6A23C',
    danger: '#F56C6C',
    info: '#909399',

    // 金融色 (A股标准)
    rise: '#FF5252', // 涨 - 红色
    fall: '#00E676', // 跌 - 绿色
    flat: '#888888', // 平 - 灰色

    // 背景色
    background: '#0A0A0A', // 黑曜石黑
    surface: '#141414', // 丰富的炭黑
    elevated: '#1a1a1a', // 提升表面

    // 文字色
    text: '#F2F0E4', // 香槟奶油
    textMuted: '#888888', // 锡色
    textSubtle: 'rgba(255,255,255,0.6)' // 微妙
}

// 注意: 默认导出已移除，使用命名导出即可
// export default removed - use named exports
