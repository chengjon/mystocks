/**
 * Chart Data Processing Utilities
 *
 * Provides comprehensive data processing, formatting, and transformation utilities
 * for all chart components in the MyStocks data visualization system.
 */

import type { EChartsOption } from 'echarts'
import { FINANCIAL_COLORS, GRADIENTS } from '../styles/chart-theme'

// ================ 数据类型定义 ================

export interface ChartDataPoint {
    name: string
    value: number
    [key: string]: any
}

export interface TimeSeriesDataPoint {
    timestamp: number | string | Date
    value: number
    [key: string]: any
}

export interface SankeyNode {
    name: string
    [key: string]: any
}

export interface SankeyLink {
    source: string
    target: string
    value: number
    [key: string]: any
}

export interface TreeNode {
    name: string
    value?: number
    children?: TreeNode[]
    [key: string]: any
}

export interface HeatmapDataPoint {
    x: number | string
    y: number | string
    value: number
    [key: string]: any
}

// ================ 数据格式化工具 ================

/**
 * 格式化数字显示
 */
export class NumberFormatter {
    /**
     * 格式化为百分比
     */
    static toPercentage(value: number, decimals: number = 2): string {
        return `${(value * 100).toFixed(decimals)}%`
    }

    /**
     * 格式化为货币
     */
    static toCurrency(value: number, currency: string = '¥', decimals: number = 2): string {
        return `${currency}${value.toLocaleString('zh-CN', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}`
    }

    /**
     * 格式化为数量单位
     */
    static toVolume(value: number): string {
        if (value >= 100000000) {
            return `${(value / 100000000).toFixed(1)}亿`
        } else if (value >= 10000) {
            return `${(value / 10000).toFixed(1)}万`
        }
        return value.toString()
    }

    /**
     * 智能格式化大数字
     */
    static toSmartNumber(value: number): string {
        if (Math.abs(value) >= 100000000) {
            return `${(value / 100000000).toFixed(1)}亿`
        } else if (Math.abs(value) >= 10000) {
            return `${(value / 10000).toFixed(1)}万`
        } else if (Math.abs(value) >= 1000) {
            return `${(value / 1000).toFixed(1)}k`
        }
        return value.toString()
    }
}

/**
 * 时间格式化工具
 */
export class TimeFormatter {
    /**
     * 格式化为日期字符串
     */
    static toDateString(timestamp: number | string | Date): string {
        const date = new Date(timestamp)
        return date.toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        })
    }

    /**
     * 格式化为时间字符串
     */
    static toTimeString(timestamp: number | string | Date): string {
        const date = new Date(timestamp)
        return date.toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        })
    }

    /**
     * 格式化为日期时间字符串
     */
    static toDateTimeString(timestamp: number | string | Date): string {
        const date = new Date(timestamp)
        return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    /**
     * 获取时间范围描述
     */
    static getTimeRangeDescription(start: Date, end: Date): string {
        const diffMs = end.getTime() - start.getTime()
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

        if (diffDays < 1) return '今日'
        if (diffDays < 7) return `${diffDays}天`
        if (diffDays < 30) return `${Math.floor(diffDays / 7)}周`
        if (diffDays < 365) return `${Math.floor(diffDays / 30)}月`
        return `${Math.floor(diffDays / 365)}年`
    }
}

// ================ 数据处理工具 ================

/**
 * 数据聚合工具
 */
export class DataAggregator {
    /**
     * 按时间间隔聚合数据
     */
    static aggregateByTime<T extends TimeSeriesDataPoint>(
        data: T[],
        interval: '1m' | '5m' | '15m' | '30m' | '1h' | '1d',
        valueField: keyof T = 'value' as keyof T
    ): T[] {
        if (!data.length) return []

        const intervalMs = this.getIntervalMs(interval)
        const grouped = new Map<number, T[]>()

        // 按时间间隔分组
        data.forEach(item => {
            const timestamp = new Date(item.timestamp).getTime()
            const groupKey = Math.floor(timestamp / intervalMs) * intervalMs
            if (!grouped.has(groupKey)) {
                grouped.set(groupKey, [])
            }
            grouped.get(groupKey)!.push(item)
        })

        // 聚合每组数据
        const result: T[] = []
        grouped.forEach((group, timestamp) => {
            if (group.length === 1) {
                result.push({ ...group[0], timestamp: new Date(timestamp) })
            } else {
                const aggregated = this.aggregateGroup(group, valueField)
                result.push({
                    ...group[0],
                    ...aggregated,
                    timestamp: new Date(timestamp)
                } as T)
            }
        })

        return result.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
    }

