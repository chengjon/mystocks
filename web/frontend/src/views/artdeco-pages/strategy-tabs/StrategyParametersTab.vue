<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ArtDecoBadge, ArtDecoButton, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { useStrategyCrossTabContext } from '@/composables/strategy/useStrategyCrossTabContext'
import { strategyApi } from '@/api'
import type { StrategyConfig } from '@/api/types/common'
import { extractStrategyIdFromQuery } from './strategyCrossTabNavigation'
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
const { getSnapshot, setActiveStrategy } = useStrategyCrossTabContext()

const selectedStrategyId = computed(() => extractStrategyIdFromQuery(route.query as Record<string, unknown>))
const selectedStrategySnapshot = computed(() => {
  if (!selectedStrategyId.value) {
    return null
  }
  return getSnapshot(selectedStrategyId.value)
})

const traceRequestId = computed(() => {
  const requestId = lastRequestId.value.trim()
  return requestId.length > 0 ? requestId : 'N/A'
})
const traceProcessTimeMs = computed(() => normalizeProcessTimeMs(lastProcessTime.value))
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
  if (headerError.value) return '接口异常'
  return selectedStrategyId.value ? '参数上下文已绑定' : '策略参数在线'
})
const pageStatusType = computed(() => {
  if (headerError.value) return 'warning'
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

const headerError = computed(() => {
  return error.value || fallbackReason.value
})

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
  const payload = await exec(() => strategyApi.getStrategies({}), {
    silent: true,
    errorMsg: '获取策略参数失败'
  })

  if (!payload) {
    strategies.value = []
    dataSource.value = 'real'
    fallbackReason.value = error.value || '获取策略参数失败'
    return
  }

  const extracted = extractStrategyConfigs(payload)
  if (extracted === null) {
    strategies.value = []
    dataSource.value = 'real'
    fallbackReason.value = '策略参数数据格式异常'
    return
  }

  strategies.value = extracted
  dataSource.value = 'real'
  fallbackReason.value = ''
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
      <ArtDecoStatCard label="可见策略" :value="visibleStrategyCount" variant="gold" />
      <ArtDecoStatCard label="参数总项" :value="parameterEntryCount" variant="gold" />
      <ArtDecoStatCard label="优化联动" :value="optimizationLinkedCount" variant="rise" />
      <ArtDecoStatCard label="当前焦点" :value="selectedStrategyLabel" variant="gold" />
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

      <p v-if="headerError" class="error-tip">{{ headerError }}</p>

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

            <p class="description">{{ strategy.description }}</p>

            <div class="params-list">
              <div v-for="param in strategy.parameters" :key="param.name" class="param-item">
                <span class="param-label">{{ param.name }}</span>
                <span class="param-value">{{ param.value }}</span>
              </div>
            </div>

            <div class="card-footer">
              <button class="artdeco-button gold-outline">Edit Parameters</button>
              <button class="artdeco-button gold-solid" v-if="strategy.status !== 'active'">Activate</button>
            </div>
          </div>
        </div>

        <div v-if="!loading && selectedStrategyMissing" class="empty-state artdeco-card">
          <p>未找到策略 {{ selectedStrategyId }} 的参数配置，请返回策略管理页重试。</p>
        </div>
        <div v-else-if="!loading && strategies.length === 0" class="empty-state artdeco-card">
          <p>REAL 数据为空，请先在 Strategy Management 中创建策略。</p>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss">
@use './styles/StrategyParametersTab';
</style>
