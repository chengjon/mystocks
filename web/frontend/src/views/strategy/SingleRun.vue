<template>
  <div class="single-run">
    <el-card>
      <template #header>
        <span>🎯 单只股票策略运行</span>
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
            >
              <div class="strategy-option">
                <span class="strategy-name">{{ strategy.strategy_name_cn }}</span>
                <span class="strategy-desc">{{ strategy.description }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="股票代码">
          <el-input
            v-model="form.symbol"
            placeholder="请输入股票代码（如：600519）"
            clearable
          >
            <template #prepend>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="股票名称">
          <el-input
            v-model="form.stock_name"
            placeholder="可选，如：贵州茅台"
            clearable
          />
        </el-form-item>

        <el-form-item label="检查日期">
          <el-date-picker
            v-model="form.check_date"
            type="date"
            placeholder="选择日期（可选）"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
          <div class="form-tip">留空则使用今天的数据</div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleRun" :loading="running">
            <el-icon><VideoPlay /></el-icon> 运行策略
          </el-button>
          <el-button @click="handleReset">
            <el-icon><RefreshLeft /></el-icon> 重置
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 运行结果 -->
      <el-divider v-if="result" />

      <div v-if="result" class="result-section">
        <h3>运行结果</h3>

        <el-result
          :icon="result.data?.match_result ? 'success' : 'info'"
          :title="result.data?.match_result ? '✅ 匹配策略条件' : '❌ 不匹配策略条件'"
        >
          <template #sub-title>
            <div class="result-info">
              <p><strong>策略：</strong>{{ getStrategyName(result.data?.strategy_code) }}</p>
              <p><strong>股票：</strong>{{ result.data?.symbol }} {{ form.stock_name }}</p>
              <p><strong>检查日期：</strong>{{ result.data?.check_date }}</p>
              <p><strong>消息：</strong>{{ result.message }}</p>
            </div>
          </template>
          <template #extra>
            <el-button type="primary" @click="viewAllResults">
              查看所有结果
            </el-button>
          </template>
        </el-result>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, VideoPlay, RefreshLeft } from '@element-plus/icons-vue'
import axios from 'axios'
import { API_ENDPOINTS } from '@/config/api'

// Props
const props = defineProps({
  initialStrategy: {
    type: Object,
    default: null
  }
})

// 响应式数据
const strategies = ref([])
const running = ref(false)
const result = ref(null)

const form = ref({
  strategy_code: '',
  symbol: '',
  stock_name: '',
  check_date: ''
})

// 监听初始策略变化
watch(() => props.initialStrategy, (newVal) => {
  if (newVal) {
    form.value.strategy_code = newVal.strategy_code
  }
}, { immediate: true })

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

// 获取策略名称
const getStrategyName = (code) => {
  const strategy = strategies.value.find(s => s.strategy_code === code)
  return strategy ? strategy.strategy_name_cn : code
}

// 运行策略
const handleRun = async () => {
  if (!form.value.strategy_code) {
    ElMessage.warning('请选择策略')
    return
  }
  if (!form.value.symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }

  running.value = true
  result.value = null

  try {
    const params = {
      strategy_code: form.value.strategy_code,
      symbol: form.value.symbol
    }
    if (form.value.stock_name) {
      params.stock_name = form.value.stock_name
    }
    if (form.value.check_date) {
      params.check_date = form.value.check_date
    }

    const response = await axios.post(API_ENDPOINTS.strategy.runSingle, null, { params })
    result.value = response.data

    if (response.data.success) {
      ElMessage.success('策略运行完成')
    } else {
      ElMessage.error(response.data.message || '运行失败')
    }
  } catch (error) {
    console.error('运行策略失败:', error)
    ElMessage.error('运行策略失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    running.value = false
  }
}

// 重置表单
const handleReset = () => {
  form.value = {
    strategy_code: '',
    symbol: '',
    stock_name: '',
    check_date: ''
  }
  result.value = null
}

// 查看所有结果
const viewAllResults = () => {
  // 这里可以触发事件切换到结果查询标签
  ElMessage.info('切换到结果查询标签查看')
}

// 组件挂载时加载数据
onMounted(() => {
  loadStrategies()
})
</script>

<style scoped lang="scss">
.single-run {
  .strategy-option {
    display: flex;
    flex-direction: column;

    .strategy-name {
      font-size: 14px;
      color: #303133;
    }

    .strategy-desc {
      font-size: 12px;
      color: #909399;
      margin-top: 2px;
    }
  }

  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
  }

  .result-section {
    h3 {
      font-size: 18px;
      margin-bottom: 16px;
    }

    .result-info {
      text-align: left;
      font-size: 14px;
      color: #606266;

      p {
        margin: 8px 0;
      }
    }
  }
}
</style>
