<template>
    <div class="artdeco-market-quotes">
        <!-- Page Header -->
        <div class="page-header">
            <div class="header-content">
                <h1 class="page-title">市场行情中心</h1>
                <p class="page-subtitle">全方位实时行情监控与技术分析平台</p>
            </div>
            <div class="header-actions">
                <div class="time-display">
                    <span class="time-label">市场状态</span>
                    <span class="time-value">交易中</span>
                </div>
                <ArtDecoButton variant="outline" size="sm" @click="refreshData">刷新行情</ArtDecoButton>
            </div>
        </div>

        <!-- Quick Stats Bar -->
        <div class="quick-stats">
            <div class="stat-item">
                <div class="stat-label">上证指数</div>
                <div class="stat-value">3128.45</div>
                <div class="stat-change rise">+0.85%</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">深证成指</div>
                <div class="stat-value">10245.67</div>
                <div class="stat-change rise">+1.23%</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">创业板指</div>
                <div class="stat-value">2156.89</div>
                <div class="stat-change fall">-0.45%</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">北向资金</div>
                <div class="stat-value">58.8亿</div>
                <div class="stat-change rise">+15.6%</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">成交金额</div>
                <div class="stat-value">8956亿</div>
                <div class="stat-change rise">+15.8%</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">涨跌家数</div>
                <div class="stat-value">2856↑/1689↓</div>
                <div class="stat-change neutral">净涨</div>
            </div>
        </div>

        <!-- Main Tabs -->
        <nav class="main-tabs">
            <button
                v-for="tab in mainTabs"
                :key="tab.key"
                class="main-tab"
                :class="{ active: activeTab === tab.key }"
                @click="switchTab(tab.key)"
            >
                <span class="tab-icon">{{ tab.icon }}</span>
                <span class="tab-label">{{ tab.label }}</span>
            </button>
        </nav>

        <!-- Tab Content -->
        <div class="tab-content">
            <!-- 实时行情 -->
            <div v-if="activeTab === 'realtime'" class="tab-panel">
                <div class="realtime-controls">
                    <div class="market-selector">
                        <ArtDecoSelect v-model="selectedMarket" :options="marketOptions" placeholder="选择市场" />
                    </div>
                    <div class="sort-controls">
                        <button
                            v-for="sort in sortOptions"
                            :key="sort.key"
                            class="sort-btn"
                            :class="{ active: activeSort === sort.key }"
                            @click="activeSort = sort.key"
                        >
                            {{ sort.label }}
                        </button>
                    </div>
                </div>

                <ArtDecoCard title="实时行情列表" hoverable class="quotes-table-card">
                    <div class="quotes-table">
                        <div class="table-header">
                            <div class="col-code">代码</div>
                            <div class="col-name">名称</div>
                            <div class="col-price">最新价</div>
                            <div class="col-change">涨跌幅</div>
                            <div class="col-volume">成交量</div>
                            <div class="col-amount">成交额</div>
                            <div class="col-turnover">换手率</div>
                            <div class="col-pe">市盈率</div>
                        </div>
                        <div class="table-body">
                            <div
                                class="table-row"
                                v-for="stock in realtimeQuotes"
                                :key="stock.code"
                                :class="{ 'price-up': stock.change > 0, 'price-down': stock.change < 0 }"
                            >
                                <div class="col-code">{{ stock.code }}</div>
                                <div class="col-name">{{ stock.name }}</div>
                                <div class="col-price">{{ stock.price }}</div>
                                <div class="col-change">{{ stock.change > 0 ? '+' : '' }}{{ stock.change }}%</div>
                                <div class="col-volume">{{ stock.volume }}</div>
                                <div class="col-amount">{{ stock.amount }}</div>
                                <div class="col-turnover">{{ stock.turnover }}%</div>
                                <div class="col-pe">{{ stock.pe }}</div>
                            </div>
                        </div>
                    </div>
                </ArtDecoCard>

                <div class="realtime-grid">
                    <ArtDecoCard title="热门板块" hoverable class="hot-sectors-card">
                        <div class="sectors-list">
                            <div class="sector-item" v-for="sector in hotSectors" :key="sector.name">
                                <div class="sector-name">{{ sector.name }}</div>
                                <div class="sector-change" :class="sector.change >= 0 ? 'rise' : 'fall'">
                                    {{ sector.change >= 0 ? '+' : '' }}{{ sector.change }}%
                                </div>
                                <div class="sector-stocks">{{ sector.leadingStocks }}只领涨</div>
                            </div>
                        </div>
                    </ArtDecoCard>

                    <ArtDecoCard title="异动监控" hoverable class="abnormal-monitor-card">
                        <div class="abnormal-list">
                            <div class="abnormal-item" v-for="item in abnormalStocks" :key="item.code">
                                <div class="abnormal-type" :class="item.type">{{ item.typeText }}</div>
                                <div class="abnormal-stock">
                                    <div class="stock-name">{{ item.name }}</div>
                                    <div class="stock-code">{{ item.code }}</div>
                                </div>
                                <div class="abnormal-change" :class="item.change >= 0 ? 'rise' : 'fall'">
                                    {{ item.change >= 0 ? '+' : '' }}{{ item.change }}%
                                </div>
                            </div>
                        </div>
                    </ArtDecoCard>
                </div>
            </div>

            <!-- 技术分析 -->
            <div v-if="activeTab === 'technical'" class="tab-panel">
                <div class="technical-controls">
                    <div class="symbol-input">
                        <ArtDecoInput v-model="analysisSymbol" placeholder="输入股票代码，如: 600519" />
                    </div>
                    <div class="period-selector">
                        <ArtDecoSelect v-model="analysisPeriod" :options="periodOptions" placeholder="选择周期" />
                    </div>
                    <ArtDecoButton variant="solid" @click="analyzeStock">开始分析</ArtDecoButton>
                </div>

                <div class="analysis-grid">
                    <ArtDecoCard title="技术指标" hoverable class="indicators-card">
                        <div class="indicators-grid">
                            <div class="indicator-item">
                                <div class="indicator-name">RSI</div>
                                <div class="indicator-value">67.8</div>
                                <div class="indicator-signal">中性</div>
                            </div>
                            <div class="indicator-item">
                                <div class="indicator-name">MACD</div>
                                <div class="indicator-value">+0.45</div>
                                <div class="indicator-signal rise">买入</div>
                            </div>
                            <div class="indicator-item">
                                <div class="indicator-name">KDJ</div>
                                <div class="indicator-value">78.5</div>
                                <div class="indicator-signal">超买</div>
                            </div>
                            <div class="indicator-item">
                                <div class="indicator-name">布林带</div>
                                <div class="indicator-value">上轨</div>
                                <div class="indicator-signal">强势</div>
                            </div>
                            <div class="indicator-item">
                                <div class="indicator-name">威廉指标</div>
                                <div class="indicator-value">-23.4</div>
                                <div class="indicator-signal fall">卖出</div>
                            </div>
                            <div class="indicator-item">
                                <div class="indicator-name">均线系统</div>
                                <div class="indicator-value">多头排列</div>
                                <div class="indicator-signal rise">看好</div>
                            </div>
                        </div>
                    </ArtDecoCard>

                    <ArtDecoCard title="形态识别" hoverable class="patterns-card">
                        <div class="patterns-list">
                            <div class="pattern-item">
                                <div class="pattern-name">头肩顶形态</div>
                                <div class="pattern-confidence">置信度: 85%</div>
                                <div class="pattern-signal fall">看跌</div>
                            </div>
                            <div class="pattern-item">
                                <div class="pattern-name">上升三角形</div>
                                <div class="pattern-confidence">置信度: 72%</div>
                                <div class="pattern-signal rise">看涨</div>
                            </div>
                            <div class="pattern-item">
                                <div class="pattern-name">锤头线</div>
                                <div class="pattern-confidence">置信度: 68%</div>
                                <div class="pattern-signal rise">反弹</div>
                            </div>
                        </div>
                    </ArtDecoCard>

                    <ArtDecoCard title="支撑阻力" hoverable class="support-resistance-card">
                        <div class="levels-list">
                            <div class="level-item resistance">
                                <div class="level-label">阻力位</div>
                                <div class="level-value">¥195.80</div>
                                <div class="level-strength">强</div>
                            </div>
                            <div class="level-item resistance">
                                <div class="level-label">阻力位</div>
                                <div class="level-value">¥189.50</div>
                                <div class="level-strength">中</div>
                            </div>
                            <div class="level-item support">
                                <div class="level-label">支撑位</div>
                                <div class="level-value">¥178.20</div>
                                <div class="level-strength">强</div>
                            </div>
                            <div class="level-item support">
                                <div class="level-label">支撑位</div>
                                <div class="level-value">¥172.80</div>
                                <div class="level-strength">中</div>
                            </div>
                        </div>
                    </ArtDecoCard>
                </div>

                <ArtDecoCard title="技术分析建议" hoverable class="analysis-recommendation-card">
                    <div class="recommendation-content">
                        <div class="recommendation-score">
                            <div
                                class="score-circle"
                                :class="
                                    recommendationScore >= 70
                                        ? 'bullish'
                                        : recommendationScore <= 30
                                          ? 'bearish'
                                          : 'neutral'
                                "
                            >
                                <span class="score-value">{{ recommendationScore }}</span>
                                <span class="score-label">技术评分</span>
                            </div>
                        </div>
                        <div class="recommendation-text">
                            <h3>
                                {{
                                    recommendationScore >= 70
                                        ? '技术面偏乐观'
                                        : recommendationScore <= 30
                                          ? '技术面偏悲观'
                                          : '技术面中性'
                                }}
                            </h3>
                            <ul>
                                <li v-for="point in recommendationPoints" :key="point">
                                    {{ point }}
                                </li>
                            </ul>
                        </div>
                    </div>
                </ArtDecoCard>
            </div>

            <!-- TDX深度 -->
            <div v-if="activeTab === 'tdx'" class="tab-panel">
                <div class="tdx-controls">
                    <div class="symbol-input">
                        <ArtDecoInput v-model="tdxSymbol" placeholder="输入股票代码" />
                    </div>
                    <ArtDecoButton variant="solid" @click="loadTDXData">加载TDX数据</ArtDecoButton>
                </div>

                <div class="tdx-grid">
                    <ArtDecoCard title="十档报价 (Level 2)" hoverable class="order-book-card">
                        <div class="order-book-detailed">
                            <!-- 卖盘 (Ask) -->
                            <div class="order-side sell-side">
                                <div class="order-side-header">卖盘 (10档)</div>
                                <div class="order-side-body">
                                    <div class="order-row-header">
                                        <span class="order-price-header">价格</span>
                                        <span class="order-volume-header">委托量</span>
                                    </div>
                                    <div class="order-row sell-row" v-for="ask in detailedOrderBook.asks" :key="ask.price">
                                        <span class="order-price sell">{{ ask.price }}</span>
                                        <span class="order-volume">{{ ask.volume }}</span>
                                    </div>
                                </div>
                            </div>

                            <!-- 中间价格显示 -->
                            <div class="price-center">
                                <div class="latest-price">{{ detailedOrderBook.latestPrice }}</div>
                                <div class="price-change" :class="{ positive: detailedOrderBook.change > 0, negative: detailedOrderBook.change < 0 }">
                                    {{ detailedOrderBook.change > 0 ? '+' : '' }}{{ detailedOrderBook.change }}
                                    ({{ detailedOrderBook.changePercent }}%)
                                </div>
                            </div>

                            <!-- 买盘 (Bid) -->
                            <div class="order-side buy-side">
                                <div class="order-side-header">买盘 (10档)</div>
                                <div class="order-side-body">
                                    <div class="order-row-header">
                                        <span class="order-price-header">价格</span>
                                        <span class="order-volume-header">委托量</span>
                                    </div>
                                    <div class="order-row buy-row" v-for="bid in detailedOrderBook.bids" :key="bid.price">
                                        <span class="order-price buy">{{ bid.price }}</span>
                                        <span class="order-volume">{{ bid.volume }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </ArtDecoCard>

                    <ArtDecoCard title="成交明细" hoverable class="trade-ticks-card">
                        <div class="trade-ticks">
                            <div class="tick-header">
                                <span>时间</span>
                                <span>价格</span>
                                <span>成交量</span>
                                <span>性质</span>
                            </div>
                            <div class="tick-body">
                                <div class="tick-row" v-for="tick in tradeTicks" :key="tick.time">
                                    <div class="tick-time">{{ tick.time }}</div>
                                    <div class="tick-price" :class="tick.type">{{ tick.price }}</div>
                                    <div class="tick-volume">{{ tick.volume }}</div>
                                    <div class="tick-type" :class="tick.type">{{ tick.typeText }}</div>
                                </div>
                            </div>
                        </div>
                    </ArtDecoCard>

                    <ArtDecoCard title="技术指标" hoverable class="tdx-indicators-card">
                        <div class="tdx-indicators">
                            <div class="indicator-group">
                                <h4>KDJ指标</h4>
                                <div class="indicator-values">
                                    <div class="indicator-value">K: {{ kdjData.k }}</div>
                                    <div class="indicator-value">D: {{ kdjData.d }}</div>
                                    <div class="indicator-value">J: {{ kdjData.j }}</div>
                                </div>
                            </div>
                            <div class="indicator-group">
                                <h4>MACD指标</h4>
                                <div class="indicator-values">
                                    <div class="indicator-value">DIF: {{ macdData.dif }}</div>
                                    <div class="indicator-value">DEA: {{ macdData.dea }}</div>
                                    <div class="indicator-value">MACD: {{ macdData.macd }}</div>
                                </div>
                            </div>
                            <div class="indicator-group">
                                <h4>RSI指标</h4>
                                <div class="indicator-values">
                                    <div class="indicator-value">RSI1: {{ rsiData.rsi1 }}</div>
                                    <div class="indicator-value">RSI2: {{ rsiData.rsi2 }}</div>
                                    <div class="indicator-value">RSI3: {{ rsiData.rsi3 }}</div>
                                </div>
                            </div>
                        </div>
                    </ArtDecoCard>
                </div>
            </div>

            <!-- 自定义指标 -->
            <!-- 实时监控 -->
            <div v-if="activeTab === 'monitoring'" class="tab-panel">
                <div class="monitoring-controls">
                    <ArtDecoSelect v-model="monitoringPeriod" :options="periodOptions" placeholder="选择监控周期" />
                    <div class="alert-settings">
                        <label class="checkbox-label">
                            <input type="checkbox" v-model="enablePriceAlerts" />
                            价格异动告警
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" v-model="enableVolumeAlerts" />
                            成交量异常告警
                        </label>
                    </div>
                </div>

                <div class="monitoring-grid">
                    <ArtDecoCard title="行情异动监控" hoverable class="abnormal-card">
                        <div class="abnormal-list">
                            <div class="abnormal-item" v-for="item in marketAbnormals" :key="item.id">
                                <div class="abnormal-time">{{ item.time }}</div>
                                <div class="abnormal-info">
                                    <div class="abnormal-symbol">{{ item.symbol }} {{ item.name }}</div>
                                    <div class="abnormal-type">{{ item.type }}</div>
                                </div>
                                <div class="abnormal-change" :class="item.changeType">
                                    {{ item.change > 0 ? '+' : '' }}{{ item.change }}%
                                </div>
                                <div class="abnormal-volume">{{ item.volume }}</div>
                            </div>
                        </div>
                    </ArtDecoCard>

                    <ArtDecoCard title="监控指标概览" hoverable class="metrics-card">
                        <div class="metrics-grid">
                            <div class="metric-item">
                                <div class="metric-name">监控股票数</div>
                                <div class="metric-value">{{ monitoringMetrics.stockCount }}</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-name">今日异动</div>
                                <div class="metric-value">{{ monitoringMetrics.todayAlerts }}</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-name">活跃告警</div>
                                <div class="metric-value">{{ monitoringMetrics.activeAlerts }}</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-name">监控覆盖率</div>
                                <div class="metric-value">{{ monitoringMetrics.coverage }}%</div>
                            </div>
                        </div>
                    </ArtDecoCard>
                </div>

                <ArtDecoCard title="实时告警日志" hoverable class="alerts-card">
                    <div class="alerts-list">
                        <div class="alert-item" v-for="alert in recentAlerts" :key="alert.id">
                            <div class="alert-time">{{ alert.time }}</div>
                            <div class="alert-level" :class="alert.level">{{ alert.levelText }}</div>
                            <div class="alert-message">{{ alert.message }}</div>
                            <div class="alert-status" :class="alert.status">{{ alert.statusText }}</div>
                        </div>
                    </div>
                </ArtDecoCard>
            </div>
            <div v-if="activeTab === 'custom'" class="tab-panel">
                <!-- 实时监控 -->
                <div v-if="activeTab === 'monitoring'" class="tab-panel">
                    <div class="monitoring-controls">
                        <ArtDecoSelect v-model="monitoringPeriod" :options="periodOptions" placeholder="选择监控周期" />
                        <div class="alert-settings">
                            <label class="checkbox-label">
                                <input type="checkbox" v-model="enablePriceAlerts" />
                                价格异动告警
                            </label>
                            <label class="checkbox-label">
                                <input type="checkbox" v-model="enableVolumeAlerts" />
                                成交量异常告警
                            </label>
                        </div>
                    </div>

                    <div class="monitoring-grid">
                        <ArtDecoCard title="行情异动监控" hoverable class="abnormal-card">
                            <div class="abnormal-list">
                                <div class="abnormal-item" v-for="item in marketAbnormals" :key="item.id">
                                    <div class="abnormal-time">{{ item.time }}</div>
                                    <div class="abnormal-info">
                                        <div class="abnormal-symbol">{{ item.symbol }} {{ item.name }}</div>
                                        <div class="abnormal-type">{{ item.type }}</div>
                                    </div>
                                    <div class="abnormal-change" :class="item.changeType">
                                        {{ item.change > 0 ? '+' : '' }}{{ item.change }}%
                                    </div>
                                    <div class="abnormal-volume">{{ item.volume }}</div>
                                </div>
                            </div>
                        </ArtDecoCard>

                        <ArtDecoCard title="监控指标概览" hoverable class="metrics-card">
                            <div class="metrics-grid">
                                <div class="metric-item">
                                    <div class="metric-name">监控股票数</div>
                                    <div class="metric-value">{{ monitoringMetrics.stockCount }}</div>
                                </div>
                                <div class="metric-item">
                                    <div class="metric-name">今日异动</div>
                                    <div class="metric-value">{{ monitoringMetrics.todayAlerts }}</div>
                                </div>
                                <div class="metric-item">
                                    <div class="metric-name">活跃告警</div>
                                    <div class="metric-value">{{ monitoringMetrics.activeAlerts }}</div>
                                </div>
                                <div class="metric-item">
                                    <div class="metric-name">监控覆盖率</div>
                                    <div class="metric-value">{{ monitoringMetrics.coverage }}%</div>
                                </div>
                            </div>
                        </ArtDecoCard>
                    </div>

                    <ArtDecoCard title="实时告警日志" hoverable class="alerts-card">
                        <div class="alerts-list">
                            <div class="alert-item" v-for="alert in recentAlerts" :key="alert.id">
                                <div class="alert-time">{{ alert.time }}</div>
                                <div class="alert-level" :class="alert.level">{{ alert.levelText }}</div>
                                <div class="alert-message">{{ alert.message }}</div>
                                <div class="alert-status" :class="alert.status">{{ alert.statusText }}</div>
                            </div>
                        </div>
                    </ArtDecoCard>
                </div>
                <div class="custom-controls">
                    <!-- 实时监控 -->
                    <div v-if="activeTab === 'monitoring'" class="tab-panel">
                        <div class="monitoring-controls">
                            <ArtDecoSelect
                                v-model="monitoringPeriod"
                                :options="periodOptions"
                                placeholder="选择监控周期"
                            />
                            <div class="alert-settings">
                                <label class="checkbox-label">
                                    <input type="checkbox" v-model="enablePriceAlerts" />
                                    价格异动告警
                                </label>
                                <label class="checkbox-label">
                                    <input type="checkbox" v-model="enableVolumeAlerts" />
                                    成交量异常告警
                                </label>
                            </div>
                        </div>

                        <div class="monitoring-grid">
                            <ArtDecoCard title="行情异动监控" hoverable class="abnormal-card">
                                <div class="abnormal-list">
                                    <div class="abnormal-item" v-for="item in marketAbnormals" :key="item.id">
                                        <div class="abnormal-time">{{ item.time }}</div>
                                        <div class="abnormal-info">
                                            <div class="abnormal-symbol">{{ item.symbol }} {{ item.name }}</div>
                                            <div class="abnormal-type">{{ item.type }}</div>
                                        </div>
                                        <div class="abnormal-change" :class="item.changeType">
                                            {{ item.change > 0 ? '+' : '' }}{{ item.change }}%
                                        </div>
                                        <div class="abnormal-volume">{{ item.volume }}</div>
                                    </div>
                                </div>
                            </ArtDecoCard>

                            <ArtDecoCard title="监控指标概览" hoverable class="metrics-card">
                                <div class="metrics-grid">
                                    <div class="metric-item">
                                        <div class="metric-name">监控股票数</div>
                                        <div class="metric-value">{{ monitoringMetrics.stockCount }}</div>
                                    </div>
                                    <div class="metric-item">
                                        <div class="metric-name">今日异动</div>
                                        <div class="metric-value">{{ monitoringMetrics.todayAlerts }}</div>
                                    </div>
                                    <div class="metric-item">
                                        <div class="metric-name">活跃告警</div>
                                        <div class="metric-value">{{ monitoringMetrics.activeAlerts }}</div>
                                    </div>
                                    <div class="metric-item">
                                        <div class="metric-name">监控覆盖率</div>
                                        <div class="metric-value">{{ monitoringMetrics.coverage }}%</div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>

                        <ArtDecoCard title="实时告警日志" hoverable class="alerts-card">
                            <div class="alerts-list">
                                <div class="alert-item" v-for="alert in recentAlerts" :key="alert.id">
                                    <div class="alert-time">{{ alert.time }}</div>
                                    <div class="alert-level" :class="alert.level">{{ alert.levelText }}</div>
                                    <div class="alert-message">{{ alert.message }}</div>
                                    <div class="alert-status" :class="alert.status">{{ alert.statusText }}</div>
                                </div>
                            </div>
                        </ArtDecoCard>
                    </div>
                    <div class="indicator-builder">
                        <!-- 实时监控 -->
                        <div v-if="activeTab === 'monitoring'" class="tab-panel">
                            <div class="monitoring-controls">
                                <ArtDecoSelect
                                    v-model="monitoringPeriod"
                                    :options="periodOptions"
                                    placeholder="选择监控周期"
                                />
                                <div class="alert-settings">
                                    <label class="checkbox-label">
                                        <input type="checkbox" v-model="enablePriceAlerts" />
                                        价格异动告警
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" v-model="enableVolumeAlerts" />
                                        成交量异常告警
                                    </label>
                                </div>
                            </div>

                            <div class="monitoring-grid">
                                <ArtDecoCard title="行情异动监控" hoverable class="abnormal-card">
                                    <div class="abnormal-list">
                                        <div class="abnormal-item" v-for="item in marketAbnormals" :key="item.id">
                                            <div class="abnormal-time">{{ item.time }}</div>
                                            <div class="abnormal-info">
                                                <div class="abnormal-symbol">{{ item.symbol }} {{ item.name }}</div>
                                                <div class="abnormal-type">{{ item.type }}</div>
                                            </div>
                                            <div class="abnormal-change" :class="item.changeType">
                                                {{ item.change > 0 ? '+' : '' }}{{ item.change }}%
                                            </div>
                                            <div class="abnormal-volume">{{ item.volume }}</div>
                                        </div>
                                    </div>
                                </ArtDecoCard>

                                <ArtDecoCard title="监控指标概览" hoverable class="metrics-card">
                                    <div class="metrics-grid">
                                        <div class="metric-item">
                                            <div class="metric-name">监控股票数</div>
                                            <div class="metric-value">{{ monitoringMetrics.stockCount }}</div>
                                        </div>
                                        <div class="metric-item">
                                            <div class="metric-name">今日异动</div>
                                            <div class="metric-value">{{ monitoringMetrics.todayAlerts }}</div>
                                        </div>
                                        <div class="metric-item">
                                            <div class="metric-name">活跃告警</div>
                                            <div class="metric-value">{{ monitoringMetrics.activeAlerts }}</div>
                                        </div>
                                        <div class="metric-item">
                                            <div class="metric-name">监控覆盖率</div>
                                            <div class="metric-value">{{ monitoringMetrics.coverage }}%</div>
                                        </div>
                                    </div>
                                </ArtDecoCard>
                            </div>

                            <ArtDecoCard title="实时告警日志" hoverable class="alerts-card">
                                <div class="alerts-list">
                                    <div class="alert-item" v-for="alert in recentAlerts" :key="alert.id">
                                        <div class="alert-time">{{ alert.time }}</div>
                                        <div class="alert-level" :class="alert.level">{{ alert.levelText }}</div>
                                        <div class="alert-message">{{ alert.message }}</div>
                                        <div class="alert-status" :class="alert.status">{{ alert.statusText }}</div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        <h3>指标构建器</h3>
                        <!-- 实时监控 -->
                        <div v-if="activeTab === 'monitoring'" class="tab-panel">
                            <div class="monitoring-controls">
                                <ArtDecoSelect
                                    v-model="monitoringPeriod"
                                    :options="periodOptions"
                                    placeholder="选择监控周期"
                                />
                                <div class="alert-settings">
                                    <label class="checkbox-label">
                                        <input type="checkbox" v-model="enablePriceAlerts" />
                                        价格异动告警
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" v-model="enableVolumeAlerts" />
                                        成交量异常告警
                                    </label>
                                </div>
                            </div>

                            <div class="monitoring-grid">
                                <ArtDecoCard title="行情异动监控" hoverable class="abnormal-card">
                                    <div class="abnormal-list">
                                        <div class="abnormal-item" v-for="item in marketAbnormals" :key="item.id">
                                            <div class="abnormal-time">{{ item.time }}</div>
                                            <div class="abnormal-info">
                                                <div class="abnormal-symbol">{{ item.symbol }} {{ item.name }}</div>
                                                <div class="abnormal-type">{{ item.type }}</div>
                                            </div>
                                            <div class="abnormal-change" :class="item.changeType">
                                                {{ item.change > 0 ? '+' : '' }}{{ item.change }}%
                                            </div>
                                            <div class="abnormal-volume">{{ item.volume }}</div>
                                        </div>
                                    </div>
                                </ArtDecoCard>

                                <ArtDecoCard title="监控指标概览" hoverable class="metrics-card">
                                    <div class="metrics-grid">
                                        <div class="metric-item">
                                            <div class="metric-name">监控股票数</div>
                                            <div class="metric-value">{{ monitoringMetrics.stockCount }}</div>
                                        </div>
                                        <div class="metric-item">
                                            <div class="metric-name">今日异动</div>
                                            <div class="metric-value">{{ monitoringMetrics.todayAlerts }}</div>
                                        </div>
                                        <div class="metric-item">
                                            <div class="metric-name">活跃告警</div>
                                            <div class="metric-value">{{ monitoringMetrics.activeAlerts }}</div>
                                        </div>
                                        <div class="metric-item">
                                            <div class="metric-name">监控覆盖率</div>
                                            <div class="metric-value">{{ monitoringMetrics.coverage }}%</div>
                                        </div>
                                    </div>
                                </ArtDecoCard>
                            </div>

                            <ArtDecoCard title="实时告警日志" hoverable class="alerts-card">
                                <div class="alerts-list">
                                    <div class="alert-item" v-for="alert in recentAlerts" :key="alert.id">
                                        <div class="alert-time">{{ alert.time }}</div>
                                        <div class="alert-level" :class="alert.level">{{ alert.levelText }}</div>
                                        <div class="alert-message">{{ alert.message }}</div>
                                        <div class="alert-status" :class="alert.status">{{ alert.statusText }}</div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        <div class="builder-form">
                            <!-- 实时监控 -->
                            <div v-if="activeTab === 'monitoring'" class="tab-panel">
                                <div class="monitoring-controls">
                                    <ArtDecoSelect
                                        v-model="monitoringPeriod"
                                        :options="periodOptions"
                                        placeholder="选择监控周期"
                                    />
                                    <div class="alert-settings">
                                        <label class="checkbox-label">
                                            <input type="checkbox" v-model="enablePriceAlerts" />
                                            价格异动告警
                                        </label>
                                        <label class="checkbox-label">
                                            <input type="checkbox" v-model="enableVolumeAlerts" />
                                            成交量异常告警
                                        </label>
                                    </div>
                                </div>

                                <div class="monitoring-grid">
                                    <ArtDecoCard title="行情异动监控" hoverable class="abnormal-card">
                                        <div class="abnormal-list">
                                            <div class="abnormal-item" v-for="item in marketAbnormals" :key="item.id">
                                                <div class="abnormal-time">{{ item.time }}</div>
                                                <div class="abnormal-info">
                                                    <div class="abnormal-symbol">{{ item.symbol }} {{ item.name }}</div>
                                                    <div class="abnormal-type">{{ item.type }}</div>
                                                </div>
                                                <div class="abnormal-change" :class="item.changeType">
                                                    {{ item.change > 0 ? '+' : '' }}{{ item.change }}%
                                                </div>
                                                <div class="abnormal-volume">{{ item.volume }}</div>
                                            </div>
                                        </div>
                                    </ArtDecoCard>

                                    <ArtDecoCard title="监控指标概览" hoverable class="metrics-card">
                                        <div class="metrics-grid">
                                            <div class="metric-item">
                                                <div class="metric-name">监控股票数</div>
                                                <div class="metric-value">{{ monitoringMetrics.stockCount }}</div>
                                            </div>
                                            <div class="metric-item">
                                                <div class="metric-name">今日异动</div>
                                                <div class="metric-value">{{ monitoringMetrics.todayAlerts }}</div>
                                            </div>
                                            <div class="metric-item">
                                                <div class="metric-name">活跃告警</div>
                                                <div class="metric-value">{{ monitoringMetrics.activeAlerts }}</div>
                                            </div>
                                            <div class="metric-item">
                                                <div class="metric-name">监控覆盖率</div>
                                                <div class="metric-value">{{ monitoringMetrics.coverage }}%</div>
                                            </div>
                                        </div>
                                    </ArtDecoCard>
                                </div>

                                <ArtDecoCard title="实时告警日志" hoverable class="alerts-card">
                                    <div class="alerts-list">
                                        <div class="alert-item" v-for="alert in recentAlerts" :key="alert.id">
                                            <div class="alert-time">{{ alert.time }}</div>
                                            <div class="alert-level" :class="alert.level">{{ alert.levelText }}</div>
                                            <div class="alert-message">{{ alert.message }}</div>
                                            <div class="alert-status" :class="alert.status">{{ alert.statusText }}</div>
                                        </div>
                                    </div>
                                </ArtDecoCard>
                            </div>
                            <div class="form-row">
                                <!-- 实时监控 -->
                                <div v-if="activeTab === 'monitoring'" class="tab-panel">
                                    <div class="monitoring-controls">
                                        <ArtDecoSelect
                                            v-model="monitoringPeriod"
                                            :options="periodOptions"
                                            placeholder="选择监控周期"
                                        />
                                        <div class="alert-settings">
                                            <label class="checkbox-label">
                                                <input type="checkbox" v-model="enablePriceAlerts" />
                                                价格异动告警
                                            </label>
                                            <label class="checkbox-label">
                                                <input type="checkbox" v-model="enableVolumeAlerts" />
                                                成交量异常告警
                                            </label>
                                        </div>
                                    </div>

                                    <div class="monitoring-grid">
                                        <ArtDecoCard title="行情异动监控" hoverable class="abnormal-card">
                                            <div class="abnormal-list">
                                                <div
                                                    class="abnormal-item"
                                                    v-for="item in marketAbnormals"
                                                    :key="item.id"
                                                >
                                                    <div class="abnormal-time">{{ item.time }}</div>
                                                    <div class="abnormal-info">
                                                        <div class="abnormal-symbol">
                                                            {{ item.symbol }} {{ item.name }}
                                                        </div>
                                                        <div class="abnormal-type">{{ item.type }}</div>
                                                    </div>
                                                    <div class="abnormal-change" :class="item.changeType">
                                                        {{ item.change > 0 ? '+' : '' }}{{ item.change }}%
                                                    </div>
                                                    <div class="abnormal-volume">{{ item.volume }}</div>
                                                </div>
                                            </div>
                                        </ArtDecoCard>

                                        <ArtDecoCard title="监控指标概览" hoverable class="metrics-card">
                                            <div class="metrics-grid">
                                                <div class="metric-item">
                                                    <div class="metric-name">监控股票数</div>
                                                    <div class="metric-value">{{ monitoringMetrics.stockCount }}</div>
                                                </div>
                                                <div class="metric-item">
                                                    <div class="metric-name">今日异动</div>
                                                    <div class="metric-value">{{ monitoringMetrics.todayAlerts }}</div>
                                                </div>
                                                <div class="metric-item">
                                                    <div class="metric-name">活跃告警</div>
                                                    <div class="metric-value">{{ monitoringMetrics.activeAlerts }}</div>
                                                </div>
                                                <div class="metric-item">
                                                    <div class="metric-name">监控覆盖率</div>
                                                    <div class="metric-value">{{ monitoringMetrics.coverage }}%</div>
                                                </div>
                                            </div>
                                        </ArtDecoCard>
                                    </div>

                                    <ArtDecoCard title="实时告警日志" hoverable class="alerts-card">
                                        <div class="alerts-list">
                                            <div class="alert-item" v-for="alert in recentAlerts" :key="alert.id">
                                                <div class="alert-time">{{ alert.time }}</div>
                                                <div class="alert-level" :class="alert.level">
                                                    {{ alert.levelText }}
                                                </div>
                                                <div class="alert-message">{{ alert.message }}</div>
                                                <div class="alert-status" :class="alert.status">
                                                    {{ alert.statusText }}
                                                </div>
                                            </div>
                                        </div>
                                    </ArtDecoCard>
                                </div>
                                <label>指标名称</label>
                                <!-- 实时监控 -->
                                <div v-if="activeTab === 'monitoring'" class="tab-panel">
                                    <div class="monitoring-controls">
                                        <ArtDecoSelect
                                            v-model="monitoringPeriod"
                                            :options="periodOptions"
                                            placeholder="选择监控周期"
                                        />
                                        <div class="alert-settings">
                                            <label class="checkbox-label">
                                                <input type="checkbox" v-model="enablePriceAlerts" />
                                                价格异动告警
                                            </label>
                                            <label class="checkbox-label">
                                                <input type="checkbox" v-model="enableVolumeAlerts" />
                                                成交量异常告警
                                            </label>
                                        </div>
                                    </div>

                                    <div class="monitoring-grid">
                                        <ArtDecoCard title="行情异动监控" hoverable class="abnormal-card">
                                            <div class="abnormal-list">
                                                <div
                                                    class="abnormal-item"
                                                    v-for="item in marketAbnormals"
                                                    :key="item.id"
                                                >
                                                    <div class="abnormal-time">{{ item.time }}</div>
                                                    <div class="abnormal-info">
                                                        <div class="abnormal-symbol">
                                                            {{ item.symbol }} {{ item.name }}
                                                        </div>
                                                        <div class="abnormal-type">{{ item.type }}</div>
                                                    </div>
                                                    <div class="abnormal-change" :class="item.changeType">
                                                        {{ item.change > 0 ? '+' : '' }}{{ item.change }}%
                                                    </div>
                                                    <div class="abnormal-volume">{{ item.volume }}</div>
                                                </div>
                                            </div>
                                        </ArtDecoCard>

                                        <ArtDecoCard title="监控指标概览" hoverable class="metrics-card">
                                            <div class="metrics-grid">
                                                <div class="metric-item">
                                                    <div class="metric-name">监控股票数</div>
                                                    <div class="metric-value">{{ monitoringMetrics.stockCount }}</div>
                                                </div>
                                                <div class="metric-item">
                                                    <div class="metric-name">今日异动</div>
                                                    <div class="metric-value">{{ monitoringMetrics.todayAlerts }}</div>
                                                </div>
                                                <div class="metric-item">
                                                    <div class="metric-name">活跃告警</div>
                                                    <div class="metric-value">{{ monitoringMetrics.activeAlerts }}</div>
                                                </div>
                                                <div class="metric-item">
                                                    <div class="metric-name">监控覆盖率</div>
                                                    <div class="metric-value">{{ monitoringMetrics.coverage }}%</div>
                                                </div>
                                            </div>
                                        </ArtDecoCard>
                                    </div>

                                    <ArtDecoCard title="实时告警日志" hoverable class="alerts-card">
                                        <div class="alerts-list">
                                            <div class="alert-item" v-for="alert in recentAlerts" :key="alert.id">
                                                <div class="alert-time">{{ alert.time }}</div>
                                                <div class="alert-level" :class="alert.level">
                                                    {{ alert.levelText }}
                                                </div>
                                                <div class="alert-message">{{ alert.message }}</div>
                                                <div class="alert-status" :class="alert.status">
                                                    {{ alert.statusText }}
                                                </div>
                                            </div>
                                        </div>
                                    </ArtDecoCard>
                                </div>
                                <ArtDecoInput v-model="customIndicator.name" placeholder="自定义指标名称" />
                                <!-- 实时监控 -->
                                <div v-if="activeTab === 'monitoring'" class="tab-panel">
                                    <div class="monitoring-controls">
                                        <ArtDecoSelect
                                            v-model="monitoringPeriod"
                                            :options="periodOptions"
                                            placeholder="选择监控周期"
                                        />
                                        <div class="alert-settings">
                                            <label class="checkbox-label">
                                                <input type="checkbox" v-model="enablePriceAlerts" />
                                                价格异动告警
                                            </label>
                                            <label class="checkbox-label">
                                                <input type="checkbox" v-model="enableVolumeAlerts" />
                                                成交量异常告警
                                            </label>
                                        </div>
                                    </div>

                                    <div class="monitoring-grid">
                                        <ArtDecoCard title="行情异动监控" hoverable class="abnormal-card">
                                            <div class="abnormal-list">
                                                <div
                                                    class="abnormal-item"
                                                    v-for="item in marketAbnormals"
                                                    :key="item.id"
                                                >
                                                    <div class="abnormal-time">{{ item.time }}</div>
                                                    <div class="abnormal-info">
                                                        <div class="abnormal-symbol">
                                                            {{ item.symbol }} {{ item.name }}
                                                        </div>
                                                        <div class="abnormal-type">{{ item.type }}</div>
                                                    </div>
                                                    <div class="abnormal-change" :class="item.changeType">
                                                        {{ item.change > 0 ? '+' : '' }}{{ item.change }}%
                                                    </div>
                                                    <div class="abnormal-volume">{{ item.volume }}</div>
                                                </div>
                                            </div>
                                        </ArtDecoCard>

                                        <ArtDecoCard title="监控指标概览" hoverable class="metrics-card">
                                            <div class="metrics-grid">
                                                <div class="metric-item">
                                                    <div class="metric-name">监控股票数</div>
                                                    <div class="metric-value">{{ monitoringMetrics.stockCount }}</div>
                                                </div>
                                                <div class="metric-item">
                                                    <div class="metric-name">今日异动</div>
                                                    <div class="metric-value">{{ monitoringMetrics.todayAlerts }}</div>
                                                </div>
                                                <div class="metric-item">
                                                    <div class="metric-name">活跃告警</div>
                                                    <div class="metric-value">{{ monitoringMetrics.activeAlerts }}</div>
                                                </div>
                                                <div class="metric-item">
                                                    <div class="metric-name">监控覆盖率</div>
                                                    <div class="metric-value">{{ monitoringMetrics.coverage }}%</div>
                                                </div>
                                            </div>
                                        </ArtDecoCard>
                                    </div>

                                    <ArtDecoCard title="实时告警日志" hoverable class="alerts-card">
                                        <div class="alerts-list">
                                            <div class="alert-item" v-for="alert in recentAlerts" :key="alert.id">
                                                <div class="alert-time">{{ alert.time }}</div>
                                                <div class="alert-level" :class="alert.level">
                                                    {{ alert.levelText }}
                                                </div>
                                                <div class="alert-message">{{ alert.message }}</div>
                                                <div class="alert-status" :class="alert.status">
                                                    {{ alert.statusText }}
                                                </div>
                                            </div>
                                        </div>
                                    </ArtDecoCard>
                                </div>
                            </div>
                            <!-- 实时监控 -->
                            <div v-if="activeTab === 'monitoring'" class="tab-panel">
                                <div class="monitoring-controls">
                                    <ArtDecoSelect
                                        v-model="monitoringPeriod"
                                        :options="periodOptions"
                                        placeholder="选择监控周期"
                                    />
                                    <div class="alert-settings">
                                        <label class="checkbox-label">
                                            <input type="checkbox" v-model="enablePriceAlerts" />
                                            价格异动告警
                                        </label>
                                        <label class="checkbox-label">
                                            <input type="checkbox" v-model="enableVolumeAlerts" />
                                            成交量异常告警
                                        </label>
                                    </div>
                                </div>

                                <div class="monitoring-grid">
                                    <ArtDecoCard title="行情异动监控" hoverable class="abnormal-card">
                                        <div class="abnormal-list">
                                            <div class="abnormal-item" v-for="item in marketAbnormals" :key="item.id">
                                                <div class="abnormal-time">{{ item.time }}</div>
                                                <div class="abnormal-info">
                                                    <div class="abnormal-symbol">{{ item.symbol }} {{ item.name }}</div>
                                                    <div class="abnormal-type">{{ item.type }}</div>
                                                </div>
                                                <div class="abnormal-change" :class="item.changeType">
                                                    {{ item.change > 0 ? '+' : '' }}{{ item.change }}%
                                                </div>
                                                <div class="abnormal-volume">{{ item.volume }}</div>
                                            </div>
                                        </div>
                                    </ArtDecoCard>

                                    <ArtDecoCard title="监控指标概览" hoverable class="metrics-card">
                                        <div class="metrics-grid">
                                            <div class="metric-item">
                                                <div class="metric-name">监控股票数</div>
                                                <div class="metric-value">{{ monitoringMetrics.stockCount }}</div>
                                            </div>
                                            <div class="metric-item">
                                                <div class="metric-name">今日异动</div>
                                                <div class="metric-value">{{ monitoringMetrics.todayAlerts }}</div>
                                            </div>
                                            <div class="metric-item">
                                                <div class="metric-name">活跃告警</div>
                                                <div class="metric-value">{{ monitoringMetrics.activeAlerts }}</div>
                                            </div>
                                            <div class="metric-item">
                                                <div class="metric-name">监控覆盖率</div>
                                                <div class="metric-value">{{ monitoringMetrics.coverage }}%</div>
                                            </div>
                                        </div>
                                    </ArtDecoCard>
                                </div>

                                <ArtDecoCard title="实时告警日志" hoverable class="alerts-card">
                                    <div class="alerts-list">
                                        <div class="alert-item" v-for="alert in recentAlerts" :key="alert.id">
                                            <div class="alert-time">{{ alert.time }}</div>
                                            <div class="alert-level" :class="alert.level">{{ alert.levelText }}</div>
                                            <div class="alert-message">{{ alert.message }}</div>
                                            <div class="alert-status" :class="alert.status">{{ alert.statusText }}</div>
                                        </div>
                                    </div>
                                </ArtDecoCard>
                            </div>
                            <div class="form-row">
                                <label>计算公式</label>
                                <ArtDecoInput
                                    v-model="customIndicator.formula"
                                    placeholder="如: (CLOSE - OPEN) / OPEN * 100"
                                />
                            </div>
                            <div class="form-row">
                                <label>参数设置</label>
                                <div class="parameters">
                                    <ArtDecoInput v-model="customIndicator.param1" placeholder="参数1" />
                                    <ArtDecoInput v-model="customIndicator.param2" placeholder="参数2" />
                                </div>
                            </div>
                            <ArtDecoButton variant="solid">创建指标</ArtDecoButton>
                        </div>
                    </div>
                </div>

                <ArtDecoCard title="我的自定义指标" hoverable class="custom-indicators-card">
                    <div class="indicators-list">
                        <div class="indicator-item" v-for="indicator in customIndicators" :key="indicator.id">
                            // 实时监控 const monitoringPeriod = ref('realtime') const enablePriceAlerts = ref(true)
                            const enableVolumeAlerts = ref(true) const marketAbnormals = ref([ { id: 1, time:
                            '09:45:30', symbol: '600519', name: '贵州茅台', type: '涨停', change: 10.0, changeType:
                            'rise', volume: '123万手' }, { id: 2, time: '10:15:22', symbol: '000001', name: '平安银行',
                            type: '放量', change: -3.5, changeType: 'fall', volume: '456万手' }, { id: 3, time:
                            '11:30:45', symbol: '300750', name: '宁德时代', type: '异动', change: 8.2, changeType:
                            'rise', volume: '789万手' } ]) const monitoringMetrics = ref({ stockCount: 2456,
                            todayAlerts: 23, activeAlerts: 7, coverage: 94.5 }) const recentAlerts = ref([ { id: 1,
                            time: '09:45:30', level: 'warning', levelText: '警告', message: '贵州茅台成交量异常放大',
                            status: 'active', statusText: '活跃' }, { id: 2, time: '10:15:22', level: 'info', levelText:
                            '信息', message: '平安银行价格异动监控', status: 'acknowledged', statusText: '已确认' }, {
                            id: 3, time: '11:30:45', level: 'critical', levelText: '严重', message:
                            '宁德时代涨停板打开', status: 'resolved', statusText: '已解决' } ])
                            <div class="indicator-info">
                                <div class="indicator-name">{{ indicator.name }}</div>
                                <div class="indicator-formula">{{ indicator.formula }}</div>
                            </div>
                            <div class="indicator-actions">
                                <ArtDecoButton variant="outline" size="sm">编辑</ArtDecoButton>
                                <ArtDecoButton variant="outline" size="sm">删除</ArtDecoButton>
                            </div>
                        </div>
                    </div>
                </ArtDecoCard>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref } from 'vue'
    import { ArtDecoStatCard, ArtDecoCard, ArtDecoButton, ArtDecoInput, ArtDecoSelect } from '@/components/artdeco'

    // 响应式数据
    const activeTab = ref('realtime')
    const selectedMarket = ref('all')
    const activeSort = ref('change')
    const analysisSymbol = ref('600519')
    const analysisPeriod = ref('1d')
    const tdxSymbol = ref('600519')
    const recommendationScore = ref(68)
    const customIndicator = ref({
        name: '',
        formula: '',
        param1: '',
        param2: ''
    })

    // 主标签页
    const mainTabs = [
        { key: 'monitoring', label: '实时监控', icon: '📊' },
        { key: 'realtime', label: '实时行情', icon: '⚡' },
        { key: 'technical', label: '技术分析', icon: '📊' },
        { key: 'tdx', label: 'TDX深度', icon: '📡' },
        { key: 'custom', label: '自定义指标', icon: '🔧' }
    ]

    // 市场选项
    const marketOptions = [
        { label: '全部A股', value: 'all' },
        { label: '沪市主板', value: 'sh' },
        { label: '深市主板', value: 'sz' },
        { label: '创业板', value: 'cyb' },
        { label: '科创板', value: 'kcb' }
    ]

    // 排序选项
    const sortOptions = [
        { key: 'change', label: '涨跌幅' },
        { key: 'volume', label: '成交量' },
        { key: 'amount', label: '成交额' },
        { key: 'turnover', label: '换手率' }
    ]

    // 周期选项
    const periodOptions = [
        { label: '1分钟', value: '1m' },
        { label: '5分钟', value: '5m' },
        { label: '15分钟', value: '15m' },
        { label: '30分钟', value: '30m' },
        { label: '1小时', value: '1h' },
        { label: '日线', value: '1d' },
        { label: '周线', value: '1w' },
        { label: '月线', value: '1M' }
    ]

    // 实时行情数据
    const realtimeQuotes = ref([
        {
            code: '600519',
            name: '贵州茅台',
            price: '1850.00',
            change: 2.1,
            volume: '1234万',
            amount: '22.8亿',
            turnover: '0.85%',
            pe: '28.5'
        },
        {
            code: '000002',
            name: '万科A',
            price: '18.90',
            change: -0.5,
            volume: '987万',
            amount: '1.87亿',
            turnover: '1.23%',
            pe: '8.9'
        },
        {
            code: '000001',
            name: '平安银行',
            price: '12.45',
            change: 1.8,
            volume: '3456万',
            amount: '4.29亿',
            turnover: '2.15%',
            pe: '6.7'
        },
        {
            code: '600036',
            name: '招商银行',
            price: '38.45',
            change: 0.9,
            volume: '2345万',
            amount: '9.02亿',
            turnover: '1.67%',
            pe: '11.2'
        }
    ])

    // 热门板块
    const hotSectors = ref([
        { name: '新能源汽车', change: 3.2, leadingStocks: 15 },
        { name: '人工智能', change: 2.8, leadingStocks: 12 },
        { name: '半导体', change: -1.5, leadingStocks: 8 },
        { name: '医疗器械', change: 1.9, leadingStocks: 10 },
        { name: '云计算', change: 4.1, leadingStocks: 18 }
    ])

    // 异动股票
    const abnormalStocks = ref([
        { name: 'N迈为股份', code: '300751', change: 44.0, type: 'new', typeText: '新股' },
        { name: 'N爱德曼', code: '300751', change: 123.0, type: 'limit-up', typeText: '涨停' },
        { name: 'N科创板', code: '300751', change: 89.0, type: 'surge', typeText: '冲高' }
    ])

    // 五档报价 (兼容现有代码)
    const orderBook = ref([
        { sellVolume: '50万', price: '185.50', buyVolume: '', type: 'sell' },
        { sellVolume: '80万', price: '185.45', buyVolume: '', type: 'sell' },
        { sellVolume: '120万', price: '185.40', buyVolume: '', type: 'sell' },
        { sellVolume: '200万', price: '185.35', buyVolume: '', type: 'sell' },
        { sellVolume: '300万', price: '185.30', buyVolume: '', type: 'sell' },
        { sellVolume: '', price: '185.25', buyVolume: '', type: 'current' },
        { sellVolume: '', price: '185.20', buyVolume: '150万', type: 'buy' },
        { sellVolume: '', price: '185.15', buyVolume: '200万', type: 'buy' },
        { sellVolume: '', price: '185.10', buyVolume: '250万', type: 'buy' },
        { sellVolume: '', price: '185.05', buyVolume: '180万', type: 'buy' },
        { sellVolume: '', price: '185.00', buyVolume: '320万', type: 'buy' }
    ])

    // 详细Level 2数据 - 从HTML功能增强
    const detailedOrderBook = ref({
        latestPrice: '185.25',
        change: '+2.34',
        changePercent: '+1.28%',
        asks: [ // 卖盘
            { price: '185.60', volume: '3,245' },
            { price: '185.50', volume: '5,678' },
            { price: '185.40', volume: '2,345' },
            { price: '185.30', volume: '8,901' },
            { price: '185.20', volume: '4,567' },
            { price: '185.10', volume: '6,789' },
            { price: '185.00', volume: '3,456' },
            { price: '184.90', volume: '2,134' },
            { price: '184.80', volume: '7,890' },
            { price: '184.70', volume: '5,432' }
        ],
        bids: [ // 买盘
            { price: '185.20', volume: '4,567' },
            { price: '185.10', volume: '3,234' },
            { price: '185.00', volume: '6,789' },
            { price: '184.90', volume: '2,345' },
            { price: '184.80', volume: '5,678' },
            { price: '184.70', volume: '3,456' },
            { price: '184.60', volume: '7,890' },
            { price: '184.50', volume: '4,567' },
            { price: '184.40', volume: '2,134' },
            { price: '184.30', volume: '8,901' }
        ]
    })

    // 成交明细
    const tradeTicks = ref([
        { time: '09:45:30', price: '185.25', volume: '100', type: 'sell', typeText: '卖出' },
        { time: '09:45:28', price: '185.30', volume: '50', type: 'buy', typeText: '买入' },
        { time: '09:45:25', price: '185.20', volume: '200', type: 'sell', typeText: '卖出' },
        { time: '09:45:22', price: '185.35', volume: '80', type: 'buy', typeText: '买入' },
        { time: '09:45:20', price: '185.25', volume: '150', type: 'sell', typeText: '卖出' }
    ])

    // 技术指标数据
    const kdjData = ref({ k: '78.5', d: '72.3', j: '90.9' })
    const macdData = ref({ dif: '0.45', dea: '0.32', macd: '0.13' })
    const rsiData = ref({ rsi1: '67.8', rsi2: '62.4', rsi3: '58.9' })

    // 技术分析建议
    const recommendationPoints = ref([
        'RSI指标显示超卖区域，存在反弹机会',
        'MACD金叉形成，短期看涨信号',
        '布林带下轨支撑明显，建议关注突破',
        '均线系统多头排列，中长期趋势向上'
    ])

    // 自定义指标
    const customIndicators = ref([
        { id: 1, name: '自定义动量指标', formula: '(CLOSE - OPEN) / OPEN * 100' },
        { id: 2, name: '成交量比率', formula: 'VOLUME / MA(VOLUME, 5)' }
    ])

    // 实时监控
    const monitoringPeriod = ref('realtime')
    const enablePriceAlerts = ref(true)
    const enableVolumeAlerts = ref(true)

    const marketAbnormals = ref([
        {
            id: 1,
            time: '09:45:30',
            symbol: '600519',
            name: '贵州茅台',
            type: '涨停',
            change: 10.0,
            changeType: 'rise',
            volume: '123万手'
        },
        {
            id: 2,
            time: '10:15:22',
            symbol: '000001',
            name: '平安银行',
            type: '放量',
            change: -3.5,
            changeType: 'fall',
            volume: '456万手'
        },
        {
            id: 3,
            time: '11:30:45',
            symbol: '300750',
            name: '宁德时代',
            type: '异动',
            change: 8.2,
            changeType: 'rise',
            volume: '789万手'
        }
    ])

    const monitoringMetrics = ref({
        stockCount: 2456,
        todayAlerts: 23,
        activeAlerts: 7,
        coverage: 94.5
    })

    const recentAlerts = ref([
        {
            id: 1,
            time: '09:45:30',
            level: 'warning',
            levelText: '警告',
            message: '贵州茅台成交量异常放大',
            status: 'active',
            statusText: '活跃'
        },
        {
            id: 2,
            time: '10:15:22',
            level: 'info',
            levelText: '信息',
            message: '平安银行价格异动监控',
            status: 'acknowledged',
            statusText: '已确认'
        },
        {
            id: 3,
            time: '11:30:45',
            level: 'critical',
            levelText: '严重',
            message: '宁德时代涨停板打开',
            status: 'resolved',
            statusText: '已解决'
        }
    ])

    // 方法
    const switchTab = tabKey => {
        activeTab.value = tabKey
    }

    const refreshData = () => {
        // 刷新数据逻辑
        console.log('Refreshing market data...')
    }

    const analyzeStock = () => {
        // 技术分析逻辑
        console.log('Analyzing stock:', analysisSymbol.value)
    }

    const loadTDXData = () => {
        // 加载TDX数据逻辑
        console.log('Loading TDX data for:', tdxSymbol.value)
    }
