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
        <h2 class="strategy-count">{{ strategies.length }} STRATEGIES</h2>
        <p class="header-desc">MANAGE AND BACKTEST YOUR QUANTITATIVE TRADING STRATEGIES</p>
      </div>
      <Web3Button variant="primary" @click="showCreateDialog = true" size="lg" class="create-btn">
        <el-icon><Plus /></el-icon> CREATE STRATEGY
      </Web3Button>
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
    <div v-else-if="strategies.length === 0" class="empty-state grid-bg">
      <div class="empty-icon">📊</div>
      <h3>NO STRATEGIES</h3>
      <p>YOU HAVEN'T CREATED ANY QUANTITATIVE TRADING STRATEGIES YET</p>
      <Web3Button variant="primary" @click="showCreateDialog = true" class="create-btn">
        CREATE FIRST STRATEGY
      </Web3Button>
    </div>

    <!-- Strategy Grid -->
    <div v-else class="strategy-grid">
      <div
        v-for="strategy in strategies"
        :key="strategy.id"
        class="strategy-card web3-card hover-lift corner-border"
      >
        <div class="strategy-header">
          <h3 class="strategy-name">{{ strategy.name }}</h3>
          <el-tag :type="getStatusType(strategy.status) as any" size="small" class="web3-tag">
            {{ strategy.status || 'ACTIVE' }}
          </el-tag>
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
          <Web3Button variant="ghost" size="sm" @click="handleEdit(strategy)">
            <el-icon><Edit /></el-icon> EDIT
          </Web3Button>
          <Web3Button variant="outline" size="sm" @click="handleBacktest(strategy)">
            <el-icon><VideoPlay /></el-icon> BACKTEST
          </Web3Button>
          <Web3Button variant="ghost" size="sm" @click="handleDelete(strategy)" class="delete-btn">
            <el-icon><Delete /></el-icon> DELETE
          </Web3Button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingStrategy ? 'EDIT STRATEGY' : 'CREATE STRATEGY'"
      width="600px"
      class="web3-dialog"
    >
      <el-form :model="strategyForm" label-width="120px">
        <el-form-item label="STRATEGY NAME">
          <Web3Input v-model="strategyForm.name" placeholder="ENTER STRATEGY NAME" />
        </el-form-item>
        <el-form-item label="DESCRIPTION">
          <Web3Input
            v-model="strategyForm.description"
            type="textarea"
            :rows="3"
            placeholder="STRATEGY DESCRIPTION"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <Web3Button variant="ghost" @click="handleCancel">CANCEL</Web3Button>
        <Web3Button variant="primary" @click="handleSave" :loading="saving">
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
import { ref } from 'vue'
import { useStrategy } from '@/composables/useStrategy'
import { Web3Button, Web3Card, Web3Input } from '@/components/web3'
import { Plus, Edit, Delete, VideoPlay } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { Strategy } from '@/api/types/strategy'
import type { CreateStrategyRequest, UpdateStrategyRequest } from '@/api/types/strategy'

const { strategies, loading, error, fetchStrategies, createStrategy, updateStrategy, deleteStrategy } = useStrategy()

const showCreateDialog = ref(false)
const editingStrategy = ref<Strategy | null>(null)
const backtestingStrategy = ref<Strategy | null>(null)
const showBacktestDialog = ref(false)
const saving = ref(false)

const strategyForm = ref({
  name: '',
  description: ''
})

const handleEdit = (strategy: Strategy) => {
  editingStrategy.value = strategy
  strategyForm.value = {
    name: strategy.name,
    description: strategy.description || ''
  }
  showCreateDialog.value = true
}

const handleDelete = async (strategy: Strategy) => {
  const success = await deleteStrategy(strategy.id)
  if (success) {
    ElMessage.success(`STRATEGY "${strategy.name}" DELETED`)
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
  strategyForm.value = { name: '', description: '' }
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
    margin-bottom: 32px;
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
