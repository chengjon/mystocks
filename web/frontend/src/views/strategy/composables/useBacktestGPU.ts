import { computed, ref, onMounted, onUnmounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import {
    createUnknownGpuDashboardSummary,
    createUnknownGpuStatus,
    deriveGpuDashboardSummary,
    type GpuDashboardStatus,
    mapGpuStatusPayload
} from './gpuMonitorData'

interface LogEntry {
    id: string
    timestamp: number
    level: 'info' | 'warning' | 'error'
    message: string
}

export function useBacktestGPU() {
    const initialSummary = createUnknownGpuDashboardSummary()

    // Reactive state
    const gpuStatus = reactive<GpuDashboardStatus>(createUnknownGpuStatus())

    const autoRefresh = ref(true)
    const refreshing = ref(false)
    const refreshError = ref('')
    const lastUpdatedAt = ref<number | null>(null)
    const hasStatusSnapshot = ref(false)
    const hasPerformanceSnapshot = ref(false)
    const partialSyncNotice = ref('')
    const accelerationRatio = ref<number | null>(initialSummary.accelerationRatio)
    const performanceGain = ref<number | null>(initialSummary.performanceGain)
    const energyEfficiency = ref<number | null>(initialSummary.energyEfficiency)
    const monitorFrequency = ref('5000')
    const activeLogTab = ref('realtime')
    const runtimeControlNotice =
        '当前页面仅接入 GPU 状态与性能快照读取接口；运行模式切换、基准测试和重置操作未接入后端执行链路。'
    let refreshInterval: ReturnType<typeof setInterval> | null = null
    let refreshPromise: Promise<void> | null = null

    const realtimeLogs = ref<LogEntry[]>([
        {
            id: 'gpu-monitor-pending',
            timestamp: Date.now(),
            level: 'info',
            message: '等待首轮 GPU 监控快照同步'
        },
        {
            id: 'gpu-monitor-scope',
            timestamp: Date.now(),
            level: 'info',
            message: 'GPU 页面当前仅提供监控读取，不执行本地基准测试或运行态重置'
        }
    ])

    // Methods
    const getAvailabilityColor = () => {
        const { availability } = gpuStatus
        if (availability >= 90) return '#67C23A'
        if (availability >= 70) return '#E6A23C'
        return '#F56C6C'
    }

    const getUtilizationColor = () => {
        const { utilization } = gpuStatus
        if (utilization >= 80) return '#F56C6C'
        if (utilization >= 60) return '#E6A23C'
        return '#67C23A'
    }

    const getMemoryColor = () => {
        const { memoryUsagePercent } = gpuStatus
        if (memoryUsagePercent >= 90) return '#F56C6C'
        if (memoryUsagePercent >= 70) return '#E6A23C'
        return '#67C23A'
    }

    const getTemperatureStatus = () => {
        if (gpuStatus.temperature === null) {
            return 'info'
        }
        const { temperature } = gpuStatus
        if (temperature >= 80) return 'danger'
        if (temperature >= 70) return 'warning'
        return 'success'
    }

    const getTemperatureStatusText = () => {
        if (gpuStatus.temperature === null) {
            return '未校验'
        }
        const { temperature } = gpuStatus
        if (temperature >= 80) return '高温'
        if (temperature >= 70) return '偏高'
        return '正常'
    }

    const hasVerifiedTemperature = computed(() => hasStatusSnapshot.value && gpuStatus.temperature !== null)
    const hasVerifiedPowerUsage = computed(() => hasStatusSnapshot.value && gpuStatus.powerUsage !== null)
    const hasBenchmarkMetrics = computed(
        () =>
            hasPerformanceSnapshot.value &&
            accelerationRatio.value !== null &&
            performanceGain.value !== null &&
            energyEfficiency.value !== null
    )

    const temperatureDisplayValue = computed(() => {
        if (!hasStatusSnapshot.value) {
            return '--'
        }
        if (gpuStatus.temperature === null) {
            return '未校验'
        }
        return `${gpuStatus.temperature}°C`
    })

    const formatTemperatureDetail = (value: number | null): string => {
        if (!hasStatusSnapshot.value || value === null) {
            return '--'
        }
        return `${value}°C`
    }

    const powerUsageDisplayValue = computed(() => {
        if (!hasStatusSnapshot.value) {
            return '--'
        }
        if (gpuStatus.powerUsage === null) {
            return '未校验'
        }
        return `${gpuStatus.powerUsage} W`
    })

    const formatOptionalStatusMetric = (value: number | null, unit: string): string => {
        if (!hasStatusSnapshot.value) {
            return '--'
        }
        if (value === null) {
            return '未校验'
        }
        return `${value} ${unit}`
    }

    const accelerationRatioDisplayValue = computed(() => {
        if (!hasPerformanceSnapshot.value) {
            return '--'
        }
        if (accelerationRatio.value === null) {
            return '待接入'
        }
        return `${accelerationRatio.value}x`
    })

    const performanceGainDisplayValue = computed(() => {
        if (!hasPerformanceSnapshot.value) {
            return '--'
        }
        if (performanceGain.value === null) {
            return '待接入'
        }
        return `${performanceGain.value}%`
    })

    const energyEfficiencyDisplayValue = computed(() => {
        if (!hasPerformanceSnapshot.value) {
            return '--'
        }
        if (energyEfficiency.value === null) {
            return '待接入'
        }
        return String(energyEfficiency.value)
    })

    const performanceSnapshotNote = computed(() => {
        if (!hasPerformanceSnapshot.value) {
            return '等待后端性能快照'
        }
        if (!hasBenchmarkMetrics.value) {
            return '基准性能待接入'
        }
        return accelerationRatio.value !== null && accelerationRatio.value > 50
            ? '✓ 已返回后端性能快照'
            : '⚠ 后端快照未达 50x'
    })

    const performanceTrendLabel = computed(() => {
        if (!hasPerformanceSnapshot.value) {
            return '等待性能对比'
        }
        if (!hasBenchmarkMetrics.value) {
            return '缺少 CPU/GPU 对比'
        }
        return '相比 CPU'
    })

    const performanceChartTitle = computed(() => {
        if (!hasPerformanceSnapshot.value) {
            return '等待性能快照'
        }
        if (!hasBenchmarkMetrics.value) {
            return '基准性能待接入'
        }
        return '性能对比图表'
    })

    const performanceChartSubtitle = computed(() => {
        if (!hasPerformanceSnapshot.value) {
            return '后端性能接口返回后展示'
        }
        if (!hasBenchmarkMetrics.value) {
            return '当前只同步 GPU 监控指标，未返回矩阵基准性能字段'
        }
        return '实时更新中...'
    })

    const formatBytes = (bytes: number): string => {
        if (bytes === 0) return '0 B'
        const k = 1024
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
        const i = Math.floor(Math.log(bytes) / Math.log(k))
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
    }

    const formatTime = (timestamp: number): string => {
        return new Date(timestamp).toLocaleTimeString()
    }

    const runtimeStatusMessage = computed(() => {
        if (refreshError.value) {
            return refreshError.value
        }

        if (lastUpdatedAt.value !== null) {
            const prefix = partialSyncNotice.value ? '部分同步' : '最近同步'
            const suffix = partialSyncNotice.value ? ` · ${partialSyncNotice.value}` : ''
            return `${prefix} ${formatTime(lastUpdatedAt.value)}${suffix}`
        }

        return '等待首轮 GPU 数据同步'
    })

    const toggleAutoRefresh = () => {
        if (autoRefresh.value) {
            startAutoRefresh()
        } else {
            stopAutoRefresh()
        }
    }

    const manualRefresh = async () => {
        if (refreshing.value) {
            return
        }
        refreshing.value = true
        try {
            await refreshGPUStatus()
            ElMessage.success('GPU 监控快照已刷新')
        } catch (_error) {
            ElMessage.error('刷新失败')
        } finally {
            refreshing.value = false
        }
    }

    const refreshGPUStatus = async () => {
        if (refreshPromise) {
            return refreshPromise
        }

        refreshPromise = (async () => {
            try {
                const hadStatusSnapshot = hasStatusSnapshot.value
                const hadPerformanceSnapshot = hasPerformanceSnapshot.value
                const [statusResponse, performanceResponse] = await Promise.all([
                    axios.get('/api/gpu/status'),
                    axios.get('/api/gpu/performance'),
                ])

                const mappedStatus = mapGpuStatusPayload(statusResponse.data)
                if (mappedStatus) {
                    Object.assign(gpuStatus, mappedStatus)
                    hasStatusSnapshot.value = true
                }

                const summary = deriveGpuDashboardSummary(performanceResponse.data)
                if (summary) {
                    accelerationRatio.value = summary.accelerationRatio
                    performanceGain.value = summary.performanceGain
                    energyEfficiency.value = summary.energyEfficiency
                    hasPerformanceSnapshot.value = true
                }

                if (!mappedStatus && !summary) {
                    throw new Error('GPU 监控接口未返回有效快照')
                }

                const missingSlices: string[] = []
                if (!mappedStatus) {
                    missingSlices.push(hadStatusSnapshot ? 'GPU 状态仍显示上次成功快照' : 'GPU 状态待同步')
                }
                if (!summary) {
                    missingSlices.push(hadPerformanceSnapshot ? '性能快照仍显示上次成功快照' : '性能快照待同步')
                }

                refreshError.value = ''
                partialSyncNotice.value = missingSlices.join(' · ')
                lastUpdatedAt.value = Date.now()
                const syncDetails: string[] = []
                if (mappedStatus) {
                    syncDetails.push(`利用率 ${gpuStatus.utilization}%`)
                } else {
                    syncDetails.push('状态快照缺失')
                }
                const syncedAccelerationRatio = summary?.accelerationRatio
                if (syncedAccelerationRatio !== null && syncedAccelerationRatio !== undefined) {
                    syncDetails.push(`加速倍数 ${syncedAccelerationRatio}x`)
                } else if (summary) {
                    syncDetails.push('基准性能待接入')
                } else {
                    syncDetails.push('性能快照缺失')
                }
                realtimeLogs.value.unshift({
                    id: Date.now().toString(),
                    timestamp: Date.now(),
                    level: mappedStatus && summary ? 'info' : 'warning',
                    message: `${mappedStatus && summary ? 'GPU 监控已同步' : 'GPU 监控部分同步'} - ${syncDetails.join(' · ')}`
                })
            } catch (error) {
                const message = error instanceof Error ? error.message : 'GPU 状态拉取失败'
                refreshError.value = `GPU 状态同步失败：${message}`
                if (!hasStatusSnapshot.value) {
                    Object.assign(gpuStatus, createUnknownGpuStatus())
                }
                if (!hasPerformanceSnapshot.value) {
                    const fallbackSummary = createUnknownGpuDashboardSummary()
                    accelerationRatio.value = fallbackSummary.accelerationRatio
                    performanceGain.value = fallbackSummary.performanceGain
                    energyEfficiency.value = fallbackSummary.energyEfficiency
                }
                partialSyncNotice.value = ''
                realtimeLogs.value.unshift({
                    id: Date.now().toString(),
                    timestamp: Date.now(),
                    level: 'error',
                    message: refreshError.value
                })
                throw error
            } finally {
                if (realtimeLogs.value.length > 50) {
                    realtimeLogs.value = realtimeLogs.value.slice(0, 50)
                }
                refreshPromise = null
            }
        })()

        return refreshPromise
    }

    const startAutoRefresh = () => {
        if (refreshInterval) {
            clearInterval(refreshInterval)
        }
        refreshInterval = setInterval(() => {
            void refreshGPUStatus().catch(() => undefined)
        }, parseInt(monitorFrequency.value))
    }

    const stopAutoRefresh = () => {
        if (refreshInterval) {
            clearInterval(refreshInterval)
            refreshInterval = null
        }
    }

    const handleMonitorFrequencyChange = (frequency: string) => {
        if (autoRefresh.value) {
            stopAutoRefresh()
            startAutoRefresh()
        }
        ElMessage.info(`监控频率已更新: ${parseInt(frequency) / 1000}秒`)
    }

    // Lifecycle
    onMounted(() => {
        void refreshGPUStatus().catch(() => undefined)
        if (autoRefresh.value) {
            startAutoRefresh()
        }
    })

    onUnmounted(() => {
        stopAutoRefresh()
    })

  return {
    gpuStatus,
    autoRefresh,
    refreshing,
    refreshError,
    lastUpdatedAt,
    hasStatusSnapshot,
    hasPerformanceSnapshot,
    runtimeStatusMessage,
    accelerationRatio,
    performanceGain,
    energyEfficiency,
    monitorFrequency,
    activeLogTab,
    realtimeLogs,
    runtimeControlNotice,
    getAvailabilityColor,
    getUtilizationColor,
    getMemoryColor,
    getTemperatureStatus,
    getTemperatureStatusText,
    hasVerifiedTemperature,
    hasVerifiedPowerUsage,
    hasBenchmarkMetrics,
    temperatureDisplayValue,
    formatTemperatureDetail,
    powerUsageDisplayValue,
    formatOptionalStatusMetric,
    accelerationRatioDisplayValue,
    performanceGainDisplayValue,
    energyEfficiencyDisplayValue,
    performanceSnapshotNote,
    performanceTrendLabel,
    performanceChartTitle,
    performanceChartSubtitle,
    formatBytes,
    formatTime,
    toggleAutoRefresh,
    manualRefresh,
    refreshGPUStatus,
    startAutoRefresh,
    stopAutoRefresh,
    handleMonitorFrequencyChange,
  }
}
