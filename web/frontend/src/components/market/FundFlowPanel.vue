<template>
  <div class="fund-flow-panel">
    <!-- 查询表单 -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="股票代码">
          <el-input
            v-model="queryForm.symbol"
            placeholder="如: 600519.SH"
            style="width: 160px"
            clearable
          />
        </el-form-item>

        <el-form-item label="时间维度">
          <el-select v-model="queryForm.timeframe" style="width: 120px">
            <el-option label="今日" value="1" />
            <el-option label="3日" value="3" />
            <el-option label="5日" value="5" />
            <el-option label="10日" value="10" />
          </el-select>
        </el-form-item>

        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="-"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 240px"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleQuery" :loading="loading">
            查询
          </el-button>
          <el-button :icon="Refresh" @click="handleRefresh" :loading="refreshing">
            刷新数据
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 资金流向数据展示 -->
    <el-card class="data-card" shadow="never" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span class="title">资金流向数据</span>
          <el-tag v-if="fundFlowData.length > 0" type="info">
            共 {{ fundFlowData.length }} 条记录
          </el-tag>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table :data="fundFlowData" stripe border style="width: 100%">
        <el-table-column prop="trade_date" label="交易日期" width="120" sortable />
        <el-table-column prop="timeframe" label="时间维度" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ row.timeframe }}天</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="main_net_inflow" label="主力净流入" width="140" sortable>
          <template #default="{ row }">
            <span :class="getAmountClass(row.main_net_inflow)">
              {{ formatAmount(row.main_net_inflow) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="main_net_inflow_rate" label="主力净占比" width="120" sortable>
          <template #default="{ row }">
            <span :class="getAmountClass(row.main_net_inflow_rate)">
              {{ formatPercent(row.main_net_inflow_rate) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="super_large_net_inflow" label="超大单" width="140" sortable>
          <template #default="{ row }">
            <span :class="getAmountClass(row.super_large_net_inflow)">
              {{ formatAmount(row.super_large_net_inflow) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="large_net_inflow" label="大单" width="140" sortable>
          <template #default="{ row }">
            <span :class="getAmountClass(row.large_net_inflow)">
              {{ formatAmount(row.large_net_inflow) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="medium_net_inflow" label="中单" width="140" sortable>
          <template #default="{ row }">
            <span :class="getAmountClass(row.medium_net_inflow)">
              {{ formatAmount(row.medium_net_inflow) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="small_net_inflow" label="小单" width="140" sortable>
          <template #default="{ row }">
            <span :class="getAmountClass(row.small_net_inflow)">
              {{ formatAmount(row.small_net_inflow) }}
            </span>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty v-if="!loading && fundFlowData.length === 0" description="暂无数据" />
    </el-card>

    <!-- ECharts图表展示 -->
    <el-card class="chart-card" shadow="never" v-if="fundFlowData.length > 0">
      <template #header>
        <span class="title">资金流向趋势图</span>
      </template>
      <div ref="chartRef" style="width: 100%; height: 400px"></div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, watch, nextTick, type Ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import type { ECharts, EChartsOption } from '@/types/echarts'
import request from '@/api'

// ============================================
// 类型定义
// ============================================

interface QueryForm {
  symbol: string
  timeframe: string
}

interface FundFlowItem {
  trade_date: string
  timeframe: string
  main_net_inflow: number
  main_net_inflow_rate: number
  super_large_net_inflow: number
  large_net_inflow: number
  medium_net_inflow: number
  small_net_inflow: number
}

// 响应式数据
const queryForm = reactive<QueryForm>({
  symbol: '600519.SH',
  timeframe: '1'
})

const dateRange: Ref<string[]> = ref([])
const fundFlowData: Ref<FundFlowItem[]> = ref([])
const loading: Ref<boolean> = ref(false)
const refreshing: Ref<boolean> = ref(false)
const chartRef: Ref<HTMLDivElement | null> = ref(null)
let chartInstance: ECharts | null = null

// 使用配置好的request实例，baseURL已经在api/index.js中配置

// 查询资金流向
const handleQuery = async (): Promise<void> => {
  if (!queryForm.symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }

  loading.value = true
  try {
    const params: any = {
      symbol: queryForm.symbol,
      timeframe: queryForm.timeframe
    }

    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    const response = await request.get('/market/fund-flow', { params })
    fundFlowData.value = response.data.fund_flow || []

    if (fundFlowData.value.length === 0) {
      ElMessage.info('未查询到数据')
    } else {
      ElMessage.success(`查询成功: ${fundFlowData.value.length}条记录`)
      // 渲染图表
      await nextTick()
      renderChart()
    }
  } catch (error: any) {
    ElMessage.error(`查询失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    loading.value = false
  }
}

// 刷新数据
const handleRefresh = async (): Promise<void> => {
  if (!queryForm.symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }

  refreshing.value = true
  try {
    await request.post('/market/fund-flow/refresh', null, {
      params: {
        symbol: queryForm.symbol,
        timeframe: queryForm.timeframe
      }
    })

    ElMessage.success('数据刷新成功')
    // 自动重新查询
    await handleQuery()
  } catch (error: any) {
    ElMessage.error(`刷新失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    refreshing.value = false
  }
}

// 格式化金额
const formatAmount = (value: number): string => {
  if (value === null || value === undefined) return '-'
  const abs = Math.abs(value)
  if (abs >= 100000000) {
    return (value / 100000000).toFixed(2) + '亿'
  } else if (abs >= 10000) {
    return (value / 10000).toFixed(2) + '万'
  }
  return value.toFixed(2)
}

// 格式化百分比
const formatPercent = (value: number): string => {
  if (value === null || value === undefined) return '-'
  return value.toFixed(2) + '%'
}

// 获取金额样式类
const getAmountClass = (value: number): string => {
  if (value > 0) return 'amount-positive'
  if (value < 0) return 'amount-negative'
  return 'amount-neutral'
}

// 渲染ECharts图表
const renderChart = (): void => {
  if (!chartRef.value || fundFlowData.value.length === 0) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  const dates = fundFlowData.value.map(d => d.trade_date)
  const mainFlow = fundFlowData.value.map(d => d.main_net_inflow.toFixed(2))
  const superLargeFlow = fundFlowData.value.map(d => d.super_large_net_inflow.toFixed(2))
  const largeFlow = fundFlowData.value.map(d => d.large_net_inflow.toFixed(2))

  console.log('Chart data:', { dates, mainFlow, superLargeFlow, largeFlow })

  const option: EChartsOption = {
    title: {
      text: `${queryForm.symbol} 资金流向趋势`,
      left: 'center',
      textStyle: { fontSize: 16, fontWeight: 'bold' }
    },
    tooltip: {
      trigger: 'axis',
      formatter: function (params: any) {
        let result = params[0].axisValue + '<br/>'
        params.forEach((param: any) => {
          const value = parseFloat(param.value)
          const color = value >= 0 ? '#67C23A' : '#F56C6C'
          result += `<span style="color: ${color}">${param.seriesName}: ${value} 万元</span><br/>`
        })
        return result
      }
    },
    legend: {
      data: ['主力净流入', '超大单', '大单'],
      top: 40,
      itemGap: 20
    },
    grid: {
      left: '5%',
      right: '5%',
      bottom: '10%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLabel: { interval: 0, rotate: 45 }
    },
    yAxis: {
      type: 'value',
      name: '金额(万元)',
      axisLabel: {
        formatter: function(value: any) {
          return value + '万'
        }
      },
      splitLine: { show: true, lineStyle: { type: 'dashed', color: '#E4E7ED' } }
    },
    series: [
      {
        name: '主力净流入',
        type: 'line',
        data: mainFlow,
        smooth: true,
        itemStyle: { color: '#409EFF' },
        lineStyle: { width: 3 },
        symbol: 'circle',
        symbolSize: 8,
        emphasis: { focus: 'series' }
      },
      {
        name: '超大单',
        type: 'line',
        data: superLargeFlow,
        smooth: true,
        itemStyle: { color: '#F56C6C' },
        lineStyle: { width: 3 },
        symbol: 'triangle',
        symbolSize: 8,
        emphasis: { focus: 'series' }
      },
      {
        name: '大单',
        type: 'line',
        data: largeFlow,
        smooth: true,
        itemStyle: { color: '#E6A23C' },
        lineStyle: { width: 3 },
        symbol: 'diamond',
        symbolSize: 8,
        emphasis: { focus: 'series' }
      }
    ]
  }

  chartInstance.setOption(option, true)

  // 调整图表大小
  nextTick(() => {
    chartInstance?.resize()
  })
}

// 监听数据变化
watch(() => fundFlowData.value, () => {
  if (fundFlowData.value.length > 0) {
    nextTick(() => renderChart())
  }
})

// 监听窗口大小变化
const handleResize = (): void => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// 组件挂载
onMounted(() => {
  // 默认查询
  handleQuery()

  // 添加窗口大小监听
  window.addEventListener('resize', handleResize)
})

// 组件卸载
onUnmounted(() => {
  // 移除事件监听
  window.removeEventListener('resize', handleResize)

  // 销毁图表实例
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>
// 监听数据变化
watch(() => fundFlowData.value, () => {
  if (fundFlowData.value.length > 0) {
    nextTick(() => renderChart())
  }
})

// 监听窗口大小变化
const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// 组件挂载
onMounted(() => {
  // 默认查询
  handleQuery()

  // 添加窗口大小监听
  window.addEventListener('resize', handleResize)
})

// 组件卸载
onUnmounted(() => {
  // 移除事件监听
  window.removeEventListener('resize', handleResize)

  // 销毁图表实例
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<style scoped>
.fund-flow-panel {
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.data-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 16px;
  font-weight: 600;
}

.amount-positive {
  color: #F56C6C;
  font-weight: 500;
}

.amount-negative {
  color: #67C23A;
  font-weight: 500;
}

.amount-neutral {
  color: #909399;
}

.search-form {
  margin-bottom: 0;
}
</style>
