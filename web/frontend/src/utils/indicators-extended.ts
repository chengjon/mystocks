// @ts-nocheck

/**
 * Extended Technical Indicators Utility
 *
 * Extended wrapper for technicalindicators npm package
 * Provides 70+ technical indicators for A股 market
 */

import {
  SMA,
  EMA,
  MACD,
  RSI,
  Stochastic,
  BollingerBands,
  ATR,
  WMA,
  ADL,
  ADX,
  AwesomeOscillator,
  CCI,
  MFI,
  // MOM 已移除 - technicalindicators v3.1.0 不存在，使用 ROC 替代
  OBV,
  PSAR,
  ROC,
  StochasticRSI,
  TRIX,
  VWAP,
  WilliamsR,
  KST,
  ForceIndex
  // VWMA 已移除 - technicalindicators v3.1.0 不存在，使用自定义实现
} from 'technicalindicators'

// Re-export basic types and functions from indicators.ts
export * from './indicators'

/**
 * K线数据点接口 (扩展)
 */
export interface ExtendedKLineDataPoint {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

// ============ TREND INDICATORS (15个) ============

/**
 * 累积/派发线 (A/D Line)
 */
export function calculateADL(data: ExtendedKLineDataPoint[]): number[] {
  const adlInput = {
    high: data.map(d => d.high),
    low: data.map(d => d.low),
    close: data.map(d => d.close),
    volume: data.map(d => d.volume)
  }
  return ADL.calculate(adlInput)
}

/**
 * 平均趋向指数 (ADX)
 */
export function calculateADX(
  data: ExtendedKLineDataPoint[],
  period: number = 14
): number[] {
  const adxInput = {
    high: data.map(d => d.high),
    low: data.map(d => d.low),
    close: data.map(d => d.close),
    period
  }
  const result = ADX.calculate(adxInput)
  return result.map(r => r.adx)
}

/**
 * 双指数移动平均线 (DEMA)
 * 简化实现: 2*EMA - EMA(EMA)
 */
export function calculateDEMA(
  data: ExtendedKLineDataPoint[],
  period: number = 20
): number[] {
  const closePrices = data.map(d => d.close)
  const ema1 = EMA.calculate({ period, values: closePrices })
  const ema2 = EMA.calculate({ period, values: ema1 })

  return ema1.map((e1, i) => 2 * e1 - (ema2[i] || e1))
}

/**
 * 指数移动平均线 (EMA)
 */
export function calculateEMA(
  data: ExtendedKLineDataPoint[],
  period: number = 20
): number[] {
  const closePrices = data.map(d => d.close)
  return EMA.calculate({ period, values: closePrices })
}

/**
 * 三指数移动平均线 (TEMA)
 * 简化实现: 3*EMA - 3*EMA(EMA) + EMA(EMA(EMA))
 */
export function calculateTEMA(
  data: ExtendedKLineDataPoint[],
  period: number = 20
): number[] {
  const closePrices = data.map(d => d.close)
  const ema1 = EMA.calculate({ period, values: closePrices })
  const ema2 = EMA.calculate({ period, values: ema1 })
  const ema3 = EMA.calculate({ period, values: ema2 })

  return ema1.map((e1, i) => {
    const e2 = ema2[i] || e1
    const e3 = ema3[i] || e2
    return 3 * e1 - 3 * e2 + e3
  })
}

/**
 * 三角移动平均线 (TRIMA)
 * 简化实现: SMA of SMA
 */
export function calculateTRIMA(
  data: ExtendedKLineDataPoint[],
  period: number = 18
): number[] {
  const closePrices = data.map(d => d.close)
  const halfPeriod = Math.ceil(period / 2)
  const sma1 = SMA.calculate({ period: halfPeriod, values: closePrices })
  return SMA.calculate({ period: halfPeriod, values: sma1 })
}

/**
 * 加权移动平均线 (WMA)
 */
export function calculateWMA(
  data: ExtendedKLineDataPoint[],
  period: number = 20
): number[] {
  const closePrices = data.map(d => d.close)
  return WMA.calculate({ period, values: closePrices })
}

/**
 * 简单移动平均线 (SMA)
 */
export function calculateSMA(
  data: ExtendedKLineDataPoint[],
  period: number = 20
): number[] {
  const closePrices = data.map(d => d.close)
  return SMA.calculate({ period, values: closePrices })
}

/**
 * 成交量加权平均价 (VWAP)
 */
export function calculateVWAP(data: ExtendedKLineDataPoint[]): number[] {
  const vwapInput = {
    high: data.map(d => d.high),
    low: data.map(d => d.low),
    close: data.map(d => d.close),
    volume: data.map(d => d.volume)
  }
  return VWAP.calculate(vwapInput)
}

/**
 * 成交量加权移动平均线 (VWMA)
 * 自定义实现 - technicalindicators v3.1.0 不包含此指标
 */
export function calculateVWMA(
  data: ExtendedKLineDataPoint[],
  period: number = 20
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
 * 抛物线转向 (PSAR)
 */
export function calculatePSAR(
  data: ExtendedKLineDataPoint[],
  step: number = 0.02,
  max: number = 0.2
): number[] {
  const psarInput = {
    high: data.map(d => d.high),
    low: data.map(d => d.low),
    step,
    max
  }
  return PSAR.calculate(psarInput)
}

/**
 * 考夫曼自适应移动平均线 (KAMA)
 * 简化实现
 */
export function calculateKAMA(
  data: ExtendedKLineDataPoint[],
  period: number = 20,
  fastPeriod: number = 2,
  slowPeriod: number = 30
): number[] {
  const closePrices = data.map(d => d.close)
  const result: number[] = []
  let kama = closePrices[0]

  for (let i = 0; i < closePrices.length; i++) {
    if (i < period) {
      result.push(kama)
      continue
    }

    const change = Math.abs(closePrices[i] - closePrices[i - period])
    let volatility = 0
    for (let j = i - period + 1; j <= i; j++) {
      volatility += Math.abs(closePrices[j] - closePrices[j - 1])
    }

    const er = volatility === 0 ? 0 : change / volatility
    const sc = Math.pow(er * (2 / (fastPeriod + 1) - 2 / (slowPeriod + 1)) + 2 / (slowPeriod + 1), 2)
    kama = kama + sc * (closePrices[i] - kama)
    result.push(kama)
  }

  return result
}

/**
 * 赫尔移动平均线 (HMA)
 * 简化实现
 */
export function calculateHMA(
  data: ExtendedKLineDataPoint[],
  period: number = 20
): number[] {
  const closePrices = data.map(d => d.close)
  const halfPeriod = Math.floor(period / 2)
  const sqrtPeriod = Math.floor(Math.sqrt(period))

  const wmaHalf = WMA.calculate({ period: halfPeriod, values: closePrices })
  const wmaFull = WMA.calculate({ period, values: closePrices })

  const rawHMA = wmaHalf.map((v, i) => 2 * v - wmaFull[i])
  return WMA.calculate({ period: sqrtPeriod, values: rawHMA })
}

/**
 * 艾肯通道上限
 */
export function calculateDonchianUpper(
  data: ExtendedKLineDataPoint[],
  period: number = 20
): number[] {
  const result: number[] = []
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(data[i].high)
      continue
    }
    let maxHigh = -Infinity
    for (let j = i - period + 1; j <= i; j++) {
      if (data[j].high > maxHigh) {
        maxHigh = data[j].high
      }
    }
    result.push(maxHigh)
  }
  return result
}

