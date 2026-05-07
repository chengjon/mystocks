import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import { apiClient } from '@/api/apiClient'
import { monitoringApi } from '@/api/index'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'

export type ResourceStatus = 'normal' | 'warning' | 'critical'

export interface TrendPoint {
  timestamp: string
  value: number
}

export interface ResourceMetric {
  metric_key: string
  label: string
  unit: string
  current_value: number
  status: ResourceStatus
  warning_threshold: number
  critical_threshold: number
  series: TrendPoint[]
  meta: Record<string, unknown>
}

export interface ProcessSnapshot {
  process_key: string
  display_name: string
  status: ResourceStatus
  pid: number | null
  cpu_percent: number | null
  memory_mb: number | null
  memory_percent: number | null
  sampled_at: string
  started_at: string | null
  thresholds: Record<string, unknown>
  summary: string
}

export interface DependencySnapshot {
  dependency_key: string
  display_name: string
  status: ResourceStatus
  summary: string
  sampled_at: string
  warning_threshold: number | null
  critical_threshold: number | null
  metrics: Record<string, unknown>
}

export interface ResourcePayload {
  node: {
    node_id: string
    scope: string
    sampled_at: string
    window_minutes: number
    polling_interval_seconds: number
    overall_status: ResourceStatus
  }
  host: {
    cpu: ResourceMetric
    memory: ResourceMetric
    disk: ResourceMetric
    load: ResourceMetric
  }
  processes: ProcessSnapshot[]
  dependencies: DependencySnapshot[]
  thresholds: Record<string, { warning: number; critical: number; unit: string }>
}

export const DEFAULT_WINDOW_MINUTES = 60
const DEFAULT_POLL_INTERVAL_MS = 15_000

function getSystemResourcesRequest(params: Record<string, unknown>) {
  if (typeof monitoringApi.getSystemResources === 'function') {
    return monitoringApi.getSystemResources(params)
  }
  return apiClient.get('/v1/system/resources', { params })
}

