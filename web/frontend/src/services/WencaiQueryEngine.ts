/**
 * WenCai Query Engine Service
 *
 * 问财查询引擎 - 自然语言股票筛选服务
 * 支持9种预定义查询模式和AI回退机制
 */

import { apiClient } from '@/services/api-client'

// Query Pattern Types
export enum QueryPattern {
    PRICE_RANGE = 'price_range',
    VOLUME_SPIKE = 'volume_spike',
    TECHNICAL_BREAKTHROUGH = 'technical_breakthrough',
    FUNDAMENTAL_FILTER = 'fundamental_filter',
    MARKET_CAP_FILTER = 'market_cap_filter',
    SECTOR_PERFORMANCE = 'sector_performance',
    TREND_ANALYSIS = 'trend_analysis',
    VOLATILITY_FILTER = 'volatility_filter',
    CUSTOM_QUERY = 'custom_query'
}

// Query Result Interface
export interface QueryResult {
    success: boolean
    data?: QueryResultData
    error?: string
    executionTime: number
    patternUsed: QueryPattern
    aiFallback?: boolean
}

export interface QueryResultData {
    stocks: StockMatch[]
    total: number
    query: string
    pattern: QueryPattern
    filters: QueryFilter[]
}

export interface StockMatch {
    symbol: string
    name: string
    matchScore: number
    reasons: string[]
    data: Record<string, any>
}

export interface QueryFilter {
    type: string
    value: any
    description: string
}

// Predefined Query Patterns
const QUERY_PATTERNS = {
    [QueryPattern.PRICE_RANGE]: {
        patterns: [/股价在(\d+)到(\d+)元之间/, /价格区间(\d+)-(\d+)/, /股价(\d+)元以上/, /股价(\d+)元以下/],
        template: (matches: RegExpMatchArray) => ({
            price_min: matches[1] ? parseFloat(matches[1]) : undefined,
            price_max: matches[2] ? parseFloat(matches[2]) : undefined
        })
    },

    [QueryPattern.VOLUME_SPIKE]: {
        patterns: [/成交量放大(\d+)倍/, /放量(\d+)倍/, /成交量大于(\d+)万手/],
        template: (matches: RegExpMatchArray) => ({
            volume_multiplier: matches[1] ? parseFloat(matches[1]) : 2,
            min_volume: matches[2] ? parseInt(matches[2]) * 10000 : undefined
        })
    },

    [QueryPattern.TECHNICAL_BREAKTHROUGH]: {
        patterns: [/突破(\d+)日均线/, /站上(\d+)日线/, /突破(\d+)日均价/],
        template: (matches: RegExpMatchArray) => ({
            ma_period: parseInt(matches[1]),
            direction: 'up'
        })
    },

    [QueryPattern.FUNDAMENTAL_FILTER]: {
        patterns: [/市盈率小于(\d+)/, /市净率小于([\d.]+)/, /净利润增长(\d+)%/, /营收增长(\d+)%/],
        template: (matches: RegExpMatchArray) => ({
            pe_ratio_max: matches[1] ? parseFloat(matches[1]) : undefined,
            pb_ratio_max: matches[2] ? parseFloat(matches[2]) : undefined,
            profit_growth_min: matches[3] ? parseFloat(matches[3]) : undefined,
            revenue_growth_min: matches[4] ? parseFloat(matches[4]) : undefined
        })
    },

    [QueryPattern.MARKET_CAP_FILTER]: {
        patterns: [/市值大于(\d+)亿/, /市值小于(\d+)亿/, /大盘股/, /中小盘股/],
        template: (matches: RegExpMatchArray) => ({
            market_cap_min: matches[1] ? parseFloat(matches[1]) * 100000000 : undefined,
            market_cap_max: matches[2] ? parseFloat(matches[2]) * 100000000 : undefined,
            size_category: matches[3] || matches[4]
        })
    },

    [QueryPattern.SECTOR_PERFORMANCE]: {
        patterns: [/(\w+)板块涨幅前(\d+)名/, /(\w+)行业表现最好/, /(\w+)概念股/],
        template: (matches: RegExpMatchArray) => ({
            sector: matches[1],
            top_n: matches[2] ? parseInt(matches[2]) : 10,
            performance_metric: 'change_percent'
        })
    },

    [QueryPattern.TREND_ANALYSIS]: {
        patterns: [/连续(\d+)天上涨/, /连续(\d+)天下跌/, /上涨趋势股/, /下跌趋势股/],
        template: (matches: RegExpMatchArray) => ({
            consecutive_days: matches[1] ? parseInt(matches[1]) : 3,
            trend_direction: matches[2] ? 'down' : matches[3] ? 'up' : 'up'
        })
    },

    [QueryPattern.VOLATILITY_FILTER]: {
        patterns: [/波动率大于(\d+)%/, /波动率小于(\d+)%/, /高波动股/, /低波动股/],
        template: (matches: RegExpMatchArray) => ({
            volatility_min: matches[1] ? parseFloat(matches[1]) / 100 : undefined,
            volatility_max: matches[2] ? parseFloat(matches[2]) / 100 : undefined,
            volatility_level: matches[3] || matches[4]
        })
    }
}

