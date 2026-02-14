<template>
    <div class="artdeco-batch-analysis-view">
        <!-- 批量分析概览 -->
        <div class="batch-overview">
            <ArtDecoStatCard
                label="分析任务总数"
                :value="getTotalTasks()"
                description="已完成的批量分析任务"
                variant="default"
            />

            <ArtDecoStatCard
                label="平均处理时间"
                :value="getAvgProcessingTime()"
                description="单个任务平均处理时长"
                variant="default"
            />

            <ArtDecoStatCard
                label="成功率"
                :value="getSuccessRate()"
                description="批量分析任务成功率"
                variant="rise"
            />

            <ArtDecoStatCard
                label="总数据量"
                :value="getTotalDataSize()"
                description="批量分析处理的总数据量"
                variant="default"
            />
        </div>

        <!-- 批量分析进度 -->
        <ArtDecoCard class="batch-progress">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M12 2v6m0 0l4-4m-4 4L8 4m4 4v10m0 0l4-4m-4 4l-4-4"></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>批量分析进度</h4>
                        <p>BATCH ANALYSIS PROGRESS</p>
                    </div>
                    <div class="progress-controls">
                        <ArtDecoSwitch v-model="autoRefresh" label="自动刷新" />
                        <ArtDecoButton size="sm" variant="outline" @click="refreshProgress">刷新</ArtDecoButton>
                    </div>
                </div>
            </template>

            <div class="progress-dashboard">
                <div class="overall-progress">
                    <div class="progress-gauge">
                        <div class="gauge-container">
                            <div class="gauge-background">
                                <div
                                    class="gauge-fill"
                                    :style="{ transform: `rotate(${(overallProgress / 100) * 180 - 90}deg)` }"
                                    :class="getProgressClass(overallProgress)"
                                ></div>
                            </div>
                            <div class="gauge-center">
                                <div class="gauge-value">{{ overallProgress }}%</div>
                                <div class="gauge-label">完成进度</div>
                            </div>
                        </div>
                    </div>

                    <div class="progress-details">
                        <div class="detail-item">
                            <span class="label">已完成:</span>
                            <span class="value">{{ completedTasks }}/{{ totalTasks }}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">进行中:</span>
                            <span class="value">{{ runningTasks }}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">待处理:</span>
                            <span class="value">{{ pendingTasks }}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">失败:</span>
                            <span class="value">{{ failedTasks }}</span>
                        </div>
                    </div>
                </div>

                <div class="task-breakdown">
                    <div class="breakdown-charts">
                        <div class="chart-item">
                            <div class="chart-title">任务状态分布</div>
                            <div class="status-pie">
                                <!-- 任务状态饼图 -->
                                <div class="pie-chart">
                                    <div
                                        v-for="(status, _idx) in taskStatusData"
                                        :key="status.name"
                                        class="pie-segment"
                                        :style="{
                                            background: status.color,
                                            transform: `rotate(${status.startAngle}deg)`,
                                            clipPath: `polygon(50% 50%, 50% 0%, ${status.endAngle > 180 ? '100%' : Math.cos(((status.endAngle - 90) * Math.PI) / 180) * 50 + 50 + '%'} ${Math.sin(((status.endAngle - 90) * Math.PI) / 180) * 50 + 50 + '%'})`
                                        }"
                                    ></div>
                                    <div class="pie-center">
                                        <div class="center-text">{{ totalTasks }}</div>
                                        <div class="center-label">总任务</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="chart-item">
                            <div class="chart-title">分析类型分布</div>
                            <div class="type-bars">
                                <div v-for="type in analysisTypeData" :key="type.name" class="type-bar">
                                    <div class="bar-label">{{ type.name }}</div>
                                    <div class="bar-container">
                                        <div class="bar-fill" :style="{ width: type.percentage + '%' }"></div>
                                    </div>
                                    <div class="bar-value">{{ type.count }}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 批量分析结果 -->
        <ArtDecoCard class="batch-results">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>批量分析结果</h4>
                        <p>BATCH ANALYSIS RESULTS</p>
                    </div>
                    <div class="results-controls">
                        <ArtDecoSelect v-model="resultsFilter" :options="filterOptions" size="sm" />
                        <ArtDecoSelect v-model="resultsSort" :options="sortOptions" size="sm" />
                    </div>
                </div>
            </template>

            <div class="results-content">
                <div class="results-summary">
                    <div class="summary-stats">
                        <div class="stat-item">
                            <div class="stat-label">平均置信度</div>
                            <div class="stat-value">{{ avgConfidence.toFixed(1) }}%</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">信号覆盖率</div>
                            <div class="stat-value">{{ signalCoverage.toFixed(1) }}%</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">数据质量评分</div>
                            <div class="stat-value" :class="getQualityClass(dataQuality)">{{ dataQuality }}/100</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">分析深度</div>
                            <div class="stat-value">{{ analysisDepth }}/10</div>
                        </div>
                    </div>
                </div>

                <div class="results-list">
                    <div class="results-table">
                        <div class="table-header">
                            <div class="col-symbol">股票代码</div>
                            <div class="col-analysis">分析类型</div>
                            <div class="col-signal">信号</div>
                            <div class="col-confidence">置信度</div>
                            <div class="col-time">完成时间</div>
                        </div>
                        <div class="table-body">
                            <div
                                v-for="(result, _idx) in filteredResults"
                                :key="result.id"
                                class="table-row"
                                :class="getResultClass(result)"
                            >
                                <div class="col-symbol">
                                    <div class="symbol-code">{{ result.symbol }}</div>
                                    <div class="symbol-name">{{ result.symbolName }}</div>
                                </div>
                                <div class="col-analysis">
                                    <span class="analysis-type">{{ getAnalysisTypeText(result.analysisType) }}</span>
                                </div>
                                <div class="col-signal">
                                    <span :class="getSignalClass(result.signal)">
                                        {{ getSignalText(result.signal) }}
                                    </span>
                                </div>
                                <div class="col-confidence">
                                    <div class="confidence-bar">
                                        <div class="confidence-fill" :style="{ width: result.confidence + '%' }"></div>
                                    </div>
                                    <div class="confidence-text">{{ result.confidence }}%</div>
                                </div>
                                <div class="col-time">
                                    {{ formatTime(result.completedAt) }}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 批量分析报告 -->
        <ArtDecoCard class="batch-report">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path
                                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                            ></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>批量分析报告</h4>
                        <p>BATCH ANALYSIS REPORT</p>
                    </div>
                    <div class="report-controls">
                        <ArtDecoButton size="sm" @click="exportReport">导出报告</ArtDecoButton>
                        <ArtDecoButton size="sm" variant="outline" @click="generateReport">生成报告</ArtDecoButton>
                    </div>
                </div>
            </template>

            <div class="report-content">
                <div class="report-summary">
                    <div class="summary-section">
                        <h5>执行概况</h5>
                        <div class="summary-grid">
                            <div class="summary-item">
                                <div class="item-label">开始时间</div>
                                <div class="item-value">{{ formatTime(batchStartTime) }}</div>
                            </div>
                            <div class="summary-item">
                                <div class="item-label">结束时间</div>
                                <div class="item-value">{{ formatTime(batchEndTime) }}</div>
                            </div>
                            <div class="summary-item">
                                <div class="item-label">总耗时</div>
                                <div class="item-value">{{ formatDuration(totalDuration) }}</div>
                            </div>
                            <div class="summary-item">
                                <div class="item-label">平均耗时</div>
                                <div class="item-value">{{ formatDuration(avgTaskDuration) }}</div>
                            </div>
                        </div>
                    </div>

                    <div class="summary-section">
                        <h5>结果统计</h5>
                        <div class="summary-grid">
                            <div class="summary-item">
                                <div class="item-label">买入信号</div>
                                <div class="item-value">{{ buySignals }}</div>
                            </div>
                            <div class="summary-item">
                                <div class="item-label">卖出信号</div>
                                <div class="item-value">{{ sellSignals }}</div>
                            </div>
                            <div class="summary-item">
                                <div class="item-label">持有信号</div>
                                <div class="item-value">{{ holdSignals }}</div>
                            </div>
                            <div class="summary-item">
                                <div class="item-label">高置信度信号</div>
                                <div class="item-value">{{ highConfidenceSignals }}</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="report-insights">
                    <h5>关键洞察</h5>
                    <div class="insights-list">
                        <div
                            v-for="(insight, _idx) in reportInsights"
                            :key="insight.id"
                            class="insight-item"
                            :class="insight.type"
                        >
                            <div class="insight-icon">
                                <svg
                                    v-if="insight.type === 'success'"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                >
                                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                                <svg
                                    v-else-if="insight.type === 'warning'"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                >
                                    <path d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                                </svg>
                            </div>
                            <div class="insight-content">
                                <div class="insight-title">{{ insight.title }}</div>
                                <div class="insight-description">{{ insight.description }}</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="report-actions">
                    <div class="action-buttons">
                        <ArtDecoButton @click="saveReport" variant="outline">保存报告</ArtDecoButton>
                        <ArtDecoButton @click="shareReport" variant="outline">分享报告</ArtDecoButton>
                        <ArtDecoButton @click="scheduleReport" variant="outline">定时报告</ArtDecoButton>
                    </div>
                </div>
            </div>
        </ArtDecoCard>
    </div>
