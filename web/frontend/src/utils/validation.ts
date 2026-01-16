// Runtime Validation Module
// 使用Zod进行运行时数据验证，确保store数据的类型安全

import { z } from 'zod'

// 基础类型验证器
export const StringSchema = z.string()
export const NumberSchema = z.number()
export const BooleanSchema = z.boolean()
export const DateSchema = z.date()
export const OptionalStringSchema = z.string().optional()
export const OptionalNumberSchema = z.number().optional()
export const OptionalBooleanSchema = z.boolean().optional()

// 市场数据验证器
export const MarketAnalysisSchema = z.object({
    trend: OptionalStringSchema,
    sentiment: OptionalNumberSchema,
    volatility: OptionalNumberSchema,
    volume: OptionalNumberSchema
}).catchall(z.any()) // 允许扩展属性

// 交易数据验证器
export const TradingFiltersSchema = z.object({
    symbol: OptionalStringSchema,
    dateFrom: OptionalStringSchema,
    dateTo: OptionalStringSchema,
    status: OptionalStringSchema
}).catchall(z.any())

// 回测结果验证器
export const BacktestResultSchema = z.object({
    id: OptionalStringSchema,
    strategyId: OptionalStringSchema,
    status: z.enum(['pending', 'running', 'completed', 'failed']).optional(),
    result: z.any().optional(),
    error: OptionalStringSchema,
    startTime: z.date().optional(),
    endTime: z.date().optional()
})

// 优化任务验证器
export const OptimizationTaskSchema = z.object({
    id: OptionalStringSchema,
    strategyId: OptionalStringSchema,
    status: z.enum(['pending', 'running', 'completed', 'failed']).optional(),
    parameters: z.record(z.string(), z.unknown()).optional(),
    result: z.any().optional(),
    error: OptionalStringSchema,
    startTime: z.date().optional(),
    endTime: z.date().optional()
})

// 缓存数据验证器
export const CachedDataSchema = z.object({
    data: z.any(),
    timestamp: z.number(),
    ttl: z.number()
})

// 实时更新验证器
export const RealtimeUpdateSchema = z.object({
    type: z.string(),
    data: z.any(),
    timestamp: z.number()
})

// Store状态验证器
export const MarketStateSchema = z.object({
    marketOverview: z.any().nullable(),
    marketAnalysis: MarketAnalysisSchema.nullable(),
    lastUpdateTime: z.string()
})

export const TradingDataStateSchema = z.object({
    tradingSignals: z.any().nullable(),
    tradingHistory: z.any().nullable(),
    positionMonitor: z.any().nullable(),
    performanceAnalysis: z.any().nullable(),
    lastUpdateTime: z.string()
})

export const StrategyStateSchema = z.object({
    strategyManagement: z.any().nullable(),
    backtestResults: z.array(BacktestResultSchema),
    optimizationTasks: z.array(OptimizationTaskSchema),
    lastUpdateTime: z.string()
})

export const RiskStateSchema = z.object({
    riskMonitor: z.any().nullable(),
    announcementMonitor: z.any().nullable(),
    riskAlerts: z.any().nullable(),
    lastUpdateTime: z.string()
})

export const SystemStateSchema = z.object({
    monitoringDashboard: z.any().nullable(),
    systemSettings: z.any().nullable(),
    systemHealth: z.any().nullable(),
    systemConfig: z.record(z.string(), z.unknown()).nullable(),
    lastUpdateTime: z.string()
})

export const UiStateSchema = z.object({
    activeFunction: z.string(),
    expandedNodes: z.instanceof(Set).transform(set => Array.from(set)),
    loadingStates: z.record(z.string(), z.boolean()).optional(),
    cache: z.any(), // Map类型在Zod中处理比较复杂，使用any暂时
    lastUpdateTime: z.string()
})

// 验证函数
export function validateMarketState(data: any): boolean {
    try {
        MarketStateSchema.parse(data)
        return true
    } catch (error) {
        console.error('MarketState validation failed:', error)
        return false
    }
}

export function validateTradingDataState(data: any): boolean {
    try {
        TradingDataStateSchema.parse(data)
        return true
    } catch (error) {
        console.error('TradingDataState validation failed:', error)
        return false
    }
}

export function validateStrategyState(data: any): boolean {
    try {
        StrategyStateSchema.parse(data)
        return true
    } catch (error) {
        console.error('StrategyState validation failed:', error)
        return false
    }
}

export function validateRiskState(data: any): boolean {
    try {
        RiskStateSchema.parse(data)
        return true
    } catch (error) {
        console.error('RiskState validation failed:', error)
        return false
    }
}

export function validateSystemState(data: any): boolean {
    try {
        SystemStateSchema.parse(data)
        return true
    } catch (error) {
        console.error('SystemState validation failed:', error)
        return false
    }
}

export function validateUiState(data: any): boolean {
    try {
        UiStateSchema.parse(data)
        return true
    } catch (error) {
        console.error('UiState validation failed:', error)
        return false
    }
}

// 通用验证函数
export function validateWithSchema<T>(data: any, schema: z.ZodSchema<T>): T | null {
    try {
        return schema.parse(data)
    } catch (error) {
        console.error('Validation failed:', error)
        return null
    }
}

// 开发模式下的严格验证
export const isDevelopment = import.meta.env.DEV

export function validateInDevelopment<T>(data: any, schema: z.ZodSchema<T>, context: string): T | null {
    if (!isDevelopment) return data

    const result = validateWithSchema(data, schema)
    if (result === null) {
        console.error(`Validation failed in ${context}`)
    }
    return result
}