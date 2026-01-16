<template>
    <div class="backtest-gpu-dashboard">
        <!-- Header Section -->
        <div class="dashboard-header">
            <div class="header-content">
                <h1 class="dashboard-title">
                    <el-icon class="title-icon">
                        <Cpu />
                    </el-icon>
                    GPU 加速回测
                </h1>
                <p class="dashboard-subtitle">实时监控 GPU 加速状态，实现 50x+ 性能提升</p>
            </div>
            <div class="header-actions">
                <el-switch
                    v-model="autoRefresh"
                    active-text="自动刷新"
                    inactive-text="手动刷新"
                    @change="toggleAutoRefresh"
                />
                <el-button type="primary" :loading="refreshing" @click="manualRefresh">
                    <el-icon><RefreshRight /></el-icon>
                    刷新
                </el-button>
            </div>
        </div>

        <!-- GPU Status Cards -->
        <div class="status-cards-grid">
            <!-- GPU Availability Card -->
            <el-card class="status-card gpu-availability">
                <template #header>
                    <div class="card-header">
                        <el-icon class="card-icon">
                            <VideoPlay />
                        </el-icon>
                        <span>GPU 可用性</span>
                    </div>
                </template>
                <div class="card-content">
                    <div class="availability-indicator">
                        <el-progress
                            type="circle"
                            :percentage="gpuStatus.availability"
                            :color="getAvailabilityColor()"
                            :stroke-width="8"
                        />
                    </div>
                    <div class="availability-details">
                        <div class="detail-item">
                            <span class="label">状态:</span>
                            <el-tag :type="gpuStatus.available ? 'success' : 'danger'">
                                {{ gpuStatus.available ? '可用' : '不可用' }}
                            </el-tag>
                        </div>
                        <div class="detail-item">
                            <span class="label">GPU 型号:</span>
                            <span class="value">{{ gpuStatus.model || '未知' }}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">驱动版本:</span>
                            <span class="value">{{ gpuStatus.driverVersion || '未知' }}</span>
                        </div>
                    </div>
                </div>
            </el-card>

            <!-- GPU Utilization Card -->
            <el-card class="status-card gpu-utilization">
                <template #header>
                    <div class="card-header">
                        <el-icon class="card-icon">
                            <TrendCharts />
                        </el-icon>
                        <span>GPU 利用率</span>
                    </div>
                </template>
                <div class="card-content">
                    <div class="utilization-chart">
                        <el-progress
                            type="circle"
                            :percentage="gpuStatus.utilization"
                            :color="getUtilizationColor()"
                            :stroke-width="8"
                        />
                    </div>
                    <div class="utilization-details">
                        <div class="detail-item">
                            <span class="label">当前利用率:</span>
                            <span class="value">{{ gpuStatus.utilization }}%</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">峰值利用率:</span>
                            <span class="value">{{ gpuStatus.peakUtilization }}%</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">平均利用率:</span>
                            <span class="value">{{ gpuStatus.averageUtilization }}%</span>
                        </div>
                    </div>
                </div>
            </el-card>

            <!-- Memory Usage Card -->
            <el-card class="status-card memory-usage">
                <template #header>
                    <div class="card-header">
                        <el-icon class="card-icon">
                            <Memo />
                        </el-icon>
                        <span>显存使用</span>
                    </div>
                </template>
                <div class="card-content">
                    <div class="memory-chart">
                        <el-progress
                            type="circle"
                            :percentage="gpuStatus.memoryUsagePercent"
                            :color="getMemoryColor()"
                            :stroke-width="8"
                        />
                    </div>
                    <div class="memory-details">
                        <div class="detail-item">
                            <span class="label">已用显存:</span>
                            <span class="value">{{ formatBytes(gpuStatus.memoryUsed) }}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">总显存:</span>
                            <span class="value">{{ formatBytes(gpuStatus.memoryTotal) }}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">空闲显存:</span>
                            <span class="value">{{ formatBytes(gpuStatus.memoryFree) }}</span>
                        </div>
                    </div>
                </div>
            </el-card>

            <!-- Temperature Card -->
            <el-card class="status-card temperature">
                <template #header>
                    <div class="card-header">
                        <el-icon class="card-icon">
                            <HotWater />
                        </el-icon>
                        <span>GPU 温度</span>
                    </div>
                </template>
                <div class="card-content">
                    <div class="temperature-display">
                        <div class="temp-value">{{ gpuStatus.temperature }}°C</div>
                        <div class="temp-status">
                            <el-tag :type="getTemperatureStatus()">
                                {{ getTemperatureStatusText() }}
                            </el-tag>
                        </div>
                    </div>
                    <div class="temperature-details">
                        <div class="detail-item">
                            <span class="label">最高温度:</span>
                            <span class="value">{{ gpuStatus.maxTemperature }}°C</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">最低温度:</span>
                            <span class="value">{{ gpuStatus.minTemperature }}°C</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">平均温度:</span>
                            <span class="value">{{ gpuStatus.averageTemperature }}°C</span>
                        </div>
                    </div>
                </div>
            </el-card>
        </div>

        <!-- Acceleration Performance -->
        <el-card class="performance-card">
            <template #header>
                <div class="card-header">
                    <el-icon class="card-icon">
                        <Lightning />
                    </el-icon>
                    <span>加速性能对比</span>
                </div>
            </template>
            <div class="performance-content">
                <div class="performance-metrics">
                    <div class="metric-item">
                        <div class="metric-label">当前加速倍数</div>
                        <div class="metric-value">{{ accelerationRatio }}x</div>
                        <div class="metric-change" :class="{ positive: accelerationRatio > 50 }">
                            {{ accelerationRatio > 50 ? '✓ 达标' : '⚠ 未达标' }}
                        </div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">计算性能提升</div>
                        <div class="metric-value">{{ performanceGain }}%</div>
                        <div class="metric-trend">
                            <el-icon><Top /></el-icon>
                            相比 CPU
                        </div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">能效比</div>
                        <div class="metric-value">{{ energyEfficiency }}</div>
                        <div class="metric-unit">计算/瓦</div>
                    </div>
                </div>

                <div class="performance-chart">
                    <div class="chart-placeholder">
                        <el-icon class="chart-icon"><TrendCharts /></el-icon>
                        <p>性能对比图表</p>
                        <small>实时更新中...</small>
                    </div>
                </div>
            </div>
        </el-card>

        <!-- Control Panel -->
        <el-card class="control-panel">
            <template #header>
                <div class="card-header">
                    <el-icon class="card-icon">
                        <Setting />
                    </el-icon>
                    <span>控制面板</span>
                </div>
            </template>
            <div class="control-content">
                <div class="control-row">
                    <div class="control-item">
                        <label class="control-label">计算模式</label>
                        <el-radio-group v-model="computeMode" @change="handleComputeModeChange">
                            <el-radio label="auto">自动</el-radio>
                            <el-radio label="gpu">强制 GPU</el-radio>
                            <el-radio label="cpu">强制 CPU</el-radio>
                        </el-radio-group>
                    </div>
                    <div class="control-item">
                        <label class="control-label">监控频率</label>
                        <el-select v-model="monitorFrequency" @change="handleMonitorFrequencyChange">
                            <el-option label="实时 (1秒)" value="1000" />
                            <el-option label="快速 (5秒)" value="5000" />
                            <el-option label="标准 (10秒)" value="10000" />
                            <el-option label="节能 (30秒)" value="30000" />
                        </el-select>
                    </div>
                </div>

                <div class="control-row">
                    <div class="control-item">
                        <el-button type="primary" @click="runBenchmark">
                            <el-icon><VideoPlay /></el-icon>
                            运行基准测试
                        </el-button>
                    </div>
                    <div class="control-item">
                        <el-button type="warning" @click="resetGPU">
                            <el-icon><Refresh /></el-icon>
                            重置 GPU 状态
                        </el-button>
                    </div>
                </div>
            </div>
        </el-card>

        <!-- Logs and Alerts -->
        <el-card class="logs-card">
            <template #header>
                <div class="card-header">
                    <el-icon class="card-icon">
                        <Document />
                    </el-icon>
                    <span>日志与告警</span>
                </div>
            </template>
            <div class="logs-content">
                <el-tabs v-model="activeLogTab">
                    <el-tab-pane label="实时日志" name="realtime">
                        <div class="log-entries">
                            <div v-for="log in realtimeLogs" :key="log.id" class="log-entry" :class="log.level">
                                <span class="log-time">{{ formatTime(log.timestamp) }}</span>
                                <span class="log-level">{{ log.level.toUpperCase() }}</span>
                                <span class="log-message">{{ log.message }}</span>
                            </div>
                        </div>
                    </el-tab-pane>
                    <el-tab-pane label="性能指标" name="metrics">
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <h4>GPU 核心频率</h4>
                                <div class="metric-value">{{ gpuStatus.coreClock }} MHz</div>
                            </div>
                            <div class="metric-card">
                                <h4>显存频率</h4>
                                <div class="metric-value">{{ gpuStatus.memoryClock }} MHz</div>
                            </div>
                            <div class="metric-card">
                                <h4>风扇转速</h4>
                                <div class="metric-value">{{ gpuStatus.fanSpeed }}%</div>
                            </div>
                            <div class="metric-card">
                                <h4>电源使用</h4>
                                <div class="metric-value">{{ gpuStatus.powerUsage }} W</div>
                            </div>
                        </div>
                    </el-tab-pane>
                </el-tabs>
            </div>
        </el-card>
    </div>
