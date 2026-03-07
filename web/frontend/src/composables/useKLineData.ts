import { ref, computed, type Ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  RENDER_BATCH_SIZE,
  ENABLE_DATA_CACHING,
  CACHE_MAX_SIZE,
  DEBOUNCE_DELAY
} from '@/components/technical/config/klineChartConfig'

interface OHLCVData {
  dates: string[]
  open: number[]
  high: number[]
  low: number[]
  close: number[]
  volume: number[]
  turnover?: number[]
  [key: string]: unknown
}

interface KLineDataItem {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
  turnover?: number
}

interface ChartRef {
  applyNewData: (data: KLineDataItem[]) => void
  applyMoreData: (data: KLineDataItem[]) => void
}

interface Props {
  ohlcvData?: OHLCVData
  [key: string]: unknown
}

/**
 * Composable for K-Line chart data management
 * Handles data conversion, caching, batching, and chart updates
 * @param {Ref} chartRef - Reference to klinecharts instance
 * @param {Object} props - Component props containing ohlcvData
 * @returns {Object} Data management functions and state
 */
export function useKLineData(chartRef: Ref<ChartRef | null>, _props: Props) {
  // State
  const dataCache = ref(new Map<string, KLineDataItem[]>())
  const lastDataHash = ref('')
  const loadingProgress = ref(0)
  const showLoadingProgress = ref(false)
  const loadingText = ref('加载数据中...')
  const loadingSubText = ref('')
  const debounceTimer = ref<ReturnType<typeof setTimeout> | null>(null)

  /**
   * Generate a unique hash for data to detect changes
   * @param {Object} ohlcvData
   * @returns {string}
   */
  const generateDataHash = (ohlcvData: OHLCVData): string => {
    try {
      const { dates, close } = ohlcvData
      const length = dates?.length || 0
      const firstDate = length > 0 ? new Date(dates[0]).getTime() : 0
      const lastDate = length > 0 ? new Date(dates[length - 1]).getTime() : 0
      const firstClose = length > 0 ? close[0] : 0
      const lastClose = length > 0 ? close[length - 1] : 0

      return `${length}-${firstDate}-${lastDate}-${firstClose}-${lastClose}`
    } catch (error) {
      console.error('[useKLineData] Error generating data hash:', error)
      return Date.now().toString()
    }
  }

  /**
   * Convert OHLCV data to klinecharts format
   * @param {Object} ohlcvData
   * @returns {Array}
   */
  const convertToKlineData = (ohlcvData: OHLCVData): KLineDataItem[] => {
    try {
      const { dates, open, high, low, close, volume, turnover } = ohlcvData
      const length = dates.length
      const klineData: KLineDataItem[] = new Array(length)

      for (let i = 0; i < length; i++) {
        const item: KLineDataItem = {
          timestamp: new Date(dates[i]).getTime(),
          open: open[i],
          high: high[i],
          low: low[i],
          close: close[i],
          volume: volume[i]
        }

        if (turnover && turnover.length > i) {
          item.turnover = turnover[i]
        }

        klineData[i] = item
      }

      return klineData
    } catch (error) {
      console.error('[useKLineData] Error converting kline data:', error)
      return []
    }
  }

  /**
   * Manage data cache with size limit
   * @param {string} hash
   * @param {Array} data
   */
  const manageCache = (hash: string, data: KLineDataItem[]): void => {
    if (!ENABLE_DATA_CACHING) return

    if (dataCache.value.size >= CACHE_MAX_SIZE) {
      const firstKey = dataCache.value.keys().next().value
      if (firstKey !== undefined) {
        dataCache.value.delete(firstKey)
      }
    }

    dataCache.value.set(hash, data)
  }

  /**
   * Render data in batches for better performance
   * @param {Array} klineData
   * @param {number} totalPoints
   * @returns {Promise<void>}
   */
  const renderDataInBatches = async (klineData: KLineDataItem[], totalPoints: number): Promise<void> => {
    showLoadingProgress.value = true
    console.log(`[useKLineData] Rendering ${totalPoints} data points in batches...`)

    const startTime = performance.now()
    const totalBatches = Math.ceil(totalPoints / RENDER_BATCH_SIZE)

    const firstBatch = klineData.slice(0, RENDER_BATCH_SIZE)
    chartRef.value?.applyNewData(firstBatch)

    loadingProgress.value = Math.round((RENDER_BATCH_SIZE / totalPoints) * 100)
    loadingSubText.value = `已加载 ${RENDER_BATCH_SIZE}/${totalPoints} 个数据点`

    for (let i = 1; i < totalBatches; i++) {
      const startIdx = i * RENDER_BATCH_SIZE
      const endIdx = Math.min((i + 1) * RENDER_BATCH_SIZE, totalPoints)
      const batch = klineData.slice(startIdx, endIdx)

      await new Promise<void>(resolve => {
        setTimeout(() => {
          chartRef.value?.applyMoreData(batch)
          loadingProgress.value = Math.round((endIdx / totalPoints) * 100)
          loadingSubText.value = `已加载 ${endIdx}/${totalPoints} 个数据点`
          resolve()
        }, 50)
      })
    }

    const endTime = performance.now()
    const renderTime = endTime - startTime

    console.log(`[useKLineData] Rendered ${totalPoints} points in ${renderTime.toFixed(2)}ms`)

    loadingProgress.value = 100
    loadingSubText.value = '渲染完成'

    setTimeout(() => {
      showLoadingProgress.value = false
      loadingSubText.value = ''
    }, 500)
  }

  /**
   * Update chart data with progressive loading
   * @param {Object} ohlcvData
   * @returns {Promise<void>}
   */
  const updateChartData = async (ohlcvData: OHLCVData): Promise<void> => {
    if (!chartRef.value || !ohlcvData) return

    try {
      const dataHash = generateDataHash(ohlcvData)

      if (ENABLE_DATA_CACHING && dataHash === lastDataHash.value) {
        console.log('[useKLineData] Using cached data, skipping update')
        return
      }

      const klineData = convertToKlineData(ohlcvData)
      const totalPoints = klineData.length

      if (totalPoints === 0) {
        console.warn('[useKLineData] No data to display')
        return
      }

      loadingText.value = `加载 ${totalPoints} 个数据点`
      loadingSubText.value = totalPoints > RENDER_BATCH_SIZE
        ? `大数据集将分批渲染以优化性能`
        : ''

      if (totalPoints > RENDER_BATCH_SIZE) {
        await renderDataInBatches(klineData, totalPoints)
      } else {
        chartRef.value.applyNewData(klineData)
        loadingProgress.value = 100
      }

      lastDataHash.value = dataHash
      manageCache(dataHash, klineData)
    } catch (error) {
      console.error('[useKLineData] Failed to update chart data:', error)
      ElMessage.error('图表数据更新失败')
      showLoadingProgress.value = false
    }
  }

  /**
   * Debounce function for performance
   * @param {Function} fn
   * @param {number} delay
   * @returns {Function}
   */
  const debounce = <T extends unknown[]>(fn: (...args: T) => void, delay: number) => {
    return (...args: T) => {
      if (debounceTimer.value) {
        clearTimeout(debounceTimer.value)
      }
      debounceTimer.value = setTimeout(() => {
        fn(...args)
      }, delay)
    }
  }

  /**
   * Cleanup resources
   */
  const cleanup = () => {
    if (debounceTimer.value) {
      clearTimeout(debounceTimer.value)
      debounceTimer.value = null
    }
    dataCache.value.clear()
  }

  return {
    dataCache,
    lastDataHash,
    loadingProgress,
    showLoadingProgress,
    loadingText,
    loadingSubText,
    generateDataHash,
    convertToKlineData,
    manageCache,
    renderDataInBatches,
    updateChartData,
    debounce,
    cleanup
  }
}
