<template>
  <div class="batch-scan">
    <div class="card">
      <div class="page-header">
        <h1 class="page-title">批量策略扫描</h1>
        <div class="page-subtitle">Batch Strategy Scanner</div>
        <div class="decorative-line"></div>
      </div>

      <div class="form-section">
        <div class="form-row">
          <div class="form-item">
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
            <label class="form-label">扫描模式</label>
            <div class="radio-group">
              <label class="radio-label">
                <input
                  type="radio"
                  v-model="form.scan_mode"
                  value="all"
                  class="radio"
                />
                <span>全市场扫描</span>
              </label>
              <label class="radio-label">
                <input
                  type="radio"
                  v-model="form.scan_mode"
                  value="list"
                  class="radio"
                />
                <span>指定股票列表</span>
              </label>
              <label class="radio-label">
                <input
                  type="radio"
                  v-model="form.scan_mode"
                  value="limit"
                  class="radio"
                />
                <span>限制数量扫描</span>
              </label>
            </div>
          </div>
        </div>

        <div v-if="form.scan_mode === 'list'" class="form-row">
          <div class="form-item full-width">
            <label class="form-label">股票列表</label>
            <textarea
              v-model="form.symbols"
              class="textarea"
              :rows="4"
              placeholder="输入股票代码，用逗号分隔（如：600519,000001,600000）"
            />
            <div class="form-tip">支持批量输入，逗号分隔</div>
          </div>
        </div>

        <div v-if="form.scan_mode === 'limit'" class="form-row">
          <div class="form-item">
            <label class="form-label">扫描数量</label>
            <input
              v-model.number="form.limit"
              type="number"
              class="input"
              min="1"
              max="5000"
              step="10"
            />
            <div class="form-tip">用于测试，建议先扫描少量股票</div>
          </div>
        </div>

        <div v-if="form.scan_mode !== 'list'" class="form-row">
          <div class="form-item">
            <label class="form-label">市场类型</label>
            <select v-model="form.market" class="select">
              <option value="A">全部A股</option>
              <option value="SH">上证</option>
              <option value="SZ">深证</option>
              <option value="CYB">创业板</option>
              <option value="KCB">科创板</option>
            </select>
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
          <button class="button" @click="handleScan" :disabled="scanning">
            <svg v-if="scanning" class="spinner" width="16" height="16" viewBox="0 0 50 50">
              <circle cx="25" cy="25" r="20" fill="none" :stroke="'var(--gold-primary)'" stroke-width="4"></circle>
            </svg>
            <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-primary)'" stroke-width="2">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            开始扫描
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

      <div v-if="scanning" class="scan-progress">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
        <p class="progress-text">正在扫描中，请稍候...</p>
      </div>

      <div v-if="result" class="result-section">
        <h2 class="section-title">扫描结果</h2>

        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-value">{{ result.data?.total || 0 }}</div>
            <div class="stat-label">总计扫描</div>
            <div class="stat-unit">只</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ result.data?.matched || 0 }}</div>
            <div class="stat-label">匹配数量</div>
            <div class="stat-unit">只</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ result.data?.failed || 0 }}</div>
            <div class="stat-label">失败数量</div>
            <div class="stat-unit">只</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ matchRate.toFixed(2) }}</div>
            <div class="stat-label">匹配率</div>
            <div class="stat-unit">%</div>
          </div>
        </div>

        <div class="alert-box" :class="result.success ? 'success' : 'error'">
          <svg class="alert-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" :stroke="'currentColor'" stroke-width="2">
            <path v-if="result.success" d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline v-if="result.success" points="22,4 12,14.01 9,11.01"></polyline>
            <circle v-else cx="12" cy="12" r="10"></circle>
            <line v-else x1="12" y1="8" x2="12" y2="12"></line>
            <line v-else x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <span>{{ result.message }}</span>
        </div>

        <div class="result-actions">
          <button class="button" @click="viewMatchedStocks">
            查看匹配股票
          </button>
          <button class="button secondary" @click="viewAllResults">
            查看详细结果
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { strategyApi } from '@/api'

const strategies = ref([])
const scanning = ref(false)
const result = ref(null)
const progress = ref(0)

const form = ref({
  strategy_code: '',
  scan_mode: 'limit',
  symbols: '',
  limit: 100,
  market: 'A',
  check_date: ''
})

const matchRate = computed(() => {
  if (!result.value?.data?.total) return 0
  return (result.value.data.matched / result.value.data.total) * 100
})

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

    const response = await strategyApi.runBatch(params)
    result.value = response.data

    progress.value = 100

    if (response.data.success) {
      ElMessage.success('扫描完成')
    } else {
      ElMessage.error(response.data.message || '扫描失败')
    }
  } catch (error) {
    console.error('扫描失败:', error)
    progress.value = 100
    ElMessage.error('扫描失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    clearInterval(progressInterval)
    scanning.value = false
  }
}

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

const viewMatchedStocks = () => {
  ElMessage.info('功能开发中：跳转到匹配股票列表')
}

const viewAllResults = () => {
  ElMessage.info('功能开发中：跳转到结果查询页面')
}

onMounted(() => {
  loadStrategies()
})
</script>

<style scoped lang="scss">
@import "./styles/BatchScan";
</style>
