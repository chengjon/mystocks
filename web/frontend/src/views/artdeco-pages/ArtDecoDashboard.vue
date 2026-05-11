<template>
    <section class="artdeco-dashboard">
        <!-- 戏剧性的页面头部 -->
        <ArtDecoHeader
            title="量化驾驶舱"
            subtitle="QUANTIX · 实时洞察 · 策略执行"
            :show-status="true"
            :status-text="marketStatus"
            :status-type="marketStatusType"
        />

        <div class="request-meta-bar" aria-live="polite">
            <span class="meta-label">DASHBOARD</span><span>DATA: {{ aggregateDataStatus }}</span>
            <span>REQ: {{ displayRequestId }}</span>
            <span>TIME: {{ displayProcessTime }}</span>
            <span>SYNC: {{ aggregateSyncStatus }}</span>
        </div>

        <div v-if="dashboardAlertItems.length > 0" class="dashboard-alerts" aria-live="polite">
            <div
                v-for="alert in dashboardAlertItems"
                :key="alert.id"
                class="dashboard-alert"
                :class="`dashboard-alert--${alert.severity}`"
            >
                <ArtDecoIcon name="alert-circle" />
                <span class="alert-label">{{ alert.label }}</span>
                <span class="alert-message">{{ alert.message }}</span>
                <span class="alert-action">{{ alert.action }}</span>
            </div>
        </div>

        <!-- 市场全景仪表盘 -->
        <DashboardMarketPanorama
            :market-data="marketData"
            :loading="loading"
            :error="error"
            :show-fund-flow-skeleton="showFundFlowSkeleton"
            :fund-flow-chart-option="fundFlowChartOption"
            :market-trend-option="marketTrendOption"
            :trend-state-message="trendStateMessage"
            :loading-trend-data="loadingTrendData"
            :market-sentiment="marketSentiment"
            :sentiment-color="sentimentColor"
            :to-number="toNumber"
        />

        <!-- Main Content Grid -->
        <!-- Technical Indicators Overview - Collapsible -->
        <div class="indicators-section">
            <ArtDecoCollapsible v-model="indicatorsExpanded" title="技术指标概览" @toggle="handleIndicatorsToggle">
                <p v-if="loading.indicators" class="integration-note">技术指标链路加载中...</p>
                <p v-else-if="indicatorStateMessage && indicatorList.length === 0" class="integration-note">{{ indicatorStateMessage }}</p>
                <section v-else class="charts-section">
                    <p v-if="indicatorStateMessage" class="integration-note">{{ indicatorStateMessage }}</p>
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
                <p v-if="loading.monitoring" class="integration-note">系统监控链路加载中...</p>
                <p v-else-if="monitoringStateMessage && systemHealth.length === 0" class="integration-note">{{ monitoringStateMessage }}</p>
                <section v-else class="charts-section">
                    <p v-if="monitoringStateMessage" class="integration-note">{{ monitoringStateMessage }}</p>
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
            <ArtDecoCard title="市场热度板块" :hoverable="false" class="heat-map-card">
                <section class="heatmap-section chart-fixed-height">
                    <template v-if="loading.industry">
                         <div class="skeleton-chart skeleton-center">
                             <ArtDecoSkeleton variant="rect" width="90%" height="90%" />
                         </div>
                    </template>
                    <div v-else-if="error.industry" class="chart-state-note">{{ error.industry }}</div>
                    <template v-else>
                        <ArtDecoChart
                            :option="heatmapOption"
                            :loading="loading.industry"
                            accessible-label="市场热度板块热力图"
                            height="100%"
                        />
                    </template>
                </section>
            </ArtDecoCard>

            <ArtDecoCard title="资金流向热力图" :hoverable="false" class="capital-heatmap-card">
                <section class="heatmap-section chart-fixed-height">
                    <div v-if="capitalFlowDegradedMessage" class="chart-state-note">{{ capitalFlowDegradedMessage }}</div>
                    <ArtDecoChart
                        :option="capitalFlowHeatmapOption"
                        :loading="showCapitalFlowSkeleton"
                        accessible-label="资金流向热力图"
                        height="100%"
                    />
                </section>
            </ArtDecoCard>

            <ArtDecoCard title="行业轮动雷达" :hoverable="false" class="sector-radar-card">
                <section class="heatmap-section chart-fixed-height">
                    <div v-if="error.industry && !loading.industry" class="chart-state-note">{{ error.industry }}</div>
                    <ArtDecoChart
                        v-else
                        :option="sectorRotationRadarOption"
                        :loading="loading.industry"
                        accessible-label="行业轮动雷达图"
                        height="100%"
                    />
                </section>
            </ArtDecoCard>

            <ArtDecoCard title="一键压力测试" hoverable class="stress-test-card priority-action-card">
                <div class="stress-test-actions">
                    <button
                        type="button"
                        class="stress-test-btn"
                        :disabled="isStressTestDisabled"
                        @click="runOneClickStressTest"
                    >
                        {{ isStressTestDisabled ? '行情链路未就绪' : '立即执行压力测试' }}
                    </button>
                    <span class="stress-test-time" v-if="stressTestResult?.timestamp">{{ stressTestResult.timestamp }}</span>
                </div>
                <p v-if="!stressTestResult" class="integration-note">
                    {{ isStressTestDisabled ? '等待市场与资金流向真实数据就绪后可执行压力测试。' : '压力测试待执行，点击后将基于当前页面已加载的行情数据做本地估算（非后端风险分析）。' }}
                </p>
                <p v-else class="integration-note stress-test-disclaimer">以下为基于当前页面数据的本地估算结果，不构成后端验证的风险分析。</p>
                <div class="stress-test-metrics" aria-live="polite">
                    <div class="stress-metric-item">
                        <span class="metric-label">预估最大回撤</span>
                        <span class="metric-value">{{ stressTestResult ? `${stressTestResult.drawdown}%` : '--' }}</span>
                    </div>
                    <div class="stress-metric-item">
                        <span class="metric-label">VaR(95%)</span>
                        <span class="metric-value">{{ stressTestResult ? `${stressTestResult.var95}%` : '--' }}</span>
                    </div>
                    <div class="stress-metric-item">
                        <span class="metric-label">集中度风险</span>
                        <span class="metric-value">{{ stressTestResult ? `${stressTestResult.concentrationRisk}%` : '--' }}</span>
                    </div>
                </div>
            </ArtDecoCard>

            <!-- 新增: 龙虎榜 -->
            <ArtDecoLongHuBang class="long-hu-bang-card" />

            <!-- 新增: 大宗交易 -->
            <ArtDecoBlockTrading class="block-trading-card" />

            <!-- Capital Flow Ranking -->
            <ArtDecoCard title="资金流向持续排名" :hoverable="false" class="capital-flow-card">
                <div class="flow-tabs" role="tablist" @keydown="handleFlowTabKeydown">
                    <button
                        v-for="(tab, _idx) in flowTabs"
                        :key="tab.key"
                        :id="'flow-tab-' + tab.key"
                        type="button"
                        role="tab"
                        class="flow-tab"
                        :class="{ active: activeFlowTab === tab.key }"
                        :aria-selected="activeFlowTab === tab.key"
                        :aria-controls="'flow-tabpanel'"
                        :tabindex="activeFlowTab === tab.key ? 0 : -1"
                        @click="activeFlowTab = tab.key"
                    >
                        {{ tab.label }}
                    </button>
                </div>
                <div id="flow-tabpanel" class="flow-list" role="tabpanel" :aria-labelledby="'flow-tab-' + activeFlowTab">
                    <p v-if="capitalFlowDegradedMessage" class="integration-note">{{ capitalFlowDegradedMessage }}</p>
                    <template v-if="showCapitalFlowSkeleton">
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
            <ArtDecoCard title="我的股票池表现" :hoverable="false" class="stock-pool-card">
                <div class="pool-tabs" role="tablist" @keydown="handlePoolTabKeydown">
                    <button
                        v-for="(tab, _idx) in poolTabs"
                        :key="tab.key"
                        :id="'pool-tab-' + tab.key"
                        type="button"
                        role="tab"
                        class="pool-tab"
                        :class="{ active: activePoolTab === tab.key }"
                        :aria-selected="activePoolTab === tab.key"
                        :aria-controls="'pool-tabpanel'"
                        :tabindex="activePoolTab === tab.key ? 0 : -1"
                        @click="activePoolTab = tab.key"
                    >
                        {{ tab.label }}
                    </button>
                </div>
                <div id="pool-tabpanel" role="tabpanel" :aria-labelledby="'pool-tab-' + activePoolTab">
                <p v-if="topStocks.length === 0" class="integration-note">{{ stockPoolNotice }}</p>
                <section v-else class="pool-section">
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
                </div>
            </ArtDecoCard>

            <!-- Quick Navigation -->
            <ArtDecoCard title="快速导航" :hoverable="false" class="quick-nav-card">
                <nav class="nav-section">
                    <router-link to="/market" class="nav-item">
                        <ArtDecoIcon name="Market" size="xl" class="nav-icon" />
                        <div class="nav-label">市场行情</div>
                        <div class="nav-desc">实时报价与技术分析</div>
                    </router-link>
                    <router-link to="/watchlist" class="nav-item">
                        <ArtDecoIcon name="Watchlist" size="xl" class="nav-icon" />
                        <div class="nav-label">自选管理</div>
                        <div class="nav-desc">自选股与投资组合</div>
                    </router-link>
                    <router-link to="/data" class="nav-item">
                        <ArtDecoIcon name="Analysis" size="xl" class="nav-icon" />
                        <div class="nav-label">数据分析</div>
                        <div class="nav-desc">深度数据分析工具</div>
                    </router-link>
                    <router-link to="/trade" class="nav-item">
                        <ArtDecoIcon name="Briefcase" size="xl" class="nav-icon" />
                        <div class="nav-label">交易管理</div>
                        <div class="nav-desc">信号到订单的闭环</div>
                    </router-link>
                    <router-link to="/strategy" class="nav-item">
                        <ArtDecoIcon name="StrategyTrading" size="xl" class="nav-icon" />
                        <div class="nav-label">策略中心</div>
                        <div class="nav-desc">量化策略开发平台</div>
                    </router-link>
                    <router-link to="/risk" class="nav-item">
                        <ArtDecoIcon name="RiskManagement" size="xl" class="nav-icon" />
                        <div class="nav-label">风险监控</div>
                        <div class="nav-desc">实时风险评估系统</div>
                    </router-link>
                </nav>
            </ArtDecoCard>
        </div>
    </section>
