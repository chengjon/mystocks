/**
 * TypeScript Type Definitions for MyStocks Data Visualization System
 *
 * Comprehensive type definitions for chart components, utilities, and data structures
 */

import type { EChartsOption } from 'echarts'

/**
 * 数据采样配置
 */
export interface SamplingConfig {
    /** 最大点数 */
    maxPoints: number
    /** 采样策略 */
    strategy: 'lttb' | 'minmax' | 'average' | 'random'
    /** 是否保留极值 */
    preserveExtremes?: boolean
    /** 自定义采样函数 */
    customSampler?: (data: unknown[], maxPoints: number) => unknown[]
}

