<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { monitoringApi } from '@/api/index'
import type { AlertRecordResponse, AlertRuleResponse } from '@/api/types/common'
import { ArtDecoButton, ArtDecoCard, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard, ArtDecoTable } from '@/components/artdeco'

type JsonLike = Record<string, unknown>

interface OverviewMetricRow {
  metric: string
  value: string
  status: string
}

interface AlertMessageRow {
  level: '高' | '中' | '低'
  content: string
  time: string
}

const { loading, error, lastRequestId, exec } = useArtDecoApi()
const rules = ref<AlertRuleResponse[]>([])
const alertRecords = ref<AlertRecordResponse[]>([])
const activeTab = ref<'overview' | 'rules' | 'alerts'>('overview')
const hasStartedRulesSync = ref(false)
const hasStartedAlertsSync = ref(false)
const hasVerifiedRulesSnapshot = ref(false)
const hasVerifiedAlertsSnapshot = ref(false)
const lastVerifiedRulesRequestId = ref('')
const lastVerifiedAlertsRequestId = ref('')
const latestRulesFailure = ref<string | null>(null)
const latestAlertsFailure = ref<string | null>(null)
const staleRulesError = ref<string | null>(null)
const staleAlertsError = ref<string | null>(null)

const riskOverviewTabMeta = {
  overview: {
    icon: 'RiskManagement',
    label: '风险概览',
    description: '展示风险指标接入状态与当前规则侧真值，未接入的 Beta、波动率和 VaR 指标不会伪装成实时数据。'
  },
  rules: {
    icon: 'AlertConfig',
    label: '规则清单',
    description: '审查当前风险规则、优先级和启用状态，确认治理约束是否完整在线。'
  },
  alerts: {
    icon: 'Alert',
    label: '预警消息',
    description: '聚合当日预警与提示信息，识别当前最需要关注的风险触发点。'
  }
} as const

const overviewMetricLabels = [
  '组合Beta',
  '波动率(20日)',
  '最大回撤(近3月)',
  'VaR(95%)',
] as const

const overviewColumns = [
  { key: 'metric', label: '风险指标' },
  { key: 'value', label: '当前值' },
  { key: 'status', label: '状态', variant: 'color' }
]

function formatRulePriority(value: unknown): string {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return `${Math.trunc(value)}`
  }

  if (typeof value === 'string' && value.trim()) {
    const parsed = Number.parseFloat(value)
    if (Number.isFinite(parsed)) {
      return `${Math.trunc(parsed)}`
    }
    return value
  }

  return '--'
}

const ruleColumns = [
  { key: 'rule_name', label: '规则名称' },
  { key: 'rule_type', label: '类型' },
  { key: 'symbol', label: '目标' },
  { key: 'is_active', label: '状态' },
  { key: 'priority', label: '优先级', format: formatRulePriority }
]

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

function toAlertLevelLabel(level?: string): AlertMessageRow['level'] {
  const normalized = String(level || '').toLowerCase()
  if (normalized === 'critical' || normalized === 'error' || normalized === 'danger') return '高'
  if (normalized === 'warning') return '中'
  return '低'
}

function formatAlertTime(value?: string): string {
  if (!value) return '--:--'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleTimeString('zh-CN', { hour12: false, hour: '2-digit', minute: '2-digit' })
}

const alertMessages = computed<AlertMessageRow[]>(() => alertRecords.value.map((record, index) => ({
  level: toAlertLevelLabel(record.alert_level),
  content: record.alert_message || record.alert_title || record.rule_name || record.alert_type || `风险事件 ${index + 1}`,
  time: formatAlertTime(record.alert_time || record.created_at),
})))

const overviewRows = computed<OverviewMetricRow[]>(() => overviewMetricLabels.map((metric) => ({
  metric,
  value: '未校验',
  status: '待接入',
})))

const hasVerifiedOverviewSnapshot = computed(() => hasVerifiedRulesSnapshot.value && hasVerifiedAlertsSnapshot.value)
const hasAnyVerifiedSlice = computed(() => hasVerifiedRulesSnapshot.value || hasVerifiedAlertsSnapshot.value)
const displayRequestId = computed(() => {
  if (activeTab.value === 'rules') {
    return hasVerifiedRulesSnapshot.value ? (lastVerifiedRulesRequestId.value || 'N/A') : 'N/A'
  }

  if (activeTab.value === 'alerts') {
    return hasVerifiedAlertsSnapshot.value ? (lastVerifiedAlertsRequestId.value || 'N/A') : 'N/A'
  }

  return hasVerifiedOverviewSnapshot.value
    ? (lastVerifiedAlertsRequestId.value || lastVerifiedRulesRequestId.value || 'N/A')
    : 'N/A'
})
const displayAlertCount = computed(() => (hasVerifiedAlertsSnapshot.value ? `${alertRecords.value.length}` : '--'))
const displayRuleCount = computed(() => (hasVerifiedRulesSnapshot.value ? `${rules.value.length}` : '--'))
const statCards = computed(() => {
  return {
    total: hasVerifiedRulesSnapshot.value ? `${rules.value.length}` : '--',
    active: hasVerifiedRulesSnapshot.value ? `${rules.value.filter((r) => r.is_active).length}` : '--',
    alerts: hasVerifiedAlertsSnapshot.value ? `${alertRecords.value.length}` : '--',
    concentration: hasVerifiedRulesSnapshot.value ? '未校验' : '--'
  }
})

