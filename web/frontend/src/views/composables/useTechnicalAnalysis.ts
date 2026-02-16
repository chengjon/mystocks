import { ref, reactive, onMounted, watch, type Ref, computed, onUnmounted } from 'vue'
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'
import StockSearchBar from '@/components/technical/StockSearchBar.vue'
import ProKLineChart from '@/components/market/ProKLineChart.vue'
import IndicatorPanel from '@/components/technical/IndicatorPanel.vue'
import { ElCard, ElButton, ElInput, ElDropdown, ElDropdownMenu, ElDropdownItem, ElIcon } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import { indicatorService, handleIndicatorError } from '@/services/indicatorService.ts'
import { dataApi } from '@/api/index.js'
import { calculateTechnicalIndicators } from '@/utils/technicalIndicators.js'

// ============================================
// 类型定义
// ============================================

interface IndicatorParameters {
  [key: string]: number | string | boolean | undefined
  timeperiod?: number
}

interface SelectedIndicator {
  abbreviation: string
  parameters: IndicatorParameters
}

interface OHLCVData {
  dates: string[]
  open: number[]
  high: number[]
  low: number[]
  close: number[]
  volume: number[]
}

interface IndicatorOutput {
  output_name: string
  values: (number | null)[]
  displayName: string
}

interface ChartIndicator {
  abbreviation: string
  parameters: IndicatorParameters
  outputs: IndicatorOutput[]
  panelType: 'overlay' | 'separate'
}

interface ChartData {
  symbol: string
  symbolName: string
  ohlcv: OHLCVData | null
  indicators: ChartIndicator[]
  calculationTime: number
}

interface DateRangeShortcut {
  text: string
  value: () => Date[]
}

interface KlineDataItem {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

interface KlineApiResponse {
  success: boolean
  data: KlineDataItem[]
  stock_code?: string
  stock_name?: string
  total?: number
}

interface IndicatorConfig {
  id: number
  name: string
  indicators: SelectedIndicator[]
}

interface ConfigListResponse {
  total_count: number
  configs: IndicatorConfig[]
}

interface ConfigOption {
  label: string
  value: number
}

declare global {
  interface Window {
    deleteConfig: (configId: number) => Promise<void>
  }
}

export function useTechnicalAnalysis() {
// @ts-nocheck

// ============================================
// 状态管理
// ============================================

const loading: Ref<boolean> = ref(false)
const selectedSymbol: Ref<string> = ref('')
const dateRange: Ref<string[]> = ref([])
const showIndicatorPanel: Ref<boolean> = ref(false)
const selectedPeriod: Ref<string> = ref('day')

const selectedIndicators: Ref<SelectedIndicator[]> = ref([
  { abbreviation: 'SMA', parameters: { timeperiod: 5 } },
  { abbreviation: 'SMA', parameters: { timeperiod: 10 } }
])

const chartData: ChartData = reactive({
  symbol: '',
  symbolName: '',
  ohlcv: null,
  indicators: [],
  calculationTime: 0
})

const lastUpdateTime = computed(() => {
  return chartData.ohlcv ? new Date() : undefined
})

// ============================================
// 方法定义
// ============================================

const handleRetry = async (): Promise<void> => {
  if (selectedSymbol.value && dateRange.value && dateRange.value.length === 2) {
    await fetchKlineData()
  } else {
    ElMessage.warning('Please select stock code and date range first')
  }
}

const dateRangeShortcuts: DateRangeShortcut[] = [
  {
    text: 'LAST 1 MONTH',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setMonth(start.getMonth() - 1)
      return [start, end]
    }
  },
  {
    text: 'LAST 3 MONTHS',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setMonth(start.getMonth() - 3)
      return [start, end]
    }
  },
  {
    text: 'LAST 6 MONTHS',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setMonth(start.getMonth() - 6)
      return [start, end]
    }
  },
  {
    text: 'LAST 1 YEAR',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setFullYear(start.getFullYear() - 1)
      return [start, end]
    }
  }
]

const handleStockSearch = async (symbol: string): Promise<void> => {
  selectedSymbol.value = symbol

  if (!dateRange.value || dateRange.value.length === 0) {
    const end = new Date()
    const start = new Date()
    start.setMonth(start.getMonth() - 3)
    dateRange.value = [
      start.toISOString().split('T')[0],
      end.toISOString().split('T')[0]
    ]
  }

  await fetchKlineData()
}

const handleDateRangeChange = (): void => {
  if (selectedSymbol.value && dateRange.value && dateRange.value.length === 2) {
    fetchKlineData()
  }
}

const refreshData = (): void => {
  if (selectedSymbol.value && dateRange.value && dateRange.value.length === 2) {
    fetchKlineData()
  } else {
    ElMessage.warning('Please select stock code and date range first')
  }
}

