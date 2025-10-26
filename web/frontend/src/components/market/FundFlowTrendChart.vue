<template>
  <div class="fund-flow-trend-chart">
    <v-chart
      v-if="trendData && trendData.length > 0"
      :option="chartOption"
      autoresize
      :style="{ height: '400px', width: '100%' }"
    />
    <el-empty
      v-else
      description="暂无趋势数据"
      :image-size="100"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

// Register ECharts components
use([
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  CanvasRenderer
])

// Props
const props = defineProps({
  industryName: {
    type: String,
    required: true
  },
  trendData: {
    type: Array,
    required: true,
    default: () => []
  }
})

// Chart configuration
const chartOption = computed(() => {
  if (!props.trendData || props.trendData.length === 0) {
    return {}
  }

  // Extract dates and values from trend data
  const dates = props.trendData.map(d => d.date || d.trade_date)
  const netInflow = props.trendData.map(d => (d.net_inflow / 100000000).toFixed(2))
  const mainInflow = props.trendData.map(d => (d.main_inflow / 100000000).toFixed(2))
  const retailInflow = props.trendData.map(d => (d.retail_inflow / 100000000).toFixed(2))

  return {
    title: {
      text: `${props.industryName} - 资金流向趋势`,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 600
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        crossStyle: {
          color: '#999'
        }
      },
      formatter: (params) => {
        let result = `<div style="font-weight:600">${params[0].axisValue}</div>`
        params.forEach((param) => {
          const value = parseFloat(param.value)
          const color = value >= 0 ? '#F56C6C' : '#67C23A'
          result += `
            <div style="margin-top:4px">
              ${param.marker}
              <span style="margin-right:8px">${param.seriesName}:</span>
              <span style="font-weight:600;color:${color}">${value.toFixed(2)} 亿元</span>
            </div>
          `
        })
        return result
      }
    },
    legend: {
      data: ['净流入', '主力流入', '散户流入'],
      top: 35,
      icon: 'roundRect'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: 80,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLine: {
        lineStyle: {
          color: '#ddd'
        }
      },
      axisLabel: {
        color: '#666',
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '金额(亿元)',
      nameTextStyle: {
        color: '#666',
        fontSize: 12
      },
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#666',
        formatter: (value) => {
          return value >= 0 ? `+${value}` : value
        }
      },
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#eee'
        }
      }
    },
    series: [
      {
        name: '净流入',
        type: 'line',
        data: netInflow,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          width: 3,
          color: '#409EFF'
        },
        itemStyle: {
          color: '#409EFF',
          borderWidth: 2,
          borderColor: '#fff'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color: 'rgba(64, 158, 255, 0.3)'
              },
              {
                offset: 1,
                color: 'rgba(64, 158, 255, 0.05)'
              }
            ]
          }
        },
        emphasis: {
          focus: 'series'
        }
      },
      {
        name: '主力流入',
        type: 'line',
        data: mainInflow,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          width: 2,
          color: '#F56C6C'
        },
        itemStyle: {
          color: '#F56C6C',
          borderWidth: 2,
          borderColor: '#fff'
        },
        emphasis: {
          focus: 'series'
        }
      },
      {
        name: '散户流入',
        type: 'line',
        data: retailInflow,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          width: 2,
          color: '#E6A23C'
        },
        itemStyle: {
          color: '#E6A23C',
          borderWidth: 2,
          borderColor: '#fff'
        },
        emphasis: {
          focus: 'series'
        }
      }
    ],
    animation: true,
    animationDuration: 500,
    animationEasing: 'cubicOut'
  }
})
</script>

<style scoped>
.fund-flow-trend-chart {
  width: 100%;
  min-height: 400px;
  padding: 20px 0;
}
</style>
