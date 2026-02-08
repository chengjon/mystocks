// web/frontend/src/styles/echarts-theme.ts

export const ARTDECO_THEME = {
  color: [
    '#D4AF37', // Metallic Gold
    '#FF5252', // Red (Up/Rise in Chinese context, or Down in global - context dependent, here Red)
    '#00E676', // Green (Down/Fall in Chinese context, or Up in global - here Green)
    '#2196f3', // Blue
    '#9c27b0', // Purple
    '#ff9800', // Orange
    '#795548', // Brown
    '#607d8b'  // Grey
  ],
  backgroundColor: 'transparent',
  textStyle: {
    fontFamily: '"Josefin Sans", sans-serif'
  },
  title: {
    textStyle: {
      color: '#F2F0E4', // Champagne Cream
      fontFamily: '"Marcellus", serif',
      fontWeight: 'bold'
    },
    subtextStyle: {
      color: '#888888' // Pewter
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
  candlestick: {
    itemStyle: {
      color: '#FF5252',       // Red (Rise)
      color0: '#00E676',      // Green (Fall)
      borderColor: '#FF5252',
      borderColor0: '#00E676'
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
    color: ['#D4AF37', '#FF5252', '#00E676', '#2196f3', '#9c27b0', '#ff9800', '#795548', '#607d8b'],
    label: {
      color: '#F2F0E4'
    }
  },
  categoryAxis: {
    axisLine: {
      show: true,
      lineStyle: {
        color: 'rgba(212, 175, 55, 0.3)' // Gold 30%
      }
    },
    axisTick: {
      show: true,
      lineStyle: {
        color: 'rgba(212, 175, 55, 0.3)'
      }
    },
    axisLabel: {
      show: true,
      color: '#888888'
    },
    splitLine: {
      show: false
    }
  },
  valueAxis: {
    axisLine: {
      show: true,
      lineStyle: {
        color: 'rgba(212, 175, 55, 0.3)'
      }
    },
    axisTick: {
      show: true,
      lineStyle: {
        color: 'rgba(212, 175, 55, 0.3)'
      }
    },
    axisLabel: {
      show: true,
      color: '#888888'
    },
    splitLine: {
      show: true,
      lineStyle: {
        color: ['rgba(255, 255, 255, 0.05)']
      }
    }
  },
  legend: {
    textStyle: {
      color: '#F2F0E4'
    }
  },
  tooltip: {
    backgroundColor: '#141414', // Rich Charcoal
    borderColor: '#D4AF37',     // Gold
    textStyle: {
      color: '#F2F0E4'
    },
    axisPointer: {
      lineStyle: {
        color: '#D4AF37',
        type: 'dashed'
      }
    }
  }
}