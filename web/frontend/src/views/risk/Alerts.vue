<template>
  <div class="risk-alerts page-enter" :class="{ 'is-embedded': isEmbedded }">
    <section v-if="!isEmbedded" class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">风险告警审阅</span>
          <div class="hero-meta">
            <span>REQ_ID: {{ displayRequestId }}</span>
            <span>UNREAD: {{ displayUnreadAlertCount }}</span>
            <span>FOCUS: triage</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="风险告警工作台"
        subtitle="优先审阅未读和高优先级告警，保留规则配置作为次级治理入口"
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

    <section v-if="!isEmbedded" class="stats-strip artdeco-card-shell" aria-label="告警摘要">
      <div v-for="item in summaryStats" :key="item.label" class="compact-stat">
        <span class="compact-stat-label">{{ item.label }}</span>
        <span class="artdeco-stat-value" :class="item.valueClass">{{ item.value }}</span>
      </div>
    </section>

    <section :class="isEmbedded ? 'embedded-shell' : 'content-shell artdeco-card-shell'">
      <div v-if="!isEmbedded" class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">告警审阅</span>
          <h2 class="content-shell-title">告警分诊队列</h2>
          <p class="content-shell-subtitle">{{ contentShellDescription }}</p>
        </div>
        <div class="content-shell-meta">
          <span>RULES: {{ displayRuleCount }}</span>
          <span>ALERTS: {{ displayAlertCount }}</span>
        </div>
      </div>

      <div class="triage-control-row" data-test="risk-alerts-triage-controls" aria-label="告警分诊筛选">
        <div class="triage-control-group" role="group" aria-label="告警等级筛选">
          <button
            v-for="option in severityFilters"
            :key="option.value"
            type="button"
            class="triage-control"
            :class="{ 'is-active': activeAlertFilter === option.value }"
            :aria-pressed="activeAlertFilter === option.value"
            :data-test="option.testId"
            @click="activeAlertFilter = option.value"
          >
            <span>{{ option.label }}</span>
            <strong>{{ option.count }}</strong>
          </button>
        </div>
        <button
          type="button"
          class="triage-control triage-control-unread"
          :class="{ 'is-active': activeAlertFilter === 'unread' }"
          :aria-pressed="activeAlertFilter === 'unread'"
          data-test="risk-alerts-filter-unread"
          @click="activeAlertFilter = activeAlertFilter === 'unread' ? 'all' : 'unread'"
        >
          <span>仅未读</span>
          <strong>{{ unreadAlertCount }}</strong>
        </button>
      </div>

      <div class="runtime-status-strip" data-test="risk-alerts-runtime-strip" aria-live="polite">
        <div>
          <span class="runtime-status-label">{{ pageStatusText }}</span>
          <p>{{ visibleRuntimeMessage }}</p>
        </div>
        <div class="runtime-status-meta">
          <span>VISIBLE: {{ displayVisibleAlertCount }}</span>
          <span>REQ_ID: {{ displayRequestId }}</span>
        </div>
      </div>

      <ArtDecoCard title="近期告警" class="table-card" hoverable>
        <div v-if="!loading && hasVerifiedAlertsSnapshot && filteredAlertRecords.length === 0" class="empty-state">
          {{ visibleAlertsEmptyText }}
        </div>
        <div class="alerts-table-shell" data-test="risk-alerts-table">
          <el-table :data="filteredAlertRecords" stripe :empty-text="visibleAlertsEmptyText">
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
        </div>
      </ArtDecoCard>

      <section class="rule-management-secondary" data-test="risk-alerts-rules-secondary" aria-labelledby="risk-alerts-rules-title">
        <div class="rule-management-heading">
          <div>
            <span class="content-shell-kicker">次级配置</span>
            <h2 id="risk-alerts-rules-title">规则配置</h2>
          </div>
          <p>规则创建、启停和删除留在配置区，不打断告警审阅队列。</p>
        </div>
        <AlertRuleManagementPanel
          :alert-rules="alertRules"
          :editable="!isEmbedded"
          :format-time="formatTime"
          :has-verified-rules-snapshot="hasVerifiedRulesSnapshot"
          :loading="loading"
          :mutation-message="ruleMutationMessage"
          :rules-empty-text="rulesEmptyText"
          @create-rule="createRule"
          @delete-rule="deleteRule"
          @update-rule="updateRule"
        />
      </section>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { monitoringApi } from '@/api/index'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { ArtDecoButton, ArtDecoCard, ArtDecoHeader, ArtDecoIcon } from '@/components/artdeco'
