<template>
  <div class="lhb-panel dragon-tiger-panel">
    <el-card class="search-card">
      <el-form :inline="true">
        <el-form-item label="股票代码">
          <el-input v-model="symbol" placeholder="输入股票代码" clearable style="width: 150px" />
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
        <el-form-item label="最小净买入额">
          <el-input-number v-model="minNetAmount" :min="0" :step="1000000" placeholder="单位:元" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="queryData" :loading="loading">查询</el-button>
          <el-button type="success" @click="refreshData" :loading="refreshing">刷新数据</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="data-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>龙虎榜数据</span>
          <div class="header-controls">
            <el-tag v-if="tableData.length > 0" style="margin-right: 10px">共 {{ totalItems }} 条</el-tag>
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

      <el-table
        :data="paginatedData"
        stripe
        border
        class="sticky-header-table"
        height="calc(100vh - 400px)"
      >
        <el-table-column prop="trade_date" label="交易日期" width="120" sortable />
        <el-table-column prop="symbol" label="代码" width="100" />
        <el-table-column prop="name" label="名称" width="120" />
        <el-table-column prop="reason" label="上榜原因" min-width="200" show-overflow-tooltip />
        <el-table-column prop="buy_amount" label="买入额" width="120" sortable :formatter="formatAmount">
          <template #default="{ row }">
            <span class="text-red">{{ formatAmount(row, null, row.buy_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="sell_amount" label="卖出额" width="120" sortable :formatter="formatAmount">
          <template #default="{ row }">
            <span class="text-green">{{ formatAmount(row, null, row.sell_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="net_amount" label="净买入额" width="120" sortable :formatter="formatAmount">
          <template #default="{ row }">
            <span :class="row.net_amount >= 0 ? 'text-red' : 'text-green'">
              {{ formatAmount(row, null, row.net_amount) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="turnover_rate" label="换手率" width="100">
          <template #default="{ row }">{{ (row.turnover_rate * 100)?.toFixed(2) }}%</template>
        </el-table-column>
        <el-table-column prop="institution_buy" label="机构买入" width="120" :formatter="formatAmount" />
        <el-table-column prop="institution_sell" label="机构卖出" width="120" :formatter="formatAmount" />
      </el-table>

      <el-empty v-if="!loading && tableData.length === 0" description="暂无数据" />

      <!-- 分页控件 (T016) -->
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
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { dataApi } from '@/api'
import dayjs from 'dayjs'
import { usePagination } from '@/composables/usePagination'

const symbol = ref('')
const dateRange = ref([])
const minNetAmount = ref(null)
const tableData = ref([])

// Pagination setup (T016)
const {
  paginatedData,
  currentPage,
  pageSize,
  totalItems,
  showPagination,
  handleSizeChange,
  handleCurrentChange,
  pageSizes
} = usePagination(tableData, {
  initialPageSize: 20,
  preferenceKey: 'pageSizeDragonTiger'
})
const loading = ref(false)
const refreshing = ref(false)

const queryData = async () => {
  loading.value = true
  try {
    const params = { limit: 200 }
    if (dateRange.value && dateRange.value.length === 2) {
      params.trade_date = dateRange.value[1] // Use end date as trade_date
    }

    const response = await dataApi.getDragonTiger(params)

    if (response.success) {
      // Map PostgreSQL response to table format
      tableData.value = response.data.map(item => ({
        trade_date: item.trade_date,
        symbol: item.symbol,
        name: item.name,
        reason: item.buy_reason,
        buy_amount: item.total_buy,
        sell_amount: item.total_sell,
        net_amount: item.net_buy,
        turnover_rate: 0, // Not available in new API
        institution_buy: 0, // Not available in new API
        institution_sell: 0 // Not available in new API
      }))
      ElMessage.success(`查询成功，共${response.data.length}条记录`)
    }
  } catch (error) {
    ElMessage.error(`查询失败: ${error.message || '请稍后重试'}`)
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  refreshing.value = true
  try {
    await queryData()
    ElMessage.success('数据已刷新')
  } catch (error) {
    ElMessage.error(`刷新失败: ${error.message || '请稍后重试'}`)
  } finally {
    refreshing.value = false
  }
}

const formatAmount = (row, column, cellValue) => {
  if (!cellValue) return '-'
  if (cellValue >= 100000000) return (cellValue / 100000000).toFixed(2) + '亿'
  return (cellValue / 10000).toFixed(2) + '万'
}

// 初始查询最近10天数据
dateRange.value = [
  dayjs().subtract(10, 'day').format('YYYY-MM-DD'),
  dayjs().format('YYYY-MM-DD')
]
queryData()
</script>

<style scoped lang="scss">
.lhb-panel {
  padding: 20px;

  .search-card {
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

  .text-red {
    color: #f56c6c;
    font-weight: 500;
  }

  .text-green {
    color: #67c23a;
    font-weight: 500;
  }
}
</style>