/**
 * 艾肯通道下限
 */
export function calculateDonchianLower(
  data: ExtendedKLineDataPoint[],
  period: number = 20
): number[] {
  const result: number[] = []
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(data[i].low)
      continue
    }
    let minLow = Infinity
    for (let j = i - period + 1; j <= i; j++) {
      if (data[j].low < minLow) {
        minLow = data[j].low
      }
    }
    result.push(minLow)
  }
  return result
}

// ============ MOMENTUM INDICATORS (15个) ============

/**
 * 动量振荡指标 (AO)
 */
export function calculateAO(data: ExtendedKLineDataPoint[]): number[] {
  const aoInput = {
    high: data.map(d => d.high),
    low: data.map(d => d.low),
    fast: 5,
    slow: 34
  }
  return AwesomeOscillator.calculate(aoInput)
}

/**
 * 顺势指标 (CCI)
 */
export function calculateCCI(
  data: ExtendedKLineDataPoint[],
  period: number = 20
): number[] {
  const cciInput = {
    high: data.map(d => d.high),
    low: data.map(d => d.low),
    close: data.map(d => d.close),
    period
  }
  return CCI.calculate(cciInput)
}

/**
 * 钱德动量摆动指标 (CMO)
 * 简化实现
 */
export function calculateCMO(
  data: ExtendedKLineDataPoint[],
  period: number = 14
): number[] {
  const closePrices = data.map(d => d.close)
  const result: number[] = []

  for (let i = period; i < closePrices.length; i++) {
    let gain = 0
    let loss = 0

    for (let j = i - period + 1; j <= i; j++) {
      const diff = closePrices[j] - closePrices[j - 1]
      if (diff > 0) {
        gain += diff
      } else {
        loss -= diff
      }
    }

    const cmo = gain + loss === 0 ? 0 : ((gain - loss) / (gain + loss)) * 100
    result.push(cmo)
  }

  // 填充前面的 null
  return Array(period).fill(0).concat(result)
}

