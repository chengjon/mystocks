import type { LayoutChildType, LayoutOptions } from '@/types/klinecharts'

export function createMainChartConfig() {
  return {
    locale: 'zh-CN',
    styles: {
      grid: {
        show: true,
        horizontal: { show: true, size: 1, color: '#1A1A1A' },
        vertical: { show: true, size: 1, color: '#1A1A1A' }
      },
      candle: {
        type: 'candle_solid' as const,
        bar: {
          upColor: '#2DC08E',
          downColor: '#F92855',
          upBorderColor: '#2DC08E',
          downBorderColor: '#F92855',
          upWickColor: '#2DC08E',
          downWickColor: '#F92855'
        }
      },
      volume: {
        barColor: {
          upColor: 'rgb(45 192 142 / 40%)',
          downColor: 'rgb(249 40 85 / 40%)'
        }
      },
      xAxis: {
        axisLine: { show: true, color: '#333333' },
        tickLine: { show: true, color: '#333333' },
        tickText: { color: '#888888', size: 11 }
      },
      yAxis: {
        axisLine: { show: true, color: '#333333' },
        tickLine: { show: true, color: '#333333' },
        tickText: { color: '#888888', size: 11 }
      },
      crosshair: {
        show: true,
        horizontal: { show: true, lineColor: '#D4AF37', lineWidth: 1, lineStyle: 'dashed' as const },
        vertical: { show: true, lineColor: '#D4AF37', lineWidth: 1, lineStyle: 'dashed' as const }
      },
      tooltip: {
        show: true,
        type: 'standard' as const,
        labels: ['时间', '开盘', '最高', '最低', '收盘', '成交量'],
        labelColor: '#F2F0E4',
        labelColorDot: '#D4AF37'
      }
    } as unknown,
    layout: [
      { type: 'candle' as LayoutChildType, height: '65%' } as LayoutOptions,
      { type: 'volume' as LayoutChildType, height: '15%' } as LayoutOptions,
      { type: 'xAxis' as LayoutChildType, height: 30 } as LayoutOptions
    ]
  }
}

export function createOscillatorChartConfig() {
  return {
    locale: 'zh-CN',
    styles: {
      grid: { show: true, horizontal: { show: true, size: 1, color: '#1A1A1A' }, vertical: { show: false } },
      xAxis: { axisLine: { show: true, color: '#333333' }, tickText: { color: '#888888' } },
      yAxis: { axisLine: { show: true, color: '#333333' }, tickText: { color: '#888888' } }
    },
    layout: [{ type: 'xAxis' as LayoutChildType, height: 25 } as LayoutOptions]
  }
}
