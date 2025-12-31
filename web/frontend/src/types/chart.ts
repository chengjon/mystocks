
/**
 * Chart TypeScript Type Definitions
 * K线图表类型定义
 */

import type { KLineData, IndicatorCreate } from 'klinecharts'
import type { IndicatorSpec, IndicatorResult, OHLCVData } from './indicator'

/**
 * K线数据点
 * 兼容 klinecharts 的 KLineData 接口
 */
export interface CandleData extends KLineData {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
  turnover?: number
}

/**
 * 图表实例引用
 */
export type ChartInstance = ReturnType<typeof import('klinecharts').init>

/**
 * 图表主题
 */
export enum ChartTheme {
  LIGHT = 'light',
  DARK = 'dark'
}

/**
 * 时间范围快捷选项
 */
export enum TimeRangePreset {
  ONE_MONTH = '1M',
  THREE_MONTHS = '3M',
  SIX_MONTHS = '6M',
  ONE_YEAR = '1Y',
  THREE_YEARS = '3Y',
  FIVE_YEARS = '5Y',
  ALL = 'ALL'
}

/**
 * 图表面板类型
 */
export enum ChartPanelType {
  MAIN = 'candle_pane',     // 主图 (K线)
  VOLUME = 'volume_pane',   // 成交量面板
  OSCILLATOR = 'oscillator' // 震荡器面板 (RSI, MACD等)
}

/**
 * 图表面板配置
 */
export interface ChartPanel {
  id: string
  type: ChartPanelType
  height: number | 'auto'
  indicators: IndicatorSpec[]
}

/**
 * 图表配置选项
 */
export interface ChartOptions {
  theme: ChartTheme
  locale: 'zh-CN' | 'en-US'
  timezone: string
  grid: {
    show: boolean
    horizontal: {
      show: boolean
      size: number
      color: string
      style: 'solid' | 'dashed'
    }
    vertical: {
      show: boolean
      size: number
      color: string
      style: 'solid' | 'dashed'
    }
  }
  candle: {
    type: 'candle_solid' | 'candle_stroke' | 'candle_up_stroke' | 'candle_down_stroke' | 'ohlc' | 'area'
    bar: {
      upColor: string
      downColor: string
      noChangeColor: string
    }
  }
  indicator: {
    tooltip: {
      showRule: 'always' | 'follow_cross' | 'none'
      showType: 'standard' | 'rect'
    }
  }
  crosshair: {
    show: boolean
    horizontal: {
      show: boolean
      line: {
        show: boolean
        style: 'solid' | 'dashed'
        color: string
        size: number
      }
      text: {
        show: boolean
        color: string
        size: number
        backgroundColor: string
      }
    }
    vertical: {
      show: boolean
      line: {
        show: boolean
        style: 'solid' | 'dashed'
        color: string
        size: number
      }
      text: {
        show: boolean
        color: string
        size: number
        backgroundColor: string
      }
    }
  }
}

/**
 * 图表数据状态
 */
export interface ChartDataState {
  symbol: string
  symbolName: string
  startDate: string
  endDate: string
  ohlcv: OHLCVData | null
  candles: CandleData[]
  indicators: IndicatorResult[]
  loading: boolean
  error: string | null
}

/**
 * 图表交互状态
 */
export interface ChartInteractionState {
  isZooming: boolean
  isPanning: boolean
  crosshairActive: boolean
  selectedCandle: CandleData | null
}

/**
 * 图表工具栏配置
 */
export interface ChartToolbar {
  timeRange: {
    show: boolean
    presets: TimeRangePreset[]
  }
  theme: {
    show: boolean
  }
  chartType: {
    show: boolean
    types: Array<'candle_solid' | 'candle_stroke' | 'ohlc' | 'area'>
  }
  indicators: {
    show: boolean
  }
  fullscreen: {
    show: boolean
  }
  export: {
    show: boolean
    formats: Array<'png' | 'jpeg' | 'svg' | 'pdf'>
  }
}

/**
 * 图表注解/标记
 */
export interface ChartAnnotation {
  id: string
  type: 'horizontal_line' | 'vertical_line' | 'trend_line' | 'fibonacci' | 'text'
  timestamp?: number
  value?: number
  points?: Array<{ timestamp: number; value: number }>
  style: {
    color: string
    lineWidth: number
    lineStyle: 'solid' | 'dashed'
  }
  text?: string
}

/**
 * 技术图形
 */
export interface ChartShape {
  id: string
  type: 'horizontal_segment' | 'horizontal_ray_line' | 'horizontal_straight_line' |
        'vertical_segment' | 'vertical_ray_line' | 'vertical_straight_line' |
        'straight_line' | 'ray_line' | 'segment' | 'price_line' |
        'fibonacci_line' | 'fibonacci_segment' |
        'parallel_straight_line' | 'price_channel_line'
  points: Array<{ timestamp: number; value: number }>
  style?: {
    color?: string
    lineWidth?: number
    lineStyle?: 'solid' | 'dashed'
  }
}

/**
 * 图表事件
 */
export interface ChartEvent {
  type: 'click' | 'double_click' | 'right_click' | 'mouse_move' | 'zoom' | 'scroll'
  timestamp: number
  x: number
  y: number
  candleData?: CandleData
  indicatorData?: Record<string, number>
}

/**
 * 图表性能指标
 */
export interface ChartPerformanceMetrics {
  renderTime: number      // 渲染耗时 (ms)
  dataPoints: number      // 数据点数量
  indicators: number      // 指标数量
  fps: number             // 帧率
  memoryUsage: number     // 内存占用 (MB)
}

/**
 * 自定义指标样式
 */
export interface CustomIndicatorStyle {
  lines: Array<{
    key: string
    title: string
    color: string
    size: number
    style: 'solid' | 'dashed'
  }>
  circles?: Array<{
    key: string
    color: string
    size: number
  }>
  bars?: Array<{
    key: string
    upColor: string
    downColor: string
  }>
  referenceLinesStyles?: Array<{
    value: number
    color: string
    style: 'solid' | 'dashed'
  }>
}

/**
 * 图表导出选项
 */
export interface ChartExportOptions {
  format: 'png' | 'jpeg' | 'svg' | 'pdf'
  quality?: number          // JPEG 质量 (0-1)
  width?: number            // 导出宽度
  height?: number           // 导出高度
  backgroundColor?: string  // 背景颜色
  includeTooltip?: boolean  // 是否包含工具提示
}

/**
 * 图表缩放/平移状态
 */
export interface ChartViewport {
  startTimestamp: number
  endTimestamp: number
  minValue: number
  maxValue: number
  visibleCandleCount: number
}

/**
 * 技术分析工具状态
 */
export interface TechnicalToolState {
  activeTool: string | null
  drawings: ChartShape[]
  annotations: ChartAnnotation[]
}
