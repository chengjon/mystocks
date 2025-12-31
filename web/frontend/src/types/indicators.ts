/**
 * Technical Indicators Type Definitions
 *
 * 技术指标类型定义，包括：
 * - 指标基础接口 (Indicator)
 * - 指标配置 (IndicatorConfig)
 * - 指标结果 (IndicatorResult)
 * - 各类具体指标类型（MA, MACD, KDJ, RSI, BOLL, 等）
 *
 * @module types/indicators
 */

// ============================================
// 基础类型定义
// ============================================

/**
 * 指标类别枚举
 */
export enum IndicatorCategory {
  /** 趋势类指标 */
  TREND = 'trend',

  /** 动量类指标 */
  MOMENTUM = 'momentum',

  /** 波动率类指标 */
  VOLATILITY = 'volatility',

  /** 成交量类指标 */
  VOLUME = 'volume',

  /** 自定义指标 */
  CUSTOM = 'custom',
}

/**
 * 指标计算周期
 */
export type IndicatorPeriod = '1m' | '5m' | '15m' | '30m' | '1h' | '4h' | '1d' | '1w' | '1M';

/**
 * 指标数据点
 */
export interface IndicatorDataPoint {
  /** 时间戳 */
  timestamp: string;

  /** 数值 */
  value: number;

  /** 可选的额外数据 */
  extra?: Record<string, number | string>;
}

// ============================================
// 指标基础接口
// ============================================

/**
 * 指标基础接口
 */
export interface Indicator {
  /** 指标唯一标识 */
  id: string;

  /** 指标名称 */
  name: string;

  /** 指标显示名称（中文） */
  displayName: string;

  /** 指标类别 */
  category: IndicatorCategory;

  /** 指标描述 */
  description: string;

  /** 指标配置 */
  config: IndicatorConfig;

  /** 指标结果 */
  result: IndicatorResult;

  /** 创建时间 */
  createdAt: string;

  /** 更新时间 */
  updatedAt: string;
}

/**
 * 指标配置接口
 */
export interface IndicatorConfig {
  /** 指标类型 */
  type: string;

  /** 计算周期 */
  period: IndicatorPeriod;

  /** 参数列表 */
  params: IndicatorParam[];

  /** 是否启用 */
  enabled: boolean;

  /** 颜色配置 */
  colors?: IndicatorColors;

  /** 显示选项 */
  displayOptions?: IndicatorDisplayOptions;
}

/**
 * 指标参数
 */
export interface IndicatorParam {
  /** 参数名称 */
  name: string;

  /** 参数值 */
  value: number;

  /** 参数最小值 */
  min?: number;

  /** 参数最大值 */
  max?: number;

  /** 参数步长 */
  step?: number;

  /** 参数描述 */
  description?: string;
}

/**
 * 指标颜色配置
 */
export interface IndicatorColors {
  /** 主线条颜色 */
  lineColor?: string;

  /** 填充颜色 */
  fillColor?: string;

  /** 柱状图颜色 */
  barColor?: string;

  /** 多线条颜色数组 */
  lineColors?: string[];
}

/**
 * 指标显示选项
 */
export interface IndicatorDisplayOptions {
  /** 是否显示在图表上 */
  showOnChart: boolean;

  /** 显示位置 */
  position?: 'main' | 'sub';

  /** Y轴位置 */
  yAxisIndex?: number;

  /** 线条宽度 */
  lineWidth?: number;

  /** 线条样式 */
  lineStyle?: 'solid' | 'dashed' | 'dotted';

  /** 是否填充区域 */
  area?: boolean;
}

/**
 * 指标计算结果接口
 */
export interface IndicatorResult {
  /** 计算状态 */
  status: 'success' | 'error' | 'pending';

  /** 数据点数组 */
  data: IndicatorDataPoint[];

  /** 计算时间 */
  calculatedAt: string;

  /** 错误信息（如果有） */
  error?: string;

  /** 元数据 */
  meta?: IndicatorResultMeta;
}

/**
 * 指标结果元数据
 */
export interface IndicatorResultMeta {
  /** 数据点数量 */
  dataPoints: number;

  /** 起始时间 */
  startTime: string;

  /** 结束时间 */
  endTime: string;

  /** 计算耗时（毫秒） */
  calculationTime: number;

  /** 缓存键 */
  cacheKey?: string;
}

// ============================================
// 具体指标类型
// ============================================

/**
 * 移动平均线（MA）指标
 */
export interface MAIndicator extends Indicator {
  type: 'MA';
  config: MAConfig;
  result: MAResult;
}

/**
 * MA 配置
 */
export interface MAConfig extends IndicatorConfig {
  type: 'MA';
  params: [
    IndicatorParam & { name: 'shortPeriod' }, // 短期周期
    IndicatorParam & { name: 'mediumPeriod' }, // 中期周期
    IndicatorParam & { name: 'longPeriod' }, // 长期周期
  ];
}

/**
 * MA 结果
 */
