<template>
  <div class="system-settings-page">
    <div class="page-header">
      <div>
        <h2 class="section-title">系统配置中心</h2>
        <div class="header-meta">
          <span>DATA: {{ activeDataSource }}</span>
          <span>REQ_ID: {{ displayRequestId }}</span>
          <span>TIME: {{ displayProcessTime }}</span>
        </div>
      </div>
      <ArtDecoButton variant="solid" size="sm" @click="saveAll">{{ saveButtonLabel }}</ArtDecoButton>
    </div>

    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="tab"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <p v-if="runtimeMessage" class="runtime-message" aria-live="polite">{{ runtimeMessage }}</p>

    <div class="analysis-blocker" role="status" aria-live="polite">
      <p>
        System-Config 仍按分段真相运行，不存在单体统一后端存储；
        当前页面保留健康监控视图，并按 section owner 分别读取和写入。
      </p>
      <p>general 与 security 已接入系统级 /api/v1/system/settings/* 契约。</p>
      <p>数据源配置使用系统级后端契约，通知偏好使用用户级 /api/notification/preferences 契约。</p>
      <p>下方“系统设置”表单直接写入 general section 的系统级后端真相，不再使用本地草稿持久化。</p>
      <p>下方“安全设置”表单直接写入 security section 的系统级后端真相，不再使用本地草稿持久化。</p>
    </div>

    <template v-if="activeTab === 'sources'">
      <div class="stats-grid">
        <ArtDecoStatCard label="可见端点" :value="sourceStatTotal" variant="gold" :show-change="false" />
        <ArtDecoStatCard label="已启用" :value="sourceStatEnabled" variant="rise" :show-change="false" />
        <ArtDecoStatCard label="写回能力" :value="sourceWriteCapability" variant="gold" :show-change="false" />
        <ArtDecoStatCard label="当前请求" :value="sourceDisplayRequestId" variant="gold" :show-change="false" />
      </div>
      <ArtDecoCard title="数据源配置清单" hoverable>
        <ArtDecoTable :columns="sourceColumns" :data="sourceRows" />
      </ArtDecoCard>
    </template>

    <template v-if="activeTab === 'settings'">
      <ArtDecoCard title="核心参数" hoverable>
        <div class="form-grid">
          <div class="field">
            <label>后端地址</label>
            <ArtDecoInput v-model="form.backendUrl" />
          </div>
          <div class="field">
            <label>回测最大并发</label>
            <ArtDecoInput v-model="form.maxBacktestJobs" />
          </div>
          <div class="field">
            <label>默认滑点(%)</label>
            <ArtDecoInput v-model="form.slippage" />
          </div>
          <div class="field">
            <label>交易手续费(万分比)</label>
            <ArtDecoInput v-model="form.feeRate" />
          </div>
        </div>
      </ArtDecoCard>
    </template>

    <template v-if="activeTab === 'security'">
      <ArtDecoCard title="安全参数" hoverable>
        <div class="form-grid">
          <div class="field">
            <label>会话超时(分钟)</label>
            <ArtDecoInput v-model="securityForm.sessionTimeoutMinutes" />
          </div>
          <div class="field">
            <label>密码策略</label>
            <select v-model="securityForm.passwordPolicyLevel" class="field-select">
              <option value="standard">standard</option>
              <option value="strict">strict</option>
            </select>
          </div>
          <label class="checkbox-field">
            <span>强制多因子认证</span>
            <input
              :checked="securityForm.mfaRequired"
              class="checkbox-control"
              type="checkbox"
              @change="securityForm.mfaRequired = ($event.target as HTMLInputElement).checked"
            />
          </label>
          <label class="checkbox-field">
            <span>启用 IP 白名单</span>
            <input
              :checked="securityForm.ipAllowlistEnabled"
              class="checkbox-control"
              type="checkbox"
              @change="securityForm.ipAllowlistEnabled = ($event.target as HTMLInputElement).checked"
            />
          </label>
        </div>
      </ArtDecoCard>
    </template>

    <template v-if="activeTab === 'monitor'">
      <ArtDecoCard title="API性能监控" hoverable>
        <ArtDecoTable v-if="apiRows.length > 0" :columns="apiColumns" :data="apiRows" />
        <div v-else class="empty-state">暂无系统监控接口数据。</div>
      </ArtDecoCard>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { ArtDecoButton, ArtDecoCard, ArtDecoInput, ArtDecoStatCard, ArtDecoTable } from '@/components/artdeco'
import { monitoringApi } from '@/api'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { API_BASE_URL } from '@/config/runtime-endpoints'
import { normalizeSystemSettingsMonitorRows, type MonitorRow } from '@/views/artdeco-pages/system-tabs/systemSettingsMonitorData.ts'
import { normalizeSystemHealthProbeResponse } from './healthProbeContract'
import {
  extractDataSourceConfigItems,
  type NormalizedDataSourceConfigItem as DataSourceConfigItem,
} from '@/views/artdeco-pages/system-tabs/dataManagementData'
import { supportsDataSourceConfigWrite } from '@/views/artdeco-pages/system-tabs/dataManagementCapabilities'

const tabs = [
  { key: 'sources', label: '数据源' },
  { key: 'settings', label: '系统设置' },
  { key: 'security', label: '安全设置' },
  { key: 'monitor', label: '系统监控' }
]

const activeTab = ref('sources')

const form = reactive({
  backendUrl: API_BASE_URL,
  maxBacktestJobs: '4',
  slippage: '0.05',
  feeRate: '2.5'
})
const securityForm = reactive({
  sessionTimeoutMinutes: '120',
  mfaRequired: false,
  ipAllowlistEnabled: false,
  passwordPolicyLevel: 'standard' as 'standard' | 'strict',
})

const { loading, error, exec } = useArtDecoApi()
const generalSource = ref<'PENDING' | 'REAL' | 'UNAVAILABLE'>('PENDING')
const securitySource = ref<'PENDING' | 'REAL' | 'UNAVAILABLE'>('PENDING')
const monitorSource = ref<'PENDING' | 'REAL' | 'SUMMARY' | 'UNAVAILABLE'>('PENDING')
const sourceTabSource = ref<'PENDING' | 'REAL' | 'UNAVAILABLE'>('PENDING')
const monitorLoading = ref(false)
const monitorMessage = ref('')
const sourceLoading = ref(false)
const sourceMessage = ref('')
const sourceConfigItems = ref<DataSourceConfigItem[]>([])
const generalRequestId = ref('')
const generalProcessTime = ref('')
const securityRequestId = ref('')
const securityProcessTime = ref('')
const monitorRequestId = ref('')
const monitorProcessTime = ref('')
const sourceRequestId = ref('')
const sourceProcessTime = ref('')
const sourceWriteEnabled = supportsDataSourceConfigWrite()

const sourceColumns = [
  { key: 'name', label: '数据源' },
  { key: 'status', label: '状态' },
  { key: 'endpointName', label: '端点标识' },
  { key: 'endpoint', label: '端点' }
]

const apiColumns = [
  { key: 'endpoint', label: '接口' },
  { key: 'qps', label: 'QPS' },
  { key: 'p95', label: 'P95 延迟(ms)' },
  { key: 'errorRate', label: '错误率' }
]

const apiRows = ref<MonitorRow[]>([])
const sourceRows = computed(() =>
  sourceConfigItems.value.map((item) => ({
    name: item.name,
    status: item.enabled ? '启用' : '维护',
    endpointName: item.endpointName,
    endpoint: item.endpoint,
  }))
)
const hasVerifiedSourceSnapshot = computed(() => sourceTabSource.value === 'REAL')
const sourceStatTotal = computed(() => (hasVerifiedSourceSnapshot.value ? `${sourceConfigItems.value.length}` : '--'))
const sourceStatEnabled = computed(() => (
  hasVerifiedSourceSnapshot.value ? `${sourceConfigItems.value.filter((item) => item.enabled).length}` : '--'
))
const sourceWriteCapability = computed(() => (sourceWriteEnabled ? 'ON' : 'OFF'))
const sourceDisplayRequestId = computed(() => sourceRequestId.value || 'N/A')
const saveButtonLabel = computed(() => (activeTab.value === 'security' ? '保存安全设置' : '保存系统设置'))
const activeDataSource = computed(() => {
  if (activeTab.value === 'sources') {
    return sourceTabSource.value
  }

  if (activeTab.value === 'security') {
    return securitySource.value
  }

  if (activeTab.value === 'monitor') {
    return monitorSource.value
  }

  return generalSource.value
})

function formatProcessTime(value: string) {
  if (!value) {
    return 'N/A'
  }

  const parsed = Number.parseFloat(value)
  if (Number.isNaN(parsed)) {
    return value
  }

  return `${parsed.toFixed(2)}ms`
}

const displayRequestId = computed(() => {
  if (activeTab.value === 'sources') {
    return sourceRequestId.value || 'N/A'
  }

  if (activeTab.value === 'security') {
    return securityRequestId.value || 'N/A'
  }

  if (activeTab.value === 'monitor') {
    return monitorRequestId.value || 'N/A'
  }

  return generalRequestId.value || 'N/A'
})

const displayProcessTime = computed(() => {
  if (activeTab.value === 'sources') {
    return formatProcessTime(sourceProcessTime.value)
  }

  if (activeTab.value === 'security') {
    return formatProcessTime(securityProcessTime.value)
  }

  if (activeTab.value === 'monitor') {
    return formatProcessTime(monitorProcessTime.value)
  }

  return formatProcessTime(generalProcessTime.value)
})
const runtimeMessage = computed(() => {
  if (activeTab.value === 'sources') {
    if (sourceLoading.value) return '数据源配置同步中...'
    if (sourceMessage.value) return sourceMessage.value
    if (sourceConfigItems.value.length === 0) return '当前没有可展示的数据源配置。'
    return ''
  }

  if (activeTab.value === 'monitor') {
    if (monitorLoading.value) return '系统监控同步中...'
    if (monitorMessage.value) return monitorMessage.value
    if (apiRows.value.length === 0) return '当前没有可展示的系统监控接口数据。'
    return ''
  }

  if (activeTab.value === 'security') {
    if (loading.value) return '系统安全配置同步中...'
    if (error.value) return error.value
    return ''
  }

  if (loading.value) return '系统配置同步中...'
  if (error.value) return error.value
  return ''
})

function hasConcreteMonitorMetrics(rows: MonitorRow[]) {
  return rows.some((row) => row.qps !== '-' || row.p95 !== '-')
}

function applyMonitorRows(rows: MonitorRow[]) {
  apiRows.value = rows

  if (hasConcreteMonitorMetrics(rows)) {
    monitorSource.value = 'REAL'
    monitorMessage.value = ''
    return
  }

  monitorSource.value = 'SUMMARY'
  monitorMessage.value = '系统健康接口已连通，但当前未返回 API 性能明细；下表仅展示健康摘要。'
}

function applyGeneralSettings(data: Partial<{
  backend_url: string
  max_backtest_jobs: number
  default_slippage_percent: number
  fee_rate_bps: number
}>) {
  if (typeof data.backend_url === 'string' && data.backend_url.trim()) {
    form.backendUrl = data.backend_url
  }
  if (typeof data.max_backtest_jobs === 'number') {
    form.maxBacktestJobs = String(data.max_backtest_jobs)
  }
  if (typeof data.default_slippage_percent === 'number') {
    form.slippage = String(data.default_slippage_percent)
  }
  if (typeof data.fee_rate_bps === 'number') {
    form.feeRate = String(data.fee_rate_bps)
  }
}

function buildGeneralSettingsPayload() {
  return {
    backend_url: form.backendUrl.trim(),
    max_backtest_jobs: Number.parseInt(form.maxBacktestJobs.trim(), 10),
    default_slippage_percent: Number.parseFloat(form.slippage.trim()),
    fee_rate_bps: Number.parseFloat(form.feeRate.trim()),
  }
}

function applySecuritySettings(data: Partial<{
  session_timeout_minutes: number
  mfa_required: boolean
  ip_allowlist_enabled: boolean
  password_policy_level: 'standard' | 'strict'
}>) {
  if (typeof data.session_timeout_minutes === 'number') {
    securityForm.sessionTimeoutMinutes = String(data.session_timeout_minutes)
  }
  if (typeof data.mfa_required === 'boolean') {
    securityForm.mfaRequired = data.mfa_required
  }
  if (typeof data.ip_allowlist_enabled === 'boolean') {
    securityForm.ipAllowlistEnabled = data.ip_allowlist_enabled
  }
  if (data.password_policy_level === 'standard' || data.password_policy_level === 'strict') {
    securityForm.passwordPolicyLevel = data.password_policy_level
  }
}

function buildSecuritySettingsPayload() {
  return {
    session_timeout_minutes: Number.parseInt(securityForm.sessionTimeoutMinutes.trim(), 10),
    mfa_required: securityForm.mfaRequired,
    ip_allowlist_enabled: securityForm.ipAllowlistEnabled,
    password_policy_level: securityForm.passwordPolicyLevel,
  }
}

async function loadGeneralSettings() {
  const settings = await exec(async () => {
    const response = await monitoringApi.getSystemGeneralSettings()

    if (response?.success) {
      generalRequestId.value = response.request_id ?? ''
      generalProcessTime.value = response.process_time ?? ''
    }

    return response
  }, {
    silent: true,
    errorMsg: '系统通用设置加载失败',
  })

  if (settings) {
    generalSource.value = 'REAL'
    applyGeneralSettings(settings as Record<string, unknown> as {
      backend_url: string
      max_backtest_jobs: number
      default_slippage_percent: number
      fee_rate_bps: number
    })
    return
  }

  generalSource.value = 'UNAVAILABLE'
}

async function loadSecuritySettings() {
  const settings = await exec(async () => {
    const response = await monitoringApi.getSystemSecuritySettings()

    if (response?.success) {
      securityRequestId.value = response.request_id ?? ''
      securityProcessTime.value = response.process_time ?? ''
    }

    return response
  }, {
    silent: true,
    errorMsg: '系统安全设置加载失败',
  })

  if (settings) {
    securitySource.value = 'REAL'
    applySecuritySettings(settings as Record<string, unknown> as {
      session_timeout_minutes: number
      mfa_required: boolean
      ip_allowlist_enabled: boolean
      password_policy_level: 'standard' | 'strict'
    })
    return
  }

  securitySource.value = 'UNAVAILABLE'
}

async function loadSourceRows() {
  sourceLoading.value = true
  sourceMessage.value = ''
  sourceTabSource.value = 'PENDING'
  sourceConfigItems.value = []
  sourceRequestId.value = ''
  sourceProcessTime.value = ''

  try {
    const sourceConfig = await exec(async () => {
      const response = await monitoringApi.getDataSourceConfig()

      if (response?.success) {
        sourceRequestId.value = response.request_id ?? ''
        sourceProcessTime.value = response.process_time ?? ''
      }

      return response
    }, {
      silent: true,
      errorMsg: '数据源配置加载失败',
    })

    if (sourceConfig) {
      const rows = extractDataSourceConfigItems(sourceConfig)
      sourceConfigItems.value = rows

      if (rows.length > 0) {
        sourceTabSource.value = 'REAL'
        return
      }
    }

    sourceTabSource.value = 'UNAVAILABLE'
    sourceMessage.value = '数据源真实配置暂不可用，当前页面不再展示示例数据源清单。'
  } finally {
    sourceLoading.value = false
  }
}

async function loadMonitorRows() {
  monitorLoading.value = true
  monitorMessage.value = ''
  monitorSource.value = 'PENDING'
  apiRows.value = []

  try {
    const detailed = await exec(async () => {
      const response = await monitoringApi.getDetailedSystemHealth()

      if (response?.success) {
        monitorRequestId.value = response.request_id ?? ''
        monitorProcessTime.value = response.process_time ?? ''
      }

      return response
    }, {
      silent: true,
      errorMsg: '系统监控数据加载失败'
    })

    if (detailed !== null) {
      const fromDetailed = normalizeSystemSettingsMonitorRows(detailed)

      if (fromDetailed.length > 0) {
        applyMonitorRows(fromDetailed)
        return
      }
    }

    const health = await exec(async () => {
      const response = await monitoringApi.getSystemHealth()
      const normalized = normalizeSystemHealthProbeResponse(response)

      if (normalized?.success) {
        monitorRequestId.value = normalized.request_id ?? ''
        monitorProcessTime.value = normalized.process_time ?? ''
      }

      return normalized
    }, {
      silent: true,
      errorMsg: '系统健康状态加载失败'
    })

    if (health !== null) {
      const fromHealth = normalizeSystemSettingsMonitorRows(health)

      if (fromHealth.length > 0) {
        applyMonitorRows(fromHealth)
        return
      }
    }

    monitorSource.value = 'UNAVAILABLE'
    monitorMessage.value = '系统监控真实接口暂不可用，当前页面不再展示示例监控指标。'
  } finally {
    monitorLoading.value = false
  }
}

async function saveAll() {
  if (activeTab.value === 'sources' || activeTab.value === 'monitor') {
    ElMessage.warning('请切换到“系统设置”或“安全设置”后再保存。')
    return
  }

  if (activeTab.value === 'security') {
    if (!securityForm.sessionTimeoutMinutes.trim()) {
      ElMessage.warning('请填写会话超时时间后再保存。')
      return
    }

    const securityPayload = buildSecuritySettingsPayload()
    if (Number.isNaN(securityPayload.session_timeout_minutes)) {
      ElMessage.warning('会话超时时间必须是有效数字。')
      return
    }

    const savedSecurity = await exec(async () => {
      const response = await monitoringApi.updateSystemSecuritySettings(securityPayload)

      if (response?.success) {
        securityRequestId.value = response.request_id ?? ''
        securityProcessTime.value = response.process_time ?? ''
      }

      return response
    }, {
      successMsg: '系统安全设置已保存',
      errorMsg: '系统安全设置保存失败',
    })

    if (savedSecurity) {
      securitySource.value = 'REAL'
      applySecuritySettings(savedSecurity as Record<string, unknown> as {
        session_timeout_minutes: number
        mfa_required: boolean
        ip_allowlist_enabled: boolean
        password_policy_level: 'standard' | 'strict'
      })
    }

    return
  }

  if (!form.backendUrl.trim() || !form.maxBacktestJobs.trim() || !form.slippage.trim() || !form.feeRate.trim()) {
    ElMessage.warning('请完整填写系统设置字段后再保存。')
    return
  }

  const payload = buildGeneralSettingsPayload()
  if (
    Number.isNaN(payload.max_backtest_jobs) ||
    Number.isNaN(payload.default_slippage_percent) ||
    Number.isNaN(payload.fee_rate_bps)
  ) {
    ElMessage.warning('并发、滑点和手续费必须是有效数字。')
    return
  }

  const saved = await exec(async () => {
    const response = await monitoringApi.updateSystemGeneralSettings(payload)

    if (response?.success) {
      generalRequestId.value = response.request_id ?? ''
      generalProcessTime.value = response.process_time ?? ''
    }

    return response
  }, {
    successMsg: '系统通用设置已保存',
    errorMsg: '系统通用设置保存失败',
  })

  if (saved) {
    generalSource.value = 'REAL'
    applyGeneralSettings(saved as Record<string, unknown> as {
      backend_url: string
      max_backtest_jobs: number
      default_slippage_percent: number
      fee_rate_bps: number
    })
  }
}

onMounted(() => {
  void loadGeneralSettings()
  void loadSecuritySettings()
  void loadSourceRows()
  void loadMonitorRows()
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.system-settings-page {
  padding: var(--artdeco-spacing-6);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-5);
}

.section-title {
  margin: 0;
  font-size: var(--artdeco-text-2xl);
  color: var(--artdeco-gold-primary);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
}

.header-meta {
  margin-top: var(--artdeco-spacing-2);
  display: flex;
  gap: var(--artdeco-spacing-3);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-xs);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
}

.tabs {
  display: flex;
  gap: var(--artdeco-spacing-2);
  margin-bottom: var(--artdeco-spacing-5);
}

.analysis-blocker {
  margin-bottom: var(--artdeco-spacing-5);
  padding: var(--artdeco-spacing-4);
  border: 1px solid var(--artdeco-warning);
  background: color-mix(in srgb, var(--artdeco-warning) 14%, transparent);
  color: var(--artdeco-fg-primary);
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
}

.runtime-message,
.empty-state {
  margin: 0 0 var(--artdeco-spacing-5);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
}

.tab {
  background: transparent;
  border: 1px solid var(--artdeco-border-default);
  color: var(--artdeco-fg-muted);
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
  cursor: pointer;

  &.active {
    color: var(--artdeco-gold-primary);
    border-color: var(--artdeco-gold-primary);
    background: var(--artdeco-gold-opacity-10);
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-5);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}

.field {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);

  label {
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-xs);
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }
}
</style>
