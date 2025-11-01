<template>
  <div class="batch-scan">
    <el-card>
      <template #header>
        <span>🚀 批量策略扫描</span>
      </template>

      <el-form :model="form" label-width="120px">
        <el-form-item label="选择策略">
          <el-select
            v-model="form.strategy_code"
            placeholder="请选择策略"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="strategy in strategies"
              :key="strategy.strategy_code"
              :label="`${strategy.strategy_name_cn} (${strategy.strategy_code})`"
              :value="strategy.strategy_code"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="扫描模式">
          <el-radio-group v-model="form.scan_mode">
            <el-radio label="all">全市场扫描</el-radio>
            <el-radio label="list">指定股票列表</el-radio>
            <el-radio label="limit">限制数量扫描</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 指定股票列表 -->
        <el-form-item v-if="form.scan_mode === 'list'" label="股票列表">
          <el-input
            v-model="form.symbols"
            type="textarea"
            :rows="4"
            placeholder="输入股票代码，用逗号分隔（如：600519,000001,600000）"
          />
          <div class="form-tip">支持批量输入，逗号分隔</div>
        </el-form-item>

        <!-- 限制数量 -->
        <el-form-item v-if="form.scan_mode === 'limit'" label="扫描数量">
          <el-input-number
            v-model="form.limit"
            :min="1"
            :max="5000"
            :step="10"
          />
          <div class="form-tip">用于测试，建议先扫描少量股票</div>
        </el-form-item>

        <!-- 市场类型 -->
        <el-form-item v-if="form.scan_mode !== 'list'" label="市场类型">
          <el-select v-model="form.market" style="width: 200px">
            <el-option label="全部A股" value="A" />
            <el-option label="上证" value="SH" />
            <el-option label="深证" value="SZ" />
            <el-option label="创业板" value="CYB" />
            <el-option label="科创板" value="KCB" />
          </el-select>
        </el-form-item>

        <el-form-item label="检查日期">
          <el-date-picker
            v-model="form.check_date"
            type="date"
            placeholder="选择日期（可选）"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 200px"
          />
          <div class="form-tip">留空则使用今天的数据</div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleScan" :loading="scanning">
            <el-icon><Search /></el-icon> 开始扫描
          </el-button>
          <el-button @click="handleReset">
            <el-icon><RefreshLeft /></el-icon> 重置
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 扫描进度 -->
      <div v-if="scanning" class="scan-progress">
        <el-progress :percentage="progress" :status="progressStatus" />
        <p class="progress-text">正在扫描中，请稍候...</p>
      </div>

      <!-- 扫描结果 -->
      <el-divider v-if="result" />

      <div v-if="result" class="result-section">
        <h3>扫描结果</h3>

        <el-row :gutter="20" class="stats-row">
          <el-col :span="6">
            <el-statistic title="总计扫描" :value="result.data?.total || 0">
              <template #suffix>只</template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="匹配数量" :value="result.data?.matched || 0">
              <template #suffix>只</template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="失败数量" :value="result.data?.failed || 0">
              <template #suffix>只</template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic
              title="匹配率"
              :value="matchRate"
              :precision="2"
            >
              <template #suffix>%</template>
            </el-statistic>
          </el-col>
        </el-row>

        <el-alert
          :type="result.success ? 'success' : 'error'"
          :title="result.message"
          :closable="false"
          show-icon
          style="margin-top: 20px"
        />

        <div class="result-actions">
          <el-button type="primary" @click="viewMatchedStocks">
            查看匹配股票
          </el-button>
          <el-button @click="viewAllResults">
            查看详细结果
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, RefreshLeft } from '@element-plus/icons-vue'
import axios from 'axios'
import { API_ENDPOINTS } from '@/config/api'

// 响应式数据
const strategies = ref([])
const scanning = ref(false)
const result = ref(null)
const progress = ref(0)
const progressStatus = ref('')

const form = ref({
  strategy_code: '',
  scan_mode: 'limit',
  symbols: '',
  limit: 100,
  market: 'A',
  check_date: ''
})

// 计算匹配率
const matchRate = computed(() => {
  if (!result.value?.data?.total) return 0
  return (result.value.data.matched / result.value.data.total) * 100
})

// 加载策略列表
const loadStrategies = async () => {
  try {
    const response = await axios.get(API_ENDPOINTS.strategy.definitions)
    if (response.data.success) {
      strategies.value = response.data.data
    }
  } catch (error) {
    console.error('加载策略列表失败:', error)
  }
}

// 执行扫描
const handleScan = async () => {
  if (!form.value.strategy_code) {
    ElMessage.warning('请选择策略')
    return
  }

  if (form.value.scan_mode === 'list' && !form.value.symbols) {
    ElMessage.warning('请输入股票列表')
    return
  }

  scanning.value = true
  result.value = null
  progress.value = 0
  progressStatus.value = ''

  // 模拟进度
  const progressInterval = setInterval(() => {
    if (progress.value < 90) {
      progress.value += 10
    }
  }, 1000)

  try {
    const params = {
      strategy_code: form.value.strategy_code
    }

    if (form.value.scan_mode === 'list') {
      params.symbols = form.value.symbols
    } else if (form.value.scan_mode === 'limit') {
      params.limit = form.value.limit
    }

    if (form.value.scan_mode !== 'list') {
      params.market = form.value.market
    }

    if (form.value.check_date) {
      params.check_date = form.value.check_date
    }

    const response = await axios.post(API_ENDPOINTS.strategy.runBatch, null, { params })
    result.value = response.data

    progress.value = 100
    progressStatus.value = response.data.success ? 'success' : 'exception'

    if (response.data.success) {
      ElMessage.success('扫描完成')
    } else {
      ElMessage.error(response.data.message || '扫描失败')
    }
  } catch (error) {
    console.error('扫描失败:', error)
    progress.value = 100
    progressStatus.value = 'exception'
    ElMessage.error('扫描失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    clearInterval(progressInterval)
    scanning.value = false
  }
}

// 重置表单
const handleReset = () => {
  form.value = {
    strategy_code: '',
    scan_mode: 'limit',
    symbols: '',
    limit: 100,
    market: 'A',
    check_date: ''
  }
  result.value = null
  progress.value = 0
}

// 查看匹配股票
const viewMatchedStocks = () => {
  ElMessage.info('功能开发中：跳转到匹配股票列表')
}

// 查看所有结果
const viewAllResults = () => {
  ElMessage.info('功能开发中：跳转到结果查询页面')
}

// 组件挂载时加载数据
onMounted(() => {
  loadStrategies()
})
</script>

<style scoped lang="scss">
.batch-scan {
  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
  }

  .scan-progress {
    margin: 20px 0;

    .progress-text {
      text-align: center;
      margin-top: 10px;
      color: #606266;
    }
  }

  .result-section {
    h3 {
      font-size: 18px;
      margin-bottom: 20px;
    }

    .stats-row {
      margin-bottom: 20px;
    }

    .result-actions {
      margin-top: 20px;
      display: flex;
      gap: 12px;
    }
  }
}
</style>
