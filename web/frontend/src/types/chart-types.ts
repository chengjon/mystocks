/**
 * TypeScript Type Definitions for MyStocks Data Visualization System
 *
 * Comprehensive type definitions for chart components, utilities, and data structures
 */

import type { EChartsOption } from 'echarts'

// ================ 基础数据类型 ================

/**
 * 基础数据点接口
 */
export interface DataPoint {
    /** 数据值 */
    value: number
    /** 数据名称或标签 */
    name?: string
    /** 时间戳 */
    timestamp?: number | string | Date
    /** 额外属性 */
    [key: string]: any
}

/**
 * 风险分解数据点
 */
export interface RiskBreakdown {
    /** 风险来源标签 */
    label: string
    /** 风险值 */
    value: number
    /** 百分比 */
    percentage: number
}

/**
 * 时间序列数据点
 */
export interface TimeSeriesPoint extends DataPoint {
    /** 时间戳（必需） */
    timestamp: number | string | Date
    /** 开盘价 */
    open?: number
    /** 最高价 */
    high?: number
    /** 最低价 */
    low?: number
    /** 收盘价 */
    close?: number
    /** 成交量 */
    volume?: number
    /** 成交额 */
    amount?: number
}

// ================ 图表配置类型 ================

/**
 * 图表主题配置
 */
export interface ChartTheme {
    /** 颜色方案 */
    colors: string[]
    /** 背景色 */
    backgroundColor?: string
    /** 文本颜色 */
    textColor?: string
    /** 网格线颜色 */
    gridColor?: string
    /** 边框颜色 */
    borderColor?: string
    /** 阴影配置 */
    shadow?: {
        color: string
        blur: number
        offsetX: number
        offsetY: number
    }
}

/**
 * 图表基础配置
 */
export interface BaseChartConfig {
    /** 图表宽度 */
    width?: string | number
    /** 图表高度 */
    height?: string | number
    /** 主题配置 */
    theme?: 'default' | 'dark' | 'compact' | 'mobile' | ChartTheme
    /** 标题 */
    title?: string
    /** 是否显示加载状态 */
    loading?: boolean
    /** 是否可缩放 */
    zoomable?: boolean
    /** 是否可拖拽 */
    draggable?: boolean
    /** 动画配置 */
    animation?: {
        duration?: number
        easing?: string
        delay?: number
    }
}

// ================ 桑基图类型 ================

/**
 * 桑基图节点
 */
export interface SankeyNode {
    /** 节点名称 */
    name: string
    /** 节点值（可选，用于计算节点大小） */
    value?: number
    /** 节点样式 */
    itemStyle?: {
        color?: string
        borderColor?: string
        borderWidth?: number
    }
    /** 节点标签 */
    label?: {
        show?: boolean
        position?: 'left' | 'right' | 'top' | 'bottom' | 'inside'
        color?: string
        fontSize?: number
    }
    /** 额外属性 */
    [key: string]: any
}

/**
 * 桑基图连接
 */
export interface SankeyLink {
    /** 源节点名称 */
    source: string
    /** 目标节点名称 */
    target: string
    /** 连接值 */
    value: number
    /** 连接样式 */
    lineStyle?: {
        color?: string
        opacity?: number
        curveness?: number
    }
    /** 连接标签 */
    label?: {
        show?: boolean
        position?: 'left' | 'right' | 'top' | 'bottom' | 'inside'
        formatter?: string | Function
    }
    /** 额外属性 */
    [key: string]: any
}

/**
 * 桑基图数据
 */
export interface SankeyData {
    /** 节点列表 */
    nodes: SankeyNode[]
    /** 连接列表 */
    links: SankeyLink[]
}

/**
 * 桑基图配置
 */
export interface SankeyChartConfig extends BaseChartConfig {
    /** 桑基图数据 */
    data: SankeyData
    /** 节点宽度 */
    nodeWidth?: number
    /** 节点间距 */
    nodeGap?: number
    /** 布局方向 */
    orient?: 'horizontal' | 'vertical'
    /** 标签位置 */
    labelPosition?: 'left' | 'right' | 'top' | 'bottom'
    /** 是否可拖拽 */
    draggable?: boolean
}

