<template>
    <div class="artdeco-dashboard">
        <!-- 戏剧性的页面头部 -->
        <ArtDecoHeader
            title="QUANTIX"
            subtitle="实时 洞察 策略 执行"
            :show-status="true"
            :status-text="marketStatus"
            :status-type="marketStatusType"
        >
            <template #actions>
                <div class="header-metrics">
                    <ArtDecoSkeleton v-if="loading.strategies" variant="button" width="120px" />
                    <ArtDecoBadge v-else variant="primary" pulse>
                        <ArtDecoIcon name="activity" />
                        {{ activeStrategiesCount }} 策略运行中
                    </ArtDecoBadge>
                    
                    <ArtDecoSkeleton v-if="loading.pnl" variant="button" width="120px" />
                    <ArtDecoBadge v-else variant="success" pulse>
                        <ArtDecoIcon name="trending-up" />
                        {{ todayPnLValue }}
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

        <!-- 市场全景仪表盘 - 增强功能展示 -->
        <div class="market-panorama">
            <!-- 增强的市场资金流向概览 -->
            <div class="enhanced-fund-flow">
                <ArtDecoCard class="fund-flow-overview" variant="elevated" gradient>
                    <template #header>
                        <div class="card-header">
                            <ArtDecoIcon name="trending-up" />
                            <h3>市场资金流向概览</h3>
                        </div>
                    </template>

                    <section class="summary-section">
                        <template v-if="loading.fundFlow">
                             <div class="skeleton-stat" v-for="i in 4" :key="i">
                                 <ArtDecoSkeleton variant="text" width="60%" />
                                 <ArtDecoSkeleton variant="text" width="80%" height="24px" />
                             </div>
                        </template>
                        <template v-else>
                            <ArtDecoStatCard
                                label="沪股通净流入"
                                :value="marketData.fundFlow.hgt.amount + '亿'"
                                :change="toNumber(marketData.fundFlow.hgt.change)"
                                :change-percent="false"
                                :variant="toNumber(marketData.fundFlow.hgt.change) >= 0 ? 'rise' : 'fall'"
                                size="medium"
                                :description="'较昨日（亿元）'"
                            />
                            <ArtDecoStatCard
                                label="深股通净流入"
                                :value="marketData.fundFlow.sgt.amount + '亿'"
                                :change="toNumber(marketData.fundFlow.sgt.change)"
                                :change-percent="false"
                                :variant="toNumber(marketData.fundFlow.sgt.change) >= 0 ? 'rise' : 'fall'"
                                size="medium"
                                :description="'较昨日（亿元）'"
                            />
                            <ArtDecoStatCard
                                label="北向资金总额"
                                :value="marketData.fundFlow.northTotal.amount + '亿'"
                                :description="'本月累计 ' + marketData.fundFlow.northTotal.monthly + '亿'"
                                variant="gold"
                                size="medium"
                            />
                            <ArtDecoStatCard
                                label="主力净流入"
                                :value="marketData.fundFlow.mainForce.amount + '亿'"
                                :description="'占比 ' + marketData.fundFlow.mainForce.percentage + '%'"
                                variant="gold"
                                size="medium"
                            />
                        </template>
                    </section>
                    
                    <!-- Fund Flow Chart -->
                    <section class="chart-section" v-if="!loading.fundFlow">
                        <ArtDecoChart 
                            :option="fundFlowChartOption" 
                            :loading="loading.fundFlow" 
                            height="200px" 
                        />
                    </section>
                </ArtDecoCard>
            </div>

            <!-- 主要市场指标 - 戏剧性布局 -->
            <ArtDecoCard class="market-indicators" variant="elevated" gradient>
                <template #header>
                    <div class="card-header">
                        <ArtDecoIcon name="bar-chart-3" />
                        <h3>主要市场指标</h3>
                    </div>
                </template>

                <div v-if="loading.market" class="charts-section">
                    <div class="skeleton-chart" v-for="i in 3" :key="i">
                        <ArtDecoSkeleton variant="text" width="50%" />
                        <ArtDecoSkeleton variant="text" width="80%" height="32px" />
                        <ArtDecoSkeleton variant="text" width="40%" />
                    </div>
                </div>
                <div v-else-if="error.market" class="error-message">
                    <ArtDecoIcon name="alert-circle" />
                    <span>{{ error.market }}</span>
                </div>
                <section v-else class="charts-section">
                    <ArtDecoStatCard
                        label="上证指数"
                        :value="marketData.shanghai.index"
                        :change="toNumber(marketData.shanghai.change)"
                        change-percent
                        variant="gold"
                        size="large"
                        glow
                    />
                    <ArtDecoStatCard
                        label="深证成指"
                        :value="marketData.shenzhen.index"
                        :change="toNumber(marketData.shenzhen.change)"
                        change-percent
                        variant="gold"
                        size="large"
                        glow
                    />
                    <ArtDecoStatCard
                        label="创业板指"
                        :value="marketData.chuangye.index"
                        :change="toNumber(marketData.chuangye.change)"
                        change-percent
                        variant="gold"
                        size="large"
                        glow
                    />
                </section>

                <!-- Market Trend Chart -->
                <section class="chart-section" v-if="!loading.market">
                    <div class="trend-chart-title">上证指数分时趋势</div>
                    <ArtDecoChart 
                        :option="marketTrendOption" 
                        :loading="loading.market" 
                        height="200px" 
                    />
                </section>
            </ArtDecoCard>

            <!-- 资金流向和市场情绪 -->
            <section class="flow-section">
                <ArtDecoCard class="sentiment-card" variant="outlined">
                    <template #header>
                        <div class="card-header">
                            <ArtDecoIcon name="dollar-sign" />
                            <h4>资金流向</h4>
                        </div>
                    </template>

                    <div class="sentiment-metrics">
                        <template v-if="loading.fundFlow">
                             <ArtDecoSkeleton variant="rect" width="100%" height="80px" />
                        </template>
                        <template v-else>
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
                        </template>
                    </div>
                </ArtDecoCard>

                <ArtDecoCard class="market-status-card" variant="elevated">
                    <template #header>
                        <div class="card-header">
                            <ArtDecoIcon name="activity" />
                            <h4>市场状态</h4>
                        </div>
                    </template>
                    
                    <template v-if="loading.market">
                        <ArtDecoSkeleton variant="text" width="100%" height="40px" />
                        <ArtDecoSkeleton variant="text" width="100%" height="40px" style="margin-top: 10px;" />
                    </template>
                    <template v-else>
                        <ArtDecoStatCard
                            label="涨跌家数"
                            :value="`${marketData.stocks.up}↑/${marketData.stocks.down}↓`"
                            :change="2.1"
                            change-percent
                            variant="gold"
                        />
                        <ArtDecoStatCard
                            label="成交金额"
                            :value="marketData.volume.amount"
                            :change="15.8"
                            change-percent
                            variant="gold"
                        />
                    </template>
                </ArtDecoCard>
            </section>
        </div>

        <!-- Main Content Grid -->
        <!-- Technical Indicators Overview - Collapsible -->
        <div class="indicators-section">
            <ArtDecoCollapsible v-model="indicatorsExpanded" title="技术指标概览" @toggle="handleIndicatorsToggle">
                <section class="charts-section">
                    <div v-for="ind in indicatorList" :key="ind.name" class="indicator-item">
                        <div class="indicator-name">{{ ind.name }}</div>
                        <div class="indicator-value">{{ ind.value }}</div>
                        <div class="indicator-trend" :class="ind.trend">{{ ind.signal }}</div>
                    </div>
                </section>
            </ArtDecoCollapsible>
        </div>

        <!-- System Monitoring - Collapsible -->
        <div class="monitoring-section">
            <ArtDecoCollapsible v-model="monitoringExpanded" title="系统监控状态" @toggle="handleMonitoringToggle">
                <section class="charts-section">
                    <div v-for="m in systemHealth" :key="m.label" class="monitor-item">
                        <div class="monitor-label">{{ m.label }}</div>
                        <div class="monitor-value">{{ m.value }}</div>
                        <div class="monitor-status" :class="m.status">{{ m.status === 'good' ? '正常' : '警告' }}</div>
                    </div>
                </section>
            </ArtDecoCollapsible>
        </div>
        <div class="content-grid">
            <!-- Market Heat Map -->
            <ArtDecoCard title="市场热度板块" hoverable class="heat-map-card">
                <section class="heatmap-section" style="height: 300px;">
                    <template v-if="loading.industry">
                         <div class="skeleton-chart" style="height: 100%; display: flex; align-items: center; justify-content: center;">
                             <ArtDecoSkeleton variant="rect" width="90%" height="90%" />
                         </div>
                    </template>
                    <template v-else>
                        <ArtDecoChart 
                            :option="heatmapOption" 
                            :loading="loading.industry" 
                            height="100%" 
                        />
                    </template>
                </section>
            </ArtDecoCard>

            <!-- 新增: 龙虎榜 -->
            <ArtDecoLongHuBang class="long-hu-bang-card" />

            <!-- 新增: 大宗交易 -->
            <ArtDecoBlockTrading class="block-trading-card" />

            <!-- Capital Flow Ranking -->
            <ArtDecoCard title="资金流向持续排名" hoverable class="capital-flow-card">
                <div class="flow-tabs">
                    <button
                        v-for="(tab, _idx) in flowTabs"
                        :key="tab.key"
                        class="flow-tab"
                        :class="{ active: activeFlowTab === tab.key }"
                        @click="activeFlowTab = tab.key"
                    >
                        {{ tab.label }}
                    </button>
                </div>
                <div class="flow-list">
                    <template v-if="loading.fundFlow">
                        <div class="flow-item" v-for="i in 5" :key="i">
                            <ArtDecoSkeleton variant="text" width="100%" />
                        </div>
                    </template>
                    <template v-else>
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
                    </template>
                </div>
            </ArtDecoCard>

            <!-- Stock Pool Performance -->
            <ArtDecoCard title="我的股票池表现" hoverable class="stock-pool-card">
                <div class="pool-tabs">
                    <button
                        v-for="(tab, _idx) in poolTabs"
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
                <section class="pool-section">
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
                </section>
            </ArtDecoCard>

            <!-- Quick Navigation -->
            <ArtDecoCard title="快速导航" hoverable class="quick-nav-card">
                <nav class="nav-section">
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
                </nav>
            </ArtDecoCard>
        </div>
    </div>