</template>

<script setup lang="ts">
    import { ref, onMounted, onUnmounted, reactive } from 'vue'
    import {
        Cpu,
        VideoPlay,
        TrendCharts,
        Memo,
        HotWater,
        Lightning,
        Top,
        Setting,
        Refresh,
        RefreshRight,
        Document
    } from '@element-plus/icons-vue'
    import { ElMessage } from 'element-plus'

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
        } catch (error) {
            ElMessage.error('刷新失败')
        } finally {
            refreshing.value = false
        }
    }

    const refreshGPUStatus = async () => {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000))

        // Update with mock data
        gpuStatus.utilization = Math.floor(Math.random() * 30) + 60
        gpuStatus.temperature = Math.floor(Math.random() * 20) + 60
        gpuStatus.memoryUsagePercent = Math.floor(Math.random() * 20) + 25

        // Add log entry
        realtimeLogs.value.unshift({
            id: Date.now().toString(),
            timestamp: Date.now(),
            level: 'info',
            message: `状态更新 - 利用率: ${gpuStatus.utilization}%, 温度: ${gpuStatus.temperature}°C`
        })

        // Keep only last 50 logs
        if (realtimeLogs.value.length > 50) {
            realtimeLogs.value = realtimeLogs.value.slice(0, 50)
        }
    }

    const startAutoRefresh = () => {
        const interval = setInterval(refreshGPUStatus, parseInt(monitorFrequency.value))
        // Store interval ID for cleanup
        ;(window as any).gpuRefreshInterval = interval
    }

    const stopAutoRefresh = () => {
        if ((window as any).gpuRefreshInterval) {
            clearInterval((window as any).gpuRefreshInterval)
            ;(window as any).gpuRefreshInterval = null
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
</script>

<style scoped lang="scss">
    .backtest-gpu-dashboard {
        padding: var(--spacing-6);
        max-width: 1400px;
        margin: 0 auto;
    }

    .dashboard-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--spacing-6);
        padding: var(--spacing-6);
        background: var(--color-bg-secondary);
        border-radius: var(--border-radius-lg);
        border: 1px solid var(--color-border-primary);

        .header-content {
            .dashboard-title {
                display: flex;
                align-items: center;
                gap: var(--spacing-3);
                font-size: var(--font-size-3xl);
                font-weight: var(--font-weight-bold);
                color: var(--color-text-primary);
                margin: 0 0 var(--spacing-1) 0;

                .title-icon {
                    color: var(--color-primary-400);
                }
            }

            .dashboard-subtitle {
                color: var(--color-text-secondary);
                margin: 0;
            }
        }

        .header-actions {
            display: flex;
            gap: var(--spacing-4);
            align-items: center;
        }
    }

    .status-cards-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: var(--spacing-6);
        margin-bottom: var(--spacing-6);
    }

    .status-card {
        .card-header {
            display: flex;
            align-items: center;
            gap: var(--spacing-2);

            .card-icon {
                color: var(--color-primary-400);
            }
        }

        .card-content {
            display: flex;
            align-items: center;
            gap: var(--spacing-6);

            .availability-indicator,
            .utilization-chart,
            .memory-chart {
                flex-shrink: 0;
            }

            .availability-details,
            .utilization-details,
            .memory-details {
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: var(--spacing-2);
            }

            .temperature-display {
                text-align: center;
                flex: 1;

                .temp-value {
                    font-size: var(--font-size-4xl);
                    font-weight: var(--font-weight-bold);
                    color: var(--color-text-primary);
                    margin-bottom: var(--spacing-2);
                }

                .temp-status {
                    display: flex;
                    justify-content: center;
                }
            }

            .temperature-details {
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: var(--spacing-2);
            }
        }
    }

    .detail-item {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .label {
            color: var(--color-text-secondary);
            font-size: var(--font-size-sm);
        }

        .value {
            color: var(--color-text-primary);
            font-weight: var(--font-weight-medium);
        }
    }

    .performance-card {
        margin-bottom: var(--spacing-6);

        .card-header {
            display: flex;
            align-items: center;
            gap: var(--spacing-2);

            .card-icon {
                color: var(--color-primary-400);
            }
        }

        .performance-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: var(--spacing-6);

            .performance-metrics {
                display: flex;
                flex-direction: column;
                gap: var(--spacing-4);
            }

            .metric-item {
                padding: var(--spacing-4);
                background: var(--color-bg-tertiary);
                border-radius: var(--border-radius-md);
                border: 1px solid var(--color-border-secondary);

                .metric-label {
                    color: var(--color-text-secondary);
                    font-size: var(--font-size-sm);
                    margin-bottom: var(--spacing-1);
                }

                .metric-value {
                    font-size: var(--font-size-3xl);
                    font-weight: var(--font-weight-bold);
                    color: var(--color-text-primary);
                    margin-bottom: var(--spacing-1);
                }

                .metric-change {
                    font-size: var(--font-size-sm);
                    font-weight: var(--font-weight-medium);

                    &.positive {
                        color: var(--color-financial-positive);
                    }
                }

                .metric-trend {
                    display: flex;
                    align-items: center;
                    gap: var(--spacing-1);
                    color: var(--color-text-secondary);
                    font-size: var(--font-size-sm);
                }

                .metric-unit {
                    color: var(--color-text-tertiary);
                    font-size: var(--font-size-sm);
                }
            }

            .performance-chart {
                display: flex;
                align-items: center;
                justify-content: center;

                .chart-placeholder {
                    text-align: center;
                    color: var(--color-text-tertiary);

                    .chart-icon {
                        font-size: var(--font-size-6xl);
                        margin-bottom: var(--spacing-3);
                    }

                    p {
                        margin: var(--spacing-1) 0;
                        font-size: var(--font-size-lg);
                    }

                    small {
                        font-size: var(--font-size-sm);
                    }
                }
            }
        }
    }

    .control-panel {
        margin-bottom: var(--spacing-6);

        .card-header {
            display: flex;
            align-items: center;
            gap: var(--spacing-2);

            .card-icon {
                color: var(--color-primary-400);
            }
        }

        .control-content {
            .control-row {
                display: flex;
                gap: var(--spacing-8);
                margin-bottom: var(--spacing-4);

                &:last-child {
                    margin-bottom: 0;
                }
            }

            .control-item {
                display: flex;
                flex-direction: column;
                gap: var(--spacing-2);

                .control-label {
                    font-weight: var(--font-weight-medium);
                    color: var(--color-text-primary);
                }
            }
        }
    }

    .logs-card {
        .card-header {
            display: flex;
            align-items: center;
            gap: var(--spacing-2);

            .card-icon {
                color: var(--color-primary-400);
            }
        }

        .logs-content {
            .log-entries {
                max-height: 400px;
                overflow-y: auto;
                background: var(--color-bg-tertiary);
                border-radius: var(--border-radius-md);
                padding: var(--spacing-2);
            }

            .log-entry {
                display: flex;
                gap: var(--spacing-3);
                padding: var(--spacing-2);
                margin-bottom: var(--spacing-1);
                border-radius: var(--border-radius-sm);
                font-family: var(--font-family-mono);
                font-size: var(--font-size-sm);

                &:last-child {
                    margin-bottom: 0;
                }

                &.info {
                    background: rgba(33, 150, 243, 0.1);
                    border-left: 3px solid var(--color-primary-400);
                }

                &.warning {
                    background: rgba(255, 183, 77, 0.1);
                    border-left: 3px solid var(--color-status-warning);
                }

                &.error {
                    background: rgba(239, 83, 80, 0.1);
                    border-left: 3px solid var(--color-status-error);
                }

                .log-time {
                    color: var(--color-text-tertiary);
                    flex-shrink: 0;
                }

                .log-level {
                    font-weight: var(--font-weight-bold);
                    flex-shrink: 0;
                    min-width: 60px;
                }

                .log-message {
                    color: var(--color-text-primary);
                    flex: 1;
                }
            }

            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: var(--spacing-4);

                .metric-card {
                    padding: var(--spacing-4);
                    background: var(--color-bg-tertiary);
                    border-radius: var(--border-radius-md);
                    border: 1px solid var(--color-border-secondary);
                    text-align: center;

                    h4 {
                        margin: 0 0 var(--spacing-2) 0;
                        color: var(--color-text-secondary);
                        font-size: var(--font-size-base);
                    }

                    .metric-value {
                        font-size: var(--font-size-xl);
                        font-weight: var(--font-weight-bold);
                        color: var(--color-text-primary);
                    }
                }
            }
        }
    }

    /* Responsive adjustments */
    @media (max-width: 1024px) {
        .status-cards-grid {
            grid-template-columns: repeat(2, 1fr);
        }

        .performance-content {
            grid-template-columns: 1fr !important;
        }

        .control-row {
            flex-direction: column;
            gap: var(--spacing-4) !important;
        }
    }

    @media (max-width: 768px) {
        .dashboard-header {
            flex-direction: column;
            gap: var(--spacing-4);
            text-align: center;

            .header-actions {
                justify-content: center;
            }
        }

        .status-cards-grid {
            grid-template-columns: 1fr;
        }

        .performance-metrics {
            flex-direction: column;
            gap: var(--spacing-2) !important;
        }
    }
</style>
