// web/frontend/src/composables/useChart.ts

import { ref, onMounted, onUnmounted, nextTick, watch, type Ref } from 'vue'
import * as echarts from 'echarts'

// ArtDeco Theme Definition
const artDecoTheme = {
  color: [
    '#d4af37', // Gold
    '#4caf50', // Green (Up)
    '#f44336', // Red (Down)
    '#2196f3', // Blue (Info)
    '#9c27b0', // Purple
    '#ff9800', // Orange
    '#795548', // Brown
    '#607d8b'  // Grey
  ],
  backgroundColor: 'transparent',
  textStyle: {
    fontFamily: '"Inter", "Helvetica Neue", Arial, sans-serif'
  },
  title: {
    textStyle: {
      color: '#e0e0e0',
      fontWeight: 'bold'
    },
    subtextStyle: {
      color: '#a0a0a0'
    }
  },
  line: {
    itemStyle: {
      borderWidth: 1
    },
    lineStyle: {
      width: 2
    },
    symbolSize: 4,
    symbol: 'emptyCircle',
    smooth: true
  },
  radar: {
    itemStyle: {
      borderWidth: 1
    },
    lineStyle: {
      width: 2
    },
    symbolSize: 4,
    symbol: 'emptyCircle',
    smooth: true
  },
  bar: {
    itemStyle: {
      barBorderWidth: 0,
      barBorderColor: '#ccc'
    }
  },
  pie: {
    itemStyle: {
      borderWidth: 0,
      borderColor: '#ccc'
    }
  },
  scatter: {
    itemStyle: {
      borderWidth: 0,
      borderColor: '#ccc'
    }
  },
  boxplot: {
    itemStyle: {
      borderWidth: 0,
      borderColor: '#ccc'
    }
  },
  parallel: {
    itemStyle: {
      borderWidth: 0,
      borderColor: '#ccc'
    }
  },
  sankey: {
    itemStyle: {
      borderWidth: 0,
      borderColor: '#ccc'
    }
  },
  funnel: {
    itemStyle: {
      borderWidth: 0,
      borderColor: '#ccc'
    }
  },
  gauge: {
    itemStyle: {
      borderWidth: 0,
      borderColor: '#ccc'
    }
  },
  candlestick: {
    itemStyle: {
      color: '#f44336',       // Red (Down/Fall) - Chinese standard: Red is Up, Green is Down usually, but verify user preference. 
                              // Global standard: Green Up, Red Down. 
                              // User's CSS has .rise as #4caf50 (Green) and .fall as #f44336 (Red). So Green = Up.
      color0: '#4caf50',      // Green (Up/Rise) - Wait, in candlestick, color is usually the *increasing* candle.
                              // Let's stick to standard: Green is Up/Bullish, Red is Down/Bearish.
                              // Wait, checking user's CSS: --artdeco-up: #4caf50; --artdeco-down: #f44336;
                              // So Green is Up.
      borderColor: '#f44336',
      borderColor0: '#4caf50'
    }
  },
  graph: {
    itemStyle: {
      borderWidth: 0,
      borderColor: '#ccc'
    },
    lineStyle: {
      width: 1,
      color: '#aaa'
    },
    symbolSize: 4,
    symbol: 'emptyCircle',
    smooth: true,
    color: ['#d4af37', '#4caf50', '#f44336', '#2196f3', '#9c27b0', '#ff9800', '#795548', '#607d8b'],
    label: {
      color: '#e0e0e0'
    }
  },
  map: {
    itemStyle: {
      areaColor: '#eee',
      borderColor: '#444',
      borderWidth: 0.5
    },
    label: {
      color: '#000'
    },
    emphasis: {
      itemStyle: {
        areaColor: 'rgba(255,215,0,0.8)',
        borderColor: '#444',
        borderWidth: 1
      },
      label: {
        color: 'rgb(100,0,0)'
      }
    }
  },
  geo: {
    itemStyle: {
      areaColor: '#eee',
      borderColor: '#444',
      borderWidth: 0.5
    },
    label: {
      color: '#000'
    },
    emphasis: {
      itemStyle: {
        areaColor: 'rgba(255,215,0,0.8)',
        borderColor: '#444',
        borderWidth: 1
      },
      label: {
        color: 'rgb(100,0,0)'
      }
    }
  },
  categoryAxis: {
    axisLine: {
      show: true,
      lineStyle: {
        color: '#666'
      }
    },
    axisTick: {
      show: true,
      lineStyle: {
        color: '#666'
      }
    },
    axisLabel: {
      show: true,
      color: '#a0a0a0'
    },
    splitLine: {
      show: false,
      lineStyle: {
        color: ['#ccc']
      }
    },
    splitArea: {
      show: false,
      areaStyle: {
        color: ['rgba(250,250,250,0.3)', 'rgba(200,200,200,0.3)']
      }
    }
  },
  valueAxis: {
    axisLine: {
      show: true,
      lineStyle: {
        color: '#666'
      }
    },
    axisTick: {
      show: true,
      lineStyle: {
        color: '#666'
      }
    },
    axisLabel: {
      show: true,
      color: '#a0a0a0'
    },
    splitLine: {
      show: true,
      lineStyle: {
        color: ['rgba(255, 255, 255, 0.1)'] // Subtle grid lines
      }
    },
    splitArea: {
      show: false,
      areaStyle: {
        color: ['rgba(250,250,250,0.3)', 'rgba(200,200,200,0.3)']
      }
    }
  },
  logAxis: {
    axisLine: {
      show: true,
      lineStyle: {
        color: '#666'
      }
    },
    axisTick: {
      show: true,
      lineStyle: {
        color: '#666'
      }
    },
    axisLabel: {
      show: true,
      color: '#a0a0a0'
    },
    splitLine: {
      show: true,
      lineStyle: {
        color: ['rgba(255, 255, 255, 0.1)']
      }
    },
    splitArea: {
      show: false,
      areaStyle: {
        color: ['rgba(250,250,250,0.3)', 'rgba(200,200,200,0.3)']
      }
    }
  },
  timeAxis: {
    axisLine: {
      show: true,
      lineStyle: {
        color: '#666'
      }
    },
    axisTick: {
      show: true,
      lineStyle: {
        color: '#666'
      }
    },
    axisLabel: {
      show: true,
      color: '#a0a0a0'
    },
    splitLine: {
      show: true,
      lineStyle: {
        color: ['rgba(255, 255, 255, 0.1)']
      }
    },
    splitArea: {
      show: false,
      areaStyle: {
        color: ['rgba(250,250,250,0.3)', 'rgba(200,200,200,0.3)']
      }
    }
  },
  toolbox: {
    iconStyle: {
      borderColor: '#999'
    },
    emphasis: {
      iconStyle: {
        borderColor: '#666'
      }
    }
  },
  legend: {
    textStyle: {
      color: '#e0e0e0'
    }
  },
  tooltip: {
    axisPointer: {
      lineStyle: {
        color: '#ccc',
        width: 1
      },
      crossStyle: {
        color: '#ccc',
        width: 1
      }
    }
  },
  timeline: {
    lineStyle: {
      color: '#d4af37',
      width: 1
    },
    itemStyle: {
      color: '#d4af37',
      borderWidth: 1
    },
    controlStyle: {
      color: '#d4af37',
      borderColor: '#d4af37',
      borderWidth: 0.5
    },
    checkpointStyle: {
      color: '#4caf50',
      borderColor: '#d4af37'
    },
    label: {
      color: '#d4af37'
    },
    emphasis: {
      itemStyle: {
        color: '#a9334c'
      },
      controlStyle: {
        color: '#d4af37',
        borderColor: '#d4af37',
        borderWidth: 0.5
      },
      label: {
        color: '#d4af37'
      }
    }
  },
  visualMap: {
    color: ['#bf444c', '#d88273', '#f6efa6']
  },
  dataZoom: {
    backgroundColor: 'rgba(47,69,84,0)',
    dataBackgroundColor: 'rgba(255,255,255,0.3)',
    fillerColor: 'rgba(167,183,204,0.4)',
    handleColor: '#a7b7cc',
    handleSize: '100%',
    textStyle: {
      color: '#333'
    }
  },
  markPoint: {
    label: {
      color: '#eee'
    },
    emphasis: {
      label: {
        color: '#eee'
      }
    }
  }
}

// Register Theme
echarts.registerTheme('artDeco', artDecoTheme)

export function useChart(chartRef: Ref<HTMLElement | undefined>) {
  const chartInstance = ref<echarts.ECharts | null>(null)
  let resizeObserver: ResizeObserver | null = null

  const initChart = () => {
    if (!chartRef.value) return

    // Dispose if exists
    if (chartInstance.value) {
      chartInstance.value.dispose()
    }

    chartInstance.value = echarts.init(chartRef.value, 'artDeco', { renderer: 'canvas' })
  }

  const setOption = (option: any) => {
    if (!chartInstance.value) {
      initChart()
    }
    chartInstance.value?.setOption(option)
  }

  const resize = () => {
    chartInstance.value?.resize()
  }

  onMounted(() => {
    initChart()
    
    // Resize Handling
    resizeObserver = new ResizeObserver(() => {
        resize()
    })
    
    if (chartRef.value) {
        resizeObserver.observe(chartRef.value)
    }
    
    window.addEventListener('resize', resize)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', resize)
    resizeObserver?.disconnect()
    chartInstance.value?.dispose()
    chartInstance.value = null
  })

  return {
    chartInstance,
    setOption,
    resize
  }
}