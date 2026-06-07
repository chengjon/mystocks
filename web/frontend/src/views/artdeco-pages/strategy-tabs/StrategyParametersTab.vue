<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArtDecoBadge, ArtDecoButton, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { useStrategyCrossTabContext } from '@/composables/strategy/useStrategyCrossTabContext'
import { strategyApi } from '@/api'
import type { StrategyConfig } from '@/api/types/common'
import { buildStrategyCrossTabRoute, extractStrategyIdFromQuery, type StrategyCrossTabTarget } from './strategyCrossTabNavigation'
import {
  extractStrategyConfigs,
  normalizeProcessTimeMs
} from './strategyParametersData'

type ParametersDataSource = 'real'
type StrategyParameterValue = NonNullable<NonNullable<StrategyConfig['parameters']>[number]>['value']

const { loading, error, lastRequestId, lastProcessTime, exec } = useArtDecoApi()
const strategies = ref<StrategyConfig[]>([])
const dataSource = ref<ParametersDataSource>('real')
const fallbackReason = ref('')
const route = useRoute()
const router = useRouter()
const { getSnapshot, setActiveStrategy } = useStrategyCrossTabContext()
const hasLoaded = ref(false)
const hasVerifiedStrategySnapshot = ref(false)
const verifiedStrategyIds = ref<Set<string>>(new Set())
const lastVerifiedRequestId = ref('')
const lastVerifiedProcessTime = ref('')
const staleError = ref('')

const selectedStrategyId = computed(() => extractStrategyIdFromQuery(route.query as Record<string, unknown>))
const selectedStrategySnapshot = computed(() => {
  if (!selectedStrategyId.value) {
    return null
  }
  return getSnapshot(selectedStrategyId.value)
})

const traceRequestId = computed(() => {
  if (hasCurrentVerifiedStrategySnapshot.value) {
    return lastVerifiedRequestId.value || 'N/A'
  }

  if (selectedStrategyId.value && hasLoaded.value) {
    return loading.value && !hasLoaded.value ? '--' : 'N/A'
  }

  const requestId = lastRequestId.value.trim()
  if (!requestId.length) {
    return loading.value && !hasLoaded.value ? '--' : 'N/A'
  }

  return effectiveError.value ? 'N/A' : requestId
})
const traceProcessTimeMs = computed(() => {
  if (hasCurrentVerifiedStrategySnapshot.value) {
    return normalizeProcessTimeMs(lastVerifiedProcessTime.value)
  }

  if (selectedStrategyId.value && hasLoaded.value) {
    return loading.value && !hasLoaded.value ? '--' : 'N/A'
  }

  const rawProcessTime = lastProcessTime.value.trim()
  if (!rawProcessTime.length) {
    return loading.value && !hasLoaded.value ? '--' : 'N/A'
  }

  return effectiveError.value ? 'N/A' : normalizeProcessTimeMs(rawProcessTime)
})
const selectedStrategyLabel = computed(() => selectedStrategyId.value || 'ALL')
const visibleStrategyCount = computed(() => hydratedStrategies.value.length)
const parameterEntryCount = computed(() =>
  hydratedStrategies.value.reduce((sum, strategy) => sum + (strategy.parameters?.length || 0), 0)
)
const optimizationLinkedCount = computed(() =>
  hydratedStrategies.value.filter((strategy) => getOptimizationScore(strategy) !== null).length
)
const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  if (staleError.value) return '刷新异常'
  if (effectiveError.value) return '接口异常'
  return selectedStrategyId.value ? '参数上下文已绑定' : '策略参数在线'
})
const pageStatusType = computed(() => {
  if (staleError.value || effectiveError.value) return 'warning'
  return 'success'
})
const contentShellDescription = computed(() => {
  if (selectedStrategyId.value) {
    return `聚合策略 ${selectedStrategyId.value} 的参数快照、优化评分和当前运行状态，形成可追踪的参数工作台。`
  }
  return '浏览策略参数、优化评分和当前状态，作为策略管理与回测验证之间的参数中转面板。'
})

