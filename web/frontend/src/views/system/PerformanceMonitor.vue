<template>
    <div class="performance-monitor">
        <ArtDecoCard class="monitor-card" hoverable>
            <template #header>
                <div class="card-header">
                    <div class="header-icon">📊</div>
                    <div class="header-text">
                        <div class="title">性能监控</div>
                        <div class="subtitle">CORE WEB VITALS</div>
                    </div>
                    <div class="header-actions">
                        <ArtDecoButton @click="startMonitoring" :loading="monitoring" variant="solid" size="sm">
                            {{ monitoring ? '监控中...' : '开始监控' }}
                        </ArtDecoButton>
                    </div>
                </div>
            </template>

            <!-- Core Web Vitals Metrics -->
            <div class="metrics-grid">
                <!-- Largest Contentful Paint (LCP) -->
                <div class="metric-card lcp">
                    <div class="metric-header">
                        <div class="metric-icon">🏁</div>
                        <div class="metric-title">LCP</div>
                        <div class="metric-subtitle">Largest Contentful Paint</div>
                    </div>
                    <div class="metric-value">
                        <div class="value">{{ formatTime(lcp) }}</div>
                        <div class="status" :class="getLCPStatus(lcp)">
                            {{ getLCPStatusText(lcp) }}
                        </div>
                    </div>
                    <div class="metric-bar">
                        <div
                            class="bar-fill"
                            :style="{ width: getLCPProgress(lcp) + '%' }"
                            :class="getLCPStatus(lcp)"
                        ></div>
                    </div>
                </div>

                <!-- First Input Delay (FID) -->
                <div class="metric-card fid">
                    <div class="metric-header">
                        <div class="metric-icon">👆</div>
                        <div class="metric-title">FID</div>
                        <div class="metric-subtitle">First Input Delay</div>
                    </div>
                    <div class="metric-value">
                        <div class="value">{{ formatTime(fid) }}</div>
                        <div class="status" :class="getFIDStatus(fid)">
                            {{ getFIDStatusText(fid) }}
                        </div>
                    </div>
                    <div class="metric-bar">
                        <div
                            class="bar-fill"
                            :style="{ width: getFIDProgress(fid) + '%' }"
                            :class="getFIDStatus(fid)"
                        ></div>
                    </div>
                </div>

                <!-- Cumulative Layout Shift (CLS) -->
                <div class="metric-card cls">
                    <div class="metric-header">
                        <div class="metric-icon">📐</div>
                        <div class="metric-title">CLS</div>
                        <div class="metric-subtitle">Cumulative Layout Shift</div>
                    </div>
                    <div class="metric-value">
                        <div class="value">{{ cls.toFixed(4) }}</div>
                        <div class="status" :class="getCLSStatus(cls)">
                            {{ getCLSStatusText(cls) }}
                        </div>
                    </div>
                    <div class="metric-bar">
                        <div
                            class="bar-fill"
                            :style="{ width: getCLSProgress(cls) + '%' }"
                            :class="getCLSStatus(cls)"
                        ></div>
                    </div>
                </div>
            </div>

            <!-- Performance Trend Chart -->
            <div class="trend-section">
                <div class="section-header">
                    <div class="section-icon">📈</div>
                    <div class="section-title">性能趋势</div>
                    <div class="section-subtitle">PERFORMANCE TRENDS</div>
                </div>

                <div class="trend-chart" v-if="performanceHistory.length > 0">
                    <div class="chart-placeholder">
                        <div class="placeholder-icon">📊</div>
                        <div class="placeholder-text">性能趋势图表</div>
                        <div class="placeholder-subtext">Performance Trend Chart</div>
                    </div>
                </div>

                <div v-else class="empty-state">
                    <div class="empty-icon">📈</div>
                    <div class="empty-text">暂无性能数据</div>
                </div>
            </div>

            <!-- Optimization Suggestions -->
            <div class="suggestions-section">
                <div class="section-header">
                    <div class="section-icon">💡</div>
                    <div class="section-title">优化建议</div>
                    <div class="section-subtitle">OPTIMIZATION SUGGESTIONS</div>
                </div>

                <div class="suggestions-list">
                    <div
                        v-for="(suggestion, _idx) in optimizationSuggestions"
                        :key="suggestion.id"
                        class="suggestion-item"
                        :class="{ applied: suggestion.applied }"
                    >
                        <div class="suggestion-icon">{{ suggestion.icon }}</div>
                        <div class="suggestion-content">
                            <div class="suggestion-title">{{ suggestion.title }}</div>
                            <div class="suggestion-description">{{ suggestion.description }}</div>
                            <div class="suggestion-impact">
                                <span class="impact-label">预期改善:</span>
                                <span class="impact-value">{{ suggestion.impact }}</span>
                            </div>
                        </div>
                        <div class="suggestion-actions">
                            <ArtDecoButton
                                v-if="!suggestion.applied"
                                @click="applySuggestion(suggestion)"
                                variant="solid"
                                size="sm"
                            >
                                应用
                            </ArtDecoButton>
                            <div v-else class="applied-badge">已应用</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Performance Budget -->
            <div class="budget-section">
                <div class="section-header">
                    <div class="section-icon">🎯</div>
                    <div class="section-title">性能预算</div>
                    <div class="section-subtitle">PERFORMANCE BUDGET</div>
                </div>

                <div class="budget-grid">
                    <div class="budget-item">
                        <div class="budget-label">JavaScript Bundle</div>
                        <div class="budget-value">
                            <div class="value">{{ formatBytes(bundleSize) }}</div>
                            <div class="budget-limit">预算: {{ formatBytes(bundleBudget) }}</div>
                        </div>
                        <div class="budget-bar">
                            <div
                                class="bar-fill"
                                :style="{ width: getBundleProgress() + '%' }"
                                :class="getBundleStatus()"
                            ></div>
                        </div>
                    </div>

                    <div class="budget-item">
                        <div class="budget-label">首次内容绘制</div>
                        <div class="budget-value">
                            <div class="value">{{ formatTime(fcp) }}</div>
                            <div class="budget-limit">预算: {{ formatTime(fcpBudget) }}</div>
                        </div>
                        <div class="budget-bar">
                            <div
                                class="bar-fill"
                                :style="{ width: getFCPProgress() + '%' }"
                                :class="getFCPStatus()"
                            ></div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>
    </div>
