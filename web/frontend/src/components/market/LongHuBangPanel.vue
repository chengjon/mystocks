<template>
  <div class="lhb-panel">
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
          <el-tag v-if="tableData.length > 0">共 {{ tableData.length }} 条</el-tag>
        </div>
      </template>

      <el-table :data="tableData" stripe height="600">
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
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import dayjs from 'dayjs'

const symbol = ref('')
const dateRange = ref([])
const minNetAmount = ref(null)
const tableData = ref([])
const loading = ref(false)
const refreshing = ref(false)
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8888'

const queryData = async () => {
  loading.value = true
  try {
    const params = { limit: 200 }
    if (symbol.value) params.symbol = symbol.value
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    if (minNetAmount.value) params.min_net_amount = minNetAmount.value

    const { data } = await axios.get(`${API_BASE}/api/market/lhb`, { params })
    tableData.value = data
    ElMessage.success(`查询成功，共${data.length}条记录`)
  } catch (error) {
    ElMessage.error(`查询失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  const yesterday = dayjs().subtract(1, 'day').format('YYYY-MM-DD')
  
  refreshing.value = true
  try {
    await axios.post(`${API_BASE}/api/market/lhb/refresh`, null, {
      params: { trade_date: yesterday }
    })
    ElMessage.success('数据刷新成功')
    await queryData()
  } catch (error) {
    ElMessage.error(`刷新失败: ${error.message}`)
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
