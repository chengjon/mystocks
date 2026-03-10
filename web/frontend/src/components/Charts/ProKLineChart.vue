<template>
  <div class="pro-kline-chart" ref="chartContainer">
    <div class="chart-toolbar">
      <div class="toolbar-left">
        <select v-model="selectedSymbol" class="chart-toolbar-select" @change="onSymbolChange">
          <option v-for="symbol in availableSymbols" :key="symbol.code" :value="symbol.code">
            {{ symbol.name }} ({{ symbol.code }})
          </option>
        </select>

        <select v-model="selectedInterval" class="chart-toolbar-select" @change="onIntervalChange">
          <option v-for="interval in intervals" :key="interval.value" :value="interval.value">
            {{ interval.label }}
          </option>
        </select>

        <select v-model="selectedAdjust" class="chart-toolbar-select" @change="onAdjustChange">
          <option value="qfq">前复权</option>
          <option value="hfq">后复权</option>
          <option value="none">不复权</option>
        </select>
      </div>

      <div class="toolbar-center">
        <button
          v-for="(indicator, _idx) in mainIndicators"
          :key="indicator.key"
          :class="['chart-toolbar-btn', { active: activeMainIndicators.has(indicator.key) }]"
          @click="toggleMainIndicator(indicator.key)"
        >
          {{ indicator.label }}
        </button>
      </div>

      <div class="toolbar-right">
        <button class="chart-toolbar-btn" @click="toggleOscillatorPanel">
          {{ showOscillatorPanel ? '隐藏副图' : '显示副图' }}
        </button>
        <button class="chart-toolbar-btn" @click="handleZoomIn">+</button>
        <button class="chart-toolbar-btn" @click="handleZoomOut">-</button>
        <button class="chart-toolbar-btn" @click="handleResetView">重置</button>
      </div>
    </div>

    <div class="chart-info">
      <div class="info-group">
        <div class="info-item">
          <span class="info-label">最新</span>
          <span :class="['info-value', (latestChange ?? 0) >= 0 ? 'up' : 'down']">
            {{ latestClose?.toFixed(2) }}
          </span>
        </div>
        <div class="info-item">
          <span class="info-label">涨跌</span>
          <span :class="['info-value', (latestChange ?? 0) >= 0 ? 'up' : 'down']">
            {{ (latestChange ?? 0) >= 0 ? '+' : '' }}{{ latestChange?.toFixed(2) }}
          </span>
        </div>
        <div class="info-item">
          <span class="info-label">涨幅</span>
          <span :class="['info-value', (latestChange ?? 0) >= 0 ? 'up' : 'down']">
            {{ (latestChange ?? 0) >= 0 ? '+' : '' }}{{ latestChangePercent?.toFixed(2) }}%
          </span>
        </div>
      </div>
      <div class="info-group">
        <div class="info-item">
          <span class="info-label">最高</span>
          <span class="info-value">{{ latestHigh?.toFixed(2) }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">最低</span>
          <span class="info-value">{{ latestLow?.toFixed(2) }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">成交量</span>
          <span class="info-value">{{ formatVolume(latestVolume) }}</span>
        </div>
      </div>
      <div class="info-group" v-if="limitData">
        <div class="info-item">
          <span class="info-label">涨停</span>
          <span class="info-value up">{{ limitData.limit_up.toFixed(2) }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">跌停</span>
          <span class="info-value down">{{ limitData.limit_down.toFixed(2) }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">涨跌幅</span>
          <span class="info-value">{{ (limitData.limit_pct * 100).toFixed(1) }}%</span>
        </div>
      </div>
    </div>

    <div class="chart-content">
      <div ref="klineRef" class="kline-chart"></div>

      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <div class="loading-text">加载数据中...</div>
      </div>

      <div v-if="error" class="error-toast">
        <span class="error-icon">!</span>
        <span class="error-text">{{ error }}</span>
        <button class="error-retry" @click="handleRetry">重试</button>
      </div>
    </div>

    <div v-if="showOscillatorPanel" class="oscillator-panel">
      <div class="oscillator-tabs">
        <button
          v-for="(indicator, _idx) in oscillatorIndicators"
          :key="indicator.key"
          :class="['oscillator-tab', { active: activeOscillatorIndicator === indicator.key }]"
          @click="activeOscillatorIndicator = indicator.key; updateOscillatorIndicator()"
        >
          {{ indicator.label }}
        </button>
      </div>
      <div ref="oscillatorRef" class="oscillator-chart"></div>
    </div>
  </div>
</template>

<script lang="ts">

</script>

<script setup lang="ts">
import { useProKLineChart } from './composables/useProKLineChart'

const {
  chartContainer,
  klineRef,
  oscillatorRef,
  selectedSymbol,
  selectedInterval,
  selectedAdjust,
  showOscillatorPanel,
  activeMainIndicators,
  activeOscillatorIndicator,
  availableSymbols,
  intervals,
  mainIndicators,
  oscillatorIndicators,
  latestClose,
  latestChange,
  latestChangePercent,
  latestHigh,
  latestLow,
  latestVolume,
  formatVolume,
  toggleMainIndicator,
  updateOscillatorIndicator,
  onSymbolChange,
  onIntervalChange,
  onAdjustChange,
  toggleOscillatorPanel,
  handleZoomIn,
  handleZoomOut,
  handleResetView,
  handleRetry,
  loading,
  error,
  limitData
} = useProKLineChart()
</script>

<style scoped>
@import "./styles/ProKLineChart.css";
</style>