</template>

<script setup lang="ts">
    import { ref, onMounted } from 'vue'
    import { ElMessage } from 'element-plus'
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'

    // Types
    interface PerformanceMetrics {
        lcp: number
        fid: number
        cls: number
        fcp: number
    }

    interface OptimizationSuggestion {
        id: string
        title: string
        description: string
        impact: string
        icon: string
        applied: boolean
    }

    interface PerformanceHistory {
        timestamp: number
        metrics: PerformanceMetrics
    }

    // Reactive data
    const monitoring = ref(false)
    const lcp = ref(0)
    const fid = ref(0)
    const cls = ref(0)
    const fcp = ref(0)
    const bundleSize = ref(0)
    const performanceHistory = ref<PerformanceHistory[]>([])
    const optimizationSuggestions = ref<OptimizationSuggestion[]>([])

    // Performance budgets
    const bundleBudget = 500 * 1024 // 500KB
    const fcpBudget = 1800 // 1.8 seconds

    // Methods
    const startMonitoring = async () => {
        if (monitoring.value) {
            monitoring.value = false
            return
        }

        monitoring.value = true

        try {
            // Start monitoring Core Web Vitals
            await monitorCoreWebVitals()

            // Load optimization suggestions
            await loadOptimizationSuggestions()

            // Monitor performance over time
            const interval = setInterval(() => {
                if (!monitoring.value) {
                    clearInterval(interval)
                    return
                }

                updatePerformanceMetrics()
            }, 5000) // Update every 5 seconds

            ElMessage.success('性能监控已启动')
        } catch (error) {
            console.error('Failed to start monitoring:', error)
            ElMessage.error('启动监控失败')
            monitoring.value = false
        }
    }

    const monitorCoreWebVitals = async () => {
        // Monitor LCP (Largest Contentful Paint)
        new PerformanceObserver(list => {
            const entries = list.getEntries()
            const lastEntry = entries[entries.length - 1]
            lcp.value = lastEntry.startTime
        }).observe({ entryTypes: ['largest-contentful-paint'] })

        // Monitor FID (First Input Delay)
        new PerformanceObserver(list => {
            const entries = list.getEntries()
            for (const entry of entries) {
                fid.value = (entry as PerformanceEntry & { processingStart: number }).processingStart - entry.startTime
            }
        }).observe({ entryTypes: ['first-input'] })

        // Monitor CLS (Cumulative Layout Shift)
        new PerformanceObserver(list => {
            let clsValue = 0
            const entries = list.getEntries()
            for (const entry of entries) {
                clsValue += (entry as PerformanceEntry & { value: number }).value
            }
            cls.value = clsValue
        }).observe({ entryTypes: ['layout-shift'] })

        // Get FCP (First Contentful Paint)
        const navigationEntries = performance.getEntriesByType('navigation')
        if (navigationEntries.length > 0) {
            const navigationEntry = navigationEntries[0] as PerformanceNavigationTiming
            fcp.value = navigationEntry.domContentLoadedEventEnd - navigationEntry.fetchStart
        }
    }

    const updatePerformanceMetrics = () => {
        // Update metrics periodically
        const metrics: PerformanceMetrics = {
            lcp: lcp.value,
            fid: fid.value,
            cls: cls.value,
            fcp: fcp.value
        }

        performanceHistory.value.push({
            timestamp: Date.now(),
            metrics
        })

        // Keep only last 50 data points
        if (performanceHistory.value.length > 50) {
            performanceHistory.value.shift()
        }
    }

    const loadOptimizationSuggestions = async () => {
        optimizationSuggestions.value = [
            {
                id: '1',
                title: '启用代码分割',
                description: '将路由组件进行代码分割，减少初始包体积',
                impact: '减少 30% 初始加载时间',
                icon: '✂️',
                applied: false
            },
            {
                id: '2',
                title: '优化图片加载',
                description: '实现懒加载和 WebP 格式支持',
                impact: '减少 25% 图片加载时间',
                icon: '🖼️',
                applied: false
            },
            {
                id: '3',
                title: '启用 Service Worker',
                description: '添加离线缓存和资源预加载',
                impact: '提高 40% 缓存命中率',
                icon: '⚡',
                applied: false
            },
            {
                id: '4',
                title: '优化字体加载',
                description: '使用 font-display: swap 和预加载关键字体',
                impact: '减少 15% 字体阻塞时间',
                icon: '🔤',
                applied: false
            }
        ]
    }

    const applySuggestion = (suggestion: OptimizationSuggestion) => {
        suggestion.applied = true
        ElMessage.success(`已应用优化: ${suggestion.title}`)
    }

    // Status and formatting methods
    const getLCPStatus = (value: number): string => {
        if (value <= 2500) return 'good'
        if (value <= 4000) return 'needs-improvement'
        return 'poor'
    }

    const getLCPStatusText = (value: number): string => {
        if (value <= 2500) return '良好'
        if (value <= 4000) return '需改进'
        return '较差'
    }

    const getLCPProgress = (value: number): number => {
        return Math.min((value / 4000) * 100, 100)
    }

    const getFIDStatus = (value: number): string => {
        if (value <= 100) return 'good'
        if (value <= 300) return 'needs-improvement'
        return 'poor'
    }

    const getFIDStatusText = (value: number): string => {
        if (value <= 100) return '良好'
        if (value <= 300) return '需改进'
        return '较差'
    }

    const getFIDProgress = (value: number): number => {
        return Math.min((value / 300) * 100, 100)
    }

    const getCLSStatus = (value: number): string => {
        if (value <= 0.1) return 'good'
        if (value <= 0.25) return 'needs-improvement'
        return 'poor'
    }

    const getCLSStatusText = (value: number): string => {
        if (value <= 0.1) return '良好'
        if (value <= 0.25) return '需改进'
        return '较差'
    }

    const getCLSProgress = (value: number): number => {
        return Math.min((value / 0.25) * 100, 100)
    }

    const getBundleStatus = (): string => {
        const ratio = bundleSize.value / bundleBudget
        if (ratio <= 0.8) return 'good'
        if (ratio <= 1.0) return 'needs-improvement'
        return 'poor'
    }

    const getBundleProgress = (): number => {
        return Math.min((bundleSize.value / bundleBudget) * 100, 100)
    }

    const getFCPStatus = (): string => {
        const ratio = fcp.value / fcpBudget
        if (ratio <= 0.8) return 'good'
        if (ratio <= 1.0) return 'needs-improvement'
        return 'poor'
    }

    const getFCPProgress = (): number => {
        return Math.min((fcp.value / fcpBudget) * 100, 100)
    }

    const formatTime = (ms: number): string => {
        if (ms < 1000) return `${ms.toFixed(0)}ms`
        return `${(ms / 1000).toFixed(2)}s`
    }

    const formatBytes = (bytes: number): string => {
        if (bytes === 0) return '0 B'
        const k = 1024
        const sizes = ['B', 'KB', 'MB', 'GB']
        const i = Math.floor(Math.log(bytes) / Math.log(k))
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    // Initialize on mount
    onMounted(async () => {
        // Load initial bundle size (simulated)
        bundleSize.value = 450 * 1024 // 450KB

        // Load initial performance metrics
        await monitorCoreWebVitals()
    })
</script>

<style scoped>
@import "./styles/PerformanceMonitor.css";
</style>
