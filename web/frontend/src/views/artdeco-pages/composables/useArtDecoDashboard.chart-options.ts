import type { MarketData, MarketHeatItem } from './useArtDecoDashboard.types.ts'

type NumericParser = (value: unknown, fallback?: number) => number

const A_SHARE_UP = '#FF5252'
const A_SHARE_DOWN = '#00E676'
const ARTDECO_GOLD = '#D4AF37'

export function createFundFlowChartOption(marketData: MarketData): Record<string, unknown> {
  const data = marketData.fundFlow
  const categories = ['沪股通', '深股通', '主力']
  const values = [data.hgt.amount, data.sgt.amount, data.mainForce.amount]

  return {
    tooltip: { trigger: 'axis' },
    grid: { top: 30, bottom: 20, left: 40, right: 10, containLabel: true },
    xAxis: {
      type: 'category',
      data: categories,
      axisLine: { show: false },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      splitLine: { show: true, lineStyle: { color: 'rgb(255 255 255 / 5%)' } }
    },
    series: [{
      type: 'bar',
      barWidth: '40%',
      data: values.map(value => ({
        value,
        itemStyle: {
          color: value >= 0 ? A_SHARE_UP : A_SHARE_DOWN,
          borderRadius: [4, 4, 0, 0]
        }
      }))
    }]
  }
}

export function createMarketTrendOption(trendData: number[]): Record<string, unknown> | null {
  if (!trendData.length) {
    return null
  }

  const hours = Array.from({ length: trendData.length }, (_, index) => index)

  return {
    tooltip: { trigger: 'axis' },
    grid: { top: 10, bottom: 20, left: 40, right: 10, containLabel: true },
    xAxis: {
      type: 'category',
      data: hours,
      boundaryGap: false,
      axisLine: { show: false },
      axisLabel: { show: false }
    },
    yAxis: {
      type: 'value',
      scale: true,
      splitLine: { show: true, lineStyle: { color: 'rgb(255 255 255 / 5%)' } }
    },
    series: [{
      type: 'line',
      smooth: true,
      symbol: 'none',
      lineStyle: { width: 2, color: ARTDECO_GOLD },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgb(212 175 55 / 30%)' },
            { offset: 1, color: 'rgb(212 175 55 / 0)' }
          ]
        }
      },
      data: trendData
    }]
  }
}

export function createHeatmapOption(marketHeat: MarketHeatItem[]): Record<string, unknown> | null {
  if (!marketHeat.length) {
    return null
  }

  const data = marketHeat.map(item => ({
    name: item.name,
    value: Math.abs(item.change),
    change: item.change,
    itemStyle: {
      color: item.change >= 0 ? A_SHARE_UP : A_SHARE_DOWN
    }
  }))

  return {
    tooltip: {
      formatter: (params: { data: { name: string; change: number } }): string => {
        const { name, change } = params.data
        const sign = change > 0 ? '+' : ''
        return `${name}: ${sign}${change}%`
      }
    },
    series: [{
      type: 'treemap',
      width: '100%',
      height: '100%',
      roam: false,
      nodeClick: false,
      breadcrumb: { show: false },
      label: {
        show: true,
        formatter: '{b}\n{c}%'
      },
      itemStyle: {
        borderColor: '#1f2833',
        borderWidth: 1,
        gapWidth: 1
      },
      data
    }]
  }
}

export function createCapitalFlowHeatmapOption(
  capitalFlowData: Array<{ name?: string; amount?: number }>,
  toNumber: NumericParser
): Record<string, unknown> | null {
  if (!capitalFlowData.length) {
    return null
  }

  const data = capitalFlowData.map(item => {
    const amount = toNumber(item.amount)
    return {
      name: item.name || '--',
      value: Math.abs(amount),
      amount,
      itemStyle: {
        color: amount >= 0 ? A_SHARE_UP : A_SHARE_DOWN
      }
    }
  })

  return {
    tooltip: {
      formatter: (params: { data: { name: string; amount: number } }): string => {
        const { name, amount } = params.data
        const sign = amount > 0 ? '+' : ''
        return `${name}<br/>净流向: ${sign}${amount.toFixed(2)}亿`
      }
    },
    series: [{
      type: 'treemap',
      roam: false,
      nodeClick: false,
      breadcrumb: { show: false },
      label: { show: true, formatter: '{b}' },
      itemStyle: {
        borderColor: '#1f2833',
        borderWidth: 1,
        gapWidth: 1
      },
      data
    }]
  }
}

export function createSectorRotationRadarOption(
  marketHeat: MarketHeatItem[],
  toNumber: NumericParser
): Record<string, unknown> | null {
  if (!marketHeat.length) {
    return null
  }

  const sectors = marketHeat
    .slice()
    .sort((left, right) => Math.abs(right.change) - Math.abs(left.change))
    .slice(0, 6)

  if (!sectors.length) {
    return null
  }

  const maxValue = Math.max(...sectors.map(item => Math.abs(toNumber(item.change))), 1)
  const indicator = sectors.map(item => ({
    name: item.name,
    max: Number((maxValue * 1.2).toFixed(2))
  }))

  return {
    tooltip: {
      formatter: (params: { value: number[] }): string => {
        return params.value
          .map((value, index) => `${indicator[index].name}: ${value.toFixed(2)}%`)
          .join('<br/>')
      }
    },
    radar: {
      radius: '62%',
      indicator,
      splitLine: { lineStyle: { color: 'rgb(255 255 255 / 12%)' } },
      splitArea: { areaStyle: { color: ['transparent'] } },
      axisLine: { lineStyle: { color: 'rgb(255 255 255 / 20%)' } },
      axisName: { color: ARTDECO_GOLD, fontSize: 11 }
    },
    series: [{
      type: 'radar',
      data: [{
        value: sectors.map(item => Number(Math.abs(toNumber(item.change)).toFixed(2))),
        name: '行业轮动强度',
        areaStyle: { color: 'rgb(212 175 55 / 25%)' },
        lineStyle: { color: ARTDECO_GOLD, width: 2 },
        itemStyle: { color: ARTDECO_GOLD }
      }]
    }]
  }
}
