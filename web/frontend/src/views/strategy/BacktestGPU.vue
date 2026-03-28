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
import { useBacktestGPU } from './composables/useBacktestGPU'

const { gpuStatus, autoRefresh, refreshing, accelerationRatio, performanceGain, energyEfficiency, computeMode, monitorFrequency, activeLogTab, realtimeLogs, getAvailabilityColor, getUtilizationColor, getMemoryColor, getTemperatureStatus, getTemperatureStatusText, formatBytes, formatTime, toggleAutoRefresh, manualRefresh, handleComputeModeChange, handleMonitorFrequencyChange, runBenchmark, resetGPU } = useBacktestGPU()
</script>

<style scoped lang="scss">
@use "./styles/BacktestGPU.scss" as *;
</style>
