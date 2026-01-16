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
                                            v-for="metric in formatPerformanceMetrics(scope.row.performance_metrics)"
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
    import { ref, onMounted, onUnmounted } from 'vue'
    import {
        VideoPlay,
        VideoPause,
        RefreshRight,
        Setting,
        Warning,
        DataAnalysis,
        TrendCharts,
        ArrowUp,
        ArrowDown
    } from '@element-plus/icons-vue'
    import axios from 'axios'

    // 响应式数据
    const isRunning = ref(false)
    const controlLoading = ref(false)
    const refreshLoading = ref(false)
    const strategyLoading = ref(false)

    const tradingData = ref({})
    const strategyPerformance = ref([])
    const marketData = ref({})
    const riskData = ref({})

    const strategyDialogVisible = ref(false)
    const riskDialogVisible = ref(false)
    const activeStrategyTab = ref('add')

    const newStrategy = ref({
        type: ''
    })

    // 状态指标
    const statusMetrics = ref([
        {
            key: 'total_pnl',
            label: '总盈亏',
            value: '¥0.00',
            icon: 'TrendCharts',
            status: 'normal'
        },
        {
            key: 'active_positions',
            label: '活跃头寸',
            value: '0',
            icon: 'DataAnalysis',
            status: 'normal'
        },
        {
            key: 'win_rate',
            label: '胜率',
            value: '0.00%',
            icon: 'PieChart',
            status: 'normal'
        },
        {
            key: 'current_drawdown',
            label: '当前回撤',
            value: '0.00%',
            icon: 'Warning',
            status: 'normal'
        }
    ])

    // 计算属性
    const tradingStatus = computed(() => {
        if (!isRunning.value) {
            return { text: '已停止', type: 'info' }
        }

        if (tradingData.value.current_drawdown > 0.05) {
            return { text: '高风险', type: 'warning' }
        }

        return { text: '运行中', type: 'success' }
    })

    // 方法
    const toggleTradingSession = async () => {
        controlLoading.value = true
        try {
            if (isRunning.value) {
                // 停止交易会话
                const response = await axios.post('/api/trading/stop')
                ElMessage.success('交易会话已停止')
                isRunning.value = false
                await loadTradingData()
            } else {
                // 启动交易会话
                await axios.post('/api/trading/start')
                ElMessage.success('交易会话已启动')
                isRunning.value = true
                await loadTradingData()
            }
        } catch (error) {
            ElMessage.error(`操作失败: ${error.response?.data?.detail || error.message}`)
        } finally {
            controlLoading.value = false
        }
    }

    const refreshData = async () => {
        refreshLoading.value = true
        try {
            await Promise.all([loadTradingData(), loadStrategyPerformance(), loadMarketData(), loadRiskData()])
            ElMessage.success('数据已刷新')
        } catch (error) {
            ElMessage.error(`刷新失败: ${error.message}`)
        } finally {
            refreshLoading.value = false
        }
    }

    const loadTradingData = async () => {
        try {
            const response = await axios.get('/api/trading/status')
            tradingData.value = response.data

            // 更新状态指标
            statusMetrics.value[0].value = `¥${formatNumber(tradingData.value.total_pnl || 0, 2)}`
            statusMetrics.value[0].status = (tradingData.value.total_pnl || 0) >= 0 ? 'profit' : 'loss'

            statusMetrics.value[1].value = `${tradingData.value.active_positions || 0}`

            statusMetrics.value[3].value = `${formatPercent(tradingData.value.current_drawdown || 0)}`
            statusMetrics.value[3].status = (tradingData.value.current_drawdown || 0) > 0.05 ? 'warning' : 'normal'
        } catch (error) {
            console.error('Failed to load trading data:', error)
        }
    }

    const loadStrategyPerformance = async () => {
        try {
            const response = await axios.get('/api/trading/strategies/performance')
            strategyPerformance.value = response.data
        } catch (error) {
            console.error('Failed to load strategy performance:', error)
        }
    }

    const loadMarketData = async () => {
        try {
            const response = await axios.get('/api/trading/market/snapshot')
            marketData.value = response.data
        } catch (error) {
            console.error('Failed to load market data:', error)
        }
    }

    const loadRiskData = async () => {
        try {
            const response = await axios.get('/api/trading/risk/metrics')
            riskData.value = response.data
        } catch (error) {
            console.error('Failed to load risk data:', error)
        }
    }

    const openStrategyManager = () => {
        strategyDialogVisible.value = true
    }

    const openRiskReport = () => {
        riskDialogVisible.value = true
    }

    const addStrategy = async () => {
        if (!newStrategy.value.type) {
            ElMessage.warning('请选择策略类型')
            return
        }

        strategyLoading.value = true
        try {
            await axios.post('/api/trading/strategies/add', {
                strategy_name: newStrategy.value.type
            })
            ElMessage.success('策略添加成功')
            newStrategy.value.type = ''
            await loadStrategyPerformance()
        } catch (error) {
            ElMessage.error(`添加策略失败: ${error.response?.data?.detail || error.message}`)
        } finally {
            strategyLoading.value = false
        }
    }

    const removeStrategy = async strategyName => {
        try {
            await ElMessageBox.confirm(`确定要移除策略 "${strategyName}" 吗？`, '确认移除', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            })

            await axios.delete(`/api/trading/strategies/${strategyName}`)
            ElMessage.success('策略移除成功')
            await loadStrategyPerformance()
        } catch (error) {
            if (error !== 'cancel') {
                ElMessage.error(`移除策略失败: ${error.response?.data?.detail || error.message}`)
            }
        }
    }

    const viewStrategyDetails = strategy => {
        ElMessage.info(`查看策略详情: ${strategy.strategy_name}`)
        // 这里可以打开策略详情对话框
    }

    const formatNumber = (num, decimals = 2) => {
        return Number(num).toLocaleString('zh-CN', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        })
    }

    const formatPercent = (num, decimals = 2) => {
        return `${(num * 100).toFixed(decimals)}%`
    }

    const formatTime = timestamp => {
        return new Date(timestamp).toLocaleString('zh-CN')
    }

    const formatPerformanceMetrics = metrics => {
        if (!metrics) return []

        const formatted = []
        if (metrics.expected_return !== undefined) {
            formatted.push({
                key: '预期收益',
                value: formatPercent(metrics.expected_return)
            })
        }
        if (metrics.sharpe_ratio !== undefined) {
            formatted.push({
                key: '夏普比率',
                value: metrics.sharpe_ratio.toFixed(2)
            })
        }
        if (metrics.win_rate !== undefined) {
            formatted.push({
                key: '胜率',
                value: formatPercent(metrics.win_rate)
            })
        }

        return formatted
    }

    // 自动刷新定时器
    let refreshTimer = null

    const startAutoRefresh = () => {
        refreshTimer = setInterval(() => {
            if (isRunning.value) {
                loadTradingData()
                loadStrategyPerformance()
                loadMarketData()
                loadRiskData()
            }
        }, 30000) // 每30秒刷新一次
    }

    const stopAutoRefresh = () => {
        if (refreshTimer) {
            clearInterval(refreshTimer)
            refreshTimer = null
        }
    }

    // 生命周期
    onMounted(async () => {
        await refreshData()
        startAutoRefresh()
    })

    onUnmounted(() => {
        stopAutoRefresh()
    })
