<template>
  <div class="web3-strategy-list">
    <!-- Page Header with Gradient Text -->
    <div class="page-header">
      <h1 class="text-4xl font-heading font-semibold">
        <span class="bg-gradient-to-r from-[#F7931A] to-[#FFD600] bg-clip-text text-transparent">
          STRATEGY MANAGEMENT
        </span>
      </h1>
      <p class="subtitle">QUANTITATIVE TRADING STRATEGIES | BACKTESTING | PERFORMANCE ANALYTICS</p>
    </div>

    <!-- Header Actions -->
    <div class="header-section">
      <div class="header-info">
        <h2 class="strategy-count">{{ filteredStrategies.length }} STRATEGIES</h2>
        <p class="header-desc">MANAGE AND BACKTEST YOUR QUANTITATIVE TRADING STRATEGIES</p>
      </div>
      <Web3Button variant="solid" @click="showCreateDialog = true" size="lg" class="create-btn">
        <el-icon><Plus /></el-icon> CREATE STRATEGY
      </Web3Button>
    </div>

    <!-- Task 2.2.2: Search, Filter, and Pagination -->
    <div class="filters-section">
      <el-input
        v-model="searchQuery"
        placeholder="SEARCH STRATEGIES..."
        prefix-icon="Search"
        clearable
        class="search-input"
      />
      <el-select
        v-model="filterType"
        placeholder="FILTER BY TYPE"
        clearable
        class="filter-select"
      >
        <el-option label="ALL TYPES" value="" />
        <el-option label="TREND FOLLOWING" value="trend_following" />
        <el-option label="MEAN REVERSION" value="mean_reversion" />
        <el-option label="MOMENTUM" value="momentum" />
      </el-select>
      <el-select
        v-model="filterStatus"
        placeholder="FILTER BY STATUS"
        clearable
        class="filter-select"
      >
        <el-option label="ALL STATUSES" value="" />
        <el-option label="ACTIVE" value="active" />
        <el-option label="INACTIVE" value="inactive" />
        <el-option label="TESTING" value="testing" />
      </el-select>
    </div>

    <!-- Loading State -->
    <div v-if="loading && strategies.length === 0" class="loading-state grid-bg">
      <div class="spinner"></div>
      <p>LOADING STRATEGIES...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state grid-bg">
      <div class="error-icon">⚠️</div>
      <h3>LOADING FAILED</h3>
      <p>{{ error }}</p>
      <Web3Button variant="outline" @click="fetchStrategies" class="retry-btn">RETRY</Web3Button>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredStrategies.length === 0" class="empty-state grid-bg">
      <div class="empty-icon">📊</div>
      <h3>NO STRATEGIES FOUND</h3>
      <p>TRY ADJUSTING YOUR SEARCH OR FILTER CRITERIA</p>
      <Web3Button variant="outline" @click="clearFilters" class="clear-btn">
        CLEAR FILTERS
      </Web3Button>
    </div>

    <!-- Strategy Grid -->
    <div v-else class="strategy-grid">
      <div
        v-for="strategy in paginatedStrategies"
        :key="strategy.id"
        class="strategy-card web3-card hover-lift corner-border"
      >
        <div class="strategy-header">
          <h3 class="strategy-name">{{ strategy.name }}</h3>
          <div class="tags">
            <!-- Task 2.2.3: Display strategy type -->
            <el-tag :type="getTypeColor(strategy.type)" size="small" class="web3-tag type-tag">
              {{ formatType(strategy.type) }}
            </el-tag>
            <el-tag :type="getStatusType(strategy.status) as any" size="small" class="web3-tag">
              {{ strategy.status || 'ACTIVE' }}
            </el-tag>
          </div>
        </div>

        <div class="strategy-body">
          <p class="strategy-description">{{ strategy.description || 'No description available' }}</p>

          <div class="strategy-stats">
            <div class="stat-item">
              <span class="stat-label">RETURN</span>
              <span class="stat-value" :class="getReturnClass((strategy as any).return)">
                {{ formatPercent((strategy as any).return) }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">SHARPE</span>
              <span class="stat-value blue-glow">{{ (strategy as any).sharpe_ratio?.toFixed(2) || '-' }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">WIN RATE</span>
              <span class="stat-value green-glow">{{ formatPercent((strategy as any).win_rate) }}</span>
            </div>
          </div>
        </div>

        <div class="strategy-actions">
          <Web3Button variant="outline" size="sm" @click="handleEdit(strategy)">
            <el-icon><Edit /></el-icon> EDIT
          </Web3Button>
          <Web3Button variant="outline" size="sm" @click="handleBacktest(strategy)">
            <el-icon><VideoPlay /></el-icon> BACKTEST
          </Web3Button>
          <Web3Button variant="outline" size="sm" @click="handleDelete(strategy)" class="delete-btn">
            <el-icon><Delete /></el-icon> DELETE
          </Web3Button>
        </div>
      </div>
    </div>

    <!-- Task 2.2.2: Pagination -->
    <div v-if="filteredStrategies.length > 0" class="pagination-section">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 48]"
        :total="filteredStrategies.length"
        layout="total, sizes, prev, pager, next, jumper"
        background
        class="web3-pagination"
      />
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingStrategy ? 'EDIT STRATEGY' : 'CREATE STRATEGY'"
      width="700px"
      class="web3-dialog"
    >
      <el-form :model="strategyForm" label-width="140px">
        <el-form-item label="STRATEGY NAME" required>
          <Web3Input v-model="strategyForm.name" placeholder="ENTER STRATEGY NAME" />
        </el-form-item>

        <!-- Task 2.2.3: Strategy Type Field -->
        <el-form-item label="STRATEGY TYPE" required>
          <el-select v-model="strategyForm.type" placeholder="SELECT STRATEGY TYPE" style="width: 100%">
            <el-option label="TREND FOLLOWING" value="trend_following" />
            <el-option label="MEAN REVERSION" value="mean_reversion" />
            <el-option label="MOMENTUM" value="momentum" />
          </el-select>
        </el-form-item>

        <el-form-item label="DESCRIPTION">
          <Web3Input
            v-model="strategyForm.description"
            type="textarea"
            :rows="3"
            placeholder="STRATEGY DESCRIPTION"
          />
        </el-form-item>

        <!-- Task 2.2.3: Parameters Field -->
        <el-form-item label="PARAMETERS">
          <div class="parameters-container">
            <div
              v-for="(param, index) in strategyForm.parameters"
              :key="index"
              class="parameter-row"
            >
              <el-input
                v-model="param.key"
                placeholder="PARAMETER NAME"
                style="flex: 1"
              />
              <el-input
                v-model="param.value"
                placeholder="VALUE"
                style="flex: 1"
              />
              <Web3Button
                variant="outline"
                size="sm"
                @click="removeParameter(index)"
                class="remove-btn"
              >
                <el-icon><Delete /></el-icon>
              </Web3Button>
            </div>
            <Web3Button
              variant="outline"
              size="sm"
              @click="addParameter"
              class="add-param-btn"
            >
              <el-icon><Plus /></el-icon> ADD PARAMETER
            </Web3Button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <Web3Button variant="outline" @click="handleCancel">CANCEL</Web3Button>
        <Web3Button variant="solid" @click="handleSave" :loading="saving">
          {{ editingStrategy ? 'UPDATE' : 'CREATE' }}
        </Web3Button>
      </template>
    </el-dialog>

    <!-- Backtest Panel -->
    <el-dialog
      v-model="showBacktestDialog"
      title="BACKTEST STRATEGY"
      width="900px"
      class="web3-dialog"
    >
      <div v-if="backtestingStrategy" class="backtest-content">
        <h4>{{ backtestingStrategy.name }}</h4>
        <p>BACKTEST FUNCTIONALITY COMING SOON</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useStrategy } from '@/composables/useStrategy'
