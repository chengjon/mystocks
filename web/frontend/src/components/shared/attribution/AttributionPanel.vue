<script setup lang="ts">
import { computed } from 'vue'

import type {
  AttributionAnalysisResponse,
  AttributionContributionRow,
  AttributionIndustryBreakdown,
  FactorExposureDetail,
} from '@/api/portfolioAttribution'

const props = withDefaults(defineProps<{
  analysis: AttributionAnalysisResponse | null
  loading?: boolean
  error?: string | null
  title?: string
  requestId?: string
}>(), {
  loading: false,
  error: null,
  title: '绩效归因',
  requestId: '',
})

const summaryItems = computed(() => [
  {
    label: '组合收益',
    value: formatPercent(props.analysis?.snapshot_meta?.total_return),
  },
  {
    label: '基准收益',
    value: formatPercent(props.analysis?.benchmark_meta?.total_return),
  },
  {
    label: '持仓数量',
    value: String(props.analysis?.snapshot_meta?.constituent_count ?? '--'),
  },
])

const brinsonItems = computed(() => [
  { label: '配置效应', value: props.analysis?.brinson?.allocation_effect },
  { label: '选择效应', value: props.analysis?.brinson?.selection_effect },
  { label: '交互效应', value: props.analysis?.brinson?.interaction_effect },
])

const industryRows = computed(() => Object.entries(props.analysis?.brinson?.industry_breakdown ?? {})
  .map(([industry, row]) => ({
    industry,
    ...normalizeIndustryRow(row),
  }))
  .slice(0, 6))

const factorRows = computed(() => Object.entries(props.analysis?.factor_attribution?.factor_exposures ?? {})
  .map(([factor, exposure]) => ({
    factor,
    ...normalizeFactorRow(exposure),
    contribution: props.analysis?.factor_attribution?.factor_contributions?.[factor] ?? 0,
  })))

const contributorRows = computed(() => [
  ...(props.analysis?.top_contributors ?? []).slice(0, 3).map((row) => ({ ...row, kind: 'rise' as const })),
  ...(props.analysis?.top_detractors ?? []).slice(0, 3).map((row) => ({ ...row, kind: 'fall' as const })),
])

function normalizeIndustryRow(row: AttributionIndustryBreakdown) {
  return {
    portfolioWeight: row.portfolio_weight ?? 0,
    benchmarkWeight: row.benchmark_weight ?? 0,
    allocationEffect: row.allocation_effect ?? 0,
    selectionEffect: row.selection_effect ?? 0,
  }
}

function normalizeFactorRow(row: FactorExposureDetail) {
  return {
    portfolioExposure: row.portfolio_exposure ?? 0,
    benchmarkExposure: row.benchmark_exposure ?? 0,
    activeExposure: row.active_exposure ?? 0,
  }
}

function formatPercent(value: number | null | undefined): string {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    return '--'
  }
  const normalized = Math.abs(value) <= 1 ? value * 100 : value
  const sign = normalized > 0 ? '+' : normalized < 0 ? '-' : ''
  return `${sign}${Math.abs(normalized).toFixed(2)}%`
}

function formatSigned(value: number | null | undefined): string {
  return formatPercent(value)
}

function rowClass(row: Pick<AttributionContributionRow, 'contribution_value'> & { kind?: 'rise' | 'fall' }) {
  const value = row.contribution_value ?? 0
  if (value > 0) return 'rise'
  if (value < 0) return 'fall'
  return row.kind ?? ''
}
</script>

