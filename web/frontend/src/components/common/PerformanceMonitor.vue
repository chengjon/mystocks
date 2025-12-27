<template>
  <div class="performance-monitor" v-if="enabled">
    <el-card class="monitor-card" :body-style="{ padding: '12px' }">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Timer /></el-icon>
            性能监控
          </span>
          <div class="header-controls">
            <el-tag :type="overallStatus.type" size="small">
              {{ overallStatus.text }}
            </el-tag>
            <el-switch
              v-model="enabled"
              size="small"
              @change="handleToggle"
            />
          </div>
        </div>
      </template>

      <div class="metrics-grid">
        <!-- 计算耗时 -->
        <div class="metric-item">
          <div class="metric-label">计算耗时</div>
          <div class="metric-value" :class="getMetricClass(calculationTime, 100)">
            {{ calculationTime.toFixed(2) }}<span class="unit">ms</span>
          </div>
          <div class="metric-bar">
            <div
              class="bar-fill"
              :style="{ width: `${Math.min(calculationTime / 5, 100)}%` }"
              :class="getMetricClass(calculationTime, 100)"
            ></div>
          </div>
        </div>

        <!-- 数据点数 -->
        <div class="metric-item">
          <div class="metric-label">数据点数</div>
          <div class="metric-value">
            {{ dataPointCount.toLocaleString() }}
          </div>
          <div class="metric-bar">
            <div
              class="bar-fill blue"
              :style="{ width: `${Math.min(dataPointCount / 100, 100)}%` }"
            ></div>
          </div>
        </div>

        <!-- API响应时间 -->
        <div class="metric-item">
          <div class="metric-label">API响应</div>
          <div class="metric-value" :class="getMetricClass(apiResponseTime, 500)">
            {{ apiResponseTime.toFixed(2) }}<span class="unit">ms</span>
          </div>
          <div class="metric-bar">
            <div
              class="bar-fill"
              :style="{ width: `${Math.min(apiResponseTime / 10, 100)}%` }"
              :class="getMetricClass(apiResponseTime, 500)"
            ></div>
          </div>
        </div>

        <!-- 渲染FPS -->
        <div class="metric-item">
          <div class="metric-label">渲染FPS</div>
          <div class="metric-value" :class="getFPSClass(renderFPS)">
            {{ renderFPS.toFixed(1) }}
          </div>
          <div class="metric-bar">
            <div
              class="bar-fill green"
              :style="{ width: `${Math.min(renderFPS / 60 * 100, 100)}%` }"
            ></div>
          </div>
        </div>

        <!-- 内存占用 -->
        <div class="metric-item">
          <div class="metric-label">内存占用</div>
          <div class="metric-value" :class="getMemoryClass(memoryUsage)">
            {{ memoryUsage.toFixed(1) }}<span class="unit">MB</span>
          </div>
          <div class="metric-bar">
            <div
              class="bar-fill"
              :style="{ width: `${Math.min(memoryUsage / 2, 100)}%` }"
              :class="getMemoryClass(memoryUsage)"
            ></div>
          </div>
        </div>
      </div>

      <!-- 历史趋势图 -->
      <div class="history-section" v-if="showHistory">
        <el-divider />
        <div class="history-title">历史趋势（最近20次）</div>
        <div class="history-charts">
          <div class="history-chart">
            <div class="chart-label">计算耗时趋势</div>
            <div class="sparkline" ref="calculationHistoryRef"></div>
          </div>
          <div class="history-chart">
            <div class="chart-label">API响应趋势</div>
            <div class="sparkline" ref="apiHistoryRef"></div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { Timer } from '@element-plus/icons-vue'

// Props
const props = defineProps({
  // 是否默认启用
  defaultEnabled: {
    type: Boolean,
    default: false
  },
  // 是否显示历史趋势
  showHistory: {
    type: Boolean,
    default: true
  },
  // 历史数据保留数量
  historySize: {
    type: Number,
    default: 20
  }
})

// Emits
const emit = defineEmits(['toggle', 'metric-update'])

// 状态
const enabled = ref(props.defaultEnabled)
const calculationTime = ref(0)
const dataPointCount = ref(0)
const apiResponseTime = ref(0)
const renderFPS = ref(60)
const memoryUsage = ref(0)

// 历史数据
const calculationHistory = ref([])
const apiHistory = ref([])

// Refs
const calculationHistoryRef = ref(null)
const apiHistoryRef = ref(null)

// 性能监控API
let performanceObserver = null
let lastFrameTime = performance.now()
let frameCount = 0
let fpsUpdateInterval = null

// 计算属性
const overallStatus = computed(() => {
  // 判断整体性能状态
  const calcScore = calculationTime.value > 100 ? 1 : 0
  const apiScore = apiResponseTime.value > 500 ? 1 : 0
  const fpsScore = renderFPS.value < 30 ? 1 : 0
  const memoryScore = memoryUsage.value > 100 ? 1 : 0

  const totalScore = calcScore + apiScore + fpsScore + memoryScore

  if (totalScore === 0) {
    return { type: 'success', text: '优秀' }
  } else if (totalScore <= 1) {
    return { type: 'warning', text: '良好' }
  } else {
    return { type: 'danger', text: '需优化' }
  }
})

// 方法
const getMetricClass = (value, threshold) => {
  if (value < threshold * 0.5) return 'green'
  if (value < threshold) return 'yellow'
  return 'red'
}

const getFPSClass = (fps) => {
  if (fps >= 50) return 'green'
  if (fps >= 30) return 'yellow'
  return 'red'
}

const getMemoryClass = (memory) => {
  if (memory < 50) return 'green'
  if (memory < 100) return 'yellow'
  return 'red'
}