    /**
     * 聚合数据组
     */
    private static aggregateGroup<T extends TimeSeriesDataPoint>(group: T[], valueField: keyof T): Partial<T> {
        const values = group.map(item => Number(item[valueField])).filter(v => !isNaN(v))

        if (!values.length) return {}

        const open = values[0]
        const close = values[values.length - 1]
        const high = Math.max(...values)
        const low = Math.min(...values)
        const volume = group.reduce((sum, item) => sum + (Number(item.volume) || 0), 0)

        return {
            [valueField]: close,
            open,
            high,
            low,
            volume
        } as unknown as Partial<T>
    }

    /**
     * 获取时间间隔的毫秒数
     */
    private static getIntervalMs(interval: string): number {
        const intervals: Record<string, number> = {
            '1m': 60 * 1000,
            '5m': 5 * 60 * 1000,
            '15m': 15 * 60 * 1000,
            '30m': 30 * 60 * 1000,
            '1h': 60 * 60 * 1000,
            '1d': 24 * 60 * 60 * 1000
        }
        return intervals[interval] || 60 * 1000
    }

    /**
     * 计算移动平均
     */
    static calculateMovingAverage(data: number[], period: number): number[] {
        const result: number[] = []

        for (let i = 0; i < data.length; i++) {
            if (i < period - 1) {
                result.push(NaN)
            } else {
                const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0)
                result.push(sum / period)
            }
        }

        return result
    }

    /**
     * 计算百分位数
     */
    static calculatePercentile(data: number[], percentile: number): number {
        if (!data.length) return 0

        const sorted = [...data].sort((a, b) => a - b)
        const index = (percentile / 100) * (sorted.length - 1)
        const lower = Math.floor(index)
        const upper = Math.ceil(index)

        if (lower === upper) {
            return sorted[lower]
        }

        return sorted[lower] + (sorted[upper] - sorted[lower]) * (index - lower)
    }
}

/**
 * 数据验证工具
 */
export class DataValidator {
    /**
     * 验证时间序列数据
     */
    static validateTimeSeriesData(data: TimeSeriesDataPoint[]): {
        isValid: boolean
        errors: string[]
        warnings: string[]
    } {
        const errors: string[] = []
        const warnings: string[] = []

        if (!Array.isArray(data)) {
            errors.push('数据必须是数组格式')
            return { isValid: false, errors, warnings }
        }

        if (data.length === 0) {
            warnings.push('数据为空')
            return { isValid: true, errors, warnings }
        }

        // 检查必需字段
        const requiredFields = ['timestamp', 'value']
        data.forEach((item, index) => {
            requiredFields.forEach(field => {
                if (!(field in item)) {
                    errors.push(`第${index + 1}个数据项缺少必需字段: ${field}`)
                }
            })

            // 验证时间戳
            if (item.timestamp) {
                const timestamp = new Date(item.timestamp)
                if (isNaN(timestamp.getTime())) {
                    errors.push(`第${index + 1}个数据项的时间戳格式无效`)
                }
            }

            // 验证数值
            if (typeof item.value !== 'number' || isNaN(item.value)) {
                errors.push(`第${index + 1}个数据项的数值无效`)
            }
        })

        // 检查时间顺序
        const timestamps = data.map(item => new Date(item.timestamp).getTime()).filter(t => !isNaN(t))
        for (let i = 1; i < timestamps.length; i++) {
            if (timestamps[i] < timestamps[i - 1]) {
                warnings.push('数据时间戳不是严格递增顺序')
                break
            }
        }

        return {
            isValid: errors.length === 0,
            errors,
            warnings
        }
    }

