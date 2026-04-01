import { ref, onMounted, onUnmounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { deriveGpuDashboardSummary, mapGpuStatusPayload } from './gpuMonitorData'

// Types
interface GPUStatus {
    available: boolean
    model: string
    driverVersion: string
    availability: number
    utilization: number
    peakUtilization: number
    averageUtilization: number
    memoryUsed: number
    memoryTotal: number
    memoryFree: number
    memoryUsagePercent: number
    temperature: number
    maxTemperature: number
    minTemperature: number
    averageTemperature: number
    coreClock: number
    memoryClock: number
    fanSpeed: number
    powerUsage: number
}

interface LogEntry {
    id: string
    timestamp: number
    level: 'info' | 'warning' | 'error'
    message: string
}

export function useBacktestGPU() {

    // Reactive state
    const gpuStatus = reactive<GPUStatus>({
        available: true,
        model: 'NVIDIA RTX 4090',
        driverVersion: '525.60.13',
        availability: 95,
        utilization: 78,
        peakUtilization: 95,
        averageUtilization: 65,
        memoryUsed: 8 * 1024 * 1024 * 1024, // 8GB
        memoryTotal: 24 * 1024 * 1024 * 1024, // 24GB
        memoryFree: 16 * 1024 * 1024 * 1024, // 16GB
        memoryUsagePercent: 33,
        temperature: 72,
        maxTemperature: 85,
        minTemperature: 45,
        averageTemperature: 68,
        coreClock: 2235,
        memoryClock: 1313,
        fanSpeed: 65,
        powerUsage: 285
    })

    const autoRefresh = ref(true)
    const refreshing = ref(false)
    const accelerationRatio = ref(52)
    const performanceGain = ref(5100)
    const energyEfficiency = ref(15.7)
    const computeMode = ref('auto')
    const monitorFrequency = ref('5000')
    const activeLogTab = ref('realtime')
    let refreshInterval: ReturnType<typeof setInterval> | null = null

    const realtimeLogs = ref<LogEntry[]>([
        {
            id: '1',
            timestamp: Date.now() - 30000,
            level: 'info',
            message: 'GPU 加速引擎已启动'
        },
        {
            id: '2',
            timestamp: Date.now() - 25000,
            level: 'info',
            message: '检测到 NVIDIA RTX 4090 GPU'
        },
        {
            id: '3',
            timestamp: Date.now() - 20000,
            level: 'info',
            message: '显存使用率: 33% (8GB/24GB)'
        },
        {
            id: '4',
            timestamp: Date.now() - 15000,
            level: 'warning',
            message: 'GPU 温度达到 72°C，建议检查散热'
        },
        {
            id: '5',
            timestamp: Date.now() - 10000,
            level: 'info',
            message: '当前加速倍数: 52x'
        }
    ])

    // Methods
    const getAvailabilityColor = () => {
        const { availability } = gpuStatus
        if (availability >= 90) return 'var(--artdeco-rise)'
        if (availability >= 70) return 'var(--artdeco-warning)'
        return 'var(--artdeco-down)'
    }

    const getUtilizationColor = () => {
        const { utilization } = gpuStatus
        if (utilization >= 80) return 'var(--artdeco-down)'
        if (utilization >= 60) return 'var(--artdeco-warning)'
        return 'var(--artdeco-rise)'
    }

    const getMemoryColor = () => {
        const { memoryUsagePercent } = gpuStatus
        if (memoryUsagePercent >= 90) return 'var(--artdeco-down)'
        if (memoryUsagePercent >= 70) return 'var(--artdeco-warning)'
        return 'var(--artdeco-rise)'
    }

    const getTemperatureStatus = () => {
        const { temperature } = gpuStatus
        if (temperature >= 80) return 'danger'
        if (temperature >= 70) return 'warning'
        return 'success'
    }

    const getTemperatureStatusText = () => {
        const { temperature } = gpuStatus
        if (temperature >= 80) return '高温'
        if (temperature >= 70) return '偏高'
        return '正常'
    }

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

    const toggleAutoRefresh = () => {
        if (autoRefresh.value) {
            startAutoRefresh()
        } else {
            stopAutoRefresh()
        }
    }

    const manualRefresh = async () => {
        refreshing.value = true
        try {
            await refreshGPUStatus()
            ElMessage.success('GPU 状态已刷新')
        } catch (_error) {
            ElMessage.error('刷新失败')
        } finally {
            refreshing.value = false
        }
    }

    const refreshGPUStatus = async () => {
        const [statusResponse, performanceResponse] = await Promise.all([
            axios.get('/api/gpu/status'),
            axios.get('/api/gpu/performance'),
        ])

        const mappedStatus = mapGpuStatusPayload(statusResponse.data)
        if (mappedStatus) {
            Object.assign(gpuStatus, mappedStatus)
        }

        const summary = deriveGpuDashboardSummary(performanceResponse.data)
        if (summary) {
            accelerationRatio.value = summary.accelerationRatio
            performanceGain.value = summary.performanceGain
            energyEfficiency.value = summary.energyEfficiency
        }

        realtimeLogs.value.unshift({
            id: Date.now().toString(),
            timestamp: Date.now(),
            level: 'info',
            message: `状态更新 - 利用率: ${gpuStatus.utilization}%, 温度: ${gpuStatus.temperature}°C`
        })

        if (realtimeLogs.value.length > 50) {
            realtimeLogs.value = realtimeLogs.value.slice(0, 50)
        }
    }

    const startAutoRefresh = () => {
        if (refreshInterval) {
            clearInterval(refreshInterval)
        }
        refreshInterval = setInterval(refreshGPUStatus, parseInt(monitorFrequency.value))
    }

    const stopAutoRefresh = () => {
        if (refreshInterval) {
            clearInterval(refreshInterval)
            refreshInterval = null
        }
    }

    const handleComputeModeChange = (mode: string) => {
        ElMessage.info(`计算模式已切换为: ${mode === 'auto' ? '自动' : mode === 'gpu' ? 'GPU' : 'CPU'}`)
    }

    const handleMonitorFrequencyChange = (frequency: string) => {
        if (autoRefresh.value) {
            stopAutoRefresh()
            startAutoRefresh()
        }
        ElMessage.info(`监控频率已更新: ${parseInt(frequency) / 1000}秒`)
    }

    const runBenchmark = () => {
        ElMessage.info('正在运行 GPU 基准测试...')
        // Simulate benchmark
        setTimeout(() => {
            const newRatio = Math.floor(Math.random() * 20) + 45
            accelerationRatio.value = newRatio
            ElMessage.success(`基准测试完成 - 加速倍数: ${newRatio}x`)
        }, 3000)
    }

    const resetGPU = () => {
        ElMessage.warning('正在重置 GPU 状态...')
        // Simulate reset
        setTimeout(() => {
            gpuStatus.utilization = 0
            gpuStatus.temperature = 45
            gpuStatus.memoryUsagePercent = 5
            ElMessage.success('GPU 状态已重置')
        }, 2000)
    }

    // Lifecycle
    onMounted(() => {
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
    accelerationRatio,
    performanceGain,
    energyEfficiency,
    computeMode,
    monitorFrequency,
    activeLogTab,
    realtimeLogs,
    getAvailabilityColor,
    getUtilizationColor,
    getMemoryColor,
    getTemperatureStatus,
    getTemperatureStatusText,
    formatBytes,
    formatTime,
    toggleAutoRefresh,
    manualRefresh,
    refreshGPUStatus,
    startAutoRefresh,
    stopAutoRefresh,
    handleComputeModeChange,
    handleMonitorFrequencyChange,
    runBenchmark,
    resetGPU,
  }
}
