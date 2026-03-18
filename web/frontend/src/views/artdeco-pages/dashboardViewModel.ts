import type { MarketData } from './composables/useArtDecoDashboard.types.ts'
import type { DashboardMarketOverviewRecord } from './dashboardContract'

type DashboardMarketSlice = Pick<
  MarketData,
  'shanghai' | 'shenzhen' | 'chuangye' | 'stocks' | 'volume'
>

function toNumber(value: unknown): number {
  const numeric = Number(value)
  return Number.isFinite(numeric) ? numeric : 0
}

function formatIndexValue(value: unknown): string {
  const numeric = toNumber(value)
  return numeric > 0 ? numeric.toFixed(2) : '--'
}

function formatChangeValue(value: unknown): string {
  return toNumber(value).toFixed(2)
}

function formatTurnover(value: unknown): string {
  const numeric = toNumber(value)
  if (numeric <= 0) {
    return '--'
  }

  return `${(numeric / 100000000).toFixed(1)}亿`
}

function pickIndex(
  indices: DashboardMarketOverviewRecord['indices'],
  matcher: (name: string, symbol: string) => boolean,
  fallbackIndex: number
) {
  return (
    indices.find((item: DashboardMarketOverviewRecord['indices'][number]) =>
      matcher(String(item.name ?? ''), String(item.symbol ?? ''))
    ) ??
    indices[fallbackIndex] ??
    null
  )
}

export function createEmptyDashboardMarketSlice(): DashboardMarketSlice {
  return {
    shanghai: { index: '--', change: '0.00' },
    shenzhen: { index: '--', change: '0.00' },
    chuangye: { index: '--', change: '0.00' },
    stocks: { up: 0, down: 0 },
    volume: { amount: '--' }
  }
}

export function toDashboardMarketData(overview: DashboardMarketOverviewRecord): DashboardMarketSlice {
  const fallback = createEmptyDashboardMarketSlice()
  const shanghai = pickIndex(
    overview.indices,
    (name, symbol) => name.includes('上证') || symbol.includes('000001'),
    0
  )
  const shenzhen = pickIndex(
    overview.indices,
    (name, symbol) => name.includes('深证') || symbol.includes('399001'),
    1
  )
  const chuangye = pickIndex(
    overview.indices,
    (name, symbol) => name.includes('创业板') || symbol.includes('399006'),
    2
  )

  return {
    shanghai: shanghai
      ? {
          index: formatIndexValue(shanghai.current_price),
          change: formatChangeValue(shanghai.change_percent)
        }
      : fallback.shanghai,
    shenzhen: shenzhen
      ? {
          index: formatIndexValue(shenzhen.current_price),
          change: formatChangeValue(shenzhen.change_percent)
        }
      : fallback.shenzhen,
    chuangye: chuangye
      ? {
          index: formatIndexValue(chuangye.current_price),
          change: formatChangeValue(chuangye.change_percent)
        }
      : fallback.chuangye,
    stocks: {
      up: toNumber(overview.up_count),
      down: toNumber(overview.down_count)
    },
    volume: {
      amount: formatTurnover(overview.total_turnover)
    }
  }
}

export function formatDashboardProcessTime(value: string): string {
  if (!value) {
    return 'N/A'
  }

  if (value.trim().toLowerCase().endsWith('ms')) {
    return value
  }

  const numeric = Number.parseFloat(value)
  if (Number.isNaN(numeric)) {
    return value
  }

  return `${numeric.toFixed(2)}ms`
}
