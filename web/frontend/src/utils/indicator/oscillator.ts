import type { KLineData } from '@/types/kline'
import {
  calculateATR as calculateATRBase,
  calculateKDJ as calculateKDJBase,
  calculateMACD as calculateMACDBase,
  calculateRSI as calculateRSIBase,
  formatIndicatorData,
  type KLineDataPoint,
} from '@/utils/indicators'

export type OscillatorType = 'MACD' | 'RSI' | 'KDJ' | 'WR' | 'CCI' | 'OBV' | 'ATR'

export interface OscillatorConfig {
  name: string
  shortName: string
  type: OscillatorType
  params: number[]
  colors: string[]
  visible: boolean
  range?: [number, number]
}

export type OscillatorValue = number | null
export type OscillatorResult = Record<string, OscillatorValue[]>

export interface MACDResult extends Record<string, OscillatorValue[]> {
  DIF: OscillatorValue[]
  DEA: OscillatorValue[]
  MACD: OscillatorValue[]
}

export interface KDJResult extends Record<string, OscillatorValue[]> {
  K: OscillatorValue[]
  D: OscillatorValue[]
  J: OscillatorValue[]
}

export const DEFAULT_OSCILLATORS: OscillatorConfig[] = [
  { name: 'MACD', shortName: 'MACD', type: 'MACD', params: [12, 26, 9], colors: ['#2DC08E', '#F92855', '#D4AF37'], visible: true, range: [-5, 5] },
  { name: '相对强弱', shortName: 'RSI', type: 'RSI', params: [14], colors: ['#D4AF37'], visible: false, range: [0, 100] },
  { name: '随机指标', shortName: 'KDJ', type: 'KDJ', params: [9, 3, 3], colors: ['#D4AF37', '#2DC08E', '#F92855'], visible: false, range: [0, 100] },
  { name: '威廉指标', shortName: 'WR', type: 'WR', params: [14], colors: ['#D4AF37'], visible: false, range: [-100, 0] },
  { name: '顺势指标', shortName: 'CCI', type: 'CCI', params: [14], colors: ['#D4AF37'], visible: false },
  { name: '能量潮', shortName: 'OBV', type: 'OBV', params: [], colors: ['#D4AF37'], visible: false },
  { name: '真实波幅', shortName: 'ATR', type: 'ATR', params: [14], colors: ['#D4AF37'], visible: false },
]

function toPoints(data: KLineData[]): KLineDataPoint[] {
  return data.map((item) => ({
    timestamp: item.timestamp,
    open: item.open,
    high: item.high,
    low: item.low,
    close: item.close,
    volume: item.volume,
  }))
}

function padSeries(values: number[], dataLength: number): OscillatorValue[] {
  return formatIndicatorData(values, dataLength)
}

export function calculateMACD(data: KLineData[]): MACDResult {
  const points = toPoints(data)
  const result = calculateMACDBase(points)
  const dataLength = data.length

  return {
    DIF: padSeries(result.macd, dataLength),
    DEA: padSeries(result.signal, dataLength),
    MACD: padSeries(result.histogram, dataLength),
  }
}

export function calculateRSI(data: KLineData[], period: number = 14): OscillatorValue[] {
  return padSeries(calculateRSIBase(toPoints(data), period), data.length)
}

export function calculateKDJ(data: KLineData[], kPeriod: number = 9, dPeriod: number = 3, jPeriod: number = 3): KDJResult {
  const result = calculateKDJBase(toPoints(data), kPeriod, dPeriod, jPeriod)
  const dataLength = data.length

  return {
    K: padSeries(result.k, dataLength),
    D: padSeries(result.d, dataLength),
    J: padSeries(result.j, dataLength),
  }
}

export function calculateWR(data: KLineData[], period: number = 14): OscillatorValue[] {
  const result: number[] = []

  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(NaN)
      continue
    }

    const window = data.slice(i - period + 1, i + 1)
    const highest = Math.max(...window.map((item) => item.high))
    const lowest = Math.min(...window.map((item) => item.low))
    const currentClose = data[i].close

    if (highest === lowest) {
      result.push(0)
      continue
    }

    result.push(Number((((highest - currentClose) / (highest - lowest)) * -100).toFixed(2)))
  }

  return result
}

export function calculateCCI(data: KLineData[], period: number = 14): OscillatorValue[] {
  const result: number[] = []
  const typicalPrices = data.map((item) => (item.high + item.low + item.close) / 3)

  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(NaN)
      continue
    }

    const window = typicalPrices.slice(i - period + 1, i + 1)
    const sma = window.reduce((sum, value) => sum + value, 0) / period
    const meanDeviation = window.reduce((sum, value) => sum + Math.abs(value - sma), 0) / period

    if (meanDeviation === 0) {
      result.push(0)
      continue
    }

    const cci = (typicalPrices[i] - sma) / (0.015 * meanDeviation)
    result.push(Number(cci.toFixed(2)))
  }

  return result
}

export function calculateOBV(data: KLineData[]): OscillatorValue[] {
  const result: number[] = []
  let current = 0

  for (let i = 0; i < data.length; i++) {
    if (i === 0) {
      result.push(current)
      continue
    }

    if (data[i].close > data[i - 1].close) {
      current += data[i].volume
    } else if (data[i].close < data[i - 1].close) {
      current -= data[i].volume
    }

    result.push(current)
  }

  return result
}

export function calculateATR(data: KLineData[], period: number = 14): OscillatorValue[] {
  return padSeries(calculateATRBase(toPoints(data), period), data.length)
}

export function calculateOscillator(
  data: KLineData[],
  type: OscillatorType,
  params: number[] = []
): OscillatorResult {
  switch (type) {
    case 'MACD':
      return calculateMACD(data)
    case 'RSI':
      return { RSI: calculateRSI(data, params[0] ?? 14) }
    case 'KDJ':
      return calculateKDJ(data, params[0] ?? 9, params[1] ?? 3, params[2] ?? 3)
    case 'WR': {
      const periods = params.length > 0 ? params : [14]
      return Object.fromEntries(periods.map((period) => [`WR${period}`, calculateWR(data, period)]))
    }
    case 'CCI':
      return { CCI: calculateCCI(data, params[0] ?? 14) }
    case 'OBV':
      return { OBV: calculateOBV(data) }
    case 'ATR':
      return { ATR: calculateATR(data, params[0] ?? 14) }
    default:
      return {}
  }
}

export function formatOscillatorValue(value: OscillatorValue, type: OscillatorType): string {
  if (value === null || Number.isNaN(value) || !Number.isFinite(value)) {
    return '--'
  }

  if (type === 'OBV') {
    return value.toFixed(0)
  }

  return value.toFixed(2)
}