</template>

<script setup>
    import ArtDecoSkeleton from '@/components/artdeco/core/ArtDecoSkeleton.vue'
    import ArtDecoChart from '@/components/artdeco/charts/ArtDecoChart.vue'
    import ArtDecoLongHuBang from '@/components/artdeco/specialized/ArtDecoLongHuBang.vue'
    import ArtDecoBlockTrading from '@/components/artdeco/specialized/ArtDecoBlockTrading.vue'
    import DashboardMarketPanorama from './components/DashboardMarketPanorama.vue'
import { useArtDecoDashboard } from './composables/useArtDecoDashboard'

const {
  fundFlowChartOption,
  marketTrendOption,
  heatmapOption,
  capitalFlowHeatmapOption,
  sectorRotationRadarOption,
  activeFlowTab,
  activePoolTab,
  refreshing,
  displayRequestId,
  displayProcessTime,
  indicatorList,
  systemHealth,
  loading,
  error,
  dashboardAlertItems,
  showFundFlowSkeleton,
  aggregateDataStatus,
  aggregateSyncStatus,
  marketData,
  capitalFlowData,
  showCapitalFlowSkeleton,
  capitalFlowDegradedMessage,
  trendStateMessage,
  indicatorStateMessage,
  monitoringStateMessage,
  loadingTrendData,
  flowTabs,
  poolTabs,
  topStocks,
  stockPoolNotice,
  indicatorsExpanded,
  monitoringExpanded,
  toNumber,
  marketSentiment,
  sentimentColor,
  marketStatus,
  marketStatusType,
  isStressTestDisabled,
  stressTestResult,
  handleIndicatorsToggle,
  handleMonitoringToggle,
  handleFlowTabKeydown,
  handlePoolTabKeydown,
  runOneClickStressTest,
} = useArtDecoDashboard()
</script>

