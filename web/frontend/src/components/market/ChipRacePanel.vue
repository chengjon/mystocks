<template>
  <div class="chip-race-panel">
    <el-card class="search-card">
      <el-form :inline="true">
        <el-form-item label="抢筹类型">
          <el-select v-model="raceType" style="width: 130px">
            <el-option label="早盘抢筹" value="open" />
            <el-option label="尾盘抢筹" value="end" />
          </el-select>
        </el-form-item>
        <el-form-item label="交易日期">
          <el-date-picker v-model="tradeDate" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 160px" />
        </el-form-item>
        <el-form-item label="最小抢筹金额">
          <el-input-number v-model="minAmount" :min="0" :step="10000000" placeholder="单位:元" />
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
          <span>{{ raceType === 'open' ? '早盘抢筹' : '尾盘抢筹' }}数据</span>
          <el-tag v-if="tableData.length > 0">共 {{ tableData.length }} 条</el-tag>
        </div>
      </template>

      <el-table :data="tableData" stripe height="600">
        <el-table-column type="index" label="排名" width="60" />
        <el-table-column prop="symbol" label="代码" width="100" />
        <el-table-column prop="name" label="名称" width="120" />
        <el-table-column prop="latest_price" label="最新价" width="90" />
        <el-table-column prop="change_percent" label="涨跌幅" width="90">
          <template #default="{ row }">
            <span :class="row.change_percent >= 0 ? 'text-red' : 'text-green'">
              {{ row.change_percent?.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="race_amount" label="抢筹金额" width="120" sortable :formatter="formatAmount" />
        <el-table-column prop="race_amplitude" label="抢筹幅度" width="100">
          <template #default="{ row }">{{ (row.race_amplitude * 100)?.toFixed(2) }}%</template>
        </el-table-column>
        <el-table-column prop="race_commission" label="委托金额" width="120" :formatter="formatAmount" />
        <el-table-column prop="race_transaction" label="成交金额" width="120" :formatter="formatAmount" />
        <el-table-column prop="race_ratio" label="抢筹占比" width="100">
          <template #default="{ row }">{{ (row.race_ratio * 100)?.toFixed(2) }}%</template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && tableData.length === 0" description="暂无数据" />
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const raceType = ref('open')
const tradeDate = ref('')
const minAmount = ref(null)
const tableData = ref([])
const loading = ref(false)
const refreshing = ref(false)
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8888'

const queryData = async () => {
  loading.value = true
  try {
    const params = { race_type: raceType.value, limit: 200 }
    if (tradeDate.value) params.trade_date = tradeDate.value
    if (minAmount.value) params.min_race_amount = minAmount.value

    const { data } = await axios.get(`${API_BASE}/api/market/chip-race`, { params })
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
    const params = { race_type: raceType.value }
    if (tradeDate.value) params.trade_date = tradeDate.value

    await axios.post(`${API_BASE}/api/market/chip-race/refresh`, null, { params })
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

// 初始查询
queryData()
</script>

<style scoped lang="scss">
.chip-race-panel {
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