</script>

<style scoped lang="scss">
    .artdeco-market-quotes {
        min-height: 100vh;
        padding: var(--artdeco-spacing-6);
        background: var(--artdeco-bg-global);
        color: var(--artdeco-fg-primary);
    }

    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--artdeco-spacing-6);
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

    // 快速统计栏
    .quick-stats {
        display: flex;
        gap: var(--artdeco-spacing-4);
        margin-bottom: var(--artdeco-spacing-6);
        overflow-x: auto;
        padding-bottom: var(--artdeco-spacing-2);
    }

    .stat-item {
        min-width: 160px;
        padding: var(--artdeco-spacing-4);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);
        text-align: center;

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
            color: var(--artdeco-fg-primary);
            margin-bottom: var(--artdeco-spacing-1);
        }

        .stat-change {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-sm);
            font-weight: 600;

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

    // 主标签页
    .main-tabs {
        display: flex;
        gap: var(--artdeco-spacing-2);
        margin-bottom: var(--artdeco-spacing-6);
        border-bottom: 2px solid rgba(212, 175, 55, 0.2);
        padding-bottom: var(--artdeco-spacing-2);
    }

    .main-tab {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-2);
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: var(--artdeco-radius-none);
        color: var(--artdeco-fg-primary);
        font-family: var(--artdeco-font-body);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
        cursor: pointer;
        transition: all var(--artdeco-transition-base);

        &:hover {
            border-color: var(--artdeco-gold-primary);
            box-shadow: var(--artdeco-glow-subtle);
        }

        &.active {
            background: linear-gradient(135deg, rgba(212, 175, 55, 0.1), rgba(212, 175, 55, 0.05));
            border-color: var(--artdeco-gold-primary);
            color: var(--artdeco-gold-primary);
            box-shadow: var(--artdeco-glow-medium);
        }

        .tab-icon {
            font-size: var(--artdeco-text-lg);
        }

        .tab-label {
            font-size: var(--artdeco-text-base);
        }
    }

    // 标签页内容
    .tab-content {
        .tab-panel {
            animation: fadeIn 0.5s ease-out;
        }
    }

    // 实时行情控制栏
    .realtime-controls {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--artdeco-spacing-6);
        gap: var(--artdeco-spacing-4);
    }

    .market-selector,
    .sort-controls {
        display: flex;
        gap: var(--artdeco-spacing-2);
    }

    .sort-btn {
        padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: var(--artdeco-radius-none);
        color: var(--artdeco-fg-primary);
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-sm);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
        cursor: pointer;
        transition: all var(--artdeco-transition-base);

        &:hover {
            border-color: var(--artdeco-gold-primary);
        }

        &.active {
            background: rgba(212, 175, 55, 0.1);
            border-color: var(--artdeco-gold-primary);
            color: var(--artdeco-gold-primary);
        }
    }

    // 行情表格
    .quotes-table {
        .table-header,
        .table-row {
            display: grid;
            grid-template-columns: 80px 2fr 1fr 1fr 1fr 1.5fr 1fr 1fr;
            gap: var(--artdeco-spacing-4);
            padding: var(--artdeco-spacing-3);
            align-items: center;
        }

        .table-header {
            background: rgba(212, 175, 55, 0.05);
            border-bottom: 1px solid rgba(212, 175, 55, 0.2);

            > div {
                font-family: var(--artdeco-font-display);
                font-size: var(--artdeco-text-sm);
                font-weight: 600;
                color: var(--artdeco-gold-primary);
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
                text-align: center;
            }
        }

        .table-row {
            border-bottom: 1px solid rgba(212, 175, 55, 0.1);
            transition: all var(--artdeco-transition-base);

            &:hover {
                background: rgba(212, 175, 55, 0.02);
            }

            &.price-up {
                border-left: 3px solid var(--artdeco-up);
            }

            &.price-down {
                border-left: 3px solid var(--artdeco-down);
            }

            .col-code {
                font-family: var(--artdeco-font-display);
                font-weight: 700;
                color: var(--artdeco-gold-primary);
                text-align: center;
            }

            .col-name {
                font-family: var(--artdeco-font-body);
                font-weight: 600;
                color: var(--artdeco-fg-primary);
            }

            .col-price {
                font-family: var(--artdeco-font-mono);
                font-weight: 600;
                color: var(--artdeco-fg-primary);
                text-align: right;
            }

            .col-change {
                font-family: var(--artdeco-font-mono);
                font-weight: 700;
                text-align: right;

                &.rise {
                    color: var(--artdeco-up);
                }

                &.fall {
                    color: var(--artdeco-down);
                }
            }

            .col-volume,
            .col-amount,
            .col-turnover,
            .col-pe {
                font-family: var(--artdeco-font-mono);
                color: var(--artdeco-fg-primary);
                text-align: right;
            }
        }
    }

    // 实时行情网格
    .realtime-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--artdeco-spacing-6);
        margin-top: var(--artdeco-spacing-6);
    }

    // 热门板块
    .sectors-list {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-3);
    }

    .sector-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
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
            margin-right: var(--artdeco-spacing-4);

            &.rise {
                color: var(--artdeco-up);
            }

            &.fall {
                color: var(--artdeco-down);
            }
        }

        .sector-stocks {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            color: var(--artdeco-fg-muted);
        }
    }

    // 异动监控
    .abnormal-list {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-2);
    }

    .abnormal-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--artdeco-spacing-3);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);
        transition: all var(--artdeco-transition-base);

        &:hover {
            border-color: var(--artdeco-gold-primary);
            box-shadow: var(--artdeco-glow-subtle);
        }

        .abnormal-type {
            padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
            border-radius: var(--artdeco-radius-none);
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-xs);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);

            &.new {
                background: rgba(212, 175, 55, 0.1);
                color: var(--artdeco-gold-primary);
            }

            &.limit-up {
                background: rgba(255, 82, 82, 0.1);
                color: var(--artdeco-up);
            }

            &.surge {
                background: rgba(0, 230, 118, 0.1);
                color: var(--artdeco-down);
            }
        }

        .abnormal-stock {
            flex: 1;
            margin-left: var(--artdeco-spacing-3);

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

        .abnormal-change {
            font-family: var(--artdeco-font-mono);
            font-weight: 700;

            &.rise {
                color: var(--artdeco-up);
            }

            &.fall {
                color: var(--artdeco-down);
            }
        }
    }

    // 技术分析控制栏
    .technical-controls {
        display: flex;
        gap: var(--artdeco-spacing-4);
        margin-bottom: var(--artdeco-spacing-6);
        align-items: flex-end;
    }

    // 技术分析网格
    .analysis-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: var(--artdeco-spacing-6);
        margin-bottom: var(--artdeco-spacing-6);
    }

    // 技术指标
    .indicators-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--artdeco-spacing-4);
    }

    .indicator-item {
        padding: var(--artdeco-spacing-4);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);
        text-align: center;

        .indicator-name {
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-base);
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

        .indicator-signal {
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
        }
    }

    // 形态识别
    .patterns-list {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-3);
    }

    .pattern-item {
        padding: var(--artdeco-spacing-4);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);

        .pattern-name {
            font-family: var(--artdeco-font-body);
            font-weight: 600;
            color: var(--artdeco-fg-primary);
            margin-bottom: var(--artdeco-spacing-2);
        }

        .pattern-confidence {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            color: var(--artdeco-fg-muted);
            margin-bottom: var(--artdeco-spacing-2);
        }

        .pattern-signal {
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
        }
    }

    // 支撑阻力位
    .levels-list {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-3);
    }

    .level-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--artdeco-spacing-3);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);

        &.resistance {
            border-left: 3px solid var(--artdeco-up);
        }

        &.support {
            border-left: 3px solid var(--artdeco-down);
        }

        .level-label {
            font-family: var(--artdeco-font-body);
            font-weight: 600;
            color: var(--artdeco-fg-primary);
        }

        .level-value {
            font-family: var(--artdeco-font-mono);
            font-weight: 700;
            color: var(--artdeco-fg-primary);
        }

        .level-strength {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            font-weight: 600;
            color: var(--artdeco-gold-primary);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
        }
    }

    // 技术分析建议
    .recommendation-content {
        display: flex;
        gap: var(--artdeco-spacing-6);
        align-items: flex-start;
    }

    .recommendation-score {
        flex-shrink: 0;
    }

    .score-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        border: 3px solid var(--artdeco-gold-primary);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        position: relative;

        &.bullish {
            background: rgba(255, 82, 82, 0.1);
            border-color: var(--artdeco-up);
        }

        &.bearish {
            background: rgba(0, 230, 118, 0.1);
            border-color: var(--artdeco-down);
        }

        &.neutral {
            background: rgba(212, 175, 55, 0.1);
            border-color: var(--artdeco-gold-primary);
        }

        .score-value {
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-3xl);
            font-weight: 700;
            color: var(--artdeco-fg-primary);
            line-height: 1;
        }

        .score-label {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            color: var(--artdeco-fg-muted);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
            margin-top: var(--artdeco-spacing-1);
        }
    }

    .recommendation-text {
        flex: 1;

        h3 {
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-xl);
            font-weight: 600;
            color: var(--artdeco-gold-primary);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
            margin: 0 0 var(--artdeco-spacing-4) 0;
        }

        ul {
            list-style: none;
            padding: 0;
            margin: 0;
            display: flex;
            flex-direction: column;
            gap: var(--artdeco-spacing-2);

            li {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-base);
                color: var(--artdeco-fg-primary);
                padding-left: var(--artdeco-spacing-4);
                position: relative;

                &::before {
                    content: '◆';
                    position: absolute;
                    left: 0;
                    color: var(--artdeco-gold-primary);
                    font-size: var(--artdeco-text-sm);
                }
            }
        }
    }

    // TDX控制栏
    .tdx-controls {
        display: flex;
        gap: var(--artdeco-spacing-4);
        margin-bottom: var(--artdeco-spacing-6);
        align-items: flex-end;
    }

    // TDX网格
    .tdx-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: var(--artdeco-spacing-6);
    }

    // 五档报价
    .order-book {
        .order-book-header {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: var(--artdeco-spacing-4);
            padding: var(--artdeco-spacing-3);
            background: rgba(212, 175, 55, 0.05);
            border-bottom: 1px solid rgba(212, 175, 55, 0.2);
            text-align: center;
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-sm);
            font-weight: 600;
            color: var(--artdeco-gold-primary);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
        }

        .order-book-body {
            display: flex;
            flex-direction: column;
        }

        .order-row {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: var(--artdeco-spacing-4);
            padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
            border-bottom: 1px solid rgba(212, 175, 55, 0.1);
            align-items: center;
            text-align: center;

            &:last-child {
                border-bottom: none;
                background: rgba(212, 175, 55, 0.05);
                font-weight: 700;
            }

            .sell-volume,
            .buy-volume {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-muted);
            }

            .price {
                font-family: var(--artdeco-font-mono);
                font-weight: 600;

                &.sell {
                    color: var(--artdeco-down);
                }

                &.buy {
                    color: var(--artdeco-up);
                }

                &.current {
                    color: var(--artdeco-gold-primary);
                    font-size: var(--artdeco-text-base);
                }
            }
        }
    }

    // 详细Level 2报价 - 从HTML功能增强
    .order-book-detailed {
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        gap: var(--artdeco-spacing-4);
        align-items: stretch;

        .order-side {
            background: var(--artdeco-bg-card);
            border: 1px solid rgba(212, 175, 55, 0.1);
            border-radius: var(--artdeco-radius-none);

            &.sell-side {
                border-color: rgba(239, 68, 68, 0.3);
            }

            &.buy-side {
                border-color: rgba(34, 197, 148, 0.3);
            }

            .order-side-header {
                padding: var(--artdeco-spacing-3);
                background: rgba(212, 175, 55, 0.05);
                text-align: center;
                font-family: var(--artdeco-font-display);
                font-size: var(--artdeco-text-sm);
                font-weight: 600;
                color: var(--artdeco-gold-primary);
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
                border-bottom: 1px solid rgba(212, 175, 55, 0.2);
            }

            .order-side-body {
                max-height: 300px;
                overflow-y: auto;

                .order-row-header {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: var(--artdeco-spacing-2);
                    padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
                    background: rgba(212, 175, 55, 0.02);
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-text-xs);
                    font-weight: 600;
                    color: var(--artdeco-fg-muted);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    border-bottom: 1px solid rgba(212, 175, 55, 0.1);

                    .order-price-header,
                    .order-volume-header {
                        text-align: center;
                    }
                }

                .order-row {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: var(--artdeco-spacing-2);
                    padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
                    border-bottom: 1px solid rgba(212, 175, 55, 0.05);
                    font-family: var(--artdeco-font-mono);
                    font-size: var(--artdeco-text-sm);
                    align-items: center;

                    &:hover {
                        background: rgba(212, 175, 55, 0.02);
                    }

                    &.sell-row {
                        .order-price {
                            color: var(--artdeco-down);
                        }
                    }

                    &.buy-row {
                        .order-price {
                            color: var(--artdeco-up);
                        }
                    }

                    .order-price,
                    .order-volume {
                        text-align: center;
                        font-weight: 500;
                    }
                }
            }
        }

        .price-center {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: var(--artdeco-spacing-4);
            background: linear-gradient(135deg, var(--artdeco-bg-card), rgba(212, 175, 55, 0.02));
            border: 1px solid rgba(212, 175, 55, 0.2);
            border-radius: var(--artdeco-radius-none);
            min-width: 150px;

            .latest-price {
                font-family: var(--artdeco-font-display);
                font-size: var(--artdeco-text-2xl);
                font-weight: 700;
                color: var(--artdeco-gold-primary);
                text-shadow: 0 0 10px rgba(212, 175, 55, 0.3);
                margin-bottom: var(--artdeco-spacing-1);
            }

            .price-change {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-sm);
                font-weight: 600;

                &.positive {
                    color: var(--artdeco-up);
                }

                &.negative {
                    color: var(--artdeco-down);
                }
            }
        }
    }

    // 成交明细
    .trade-ticks {
        .tick-header {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr;
            gap: var(--artdeco-spacing-4);
            padding: var(--artdeco-spacing-3);
            background: rgba(212, 175, 55, 0.05);
            border-bottom: 1px solid rgba(212, 175, 55, 0.2);
            text-align: center;
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-sm);
            font-weight: 600;
            color: var(--artdeco-gold-primary);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
        }

        .tick-body {
            display: flex;
            flex-direction: column;
            max-height: 300px;
            overflow-y: auto;
        }

        .tick-row {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr;
            gap: var(--artdeco-spacing-4);
            padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
            border-bottom: 1px solid rgba(212, 175, 55, 0.1);
            align-items: center;
            text-align: center;

            .tick-time {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-muted);
            }

            .tick-price {
                font-family: var(--artdeco-font-mono);
                font-weight: 600;

                &.buy {
                    color: var(--artdeco-up);
                }

                &.sell {
                    color: var(--artdeco-down);
                }
            }

            .tick-volume {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-primary);
            }

            .tick-type {
                padding: 2px 8px;
                border-radius: var(--artdeco-radius-none);
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-xs);
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);

                &.buy {
                    background: rgba(255, 82, 82, 0.1);
                    color: var(--artdeco-up);
                }

                &.sell {
                    background: rgba(0, 230, 118, 0.1);
                    color: var(--artdeco-down);
                }
            }
        }
    }

    // TDX技术指标
    .tdx-indicators {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-4);
    }

    .indicator-group {
        h4 {
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-base);
            font-weight: 600;
            color: var(--artdeco-gold-primary);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
            margin: 0 0 var(--artdeco-spacing-3) 0;
        }

        .indicator-values {
            display: flex;
            flex-direction: column;
            gap: var(--artdeco-spacing-2);
        }

        .indicator-value {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-sm);
            color: var(--artdeco-fg-primary);
            padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
            background: var(--artdeco-bg-card);
            border: 1px solid rgba(212, 175, 55, 0.1);
            border-radius: var(--artdeco-radius-none);
        }
    }

    // 自定义指标控制栏
    .custom-controls {
        margin-bottom: var(--artdeco-spacing-6);
    }

    // 指标构建器
    .indicator-builder {
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);
        padding: var(--artdeco-spacing-6);

        h3 {
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-xl);
            font-weight: 600;
            color: var(--artdeco-gold-primary);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
            margin: 0 0 var(--artdeco-spacing-4) 0;
        }

        .builder-form {
            display: flex;
            flex-direction: column;
            gap: var(--artdeco-spacing-4);
        }

        .form-row {
            display: flex;
            flex-direction: column;
            gap: var(--artdeco-spacing-2);

            label {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-sm);
                font-weight: 600;
                color: var(--artdeco-gold-primary);
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
            }
        }

        .parameters {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: var(--artdeco-spacing-3);
        }
    }

    // 自定义指标列表
    .indicators-list {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-3);
    }

    .indicator-item {
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

        .indicator-info {
            flex: 1;

            .indicator-name {
                font-family: var(--artdeco-font-body);
                font-weight: 600;
                color: var(--artdeco-fg-primary);
                margin-bottom: var(--artdeco-spacing-1);
            }

            .indicator-formula {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-muted);
            }
        }

        .indicator-actions {
            display: flex;
            gap: var(--artdeco-spacing-2);
        }
    }

    // 响应式设计
    @media (max-width: 1400px) {
        .analysis-grid,
        .tdx-grid {
            grid-template-columns: 1fr 1fr;
        }

        .quotes-table {
            .table-header,
            .table-row {
                grid-template-columns: 80px 1.5fr 1fr 1fr 1fr 1fr 1fr 1fr;
                font-size: var(--artdeco-text-sm);
            }
        }
    }

    @media (max-width: 1024px) {
        .realtime-grid {
            grid-template-columns: 1fr;
        }

        .analysis-grid,
        .tdx-grid {
            grid-template-columns: 1fr;
        }

        .recommendation-content {
            flex-direction: column;
            align-items: center;
            text-align: center;
        }

        .score-circle {
            margin-bottom: var(--artdeco-spacing-4);
        }
    }

    @media (max-width: 768px) {
        .quick-stats {
            flex-wrap: wrap;
            justify-content: center;
        }

        .main-tabs {
            flex-wrap: wrap;
        }

        .realtime-controls {
            flex-direction: column;
            align-items: stretch;
            gap: var(--artdeco-spacing-3);
        }

        .technical-controls,
        .tdx-controls {
            flex-direction: column;
            align-items: stretch;
            gap: var(--artdeco-spacing-3);
        }

        .quotes-table {
            .table-header,
            .table-row {
                grid-template-columns: 70px 1fr 1fr 1fr;
                gap: var(--artdeco-spacing-2);
            }

            .table-row .col-name,
            .table-row .col-volume,
            .table-row .col-amount,
            .table-row .col-turnover,
            .table-row .col-pe {
                display: none;
            }
        }

        .parameters {
            grid-template-columns: 1fr;
        }
    }

    // 动画
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    // ============================================
    //   DESIGN NOTE - 设计说明
    //   本项目仅支持桌面端，不包含移动端响应式代码
    // ============================================