import type { AlertRecordResponse, AlertRuleResponse } from '@/api/types/common'
import AlertRuleManagementPanel from './AlertRuleManagementPanel.vue'

type JsonLike = Record<string, unknown>
type AlertRuleMutationResponse = { success?: boolean; message?: string; data?: unknown }
type AlertTriageFilter = 'all' | 'unread' | 'critical' | 'warning' | 'normal'

interface Props {
  functionKey?: string
  userPermissions?: string[]
  systemConfig?: unknown
}

const props = defineProps<Props>()

const { loading, error, lastRequestId, exec } = useArtDecoApi()
const alertRules = ref<AlertRuleResponse[]>([])
const alertRecords = ref<AlertRecordResponse[]>([])
const hasVerifiedRulesSnapshot = ref(false)
const hasVerifiedAlertsSnapshot = ref(false)
const lastVerifiedRulesRequestId = ref('')
const lastVerifiedAlertsRequestId = ref('')
const lastVerifiedRouteRequestId = ref('')
const latestRulesFailure = ref<string | null>(null)
const latestAlertsFailure = ref<string | null>(null)
const staleRulesError = ref<string | null>(null)
const staleAlertsError = ref<string | null>(null)
const ruleMutationMessage = ref('')
const activeAlertFilter = ref<AlertTriageFilter>('all')

