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
        v-for="(strategy, _idx) in paginatedStrategies"
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
import { ref, computed , onUnmounted } from 'vue'
import { ElInput } from 'element-plus'

interface Strategy {
  id: string
  name: string
  description?: string
  type: string
  status: string
  parameters?: Record<string, unknown>
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

const _strategyFilters = [
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

const _strategyQuickFilters = [
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

const _handleFilterChange = (filters: Record<string, unknown>) => {
  searchQuery.value = filters.search || ''
  filterType.value = filters.type || ''
  filterStatus.value = filters.status || ''
  currentPage.value = 1
}

const _mapStrategyToCard = (strategy: Strategy) => ({
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
const _handleStart = (strategy: Strategy) => console.log('Start:', strategy)
const _handleStop = (strategy: Strategy) => console.log('Stop:', strategy)
const _handleEdit = (strategy: Strategy) => {
  editingStrategy.value = strategy
  strategyForm.value = {
    name: strategy.name,
    description: strategy.description || '',
    type: strategy.type,
    parameters: strategy.parameters ? Object.entries(strategy.parameters).map(([k, v]) => ({ key: k, value: String(v) })) : []
  }
  showCreateDialog.value = true
}

const _handleDelete = async (strategy: Strategy) => {
  strategies.value = strategies.value.filter(s => s.id !== strategy.id)
}

const _handleBacktest = (strategy: Strategy) => {
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

// Auto-generated: cleanup timers to prevent memory leaks
const _timer_1: ReturnType<typeof setTimeout> | null = null
onUnmounted(() => {
  if (_timer_1) clearTimeout(_timer_1)
})
</script>

<style scoped>
@import "./styles/StrategyManagement.css";
</style>
