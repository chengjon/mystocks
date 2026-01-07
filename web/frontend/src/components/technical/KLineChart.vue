<template>
  <div class="kline-chart-container">
    <!-- 图表加载状态 (增强版: 骨架屏 + 进度指示器) -->
    <ChartLoadingSkeleton
      v-if="loading"
      :show-progress="showLoadingProgress"
      :progress="loadingProgress"
      :loading-text="loadingText"
      :sub-text="loadingSubText"
    />

    <!-- 图表主容器 -->
    <div
      v-show="!loading"
      ref="chartContainer"
      class="chart-canvas"
    />

    <!-- 图表工具栏 -->
    <div v-show="!loading" class="chart-toolbar">
      <el-space wrap>
        <!-- 周期切换 -->
        <el-radio-group v-model="currentPeriod" size="small" @change="handlePeriodChange">
          <el-radio-button label="1min">分时</el-radio-button>
          <el-radio-button label="5min">5分钟</el-radio-button>
          <el-radio-button label="15min">15分钟</el-radio-button>
          <el-radio-button label="30min">30分钟</el-radio-button>
          <el-radio-button label="60min">60分钟</el-radio-button>
          <el-radio-button label="1day">日线</el-radio-button>
        </el-radio-group>

        <!-- 图表类型 -->
        <el-dropdown trigger="click" @command="handleChartTypeChange">
          <el-button size="small">
            {{ currentChartType }}
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="candle_solid">蜡烛图</el-dropdown-item>
              <el-dropdown-item command="candle_stroke">空心蜡烛</el-dropdown-item>
              <el-dropdown-item command="candle_up_stroke">涨空心跌实心</el-dropdown-item>
              <el-dropdown-item command="ohlc">OHLC</el-dropdown-item>
              <el-dropdown-item command="area">面积图</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!-- 主图指标管理 (增强版: 可见性切换) -->
        <el-tag
          v-for="(indicator, index) in overlayIndicators"
          :key="`overlay-${index}`"
          closable
          size="small"
          :type="indicator.visible ? 'info' : 'warning'"
          :style="{ opacity: indicator.visible ? 1 : 0.5 }"
          @close="handleRemoveIndicator(index)"
        >
          <el-icon
            :size="14"
            style="margin-right: 4px; cursor: pointer;"
            @click.stop="handleToggleIndicator(indicator)"
          >
            <component :is="indicator.visible ? View : Hide" />
          </el-icon>
          {{ indicator.name }}
        </el-tag>

        <!-- 分隔线 -->
        <el-divider direction="vertical" />

        <!-- 缩放控制 -->
        <el-button-group size="small">
          <el-button @click="zoomOut">-</el-button>
          <el-button disabled>{{ zoomLevels[currentZoomIndex] }}x</el-button>
          <el-button @click="zoomIn">+</el-button>
        </el-button-group>

        <!-- 平移控制 -->
        <el-button-group size="small">
          <el-button @click="panChart('left')">◀</el-button>
          <el-button @click="panChart('right')">▶</el-button>
        </el-button-group>

        <!-- 重置缩放 -->
        <el-button
          size="small"
          :icon="Refresh"
          @click="resetChart"
        >
          重置
        </el-button>

        <!-- 性能监控开关 -->
        <el-tooltip content="性能监控" placement="bottom">
          <el-button
            size="small"
            @click="togglePerformanceMonitor"
          >
            <el-icon><Odometer /></el-icon>
          </el-button>
        </el-tooltip>
      </el-space>
    </div>

    <!-- 性能监控面板 -->
    <PerformanceMonitor
      v-if="showPerformanceMonitor"
      ref="performanceMonitor"
      :default-enabled="true"
      :show-history="true"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick, computed } from 'vue'
import { init, dispose } from 'klinecharts'
import { Refresh, ArrowDown, View, Hide, Odometer } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import ChartLoadingSkeleton from '@/components/common/ChartLoadingSkeleton.vue'
import PerformanceMonitor from '@/components/common/PerformanceMonitor.vue'

// ============================================================================
// Type Definitions & Constants
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