import { ArtDecoButton as Web3Button, ArtDecoCard as Web3Card, ArtDecoInput as Web3Input } from '@/components/artdeco'
import { Plus, Edit, Delete, VideoPlay } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Strategy } from '@/api/types/strategy'
import type { CreateStrategyRequest, UpdateStrategyRequest } from '@/api/types/strategy'

const { strategies, loading, error, fetchStrategies, createStrategy, updateStrategy, deleteStrategy } = useStrategy()

const showCreateDialog = ref(false)
const editingStrategy = ref<Strategy | null>(null)
const backtestingStrategy = ref<Strategy | null>(null)
const showBacktestDialog = ref(false)
const saving = ref(false)

// Task 2.2.2: Search, Filter, and Pagination State
const searchQuery = ref('')
const filterType = ref('')
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(12)

const strategyForm = ref({
  name: '',
  description: '',
  type: 'trend_following',      // Task 2.2.3: Add type field
  parameters: []                 // Task 2.2.3: Add parameters array
})

// Task 2.2.3: Parameter management functions
const addParameter = () => {
  strategyForm.value.parameters.push({ key: '', value: '' })
}

const removeParameter = (index: number) => {
  strategyForm.value.parameters.splice(index, 1)
}

// Task 2.2.2: Computed properties for filtering and pagination
const filteredStrategies = computed(() => {
  let result = strategies.value

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(strategy =>
      strategy.name.toLowerCase().includes(query) ||
      (strategy.description && strategy.description.toLowerCase().includes(query))
    )
  }

  // Filter by type
  if (filterType.value) {
    result = result.filter(strategy => strategy.type === filterType.value)
  }

  // Filter by status
  if (filterStatus.value) {
    result = result.filter(strategy => strategy.status === filterStatus.value)
  }

  return result
})

