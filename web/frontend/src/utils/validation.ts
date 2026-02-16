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
}).catchall(z.unknown()) // 允许扩展属性

// 交易数据验证器
export const TradingFiltersSchema = z.object({
    symbol: OptionalStringSchema,
    dateFrom: OptionalStringSchema,
    dateTo: OptionalStringSchema,
    status: OptionalStringSchema
}).catchall(z.unknown())

// 回测结果验证器
export const BacktestResultSchema = z.object({
    id: OptionalStringSchema,
    strategyId: OptionalStringSchema,
    status: z.enum(['pending', 'running', 'completed', 'failed']).optional(),
    result: z.unknown().optional(),
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
    result: z.unknown().optional(),
    error: OptionalStringSchema,
    startTime: z.date().optional(),
    endTime: z.date().optional()
})

// 缓存数据验证器
export const CachedDataSchema = z.object({
    data: z.unknown(),
    timestamp: z.number(),
    ttl: z.number()
})

// 实时更新验证器
export const RealtimeUpdateSchema = z.object({
    type: z.string(),
    data: z.unknown(),
    timestamp: z.number()
})

// Store状态验证器
export const MarketStateSchema = z.object({
    marketOverview: z.unknown().nullable(),
    marketAnalysis: MarketAnalysisSchema.nullable(),
    lastUpdateTime: z.string()
})

export const TradingDataStateSchema = z.object({
    tradingSignals: z.unknown().nullable(),
    tradingHistory: z.unknown().nullable(),
    positionMonitor: z.unknown().nullable(),
    performanceAnalysis: z.unknown().nullable(),
    lastUpdateTime: z.string()
})

export const StrategyStateSchema = z.object({
    strategyManagement: z.unknown().nullable(),
    backtestResults: z.array(BacktestResultSchema),
    optimizationTasks: z.array(OptimizationTaskSchema),
    lastUpdateTime: z.string()
})

export const RiskStateSchema = z.object({
    riskMonitor: z.unknown().nullable(),
    announcementMonitor: z.unknown().nullable(),
    riskAlerts: z.unknown().nullable(),
    lastUpdateTime: z.string()
})

export const SystemStateSchema = z.object({
    monitoringDashboard: z.unknown().nullable(),
    systemSettings: z.unknown().nullable(),
    systemHealth: z.unknown().nullable(),
    systemConfig: z.record(z.string(), z.unknown()).nullable(),
    lastUpdateTime: z.string()
})

export const UiStateSchema = z.object({
    activeFunction: z.string(),
    expandedNodes: z.instanceof(Set).transform(set => Array.from(set)),
    loadingStates: z.record(z.string(), z.boolean()).optional(),
    cache: z.unknown(), // Map类型在Zod中处理比较复杂，使用any暂时
    lastUpdateTime: z.string()
})

// 验证函数
export function validateMarketState(data: unknown): boolean {
    try {
        MarketStateSchema.parse(data)
        return true
    } catch (error) {
        console.error('MarketState validation failed:', error)
        return false
    }
}

export function validateTradingDataState(data: unknown): boolean {
    try {
        TradingDataStateSchema.parse(data)
        return true
    } catch (error) {
        console.error('TradingDataState validation failed:', error)
        return false
    }
}

export function validateStrategyState(data: unknown): boolean {
    try {
        StrategyStateSchema.parse(data)
        return true
    } catch (error) {
        console.error('StrategyState validation failed:', error)
        return false
    }
}

export function validateRiskState(data: unknown): boolean {
    try {
        RiskStateSchema.parse(data)
        return true
    } catch (error) {
        console.error('RiskState validation failed:', error)
        return false
    }
}

export function validateSystemState(data: unknown): boolean {
    try {
        SystemStateSchema.parse(data)
        return true
    } catch (error) {
        console.error('SystemState validation failed:', error)
        return false
    }
}

export function validateUiState(data: unknown): boolean {
    try {
        UiStateSchema.parse(data)
        return true
    } catch (error) {
        console.error('UiState validation failed:', error)
        return false
    }
}

// 通用验证函数
export function validateWithSchema<T>(data: unknown, schema: z.ZodSchema<T>): T | null {
    try {
        return schema.parse(data)
    } catch (error) {
        console.error('Validation failed:', error)
        return null
    }
}

// 开发模式下的严格验证
export const isDevelopment = import.meta.env.DEV

export function validateInDevelopment<T>(data: unknown, schema: z.ZodSchema<T>, context: string): T | null {
    if (!isDevelopment) return data as T

    const result = validateWithSchema(data, schema)
    if (result === null) {
        console.error(`Validation failed in ${context}`)
    }
    return result
}