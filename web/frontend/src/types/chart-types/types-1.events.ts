import type { RelationLink, RelationNode, SankeyLink, SankeyNode, TreeNode } from './types-1';

/**
 * 图表事件基础接口
 */
export interface ChartEvent {
    /** 事件类型 */
    type: string;
    /** 事件数据 */
    data: unknown;
    /** 事件时间戳 */
    timestamp: number;
    /** 图表实例 */
    chartInstance?: unknown;
}

/**
 * 桑基图事件
 */
export interface SankeyEvent extends ChartEvent {
    /** 节点或连接数据 */
    node?: SankeyNode;
    link?: SankeyLink;
}

/**
 * 树状图事件
 */
export interface TreeEvent extends ChartEvent {
    /** 树节点数据 */
    node: TreeNode;
    /** 树结构数据 */
    tree: TreeNode;
}

/**
 * 关系图事件
 */
export interface RelationEvent extends ChartEvent {
    /** 节点数据 */
    node?: RelationNode;
    /** 连接数据 */
    link?: RelationLink;
}

/**
 * 热力图事件
 */
export interface HeatmapEvent extends ChartEvent {
    /** X轴标签 */
    xLabel: string;
    /** Y轴标签 */
    yLabel: string;
    /** 数据值 */
    value: number;
    /** 行索引 */
    rowIndex: number;
    /** 列索引 */
    colIndex: number;
}

/**
 * 数字格式化选项
 */
export interface NumberFormatOptions {
    /** 小数位数 */
    decimals?: number;
    /** 货币符号 */
    currency?: string;
    /** 是否使用千分位分隔符 */
    useGrouping?: boolean;
    /** 最小整数位数 */
    minimumIntegerDigits?: number;
    /** 最大小数位数 */
    maximumFractionDigits?: number;
}

/**
 * 时间格式化选项
 */
export interface TimeFormatOptions {
    /** 格式化模式 */
    format?: 'date' | 'time' | 'datetime' | 'relative';
    /** 语言环境 */
    locale?: string;
    /** 时区 */
    timeZone?: string;
    /** 相对时间基准 */
    relativeTo?: Date;
}

/**
 * 数据聚合选项
 */
export interface AggregationOptions {
    /** 时间间隔 */
    interval?: '1m' | '5m' | '15m' | '30m' | '1h' | '1d';
    /** 聚合方法 */
    method?: 'sum' | 'avg' | 'max' | 'min' | 'count';
    /** 分组字段 */
    groupBy?: string[];
    /** 过滤条件 */
    filter?: (item: unknown) => boolean;
}

/**
 * 数据验证结果
 */
export interface ValidationResult {
    /** 是否有效 */
    isValid: boolean;
    /** 错误信息 */
    errors: string[];
    /** 警告信息 */
    warnings: string[];
    /** 验证统计 */
    stats?: {
        totalItems: number;
        validItems: number;
        invalidItems: number;
    };
}