const isEmbedded = computed(() => Boolean(props.functionKey))
const hasVerifiedFullSnapshot = computed(() => hasVerifiedRulesSnapshot.value && hasVerifiedAlertsSnapshot.value)
const hasAnyVerifiedSlice = computed(() => hasVerifiedRulesSnapshot.value || hasVerifiedAlertsSnapshot.value)
const displayRequestId = computed(() =>
  hasVerifiedFullSnapshot.value
    ? (lastVerifiedRouteRequestId.value || lastVerifiedAlertsRequestId.value || lastVerifiedRulesRequestId.value || 'N/A')
    : 'N/A'
)
const displayRuleCount = computed(() => (hasVerifiedRulesSnapshot.value ? `${alertRules.value.length}` : '--'))
const displayAlertCount = computed(() => (hasVerifiedAlertsSnapshot.value ? `${alertRecords.value.length}` : '--'))
const displayUnreadAlertCount = computed(() => (hasVerifiedAlertsSnapshot.value ? `${unreadAlertCount.value}` : '--'))
const displayVisibleAlertCount = computed(() => (hasVerifiedAlertsSnapshot.value ? `${filteredAlertRecords.value.length}` : '--'))
const statCards = computed(() => {
  return {
    total: hasVerifiedRulesSnapshot.value ? `${alertRules.value.length}` : '--',
    active: hasVerifiedRulesSnapshot.value ? `${activeRuleCount.value}` : '--',
    unread: hasVerifiedAlertsSnapshot.value ? `${unreadAlertCount.value}` : '--',
    critical: hasVerifiedAlertsSnapshot.value ? `${criticalAlertCount.value}` : '--',
  }
})
const summaryStats = computed(() => [
  { label: '规则总数', value: statCards.value.total, valueClass: 'artdeco-stat-value-gold' },
  { label: '启用规则', value: statCards.value.active, valueClass: 'artdeco-stat-value-rise' },
  { label: '未读告警', value: statCards.value.unread, valueClass: 'artdeco-stat-value-gold' },
  { label: '高优先级', value: statCards.value.critical, valueClass: 'artdeco-stat-value-fall' },
])
const activeRuleCount = computed(() => alertRules.value.filter((rule) => rule.is_active).length)
const unreadAlertCount = computed(() => alertRecords.value.filter((item) => !item.is_read).length)
const warningAlertCount = computed(() => alertRecords.value.filter((item) => normalizeAlertLevel(item.alert_level) === 'warning').length)
const normalAlertCount = computed(() => alertRecords.value.filter((item) => isNormalPriorityAlert(item)).length)
const criticalAlertCount = computed(() =>
  alertRecords.value.filter((item) => isHighPriorityAlert(item)).length
)
const severityFilters = computed(() => [
  {
    value: 'all' as const,
    label: '全部',
    count: alertRecords.value.length,
    testId: 'risk-alerts-filter-all',
  },
  {
    value: 'critical' as const,
    label: '高优先级',
    count: criticalAlertCount.value,
    testId: 'risk-alerts-filter-critical',
  },
  {
    value: 'warning' as const,
    label: '预警',
    count: warningAlertCount.value,
    testId: 'risk-alerts-filter-warning',
  },
  {
    value: 'normal' as const,
    label: '普通',
    count: normalAlertCount.value,
    testId: 'risk-alerts-filter-normal',
  },
])
const filteredAlertRecords = computed(() => {
  const records = [...alertRecords.value].sort((left, right) => alertSortRank(left) - alertSortRank(right))

  if (activeAlertFilter.value === 'unread') return records.filter((item) => !item.is_read)
  if (activeAlertFilter.value === 'critical') return records.filter((item) => isHighPriorityAlert(item))
  if (activeAlertFilter.value === 'warning') return records.filter((item) => normalizeAlertLevel(item.alert_level) === 'warning')
  if (activeAlertFilter.value === 'normal') return records.filter((item) => isNormalPriorityAlert(item))
  return records
})
const rulesEmptyText = computed(() => {
  if (loading.value && !hasVerifiedRulesSnapshot.value) return '风险规则同步中'
  if (latestRulesFailure.value && !hasVerifiedRulesSnapshot.value) return '当前告警规则暂不可用'
  return '暂无规则'
})
const alertsEmptyText = computed(() => {
  if (loading.value && !hasVerifiedAlertsSnapshot.value) return '告警记录同步中'
  if (latestAlertsFailure.value && !hasVerifiedAlertsSnapshot.value) return '当前告警记录暂不可用'
  return '当前无告警记录，风险告警队列为空。'
})
const pageStatusText = computed(() => {
  if (staleRulesError.value || staleAlertsError.value) return '刷新异常'
  if ((latestRulesFailure.value && !hasVerifiedRulesSnapshot.value) || (latestAlertsFailure.value && !hasVerifiedAlertsSnapshot.value)) {
    return hasAnyVerifiedSlice.value ? '部分同步' : '同步异常'
  }
  if (loading.value) return hasAnyVerifiedSlice.value ? '刷新中' : '同步中'
  if (hasVerifiedRulesSnapshot.value && hasVerifiedAlertsSnapshot.value && alertRules.value.length === 0 && alertRecords.value.length === 0) {
    return '告警为空'
  }
  if (hasVerifiedAlertsSnapshot.value && unreadAlertCount.value > 0) return '存在未读告警'
  if (hasAnyVerifiedSlice.value) return '告警在线'
  return '同步中'
})
const pageStatusType = computed(() => {
  if (staleRulesError.value || staleAlertsError.value) return 'warning'
  if ((latestRulesFailure.value && !hasVerifiedRulesSnapshot.value) || (latestAlertsFailure.value && !hasVerifiedAlertsSnapshot.value)) {
    return hasAnyVerifiedSlice.value ? 'warning' : 'info'
  }
  if (hasVerifiedRulesSnapshot.value && hasVerifiedAlertsSnapshot.value && alertRules.value.length === 0 && alertRecords.value.length === 0) {
    return 'info'
  }
  return hasVerifiedAlertsSnapshot.value && criticalAlertCount.value > 0 ? 'warning' : 'success'
})
const contentShellDescription = computed(() => '审查近期告警、规则启用状态和高优先级事件，作为风险治理链路里的告警审阅面板。')
const visibleRuntimeMessage = computed(() => {
  if (runtimeMessage.value) return runtimeMessage.value
  if (hasVerifiedAlertsSnapshot.value) {
    return `当前显示 ${filteredAlertRecords.value.length} 条告警，未读 ${unreadAlertCount.value} 条，高优先级 ${criticalAlertCount.value} 条。`
  }
  return '等待风险告警同步结果。'
})
const visibleAlertsEmptyText = computed(() => {
  if (loading.value && !hasVerifiedAlertsSnapshot.value) return alertsEmptyText.value
  if (latestAlertsFailure.value && !hasVerifiedAlertsSnapshot.value) return alertsEmptyText.value
  if (alertRecords.value.length === 0) return '当前无告警记录，风险告警队列为空。'
  return '当前筛选条件下无告警记录。'
})
const runtimeMessage = computed(() => {
  if (staleRulesError.value && staleAlertsError.value) {
    return `${staleAlertsError.value || staleRulesError.value}，当前仍显示上次成功同步的告警快照。`
  }
  if (staleAlertsError.value) return `${staleAlertsError.value}，当前仍显示上次成功同步的告警记录快照。`
  if (staleRulesError.value) return `${staleRulesError.value}，当前仍显示上次成功同步的告警规则快照。`
  if (latestAlertsFailure.value && !hasVerifiedAlertsSnapshot.value && hasVerifiedRulesSnapshot.value) {
    return `${latestAlertsFailure.value}，当前告警记录暂不可用。`
  }
  if (latestRulesFailure.value && !hasVerifiedRulesSnapshot.value && hasVerifiedAlertsSnapshot.value) {
    return `${latestRulesFailure.value}，当前告警规则暂不可用。`
  }
  if (latestAlertsFailure.value || latestRulesFailure.value) {
    return `${latestAlertsFailure.value || latestRulesFailure.value}，当前暂无已验证告警快照。`
  }
  if (loading.value) return hasAnyVerifiedSlice.value ? '风险告警刷新中...' : '风险告警同步中...'
  if (hasVerifiedRulesSnapshot.value && hasVerifiedAlertsSnapshot.value && alertRules.value.length === 0 && alertRecords.value.length === 0) {
    return '当前没有可展示的告警记录或规则。'
  }
  return ''
})

