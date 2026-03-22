// @ts-nocheck

/**
 * Extended Technical Indicators Utility
 *
 * Extended wrapper for technicalindicators npm package
 * Provides 70+ technical indicators for A股 market
 */

import {
  EMA,
  _MACD,
  RSI,
  BollingerBands,
  ATR,
  MFI,
  // MOM 已移除 - technicalindicators v3.1.0 不存在，使用 ROC 替代
  OBV,
  _KST,
  ForceIndex
  // VWMA 已移除 - technicalindicators v3.1.0 不存在，使用自定义实现
} from 'technicalindicators'

// 导入自定义实现函数
import { calculateMACD } from '../technicalIndicators.js'
import {
  calculateADX,
  calculateAO,
  calculateCCI,
  calculateCMO,
  calculateDEMA,
  calculateEMA,
  calculateHMA,
  calculateKAMA,
  calculateMOM,
  calculatePSAR,
  calculateROC,
  calculateSMA,
  calculateStochastic,
  calculateStochRSI,
  calculateTEMA,
  calculateTRIMA,
  calculateTRIX,
  calculateVWAP,
  calculateVWMA,
  calculateWMA,
  calculateWilliamsR,
  calculateADL,
  type ExtendedKLineDataPoint
} from './part-1.ts'

function calculateAverage(values: number[], divisors: number[], period: number): number[] {
  const result: number[] = []

  for (let index = 0; index < values.length; index += 1) {
    if (index < period - 1) {
      result.push(0)
      continue
    }

    const valueSlice = values.slice(index - period + 1, index + 1)
    const divisorSlice = divisors.slice(index - period + 1, index + 1)
    const numerator = valueSlice.reduce((sum, value) => sum + value, 0)
    const denominator = divisorSlice.reduce((sum, value) => sum + value, 0)

    result.push(denominator === 0 ? 0 : numerator / denominator)
  }

  return result
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

    // 确保返回数据长度与输入一致，前面填充 0
    const padding = data.length - bbData.length

    return {
      upper: Array(padding).fill(0).concat(bbData.map(d => d.upper)),
      middle: Array(padding).fill(0).concat(bbData.map(d => d.middle)),
      lower: Array(padding).fill(0).concat(bbData.map(d => d.lower))
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
  params: unknown
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
      return typeof params === 'object' &&
             params !== null &&
             'period' in params &&
             typeof params.period === 'number' &&
             params.period >= 6 && params.period <= 99

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
  params?: unknown
): unknown {
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
      case 'MACD': return calculateMACD(data.map(d => d.close), params?.fastPeriod, params?.slowPeriod, params?.signalPeriod)
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