const displayedStrategies = computed(() => {
  if (!selectedStrategyId.value) {
    return strategies.value
  }

  return strategies.value.filter((strategy) => String(strategy.strategy_id ?? '') === selectedStrategyId.value)
})

const selectedStrategyMissing = computed(() => {
  return Boolean(selectedStrategyId.value) && displayedStrategies.value.length === 0
})

const hasCurrentVerifiedStrategySnapshot = computed(() => {
  if (!selectedStrategyId.value) {
    return hasVerifiedStrategySnapshot.value
  }

  return verifiedStrategyIds.value.has(selectedStrategyId.value)
})

const hydratedStrategies = computed(() => {
  return displayedStrategies.value.map((strategy) => {
    const strategyId = getStrategyId(strategy)
    const snapshot = getSnapshot(strategyId)
    if (!snapshot) {
      return strategy
    }

    return {
      ...strategy,
      status: mapSnapshotStatus(snapshot.status, strategy.status),
      parameters: toStrategyParameters(snapshot.parameters, strategy.parameters)
    }
  })
})

const effectiveError = computed(() => (!hasVerifiedStrategySnapshot.value ? (error.value || fallbackReason.value) : ''))
const headerError = computed(() => effectiveError.value)
const showInitialLoading = computed(() => loading.value && !hasLoaded.value)
const showErrorState = computed(() => !loading.value && hasLoaded.value && Boolean(headerError.value))
const showEmptyState = computed(() => !loading.value && hasLoaded.value && !headerError.value && strategies.value.length === 0)
const showStaleWarning = computed(() => !loading.value && staleError.value.length > 0 && strategies.value.length > 0)
const showSummaryPlaceholders = computed(() => !hasCurrentVerifiedStrategySnapshot.value)
const displayVisibleStrategyCount = computed(() => showSummaryPlaceholders.value ? '--' : `${visibleStrategyCount.value}`)
const displayParameterEntryCount = computed(() => showSummaryPlaceholders.value ? '--' : `${parameterEntryCount.value}`)
const displayOptimizationLinkedCount = computed(() => showSummaryPlaceholders.value ? '--' : `${optimizationLinkedCount.value}`)
const optimizationLinkedVariant = computed(() => showSummaryPlaceholders.value ? 'gold' : 'rise')

function markVerifiedStrategySnapshot(strategyIds: string[]) {
  hasVerifiedStrategySnapshot.value = true
  lastVerifiedRequestId.value = lastRequestId.value || lastVerifiedRequestId.value
  lastVerifiedProcessTime.value = lastProcessTime.value || lastVerifiedProcessTime.value
  verifiedStrategyIds.value = new Set(strategyIds)
}

function getStrategyId(strategy: StrategyConfig): string {
  return String(strategy.strategy_id ?? '')
}

function mapSnapshotStatus(snapshotStatus: string, fallback?: StrategyConfig['status']): StrategyConfig['status'] {
  if (snapshotStatus === 'running') return 'active'
  if (snapshotStatus === 'paused') return 'paused'
  if (snapshotStatus === 'stopped') return 'draft'
  if (snapshotStatus === 'error') return 'paused'
  return fallback
}

function toStrategyParameters(
  snapshotParameters: Record<string, unknown>,
  fallback?: StrategyConfig['parameters']
): StrategyConfig['parameters'] {
  const entries = Object.entries(snapshotParameters)
  if (!entries.length) {
    return fallback
  }

  return entries.map(([name, value]) => ({
    name,
    value: normalizeParameterValue(value),
    data_type: typeof value
  }))
}

