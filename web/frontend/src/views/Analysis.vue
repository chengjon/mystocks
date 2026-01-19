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
              variant="primary"
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
              variant="gold"
              @click="toggleAdvancedOptions"
            >
              {{ showAdvancedOptions ? 'HIDE' : 'SHOW' }} ADVANCED
            </ArtDecoButton>

            <ArtDecoButton
              variant="info"
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
import TimeSeriesChart from '@/components/artdeco/specialized/TimeSeriesChart.vue'

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
const indicatorColumns = [
  { key: 'date', label: 'DATE', sortable: true, width: 120 },
  { key: 'price', label: 'PRICE', align: 'right', format: 'currency', width: 100 },
  { key: 'ma', label: 'MA(20)', align: 'right', width: 80 },
  { key: 'rsi', label: 'RSI', align: 'right', width: 80 },
  { key: 'macd', label: 'MACD', align: 'right', width: 100 },
  { key: 'trend', label: 'TREND', slot: 'trend', width: 100 },
  { key: 'signal', label: 'SIGNAL', slot: 'signal', width: 100 }
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
    default: return 'secondary'
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
            </select>
          </div>

          <div class="form-row">
            <label class="form-label">数据范围</label>
            <div class="number-input">
              <input type="number" v-model="form.days" :min="30" :max="365" :step="30" class="input" />
              <span>天</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="analysisResult" class="analysis-results">
      <div class="card result-card">
        <div class="card-header">
          <div class="header-title">
            <div class="title-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                <line x1="12" y1="22.08" x2="12" y2="12"></line>
              </svg>
            </div>
            <span class="title-text">{{ getAnalysisTitle() }} - {{ form.symbol }}</span>
          </div>
          <el-tag :type="getSignalTagType(analysisResult.overall_signal)">
            {{ analysisResult.overall_signal || '中性' }}
          </el-tag>
        </div>
        <div class="card-body">
          <div class="metrics-grid">
            <div v-for="metric in keyMetrics" :key="metric.key" :class="['metric-card', metric.class]">
              <div class="metric-value">{{ metric.value }}</div>
              <div class="metric-label">{{ metric.label }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="card detail-card">
        <div class="card-header">
          <div class="header-title">
            <span class="title-text">指标详情</span>
            <span class="title-sub">INDICATOR DETAILS</span>
          </div>
        </div>
        <div class="card-body">
          <StockListTable
            :columns="tableColumns"
            :data="indicatorDetails"
            :loading="false"
            :row-clickable="false"
          >
            <template #cell-signal="{ row }">
              <el-tag :type="getSignalTagType(row.signal)">
                {{ row.signal }}
              </el-tag>
            </template>
          </StockListTable>
        </div>
      </div>

      <div class="card chart-card">
        <div class="card-header">
          <div class="header-title">
            <span class="title-text">趋势图表</span>
            <span class="title-sub">TREND CHART</span>
          </div>
        </div>
        <div class="card-body">
          <ChartContainer
            chart-type="line"
            :data="chartData"
            :options="chartOptions"
            height="400px"
            :loading="loading"
          />
        </div>
      </div>

      <div class="card advice-card">
        <div class="card-header">
          <div class="header-title">
            <div class="title-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9 11l3 3L22 4"></path>
                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
              </svg>
            </div>
            <span class="title-text">分析建议</span>
            <span class="title-sub">ANALYSIS ADVICE</span>
          </div>
        </div>
        <div class="card-body">
          <div v-if="analysisResult.advices && analysisResult.advices.length" class="advice-list">
            <div v-for="(advice, index) in analysisResult.advices" :key="index" :class="['advice-item', advice.type || 'info']">
              <div class="advice-icon">
                <svg v-if="advice.type === 'success'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                <svg v-else-if="advice.type === 'warning'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="8" x2="12" y2="12"></line>
                  <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="16" x2="12" y2="12"></line>
                  <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
              </div>
              <div class="advice-content">
                <div class="advice-title">{{ advice.title }}</div>
                <div class="advice-desc">{{ advice.description }}</div>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <p>暂无分析建议</p>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="card empty-card">
      <div class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 3v18h18"></path>
          <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"></path>
        </svg>
        <p>请选择股票并开始分析</p>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { technicalApi } from '@/api'
import { PageHeader, StockListTable, ChartContainer } from '@/components/shared'
import type { TableColumn } from '@/components/shared'

interface AnalysisForm {
  symbol: string
  analysisType: string
  period: string
  days: number
}

interface AnalysisResult {
  price?: number
  change_percent?: number
  ma5?: number
  ma20?: number
  rsi?: number
  volatility?: number
  overall_signal?: string
  indicators?: IndicatorDetail[]
  chart_data?: ChartData
  advices?: Advice[]
}

interface IndicatorDetail {
  name: string
  value: string | number
  signal: string
  description: string
}

interface ChartData {
  legend?: string[]
  dates?: string[]
  prices?: number[]
  ma5?: number[]
  ma20?: number[]
  series?: any[]
}

interface Advice {
  type?: string
  title: string
  description: string
}

interface Metric {
  key: string
  label: string
  value: string
  class: string
}

const loading = ref(false)
const analysisResult = ref<AnalysisResult | null>(null)

const form = ref<AnalysisForm>({
  symbol: '',
  analysisType: 'indicators',
  period: 'daily',
  days: 60
})

const tableColumns = computed((): TableColumn[] => [
  {
    prop: 'name',
    label: '指标',
    width: 150
  },
  {
    prop: 'value',
    label: '数值',
    width: 120,
    className: 'mono'
  },
  {
    prop: 'signal',
    label: '信号',
    width: 120
  },
  {
    prop: 'description',
    label: '说明',
    minWidth: 200
  }
])

const keyMetrics = computed((): Metric[] => {
  if (!analysisResult.value) return []
  const result = analysisResult.value
  const metrics: Metric[] = []

  if (result.price !== undefined) {
    metrics.push({
      key: 'price',
      label: '当前价格',
      value: `¥${result.price.toFixed(2)}`,
      class: ''
    })
  }

  if (result.change_percent !== undefined) {
    const change = result.change_percent
    metrics.push({
      key: 'change',
      label: '涨跌幅',
      value: `${change > 0 ? '+' : ''}${change.toFixed(2)}%`,
      class: change > 0 ? 'positive' : change < 0 ? 'negative' : ''
    })
  }

  if (result.ma5 !== undefined) {
    metrics.push({
      key: 'ma5',
      label: 'MA5',
      value: result.ma5.toFixed(2),
      class: result.price !== undefined && result.price > result.ma5 ? 'positive' : 'negative'
    })
  }

  if (result.ma20 !== undefined) {
    metrics.push({
      key: 'ma20',
      label: 'MA20',
      value: result.ma20.toFixed(2),
      class: result.price !== undefined && result.price > result.ma20 ? 'positive' : 'negative'
    })
  }

  if (result.rsi !== undefined) {
    metrics.push({
      key: 'rsi',
      label: 'RSI',
      value: result.rsi.toFixed(2),
      class: result.rsi > 70 ? 'negative' : result.rsi < 30 ? 'positive' : ''
    })
  }

  if (result.volatility !== undefined) {
    metrics.push({
      key: 'volatility',
      label: '波动率',
      value: `${(result.volatility * 100).toFixed(2)}%`,
      class: ''
    })
  }

  return metrics.slice(0, 4)
})

const indicatorDetails = computed((): IndicatorDetail[] => {
  if (!analysisResult.value?.indicators) return []
  return analysisResult.value.indicators
})

const chartData = computed((): any[] => {
  if (!analysisResult.value?.chart_data) return []

  const chartInfo = analysisResult.value.chart_data
  return [
    {
      name: '价格',
      data: (chartInfo.dates || []).map((date: string, index: number) => ({
        name: date,
        value: chartInfo.prices?.[index] || 0
      }))
    },
    {
      name: 'MA5',
      data: (chartInfo.dates || []).map((date: string, index: number) => ({
        name: date,
        value: chartInfo.ma5?.[index] || 0
      }))
    },
    {
      name: 'MA20',
      data: (chartInfo.dates || []).map((date: string, index: number) => ({
        name: date,
        value: chartInfo.ma20?.[index] || 0
      }))
    }
  ]
})

const chartOptions = computed((): Record<string, any> => {
  return {
    tooltip: {
      trigger: 'axis' as const,
      axisPointer: { type: 'cross' as const },
      backgroundColor: 'rgba(10, 10, 10, 0.95)',
      borderColor: '#D4AF37',
      textStyle: { color: '#E5E7EB' }
    },
    legend: {
      data: ['价格', 'MA5', 'MA20'],
      textStyle: { color: '#D4AF37' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category' as const,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#374151' } },
      axisLabel: { color: '#9CA3AF' }
    },
    yAxis: {
      type: 'value' as const,
      scale: true,
      axisLine: { lineStyle: { color: '#374151' } },
      axisLabel: { color: '#9CA3AF' }
    },
    color: ['#FF5252', '#D4AF37', '#67C23A']
  }
})

const getAnalysisTitle = (): string => {
  const titles: Record<string, string> = {
    indicators: '技术指标分析',
    trend: '趋势分析',
    momentum: '动量分析',
    volatility: '波动率分析',
    volume: '成交量分析',
    signals: '信号综合分析'
  }
  return titles[form.value.analysisType] || '数据分析'
}

const getSignalBadgeClass = (signal?: string): string => {
  if (!signal) return 'neutral'
  const signalLower = signal.toLowerCase()
  if (signalLower.includes('买') || signalLower.includes('buy') || signalLower.includes('强')) {
    return 'success'
  }
  if (signalLower.includes('卖') || signalLower.includes('sell') || signalLower.includes('弱')) {
    return 'danger'
  }
  return 'warning'
}

const getSignalTagType = (signal?: string): 'success' | 'danger' | 'warning' | 'info' => {
  if (!signal) return 'info'
  const signalLower = signal.toLowerCase()
  if (signalLower.includes('买') || signalLower.includes('buy') || signalLower.includes('强')) {
    return 'success'
  }
  if (signalLower.includes('卖') || signalLower.includes('sell') || signalLower.includes('弱')) {
    return 'danger'
  }
  return 'warning'
}

const getSignalTagClass = (signal: string): string => {
  if (!signal) return 'neutral'
  const signalLower = signal.toLowerCase()
  if (signalLower.includes('买') || signalLower.includes('buy') || signalLower.includes('强')) {
    return 'success'
  }
  if (signalLower.includes('卖') || signalLower.includes('sell') || signalLower.includes('弱')) {
    return 'danger'
  }
  return 'warning'
}

const runAnalysis = async (): Promise<void> => {
  if (!form.value.symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }

  loading.value = true
  try {
    let response
    const params = {
      period: form.value.period,
      days: form.value.days
    }

    switch (form.value.analysisType) {
      case 'indicators':
        response = await technicalApi.getIndicators(form.value.symbol, params)
        break
      case 'trend':
        response = await technicalApi.getTrend(form.value.symbol, params)
        break
      case 'momentum':
        response = await technicalApi.getMomentum(form.value.symbol, params)
        break
      case 'volatility':
        response = await technicalApi.getVolatility(form.value.symbol, params)
        break
      case 'volume':
        response = await technicalApi.getVolume(form.value.symbol, params)
        break
      case 'signals':
        response = await technicalApi.getSignals(form.value.symbol, params)
        break
      default:
        response = await technicalApi.getIndicators(form.value.symbol, params)
    }

    if (response.data?.success) {
      analysisResult.value = response.data.data
      ElMessage.success('分析完成')
    } else {
      ElMessage.error(response.data?.message || '分析失败')
    }
  } catch (error: any) {
    console.error('分析失败:', error)
    ElMessage.error('分析失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">

.analysis {
  padding: 24px;
  background: var(--bg-primary);
  background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(212, 175, 55, 0.02) 10px, rgba(212, 175, 55, 0.02) 11px);
  min-height: 100vh;

  .config-card {
    margin-bottom: 24px;

    .analysis-form {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;

      .form-row {
        display: flex;
        flex-direction: column;
        gap: 8px;

        .form-label {
          font-family: var(--font-body);
          font-size: 12px;
          color: var(--gold-muted);
          text-transform: uppercase;
          letter-spacing: 2px;
        }

        .input {
          background: transparent;
          border: none;
          border-bottom: 2px solid var(--gold-dim);
          padding: 8px 0;
          font-family: var(--font-body);
          font-size: 14px;
          color: var(--text-primary);
          transition: all 0.3s ease;

          &:focus {
            outline: none;
            border-bottom-color: var(--gold-primary);
            box-shadow: 0 4px 12px rgba(212, 175, 55, 0.2);
          }

          &::placeholder {
            color: var(--text-muted);
          }
        }

        .select {
          background: transparent;
          border: none;
          border-bottom: 2px solid var(--gold-dim);
          padding: 8px 0;
          font-family: var(--font-body);
          font-size: 14px;
          color: var(--text-primary);
          cursor: pointer;
          transition: all 0.3s ease;

          &:focus {
            outline: none;
            border-bottom-color: var(--gold-primary);
            box-shadow: 0 4px 12px rgba(212, 175, 55, 0.2);
          }

          option {
            background: var(--bg-card);
            color: var(--text-primary);
          }
        }

        .number-input {
          display: flex;
          align-items: center;
          gap: 8px;

          .input {
            width: 100px;
          }

          span {
            font-family: var(--font-body);
            font-size: 14px;
            color: var(--text-muted);
          }
        }
      }
    }
  }

  .analysis-results {
    .result-card {
      margin-bottom: 24px;

      .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;

        .metric-card {
          background: rgba(212, 175, 55, 0.05);
          border: 1px solid var(--gold-dim);
          padding: 20px;
          text-align: center;
          position: relative;

          &::before {
            content: '';
            position: absolute;
            top: 8px;
            left: 8px;
            width: 6px;
            height: 6px;
            background: var(--gold-primary);
          }

          .metric-value {
            font-family: var(--font-mono);
            font-size: 24px;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 8px;

            &.positive {
              color: var(--rise);
            }

            &.negative {
              color: var(--fall);
            }
          }

          .metric-label {
            font-family: var(--font-body);
            font-size: 12px;
            color: var(--gold-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
          }
        }
      }
    }

    .detail-card {
      margin-bottom: 24px;
    }

    .chart-card {
      margin-bottom: 24px;
    }

    .advice-card {
      margin-bottom: 24px;

      .advice-list {
        display: flex;
        flex-direction: column;
        gap: 12px;

        .advice-item {
          background: rgba(212, 175, 55, 0.05);
          border-left: 4px solid var(--gold-primary);
          padding: 16px;
          display: flex;
          gap: 16px;
          align-items: flex-start;

          &.success {
            border-left-color: var(--fall);
            background: rgba(0, 230, 118, 0.05);
          }

          &.warning {
            border-left-color: #e6a23c;
            background: rgba(230, 162, 60, 0.05);
          }

          &.info {
            border-left-color: var(--gold-primary);
          }

          .advice-icon {
            flex-shrink: 0;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--gold-primary);
          }

          .advice-content {
            flex: 1;

            .advice-title {
              font-family: var(--font-body);
              font-size: 14px;
              font-weight: 600;
              color: var(--gold-primary);
              margin-bottom: 4px;
            }

            .advice-desc {
              font-family: var(--font-body);
              font-size: 13px;
              color: var(--text-secondary);
              line-height: 1.6;
            }
          }
        }
      }

      .empty-state {
        text-align: center;
        padding: 40px 20px;

        svg {
          width: 60px;
          height: 60px;
          margin: 0 auto 16px;
          color: var(--gold-primary);
        }

        p {
          font-family: var(--font-body);
          font-size: 14px;
          color: var(--text-muted);
          margin: 0;
        }
      }
    }
  }

  .empty-card {
    .empty-state {
      text-align: center;
      padding: 80px 20px;

      svg {
        width: 80px;
        height: 80px;
        margin: 0 auto 24px;
        color: var(--gold-muted);
      }

      p {
        font-family: var(--font-body);
        font-size: 16px;
        color: var(--text-secondary);
        margin: 0;
      }
    }
  }
  }

  .card {
    background: var(--bg-card);
    border: 1px solid var(--gold-dim);
    position: relative;

    &::before,
  &::after {
    content: '';
    position: absolute;
    width: 16px;
    height: 16px;
    border: 2px solid var(--gold-primary);
    z-index: 1;
  }

  &::before {
    top: 12px;
    left: 12px;
    border-right: none;
    border-bottom: none;
  }

  &::after {
    bottom: 12px;
    right: 12px;
    border-left: none;
    border-top: none;
  }

  .card-header {
    padding: 16px 24px;
    border-bottom: 1px solid var(--gold-dim);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;

    .header-title {
      display: flex;
      align-items: center;
      gap: 12px;

      .title-icon {
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--gold-primary);
        flex-shrink: 0;
      }

      .title-text {
        font-family: var(--font-body);
        font-size: 16px;
        font-weight: 600;
        color: var(--gold-primary);
        text-transform: uppercase;
        letter-spacing: 2px;
      }

      .title-sub {
        font-family: var(--font-body);
        font-size: 10px;
        color: var(--gold-muted);
        text-transform: uppercase;
        letter-spacing: 3px;
        display: block;
        margin-top: 2px;
      }
    }

    .badge {
      font-family: var(--font-body);
      font-size: 11px;
      padding: 6px 16px;
      border: 1px solid var(--gold-primary);
      text-transform: uppercase;
      letter-spacing: 1px;

      &.success {
        background: var(--fall);
        color: var(--bg-primary);
        border-color: var(--fall);
      }

      &.danger {
        background: var(--rise);
        color: var(--bg-primary);
        border-color: var(--rise);
      }

      &.warning {
        background: #e6a23c;
        color: var(--bg-primary);
        border-color: #e6a23c;
      }

      &.neutral {
        background: rgba(212, 175, 55, 0.1);
        color: var(--gold-primary);
      }
    }
  }

  .card-body {
    padding: 24px;
  }
}

.button {
  padding: 12px 24px;
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 2px;
  border: 2px solid var(--gold-primary);
  background: transparent;
  color: var(--gold-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
  position: relative;

  svg {
    width: 18px;
    height: 18px;
  }

  &:hover:not(.loading) {
    background: var(--gold-primary);
    color: var(--bg-primary);
  }

  &.loading {
    opacity: 0.6;
    cursor: not-allowed;
  }

  &::before {
    content: '';
    position: absolute;
    top: 4px;
    left: 4px;
    width: 8px;
    height: 8px;
    border-left: 1px solid var(--gold-primary);
    border-top: 1px solid var(--gold-primary);
  }

  &.button-primary {
    border-color: var(--rise);
    color: var(--rise);

    &::before {
      border-color: var(--rise);
    }

    &:hover:not(.loading) {
      background: var(--rise);
      color: var(--bg-primary);
    }
  }
}

.tag {
  font-family: var(--font-body);
  font-size: 11px;
  padding: 4px 12px;
  text-transform: uppercase;
  letter-spacing: 1px;

  &.success {
    background: rgba(0, 230, 118, 0.1);
    color: var(--fall);
    border: 1px solid var(--fall);
  }

  &.danger {
    background: rgba(255, 82, 82, 0.1);
    color: var(--rise);
    border: 1px solid var(--rise);
  }

  &.warning {
    background: rgba(230, 162, 60, 0.1);
    color: #e6a23c;
    border: 1px solid #e6a23c;
  }

  &.neutral {
    background: rgba(212, 175, 55, 0.1);
    color: var(--gold-primary);
    border: 1px solid var(--gold-primary);
  }
}

@media (max-width: 768px) {
  .analysis {
    padding: 16px;

    .config-card {
      .analysis-form {
        grid-template-columns: 1fr;
      }
    }

    .analysis-results {
      .result-card {
        .metrics-grid {
          grid-template-columns: repeat(2, 1fr);
        }
      }
    }
  }
}
</style>