function normalizeAlertLevel(level?: string): string {
  return String(level || '').toLowerCase()
}

function isHighPriorityAlert(item: AlertRecordResponse): boolean {
  const level = normalizeAlertLevel(item.alert_level)
  return level === 'critical' || level === 'error' || level === 'danger' || level === 'high'
}

function isNormalPriorityAlert(item: AlertRecordResponse): boolean {
  const level = normalizeAlertLevel(item.alert_level)
  return level === 'info' || level === 'normal' || level === 'low' || !level
}

function alertSortRank(item: AlertRecordResponse): number {
  if (!item.is_read && isHighPriorityAlert(item)) return 0
  if (isHighPriorityAlert(item)) return 1
  if (!item.is_read) return 2
  if (normalizeAlertLevel(item.alert_level) === 'warning') return 3
  return 4
}

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

function mutationFailed(response: AlertRuleMutationResponse): string {
  if (response?.success === false) return response.message || '告警规则操作失败'
  return ''
}

async function createRule(payload: Record<string, unknown>): Promise<void> {
  ruleMutationMessage.value = ''
  const response = await monitoringApi.createAlertRule(payload)
  const failure = mutationFailed(response)
  if (failure) {
    ruleMutationMessage.value = failure
    return
  }

  await fetchRiskAlerts()
}

