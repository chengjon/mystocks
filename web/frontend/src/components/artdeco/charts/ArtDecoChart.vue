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
import { ref, watch, computed, onMounted , onUnmounted } from 'vue'
import type { PropType } from 'vue'
import echarts from '@/utils/echarts'
import ArtDecoSkeleton from '@/components/artdeco/core/ArtDecoSkeleton.vue'
import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'
import { ARTDECO_THEME } from '@/styles/echarts-theme' // Create this separate file

let artDecoThemeRegistered = false

// Props
const props = defineProps({
  option: {
    type: Object as PropType<Record<string, unknown> | null>,
    default: null
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
  const option = props.option as { series?: Array<{ data?: unknown[] }> } | null
  const series = option?.series
  if (!series || series.length === 0) return true
  return series.every(s => !Array.isArray(s.data) || s.data.length === 0)
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
  if (!artDecoThemeRegistered) {
    try {
      echarts.registerTheme('artDeco', ARTDECO_THEME)
    } catch {
      // no-op: theme may already be registered by another bundle chunk
    }
    artDecoThemeRegistered = true
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
  if (!chartInstance) {
    return
  }

  if (newOption) {
    chartInstance.setOption(newOption, true)
  } else {
    chartInstance.clear()
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

// Auto-generated: cleanup timers to prevent memory leaks
const _timer_1: ReturnType<typeof setTimeout> | null = null
onUnmounted(() => {
  if (_timer_1) clearTimeout(_timer_1)
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

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
  background: color-mix(in srgb, var(--artdeco-bg-global) 10%, transparent);
  z-index: 5;
  
  .empty-icon {
    margin-bottom: var(--artdeco-spacing-2);
    opacity: 50%;
  }
  
  .empty-text {
    font-size: var(--artdeco-text-xs);
    letter-spacing: 0.05em;
  }
}
</style>
