<template>
    <div class="trading-dashboard">
        <!-- 页面头部 -->
        <div class="page-header">
            <div class="page-title">实时交易监控仪表板</div>
            <div class="page-subtitle">REAL-TIME TRADING MONITORING DASHBOARD</div>
            <div class="page-decorative-line"></div>
            <p class="subtitle">实时监控交易状态、策略性能、市场数据和风险指标</p>
        </div>

        <!-- 控制面板 -->
        <div class="control-panel">
            <el-row :gutter="20" class="control-buttons">
                <el-col :span="6">
                    <el-button
                        :type="isRunning ? 'danger' : 'success'"
                        :loading="controlLoading"
                        @click="toggleTradingSession"
                        class="control-btn"
                        size="large"
                    >
                        <el-icon class="btn-icon">
                            <VideoPlay v-if="!isRunning" />
                            <VideoPause v-else />
                        </el-icon>
                        {{ isRunning ? '停止交易' : '启动交易' }}
                    </el-button>
                </el-col>
                <el-col :span="6">
                    <el-button
                        type="primary"
                        @click="refreshData"
                        :loading="refreshLoading"
                        class="control-btn"
                        size="large"
                    >
                        <el-icon class="btn-icon">
                            <RefreshRight />
                        </el-icon>
                        刷新数据
                    </el-button>
                </el-col>
                <el-col :span="6">
                    <el-button type="info" @click="openStrategyManager" class="control-btn" size="large">
                        <el-icon class="btn-icon">
                            <Setting />
                        </el-icon>
                        策略管理
                    </el-button>
                </el-col>
                <el-col :span="6">
                    <el-button type="warning" @click="openRiskReport" class="control-btn" size="large">
                        <el-icon class="btn-icon">
                            <Warning />
                        </el-icon>
                        风险报告
                    </el-button>
                </el-col>
            </el-row>
        </div>

        <!-- 状态概览 -->
        <el-row :gutter="20" class="status-overview">
            <el-col :xs="24" :sm="12" :lg="6" v-for="metric in statusMetrics" :key="metric.key">
                <div class="metric-card" :class="metric.status">
                    <div class="metric-icon">
                        <el-icon :size="24">
                            <component :is="metric.icon" />
                        </el-icon>
                    </div>
                    <div class="metric-content">
                        <div class="metric-value">{{ metric.value }}</div>
                        <div class="metric-label">{{ metric.label }}</div>
                        <div class="metric-change" v-if="metric.change">
                            <el-icon :class="metric.change.type">
                                <ArrowUp v-if="metric.change.type === 'increase'" />
                                <ArrowDown v-if="metric.change.type === 'decrease'" />
                            </el-icon>
                            {{ metric.change.value }}
                        </div>
                    </div>
                </div>
            </el-col>
        </el-row>

        <!-- 主要内容区域 -->
        <el-row :gutter="20" class="main-content">
            <!-- 左侧：交易状态和策略性能 -->
            <el-col :xs="24" :lg="16">
                <el-card class="content-card" shadow="never">
                    <template #header>
                        <div class="card-header">
                            <el-icon class="card-icon"><DataAnalysis /></el-icon>
                            <span>交易状态与策略性能</span>
                            <el-tag :type="tradingStatus.type" size="small">{{ tradingStatus.text }}</el-tag>
                        </div>
                    </template>

                    <!-- 交易状态详情 -->
                    <div class="trading-details">
                        <el-descriptions :column="2" border>
                            <el-descriptions-item label="会话ID">
                                {{ tradingData.session_id || '未启动' }}
                            </el-descriptions-item>
                            <el-descriptions-item label="运行状态">
                                <el-tag :type="isRunning ? 'success' : 'info'">
                                    {{ isRunning ? '运行中' : '已停止' }}
                                </el-tag>
                            </el-descriptions-item>
                            <el-descriptions-item label="活跃头寸">
                                {{ tradingData.active_positions || 0 }} 个
                            </el-descriptions-item>
                            <el-descriptions-item label="总盈亏">
                                <span :class="tradingData.total_pnl >= 0 ? 'profit' : 'loss'">
                                    ¥{{ formatNumber(tradingData.total_pnl || 0, 2) }}
                                </span>
                            </el-descriptions-item>
                            <el-descriptions-item label="当日盈亏">
                                <span :class="tradingData.daily_pnl >= 0 ? 'profit' : 'loss'">
                                    ¥{{ formatNumber(tradingData.daily_pnl || 0, 2) }}
                                </span>
                            </el-descriptions-item>
                            <el-descriptions-item label="当前回撤">
                                <span :class="tradingData.current_drawdown > 0.05 ? 'warning' : 'normal'">
                                    {{ formatPercent(tradingData.current_drawdown || 0) }}
                                </span>
                            </el-descriptions-item>
                        </el-descriptions>
                    </div>

                    <!-- 策略性能表格 -->
                    <div class="strategy-performance">
                        <h4>策略性能监控</h4>
                        <el-table :data="strategyPerformance" stripe style="width: 100%">
                            <el-table-column prop="strategy_name" label="策略名称" width="150"></el-table-column>
                            <el-table-column prop="status" label="状态" width="100">
                                <template #default="scope">
                                    <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'">
                                        {{ scope.row.status === 'active' ? '活跃' : '非活跃' }}
                                    </el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column label="性能指标">
                                <template #default="scope">
                                    <div class="performance-metrics">
                                        <div
                                            v-for="(metric, _idx) in formatPerformanceMetrics(scope.row.performance_metrics)"
                                            :key="metric.key"
                                        >
                                            <span class="metric-key">{{ metric.key }}:</span>
                                            <span class="metric-value">{{ metric.value }}</span>
                                        </div>
                                    </div>
                                </template>
                            </el-table-column>
                            <el-table-column label="操作" width="120">
                                <template #default="scope">
                                    <el-button size="small" @click="viewStrategyDetails(scope.row)">详情</el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>
                </el-card>
            </el-col>

            <!-- 右侧：市场数据和风险指标 -->
            <el-col :xs="24" :lg="8">
                <!-- 市场数据快照 -->
                <el-card class="content-card market-snapshot" shadow="never">
                    <template #header>
                        <div class="card-header">
                            <el-icon class="card-icon"><TrendCharts /></el-icon>
                            <span>市场数据快照</span>
                            <el-tag type="info" size="small">
                                {{ marketData.timestamp ? formatTime(marketData.timestamp) : '无数据' }}
                            </el-tag>
                        </div>
                    </template>

                    <div class="market-data">
                        <div v-if="marketData.data && Object.keys(marketData.data).length > 0">
                            <div class="market-item" v-for="(data, symbol) in marketData.data" :key="symbol">
                                <div class="symbol">{{ symbol }}</div>
                                <div class="price">¥{{ formatNumber(data.price, 2) }}</div>
                                <div class="change" :class="data.change >= 0 ? 'positive' : 'negative'">
                                    {{ formatNumber(data.change, 2) }}
                                </div>
                                <div class="change-percent" :class="data.change_percent >= 0 ? 'positive' : 'negative'">
                                    {{ formatPercent(data.change_percent / 100) }}
                                </div>
                            </div>
                        </div>
                        <div v-else class="no-data">
                            <el-empty description="暂无市场数据"></el-empty>
                        </div>
                    </div>
                </el-card>

                <!-- 风险指标面板 -->
                <el-card class="content-card risk-panel" shadow="never">
                    <template #header>
                        <div class="card-header">
                            <el-icon class="card-icon"><Warning /></el-icon>
                            <span>风险监控</span>
                            <el-tag :type="riskData.risk_status === 'normal' ? 'success' : 'warning'" size="small">
                                {{ riskData.risk_status === 'normal' ? '正常' : '警告' }}
                            </el-tag>
                        </div>
                    </template>

                    <div class="risk-metrics">
                        <div class="risk-item">
                            <div class="risk-label">当前回撤</div>
                            <div
                                class="risk-value"
                                :class="riskData.current_drawdown > 0.05 ? 'high-risk' : 'normal-risk'"
                            >
                                {{ formatPercent(riskData.current_drawdown || 0) }}
                            </div>
                        </div>
                        <div class="risk-item">
                            <div class="risk-label">当日盈亏</div>
                            <div class="risk-value" :class="riskData.daily_pnl >= 0 ? 'profit' : 'loss'">
                                ¥{{ formatNumber(riskData.daily_pnl || 0, 2) }}
                            </div>
                        </div>
                        <div class="risk-item">
                            <div class="risk-label">活跃头寸</div>
                            <div class="risk-value">{{ riskData.active_positions || 0 }} 个</div>
                        </div>
                        <div class="risk-item">
                            <div class="risk-label">最后更新</div>
                            <div class="risk-value small">
                                {{ riskData.last_updated ? formatTime(riskData.last_updated) : '未知' }}
                            </div>
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <!-- 策略管理对话框 -->
        <el-dialog v-model="strategyDialogVisible" title="策略管理" width="800px">
            <div class="strategy-management">
                <el-tabs v-model="activeStrategyTab">
                    <el-tab-pane label="添加策略" name="add">
                        <el-form :model="newStrategy" label-width="120px">
                            <el-form-item label="策略类型">
                                <el-select v-model="newStrategy.type" placeholder="选择策略类型">
                                    <el-option label="SVM交易策略" value="SVMTradingStrategy"></el-option>
                                    <el-option label="决策树策略" value="DecisionTreeTradingStrategy"></el-option>
                                    <el-option label="朴素贝叶斯策略" value="NaiveBayesTradingStrategy"></el-option>
                                    <el-option label="LSTM策略" value="LSTMTradingStrategy"></el-option>
                                    <el-option label="Transformer策略" value="TransformerTradingStrategy"></el-option>
                                </el-select>
                            </el-form-item>
                            <el-form-item>
                                <el-button type="primary" @click="addStrategy" :loading="strategyLoading">
                                    添加策略
                                </el-button>
                            </el-form-item>
                        </el-form>
                    </el-tab-pane>
                    <el-tab-pane label="移除策略" name="remove">
                        <el-table :data="strategyPerformance" stripe>
                            <el-table-column prop="strategy_name" label="策略名称"></el-table-column>
                            <el-table-column label="操作" width="100">
                                <template #default="scope">
                                    <el-button
                                        size="small"
                                        type="danger"
                                        @click="removeStrategy(scope.row.strategy_name)"
                                    >
                                        移除
                                    </el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </el-tab-pane>
                </el-tabs>
            </div>
        </el-dialog>

        <!-- 风险报告对话框 -->
        <el-dialog v-model="riskDialogVisible" title="风险报告" width="600px">
            <div class="risk-report">
                <el-alert
                    title="风险状态"
                    :type="riskData.risk_status === 'normal' ? 'success' : 'warning'"
                    :description="`当前系统风险状态：${riskData.risk_status === 'normal' ? '正常' : '警告'}`"
                    show-icon
                ></el-alert>

                <div class="risk-details">
                    <h4>风险指标详情</h4>
                    <ul>
                        <li>当前回撤: {{ formatPercent(riskData.current_drawdown || 0) }}</li>
                        <li>当日盈亏: ¥{{ formatNumber(riskData.daily_pnl || 0, 2) }}</li>
                        <li>活跃头寸: {{ riskData.active_positions || 0 }} 个</li>
                    </ul>

                    <h4>建议措施</h4>
                    <ul>
                        <li v-if="riskData.current_drawdown > 0.05">建议减少头寸规模或暂停部分策略</li>
                        <li v-if="riskData.daily_pnl < -1000">建议检查策略表现并调整参数</li>
                        <li v-if="riskData.active_positions > 10">建议监控头寸集中度风险</li>
                        <li v-else>系统运行正常，继续监控</li>
                    </ul>
                </div>
            </div>
        </el-dialog>
    </div>
</template>

<script setup>
import { useTradingDashboard } from './composables/useTradingDashboard'

const { isRunning, controlLoading, refreshLoading, strategyLoading, tradingData, strategyPerformance, marketData, riskData, strategyDialogVisible, riskDialogVisible, activeStrategyTab, newStrategy, statusMetrics, tradingStatus, toggleTradingSession, _response, refreshData, loadTradingData, response, loadStrategyPerformance, response, loadMarketData, response, loadRiskData, response, openStrategyManager, openRiskReport, addStrategy, removeStrategy, viewStrategyDetails, formatNumber, formatPercent, formatTime, formatPerformanceMetrics, formatted, refreshTimer, startAutoRefresh, stopAutoRefresh } = useTradingDashboard()
</script>

<style scoped>
@import "./styles/TradingDashboard.css";
</style>
