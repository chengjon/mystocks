<template>
  <div class="kline-chart-container">
    <!-- 图表加载状态 (增强版: 骨架屏 + 进度指示器) -->
    <ChartLoadingSkeleton
      v-if="loading"
      :show-progress="showLoadingProgress"
      :progress="loadingProgress"
      :loading-text="loadingText"
      :sub-text="loadingSubText"
    />

    <!-- 图表主容器 -->
    <div
      v-show="!loading"
      ref="chartContainer"
      class="chart-canvas"
    />

    <!-- 图表工具栏 -->
    <div v-show="!loading" class="chart-toolbar">
      <el-space wrap>
        <!-- 周期切换 -->
        <el-radio-group v-model="currentPeriod" size="small" @change="handlePeriodChange">
          <el-radio-button label="1min">分时</el-radio-button>
          <el-radio-button label="5min">5分钟</el-radio-button>
          <el-radio-button label="15min">15分钟</el-radio-button>
          <el-radio-button label="30min">30分钟</el-radio-button>
          <el-radio-button label="60min">60分钟</el-radio-button>
          <el-radio-button label="1day">日线</el-radio-button>
        </el-radio-group>

        <!-- 图表类型 -->
        <el-dropdown trigger="click" @command="handleChartTypeChange">
          <el-button size="small">
            {{ currentChartType }}
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="candle_solid">蜡烛图</el-dropdown-item>
              <el-dropdown-item command="candle_stroke">空心蜡烛</el-dropdown-item>
              <el-dropdown-item command="candle_up_stroke">涨空心跌实心</el-dropdown-item>
              <el-dropdown-item command="ohlc">OHLC</el-dropdown-item>
              <el-dropdown-item command="area">面积图</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!-- 主图指标管理 (增强版: 可见性切换) -->
        <el-tag
          v-for="(indicator, index) in overlayIndicators"
          :key="`overlay-${index}`"
          closable
          size="small"
          :type="indicator.visible ? 'info' : 'warning'"
          :style="{ opacity: indicator.visible ? 1 : 0.5 }"
          @close="handleRemoveIndicator(index)"
        >
          <el-icon
            :size="14"
            style="margin-right: 4px; cursor: pointer;"
            @click.stop="handleToggleIndicator(indicator)"
          >
            <component :is="indicator.visible ? View : Hide" />
          </el-icon>
          {{ indicator.name }}
        </el-tag>

        <!-- 分隔线 -->
        <el-divider direction="vertical" />

        <!-- 缩放控制 -->
        <el-button-group size="small">
          <el-button @click="zoomOut">-</el-button>
          <el-button disabled>{{ zoomLevels[currentZoomIndex] }}x</el-button>
          <el-button @click="zoomIn">+</el-button>
        </el-button-group>

        <!-- 平移控制 -->
        <el-button-group size="small">
          <el-button @click="panChart('left')">◀</el-button>
          <el-button @click="panChart('right')">▶</el-button>
        </el-button-group>

        <!-- 重置缩放 -->
        <el-button
          size="small"
          :icon="Refresh"
          @click="resetChart"
        >
          重置
        </el-button>

        <!-- 性能监控开关 -->
        <el-tooltip content="性能监控" placement="bottom">
          <el-button
            size="small"
            @click="togglePerformanceMonitor"
          >
            <el-icon><Odometer /></el-icon>
          </el-button>
        </el-tooltip>
      </el-space>
    </div>

    <!-- 性能监控面板 -->
    <PerformanceMonitor
      v-if="showPerformanceMonitor"
      ref="performanceMonitor"
      :default-enabled="true"
      :show-history="true"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { init, dispose } from 'klinecharts'
import { Refresh, ArrowDown, View, Hide, Odometer } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import ChartLoadingSkeleton from '@/components/common/ChartLoadingSkeleton.vue'
import PerformanceMonitor from '@/components/common/PerformanceMonitor.vue'
import { CHART_INIT_OPTIONS, getIndicatorColor } from '@/components/technical/config/klineChartConfig'
import { useKLineData } from '@/composables/useKLineData'
import { useKLineControls } from '@/composables/useKLineControls'

