// 高级分析API客户端
// Advanced Analysis API Client

import request from '@/utils/request'

// 创建专用的 http 客户端
const http = {
    get: (url: string, config?: any) => request.get(url, config).then((resp: any) => resp.data || resp),
    post: (url: string, data?: any, config?: any) =>
        request.post(url, data, config).then((resp: any) => resp.data || resp)
}

export interface AnalysisRequest {
    symbol: string
    include_raw_data?: boolean
}

export interface BatchAnalysisRequest {
    analyses: string[]
    symbol: string
    options?: {
        include_raw_data?: boolean
    }
}

export interface AnalysisResponse {
    success: boolean
    message?: string
    data?: any
}

// 基本面分析
export const getFundamentalAnalysis = async (params: AnalysisRequest): Promise<AnalysisResponse> => {
    return await http.get('/api/v1/advanced-analysis/fundamental', { params })
}

// 技术面分析
export const getTechnicalAnalysis = async (params: AnalysisRequest): Promise<AnalysisResponse> => {
    return await http.get('/api/v1/advanced-analysis/technical', { params })
}

// 交易信号分析
export const getTradingSignalsAnalysis = async (params: AnalysisRequest): Promise<AnalysisResponse> => {
    return await http.get('/api/v1/advanced-analysis/trading-signals', { params })
}

// 时序分析
export const getTimeSeriesAnalysis = async (params: AnalysisRequest): Promise<AnalysisResponse> => {
    return await http.get('/api/v1/advanced-analysis/time-series', { params })
}

// 市场全景分析
export const getMarketPanoramaAnalysis = async (params: AnalysisRequest): Promise<AnalysisResponse> => {
    return await http.get('/api/v1/advanced-analysis/market-panorama', { params })
}

// 资金流向分析
export const getCapitalFlowAnalysis = async (params: AnalysisRequest): Promise<AnalysisResponse> => {
    return await http.get('/api/v1/advanced-analysis/capital-flow', { params })
}

// 筹码分布分析
export const getChipDistributionAnalysis = async (params: AnalysisRequest): Promise<AnalysisResponse> => {
    return await http.get('/api/v1/advanced-analysis/chip-distribution', { params })
}

// 异常追踪分析
export const getAnomalyTrackingAnalysis = async (params: AnalysisRequest): Promise<AnalysisResponse> => {
    return await http.get('/api/v1/advanced-analysis/anomaly-tracking', { params })
}

// 财务估值分析
export const getFinancialValuationAnalysis = async (params: AnalysisRequest): Promise<AnalysisResponse> => {
    return await http.get('/api/v1/advanced-analysis/financial-valuation', { params })
}

// 情绪分析
export const getSentimentAnalysis = async (params: AnalysisRequest): Promise<AnalysisResponse> => {
    return await http.get('/api/v1/advanced-analysis/sentiment', { params })
}

// 决策模型分析
export const getDecisionModelsAnalysis = async (params: AnalysisRequest): Promise<AnalysisResponse> => {
    return await http.get('/api/v1/advanced-analysis/decision-models', { params })
}

// 多维度雷达分析
export const getMultidimensionalRadarAnalysis = async (params: AnalysisRequest): Promise<AnalysisResponse> => {
    return await http.get('/api/v1/advanced-analysis/multidimensional-radar', { params })
}

// 批量分析
export const getBatchAnalysis = async (data: BatchAnalysisRequest): Promise<AnalysisResponse> => {
    return await http.post('/api/v1/advanced-analysis/batch', data)
}

// 健康检查
export const getAnalysisHealth = async (): Promise<AnalysisResponse> => {
    return await http.get('/api/v1/advanced-analysis/health')
}

// 统一的高级分析API对象
export const advancedAnalysisApi = {
    fundamental: getFundamentalAnalysis,
    technical: getTechnicalAnalysis,
    'trading-signals': getTradingSignalsAnalysis,
    'time-series': getTimeSeriesAnalysis,
    'market-panorama': getMarketPanoramaAnalysis,
    'capital-flow': getCapitalFlowAnalysis,
    'chip-distribution': getChipDistributionAnalysis,
    'anomaly-tracking': getAnomalyTrackingAnalysis,
    'financial-valuation': getFinancialValuationAnalysis,
    sentiment: getSentimentAnalysis,
    'decision-models': getDecisionModelsAnalysis,
    'multidimensional-radar': getMultidimensionalRadarAnalysis,
    batch: getBatchAnalysis,
    health: getAnalysisHealth
}