<template>
  <section class="attribution-panel artdeco-card" :aria-busy="loading">
    <header class="attribution-panel__header">
      <div>
        <h3>{{ title }}</h3>
        <p>
          {{ analysis?.analysis_date || 'N/A' }}
          <span v-if="requestId"> · REQ {{ requestId }}</span>
        </p>
      </div>
      <span v-if="analysis?.snapshot_meta?.stale" class="attribution-panel__badge">
        {{ analysis.snapshot_meta.stale_reason || 'stale' }}
      </span>
    </header>

    <div v-if="loading" class="attribution-panel__state">归因分析同步中。</div>
    <div v-else-if="error" class="attribution-panel__state attribution-panel__state--error">{{ error }}</div>
    <div v-else-if="!analysis" class="attribution-panel__state">暂无归因数据。</div>

    <template v-else>
      <div class="attribution-panel__summary">
        <div v-for="item in summaryItems" :key="item.label" class="attribution-panel__summary-item">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
        </div>
      </div>

      <div class="attribution-panel__grid">
        <section class="attribution-panel__block">
          <h4>Brinson 归因</h4>
          <div class="attribution-panel__metric-list">
            <div v-for="item in brinsonItems" :key="item.label" class="attribution-panel__metric-row">
              <span>{{ item.label }}</span>
              <strong :class="(item.value ?? 0) >= 0 ? 'rise' : 'fall'">{{ formatSigned(item.value) }}</strong>
            </div>
          </div>
          <div class="attribution-panel__table">
            <div v-for="row in industryRows" :key="row.industry" class="attribution-panel__table-row">
              <span>{{ row.industry }}</span>
              <span>{{ formatPercent(row.portfolioWeight) }}</span>
              <span>{{ formatPercent(row.allocationEffect + row.selectionEffect) }}</span>
            </div>
          </div>
        </section>

        <section class="attribution-panel__block">
          <h4>五因子归因</h4>
          <div class="attribution-panel__table attribution-panel__table--factor">
            <div v-for="row in factorRows" :key="row.factor" class="attribution-panel__table-row">
              <span>{{ row.factor }}</span>
              <span>{{ formatSigned(row.activeExposure) }}</span>
              <strong :class="row.contribution >= 0 ? 'rise' : 'fall'">{{ formatSigned(row.contribution) }}</strong>
            </div>
          </div>
          <div class="attribution-panel__metric-row attribution-panel__specific">
            <span>特异收益</span>
            <strong :class="(analysis.factor_attribution?.specific_return ?? 0) >= 0 ? 'rise' : 'fall'">
              {{ formatSigned(analysis.factor_attribution?.specific_return) }}
            </strong>
          </div>
        </section>
      </div>

      <section class="attribution-panel__block">
        <h4>贡献 / 拖累</h4>
        <div class="attribution-panel__contributors">
          <div
            v-for="row in contributorRows"
            :key="`${row.kind}-${row.symbol}`"
            class="attribution-panel__contributor"
          >
            <div>
              <strong>{{ row.symbol }}</strong>
              <span>{{ row.industry || '未分类' }}</span>
            </div>
            <span :class="rowClass(row)">{{ formatSigned(row.contribution_value) }}</span>
          </div>
        </div>
      </section>
    </template>
  </section>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.attribution-panel {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-5);
  padding: var(--artdeco-spacing-5);
  background: var(--artdeco-bg-card);
}

.attribution-panel__header,
.attribution-panel__summary,
.attribution-panel__grid,
.attribution-panel__table-row,
.attribution-panel__metric-row,
.attribution-panel__contributor {
  display: grid;
  gap: var(--artdeco-spacing-3);
}

.attribution-panel__header {
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: start;

  h3 {
    margin: 0;
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-display);
    font-size: var(--artdeco-text-xl);
  }

  p {
    margin: var(--artdeco-spacing-1) 0 0;
    color: var(--artdeco-fg-muted);
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-xs);
  }
}

.attribution-panel__badge {
  padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
  border: 1px solid var(--artdeco-gold-opacity-20);
  color: var(--artdeco-gold-light);
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
}

.attribution-panel__state {
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
}

.attribution-panel__state--error {
  color: var(--artdeco-down);
}

.attribution-panel__summary {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.attribution-panel__summary-item {
  min-height: var(--artdeco-spacing-16);
  padding: var(--artdeco-spacing-3);
  border: 1px solid var(--artdeco-gold-opacity-10);

  span {
    display: block;
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-xs);
  }

  strong {
    display: block;
    margin-top: var(--artdeco-spacing-2);
    color: var(--artdeco-fg-primary);
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-lg);
  }
}

.attribution-panel__grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.attribution-panel__block {
  min-width: 0;

  h4 {
    margin: 0 0 var(--artdeco-spacing-3);
    color: var(--artdeco-gold-light);
    font-family: var(--artdeco-font-display);
    font-size: var(--artdeco-text-md);
  }
}

.attribution-panel__metric-list,
.attribution-panel__table,
.attribution-panel__contributors {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.attribution-panel__metric-row,
.attribution-panel__table-row,
.attribution-panel__contributor {
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  color: var(--artdeco-fg-primary);
  font-size: var(--artdeco-text-sm);
}

.attribution-panel__table-row {
  grid-template-columns: minmax(0, 1fr) auto auto;
  padding: var(--artdeco-spacing-2) 0;
  border-bottom: 1px solid var(--artdeco-gold-opacity-10);
}

.attribution-panel__specific {
  margin-top: var(--artdeco-spacing-3);
}

.attribution-panel__contributor {
  padding: var(--artdeco-spacing-2) 0;
  border-bottom: 1px solid var(--artdeco-gold-opacity-10);

  div {
    display: flex;
    flex-direction: column;
    gap: calc(var(--artdeco-spacing-1) / 2);
  }

  span {
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-xs);
  }
}

.rise {
  color: var(--artdeco-rise);
}

.fall {
  color: var(--artdeco-down);
}

@media (width <= 48rem) {
  .attribution-panel__header,
  .attribution-panel__summary,
  .attribution-panel__grid {
    grid-template-columns: 1fr;
  }
}
</style>
