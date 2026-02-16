/**
 * KLineChart Configuration Module
 * Centralized configuration for chart styles, initialization options, and constants
 */

// ============================================================================
// Performance Constants
// ============================================================================

export const RENDER_BATCH_SIZE = 500
export const ENABLE_DATA_CACHING = true
export const CACHE_MAX_SIZE = 10
export const DEBOUNCE_DELAY = 300
export const ANIMATION_DURATION = 300
export const PAN_DISTANCE = 100

// ============================================================================
// Zoom Configuration
// ============================================================================

export const ZOOM_LEVELS = [0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0]

// ============================================================================
// Type Definitions
// ============================================================================

/**
 * @typedef {Object} OHLCVData
 * @property {Array<string|Date>} dates - Date array
 * @property {Array<number>} open - Open prices
 * @property {Array<number>} high - High prices
 * @property {Array<number>} low - Low prices
 * @property {Array<number>} close - Close prices
 * @property {Array<number>} volume - Volume data
 * @property {Array<number>} [turnover] - Optional turnover data
 */

/**
 * @typedef {Object} Indicator
 * @property {string} abbreviation - Indicator abbreviation
 * @property {string} panel_type - 'overlay' or 'separate'
 * @property {Array} outputs - Indicator outputs
 * @property {string} [display_name] - Display name
 */

// ============================================================================
// Chart Styles Configuration
// ============================================================================

export const CHART_STYLES = {
  grid: {
    show: true,
    horizontal: {
      show: true,
      size: 1,
      color: '#e0e0e0',
      style: 'dashed'
    },
    vertical: {
      show: true,
      size: 1,
      color: '#e0e0e0',
      style: 'dashed'
    }
  },
  candle: {
    type: 'candle_solid',
    bar: {
      upColor: '#ef5350',
      downColor: '#26a69a',
      noChangeColor: '#888888'
    },
    tooltip: {
      showRule: 'always',
      showType: 'standard',
      labels: ['时间: ', '开: ', '收: ', '高: ', '低: ', '成交量: '],
      values: null,
      defaultValue: 'n/a',
      rect: {
        paddingLeft: 8,
        paddingRight: 8,
        paddingTop: 8,
        paddingBottom: 8,
        offsetLeft: 12,
        offsetTop: 12,
        borderRadius: 4,
        borderSize: 1,
        borderColor: '#3f4254',
        backgroundColor: 'rgb(17 17 17 / .8)'
      },
      text: {
        size: 12,
        family: 'Helvetica Neue',
        weight: 'normal',
        color: '#D9D9D9'
      }
    }
  },
  indicator: {
    tooltip: {
      showRule: 'always',
      showType: 'standard',
      showName: true,
      showParams: true,
      defaultValue: 'n/a',
      text: {
        size: 12,
        family: 'Helvetica Neue',
        weight: 'normal',
        color: '#D9D9D9',
        marginTop: 6,
        marginRight: 8,
        marginBottom: 0,
        marginLeft: 8
      }
    }
  },
  xAxis: {
    show: true,
    height: null,
    axisLine: {
      show: true,
      color: '#888888',
      size: 1
    },
    tickText: {
      show: true,
      color: '#D9D9D9',
      family: 'Helvetica Neue',
      weight: 'normal',
      size: 12,
      paddingTop: 3,
      paddingBottom: 6
    },
    tickLine: {
      show: true,
      size: 1,
      length: 3,
      color: '#888888'
    }
  },
  yAxis: {
    show: true,
    width: null,
    position: 'right',
    type: 'normal',
    inside: false,
    reverse: false,
    axisLine: {
      show: true,
      color: '#888888',
      size: 1
    },
    tickText: {
      show: true,
      color: '#D9D9D9',
      family: 'Helvetica Neue',
      weight: 'normal',
      size: 12,
      paddingLeft: 3,
      paddingRight: 6
    },
    tickLine: {
      show: true,
      size: 1,
      length: 3,
      color: '#888888'
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
        color: '#888888'
      },
      text: {
        show: true,
        color: '#D9D9D9',
        size: 12,
        family: 'Helvetica Neue',
        weight: 'normal',
        paddingLeft: 4,
        paddingRight: 4,
        paddingTop: 4,
        paddingBottom: 4,
        borderSize: 1,
        borderColor: '#505050',
        borderRadius: 2,
        backgroundColor: '#505050'
      }
    },
    vertical: {
      show: true,
      line: {
        show: true,
        style: 'dashed',
        dashValue: [4, 2],
        size: 1,
        color: '#888888'
      },
      text: {
        show: true,
        color: '#D9D9D9',
        size: 12,
        family: 'Helvetica Neue',
        weight: 'normal',
        paddingLeft: 4,
        paddingRight: 4,
        paddingTop: 4,
        paddingBottom: 4,
        borderSize: 1,
        borderColor: '#505050',
        borderRadius: 2,
        backgroundColor: '#505050'
      }
    }
  }
}

// ============================================================================
// Chart Initialization Options
// ============================================================================

export const CHART_INIT_OPTIONS = {
  locale: 'zh-CN',
  timezone: 'Asia/Shanghai',
  styles: CHART_STYLES
}

// ============================================================================
// Indicator Colors
// ============================================================================

export const INDICATOR_COLORS = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#00BCD4', '#FF5722']

/**
 * Get indicator color by index
 * @param {number} index
 * @returns {string}
 */
export const getIndicatorColor = (index: number): string => {
  return INDICATOR_COLORS[index % INDICATOR_COLORS.length]
}