</script>

<style scoped>
    .trading-dashboard {
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }

    .page-header {
        text-align: center;
        margin-bottom: 30px;
        color: white;
    }

    .page-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }

    .page-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 15px;
        letter-spacing: 2px;
    }

    .page-decorative-line {
        width: 100px;
        height: 3px;
        background: linear-gradient(90deg, #ffd89b, #19547b);
        margin: 0 auto 20px;
        border-radius: 2px;
    }

    .subtitle {
        font-size: 1rem;
        opacity: 0.8;
    }

    .control-panel {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 30px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .control-buttons {
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .control-btn {
        width: 100%;
        height: 50px;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .control-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    }

    .btn-icon {
        margin-right: 8px;
    }

    .status-overview {
        margin-bottom: 30px;
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        display: flex;
        align-items: center;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
    }

    .metric-card.profit {
        border-color: #67c23a;
    }

    .metric-card.loss {
        border-color: #f56c6c;
    }

    .metric-card.warning {
        border-color: #e6a23c;
    }

    .metric-icon {
        margin-right: 15px;
        color: #409eff;
    }

    .metric-content {
        flex: 1;
    }

    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #303133;
        margin-bottom: 5px;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #909399;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .metric-change {
        font-size: 0.8rem;
        margin-top: 5px;
    }

    .metric-change.increase {
        color: #67c23a;
    }

    .metric-change.decrease {
        color: #f56c6c;
    }

    .main-content {
        margin-bottom: 30px;
    }

    .content-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        height: 100%;
    }

    .card-header {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .card-icon {
        color: #409eff;
    }

    .trading-details {
        margin-bottom: 30px;
    }

    .strategy-performance h4 {
        margin-bottom: 15px;
        color: #303133;
    }

    .performance-metrics {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }

    .performance-metrics > div {
        display: flex;
        align-items: center;
        gap: 5px;
    }

    .metric-key {
        font-weight: bold;
        color: #606266;
    }

    .metric-value {
        color: #409eff;
    }

    .market-snapshot {
        margin-bottom: 20px;
    }

    .market-data {
        max-height: 300px;
        overflow-y: auto;
    }

    .market-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #f0f0f0;
    }

    .market-item:last-child {
        border-bottom: none;
    }

    .symbol {
        font-weight: bold;
        color: #303133;
        min-width: 60px;
    }

    .price {
        font-weight: bold;
        color: #303133;
    }

    .change,
    .change-percent {
        min-width: 60px;
        text-align: right;
    }

    .change.positive,
    .change-percent.positive {
        color: #67c23a;
    }

    .change.negative,
    .change-percent.negative {
        color: #f56c6c;
    }

    .risk-panel {
        margin-bottom: 20px;
    }

    .risk-metrics {
        display: flex;
        flex-direction: column;
        gap: 15px;
    }

    .risk-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #f0f0f0;
    }

    .risk-item:last-child {
        border-bottom: none;
    }

    .risk-label {
        font-weight: 500;
        color: #606266;
    }

    .risk-value {
        font-weight: bold;
        text-align: right;
    }

    .risk-value.profit {
        color: #67c23a;
    }

    .risk-value.loss {
        color: #f56c6c;
    }

    .risk-value.high-risk {
        color: #f56c6c;
    }

    .risk-value.normal-risk {
        color: #67c23a;
    }

    .risk-value.small {
        font-size: 0.8rem;
        font-weight: normal;
        color: #909399;
    }

    .strategy-management {
        min-height: 300px;
    }

    .risk-report {
        max-height: 400px;
        overflow-y: auto;
    }

    .risk-details {
        margin-top: 20px;
    }

    .risk-details h4 {
        margin: 20px 0 10px 0;
        color: #303133;
    }

    .risk-details ul {
        padding-left: 20px;
    }

    .risk-details li {
        margin-bottom: 5px;
        color: #606266;
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .page-title {
            font-size: 2rem;
        }

        .control-buttons .el-col {
            margin-bottom: 10px;
        }

        .metric-card {
            padding: 15px;
        }

        .metric-value {
            font-size: 1.5rem;
        }
    }

    /* 滚动条样式 */
    .market-data::-webkit-scrollbar {
        width: 6px;
    }

    .market-data::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 3px;
    }

    .market-data::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 3px;
    }

    .market-data::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
    }
</style>
