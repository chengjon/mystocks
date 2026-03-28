<template>
  <div class="single-run">
    <div class="card">
      <div class="page-header">
        <h1 class="page-title">单只股票策略运行</h1>
        <div class="page-subtitle">Single Stock Strategy Runner</div>
        <div class="decorative-line"></div>
      </div>

      <div class="form-section">
        <div class="form-row">
          <div class="form-item full-width">
            <label class="form-label">选择策略</label>
            <select v-model="form.strategy_code" class="select">
              <option value="">请选择策略</option>
              <option
                v-for="(strategy, _idx) in strategies"
                :key="strategy.strategy_code"
                :value="strategy.strategy_code"
              >
                {{ strategy.strategy_name_cn }} ({{ strategy.strategy_code }})
              </option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-item">
            <label class="form-label">股票代码</label>
            <div class="input-with-icon">
              <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-dim)'" stroke-width="2">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
              <input
                v-model="form.symbol"
                type="text"
                class="input"
                placeholder="请输入股票代码（如：600519）"
              />
            </div>
          </div>

          <div class="form-item">
            <label class="form-label">股票名称</label>
            <input
              v-model="form.stock_name"
              type="text"
              class="input"
              placeholder="可选，如：贵州茅台"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-item">
            <label class="form-label">检查日期</label>
            <el-date-picker
              v-model="form.check_date"
              type="date"
              placeholder="选择日期（可选）"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              :deep="true"
            />
            <div class="form-tip">留空则使用今天的数据</div>
          </div>
        </div>

        <div class="form-actions">
          <button class="button" @click="handleRun" :disabled="running">
            <svg v-if="running" class="spinner" width="16" height="16" viewBox="0 0 50 50">
              <circle cx="25" cy="25" r="20" fill="none" :stroke="'var(--gold-primary)'" stroke-width="4"></circle>
            </svg>
            <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-primary)'" stroke-width="2">
              <polygon points="5,3 19,12 5,21 5,3"></polygon>
            </svg>
            运行策略
          </button>
          <button class="button secondary" @click="handleReset">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-primary)'" stroke-width="2">
              <path d="M23 4v6h-6"></path>
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
            </svg>
            重置
          </button>
        </div>
      </div>

      <div v-if="result" class="result-section">
        <h2 class="section-title">运行结果</h2>

        <div class="result-card" :class="result.data?.match_result ? 'match' : 'no-match'">
          <div class="result-icon">
            <svg v-if="result.data?.match_result" width="64" height="64" viewBox="0 0 24 24" fill="none" :stroke="'currentColor'" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22,4 12,14.01 9,11.01"></polyline>
            </svg>
            <svg v-else width="64" height="64" viewBox="0 0 24 24" fill="none" :stroke="'currentColor'" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
          </div>

          <div class="result-title">
            {{ result.data?.match_result ? '✅ 匹配策略条件' : '❌ 不匹配策略条件' }}
          </div>

          <div class="result-info">
            <div class="info-item">
              <label>策略</label>
              <span>{{ getStrategyName(result.data?.strategy_code) }}</span>
            </div>
            <div class="info-item">
              <label>股票</label>
              <span>{{ result.data?.symbol }} {{ form.stock_name }}</span>
            </div>
            <div class="info-item">
              <label>检查日期</label>
              <span>{{ result.data?.check_date }}</span>
            </div>
            <div class="info-item">
              <label>消息</label>
              <span>{{ result.message }}</span>
            </div>
          </div>

          <div class="result-actions">
            <button class="button" @click="viewAllResults">
              查看所有结果
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { strategyApi } from '@/api'

const props = defineProps({
  initialStrategy: {
    type: Object,
    default: null
  }
})

const strategies = ref([])
const running = ref(false)
const result = ref(null)

const form = ref({
  strategy_code: '',
  symbol: '',
  stock_name: '',
  check_date: ''
})

watch(() => props.initialStrategy, (newVal) => {
  if (newVal) {
    form.value.strategy_code = newVal.strategy_code
  }
}, { immediate: true })

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

const getStrategyName = (code) => {
  const strategy = strategies.value.find(s => s.strategy_code === code)
  return strategy ? strategy.strategy_name_cn : code
}

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

    const response = await strategyApi.runSingle(params)
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

const handleReset = () => {
  form.value = {
    strategy_code: '',
    symbol: '',
    stock_name: '',
    check_date: ''
  }
  result.value = null
}

const viewAllResults = () => {
  ElMessage.info('切换到结果查询标签查看')
}

onMounted(() => {
  loadStrategies()
})
</script>

<style scoped lang="scss">
@use "./styles/SingleRun.scss" as *;
</style>
