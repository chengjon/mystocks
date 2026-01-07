<template>
  <div class="technical-analysis">

    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">TECHNICAL ANALYSIS</h1>
      <p class="page-subtitle">STOCK CHARTS | INDICATORS | PATTERNS</p>
    </div>

    <!-- Toolbar -->
    <div class="toolbar-section">
      <div class="toolbar-actions">
        <div class="search-section">
          <StockSearchBar
            v-model="selectedSymbol"
            @search="handleStockSearch"
            class="search"
          />
        </div>

        <div class="date-section">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="TO"
            start-placeholder="START DATE"
            end-placeholder="END DATE"
            :shortcuts="dateRangeShortcuts"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            class="date-picker"
            @change="handleDateRangeChange"
          />
        </div>

        <div class="period-section">
          <el-radio-group v-model="selectedPeriod" size="default" @change="fetchKlineData" class="period-selector">
            <el-radio-button label="day">DAY</el-radio-button>
            <el-radio-button label="week">WEEK</el-radio-button>
            <el-radio-button label="month">MONTH</el-radio-button>
          </el-radio-group>
        </div>

        <div class="button-group">
          <el-button type="info" :loading="loading" @click="refreshData">
            REFRESH
          </el-button>
          <el-button type="info" :loading="loading" @click="handleRetry">
            RETRY
          </el-button>
          <el-button type="info" @click="showIndicatorPanel = true">
            INDICATORS
          </el-button>
        </div>

        <el-dropdown @command="handleConfigCommand">
          <el-button type="info">
            CONFIGURATION
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="save">
                <el-icon><DocumentAdd /></el-icon>
                SAVE CURRENT CONFIG
              </el-dropdown-item>
              <el-dropdown-item command="load">
                <el-icon><FolderOpened /></el-icon>
                LOAD SAVED CONFIG
              </el-dropdown-item>
              <el-dropdown-item command="manage" divided>
                <el-icon><Files /></el-icon>
                MANAGE CONFIGS
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- K线图表区域 -->
    <div class="chart-section">
        title="K-LINE CHART"
        :symbol="chartData.symbol"
        :data="chartData.ohlcv"
        :indicators="chartData.indicators"
        :loading="loading"
        :last-update="lastUpdateTime"
        @indicator-remove="handleIndicatorRemove"
      />
    </div>

    <!-- 指标选择面板 -->
    <IndicatorPanel
      v-model="showIndicatorPanel"
      :selected-indicators="selectedIndicators"
      @add-indicator="handleAddIndicator"
      @remove-indicator="handleRemoveIndicator"
    />

    <!-- 数据统计信息 -->
    <div v-if="chartData.ohlcv" class="stats-section">
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-label">SYMBOL</span>
          <span class="stat-value mono">{{ chartData.symbol }} ({{ chartData.symbolName }})</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">DATA POINTS</span>
          <span class="stat-value mono gold">{{ chartData.ohlcv.dates.length }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">CALC TIME</span>
          <span class="stat-value mono">{{ chartData.calculationTime }}ms</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">INDICATORS</span>
          <span class="stat-value mono gold">{{ selectedIndicators.length }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck

import { ref, reactive, onMounted, watch, type Ref, computed } from 'vue'
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'
import { FolderOpened, DocumentAdd, Files, ArrowDown } from '@element-plus/icons-vue'
import StockSearchBar from '@/components/technical/StockSearchBar.vue'
import KLineChart from '@/components/technical/KLineChart.vue'
import IndicatorPanel from '@/components/technical/IndicatorPanel.vue'
import { ElButton } from 'element-plus'
import { indicatorService, handleIndicatorError } from '@/services/indicatorService.ts'
import { dataApi } from '@/api/index.js'
import { calculateTechnicalIndicators } from '@/utils/technicalIndicators.js'

// ============================================
// 类型定义
// ============================================

interface IndicatorParameters {
  [key: string]: number | string | boolean
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
  display_name: string
}

interface ChartIndicator {
  abbreviation: string
  parameters: IndicatorParameters
  outputs: IndicatorOutput[]
  panel_type: 'overlay' | 'separate'
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
    const response: KlineApiResponse = await dataApi.getKline({
      symbol: selectedSymbol.value,
      start_date: dateRange.value[0],
      end_date: dateRange.value[1],
      period: selectedPeriod.value,
      adjust: 'qfq'
    })

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
        const values = calculatedIndicators[key]
        return {
          abbreviation: key,
          parameters: {},
          outputs: [{
            output_name: key,
            values: values,
            display_name: key
          }],
          panel_type: (key.toLowerCase().includes('rsi') || key.toLowerCase().includes('macd') ? 'separate' : 'overlay') as 'overlay' | 'separate'
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
  } catch (error: any) {
    console.error('Failed to fetch kline data:', error)
    const errorMessage = error.response?.data?.msg || error.message || 'Failed to fetch K-line data'

    ElNotification({
      title: 'DATA LOAD FAILED',
      message: errorMessage,
      type: 'error',
      duration: 3000
    })

    if (error.response?.status === 404) {
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
    } catch (error: any) {
      console.error('Failed to save config:', error)
      const errorMessage = handleIndicatorError(error)
      ElMessage.error(`Save failed: ${errorMessage}`)
    }
  }).catch(() => {
    // User cancelled
  })
}

const handleLoadConfig = async (): Promise<void> => {
  try {
    const response: ConfigListResponse = await indicatorService.listConfigs()

    if (response.total_count === 0) {
      ElMessage.info('No saved configs available')
      return
    }

    const configOptions: ConfigOption[] = response.configs.map(config => ({
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
            .then((config: IndicatorConfig) => {
              selectedIndicators.value = config.indicators
              ElMessage.success(`Config "${config.name}" loaded`)

              if (chartData.ohlcv) {
                fetchKlineData()
              }

              done()
            })
            .catch((error: any) => {
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
  } catch (error: any) {
    console.error('Failed to list configs:', error)
    ElMessage.error('Failed to fetch config list')
  }
}

const handleManageConfigs = async (): Promise<void> => {
  try {
    const response: ConfigListResponse = await indicatorService.listConfigs()

    if (response.total_count === 0) {
      ElMessage.info('No saved configs available')
      return
    }

    const configListHtml = response.configs.map(config => `
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid rgba(212, 175, 55, 0.2);">
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
  } catch (error: any) {
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
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Failed to delete config:', error)
      ElMessage.error('Delete failed')
    }
  }
}

declare global {
  interface Window {
    deleteConfig: (configId: number) => Promise<void>
  }
}

window.deleteConfig = deleteConfig
</script>

<style scoped>

.technical-analysis {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
  padding: var(--space-xl);
  position: relative;
}

/* Background pattern */
.background-pattern {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    repeating-linear-gradient(
      45deg,
      transparent,
      transparent 10px,
      rgba(212, 175, 55, 0.02) 10px,
      rgba(212, 175, 55, 0.02) 11px
    );
  pointer-events: none;
  z-index: -1;
}

/* Page Header */
.page-header {
  text-align: center;
  margin-bottom: var(--space-lg);
}

.page-title {
  font-family: var(--font-display);
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--gold-primary);
  text-transform: uppercase;
  letter-spacing: 0.2em;
  margin: 0 0 var(--space-md) 0;
  text-shadow: 0 0 20px rgba(212, 175, 55, 0.3);
}

.page-subtitle {
  font-family: var(--font-body);
  font-size: 1rem;
  color: var(--silver-muted);
  letter-spacing: 0.1em;
  margin: 0;
}

/* Toolbar Section */
.toolbar-section {
  background: var(--bg-card);
  border: 1px solid var(--gold-dim);
  padding: var(--space-lg);
  position: relative;
  overflow: hidden;
}

.toolbar-section::before {
  content: '';
  position: absolute;
  top: 4px;
  left: 4px;
  right: 4px;
  bottom: 4px;
  border: 1px solid var(--gold-dim);
  pointer-events: none;
  opacity: 0.3;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
  flex-wrap: wrap;
}

.search-section,
.date-section,
.period-section {
  display: flex;
  align-items: center;
}

  width: 300px;
}

  width: 320px;
}

.period-selector {
  font-family: var(--font-body);
  font-size: 0.875rem;
}

.button-group {
  display: flex;
  gap: var(--space-md);
  margin-left: auto;
}

/* Chart Section */
.chart-section {
  flex: 1;
  min-height: 600px;
}

/* Stats Section */
.stats-section {
  background: var(--bg-card);
  border: 1px solid var(--gold-dim);
  padding: var(--space-lg);
  position: relative;
  overflow: hidden;
}

.stats-section::before {
  content: '';
  position: absolute;
  top: 4px;
  left: 4px;
  right: 4px;
  bottom: 4px;
  border: 1px solid var(--gold-dim);
  pointer-events: none;
  opacity: 0.3;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-lg);
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  align-items: center;
}

.stat-label {
  font-family: var(--font-body);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--silver-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.stat-value {
  font-family: var(--font-mono);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--silver-text);
}

.stat-value.mono {
  font-family: var(--font-mono);
}

.stat-value.gold {
  color: var(--gold-primary);
}

/* Element Plus overrides */
:deep(.el-date-editor) {
  background: var(--bg-primary);
  border: 1px solid var(--gold-dim);
  color: var(--silver-text);
}

:deep(.el-date-editor__inner) {
  background: transparent;
  color: var(--silver-text);
  font-family: var(--font-mono);
}

:deep(.el-date-editor:hover) {
  border-color: var(--gold-primary);
}

:deep(.el-radio-button__inner) {
  background: var(--bg-primary);
  border: 1px solid var(--gold-dim);
  color: var(--silver-text);
  font-family: var(--font-body);
  font-size: 0.875rem;
  text-transform: uppercase;
}

:deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: var(--gold-primary);
  border-color: var(--gold-primary);
  color: var(--bg-primary);
}

:deep(.el-dropdown-menu) {
  background: var(--bg-card);
  border: 1px solid var(--gold-dim);
}

:deep(.el-dropdown-menu__item) {
  color: var(--silver-text);
  font-family: var(--font-body);
}

:deep(.el-dropdown-menu__item:hover) {
  background: rgba(212, 175, 55, 0.1);
  color: var(--gold-primary);
}

:deep(.el-empty) {
  --el-empty-description-color: var(--silver-muted);
}

:deep(.el-empty__description) {
  color: var(--silver-muted);
  font-family: var(--font-body);
}
</style>
