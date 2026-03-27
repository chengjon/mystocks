<template>
  <div class="health-radar-chart">
    <!-- 图表头部 -->
    <div class="chart-header">
      <div class="header-info">
        <h3 class="fintech-text-primary chart-title">HEALTH RADAR</h3>
        <p class="fintech-text-secondary chart-subtitle">5-Dimension Portfolio Analysis</p>
      </div>
      <div class="header-actions">
        <button class="fintech-btn" @click="toggleView" v-if="hasComparison">
          <swap-outlined />
          <span>{{ showComparison ? 'SINGLE' : 'COMPARE' }}</span>
        </button>
        <button class="fintech-btn" @click="exportChart">
          <download-outlined />
        </button>
      </div>
    </div>

    <!-- 图表容器 -->
    <div class="chart-content">
      <div class="radar-container">
        <div ref="chartRef" class="chart-canvas" :style="{ height: chartHeight, width: '100%' }"></div>

        <!-- 中心数值显示 -->
        <div class="center-display">
          <div class="center-value fintech-text-primary">{{ averageScore.toFixed(1) }}</div>
          <div class="center-label fintech-text-secondary">AVG SCORE</div>
        </div>
      </div>

      <!-- 图例 -->
      <div v-if="showLegend" class="legend-panel">
        <div class="legend-header">
          <h4 class="fintech-text-primary legend-title">DIMENSIONS</h4>
        </div>
        <div class="legend-items">
          <div
            v-for="(item, index) in legendItems"
            :key="index"
            class="legend-item"
            :class="{ active: hoveredDimension === item.key }"
            @mouseenter="highlightDimension(item.key)"
            @mouseleave="clearHighlight()"
          >
            <div class="legend-indicator">
              <span class="legend-color" :style="{ backgroundColor: item.color }"></span>
              <span class="legend-rank">#{{ index + 1 }}</span>
            </div>
            <div class="legend-info">
              <div class="legend-name fintech-text-primary">{{ item.name }}</div>
              <div class="legend-value fintech-text-secondary">
                {{ item.value.toFixed(1) }}
                <span class="value-change" :class="getChangeClass(item.change)">
                  {{ getChangeText(item.change) }}
                </span>
              </div>
            </div>
            <div class="legend-bar">
              <div class="bar-track">
                <div
                  class="bar-fill"
                  :style="{ width: `${(item.value / 100) * 100}%`, backgroundColor: item.color }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部统计 -->
    <div class="chart-footer">
      <div class="footer-stats">
        <div class="stat-item">
          <span class="stat-label fintech-text-secondary">BEST</span>
          <span class="stat-value fintech-text-up">{{ bestDimension }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label fintech-text-secondary">WORST</span>
          <span class="stat-value fintech-text-down">{{ worstDimension }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label fintech-text-secondary">TREND</span>
          <span class="stat-value" :class="overallTrend >= 0 ? 'fintech-text-up' : 'fintech-text-down'">
            {{ overallTrend >= 0 ? '↗ IMPROVING' : '↘ DECLINING' }}
          </span>
        </div>
      </div>
    </div>

    <!-- 工具提示层 -->
    <div v-if="tooltip.visible" class="tooltip-overlay" :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }">
      <div class="tooltip-content">
        <div class="tooltip-title fintech-text-primary">{{ tooltip.title }}</div>
        <div class="tooltip-value fintech-text-secondary">{{ tooltip.value }}</div>
        <div class="tooltip-desc fintech-text-tertiary">{{ tooltip.description }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useHealthRadarChart } from './composables/useHealthRadarChart'

const {
  chartRef,
  showComparison,
  hoveredDimension,
  tooltip,
  chartHeight,
  hasComparison,
  averageScore,
  legendItems,
  bestDimension,
  worstDimension,
  overallTrend,
  getChangeClass,
  getChangeText,
  highlightDimension,
  clearHighlight,
  toggleView,
  exportChart
} = useHealthRadarChart()
</script>

<style scoped lang="scss">
@use "./styles/HealthRadarChart.css";
</style>
