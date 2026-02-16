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
                  v-for="(indicator, _idx) in availableIndicators"
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
                  v-for="(signal, _idx) in analysisResults.recentSignals"
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
import TimeSeriesChart from '@/components/artdeco/charts/TimeSeriesChart.vue'
import { useAnalysis } from './composables/useAnalysis'

const {
  menuItems,
  breadcrumbItems,
  form,
  showAdvancedOptions,
  loading,
  stockInfo,
  analysisResults,
  analysisTypes,
  timePeriods,
  availableIndicators,
  chartTimeRanges,
  exportSettings,
  indicatorColumns,
  isFormValid,
  handleSymbolChange,
  runAnalysis,
  resetForm,
  toggleAdvancedOptions,
  loadPreset,
  generatePriceData,
  generateVolumeData,
  generateIndicatorValues,
  generateRecentSignals,
  getTrendVariant,
  getSignalVariant,
  getOverallTrendClass,
  getStrengthClass,
  exportToPDF,
  exportToExcel,
  exportToJSON
} = useAnalysis()
</script>

<style scoped lang="scss">
@import './styles/Analysis.scss';
</style>