<style scoped lang="scss">
@import './styles/ArtDecoDashboard';

.request-meta-bar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-4);
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
}

.integration-note {
  margin: 0;
  color: var(--artdeco-fg-muted);
  line-height: 1.6;
}

.dashboard-alerts {
  display: grid;
  gap: var(--artdeco-spacing-2);
  margin-bottom: var(--artdeco-spacing-4);
}

.stress-test-disclaimer {
  margin: 0 0 var(--artdeco-spacing-2) 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-xs);
  line-height: 1.4;
}

.dashboard-alert,
.chart-state-note {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
  border: 1px solid var(--artdeco-border-default);
  background: color-mix(in srgb, var(--artdeco-bg-card) 90%, transparent);
  color: var(--artdeco-fg-primary);
  font-size: var(--artdeco-text-sm);
}

.dashboard-alert--failed,
.chart-state-note {
  border-color: color-mix(in srgb, var(--artdeco-down) 32%, transparent);
  background: color-mix(in srgb, var(--artdeco-down) 8%, transparent);
}

.dashboard-alert--degraded {
  border-color: var(--artdeco-gold-opacity-30);
  background: var(--artdeco-gold-opacity-05);
}

.alert-label {
  color: var(--artdeco-gold-primary);
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  font-weight: 700;
  letter-spacing: var(--artdeco-tracking-wide);
}

.alert-message {
  font-weight: 600;
}

.alert-action {
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-xs);
}
</style>