export class WencaiQueryEngine {
    private static instance: WencaiQueryEngine
    private queryCache = new Map<string, QueryResult>()
    private aiServiceUrl = process.env.VUE_APP_AI_SERVICE_URL || 'https://api.openai.com/v1'

    private constructor() {}

    static getInstance(): WencaiQueryEngine {
        if (!WencaiQueryEngine.instance) {
            WencaiQueryEngine.instance = new WencaiQueryEngine()
        }
        return WencaiQueryEngine.instance
    }

    /**
     * Execute natural language query
     */
    async executeQuery(
        query: string,
        options: {
            useCache?: boolean
            aiFallback?: boolean
            maxResults?: number
        } = {}
    ): Promise<QueryResult> {
        const startTime = Date.now()
        const cacheKey = `${query}_${JSON.stringify(options)}`

        // Check cache first
        if (options.useCache !== false && this.queryCache.has(cacheKey)) {
            const cached = this.queryCache.get(cacheKey)!
            return {
                ...cached,
                executionTime: Date.now() - startTime
            }
        }

        try {
            // Try pattern matching first
            const patternResult = await this.tryPatternMatching(query, options.maxResults || 50)

            if (patternResult.success) {
                const result: QueryResult = {
                    success: true,
                    data: patternResult.data,
                    executionTime: Date.now() - startTime,
                    patternUsed: patternResult.data!.pattern
                }

                // Cache result
                if (options.useCache !== false) {
                    this.queryCache.set(cacheKey, result)
                }

                return result
            }

            // Fallback to AI if enabled
            if (options.aiFallback !== false) {
                const aiResult = await this.tryAIService(query, options.maxResults || 50)
                const result: QueryResult = {
                    success: aiResult.success,
                    data: aiResult.data,
                    error: aiResult.error,
                    executionTime: Date.now() - startTime,
                    patternUsed: QueryPattern.CUSTOM_QUERY,
                    aiFallback: true
                }

                // Cache result
                if (options.useCache !== false) {
                    this.queryCache.set(cacheKey, result)
                }

                return result
            }

            // No pattern matched and AI disabled
            return {
                success: false,
                error: '无法识别查询模式，请尝试更具体的描述',
                executionTime: Date.now() - startTime,
                patternUsed: QueryPattern.CUSTOM_QUERY
            }
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : '查询执行失败',
                executionTime: Date.now() - startTime,
                patternUsed: QueryPattern.CUSTOM_QUERY
            }
        }
    }

    /**
     * Try pattern matching for predefined queries
     */
    private async tryPatternMatching(
        query: string,
        maxResults: number
    ): Promise<{
        success: boolean
        data?: QueryResultData
    }> {
        for (const [patternKey, patternConfig] of Object.entries(QUERY_PATTERNS)) {
            for (const regex of patternConfig.patterns) {
                const matches = query.match(regex)
                if (matches) {
                    const filters = patternConfig.template(matches)
                    const result = await this.executeBackendQuery(patternKey as QueryPattern, filters, maxResults)

                    if (result.success) {
                        return {
                            success: true,
                            data: {
                                ...result.data!,
                                query,
                                pattern: patternKey as QueryPattern,
                                filters: this.buildFilterList(filters)
                            }
                        }
                    }
                }
            }
        }

        return { success: false }
    }

    /**
     * Execute query against backend API
     */
    private async executeBackendQuery(
        pattern: QueryPattern,
        filters: Record<string, any>,
        maxResults: number
    ): Promise<{ success: boolean; data?: QueryResultData }> {
        try {
            const response = await apiClient.post('/api/wencai/query', {
                pattern,
                filters,
                limit: maxResults
            })

            if (response.data?.success) {
                return {
                    success: true,
                    data: {
                        stocks: response.data.data.stocks || [],
                        total: response.data.data.total || 0,
                        query: '',
                        pattern,
                        filters: []
                    }
                }
            }

            return { success: false }
        } catch (error) {
            console.error('Backend query failed:', error)
            return { success: false }
        }
    }

    /**
     * Try AI service for unrecognized queries
     */
    private async tryAIService(
        query: string,
        maxResults: number
    ): Promise<{
        success: boolean
        data?: QueryResultData
        error?: string
    }> {
        try {
            const aiResponse = await fetch(this.aiServiceUrl + '/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${process.env.VUE_APP_OPENAI_API_KEY}`
                },
                body: JSON.stringify({
                    model: 'gpt-4',
                    messages: [
                        {
                            role: 'system',
                            content: `你是一个专业的股票筛选助手。用户会用自然语言描述筛选条件，你需要将其转换为结构化的筛选参数。

请返回以下JSON格式：
{
  "pattern": "price_range|volume_spike|technical_breakthrough|fundamental_filter|market_cap_filter|sector_performance|trend_analysis|volatility_filter",
  "filters": {
    // 对应的筛选参数
  }
}

示例：
用户: "股价在10到20元之间，成交量大于100万股"
返回: {"pattern": "price_range", "filters": {"price_min": 10, "price_max": 20, "volume_min": 1000000}}`
                        },
                        {
                            role: 'user',
                            content: query
                        }
                    ]
                })
            })

            if (!aiResponse.ok) {
                throw new Error('AI service unavailable')
            }

            const aiResult = await aiResponse.json()
            const parsedQuery = JSON.parse(aiResult.choices[0].message.content)

            // Execute the AI-parsed query
            return await this.executeBackendQuery(parsedQuery.pattern as QueryPattern, parsedQuery.filters, maxResults)
        } catch (error) {
            console.error('AI service error:', error)
            return {
                success: false,
                error: 'AI服务暂时不可用，请尝试使用预定义查询模式'
            }
        }
    }

    /**
     * Build filter list from raw filters
     */
    private buildFilterList(filters: Record<string, any>): QueryFilter[] {
        const filterList: QueryFilter[] = []

        for (const [key, value] of Object.entries(filters)) {
            if (value !== undefined) {
                filterList.push({
                    type: key,
                    value,
                    description: this.getFilterDescription(key, value)
                })
            }
        }

        return filterList
    }

    /**
     * Get human-readable filter description
     */
    private getFilterDescription(key: string, value: any): string {
        const descriptions: Record<string, (value: any) => string> = {
            price_min: v => `股价 ≥ ¥${v}`,
            price_max: v => `股价 ≤ ¥${v}`,
            volume_multiplier: v => `成交量放大 ${v} 倍`,
            ma_period: v => `突破 ${v} 日均线`,
            pe_ratio_max: v => `市盈率 ≤ ${v}`,
            market_cap_min: v => `市值 ≥ ${v / 100000000} 亿`,
            sector: v => `${v} 板块`,
            consecutive_days: v => `连续 ${v} 天`,
            volatility_min: v => `波动率 ≥ ${(v * 100).toFixed(1)}%`
        }

        return descriptions[key]?.(value) || `${key}: ${value}`
    }

    /**
     * Clear query cache
     */
    clearCache(): void {
        this.queryCache.clear()
    }

    /**
     * Get supported patterns
     */
    getSupportedPatterns(): QueryPattern[] {
        return Object.values(QueryPattern)
    }

    /**
     * Get pattern examples
     */
    getPatternExamples(pattern: QueryPattern): string[] {
        const examples: Record<QueryPattern, string[]> = {
            [QueryPattern.PRICE_RANGE]: ['股价在10到50元之间', '价格区间20-100', '股价30元以上'],
            [QueryPattern.VOLUME_SPIKE]: ['成交量放大2倍', '放量3倍以上', '成交量大于50万手'],
            [QueryPattern.TECHNICAL_BREAKTHROUGH]: ['突破5日均线', '站上10日线', '突破20日均价'],
            [QueryPattern.FUNDAMENTAL_FILTER]: ['市盈率小于20', '市净率小于2', '净利润增长30%'],
            [QueryPattern.MARKET_CAP_FILTER]: ['市值大于500亿', '市值小于100亿', '大盘股'],
            [QueryPattern.SECTOR_PERFORMANCE]: ['科技板块涨幅前10名', '医药行业表现最好', '新能源概念股'],
            [QueryPattern.TREND_ANALYSIS]: ['连续3天上涨', '连续5天下跌', '上涨趋势股'],
            [QueryPattern.VOLATILITY_FILTER]: ['波动率大于10%', '波动率小于5%', '高波动股'],
            [QueryPattern.CUSTOM_QUERY]: ['AI智能解析模式']
        }

        return examples[pattern] || []
    }
}

// Export singleton instance
export const wencaiQueryEngine = WencaiQueryEngine.getInstance()
