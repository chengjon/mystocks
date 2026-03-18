import type { KLineData, MarketColorType } from './market'

export function isUp(colorType: MarketColorType): boolean {
  return colorType === 'up'
}

export function isDown(colorType: MarketColorType): boolean {
  return colorType === 'down'
}

export function isFlat(colorType: MarketColorType): boolean {
  return colorType === 'flat'
}

export function calculateColorType(changePercent: number): MarketColorType {
  if (changePercent > 0) return 'up'
  if (changePercent < 0) return 'down'
  return 'flat'
}

export function formatKLineForChart(kline: KLineData): {
  categoryData: string[]
  values: number[][]
  volumes: number[]
} {
  return {
    categoryData: kline.data.map((candle) => candle.datetime),
    values: kline.data.map((candle) => [
      candle.open,
      candle.close,
      candle.low,
      candle.high,
    ]),
    volumes: kline.data.map((candle) => candle.volume),
  }
}
