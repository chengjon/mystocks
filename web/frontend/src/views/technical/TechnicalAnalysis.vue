<template>
  <div class="web3-technical-analysis">
    <!-- Page header with gradient text -->
    <div class="web3-page-header">
      <h1 class="web3-page-title">
        <span class="gradient-text">TECHNICAL ANALYSIS SYSTEM</span>
      </h1>
      <p class="web3-page-subtitle">26 TECHNICAL INDICATORS & TRADING SIGNAL GENERATION</p>
    </div>

    <!-- Search and Filter -->
    <Web3Card class="search-card" hoverable>
      <el-form :inline="true" :model="searchForm" class="web3-search-form">
        <el-form-item label="SYMBOL">
          <Web3Input
            v-model="searchForm.symbol"
            placeholder="ENTER STOCK SYMBOL"
            clearable
            style="width: 180px"
          />
        </el-form-item>

        <el-form-item label="INDICATORS">
          <el-select
            v-model="searchForm.indicators"
            multiple
            placeholder="SELECT INDICATORS"
            style="width: 320px"
          >
            <el-option
              v-for="(indicator, _idx) in availableIndicators"
              :key="indicator.value"
              :label="indicator.label"
              :value="indicator.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="DATE RANGE">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            start-placeholder="START DATE"
            end-placeholder="END DATE"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <el-form-item>
          <Web3Button type="primary" @click="fetchTechnicalData" :loading="loading.search">
            SEARCH
          </Web3Button>
          <Web3Button variant="secondary" @click="resetSearch">
            RESET
          </Web3Button>
        </el-form-item>
      </el-form>
    </Web3Card>

    <!-- Indicators Overview -->
    <el-row :gutter="20" class="indicators-overview">
      <el-col :xs="24" :sm="12" :md="8">
        <Web3Card class="indicator-card" hoverable>
          <div class="indicator-content">
            <div class="indicator-header">
              <div class="icon-wrapper">
                <el-icon :size="32"><TrendCharts /></el-icon>
              </div>
              <h3>TREND</h3>
            </div>
            <div class="indicator-value gradient-text">
              {{ indicatorStats.trend || 0 }} INDICATORS
            </div>
            <div class="indicator-description">
              MA, EMA, MACD, BOLL
            </div>
          </div>
        </Web3Card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8">
        <Web3Card class="indicator-card" hoverable>
          <div class="indicator-content">
            <div class="indicator-header">
              <div class="icon-wrapper">
                <el-icon :size="32"><Odometer /></el-icon>
              </div>
              <h3>MOMENTUM</h3>
            </div>
            <div class="indicator-value gradient-text">
              {{ indicatorStats.momentum || 0 }} INDICATORS
            </div>
            <div class="indicator-description">
              RSI, KDJ, CCI, W%R
            </div>
          </div>
        </Web3Card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8">
        <Web3Card class="indicator-card" hoverable>
          <div class="indicator-content">
            <div class="indicator-header">
              <div class="icon-wrapper">
                <el-icon :size="32"><DataAnalysis /></el-icon>
              </div>
              <h3>SIGNALS</h3>
            </div>
            <div class="indicator-value" :class="signalCountClass">
              {{ indicatorStats.signals || 0 }} SIGNALS
            </div>
            <div class="indicator-description">
              BUY / SELL SIGNALS
            </div>
          </div>
        </Web3Card>
      </el-col>
    </el-row>

    <!-- Technical Indicators Chart -->
    <Web3Card class="chart-card" hoverable>
      <template #header>
        <div class="flex-between">
          <span class="web3-section-title">
            I. {{ selectedStock ? selectedStock.symbol.toUpperCase() + ' ' + selectedStock.name.toUpperCase() : 'TECHNICAL INDICATORS CHART' }}
          </span>
          <div class="card-actions">
            <Web3Button variant="secondary" size="small" @click="exportChart">
              EXPORT CHART
            </Web3Button>
          </div>
        </div>
      </template>

      <div v-if="selectedStock" class="chart-wrapper">
        <div ref="chartContainer" class="web3-chart-container"></div>
      </div>
      <el-empty v-else description="PLEASE SELECT A STOCK TO VIEW TECHNICAL INDICATORS" />
    </Web3Card>

    <!-- Indicators Details Table -->
    <Web3Card class="indicators-card" hoverable>
      <template #header>
        <div class="flex-between">
          <span class="web3-section-title">II. INDICATORS DETAILS</span>
        </div>
      </template>

      <el-table
        :data="indicatorsData"
        class="web3-table"
        v-loading="loading.indicators"
        row-key="id"
      >
        <el-table-column prop="name" label="INDICATOR" width="180">
          <template #default="{ row }">
            <strong class="gradient-text">{{ row.name }}</strong>
            <el-tag size="small" :type="getIndicatorTypeTag(row.type)" class="web3-tag">
              {{ formatIndicatorType(row.type) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="value" label="CURRENT VALUE" width="140" align="right">
          <template #default="{ row }">
            <span :class="getValueClass(row)">
              {{ formatIndicatorValue(row) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="signal" label="SIGNAL" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.signal" :type="getSignalTagType(row.signal)" size="small" class="web3-tag">
              {{ formatSignal(row.signal) }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="STATUS" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small" class="web3-tag">
              {{ formatStatus(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="description" label="DESCRIPTION" min-width="220" />
        <el-table-column prop="last_updated" label="UPDATED" width="160" />
      </el-table>
    </Web3Card>

    <!-- Batch Calculation -->
    <Web3Card class="batch-card" hoverable>
      <template #header>
        <div class="flex-between">
          <span class="web3-section-title">III. BATCH CALCULATION</span>
        </div>
      </template>

      <el-form :inline="true" :model="batchForm" class="web3-batch-form">
        <el-form-item label="SYMBOLS">
          <Web3Input
            v-model="batchForm.symbols"
            placeholder="ENTER STOCK SYMBOLS, COMMA-SEPARATED"
            style="width: 440px"
          />
        </el-form-item>

        <el-form-item label="INDICATORS">
          <el-select
            v-model="batchForm.indicators"
            multiple
            placeholder="SELECT INDICATORS TO CALCULATE"
            style="width: 320px"
          >
            <el-option
              v-for="(indicator, _idx) in availableIndicators"
              :key="indicator.value"
              :label="indicator.label"
              :value="indicator.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <Web3Button
            type="primary"
            @click="calculateBatchIndicators"
            :loading="loading.batch"
            :disabled="!batchForm.symbols"
          >
            START CALCULATION
          </Web3Button>
        </el-form-item>
      </el-form>

      <div v-if="batchResult" class="batch-result">
        <el-alert
          :type="batchResult.success ? 'success' : 'error'"
          :closable="false"
          show-icon
        >
          <template #default>
            <p>{{ batchResult.message }}</p>
            <div v-if="batchResult.data">
              <p>STOCKS CALCULATED: {{ batchResult.data.stocks_count }}</p>
              <p>SUCCESSFUL CALCULATIONS: {{ batchResult.data.success_count }}</p>
              <p>SIGNALS GENERATED: {{ batchResult.data.signals_count }}</p>
            </div>
          </template>
        </el-alert>
      </div>
    </Web3Card>
  </div>
</template>

<script setup lang="ts">
import { useTechnicalAnalysis } from './composables/useTechnicalAnalysis'

const {
  searchForm,
  batchForm,
  loading,
  selectedStock,
  indicatorsData,
  chartContainer,
  chartInstance,
  batchResult,
  availableIndicators,
  indicatorStats,
  getIndicatorTypeTag,
  formatIndicatorType,
  getValueClass,
  formatIndicatorValue,
  getSignalTagType,
  formatSignal,
  getStatusTagType,
  formatStatus,
  signalCountClass,
  fetchTechnicalData,
  updateIndicatorStats,
  renderChart,
  resetSearch,
  exportChart,
  calculateBatchIndicators
} = useTechnicalAnalysis()
</script>

<style scoped lang="scss">
@import "./styles/TechnicalAnalysis";
</style>
