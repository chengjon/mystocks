<template>
  <div class="risk-alerts page-enter" :class="{ 'is-embedded': isEmbedded }">
    <section v-if="!isEmbedded" class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">alert governance desk</span>
          <div class="hero-meta">
            <span>REQ_ID: {{ displayRequestId }}</span>
            <span>UNREAD: {{ unreadAlertCount }}</span>
            <span>FOCUS: alert center</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="风险告警工作台"
        subtitle="汇聚告警记录、规则状态和高优先级事件，形成风险治理中的告警节点"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" :loading="loading" @click="fetchRiskAlerts">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新告警
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section v-if="!isEmbedded" class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="规则总数" :value="alertRules.length" variant="gold" />
      <ArtDecoStatCard label="启用规则" :value="activeRuleCount" variant="rise" />
      <ArtDecoStatCard label="未读告警" :value="unreadAlertCount" variant="gold" />
      <ArtDecoStatCard label="高优先级" :value="criticalAlertCount" variant="fall" />
    </section>

    <section :class="isEmbedded ? 'embedded-shell' : 'content-shell artdeco-card-shell'">
      <div v-if="!isEmbedded" class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">alert review route</span>
          <h3 class="content-shell-title">告警记录与规则面板</h3>
          <p class="content-shell-subtitle">{{ contentShellDescription }}</p>
        </div>
        <div class="content-shell-meta">
          <span>RULES: {{ alertRules.length }}</span>
          <span>ALERTS: {{ alertRecords.length }}</span>
        </div>
      </div>

      <div class="stats-grid" v-loading="loading">
        <ArtDecoCard title="规则总数" hoverable>
          <div class="stat-value">{{ alertRules.length }}</div>
        </ArtDecoCard>
        <ArtDecoCard title="启用规则" hoverable>
          <div class="stat-value positive">{{ activeRuleCount }}</div>
        </ArtDecoCard>
        <ArtDecoCard title="未读告警" hoverable>
          <div class="stat-value warning">{{ unreadAlertCount }}</div>
        </ArtDecoCard>
        <ArtDecoCard title="高优先级" hoverable>
          <div class="stat-value danger">{{ criticalAlertCount }}</div>
        </ArtDecoCard>
      </div>

      <ArtDecoCard title="近期告警" class="table-card" hoverable>
        <el-table :data="alertRecords" stripe empty-text="暂无告警记录">
          <el-table-column prop="symbol" label="代码" width="110" />
          <el-table-column prop="stock_name" label="名称" width="140" />
          <el-table-column prop="alert_type" label="告警类型" width="140" />
          <el-table-column label="等级" width="120">
            <template #default="{ row }">
              <el-tag :type="levelTagType(row.alert_level)">{{ levelLabel(row.alert_level) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="alert_message" label="告警内容" min-width="260" show-overflow-tooltip />
          <el-table-column label="时间" width="180">
            <template #default="{ row }">
              <span class="mono">{{ formatTime(row.alert_time || row.created_at) }}</span>
            </template>
          </el-table-column>
        </el-table>
      </ArtDecoCard>

      <ArtDecoCard title="规则列表" class="table-card" hoverable>
        <el-table :data="alertRules" stripe empty-text="暂无规则">
          <el-table-column prop="rule_name" label="规则名" min-width="220" show-overflow-tooltip />
          <el-table-column prop="rule_type" label="规则类型" width="150" />
          <el-table-column prop="symbol" label="标的" width="120" />
          <el-table-column label="启用状态" width="120">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" label="更新时间" width="180">
            <template #default="{ row }">
              <span class="mono">{{ formatTime(row.updated_at || row.created_at) }}</span>
            </template>
          </el-table-column>
        </el-table>
      </ArtDecoCard>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { monitoringApi } from '@/api/index'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { ArtDecoButton, ArtDecoCard, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import type { AlertRecordResponse, AlertRuleResponse } from '@/api/types/common'

type JsonLike = Record<string, unknown>

interface Props {
  functionKey?: string
  userPermissions?: string[]
  systemConfig?: unknown
}

const props = withDefaults(defineProps<Props>(), {
  functionKey: '',
  userPermissions: () => [],
  systemConfig: undefined
})

const { loading, lastRequestId, exec } = useArtDecoApi()
const alertRules = ref<AlertRuleResponse[]>([])
const alertRecords = ref<AlertRecordResponse[]>([])
const requestId = ref('')

const isEmbedded = computed(() => Boolean(props.functionKey))
const displayRequestId = computed(() => requestId.value || 'N/A')
const activeRuleCount = computed(() => alertRules.value.filter((rule) => rule.is_active).length)
const unreadAlertCount = computed(() => alertRecords.value.filter((item) => !item.is_read).length)
const criticalAlertCount = computed(() =>
  alertRecords.value.filter((item) => {
    const level = String(item.alert_level || '').toLowerCase()
    return level === 'critical' || level === 'error' || level === 'danger'
  }).length
)
const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  return unreadAlertCount.value > 0 ? '存在未读告警' : '告警已清空'
})
const pageStatusType = computed(() => (criticalAlertCount.value > 0 ? 'warning' : 'success'))
const contentShellDescription = computed(() => '审查近期告警、规则启用状态和高优先级事件，作为风险治理链路里的告警审阅面板。')

function normalizeList<T>(payload: unknown, keys: string[]): T[] {
  if (Array.isArray(payload)) return payload as T[]
  if (!payload || typeof payload !== 'object') return []

  const dict = payload as JsonLike
  for (const key of keys) {
    const maybe = dict[key]
    if (Array.isArray(maybe)) return maybe as T[]
  }
  return []
}

const fetchRiskAlerts = async (): Promise<void> => {
  const [rulesData, alertsData] = await Promise.all([
    exec(() => monitoringApi.getAlertRules(), { errorMsg: '获取告警规则失败', silent: true }),
    exec(() => monitoringApi.getAlerts({ page: 1, page_size: 50 }), { errorMsg: '获取告警记录失败', silent: true }),
  ])

  alertRules.value = normalizeList<AlertRuleResponse>(rulesData, ['rules', 'items', 'data'])
  alertRecords.value = normalizeList<AlertRecordResponse>(alertsData, ['alerts', 'items', 'records', 'data'])
  requestId.value = lastRequestId.value || requestId.value
}

const levelTagType = (level?: string): 'danger' | 'warning' | 'success' | 'info' => {
  const normalized = String(level || '').toLowerCase()
  if (normalized === 'critical' || normalized === 'error' || normalized === 'danger') return 'danger'
  if (normalized === 'warning') return 'warning'
  if (normalized === 'info') return 'success'
  return 'info'
}

const levelLabel = (level?: string): string => {
  const normalized = String(level || '').toLowerCase()
  if (!normalized) return '未知'
  const map: Record<string, string> = {
    critical: '严重',
    error: '高危',
    danger: '高危',
    warning: '预警',
    info: '提示',
  }
  return map[normalized] || normalized.toUpperCase()
}

const formatTime = (value?: string): string => {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', { hour12: false })
}

onMounted(fetchRiskAlerts)
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.risk-alerts {
  padding: var(--artdeco-spacing-6);
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-6);
}

