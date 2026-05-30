<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ArtDecoButton, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import AttributionPanel from '@/components/shared/attribution/AttributionPanel.vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { useAttributionAnalysis } from '@/composables/attribution/useAttributionAnalysis.ts'
import { apiClient } from '@/api/apiClient'
import {
  extractTradePositionsPayload,
  toPortfolioOverviewData,
  type PortfolioOverviewData,
} from '@/views/artdeco-pages/portfolio-tabs/portfolioOverviewData'

const { loading, error, lastRequestId, exec } = useArtDecoApi()
const {
  data: attribution,
  loading: attributionLoading,
  error: attributionError,
  lastRequestId: attributionRequestId,
  loadAttribution,
  clearAttribution,
} = useAttributionAnalysis()
const props = withDefaults(defineProps<{ functionKey?: string }>(), {
  functionKey: '',
})
const portfolio = ref<PortfolioOverviewData>(toPortfolioOverviewData(null))
const hasSuccessfulPortfolioSnapshot = ref(false)
const lastVerifiedRequestId = ref('')
const attributionMode = ref<'current' | 'date'>('current')
const attributionDate = ref('')
const isEmbedded = computed(() => Boolean(props.functionKey))
const isPendingFirstPortfolioLoad = computed(() => loading.value && !hasSuccessfulPortfolioSnapshot.value)
const isUnavailableFirstPortfolioLoad = computed(() => Boolean(error.value) && !hasSuccessfulPortfolioSnapshot.value)
const shouldUsePortfolioPlaceholders = computed(() => isPendingFirstPortfolioLoad.value || isUnavailableFirstPortfolioLoad.value)
const displayRequestId = computed(() => {
  if (shouldUsePortfolioPlaceholders.value) {
    return 'N/A'
  }

  return lastVerifiedRequestId.value || lastRequestId.value || 'N/A'
})
const pageStatusText = computed(() => {
  if (error.value) return '拉取失败'
  if (loading.value) return '同步中'
  if ((portfolio.value?.positions?.length ?? 0) === 0) return '组合为空'
  return (portfolio.value?.today_pnl ?? 0) >= 0 ? '组合偏强' : '组合承压'
})
const pageStatusType = computed(() => {
  if (error.value) return 'warning'
  if ((portfolio.value?.positions?.length ?? 0) === 0) return 'info'
  return (portfolio.value?.today_pnl ?? 0) >= 0 ? 'success' : 'warning'
})
const runtimeMessage = computed(() => {
  if (error.value) {
    return hasSuccessfulPortfolioSnapshot.value
      ? `${error.value}，当前仍显示上次成功同步的组合快照。`
      : `${error.value}，当前暂无已验证组合快照。`
  }
  if (loading.value) {
    return '组合资产同步中...'
  }
  if ((portfolio.value?.positions?.length ?? 0) === 0) {
    return '当前暂无持仓，归因与再平衡建议已折叠为空状态。'
  }
  return ''
})

const rebalancePolicyReady = computed(() => portfolio.value?.rebalance_policy_ready === true)

const autoRebalanceSuggestions = computed(() => {
  const positions = portfolio.value?.positions ?? []
  if (positions.length === 0 || !rebalancePolicyReady.value) {
    return []
  }

  const total = Math.max(
    1,
    positions.reduce((sum, item) => sum + item.market_value, 0),
  )

  return positions
    .flatMap((item) => {
      if (item.target_weight === null) {
        return []
      }
      const currentWeight = Number(((item.market_value / total) * 100).toFixed(2))
      const targetWeight = Number(item.target_weight.toFixed(2))
      const gap = Number((currentWeight - targetWeight).toFixed(2))
      const amount = Number(((Math.abs(gap) / 100) * total).toFixed(2))
      return [{
        symbol: item.symbol,
        name: item.name,
        currentWeight,
        targetWeight,
        gap,
        amount,
        action: gap > 0 ? '减仓' : '加仓',
      }]
    })
    .filter((item) => Math.abs(item.gap) >= 3)
    .sort((a, b) => Math.abs(b.gap) - Math.abs(a.gap))
    .slice(0, 6)
})

const rebalanceStatValue = computed(() => (
  rebalancePolicyReady.value ? autoRebalanceSuggestions.value.length : '待接入'
))

