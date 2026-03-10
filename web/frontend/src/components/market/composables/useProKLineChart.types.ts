import type { PriceLimitStatus } from '@/utils/atrading'

export interface TimePeriod {
  label: string
  value: string
}

export interface Indicator {
  label: string
  value: string
}

export interface PriceLimitMarker {
  timestamp: number
  status: PriceLimitStatus
  color: string
  price: number
}

export interface ProKLineChartProps {
  symbol: string
  periods?: TimePeriod[]
  defaultPeriod?: string
  indicators?: Indicator[]
  height?: string | number
  showPriceLimits?: boolean
  forwardAdjusted?: boolean
  boardType?: 'main' | 'chiNext' | 'star' | 'bje'
}

export const buildDefaultPeriods = (): TimePeriod[] => [
  { label: '分时', value: '1m' },
  { label: '5分', value: '5m' },
  { label: '15分', value: '15m' },
  { label: '30分', value: '30m' },
  { label: '60分', value: '1h' },
  { label: '日K', value: '1d' },
  { label: '周K', value: '1w' },
  { label: '月K', value: '1M' }
]

export const buildDefaultIndicators = (): Indicator[] => [
  { label: 'MA5', value: 'MA5' },
  { label: 'MA10', value: 'MA10' },
  { label: 'MA20', value: 'MA20' },
  { label: 'MA60', value: 'MA60' },
  { label: 'VOL', value: 'VOL' },
  { label: 'MACD', value: 'MACD' },
  { label: 'RSI', value: 'RSI' },
  { label: 'KDJ', value: 'KDJ' }
]

export const defaultSelectedIndicators = ['MA5', 'MA10', 'MA20', 'VOL']

export const defaultProKLineChartProps = {
  periods: buildDefaultPeriods,
  defaultPeriod: '1d',
  indicators: buildDefaultIndicators,
  height: '600px',
  showPriceLimits: true,
  forwardAdjusted: false,
  boardType: 'main' as const
}