const fetchKlineData = async (): Promise<void> => {
  if (!selectedSymbol.value) {
    ElMessage.warning('Please enter stock code')
    return
  }

  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('Please select date range')
    return
  }

  loading.value = true

  try {
    const response = await dataApi.getKline({
      symbol: selectedSymbol.value,
      start_date: dateRange.value[0],
      end_date: dateRange.value[1],
      period: selectedPeriod.value,
      adjust: 'qfq'
    }) as unknown as KlineApiResponse

    if (response.success && response.data && response.data.length > 0) {
      const dates = response.data.map(item => item.date)
      const opens = response.data.map(item => item.open)
      const highs = response.data.map(item => item.high)
      const lows = response.data.map(item => item.low)
      const closes = response.data.map(item => item.close)
      const volumes = response.data.map(item => item.volume)

      chartData.symbol = response.stock_code || selectedSymbol.value
      chartData.symbolName = response.stock_name || selectedSymbol.value
      chartData.ohlcv = {
        dates,
        open: opens,
        high: highs,
        low: lows,
        close: closes,
        volume: volumes
      }

      const startTime = performance.now()
      const calculatedIndicators = calculateTechnicalIndicators(
        chartData.ohlcv,
        selectedIndicators.value
      )
      const endTime = performance.now()

      const indicatorsResult = Object.keys(calculatedIndicators).map(key => {
        const values = (calculatedIndicators as Record<string, (number | null)[]>)[key]
        return {
          abbreviation: key,
          parameters: {},
          outputs: [{
            output_name: key,
            values: values,
            displayName: key
          }],
          panelType: (key.toLowerCase().includes('rsi') || key.toLowerCase().includes('macd') ? 'separate' : 'overlay') as 'overlay' | 'separate'
        }
      })

      chartData.indicators = indicatorsResult
      chartData.calculationTime = Math.round(endTime - startTime)

      ElNotification({
        title: 'DATA LOADED SUCCESSFULLY',
        message: `${response.total} data points loaded, ${selectedIndicators.value.length} indicators calculated`,
        type: 'success',
        duration: 2000
      })
    } else {
      ElMessage.info('No historical data found for this stock')
      chartData.ohlcv = null
    }
  } catch (error: unknown) {
    console.error('Failed to fetch kline data:', error)
    const errorObj = error as Record<string, any>
    const errorMessage = errorObj?.response?.data?.msg || errorObj?.message || 'Failed to fetch K-line data'

    ElNotification({
      title: 'DATA LOAD FAILED',
      message: errorMessage as string,
      type: 'error',
      duration: 3000
    })

    if (errorObj?.response?.status === 404) {
      ElMessage.info('No historical data available in database')
    }
  } finally {
    loading.value = false
  }
}

const handleAddIndicator = (indicator: SelectedIndicator): void => {
  selectedIndicators.value.push(indicator)

  if (chartData.ohlcv) {
    fetchKlineData()
  }
}

const handleRemoveIndicator = (index: number): void => {
  selectedIndicators.value.splice(index, 1)

  if (chartData.ohlcv) {
    fetchKlineData()
  }
}

const handleIndicatorRemove = (indicatorIndex: number): void => {
  handleRemoveIndicator(indicatorIndex)
}

// ============================================
// 生命周期与监听器
// ============================================

onMounted((): void => {
  const cachedSymbol = localStorage.getItem('lastSelectedSymbol')
  const cachedDateRange = localStorage.getItem('lastDateRange')

  if (cachedSymbol) {
    selectedSymbol.value = cachedSymbol
  }

  if (cachedDateRange) {
    try {
      dateRange.value = JSON.parse(cachedDateRange)
    } catch (e) {
      console.error('Failed to parse cached date range:', e)
    }
  }
})

const saveToLocalStorage = (): void => {
  if (selectedSymbol.value) {
    localStorage.setItem('lastSelectedSymbol', selectedSymbol.value)
  }
  if (dateRange.value) {
    localStorage.setItem('lastDateRange', JSON.stringify(dateRange.value))
  }
}

watch([selectedSymbol, dateRange], saveToLocalStorage)

// ============================================
// 配置管理功能
// ============================================

const handleConfigCommand = async (command: string): Promise<void> => {
  switch (command) {
    case 'save':
      await handleSaveConfig()
      break
    case 'load':
      await handleLoadConfig()
      break
    case 'manage':
      await handleManageConfigs()
      break
  }
}