const positionCount = computed(() => portfolio.value?.positions?.length || 0)
const displayPositionCount = computed(() => (shouldUsePortfolioPlaceholders.value ? '--' : `${positionCount.value}`))
const totalAssetsLabel = computed(() =>
  portfolio.value?.total_assets?.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) || '0.00',
)
const displayTotalAssetsLabel = computed(() => (shouldUsePortfolioPlaceholders.value ? '--' : totalAssetsLabel.value))
const todayPnlLabel = computed(() =>
  `${(portfolio.value?.today_pnl ?? 0) >= 0 ? '+' : ''}${portfolio.value?.today_pnl?.toLocaleString() || 0}`,
)
const displayTodayPnlLabel = computed(() => (shouldUsePortfolioPlaceholders.value ? '--' : todayPnlLabel.value))
const displayTodayPnlPct = computed(() => (shouldUsePortfolioPlaceholders.value ? '--' : `${portfolio.value?.today_pnl_pct ?? 0}%`))
const displayRebalanceStatValue = computed(() => (shouldUsePortfolioPlaceholders.value ? '--' : `${rebalanceStatValue.value}`))
const todayPnlStatVariant = computed(() => (
  shouldUsePortfolioPlaceholders.value ? 'gold' : (portfolio.value?.today_pnl ?? 0) >= 0 ? 'rise' : 'fall'
))
const todayPnlHeroClass = computed(() => (
  shouldUsePortfolioPlaceholders.value ? 'pending' : (portfolio.value?.today_pnl ?? 0) >= 0 ? 'rise' : 'down'
))

const fetchAttribution = async () => {
  if ((portfolio.value?.positions?.length ?? 0) === 0) {
    clearAttribution()
    return
  }

  await loadAttribution({
    source: 'trade',
    date: attributionMode.value === 'date' && attributionDate.value ? attributionDate.value : undefined,
  })
}

const setAttributionMode = (mode: 'current' | 'date') => {
  attributionMode.value = mode
  if (mode === 'current') {
    void fetchAttribution()
  }
}

const handleAttributionDateChange = () => {
  attributionMode.value = 'date'
  if (attributionDate.value) {
    void fetchAttribution()
  }
}

const fetchPortfolio = async () => {
  const responseData = await exec(() => apiClient.get('/v1/trade/positions'), {
    silent: true,
  })

  const payload = extractTradePositionsPayload(responseData)
  if (payload) {
    portfolio.value = toPortfolioOverviewData(payload)
    hasSuccessfulPortfolioSnapshot.value = true
    lastVerifiedRequestId.value = lastRequestId.value || lastVerifiedRequestId.value
    await fetchAttribution()
    return
  }

  if (!hasSuccessfulPortfolioSnapshot.value) {
    portfolio.value = toPortfolioOverviewData(null)
    clearAttribution()
  }
}

onMounted(() => {
  void fetchPortfolio()
})
</script>