async function updateRule(id: string, payload: Record<string, unknown>): Promise<void> {
  ruleMutationMessage.value = ''
  const response = await monitoringApi.updateAlertRule(id, payload)
  const failure = mutationFailed(response)
  if (failure) {
    ruleMutationMessage.value = failure
    return
  }

  await fetchRiskAlerts()
}

async function deleteRule(id: string): Promise<void> {
  ruleMutationMessage.value = ''
  const response = await monitoringApi.deleteAlertRule(id)
  const failure = mutationFailed(response)
  if (failure) {
    ruleMutationMessage.value = failure
    return
  }

  await fetchRiskAlerts()
}

const fetchRiskAlerts = async (): Promise<void> => {
  staleRulesError.value = null
  staleAlertsError.value = null
  latestRulesFailure.value = null
  latestAlertsFailure.value = null

  const rulesData = await exec(() => monitoringApi.getAlertRules(), { errorMsg: '获取告警规则失败', silent: true })
  const rulesRequestId = lastRequestId.value || ''
  const rulesError = error.value
  if (rulesData === null) {
    latestRulesFailure.value = rulesError || '风险告警规则刷新失败'
    if (hasVerifiedRulesSnapshot.value) {
      staleRulesError.value = latestRulesFailure.value
    }
  } else {
    alertRules.value = normalizeList<AlertRuleResponse>(rulesData, ['rules', 'items', 'data'])
    hasVerifiedRulesSnapshot.value = true
    lastVerifiedRulesRequestId.value = rulesRequestId || lastVerifiedRulesRequestId.value
  }

  const alertsData = await exec(() => monitoringApi.getAlerts({ page: 1, page_size: 50 }), {
    errorMsg: '获取告警记录失败',
    silent: true,
  })
  const alertsRequestId = lastRequestId.value || ''
  const alertsError = error.value
  if (alertsData === null) {
    latestAlertsFailure.value = alertsError || '风险告警记录刷新失败'
    if (hasVerifiedAlertsSnapshot.value) {
      staleAlertsError.value = latestAlertsFailure.value
    }
    return
  }

  alertRecords.value = normalizeList<AlertRecordResponse>(alertsData, ['alerts', 'items', 'records', 'data'])
  hasVerifiedAlertsSnapshot.value = true
  lastVerifiedAlertsRequestId.value = alertsRequestId || lastVerifiedAlertsRequestId.value

  if (rulesData !== null) {
    lastVerifiedRouteRequestId.value = alertsRequestId || rulesRequestId || lastVerifiedRouteRequestId.value
  }
}

const levelTagType = (level?: string): 'danger' | 'warning' | 'success' | 'info' => {
  const normalized = normalizeAlertLevel(level)
  if (normalized === 'critical' || normalized === 'error' || normalized === 'danger' || normalized === 'high') return 'danger'
  if (normalized === 'warning') return 'warning'
  if (normalized === 'info') return 'success'
  return 'info'
}

const levelLabel = (level?: string): string => {
  const normalized = normalizeAlertLevel(level)
  if (!normalized) return '未知'
  const map: Record<string, string> = {
    critical: '严重',
    error: '高危',
    danger: '高危',
    high: '高危',
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

onMounted(() => {
  void fetchRiskAlerts()
})
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

.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(calc(var(--artdeco-spacing-20) * 3 - var(--artdeco-spacing-10)), 1fr));
  gap: var(--artdeco-spacing-3);
}

.compact-stat {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--artdeco-spacing-3);
  min-height: calc(var(--artdeco-spacing-10) + var(--artdeco-spacing-2));
  padding: var(--artdeco-spacing-3);
  border: 1px solid var(--artdeco-border-subtle);
  border-radius: var(--artdeco-radius-md);
  background: var(--artdeco-bg-elevated);
}

.compact-stat-label {
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
}

.compact-stat .artdeco-stat-value {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-lg);
  font-weight: 600;
  line-height: 1;
}