function normalizeParameterValue(value: unknown): StrategyParameterValue {
  if (value === undefined) return undefined
  if (value === null) return null
  if (Array.isArray(value)) return value

  switch (typeof value) {
    case 'string':
    case 'number':
    case 'boolean':
      return value
    case 'object':
      return value as Record<string, unknown>
    default:
      return String(value)
  }
}

function getOptimizationScore(strategy: StrategyConfig): number | null {
  const strategyId = getStrategyId(strategy)
  if (!strategyId) {
    return null
  }

  const snapshot = getSnapshot(strategyId)
  return snapshot?.optimization?.score ?? null
}

function getStrategyStatusBadgeVariant(status?: StrategyConfig['status']): 'profit' | 'warning' | 'neutral' {
  if (status === 'active') return 'profit'
  if (status === 'paused') return 'warning'
  return 'neutral'
}

const fetchStrategies = async () => {
  staleError.value = ''
  const payload = await exec(() => strategyApi.getStrategies({}), {
    silent: true,
    errorMsg: '获取策略参数失败'
  })

  if (!payload) {
    hasLoaded.value = true
    if (hasVerifiedStrategySnapshot.value) {
      staleError.value = error.value || '获取策略参数失败'
      return
    }
    strategies.value = []
    dataSource.value = 'real'
    fallbackReason.value = error.value || '获取策略参数失败'
    return
  }

  const extracted = extractStrategyConfigs(payload)
  if (extracted === null) {
    hasLoaded.value = true
    if (hasVerifiedStrategySnapshot.value) {
      staleError.value = '策略参数数据格式异常'
      return
    }
    strategies.value = []
    dataSource.value = 'real'
    fallbackReason.value = '策略参数数据格式异常'
    return
  }

  strategies.value = extracted
  dataSource.value = 'real'
  fallbackReason.value = ''
  staleError.value = ''
  markVerifiedStrategySnapshot(extracted.map((strategy) => getStrategyId(strategy)))
  hasLoaded.value = true
}

function getStrategyCardDescription(strategy: StrategyConfig): string {
  return strategy.description || '暂无策略说明'
}

function getParameterDisplayValue(value: StrategyParameterValue): string {
  if (value === undefined || value === null || value === '') {
    return '--'
  }

  if (Array.isArray(value)) {
    return value.join(', ')
  }

  if (typeof value === 'object') {
    return JSON.stringify(value)
  }

  return String(value)
}

async function navigateToStrategyTab(target: StrategyCrossTabTarget, strategyId: string) {
  const routeLocation = buildStrategyCrossTabRoute(target, strategyId)
  if (!routeLocation) {
    return
  }

  setActiveStrategy(strategyId)
  await router.push(routeLocation)
}

onMounted(() => {
  void fetchStrategies()
})

watch(selectedStrategyId, (value) => {
  setActiveStrategy(value)
}, { immediate: true })
</script>