.risk-alerts.is-embedded {
  padding: 0;
}

.hero-shell,
.stats-strip,
.content-shell,
.embedded-shell {
  width: 100%;
}

.hero-shell,
.content-shell {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-5);
}

.hero-rail,
.content-shell-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--artdeco-spacing-4);
  flex-wrap: wrap;
}

.hero-copy,
.content-shell-copy {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.hero-eyebrow,
.content-shell-kicker {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-gold-dim);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
}

.hero-meta,
.content-shell-meta {
  display: flex;
  gap: var(--artdeco-spacing-3);
  flex-wrap: wrap;
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
}

.content-shell-title {
  margin: 0;
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-xl);
  color: var(--artdeco-fg-primary);
}

.content-shell-subtitle {
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
}

.stats-strip,
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(calc(var(--artdeco-spacing-20) * 3 - var(--artdeco-spacing-10)), 1fr));
  gap: var(--artdeco-spacing-4);
}

.stats-grid {
  margin-bottom: var(--artdeco-spacing-6);
}

.stat-value {
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-3xl);
  line-height: 1;
  color: var(--artdeco-gold-primary);
}

.stat-value.positive {
  color: var(--artdeco-rise);
}

.stat-value.warning {
  color: var(--artdeco-warning);
}

.stat-value.danger {
  color: var(--artdeco-down);
}

.table-card {
  margin-bottom: var(--artdeco-spacing-6);
}

.mono {
  font-family: var(--artdeco-font-mono);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-xs);
}

@media (width <= 75rem) {
  .stats-strip,
  .stats-grid {
    grid-template-columns: repeat(2, minmax(calc(var(--artdeco-spacing-20) * 2 + var(--artdeco-spacing-4)), 1fr));
  }
}

@media (width <= 48rem) {
  .stats-strip,
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .content-shell-meta,
  .hero-meta {
    width: 100%;
  }
}
</style>
