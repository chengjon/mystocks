<template>
  <div class="strategy-management">

    <div class="page-header">
      <h1 class="page-title">STRATEGY MANAGEMENT</h1>
      <p class="page-subtitle">QUANTITATIVE TRADING STRATEGIES | BACKTESTING | PERFORMANCE ANALYTICS</p>
    </div>

    <div class="header-section">
      <div class="header-info">
        <h2 class="strategy-count mono">{{ filteredStrategies.length }} STRATEGIES</h2>
        <p class="header-desc">MANAGE AND BACKTEST YOUR QUANTITATIVE TRADING STRATEGIES</p>
      </div>
      <el-button type="warning" @click="showCreateDialog = true" class="create-btn">
        CREATE STRATEGY
      </el-button>
    </div>

      title="STRATEGY FILTERS"
      :filters="strategyFilters"
      :quick-filters="strategyQuickFilters"
      @filter-change="handleFilterChange"
      @reset="clearFilters"
    /> -->

    <div v-if="loading && strategies.length === 0" class="loading-state">
      <div class="spinner"></div>
      <p>LOADING STRATEGIES...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>LOADING FAILED</h3>
      <p>{{ error }}</p>
      <el-button @click="fetchStrategies">
        RETRY
      </el-button>
    </div>

    <div v-else-if="filteredStrategies.length === 0" class="empty-state">
      <div class="empty-icon">📊</div>
      <h3>NO STRATEGIES FOUND</h3>
      <p>TRY ADJUSTING YOUR SEARCH OR FILTER CRITERIA</p>
      <el-button @click="clearFilters">
        CLEAR FILTERS
      </el-button>
    </div>

    <div v-else class="strategy-grid">
      <el-card
        v-for="strategy in paginatedStrategies"
        :key="strategy.id"
        class="strategy-card"
        @click="handleView(strategy)"
      >
        <h3>{{ strategy.name }}</h3>
        <p>{{ strategy.description }}</p>
        <p>Type: {{ strategy.type }}</p>
        <p>Status: {{ strategy.status }}</p>
      </el-card>
    </div>

    <div v-if="filteredStrategies.length > 0" class="pagination-section">
      <div class="pagination">
        <button
          class="page-btn"
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          PREV
        </button>
        <span class="page-info">PAGE {{ currentPage }} OF {{ totalPages }}</span>
        <button
          class="page-btn"
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          NEXT
        </button>
      </div>
    </div>

    <div v-if="showCreateDialog" class="modal-overlay" @click.self="handleCancel">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">{{ editingStrategy ? 'EDIT STRATEGY' : 'CREATE STRATEGY' }}</h3>
          <button class="modal-close" @click="handleCancel">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">STRATEGY NAME *</label>
            <el-input v-model="strategyForm.name" placeholder="ENTER STRATEGY NAME" />
          </div>

          <div class="form-group">
            <label class="form-label">STRATEGY TYPE *</label>
            <div class="select">
              <select v-model="strategyForm.type">
                <option value="trend_following">TREND FOLLOWING</option>
                <option value="mean_reversion">MEAN REVERSION</option>
                <option value="momentum">MOMENTUM</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">DESCRIPTION</label>
            <el-input
              v-model="strategyForm.description"
              type="textarea"
              :rows="3"
              placeholder="STRATEGY DESCRIPTION"
            />
          </div>

          <div class="form-group">
            <label class="form-label">PARAMETERS</label>
            <div class="parameters-container">
              <div
                v-for="(param, index) in strategyForm.parameters"
                :key="index"
                class="parameter-row"
              >
                <el-input
                  v-model="param.key"
                  placeholder="PARAMETER NAME"
                />
                <el-input
                  v-model="param.value"
                  placeholder="VALUE"
                />
                <el-button size="small" @click="removeParameter(index)">
                  DELETE
                </el-button>
              </div>
              <el-button size="small" @click="addParameter" class="add-param-btn">
                ADD PARAMETER
              </el-button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <el-button @click="handleCancel">
            CANCEL
          </el-button>
          <el-button type="warning" @click="handleSave" :loading="saving">
            {{ editingStrategy ? 'UPDATE' : 'CREATE' }}
          </el-button>
        </div>
      </div>
    </div>

    <div v-if="showBacktestDialog" class="modal-overlay" @click.self="showBacktestDialog = false">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">BACKTEST STRATEGY</h3>
          <button class="modal-close" @click="showBacktestDialog = false">×</button>
        </div>
        <div class="modal-body">
          <div v-if="backtestingStrategy" class="backtest-content">
            <h4>{{ backtestingStrategy.name }}</h4>
            <p>BACKTEST FUNCTIONALITY COMING SOON</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElInput } from 'element-plus'

interface Strategy {
  id: string
  name: string
  description?: string
  type: string
  status: string
  parameters?: Record<string, any>
}

