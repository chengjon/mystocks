<template>
    <div class="artdeco-anomaly-tracking">
        <!-- 异动跟踪概览 -->
        <div class="anomaly-overview">
            <ArtDecoStatCard
                label="检测异动数"
                :value="getAnomalyCount()"
                description="今日检测到的异常事件"
                variant="default"
            />

            <ArtDecoStatCard
                label="高风险异动"
                :value="getHighRiskCount()"
                description="需要立即关注的异常"
                variant="fall"
            />

            <ArtDecoStatCard
                label="异动成功率"
                :value="getDetectionAccuracy()"
                description="异常检测准确率"
                variant="default"
            />

            <ArtDecoStatCard
                label="平均响应时间"
                :value="getAvgResponseTime()"
                description="异动检测到告警的时间"
                variant="default"
            />
        </div>

        <!-- 实时异动监控 -->
        <ArtDecoCard class="realtime-anomaly-monitoring">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>实时异动监控</h4>
                        <p>REAL-TIME ANOMALY MONITORING</p>
                    </div>
                    <div class="monitoring-controls">
                        <ArtDecoSelect v-model="monitoringMode" :options="monitoringModeOptions" size="sm" />
                        <ArtDecoSwitch v-model="autoAlert" label="自动告警" />
                        <ArtDecoButton size="sm" variant="outline" @click="clearAllAlerts">清空告警</ArtDecoButton>
                    </div>
                </div>
            </template>

            <div class="monitoring-dashboard">
                <div class="anomaly-alerts">
                    <div class="alerts-list">
                        <div
                            v-for="alert in activeAlerts"
                            :key="alert.id"
                            class="alert-item"
                            :class="getAlertSeverityClass(alert.severity)"
                        >
                            <div class="alert-header">
                                <div class="alert-indicator">
                                    <div class="severity-dot" :class="alert.severity"></div>
                                    <span class="alert-type">{{ getAlertTypeText(alert.type) }}</span>
                                </div>
                                <div class="alert-time">
                                    {{ formatTime(alert.timestamp) }}
                                </div>
                                <div class="alert-status" :class="alert.status">
                                    {{ getStatusText(alert.status) }}
                                </div>
                            </div>

                            <div class="alert-content">
                                <div class="alert-symbol">
                                    <span class="symbol-code">{{ alert.symbol }}</span>
                                    <span class="symbol-name">{{ alert.symbolName }}</span>
                                </div>
                                <div class="alert-description">
                                    {{ alert.description }}
                                </div>
                                <div class="alert-metrics">
                                    <div class="metric">
                                        <span class="label">异动幅度:</span>
                                        <span class="value" :class="getMetricClass(alert.anomalyScore)">
                                            {{ alert.anomalyScore?.toFixed(2) }}
                                        </span>
                                    </div>
                                    <div class="metric">
                                        <span class="label">置信度:</span>
                                        <span class="value">{{ alert.confidence?.toFixed(1) }}%</span>
                                    </div>
                                    <div class="metric">
                                        <span class="label">影响范围:</span>
                                        <span class="value">{{ getImpactLevelText(alert.impactLevel) }}</span>
                                    </div>
                                </div>
                            </div>

                            <div class="alert-actions">
                                <ArtDecoButton
                                    size="sm"
                                    :type="alert.severity === 'critical' ? 'danger' : 'primary'"
                                    @click="handleAlertAction(alert, 'investigate')"
                                >
                                    立即调查
                                </ArtDecoButton>
                                <ArtDecoButton
                                    size="sm"
                                    variant="outline"
                                    @click="handleAlertAction(alert, 'acknowledge')"
                                >
                                    确认
                                </ArtDecoButton>
                                <ArtDecoButton size="sm" variant="outline" @click="handleAlertAction(alert, 'ignore')">
                                    忽略
                                </ArtDecoButton>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="anomaly-stats">
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"></path>
                                </svg>
                            </div>
                            <div class="stat-content">
                                <div class="stat-value">{{ criticalAlerts }}</div>
                                <div class="stat-label">紧急告警</div>
                            </div>
                        </div>

                        <div class="stat-item">
                            <div class="stat-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                            </div>
                            <div class="stat-content">
                                <div class="stat-value">{{ warningAlerts }}</div>
                                <div class="stat-label">警告告警</div>
                            </div>
                        </div>

                        <div class="stat-item">
                            <div class="stat-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <circle cx="12" cy="12" r="10"></circle>
                                    <path d="M9 12l2 2 4-4"></path>
                                </svg>
                            </div>
                            <div class="stat-content">
                                <div class="stat-value">{{ resolvedAlerts }}</div>
                                <div class="stat-label">已解决</div>
                            </div>
                        </div>

                        <div class="stat-item">
                            <div class="stat-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                            </div>
                            <div class="stat-content">
                                <div class="stat-value">{{ pendingAlerts }}</div>
                                <div class="stat-label">待处理</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 异常模式识别 -->
        <ArtDecoCard class="anomaly-patterns">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path
                                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                            ></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>异常模式识别</h4>
                        <p>ANOMALY PATTERN RECOGNITION</p>
                    </div>
                </div>
            </template>

            <div class="patterns-analysis">
                <div class="detected-patterns">
                    <div class="patterns-grid">
                        <div v-for="pattern in detectedPatterns" :key="pattern.id" class="pattern-card">
                            <div class="pattern-header">
                                <div class="pattern-type">
                                    <span class="type-badge" :class="pattern.type">
                                        {{ getPatternTypeText(pattern.type) }}
                                    </span>
                                </div>
                                <div class="pattern-frequency">出现{{ pattern.frequency }}次</div>
                            </div>

                            <div class="pattern-content">
                                <div class="pattern-name">{{ pattern.name }}</div>
                                <div class="pattern-description">{{ pattern.description }}</div>
                                <div class="pattern-confidence">
                                    <div class="confidence-bar">
                                        <div class="confidence-fill" :style="{ width: pattern.confidence + '%' }"></div>
                                    </div>
                                    <span class="confidence-text">{{ pattern.confidence }}% 置信度</span>
                                </div>
                            </div>

                            <div class="pattern-examples">
                                <h6>典型案例</h6>
                                <div class="examples-list">
                                    <div v-for="example in pattern.examples" :key="example.id" class="example-item">
                                        <span class="example-symbol">{{ example.symbol }}</span>
                                        <span class="example-time">{{ formatTime(example.timestamp) }}</span>
                                        <span class="example-impact">{{ getImpactText(example.impact) }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="pattern-insights">
                    <h5>模式洞察</h5>
                    <div class="insights-list">
                        <div class="insight-item">
                            <div class="insight-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                            </div>
                            <div class="insight-content">
                                <div class="insight-title">最常见异常模式</div>
                                <div class="insight-value">{{ getMostCommonPattern() }}</div>
                                <div class="insight-description">该模式在历史数据中出现频率最高，需要重点监控</div>
                            </div>
                        </div>

                        <div class="insight-item">
                            <div class="insight-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                                </svg>
                            </div>
                            <div class="insight-content">
                                <div class="insight-title">高风险异常时段</div>
                                <div class="insight-value">{{ getHighRiskTimePeriod() }}</div>
                                <div class="insight-description">在这个时间段内发生的异常事件风险更高</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 风险等级评估 -->
        <ArtDecoCard class="risk-assessment">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>风险等级评估</h4>
                        <p>RISK LEVEL ASSESSMENT</p>
                    </div>
                </div>
            </template>

            <div class="risk-analysis">
                <div class="current-risk-level">
                    <div class="risk-gauge">
                        <div class="gauge-container">
                            <div class="gauge-background">
                                <div
                                    class="gauge-fill"
                                    :style="{ transform: `rotate(${(currentRiskLevel / 100) * 180 - 90}deg)` }"
                                    :class="getRiskGaugeClass(currentRiskLevel)"
                                ></div>
                            </div>
                            <div class="gauge-center">
                                <div class="gauge-value">{{ currentRiskLevel }}</div>
                                <div class="gauge-label">风险等级</div>
                            </div>
                            <div class="gauge-labels">
                                <span>低风险</span>
                                <span>高风险</span>
                            </div>
                        </div>
                    </div>

                    <div class="risk-description">
                        <h5>{{ getRiskLevelText(currentRiskLevel) }}</h5>
                        <p>{{ getRiskDescription(currentRiskLevel) }}</p>
                        <div class="risk-factors">
                            <div class="factor-item">
                                <span class="factor-label">异动频率:</span>
                                <span class="factor-value" :class="getFactorClass(anomalyFrequency)">
                                    {{ anomalyFrequency }}/小时
                                </span>
                            </div>
                            <div class="factor-item">
                                <span class="factor-label">平均幅度:</span>
                                <span class="factor-value" :class="getFactorClass(avgAnomalyMagnitude)">
                                    {{ avgAnomalyMagnitude.toFixed(2) }}
                                </span>
                            </div>
                            <div class="factor-item">
                                <span class="factor-label">市场影响:</span>
                                <span class="factor-value" :class="getFactorClass(marketImpact)">
                                    {{ marketImpact }}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="risk-trends">
                    <h5>风险趋势分析</h5>
                    <div class="trends-chart">
                        <!-- 风险趋势图 -->
                        <div class="trends-visualization">
                            <div class="trend-lines">
                                <div class="trend-line risk-trend">
                                    <div
                                        v-for="(point, index) in riskTrendData"
                                        :key="index"
                                        class="trend-point"
                                        :style="{
                                            left: (index / (riskTrendData.length - 1)) * 100 + '%',
                                            top: (1 - point.risk / 100) * 100 + '%'
                                        }"
                                        :title="`风险等级: ${point.risk}, 时间: ${formatTime(point.timestamp)}`"
                                    ></div>
                                </div>
                                <div class="trend-line threshold-line"></div>
                            </div>
                            <div class="trend-axis">
                                <span class="axis-start">过去24小时</span>
                                <span class="axis-end">现在</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 告警设置配置 -->
        <ArtDecoCard class="alert-configuration">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path
                                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                            ></path>
                            <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>告警设置配置</h4>
                        <p>ALERT CONFIGURATION SETTINGS</p>
                    </div>
                </div>
            </template>

            <div class="configuration-panel">
                <div class="alert-rules">
                    <div class="rules-grid">
                        <div v-for="rule in alertRules" :key="rule.id" class="rule-item">
                            <div class="rule-header">
                                <div class="rule-name">{{ rule.name }}</div>
                                <ArtDecoSwitch v-model="rule.enabled" size="sm" />
                            </div>

                            <div class="rule-description">{{ rule.description }}</div>

                            <div class="rule-settings">
                                <div class="setting-item">
                                    <label>阈值</label>
                                    <ArtDecoInput v-model="rule.threshold" size="sm" type="number" :step="rule.step" />
                                </div>
                                <div class="setting-item">
                                    <label>严重程度</label>
                                    <ArtDecoSelect v-model="rule.severity" :options="severityOptions" size="sm" />
                                </div>
                                <div class="setting-item">
                                    <label>冷却时间</label>
                                    <ArtDecoSelect v-model="rule.cooldown" :options="cooldownOptions" size="sm" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="notification-settings">
                    <h5>通知设置</h5>
                    <div class="notification-options">
                        <div class="option-item">
                            <ArtDecoSwitch v-model="emailNotifications" label="邮件通知" />
                        </div>
                        <div class="option-item">
                            <ArtDecoSwitch v-model="smsNotifications" label="短信通知" />
                        </div>
                        <div class="option-item">
                            <ArtDecoSwitch v-model="appNotifications" label="应用内通知" />
                        </div>
                        <div class="option-item">
                            <ArtDecoSwitch v-model="soundAlerts" label="声音告警" />
                        </div>
                    </div>

                    <div class="notification-schedule">
                        <h6>通知时间</h6>
                        <div class="schedule-options">
                            <ArtDecoSwitch v-model="workdayOnly" label="仅工作日" />
                            <div class="time-range">
                                <ArtDecoInput v-model="startTime" type="time" size="sm" placeholder="开始时间" />
                                <span>至</span>
                                <ArtDecoInput v-model="endTime" type="time" size="sm" placeholder="结束时间" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>
    </div>