/**
 * 动量指标 (MOM)
 * 使用 ROC (Rate of Change) 替代 - technicalindicators v3.1.0 不包含 MOM
 */
export function calculateMOM(
  data: ExtendedKLineDataPoint[],
  period: number = 10
): number[] {
  const closePrices = data.map(d => d.close)
  // 使用 ROC 作为 MOM 的替代指标
  return ROC.calculate({ period, values: closePrices })
}

/**
 * 变动率指标 (ROC)
 */
export function calculateROC(
  data: ExtendedKLineDataPoint[],
  period: number = 12
): number[] {
  const closePrices = data.map(d => d.close)
  return ROC.calculate({ period, values: closePrices })
}

/**
 * 随机RSI (StochRSI)
 */
export function calculateStochRSI(
  data: ExtendedKLineDataPoint[],
  rsiPeriod: number = 14,
  stochasticPeriod: number = 14,
  kPeriod: number = 3,
  dPeriod: number = 3
): {
  stochRSI: number[]
  k: number[]
  d: number[]
} {
  const closePrices = data.map(d => d.close)

  const stochRsiInput = {
    values: closePrices,
    rsiPeriod,
    stochasticPeriod,
    kPeriod,
    dPeriod
  }

  const stochRsiData = StochasticRSI.calculate(stochRsiInput)

  return {
    stochRSI: stochRsiData.map(d => d.stochRSI),
    k: stochRsiData.map(d => d.k),
    d: stochRsiData.map(d => d.d)
  }
}

/**
 * 三重指数平滑平均线 (TRIX)
 */
export function calculateTRIX(
  data: ExtendedKLineDataPoint[],
  period: number = 18
): number[] {
  const closePrices = data.map(d => d.close)
  return TRIX.calculate({ period, values: closePrices })
}

/**
 * 威廉指标 (Williams %R)
 */
export function calculateWilliamsR(
  data: ExtendedKLineDataPoint[],
  period: number = 14
): number[] {
  const williamsRInput = {
    high: data.map(d => d.high),
    low: data.map(d => d.low),
    close: data.map(d => d.close),
    period
  }
  return WilliamsR.calculate(williamsRInput)
}

/**
 * 随机指标 (Stochastic)
 */
export function calculateStochastic(
  data: ExtendedKLineDataPoint[],
  period: number = 14,
  signalPeriod: number = 3
): {
  k: number[]
  d: number[]
} {
  const stochInput = {
    high: data.map(d => d.high),
    low: data.map(d => d.low),
    close: data.map(d => d.close),
    period,
    signalPeriod
  }

  const stochData = Stochastic.calculate(stochInput)

  return {
    k: stochData.map(d => d.k),
    d: stochData.map(d => d.d)
  }
}

