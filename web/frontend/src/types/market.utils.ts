import type { KLineData } from './kline'

export function isUp(item: Pick<KLineData, 'open' | 'close'>): boolean {
  return item.close > item.open
}

export function isDown(item: Pick<KLineData, 'open' | 'close'>): boolean {
  return item.close < item.open
}

export function isFlat(item: Pick<KLineData, 'open' | 'close'>): boolean {
  return item.close === item.open
}

export function calculateColorType(item: Pick<KLineData, 'open' | 'close'>): 'up' | 'down' | 'flat' {
  if (isUp(item)) return 'up'
  if (isDown(item)) return 'down'
  return 'flat'
}

export function formatKLineForChart(data: KLineData[]) {
  return data.map((item) => ({
    timestamp: item.timestamp,
    values: [item.open, item.close, item.low, item.high],
    volume: item.volume,
    colorType: calculateColorType(item)
  }))
}