</style>
// 实时监控控制栏 .monitoring-controls { display: flex; gap: var(--artdeco-spacing-4); margin-bottom:
var(--artdeco-spacing-6); align-items: flex-end; } .alert-settings { display: flex; gap: var(--artdeco-spacing-4); }
.checkbox-label { display: flex; align-items: center; gap: var(--artdeco-spacing-2); font-family:
var(--artdeco-font-body); font-size: var(--artdeco-text-sm); color: var(--artdeco-fg-muted); cursor: pointer;
input[type="checkbox"] { width: 16px; height: 16px; accent-color: var(--artdeco-gold-primary); } } // 监控网格
.monitoring-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--artdeco-spacing-6); margin-bottom:
var(--artdeco-spacing-6); }; // 异动列表 .abnormal-list { display: flex; flex-direction: column gap:
var(--artdeco-spacing-2); } .abnormal-item { display: grid; grid-template-columns: 80px 1fr 80px 100px; gap:
var(--artdeco-spacing-3); padding: var(--artdeco-spacing-3); background: var(--artdeco-bg-card); border: 1px solid
rgba(212, 175, 55, 0.1); border-radius: var(--artdeco-radius-none); align-items: center; .abnormal-time { font-family:
var(--artdeco-font-mono); font-size: var(--artdeco-text-sm); color: var(--artdeco-fg-muted); } .abnormal-info {
.abnormal-symbol { font-family: var(--artdeco-font-body); font-weight: 600; color: var(--artdeco-fg-primary);
margin-bottom: 2px; } .abnormal-type { font-family: var(--artdeco-font-body); font-size: var(--artdeco-text-sm); color:
var(--artdeco-gold-primary); text-transform: uppercase; letter-spacing: var(--artdeco-tracking-wide); } }
.abnormal-change { font-family: var(--artdeco-font-mono); font-weight: 700; text-align: right; &.rise { color:
var(--artdeco-up); } &.fall { color: var(--artdeco-down); } } .abnormal-volume { font-family: var(--artdeco-font-mono);
font-size: var(--artdeco-text-sm); color: var(--artdeco-fg-primary); text-align: right; } } // 监控指标网格
.metrics-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--artdeco-spacing-4); } .metric-item {
padding: var(--artdeco-spacing-4); background: var(--artdeco-bg-card); border: 1px solid rgba(212, 175, 55, 0.1);
border-radius: var(--artdeco-radius-none); text-align: center; .metric-name { font-family: var(--artdeco-font-body);
font-size: var(--artdeco-text-sm); color: var(--artdeco-fg-muted); text-transform: uppercase; letter-spacing:
var(--artdeco-tracking-wide); margin-bottom: var(--artdeco-spacing-2); } .metric-value { font-family:
var(--artdeco-font-mono); font-size: var(--artdeco-text-xl); font-weight: 700; color: var(--artdeco-fg-primary); } } //
告警列表 .alerts-list { display: flex; flex-direction: column; gap: var(--artdeco-spacing-2); max-height: 400px;
overflow-y: auto; } .alert-item { display: grid; grid-template-columns: 120px 80px 1fr 100px; gap:
var(--artdeco-spacing-3); padding: var(--artdeco-spacing-3); background: var(--artdeco-bg-card); border: 1px solid
rgba(212, 175, 55, 0.1); border-radius: var(--artdeco-radius-none); align-items: center; .alert-time { font-family:
var(--artdeco-font-mono); font-size: var(--artdeco-text-sm); color: var(--artdeco-fg-muted); } .alert-level { padding:
var(--artdeco-spacing-1) var(--artdeco-spacing-2); border-radius: var(--artdeco-radius-none); font-family:
var(--artdeco-font-body); font-size: var(--artdeco-text-xs); font-weight: 600; text-transform: uppercase;
letter-spacing: var(--artdeco-tracking-wide); text-align: center; &.warning { background: rgba(212, 175, 55, 0.1);
color: var(--artdeco-gold-primary); } &.info { background: rgba(30, 61, 89, 0.1); color: #1E3D59; } &.critical {
background: rgba(231, 76, 60, 0.1); color: var(--artdeco-down); } } .alert-message { font-family:
var(--artdeco-font-body); font-size: var(--artdeco-text-sm); color: var(--artdeco-fg-primary); } .alert-status {
text-align: center; padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2); border-radius:
var(--artdeco-radius-none); font-family: var(--artdeco-font-body); font-size: var(--artdeco-text-xs); font-weight: 600;
text-transform: uppercase; letter-spacing: var(--artdeco-tracking-wide); &.active { background: rgba(255, 82, 82, 0.1);
color: var(--artdeco-up); } &.acknowledged { background: rgba(212, 175, 55, 0.1); color: var(--artdeco-gold-primary); }
&.resolved { background: rgba(0, 230, 118, 0.1); color: var(--artdeco-down); } } }
