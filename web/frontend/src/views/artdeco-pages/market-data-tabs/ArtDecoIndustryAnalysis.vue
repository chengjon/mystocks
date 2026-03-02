<template>
  <div class="industry-analysis-page">
    <div class="page-header">
      <h2 class="section-title">板块动向分析</h2>
      <div class="header-meta">
        <span>DATA: {{ dataSource }}</span>
        <span>REQ_ID: {{ displayRequestId }}</span>
        <span>TIME: {{ displayProcessTime }}</span>
      </div>
      <ArtDecoButton variant="outline" size="sm" @click="refreshBoards">刷新板块</ArtDecoButton>
    </div>

    <div class="stats-grid">
      <ArtDecoStatCard label="活跃板块" :value="stats.activeBoards" variant="gold" />
      <ArtDecoStatCard label="上涨板块" :value="stats.risingBoards" variant="rise" />
      <ArtDecoStatCard label="领涨强度" :value="`${stats.leadStrength}%`" variant="gold" />
      <ArtDecoStatCard label="回撤板块" :value="stats.fallingBoards" variant="fall" />
    </div>

    <div class="content-grid">
      <ArtDecoCard title="板块热度排行" hoverable>
        <ArtDecoTable :columns="boardColumns" :data="boardRows" />
      </ArtDecoCard>

      <ArtDecoCard title="资金轮动快照" hoverable>
        <div class="rotation-list">
          <div class="rotation-item" v-for="item in rotationRows" :key="item.name">
            <div class="name">{{ item.name }}</div>
            <div class="meta">{{ item.window }}</div>
            <div class="value" :class="item.flow > 0 ? 'rise' : 'fall'">
              {{ item.flow > 0 ? '+' : '' }}{{ item.flow }} 亿
            </div>
          </div>
        </div>
      </ArtDecoCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { ArtDecoButton, ArtDecoCard, ArtDecoStatCard, ArtDecoTable } from '@/components/artdeco'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { apiClient } from '@/api/apiClient'
import type { UnifiedResponse } from '@/api/types/common'
import mockDashboard from '@/mock/mockDashboard'

interface IndustryFlowRow {
  rank?: number
  name?: string
  change?: number | string
  amount?: number | string
}

interface BoardRow {
  rank: number
  name: string
  change: string
  turnover: number
  netInflow: string
}

interface RotationRow {
  name: string
  window: string
  flow: number
}

const { lastRequestId, lastProcessTime, exec } = useArtDecoApi()

const boardColumns = [
  { key: 'rank', label: '排名', width: '80px' },
  { key: 'name', label: '板块' },
  { key: 'change', label: '涨跌幅', variant: 'color' },
  { key: 'turnover', label: '成交额(亿)' },
  { key: 'netInflow', label: '主力净流入(亿)', variant: 'color' }
]

const boardRows = ref<BoardRow[]>([])
const rotationRows = ref<RotationRow[]>([])
const dataSource = ref<'REAL' | 'MOCK'>('REAL')

const displayRequestId = computed(() => lastRequestId.value || 'N/A')
const displayProcessTime = computed(() => {
  if (!lastProcessTime.value) {
    return 'N/A'
  }

  const value = Number.parseFloat(lastProcessTime.value)
  if (Number.isNaN(value)) {
    return lastProcessTime.value
  }

  return `${value.toFixed(2)}ms`
})

const stats = computed(() => {
  const risingBoards = boardRows.value.filter((row) => parsePercent(row.change) > 0).length
  const fallingBoards = boardRows.value.filter((row) => parsePercent(row.change) < 0).length
  const leadStrength = boardRows.value.length > 0
    ? Math.max(...boardRows.value.map((row) => Math.max(parsePercent(row.change), 0))).toFixed(2)
    : '0.00'

  return {
    activeBoards: boardRows.value.length,
    risingBoards,
    fallingBoards,
    leadStrength
  }
})

function parsePercent(change: string): number {
  return Number.parseFloat(change.replace('%', '')) || 0
}