<template>
  <div
    class="portfolio-overview-tab page-enter"
    :class="{ 'is-embedded': isEmbedded }"
    data-testid="trade-portfolio-page"
  >
    <section v-if="!isEmbedded" class="hero-shell artdeco-card-shell" data-testid="trade-portfolio-header">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">portfolio assets desk</span>
          <div class="hero-meta">
            <span>REQ: {{ displayRequestId }}</span>
            <span>POSITIONS: {{ displayPositionCount }}</span>
            <span>REBALANCE: {{ displayRebalanceStatValue }}</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="组合资产工作台"
        subtitle="统一查看资产规模、持仓分布、绩效归因和再平衡建议"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton
            variant="outline"
            size="sm"
            :loading="loading"
            data-testid="trade-portfolio-refresh"
            @click="fetchPortfolio"
          >
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新资产
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section v-if="!isEmbedded" class="stats-strip artdeco-card-shell" data-testid="trade-portfolio-status-strip">
      <ArtDecoStatCard label="总资产" :value="displayTotalAssetsLabel" :show-change="false" variant="gold" />
      <ArtDecoStatCard
        label="今日盈亏"
        :value="displayTodayPnlLabel"
        :show-change="false"
        :variant="todayPnlStatVariant"
      />
      <ArtDecoStatCard label="持仓数量" :value="displayPositionCount" :show-change="false" variant="gold" />
      <ArtDecoStatCard label="再平衡建议" :value="displayRebalanceStatValue" :show-change="false" variant="gold" />
    </section>

    <div class="assets-hero artdeco-card" v-loading="loading" data-testid="trade-portfolio-primary-surface">
      <div class="hero-content">
        <div class="asset-main">
          <span class="asset-label">Total Assets (CNY)</span>
          <div class="value">{{ displayTotalAssetsLabel }}</div>
        </div>
        <div class="asset-pnl">
          <span class="asset-label">Today's P&amp;L</span>
          <div :class="['pnl-value', todayPnlHeroClass]">
            {{ displayTodayPnlLabel }}
            <span class="pct">({{ displayTodayPnlPct }})</span>
          </div>
        </div>
      </div>
      <div class="hero-decoration"></div>
    </div>

    <p v-if="runtimeMessage" class="runtime-message" aria-live="polite" data-testid="trade-portfolio-runtime-state">
      {{ runtimeMessage }}
    </p>

    <div class="position-list-section" data-testid="trade-portfolio-position-surface">
      <h3 class="subsection-title">Top Positions</h3>
      <div v-if="isPendingFirstPortfolioLoad" class="section-empty artdeco-card">持仓明细同步中，正在等待真实组合返回。</div>
      <div v-else-if="isUnavailableFirstPortfolioLoad" class="section-empty artdeco-card">组合资产不可用，暂无可展示的持仓快照。</div>
      <div v-else-if="portfolio?.positions?.length" class="positions-grid">
        <div v-for="pos in portfolio?.positions" :key="pos.symbol" class="position-item artdeco-card">
          <div class="pos-header">
            <span class="name">{{ pos.name }}</span>
            <span class="symbol">{{ pos.symbol }}</span>
          </div>
          <div class="pos-data">
            <div class="data-group">
              <label>Market Value</label>
              <div class="val">{{ pos.market_value.toLocaleString() }}</div>
            </div>
            <div class="data-group">
              <label>P&amp;L %</label>
              <div :class="['val', pos.pnl_pct >= 0 ? 'rise' : 'down']">{{ pos.pnl_pct }}%</div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="section-empty artdeco-card">暂无持仓数据。</div>
    </div>

    <div class="attribution-section">
      <div class="attribution-controls artdeco-card" data-testid="trade-portfolio-control-lens">
        <div class="attribution-controls__group" role="group" aria-label="归因口径">
          <button
            type="button"
            class="attribution-controls__mode"
            :class="{ active: attributionMode === 'current' }"
            data-testid="attribution-mode-current"
            @click="setAttributionMode('current')"
          >
            当前快照
          </button>
          <button
            type="button"
            class="attribution-controls__mode"
            :class="{ active: attributionMode === 'date' }"
            data-testid="attribution-mode-date"
            @click="setAttributionMode('date')"
          >
            指定日期
          </button>
        </div>
        <label class="attribution-controls__date">
          <span>归因日期</span>
          <input
            v-model="attributionDate"
            type="date"
            data-testid="attribution-date-input"
            :disabled="attributionMode !== 'date'"
            @change="handleAttributionDateChange"
          />
        </label>
      </div>
      <AttributionPanel
        :analysis="attribution"
        :loading="isPendingFirstPortfolioLoad || attributionLoading"
        :error="isUnavailableFirstPortfolioLoad ? '组合资产不可用，暂无可展示的归因快照。' : attributionError"
        title="绩效归因"
        :request-id="attributionRequestId"
      />
    </div>

    <div class="rebalance-section" data-testid="trade-portfolio-rebalance-surface">
      <h3 class="subsection-title">自动再平衡建议</h3>
      <div class="rebalance-list artdeco-card">
        <div v-if="isPendingFirstPortfolioLoad" class="rebalance-empty">
          再平衡上下文同步中，正在等待真实持仓返回。
        </div>
        <div v-else-if="isUnavailableFirstPortfolioLoad" class="rebalance-empty">
          组合资产不可用，当前暂无可评估的再平衡上下文。
        </div>
        <div v-else-if="positionCount > 0 && !rebalancePolicyReady" class="rebalance-empty">
          再平衡策略待接入，当前持仓数据未提供目标仓位或组合约束。
        </div>
        <div v-else-if="autoRebalanceSuggestions.length === 0" class="rebalance-empty">
          当前持仓权重偏离较小，暂无自动再平衡建议。
        </div>
        <div v-else>
          <div
            v-for="item in autoRebalanceSuggestions"
            :key="`rebalance-${item.symbol}`"
            class="rebalance-row"
          >
            <div class="rebalance-main">
              <span class="name">{{ item.name }}</span>
              <span class="symbol">{{ item.symbol }}</span>
            </div>
            <div class="rebalance-detail">
              当前 {{ item.currentWeight }}% → 目标 {{ item.targetWeight }}%
            </div>
            <div class="rebalance-action" :class="item.gap > 0 ? 'down' : 'rise'">
              建议{{ item.action }}约 ¥{{ item.amount.toLocaleString('zh-CN') }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use './styles/Portfolio';
</style>