</template>

<script setup lang="ts">
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
    import _ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'
    import ArtDecoSelect from '@/components/artdeco/base/ArtDecoSelect.vue'
    import ArtDecoSwitch from '@/components/artdeco/base/ArtDecoSwitch.vue'
    import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'
import { useArtDecoBatchAnalysisView } from './composables/useArtDecoBatchAnalysisView'

const { props, autoRefresh, resultsFilter, resultsSort, batchData, progressData, resultsData, reportData, totalTasks, completedTasks, runningTasks, pendingTasks, failedTasks, overallProgress, avgConfidence, total, signalCoverage, signaled, dataQuality, analysisDepth, batchStartTime, batchEndTime, totalDuration, start, end, avgTaskDuration, buySignals, sellSignals, holdSignals, highConfidenceSignals, taskStatusData, analysisTypeData, types, filteredResults, filtered, reportInsights, filterOptions, sortOptions, getTotalTasks, getAvgProcessingTime, duration, getSuccessRate, successRate, getTotalDataSize, size, getProgressClass, getResultClass, getSignalClass, getSignalText, texts, getAnalysisTypeText, texts, getQualityClass, formatTime, formatDuration, refreshProgress, exportReport, generateReport, saveReport, shareReport, scheduleReport, refreshTimer, startAutoRefresh, stopAutoRefresh } = useArtDecoBatchAnalysisView()
</script>

<style scoped lang="scss">
@import './styles/ArtDecoBatchAnalysisView.scss';
</style>
