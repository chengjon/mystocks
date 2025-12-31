/**
 * ECharts Type Standardization
 * 统一 ECharts 类型定义，解决 EChartOption vs EChartsOption 冲突
 */

import type { ECharts, EChartsOption as OriginalEChartsOption } from 'echarts'

/**
 * 统一的 ECharts 选项类型
 */
export type EChartsOption = OriginalEChartsOption

/**
 * 别名，用于兼容部分旧代码或简化命名
 */
export type ChartOption = EChartsOption

/**
 * 导出 ECharts 实例类型
 */
export type EChartsInstance = ECharts

export type { ECharts }