const activeTabMeta = computed(() => riskOverviewTabMeta[activeTab.value])
const pageStatusText = computed(() => {
  if (activeTab.value === 'rules') {
    if (staleRulesError.value) return '刷新异常'
    if (latestRulesFailure.value && !hasVerifiedRulesSnapshot.value) return '规则异常'
    if (loading.value) return hasVerifiedRulesSnapshot.value ? '刷新中' : '同步中'
    if (rules.value.length === 0) return '数据为空'
    return '规则在线'
  }

  if (activeTab.value === 'alerts') {
    if (staleAlertsError.value) return '刷新异常'
    if (latestAlertsFailure.value && !hasVerifiedAlertsSnapshot.value) return '预警异常'
    if (loading.value) return hasVerifiedAlertsSnapshot.value ? '刷新中' : '同步中'
    if (alertRecords.value.length === 0) return '数据为空'
    return '预警在线'
  }

  if (staleRulesError.value || staleAlertsError.value) return '刷新异常'
  if ((latestRulesFailure.value && !hasVerifiedRulesSnapshot.value) || (latestAlertsFailure.value && !hasVerifiedAlertsSnapshot.value)) {
    return hasAnyVerifiedSlice.value ? '部分同步' : '同步异常'
  }
  if (loading.value) return hasVerifiedOverviewSnapshot.value ? '刷新中' : '同步中'
  if (rules.value.length === 0 && alertRecords.value.length === 0) return '数据为空'
  if (alertRecords.value.length > 0) return '预警在线'
  if (rules.value.length > 0) return '规则在线'
  return '观察中'
})
const pageStatusType = computed(() => {
  if (staleRulesError.value || staleAlertsError.value) return 'warning'
  if ((latestRulesFailure.value && !hasVerifiedRulesSnapshot.value) || (latestAlertsFailure.value && !hasVerifiedAlertsSnapshot.value)) {
    return hasAnyVerifiedSlice.value ? 'warning' : 'info'
  }
  if (rules.value.length === 0 && alertRecords.value.length === 0) return 'info'
  return alertMessages.value.some((item) => item.level === '高') ? 'warning' : 'success'
})
const runtimeMessage = computed(() => {
  if (activeTab.value === 'rules') {
    if (staleRulesError.value) return `${staleRulesError.value}，当前仍显示上次成功同步的风险规则快照。`
    if (latestRulesFailure.value && !hasVerifiedRulesSnapshot.value) return `${latestRulesFailure.value}，当前暂无已验证风险规则快照。`
    if (latestAlertsFailure.value && !hasVerifiedAlertsSnapshot.value) return `${latestAlertsFailure.value}，当前预警消息暂不可用。`
    if (loading.value) return hasVerifiedRulesSnapshot.value ? '风险规则刷新中...' : '风险规则同步中...'
    if (rules.value.length === 0) return '当前暂无风险规则。'
    return ''
  }

  if (activeTab.value === 'alerts') {
    if (staleAlertsError.value) return `${staleAlertsError.value}，当前仍显示上次成功同步的预警快照。`
    if (latestAlertsFailure.value && !hasVerifiedAlertsSnapshot.value) return `${latestAlertsFailure.value}，当前暂无已验证预警快照。`
    if (loading.value) return hasVerifiedAlertsSnapshot.value ? '风险预警刷新中...' : '风险预警同步中...'
    if (alertMessages.value.length === 0) return '暂无预警消息。'
    return ''
  }

  if ((staleRulesError.value || staleAlertsError.value) && hasVerifiedOverviewSnapshot.value) {
    return `${staleAlertsError.value || staleRulesError.value}，当前仍显示上次成功同步的风险概览快照。`
  }
  if (hasVerifiedRulesSnapshot.value && latestAlertsFailure.value && !hasVerifiedAlertsSnapshot.value) {
    return `${latestAlertsFailure.value}，当前预警消息暂不可用。`
  }
  if (hasVerifiedAlertsSnapshot.value && latestRulesFailure.value && !hasVerifiedRulesSnapshot.value) {
    return `${latestRulesFailure.value}，当前风控规则暂不可用。`
  }
  if (latestAlertsFailure.value || latestRulesFailure.value) {
    return `${latestAlertsFailure.value || latestRulesFailure.value}，当前暂无已验证风险概览快照。`
  }
  if (loading.value) return hasVerifiedOverviewSnapshot.value ? '风险规则与预警刷新中...' : '风险规则与预警同步中...'
  if (activeTab.value === 'overview') return '风险指标仍待接入实时风险引擎，当前概览表仅显示未校验状态。'
  return ''
})

