<template>
  <div class="strategy-optimization page-enter">
    <ArtDecoCard class="optimization-card" variant="bordered">
      <template #header>
        <div class="header-row">
          <h2>策略优化</h2>
          <div class="header-meta">
            <span class="trace-id">REQ_ID: {{ traceRequestId }}</span>
            <span class="trace-id">PROCESS: {{ traceProcessTimeMs }} ms</span>
            <span :class="['source-badge', dataSource]">SOURCE: {{ dataSource.toUpperCase() }}</span>
          </div>
        </div>
      </template>

      <section v-if="selectedStrategyId" class="context-strip">
        <span class="context-label">当前策略上下文</span>
        <strong class="context-value">ID {{ selectedStrategyId }}</strong>
        <span class="context-meta" v-if="selectedSnapshot">
          {{ selectedSnapshot.status.toUpperCase() }} · 参数 {{ Object.keys(selectedSnapshot.parameters).length }} 项
        </span>
        <span class="context-meta" v-if="selectedSnapshot?.backtest">
          回测 {{ selectedSnapshot.backtest.status.toUpperCase() }}
        </span>
        <span class="context-meta" v-if="selectedSnapshot?.optimization">
          优化评分 {{ selectedSnapshot.optimization.score }}
        </span>
      </section>

      <div class="toolbar">
        <input
          v-model.trim="keyword"
          class="toolbar-input"
          type="text"
          placeholder="搜索策略名称 / 类型"
        />
        <select v-model="statusFilter" class="toolbar-select">
          <option value="all">全部状态</option>
          <option value="RUNNING">运行中</option>
          <option value="PAUSED">已暂停</option>
          <option value="STOPPED">已停止</option>
          <option value="ERROR">异常</option>
        </select>
        <button class="toolbar-button" :disabled="loading" @click="refreshOptimizationRows">刷新</button>
      </div>

      <p v-if="error" class="error-tip">{{ error }}</p>

      <div class="content-grid">
        <div class="table-wrap" v-loading="loading">
          <table class="optimization-table" v-if="displayedRows.length > 0">
            <thead>
              <tr>
                <th>策略</th>
                <th>状态</th>
                <th>参数项</th>
                <th>回测</th>
                <th>评分</th>
                <th>更新时间</th>
                <th>回写</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in displayedRows" :key="row.strategyId" :class="{ selected: row.strategyId === selectedStrategyId }">
                <td>
                  <div class="name-cell">{{ row.strategyName }}</div>
                  <div class="meta-cell">{{ row.strategyType }}</div>
                </td>
                <td>
                  <span :class="['status-chip', row.statusLabel.toLowerCase()]">{{ row.statusLabel }}</span>
                </td>
                <td>{{ row.parameterCount }}</td>
                <td>{{ row.backtestStatus }}</td>
                <td>{{ row.score }}</td>
                <td>{{ formatUpdatedTime(row.lastUpdated) }}</td>
                <td class="writeback-cell">
                  <button class="action-button" :disabled="loading" @click="writebackToManagement(row)">
                    管理
                  </button>
                  <button class="action-button" :disabled="loading" @click="writebackToParameters(row)">
                    参数
                  </button>
                  <button class="action-button" :disabled="loading" @click="writebackToBacktest(row)">
                    回测
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

          <p v-else-if="selectedStrategyMissing" class="empty-state">
            未找到策略 {{ selectedStrategyId }} 的优化候选，请返回策略管理页重试。
          </p>
          <p v-else class="empty-state">REAL 数据为空，暂无可优化策略。</p>
        </div>

        <aside class="contract-card artdeco-card">
          <h3>Optimization Contract</h3>
          <ul class="contract-list">
            <li>strategyId: {{ selectedStrategyId || 'N/A' }}</li>
            <li>status: {{ selectedSnapshot?.status?.toUpperCase() || 'N/A' }}</li>
            <li>parameters: {{ selectedSnapshot ? Object.keys(selectedSnapshot.parameters).length : 0 }}</li>
            <li>backtest: {{ selectedSnapshot?.backtest?.status?.toUpperCase() || 'N/A' }}</li>
            <li>optimization: {{ selectedSnapshot?.optimization?.score ?? 'N/A' }}</li>
            <li>source: {{ dataSource.toUpperCase() }}</li>
          </ul>
          <h3>Writeback Points</h3>
          <ul class="contract-list">
            <li v-for="point in writebackPoints" :key="point.target">
              {{ point.label }}: {{ point.description }}
            </li>
          </ul>
        </aside>
      </div>
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { strategyApi } from '@/api'
import type { StrategyConfig } from '@/api/types/common'
import { ArtDecoCard } from '@/components/artdeco'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import type { StrategySnapshot } from '@/composables/strategy/useStrategyCrossTabContext'
import { useStrategyCrossTabContext } from '@/composables/strategy/useStrategyCrossTabContext'
import { createMockStrategyManagementList } from '@/mock/strategyTabsMock'
import {
  buildQuickBacktestRoute,
  buildStrategyCrossTabRoute,
  extractStrategyIdFromQuery
} from './strategyCrossTabNavigation'
import {
  buildOptimizationRows,
  createMockOptimizationRows,
  type StrategyOptimizationRow,
  type OptimizationDataSource,
  type OptimizationStatusLabel
} from './strategyOptimizationViewModel'
import {
  OPTIMIZATION_WRITEBACK_POINTS,
  createOptimizationWritebackPayload
} from './strategyOptimizationWriteback'

