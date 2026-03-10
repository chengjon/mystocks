export function createProKLineChartStyleConfig(): Record<string, unknown> {
  return {
    grid: {
      show: true,
      horizontal: {
        show: true,
        size: 1,
        color: 'rgb(255 255 255 / 10%)',
        style: 'dashed',
        dashedValue: [2, 2]
      },
      vertical: {
        show: true,
        size: 1,
        color: 'rgb(255 255 255 / 10%)',
        style: 'dashed',
        dashedValue: [2, 2]
      }
    },
    candle: {
      type: 'candle_solid',
      bar: {
        upColor: '#EF5350',
        downColor: '#26A69A',
        noChangeColor: '#888888'
      },
      tooltip: {
        showRule: 'always',
        showType: 'standard',
        labels: ['时间: ', '开: ', '收: ', '低: ', '高: ', '涨跌: ', '涨幅: ', '成交量: ', '成交额: '],
        text: {
          size: 12,
          color: '#D9D9D9'
        }
      },
      priceMark: {
        show: true,
        high: {
          show: true,
          color: '#EF5350',
          textSize: 10
        },
        low: {
          show: true,
          color: '#26A69A',
          textSize: 10
        }
      }
    },
    indicator: {
      tooltip: {
        showRule: 'always',
        showType: 'standard',
        text: {
          size: 12,
          color: '#D9D9D9'
        }
      }
    },
    crosshair: {
      show: true,
      horizontal: {
        show: true,
        line: {
          show: true,
          style: 'dashed',
          dashValue: [4, 2],
          size: 1,
          color: '#ffffff'
        },
        text: {
          show: true,
          color: '#D9D9D9',
          size: 12
        }
      },
      vertical: {
        show: true,
        line: {
          show: true,
          style: 'dashed',
          dashValue: [4, 2],
          size: 1,
          color: '#ffffff'
        },
        text: {
          show: true,
          color: '#D9D9D9',
          size: 12
        }
      }
    },
    yAxis: {
      show: true,
      position: 'right',
      showTitle: false
    },
    xAxis: {
      show: true,
      axisLabel: {
        show: true,
        format: (date: number) => {
          const value = new Date(date)
          return `${value.getMonth() + 1}/${value.getDate()}`
        }
      }
    }
  }
}

export function applyChartContainerHeight(container: HTMLElement, height: string | number): void {
  if (typeof height === 'number') {
    container.style.height = `${height}px`
    return
  }

  container.style.height = height
}