const strategies = ref<Strategy[]>([
  { id: '1', name: 'MA Crossover', description: 'Moving average crossover strategy', type: 'trend_following', status: 'active' },
  { id: '2', name: 'RSI Reversal', description: 'RSI-based mean reversion', type: 'mean_reversion', status: 'inactive' },
  { id: '3', name: 'Momentum Breakout', description: 'Momentum-based breakout strategy', type: 'momentum', status: 'testing' }
])

const loading = ref(false)
const error = ref('')
const showCreateDialog = ref(false)
const editingStrategy = ref<Strategy | null>(null)
const backtestingStrategy = ref<Strategy | null>(null)
const showBacktestDialog = ref(false)
const saving = ref(false)

const searchQuery = ref('')
const filterType = ref('')
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(12)

const strategyForm = ref({
  name: '',
  description: '',
  type: 'trend_following',
  parameters: [] as Array<{ key: string; value: string }>
})

const strategyFilters = [
  { key: 'search', label: 'SEARCH', type: 'text' as const, placeholder: 'SEARCH STRATEGIES...' },
  { key: 'type', label: 'TYPE', type: 'select' as const, placeholder: 'FILTER BY TYPE', options: [
    { label: 'TREND FOLLOWING', value: 'trend_following' },
    { label: 'MEAN REVERSION', value: 'mean_reversion' },
    { label: 'MOMENTUM', value: 'momentum' }
  ]},
  { key: 'status', label: 'STATUS', type: 'select' as const, placeholder: 'FILTER BY STATUS', options: [
    { label: 'ACTIVE', value: 'active' },
    { label: 'INACTIVE', value: 'inactive' },
    { label: 'TESTING', value: 'testing' }
  ]}
]

const strategyQuickFilters = [
  { key: 'all', label: 'ALL', filters: { search: '', type: '', status: '' } },
  { key: 'active', label: 'ACTIVE', filters: { search: '', type: '', status: 'active' } },
  { key: 'trend', label: 'TREND', filters: { search: '', type: 'trend_following', status: '' } }
]

const filteredStrategies = computed(() => {
  let result = strategies.value
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(s => s.name.toLowerCase().includes(query) || s.description?.toLowerCase().includes(query))
  }
  if (filterType.value) result = result.filter(s => s.type === filterType.value)
  if (filterStatus.value) result = result.filter(s => s.status === filterStatus.value)
  return result
})

const paginatedStrategies = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredStrategies.value.slice(start, end)
})

const totalPages = computed(() => Math.ceil(filteredStrategies.value.length / pageSize.value))

const fetchStrategies = () => {
  loading.value = false
  error.value = ''
}

const addParameter = () => {
  strategyForm.value.parameters.push({ key: '', value: '' })
}

const removeParameter = (index: number) => {
  strategyForm.value.parameters.splice(index, 1)
}

const clearFilters = () => {
  searchQuery.value = ''
  filterType.value = ''
  filterStatus.value = ''
  currentPage.value = 1
}

const handleFilterChange = (filters: Record<string, any>) => {
  searchQuery.value = filters.search || ''
  filterType.value = filters.type || ''
  filterStatus.value = filters.status || ''
  currentPage.value = 1
}

const mapStrategyToCard = (strategy: Strategy) => ({
  strategy_code: strategy.id,
  strategy_name_cn: strategy.name,
  description: strategy.description,
  status: strategy.status || 'active',
  running: strategy.status === 'active',
  total_return: 0,
  annual_return: 0,
  sharpe_ratio: 0,
  max_drawdown: 0,
  win_rate: 0
})

const handleView = (strategy: Strategy) => console.log('View:', strategy)
const handleStart = (strategy: Strategy) => console.log('Start:', strategy)
const handleStop = (strategy: Strategy) => console.log('Stop:', strategy)
const handleEdit = (strategy: Strategy) => {
  editingStrategy.value = strategy
  strategyForm.value = {
    name: strategy.name,
    description: strategy.description || '',
    type: strategy.type,
    parameters: strategy.parameters ? Object.entries(strategy.parameters).map(([k, v]) => ({ key: k, value: String(v) })) : []
  }
  showCreateDialog.value = true
}

const handleDelete = async (strategy: Strategy) => {
  strategies.value = strategies.value.filter(s => s.id !== strategy.id)
}

const handleBacktest = (strategy: Strategy) => {
  backtestingStrategy.value = strategy
  showBacktestDialog.value = true
}

const handleSave = async () => {
  if (!strategyForm.value.name) return
  saving.value = true
  await new Promise(r => setTimeout(r, 500))
  saving.value = false
  showCreateDialog.value = false
}

const handleCancel = () => {
  editingStrategy.value = null
  showCreateDialog.value = false
  strategyForm.value = { name: '', description: '', type: 'trend_following', parameters: [] }
}
</script>

