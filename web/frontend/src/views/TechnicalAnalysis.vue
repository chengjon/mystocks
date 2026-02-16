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
    <el-card class="chart-section">
      <template #header>
        <div class="card-header">
          <span class="card-title">K-LINE CHART</span>
        </div>
      </template>

      <ProKLineChart
        :symbol="chartData.symbol"
        :data="chartData.ohlcv"
        :indicators="chartData.indicators"
        :loading="loading"
        :last-update="lastUpdateTime"
        @indicator-remove="handleIndicatorRemove"
      />
    </el-card>

    <!-- 指标选择面板 -->
    <IndicatorPanel
      v-model="showIndicatorPanel"
      :selected-indicators="selectedIndicators"
      @add-indicator="handleAddIndicator"
      @remove-indicator="handleRemoveIndicator"
    />

    <!-- 数据统计信息 -->
    <el-card v-if="chartData.ohlcv" class="stats-section">
      <template #header>
        <div class="card-header">
          <span class="card-title">ANALYSIS SUMMARY</span>
        </div>
      </template>

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
    </el-card>
  </div>
</template>

<script setup lang="ts">
import StockSearchBar from '@/components/technical/StockSearchBar.vue'
import ProKLineChart from '@/components/market/ProKLineChart.vue'
import IndicatorPanel from '@/components/technical/IndicatorPanel.vue'
import { useTechnicalAnalysis } from './composables/useTechnicalAnalysis'

const {
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
  handleConfigCommand
} = useTechnicalAnalysis()
</script>

<style scoped>
@import "./styles/TechnicalAnalysis.css";
</style>