const normalizedRuleRows = computed(() => rules.value.map((r) => ({
  ...r,
  symbol: r.symbol || 'Global',
  is_active: r.is_active ? 'Active' : 'Disabled'
})))

function markVerifiedRulesSnapshot(requestId: string) {
  hasVerifiedRulesSnapshot.value = true
  lastVerifiedRulesRequestId.value = requestId || lastVerifiedRulesRequestId.value
}

function markVerifiedAlertsSnapshot(requestId: string) {
  hasVerifiedAlertsSnapshot.value = true
  lastVerifiedAlertsRequestId.value = requestId || lastVerifiedAlertsRequestId.value
}

const fetchRules = async () => {
  hasStartedRulesSync.value = true
  hasStartedAlertsSync.value = true
  staleRulesError.value = null
  staleAlertsError.value = null
  latestRulesFailure.value = null
  latestAlertsFailure.value = null

  const rulesData = await exec(() => monitoringApi.getAlertRules(), { errorMsg: '获取风控规则失败', silent: true })
  const rulesRequestId = lastRequestId.value || ''
  const rulesError = error.value
  if (rulesData === null) {
    latestRulesFailure.value = rulesError || '风险规则刷新失败'
    if (hasVerifiedRulesSnapshot.value) {
      staleRulesError.value = latestRulesFailure.value
    }
  } else {
    rules.value = normalizeList<AlertRuleResponse>(rulesData, ['rules', 'items', 'data'])
    markVerifiedRulesSnapshot(rulesRequestId)
  }

  const alertsData = await exec(() => monitoringApi.getAlerts({ page: 1, page_size: 50 }), {
    errorMsg: '获取预警记录失败',
    silent: true,
  })
  const alertsRequestId = lastRequestId.value || ''
  const alertsError = error.value
  if (alertsData === null) {
    latestAlertsFailure.value = alertsError || '风险预警刷新失败'
    if (hasVerifiedAlertsSnapshot.value) {
      staleAlertsError.value = latestAlertsFailure.value
    }
    return
  }

  alertRecords.value = normalizeList<AlertRecordResponse>(alertsData, ['alerts', 'items', 'records', 'data'])
  markVerifiedAlertsSnapshot(alertsRequestId)
}

const handleExport = () => {
  ElMessage.info('导出能力待接入，本页暂提供运行态审查。')
}

const handleSettings = () => {
  ElMessage.info('设置入口待接入风险配置工作流。')
}

onMounted(() => {
  void fetchRules()
})
</script>

