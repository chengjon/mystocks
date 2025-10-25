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
          <el-tag v-if="tableData.length > 0">共 {{ tableData.length }} 条</el-tag>
        </div>
      </template>

      <el-table :data="tableData" stripe height="600" @sort-change="handleSortChange">
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
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const keyword = ref('')
const tableData = ref([])
const loading = ref(false)
const refreshing = ref(false)
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8888'

const queryData = async () => {
  loading.value = true
  try {
    const params = keyword.value ? { keyword: keyword.value, limit: 100 } : { limit: 100 }
    const { data } = await axios.get(`${API_BASE}/api/market/etf/list`, { params })
    tableData.value = data
    ElMessage.success(`查询成功，共${data.length}条记录`)
  } catch (error) {
    ElMessage.error(`查询失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  refreshing.value = true
  try {
    await axios.post(`${API_BASE}/api/market/etf/refresh`)
    ElMessage.success('数据刷新成功')
    await queryData()
  } catch (error) {
    ElMessage.error(`刷新失败: ${error.message}`)
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
