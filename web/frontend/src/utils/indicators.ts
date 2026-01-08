
/**
 * Technical Indicators Utility
 *
 * Wrapper functions for technicalindicators npm package
 * Provides custom indicator calculations for A股 market
 */

import {
  SMA,
  EMA,
  MACD,
  RSI,
  Stochastic,
  BollingerBands,
  ATR,
  // AT 不存在于 technicalindicators v3.1.0，已移除
  WMA
} from 'technicalindicators'

/**
 * K线数据点接口
 */
export interface KLineDataPoint {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

/**
 * 移动平均线 (MA)
 */
export function calculateMA(
  data: KLineDataPoint[],
  period: number
): number[] {
  const closePrices = data.map(d => d.close)
  const ma = SMA.calculate({ period, values: closePrices })
  return ma
}

/**
 * 指数移动平均线 (EMA)
 */
export function calculateEMA(
  data: KLineDataPoint[],
  period: number
): number[] {
  const closePrices = data.map(d => d.close)
  const ema = EMA.calculate({ period, values: closePrices })
  return ema
}

/**
 * 成交量移动平均线
 */
export function calculateVOLUME_MA(
  data: KLineDataPoint[],
  period: number
): number[] {
  const volumes = data.map(d => d.volume)
  const ma = SMA.calculate({ period, values: volumes })
  return ma
}

/**
 * MACD 指标
 */
export function calculateMACD(data: KLineDataPoint[]): {
  macd: number[]
  signal: number[]
  histogram: number[]
} {
  // 数据验证：确保有足够的数据点
  if (data.length < 26) {
    return {
      macd: [],
      signal: [],
      histogram: []
    }
  }

  // 验证数据有效性
  const isValidData = data.every(d =>
    d.close > 0 &&
    isFinite(d.close) &&
    !isNaN(d.close)
  )

  if (!isValidData) {
    return {
      macd: [],
      signal: [],
      histogram: []
    }
  }

  const closePrices = data.map(d => d.close)
  const macdInput = {
    values: closePrices,
    fastPeriod: 12,
    slowPeriod: 26,
    signalPeriod: 9,
    SimpleMAOscillator: false,
    SimpleMASignal: false,  // v3.1.0 requires this field
    StandardDeviation: 1,
    MovingAverageType: 'SMA' as const
  }

  try {
    const macdData = MACD.calculate(macdInput as any)

    // ✅ 修复：使用类型断言确保返回number[]类型
    // 替换无效值而非过滤，保持长度一致
    const macd = macdData.map(d => isFinite(d.MACD) ? d.MACD : 0) as number[]
    const signal = macdData.map(d => isFinite(d.signal) ? d.signal : 0) as number[]
    const histogram = macdData.map(d => isFinite(d.histogram) ? d.histogram : 0) as number[]

    return { macd, signal, histogram }
  } catch (error) {
    console.error('MACD calculation error:', error)
    return {
      macd: [],
      signal: [],
      histogram: []
    }
  }
}

/**
 * RSI 相对强弱指标
 */
export function calculateRSI(
  data: KLineDataPoint[],
  period: number = 14
): number[] {
  const closePrices = data.map(d => d.close)
  const rsi = RSI.calculate({ period, values: closePrices })
  return rsi
}

/**
 * KDJ 随机指标
 */
export function calculateKDJ(
  data: KLineDataPoint[],
  kPeriod: number = 9,
  dPeriod: number = 3,
  jPeriod: number = 3
): {
  k: number[]
  d: number[]
  j: number[]
} {
  const highPrices = data.map(d => d.high)
  const lowPrices = data.map(d => d.low)
  const closePrices = data.map(d => d.close)

  // 使用正确的 Stochastic 参数格式
  const stochInput = {
    high: highPrices,
    low: lowPrices,
    close: closePrices,
    period: kPeriod,
    signalPeriod: dPeriod
  }

  const stochData = Stochastic.calculate(stochInput)

  // 同步过滤k和d值，确保长度一致
  const k: number[] = []
  const d: number[] = []

  for (const item of stochData) {
    const kVal = item.k
    const dVal = item.d
    // 只有当k和d都是有效数字时才添加
    if (typeof kVal === 'number' && !isNaN(kVal) && isFinite(kVal) &&
        typeof dVal === 'number' && !isNaN(dVal) && isFinite(dVal)) {
      k.push(kVal)
      d.push(dVal)
    }
  }

  // Calculate J = 3K - 2D
  const j: number[] = k.map((kVal, i) => {
    const dVal = d[i]
    return 3 * kVal - 2 * dVal
  })

  return { k, d, j }
}

/**
 * 布林带 (BOLL)
 */
export function calculateBOLL(
  data: KLineDataPoint[],
  period: number = 20,
  stdDev: number = 2
): {
  upper: number[]
  middle: number[]
  lower: number[]
} {
  const closePrices = data.map(d => d.close)

  const bollInput = {
    period,
    values: closePrices,
    stdDev  // v3.1.0 uses stdDev instead of stdDevUp/stdDevDown
  }

  const bollData = BollingerBands.calculate(bollInput)

  // 确保返回数据长度与输入一致，前面填充 null
  const padding = data.length - bollData.length

  return {
    upper: Array(padding).fill(null).concat(bollData.map(d => d.upper)),
    middle: Array(padding).fill(null).concat(bollData.map(d => d.middle)),
    lower: Array(padding).fill(null).concat(bollData.map(d => d.lower))
  }
}

/**
 * 布林带别名（为了兼容测试）
 */
export const calculateBollingerBands = calculateBOLL

/**
 * 真实波幅 (ATR)
 */
export function calculateATR(
  data: KLineDataPoint[],
  period: number = 14
): number[] {
  const atrInput = {
    high: data.map(d => d.high),
    low: data.map(d => d.low),
    close: data.map(d => d.close),
    period
  }

  return ATR.calculate(atrInput)
}

/**
 * 成交量加权移动平均线 (VWMA)
 * 自定义实现 - technicalindicators v3.1.0 不包含此指标
 */
export function calculateVWMA(
  data: KLineDataPoint[],
  period: number
): number[] {
  const result: number[] = []

  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(0)
      continue
    }

    let sumPriceVolume = 0
    let sumVolume = 0

    for (let j = i - period + 1; j <= i; j++) {
      sumPriceVolume += data[j].close * data[j].volume
      sumVolume += data[j].volume
    }

    const vwma = sumVolume === 0 ? 0 : sumPriceVolume / sumVolume
    result.push(vwma)
  }

  return result
}

/**
 * 加权移动平均线 (WMA)
 */
export function calculateWMA(
  data: KLineDataPoint[],
  period: number
): number[] {
  const closePrices = data.map(d => d.close)
  return WMA.calculate({ period, values: closePrices })
}

/**
 * 为klinecharts格式化指标数据
 * 填充前面NaN值以确保数据长度一致
 */
export function formatIndicatorData(
  indicator: number[],
  dataLength: number
): (number | null)[] {
  const result: (number | null)[] = []
  const padding = dataLength - indicator.length

  // 前面填充null
  for (let i = 0; i < padding; i++) {
    result.push(null)
  }

  // 添加指标值
  for (let i = 0; i < indicator.length; i++) {
    result.push(indicator[i])
  }

  return result
}
