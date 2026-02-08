<template>
  <div class="artdeco-chart-container" :class="{ 'is-loading': loading }">
    <!-- Chart Container -->
    <div ref="chartElement" class="chart-canvas" :style="{ height: height, width: width }"></div>

    <!-- Loading State -->
    <div v-if="loading" class="chart-loading-overlay">
      <ArtDecoSkeleton variant="rect" width="100%" height="100%" />
    </div>

    <!-- Error/Empty State -->
    <div v-if="!loading && isEmpty" class="chart-empty-state">
      <ArtDecoIcon name="BarChart2" size="xl" class="empty-icon" />
      <span class="empty-text">No Data Available</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'
import * as echarts from 'echarts'
import ArtDecoSkeleton from '@/components/artdeco/core/ArtDecoSkeleton.vue'
import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'
import { ARTDECO_THEME } from '@/styles/echarts-theme' // Create this separate file

// Props
const props = defineProps({
  option: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  height: {
    type: String,
    default: '300px'
  },
  width: {
    type: String,
    default: '100%'
  }
})

// State
const chartElement = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

// Computed
const isEmpty = computed(() => {
  if (!props.option || !props.option.series || props.option.series.length === 0) return true
  // Check if data arrays are empty
  return props.option.series.every((s: any) => !s.data || s.data.length === 0)
})

// Methods
const initChart = () => {
  if (!chartElement.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }

  // Use the registered theme 'artDeco'
  chartInstance = echarts.init(chartElement.value, 'artDeco')
  
  if (props.option) {
    chartInstance.setOption(props.option)
  }
}

const resize = () => {
  chartInstance?.resize()
}

// Lifecycle
onMounted(() => {
  // Register theme if not already (assuming global registration or import)
  if (!echarts.getTheme('artDeco')) {
      echarts.registerTheme('artDeco', ARTDECO_THEME)
  }

  initChart()

  resizeObserver = new ResizeObserver(() => {
    resize()
  })
  if (chartElement.value) {
    resizeObserver.observe(chartElement.value)
  }
  
  window.addEventListener('resize', resize)
})

// Watchers
watch(() => props.option, (newOption) => {
  if (chartInstance && newOption) {
    chartInstance.setOption(newOption, true) // true = not merge, replace? No, usually merge. let's check. 
    // chartInstance.setOption(newOption) is merge. 
    // If we want complete replace, we use setOption(newOption, true)
    // For now, let's use merge (default) to animate updates
    chartInstance.setOption(newOption)
  }
}, { deep: true })

watch(() => props.loading, (isLoading) => {
  if (!isLoading) {
    // Re-init or resize might be needed if container size changed during loading
    setTimeout(() => {
        resize()
    }, 50)
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.artdeco-chart-container {
  position: relative;
  width: 100%;
}

.chart-canvas {
  width: 100%;
}

.chart-loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 10;
  background: var(--artdeco-bg-surface);
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-empty-state {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--artdeco-fg-muted);
  background: rgba(0,0,0,0.1);
  z-index: 5;
  
  .empty-icon {
    margin-bottom: 8px;
    opacity: 0.5;
  }
  
  .empty-text {
    font-size: 12px;
    letter-spacing: 0.05em;
  }
}
</style>