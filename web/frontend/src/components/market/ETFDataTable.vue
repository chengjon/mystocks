<template>
  <div class="etf-data-table">
    <!-- 查询工具栏 -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="ETF代码">
          <el-input
            v-model="queryForm.symbol"
            placeholder="如: 510300"
            style="width: 140px"
            clearable
          />
        </el-form-item>

        <el-form-item label="关键词">
          <el-input
            v-model="queryForm.keyword"
            placeholder="名称/代码搜索"
            style="width: 160px"
            clearable
          />
        </el-form-item>

        <el-form-item label="显示数量">
          <el-input-number
            v-model="queryForm.limit"
            :min="10"
            :max="500"
            :step="10"
            style="width: 120px"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleQuery" :loading="loading">
            查询
          </el-button>
          <el-button :icon="Refresh" @click="handleRefresh" :loading="refreshing">
            刷新全市场数据
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- ETF数据表格 -->
    <el-card class="data-card" shadow="never" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span class="title">ETF行情数据</span>
          <el-tag v-if="etfData.length > 0" type="success">
            共 {{ etfData.length }} 只ETF
          </el-tag>
        </div>
      </template>

      <el-table
        :data="etfData"
        stripe
        border
        style="width: 100%"
        :default-sort="{ prop: 'change_percent', order: 'descending' }"
        @row-click="handleRowClick"
      >
        <el-table-column prop="symbol" label="代码" width="100" fixed />
        <el-table-column prop="name" label="名称" width="180" fixed show-overflow-tooltip />

        <el-table-column prop="latest_price" label="最新价" width="100" sortable align="right">
          <template #default="{ row }">
            <span class="price">{{ row.latest_price.toFixed(3) }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="change_percent" label="涨跌幅" width="100" sortable align="right">
          <template #default="{ row }">
            <span :class="getChangeClass(row.change_percent)">
              {{ formatPercent(row.change_percent) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="change_amount" label="涨跌额" width="100" sortable align="right">
          <template #default="{ row }">
            <span :class="getChangeClass(row.change_amount)">
              {{ row.change_amount.toFixed(3) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="volume" label="成交量" width="120" sortable align="right">
          <template #default="{ row }">
            {{ formatVolume(row.volume) }}
          </template>
        </el-table-column>

        <el-table-column prop="amount" label="成交额" width="120" sortable align="right">
          <template #default="{ row }">
            {{ formatAmount(row.amount) }}
          </template>
        </el-table-column>

        <el-table-column prop="turnover_rate" label="换手率" width="100" sortable align="right">
          <template #default="{ row }">
            {{ row.turnover_rate.toFixed(2) }}%
          </template>
        </el-table-column>

        <el-table-column prop="open_price" label="开盘价" width="100" align="right">
          <template #default="{ row }">
            {{ row.open_price.toFixed(3) }}
          </template>
        </el-table-column>

        <el-table-column prop="high_price" label="最高价" width="100" align="right">
          <template #default="{ row }">
            {{ row.high_price.toFixed(3) }}
          </template>
        </el-table-column>

        <el-table-column prop="low_price" label="最低价" width="100" align="right">
          <template #default="{ row }">
            {{ row.low_price.toFixed(3) }}
          </template>
        </el-table-column>

        <el-table-column prop="prev_close" label="昨收" width="100" align="right">
          <template #default="{ row }">
            {{ row.prev_close.toFixed(3) }}
          </template>
        </el-table-column>

        <el-table-column
          prop="circulating_market_cap"
          label="流通市值"
          width="140"
          sortable
          align="right"
        >
          <template #default="{ row }">
            {{ formatMarketCap(row.circulating_market_cap) }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty v-if="!loading && etfData.length === 0" description="暂无数据" />
    </el-card>

    <!-- ETF详情抽屉 -->
    <el-drawer v-model="drawerVisible" title="ETF详情" size="50%">
      <div v-if="selectedETF" class="etf-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ETF代码">
            {{ selectedETF.symbol }}
          </el-descriptions-item>
          <el-descriptions-item label="ETF名称">
            {{ selectedETF.name }}
          </el-descriptions-item>
          <el-descriptions-item label="最新价">
            <span class="price-large">{{ selectedETF.latest_price.toFixed(3) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="涨跌幅">
            <span :class="getChangeClass(selectedETF.change_percent)" class="price-large">
              {{ formatPercent(selectedETF.change_percent) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="成交量">
            {{ formatVolume(selectedETF.volume) }}
          </el-descriptions-item>
          <el-descriptions-item label="成交额">
            {{ formatAmount(selectedETF.amount) }}
          </el-descriptions-item>
          <el-descriptions-item label="换手率">
            {{ selectedETF.turnover_rate.toFixed(2) }}%
          </el-descriptions-item>
          <el-descriptions-item label="流通市值">
            {{ formatMarketCap(selectedETF.circulating_market_cap) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import axios from 'axios'

// 响应式数据
const queryForm = reactive({
  symbol: '',
  keyword: '',
  limit: 50
})

const etfData = ref([])
const loading = ref(false)
const refreshing = ref(false)
const drawerVisible = ref(false)
const selectedETF = ref(null)

// API基础URL
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8888'

// 查询ETF数据
const handleQuery = async () => {
  loading.value = true
  try {
    const params = {
      limit: queryForm.limit
    }

    if (queryForm.symbol) {
      params.symbol = queryForm.symbol
    }

    if (queryForm.keyword) {
      params.keyword = queryForm.keyword
    }

    const response = await axios.get(`${API_BASE}/api/market/etf/list`, { params })
    etfData.value = response.data

    if (response.data.length === 0) {
      ElMessage.info('未查询到ETF数据')
    } else {
      ElMessage.success(`查询成功: ${response.data.length}只ETF`)
    }
  } catch (error) {
    ElMessage.error(`查询失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    loading.value = false
  }
}

// 刷新全市场ETF数据
const handleRefresh = async () => {
  refreshing.value = true
  try {
    const response = await axios.post(`${API_BASE}/api/market/etf/refresh`)

    ElMessage.success(response.data.message || '数据刷新成功')

    // 自动重新查询
    await handleQuery()
  } catch (error) {
    ElMessage.error(`刷新失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    refreshing.value = false
  }
}

// 行点击事件
const handleRowClick = (row) => {
  selectedETF.value = row
  drawerVisible.value = true
}

// 格式化涨跌幅
const formatPercent = (value) => {
  if (value > 0) return `+${value.toFixed(2)}%`
  return `${value.toFixed(2)}%`
}

// 格式化成交量
const formatVolume = (value) => {
  if (value >= 100000000) {
    return (value / 100000000).toFixed(2) + '亿'
  } else if (value >= 10000) {
    return (value / 10000).toFixed(2) + '万'
  }
  return value.toLocaleString()
}

// 格式化金额
const formatAmount = (value) => {
  if (value >= 100000000) {
    return (value / 100000000).toFixed(2) + '亿'
  } else if (value >= 10000) {
    return (value / 10000).toFixed(2) + '万'
  }
  return value.toFixed(2)
}

// 格式化市值
const formatMarketCap = (value) => {
  if (value >= 100000000) {
    return (value / 100000000).toFixed(2) + '亿'
  } else if (value >= 10000) {
    return (value / 10000).toFixed(2) + '万'
  }
  return value.toFixed(2)
}

// 获取涨跌颜色类
const getChangeClass = (value) => {
  if (value > 0) return 'change-up'
  if (value < 0) return 'change-down'
  return 'change-neutral'
}

// 组件挂载
onMounted(() => {
  handleQuery()
})
</script>

<style scoped>
.etf-data-table {
  padding: 20px;
}

.search-card {
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

.price {
  font-weight: 500;
}

.price-large {
  font-size: 18px;
  font-weight: 600;
}

.change-up {
  color: #F56C6C;
  font-weight: 500;
}

.change-down {
  color: #67C23A;
  font-weight: 500;
}

.change-neutral {
  color: #909399;
}

.search-form {
  margin-bottom: 0;
}

.etf-detail {
  padding: 20px;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}
</style>
