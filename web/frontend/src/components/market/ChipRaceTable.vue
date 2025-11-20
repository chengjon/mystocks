<template>
  <div class="chip-race-table">
    <!-- 查询工具栏 -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="抢筹类型">
          <el-radio-group v-model="queryForm.race_type">
            <el-radio-button label="open">早盘抢筹</el-radio-button>
            <el-radio-button label="end">尾盘抢筹</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="交易日期">
          <el-date-picker
            v-model="queryForm.trade_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 160px"
          />
        </el-form-item>

        <el-form-item label="最小抢筹金额">
          <el-input-number
            v-model="queryForm.min_race_amount"
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
            刷新数据
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 抢筹数据表格 -->
    <el-card class="data-card" shadow="never" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span class="title">
            {{ queryForm.race_type === 'open' ? '早盘抢筹' : '尾盘抢筹' }}数据
          </span>
          <el-tag v-if="chipRaceData.length > 0" type="warning">
            共 {{ chipRaceData.length }} 只个股
          </el-tag>
        </div>
      </template>

      <el-table
        :data="chipRaceData"
        stripe
        border
        style="width: 100%"
        :default-sort="{ prop: 'race_amount', order: 'descending' }"
      >
        <el-table-column type="index" label="排名" width="60" align="center" />

        <el-table-column prop="symbol" label="代码" width="100" fixed />
        <el-table-column prop="name" label="名称" width="120" fixed show-overflow-tooltip />

        <el-table-column prop="latest_price" label="最新价" width="100" align="right">
          <template #default="{ row }">
            {{ row.latest_price.toFixed(2) }}
          </template>
        </el-table-column>

        <el-table-column prop="change_percent" label="涨跌幅" width="100" sortable align="right">
          <template #default="{ row }">
            <span :class="getChangeClass(row.change_percent)">
              {{ formatPercent(row.change_percent) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="race_amount" label="抢筹金额" width="140" sortable align="right">
          <template #default="{ row }">
            <span class="highlight-amount">{{ formatAmount(row.race_amount) }}</span>
          </template>
        </el-table-column>

        <el-table-column
          prop="race_amplitude"
          label="抢筹幅度"
          width="110"
          sortable
          align="right"
        >
          <template #default="{ row }">
            <span :class="getChangeClass(row.race_amplitude)">
              {{ row.race_amplitude.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="race_ratio" label="抢筹占比" width="110" sortable align="right">
          <template #default="{ row }">
            <el-progress
              :percentage="Math.min(row.race_ratio, 100)"
              :color="getProgressColor(row.race_ratio)"
            />
          </template>
        </el-table-column>

        <el-table-column
          prop="race_commission"
          label="委托金额"
          width="140"
          sortable
          align="right"
        >
          <template #default="{ row }">
            {{ formatAmount(row.race_commission) }}
          </template>
        </el-table-column>

        <el-table-column
          prop="race_transaction"
          label="成交金额"
          width="140"
          sortable
          align="right"
        >
          <template #default="{ row }">
            {{ formatAmount(row.race_transaction) }}
          </template>
        </el-table-column>

        <el-table-column prop="prev_close" label="昨收价" width="100" align="right">
          <template #default="{ row }">
            {{ row.prev_close.toFixed(2) }}
          </template>
        </el-table-column>

        <el-table-column prop="open_price" label="今开价" width="100" align="right">
          <template #default="{ row }">
            {{ row.open_price.toFixed(2) }}
          </template>
        </el-table-column>

        <el-table-column prop="trade_date" label="交易日期" width="120" sortable />
      </el-table>

      <!-- 空状态 -->
      <el-empty v-if="!loading && chipRaceData.length === 0" description="暂无数据" />
    </el-card>

    <!-- 统计信息卡片 -->
    <el-card class="stats-card" shadow="never" v-if="chipRaceData.length > 0">
      <template #header>
        <span class="title">统计信息</span>
      </template>

      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic title="个股数量" :value="chipRaceData.length" suffix="只" />
        </el-col>
        <el-col :span="6">
          <el-statistic
            title="总抢筹金额"
            :value="(totalRaceAmount / 100000000).toFixed(2)"
            suffix="亿元"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic
            title="平均抢筹金额"
            :value="(avgRaceAmount / 100000000).toFixed(2)"
            suffix="亿元"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic title="上涨个股占比" :value="upStockRatio.toFixed(2)" suffix="%" />
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import axios from 'axios'

// 响应式数据
const queryForm = reactive({
  race_type: 'open',
  trade_date: null,
  min_race_amount: null,
  limit: 100
})

const chipRaceData = ref([])
const loading = ref(false)
const refreshing = ref(false)

// API基础URL
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 计算属性 - 统计信息
const totalRaceAmount = computed(() => {
  return chipRaceData.value.reduce((sum, item) => sum + item.race_amount, 0)
})

const avgRaceAmount = computed(() => {
  if (chipRaceData.value.length === 0) return 0
  return totalRaceAmount.value / chipRaceData.value.length
})

const upStockRatio = computed(() => {
  if (chipRaceData.value.length === 0) return 0
  const upCount = chipRaceData.value.filter((item) => item.change_percent > 0).length
  return (upCount / chipRaceData.value.length) * 100
})

// 查询抢筹数据
const handleQuery = async () => {
  loading.value = true
  try {
    const params = {
      race_type: queryForm.race_type,
      limit: queryForm.limit
    }

    if (queryForm.trade_date) {
      params.trade_date = queryForm.trade_date
    }

    if (queryForm.min_race_amount) {
      params.min_race_amount = queryForm.min_race_amount
    }

    const response = await axios.get(`${API_BASE}/api/market/chip-race`, { params })
    chipRaceData.value = response.data

    if (response.data.length === 0) {
      ElMessage.info('未查询到抢筹数据')
    } else {
      ElMessage.success(`查询成功: ${response.data.length}只个股`)
    }
  } catch (error) {
    ElMessage.error(`查询失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    loading.value = false
  }
}

// 刷新抢筹数据
const handleRefresh = async () => {
  refreshing.value = true
  try {
    const params = {
      race_type: queryForm.race_type
    }

    if (queryForm.trade_date) {
      params.trade_date = queryForm.trade_date
    }

    await axios.post(`${API_BASE}/api/market/chip-race/refresh`, null, { params })

    ElMessage.success('数据刷新成功')

    // 自动重新查询
    await handleQuery()
  } catch (error) {
    ElMessage.error(`刷新失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    refreshing.value = false
  }
}

// 格式化涨跌幅
const formatPercent = (value) => {
  if (value > 0) return `+${value.toFixed(2)}%`
  return `${value.toFixed(2)}%`
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

// 获取涨跌颜色类
const getChangeClass = (value) => {
  if (value > 0) return 'change-up'
  if (value < 0) return 'change-down'
  return 'change-neutral'
}

// 获取进度条颜色
const getProgressColor = (value) => {
  if (value >= 20) return '#F56C6C'
  if (value >= 10) return '#E6A23C'
  return '#409EFF'
}

// 组件挂载
onMounted(() => {
  handleQuery()
})
</script>

<style scoped>
.chip-race-table {
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
  color: #E6A23C;
  font-weight: 600;
}

.change-up {
  color: #f56c6c;
  font-weight: 500;
}

.change-down {
  color: #67c23a;
  font-weight: 500;
}

.change-neutral {
  color: #909399;
}

.search-form {
  margin-bottom: 0;
}
</style>
