<template>
    <div class="technical-analysis">
        <!-- Page Header -->
        <div class="page-header">
            <div class="header-title-section">
                <h1 class="page-title">
                    <el-icon><DataLine /></el-icon>
                    TECHNICAL INDICATORS
                </h1>
                <p class="page-subtitle">REAL-TIME TECHNICAL ANALYSIS & CHART INDICATORS</p>
            </div>
            <div class="header-actions">
                <el-button type="primary" @click="refreshData" :loading="loading">
                    <template #icon>
                        <RefreshRight />
                    </template>
                    REFRESH DATA
                </el-button>
                <el-button @click="showIndicatorPanel = true">
                    <template #icon>
                        <Setting />
                    </template>
                    INDICATORS
                </el-button>
            </div>
        </div>

        <!-- Toolbar Section -->
        <div class="toolbar-section">
            <div class="toolbar-content">
                <!-- Stock Search -->
                <div class="search-section">
                    <el-input
                        v-model="selectedSymbol"
                        placeholder="Enter stock symbol (e.g., 600519)"
                        clearable
                        class="symbol-input"
                        @change="handleSymbolChange"
                    >
                        <template #prefix>
                            <Search />
                        </template>
                    </el-input>
                </div>

                <!-- Date Range Picker -->
                <div class="date-section">
                    <el-date-picker
                        v-model="dateRange"
                        type="daterange"
                        range-separator="to"
                        start-placeholder="Start Date"
                        end-placeholder="End Date"
                        format="YYYY-MM-DD"
                        value-format="YYYY-MM-DD"
                        class="date-picker"
                        :shortcuts="dateShortcuts"
                        @change="handleDateRangeChange"
                    />
                </div>

                <!-- Time Period Selector -->
                <div class="period-section">
                    <el-radio-group
                        v-model="selectedPeriod"
                        size="small"
                        @change="handlePeriodChange"
                        class="period-selector"
                    >
                        <el-radio-button label="1d">1D</el-radio-button>
                        <el-radio-button label="5d">5D</el-radio-button>
                        <el-radio-button label="1M">1M</el-radio-button>
                        <el-radio-button label="3M">3M</el-radio-button>
                        <el-radio-button label="6M">6M</el-radio-button>
                        <el-radio-button label="1Y">1Y</el-radio-button>
                    </el-radio-group>
                </div>

                <!-- Chart Type Selector -->
                <div class="chart-type-section">
                    <el-select
                        v-model="chartType"
                        placeholder="Chart Type"
                        size="small"
                        class="chart-type-select"
                        @change="handleChartTypeChange"
                    >
                        <el-option label="Candlestick" value="candlestick" />
                        <el-option label="Line" value="line" />
                        <el-option label="Area" value="area" />
                    </el-select>
                </div>
            </div>
        </div>

        <!-- Main Chart Section -->
        <div class="chart-section">
            <el-card class="main-chart-card" shadow="never">
                <template #header>
                    <div class="chart-header">
                        <div class="chart-title">
                            <span class="symbol-display">{{ selectedSymbol || 'No Symbol Selected' }}</span>
                            <span class="symbol-name">{{ symbolName }}</span>
                        </div>
                        <div class="chart-info">
                            <el-tag type="info" size="small">{{ selectedPeriod.toUpperCase() }}</el-tag>
                            <span class="last-update" v-if="lastUpdate">Updated: {{ lastUpdate }}</span>
                        </div>
                    </div>
                </template>

                <!-- Chart Container -->
                <div class="chart-container" v-loading="loading">
                    <div v-if="!selectedSymbol" class="no-data-placeholder">
                        <el-empty description="Please enter a stock symbol to view technical analysis" :image-size="80">
                            <template #image>
                                <el-icon size="80" class="placeholder-icon"><DataLine /></el-icon>
                            </template>
                        </el-empty>
                    </div>

                    <div v-else-if="!chartData || !chartData.ohlcv" class="no-data-placeholder">
                        <el-empty description="No chart data available for this symbol" :image-size="80" />
                    </div>

                    <div v-else ref="chartContainer" class="kline-chart" :style="{ height: chartHeight }"></div>
                </div>
            </el-card>
        </div>

        <!-- Indicators Overview -->
        <div class="indicators-section" v-if="selectedIndicators.length > 0">
            <el-card class="indicators-card" shadow="never">
                <template #header>
                    <div class="card-header">
                        <span class="card-title">ACTIVE INDICATORS</span>
                        <span class="indicators-count">{{ selectedIndicators.length }} active</span>
                    </div>
                </template>

                <div class="indicators-grid">
                    <div v-for="indicator in selectedIndicators" :key="indicator.name" class="indicator-item">
                        <div class="indicator-info">
                            <span class="indicator-name">{{ indicator.displayName }}</span>
                            <span class="indicator-params" v-if="indicator.params">
                                ({{ formatParams(indicator.params) }})
                            </span>
                        </div>
                        <div class="indicator-actions">
                            <el-button type="danger" size="small" text @click="removeIndicator(indicator.name)">
                                Remove
                            </el-button>
                        </div>
                    </div>
                </div>
            </el-card>
        </div>

        <!-- Technical Summary -->
        <div class="summary-section" v-if="chartData && chartData.ohlcv">
            <el-card class="summary-card" shadow="never">
                <template #header>
                    <div class="card-header">
                        <span class="card-title">TECHNICAL SUMMARY</span>
                    </div>
                </template>

                <div class="summary-grid">
                    <div class="summary-item">
                        <span class="summary-label">Data Points</span>
                        <span class="summary-value">{{ chartData.ohlcv.dates?.length || 0 }}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Time Range</span>
                        <span class="summary-value">
                            {{ dateRange?.[0] || 'N/A' }} to {{ dateRange?.[1] || 'N/A' }}
                        </span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Indicators</span>
                        <span class="summary-value">{{ selectedIndicators.length }}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Last Price</span>
                        <span class="summary-value">
                            {{ chartData.ohlcv.close?.[chartData.ohlcv.close.length - 1]?.toFixed(2) || 'N/A' }}
                        </span>
                    </div>
                </div>
            </el-card>
        </div>

        <!-- Indicator Selection Panel -->
        <el-drawer v-model="showIndicatorPanel" title="Technical Indicators" size="400px" :close-on-click-modal="false">
            <div class="indicator-drawer">
                <div class="indicator-categories">
                    <div v-for="category in indicatorCategories" :key="category.key" class="category-section">
                        <h4 class="category-title">{{ category.name }}</h4>
                        <div class="indicators-list">
                            <el-checkbox
                                v-for="(indicator, _idx) in category.indicators"
                                :key="indicator.name"
                                v-model="indicator.selected"
                                @change="handleIndicatorToggle(indicator)"
                                class="indicator-checkbox"
                            >
                                <div class="indicator-info">
                                    <span class="indicator-name">{{ indicator.displayName }}</span>
                                    <span class="indicator-desc">{{ indicator.description }}</span>
                                </div>
                            </el-checkbox>
                        </div>
                    </div>
                </div>
            </div>
        </el-drawer>
    </div>
</template>

<script setup lang="ts">
import { useTechnical } from './composables/useTechnical'

const {
  loading,
  selectedSymbol,
  symbolName,
  dateRange,
  selectedPeriod,
  chartType,
  chartHeight,
  lastUpdate,
  showIndicatorPanel,
  chartData,
  selectedIndicators,
  indicatorCategories,
  dateShortcuts,
  handleSymbolChange,
  handleDateRangeChange,
  handlePeriodChange,
  handleChartTypeChange,
  refreshData,
  fetchChartData,
  handleIndicatorToggle,
  formatParams,
  removeIndicator
} = useTechnical()
</script>

<style scoped lang="scss">
@import './styles/Technical.scss';
</style>