// ================ 树状图类型 ================

/**
 * 树节点
 */
export interface TreeNode {
    /** 节点名称 */
    name: string
    /** 节点值 */
    value?: number
    /** 子节点 */
    children?: TreeNode[]
    /** 节点样式 */
    itemStyle?: {
        color?: string
        borderColor?: string
        borderWidth?: number
    }
    /** 节点标签 */
    label?: {
        show?: boolean
        position?: 'left' | 'right' | 'top' | 'bottom' | 'inside'
        color?: string
        fontSize?: number
    }
    /** 折叠状态 */
    collapsed?: boolean
    /** 额外属性 */
    [key: string]: any
}

/**
 * 树状图配置
 */
export interface TreeChartConfig extends BaseChartConfig {
    /** 树数据 */
    data: TreeNode
    /** 布局方式 */
    layout?: 'orthogonal' | 'radial'
    /** 方向 */
    orient?: 'horizontal' | 'vertical' | 'LR' | 'RL' | 'TB' | 'BT'
    /** 是否展开所有节点 */
    expandAndCollapse?: boolean
    /** 初始展开层级 */
    initialTreeDepth?: number
    /** 节点间距 */
    nodeGap?: number
    /** 层级间距 */
    levelGap?: number
}

// ================ 关系图类型 ================

/**
 * 关系图节点
 */
export interface RelationNode {
    /** 节点ID */
    id: string
    /** 节点名称 */
    name: string
    /** 节点大小 */
    symbolSize?: number
    /** 节点形状 */
    symbol?: string
    /** 分类索引 */
    category?: number
    /** 节点样式 */
    itemStyle?: {
        color?: string
        borderColor?: string
        borderWidth?: number
    }
    /** 节点标签 */
    label?: {
        show?: boolean
        position?: 'left' | 'right' | 'top' | 'bottom' | 'inside'
        color?: string
        fontSize?: number
    }
    /** 额外属性 */
    [key: string]: any
}

/**
 * 关系图连接
 */
export interface RelationLink {
    /** 源节点ID */
    source: string
    /** 目标节点ID */
    target: string
    /** 连接值 */
    value?: number
    /** 连接样式 */
    lineStyle?: {
        color?: string
        width?: number
        opacity?: number
        curveness?: number
    }
    /** 连接标签 */
    label?: {
        show?: boolean
        position?: 'left' | 'right' | 'top' | 'bottom' | 'inside'
        formatter?: string | Function
    }
    /** 额外属性 */
    [key: string]: any
}

/**
 * 关系图分类
 */
export interface RelationCategory {
    /** 分类名称 */
    name: string
    /** 分类样式 */
    itemStyle?: {
        color?: string
    }
    /** 分类标签 */
    label?: {
        show?: boolean
        position?: 'left' | 'right' | 'top' | 'bottom' | 'inside'
        color?: string
    }
}

/**
 * 关系图配置
 */
export interface RelationChartConfig extends BaseChartConfig {
    /** 节点列表 */
    nodes: RelationNode[]
    /** 连接列表 */
    links: RelationLink[]
    /** 分类列表 */
    categories?: RelationCategory[]
    /** 布局方式 */
    layout?: 'force' | 'circular'
    /** 是否可拖拽 */
    draggable?: boolean
    /** 力导向布局配置 */
    force?: {
        repulsion?: number
        gravity?: number
        edgeLength?: number
        layoutAnimation?: boolean
    }
    /** 环形布局配置 */
    circular?: {
        rotateLabel?: boolean
    }
}

// ================ 热力图类型 ================

/**
 * 热力图数据点
 */
