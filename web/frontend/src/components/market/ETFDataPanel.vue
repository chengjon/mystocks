<template>
  <div class="etf-data-panel">
    <el-card class="search-card">
      <el-form :inline="true">
        <el-form-item label="ETF代码/名称">
          <el-input v-model="keyword" placeholder="输入关键词搜索" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="queryData" :loading="loading">查询</el-button>
          <el-button type="success" @click="refreshData" :loading="refreshing">刷新全市场ETF</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="data-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>ETF行情数据</span>
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
        @sort-change="handleSortChange"
      >
        <el-table-column prop="symbol" label="代码" width="120" fixed />
        <el-table-column prop="name" label="名称" width="180" fixed />
        <el-table-column prop="latest_price" label="最新价" width="100" sortable="custom" />
        <el-table-column prop="change_percent" label="涨跌幅" width="100" sortable="custom">
          <template #default="{ row }">
            <span :class="row.change_percent >= 0 ? 'text-red' : 'text-green'">
              {{ row.change_percent?.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="volume" label="成交量" width="120" :formatter="formatVolume" sortable="custom" />
        <el-table-column prop="amount" label="成交额" width="120" :formatter="formatAmount" sortable="custom" />
        <el-table-column prop="turnover_rate" label="换手率" width="100">
          <template #default="{ row }">{{ row.turnover_rate?.toFixed(2) }}%</template>
        </el-table-column>
        <el-table-column prop="open_price" label="开盘价" width="100" />
        <el-table-column prop="high_price" label="最高价" width="100" />
        <el-table-column prop="low_price" label="最低价" width="100" />
        <el-table-column prop="total_market_cap" label="总市值" width="120" :formatter="formatAmount" />
      </el-table>

      <el-empty v-if="!loading && tableData.length === 0" description="暂无数据" />

      <!-- 分页控件 (T014) -->
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
import { usePagination } from '@/composables/usePagination'

const keyword = ref('')
const tableData = ref([])
const loading = ref(false)
const refreshing = ref(false)

// Pagination setup (T014)
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
  preferenceKey: 'pageSizeETF'
})

const queryData = async () => {
  loading.value = true
  try {
    const params = { limit: 100, sort_by: 'volume' }
    const response = await dataApi.getETFData(params)

    if (response.success) {
      // Map PostgreSQL response to table format
      tableData.value = response.data.map(item => ({
        symbol: item.symbol,
        name: item.name,
        latest_price: item.close,
        change_percent: item.change,
        volume: item.volume,
        amount: item.amount,
        turnover_rate: item.turnover,
        open_price: item.open,
        high_price: item.high,
        low_price: item.low,
        total_market_cap: item.amount // Using amount as proxy for market cap
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

const formatVolume = (row, column, cellValue) => {
  if (!cellValue) return '-'
  return (cellValue / 10000).toFixed(2) + '万手'
}

const formatAmount = (row, column, cellValue) => {
  if (!cellValue) return '-'
  if (cellValue >= 100000000) return (cellValue / 100000000).toFixed(2) + '亿'
  return (cellValue / 10000).toFixed(2) + '万'
}

const handleSortChange = ({ prop, order }) => {
  if (!order) {
    queryData()
    return
  }
  tableData.value.sort((a, b) => {
    const aVal = a[prop] || 0
    const bVal = b[prop] || 0
    return order === 'ascending' ? aVal - bVal : bVal - aVal
  })
}

// 初始查询
queryData()
</script>

<style scoped lang="scss">
.etf-data-panel {
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