const paginatedStrategies = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredStrategies.value.slice(start, end)
})

const clearFilters = () => {
  searchQuery.value = ''
  filterType.value = ''
  filterStatus.value = ''
  currentPage.value = 1
}

const handleEdit = (strategy: Strategy) => {
  editingStrategy.value = strategy
  strategyForm.value = {
    name: strategy.name,
    description: strategy.description || '',
    type: strategy.type || 'trend_following',      // Task 2.2.3: Include type
    parameters: strategy.parameters ?             // Task 2.2.3: Include parameters
      Object.entries(strategy.parameters).map(([key, value]) => ({ key, value })) :
      []
  }
  showCreateDialog.value = true
}

const handleDelete = async (strategy: Strategy) => {
  // Task 2.2.4: Add confirmation dialog before deletion
  try {
    await ElMessageBox.confirm(
      `ARE YOU SURE YOU WANT TO DELETE STRATEGY "${strategy.name}"? THIS ACTION CANNOT BE UNDONE.`,
      'CONFIRM DELETION',
      {
        confirmButtonText: 'DELETE',
        cancelButtonText: 'CANCEL',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    const success = await deleteStrategy(strategy.id)
    if (success) {
      ElMessage.success(`STRATEGY "${strategy.name}" DELETED`)
    }
  } catch (error) {
    // User cancelled deletion
    if (error !== 'cancel') {
      console.error('Delete confirmation error:', error)
    }
  }
}

const handleBacktest = (strategy: Strategy) => {
  backtestingStrategy.value = strategy
  showBacktestDialog.value = true
}

const handleSave = async () => {
  if (!strategyForm.value.name) {
    ElMessage.warning('PLEASE ENTER STRATEGY NAME')
    return
  }

  saving.value = true
  try {
    if (editingStrategy.value) {
      const success = await updateStrategy(editingStrategy.value.id, strategyForm.value)
      if (success) {
        ElMessage.success(`STRATEGY "${strategyForm.value.name}" UPDATED`)
        editingStrategy.value = null
        showCreateDialog.value = false
      }
    } else {
      const success = await createStrategy(strategyForm.value as CreateStrategyRequest)
      if (success) {
        ElMessage.success('NEW STRATEGY CREATED')
        showCreateDialog.value = false
      }
    }
  } finally {
    saving.value = false
  }
}

const handleCancel = () => {
  editingStrategy.value = null
  showCreateDialog.value = false
  strategyForm.value = {
    name: '',
    description: '',
    type: 'trend_following',      // Task 2.2.3: Reset type
    parameters: []                 // Task 2.2.3: Reset parameters
  }
}

const formatPercent = (value: number | undefined): string => {
  if (value === undefined) return '-'
  return `${(value * 100).toFixed(2)}%`
}

const getReturnClass = (value: number | undefined): string => {
  if (!value) return ''
  return value > 0 ? 'profit-up' : value < 0 ? 'profit-down' : ''
}

const getStatusType = (status: string | undefined): string => {
  if (status === 'active') return 'success'
  if (status === 'inactive') return 'info'
  return 'warning'
}

// Task 2.2.3: Type formatting functions
const formatType = (type: string | undefined): string => {
  const typeMap: Record<string, string> = {
    'trend_following': 'TREND',
    'mean_reversion': 'MEAN REV',
    'momentum': 'MOMENTUM'
  }
  return typeMap[type || ''] || type || 'UNKNOWN'
}

const getTypeColor = (type: string | undefined): 'primary' | 'success' | 'warning' | 'danger' | 'info' => {
  const colorMap: Record<string, 'primary' | 'success' | 'warning' | 'danger' | 'info'> = {
    'trend_following': 'primary',
    'mean_reversion': 'success',
    'momentum': 'warning'
  }
  return colorMap[type || ''] || 'info'
}
</script>

<style scoped lang="scss">
.web3-strategy-list {
  min-height: 100vh;
  padding: 24px;
  background: #030304;

  .grid-bg {
    position: relative;
    background-image:
      linear-gradient(rgba(247, 147, 26, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(247, 147, 26, 0.03) 1px, transparent 1px);
    background-size: 20px 20px;
  }

  .page-header {
    margin-bottom: 32px;
    text-align: center;

    .subtitle {
      margin-top: 8px;
      font-size: 14px;
      color: #94A3B8;
      font-family: 'JetBrains Mono', monospace;
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }
  }

  .header-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    flex-wrap: wrap;
    gap: 16px;

    .header-info {
      .strategy-count {
        font-size: 28px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        color: #F7931A;
        margin: 0 0 4px 0;
      }

      .header-desc {
        margin: 0;
        font-size: 14px;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }
    }

    .create-btn {
      min-width: 180px;
    }
  }

  // Task 2.2.2: Filters Section Styles
  .filters-section {
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
    flex-wrap: wrap;
    align-items: center;

    .search-input {
      flex: 1;
      min-width: 250px;
      max-width: 400px;

      :deep(.el-input__wrapper) {
        background: rgba(15, 17, 21, 0.8);
        border: 1px solid rgba(30, 41, 59, 0.5);
        box-shadow: none;

        &:hover {
          border-color: rgba(247, 147, 26, 0.3);
        }

        &.is-focus {
          border-color: #F7931A;
          box-shadow: 0 0 0 2px rgba(247, 147, 26, 0.1);
        }
      }

      :deep(.el-input__inner) {
        color: #E5E7EB;
        font-family: 'JetBrains Mono', monospace;

        &::placeholder {
          color: #64748B;
        }
      }
    }

    .filter-select {
      width: 180px;

      :deep(.el-select__wrapper) {
        background: rgba(15, 17, 21, 0.8);
        border: 1px solid rgba(30, 41, 59, 0.5);
        box-shadow: none;

        &:hover {
          border-color: rgba(247, 147, 26, 0.3);
        }

        &.is-focus {
          border-color: #F7931A;
          box-shadow: 0 0 0 2px rgba(247, 147, 26, 0.1);
        }
      }

      :deep(.el-select__selected-item) {
        color: #E5E7EB;
        font-family: 'JetBrains Mono', monospace;
      }
    }
  }

  // Task 2.2.2: Pagination Styles
  .pagination-section {
    display: flex;
    justify-content: center;
    margin-top: 32px;
    padding: 24px;
    background: rgba(15, 17, 21, 0.6);
    border: 1px solid rgba(30, 41, 59, 0.5);
    border-radius: 12px;

    .web3-pagination {
      :deep(.el-pagination__total) {
        color: #94A3B8;
        font-family: 'JetBrains Mono', monospace;
      }

      :deep(.el-pager li) {
        background: rgba(15, 17, 21, 0.8);
        border: 1px solid rgba(30, 41, 59, 0.5);
        color: #E5E7EB;
        font-family: 'JetBrains Mono', monospace;
        margin: 0 2px;
        border-radius: 6px;

        &:hover {
          border-color: rgba(247, 147, 26, 0.5);
          color: #F7931A;
        }

        &.is-active {
          background: #F7931A;
          border-color: #F7931A;
          color: #030304;
        }
      }

      :deep(.btn-prev),
      :deep(.btn-next) {
        background: rgba(15, 17, 21, 0.8);
        border: 1px solid rgba(30, 41, 59, 0.5);
        color: #E5E7EB;
        border-radius: 6px;

        &:hover:not(:disabled) {
          border-color: rgba(247, 147, 26, 0.5);
          color: #F7931A;
        }

        &:disabled {
          opacity: 0.5;
        }
      }

      :deep(.el-pagination__sizes) {
        .el-select__wrapper {
          background: rgba(15, 17, 21, 0.8);
          border: 1px solid rgba(30, 41, 59, 0.5);

          &:hover {
            border-color: rgba(247, 147, 26, 0.3);
          }
        }

        .el-select__selected-item {
          color: #E5E7EB;
          font-family: 'JetBrains Mono', monospace;
        }
      }
    }
  }

  .clear-btn {
    min-width: 140px;
  }

  // Task 2.2.3: Parameters Section Styles
  .parameters-container {
    width: 100%;

    .parameter-row {
      display: flex;
      gap: 8px;
      margin-bottom: 8px;
      align-items: center;

      .remove-btn {
        flex-shrink: 0;
      }
    }

    .add-param-btn {
      width: 100%;
      margin-top: 8px;

      :deep(.el-button__content) {
        gap: 6px;
      }
    }
  }

  .loading-state,
  .error-state,
  .empty-state {
    text-align: center;
    padding: 80px 20px;
    border-radius: 12px;
    border: 1px solid rgba(30, 41, 59, 0.5);

    .spinner {
      width: 48px;
      height: 48px;
      margin: 0 auto 20px;
      border: 3px solid rgba(30, 41, 59, 0.5);
      border-top-color: #F7931A;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    .error-icon,
    .empty-icon {
      font-size: 64px;
      margin-bottom: 16px;
    }

    h3 {
      font-size: 20px;
      color: #E5E7EB;
      margin: 0 0 8px 0;
    }

    p {
      color: #94A3B8;
      margin: 0 0 24px 0;
    }

    .retry-btn {
      min-width: 120px;
    }
  }

  .strategy-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 20px;

    .strategy-card {
      background: rgba(15, 17, 21, 0.8);
      border: 1px solid rgba(30, 41, 59, 0.5);
      border-radius: 12px;
      padding: 20px;
      transition: all 0.3s ease;

      &.hover-lift:hover {
        transform: translateY(-4px);
        border-color: rgba(247, 147, 26, 0.5);
        box-shadow: 0 0 30px -10px rgba(247, 147, 26, 0.2);
      }

      &.corner-border {
        position: relative;

        &::before,
        &::after {
          content: '';
          position: absolute;
          width: 12px;
          height: 12px;
          border-color: #F7931A;
          border-style: solid;
        }

        &::before {
          top: -1px;
          left: -1px;
          border-width: 2px 0 0 2px;
          border-radius: 6px 0 0 0;
        }

        &::after {
          bottom: -1px;
          right: -1px;
          border-width: 0 2px 2px 0;
          border-radius: 0 0 6px 0;
        }
      }

      .strategy-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;

        .strategy-name {
          font-size: 18px;
          font-weight: 600;
          font-family: 'JetBrains Mono', monospace;
          color: #F7931A;
          margin: 0;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        // Task 2.2.3: Tags container
        .tags {
          display: flex;
          gap: 6px;
          align-items: center;

          .type-tag {
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            font-weight: 700;
          }
        }
      }

      .strategy-body {
        margin-bottom: 20px;

        .strategy-description {
          font-size: 14px;
          color: #94A3B8;
          margin: 0 0 16px 0;
          line-height: 1.6;
          min-height: 40px;
        }

        .strategy-stats {
          display: flex;
          gap: 16px;
          padding: 16px;
          background: rgba(30, 41, 59, 0.3);
          border-radius: 8px;

          .stat-item {
            flex: 1;
            text-align: center;

            .stat-label {
              display: block;
              font-size: 11px;
              color: #64748B;
              text-transform: uppercase;
              letter-spacing: 0.05em;
              margin-bottom: 4px;
            }

            .stat-value {
              font-size: 16px;
              font-weight: 700;
              font-family: 'JetBrains Mono', monospace;

              &.orange-glow { color: #F7931A; }
              &.blue-glow { color: #3B82F6; }
              &.green-glow { color: #22C55E; }
              &.profit-up { color: #F7931A; }
              &.profit-down { color: #22C55E; }
            }
          }
        }
      }

      .strategy-actions {
        display: flex;
        gap: 8px;
        padding-top: 16px;
        border-top: 1px solid rgba(30, 41, 59, 0.5);

        .delete-btn:hover {
          color: #EF4444;
          border-color: rgba(239, 68, 68, 0.3);
        }
      }
    }
  }

  .web3-tag {
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
    font-size: 11px;
    border: 1px solid rgba(247, 147, 26, 0.3);
    background: rgba(247, 147, 26, 0.1);
  }

  .profit-up {
    color: #F7931A;
  }

  .profit-down {
    color: #22C55E;
  }
}
</style>