/**
 * 多空力量 (Bull/Bear Power)
 * 简化实现
 */
export function calculateBullBearPower(
  data: ExtendedKLineDataPoint[],
  period: number = 13
): {
  bullPower: number[]
  bearPower: number[]
} {
  const ema = EMA.calculate({ period, values: data.map(d => d.close) })
  const bullPower = data.map((d, i) => d.high - (ema[i] || d.close))
  const bearPower = data.map((d, i) => d.low - (ema[i] || d.close))

  return { bullPower, bearPower }
}

/**
 * 终极振荡指标 (Ultimate Oscillator)
 * 简化实现
 */
export function calculateUltimateOscillator(
  data: ExtendedKLineDataPoint[],
  period1: number = 7,
  period2: number = 14,
  period3: number = 28
): number[] {
  const bp: number[] = []
  const tr: number[] = []

  for (let i = 0; i < data.length; i++) {
    const typicalPrice = (data[i].high + data[i].low + data[i].close) / 3
    bp.push(typicalPrice)

    const prevClose = i > 0 ? data[i - 1].close : data[i].close
    const trueRange = Math.max(
      data[i].high - data[i].low,
      Math.abs(data[i].high - prevClose),
      Math.abs(data[i].low - prevClose)
    )
    tr.push(trueRange)
  }

  const avg1 = calculateAverage(bp, tr, period1)
  const avg2 = calculateAverage(bp, tr, period2)
  const avg3 = calculateAverage(bp, tr, period3)

  const result: number[] = []
  for (let i = 0; i < data.length; i++) {
    if (i < period3 - 1) {
      result.push(50)
      continue
    }
    const uo = 100 * (4 * avg1[i] + 2 * avg2[i] + avg3[i]) / (4 + 2 + 1)
    result.push(uo)
  }

  return result
}

function calculateAverage(bp: number[], tr: number[], period: number): number[] {
  const result: number[] = []
  for (let i = 0; i < bp.length; i++) {
    if (i < period - 1) {
      result.push(0)
      continue
    }
    let sumBP = 0
    let sumTR = 0
    for (let j = i - period + 1; j <= i; j++) {
      sumBP += bp[j]
      sumTR += tr[j]
    }
    result.push(sumTR === 0 ? 0 : sumBP / sumTR)
  }
  return result
}

/**
 * 资金流量指数 (MFI)
 */
export function calculateMFI(
  data: ExtendedKLineDataPoint[],
  period: number = 14
): number[] {
  const mfiInput = {
    high: data.map(d => d.high),
    low: data.map(d => d.low),
    close: data.map(d => d.close),
    volume: data.map(d => d.volume),
    period
  }
  return MFI.calculate(mfiInput)
}

/**
 * 强力指标 (Force Index)
 */
export function calculateForceIndex(
  data: ExtendedKLineDataPoint[],
  period: number = 13
): number[] {
  const forceIndexInput = {
    close: data.map(d => d.close),
    volume: data.map(d => d.volume),
    period
  }
  return ForceIndex.calculate(forceIndexInput)
}

// ============ VOLATILITY INDICATORS (5个) ============

/**
 * 布林带 (BB)
 */
export function calculateBB(
  data: ExtendedKLineDataPoint[],
  period: number = 20,
  stdDev: number = 2
): {
  upper: number[]
  middle: number[]
  lower: number[]
} | null {
  try {
    // v3.1.0 使用 stdDev 而不是 stdDevUp/stdDevDown
    const bbInput = {
      period,
      stdDev,  // v3.1.0 使用 stdDev
      values: data.map(d => d.close)
    }

    const bbData = BollingerBands.calculate(bbInput)

    // 确保返回数据长度与输入一致，前面填充 null
    const padding = data.length - bbData.length

    return {
      upper: Array(padding).fill(null).concat(bbData.map(d => d.upper)),
      middle: Array(padding).fill(null).concat(bbData.map(d => d.middle)),
      lower: Array(padding).fill(null).concat(bbData.map(d => d.lower))
    }
  } catch (error) {
    console.error('BollingerBands calculation error:', error)
    return null
  }
}