.compact-stat .artdeco-stat-value-gold {
  color: var(--artdeco-gold-primary);
}

.compact-stat .artdeco-stat-value-rise {
  color: var(--artdeco-rise);
}

.compact-stat .artdeco-stat-value-fall {
  color: var(--artdeco-down);
}

.content-shell {
  gap: var(--artdeco-spacing-4);
}

.triage-control-row {
  display: flex;
  justify-content: space-between;
  gap: var(--artdeco-spacing-4);
  flex-wrap: wrap;
  padding: var(--artdeco-spacing-3);
  border: 1px solid var(--artdeco-border-subtle);
  border-radius: var(--artdeco-radius-lg);
  background: var(--artdeco-bg-card);
}

.triage-control-group {
  display: flex;
  gap: var(--artdeco-spacing-2);
  flex-wrap: wrap;
}

.triage-control {
  min-height: calc(var(--artdeco-spacing-10) + var(--artdeco-spacing-1));
  display: inline-flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
  padding: 0 var(--artdeco-spacing-3);
  border: 1px solid var(--artdeco-border-subtle);
  border-radius: var(--artdeco-radius-md);
  background: var(--artdeco-bg-elevated);
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-sans);
  font-size: var(--artdeco-text-sm);
  cursor: pointer;
  transition:
    border-color 160ms ease,
    background-color 160ms ease,
    color 160ms ease;
}

.triage-control strong {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-primary);
}

.triage-control:hover,
.triage-control:focus-visible {
  border-color: var(--artdeco-border-default);
  color: var(--artdeco-fg-primary);
  outline: none;
}

.triage-control.is-active {
  border-color: var(--artdeco-border-active);
  background: var(--artdeco-gold-opacity-08);
  color: var(--artdeco-gold-primary);
}

.triage-control-unread {
  margin-left: auto;
}

.runtime-status-strip {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--artdeco-spacing-4);
  padding: var(--artdeco-spacing-4);
  border: 1px solid var(--artdeco-border-subtle);
  border-radius: var(--artdeco-radius-lg);
  background: var(--artdeco-bg-elevated);
}

.runtime-status-strip p {
  margin: var(--artdeco-spacing-1) 0 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
}

.runtime-status-label {
  font-family: var(--artdeco-font-display);
  color: var(--artdeco-fg-primary);
  font-size: var(--artdeco-text-base);
}

.runtime-status-meta {
  display: flex;
  gap: var(--artdeco-spacing-3);
  flex-wrap: wrap;
  justify-content: flex-end;
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
}

.runtime-message,
.empty-state {
  margin: 0 0 var(--artdeco-spacing-4);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
}

.table-card {
  margin-bottom: var(--artdeco-spacing-6);
}

.alerts-table-shell {
  overflow: hidden;
}

.rule-management-secondary {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-4);
  padding-top: var(--artdeco-spacing-2);
}

.rule-management-heading {
  display: flex;
  justify-content: space-between;
  gap: var(--artdeco-spacing-4);
  flex-wrap: wrap;
  padding: var(--artdeco-spacing-4);
  border: 1px solid var(--artdeco-border-subtle);
  border-radius: var(--artdeco-radius-lg);
  background: var(--artdeco-bg-elevated);
}

.rule-management-heading h2 {
  margin: var(--artdeco-spacing-1) 0 0;
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-lg);
  color: var(--artdeco-fg-primary);
}

.rule-management-heading p {
  max-width: 34rem;
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
}

.mono {
  font-family: var(--artdeco-font-mono);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-xs);
}

@media (width <= 75rem) {
  .stats-strip {
    grid-template-columns: repeat(2, minmax(calc(var(--artdeco-spacing-20) * 2 + var(--artdeco-spacing-4)), 1fr));
  }
}

@media (width <= 48rem) {
  .stats-strip {
    grid-template-columns: 1fr;
  }

  .content-shell-meta,
  .hero-meta {
    width: 100%;
  }
}
</style>
