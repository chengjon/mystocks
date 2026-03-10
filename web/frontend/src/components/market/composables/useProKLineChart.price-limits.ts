import type { Chart } from 'klinecharts'
import { PriceLimitStatus, detectPriceLimit, getPriceLimitColor } from '@/utils/atrading'
import type { KLineDataPoint } from '@/utils/indicators'
import type { PriceLimitMarker, ProKLineChartProps } from './useProKLineChart.types.ts'

export function calculatePriceLimitMarkers(
  data: KLineDataPoint[],
  boardType: ProKLineChartProps['boardType'] = 'main'
): PriceLimitMarker[] {
  const markers: PriceLimitMarker[] = []

  for (let index = 1; index < data.length; index += 1) {
    const current = data[index]
    const prevClose = data[index - 1].close
    const status = detectPriceLimit(current.close, prevClose, boardType)

    if (status !== PriceLimitStatus.NONE) {
      markers.push({
        timestamp: current.timestamp,
        status,
        color: getPriceLimitColor(status),
        price: current.close
      })
    }
  }

  return markers
}

export function applyPriceLimitOverlay(chart: Chart | null, markers: PriceLimitMarker[]): void {
  if (!chart || markers.length === 0) {
    return
  }

  try {
    const overlayPayload = markers.map(marker => ({
      timestamp: marker.timestamp,
      text: marker.status,
      value: marker.price,
      color: marker.color
    }))

    void overlayPayload
  } catch (error: unknown) {
    console.error('Failed to apply price limit overlay:', error)
  }
}