/**
 * 平均真实波幅 (ATR)
 */
export function calculateATR(
  data: ExtendedKLineDataPoint[],
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
 * 肯特纳通道
 * 简化实现
 */
export function calculateKeltnerChannel(
  data: ExtendedKLineDataPoint[],
  period: number = 20,
  multiplier: number = 2
): {
  upper: number[]
  middle: number[]
  lower: number[]
} {
  const ema = EMA.calculate({ period, values: data.map(d => d.close) })
  const atr = ATR.calculate({
    high: data.map(d => d.high),
    low: data.map(d => d.low),
    close: data.map(d => d.close),
    period
  })

  const upper: number[] = []
  const lower: number[] = []

  for (let i = 0; i < data.length; i++) {
    upper.push(ema[i] + multiplier * (atr[i] || 0))
    lower.push(ema[i] - multiplier * (atr[i] || 0))
  }

  return { upper, middle: ema, lower }
}

// ============ VOLUME INDICATORS (4个) ============

/**
 * 能量潮 (OBV)
 */
export function calculateOBV(data: ExtendedKLineDataPoint[]): number[] {
  const obvInput = {
    close: data.map(d => d.close),
    volume: data.map(d => d.volume)
  }
  return OBV.calculate(obvInput)
}

/**
 * 佳庆资金流量 (Chaikin Money Flow)
 * 简化实现 (使用MFI作为替代)
 */
export function calculateChaikinMF(
  data: ExtendedKLineDataPoint[],
  period: number = 20
): number[] {
  return calculateMFI(data, period)
}

// ============ UTILITY FUNCTIONS ============

/**
 * 获取所有支持的指标列表
 */
export function getAllSupportedIndicators(): string[] {
  return [
    // 趋势指标 (14)
    'SMA', 'EMA', 'WMA', 'DEMA', 'TEMA', 'TRIMA', 'VWAP', 'KAMA', 'HMA',
    'PSAR', 'ADX', 'DonchianUpper', 'DonchianLower',
    // 动量指标 (15)
    'MACD', 'RSI', 'StochRSI', 'Stochastic', 'CCI', 'AO', 'CMO', 'MOM', 'ROC',
    'WilliamsR', 'BullBearPower', 'UltimateOscillator', 'MFI', 'TRIX', 'KST', 'ForceIndex',
    // 波动率指标 (5)
    'BB', 'ATR', 'KeltnerChannel',
    // 成交量指标 (4)
    'OBV', 'ADL', 'ChaikinMF', 'VWMA'
  ]
}

/**
 * 获取指标分类
 */
export function getIndicatorCategory(indicator: string): string {
  const trend = ['SMA', 'EMA', 'WMA', 'DEMA', 'TEMA', 'TRIMA', 'VWAP', 'KAMA', 'HMA',
    'PSAR', 'ADX', 'DonchianUpper', 'DonchianLower']
  const momentum = ['MACD', 'RSI', 'StochRSI', 'Stochastic', 'CCI', 'AO', 'CMO', 'MOM', 'ROC',
    'WilliamsR', 'BullBearPower', 'UltimateOscillator', 'MFI', 'TRIX', 'KST', 'ForceIndex']
  const volatility = ['BB', 'ATR', 'KeltnerChannel']
  const volume = ['OBV', 'ADL', 'ChaikinMF', 'VWMA']

  if (trend.includes(indicator)) return 'trend'
  if (momentum.includes(indicator)) return 'momentum'
  if (volatility.includes(indicator)) return 'volatility'
  if (volume.includes(indicator)) return 'volume'

  return 'unknown'
}

/**
 * 验证指标参数
 */
export function validateIndicatorParams(
  indicator: string,
  params: any
): boolean {
  // 基本参数验证逻辑 - 支持对象参数
  switch (indicator) {
    case 'SMA':
    case 'EMA':
    case 'WMA':
    case 'DEMA':
    case 'TEMA':
    case 'TRIMA':
      return typeof params === 'object' &&
             params !== null &&
             'period' in params &&
             typeof params.period === 'number' &&
             params.period > 0

    case 'MACD':
      return typeof params === 'object' &&
             params !== null &&
             'fastPeriod' in params &&
             'slowPeriod' in params &&
             'signalPeriod' in params &&
             typeof params.fastPeriod === 'number' && params.fastPeriod > 0 &&
             typeof params.slowPeriod === 'number' && params.slowPeriod > 0 &&
             typeof params.signalPeriod === 'number' && params.signalPeriod > 0

    case 'RSI':
    case 'CCI':
    case 'MOM':
    case 'ROC':
    case 'WilliamsR':
      return typeof params === 'object' &&
             params !== null &&
             'period' in params &&
             typeof params.period === 'number' &&
             params.period > 0

    case 'BB':
      return typeof params === 'object' &&
             params !== null &&
             'period' in params &&
             'stdDev' in params &&
             typeof params.period === 'number' && params.period > 0 &&
             typeof params.stdDev === 'number' && params.stdDev > 0

    default:
      return false
  }
}

/**
 * 指标计算统一接口
 */
export function calculateIndicator(
  indicator: string,
  data: ExtendedKLineDataPoint[],
  params?: any
): any {
  try {
    switch (indicator) {
      case 'SMA': return calculateSMA(data, params?.period || 20)
      case 'EMA': return calculateEMA(data, params?.period || 20)
      case 'WMA': return calculateWMA(data, params?.period || 20)
      case 'DEMA': return calculateDEMA(data, params?.period || 20)
      case 'TEMA': return calculateTEMA(data, params?.period || 20)
      case 'TRIMA': return calculateTRIMA(data, params?.period || 18)
      case 'VWMA': return calculateVWMA(data, params?.period || 20)
      case 'VWAP': return calculateVWAP(data)
      case 'KAMA': return calculateKAMA(data, params?.period || 20)
      case 'HMA': return calculateHMA(data, params?.period || 20)
      case 'PSAR': return calculatePSAR(data, params?.step || 0.02, params?.max || 0.2)
      case 'ADX': return calculateADX(data, params?.period || 14)
      case 'MACD': return calculateMACD(data)
      case 'DonchianUpper': return calculateDonchianUpper(data, params?.period || 20)
      case 'DonchianLower': return calculateDonchianLower(data, params?.period || 20)

      case 'RSI': return RSI.calculate({ period: params?.period || 14, values: data.map(d => d.close) })
      case 'CCI': return calculateCCI(data, params?.period || 20)
      case 'AO': return calculateAO(data)
      case 'CMO': return calculateCMO(data, params?.period || 14)
      case 'MOM': return calculateMOM(data, params?.period || 10)
      case 'ROC': return calculateROC(data, params?.period || 12)
      case 'WilliamsR': return calculateWilliamsR(data, params?.period || 14)
      case 'Stochastic': return calculateStochastic(data, params?.period || 14, params?.signalPeriod || 3)
      case 'StochRSI': return calculateStochRSI(data)
      case 'BullBearPower': return calculateBullBearPower(data, params?.period || 13)
      case 'UltimateOscillator': return calculateUltimateOscillator(data)
      case 'MFI': return calculateMFI(data, params?.period || 14)
      case 'TRIX': return calculateTRIX(data, params?.period || 18)
      case 'ForceIndex': return calculateForceIndex(data, params?.period || 13)

      case 'BB': return calculateBB(data, params?.period || 20, params?.stdDev || 2)
      case 'ATR': return calculateATR(data, params?.period || 14)
      case 'KeltnerChannel': return calculateKeltnerChannel(data, params?.period || 20, params?.multiplier || 2)

      case 'OBV': return calculateOBV(data)
      case 'ADL': return calculateADL(data)
      case 'ChaikinMF': return calculateChaikinMF(data, params?.period || 20)

      default:
        return null
    }
  } catch (error) {
    console.error(`Error calculating indicator ${indicator}:`, error)
    return null
  }
}
