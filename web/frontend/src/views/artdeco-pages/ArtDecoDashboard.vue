<template>
    <div class="artdeco-dashboard">
        <!-- 戏剧性的页面头部 -->
        <ArtDecoHeader
            title="MyStocks 指挥中心"
            subtitle="量化交易的神经中枢 · 实时洞察 · 智能决策"
            :show-status="true"
            :status-text="marketStatus"
            :status-type="marketStatusType"
        >
            <template #actions>
                <div class="header-metrics">
                    <ArtDecoBadge variant="primary" pulse>
                        <ArtDecoIcon name="activity" />
                        {{ activeStrategies }} 策略运行中
                    </ArtDecoBadge>
                    <ArtDecoBadge variant="success" pulse>
                        <ArtDecoIcon name="trending-up" />
                        {{ todayPnL }}
                    </ArtDecoBadge>
                </div>

                <div class="time-refresh">
                    <div class="time-display">
                        <ArtDecoIcon name="clock" />
                        <span class="time-value">{{ currentTime }}</span>
                    </div>
                    <ArtDecoButton variant="outline" size="sm" @click="refreshData" :loading="refreshing">
                        <template #icon>
                            <ArtDecoIcon name="refresh" />
                        </template>
                        刷新数据
                    </ArtDecoButton>
                </div>
            </template>
        </ArtDecoHeader>

        <!-- 市场全景仪表盘 -->
        <div class="market-panorama">
            <!-- 主要市场指标 - 戏剧性布局 -->
            <ArtDecoCard class="market-indicators" variant="elevated" gradient>
                <template #header>
                    <div class="card-header">
                        <ArtDecoIcon name="bar-chart-3" />
                        <h3>主要市场指标</h3>
                    </div>
                </template>

                <div class="indicators-grid">
                    <ArtDecoStatCard
                        label="上证指数"
                        :value="marketData.shanghai.index"
                        :change="marketData.shanghai.change"
                        change-percent
                        variant="gold"
                        size="large"
                        glow
                    />
                    <ArtDecoStatCard
                        label="深证成指"
                        :value="marketData.shenzhen.index"
                        :change="marketData.shenzhen.change"
                        change-percent
                        variant="gold"
                        size="large"
                        glow
                    />
                    <ArtDecoStatCard
                        label="创业板指"
                        :value="marketData.chuangye.index"
                        :change="marketData.chuangye.change"
                        change-percent
                        variant="gold"
                        size="large"
                        glow
                    />
                </div>
            </ArtDecoCard>

            <!-- 资金流向和市场情绪 -->
            <div class="market-sentiment-grid">
                <ArtDecoCard class="sentiment-card" variant="outlined">
                    <template #header>
                        <div class="card-header">
                            <ArtDecoIcon name="dollar-sign" />
                            <h4>资金流向</h4>
                        </div>
                    </template>

                    <div class="sentiment-metrics">
                        <ArtDecoStatCard
                            label="北向资金"
                            :value="marketData.northFund.amount"
                            :change="marketData.northFund.change"
                            change-percent
                            :variant="marketData.northFund.change > 0 ? 'rise' : 'fall'"
                        />

                        <div class="sentiment-indicator">
                            <div class="indicator-label">市场情绪</div>
                            <div class="indicator-bar">
                                <div
                                    class="indicator-fill"
                                    :style="{ width: marketSentiment + '%' }"
                                    :class="sentimentColor"
                                ></div>
                            </div>
                            <div class="indicator-value">{{ marketSentiment }}%</div>
                        </div>
                    </div>
                </ArtDecoCard>

                <ArtDecoCard class="market-status-card" variant="elevated">
                    <template #header>
                        <div class="card-header">
                            <ArtDecoIcon name="activity" />
                            <h4>市场状态</h4>
                        </div>
                    </template>

                    <ArtDecoStatCard
                        label="涨跌家数"
                        :value="`${marketData.stocks.up}↑/${marketData.stocks.down}↓`"
                    change="2.1"
                    change-percent
                    variant="gold"
                />
                <ArtDecoStatCard
                    label="成交金额"
                    :value="marketData.volume.amount"
                    change="15.8"
                    change-percent
                    variant="gold"
                />
            </div>
        </div>

        <!-- Main Content Grid -->
        <!-- Technical Indicators Overview - Collapsible -->
        <div class="indicators-section">
            <ArtDecoCollapsible v-model="indicatorsExpanded" title="技术指标概览" @toggle="handleIndicatorsToggle">
                <div class="indicators-grid">
                    <div class="indicator-item">
                        <div class="indicator-name">RSI</div>
                        <div class="indicator-value">67.8</div>
                        <div class="indicator-trend rise">↗ 多头</div>
                    </div>
                    <div class="indicator-item">
                        <div class="indicator-name">MACD</div>
                        <div class="indicator-value">+0.45</div>
                        <div class="indicator-trend rise">↗ 金叉</div>
                    </div>
                    <div class="indicator-item">
                        <div class="indicator-name">KDJ</div>
                        <div class="indicator-value">78.5</div>
                        <div class="indicator-trend neutral">→ 中性</div>
                    </div>
                    <div class="indicator-item">
                        <div class="indicator-name">威廉指标</div>
                        <div class="indicator-value">-23.4</div>
                        <div class="indicator-trend fall">↘ 超卖</div>
                    </div>
                    <div class="indicator-item">
                        <div class="indicator-name">布林带</div>
                        <div class="indicator-value">上轨</div>
                        <div class="indicator-trend rise">↗ 强势</div>
                    </div>
                    <div class="indicator-item">
                        <div class="indicator-name">均线系统</div>
                        <div class="indicator-value">多头排列</div>
                        <div class="indicator-trend rise">↗ 看好</div>
                    </div>
                </div>
            </ArtDecoCollapsible>
        </div>

        <!-- System Monitoring - Collapsible -->
        <div class="monitoring-section">
            <ArtDecoCollapsible v-model="monitoringExpanded" title="系统监控状态" @toggle="handleMonitoringToggle">
                <div class="monitoring-grid">
                    <div class="monitor-item">
                        <div class="monitor-label">API响应时间</div>
                        <div class="monitor-value">120ms</div>
                        <div class="monitor-status good">正常</div>
                    </div>
                    <div class="monitor-item">
                        <div class="monitor-label">数据更新延迟</div>
                        <div class="monitor-value">2.3s</div>
                        <div class="monitor-status warning">稍慢</div>
                    </div>
                    <div class="monitor-item">
                        <div class="monitor-label">信号生成成功率</div>
                        <div class="monitor-value">98.5%</div>
                        <div class="monitor-status good">优秀</div>
                    </div>
                    <div class="monitor-item">
                        <div class="monitor-label">系统CPU使用率</div>
                        <div class="monitor-value">45%</div>
                        <div class="monitor-status good">正常</div>
                    </div>
                    <div class="monitor-item">
                        <div class="monitor-label">内存使用率</div>
                        <div class="monitor-value">67%</div>
                        <div class="monitor-status warning">偏高</div>
                    </div>
                    <div class="monitor-item">
                        <div class="monitor-label">数据库连接数</div>
                        <div class="monitor-value">23/100</div>
                        <div class="monitor-status good">正常</div>
                    </div>
                </div>
            </ArtDecoCollapsible>
        </div>
        <div class="content-grid">
            <!-- Market Heat Map -->
            <ArtDecoCard title="市场热度板块" hoverable class="heat-map-card">
                <div class="heat-map">
                    <div class="heat-item" v-for="sector in marketHeat" :key="sector.name">
                        <div class="sector-name">{{ sector.name }}</div>
                        <div class="sector-change" :class="sector.change > 0 ? 'rise' : 'fall'">
                            {{ sector.change > 0 ? '+' : '' }}{{ sector.change }}%
                        </div>
                        <div class="heat-bar">
                            <div class="heat-fill" :style="{ width: Math.abs(sector.change) * 2 + '%' }"></div>
                        </div>
                    </div>
                </div>
            </ArtDecoCard>

            <!-- Capital Flow Ranking -->
            <ArtDecoCard title="资金流向持续排名" hoverable class="capital-flow-card">
                <div class="flow-tabs">
                    <button
                        v-for="tab in flowTabs"
                        :key="tab.key"
                        class="flow-tab"
                        :class="{ active: activeFlowTab === tab.key }"
                        @click="activeFlowTab = tab.key"
                    >
                        {{ tab.label }}
                    </button>
                </div>
                <div class="flow-list">
                    <div class="flow-item" v-for="item in capitalFlowData" :key="item.name">
                        <div class="item-info">
                            <div class="item-name">{{ item.name }}</div>
                            <div class="item-code">{{ item.code }}</div>
                        </div>
                        <div class="item-flow" :class="item.amount > 0 ? 'inflow' : 'outflow'">
                            {{ item.amount > 0 ? '+' : '' }}{{ item.amount }}亿
                        </div>
                        <div class="item-change" :class="item.change > 0 ? 'rise' : 'fall'">
                            {{ item.change > 0 ? '+' : '' }}{{ item.change }}%
                        </div>
                    </div>
                </div>
            </ArtDecoCard>

            <!-- Stock Pool Performance -->
            <ArtDecoCard title="我的股票池表现" hoverable class="stock-pool-card">
                <div class="pool-tabs">
                    <button
                        v-for="tab in poolTabs"
                        :key="tab.key"
                        class="pool-tab"
                        :class="{ active: activePoolTab === tab.key }"
                        @click="activePoolTab = tab.key"
                    >
                        {{ tab.label }}
                    </button>
                </div>
                <div class="pool-stats">
                    <div class="pool-stat">
                        <div class="stat-label">总收益率</div>
                        <div class="stat-value rise">+12.5%</div>
                    </div>
                    <div class="pool-stat">
                        <div class="stat-label">今日收益</div>
                        <div class="stat-value rise">+0.8%</div>
                    </div>
                    <div class="pool-stat">
                        <div class="stat-label">持仓股票</div>
                        <div class="stat-value">25只</div>
                    </div>
                    <div class="pool-stat">
                        <div class="stat-label">最大回撤</div>
                        <div class="stat-value fall">-3.2%</div>
                    </div>
                </div>
                <div class="pool-stocks">
                    <div class="stock-item" v-for="stock in topStocks" :key="stock.code">
                        <div class="stock-info">
                            <div class="stock-name">{{ stock.name }}</div>
                            <div class="stock-code">{{ stock.code }}</div>
                        </div>
                        <div class="stock-performance">
                            <div class="stock-price">¥{{ stock.price }}</div>
                            <div class="stock-change" :class="stock.change > 0 ? 'rise' : 'fall'">
                                {{ stock.change > 0 ? '+' : '' }}{{ stock.change }}%
                            </div>
                        </div>
                    </div>
                </div>
            </ArtDecoCard>

            <!-- Quick Navigation -->
            <ArtDecoCard title="快速导航" hoverable class="quick-nav-card">
                <div class="nav-grid">
                    <router-link to="/market" class="nav-item">
                        <div class="nav-icon">📈</div>
                        <div class="nav-label">市场行情</div>
                        <div class="nav-desc">实时报价与技术分析</div>
                    </router-link>
                    <router-link to="/stocks" class="nav-item">
                        <div class="nav-icon">📋</div>
                        <div class="nav-label">股票管理</div>
                        <div class="nav-desc">自选股与投资组合</div>
                    </router-link>
                    <router-link to="/analysis" class="nav-item">
                        <div class="nav-icon">🔍</div>
                        <div class="nav-label">投资分析</div>
                        <div class="nav-desc">深度数据分析工具</div>
                    </router-link>
                    <router-link to="/trade" class="nav-item">
                        <div class="nav-icon">💼</div>
                        <div class="nav-label">交易管理</div>
                        <div class="nav-desc">信号到订单的闭环</div>
                    </router-link>
                    <router-link to="/strategy" class="nav-item">
                        <div class="nav-icon">🎯</div>
                        <div class="nav-label">策略中心</div>
                        <div class="nav-desc">量化策略开发平台</div>
                    </router-link>
                    <router-link to="/risk" class="nav-item">
                        <div class="nav-icon">⚠️</div>
                        <div class="nav-label">风险监控</div>
                        <div class="nav-desc">实时风险评估系统</div>
                    </router-link>
                </div>
            </ArtDecoCard>
        </div>
    </div>