</template>

<script setup>
    import ArtDecoSkeleton from '@/components/artdeco/core/ArtDecoSkeleton.vue'
    import ArtDecoChart from '@/components/artdeco/charts/ArtDecoChart.vue'
    import ArtDecoLongHuBang from '@/components/artdeco/specialized/ArtDecoLongHuBang.vue'
    import ArtDecoBlockTrading from '@/components/artdeco/specialized/ArtDecoBlockTrading.vue'
import { useArtDecoDashboard } from './composables/useArtDecoDashboard'

const {
  fundFlowChartOption,
  marketTrendOption,
  heatmapOption,
  currentTime,
  activeFlowTab,
  activePoolTab,
  refreshing,
  trendData,
  activeStrategiesCount,
  todayPnLValue,
  indicatorList,
  systemHealth,
  loading,
  error,
  marketData,
  marketHeat,
  capitalFlowData,
  flowTabs,
  poolTabs,
  topStocks,
  indicatorsExpanded,
  monitoringExpanded,
  toNumber,
  marketSentiment,
  sentimentColor,
  marketStatus,
  marketStatusType,
  handleIndicatorsToggle,
  handleMonitoringToggle,
  fetchMarketOverview,
  fetchFundFlow,
  fetchIndustryFlow,
  fetchStockFlowRanking,
  fetchTrendData,
  fetchSystemStats,
  refreshData,
  updateTime,
  handleTrendUpdate
} = useArtDecoDashboard()
</script>

<style scoped lang="scss">
@import './styles/ArtDecoDashboard';
</style>