export interface MAResult extends IndicatorResult {
  data: [
    IndicatorDataPoint & { extra: { ma5: number } },
    IndicatorDataPoint & { extra: { ma10: number } },
    IndicatorDataPoint & { extra: { ma20: number } },
    IndicatorDataPoint & { extra: { ma60: number } },
  ];
}

/**
 * MACD 指标 (不继承 Indicator，避免类型冲突)
 */
export interface MACDIndicator {
  type: 'MACD';
  config: MACDConfig;
  result: MACDResult;
}

/**
 * MACD 配置
 */
export interface MACDConfig extends IndicatorConfig {
  type: 'MACD';
  params: [
    IndicatorParam & { name: 'fastPeriod' }, // 快线周期
    IndicatorParam & { name: 'slowPeriod' }, // 慢线周期
    IndicatorParam & { name: 'signalPeriod' }, // 信号线周期
  ];
}

/**
 * MACD 结果 (不继承 IndicatorResult，避免类型冲突)
 */
export interface MACDResult {
  data: IndicatorDataPoint & {
    extra: {
      dif: number; // 快线
      dea: number; // 慢线
      macd: number; // 柱状图
    };
  }[];
}

/**
 * KDJ 指标 (不继承 Indicator，避免类型冲突)
 */
export interface KDJIndicator {
  type: 'KDJ';
  config: KDJConfig;
  result: KDJResult;
}

/**
 * KDJ 配置
 */
export interface KDJConfig extends IndicatorConfig {
  type: 'KDJ';
  params: [
    IndicatorParam & { name: 'kPeriod' }, // K值周期
    IndicatorParam & { name: 'dPeriod' }, // D值周期
    IndicatorParam & { name: 'jPeriod' }, // J值周期
  ];
}

/**
 * KDJ 结果 (不继承 IndicatorResult，避免类型冲突)
 */
export interface KDJResult {
  data: IndicatorDataPoint & {
    extra: {
      k: number; // K值
      d: number; // D值
      j: number; // J值
    };
  }[];
}

/**
 * RSI 指标 (不继承 Indicator，避免类型冲突)
 */
export interface RSIIndicator {
  type: 'RSI';
  config: RSIConfig;
  result: RSIResult;
}

/**
 * RSI 配置
 */
export interface RSIConfig extends IndicatorConfig {
  type: 'RSI';
  params: [IndicatorParam & { name: 'period' }]; // RSI周期
}

/**
 * RSI 结果 (不继承 IndicatorResult，避免类型冲突)
 */
export interface RSIResult {
  data: IndicatorDataPoint & {
    extra: {
      rsi6: number; // 6日RSI
      rsi12: number; // 12日RSI
      rsi24: number; // 24日RSI
    };
  }[];
}

/**
 * 布林带（BOLL）指标 (不继承 Indicator，避免类型冲突)
 */
export interface BOLLIndicator {
  type: 'BOLL';
  config: BOLLConfig;
  result: BOLLResult;
}

/**
 * BOLL 配置
 */
export interface BOLLConfig extends IndicatorConfig {
  type: 'BOLL';
  params: [
    IndicatorParam & { name: 'period' }, // 周期
    IndicatorParam & { name: 'stdDev' }, // 标准差倍数
  ];
}

/**
 * BOLL 结果 (不继承 IndicatorResult，避免类型冲突)
 */
export interface BOLLResult {
  data: IndicatorDataPoint & {
    extra: {
      upper: number; // 上轨
      middle: number; // 中轨
      lower: number; // 下轨
    };
  }[];
}

// ============================================
// 指标模板类型
// ============================================

/**
 * 指标模板
 */
export interface IndicatorTemplate {
  /** 模板ID */
  id: string;

  /** 模板名称 */
  name: string;

  /** 模板描述 */
  description: string;

  /** 指标列表 */
  indicators: Omit<Indicator, 'id' | 'createdAt' | 'updatedAt'>[];

  /** 是否为系统模板 */
  isSystem: boolean;

  /** 创建者 */
  creator?: string;
}

/**
 * 指标计算请求
 */
export interface IndicatorCalculateRequest {
  /** 股票代码 */
  symbol: string;

  /** 指标配置 */
  config: IndicatorConfig;

  /** 数据起始日期 */
  startDate: string;

  /** 数据结束日期 */
  endDate: string;
}

/**
 * 指标计算响应
 */
export interface IndicatorCalculateResponse {
  /** 请求ID */
  requestId: string;

  /** 计算结果 */
  result: IndicatorResult;

  /** 计算耗时（毫秒） */
  calculationTime: number;
}

// ============================================
// 指标工具函数类型
// ============================================

/**
 * 指标数据格式化器
 */
export type IndicatorDataFormatter<T extends IndicatorResult> = (
  result: T,
) => {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    color?: string;
  }[];
};

/**
 * 指标验证器
 */
export type IndicatorValidator = (config: IndicatorConfig) => {
  valid: boolean;
  errors?: string[];
};

/**
 * 指标计算器函数类型
 */
export type IndicatorCalculator = (
  symbol: string,
  config: IndicatorConfig,
  startDate: string,
  endDate: string,
) => Promise<IndicatorResult>;