<template>
  <div class="risk-overview-tab page-enter">
    <section class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">portfolio guard desk</span>
          <div class="hero-meta">
            <span>REQ_ID: {{ displayRequestId }}</span>
            <span>ACTIVE TAB: {{ activeTabMeta.label }}</span>
            <span>ALERTS: {{ displayAlertCount }}</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="风险概览工作台"
        subtitle="统一审查风险指标、治理规则与预警消息，形成风险治理的总览入口"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton variant="outline" priority="ghost" size="sm" @click="handleExport">
            导出摘要
          </ArtDecoButton>
          <ArtDecoButton variant="outline" priority="ghost" size="sm" @click="handleSettings">
            风险设置
          </ArtDecoButton>
          <ArtDecoButton variant="outline" size="sm" :loading="loading" @click="fetchRules">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新概览
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="规则总数" :value="`${statCards.total}`" variant="gold" :show-change="false" />
      <ArtDecoStatCard label="启用规则" :value="`${statCards.active}`" variant="rise" :show-change="false" />
      <ArtDecoStatCard label="今日告警" :value="`${statCards.alerts}`" variant="fall" :show-change="false" />
      <ArtDecoStatCard label="仓位集中度" :value="statCards.concentration" variant="gold" :show-change="false" />
    </section>

    <section class="content-shell artdeco-card-shell">
      <div class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">risk review route</span>
          <h2 class="content-shell-title">{{ activeTabMeta.label }}</h2>
          <p class="content-shell-subtitle">{{ activeTabMeta.description }}</p>
        </div>
        <div class="content-shell-meta">
          <span>TAB: {{ activeTabMeta.label }}</span>
          <span>RULES: {{ displayRuleCount }}</span>
        </div>
      </div>

      <div class="tabs-shell">
        <button class="tab" :class="{ active: activeTab === 'overview' }" @click="activeTab = 'overview'">
          <ArtDecoIcon :name="riskOverviewTabMeta.overview.icon" size="sm" />
          风险概览
        </button>
        <button class="tab" :class="{ active: activeTab === 'rules' }" @click="activeTab = 'rules'">
          <ArtDecoIcon :name="riskOverviewTabMeta.rules.icon" size="sm" />
          规则清单
        </button>
        <button class="tab" :class="{ active: activeTab === 'alerts' }" @click="activeTab = 'alerts'">
          <ArtDecoIcon :name="riskOverviewTabMeta.alerts.icon" size="sm" />
          预警消息
        </button>
      </div>

      <div class="tab-panel" v-loading="loading">
        <p v-if="runtimeMessage" class="runtime-message" aria-live="polite">{{ runtimeMessage }}</p>
        <ArtDecoCard v-if="activeTab === 'overview'" title="组合风险摘要" hoverable>
          <ArtDecoTable :columns="overviewColumns" :data="overviewRows" />
        </ArtDecoCard>

        <ArtDecoCard v-else-if="activeTab === 'rules'" title="风险规则" hoverable>
          <ArtDecoTable v-if="normalizedRuleRows.length > 0" :columns="ruleColumns" :data="normalizedRuleRows" />
          <div v-else class="empty-state">暂无风险规则。</div>
        </ArtDecoCard>

        <ArtDecoCard v-else title="实时预警" hoverable>
          <div v-if="alertMessages.length > 0" class="alerts-list">
            <div class="alert-item" v-for="(item, index) in alertMessages" :key="`${item.content}-${item.time}-${index}`">
              <div class="left">
                <span class="level" :class="`level-${item.level}`">{{ item.level }}风险</span>
                <span class="content">{{ item.content }}</span>
              </div>
              <span class="time">{{ item.time }}</span>
            </div>
          </div>
          <div v-else class="empty-state">暂无预警消息。</div>
        </ArtDecoCard>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.risk-overview-tab {
  padding: var(--artdeco-spacing-6);
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-6);
}

.hero-shell,
.stats-strip,
.content-shell {
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
  letter-spacing: var(--artdeco-tracking-wide);
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

.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}

.tabs-shell {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-2);
  border: 1px solid var(--artdeco-border-default);
  background: var(--artdeco-gold-opacity-05);
  flex-wrap: wrap;
}

.tab {
  display: inline-flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
  border: 1px solid var(--artdeco-border-default);
  background: transparent;
  color: var(--artdeco-fg-muted);
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
  cursor: pointer;
  transition:
    border-color var(--artdeco-transition-base),
    background-color var(--artdeco-transition-base),
    color var(--artdeco-transition-base);
}

.tab:hover {
  border-color: var(--artdeco-border-accent);
  color: var(--artdeco-gold-light);
  background: var(--artdeco-gold-opacity-08);
}

.tab:focus-visible {
  outline: none;
  border-color: var(--artdeco-border-hover);
  box-shadow: 0 0 0 var(--artdeco-spacing-px) var(--artdeco-border-hover);
}

.tab.active {
  border-color: var(--artdeco-gold-primary);
  color: var(--artdeco-gold-primary);
  background: var(--artdeco-gold-opacity-08);
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-3);
}

.alert-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid var(--artdeco-border-default);
  padding: var(--artdeco-spacing-3);
}

.alert-item .left {
  display: flex;
  gap: var(--artdeco-spacing-3);
}

.alert-item .level {
  font-size: var(--artdeco-text-xs);
  font-weight: 600;
}

.alert-item .level-高 { color: var(--artdeco-down); }
.alert-item .level-中 { color: var(--artdeco-warning); }
.alert-item .level-低 { color: var(--artdeco-rise); }

.alert-item .content {
  color: var(--artdeco-fg-primary);
}

.alert-item .time {
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-mono);
}

.runtime-message,
.empty-state {
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
}

@media (width <= 75rem) {
  .stats-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (width <= 48rem) {
  .stats-strip {
    grid-template-columns: 1fr;
  }

  .hero-meta,
  .content-shell-meta {
    width: 100%;
  }

  .tabs-shell {
    align-items: stretch;
  }

  .tab {
    width: 100%;
    justify-content: center;
  }
}
</style>
