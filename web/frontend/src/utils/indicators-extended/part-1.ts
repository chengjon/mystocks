/**
 * Extended Technical Indicators Utility
 *
 * Extended wrapper for technicalindicators npm package
 * Provides 70+ technical indicators for A股 market
 */

import {
  SMA,
  EMA,
  Stochastic,
  WMA,
  ADL,
  ADX,
  AwesomeOscillator,
  CCI,
  // MOM 已移除 - technicalindicators v3.1.0 不存在，使用 ROC 替代
  PSAR,
  ROC,
  StochasticRSI,
  TRIX,
  VWAP,
  WilliamsR
  // VWMA 已移除 - technicalindicators v3.1.0 不存在，使用自定义实现
} from 'technicalindicators'

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

/**
 * 动量振荡指标 (AO)
 */
export function calculateAO(data: ExtendedKLineDataPoint[]): number[] {
  const aoInput = {
    high: data.map(d => d.high),
    low: data.map(d => d.low),
    fastPeriod: 5,
    slowPeriod: 34
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
    k: stochData.map(d => isFinite(d.k) ? d.k : 0),
    d: stochData.map(d => isFinite(d.d) ? d.d : 0)
  }
}