</template>

<script setup>
    import { ref, computed, onMounted, onUnmounted } from 'vue'
    import { ArtDecoStatCard, ArtDecoCard, ArtDecoButton, ArtDecoCollapsible, ArtDecoHeader, ArtDecoIcon, ArtDecoBadge } from '@/components/artdeco'

    // 响应式数据
    const currentTime = ref('')
    const activeFlowTab = ref('1day')
    const activePoolTab = ref('watchlist')
    const refreshing = ref(false)

    // 计算属性
    const marketStatus = computed(() => '活跃')
    const marketStatusType = computed(() => 'success')
    const activeStrategies = computed(() => 12)
    const todayPnL = computed(() => '+8,450.20')
    const marketSentiment = computed(() => 68)
    const sentimentColor = computed(() => marketSentiment.value > 70 ? 'positive' : marketSentiment.value > 30 ? 'neutral' : 'negative')

    // 可折叠面板状态（带localStorage持久化）
    const getSavedState = (key, defaultValue = true) => {
        try {
            const saved = localStorage.getItem(`dashboard-collapse-${key}`)
            return saved !== null ? saved === 'true' : defaultValue
        } catch {
            return defaultValue
        }
    }

    const saveState = (key, value) => {
        try {
            localStorage.setItem(`dashboard-collapse-${key}`, String(value))
        } catch (error) {
            console.warn('Failed to save collapse state:', error)
        }
    }

    // 技术指标面板展开状态（默认展开）
    const indicatorsExpanded = ref(getSavedState('indicators', true))

    // 系统监控面板展开状态（默认折叠以降低初始认知负荷）
    const monitoringExpanded = ref(getSavedState('monitoring', false))

    // 监听展开状态变化并持久化
    const handleIndicatorsToggle = expanded => {
        saveState('indicators', expanded)
    }

    const handleMonitoringToggle = expanded => {
        saveState('monitoring', expanded)
    }

    // 模拟市场数据
    const marketData = ref({
        shanghai: { index: 3128.45, change: 0.85 },
        shenzhen: { index: 10245.67, change: 1.23 },
        chuangye: { index: 2156.89, change: -0.45 },
        northFund: { amount: 58.8, change: 15.6 },
        stocks: { up: 2856, down: 1689 },
        volume: { amount: '8,956亿', change: 15.8 }
    })

    // 市场热度数据
    const marketHeat = ref([
        { name: '人工智能', change: 3.2 },
        { name: '新能源汽车', change: 2.8 },
        { name: '半导体', change: -1.5 },
        { name: '医疗器械', change: 1.9 },
        { name: '云计算', change: 4.1 },
        { name: '新能源', change: 2.3 }
    ])

    // 资金流向标签
    const flowTabs = [
        { key: '1day', label: '1日' },
        { key: '3day', label: '3日' },
        { key: '5day', label: '5日' },
        { key: '10day', label: '10日' }
    ]

    // 资金流向数据
    const capitalFlowData = ref([
        { name: '贵州茅台', code: '600519', amount: 12.5, change: 2.1 },
        { name: '宁德时代', code: '300750', amount: 8.9, change: 3.5 },
        { name: '中国石化', code: '600028', amount: -5.2, change: -1.8 },
        { name: '招商银行', code: '600036', amount: 6.7, change: 1.2 },
        { name: '万科A', code: '000002', amount: -3.1, change: -0.9 }
    ])

    // 股票池标签
    const poolTabs = [
        { key: 'watchlist', label: '自选股' },
        { key: 'strategy', label: '策略选股' },
        { key: 'industry', label: '行业选股' },
        { key: 'concept', label: '概念选股' }
    ]

    // 表现最好的股票
    const topStocks = ref([
        { name: '宁德时代', code: '300750', price: '245.60', change: 3.2 },
        { name: '贵州茅台', code: '600519', price: '1850.00', change: 2.1 },
        { name: '比亚迪', code: '002594', price: '198.50', change: 1.8 },
        { name: '招商银行', code: '600036', price: '38.45', change: 0.9 },
        { name: '万科A', code: '000002', price: '18.90', change: -0.5 }
    ])

    // 更新时间
    let timeInterval

    // 刷新数据
    const refreshData = async () => {
        refreshing.value = true
        try {
            // TODO: 实现数据刷新逻辑
            await new Promise(resolve => setTimeout(resolve, 2000))
            updateTime()
        } finally {
            refreshing.value = false
        }
    }

    const updateTime = () => {
        currentTime.value = new Date().toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        })
    }

    onMounted(() => {
        updateTime()
        timeInterval = setInterval(updateTime, 1000)
    })

    onUnmounted(() => {
        if (timeInterval) {
            clearInterval(timeInterval)
        }
    })
