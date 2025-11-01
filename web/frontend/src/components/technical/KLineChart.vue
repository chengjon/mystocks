<template>
  <div class="kline-chart-container">
    <!-- 图表加载状态 -->
    <div v-if="loading" class="chart-loading">
      <el-icon class="is-loading">
        <Loading />
      </el-icon>
      <p>加载数据中...</p>
    </div>

    <!-- 图表主容器 -->
    <div
      v-show="!loading"
      ref="chartContainer"
      class="chart-canvas"
    />

    <!-- 图表工具栏 -->
    <div v-show="!loading" class="chart-toolbar">
      <el-space>
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

        <!-- 主图指标管理 -->
        <el-tag
          v-for="(indicator, index) in overlayIndicators"
          :key="`overlay-${index}`"
          closable
          size="small"
          type="info"
          @close="handleRemoveIndicator(index)"
        >
          {{ indicator.name }}
        </el-tag>

        <!-- 重置缩放 -->
        <el-button
          size="small"
          :icon="Refresh"
          @click="resetChart"
        >
          重置
        </el-button>
      </el-space>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { init, dispose } from 'klinecharts'
import { Loading, Refresh, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  ohlcvData: {
    type: Object,
    required: true,
    validator: (value) => {
      return (
        value.dates &&
        value.open &&
        value.high &&
        value.low &&
        value.close &&
        value.volume
      )
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

const emit = defineEmits(['indicator-remove'])

// 状态
const chartContainer = ref(null)
const chart = ref(null)
const currentPeriod = ref('1day')
const currentChartType = ref('蜡烛图')

// 计算属性 - 叠加指标
const overlayIndicators = ref([])

// 初始化图表
onMounted(() => {
  initChart()
})

// 清理图表
onBeforeUnmount(() => {
  if (chart.value) {
    dispose(chartContainer.value)
  }
})

// 监听数据变化
watch(() => props.ohlcvData, (newData) => {
  if (newData && chart.value) {
    updateChartData(newData)
  }
}, { deep: true })

// 监听指标变化
watch(() => props.indicators, (newIndicators) => {
  if (newIndicators && chart.value) {
    updateIndicators(newIndicators)
  }
}, { deep: true })

// 初始化图表
const initChart = async () => {
  await nextTick()

  if (!chartContainer.value) {
    console.error('Chart container not found')
    return
  }

  try {
    // 初始化klinecharts实例
    chart.value = init(chartContainer.value, {
      grid: {
        show: true,
        horizontal: {
          show: true,
          size: 1,
          color: '#e0e0e0',
          style: 'dashed'
        },
        vertical: {
          show: true,
          size: 1,
          color: '#e0e0e0',
          style: 'dashed'
        }
      },
      candle: {
        type: 'candle_solid',
        bar: {
          upColor: '#ef5350',
          downColor: '#26a69a',
          noChangeColor: '#888888'
        },
        tooltip: {
          showRule: 'always',
          showType: 'standard',
          labels: ['时间: ', '开: ', '收: ', '高: ', '低: ', '成交量: '],
          values: null,
          defaultValue: 'n/a',
          rect: {
            paddingLeft: 8,
            paddingRight: 8,
            paddingTop: 8,
            paddingBottom: 8,
            offsetLeft: 12,
            offsetTop: 12,
            borderRadius: 4,
            borderSize: 1,
            borderColor: '#3f4254',
            backgroundColor: 'rgba(17, 17, 17, .8)'
          },
          text: {
            size: 12,
            family: 'Helvetica Neue',
            weight: 'normal',
            color: '#D9D9D9'
          }
        }
      },
      indicator: {
        tooltip: {
          showRule: 'always',
          showType: 'standard',
          showName: true,
          showParams: true,
          defaultValue: 'n/a',
          text: {
            size: 12,
            family: 'Helvetica Neue',
            weight: 'normal',
            color: '#D9D9D9',
            marginTop: 6,
            marginRight: 8,
            marginBottom: 0,
            marginLeft: 8
          }
        }
      },
      xAxis: {
        show: true,
        height: null,
        axisLine: {
          show: true,
          color: '#888888',
          size: 1
        },
        tickText: {
          show: true,
          color: '#D9D9D9',
          family: 'Helvetica Neue',
          weight: 'normal',
          size: 12,
          paddingTop: 3,
          paddingBottom: 6
        },
        tickLine: {
          show: true,
          size: 1,
          length: 3,
          color: '#888888'
        }
      },
      yAxis: {
        show: true,
        width: null,
        position: 'right',
        type: 'normal',
        inside: false,
        reverse: false,
        axisLine: {
          show: true,
          color: '#888888',
          size: 1
        },
        tickText: {
          show: true,
          color: '#D9D9D9',
          family: 'Helvetica Neue',
          weight: 'normal',
          size: 12,
          paddingLeft: 3,
          paddingRight: 6
        },
        tickLine: {
          show: true,
          size: 1,
          length: 3,
          color: '#888888'
        }
      },
      crosshair: {
        show: true,
        horizontal: {
          show: true,
          line: {
            show: true,
            style: 'dashed',
            dashValue: [4, 2],
            size: 1,
            color: '#888888'
          },
          text: {
            show: true,
            color: '#D9D9D9',
            size: 12,
            family: 'Helvetica Neue',
            weight: 'normal',
            paddingLeft: 4,
            paddingRight: 4,
            paddingTop: 4,
            paddingBottom: 4,
            borderSize: 1,
            borderColor: '#505050',
            borderRadius: 2,
            backgroundColor: '#505050'
          }
        },
        vertical: {
          show: true,
          line: {
            show: true,
            style: 'dashed',
            dashValue: [4, 2],
            size: 1,
            color: '#888888'
          },
          text: {
            show: true,
            color: '#D9D9D9',
            size: 12,
            family: 'Helvetica Neue',
            weight: 'normal',
            paddingLeft: 4,
            paddingRight: 4,
            paddingTop: 4,
            paddingBottom: 4,
            borderSize: 1,
            borderColor: '#505050',
            borderRadius: 2,
            backgroundColor: '#505050'
          }
        }
      }
    })

    // 创建默认的成交量副图 (作为独立面板)
    chart.value.createIndicator('VOL', false)

    // 加载初始数据
    if (props.ohlcvData) {
      updateChartData(props.ohlcvData)
    }

    // 加载初始指标
    if (props.indicators && props.indicators.length > 0) {
      updateIndicators(props.indicators)
    }
  } catch (error) {
    console.error('Failed to initialize chart:', error)
    ElMessage.error('图表初始化失败')
  }
}

// 更新图表数据
const updateChartData = (ohlcvData) => {
  if (!chart.value || !ohlcvData) return

  try {
    // 转换数据格式为klinecharts需要的格式
    const klineData = []
    const { dates, open, high, low, close, volume, turnover } = ohlcvData

    for (let i = 0; i < dates.length; i++) {
      const dataPoint = {
        timestamp: new Date(dates[i]).getTime(),
        open: open[i],
        high: high[i],
        low: low[i],
        close: close[i],
        volume: volume[i]
      }

      // 添加turnover字段 (如果可用)
      if (turnover && turnover.length > i) {
        dataPoint.turnover = turnover[i]
      }

      klineData.push(dataPoint)
    }

    // 应用数据到图表
    chart.value.applyNewData(klineData)
  } catch (error) {
    console.error('Failed to update chart data:', error)
    ElMessage.error('图表数据更新失败')
  }
}

// 更新指标
const updateIndicators = (indicators) => {
  if (!chart.value || !indicators) return

  try {
    // 清除现有的主图指标 (保留VOL)
    overlayIndicators.value = []

    // 添加新指标
    indicators.forEach((indicator, index) => {
      if (indicator.panel_type === 'overlay') {
        // 主图指标 (叠加到K线图上)
        const indicatorName = indicator.abbreviation.toUpperCase()

        // 处理多个输出
        indicator.outputs.forEach((output) => {
          chart.value.createIndicator(
            indicatorName,
            false,
            { id: 'candle_pane' }
          )

          overlayIndicators.value.push({
            name: output.display_name,
            index: index
          })
        })
      } else if (indicator.panel_type === 'separate') {
        // 副图指标 (单独面板)
        const indicatorName = indicator.abbreviation.toUpperCase()
        chart.value.createIndicator(indicatorName, false)
      }
    })
  } catch (error) {
    console.error('Failed to update indicators:', error)
    ElMessage.error('指标更新失败')
  }
}

// 移除指标
const handleRemoveIndicator = (index) => {
  emit('indicator-remove', index)
}

// 周期切换
const handlePeriodChange = (period) => {
  console.log('Period changed to:', period)
  // TODO: 实现周期切换逻辑 (需要重新请求数据)
  ElMessage.info('周期切换功能即将实现')
}

// 图表类型切换
const handleChartTypeChange = (type) => {
  if (!chart.value) return

  const typeMap = {
    'candle_solid': '蜡烛图',
    'candle_stroke': '空心蜡烛',
    'candle_up_stroke': '涨空心跌实心',
    'ohlc': 'OHLC',
    'area': '面积图'
  }

  chart.value.setStyles({
    candle: {
      type: type
    }
  })

  currentChartType.value = typeMap[type] || '蜡烛图'
  ElMessage.success(`已切换到${currentChartType.value}`)
}

// 重置图表
const resetChart = () => {
  if (!chart.value) return

  chart.value.zoomAtCoordinate(1.0, { x: 0, y: 0 }, 0)
  ElMessage.success('图表已重置')
}
</script>

<style scoped lang="scss">
.kline-chart-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
  background: #ffffff;

  .chart-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #909399;

    .el-icon {
      font-size: 48px;
      margin-bottom: 16px;
    }

    p {
      font-size: 14px;
    }
  }

  .chart-canvas {
    flex: 1;
    width: 100%;
    min-height: 400px;
  }

  .chart-toolbar {
    padding: 12px;
    border-top: 1px solid #e4e7ed;
    background: #f5f7fa;
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .kline-chart-container {
    .chart-canvas {
      min-height: 300px;
    }

    .chart-toolbar {
      padding: 8px;

      :deep(.el-radio-group) {
        flex-wrap: wrap;
      }
    }
  }
}
</style>