<template>
  <div class="strategy-parameters-tab page-enter">
    <section class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">parameter propagation desk</span>
          <div class="hero-meta">
            <span>REQ_ID: {{ traceRequestId }}</span>
            <span>PROCESS: {{ traceProcessTimeMs }} ms</span>
            <span>FOCUS: {{ selectedStrategyLabel }}</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="策略参数工作台"
        subtitle="承接策略仓库、优化写回和回测上下文的参数中转页"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" :loading="loading" @click="fetchStrategies">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新参数
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="可见策略" :value="displayVisibleStrategyCount" variant="gold" :show-change="false" />
      <ArtDecoStatCard label="参数总项" :value="displayParameterEntryCount" variant="gold" :show-change="false" />
      <ArtDecoStatCard
        label="优化联动"
        :value="displayOptimizationLinkedCount"
        :variant="optimizationLinkedVariant"
        :show-change="false"
      />
      <ArtDecoStatCard label="当前焦点" :value="selectedStrategyLabel" variant="gold" :show-change="false" />
    </section>

    <section class="content-shell artdeco-card-shell">
      <div class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">parameter context route</span>
          <h3 class="content-shell-title">参数快照与优化联动面板</h3>
          <p class="content-shell-subtitle">{{ contentShellDescription }}</p>
        </div>
        <div class="content-shell-meta">
          <span>SOURCE: {{ dataSource.toUpperCase() }}</span>
          <span v-if="selectedStrategySnapshot?.optimization">OPT_SCORE: {{ selectedStrategySnapshot.optimization.score }}</span>
        </div>
      </div>

      <div v-if="showInitialLoading" class="state-panel artdeco-card" role="status" aria-live="polite">
        <p>策略参数同步中</p>
        <span>正在拉取策略参数快照和优化联动上下文。</span>
      </div>

      <div v-else-if="showErrorState" class="state-panel artdeco-card" role="alert">
        <p>策略参数加载失败</p>
        <span>{{ headerError }}</span>
        <ArtDecoButton variant="outline" size="sm" @click="fetchStrategies">重试刷新</ArtDecoButton>
      </div>

      <div v-else-if="showEmptyState" class="state-panel artdeco-card" role="status" aria-live="polite">
        <p>暂无策略参数</p>
        <span>当前还没有可展示的策略配置，请先在策略仓库中创建策略。</span>
      </div>

      <template v-else>
        <div v-if="showStaleWarning" class="state-panel artdeco-card" role="status" aria-live="polite">
          <p>部分刷新失败</p>
          <span>{{ staleError }}，当前仍显示上次成功同步的参数快照。</span>
        </div>

        <div class="strategy-grid" v-loading="loading">
          <div
            v-for="strategy in hydratedStrategies"
            :key="getStrategyId(strategy)"
            class="artdeco-card strategy-card"
            :class="{ selected: getStrategyId(strategy) === selectedStrategyId }"
          >
            <div class="card-decoration"></div>
            <div class="card-content">
              <div class="strategy-info">
                <h3 class="strategy-name">{{ strategy.strategy_name }}</h3>
                <ArtDecoBadge
                  :text="strategy.status?.toUpperCase()"
                  :variant="getStrategyStatusBadgeVariant(strategy.status)"
                  size="sm"
                />
                <ArtDecoBadge
                  v-if="getOptimizationScore(strategy) !== null"
                  :text="`OPT ${getOptimizationScore(strategy)}`"
                  variant="gold"
                  size="sm"
                />
              </div>

              <p class="description" :title="getStrategyCardDescription(strategy)">{{ getStrategyCardDescription(strategy) }}</p>

              <div v-if="strategy.parameters?.length" class="params-list">
                <div v-for="param in strategy.parameters" :key="param.name" class="param-item">
                  <span class="param-label">{{ param.name }}</span>
                  <span class="param-value">{{ getParameterDisplayValue(param.value) }}</span>
                </div>
              </div>
              <div v-else class="param-empty-state">
                当前策略尚未写入参数，需先在策略仓库或优化联动中补全配置。
              </div>

              <div class="card-footer">
                <ArtDecoButton
                  variant="outline"
                  size="sm"
                  :disabled="loading || !getStrategyId(strategy)"
                  @click="navigateToStrategyTab('signals', getStrategyId(strategy))"
                >
                  查看信号
                </ArtDecoButton>
                <ArtDecoButton
                  variant="solid"
                  size="sm"
                  :disabled="loading || !getStrategyId(strategy)"
                  @click="navigateToStrategyTab('backtest', getStrategyId(strategy))"
                >
                  进入回测
                </ArtDecoButton>
              </div>
            </div>
          </div>

          <div v-if="!loading && selectedStrategyMissing" class="empty-state artdeco-card">
            <p>未找到策略 {{ selectedStrategyId }} 的参数配置，请返回策略管理页重试。</p>
          </div>
        </div>
      </template>
    </section>
  </div>
</template>

<style scoped lang="scss">
@use './styles/StrategyParametersTab';
</style>