<style scoped>

.strategy-management {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
  padding: var(--space-xl);
  position: relative;
}

.background-pattern {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(212, 175, 55, 0.02) 10px, rgba(212, 175, 55, 0.02) 11px);
  pointer-events: none;
  z-index: -1;
}

.page-header {
  text-align: center;
  margin-bottom: var(--space-lg);
}

.page-title {
  font-family: var(--font-display);
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--gold-primary);
  text-transform: uppercase;
  letter-spacing: 0.2em;
  margin: 0 0 var(--space-md) 0;
}

.page-subtitle {
  font-family: var(--font-body);
  font-size: 1rem;
  color: var(--silver-muted);
  letter-spacing: 0.1em;
  margin: 0;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-card);
  border: 1px solid var(--gold-dim);
  padding: var(--space-lg);
  position: relative;
}

.header-section::before {
  content: '';
  position: absolute;
  top: 4px;
  left: 4px;
  right: 4px;
  bottom: 4px;
  border: 1px solid var(--gold-dim);
  pointer-events: none;
  opacity: 0.3;
}

.header-info {
  flex: 1;
}

.strategy-count {
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 700;
  color: var(--gold-primary);
  margin: 0 0 var(--space-xs) 0;
}

.header-desc {
  font-family: var(--font-body);
  font-size: 0.875rem;
  color: var(--silver-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.create-btn {
  min-width: 200px;
}

.strategy-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: var(--space-lg);
}

.pagination-section {
  display: flex;
  justify-content: center;
  margin-top: var(--space-xl);
  padding: var(--space-lg);
  background: var(--bg-card);
  border: 1px solid var(--gold-dim);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.page-btn {
  padding: var(--space-sm) var(--space-lg);
  background: transparent;
  border: 1px solid var(--gold-dim);
  color: var(--silver-text);
  font-family: var(--font-display);
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: all var(--transition-base);
}

.page-btn:hover:not(:disabled) {
  border-color: var(--gold-primary);
  color: var(--gold-primary);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-family: var(--font-mono);
  font-size: 0.875rem;
  color: var(--silver-text);
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: var(--space-2xl);
  background: var(--bg-card);
  border: 1px solid var(--gold-dim);
}

.spinner {
  width: 48px;
  height: 48px;
  margin: 0 auto var(--space-lg);
  border: 3px solid var(--gold-dim);
  border-top-color: var(--gold-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-icon,
.empty-icon {
  font-size: 64px;
  margin-bottom: var(--space-lg);
}

.error-state h3,
.empty-state h3 {
  font-family: var(--font-display);
  font-size: 1.5rem;
  color: var(--silver-text);
  margin: 0 0 var(--space-md) 0;
}

.error-state p,
.empty-state p {
  font-family: var(--font-body);
  color: var(--silver-muted);
  margin: 0 0 var(--space-lg) 0;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--bg-card);
  border: 1px solid var(--gold-dim);
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-lg);
  border-bottom: 1px solid var(--gold-dim);
}

.modal-title {
  font-family: var(--font-display);
  font-size: 1.25rem;
  color: var(--gold-primary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--silver-muted);
  cursor: pointer;
  transition: color var(--transition-base);
}

.modal-close:hover {
  color: var(--gold-primary);
}

.modal-body {
  padding: var(--space-xl);
}

.form-group {
  margin-bottom: var(--space-lg);
}

.form-label {
  display: block;
  font-family: var(--font-display);
  font-size: 0.875rem;
  color: var(--gold-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-sm);
}

.select {
  position: relative;
}

.select select {
  width: 100%;
  padding: var(--space-md);
  background: var(--bg-primary);
  border: 1px solid var(--gold-dim);
  color: var(--silver-text);
  font-family: var(--font-mono);
  font-size: 0.875rem;
  cursor: pointer;
}

.select select:focus {
  outline: none;
  border-color: var(--gold-primary);
}

.parameters-container {
  width: 100%;
}

.parameter-row {
  display: flex;
  gap: var(--space-md);
  margin-bottom: var(--space-sm);
  align-items: center;
}

.parameter-row > * {
  flex: 1;
}

.add-param-btn {
  width: 100%;
  margin-top: var(--space-md);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-md);
  padding: var(--space-lg);
  border-top: 1px solid var(--gold-dim);
}

.backtest-content {
  text-align: center;
  padding: var(--space-xl);
}

.backtest-content h4 {
  font-family: var(--font-display);
  font-size: 1.25rem;
  color: var(--gold-primary);
  margin: 0 0 var(--space-md) 0;
}

.backtest-content p {
  font-family: var(--font-body);
  color: var(--silver-muted);
  margin: 0;
}

.mono {
  font-family: var(--font-mono);
}
</style>