</script>

<style scoped lang="scss">
    .artdeco-dashboard {
        min-height: 100vh;
        padding: 2rem;
        max-width: 1800px;
        margin: 0 auto;
        position: relative;

        // 戏剧性背景
        &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background:
                radial-gradient(circle at 30% 20%, rgba(255, 215, 0, 0.04) 0%, transparent 40%),
                radial-gradient(circle at 70% 80%, rgba(255, 165, 0, 0.03) 0%, transparent 40%),
                linear-gradient(135deg, rgba(0, 0, 0, 0.02) 0%, transparent 100%);
            pointer-events: none;
            z-index: -1;
        }

        // 金色装饰线条
        &::after {
            content: '';
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 200px;
            height: 2px;
            background: linear-gradient(90deg, transparent, #ffd700, #ffa500, #ffd700, transparent);
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
        }
    }

    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--artdeco-spacing-8);
        padding-bottom: var(--artdeco-spacing-4);
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
    }

    .header-content {
        .page-title {
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-4xl);
            font-weight: 700;
            color: var(--artdeco-gold-primary);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wider);
            margin: 0 0 var(--artdeco-spacing-2) 0;
        }

        .page-subtitle {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-lg);
            color: var(--artdeco-fg-muted);
            margin: 0;
        }
    }

    .header-actions {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-4);

        .time-display {
            text-align: right;

            .time-label {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-muted);
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
                display: block;
            }

            .time-value {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-base);
                color: var(--artdeco-gold-primary);
                font-weight: 600;
            }
        }
    }

    .stats-section {
        margin-bottom: var(--artdeco-spacing-8);
    }

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: var(--artdeco-spacing-6);
    }

    .content-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--artdeco-spacing-6);
    }

    .heat-map-card,
    .capital-flow-card,
    .stock-pool-card,
    .quick-nav-card {
        height: fit-content;
    }

    // 市场热度板块
    .heat-map {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-3);
    }

    .heat-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: var(--artdeco-spacing-3);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);
        transition: all var(--artdeco-transition-base);

        &:hover {
            border-color: var(--artdeco-gold-primary);
            box-shadow: var(--artdeco-glow-subtle);
        }

        .sector-name {
            font-family: var(--artdeco-font-body);
            font-weight: 600;
            color: var(--artdeco-fg-primary);
            flex: 1;
        }

        .sector-change {
            font-family: var(--artdeco-font-mono);
            font-weight: 700;
            margin-right: var(--artdeco-spacing-3);
            min-width: 60px;
            text-align: right;

            &.rise {
                color: var(--artdeco-up);
            }

            &.fall {
                color: var(--artdeco-down);
            }
        }

        .heat-bar {
            width: 120px;
            height: 8px;
            background: var(--artdeco-bg-base);
            border-radius: var(--artdeco-radius-sm);
            overflow: hidden;

            .heat-fill {
                height: 100%;
                background: linear-gradient(90deg, var(--artdeco-up), var(--artdeco-gold-primary));
                border-radius: var(--artdeco-radius-sm);
                transition: width var(--artdeco-transition-base);
            }
        }
    }

    // 资金流向
    .flow-tabs {
        display: flex;
        gap: var(--artdeco-spacing-2);
        margin-bottom: var(--artdeco-spacing-4);
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
        padding-bottom: var(--artdeco-spacing-2);
    }

    .flow-tab {
        background: transparent;
        border: none;
        color: var(--artdeco-fg-muted);
        padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-sm);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
        cursor: pointer;
        transition: all var(--artdeco-transition-base);
        position: relative;

        &::after {
            content: '';
            position: absolute;
            bottom: -3px;
            left: 0;
            width: 100%;
            height: 2px;
            background: var(--artdeco-gold-primary);
            transform: scaleX(0);
            transition: transform var(--artdeco-transition-base);
        }

        &:hover {
            color: var(--artdeco-gold-primary);
        }

        &.active {
            color: var(--artdeco-gold-primary);

            &::after {
                transform: scaleX(1);
            }
        }
    }

    .flow-list {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-2);
    }

    .flow-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: var(--artdeco-spacing-3);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);
        transition: all var(--artdeco-transition-base);

        &:hover {
            border-color: var(--artdeco-gold-primary);
            box-shadow: var(--artdeco-glow-subtle);
        }

        .item-info {
            flex: 1;

            .item-name {
                font-family: var(--artdeco-font-body);
                font-weight: 600;
                color: var(--artdeco-fg-primary);
                margin-bottom: 2px;
            }

            .item-code {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-muted);
            }
        }

        .item-flow {
            font-family: var(--artdeco-font-mono);
            font-weight: 700;
            margin-right: var(--artdeco-spacing-4);
            min-width: 80px;
            text-align: right;

            &.inflow {
                color: var(--artdeco-up);
            }

            &.outflow {
                color: var(--artdeco-down);
            }
        }

        .item-change {
            font-family: var(--artdeco-font-mono);
            font-weight: 600;
            min-width: 60px;
            text-align: right;

            &.rise {
                color: var(--artdeco-up);
            }

            &.fall {
                color: var(--artdeco-down);
            }
        }
    }

    // 股票池表现
    .pool-tabs {
        display: flex;
        gap: var(--artdeco-spacing-2);
        margin-bottom: var(--artdeco-spacing-4);
    }

    .pool-tab {
        @extend .flow-tab;
    }

    .pool-stats {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: var(--artdeco-spacing-4);
        margin-bottom: var(--artdeco-spacing-6);
    }

    .pool-stat {
        text-align: center;
        padding: var(--artdeco-spacing-4);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);

        .stat-label {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            color: var(--artdeco-fg-muted);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
            margin-bottom: var(--artdeco-spacing-2);
        }

        .stat-value {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-xl);
            font-weight: 700;

            &.rise {
                color: var(--artdeco-up);
            }

            &.fall {
                color: var(--artdeco-down);
            }
        }
    }

    .pool-stocks {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-2);
    }

    .stock-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: var(--artdeco-spacing-3);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);
        transition: all var(--artdeco-transition-base);

        &:hover {
            border-color: var(--artdeco-gold-primary);
            box-shadow: var(--artdeco-glow-subtle);
        }

        .stock-info {
            .stock-name {
                font-family: var(--artdeco-font-body);
                font-weight: 600;
                color: var(--artdeco-fg-primary);
                margin-bottom: 2px;
            }

            .stock-code {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-muted);
            }
        }

        .stock-performance {
            text-align: right;

            .stock-price {
                font-family: var(--artdeco-font-mono);
                font-weight: 600;
                color: var(--artdeco-fg-primary);
                margin-bottom: 2px;
            }

            .stock-change {
                font-family: var(--artdeco-font-mono);
                font-weight: 700;
                font-size: var(--artdeco-text-sm);

                &.rise {
                    color: var(--artdeco-up);
                }

                &.fall {
                    color: var(--artdeco-down);
                }
            }
        }
    }

    // 快速导航
    .nav-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: var(--artdeco-spacing-4);
    }

    .nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: var(--artdeco-spacing-6);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);
        text-decoration: none;
        transition: all var(--artdeco-transition-base);
        text-align: center;

        &:hover {
            border-color: var(--artdeco-gold-primary);
            box-shadow: var(--artdeco-glow-subtle);
            transform: translateY(-2px);
        }

        .nav-icon {
            font-size: var(--artdeco-text-3xl);
            margin-bottom: var(--artdeco-spacing-3);
            display: block;
        }

        .nav-label {
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-lg);
            font-weight: 700;
            color: var(--artdeco-gold-primary);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
            margin-bottom: var(--artdeco-spacing-2);
        }

        .nav-desc {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            color: var(--artdeco-fg-muted);
            line-height: 1.4;
        }
    }

    // 响应式设计（桌面端优先）
    @media (max-width: 1200px) {
        .content-grid {
            grid-template-columns: 1fr;
        }

        .nav-grid {
            grid-template-columns: 1fr;
        }
    }

    // 技术指标概览
    .indicators-section {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .indicators-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    .indicator-item {
        padding: var(--artdeco-spacing-4);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);
        text-align: center;
        transition: all var(--artdeco-transition-base);

        &:hover {
            border-color: var(--artdeco-gold-primary);
            box-shadow: var(--artdeco-glow-subtle);
        }

        .indicator-name {
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-sm);
            font-weight: 600;
            color: var(--artdeco-gold-primary);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
            margin-bottom: var(--artdeco-spacing-2);
        }

        .indicator-value {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-lg);
            font-weight: 700;
            color: var(--artdeco-fg-primary);
            margin-bottom: var(--artdeco-spacing-1);
        }

        .indicator-trend {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);

            &.rise {
                color: var(--artdeco-up);
            }

            &.fall {
                color: var(--artdeco-down);
            }

            &.neutral {
                color: var(--artdeco-fg-muted);
            }
        }
    }

    // 系统监控
    .monitoring-section {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .monitoring-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    .monitor-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--artdeco-spacing-4);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);
        transition: all var(--artdeco-transition-base);

        &:hover {
            border-color: var(--artdeco-gold-primary);
            box-shadow: var(--artdeco-glow-subtle);
        }

        .monitor-label {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            color: var(--artdeco-fg-muted);
            flex: 1;
        }

        .monitor-value {
            font-family: var(--artdeco-font-mono);
            font-weight: 600;
            color: var(--artdeco-fg-primary);
            margin-right: var(--artdeco-spacing-3);
        }

        .monitor-status {
            padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
            border-radius: var(--artdeco-radius-none);
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-xs);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);

            &.good {
                background: rgba(0, 230, 118, 0.1);
                color: var(--artdeco-up);
            }

            &.warning {
                background: rgba(212, 175, 55, 0.1);
                color: var(--artdeco-gold-primary);
            }
        }
    }
    // ============================================
    //   DESIGN NOTE - 设计说明
    //   本项目仅支持桌面端，不包含移动端响应式代码
    // 技术指标概览
    .indicators-section {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .indicators-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    .indicator-item {
        padding: var(--artdeco-spacing-4);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);
        text-align: center;
        transition: all var(--artdeco-transition-base);

        &:hover {
            border-color: var(--artdeco-gold-primary);
            box-shadow: var(--artdeco-glow-subtle);
        }

        .indicator-name {
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-sm);
            font-weight: 600;
            color: var(--artdeco-gold-primary);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
            margin-bottom: var(--artdeco-spacing-2);
        }

        .indicator-value {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-lg);
            font-weight: 700;
            color: var(--artdeco-fg-primary);
            margin-bottom: var(--artdeco-spacing-1);
        }

        .indicator-trend {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);

            &.rise {
                color: var(--artdeco-up);
            }

            &.fall {
                color: var(--artdeco-down);
            }

            &.neutral {
                color: var(--artdeco-fg-muted);
            }
        }
    }

    // 系统监控
    .monitoring-section {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .monitoring-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    .monitor-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--artdeco-spacing-4);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);
        transition: all var(--artdeco-transition-base);

        &:hover {
            border-color: var(--artdeco-gold-primary);
            box-shadow: var(--artdeco-glow-subtle);
        }

        .monitor-label {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            color: var(--artdeco-fg-muted);
            flex: 1;
        }

        .monitor-value {
            font-family: var(--artdeco-font-mono);
            font-weight: 600;
            color: var(--artdeco-fg-primary);
            margin-right: var(--artdeco-spacing-3);
        }

        .monitor-status {
            padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
            border-radius: var(--artdeco-radius-none);
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-xs);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);

            &.good {
                background: rgba(0, 230, 118, 0.1);
                color: var(--artdeco-up);
            }

            &.warning {
                background: rgba(212, 175, 55, 0.1);
                color: var(--artdeco-gold-primary);
            }
        }
    }
    // ============================================
