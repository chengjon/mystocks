import type { AdjustType, IntervalType } from '@/types/kline'

export interface ProKLineChartProps {
  initialSymbol?: string
  initialInterval?: IntervalType
  useMock?: boolean
}

export interface SymbolOption {
  code: string
  name: string
}

export interface OptionItem {
  value: string
  label: string
}

export interface IndicatorOption {
  key: string
  label: string
}

export const defaultProKLineChartProps = {
  initialSymbol: '000001.SZ',
  initialInterval: '1d' as IntervalType,
  useMock: true
}

export const defaultAdjustType: AdjustType = 'qfq'
export const defaultOscillatorIndicator = 'MACD'

export const availableSymbols: SymbolOption[] = [
  { code: '000001.SZ', name: '平安银行' },
  { code: '600519.SH', name: '贵州茅台' },
  { code: '000001.SH', name: '上证指数' },
  { code: '300750.SZ', name: '宁德时代' }
]

export const intervals: OptionItem[] = [
  { value: '1m', label: '1分' },
  { value: '5m', label: '5分' },
  { value: '15m', label: '15分' },
  { value: '1h', label: '1时' },
  { value: '4h', label: '4时' },
  { value: '1d', label: '日' },
  { value: '1w', label: '周' },
  { value: '1M', label: '月' }
]

export const mainIndicators: IndicatorOption[] = [
  { key: 'MA', label: 'MA' },
  { key: 'BOLL', label: 'BOLL' },
  { key: 'EMA', label: 'EMA' }
]

export const oscillatorIndicators: IndicatorOption[] = [
  { key: 'MACD', label: 'MACD' },
  { key: 'RSI', label: 'RSI' },
  { key: 'KDJ', label: 'KDJ' }
]

export function formatKLineVolume(vol: number): string {
  if (vol >= 100000000) return `${(vol / 100000000).toFixed(2)}亿`
  if (vol >= 10000) return `${(vol / 10000).toFixed(2)}万`
  return vol.toLocaleString()
}