const updateCalculationTime = (time) => {
  calculationTime.value = time
  calculationHistory.value.push(time)
  if (calculationHistory.value.length > props.historySize) {
    calculationHistory.value.shift()
  }
  emit('metric-update', { type: 'calculation', value: time })
  renderHistoryCharts()
}

const updateDataPointCount = (count) => {
  dataPointCount.value = count
  emit('metric-update', { type: 'dataPoints', value: count })
}

const updateApiResponseTime = (time) => {
  apiResponseTime.value = time
  apiHistory.value.push(time)
  if (apiHistory.value.length > props.historySize) {
    apiHistory.value.shift()
  }
  emit('metric-update', { type: 'api', value: time })
  renderHistoryCharts()
}

const updateRenderFPS = () => {
  frameCount++
  const now = performance.now()
  const elapsed = now - lastFrameTime

  if (elapsed >= 1000) {
    renderFPS.value = (frameCount / elapsed) * 1000
    frameCount = 0
    lastFrameTime = now
  }
}

const updateMemoryUsage = () => {
  if (performance.memory) {
    memoryUsage.value = performance.memory.usedJSHeapSize / 1024 / 1024
  }
}

// 渲染历史趋势图（简单的CSS sparkline）
const renderHistoryCharts = () => {
  nextTick(() => {
    if (calculationHistoryRef.value && calculationHistory.value.length > 1) {
      renderSparkline(calculationHistoryRef.value, calculationHistory.value, 100)
    }
    if (apiHistoryRef.value && apiHistory.value.length > 1) {
      renderSparkline(apiHistoryRef.value, apiHistory.value, 500)
    }
  })
}

const renderSparkline = (element, data, maxValue) => {
  const width = element.offsetWidth || 200
  const height = element.offsetHeight || 40
  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * width
    const y = height - (value / maxValue) * height
    return `${x},${y}`
  }).join(' ')

  element.innerHTML = `
    <svg width="${width}" height="${height}" style="overflow: visible">
      <polyline
        points="${points}"
        fill="none"
        stroke="#409EFF"
        stroke-width="2"
        vector-effect="non-scaling-stroke"
      />
    </svg>
  `
}

// 启动FPS监控
const startFPSMonitoring = () => {
  const updateFPS = () => {
    updateRenderFPS()
    requestAnimationFrame(updateFPS)
  }
  requestAnimationFrame(updateFPS)
}

// 启动内存监控
const startMemoryMonitoring = () => {
  setInterval(() => {
    updateMemoryUsage()
  }, 2000)
}

// 暴露给父组件的方法
const updateMetrics = (metrics) => {
  if (metrics.calculationTime !== undefined) {
    updateCalculationTime(metrics.calculationTime)
  }
  if (metrics.dataPointCount !== undefined) {
    updateDataPointCount(metrics.dataPointCount)
  }
  if (metrics.apiResponseTime !== undefined) {
    updateApiResponseTime(metrics.apiResponseTime)
  }
}

const reset = () => {
  calculationTime.value = 0
  dataPointCount.value = 0
  apiResponseTime.value = 0
  renderFPS.value = 60
  memoryUsage.value = 0
  calculationHistory.value = []
  apiHistory.value = []
}

const handleToggle = (val) => {
  emit('toggle', val)
}

// 生命周期
onMounted(() => {
  startFPSMonitoring()
  startMemoryMonitoring()
})

onBeforeUnmount(() => {
  if (fpsUpdateInterval) {
    clearInterval(fpsUpdateInterval)
  }
})

// 暴露方法给父组件
defineExpose({
  updateMetrics,
  reset
})
</script>

<style scoped lang="scss">
.performance-monitor {
  position: fixed;
  top: 80px;
  right: 20px;
  width: 280px;
  z-index: 1000;

  .monitor-card {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    border-radius: 8px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        font-weight: 600;
        color: #303133;
      }

      .header-controls {
        display: flex;
        align-items: center;
        gap: 12px;
      }
    }

    .metrics-grid {
      display: grid;
      gap: 12px;

      .metric-item {
        .metric-label {
          font-size: 12px;
          color: #909399;
          margin-bottom: 4px;
        }

        .metric-value {
          font-size: 20px;
          font-weight: 600;
          color: #303133;
          margin-bottom: 4px;

          .unit {
            font-size: 12px;
            font-weight: normal;
            color: #909399;
            margin-left: 2px;
          }

          &.green {
            color: #67C23A;
          }

          &.yellow {
            color: #E6A23C;
          }

          &.red {
            color: #F56C6C;
          }
        }

        .metric-bar {
          height: 4px;
          background: #F5F7FA;
          border-radius: 2px;
          overflow: hidden;

          .bar-fill {
            height: 100%;
            border-radius: 2px;
            transition: width 0.3s ease;

            &.green {
              background: linear-gradient(90deg, #67C23A, #85CE61);
            }

            &.yellow {
              background: linear-gradient(90deg, #E6A23C, #EEBE77);
            }

            &.red {
              background: linear-gradient(90deg, #F56C6C, #F78989);
            }

            &.blue {
              background: linear-gradient(90deg, #409EFF, #66B1FF);
            }
          }
        }
      }
    }

    .history-section {
      margin-top: 12px;

      .history-title {
        font-size: 12px;
        color: #909399;
        margin-bottom: 8px;
      }

      .history-charts {
        display: grid;
        gap: 8px;

        .history-chart {
          .chart-label {
            font-size: 11px;
            color: #909399;
            margin-bottom: 4px;
          }

          .sparkline {
            height: 40px;
            background: #F5F7FA;
            border-radius: 4px;
            padding: 4px;
          }
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .performance-monitor {
    top: auto;
    bottom: 20px;
    right: 20px;
    width: calc(100vw - 40px);
    max-width: 280px;
  }
}
</style>
