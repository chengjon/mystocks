<template>
  <div class="analysis-page">
    <!-- Art Deco Sidebar -->
    <ArtDecoSidebar :menu="menuItems" />

    <!-- Main Content Area -->
    <div class="main-content">
      <!-- Art Deco Header -->
      <ArtDecoHeader
        title="TECHNICAL ANALYSIS"
        subtitle="ADVANCED MARKET ANALYSIS & SIGNAL GENERATION"
        :show-breadcrumb="true"
        :breadcrumb-items="breadcrumbItems"
      />

      <!-- Analysis Configuration Panel -->
      <ArtDecoCard class="config-panel" title="ANALYSIS CONFIGURATION" :decorated="true">
        <template #header>
          <div class="config-header">
            <div class="header-icon">📊</div>
            <div class="header-content">
              <div class="header-title">ANALYSIS PARAMETERS</div>
              <div class="header-subtitle">CONFIGURE YOUR TECHNICAL ANALYSIS</div>
            </div>
            <ArtDecoButton
              variant="solid"
              @click="runAnalysis"
              :disabled="!isFormValid || loading"
              :loading="loading"
              class="run-button"
            >
              RUN ANALYSIS
            </ArtDecoButton>
          </div>
        </template>

        <div class="analysis-form">
          <div class="form-grid">
            <!-- Symbol Selection -->
            <div class="form-group">
              <label class="artdeco-label">SYMBOL</label>
              <ArtDecoInput
                v-model="form.symbol"
                placeholder="E.G: 600519"
                @input="handleSymbolChange"
              />
              <div class="input-hint" v-if="stockInfo.name">Stock: {{ stockInfo.name }}</div>
            </div>

            <!-- Analysis Type -->
            <div class="form-group">
              <label class="artdeco-label">ANALYSIS TYPE</label>
              <ArtDecoSelect
                v-model="form.analysisType"
                :options="analysisTypes"
              />
            </div>

            <!-- Time Period -->
            <div class="form-group">
              <label class="artdeco-label">TIME PERIOD</label>
              <ArtDecoSelect
                v-model="form.period"
                :options="timePeriods"
              />
            </div>

            <!-- Date Range -->
            <div class="form-group">
              <label class="artdeco-label">DATE RANGE</label>
              <div class="date-range-inputs">
                <ArtDecoInput
                  v-model="form.startDate"
                  type="date"
                  placeholder="START DATE"
                />
                <span class="date-separator">TO</span>
                <ArtDecoInput
                  v-model="form.endDate"
                  type="date"
                  placeholder="END DATE"
                />
              </div>
            </div>

            <!-- Technical Indicators Selection -->
            <div class="form-group full-width">
              <label class="artdeco-label">TECHNICAL INDICATORS</label>
              <div class="indicators-selection">
                <div
                  v-for="indicator in availableIndicators"
                  :key="indicator.key"
                  class="indicator-checkbox"
                >
                  <input
                    :id="`indicator-${indicator.key}`"
                    type="checkbox"
                    v-model="form.selectedIndicators"
                    :value="indicator.key"
                    class="checkbox-input"
                  />
                  <label :for="`indicator-${indicator.key}`" class="checkbox-label">
                    {{ indicator.label }}
                  </label>
                </div>
              </div>
            </div>

            <!-- Advanced Options -->
            <div class="form-group full-width" v-if="showAdvancedOptions">
              <label class="artdeco-label">ADVANCED OPTIONS</label>
              <div class="advanced-options">
                <div class="option-row">
                  <ArtDecoInput
                    v-model.number="form.lookbackPeriod"
                    type="number"
                    :min="10"
                    :max="500"
                    placeholder="LOOKBACK PERIOD"
                    label="Lookback Period"
                  />
                  <ArtDecoInput
                    v-model.number="form.signalThreshold"
                    type="number"
                    :min="0"
                    :max="1"
                    :step="0.01"
                    placeholder="SIGNAL THRESHOLD"
                    label="Signal Threshold"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="form-actions">
            <ArtDecoButton
              variant="secondary"
              @click="resetForm"
              :disabled="loading"
            >
              RESET
            </ArtDecoButton>

            <ArtDecoButton
              variant="rise"
              @click="toggleAdvancedOptions"
            >
              {{ showAdvancedOptions ? 'HIDE' : 'SHOW' }} ADVANCED
            </ArtDecoButton>

            <ArtDecoButton
              variant="outline"
              @click="loadPreset"
            >
              LOAD PRESET
            </ArtDecoButton>
          </div>
        </div>
      </ArtDecoCard>

      <!-- Analysis Results Area -->
      <div class="results-area" v-if="analysisResults">
        <!-- Technical Indicators Charts -->
        <div class="indicators-section">
          <div class="indicators-grid">
            <!-- Price Chart with Indicators -->
            <ArtDecoCard class="price-chart-card" title="PRICE CHART WITH INDICATORS" :decorated="true">
              <TimeSeriesChart
                title="PRICE & INDICATORS"
                subtitle="TECHNICAL ANALYSIS OVERVIEW"
                icon="📈"
                :data="analysisResults.priceData"
                :loading="loading"
                :show-controls="true"
                :time-range-options="chartTimeRanges"
                value-label="Price"
                :show-legend="true"
              />
            </ArtDecoCard>

            <!-- Volume Chart -->
            <ArtDecoCard class="volume-chart-card" title="VOLUME ANALYSIS" :decorated="true">
              <TimeSeriesChart
                title="TRADING VOLUME"
                subtitle="VOLUME ANALYSIS OVER TIME"
                icon="📊"
                :data="analysisResults.volumeData"
                :loading="loading"
                value-label="Volume"
                :show-legend="false"
              />
            </ArtDecoCard>
          </div>
        </div>

        <!-- Indicators Values Table -->
        <ArtDecoCard class="indicators-table-card" title="TECHNICAL INDICATORS VALUES" :decorated="true">
          <ArtDecoTable
            :columns="indicatorColumns"
            :data="analysisResults.indicatorValues"
            :loading="loading"
            striped
            hover
            :pagination="true"
            :page-size="20"
          >
            <template #trend="{ row }">
              <ArtDecoBadge
                :text="row.trend"
                :variant="getTrendVariant(row.trend)"
                size="sm"
              />
            </template>

            <template #signal="{ row }">
              <ArtDecoBadge
                :text="row.signal"
                :variant="getSignalVariant(row.signal)"
                size="sm"
              />
            </template>
          </ArtDecoTable>
        </ArtDecoCard>

        <!-- Signal Summary -->
        <div class="signals-section">
          <div class="signals-grid">
            <ArtDecoCard class="signal-summary-card" title="SIGNAL SUMMARY" :decorated="true">
              <div class="signal-stats">
                <div class="stat-item">
                  <div class="stat-label">BUY SIGNALS</div>
                  <div class="stat-value success">{{ analysisResults.signals.buy }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">SELL SIGNALS</div>
                  <div class="stat-value danger">{{ analysisResults.signals.sell }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">HOLD SIGNALS</div>
                  <div class="stat-value warning">{{ analysisResults.signals.hold }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">OVERALL TREND</div>
                  <div class="stat-value" :class="getOverallTrendClass(analysisResults.signals.overallTrend)">
                    {{ analysisResults.signals.overallTrend }}
                  </div>
                </div>
              </div>
            </ArtDecoCard>

            <ArtDecoCard class="recent-signals-card" title="RECENT SIGNALS" :decorated="true">
              <div class="recent-signals-list">
                <div
                  v-for="signal in analysisResults.recentSignals"
                  :key="signal.id"
                  class="signal-item"
                >
                  <div class="signal-info">
                    <div class="signal-date">{{ signal.date }}</div>
                    <div class="signal-type">
                      <ArtDecoBadge
                        :text="signal.type"
                        :variant="getSignalVariant(signal.type)"
                        size="sm"
                      />
                    </div>
                  </div>
                  <div class="signal-strength">
                    <div class="strength-bar">
                      <div
                        class="strength-fill"
                        :style="{ width: signal.strength + '%' }"
                        :class="getStrengthClass(signal.strength)"
                      ></div>
                    </div>
                    <span class="strength-value">{{ signal.strength }}%</span>
                  </div>
                </div>
              </div>
            </ArtDecoCard>
          </div>
        </div>

        <!-- Export Options -->
        <ArtDecoCard class="export-card" title="EXPORT ANALYSIS RESULTS" :decorated="true">
          <div class="export-options">
            <div class="export-buttons">
              <ArtDecoButton variant="secondary" @click="exportToPDF">
                EXPORT PDF REPORT
              </ArtDecoButton>
              <ArtDecoButton variant="secondary" @click="exportToExcel">
                EXPORT EXCEL DATA
              </ArtDecoButton>
              <ArtDecoButton variant="secondary" @click="exportToJSON">
                EXPORT JSON DATA
              </ArtDecoButton>
            </div>
            <div class="export-settings">
              <label class="setting-label">
                <input type="checkbox" v-model="exportSettings.includeCharts" class="setting-checkbox" />
                Include Charts
              </label>
              <label class="setting-label">
                <input type="checkbox" v-model="exportSettings.includeSignals" class="setting-checkbox" />
                Include Signals
              </label>
              <label class="setting-label">
                <input type="checkbox" v-model="exportSettings.includeRawData" class="setting-checkbox" />
                Include Raw Data
              </label>
            </div>
          </div>
        </ArtDecoCard>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-overlay">
        <ArtDecoCard class="loading-card">
          <div class="loading-content">
            <div class="loading-spinner"></div>
            <div class="loading-text">ANALYZING MARKET DATA...</div>
            <div class="loading-subtext">This may take a few moments</div>
          </div>
        </ArtDecoCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// ArtDeco Components
import {
  ArtDecoHeader,
  ArtDecoCard,
  ArtDecoInput,
  ArtDecoSelect,
  ArtDecoButton,
  ArtDecoBadge,
  ArtDecoTable,
  ArtDecoSidebar
} from '@/components/artdeco'

// Specialized Components
import TimeSeriesChart from '@/components/artdeco/charts/TimeSeriesChart.vue'

// Types
interface AnalysisForm {
  symbol: string
  analysisType: string
  period: string
  startDate: string
  endDate: string
  selectedIndicators: string[]
  lookbackPeriod: number
  signalThreshold: number
}

interface StockInfo {
  name: string
  price: number
  change: number
}

// Reactive Data
const menuItems = ref([
  { label: 'TECHNICAL ANALYSIS', icon: '📊', path: '/analysis', active: true },
  { label: 'FUNDAMENTAL ANALYSIS', icon: '🏢', path: '/analysis/fundamental' },
  { label: 'SENTIMENT ANALYSIS', icon: '💭', path: '/analysis/sentiment' },
  { label: 'QUANTITATIVE MODELS', icon: '🧮', path: '/analysis/quantitative' }
])

const breadcrumbItems = ref([
  { label: 'DASHBOARD', path: '/' },
  { label: 'ANALYSIS', active: true }
])

// Form Data
const form = ref<AnalysisForm>({
  symbol: '',
  analysisType: 'indicators',
  period: 'daily',
  startDate: '2024-01-01',
  endDate: new Date().toISOString().split('T')[0],
  selectedIndicators: ['ma', 'rsi', 'macd'],
  lookbackPeriod: 100,
  signalThreshold: 0.7
})

const showAdvancedOptions = ref(false)
const loading = ref(false)
const stockInfo = ref<StockInfo>({ name: '', price: 0, change: 0 })

// Analysis Results
const analysisResults = ref<any>(null)

// Options Data
const analysisTypes = [
  { label: 'TECHNICAL INDICATORS', value: 'indicators' },
  { label: 'TREND ANALYSIS', value: 'trend' },
  { label: 'MOMENTUM ANALYSIS', value: 'momentum' },
  { label: 'VOLATILITY ANALYSIS', value: 'volatility' },
  { label: 'VOLUME ANALYSIS', value: 'volume' },
  { label: 'SIGNAL SYNTHESIS', value: 'signals' }
]

const timePeriods = [
  { label: 'DAILY', value: 'daily' },
  { label: 'WEEKLY', value: 'weekly' },
  { label: 'MONTHLY', value: 'monthly' }
]

const availableIndicators = [
  { key: 'ma', label: 'Moving Average (MA)' },
  { key: 'ema', label: 'Exponential MA (EMA)' },
  { key: 'rsi', label: 'Relative Strength Index (RSI)' },
  { key: 'macd', label: 'MACD' },
  { key: 'bb', label: 'Bollinger Bands' },
  { key: 'stoch', label: 'Stochastic Oscillator' },
  { key: 'williams', label: 'Williams %R' },
  { key: 'cci', label: 'Commodity Channel Index' },
  { key: 'adx', label: 'Average Directional Index' }
]

const chartTimeRanges = [
  { label: '1M', value: '1M' },
  { label: '3M', value: '3M' },
  { label: '6M', value: '6M' },
  { label: '1Y', value: '1Y' },
  { label: 'ALL', value: 'ALL' }
]

// Export Settings
const exportSettings = ref({
  includeCharts: true,
  includeSignals: true,
  includeRawData: false
})

// Table Columns
const indicatorColumns: any[] = [
  { key: 'date', label: 'DATE', sortable: true, width: '120px' },
  { key: 'price', label: 'PRICE', width: '100px', format: (value: any) => `¥${value.toFixed(2)}` },
  { key: 'ma', label: 'MA(20)', width: '80px', format: (value: any) => value?.toFixed(2) || '-' },
  { key: 'rsi', label: 'RSI', width: '80px', format: (value: any) => value?.toFixed(2) || '-' },
  { key: 'macd', label: 'MACD', width: '100px', format: (value: any) => value?.toFixed(4) || '-' },
  { key: 'trend', label: 'TREND', width: '100px' },
  { key: 'signal', label: 'SIGNAL', width: '100px' }
]

// Computed Properties
const isFormValid = computed(() => {
  return form.value.symbol.trim() !== '' &&
         form.value.startDate &&
         form.value.endDate &&
         form.value.selectedIndicators.length > 0
})

// Methods
const handleSymbolChange = async () => {
  if (form.value.symbol.length === 6) {
    // Simulate API call to get stock info
    try {
      // Mock stock info
      stockInfo.value = {
        name: '浦发银行',
        price: 8.45,
        change: 0.23
      }
    } catch (error) {
      console.error('Failed to fetch stock info:', error)
    }
  }
}

const runAnalysis = async () => {
  if (!isFormValid.value) return

  loading.value = true
  try {
    // Simulate analysis API call
    await new Promise(resolve => setTimeout(resolve, 3000))

    // Mock analysis results
    analysisResults.value = {
      priceData: generatePriceData(),
      volumeData: generateVolumeData(),
      indicatorValues: generateIndicatorValues(),
      signals: {
        buy: 12,
        sell: 8,
        hold: 25,
        overallTrend: 'BULLISH'
      },
      recentSignals: generateRecentSignals()
    }

  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.value = {
    symbol: '',
    analysisType: 'indicators',
    period: 'daily',
    startDate: '2024-01-01',
    endDate: new Date().toISOString().split('T')[0],
    selectedIndicators: ['ma', 'rsi', 'macd'],
    lookbackPeriod: 100,
    signalThreshold: 0.7
  }
  stockInfo.value = { name: '', price: 0, change: 0 }
  analysisResults.value = null
}

const toggleAdvancedOptions = () => {
  showAdvancedOptions.value = !showAdvancedOptions.value
}

const loadPreset = () => {
  // Load a preset configuration
  form.value.selectedIndicators = ['ma', 'rsi', 'macd', 'bb']
  form.value.lookbackPeriod = 200
  form.value.signalThreshold = 0.8
}

// Helper Functions
const generatePriceData = () => {
  const data = []
  const basePrice = 50
  let currentPrice = basePrice

  for (let i = 0; i < 100; i++) {
    const date = new Date()
    date.setDate(date.getDate() - (99 - i))

    // Generate realistic price movement
    const change = (Math.random() - 0.5) * 4
    currentPrice += change
    currentPrice = Math.max(currentPrice, 10) // Floor price

    data.push({
      date: date.toISOString().split('T')[0],
      value: Math.round(currentPrice * 100) / 100
    })
  }

  return data
}

const generateVolumeData = () => {
  const data = []
  const baseVolume = 1000000

  for (let i = 0; i < 100; i++) {
    const date = new Date()
    date.setDate(date.getDate() - (99 - i))

    const volume = baseVolume + (Math.random() - 0.5) * 500000
    data.push({
      date: date.toISOString().split('T')[0],
      value: Math.round(volume)
    })
  }

  return data
}

const generateIndicatorValues = () => {
  const data = []

  for (let i = 0; i < 50; i++) {
    const date = new Date()
    date.setDate(date.getDate() - (49 - i))

    data.push({
      date: date.toISOString().split('T')[0],
      price: 50 + Math.random() * 20,
      ma: 52 + Math.random() * 10,
      rsi: 30 + Math.random() * 40,
      macd: (Math.random() - 0.5) * 2,
      trend: Math.random() > 0.5 ? 'UPTREND' : 'DOWNTREND',
      signal: ['BUY', 'SELL', 'HOLD'][Math.floor(Math.random() * 3)]
    })
  }

  return data
}

const generateRecentSignals = () => {
  const signals = []
  const types = ['BUY', 'SELL', 'HOLD']

  for (let i = 0; i < 10; i++) {
    const date = new Date()
    date.setDate(date.getDate() - i)

    signals.push({
      id: `signal-${i}`,
      date: date.toISOString().split('T')[0],
      type: types[Math.floor(Math.random() * types.length)],
      strength: Math.floor(Math.random() * 40) + 60
    })
  }

  return signals
}

// Utility Functions
const getTrendVariant = (trend: string) => {
  return trend === 'UPTREND' ? 'success' : 'danger'
}

const getSignalVariant = (signal: string) => {
  switch (signal) {
    case 'BUY': return 'rise'
    case 'SELL': return 'fall'
    case 'HOLD': return 'warning'
    default: return 'info'
  }
}

const getOverallTrendClass = (trend: string) => {
  return trend === 'BULLISH' ? 'success' : trend === 'BEARISH' ? 'danger' : 'warning'
}

const getStrengthClass = (strength: number) => {
  if (strength >= 80) return 'strength-high'
  if (strength >= 60) return 'strength-medium'
  return 'strength-low'
}

const exportToPDF = () => {
  console.log('Exporting to PDF...')
}

const exportToExcel = () => {
  console.log('Exporting to Excel...')
}

const exportToJSON = () => {
  console.log('Exporting to JSON...')
}

// Lifecycle
onMounted(() => {
  // Initialize form with default values
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.analysis-page {
  @include artdeco-layout;

  .main-content {
    @include artdeco-content-spacing;
  }

  .config-panel {
    margin-bottom: var(--artdeco-spacing-xl);

    .config-header {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-lg);
      width: 100%;

      .header-icon {
        font-size: var(--artdeco-font-size-xl);
      }

      .header-content {
        flex: 1;

        .header-title {
          font-family: var(--artdeco-font-display);
          font-size: var(--artdeco-font-size-lg);
          font-weight: 600;
          color: var(--artdeco-accent-gold);
          text-transform: uppercase;
          letter-spacing: var(--artdeco-tracking-wide);
        }

        .header-subtitle {
          font-family: var(--artdeco-font-body);
          font-size: var(--artdeco-font-size-sm);
          color: var(--artdeco-fg-muted);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
      }

      .run-button {
        flex-shrink: 0;
      }
    }

    .analysis-form {
      .form-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: var(--artdeco-spacing-lg);
        margin-bottom: var(--artdeco-spacing-lg);

        .form-group {
          display: flex;
          flex-direction: column;
          gap: var(--artdeco-spacing-xs);

          &.full-width {
            grid-column: 1 / -1;
          }

          .artdeco-label {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-font-size-sm);
            font-weight: 600;
            color: var(--artdeco-accent-gold);
            text-transform: uppercase;
            letter-spacing: 0.05em;
          }

          .input-hint {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-font-size-xs);
            color: var(--artdeco-fg-muted);
          }

          .date-range-inputs {
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-md);

            .date-separator {
              font-family: var(--artdeco-font-display);
              font-size: var(--artdeco-font-size-sm);
              color: var(--artdeco-accent-gold);
              text-transform: uppercase;
              letter-spacing: 0.05em;
            }
          }

          .indicators-selection {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--artdeco-spacing-sm);

            .indicator-checkbox {
              display: flex;
              align-items: center;
              gap: var(--artdeco-spacing-sm);

              .checkbox-input {
                margin: 0;
              }

              .checkbox-label {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-font-size-sm);
                color: var(--artdeco-fg-secondary);
                cursor: pointer;
              }
            }
          }

          .advanced-options {
            .option-row {
              display: grid;
              grid-template-columns: 1fr 1fr;
              gap: var(--artdeco-spacing-md);
            }
          }
        }
      }

      .form-actions {
        display: flex;
        justify-content: flex-end;
        gap: var(--artdeco-spacing-md);
      }
    }
  }

  .results-area {
    .indicators-section {
      margin-bottom: var(--artdeco-spacing-xl);

      .indicators-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--artdeco-spacing-lg);

        @media (max-width: 1200px) {
          grid-template-columns: 1fr;
        }
      }
    }

    .indicators-table-card {
      margin-bottom: var(--artdeco-spacing-xl);
    }

    .signals-section {
      margin-bottom: var(--artdeco-spacing-xl);

      .signals-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--artdeco-spacing-lg);

        @media (max-width: 1000px) {
          grid-template-columns: 1fr;
        }
      }

      .signal-summary-card {
        .signal-stats {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: var(--artdeco-spacing-md);
        }

        .stat-item {
          text-align: center;
          padding: var(--artdeco-spacing-md);
          background: var(--artdeco-bg-elevated);
          border: 1px solid rgba(212, 175, 55, 0.1);
          border-radius: 4px;

          .stat-label {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-font-size-sm);
            color: var(--artdeco-fg-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: var(--artdeco-spacing-xs);
          }

          .stat-value {
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-font-size-xl);
            font-weight: 700;

            &.success { color: var(--artdeco-success); }
            &.danger { color: var(--artdeco-danger); }
            &.warning { color: var(--artdeco-warning); }
          }
        }
      }

      .recent-signals-card {
        .recent-signals-list {
          display: flex;
          flex-direction: column;
          gap: var(--artdeco-spacing-sm);
        }

        .signal-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: var(--artdeco-spacing-sm) var(--artdeco-spacing-md);
          background: var(--artdeco-bg-elevated);
          border: 1px solid rgba(212, 175, 55, 0.1);
          border-radius: 4px;

          .signal-info {
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-md);

            .signal-date {
              font-family: var(--artdeco-font-mono);
              font-size: var(--artdeco-font-size-sm);
              color: var(--artdeco-fg-muted);
            }
          }

          .signal-strength {
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-sm);

            .strength-bar {
              width: 80px;
              height: 6px;
              background: var(--artdeco-bg-primary);
              border-radius: 3px;
              overflow: hidden;

              .strength-fill {
                height: 100%;
                transition: width var(--artdeco-transition-base);

                &.strength-high { background: var(--artdeco-success); }
                &.strength-medium { background: var(--artdeco-warning); }
                &.strength-low { background: var(--artdeco-danger); }
              }
            }

            .strength-value {
              font-family: var(--artdeco-font-mono);
              font-size: var(--artdeco-font-size-xs);
              color: var(--artdeco-fg-muted);
              min-width: 35px;
              text-align: right;
            }
          }
        }
      }
    }

    .export-card {
      .export-options {
        .export-buttons {
          display: flex;
          gap: var(--artdeco-spacing-md);
          margin-bottom: var(--artdeco-spacing-lg);
          flex-wrap: wrap;
        }

        .export-settings {
          display: flex;
          gap: var(--artdeco-spacing-lg);
          flex-wrap: wrap;

          .setting-label {
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-xs);
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-font-size-sm);
            color: var(--artdeco-fg-secondary);
            cursor: pointer;

            .setting-checkbox {
              margin: 0;
            }
          }
        }
      }
    }
  }

  .loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(4px);

    .loading-card {
      .loading-content {
        text-align: center;
        padding: var(--artdeco-spacing-xl);

        .loading-spinner {
          width: 48px;
          height: 48px;
          border: 3px solid rgba(212, 175, 55, 0.2);
          border-top-color: var(--artdeco-accent-gold);
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto var(--artdeco-spacing-lg);
        }

        .loading-text {
          font-family: var(--artdeco-font-display);
          font-size: var(--artdeco-font-size-lg);
          font-weight: 600;
          color: var(--artdeco-accent-gold);
          text-transform: uppercase;
          letter-spacing: var(--artdeco-tracking-wide);
          margin-bottom: var(--artdeco-spacing-xs);
        }

        .loading-subtext {
          font-family: var(--artdeco-font-body);
          font-size: var(--artdeco-font-size-sm);
          color: var(--artdeco-fg-muted);
        }
      }
    }
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
}
</style>