</style>

// ============================================ // ADDITIONAL STYLES FOR NEW FEATURES //
============================================ // 技术指标概览 .indicators-section { margin-bottom:
var(--artdeco-spacing-6); } .indicators-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px,
1fr)); gap: var(--artdeco-spacing-4); } .indicator-item { padding: var(--artdeco-spacing-4); background:
var(--artdeco-bg-card); border: 1px solid rgba(212, 175, 55, 0.1); border-radius: var(--artdeco-radius-none);
text-align: center; transition: all var(--artdeco-transition-base); &:hover { border-color: var(--artdeco-gold-primary);
box-shadow: var(--artdeco-glow-subtle); } .indicator-name { font-family: var(--artdeco-font-display); font-size:
var(--artdeco-text-sm); font-weight: 600; color: var(--artdeco-gold-primary); text-transform: uppercase; letter-spacing:
var(--artdeco-tracking-wide); margin-bottom: var(--artdeco-spacing-2); } .indicator-value { font-family:
var(--artdeco-font-mono); font-size: var(--artdeco-text-lg); font-weight: 700; color: var(--artdeco-fg-primary);
margin-bottom: var(--artdeco-spacing-1); } .indicator-trend { font-family: var(--artdeco-font-body); font-size:
var(--artdeco-text-sm); font-weight: 600; text-transform: uppercase; letter-spacing: var(--artdeco-tracking-wide);
&.rise { color: var(--artdeco-up); } &.fall { color: var(--artdeco-down); } &.neutral { color: var(--artdeco-fg-muted);
} } } // 系统监控 .monitoring-section { margin-bottom: var(--artdeco-spacing-6); } .monitoring-grid { display: grid;
grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: var(--artdeco-spacing-4); } .monitor-item { display:
flex; justify-content: space-between; align-items: center; padding: var(--artdeco-spacing-4); background:
var(--artdeco-bg-card); border: 1px solid rgba(212, 175, 55, 0.1); border-radius: var(--artdeco-radius-none);
transition: all var(--artdeco-transition-base); &:hover { border-color: var(--artdeco-gold-primary); box-shadow:
var(--artdeco-glow-subtle); } .monitor-label { font-family: var(--artdeco-font-body); font-size: var(--artdeco-text-sm);
color: var(--artdeco-fg-muted); flex: 1; } .monitor-value { font-family: var(--artdeco-font-mono); font-weight: 600;
color: var(--artdeco-fg-primary); margin-right: var(--artdeco-spacing-3); } .monitor-status { padding:
var(--artdeco-spacing-1) var(--artdeco-spacing-2); border-radius: var(--artdeco-radius-none); font-family:
var(--artdeco-font-body); font-size: var(--artdeco-text-xs); font-weight: 600; text-transform: uppercase;
letter-spacing: var(--artdeco-tracking-wide); &.good { background: rgba(0, 230, 118, 0.1); color: var(--artdeco-up); }
&.warning { background: rgba(212, 175, 55, 0.1); color: var(--artdeco-gold-primary); } } }
