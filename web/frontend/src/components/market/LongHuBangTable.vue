<template>
  <div class="longhubang-table">
    <!-- 查询工具栏 -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="股票代码">
          <el-input
            v-model="queryForm.symbol"
            placeholder="如: 600519"
            style="width: 140px"
            clearable
          />
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
          <el-input-number
            v-model="queryForm.min_net_amount"
            :min="0"
            :step="10000000"
            placeholder="单位:元"
            style="width: 180px"
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
            刷新最新数据
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 龙虎榜数据表格 -->
    <el-card class="data-card" shadow="never" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span class="title">龙虎榜数据</span>
          <el-tag v-if="lhbData.length > 0" type="danger">
            共 {{ lhbData.length }} 条记录
          </el-tag>
        </div>
      </template>

      <el-table
        :data="lhbData"
        stripe
        border
        style="width: 100%"
        :default-sort="{ prop: 'trade_date', order: 'descending' }"
        @row-click="handleRowClick"
      >
        <el-table-column prop="trade_date" label="交易日期" width="120" sortable fixed />
        <el-table-column prop="symbol" label="代码" width="100" fixed />
        <el-table-column prop="name" label="名称" width="120" fixed show-overflow-tooltip />

        <el-table-column prop="reason" label="上榜原因" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.reason || '-' }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="net_amount" label="净买入额" width="140" sortable align="right">
          <template #default="{ row }">
            <span :class="getAmountClass(row.net_amount)" class="highlight-amount">
              {{ formatAmount(row.net_amount) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="buy_amount" label="买入总额" width="140" sortable align="right">
          <template #default="{ row }">
            <span class="buy-amount">{{ formatAmount(row.buy_amount) }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="sell_amount" label="卖出总额" width="140" sortable align="right">
          <template #default="{ row }">
            <span class="sell-amount">{{ formatAmount(row.sell_amount) }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="turnover_rate" label="换手率" width="100" sortable align="right">
          <template #default="{ row }">
            {{ row.turnover_rate.toFixed(2) }}%
          </template>
        </el-table-column>

        <el-table-column
          prop="institution_buy"
          label="机构买入"
          width="140"
          sortable
          align="right"
        >
          <template #default="{ row }">
            {{ row.institution_buy ? formatAmount(row.institution_buy) : '-' }}
          </template>
        </el-table-column>

        <el-table-column
          prop="institution_sell"
          label="机构卖出"
          width="140"
          sortable
          align="right"
        >
          <template #default="{ row }">
            {{ row.institution_sell ? formatAmount(row.institution_sell) : '-' }}
          </template>
        </el-table-column>

        <el-table-column label="机构净买入" width="140" align="right">
          <template #default="{ row }">
            <span
              :class="
                getAmountClass(
                  (row.institution_buy || 0) - (row.institution_sell || 0)
                )
              "
            >
              {{
                formatAmount((row.institution_buy || 0) - (row.institution_sell || 0))
              }}
            </span>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty v-if="!loading && lhbData.length === 0" description="暂无数据" />
    </el-card>

    <!-- 统计信息 -->
    <el-card class="stats-card" shadow="never" v-if="lhbData.length > 0">
      <template #header>
        <span class="title">统计信息</span>
      </template>

      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic title="上榜次数" :value="lhbData.length" suffix="次" />
        </el-col>
        <el-col :span="6">
          <el-statistic
            title="总净买入额"
            :value="(totalNetAmount / 100000000).toFixed(2)"
            suffix="亿元"
          >
            <template #prefix>
              <el-icon :color="totalNetAmount > 0 ? '#F56C6C' : '#67C23A'">
                <TrendCharts v-if="totalNetAmount > 0" />
                <Bottom v-else />
              </el-icon>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic
            title="总买入额"
            :value="(totalBuyAmount / 100000000).toFixed(2)"
            suffix="亿元"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic
            title="总卖出额"
            :value="(totalSellAmount / 100000000).toFixed(2)"
            suffix="亿元"
          />
        </el-col>
      </el-row>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="dialogVisible" title="龙虎榜详情" width="60%">
      <div v-if="selectedRow" class="lhb-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="股票代码">
            {{ selectedRow.symbol }}
          </el-descriptions-item>
          <el-descriptions-item label="股票名称">
            {{ selectedRow.name }}
          </el-descriptions-item>
          <el-descriptions-item label="交易日期">
            {{ selectedRow.trade_date }}
          </el-descriptions-item>
          <el-descriptions-item label="上榜原因" :span="2">
            <el-tag type="warning">{{ selectedRow.reason || '未提供' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="净买入额">
            <span :class="getAmountClass(selectedRow.net_amount)" class="amount-large">
              {{ formatAmount(selectedRow.net_amount) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="换手率">
            {{ selectedRow.turnover_rate.toFixed(2) }}%
          </el-descriptions-item>
          <el-descriptions-item label="买入总额">
            <span class="buy-amount">{{ formatAmount(selectedRow.buy_amount) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="卖出总额">
            <span class="sell-amount">{{ formatAmount(selectedRow.sell_amount) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="机构买入">
            {{
              selectedRow.institution_buy ? formatAmount(selectedRow.institution_buy) : '无'
            }}
          </el-descriptions-item>
          <el-descriptions-item label="机构卖出">
            {{
              selectedRow.institution_sell
                ? formatAmount(selectedRow.institution_sell)
                : '无'
            }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, TrendCharts, Bottom } from '@element-plus/icons-vue'
import axios from 'axios'

// 响应式数据
const queryForm = reactive({
  symbol: '',
  min_net_amount: null,
  limit: 100
})

const dateRange = ref([])
const lhbData = ref([])
const loading = ref(false)
const refreshing = ref(false)
const dialogVisible = ref(false)
const selectedRow = ref(null)

// API基础URL
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8888'

// 计算属性 - 统计信息
const totalNetAmount = computed(() => {
  return lhbData.value.reduce((sum, item) => sum + item.net_amount, 0)
})

const totalBuyAmount = computed(() => {
  return lhbData.value.reduce((sum, item) => sum + item.buy_amount, 0)
})

const totalSellAmount = computed(() => {
  return lhbData.value.reduce((sum, item) => sum + item.sell_amount, 0)
})

// 查询龙虎榜数据
const handleQuery = async () => {
  loading.value = true
  try {
    const params = {
      limit: queryForm.limit
    }

    if (queryForm.symbol) {
      params.symbol = queryForm.symbol
    }

    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    if (queryForm.min_net_amount) {
      params.min_net_amount = queryForm.min_net_amount
    }

    const response = await axios.get(`${API_BASE}/api/market/lhb`, { params })
    lhbData.value = response.data

    if (response.data.length === 0) {
      ElMessage.info('未查询到龙虎榜数据')
    } else {
      ElMessage.success(`查询成功: ${response.data.length}条记录`)
    }
  } catch (error) {
    ElMessage.error(`查询失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    loading.value = false
  }
}

// 刷新最新龙虎榜数据
const handleRefresh = async () => {
  // 获取昨天的日期(龙虎榜数据次日公布)
  const yesterday = new Date()
  yesterday.setDate(yesterday.getDate() - 1)
  const tradeDate = yesterday.toISOString().split('T')[0]

  refreshing.value = true
  try {
    await axios.post(`${API_BASE}/api/market/lhb/refresh`, null, {
      params: { trade_date: tradeDate }
    })

    ElMessage.success(`${tradeDate} 龙虎榜数据刷新成功`)

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
  selectedRow.value = row
  dialogVisible.value = true
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

// 获取金额样式类
const getAmountClass = (value) => {
  if (value > 0) return 'amount-positive'
  if (value < 0) return 'amount-negative'
  return 'amount-neutral'
}

// 组件挂载
onMounted(() => {
  // 默认查询最近7天
  const today = new Date()
  const weekAgo = new Date()
  weekAgo.setDate(today.getDate() - 7)

  dateRange.value = [weekAgo.toISOString().split('T')[0], today.toISOString().split('T')[0]]

  handleQuery()
})
</script>

<style scoped>
.longhubang-table {
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.data-card {
  margin-bottom: 20px;
}

.stats-card {
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

.highlight-amount {
  font-weight: 600;
}

.amount-positive {
  color: #f56c6c;
}

.amount-negative {
  color: #67c23a;
}

.amount-neutral {
  color: #909399;
}

.amount-large {
  font-size: 18px;
  font-weight: 600;
}

.buy-amount {
  color: #f56c6c;
}

.sell-amount {
  color: #67c23a;
}

.search-form {
  margin-bottom: 0;
}

.lhb-detail {
  padding: 20px;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}
</style>
