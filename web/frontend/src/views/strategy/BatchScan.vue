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
                v-for="strategy in strategies"
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

.batch-scan {
  padding: 20px;
  min-height: 100vh;
  background: var(--bg-primary);
  background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(212, 175, 55, 0.02) 10px, rgba(212, 175, 55, 0.02) 11px);
}

.card {
  background: var(--bg-secondary);
  border: 1px solid var(--gold-dim);
  padding: 30px;
  position: relative;
  border-radius: 0;

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: 16px;
    height: 16px;
    border: 2px solid var(--gold-primary);
  }

  &::before {
    top: 12px;
    left: 12px;
    border-right: none;
    border-bottom: none;
  }

  &::after {
    bottom: 12px;
    right: 12px;
    border-left: none;
    border-top: none;
  }
}

.page-header {
  margin-bottom: 30px;
  position: relative;
  padding-bottom: 15px;

  .page-title {
    font-family: var(--font-display);
    font-size: 28px;
    color: var(--gold-primary);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 0 0 8px 0;
  }

  .page-subtitle {
    font-family: var(--font-display);
    font-size: 12px;
    color: var(--gold-dim);
    text-transform: uppercase;
    letter-spacing: 3px;
  }

  .decorative-line {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 200px;
    height: 2px;
    background: linear-gradient(90deg, var(--gold-primary), transparent);

    &::before {
      content: '';
      position: absolute;
      bottom: -6px;
      left: 0;
      width: 60px;
      height: 1px;
      background: linear-gradient(90deg, var(--gold-dim), transparent);
    }
  }
}

.form-section {
  margin-bottom: 30px;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  align-items: flex-start;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;

  &.full-width {
    width: 100%;
  }

  .form-label {
    font-family: var(--font-display);
    font-size: 11px;
    color: var(--gold-dim);
    text-transform: uppercase;
    letter-spacing: 1px;
    min-width: 120px;
  }

  .form-tip {
    font-size: 12px;
    color: var(--text-muted);
    font-family: var(--font-body);
  }
}

.input,
.select,
  width: 100%;
  padding: 10px 15px;
  background: var(--bg-primary);
  border: 1px solid var(--gold-dim);
  color: var(--text-primary);
  font-family: var(--font-body);
  font-size: 14px;
  border-radius: 0;
  outline: none;
  transition: all 0.3s ease;

  &:focus {
    border-color: var(--gold-primary);
    box-shadow: 0 0 8px rgba(212, 175, 55, 0.3);
  }

  &::placeholder {
    color: var(--text-muted);
  }
}

  resize: vertical;
  line-height: 1.6;
}

:deep(.el-date-editor) {
  .el-input__wrapper {
    background: var(--bg-primary);
    border: 1px solid var(--gold-dim);
    border-radius: 0;
    box-shadow: none;
    padding: 10px 15px;
    transition: all 0.3s ease;

    &:hover {
      border-color: var(--gold-muted);
    }

    &.is-focus {
      border-color: var(--gold-primary);
      box-shadow: 0 0 8px rgba(212, 175, 55, 0.3);
    }
  }

  .el-input__inner {
    color: var(--text-primary);
    font-family: var(--font-body);
  }

  .el-input__prefix {
    color: var(--gold-dim);
  }
}

.radio-group {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: var(--text-primary);
  font-family: var(--font-body);
  font-size: 14px;
  transition: all 0.3s ease;

  &:hover {
    color: var(--gold-primary);
  }
}

  width: 18px;
  height: 18px;
  accent-color: var(--gold-primary);
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 10px;
}

.button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--gold-primary);
  color: var(--bg-primary);
  border: none;
  font-family: var(--font-display);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
  cursor: pointer;
  border-radius: 0;
  transition: all 0.3s ease;

  &:hover:not(:disabled) {
    background: var(--gold-muted);
    box-shadow: 0 0 12px rgba(212, 175, 55, 0.4);
  }

  &:disabled {
    background: var(--gold-dim);
    cursor: not-allowed;
    opacity: 0.5;
  }

  &.secondary {
    background: transparent;
    border: 1px solid var(--gold-primary);
    color: var(--gold-primary);

    &:hover:not(:disabled) {
      background: var(--gold-primary);
      color: var(--bg-primary);
    }
  }
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.scan-progress {
  margin: 30px 0;
  padding: 20px;
  background: rgba(212, 175, 55, 0.03);
  border: 1px solid var(--gold-dim);

  .progress-bar {
    width: 100%;
    height: 8px;
    background: var(--bg-primary);
    border: 1px solid var(--gold-dim);
    position: relative;
    overflow: hidden;

    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--gold-primary), var(--gold-muted));
      transition: width 0.3s ease;
    }
  }

  .progress-text {
    text-align: center;
    margin-top: 12px;
    color: var(--text-primary);
    font-family: var(--font-body);
    font-size: 14px;
  }
}

.result-section {
  margin-top: 30px;
  padding-top: 30px;
  border-top: 1px solid var(--gold-dim);

  .section-title {
    font-family: var(--font-display);
    font-size: 20px;
    color: var(--gold-primary);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 0 0 25px 0;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 25px;
}

.stat-card {
  background: var(--bg-primary);
  border: 1px solid var(--gold-dim);
  padding: 20px;
  text-align: center;
  position: relative;
  transition: all 0.3s ease;

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: 10px;
    height: 10px;
    border: 2px solid var(--gold-primary);
  }

  &::before {
    top: 6px;
    left: 6px;
    border-right: none;
    border-bottom: none;
  }

  &::after {
    bottom: 6px;
    right: 6px;
    border-left: none;
    border-top: none;
  }

  &:hover {
    border-color: var(--gold-primary);
    box-shadow: 0 0 15px rgba(212, 175, 55, 0.3);
    transform: translateY(-2px);
  }

  .stat-value {
    font-family: var(--font-display);
    font-size: 36px;
    color: var(--gold-primary);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 8px;
  }

  .stat-label {
    font-family: var(--font-display);
    font-size: 12px;
    color: var(--gold-dim);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
  }

  .stat-unit {
    font-family: var(--font-body);
    font-size: 12px;
    color: var(--text-muted);
  }
}

.alert-box {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px 20px;
  margin-bottom: 25px;
  border: 1px solid;

  &.success {
    background: rgba(0, 230, 118, 0.1);
    border-color: rgba(0, 230, 118, 0.3);
    color: var(--fall);

    .alert-icon {
      color: var(--fall);
    }
  }

  &.error {
    background: rgba(255, 82, 82, 0.1);
    border-color: rgba(255, 82, 82, 0.3);
    color: var(--rise);

    .alert-icon {
      color: var(--rise);
    }
  }

  .alert-icon {
    flex-shrink: 0;
  }

  span {
    font-family: var(--font-body);
    font-size: 14px;
    flex: 1;
  }
}

.result-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .batch-scan {
    padding: 10px;
  }

  .card {
    padding: 15px;
  }

  .form-row {
    flex-direction: column;
    gap: 15px;
  }

  .form-item {
    .form-label {
      min-width: auto;
    }
  }

  .radio-group {
    flex-direction: column;
    gap: 12px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .result-actions {
    flex-direction: column;

    .button {
      width: 100%;
      justify-content: center;
    }
  }
}
</style>