const props = defineProps({
  ohlcvData: {
    type: Object,
    required: true,
    validator: (value) => {
      if (!value || typeof value !== 'object') {
        console.error('[KLineChart] Invalid data: not an object')
        return false
      }

      const requiredFields = ['dates', 'open', 'high', 'low', 'close', 'volume']
      for (const field of requiredFields) {
        if (!Array.isArray(value[field])) {
          console.error(`[KLineChart] Invalid data: ${field} is not an array`)
          return false
        }
      }

      const length = value.dates.length
      for (const field of requiredFields) {
        if (value[field].length !== length) {
          console.error(`[KLineChart] Invalid data: ${field} length mismatch`)
          return false
        }
      }

      return true
    }
  },
  indicators: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['indicator-remove', 'indicator-toggle'])

const chartContainer = ref(null)
const chart = ref(null)
const currentPeriod = ref('1day')
const currentChartType = ref('蜡烛图')
const overlayIndicators = ref([])
const performanceMonitor = ref(null)
const actionSubscriptions = ref([])

const {
  loadingProgress,
  showLoadingProgress,
  loadingText,
  loadingSubText,
  updateChartData,
  cleanup: cleanupData,
  debounce
} = useKLineData(chart, props)

const {
  currentZoomIndex,
  showPerformanceMonitor,
  zoomIn,
  zoomOut,
  panChart,
  resetChart,
  handleChartTypeChange: handleChartTypeChangeControl,
  handlePeriodChange: handlePeriodChangeControl,
  togglePerformanceMonitor,
  _measurePerformance
} = useKLineControls(chart, performanceMonitor)

const initChart = async () => {
  await nextTick()

  if (!chartContainer.value) {
    console.error('[KLineChart] Chart container not found')
    return
  }

  try {
    chart.value = init(chartContainer.value, CHART_INIT_OPTIONS)
    subscribeToChartActions()
    chart.value.createIndicator('VOL', false)

    if (props.ohlcvData) {
      await updateChartData(props.ohlcvData)
    }

    if (props.indicators?.length > 0) {
      updateIndicators(props.indicators)
    }
  } catch (error) {
    console.error('[KLineChart] Failed to initialize chart:', error)
    ElMessage.error('图表初始化失败')
  }
}

const subscribeToChartActions = () => {
  if (!chart.value) return

  try {
    const zoomUnsub = chart.value.subscribeAction('onZoom', (data) => {
      console.log('[KLineChart] Zoom event:', data)
    })

    const scrollUnsub = chart.value.subscribeAction('onScroll', (data) => {
      console.log('[KLineChart] Scroll event:', data)
    })

    actionSubscriptions.value.push(zoomUnsub, scrollUnsub)
  } catch (error) {
    console.error('[KLineChart] Error subscribing to actions:', error)
  }
}

const unsubscribeFromChartActions = () => {
  actionSubscriptions.value.forEach(unsubscribe => {
    try {
      if (typeof unsubscribe === 'function') {
        unsubscribe()
      }
    } catch (error) {
      console.error('[KLineChart] Error unsubscribing from action:', error)
    }
  })
  actionSubscriptions.value = []
}

const cleanup = () => {
  unsubscribeFromChartActions()
  cleanupData()

  if (chart.value && chartContainer.value) {
    try {
      dispose(chartContainer.value)
    } catch (error) {
      console.error('[KLineChart] Error disposing chart:', error)
    }
    chart.value = null
  }
}

const updateIndicators = (indicators) => {
  if (!chart.value || !indicators) return

  try {
    const existingIndicators = new Map()
    overlayIndicators.value.forEach(ind => {
      existingIndicators.set(ind.name, ind.visible !== false)
    })

    overlayIndicators.value = []

    indicators.forEach((indicator, index) => {
      if (indicator.panel_type === 'overlay') {
        const indicatorName = indicator.abbreviation.toUpperCase()

        indicator.outputs.forEach((output) => {
          const wasVisible = existingIndicators.get(output.display_name)

          chart.value.createIndicator(
            indicatorName,
            false,
            { id: 'candle_pane' }
          )

          overlayIndicators.value.push({
            name: output.display_name,
            index: index,
            visible: wasVisible !== false,
            color: getIndicatorColor(index)
          })
        })
      } else if (indicator.panel_type === 'separate') {
        const indicatorName = indicator.abbreviation.toUpperCase()
        chart.value.createIndicator(indicatorName, false)
      }
    })
  } catch (error) {
    console.error('[KLineChart] Failed to update indicators:', error)
    ElMessage.error('指标更新失败')
  }
}

const handleToggleIndicator = (indicator) => {
  if (!chart.value) return

  try {
    indicator.visible = !indicator.visible

    emit('indicator-toggle', {
      name: indicator.name,
      visible: indicator.visible
    })

    ElMessage.success(`${indicator.name} ${indicator.visible ? '已显示' : '已隐藏'}`)
  } catch (error) {
    console.error('[KLineChart] Failed to toggle indicator:', error)
    ElMessage.error('指标切换失败')
  }
}

const handleRemoveIndicator = (index) => {
  emit('indicator-remove', index)
}

const handleChartTypeChange = (type) => {
  const displayName = handleChartTypeChangeControl(type)
  if (displayName) {
    currentChartType.value = displayName
  }
}

const handlePeriodChange = (period) => {
  handlePeriodChangeControl(period)
}

onMounted(() => {
  initChart()
})

onBeforeUnmount(() => {
  cleanup()
})

watch(
  () => props.ohlcvData,
  (newData) => {
    if (newData && chart.value) {
      debounce(() => {
        updateChartData(newData)
      }, 300)()
    }
  },
  { deep: true }
)

watch(
  () => props.indicators,
  (newIndicators) => {
    if (newIndicators && chart.value) {
      updateIndicators(newIndicators)
    }
  },
  { deep: true }
)
</script>

<style scoped lang="scss">
@use '../../styles/artdeco-tokens.scss' as *;

.kline-chart-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
  background: var(--artdeco-bg-global);

  .chart-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--artdeco-fg-muted);

    .el-icon {
      font-size: var(--artdeco-text-4xl);
      margin-bottom: var(--artdeco-spacing-4);
    }

    p {
      font-size: var(--artdeco-text-sm);
    }
  }

  .chart-canvas {
    flex: 1;
    width: 100%;
    min-height: 25rem;
  }

  .chart-toolbar {
    padding: var(--artdeco-spacing-3);
    border-top: 1px solid var(--artdeco-gold-dim);
    background: color-mix(in srgb, var(--artdeco-gold-primary) 6%, var(--artdeco-bg-card));
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-3);
    flex-wrap: wrap;
  }
}

// Responsive design
@media (width <= 48rem) {
  .kline-chart-container {
    .chart-canvas {
      min-height: 18.75rem;
    }

    .chart-toolbar {
      padding: var(--artdeco-spacing-2);

      :deep(.el-radio-group) {
        flex-wrap: wrap;
      }
    }
  }
}
</style>
