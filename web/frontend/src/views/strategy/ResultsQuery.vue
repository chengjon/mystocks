<template>
  <div class="results-query">
    <el-card>
      <template #header>
        <span>📊 策略结果查询</span>
      </template>

      <!-- 查询表单 -->
      <el-form :model="queryForm" inline>
        <el-form-item label="策略">
          <el-select
            v-model="queryForm.strategy_code"
            placeholder="全部策略"
            clearable
            style="width: 200px"
          >
            <el-option
              v-for="strategy in strategies"
              :key="strategy.strategy_code"
              :label="strategy.strategy_name_cn"
              :value="strategy.strategy_code"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="股票代码">
          <el-input
            v-model="queryForm.symbol"
            placeholder="输入股票代码"
            clearable
            style="width: 150px"
          />
        </el-form-item>

        <el-form-item label="检查日期">
          <el-date-picker
            v-model="queryForm.check_date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            clearable
            style="width: 180px"
          />
        </el-form-item>

        <el-form-item label="匹配结果">
          <el-select
            v-model="queryForm.match_result"
            placeholder="全部"
            clearable
            style="width: 120px"
          >
            <el-option label="匹配" :value="true" />
            <el-option label="不匹配" :value="false" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleQuery" :loading="loading">
            <el-icon><Search /></el-icon> 查询
          </el-button>
          <el-button @click="handleReset">
            <el-icon><RefreshLeft /></el-icon> 重置
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 结果表格 -->
      <el-table
        :data="results"
        v-loading="loading"
        stripe
        border
        style="margin-top: 20px"
      >
        <el-table-column prop="check_date" label="检查日期" width="120" sortable />
        <el-table-column label="策略" width="150">
          <template #default="scope">
            <el-tag size="small">{{ getStrategyName(scope.row.strategy_code) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="symbol" label="股票代码" width="100" />
        <el-table-column prop="stock_name" label="股票名称" width="120" />
        <el-table-column label="匹配结果" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.match_result ? 'success' : 'info'">
              {{ scope.row.match_result ? '✓ 匹配' : '✗ 不匹配' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="latest_price" label="最新价" width="100" align="right" />
        <el-table-column label="涨跌幅" width="100" align="right">
          <template #default="scope">
            <span :class="getPriceClass(scope.row.change_percent)">
              {{ scope.row.change_percent ? scope.row.change_percent + '%' : '-' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="match_score" label="匹配度" width="100" align="center">
          <template #default="scope">
            {{ scope.row.match_score || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="viewDetails(scope.row)">
              详情
            </el-button>
            <el-button size="small" type="primary" @click="rerun(scope.row)">
              重新运行
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[20, 50, 100, 200]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleQuery"
        @current-change="handleQuery"
        style="margin-top: 20px; justify-content: center"
      />
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailsVisible" title="结果详情" width="600px">
      <el-descriptions v-if="selectedResult" :column="2" border>
        <el-descriptions-item label="策略">
          {{ getStrategyName(selectedResult.strategy_code) }}
        </el-descriptions-item>
        <el-descriptions-item label="股票">
          {{ selectedResult.symbol }} {{ selectedResult.stock_name }}
        </el-descriptions-item>
        <el-descriptions-item label="检查日期">
          {{ selectedResult.check_date }}
        </el-descriptions-item>
        <el-descriptions-item label="匹配结果">
          <el-tag :type="selectedResult.match_result ? 'success' : 'info'">
            {{ selectedResult.match_result ? '✓ 匹配' : '✗ 不匹配' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="最新价">
          {{ selectedResult.latest_price }}
        </el-descriptions-item>
        <el-descriptions-item label="涨跌幅">
          <span :class="getPriceClass(selectedResult.change_percent)">
            {{ selectedResult.change_percent }}%
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="匹配度评分">
          {{ selectedResult.match_score || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ selectedResult.created_at }}
        </el-descriptions-item>
        <el-descriptions-item label="匹配详情" :span="2">
          <pre v-if="selectedResult.match_details">{{ JSON.stringify(selectedResult.match_details, null, 2) }}</pre>
          <span v-else>-</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, RefreshLeft } from '@element-plus/icons-vue'
import { strategyApi } from '@/api'

// 响应式数据
const strategies = ref([])
const loading = ref(false)
const results = ref([])
const detailsVisible = ref(false)
const selectedResult = ref(null)

const queryForm = ref({
  strategy_code: '',
  symbol: '',
  check_date: '',
  match_result: null
})

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

// 加载策略列表
const loadStrategies = async () => {
  try {
    const response = await strategyApi.getDefinitions()
    if (response.data.success) {
      strategies.value = response.data.data
    }
  } catch (error) {
    console.error('加载策略列表失败:', error)
  }
}

// 获取策略名称
const getStrategyName = (code) => {
  const strategy = strategies.value.find(s => s.strategy_code === code)
  return strategy ? strategy.strategy_name_cn : code
}

// 获取价格颜色类
const getPriceClass = (changePercent) => {
  if (!changePercent) return ''
  const value = parseFloat(changePercent)
  if (value > 0) return 'price-up'
  if (value < 0) return 'price-down'
  return ''
}

// 查询结果
const handleQuery = async () => {
  loading.value = true
  try {
    const params = {
      limit: pagination.value.pageSize,
      offset: (pagination.value.page - 1) * pagination.value.pageSize
    }

    if (queryForm.value.strategy_code) {
      params.strategy_code = queryForm.value.strategy_code
    }
    if (queryForm.value.symbol) {
      params.symbol = queryForm.value.symbol
    }
    if (queryForm.value.check_date) {
      params.check_date = queryForm.value.check_date
    }
    if (queryForm.value.match_result !== null) {
      params.match_result = queryForm.value.match_result
    }

    const response = await strategyApi.getResults(params)
    if (response.data.success) {
      results.value = response.data.data
      pagination.value.total = response.data.total || results.value.length
      ElMessage.success(`查询成功，共${results.value.length}条结果`)
    } else {
      ElMessage.error(response.data.message || '查询失败')
    }
  } catch (error) {
    console.error('查询失败:', error)
    ElMessage.error('查询失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 重置查询
const handleReset = () => {
  queryForm.value = {
    strategy_code: '',
    symbol: '',
    check_date: '',
    match_result: null
  }
  pagination.value.page = 1
  handleQuery()
}

// 查看详情
const viewDetails = (row) => {
  selectedResult.value = row
  detailsVisible.value = true
}

// 重新运行
const rerun = (row) => {
  ElMessage.info(`重新运行策略：${row.strategy_code} on ${row.symbol}`)
  // 这里可以触发单只运行
}

// 组件挂载时加载数据
onMounted(() => {
  loadStrategies()
  handleQuery()
})
</script>

<style scoped lang="scss">
.results-query {
  .price-up {
    color: #f56c6c;
  }

  .price-down {
    color: #67c23a;
  }

  pre {
    font-size: 12px;
    background: #f5f7fa;
    padding: 10px;
    border-radius: 4px;
    max-height: 200px;
    overflow: auto;
  }
}
</style>