</template>

<script setup lang="ts">
    import { ref, computed } from 'vue'
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
    import ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'
    import ArtDecoSelect from '@/components/artdeco/base/ArtDecoSelect.vue'
    import ArtDecoSwitch from '@/components/artdeco/base/ArtDecoSwitch.vue'
    import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'
    import ArtDecoInput from '@/components/artdeco/base/ArtDecoInput.vue'

    interface Props {
        data: any
        symbol?: string
        loading?: boolean
    }

    const props = defineProps<Props>()

    // 响应式数据
    const monitoringMode = ref('realtime')
    const autoAlert = ref(true)

    const emailNotifications = ref(true)
    const smsNotifications = ref(false)
    const appNotifications = ref(true)
    const soundAlerts = ref(true)
    const workdayOnly = ref(true)
    const startTime = ref('09:00')
    const endTime = ref('18:00')

    // 计算属性
    const anomalyData = computed(() => props.data?.anomaly || {})
    const activeAlerts = computed(() => anomalyData.value?.activeAlerts || [])
    const detectedPatterns = computed(() => anomalyData.value?.patterns || [])
    const riskTrendData = computed(() => anomalyData.value?.riskTrend || [])

    const currentRiskLevel = computed(() => anomalyData.value?.currentRiskLevel || 0)
    const anomalyFrequency = computed(() => anomalyData.value?.anomalyFrequency || 0)
    const avgAnomalyMagnitude = computed(() => anomalyData.value?.avgAnomalyMagnitude || 0)
    const marketImpact = computed(() => anomalyData.value?.marketImpact || '中等')

    // 告警统计
    const criticalAlerts = computed(() => activeAlerts.value.filter((a: any) => a.severity === 'critical').length)
    const warningAlerts = computed(() => activeAlerts.value.filter((a: any) => a.severity === 'warning').length)
    const resolvedAlerts = computed(() => anomalyData.value?.resolvedAlerts || 0)
    const pendingAlerts = computed(() => activeAlerts.value.filter((a: any) => a.status === 'pending').length)

    // 配置选项
    const monitoringModeOptions = [
        { label: '实时监控', value: 'realtime' },
        { label: '定时扫描', value: 'scheduled' },
        { label: '手动检测', value: 'manual' }
    ]

    const severityOptions = [
        { label: '低', value: 'low' },
        { label: '中', value: 'medium' },
        { label: '高', value: 'high' },
        { label: '紧急', value: 'critical' }
    ]

    const cooldownOptions = [
        { label: '5分钟', value: '5m' },
        { label: '15分钟', value: '15m' },
        { label: '1小时', value: '1h' },
        { label: '4小时', value: '4h' }
    ]

    const alertRules = ref([
        {
            id: 1,
            name: '价格异动',
            description: '股价异常波动检测',
            enabled: true,
            threshold: 5,
            step: 0.1,
            severity: 'high',
            cooldown: '15m'
        },
        {
            id: 2,
            name: '成交量激增',
            description: '成交量异常放大检测',
            enabled: true,
            threshold: 200,
            step: 10,
            severity: 'medium',
            cooldown: '30m'
        },
        {
            id: 3,
            name: '龙虎榜异动',
            description: '龙虎榜数据异常检测',
            enabled: false,
            threshold: 3,
            step: 1,
            severity: 'high',
            cooldown: '1h'
        },
        {
            id: 4,
            name: '资金流异常',
            description: '资金流向异常检测',
            enabled: true,
            threshold: 50,
            step: 5,
            severity: 'medium',
            cooldown: '30m'
        }
    ])

    // 格式化函数
    const getAnomalyCount = (): string => {
        return activeAlerts.value.length.toString()
    }

    const getHighRiskCount = (): string => {
        return activeAlerts.value
            .filter((a: any) => a.severity === 'critical' || a.severity === 'high')
            .length.toString()
    }

    const getDetectionAccuracy = (): string => {
        const accuracy = anomalyData.value?.detectionAccuracy || 0
        return `${(accuracy * 100).toFixed(1)}%`
    }

    const getAvgResponseTime = (): string => {
        const responseTime = anomalyData.value?.avgResponseTime || 0
        if (responseTime < 60) return `${responseTime.toFixed(0)}秒`
        if (responseTime < 3600) return `${(responseTime / 60).toFixed(0)}分钟`
        return `${(responseTime / 3600).toFixed(1)}小时`
    }

    const getAlertSeverityClass = (severity: string): string => {
        return severity
    }

    const getAlertTypeText = (type: string): string => {
        const types: Record<string, string> = {
            price_spike: '价格异动',
            volume_surge: '成交量激增',
            longhu_abnormal: '龙虎榜异常',
            capital_flow: '资金流异常',
            technical_break: '技术突破',
            news_impact: '新闻影响'
        }
        return types[type] || type
    }

    const getStatusText = (status: string): string => {
        const statuses: Record<string, string> = {
            active: '活跃',
            acknowledged: '已确认',
            investigating: '调查中',
            resolved: '已解决',
            ignored: '已忽略'
        }
        return statuses[status] || status
    }

    const getMetricClass = (score: number): string => {
        if (score >= 8) return 'critical'
        if (score >= 6) return 'high'
        if (score >= 4) return 'medium'
        return 'low'
    }

    const getImpactLevelText = (level: string): string => {
        const levels: Record<string, string> = {
            low: '轻微影响',
            medium: '中等影响',
            high: '重大影响',
            critical: '系统性影响'
        }
        return levels[level] || level
    }

    const formatTime = (timestamp: string): string => {
        return new Date(timestamp).toLocaleString('zh-CN', {
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    const handleAlertAction = (alert: any, action: string) => {
        console.log(`Alert action: ${action} for alert ${alert.id}`)
        // 这里可以调用API执行相应的操作
    }

    const clearAllAlerts = () => {
        console.log('Clearing all alerts')
        // 这里可以调用API清空所有告警
    }

    const getPatternTypeText = (type: string): string => {
        const types: Record<string, string> = {
            price_pattern: '价格模式',
            volume_pattern: '成交量模式',
            technical_pattern: '技术模式',
            fundamental_pattern: '基本面模式'
        }
        return types[type] || type
    }

    const getMostCommonPattern = (): string => {
        if (!detectedPatterns.value.length) return '暂无'
        const mostCommon = detectedPatterns.value.reduce((prev: any, current: any) =>
            prev.frequency > current.frequency ? prev : current
        )
        return mostCommon.name
    }

    const getHighRiskTimePeriod = (): string => {
        const periods = anomalyData.value?.highRiskPeriods || []
        if (!periods.length) return '全天'

        // 返回风险最高的时段
        const highRisk = periods.find((p: any) => p.risk === 'high')
        return highRisk ? `${highRisk.start}-${highRisk.end}` : '9:00-11:30'
    }

    const getImpactText = (impact: string): string => {
        const impacts: Record<string, string> = {
            low: '轻微',
            medium: '中等',
            high: '重大',
            critical: '严重'
        }
        return impacts[impact] || impact
    }

    const getRiskGaugeClass = (level: number): string => {
        if (level >= 80) return 'critical'
        if (level >= 60) return 'high'
        if (level >= 40) return 'medium'
        return 'low'
    }

    const getRiskLevelText = (level: number): string => {
        if (level >= 80) return '极高风险'
        if (level >= 60) return '高风险'
        if (level >= 40) return '中等风险'
        if (level >= 20) return '低风险'
        return '极低风险'
    }

    const getRiskDescription = (level: number): string => {
        if (level >= 80) return '市场出现严重异常，需要立即采取行动'
        if (level >= 60) return '市场风险较高，建议密切关注'
        if (level >= 40) return '市场风险适中，需要适度关注'
        if (level >= 20) return '市场风险较低，可正常操作'
        return '市场风险极低，可以放心操作'
    }

    const getFactorClass = (value: any): string => {
        if (typeof value === 'number') {
            if (value >= 10) return 'high'
            if (value >= 5) return 'medium'
            return 'low'
        }
        if (value === '高') return 'high'
        if (value === '中') return 'medium'
        return 'low'
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-anomaly-tracking {
        display: grid;
        gap: var(--artdeco-spacing-6);
    }

    // ============================================
    //   ANOMALY OVERVIEW - 异动概览
    // ============================================

    .anomaly-overview {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    // ============================================
    //   REALTIME ANOMALY MONITORING - 实时异动监控
    // ============================================

    .realtime-anomaly-monitoring {
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-4);

            .header-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, var(--artdeco-gold-primary), var(--artdeco-gold-secondary));
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--artdeco-bg-dark);

                svg {
                    width: 24px;
                    height: 24px;
                }
            }

            .header-content {
                flex: 1;
                margin-left: var(--artdeco-spacing-4);

                h4 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-lg);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-1) 0;
                }

                p {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-font-size-xs);
                    color: var(--artdeco-fg-muted);
                    margin: 0;
                    letter-spacing: var(--artdeco-tracking-normal);
                }
            }

            .monitoring-controls {
                display: flex;
                gap: var(--artdeco-spacing-3);
                align-items: center;
            }
        }

        .monitoring-dashboard {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: var(--artdeco-spacing-5);

            .anomaly-alerts {
                .alerts-list {
                    display: flex;
                    flex-direction: column;
                    gap: var(--artdeco-spacing-3);

                    .alert-item {
                        @include artdeco-stepped-corners(6px);
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        padding: var(--artdeco-spacing-4);
                        position: relative;
                        overflow: hidden;
                        transition: all var(--artdeco-transition-base);

                        // 几何角落装饰
                        @include artdeco-geometric-corners(
                            $color: var(--artdeco-gold-primary),
                            $size: 12px,
                            $border-width: 1px
                        );

                        // 悬停效果
                        @include artdeco-hover-lift-glow;

                        &.critical {
                            border-color: #ef4444;
                            background: linear-gradient(135deg, rgba(239, 68, 68, 0.05), transparent);
                            box-shadow: 0 0 20px rgba(239, 68, 68, 0.2);
                        }

                        &.high {
                            border-color: #f59e0b;
                            background: linear-gradient(135deg, rgba(245, 158, 11, 0.05), transparent);
                        }

                        &.medium {
                            border-color: #f97316;
                            background: linear-gradient(135deg, rgba(249, 115, 22, 0.05), transparent);
                        }

                        &.low {
                            border-color: var(--artdeco-gold-primary);
                            background: linear-gradient(135deg, rgba(212, 175, 55, 0.05), transparent);
                        }

                        .alert-header {
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-bottom: var(--artdeco-spacing-3);

                            .alert-indicator {
                                display: flex;
                                align-items: center;
                                gap: var(--artdeco-spacing-2);

                                .severity-dot {
                                    width: 8px;
                                    height: 8px;
                                    border-radius: 50%;

                                    &.critical {
                                        background: #ef4444;
                                        box-shadow: 0 0 6px rgba(239, 68, 68, 0.5);
                                    }

                                    &.high {
                                        background: #f59e0b;
                                        box-shadow: 0 0 6px rgba(245, 158, 11, 0.5);
                                    }

                                    &.medium {
                                        background: #f97316;
                                        box-shadow: 0 0 6px rgba(249, 115, 22, 0.5);
                                    }

                                    &.low {
                                        background: var(--artdeco-gold-primary);
                                        box-shadow: 0 0 6px rgba(212, 175, 55, 0.5);
                                    }
                                }

                                .alert-type {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-sm);
                                    font-weight: 600;
                                    color: var(--artdeco-fg-primary);
                                    text-transform: uppercase;
                                    letter-spacing: var(--artdeco-tracking-wide);
                                }
                            }

                            .alert-time {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-xs);
                                color: var(--artdeco-fg-muted);
                            }

                            .alert-status {
                                padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
                                border-radius: 4px;
                                font-size: var(--artdeco-font-size-xs);
                                font-weight: 600;
                                text-transform: uppercase;
                                letter-spacing: var(--artdeco-tracking-wide);

                                &.active {
                                    background: var(--artdeco-up);
                                    color: white;
                                }

                                &.acknowledged {
                                    background: var(--artdeco-gold-primary);
                                    color: var(--artdeco-bg-dark);
                                }

                                &.investigating {
                                    background: #3b82f6;
                                    color: white;
                                }

                                &.resolved {
                                    background: var(--artdeco-up);
                                    color: white;
                                }

                                &.ignored {
                                    background: var(--artdeco-fg-muted);
                                    color: white;
                                }
                            }
                        }

                        .alert-content {
                            margin-bottom: var(--artdeco-spacing-3);

                            .alert-symbol {
                                margin-bottom: var(--artdeco-spacing-2);

                                .symbol-code {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-lg);
                                    font-weight: 600;
                                    color: var(--artdeco-fg-primary);
                                    display: block;
                                    margin-bottom: var(--artdeco-spacing-1);
                                }

                                .symbol-name {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-sm);
                                    color: var(--artdeco-fg-muted);
                                }
                            }

                            .alert-description {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-sm);
                                color: var(--artdeco-fg-secondary);
                                line-height: 1.5;
                                margin-bottom: var(--artdeco-spacing-2);
                            }

                            .alert-metrics {
                                display: grid;
                                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                                gap: var(--artdeco-spacing-3);

                                .metric {
                                    display: flex;
                                    justify-content: space-between;
                                    align-items: center;

                                    .label {
                                        font-family: var(--artdeco-font-body);
                                        font-size: var(--artdeco-font-size-xs);
                                        color: var(--artdeco-fg-muted);
                                        font-weight: 600;
                                    }

                                    .value {
                                        font-family: var(--artdeco-font-mono);
                                        font-size: var(--artdeco-font-size-sm);
                                        color: var(--artdeco-fg-primary);
                                        font-weight: 600;

                                        &.critical {
                                            color: #ef4444;
                                        }

                                        &.high {
                                            color: #f59e0b;
                                        }

                                        &.medium {
                                            color: #f97316;
                                        }

                                        &.low {
                                            color: var(--artdeco-gold-primary);
                                        }
                                    }
                                }
                            }
                        }

                        .alert-actions {
                            display: flex;
                            gap: var(--artdeco-spacing-2);
                            justify-content: flex-end;
                        }
                    }
                }
            }

            .anomaly-stats {
                .stats-grid {
                    display: grid;
                    grid-template-columns: 1fr;
                    gap: var(--artdeco-spacing-3);

                    .stat-item {
                        display: flex;
                        align-items: center;
                        gap: var(--artdeco-spacing-3);
                        padding: var(--artdeco-spacing-3);
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;
                        transition: all var(--artdeco-transition-base);

                        &:hover {
                            border-color: var(--artdeco-gold-primary);
                            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                        }

                        .stat-icon {
                            width: 32px;
                            height: 32px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: var(--artdeco-fg-primary);
                            flex-shrink: 0;
                        }

                        .stat-content {
                            flex: 1;

                            .stat-value {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-xl);
                                font-weight: 600;
                                color: var(--artdeco-gold-primary);
                                display: block;
                                margin-bottom: var(--artdeco-spacing-1);
                            }

                            .stat-label {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-sm);
                                color: var(--artdeco-fg-muted);
                                text-transform: uppercase;
                                letter-spacing: var(--artdeco-tracking-wide);
                            }
                        }
                    }
                }
            }
        }
    }

    // ============================================
    //   ANOMALY PATTERNS - 异常模式识别
    // ============================================

    .anomaly-patterns {
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-4);

            .header-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, var(--artdeco-gold-primary), var(--artdeco-gold-secondary));
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--artdeco-bg-dark);

                svg {
                    width: 24px;
                    height: 24px;
                }
            }

            .header-content {
                flex: 1;
                margin-left: var(--artdeco-spacing-4);

                h4 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-lg);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-1) 0;
                }

                p {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-font-size-xs);
                    color: var(--artdeco-fg-muted);
                    margin: 0;
                    letter-spacing: var(--artdeco-tracking-normal);
                }
            }
        }

        .patterns-analysis {
            .detected-patterns {
                margin-bottom: var(--artdeco-spacing-5);

                .patterns-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                    gap: var(--artdeco-spacing-4);

                    .pattern-card {
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;
                        padding: var(--artdeco-spacing-4);
                        transition: all var(--artdeco-transition-base);

                        &:hover {
                            border-color: var(--artdeco-gold-primary);
                            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                        }

                        .pattern-header {
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-bottom: var(--artdeco-spacing-3);

                            .pattern-type {
                                .type-badge {
                                    padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
                                    border-radius: 4px;
                                    font-size: var(--artdeco-font-size-xs);
                                    font-weight: 600;
                                    text-transform: uppercase;
                                    letter-spacing: var(--artdeco-tracking-wide);

                                    &.price_pattern {
                                        background: var(--artdeco-up);
                                        color: white;
                                    }

                                    &.volume_pattern {
                                        background: var(--artdeco-down);
                                        color: white;
                                    }

                                    &.technical_pattern {
                                        background: var(--artdeco-gold-primary);
                                        color: var(--artdeco-bg-dark);
                                    }

                                    &.fundamental_pattern {
                                        background: #8b5cf6;
                                        color: white;
                                    }
                                }
                            }

                            .pattern-frequency {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-sm);
                                color: var(--artdeco-fg-muted);
                                font-weight: 600;
                            }
                        }

                        .pattern-content {
                            margin-bottom: var(--artdeco-spacing-3);

                            .pattern-name {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-md);
                                font-weight: 600;
                                color: var(--artdeco-fg-primary);
                                margin-bottom: var(--artdeco-spacing-1);
                            }

                            .pattern-description {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-sm);
                                color: var(--artdeco-fg-secondary);
                                line-height: 1.5;
                                margin-bottom: var(--artdeco-spacing-2);
                            }

                            .pattern-confidence {
                                display: flex;
                                align-items: center;
                                gap: var(--artdeco-spacing-2);

                                .confidence-bar {
                                    flex: 1;
                                    height: 6px;
                                    background: var(--artdeco-bg-muted);
                                    border-radius: 3px;
                                    overflow: hidden;

                                    .confidence-fill {
                                        height: 100%;
                                        background: linear-gradient(
                                            90deg,
                                            var(--artdeco-gold-primary),
                                            var(--artdeco-gold-secondary)
                                        );
                                        border-radius: 3px;
                                        transition: width var(--artdeco-transition-base);
                                    }
                                }

                                .confidence-text {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);
                                    font-weight: 600;
                                    min-width: 50px;
                                    text-align: right;
                                }
                            }
                        }

                        .pattern-examples {
                            h6 {
                                font-family: var(--artdeco-font-display);
                                font-size: var(--artdeco-font-size-sm);
                                font-weight: 600;
                                color: var(--artdeco-gold-primary);
                                text-transform: uppercase;
                                letter-spacing: var(--artdeco-tracking-wide);
                                margin: 0 0 var(--artdeco-spacing-2) 0;
                            }

                            .examples-list {
                                display: flex;
                                flex-direction: column;
                                gap: var(--artdeco-spacing-1);

                                .example-item {
                                    display: grid;
                                    grid-template-columns: 80px 80px 1fr;
                                    gap: var(--artdeco-spacing-2);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);

                                    .example-symbol {
                                        font-family: var(--artdeco-font-mono);
                                        font-weight: 600;
                                        color: var(--artdeco-fg-primary);
                                    }

                                    .example-time {
                                        font-family: var(--artdeco-font-mono);
                                    }

                                    .example-impact {
                                        text-align: right;
                                        font-weight: 600;
                                    }
                                }
                            }
                        }
                    }
                }
            }

            .pattern-insights {
                h5 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-md);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-4) 0;
                }

                .insights-list {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: var(--artdeco-spacing-4);

                    .insight-item {
                        display: flex;
                        gap: var(--artdeco-spacing-3);
                        padding: var(--artdeco-spacing-4);
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;
                        transition: all var(--artdeco-transition-base);

                        &:hover {
                            border-color: var(--artdeco-gold-primary);
                            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                        }

                        .insight-icon {
                            flex-shrink: 0;
                            width: 24px;
                            height: 24px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: var(--artdeco-fg-primary);
                        }

                        .insight-content {
                            flex: 1;

                            .insight-title {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-md);
                                font-weight: 600;
                                color: var(--artdeco-fg-primary);
                                margin-bottom: var(--artdeco-spacing-1);
                            }

                            .insight-description {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-sm);
                                color: var(--artdeco-fg-secondary);
                                line-height: 1.5;
                            }
                        }
                    }
                }
            }
        }
    }

    // ============================================
    //   RISK ASSESSMENT - 风险等级评估
    // ============================================

    .risk-assessment {
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-4);

            .header-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, var(--artdeco-gold-primary), var(--artdeco-gold-secondary));
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--artdeco-bg-dark);

                svg {
                    width: 24px;
                    height: 24px;
                }
            }

            .header-content {
                flex: 1;
                margin-left: var(--artdeco-spacing-4);

                h4 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-lg);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-1) 0;
                }

                p {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-font-size-xs);
                    color: var(--artdeco-fg-muted);
                    margin: 0;
                    letter-spacing: var(--artdeco-tracking-normal);
                }
            }
        }

        .risk-analysis {
            .current-risk-level {
                display: grid;
                grid-template-columns: 300px 1fr;
                gap: var(--artdeco-spacing-5);
                margin-bottom: var(--artdeco-spacing-5);

                .risk-gauge {
                    .gauge-container {
                        position: relative;
                        width: 200px;
                        height: 200px;
                        margin: 0 auto;

                        .gauge-background {
                            position: relative;
                            width: 100%;
                            height: 100%;
                            border-radius: 50%;
                            background: conic-gradient(
                                from 0deg,
                                rgba(34, 197, 94, 0.2) 0deg,
                                rgba(212, 175, 55, 0.4) 45deg,
                                rgba(249, 115, 22, 0.6) 90deg,
                                rgba(239, 68, 68, 0.8) 180deg,
                                rgba(239, 68, 68, 0.8) 180deg
                            );

                            .gauge-fill {
                                position: absolute;
                                top: 0;
                                left: 0;
                                width: 100%;
                                height: 100%;
                                border-radius: 50%;
                                background: conic-gradient(
                                    from 0deg,
                                    transparent 0deg,
                                    transparent 180deg,
                                    rgba(239, 68, 68, 0.9) 180deg,
                                    rgba(239, 68, 68, 0.9) 360deg
                                );
                                clip-path: polygon(50% 50%, 50% 0%, 100% 0%, 100% 100%);
                                transition: transform var(--artdeco-transition-base);
                            }
                        }

                        .gauge-center {
                            position: absolute;
                            top: 50%;
                            left: 50%;
                            transform: translate(-50%, -50%);
                            text-align: center;

                            .gauge-value {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-xl);
                                font-weight: 600;
                                color: var(--artdeco-gold-primary);
                                display: block;
                                margin-bottom: var(--artdeco-spacing-1);
                            }

                            .gauge-label {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-xs);
                                color: var(--artdeco-fg-muted);
                                text-transform: uppercase;
                                letter-spacing: var(--artdeco-tracking-wide);
                            }
                        }

                        .gauge-labels {
                            position: absolute;
                            top: 10px;
                            left: 10px;
                            right: 10px;
                            bottom: 10px;
                            display: flex;
                            justify-content: space-between;
                            align-items: center;

                            span {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-xs);
                                color: var(--artdeco-fg-muted);
                                text-transform: uppercase;
                                letter-spacing: var(--artdeco-tracking-wide);
                            }
                        }
                    }
                }

                .risk-description {
                    h5 {
                        font-family: var(--artdeco-font-display);
                        font-size: var(--artdeco-font-size-lg);
                        font-weight: 600;
                        color: var(--artdeco-gold-primary);
                        text-transform: uppercase;
                        letter-spacing: var(--artdeco-tracking-wide);
                        margin: 0 0 var(--artdeco-spacing-2) 0;
                    }

                    p {
                        font-family: var(--artdeco-font-body);
                        font-size: var(--artdeco-font-size-sm);
                        color: var(--artdeco-fg-secondary);
                        line-height: 1.5;
                        margin-bottom: var(--artdeco-spacing-3);
                    }

                    .risk-factors {
                        .factor-item {
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-bottom: var(--artdeco-spacing-2);

                            .factor-label {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-sm);
                                color: var(--artdeco-fg-muted);
                                font-weight: 600;
                            }

                            .factor-value {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-sm);
                                color: var(--artdeco-fg-primary);
                                font-weight: 600;

                                &.high {
                                    color: #ef4444;
                                }

                                &.medium {
                                    color: #f59e0b;
                                }

                                &.low {
                                    color: var(--artdeco-up);
                                }
                            }
                        }
                    }
                }
            }

            .risk-trends {
                h5 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-md);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-4) 0;
                }

                .trends-chart {
                    height: 200px;
                    background: var(--artdeco-bg-card);
                    border: 1px solid var(--artdeco-border-default);
                    border-radius: 8px;
                    padding: var(--artdeco-spacing-4);
                    position: relative;
                    overflow: hidden;

                    // 几何装饰
                    @include artdeco-geometric-corners(
                        $color: var(--artdeco-gold-primary),
                        $size: 12px,
                        $border-width: 1px
                    );

                    .trends-visualization {
                        position: relative;
                        width: 100%;
                        height: 100%;

                        .trend-lines {
                            position: relative;
                            width: 100%;
                            height: 100%;

                            .trend-line {
                                &.risk-trend {
                                    position: absolute;
                                    width: 100%;
                                    height: 2px;
                                    background: linear-gradient(90deg, var(--artdeco-up), var(--artdeco-down));
                                    top: 50%;
                                    transform: translateY(-50%);
                                    border-radius: 1px;
                                }

                                &.threshold-line {
                                    position: absolute;
                                    width: 100%;
                                    height: 1px;
                                    background: var(--artdeco-gold-primary);
                                    top: 20%;
                                    opacity: 0.5;
                                    border-style: dashed;
                                }
                            }
                        }

                        .trend-axis {
                            position: absolute;
                            bottom: 0;
                            left: 0;
                            right: 0;
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            padding-top: var(--artdeco-spacing-2);

                            .axis-start,
                            .axis-end {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-xs);
                                color: var(--artdeco-fg-muted);
                                text-transform: uppercase;
                                letter-spacing: var(--artdeco-tracking-wide);
                            }
                        }
                    }
                }
            }
        }
    }

    // ============================================
    //   ALERT CONFIGURATION - 告警设置配置
    // ============================================

    .alert-configuration {
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-4);

            .header-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, var(--artdeco-gold-primary), var(--artdeco-gold-secondary));
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--artdeco-bg-dark);

                svg {
                    width: 24px;
                    height: 24px;
                }
            }

            .header-content {
                flex: 1;
                margin-left: var(--artdeco-spacing-4);

                h4 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-lg);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-1) 0;
                }

                p {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-font-size-xs);
                    color: var(--artdeco-fg-muted);
                    margin: 0;
                    letter-spacing: var(--artdeco-tracking-normal);
                }
            }
        }

        .configuration-panel {
            .alert-rules {
                margin-bottom: var(--artdeco-spacing-5);

                .rules-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                    gap: var(--artdeco-spacing-4);

                    .rule-item {
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;
                        padding: var(--artdeco-spacing-4);
                        transition: all var(--artdeco-transition-base);

                        &:hover {
                            border-color: var(--artdeco-gold-primary);
                            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                        }

                        .rule-header {
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-bottom: var(--artdeco-spacing-3);

                            .rule-name {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-md);
                                font-weight: 600;
                                color: var(--artdeco-fg-primary);
                            }
                        }

                        .rule-description {
                            font-family: var(--artdeco-font-body);
                            font-size: var(--artdeco-font-size-sm);
                            color: var(--artdeco-fg-secondary);
                            line-height: 1.5;
                            margin-bottom: var(--artdeco-spacing-3);
                        }

                        .rule-settings {
                            display: grid;
                            grid-template-columns: 1fr 1fr 1fr;
                            gap: var(--artdeco-spacing-3);

                            .setting-item {
                                display: flex;
                                flex-direction: column;
                                gap: var(--artdeco-spacing-1);

                                label {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);
                                    font-weight: 600;
                                    text-transform: uppercase;
                                    letter-spacing: var(--artdeco-tracking-wide);
                                }
                            }
                        }
                    }
                }
            }

            .notification-settings {
                h5 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-md);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-4) 0;
                }

                .notification-options {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: var(--artdeco-spacing-3);
                    margin-bottom: var(--artdeco-spacing-4);

                    .option-item {
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        padding: var(--artdeco-spacing-3);
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;
                        transition: all var(--artdeco-transition-base);

                        &:hover {
                            border-color: var(--artdeco-gold-primary);
                            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                        }
                    }
                }

                .notification-schedule {
                    h6 {
                        font-family: var(--artdeco-font-display);
                        font-size: var(--artdeco-font-size-sm);
                        font-weight: 600;
                        color: var(--artdeco-gold-primary);
                        text-transform: uppercase;
                        letter-spacing: var(--artdeco-tracking-wide);
                        margin: 0 0 var(--artdeco-spacing-3) 0;
                    }

                    .schedule-options {
                        display: flex;
                        flex-direction: column;
                        gap: var(--artdeco-spacing-3);

                        .time-range {
                            display: flex;
                            align-items: center;
                            gap: var(--artdeco-spacing-2);

                            span {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-sm);
                                color: var(--artdeco-fg-muted);
                            }
                        }
                    }
                }
            }
        }
    }

    // ============================================
    //   RESPONSIVE DESIGN - 响应式设计
    // ============================================

    @media (max-width: 768px) {
        .artdeco-anomaly-tracking {
            gap: var(--artdeco-spacing-4);
        }

        .anomaly-overview {
            grid-template-columns: 1fr;
        }

        .realtime-anomaly-monitoring {
            .section-header {
                flex-direction: column;
                align-items: flex-start;
                gap: var(--artdeco-spacing-3);

                .header-content {
                    margin-left: 0;
                }

                .monitoring-controls {
                    width: 100%;
                    justify-content: space-between;
                    flex-wrap: wrap;
                }
            }

            .monitoring-dashboard {
                grid-template-columns: 1fr;
            }

            .alert-item {
                .alert-header {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: var(--artdeco-spacing-2);
                }

                .alert-metrics {
                    grid-template-columns: 1fr;
                }

                .alert-actions {
                    flex-wrap: wrap;
                    justify-content: center;
                }
            }
        }

        .anomaly-patterns {
            .patterns-analysis {
                .detected-patterns {
                    .patterns-grid {
                        grid-template-columns: 1fr;
                    }
                }

                .pattern-insights {
                    .insights-list {
                        grid-template-columns: 1fr;
                    }
                }
            }
        }

        .risk-assessment {
            .risk-analysis {
                .current-risk-level {
                    grid-template-columns: 1fr;
                    gap: var(--artdeco-spacing-4);
                }
            }
        }

        .alert-configuration {
            .configuration-panel {
                .alert-rules {
                    .rules-grid {
                        grid-template-columns: 1fr;
                    }

                    .rule-item {
                        .rule-settings {
                            grid-template-columns: 1fr;
                        }
                    }
                }

                .notification-options {
                    grid-template-columns: 1fr;
                }
            }
        }
    }
</style>