export interface HeatmapDataPoint {
    /** X轴值 */
    x: number | string
    /** Y轴值 */
    y: number | string
    /** 数据值 */
    value: number
    /** 样式配置 */
    itemStyle?: {
        color?: string
        opacity?: number
    }
    /** 标签配置 */
    label?: {
        show?: boolean
        formatter?: string | Function
    }
    /** 额外属性 */
    [key: string]: any
}

/**
 * 热力图配置
 */
export interface AdvancedHeatmapConfig extends BaseChartConfig {
    /** 热力图数据 */
    data: number[][]
    /** X轴标签 */
    xAxis: string[]
    /** Y轴标签 */
    yAxis: string[]
    /** 颜色方案 */
    colorScheme?: 'financial' | 'heatmap' | 'categorical' | string[]
    /** 是否显示数值 */
    showValues?: boolean
    /** 值格式化函数 */
    valueFormatter?: (value: number) => string
    /** 数值显示位置 */
    valuePosition?: 'inside' | 'top' | 'bottom' | 'left' | 'right'
    /** 是否可点击 */
    clickable?: boolean
    /** 统计信息 */
    showStats?: boolean
    /** 统计信息位置 */
    statsPosition?: 'top' | 'bottom' | 'left' | 'right'
}

// ================ 事件类型 ================

/**
 * 图表事件基础接口
 */
export interface ChartEvent {
    /** 事件类型 */
    type: string
    /** 事件数据 */
    data: any
    /** 事件时间戳 */
    timestamp: number
    /** 图表实例 */
    chartInstance?: any
}

/**
 * 桑基图事件
 */
export interface SankeyEvent extends ChartEvent {
    /** 节点或连接数据 */
    node?: SankeyNode
    link?: SankeyLink
}

/**
 * 树状图事件
 */
export interface TreeEvent extends ChartEvent {
    /** 树节点数据 */
    node: TreeNode
    /** 树结构数据 */
    tree: TreeNode
}

/**
 * 关系图事件
 */
export interface RelationEvent extends ChartEvent {
    /** 节点数据 */
    node?: RelationNode
    /** 连接数据 */
    link?: RelationLink
}

/**
 * 热力图事件
 */
export interface HeatmapEvent extends ChartEvent {
    /** X轴标签 */
    xLabel: string
    /** Y轴标签 */
    yLabel: string
    /** 数据值 */
    value: number
    /** 行索引 */
    rowIndex: number
    /** 列索引 */
    colIndex: number
}

// ================ 工具函数类型 ================

/**
 * 数字格式化选项
 */
export interface NumberFormatOptions {
    /** 小数位数 */
    decimals?: number
    /** 货币符号 */
    currency?: string
    /** 是否使用千分位分隔符 */
    useGrouping?: boolean
    /** 最小整数位数 */
    minimumIntegerDigits?: number
    /** 最大小数位数 */
    maximumFractionDigits?: number
}

/**
 * 时间格式化选项
 */
export interface TimeFormatOptions {
    /** 格式化模式 */
    format?: 'date' | 'time' | 'datetime' | 'relative'
    /** 语言环境 */
    locale?: string
    /** 时区 */
    timeZone?: string
    /** 相对时间基准 */
    relativeTo?: Date
}

/**
 * 数据聚合选项
 */
export interface AggregationOptions {
    /** 时间间隔 */
    interval?: '1m' | '5m' | '15m' | '30m' | '1h' | '1d'
    /** 聚合方法 */
    method?: 'sum' | 'avg' | 'max' | 'min' | 'count'
    /** 分组字段 */
    groupBy?: string[]
    /** 过滤条件 */
    filter?: (item: any) => boolean
}

/**
 * 数据验证结果
 */
export interface ValidationResult {
    /** 是否有效 */
    isValid: boolean
    /** 错误信息 */
    errors: string[]
    /** 警告信息 */
    warnings: string[]
    /** 验证统计 */
    stats?: {
        totalItems: number
        validItems: number
        invalidItems: number
    }
}

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
    customSampler?: (data: any[], maxPoints: number) => any[]
}

// ================ 类型导出说明 ================
// 所有类型已在定义时使用 export 关键字导出
// 无需重复导出