type StatusFilter = 'all' | OptimizationStatusLabel

const route = useRoute()
const router = useRouter()
const { loading, error, lastRequestId, lastProcessTime, exec } = useArtDecoApi()
const {
  snapshots,
  getSnapshot,
  setActiveStrategy,
  setParametersSnapshot,
  setOptimizationSnapshot
} = useStrategyCrossTabContext()
const keyword = ref('')
const statusFilter = ref<StatusFilter>('all')
const strategyRecords = ref<StrategyConfig[]>([])
const optimizationRows = ref<StrategyOptimizationRow[]>([])
const dataSource = ref<OptimizationDataSource>('real')

const selectedStrategyId = computed(() => extractStrategyIdFromQuery(route.query as Record<string, unknown>))
const selectedSnapshot = computed(() => {
  if (!selectedStrategyId.value) {
    return null
  }
  return getSnapshot(selectedStrategyId.value)
})

const traceRequestId = computed(() => (lastRequestId.value.trim().length > 0 ? lastRequestId.value : 'N/A'))
const traceProcessTimeMs = computed(() => normalizeProcessTime(lastProcessTime.value))
const writebackPoints = OPTIMIZATION_WRITEBACK_POINTS

const filteredRows = computed(() => {
  const searchKeyword = keyword.value.trim().toLowerCase()
  return optimizationRows.value.filter((row) => {
    const matchedStatus = statusFilter.value === 'all' || row.statusLabel === statusFilter.value
    const matchedKeyword =
      searchKeyword.length === 0 ||
      row.strategyName.toLowerCase().includes(searchKeyword) ||
      row.strategyType.toLowerCase().includes(searchKeyword)
    return matchedStatus && matchedKeyword
  })
})

const displayedRows = computed(() => {
  if (!selectedStrategyId.value) {
    return filteredRows.value
  }
  return filteredRows.value.filter((row) => row.strategyId === selectedStrategyId.value)
})

const selectedStrategyMissing = computed(() => {
  if (!selectedStrategyId.value) {
    return false
  }
  return optimizationRows.value.every((row) => row.strategyId !== selectedStrategyId.value)
})

function normalizeProcessTime(rawValue: string): string {
  const value = rawValue.trim().toLowerCase()
  if (!value) {
    return 'N/A'
  }

  const numericValue = Number.parseFloat(value)
  if (!Number.isFinite(numericValue)) {
    return 'N/A'
  }

  if (value.endsWith('ms')) {
    return numericValue.toFixed(2)
  }
  if (value.endsWith('s')) {
    return (numericValue * 1000).toFixed(2)
  }
  return numericValue.toFixed(2)
}