    /**
     * 验证桑基图数据
     */
    static validateSankeyData(
        nodes: SankeyNode[],
        links: SankeyLink[]
    ): {
        isValid: boolean
        errors: string[]
        warnings: string[]
    } {
        const errors: string[] = []
        const warnings: string[] = []

        // 验证节点
        if (!Array.isArray(nodes)) {
            errors.push('节点数据必须是数组格式')
        } else {
            nodes.forEach((node, index) => {
                if (!node.name) {
                    errors.push(`第${index + 1}个节点缺少名称`)
                }
            })
        }

        // 验证连接
        if (!Array.isArray(links)) {
            errors.push('连接数据必须是数组格式')
        } else {
            const nodeNames = new Set(nodes.map(n => n.name))

            links.forEach((link, index) => {
                if (!link.source || !link.target) {
                    errors.push(`第${index + 1}个连接缺少源或目标节点`)
                } else {
                    if (!nodeNames.has(link.source)) {
                        errors.push(`第${index + 1}个连接的源节点"${link.source}"不存在`)
                    }
                    if (!nodeNames.has(link.target)) {
                        errors.push(`第${index + 1}个连接的目标节点"${link.target}"不存在`)
                    }
                }

                if (typeof link.value !== 'number' || link.value < 0) {
                    errors.push(`第${index + 1}个连接的数值无效`)
                }
            })
        }

        return {
            isValid: errors.length === 0,
            errors,
            warnings
        }
    }
}

// ================ 图表配置工具 ================

/**
 * 图表配置生成器
 */
export class ChartConfigGenerator {
    /**
     * 生成通用图表配置
     */
    static getBaseConfig(title?: string, theme: 'default' | 'dark' | 'compact' | 'mobile' = 'default'): EChartsOption {
        const isDark = theme === 'dark'
        const isCompact = theme === 'compact'
        const isMobile = theme === 'mobile'

        return {
            title: title
                ? {
                      text: title,
                      left: 'center',
                      textStyle: {
                          color: isDark ? '#ffffff' : '#333333',
                          fontSize: isCompact ? 14 : 16,
                          fontWeight: 'normal'
                      }
                  }
                : undefined,

            grid: {
                left: isMobile ? '5%' : '8%',
                right: isMobile ? '5%' : '8%',
                top: title ? (isCompact ? '15%' : '18%') : isCompact ? '8%' : '12%',
                bottom: isCompact ? '8%' : '12%',
                containLabel: true
            },

            tooltip: {
                trigger: 'axis',
                backgroundColor: isDark ? 'rgba(0,0,0,0.8)' : 'rgba(255,255,255,0.9)',
                borderColor: FINANCIAL_COLORS.neutral,
                textStyle: {
                    color: isDark ? '#ffffff' : '#333333'
                }
            },

            legend: {
                top: '8%',
                textStyle: {
                    color: isDark ? '#cccccc' : '#666666',
                    fontSize: isCompact ? 12 : 14
                }
            }
        }
    }

    /**
     * 生成颜色配置
     */
    static getColorScheme(type: 'financial' | 'heatmap' | 'categorical' = 'financial'): string[] {
        switch (type) {
            case 'financial':
                return [
                    FINANCIAL_COLORS.bullish,
                    FINANCIAL_COLORS.bearish,
                    FINANCIAL_COLORS.neutral,
                    FINANCIAL_COLORS.volume,
                    FINANCIAL_COLORS.average
                ]
            case 'heatmap':
                return GRADIENTS.heatmap
            case 'categorical':
                return ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4']
            default:
                return GRADIENTS.bullish
        }
    }

    /**
     * 生成响应式配置
     */
    static getResponsiveConfig(): {
        baseOption: EChartsOption
        media: Array<{
            query: { maxWidth?: number; minWidth?: number }
            option: EChartsOption
        }>
    } {
        return {
            baseOption: {
                // 桌面端配置
            },
            media: [
                {
                    query: { maxWidth: 768 },
                    option: {
                        // 移动端配置
                        grid: { left: '5%', right: '5%', top: '20%', bottom: '15%' },
                        title: { fontSize: 14 },
                        legend: { top: '12%' }
                    }
                }
            ]
        }
    }
}