export function useSystemResourcesPage() {
  const { loading, error, exec, lastRequestId } = useArtDecoApi()
  const resourceSnapshot = ref<ResourcePayload | null>(null)
  const pollingPaused = ref(false)
  const lastVerifiedRequestId = ref('')
  let pollTimer: ReturnType<typeof setTimeout> | null = null
  let pollGeneration = 0

  const displayRequestId = computed(() => (resourceSnapshot.value ? (lastVerifiedRequestId.value || 'N/A') : 'N/A'))
  const overallStatusLabel = computed(() => resourceSnapshot.value?.node.overall_status?.toUpperCase() || 'UNKNOWN')
  const hostMetrics = computed(() =>
    resourceSnapshot.value
      ? [
          resourceSnapshot.value.host.cpu,
          resourceSnapshot.value.host.memory,
          resourceSnapshot.value.host.disk,
          resourceSnapshot.value.host.load,
        ]
      : [],
  )
  const processSnapshots = computed(() => resourceSnapshot.value?.processes ?? [])
  const dependencySnapshots = computed(() => resourceSnapshot.value?.dependencies ?? [])
  const hasVerifiedSnapshot = computed(() => Boolean(resourceSnapshot.value))
  const criticalCount = computed(
    () =>
      hostMetrics.value.filter((metric) => metric.status === 'critical').length +
      processSnapshots.value.filter((item) => item.status === 'critical').length +
      dependencySnapshots.value.filter((item) => item.status === 'critical').length,
  )
  const statsProcessCount = computed(() => (hasVerifiedSnapshot.value ? `${processSnapshots.value.length}` : '--'))
  const statsDependencyCount = computed(() => (hasVerifiedSnapshot.value ? `${dependencySnapshots.value.length}` : '--'))
  const statsCriticalCount = computed(() => (hasVerifiedSnapshot.value ? `${criticalCount.value}` : '--'))
  const processTrackedLabel = computed(() => (hasVerifiedSnapshot.value ? `${processSnapshots.value.length} tracked` : '-- tracked'))
  const dependencyTrackedLabel = computed(() => (hasVerifiedSnapshot.value ? `${dependencySnapshots.value.length} tracked` : '-- tracked'))
  const pageStatusText = computed(() => {
    if (error.value) return '同步异常'
    if (loading.value) return '同步中'
    if (!resourceSnapshot.value) return '等待快照'
    return pollingPaused.value ? '轮询已暂停' : '轮询在线'
  })
  const pageStatusType = computed(() => {
    if (error.value) return 'warning'
    if (!resourceSnapshot.value) return 'info'
    return resourceSnapshot.value.node.overall_status === 'critical'
      ? 'warning'
      : resourceSnapshot.value.node.overall_status === 'warning'
        ? 'warning'
        : 'success'
  })
  const contentShellDescription = computed(
    () => '独立观察单节点 host、运行进程与依赖代理指标，保持系统资源使用能力与 API 健康页分层。',
  )
  const runtimeMessage = computed(() => {
    if (error.value) return `${error.value}，当前仍保留上次已验证资源快照。`
    if (!resourceSnapshot.value) return '当前没有可展示的资源快照。'
    return pollingPaused.value ? '轮询已暂停，页面保持上次成功同步的资源快照。' : ''
  })
  const pollingButtonLabel = computed(() => (pollingPaused.value ? '恢复轮询' : '暂停轮询'))

  function formatMetricValue(metric: ResourceMetric): string {
    return `${metric.current_value.toFixed(1)}${metric.unit}`
  }

  function formatPercent(value: number | null | undefined): string {
    if (value === null || value === undefined) return 'N/A'
    return `${value.toFixed(1)}%`
  }

  function formatMemoryMb(value: number | null | undefined): string {
    if (value === null || value === undefined) return 'N/A'
    return `${value.toFixed(1)} MB`
  }

  function formatTimestamp(value: string | null | undefined): string {
    if (!value) return 'N/A'
    return value.replace('T', ' ').slice(0, 19)
  }

  function statusVariant(status: ResourceStatus): 'gold' | 'rise' | 'fall' {
    if (status === 'critical') return 'fall'
    if (status === 'warning') return 'gold'
    return 'rise'
  }

  function sparklinePoints(series: TrendPoint[]): string {
    if (!series.length) return ''

    const width = 120
    const height = 40
    const values = series.map((point) => point.value)
    const minValue = Math.min(...values)
    const maxValue = Math.max(...values)
    const span = maxValue - minValue || 1

    return series
      .map((point, index) => {
        const x = series.length === 1 ? width / 2 : (index / (series.length - 1)) * width
        const y = height - ((point.value - minValue) / span) * height
        return `${x.toFixed(2)},${y.toFixed(2)}`
      })
      .join(' ')
  }

  function metricMetaSummary(metric: ResourceMetric): string {
    if (metric.metric_key === 'memory_percent') {
      return `${metric.meta.used_gb ?? 'N/A'} / ${metric.meta.total_gb ?? 'N/A'} GB`
    }
    if (metric.metric_key === 'disk_percent') {
      return `${metric.meta.used_gb ?? 'N/A'} / ${metric.meta.total_gb ?? 'N/A'} GB`
    }
    if (metric.metric_key === 'load_percent') {
      return `1m load ${metric.meta.load_average_1m ?? 'N/A'}`
    }
    return `${metric.meta.cpu_count ?? 'N/A'} cores`
  }

  async function fetchResources(force = false): Promise<void> {
    if (pollingPaused.value && !force) {
      return
    }
    const data = await exec(
      () =>
        getSystemResourcesRequest({
          window_minutes: DEFAULT_WINDOW_MINUTES,
          include_processes: true,
          include_dependencies: true,
        }),
      { errorMsg: '资源指标同步失败' },
    )

    if (data) {
      resourceSnapshot.value = data as ResourcePayload
      lastVerifiedRequestId.value = lastRequestId.value || ''
    }
  }

  function stopPolling(): void {
    pollGeneration += 1
    if (pollTimer !== null) {
      clearTimeout(pollTimer)
      pollTimer = null
    }
  }

  function scheduleNextPoll(): void {
    if (pollTimer !== null) {
      clearTimeout(pollTimer)
      pollTimer = null
    }
    if (pollingPaused.value) {
      return
    }
    const generation = pollGeneration
    pollTimer = setTimeout(async () => {
      if (pollingPaused.value || generation !== pollGeneration) {
        return
      }
      await fetchResources()
      if (pollingPaused.value || generation !== pollGeneration) {
        return
      }
      scheduleNextPoll()
    }, DEFAULT_POLL_INTERVAL_MS)
  }

  function togglePolling(): void {
    pollingPaused.value = !pollingPaused.value
    if (pollingPaused.value) {
      stopPolling()
      return
    }
    scheduleNextPoll()
  }

  onMounted(() => {
    void fetchResources(true)
    scheduleNextPoll()
  })

  onBeforeUnmount(() => {
    stopPolling()
  })

  return {
    DEFAULT_WINDOW_MINUTES,
    contentShellDescription,
    criticalCount,
    dependencySnapshots,
    dependencyTrackedLabel,
    displayRequestId,
    formatMemoryMb,
    formatMetricValue,
    formatPercent,
    formatTimestamp,
    hasVerifiedSnapshot,
    hostMetrics,
    loading,
    metricMetaSummary,
    overallStatusLabel,
    pageStatusText,
    pageStatusType,
    pollingButtonLabel,
    processSnapshots,
    processTrackedLabel,
    resourceSnapshot,
    runtimeMessage,
    sparklinePoints,
    statsCriticalCount,
    statsDependencyCount,
    statsProcessCount,
    statusVariant,
    togglePolling,
  }
}
