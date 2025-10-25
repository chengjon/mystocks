<template>
  <div class="fund-flow-panel">
    <!-- 查询表单 -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="行业分类">
          <el-select v-model="queryForm.industry_type" style="width: 140px">
            <el-option label="证监会行业" value="csrc" />
            <el-option label="申万一级" value="sw_l1" />
            <el-option label="申万二级" value="sw_l2" />
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

<script setup>
import { ref, reactive, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { dataApi } from '@/api'

// 响应式数据
const queryForm = reactive({
  industry_type: 'csrc',
  timeframe: '1'
})

const dateRange = ref([])
const fundFlowData = ref([])
const loading = ref(false)
const refreshing = ref(false)
const chartRef = ref(null)
let chartInstance = null

// 查询资金流向
const handleQuery = async () => {
  loading.value = true
  try {
    const params = {
      industry_type: queryForm.industry_type,
      limit: 20
    }

    if (dateRange.value && dateRange.value.length === 2) {
      params.trade_date = dateRange.value[1] // Use end date
    }

    const response = await dataApi.getMarketFundFlow(params)

    if (response.success) {
      // Map PostgreSQL response to table format
      fundFlowData.value = response.data.map(item => ({
        trade_date: item.trade_date,
        timeframe: queryForm.timeframe,
        main_net_inflow: item.net_inflow * 100000000, // Convert back to yuan
        main_net_inflow_rate: (item.net_inflow / (item.total_inflow + item.total_outflow)) * 100,
        super_large_net_inflow: item.main_inflow * 100000000,
        large_net_inflow: item.retail_inflow * 100000000,
        medium_net_inflow: 0,
        small_net_inflow: 0,
        industry_name: item.industry_name
      }))

      if (response.data.length === 0) {
        ElMessage.info('未查询到数据')
      } else {
        ElMessage.success(`查询成功: ${response.data.length}条记录`)
        await nextTick()
        renderChart()
      }
    }
  } catch (error) {
    ElMessage.error(`查询失败: ${error.message || '请稍后重试'}`)
  } finally {
    loading.value = false
  }
}

// 刷新数据
const handleRefresh = async () => {
  refreshing.value = true
  try {
    await handleQuery()
    ElMessage.success('数据已刷新')
  } catch (error) {
    ElMessage.error(`刷新失败: ${error.message || '请稍后重试'}`)
  } finally {
    refreshing.value = false
  }
}

// 格式化金额
const formatAmount = (value) => {
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
const formatPercent = (value) => {
  if (value === null || value === undefined) return '-'
  return value.toFixed(2) + '%'
}

// 获取金额样式类
const getAmountClass = (value) => {
  if (value > 0) return 'amount-positive'
  if (value < 0) return 'amount-negative'
  return 'amount-neutral'
}

// 渲染ECharts图表
const renderChart = () => {
  if (!chartRef.value || fundFlowData.value.length === 0) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  const dates = fundFlowData.value.map(d => d.trade_date).reverse()
  const mainFlow = fundFlowData.value.map(d => (d.main_net_inflow / 100000000).toFixed(2)).reverse()
  const superLargeFlow = fundFlowData.value.map(d => (d.super_large_net_inflow / 100000000).toFixed(2)).reverse()
  const largeFlow = fundFlowData.value.map(d => (d.large_net_inflow / 100000000).toFixed(2)).reverse()

  const option = {
    title: {
      text: `${queryForm.symbol} 资金流向趋势`,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['主力净流入', '超大单', '大单'],
      top: 30
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value',
      name: '金额(亿元)'
    },
    series: [
      {
        name: '主力净流入',
        type: 'line',
        data: mainFlow,
        smooth: true,
        itemStyle: { color: '#409EFF' }
      },
      {
        name: '超大单',
        type: 'line',
        data: superLargeFlow,
        smooth: true,
        itemStyle: { color: '#F56C6C' }
      },
      {
        name: '大单',
        type: 'line',
        data: largeFlow,
        smooth: true,
        itemStyle: { color: '#E6A23C' }
      }
    ]
  }

  chartInstance.setOption(option)
}

// 监听数据变化
watch(() => fundFlowData.value, () => {
  if (fundFlowData.value.length > 0) {
    nextTick(() => renderChart())
  }
})

// 组件挂载
onMounted(() => {
  // 默认查询
  handleQuery()
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