const handleSaveConfig = async (): Promise<void> => {
  if (selectedIndicators.value.length === 0) {
    ElMessage.warning('No indicators selected')
    return
  }

  ElMessageBox.prompt('Please enter config name', 'Save Indicator Config', {
    confirmButtonText: 'SAVE',
    cancelButtonText: 'CANCEL',
    inputPattern: /\S+/,
    inputErrorMessage: 'Config name cannot be empty'
  }).then(async ({ value }: { value: string }) => {
    try {
      await indicatorService.createConfig({
        name: value,
        indicators: selectedIndicators.value
      })

      ElMessage.success(`Config "${value}" saved`)
    } catch (error: unknown) {
      console.error('Failed to save config:', error)
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      ElMessage.error(`Save failed: ${errorMessage}`)
    }
  }).catch(() => {
    // User cancelled
  })
}

const handleLoadConfig = async (): Promise<void> => {
  try {
    const response = await indicatorService.listConfigs() as unknown as ConfigListResponse

    if (response.total_count === 0) {
      ElMessage.info('No saved configs available')
      return
    }

    const _configOptions: ConfigOption[] = response.configs.map(config => ({
      label: `${config.name} (${config.indicators.length} indicators)`,
      value: config.id
    }))

    ElMessageBox({
      title: 'LOAD CONFIG',
      message: 'Select a config to load',
      showCancelButton: true,
      confirmButtonText: 'LOAD',
      cancelButtonText: 'CANCEL',
      beforeClose: (action, instance, done) => {
        if (action === 'confirm') {
          const selectedConfigId = instance.inputValue
          if (!selectedConfigId) {
            ElMessage.warning('Please select a config')
            return
          }

          indicatorService.getConfig(parseInt(selectedConfigId))
            .then(((config: IndicatorConfig): void => {
              selectedIndicators.value = config.indicators
              ElMessage.success(`Config "${config.name}" loaded`)

              if (chartData.ohlcv) {
                fetchKlineData()
              }

              done()
            }) as any)
            .catch((error: unknown) => {
              console.error('Failed to load config:', error)
              ElMessage.error('Load failed')
            })
        } else {
          done()
        }
      }
    }).catch(() => {
      // User cancelled
    })
  } catch (error: unknown) {
    console.error('Failed to list configs:', error)
    ElMessage.error('Failed to fetch config list')
  }
}

const handleManageConfigs = async (): Promise<void> => {
  try {
    const response = await indicatorService.listConfigs() as unknown as ConfigListResponse

    if (response.total_count === 0) {
      ElMessage.info('No saved configs available')
      return
    }

    const configListHtml = response.configs.map(config => `
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid rgb(212 175 55 / 20%);">
        <div>
          <strong style="color: #D4AF37;">${config.name}</strong>
          <small style="color: #888; margin-left: 8px;">${config.indicators.length} indicators</small>
        </div>
        <div>
          <button class="el-button el-button--text el-button--small" style="color: #D4AF37;" onclick="deleteConfig(${config.id})">DELETE</button>
        </div>
      </div>
    `).join('')

    ElMessageBox({
      title: 'MANAGE CONFIGS',
      message: `<div style="background: #141414; padding: 16px; border: 1px solid #D4AF37;">${configListHtml}</div>`,
      dangerouslyUseHTMLString: true,
      showCancelButton: true,
      confirmButtonText: 'CLOSE',
      cancelButtonText: 'REFRESH',
      beforeClose: (action, instance, done) => {
        if (action === 'cancel') {
          handleManageConfigs()
        } else {
          done()
        }
      }
    })
  } catch (error: unknown) {
    console.error('Failed to manage configs:', error)
    ElMessage.error('Failed to fetch config list')
  }
}

const deleteConfig = async (configId: number): Promise<void> => {
  try {
    await ElMessageBox.confirm('Confirm delete this config?', 'Confirm', {
      type: 'warning'
    })

    await indicatorService.deleteConfig(configId)
    ElMessage.success('Config deleted')

    setTimeout(() => handleManageConfigs(), 300)
  } catch (error: unknown) {
    if (error !== 'cancel') {
      console.error('Failed to delete config:', error)
      ElMessage.error('Delete failed')
    }
  }
}

window.deleteConfig = deleteConfig

// Auto-generated: cleanup timers to prevent memory leaks
const _timer_1: ReturnType<typeof setTimeout> | null = null
onUnmounted(() => {
  if (_timer_1) clearTimeout(_timer_1)
})

  return {
    loading,
    selectedSymbol,
    dateRange,
    showIndicatorPanel,
    selectedPeriod,
    selectedIndicators,
    chartData,
    lastUpdateTime,
    handleRetry,
    dateRangeShortcuts,
    handleStockSearch,
    handleDateRangeChange,
    refreshData,
    fetchKlineData,
    handleAddIndicator,
    handleRemoveIndicator,
    handleIndicatorRemove,
    saveToLocalStorage,
    handleConfigCommand,
    handleSaveConfig,
    handleLoadConfig,
    handleManageConfigs,
    deleteConfig,
  }
}