// Performance constants
const RENDER_BATCH_SIZE = 500
const ENABLE_DATA_CACHING = true
const CACHE_MAX_SIZE = 10
const DEBOUNCE_DELAY = 300
const ZOOM_LEVELS = [0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0]
const PAN_DISTANCE = 100
const ANIMATION_DURATION = 300

// ============================================================================
// Props & Emits
// ============================================================================

const props = defineProps({
  ohlcvData: {
    type: Object,
    required: true,
    validator: (value) => {
      // Enhanced validation
      if (!value || typeof value !== 'object') {
        console.error('[KLineChart] Invalid data: not an object')
        return false
      }

      const requiredFields = ['dates', 'open', 'high', 'low', 'close', 'volume']
      for (const field of requiredFields) {
        if (!Array.isArray(value[field])) {
          console.error(`[KLineChart] Invalid data: ${field} is not an array`)
          return false
        }
      }

      // Validate array lengths match
      const length = value.dates.length
      for (const field of requiredFields) {
        if (value[field].length !== length) {
          console.error(`[KLineChart] Invalid data: ${field} length mismatch`)
          return false
        }
      }

      return true
    }
  },
  indicators: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['indicator-remove', 'indicator-toggle'])

// ============================================================================
// Reactive State
// ============================================================================

const chartContainer = ref(null)
const chart = ref(null)
const currentPeriod = ref('1day')
const currentChartType = ref('蜡烛图')
const overlayIndicators = ref([])

// Performance optimization state
const dataCache = ref(new Map())
const lastDataHash = ref('')
const currentZoomIndex = ref(2) // Default to 1.0x

// Loading state
const loadingProgress = ref(0)
const showLoadingProgress = ref(false)
const loadingText = ref('加载数据中...')
const loadingSubText = ref('')

// Performance Monitor
const performanceMonitor = ref(null)
const showPerformanceMonitor = ref(false)

// Debounce timer
const debounceTimer = ref(null)

// Action subscriptions
const actionSubscriptions = ref([])

// ============================================================================
// Chart Configuration
// ============================================================================

const CHART_STYLES = {
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
        backgroundColor: 'rgba(17, 17, 17, .8)'
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

const CHART_INIT_OPTIONS = {
  locale: 'zh-CN',
  timezone: 'Asia/Shanghai',
  styles: CHART_STYLES
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Generate a unique hash for data to detect changes
 * @param {OHLCVData} ohlcvData
 * @returns {string}
 */
const generateDataHash = (ohlcvData) => {
  try {
    const { dates, open, high, low, close, volume } = ohlcvData
    const length = dates?.length || 0
    const firstDate = length > 0 ? new Date(dates[0]).getTime() : 0
    const lastDate = length > 0 ? new Date(dates[length - 1]).getTime() : 0
    const firstClose = length > 0 ? close[0] : 0
    const lastClose = length > 0 ? close[length - 1] : 0

    return `${length}-${firstDate}-${lastDate}-${firstClose}-${lastClose}`
  } catch (error) {
    console.error('[KLineChart] Error generating data hash:', error)
    return Date.now().toString()
  }
}

/**
 * Convert OHLCV data to klinecharts format
 * Optimized for performance with pre-allocation
 * @param {OHLCVData} ohlcvData
 * @returns {Array}
 */
const convertToKlineData = (ohlcvData) => {
  try {
    const { dates, open, high, low, close, volume, turnover } = ohlcvData
    const length = dates.length
    const klineData = new Array(length)

    // Optimized loop with pre-allocated array
    for (let i = 0; i < length; i++) {
      const item = {
        timestamp: new Date(dates[i]).getTime(),
        open: open[i],
        high: high[i],
        low: low[i],
        close: close[i],
        volume: volume[i]
      }

      // Optional turnover field
      if (turnover && turnover.length > i) {
        item.turnover = turnover[i]
      }

      klineData[i] = item
    }

    return klineData
  } catch (error) {
    console.error('[KLineChart] Error converting kline data:', error)
    return []
  }
}

/**
 * Get indicator color by index
 * @param {number} index
 * @returns {string}
 */
const getIndicatorColor = (index) => {
  const colors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#00BCD4', '#FF5722']
  return colors[index % colors.length]
}

/**
 * Manage data cache with size limit
 * @param {string} hash
 * @param {Array} data
 */
const manageCache = (hash, data) => {
  if (!ENABLE_DATA_CACHING) return

  // Clear old cache if size limit reached
  if (dataCache.value.size >= CACHE_MAX_SIZE) {
    const firstKey = dataCache.value.keys().next().value
    dataCache.value.delete(firstKey)
  }

  dataCache.value.set(hash, data)
}

/**
 * Debounce function for performance
 * @param {Function} fn
 * @param {number} delay
 */
const debounce = (fn, delay) => {
  return (...args) => {
    if (debounceTimer.value) {
      clearTimeout(debounceTimer.value)
    }
    debounceTimer.value = setTimeout(() => {
      fn(...args)
    }, delay)
  }
}

// ============================================================================
// Chart Initialization & Cleanup
// ============================================================================

/**
 * Initialize the chart instance
 */
const initChart = async () => {
  await nextTick()

  if (!chartContainer.value) {
    console.error('[KLineChart] Chart container not found')
    return
  }

  try {
    // Initialize klinecharts instance
    chart.value = init(chartContainer.value, CHART_INIT_OPTIONS)

    // Subscribe to chart actions for better UX
    subscribeToChartActions()

    // Create default volume indicator
    chart.value.createIndicator('VOL', false)

    // Load initial data
    if (props.ohlcvData) {
      updateChartData(props.ohlcvData)
    }

    // Load initial indicators
    if (props.indicators?.length > 0) {
      updateIndicators(props.indicators)
    }
  } catch (error) {
    console.error('[KLineChart] Failed to initialize chart:', error)
    ElMessage.error('图表初始化失败')
  }
}

/**
 * Subscribe to chart actions for monitoring
 */
const subscribeToChartActions = () => {
  if (!chart.value) return

  try {
    // Subscribe to zoom events
    const zoomUnsub = chart.value.subscribeAction('onZoom', (data) => {
      console.log('[KLineChart] Zoom event:', data)
    })

    // Subscribe to scroll events
    const scrollUnsub = chart.value.subscribeAction('onScroll', (data) => {
      console.log('[KLineChart] Scroll event:', data)
    })

    // Store subscriptions for cleanup
    actionSubscriptions.value.push(zoomUnsub, scrollUnsub)
  } catch (error) {
    console.error('[KLineChart] Error subscribing to actions:', error)
  }
}

/**
 * Unsubscribe from chart actions
 */
const unsubscribeFromChartActions = () => {
  actionSubscriptions.value.forEach(unsubscribe => {
    try {
      if (typeof unsubscribe === 'function') {
        unsubscribe()
      }
    } catch (error) {
      console.error('[KLineChart] Error unsubscribing from action:', error)
    }
  })
  actionSubscriptions.value = []
}

/**
 * Cleanup on unmount
 */
const cleanup = () => {
  // Clear debounce timer
  if (debounceTimer.value) {
    clearTimeout(debounceTimer.value)
    debounceTimer.value = null
  }

  // Unsubscribe from actions
  unsubscribeFromChartActions()

  // Clear cache
  dataCache.value.clear()

  // Dispose chart
  if (chart.value && chartContainer.value) {
    try {
      dispose(chartContainer.value)
    } catch (error) {
      console.error('[KLineChart] Error disposing chart:', error)
    }
    chart.value = null
  }
}

// ============================================================================
// Data Management
// ============================================================================

/**
 * Update chart data with progressive loading
 * @param {OHLCVData} ohlcvData
 */
const updateChartData = async (ohlcvData) => {
  if (!chart.value || !ohlcvData) return

  try {
    const dataHash = generateDataHash(ohlcvData)

    // Check cache
    if (ENABLE_DATA_CACHING && dataHash === lastDataHash.value) {
      console.log('[KLineChart] Using cached data, skipping update')
      return
    }

    // Convert data
    const klineData = convertToKlineData(ohlcvData)
    const totalPoints = klineData.length

    if (totalPoints === 0) {
      console.warn('[KLineChart] No data to display')
      return
    }

    // Update loading text
    loadingText.value = `加载 ${totalPoints} 个数据点`
    loadingSubText.value = totalPoints > RENDER_BATCH_SIZE
      ? `大数据集将分批渲染以优化性能`
      : ''

    // Render based on data size
    if (totalPoints > RENDER_BATCH_SIZE) {
      await renderDataInBatches(klineData, totalPoints)
    } else {
      // Small dataset - direct render
      chart.value.applyNewData(klineData)
      loadingProgress.value = 100
    }

    // Update cache
    lastDataHash.value = dataHash
    manageCache(dataHash, klineData)
  } catch (error) {
    console.error('[KLineChart] Failed to update chart data:', error)
    ElMessage.error('图表数据更新失败')
    showLoadingProgress.value = false
  }
}

/**
 * Render data in batches for better performance
 * Uses applyNewData for first batch, applyMoreData for subsequent batches
 * @param {Array} klineData
 * @param {number} totalPoints
 */
const renderDataInBatches = async (klineData, totalPoints) => {
  showLoadingProgress.value = true
  console.log(`[KLineChart] Rendering ${totalPoints} data points in batches...`)

  const startTime = performance.now()

  const totalBatches = Math.ceil(totalPoints / RENDER_BATCH_SIZE)

  // First batch - apply new data (replaces existing)
  const firstBatch = klineData.slice(0, RENDER_BATCH_SIZE)
  chart.value.applyNewData(firstBatch)

  loadingProgress.value = Math.round((RENDER_BATCH_SIZE / totalPoints) * 100)
  loadingSubText.value = `已加载 ${RENDER_BATCH_SIZE}/${totalPoints} 个数据点`

  // Subsequent batches - apply more data (appends)
  for (let i = 1; i < totalBatches; i++) {
    const startIdx = i * RENDER_BATCH_SIZE
    const endIdx = Math.min((i + 1) * RENDER_BATCH_SIZE, totalPoints)
    const batch = klineData.slice(startIdx, endIdx)

    // Use applyMoreData for better performance (appends instead of replaces)
    await new Promise(resolve => {
      setTimeout(() => {
        chart.value.applyMoreData(batch)
        loadingProgress.value = Math.round((endIdx / totalPoints) * 100)
        loadingSubText.value = `已加载 ${endIdx}/${totalPoints} 个数据点`
        resolve()
      }, 50)
    })
  }

  const endTime = performance.now()
  const renderTime = endTime - startTime

  console.log(`[KLineChart] Rendered ${totalPoints} points in ${renderTime.toFixed(2)}ms`)

  // Update performance monitor
  if (performanceMonitor.value && showPerformanceMonitor.value) {
    performanceMonitor.value.updateMetrics({
      calculationTime: renderTime,
      dataPointCount: totalPoints
    })
  }

  // Render complete
  loadingProgress.value = 100
  loadingSubText.value = '渲染完成'

  // Delay hiding progress bar
  setTimeout(() => {
    showLoadingProgress.value = false
    loadingSubText.value = ''
  }, 500)
}

// ============================================================================
// Indicator Management
// ============================================================================

/**
 * Update indicators
 * @param {Array<Indicator>} indicators
 */
const updateIndicators = (indicators) => {
  if (!chart.value || !indicators) return

  try {
    // Preserve existing indicator visibility states
    const existingIndicators = new Map()
    overlayIndicators.value.forEach(ind => {
      existingIndicators.set(ind.name, ind.visible !== false)
    })

    // Clear existing overlay indicators (keep VOL)
    overlayIndicators.value = []

    // Add new indicators
    indicators.forEach((indicator, index) => {
      if (indicator.panel_type === 'overlay') {
        // Overlay indicators (on main chart)
        const indicatorName = indicator.abbreviation.toUpperCase()

        // Handle multiple outputs
        indicator.outputs.forEach((output) => {
          const wasVisible = existingIndicators.get(output.display_name)

          chart.value.createIndicator(
            indicatorName,
            false,
            { id: 'candle_pane' }
          )

          overlayIndicators.value.push({
            name: output.display_name,
            index: index,
            visible: wasVisible !== false,
            color: getIndicatorColor(index)
          })
        })
      } else if (indicator.panel_type === 'separate') {
        // Separate pane indicators
        const indicatorName = indicator.abbreviation.toUpperCase()
        chart.value.createIndicator(indicatorName, false)
      }
    })
  } catch (error) {
    console.error('[KLineChart] Failed to update indicators:', error)
    ElMessage.error('指标更新失败')
  }
}

/**
 * Toggle indicator visibility
 * @param {Object} indicator
 */
const handleToggleIndicator = (indicator) => {
  if (!chart.value) return

  try {
    indicator.visible = !indicator.visible

    // Note: klinecharts v9 doesn't have direct visibility toggle API
    // Workaround: Remove and recreate indicator, or use style overrides
    // This is a placeholder for future implementation

    emit('indicator-toggle', {
      name: indicator.name,
      visible: indicator.visible
    })

    ElMessage.success(`${indicator.name} ${indicator.visible ? '已显示' : '已隐藏'}`)
  } catch (error) {
    console.error('[KLineChart] Failed to toggle indicator:', error)
    ElMessage.error('指标切换失败')
  }
}

/**
 * Remove indicator
 * @param {number} index
 */
const handleRemoveIndicator = (index) => {
  emit('indicator-remove', index)
}

// ============================================================================
// Chart Controls
// ============================================================================

/**
 * Toggle performance monitor visibility
 */
const togglePerformanceMonitor = () => {
  showPerformanceMonitor.value = !showPerformanceMonitor.value
  console.log('[KLineChart] Performance monitor:', showPerformanceMonitor.value ? 'enabled' : 'disabled')
}

/**
 * Measure execution time of a function
 * @param {Function} fn - Function to measure
 * @param {string} metricName - Metric name for logging
 * @returns {Promise<any>} - Function result with timing
 */
const measurePerformance = async (fn, metricName = 'operation') => {
  const startTime = performance.now()
  try {
    const result = await fn()
    const endTime = performance.now()
    const executionTime = endTime - startTime

    console.log(`[KLineChart] ${metricName} took ${executionTime.toFixed(2)}ms`)

    // Update performance monitor if available
    if (performanceMonitor.value && showPerformanceMonitor.value) {
      performanceMonitor.value.updateMetrics({
        calculationTime: executionTime
      })
    }

    return result
  } catch (error) {
    const endTime = performance.now()
    const executionTime = endTime - startTime
    console.error(`[KLineChart] ${metricName} failed after ${executionTime.toFixed(2)}ms:`, error)
    throw error
  }
}

/**
 * Handle period change
 * @param {string} period
 */
const handlePeriodChange = (period) => {
  console.log('[KLineChart] Period changed to:', period)
  // TODO: Implement period switching (requires data reload)
  ElMessage.info('周期切换功能即将实现')
}

/**
 * Handle chart type change
 * @param {string} type
 */
const handleChartTypeChange = (type) => {
  if (!chart.value) return

  const typeMap = {
    'candle_solid': '蜡烛图',
    'candle_stroke': '空心蜡烛',
    'candle_up_stroke': '涨空心跌实心',
    'ohlc': 'OHLC',
    'area': '面积图'
  }

  try {
    chart.value.setStyles({
      candle: {
        type: type
      }
    })

    currentChartType.value = typeMap[type] || '蜡烛图'
    ElMessage.success(`已切换到${currentChartType.value}`)
  } catch (error) {
    console.error('[KLineChart] Failed to change chart type:', error)
    ElMessage.error('图表类型切换失败')
  }
}

/**
 * Reset chart to default state
 */
const resetChart = () => {
  if (!chart.value) return

  try {
    // Use zoomAtDataIndex with proper parameters
    // Reset to scale 1.0 at the latest data point
    chart.value.zoomAtCoordinate(1.0, { x: 0, y: 0 }, ANIMATION_DURATION)
    currentZoomIndex.value = 2 // Reset to 1.0x

    // Scroll to real-time (latest data)
    chart.value.scrollToRealTime(ANIMATION_DURATION)

    ElMessage.success('图表已重置')
  } catch (error) {
    console.error('[KLineChart] Failed to reset chart:', error)
    ElMessage.error('图表重置失败')
  }
}

/**
 * Zoom in
 */
const zoomIn = () => {
  if (!chart.value) return

  if (currentZoomIndex.value < ZOOM_LEVELS.length - 1) {
    currentZoomIndex.value++
    const zoomLevel = ZOOM_LEVELS[currentZoomIndex.value]

    try {
      // Use zoomAtCoordinate with proper scale parameter
      chart.value.zoomAtCoordinate(zoomLevel, { x: 0, y: 0 }, ANIMATION_DURATION)
      ElMessage.success(`放大: ${zoomLevel}x`)
    } catch (error) {
      console.error('[KLineChart] Failed to zoom in:', error)
      ElMessage.error('放大失败')
    }
  } else {
    ElMessage.warning('已达到最大放大级别')
  }
}

/**
 * Zoom out
 */
const zoomOut = () => {
  if (!chart.value) return

  if (currentZoomIndex.value > 0) {
    currentZoomIndex.value--
    const zoomLevel = ZOOM_LEVELS[currentZoomIndex.value]

    try {
      // Use zoomAtCoordinate with proper scale parameter
      chart.value.zoomAtCoordinate(zoomLevel, { x: 0, y: 0 }, ANIMATION_DURATION)
      ElMessage.success(`缩小: ${zoomLevel}x`)
    } catch (error) {
      console.error('[KLineChart] Failed to zoom out:', error)
      ElMessage.error('缩小失败')
    }
  } else {
    ElMessage.warning('已达到最小缩小级别')
  }
}

/**
 * Pan chart in direction
 * @param {string} direction - 'left', 'right', 'up', 'down'
 */
const panChart = (direction) => {
  if (!chart.value) return

  try {
    const distance = 0
    let xAxisDistance = 0
    let yAxisDistance = 0

    switch (direction) {
      case 'left':
        xAxisDistance = -PAN_DISTANCE
        break
      case 'right':
        xAxisDistance = PAN_DISTANCE
        break
      case 'up':
        yAxisDistance = PAN_DISTANCE
        break
      case 'down':
        yAxisDistance = -PAN_DISTANCE
        break
    }

    // Use scrollByDistance for proper pan operation
    chart.value.scrollByDistance(
      { x: xAxisDistance, y: yAxisDistance },
      ANIMATION_DURATION
    )
  } catch (error) {
    console.error('[KLineChart] Failed to pan chart:', error)
    ElMessage.error('平移失败')
  }
}

// ============================================================================
// Lifecycle Hooks
// ============================================================================

onMounted(() => {
  initChart()
})

onBeforeUnmount(() => {
  cleanup()
})

// ============================================================================
// Watchers
// ============================================================================

// Watch data changes with debouncing
watch(
  () => props.ohlcvData,
  (newData) => {
    if (newData && chart.value) {
      debounce(() => {
        updateChartData(newData)
      }, DEBOUNCE_DELAY)()
    }
  },
  { deep: true }
)

// Watch indicator changes
watch(
  () => props.indicators,
  (newIndicators) => {
    if (newIndicators && chart.value) {
      updateIndicators(newIndicators)
    }
  },
  { deep: true }
)
</script>

<style scoped lang="scss">
.kline-chart-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
  background: #ffffff;

  .chart-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #909399;

    .el-icon {
      font-size: 48px;
      margin-bottom: 16px;
    }

    p {
      font-size: 14px;
    }
  }

  .chart-canvas {
    flex: 1;
    width: 100%;
    min-height: 400px;
  }

  .chart-toolbar {
    padding: 12px;
    border-top: 1px solid #e4e7ed;
    background: #f5f7fa;
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
  }
}

// Responsive design
@media (max-width: 768px) {
  .kline-chart-container {
    .chart-canvas {
      min-height: 300px;
    }

    .chart-toolbar {
      padding: 8px;

      :deep(.el-radio-group) {
        flex-wrap: wrap;
      }
    }
  }
}
</style>
