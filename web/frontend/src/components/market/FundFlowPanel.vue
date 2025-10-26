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
          <div class="header-controls">
            <el-tag v-if="fundFlowData.length > 0" type="info" style="margin-right: 10px">
              共 {{ totalItems }} 条记录
            </el-tag>
            <el-select
              v-model="pageSize"
              @change="handleSizeChange"
              style="width: 120px"
              size="small"
            >
              <el-option
                v-for="size in pageSizes"
                :key="size"
                :label="`${size} 条/页`"
                :value="size"
              />
            </el-select>
          </div>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table
        :data="paginatedData"
        stripe
        border
        class="sticky-header-table"
        style="width: 100%"
        height="calc(100vh - 400px)"
      >
        <el-table-column prop="trade_date" label="交易日期" width="120" sortable />
        <el-table-column prop="industry_name" label="行业名称" width="150" fixed>
          <template #default="{ row }">
            <a
              class="industry-link"
              :class="{ 'industry-selected': selectedIndustry === row.industry_name }"
              @click="handleIndustryClick(row.industry_name)"
            >
              {{ row.industry_name }}
            </a>
          </template>
        </el-table-column>
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

      <!-- 分页控件 (T008) -->
      <el-pagination
        v-if="showPagination"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="totalItems"
        :page-sizes="pageSizes"
        layout="total, sizes, prev, pager, next, jumper"
        hide-on-single-page
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: center; display: flex"
      />
    </el-card>

    <!-- 资金流向趋势图 (T011) -->
    <el-card class="chart-card" shadow="never" v-if="selectedIndustry">
      <template #header>
        <div class="card-header">
          <span class="title">资金流向趋势图</span>
          <el-tag type="success" size="small">
            当前选中: {{ selectedIndustry }}
          </el-tag>
        </div>
      </template>
      <FundFlowTrendChart
        :industry-name="selectedIndustry"
        :trend-data="industryTrendData"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { dataApi } from '@/api'
import { usePagination } from '@/composables/usePagination'
import FundFlowTrendChart from './FundFlowTrendChart.vue'

// 响应式数据
const queryForm = reactive({
  industry_type: 'csrc',
  timeframe: '1'
})

const dateRange = ref([])
const fundFlowData = ref([])
const loading = ref(false)
const refreshing = ref(false)

// Selected industry for trend chart (T009)
const selectedIndustry = ref(null)
const industryTrendData = ref([])

// Pagination setup (T008)
const {
  paginatedData,
  currentPage,
  pageSize,
  totalItems,
  showPagination,
  handleSizeChange,
  handleCurrentChange,
  pageSizes
} = usePagination(fundFlowData, {
  initialPageSize: 20,
  preferenceKey: 'pageSizeFundFlow'
})

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

// Handle industry name click (T009)
const handleIndustryClick = async (industryName) => {
  selectedIndustry.value = industryName
  console.log('[FundFlow] Industry clicked:', industryName)

  // Fetch trend data for the selected industry (T011)
  // For now, use mock data from current fundFlowData
  // In T012, this will be replaced with API call
  industryTrendData.value = fundFlowData.value
    .filter(d => d.industry_name === industryName)
    .map(d => ({
      date: d.trade_date,
      net_inflow: d.main_net_inflow || 0,
      main_inflow: d.super_large_net_inflow || 0,
      retail_inflow: d.large_net_inflow || 0
    }))
}

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

.header-controls {
  display: flex;
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

/* Industry link styles (T009) */
.industry-link {
  color: #409EFF;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.3s;
}

.industry-link:hover {
  text-decoration: underline;
  color: #66b1ff;
}

.industry-selected {
  font-weight: 600;
  color: #F56C6C;
}
</style>