function rebuildRowsFromContext(source: OptimizationDataSource = dataSource.value) {
  if (strategyRecords.value.length === 0) {
    optimizationRows.value = []
    return
  }

  optimizationRows.value = buildOptimizationRows(
    strategyRecords.value,
    snapshots.value as Record<string, StrategySnapshot>,
    source
  )
}

function extractStrategiesFromPayload(payload: unknown): StrategyConfig[] | null {
  if (Array.isArray(payload)) {
    return payload as StrategyConfig[]
  }

  if (payload && typeof payload === 'object') {
    const candidate = payload as Record<string, unknown>
    const collections = [candidate.strategies, candidate.items, candidate.data, candidate.records]
    for (const collection of collections) {
      if (Array.isArray(collection)) {
        return collection as StrategyConfig[]
      }
    }
  }

  return null
}

function applyMockFallback() {
  strategyRecords.value = createMockStrategyManagementList()
  dataSource.value = 'mock'
  rebuildRowsFromContext('mock')
  if (optimizationRows.value.length === 0) {
    optimizationRows.value = createMockOptimizationRows()
  }
}

async function refreshOptimizationRows() {
  const payload = await exec(() => strategyApi.getStrategies({}), {
    silent: true,
    errorMsg: '获取策略优化数据失败，当前显示空结果'
  })

  if (!payload) {
    applyMockFallback()
    return
  }

  const realStrategies = extractStrategiesFromPayload(payload)
  if (realStrategies === null) {
    applyMockFallback()
    return
  }

  strategyRecords.value = realStrategies
  dataSource.value = 'real'

  if (realStrategies.length === 0) {
    optimizationRows.value = []
    return
  }

  rebuildRowsFromContext()
}

function formatUpdatedTime(rawTime: string): string {
  if (!rawTime || rawTime === '-') {
    return '-'
  }

  const date = new Date(rawTime)
  if (Number.isNaN(date.getTime())) {
    return rawTime
  }

  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function applyOptimizationWriteback(row: StrategyOptimizationRow) {
  const payload = createOptimizationWritebackPayload({
    strategyId: row.strategyId,
    score: row.score,
    recommendedParameters: row.recommendedParameters
  })

  setActiveStrategy(row.strategyId)
  setParametersSnapshot(row.strategyId, payload.recommendedParameters)
  setOptimizationSnapshot(row.strategyId, {
    score: payload.score,
    recommendedParameters: payload.recommendedParameters,
    writebackTargets: payload.writebackTargets,
    updatedAt: payload.updatedAt
  })
}

async function writebackToManagement(row: StrategyOptimizationRow) {
  applyOptimizationWriteback(row)
  await router.push({
    name: 'strategy-repo',
    query: {
      strategyId: row.strategyId
    }
  })
  ElMessage.success(`优化结果已回写至策略管理：${row.strategyName}`)
}

async function writebackToParameters(row: StrategyOptimizationRow) {
  applyOptimizationWriteback(row)
  const routeLocation = buildStrategyCrossTabRoute('parameters', row.strategyId)
  if (routeLocation) {
    await router.push(routeLocation)
  }
  ElMessage.success(`优化参数已回写并同步到参数页：${row.strategyName}`)
}

async function writebackToBacktest(row: StrategyOptimizationRow) {
  applyOptimizationWriteback(row)
  const routeLocation = buildQuickBacktestRoute(row.strategyId)
  if (routeLocation) {
    await router.push(routeLocation)
  }
  ElMessage.success(`优化上下文已回写并跳转回测：${row.strategyName}`)
}

onMounted(() => {
  setActiveStrategy(selectedStrategyId.value)
  void refreshOptimizationRows()
})

watch(
  selectedStrategyId,
  (value) => {
    setActiveStrategy(value)
  },
  { immediate: true }
)

watch(
  snapshots,
  () => {
    rebuildRowsFromContext()
  },
  { deep: true }
)
</script>

<style scoped lang="scss">
@import './styles/ArtDecoStrategyOptimization';
</style>