function formatSigned(value: number, digits = 2): string {
  const normalized = Number.isFinite(value) ? value : 0
  const prefix = normalized > 0 ? '+' : ''
  return `${prefix}${normalized.toFixed(digits)}`
}

function toBoardRows(rows: IndustryFlowRow[]): BoardRow[] {
  return rows.map((row, index) => {
    const change = typeof row.change === 'number'
      ? row.change
      : Number.parseFloat(String(row.change ?? '0')) || 0

    const turnover = typeof row.amount === 'number'
      ? row.amount
      : Number.parseFloat(String(row.amount ?? '0')) || 0

    return {
      rank: typeof row.rank === 'number' ? row.rank : index + 1,
      name: typeof row.name === 'string' && row.name.trim().length > 0 ? row.name : `板块-${index + 1}`,
      change: `${formatSigned(change)}%`,
      turnover: Number(turnover.toFixed(2)),
      netInflow: formatSigned(turnover * (change / 100), 1)
    }
  })
}

function toRotationRows(rows: BoardRow[]): RotationRow[] {
  const windows = ['近1日', '近3日', '近5日', '近10日']
  return rows.slice(0, 4).map((row, index) => ({
    name: row.name,
    window: windows[index] ?? '近1日',
    flow: Number.parseFloat(row.netInflow) || 0
  }))
}

function createMockBoardRows(): BoardRow[] {
  const fallback = mockDashboard.getLeadingSectors()
  if (!Array.isArray(fallback) || fallback.length === 0) {
    return []
  }

  return fallback.slice(0, 8).map((item: { name?: unknown; change?: unknown }, index: number) => {
    const change = typeof item.change === 'number' ? item.change : Number.parseFloat(String(item.change ?? '0')) || 0
    const turnover = Math.abs(change) * 100 + 120 + index * 20

    return {
      rank: index + 1,
      name: typeof item.name === 'string' && item.name.trim().length > 0 ? item.name : `板块-${index + 1}`,
      change: `${formatSigned(change)}%`,
      turnover: Number(turnover.toFixed(2)),
      netInflow: formatSigned(turnover * (change / 100), 1)
    }
  })
}

async function loadIndustryFlow() {
  const data = await exec(() => apiClient.get<UnifiedResponse<IndustryFlowRow[]>>('/v2/market/sector/fund-flow', {
    params: {
      sort: 'change_percent',
      limit: 10
    }
  }), {
    silent: true,
    errorMsg: '板块数据加载失败'
  })

  if (data === null) {
    dataSource.value = 'MOCK'
    boardRows.value = createMockBoardRows()
    rotationRows.value = toRotationRows(boardRows.value)
    return
  }

  const normalizedRows = toBoardRows(Array.isArray(data) ? data : [])

  if (normalizedRows.length === 0) {
    dataSource.value = 'REAL'
    boardRows.value = []
    rotationRows.value = []
    return
  }

  dataSource.value = 'REAL'
  boardRows.value = normalizedRows
  rotationRows.value = toRotationRows(normalizedRows)
}

function refreshBoards() {
  void loadIndustryFlow()
}

void loadIndustryFlow()
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.industry-analysis-page {
  padding: var(--artdeco-spacing-6);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-6);
}

.section-title {
  margin: 0;
  font-size: var(--artdeco-text-2xl);
  color: var(--artdeco-gold-primary);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-6);
}

.content-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: var(--artdeco-spacing-4);
}

.rotation-list {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-3);
}

.rotation-item {
  border: 1px solid var(--artdeco-border-default);
  padding: var(--artdeco-spacing-3);

  .name {
    color: var(--artdeco-fg-primary);
    font-weight: 600;
  }

  .meta {
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-xs);
    margin-top: 2px;
  }

  .value {
    margin-top: var(--artdeco-spacing-2);
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-base);
  }

  .value.rise {
    color: var(--artdeco-rise);
  }

  .value.fall {
    color: var(--artdeco-down);
  }
}
</style>
