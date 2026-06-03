<script setup lang="ts">
import { computed, getCurrentInstance, onMounted, ref } from 'vue'
import { ArtDecoButton, ArtDecoCard, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import ArtDecoRouteHeader from '@/components/artdeco/route-shell/ArtDecoRouteHeader.vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { apiClient } from '@/api/apiClient'
import {
  extractPositionsPayload,
  toTradingPositionRows,
} from '@/views/artdeco-pages/trading-tabs/tradingDataTransform'

export interface Position {
  symbol: string
  name: string
  shares: number
  avgCost: number
  currentPrice: number
  marketValue: number
  pnl: number
  pnlPercent: number
  positionPercent: number
}

type PositionSegmentKey = 'all' | 'gain' | 'loss' | 'highWeight' | 'attention'

interface RuntimeStatus {
  label: string
  detail: string
  tone: 'success' | 'warning' | 'info' | 'neutral'
}

const HIGH_WEIGHT_THRESHOLD = 30

const props = defineProps<{
  positions?: Position[]
}>()

const internalPositions = ref<Position[]>([])
const activeSegment = ref<PositionSegmentKey>('all')
const hasLoaded = ref(false)
const staleError = ref<string | null>(null)
const hasVerifiedPositionsSnapshot = ref(false)
const lastVerifiedRequestId = ref('')
const lastVerifiedProcessTime = ref('')
const instance = getCurrentInstance()
const { exec, loading, error, lastRequestId, lastProcessTime } = useArtDecoApi()

const isEmbedded = computed(() => {
  const rawProps = instance?.vnode.props
  return Boolean(rawProps && 'positions' in rawProps)
})
const hasProvidedPositionsSnapshot = computed(() => Array.isArray(props.positions))
const hasTrustedPositionsSnapshot = computed(() => hasVerifiedPositionsSnapshot.value || hasProvidedPositionsSnapshot.value)

const displayPositions = computed(() => {
  if (Array.isArray(props.positions) && props.positions.length > 0) {
    return props.positions
  }
  return internalPositions.value
})

const rawTotalMarketValue = computed(() =>
  displayPositions.value.reduce((sum, position) => sum + Number(position.marketValue || 0), 0),
)
const totalMarketValue = computed(() => `¥${rawTotalMarketValue.value.toFixed(0)}`)
const totalPnl = computed(() => displayPositions.value.reduce((sum, position) => sum + Number(position.pnl || 0), 0))
const positiveCount = computed(() =>
  displayPositions.value.filter((position) => position.pnl >= 0).length,
)
const negativeCount = computed(() =>
  displayPositions.value.filter((position) => position.pnl < 0).length,
)
const highWeightPositions = computed(() =>
  displayPositions.value.filter((position) => isHighWeightPosition(position)),
)
const attentionPositions = computed(() =>
  displayPositions.value.filter((position) => needsPositionAttention(position)),
)
const positionSegments = computed(() => [
  { key: 'all' as const, label: '全部', count: displayPositions.value.length },
  { key: 'gain' as const, label: '盈利', count: positiveCount.value },
  { key: 'loss' as const, label: '亏损', count: negativeCount.value },
  { key: 'highWeight' as const, label: '高仓位', count: highWeightPositions.value.length },
  { key: 'attention' as const, label: '需关注', count: attentionPositions.value.length },
])
const filteredPositions = computed(() => {
  switch (activeSegment.value) {
    case 'gain':
      return displayPositions.value.filter((position) => position.pnl >= 0)
    case 'loss':
      return displayPositions.value.filter((position) => position.pnl < 0)
    case 'highWeight':
      return highWeightPositions.value
    case 'attention':
      return attentionPositions.value
    default:
      return displayPositions.value
  }
})
const activeSegmentLabel = computed(() =>
  positionSegments.value.find((segment) => segment.key === activeSegment.value)?.label ?? '全部',
)
const highestWeight = computed(() => {
  if (displayPositions.value.length === 0) return '--'
  const value = Math.max(...displayPositions.value.map((position) => Number(position.positionPercent || 0)))
  return `${value.toFixed(2)}%`
})
const isAwaitingFirstPositionsLoad = computed(() => loading.value && !hasLoaded.value && !error.value && displayPositions.value.length === 0)
const effectiveError = computed(() => (!hasTrustedPositionsSnapshot.value ? error.value : null))
const showSummaryPlaceholders = computed(() => !hasTrustedPositionsSnapshot.value)
const displayRequestId = computed(() => {
  if (hasVerifiedPositionsSnapshot.value) {
    return lastVerifiedRequestId.value || 'N/A'
  }
  if (!lastRequestId.value) {
    return isAwaitingFirstPositionsLoad.value ? '--' : 'N/A'
  }
  return effectiveError.value ? 'N/A' : lastRequestId.value
})
const displayProcessTime = computed(() => {
  if (hasVerifiedPositionsSnapshot.value) {
    if (!lastVerifiedProcessTime.value) {
      return 'N/A'
    }
    const verifiedValue = Number.parseFloat(lastVerifiedProcessTime.value)
    if (Number.isNaN(verifiedValue)) {
      return lastVerifiedProcessTime.value
    }
    return `${verifiedValue.toFixed(2)}ms`
  }
  if (!lastProcessTime.value) {
    return isAwaitingFirstPositionsLoad.value ? '--' : 'N/A'
  }
  const value = Number.parseFloat(lastProcessTime.value)
  if (Number.isNaN(value)) {
    return lastProcessTime.value
  }
  return `${value.toFixed(2)}ms`
})
const displayRowCount = computed(() => (showSummaryPlaceholders.value ? '--' : String(filteredPositions.value.length)))
const displayPositiveCount = computed(() => (showSummaryPlaceholders.value ? '--' : String(positiveCount.value)))
const displayNegativeCount = computed(() => (showSummaryPlaceholders.value ? '--' : String(negativeCount.value)))
const displayTotalMarketValue = computed(() => (showSummaryPlaceholders.value ? '--' : totalMarketValue.value))
const displayHighestWeight = computed(() => (showSummaryPlaceholders.value ? '--' : highestWeight.value))
const displayTotalPnl = computed(() => (showSummaryPlaceholders.value ? '--' : `¥${totalPnl.value.toFixed(0)}`))
const pageStatusText = computed(() => {
  if (effectiveError.value) return '同步失败'
  if (staleError.value) return '显示缓存快照'
  if (loading.value && hasTrustedPositionsSnapshot.value) return '刷新中'
  if (loading.value) return '同步中'
  return displayPositions.value.length > 0 ? '快照已验证' : '暂无持仓'
})
const pageStatusType = computed(() => {
  if (effectiveError.value || staleError.value) return 'warning'
  return 'info'
})
const runtimeStatus = computed<RuntimeStatus>(() => {
  if (effectiveError.value) {
    return {
      label: '同步失败',
      detail: `${effectiveError.value}，请重试。`,
      tone: 'warning',
    }
  }
  if (staleError.value) {
    return {
      label: '显示缓存快照',
      detail: `${staleError.value}，当前仍显示上次成功同步的持仓快照。`,
      tone: 'warning',
    }
  }
  if (loading.value && hasTrustedPositionsSnapshot.value) {
    return {
      label: '刷新中',
      detail: '正在同步最新持仓，当前表格保持上次已验证快照。',
      tone: 'info',
    }
  }
  if (loading.value) {
    return {
      label: '同步中',
      detail: '持仓数据同步中...',
      tone: 'info',
    }
  }
  if (hasTrustedPositionsSnapshot.value && displayPositions.value.length > 0) {
    return {
      label: '已验证',
      detail: `当前显示 ${activeSegmentLabel.value} 持仓 ${filteredPositions.value.length} 条。`,
      tone: totalPnl.value < 0 ? 'warning' : 'success',
    }
  }
  if (hasTrustedPositionsSnapshot.value) {
    return {
      label: '暂无持仓',
      detail: '最近一次同步成功，但当前没有持仓记录。',
      tone: 'neutral',
    }
  }
  return {
    label: '等待同步',
    detail: '等待持仓数据同步。',
    tone: 'neutral',
  }
})
const positionsStateMessage = computed(() => runtimeStatus.value.detail)
const filteredEmptyMessage = computed(() =>
  `当前「${activeSegmentLabel.value}」视图没有匹配持仓。`,
)

function markVerifiedPositionsSnapshot() {
  hasVerifiedPositionsSnapshot.value = true
  lastVerifiedRequestId.value = lastRequestId.value || lastVerifiedRequestId.value
  lastVerifiedProcessTime.value = lastProcessTime.value || lastVerifiedProcessTime.value
}

const loadPositions = async () => {
  staleError.value = null
  const responseData = await exec(() => apiClient.get('/v1/trade/positions'), { silent: true })
  if (!responseData) {
    hasLoaded.value = true
    if (hasVerifiedPositionsSnapshot.value) {
      staleError.value = error.value || '持仓拉取失败'
    } else {
      internalPositions.value = []
    }
    return
  }
  internalPositions.value = toTradingPositionRows(extractPositionsPayload(responseData))
  markVerifiedPositionsSnapshot()
  hasLoaded.value = true
}

function clampPositionPercent(value: number): number {
  if (!Number.isFinite(value)) {
    return 0
  }
  return Math.min(Math.max(value, 0), 100)
}

function selectPositionSegment(segment: PositionSegmentKey) {
  activeSegment.value = segment
}

function isHighWeightPosition(position: Position): boolean {
  return Number(position.positionPercent || 0) >= HIGH_WEIGHT_THRESHOLD
}

function needsPositionAttention(position: Position): boolean {
  return position.pnl < 0 || position.pnlPercent < 0 || isHighWeightPosition(position)
}

function getPositionAttentionLabel(position: Position): string {
  if (position.pnl < 0 || position.pnlPercent < 0) {
    return '亏损'
  }
  if (isHighWeightPosition(position)) {
    return '高仓位'
  }
  return ''
}

onMounted(() => {
  if (!Array.isArray(props.positions) || props.positions.length === 0) {
    void loadPositions()
  }
})
</script>

<template>
  <div
    class="artdeco-trading-positions"
    :class="{ 'is-embedded': isEmbedded }"
    data-test="trade-positions-page"
    data-testid="trade-positions-page"
  >
    <ArtDecoRouteHeader
      v-if="!isEmbedded"
      title="持仓工作台"
      subtitle="统一查看持仓结构、盈亏表现和仓位分布，形成交易域的头寸入口"
      eyebrow="持仓审阅"
      :show-status="true"
      :status-text="pageStatusText"
      :status-type="pageStatusType"
      test-id="trade-positions-header"
      legacy-test="trade-positions-header"
    >
      <template #meta>
        <span>请求: {{ displayRequestId }}</span>
        <span>耗时: {{ displayProcessTime }}</span>
        <span>行数: {{ displayRowCount }}</span>
      </template>

      <template #actions>
        <ArtDecoButton
          variant="solid"
          priority="primary"
          motion="data"
          size="sm"
          :loading="loading"
          data-test="trade-positions-refresh"
          data-testid="trade-positions-refresh"
          @click="loadPositions"
        >
          <template #icon>
            <ArtDecoIcon name="refresh" />
          </template>
          刷新持仓
        </ArtDecoButton>
      </template>
    </ArtDecoRouteHeader>

    <section v-if="!isEmbedded" class="stats-strip artdeco-card-shell" data-testid="trade-positions-status-strip">
      <ArtDecoStatCard label="持仓标的" :value="displayRowCount" :show-change="false" variant="gold" />
      <ArtDecoStatCard label="盈利标的" :value="displayPositiveCount" :show-change="false" variant="rise" />
      <ArtDecoStatCard label="亏损标的" :value="displayNegativeCount" :show-change="false" variant="fall" />
      <ArtDecoStatCard label="组合市值" :value="displayTotalMarketValue" :show-change="false" variant="gold" />
    </section>

    <section
      :class="isEmbedded ? 'embedded-shell' : 'content-shell artdeco-card-shell'"
      data-testid="trade-positions-primary-surface"
    >
      <div v-if="!isEmbedded" class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">仓位快照</span>
          <h3 class="content-shell-title">持仓审阅与仓位面板</h3>
          <p class="content-shell-subtitle">聚焦市值、盈亏与仓位占比，快速识别需要继续跟进的持仓。</p>
        </div>
        <div class="content-shell-meta">
          <span>市值: {{ displayTotalMarketValue }}</span>
          <span>总盈亏: {{ displayTotalPnl }}</span>
          <span>最高仓位: {{ displayHighestWeight }}</span>
        </div>
      </div>

      <ArtDecoCard title="持仓明细" hoverable>
        <div
          class="artdeco-trading-positions__controls"
          data-test="trade-positions-segments"
          data-testid="trade-positions-control-lens"
          role="tablist"
          aria-label="持仓审阅视图"
        >
          <button
            v-for="segment in positionSegments"
            :key="segment.key"
            class="artdeco-trading-positions__segment"
            :class="{ 'is-active': activeSegment === segment.key }"
            type="button"
            role="tab"
            :aria-selected="activeSegment === segment.key"
            :data-segment="segment.key"
            :data-testid="`trade-positions-segment-${segment.key}`"
            @click="selectPositionSegment(segment.key)"
          >
            <span>{{ segment.label }}</span>
            <strong>{{ showSummaryPlaceholders ? '--' : segment.count }}</strong>
          </button>
        </div>
        <div
          class="artdeco-trading-positions__runtime"
          :class="`is-${runtimeStatus.tone}`"
          :data-state="runtimeStatus.label"
          data-test="trade-positions-runtime"
          data-testid="trade-positions-runtime-state"
        >
          <span class="artdeco-trading-positions__runtime-label">{{ runtimeStatus.label }}</span>
          <p class="artdeco-trading-positions__status" aria-live="polite">
            {{ positionsStateMessage }}
          </p>
        </div>
        <div
          class="artdeco-trading-positions__table"
          role="table"
          aria-label="持仓明细表"
          :aria-busy="loading ? 'true' : 'false'"
          data-test="trade-positions-table"
        >
          <div class="artdeco-trading-positions__header" role="rowgroup">
            <div class="artdeco-trading-positions__col artdeco-trading-positions__col--symbol" role="columnheader">股票</div>
            <div class="artdeco-trading-positions__col artdeco-trading-positions__col--shares" role="columnheader">持股数</div>
            <div class="artdeco-trading-positions__col artdeco-trading-positions__col--avg-cost" role="columnheader">平均成本</div>
            <div class="artdeco-trading-positions__col artdeco-trading-positions__col--current-price" role="columnheader">当前价</div>
            <div class="artdeco-trading-positions__col artdeco-trading-positions__col--market-value" role="columnheader">市值</div>
            <div class="artdeco-trading-positions__col artdeco-trading-positions__col--pnl" role="columnheader">盈亏</div>
            <div class="artdeco-trading-positions__col artdeco-trading-positions__col--pnl-percent" role="columnheader">盈亏%</div>
            <div class="artdeco-trading-positions__col artdeco-trading-positions__col--position" role="columnheader">仓位%</div>
          </div>
          <div
            v-if="effectiveError"
            class="artdeco-trading-positions__empty artdeco-trading-positions__empty--error"
            data-test="trade-positions-error"
          >
            <p>持仓拉取失败，当前无法展示真实数据。</p>
            <ArtDecoButton variant="outline" size="sm" data-test="trade-positions-retry" @click="loadPositions">
              <template #icon>
                <ArtDecoIcon name="refresh" />
              </template>
              重试
            </ArtDecoButton>
          </div>
          <div v-else-if="displayPositions.length === 0" class="artdeco-trading-positions__empty" data-test="trade-positions-empty">
            {{ loading ? '持仓数据同步中...' : '暂无持仓数据' }}
          </div>
          <div
            v-else-if="filteredPositions.length === 0"
            class="artdeco-trading-positions__empty"
            data-test="trade-positions-filtered-empty"
            data-testid="trade-positions-filtered-empty"
          >
            {{ filteredEmptyMessage }}
          </div>
          <div v-else class="artdeco-trading-positions__body" role="rowgroup">
            <div
              v-for="position in filteredPositions"
              :key="position.symbol"
              class="artdeco-trading-positions__row"
              :class="{
                'is-attention': needsPositionAttention(position),
                'is-high-weight': isHighWeightPosition(position),
                'is-loss': position.pnl < 0,
              }"
              role="row"
              data-test="trade-positions-row"
              data-testid="trade-positions-row"
            >
              <div class="artdeco-trading-positions__col artdeco-trading-positions__col--symbol" role="cell">
                <div class="artdeco-trading-positions__symbol-name">{{ position.name }}</div>
                <div class="artdeco-trading-positions__symbol-code">
                  {{ position.symbol }}
                  <span v-if="getPositionAttentionLabel(position)" class="artdeco-trading-positions__row-flag">
                    {{ getPositionAttentionLabel(position) }}
                  </span>
                </div>
              </div>
              <div class="artdeco-trading-positions__col artdeco-trading-positions__col--shares artdeco-trading-positions__numeric" role="cell">
                {{ position.shares }}
              </div>
              <div class="artdeco-trading-positions__col artdeco-trading-positions__col--avg-cost artdeco-trading-positions__numeric" role="cell">
                ¥{{ position.avgCost }}
              </div>
              <div class="artdeco-trading-positions__col artdeco-trading-positions__col--current-price artdeco-trading-positions__numeric" role="cell">
                ¥{{ position.currentPrice }}
              </div>
              <div class="artdeco-trading-positions__col artdeco-trading-positions__col--market-value artdeco-trading-positions__numeric" role="cell">
                ¥{{ position.marketValue }}
              </div>
              <div
                class="artdeco-trading-positions__col artdeco-trading-positions__col--pnl artdeco-trading-positions__numeric"
                :class="
                  position.pnl >= 0
                    ? 'artdeco-trading-positions__pnl--rise'
                    : 'artdeco-trading-positions__pnl--fall'
                "
                role="cell"
              >
                ¥{{ position.pnl }}
              </div>
              <div
                class="artdeco-trading-positions__col artdeco-trading-positions__col--pnl-percent artdeco-trading-positions__numeric"
                :class="
                  position.pnlPercent >= 0
                    ? 'artdeco-trading-positions__pnl--rise'
                    : 'artdeco-trading-positions__pnl--fall'
                "
                role="cell"
              >
                {{ position.pnlPercent >= 0 ? '+' : '' }}{{ position.pnlPercent }}%
              </div>
              <div class="artdeco-trading-positions__col artdeco-trading-positions__col--position" role="cell">
                <div class="artdeco-trading-positions__position-bar">
                  <div
                    class="artdeco-trading-positions__position-fill"
                    :style="{ transform: `scaleX(${clampPositionPercent(position.positionPercent) / 100})` }"
                  ></div>
                  <span class="artdeco-trading-positions__position-text">
                    {{ position.positionPercent }}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </ArtDecoCard>
    </section>
  </div>
</template>

<style scoped lang="scss" src="./styles/Center.scss"></style>
