import type { Chart } from 'klinecharts'

type ChartWithIndicators = {
  createIndicator?: (
    name: string,
    isPane: boolean,
    options: {
      id: string
      calcParams?: number[]
    }
  ) => void
  removeIndicator?: () => void
}

const toIndicatorChart = (chart: Chart | null): ChartWithIndicators | null =>
  chart as unknown as ChartWithIndicators | null

export function applyMAIndicator(chart: Chart | null, period: number, name: string, _color: string): void {
  const indicatorChart = toIndicatorChart(chart)
  indicatorChart?.createIndicator?.('MA', true, {
    id: name,
    calcParams: [period]
  })
}

export function applyVolumeIndicator(chart: Chart | null): void {
  const indicatorChart = toIndicatorChart(chart)
  indicatorChart?.createIndicator?.('VOL', false, {
    id: 'VOL'
  })
}

export function applyMACDIndicator(chart: Chart | null): void {
  const indicatorChart = toIndicatorChart(chart)
  indicatorChart?.createIndicator?.('MACD', false, {
    id: 'MACD',
    calcParams: [12, 26, 9]
  })
}

export function applyRSIIndicator(chart: Chart | null): void {
  const indicatorChart = toIndicatorChart(chart)
  indicatorChart?.createIndicator?.('RSI', false, {
    id: 'RSI',
    calcParams: [14]
  })
}

export function applyKDJIndicator(chart: Chart | null): void {
  const indicatorChart = toIndicatorChart(chart)
  indicatorChart?.createIndicator?.('KDJ', false, {
    id: 'KDJ',
    calcParams: [9, 3, 3]
  })
}

export function applySelectedIndicators(chart: Chart | null, indicators: string[]): void {
  const indicatorChart = toIndicatorChart(chart)
  if (!indicatorChart) {
    return
  }

  indicatorChart.removeIndicator?.()

  indicators.forEach(indicator => {
    switch (indicator) {
      case 'MA5':
        applyMAIndicator(chart, 5, 'MA5', '#FF9800')
        break
      case 'MA10':
        applyMAIndicator(chart, 10, 'MA10', '#FFC107')
        break
      case 'MA20':
        applyMAIndicator(chart, 20, 'MA20', '#4CAF50')
        break
      case 'MA60':
        applyMAIndicator(chart, 60, 'MA60', '#2196F3')
        break
      case 'VOL':
        applyVolumeIndicator(chart)
        break
      case 'MACD':
        applyMACDIndicator(chart)
        break
      case 'RSI':
        applyRSIIndicator(chart)
        break
      case 'KDJ':
        applyKDJIndicator(chart)
        break
      default:
        console.warn('Unknown indicator:', indicator)
    }
  })
}
