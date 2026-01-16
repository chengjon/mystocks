<template>
    <div class="artdeco-stock-management">
        <!-- Page Header -->
        <div class="page-header">
            <div class="header-content">
                <h1 class="page-title">智能选股管理</h1>
                <p class="page-subtitle">自选股管理、策略选股、行业分析、批量操作</p>
            </div>
            <div class="header-actions">
                <div class="time-display">
                    <span class="time-label">最后更新</span>
                    <span class="time-value">{{ currentTime }}</span>
                </div>
                <ArtDecoButton variant="outline" size="sm" @click="refreshAllData">刷新数据</ArtDecoButton>
                <ArtDecoButton variant="solid" size="sm" @click="showAddStockDialog = true">添加股票</ArtDecoButton>
            </div>
        </div>

        <!-- Summary Stats -->
        <div class="stats-section">
            <div class="stats-grid">
                <ArtDecoStatCard label="自选股票" :value="watchlistStats.totalStocks" :change="0" variant="gold" />
                <ArtDecoStatCard
                    label="策略选股"
                    :value="strategyStats.totalSelected"
                    :change="strategyStats.changePercent"
                    change-percent
                    variant="gold"
                />
                <ArtDecoStatCard label="关注行业" :value="industryStats.totalIndustries" variant="gold" />
                <ArtDecoStatCard label="概念板块" :value="conceptStats.totalConcepts" variant="gold" />
                <ArtDecoStatCard
                    label="今日涨跌"
                    :value="portfolioStats.dailyChange"
                    :change="portfolioStats.changePercent"
                    change-percent
                    :variant="portfolioStats.changePercent >= 0 ? 'rise' : 'fall'"
                />
                <ArtDecoStatCard
                    label="持仓收益"
                    :value="portfolioStats.totalReturn"
                    :change="portfolioStats.returnPercent"
                    change-percent
                    :variant="portfolioStats.returnPercent >= 0 ? 'rise' : 'fall'"
                />
            </div>
        </div>

        <!-- Main Navigation Tabs -->
        <nav class="main-tabs">
            <button
                v-for="tab in mainTabs"
                :key="tab.key"
                class="main-tab"
                :class="{ active: activeMainTab === tab.key }"
                @click="switchMainTab(tab.key)"
            >
                <span class="tab-icon">{{ tab.icon }}</span>
                <span class="tab-label">{{ tab.label }}</span>
            </button>
        </nav>

        <!-- Tab Content -->
        <div class="tab-content">
            <!-- ==================== WATCHLIST MANAGEMENT ==================== -->
            <div v-if="activeMainTab === 'watchlist'" class="tab-panel">
                <div class="watchlist-header">
                    <div class="watchlist-tabs">
                        <button
                            v-for="list in watchlists"
                            :key="list.id"
                            class="watchlist-tab"
                            :class="{ active: activeWatchlistId === list.id }"
                            @click="activeWatchlistId = list.id"
                        >
                            <span class="list-icon">{{ list.icon }}</span>
                            <span class="list-name">{{ list.name }}</span>
                            <span class="list-count">{{ list.stocks.length }}</span>
                        </button>
                        <button class="watchlist-tab add-list" @click="showCreateListDialog = true">
                            <span class="list-icon">+</span>
                            <span class="list-name">新建分组</span>
                        </button>
                    </div>
                    <div class="watchlist-actions">
                        <ArtDecoButton variant="outline" size="sm" @click="exportWatchlist">导出CSV</ArtDecoButton>
                        <ArtDecoButton variant="outline" size="sm" @click="showImportDialog = true">
                            导入股票
                        </ArtDecoButton>
                        <ArtDecoButton variant="outline" size="sm" @click="toggleBatchMode">
                            {{ batchMode ? '退出批量' : '批量操作' }}
                        </ArtDecoButton>
                    </div>
                </div>

                <!-- Stock Cards Grid -->
                <div class="stock-cards-grid">
                    <div
                        v-for="stock in currentWatchlistStocks"
                        :key="stock.symbol"
                        class="stock-card"
                        :class="{ selected: selectedStocks.includes(stock.symbol) }"
                        @click="handleStockCardClick(stock)"
                    >
                        <div class="card-header">
                            <div class="stock-info">
                                <h4 class="stock-name">{{ stock.name }}</h4>
                                <span class="stock-code">{{ stock.symbol }}</span>
                            </div>
                            <div class="stock-tags">
                                <ArtDecoBadge
                                    v-for="tag in stock.tags.slice(0, 2)"
                                    :key="tag"
                                    :text="tag"
                                    variant="gold"
                                    size="sm"
                                />
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="price-section">
                                <span class="current-price">¥{{ stock.price.toFixed(2) }}</span>
                                <span class="price-change" :class="stock.change >= 0 ? 'rise' : 'fall'">
                                    {{ stock.change >= 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}%
                                </span>
                            </div>
                            <div class="indicators-overlay">
                                <span class="indicator" :class="getIndicatorClass(stock.rsi)">
                                    RSI {{ stock.rsi.toFixed(0) }}
                                </span>
                                <span class="indicator" :class="getIndicatorClass(stock.macd)">
                                    MACD {{ stock.macd > 0 ? '+' : '' }}{{ stock.macd.toFixed(2) }}
                                </span>
                            </div>
                        </div>
                        <div class="card-footer">
                            <div class="quick-actions">
                                <button class="action-btn" title="查看详情" @click.stop="viewStockDetail(stock)">
                                    📊
                                </button>
                                <button class="action-btn" title="添加提醒" @click.stop="setAlert(stock)">🔔</button>
                                <button class="action-btn" title="技术分析" @click.stop="openTechnicalAnalysis(stock)">
                                    📈
                                </button>
                                <button class="action-btn" title="从自选移除" @click.stop="removeFromWatchlist(stock)">
                                    ✕
                                </button>
                            </div>
                        </div>
                        <div v-if="batchMode" class="batch-checkbox">
                            <input
                                type="checkbox"
                                :checked="selectedStocks.includes(stock.symbol)"
                                @change="toggleStockSelection(stock.symbol)"
                            />
                        </div>
                    </div>
                </div>

                <!-- Empty State -->
                <div v-if="currentWatchlistStocks.length === 0" class="empty-state">
                    <div class="empty-icon">📋</div>
                    <h3>暂无股票</h3>
                    <p>点击"添加股票"开始构建您的自选股池</p>
                    <ArtDecoButton variant="solid" @click="showAddStockDialog = true">添加股票</ArtDecoButton>
                </div>
            </div>

            <!-- ==================== STRATEGY STOCK SELECTION ==================== -->
            <div v-if="activeMainTab === 'strategy'" class="tab-panel">
                <div class="strategy-header">
                    <div class="strategy-tabs">
                        <button
                            v-for="strategy in strategies"
                            :key="strategy.id"
                            class="strategy-tab"
                            :class="{ active: activeStrategyId === strategy.id }"
                            @click="activeStrategyId = strategy.id"
                        >
                            <span class="strategy-name">{{ strategy.name }}</span>
                            <span class="strategy-count">{{ strategy.stockCount }}只</span>
                        </button>
                    </div>
                    <div class="strategy-actions">
                        <ArtDecoButton variant="outline" size="sm" @click="runStrategySelection">
                            重新筛选
                        </ArtDecoButton>
                        <ArtDecoButton variant="solid" size="sm" @click="addStrategyResultsToWatchlist">
                            添加到自选
                        </ArtDecoButton>
                    </div>
                </div>

                <!-- Strategy Performance Metrics -->
                <div class="strategy-metrics">
                    <ArtDecoCard title="策略表现指标" hoverable class="metrics-card">
                        <div class="metrics-grid">
                            <div class="metric-item">
                                <div class="metric-label">近1月收益率</div>
                                <div class="metric-value" :class="currentStrategy.monthReturn >= 0 ? 'rise' : 'fall'">
                                    {{ currentStrategy.monthReturn >= 0 ? '+' : ''
                                    }}{{ currentStrategy.monthReturn.toFixed(2) }}%
                                </div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-label">近3月收益率</div>
                                <div class="metric-value" :class="currentStrategy.quarterReturn >= 0 ? 'rise' : 'fall'">
                                    {{ currentStrategy.quarterReturn >= 0 ? '+' : ''
                                    }}{{ currentStrategy.quarterReturn.toFixed(2) }}%
                                </div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-label">胜率</div>
                                <div class="metric-value gold">{{ currentStrategy.winRate.toFixed(1) }}%</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-label">最大回撤</div>
                                <div class="metric-value fall">{{ currentStrategy.maxDrawdown.toFixed(2) }}%</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-label">夏普比率</div>
                                <div class="metric-value gold">{{ currentStrategy.sharpeRatio.toFixed(2) }}</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-label">交易次数</div>
                                <div class="metric-value">{{ currentStrategy.tradeCount }}次</div>
                            </div>
                        </div>
                    </ArtDecoCard>
                </div>

                <!-- Strategy Stock List -->
                <ArtDecoCard title="策略选股结果" hoverable class="strategy-results-card">
                    <div class="results-table">
                        <div class="table-header">
                            <div class="th-col">股票</div>
                            <div class="th-col">现价</div>
                            <div class="th-col">涨跌幅</div>
                            <div class="th-col">综合得分</div>
                            <div class="th-col">技术信号</div>
                            <div class="th-col">基本面</div>
                            <div class="th-col">资金流向</div>
                            <div class="th-col">操作</div>
                        </div>
                        <div v-for="stock in currentStrategyStocks" :key="stock.symbol" class="table-row">
                            <div class="td-col stock-cell">
                                <span class="stock-name">{{ stock.name }}</span>
                                <span class="stock-code">{{ stock.symbol }}</span>
                            </div>
                            <div class="td-col">¥{{ stock.price.toFixed(2) }}</div>
                            <div class="td-col" :class="stock.change >= 0 ? 'rise' : 'fall'">
                                {{ stock.change >= 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}%
                            </div>
                            <div class="td-col score-cell">
                                <div class="score-bar">
                                    <div class="score-fill" :style="{ width: (stock.score ?? 0) + '%' }"></div>
                                </div>
                                <span class="score-value">{{ (stock.score ?? 0).toFixed(0) }}</span>
                            </div>
                            <div class="td-col">
                                <ArtDecoBadge
                                    :text="stock.techSignal"
                                    :variant="stock.techSignal === '买入' ? 'rise' : 'fall'"
                                    size="sm"
                                />
                            </div>
                            <div class="td-col">
                                <ArtDecoBadge :text="stock.fundamentalScore" variant="gold" size="sm" />
                            </div>
                            <div class="td-col" :class="(stock.fundFlow ?? 0) > 0 ? 'rise' : 'fall'">
                                {{ (stock.fundFlow ?? 0) > 0 ? '+' : '' }}{{ (stock.fundFlow ?? 0).toFixed(1) }}亿
                            </div>
                            <div class="td-col actions">
                                <button class="action-icon" title="添加到自选" @click="addToWatchlist(stock)">+</button>
                                <button class="action-icon" title="查看详情" @click="viewStockDetail(stock)">📊</button>
                            </div>
                        </div>
                    </div>
                </ArtDecoCard>
            </div>

            <!-- ==================== INDUSTRY/CONCEPT SELECTION ==================== -->
            <div v-if="activeMainTab === 'industry'" class="tab-panel">
                <div class="industry-header">
                    <div class="industry-tabs">
                        <button
                            v-for="tab in industryTabs"
                            :key="tab.key"
                            class="industry-tab"
                            :class="{ active: activeIndustryTab === tab.key }"
                            @click="activeIndustryTab = tab.key"
                        >
                            {{ tab.label }}
                        </button>
                    </div>
                    <div class="filter-controls">
                        <ArtDecoSelect v-model="sortBy" :options="sortOptions" placeholder="排序方式" size="sm" />
                        <ArtDecoSelect
                            v-model="filterTrend"
                            :options="trendFilters"
                            placeholder="涨跌幅筛选"
                            size="sm"
                        />
                    </div>
                </div>

                <!-- Industry Heatmap -->
                <div v-if="activeIndustryTab === 'industry'" class="industry-content">
                    <ArtDecoCard title="行业板块热度排行" hoverable class="heatmap-card">
                        <div class="industry-heatmap">
                            <div
                                v-for="sector in industries"
                                :key="sector.name"
                                class="sector-item"
                                :class="{ positive: sector.change > 0, negative: sector.change < 0 }"
                                @click="selectIndustry(sector)"
                            >
                                <div class="sector-name">{{ sector.name }}</div>
                                <div class="sector-change" :class="sector.change >= 0 ? 'rise' : 'fall'">
                                    {{ sector.change >= 0 ? '+' : '' }}{{ sector.change.toFixed(2) }}%
                                </div>
                                <div class="sector-bar">
                                    <div
                                        class="bar-fill"
                                        :style="{ width: Math.abs(sector.change) * 3 + '%' }"
                                        :class="sector.change >= 0 ? 'rise' : 'fall'"
                                    ></div>
                                </div>
                                <div class="sector-stocks">{{ sector.stockCount }}只</div>
                            </div>
                        </div>
                    </ArtDecoCard>

                    <ArtDecoCard title="行业详情" hoverable class="industry-detail-card">
                        <div v-if="selectedIndustry" class="detail-content">
                            <div class="detail-header">
                                <h3>{{ selectedIndustry.name }}</h3>
                                <ArtDecoBadge
                                    :text="selectedIndustry.change >= 0 ? '上涨' : '下跌'"
                                    :variant="selectedIndustry.change >= 0 ? 'rise' : 'fall'"
                                />
                            </div>
                            <div class="detail-metrics">
                                <div class="metric">
                                    <span class="label">涨跌幅</span>
                                    <span class="value" :class="selectedIndustry.change >= 0 ? 'rise' : 'fall'">
                                        {{ selectedIndustry.change >= 0 ? '+' : ''
                                        }}{{ selectedIndustry.change.toFixed(2) }}%
                                    </span>
                                </div>
                                <div class="metric">
                                    <span class="label">成交额</span>
                                    <span class="value">{{ selectedIndustry.volume }}亿</span>
                                </div>
                                <div class="metric">
                                    <span class="label">领涨股</span>
                                    <span class="value gold">{{ selectedIndustry.leaderStock }}</span>
                                </div>
                            </div>
                            <div class="rotation-signal">
                                <h4>轮动信号</h4>
                                <div class="signal-item">
                                    <span class="signal-label">资金流向</span>
                                    <ArtDecoBadge
                                        :text="selectedIndustry.fundFlowTrend"
                                        :variant="selectedIndustry.fundFlowTrend === '流入' ? 'rise' : 'fall'"
                                    />
                                </div>
                                <div class="signal-item">
                                    <span class="signal-label">技术形态</span>
                                    <ArtDecoBadge :text="selectedIndustry.techPattern" variant="gold" />
                                </div>
                            </div>
                            <div class="industry-stocks">
                                <h4>板块成分股</h4>
                                <div class="stocks-grid">
                                    <div
                                        v-for="stock in selectedIndustryStocks"
                                        :key="stock.symbol"
                                        class="industry-stock-item"
                                        @click="viewStockDetail(stock)"
                                    >
                                        <span class="stock-name">{{ stock.name }}</span>
                                        <span class="stock-change" :class="stock.change >= 0 ? 'rise' : 'fall'">
                                            {{ stock.change >= 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}%
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div v-else class="empty-detail">
                            <p>点击左侧行业板块查看详情</p>
                        </div>
                    </ArtDecoCard>
                </div>

                <!-- Concept Hotspots -->
                <div v-if="activeIndustryTab === 'concept'" class="concept-content">
                    <ArtDecoCard title="概念板块热度排行" hoverable class="concept-heatmap-card">
                        <div class="concept-heatmap">
                            <div
                                v-for="concept in concepts"
                                :key="concept.name"
                                class="concept-item"
                                @click="selectConcept(concept)"
                            >
                                <div class="concept-name">{{ concept.name }}</div>
                                <div class="concept-change" :class="concept.change >= 0 ? 'rise' : 'fall'">
                                    {{ concept.change >= 0 ? '+' : '' }}{{ concept.change.toFixed(2) }}%
                                </div>
                                <div class="concept-count">{{ concept.stockCount }}只关联</div>
                                <div class="concept-hot" :class="getHotClass(concept.hotLevel)">
                                    {{ concept.hotLevel }}
                                </div>
                            </div>
                        </div>
                    </ArtDecoCard>

                    <ArtDecoCard title="概念详情" hoverable class="concept-detail-card">
                        <div v-if="selectedConcept" class="detail-content">
                            <div class="detail-header">
                                <h3>{{ selectedConcept.name }}</h3>
                                <ArtDecoBadge :text="selectedConcept.hotLevel" variant="gold" />
                            </div>
                            <div class="concept-stocks">
                                <h4>关联股票</h4>
                                <div class="stocks-list">
                                    <div
                                        v-for="stock in selectedConceptStocks"
                                        :key="stock.symbol"
                                        class="concept-stock-item"
                                        @click="viewStockDetail(stock)"
                                    >
                                        <div class="stock-main">
                                            <span class="stock-name">{{ stock.name }}</span>
                                            <span class="stock-code">{{ stock.symbol }}</span>
                                        </div>
                                        <div class="stock-price">¥{{ stock.price.toFixed(2) }}</div>
                                        <div class="stock-change" :class="stock.change >= 0 ? 'rise' : 'fall'">
                                            {{ stock.change >= 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}%
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div v-else class="empty-detail">
                            <p>点击上方概念板块查看详情</p>
                        </div>
                    </ArtDecoCard>
                </div>
            </div>

            <!-- ==================== BATCH OPERATIONS ==================== -->
            <div v-if="activeMainTab === 'batch'" class="tab-panel">
                <div class="batch-header">
                    <div class="batch-info">
                        <span class="selected-count">已选择 {{ selectedBatchStocks.length }} 只股票</span>
                        <ArtDecoButton
                            v-if="selectedBatchStocks.length > 0"
                            variant="outline"
                            size="sm"
                            @click="clearBatchSelection"
                        >
                            清除选择
                        </ArtDecoButton>
                    </div>
                    <div class="batch-actions">
                        <ArtDecoButton
                            variant="outline"
                            size="sm"
                            :disabled="selectedBatchStocks.length === 0"
                            @click="batchAddToWatchlist"
                        >
                            批量添加自选
                        </ArtDecoButton>
                        <ArtDecoButton
                            variant="outline"
                            size="sm"
                            :disabled="selectedBatchStocks.length === 0"
                            @click="batchSetAlerts"
                        >
                            批量设置提醒
                        </ArtDecoButton>
                        <ArtDecoButton
                            variant="outline"
                            size="sm"
                            :disabled="selectedBatchStocks.length === 0"
                            @click="batchExport"
                        >
                            批量导出
                        </ArtDecoButton>
                        <ArtDecoButton
                            variant="solid"
                            size="sm"
                            :disabled="selectedBatchStocks.length === 0"
                            @click="batchTechnicalAnalysis"
                        >
                            批量技术分析
                        </ArtDecoButton>
                    </div>
                </div>

                <!-- Batch Stock Selection Panel -->
                <ArtDecoCard title="股票选择" hoverable class="batch-selection-card">
                    <div class="batch-filter-bar">
                        <ArtDecoInput v-model="batchSearchQuery" placeholder="搜索股票代码或名称" size="sm" />
                        <ArtDecoSelect
                            v-model="batchFilterIndustry"
                            :options="batchIndustryOptions"
                            placeholder="行业筛选"
                            size="sm"
                        />
                        <ArtDecoSelect
                            v-model="batchFilterTrend"
                            :options="batchTrendOptions"
                            placeholder="涨跌幅筛选"
                            size="sm"
                        />
                    </div>
                    <div class="batch-stock-grid">
                        <div
                            v-for="stock in filteredBatchStocks"
                            :key="stock.symbol"
                            class="batch-stock-item"
                            :class="{ selected: selectedBatchStocks.includes(stock.symbol) }"
                            @click="toggleBatchStock(stock.symbol)"
                        >
                            <div class="stock-name">{{ stock.name }}</div>
                            <div class="stock-code">{{ stock.symbol }}</div>
                            <div class="stock-change" :class="stock.change >= 0 ? 'rise' : 'fall'">
                                {{ stock.change >= 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}%
                            </div>
                        </div>
                    </div>
                </ArtDecoCard>

                <!-- Batch Alert Configuration -->
                <ArtDecoCard title="批量提醒配置" hoverable class="batch-alert-card">
                    <div class="alert-config-form">
                        <div class="form-row">
                            <label>提醒类型</label>
                            <div class="checkbox-group">
                                <label class="checkbox-item">
                                    <input type="checkbox" v-model="alertConfig.priceChange" />
                                    <span>价格变动</span>
                                </label>
                                <label class="checkbox-item">
                                    <input type="checkbox" v-model="alertConfig.volumeSpike" />
                                    <span>成交量异动</span>
                                </label>
                                <label class="checkbox-item">
                                    <input type="checkbox" v-model="alertConfig.techSignal" />
                                    <span>技术信号</span>
                                </label>
                                <label class="checkbox-item">
                                    <input type="checkbox" v-model="alertConfig.fundFlow" />
                                    <span>资金流向</span>
                                </label>
                            </div>
                        </div>
                        <div class="form-row">
                            <label>涨跌幅阈值</label>
                            <ArtDecoInput
                                v-model.number="alertConfig.priceThreshold"
                                type="number"
                                placeholder="输入阈值"
                                size="sm"
                            />
                            <span class="unit">%</span>
                        </div>
                        <ArtDecoButton variant="solid" @click="applyBatchAlerts">应用批量提醒</ArtDecoButton>
                    </div>
                </ArtDecoCard>
            </div>

            <!-- ==================== STOCK CARDS DISPLAY ==================== -->
            <div v-if="activeMainTab === 'cards'" class="tab-panel">
                <div class="cards-header">
                    <div class="view-options">
                        <ArtDecoButtonGroup>
                            <ArtDecoButton
                                variant="outline"
                                size="sm"
                                class="view-btn"
                                :class="{ 'is-active': cardViewMode === 'grid' }"
                                @click="cardViewMode = 'grid'"
                            >
                                网格视图
                            </ArtDecoButton>
                            <ArtDecoButton
                                variant="outline"
                                size="sm"
                                class="view-btn"
                                :class="{ 'is-active': cardViewMode === 'list' }"
                                @click="cardViewMode = 'list'"
                            >
                                列表视图
                            </ArtDecoButton>
                        </ArtDecoButtonGroup>
                    </div>
                    <div class="cards-filter">
                        <ArtDecoSelect
                            v-model="cardSortBy"
                            :options="cardSortOptions"
                            placeholder="排序方式"
                            size="sm"
                        />
                        <ArtDecoSelect
                            v-model="cardFilter"
                            :options="cardFilterOptions"
                            placeholder="筛选条件"
                            size="sm"
                        />
                    </div>
                </div>

                <!-- Stock Cards Grid View -->
                <div v-if="cardViewMode === 'grid'" class="cards-grid">
                    <div
                        v-for="stock in displayCards"
                        :key="stock.symbol"
                        class="display-card"
                        @click="viewStockDetail(stock)"
                    >
                        <div class="card-top-bar"></div>
                        <div class="card-main">
                            <div class="card-header">
                                <h3 class="stock-name">{{ stock.name }}</h3>
                                <span class="stock-code">{{ stock.symbol }}</span>
                            </div>
                            <div class="card-price">
                                <span class="price">¥{{ stock.price.toFixed(2) }}</span>
                                <span class="change" :class="stock.change >= 0 ? 'rise' : 'fall'">
                                    {{ stock.change >= 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}%
                                </span>
                            </div>
                            <div class="card-indicators">
                                <div class="indicator-row">
                                    <span class="label">MA5</span>
                                    <span class="value" :class="getTrendClass(stock.ma5, stock.price)">
                                        {{ stock.ma5.toFixed(2) }}
                                    </span>
                                </div>
                                <div class="indicator-row">
                                    <span class="label">RSI</span>
                                    <span class="value" :class="getRsiClass(stock.rsi)">
                                        {{ stock.rsi.toFixed(0) }}
                                    </span>
                                </div>
                                <div class="indicator-row">
                                    <span class="label">MACD</span>
                                    <span class="value" :class="stock.macd >= 0 ? 'rise' : 'fall'">
                                        {{ stock.macd >= 0 ? '+' : '' }}{{ stock.macd.toFixed(2) }}
                                    </span>
                                </div>
                            </div>
                            <div class="card-tags">
                                <ArtDecoBadge
                                    v-for="tag in stock.tags"
                                    :key="tag"
                                    :text="tag"
                                    :variant="getTagVariant(tag)"
                                    size="sm"
                                />
                            </div>
                        </div>
                        <div class="card-actions">
                            <button class="card-action-btn" @click.stop="addToWatchlist(stock)">+自选</button>
                            <button class="card-action-btn" @click.stop="setAlert(stock)">🔔</button>
                        </div>
                    </div>
                </div>

                <!-- Stock Cards List View -->
                <div v-if="cardViewMode === 'list'" class="cards-list">
                    <div
                        v-for="stock in displayCards"
                        :key="stock.symbol"
                        class="list-card-row"
                        @click="viewStockDetail(stock)"
                    >
                        <div class="row-main">
                            <div class="stock-identity">
                                <span class="stock-name">{{ stock.name }}</span>
                                <span class="stock-code">{{ stock.symbol }}</span>
                            </div>
                            <div class="stock-price-info">
                                <span class="price">¥{{ stock.price.toFixed(2) }}</span>
                                <span class="change" :class="stock.change >= 0 ? 'rise' : 'fall'">
                                    {{ stock.change >= 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}%
                                </span>
                            </div>
                            <div class="stock-indicators-list">
                                <span class="indi">MA5: {{ stock.ma5.toFixed(2) }}</span>
                                <span class="indi">MA10: {{ stock.ma10.toFixed(2) }}</span>
                                <span class="indi">RSI: {{ stock.rsi.toFixed(0) }}</span>
                                <span class="indi">
                                    MACD: {{ stock.macd >= 0 ? '+' : '' }}{{ stock.macd.toFixed(2) }}
                                </span>
                            </div>
                            <div class="stock-tags">
                                <ArtDecoBadge
                                    v-for="tag in stock.tags.slice(0, 3)"
                                    :key="tag"
                                    :text="tag"
                                    :variant="getTagVariant(tag)"
                                    size="sm"
                                />
                            </div>
                        </div>
                        <div class="row-actions">
                            <button class="row-action-btn" @click.stop="addToWatchlist(stock)">+自选</button>
                            <button class="row-action-btn" @click.stop="setAlert(stock)">🔔</button>
                            <button class="row-action-btn" @click.stop="openTechnicalAnalysis(stock)">📈</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Add Stock Dialog -->
        <div v-if="showAddStockDialog" class="dialog-overlay" @click.self="showAddStockDialog = false">
            <div class="dialog artdeco-dialog">
                <div class="dialog-header">
                    <h3>添加股票到自选</h3>
                    <button class="close-btn" @click="showAddStockDialog = false">×</button>
                </div>
                <div class="dialog-body">
                    <ArtDecoInput v-model="newStockQuery" placeholder="输入股票代码或名称" @input="searchNewStock" />
                    <div class="search-results">
                        <div
                            v-for="result in searchResults"
                            :key="result.symbol"
                            class="search-result-item"
                            @click="confirmAddStock(result)"
                        >
                            <span class="stock-name">{{ result.name }}</span>
                            <span class="stock-code">{{ result.symbol }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Create Watchlist Dialog -->
        <div v-if="showCreateListDialog" class="dialog-overlay" @click.self="showCreateListDialog = false">
            <div class="dialog artdeco-dialog">
                <div class="dialog-header">
                    <h3>新建自选分组</h3>
                    <button class="close-btn" @click="showCreateListDialog = false">×</button>
                </div>
                <div class="dialog-body">
                    <ArtDecoInput v-model="newListName" placeholder="分组名称" />
                    <div class="dialog-actions">
                        <ArtDecoButton variant="outline" @click="showCreateListDialog = false">取消</ArtDecoButton>
                        <ArtDecoButton variant="solid" @click="createWatchlist">创建</ArtDecoButton>
                    </div>
                </div>
            </div>
        </div>

        <!-- Import Dialog -->
        <div v-if="showImportDialog" class="dialog-overlay" @click.self="showImportDialog = false">
            <div class="dialog artdeco-dialog">
                <div class="dialog-header">
                    <h3>导入股票</h3>
                    <button class="close-btn" @click="showImportDialog = false">×</button>
                </div>
                <div class="dialog-body">
                    <div class="import-options">
                        <label class="import-option">
                            <input type="radio" v-model="importType" value="csv" />
                            <span>CSV文件导入</span>
                        </label>
                        <label class="import-option">
                            <input type="radio" v-model="importType" value="text" />
                            <span>文本粘贴导入</span>
                        </label>
                    </div>
                    <div v-if="importType === 'text'" class="text-import">
                        <textarea v-model="importText" placeholder="每行一个股票代码或名称" rows="6"></textarea>
                    </div>
                    <div class="dialog-actions">
                        <ArtDecoButton variant="outline" @click="showImportDialog = false">取消</ArtDecoButton>
                        <ArtDecoButton variant="solid" @click="importStocks">导入</ArtDecoButton>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, computed, onMounted, onUnmounted } from 'vue'
    import {
        ArtDecoStatCard,
        ArtDecoCard,
        ArtDecoButton,
        ArtDecoButtonGroup,
        ArtDecoBadge,
        ArtDecoInput,
        ArtDecoSelect
    } from '@/components/artdeco'

    // ==================== TYPES ====================

    interface Stock {
        symbol: string
        name: string
        price: number
        change: number
        tags: string[]
        rsi: number
        macd: number
        ma5: number
        ma10: number
        volume: number
        industry?: string
        concept?: string[]
        score?: number
        techSignal?: string
        fundamentalScore?: string
        fundFlow?: number
    }

    interface Watchlist {
        id: string
        name: string
        icon: string
        stocks: Stock[]
    }

    interface Strategy {
        id: string
        name: string
        stockCount: number
        monthReturn: number
        quarterReturn: number
        winRate: number
        maxDrawdown: number
        sharpeRatio: number
        tradeCount: number
        stocks: Stock[]
    }

    interface Industry {
        name: string
        change: number
        volume: string
        stockCount: number
        leaderStock: string
        fundFlowTrend: string
        techPattern: string
    }

    interface Concept {
        name: string
        change: number
        stockCount: number
        hotLevel: string
    }

    // ==================== STATE ====================

    const currentTime = ref('')
    const activeMainTab = ref('watchlist')
    const batchMode = ref(false)
    const selectedStocks = ref<string[]>([])
    const selectedBatchStocks = ref<string[]>([])

    // Dialog states
    const showAddStockDialog = ref(false)
    const showCreateListDialog = ref(false)
    const showImportDialog = ref(false)
    const newStockQuery = ref('')
    const newListName = ref('')
    const importType = ref('csv')
    const importText = ref('')

    // Filter states
    const sortBy = ref('change')
    const filterTrend = ref('all')
    const batchSearchQuery = ref('')
    const batchFilterIndustry = ref('')
    const batchFilterTrend = ref('')
    const cardViewMode = ref('grid')
    const cardSortBy = ref('change')
    const cardFilter = ref('all')

    // Tabs
    const mainTabs = [
        { key: 'watchlist', label: '自选管理', icon: '📋' },
        { key: 'strategy', label: '策略选股', icon: '🎯' },
        { key: 'industry', label: '行业/概念', icon: '📊' },
        { key: 'batch', label: '批量操作', icon: '⚡' },
        { key: 'cards', label: '卡片视图', icon: '🃏' }
    ]

    const industryTabs = [
        { key: 'industry', label: '行业板块' },
        { key: 'concept', label: '概念热点' }
    ]

    const sortOptions = [
        { label: '涨跌幅', value: 'change' },
        { label: '成交额', value: 'volume' },
        { label: '股票数量', value: 'stockCount' }
    ]

    const trendFilters = [
        { label: '全部', value: 'all' },
        { label: '上涨', value: 'rise' },
        { label: '下跌', value: 'fall' }
    ]

    const batchIndustryOptions = [
        { label: '全部行业', value: '' },
        { label: '银行', value: 'bank' },
        { label: '证券', value: 'securities' },
        { label: '白酒', value: 'liquor' },
        { label: '医药', value: 'medical' }
    ]

    const batchTrendOptions = [
        { label: '全部', value: '' },
        { label: '上涨', value: 'rise' },
        { label: '下跌', value: 'fall' }
    ]

    const cardSortOptions = [
        { label: '涨跌幅', value: 'change' },
        { label: '价格', value: 'price' },
        { label: '代码', value: 'symbol' }
    ]

    const cardFilterOptions = [
        { label: '全部', value: 'all' },
        { label: '上涨', value: 'rise' },
        { label: '下跌', value: 'fall' },
        { label: '有提醒', value: 'alert' }
    ]

    // Watchlist state
    const watchlists = ref<Watchlist[]>([
        {
            id: 'default',
            name: '默认分组',
            icon: '⭐',
            stocks: []
        },
        {
            id: 'hot',
            name: '热门关注',
            icon: '🔥',
            stocks: []
        },
        {
            id: 'long',
            name: '长线持有',
            icon: '💎',
            stocks: []
        }
    ])

    const activeWatchlistId = ref('default')
    const searchResults = ref<Stock[]>([])

    // Strategy state
    const strategies = ref<Strategy[]>([
        {
            id: 'ma',
            name: '均线策略',
            stockCount: 15,
            monthReturn: 5.2,
            quarterReturn: 12.8,
            winRate: 68.5,
            maxDrawdown: -8.2,
            sharpeRatio: 1.45,
            tradeCount: 45,
            stocks: []
        },
        {
            id: 'momentum',
            name: '动量策略',
            stockCount: 20,
            monthReturn: 8.5,
            quarterReturn: 15.2,
            winRate: 72.3,
            maxDrawdown: -6.5,
            sharpeRatio: 1.68,
            tradeCount: 62,
            stocks: []
        },
        {
            id: 'value',
            name: '价值策略',
            stockCount: 12,
            monthReturn: 3.2,
            quarterReturn: 9.8,
            winRate: 82.1,
            maxDrawdown: -4.2,
            sharpeRatio: 1.92,
            tradeCount: 28,
            stocks: []
        }
    ])

    const activeStrategyId = ref('ma')

    // Industry/Concept state
    const industries = ref<Industry[]>([
        {
            name: '人工智能',
            change: 3.52,
            volume: '2850',
            stockCount: 156,
            leaderStock: '科大讯飞',
            fundFlowTrend: '流入',
            techPattern: '多头突破'
        },
        {
            name: '新能源汽车',
            change: 2.18,
            volume: '3520',
            stockCount: 228,
            leaderStock: '比亚迪',
            fundFlowTrend: '流入',
            techPattern: '强势上涨'
        },
        {
            name: '半导体',
            change: -1.25,
            volume: '1890',
            stockCount: 98,
            leaderStock: '中芯国际',
            fundFlowTrend: '流出',
            techPattern: '回调整理'
        },
        {
            name: '医疗器械',
            change: 1.85,
            volume: '980',
            stockCount: 85,
            leaderStock: '迈瑞医疗',
            fundFlowTrend: '流入',
            techPattern: '稳步上扬'
        },
        {
            name: '白酒',
            change: 0.95,
            volume: '1250',
            stockCount: 42,
            leaderStock: '贵州茅台',
            fundFlowTrend: '流入',
            techPattern: '震荡整理'
        },
        {
            name: '银行',
            change: -0.42,
            volume: '680',
            stockCount: 42,
            leaderStock: '招商银行',
            fundFlowTrend: '流出',
            techPattern: '弱势整理'
        }
    ])

    const concepts = ref<Concept[]>([
        { name: 'AI芯片', change: 4.52, stockCount: 28, hotLevel: '🔥🔥🔥' },
        { name: '机器人概念', change: 3.85, stockCount: 156, hotLevel: '🔥🔥' },
        { name: '光伏概念', change: -2.15, stockCount: 98, hotLevel: '🔥' },
        { name: '数字货币', change: 5.23, stockCount: 45, hotLevel: '🔥🔥🔥' },
        { name: '消费电子', change: 1.28, stockCount: 72, hotLevel: '🔥' },
        { name: '创新药', change: 2.45, stockCount: 55, hotLevel: '🔥🔥' }
    ])

    const activeIndustryTab = ref('industry')
    const selectedIndustry = ref<Industry | null>(null)
    const selectedConcept = ref<Concept | null>(null)

    // Alert config
    const alertConfig = ref({
        priceChange: true,
        volumeSpike: true,
        techSignal: true,
        fundFlow: false,
        priceThreshold: 3
    })

    // Stats
    const watchlistStats = ref({
        totalStocks: 0
    })

    const strategyStats = ref({
        totalSelected: 47,
        changePercent: 2.5
    })

    const industryStats = ref({
        totalIndustries: 6
    })

    const conceptStats = ref({
        totalConcepts: 6
    })

    const portfolioStats = ref({
        dailyChange: '+1,256.80',
        changePercent: 0.85,
        totalReturn: '+28,560.00',
        returnPercent: 5.68
    })

    // ==================== MOCK DATA ====================

    const generateMockStocks = (count: number): Stock[] => {
        const stockNames = [
            '贵州茅台',
            '宁德时代',
            '比亚迪',
            '招商银行',
            '中信证券',
            '中国平安',
            '五粮液',
            '恒瑞医药',
            '海康威视',
            '三一重工',
            '隆基绿能',
            '伊利股份',
            '中国中免',
            '万华化学',
            '药明康德',
            '海尔智家',
            '山西汾酒',
            '泸州老窖',
            '古井贡酒',
            '洋河股份'
        ]
        const industries = ['白酒', '新能源', '汽车', '银行', '证券', '保险', '医药', '电子']
        const tagsList = ['龙一', '行业龙头', '业绩预增', '机构重仓', '热点概念', '突破形态']

        return Array.from({ length: count }, (_, i) => {
            const name = stockNames[i % stockNames.length]
            const change = Math.random() * 10 - 4
            return {
                symbol: `${600000 + i}`,
                name: name + (i >= stockNames.length ? ` ${Math.floor(i / stockNames.length) + 1}` : ''),
                price: 50 + Math.random() * 200,
                change,
                tags: [tagsList[i % tagsList.length], tagsList[(i + 1) % tagsList.length]],
                rsi: 30 + Math.random() * 60,
                macd: Math.random() * 2 - 1,
                ma5: 100 + Math.random() * 50,
                ma10: 100 + Math.random() * 50,
                volume: Math.floor(Math.random() * 10000000),
                industry: industries[i % industries.length],
                score: 60 + Math.random() * 40,
                techSignal: Math.random() > 0.5 ? '买入' : '卖出',
                fundamentalScore: ['优秀', '良好', '一般'][Math.floor(Math.random() * 3)],
                fundFlow: Math.random() * 5 - 2
            }
        })
    }

    // Initialize mock data
    const allStocks = generateMockStocks(50)
    watchlists.value[0].stocks = allStocks.slice(0, 15).map(s => ({ ...s, tags: s.tags.slice(0, 2) }))
    watchlists.value[1].stocks = allStocks.slice(15, 25).map(s => ({ ...s, tags: s.tags.slice(0, 2) }))
    watchlists.value[2].stocks = allStocks.slice(25, 35).map(s => ({ ...s, tags: s.tags.slice(0, 2) }))

    strategies.value[0].stocks = allStocks.slice(0, 15)
    strategies.value[1].stocks = allStocks.slice(10, 30)
    strategies.value[2].stocks = allStocks.slice(20, 32)

    const industryStocksMap: Record<string, Stock[]> = {
        人工智能: allStocks.slice(0, 8),
        新能源汽车: allStocks.slice(8, 16),
        半导体: allStocks.slice(16, 24),
        医疗器械: allStocks.slice(24, 32),
        白酒: allStocks.slice(32, 40),
        银行: allStocks.slice(40, 48)
    }

    const conceptStocksMap: Record<string, Stock[]> = {
        AI芯片: allStocks.slice(0, 10),
        机器人概念: allStocks.slice(5, 15),
        光伏概念: allStocks.slice(10, 20),
        数字货币: allStocks.slice(15, 25),
        消费电子: allStocks.slice(20, 30),
        创新药: allStocks.slice(25, 35)
    }

    // ==================== COMPUTED ====================

    const currentWatchlistStocks = computed(() => {
        const list = watchlists.value.find(w => w.id === activeWatchlistId.value)
        return list?.stocks || []
    })

    const currentStrategy = computed(() => {
        return strategies.value.find(s => s.id === activeStrategyId.value) || strategies.value[0]
    })

    const currentStrategyStocks = computed(() => {
        return currentStrategy.value.stocks
    })

    const selectedIndustryStocks = computed(() => {
        if (selectedIndustry.value) {
            return industryStocksMap[selectedIndustry.value.name] || []
        }
        return []
    })

    const selectedConceptStocks = computed(() => {
        if (selectedConcept.value) {
            return conceptStocksMap[selectedConcept.value.name] || []
        }
        return []
    })

    const filteredBatchStocks = computed(() => {
        let stocks = [...allStocks]

        if (batchSearchQuery.value) {
            const query = batchSearchQuery.value.toLowerCase()
            stocks = stocks.filter(s => s.symbol.includes(query) || s.name.toLowerCase().includes(query))
        }

        if (batchFilterTrend.value === 'rise') {
            stocks = stocks.filter(s => s.change >= 0)
        } else if (batchFilterTrend.value === 'fall') {
            stocks = stocks.filter(s => s.change < 0)
        }

        return stocks
    })

    const displayCards = computed(() => {
        let cards = [...allStocks]

        if (cardFilter.value === 'rise') {
            cards = cards.filter(c => c.change >= 0)
        } else if (cardFilter.value === 'fall') {
            cards = cards.filter(c => c.change < 0)
        }

        if (cardSortBy.value === 'price') {
            cards.sort((a, b) => b.price - a.price)
        } else if (cardSortBy.value === 'symbol') {
            cards.sort((a, b) => a.symbol.localeCompare(b.symbol))
        }

        return cards
    })

    // ==================== METHODS ====================

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

    const switchMainTab = (tab: string) => {
        activeMainTab.value = tab
    }

    const refreshAllData = () => {
        // Simulate refresh
        updateTime()
    }

    const toggleBatchMode = () => {
        batchMode.value = !batchMode.value
        if (!batchMode.value) {
            selectedStocks.value = []
        }
    }

    const handleStockCardClick = (stock: Stock) => {
        if (batchMode.value) {
            toggleStockSelection(stock.symbol)
        } else {
            viewStockDetail(stock)
        }
    }

    const toggleStockSelection = (symbol: string) => {
        const index = selectedStocks.value.indexOf(symbol)
        if (index > -1) {
            selectedStocks.value.splice(index, 1)
        } else {
            selectedStocks.value.push(symbol)
        }
    }

    const viewStockDetail = (stock: Stock) => {
        console.log('View stock detail:', stock.symbol)
    }

    const setAlert = (stock: Stock) => {
        console.log('Set alert for:', stock.symbol)
    }

    const openTechnicalAnalysis = (stock: Stock) => {
        console.log('Open technical analysis for:', stock.symbol)
    }

    const removeFromWatchlist = (stock: Stock) => {
        const list = watchlists.value.find(w => w.id === activeWatchlistId.value)
        if (list) {
            const index = list.stocks.findIndex(s => s.symbol === stock.symbol)
            if (index > -1) {
                list.stocks.splice(index, 1)
            }
        }
    }

    const exportWatchlist = () => {
        const list = watchlists.value.find(w => w.id === activeWatchlistId.value)
        if (list) {
            const csv = list.stocks.map(s => `${s.symbol},${s.name},${s.price},${s.change}`).join('\n')
            console.log('Exporting:', csv)
        }
    }

    const searchNewStock = () => {
        if (newStockQuery.value.length >= 1) {
            const query = newStockQuery.value.toLowerCase()
            searchResults.value = allStocks
                .filter(s => s.symbol.includes(query) || s.name.toLowerCase().includes(query))
                .slice(0, 10)
        } else {
            searchResults.value = []
        }
    }

    const confirmAddStock = (stock: Stock) => {
        const list = watchlists.value.find(w => w.id === activeWatchlistId.value)
        if (list && !list.stocks.find(s => s.symbol === stock.symbol)) {
            list.stocks.push(stock)
        }
        showAddStockDialog.value = false
        newStockQuery.value = ''
        searchResults.value = []
    }

    const createWatchlist = () => {
        if (newListName.value.trim()) {
            watchlists.value.push({
                id: `custom-${Date.now()}`,
                name: newListName.value.trim(),
                icon: '📁',
                stocks: []
            })
            newListName.value = ''
            showCreateListDialog.value = false
        }
    }

    const importStocks = () => {
        console.log('Importing stocks:', importText.value)
        showImportDialog.value = false
        importText.value = ''
    }

    // Strategy methods
    const runStrategySelection = () => {
        console.log('Running strategy selection')
    }

    const addStrategyResultsToWatchlist = () => {
        const list = watchlists.value.find(w => w.id === activeWatchlistId.value)
        if (list) {
            currentStrategy.value.stocks.forEach(stock => {
                if (!list.stocks.find(s => s.symbol === stock.symbol)) {
                    list.stocks.push({ ...stock })
                }
            })
        }
    }

    const addToWatchlist = (stock: Stock) => {
        const list = watchlists.value.find(w => w.id === activeWatchlistId.value)
        if (list && !list.stocks.find(s => s.symbol === stock.symbol)) {
            list.stocks.push({ ...stock })
        }
    }

    // Industry/Concept methods
    const selectIndustry = (industry: Industry) => {
        selectedIndustry.value = industry
    }

    const selectConcept = (concept: Concept) => {
        selectedConcept.value = concept
    }

    const getHotClass = (level: string) => {
        if (level.includes('🔥🔥🔥')) return 'hot-high'
        if (level.includes('🔥🔥')) return 'hot-medium'
        return 'hot-low'
    }

    // Batch methods
    const toggleBatchStock = (symbol: string) => {
        const index = selectedBatchStocks.value.indexOf(symbol)
        if (index > -1) {
            selectedBatchStocks.value.splice(index, 1)
        } else {
            selectedBatchStocks.value.push(symbol)
        }
    }

    const clearBatchSelection = () => {
        selectedBatchStocks.value = []
    }

    const batchAddToWatchlist = () => {
        const list = watchlists.value.find(w => w.id === activeWatchlistId.value)
        if (list) {
            selectedBatchStocks.value.forEach(symbol => {
                const stock = allStocks.find(s => s.symbol === symbol)
                if (stock && !list.stocks.find(s => s.symbol === symbol)) {
                    list.stocks.push({ ...stock })
                }
            })
        }
        clearBatchSelection()
    }

    const batchSetAlerts = () => {
        console.log('Setting batch alerts for:', selectedBatchStocks.value)
    }

    const batchExport = () => {
        console.log('Batch export:', selectedBatchStocks.value)
    }

    const batchTechnicalAnalysis = () => {
        console.log('Batch technical analysis:', selectedBatchStocks.value)
    }

    const applyBatchAlerts = () => {
        console.log('Applying batch alerts:', alertConfig.value)
    }

    // Utility methods
    const getIndicatorClass = (value: number) => {
        if (value > 70) return 'overbought'
        if (value < 30) return 'oversold'
        return 'neutral'
    }

    const getTrendClass = (ma: number, price: number) => {
        if (price > ma) return 'rise'
        if (price < ma) return 'fall'
        return 'neutral'
    }

    const getRsiClass = (rsi: number) => {
        if (rsi > 70) return 'overbought'
        if (rsi < 30) return 'oversold'
        return 'neutral'
    }

    const getTagVariant = (tag: string): 'gold' | 'rise' | 'fall' | 'info' | 'warning' | 'success' | 'danger' => {
        if (['龙一', '行业龙头', '业绩预增'].includes(tag)) return 'gold'
        if (['机构重仓', '热点概念'].includes(tag)) return 'rise'
        return 'info'
    }

    // ==================== LIFECYCLE ====================

    let timeInterval: ReturnType<typeof setInterval>

    onMounted(() => {
        updateTime()
        timeInterval = setInterval(updateTime, 1000)

        // Update stats
        watchlistStats.value.totalStocks = watchlists.value.reduce((sum, w) => sum + w.stocks.length, 0)
    })

    onUnmounted(() => {
        if (timeInterval) {
            clearInterval(timeInterval)
        }
    })
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';
    @import '@/styles/artdeco-patterns.scss';

    // ==================== BASE LAYOUT ====================

    .artdeco-stock-management {
        min-height: 100vh;
        padding: var(--artdeco-spacing-6);
        background: var(--artdeco-bg-global);
        color: var(--artdeco-fg-primary);
    }

    // ==================== PAGE HEADER ====================

    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--artdeco-spacing-8);
        padding-bottom: var(--artdeco-spacing-4);
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);

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
    }

    // ==================== STATS SECTION ====================

    .stats-section {
        margin-bottom: var(--artdeco-spacing-8);
    }

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    // ==================== MAIN TABS ====================

    .main-tabs {
        display: flex;
        gap: var(--artdeco-spacing-2);
        margin-bottom: var(--artdeco-spacing-6);
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
        padding-bottom: var(--artdeco-spacing-2);
    }

    .main-tab {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-2);
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-5);
        background: transparent;
        border: 1px solid transparent;
        color: var(--artdeco-fg-muted);
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-sm);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
        cursor: pointer;
        transition: all var(--artdeco-transition-base);

        .tab-icon {
            font-size: var(--artdeco-text-lg);
        }

        &:hover {
            color: var(--artdeco-gold-primary);
            border-color: rgba(212, 175, 55, 0.3);
        }

        &.active {
            color: var(--artdeco-gold-primary);
            border-color: var(--artdeco-gold-primary);
            background: rgba(212, 175, 55, 0.05);
        }
    }

    // ==================== TAB CONTENT ====================

    .tab-content {
        min-height: 500px;
    }

    .tab-panel {
        animation: fadeIn 0.3s ease-out;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    // ==================== WATCHLIST SECTION ====================

    .watchlist-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--artdeco-spacing-6);
    }

    .watchlist-tabs {
        display: flex;
        gap: var(--artdeco-spacing-2);
    }

    .watchlist-tab {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-2);
        padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.2);
        color: var(--artdeco-fg-secondary);
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-sm);
        cursor: pointer;
        transition: all var(--artdeco-transition-base);

        &:hover {
            border-color: var(--artdeco-gold-primary);
            color: var(--artdeco-gold-primary);
        }

        &.active {
            border-color: var(--artdeco-gold-primary);
            background: rgba(212, 175, 55, 0.1);
            color: var(--artdeco-gold-primary);
        }

        &.add-list {
            border-style: dashed;
        }

        .list-count {
            background: var(--artdeco-gold-primary);
            color: var(--artdeco-bg-global);
            padding: 2px 6px;
            border-radius: var(--artdeco-radius-none);
            font-size: var(--artdeco-text-xs);
            font-weight: 600;
        }
    }

    .watchlist-actions {
        display: flex;
        gap: var(--artdeco-spacing-3);
    }

    // ==================== STOCK CARDS GRID ====================

    .stock-cards-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    .stock-card {
        @include artdeco-stepped-corners(4px);

        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.15);
        padding: var(--artdeco-spacing-4);
        position: relative;
        transition: all var(--artdeco-transition-base);
        cursor: pointer;

        &:hover {
            border-color: var(--artdeco-gold-primary);
            box-shadow: var(--artdeco-glow-subtle);
            transform: translateY(-2px);
        }

        &.selected {
            border-color: var(--artdeco-gold-primary);
            background: rgba(212, 175, 55, 0.05);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: var(--artdeco-spacing-3);

            .stock-info {
                .stock-name {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-text-base);
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
        }

        .card-body {
            .price-section {
                display: flex;
                align-items: baseline;
                gap: var(--artdeco-spacing-2);
                margin-bottom: var(--artdeco-spacing-3);

                .current-price {
                    font-family: var(--artdeco-font-mono);
                    font-size: var(--artdeco-text-xl);
                    font-weight: 700;
                    color: var(--artdeco-fg-primary);
                }

                .price-change {
                    font-family: var(--artdeco-font-mono);
                    font-size: var(--artdeco-text-sm);
                    font-weight: 600;

                    &.rise {
                        color: var(--artdeco-up);
                    }

                    &.fall {
                        color: var(--artdeco-down);
                    }
                }
            }

            .indicators-overlay {
                display: flex;
                gap: var(--artdeco-spacing-3);

                .indicator {
                    font-family: var(--artdeco-font-mono);
                    font-size: var(--artdeco-text-xs);
                    padding: 2px 6px;
                    background: var(--artdeco-bg-base);
                    border-radius: var(--artdeco-radius-none);

                    &.overbought {
                        color: var(--artdeco-down);
                    }

                    &.oversold {
                        color: var(--artdeco-up);
                    }

                    &.neutral {
                        color: var(--artdeco-fg-muted);
                    }
                }
            }
        }

        .card-footer {
            margin-top: var(--artdeco-spacing-3);
            padding-top: var(--artdeco-spacing-3);
            border-top: 1px solid rgba(212, 175, 55, 0.1);

            .quick-actions {
                display: flex;
                justify-content: space-around;

                .action-btn {
                    background: transparent;
                    border: none;
                    font-size: var(--artdeco-text-lg);
                    cursor: pointer;
                    padding: var(--artdeco-spacing-2);
                    transition: all var(--artdeco-transition-base);

                    &:hover {
                        transform: scale(1.2);
                    }
                }
            }
        }

        .batch-checkbox {
            position: absolute;
            top: var(--artdeco-spacing-2);
            right: var(--artdeco-spacing-2);

            input {
                width: 18px;
                height: 18px;
                accent-color: var(--artdeco-gold-primary);
            }
        }
    }

    // ==================== EMPTY STATE ====================

    .empty-state {
        text-align: center;
        padding: var(--artdeco-spacing-12);
        background: var(--artdeco-bg-card);
        border: 1px dashed rgba(212, 175, 55, 0.3);
        border-radius: var(--artdeco-radius-none);

        .empty-icon {
            font-size: 64px;
            margin-bottom: var(--artdeco-spacing-4);
        }

        h3 {
            font-family: var(--artdeco-font-display);
            color: var(--artdeco-gold-primary);
            margin-bottom: var(--artdeco-spacing-2);
        }

        p {
            color: var(--artdeco-fg-muted);
            margin-bottom: var(--artdeco-spacing-6);
        }
    }

    // ==================== STRATEGY SECTION ====================

    .strategy-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--artdeco-spacing-6);
    }

    .strategy-tabs {
        display: flex;
        gap: var(--artdeco-spacing-2);
    }

    .strategy-tab {
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-5);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.2);
        color: var(--artdeco-fg-secondary);
        cursor: pointer;
        transition: all var(--artdeco-transition-base);

        &:hover,
        &.active {
            border-color: var(--artdeco-gold-primary);
            color: var(--artdeco-gold-primary);
        }

        &.active {
            background: rgba(212, 175, 55, 0.05);
        }

        .strategy-name {
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-sm);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
            display: block;
        }

        .strategy-count {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-xs);
            color: var(--artdeco-fg-muted);
        }
    }

    .strategy-actions {
        display: flex;
        gap: var(--artdeco-spacing-3);
    }

    .strategy-metrics {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    .metric-item {
        text-align: center;
        padding: var(--artdeco-spacing-4);
        background: var(--artdeco-bg-base);
        border: 1px solid rgba(212, 175, 55, 0.1);

        .metric-label {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            color: var(--artdeco-fg-muted);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
            margin-bottom: var(--artdeco-spacing-2);
        }

        .metric-value {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-xl);
            font-weight: 700;
            color: var(--artdeco-fg-primary);

            &.rise {
                color: var(--artdeco-up);
            }

            &.fall {
                color: var(--artdeco-down);
            }

            &.gold {
                color: var(--artdeco-gold-primary);
            }
        }
    }

    // ==================== RESULTS TABLE ====================

    .results-table {
        .table-header {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1.5fr 1fr 1fr 1fr 1fr;
            gap: var(--artdeco-spacing-3);
            padding: var(--artdeco-spacing-3);
            background: var(--artdeco-bg-base);
            border-bottom: 1px solid rgba(212, 175, 55, 0.2);

            .th-col {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-muted);
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
            }
        }

        .table-row {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1.5fr 1fr 1fr 1fr 1fr;
            gap: var(--artdeco-spacing-3);
            padding: var(--artdeco-spacing-3);
            border-bottom: 1px solid rgba(212, 175, 55, 0.1);
            transition: all var(--artdeco-transition-base);

            &:hover {
                background: rgba(212, 175, 55, 0.03);
            }

            .td-col {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-sm);
                display: flex;
                align-items: center;

                &.stock-cell {
                    flex-direction: column;
                    align-items: flex-start;

                    .stock-name {
                        font-family: var(--artdeco-font-display);
                        font-weight: 600;
                        color: var(--artdeco-fg-primary);
                    }

                    .stock-code {
                        font-family: var(--artdeco-font-mono);
                        font-size: var(--artdeco-text-xs);
                        color: var(--artdeco-fg-muted);
                    }
                }

                &.score-cell {
                    flex-direction: column;
                    align-items: flex-start;

                    .score-bar {
                        width: 80px;
                        height: 6px;
                        background: var(--artdeco-bg-base);
                        border-radius: var(--artdeco-radius-none);
                        overflow: hidden;
                        margin-bottom: 2px;

                        .score-fill {
                            height: 100%;
                            background: linear-gradient(90deg, var(--artdeco-gold-primary), var(--artdeco-gold-hover));
                            border-radius: var(--artdeco-radius-none);
                        }
                    }

                    .score-value {
                        font-weight: 600;
                        color: var(--artdeco-gold-primary);
                    }
                }

                &.actions {
                    gap: var(--artdeco-spacing-2);

                    .action-icon {
                        background: transparent;
                        border: none;
                        cursor: pointer;
                        font-size: var(--artdeco-text-base);
                        padding: 2px 6px;
                        transition: all var(--artdeco-transition-base);

                        &:hover {
                            transform: scale(1.2);
                        }
                    }
                }

                &.rise {
                    color: var(--artdeco-up);
                }

                &.fall {
                    color: var(--artdeco-down);
                }
            }
        }
    }

    // ==================== INDUSTRY SECTION ====================

    .industry-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--artdeco-spacing-6);
    }

    .industry-tabs {
        display: flex;
        gap: var(--artdeco-spacing-2);
    }

    .industry-tab {
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-6);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.2);
        color: var(--artdeco-fg-secondary);
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-sm);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
        cursor: pointer;
        transition: all var(--artdeco-transition-base);

        &:hover,
        &.active {
            border-color: var(--artdeco-gold-primary);
            color: var(--artdeco-gold-primary);
        }

        &.active {
            background: rgba(212, 175, 55, 0.05);
        }
    }

    .filter-controls {
        display: flex;
        gap: var(--artdeco-spacing-3);
    }

    .industry-content,
    .concept-content {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--artdeco-spacing-6);
    }

    .industry-heatmap {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-3);
    }

    .sector-item {
        display: grid;
        grid-template-columns: 1fr 100px 120px 60px;
        align-items: center;
        gap: var(--artdeco-spacing-3);
        padding: var(--artdeco-spacing-3);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        cursor: pointer;
        transition: all var(--artdeco-transition-base);

        &:hover {
            border-color: var(--artdeco-gold-primary);
        }

        .sector-name {
            font-family: var(--artdeco-font-display);
            font-weight: 600;
            color: var(--artdeco-fg-primary);
        }

        .sector-change {
            font-family: var(--artdeco-font-mono);
            font-weight: 600;

            &.rise {
                color: var(--artdeco-up);
            }

            &.fall {
                color: var(--artdeco-down);
            }
        }

        .sector-bar {
            height: 8px;
            background: var(--artdeco-bg-base);
            border-radius: var(--artdeco-radius-none);
            overflow: hidden;

            .bar-fill {
                height: 100%;
                border-radius: var(--artdeco-radius-none);

                &.rise {
                    background: var(--artdeco-up);
                }

                &.fall {
                    background: var(--artdeco-down);
                }
            }
        }

        .sector-stocks {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-xs);
            color: var(--artdeco-fg-muted);
        }
    }

    .concept-heatmap {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-3);
    }

    .concept-item {
        display: grid;
        grid-template-columns: 1fr 100px 80px 80px;
        align-items: center;
        gap: var(--artdeco-spacing-3);
        padding: var(--artdeco-spacing-3);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        cursor: pointer;
        transition: all var(--artdeco-transition-base);

        &:hover {
            border-color: var(--artdeco-gold-primary);
        }

        .concept-name {
            font-family: var(--artdeco-font-display);
            font-weight: 600;
            color: var(--artdeco-fg-primary);
        }

        .concept-change {
            font-family: var(--artdeco-font-mono);
            font-weight: 600;

            &.rise {
                color: var(--artdeco-up);
            }

            &.fall {
                color: var(--artdeco-down);
            }
        }

        .concept-count {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-xs);
            color: var(--artdeco-fg-muted);
        }

        .concept-hot {
            font-size: var(--artdeco-text-sm);

            &.hot-high {
                color: #ff5252;
            }

            &.hot-medium {
                color: var(--artdeco-gold-primary);
            }

            &.hot-low {
                color: var(--artdeco-fg-muted);
            }
        }
    }

    .detail-content {
        .detail-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-4);

            h3 {
                font-family: var(--artdeco-font-display);
                font-size: var(--artdeco-text-xl);
                color: var(--artdeco-gold-primary);
                margin: 0;
            }
        }

        .detail-metrics {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: var(--artdeco-spacing-4);
            margin-bottom: var(--artdeco-spacing-6);

            .metric {
                text-align: center;
                padding: var(--artdeco-spacing-3);
                background: var(--artdeco-bg-base);

                .label {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-text-sm);
                    color: var(--artdeco-fg-muted);
                    display: block;
                    margin-bottom: var(--artdeco-spacing-1);
                }

                .value {
                    font-family: var(--artdeco-font-mono);
                    font-size: var(--artdeco-text-lg);
                    font-weight: 600;

                    &.rise {
                        color: var(--artdeco-up);
                    }

                    &.fall {
                        color: var(--artdeco-down);
                    }

                    &.gold {
                        color: var(--artdeco-gold-primary);
                    }
                }
            }
        }

        .rotation-signal {
            margin-bottom: var(--artdeco-spacing-6);

            h4 {
                font-family: var(--artdeco-font-display);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-gold-primary);
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
                margin-bottom: var(--artdeco-spacing-3);
            }

            .signal-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: var(--artdeco-spacing-2) 0;
                border-bottom: 1px solid rgba(212, 175, 55, 0.1);

                .signal-label {
                    font-family: var(--artdeco-font-body);
                    color: var(--artdeco-fg-secondary);
                }
            }
        }

        .industry-stocks,
        .concept-stocks {
            h4 {
                font-family: var(--artdeco-font-display);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-gold-primary);
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
                margin-bottom: var(--artdeco-spacing-3);
            }

            .stocks-grid,
            .stocks-list {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
                gap: var(--artdeco-spacing-2);
            }

            .industry-stock-item {
                padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
                background: var(--artdeco-bg-base);
                border: 1px solid rgba(212, 175, 55, 0.1);
                cursor: pointer;
                transition: all var(--artdeco-transition-base);

                &:hover {
                    border-color: var(--artdeco-gold-primary);
                }

                .stock-name {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-text-xs);
                    color: var(--artdeco-fg-primary);
                    display: block;
                }

                .stock-change {
                    font-family: var(--artdeco-font-mono);
                    font-size: var(--artdeco-text-xs);

                    &.rise {
                        color: var(--artdeco-up);
                    }

                    &.fall {
                        color: var(--artdeco-down);
                    }
                }
            }
        }
    }

    .concept-stock-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
        background: var(--artdeco-bg-base);
        border: 1px solid rgba(212, 175, 55, 0.1);
        cursor: pointer;
        transition: all var(--artdeco-transition-base);

        &:hover {
            border-color: var(--artdeco-gold-primary);
        }

        .stock-main {
            .stock-name {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-primary);
            }

            .stock-code {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-xs);
                color: var(--artdeco-fg-muted);
                margin-left: var(--artdeco-spacing-2);
            }
        }

        .stock-price {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-sm);
            color: var(--artdeco-fg-secondary);
        }

        .stock-change {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-sm);
            font-weight: 600;

            &.rise {
                color: var(--artdeco-up);
            }

            &.fall {
                color: var(--artdeco-down);
            }
        }
    }

    .empty-detail {
        text-align: center;
        padding: var(--artdeco-spacing-8);
        color: var(--artdeco-fg-muted);
    }

    // ==================== BATCH OPERATIONS SECTION ====================

    .batch-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--artdeco-spacing-6);
        padding: var(--artdeco-spacing-4);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.2);
    }

    .batch-info {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-4);

        .selected-count {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-base);
            color: var(--artdeco-gold-primary);
        }
    }

    .batch-actions {
        display: flex;
        gap: var(--artdeco-spacing-3);
    }

    .batch-filter-bar {
        display: flex;
        gap: var(--artdeco-spacing-3);
        margin-bottom: var(--artdeco-spacing-4);
    }

    .batch-stock-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: var(--artdeco-spacing-3);
    }

    .batch-stock-item {
        padding: var(--artdeco-spacing-3);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        cursor: pointer;
        transition: all var(--artdeco-transition-base);

        &:hover {
            border-color: var(--artdeco-gold-primary);
        }

        &.selected {
            border-color: var(--artdeco-gold-primary);
            background: rgba(212, 175, 55, 0.05);
        }

        .stock-name {
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-sm);
            font-weight: 600;
            color: var(--artdeco-fg-primary);
            display: block;
            margin-bottom: 2px;
        }

        .stock-code {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-xs);
            color: var(--artdeco-fg-muted);
        }

        .stock-change {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-sm);
            font-weight: 600;

            &.rise {
                color: var(--artdeco-up);
            }

            &.fall {
                color: var(--artdeco-down);
            }
        }
    }

    .batch-alert-card {
        margin-top: var(--artdeco-spacing-6);
    }

    .alert-config-form {
        .form-row {
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-4);
            margin-bottom: var(--artdeco-spacing-4);

            label {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-secondary);
                min-width: 100px;
            }

            .checkbox-group {
                display: flex;
                gap: var(--artdeco-spacing-4);

                .checkbox-item {
                    display: flex;
                    align-items: center;
                    gap: var(--artdeco-spacing-2);
                    cursor: pointer;

                    input {
                        accent-color: var(--artdeco-gold-primary);
                    }

                    span {
                        font-family: var(--artdeco-font-body);
                        font-size: var(--artdeco-text-sm);
                    }
                }
            }

            .unit {
                font-family: var(--artdeco-font-body);
                color: var(--artdeco-fg-muted);
            }
        }
    }

    // ==================== CARDS VIEW SECTION ====================

    .cards-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--artdeco-spacing-6);
    }

    .view-options {
        :deep(.artdeco-button) {
            &.active {
                background: var(--artdeco-gold-primary);
                color: var(--artdeco-bg-global);
            }
        }
    }

    .cards-filter {
        display: flex;
        gap: var(--artdeco-spacing-3);
    }

    .cards-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    .display-card {
        @include artdeco-stepped-corners(4px);

        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.15);
        overflow: hidden;
        transition: all var(--artdeco-transition-base);
        cursor: pointer;

        &:hover {
            border-color: var(--artdeco-gold-primary);
            box-shadow: var(--artdeco-glow-subtle);
            transform: translateY(-2px);
        }

        .card-top-bar {
            height: 4px;
            background: linear-gradient(90deg, var(--artdeco-gold-primary), var(--artdeco-gold-hover));
        }

        .card-main {
            padding: var(--artdeco-spacing-4);

            .card-header {
                margin-bottom: var(--artdeco-spacing-3);

                .stock-name {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-text-lg);
                    font-weight: 600;
                    color: var(--artdeco-fg-primary);
                }

                .stock-code {
                    font-family: var(--artdeco-font-mono);
                    font-size: var(--artdeco-text-sm);
                    color: var(--artdeco-fg-muted);
                }
            }

            .card-price {
                margin-bottom: var(--artdeco-spacing-4);

                .price {
                    font-family: var(--artdeco-font-mono);
                    font-size: var(--artdeco-text-2xl);
                    font-weight: 700;
                    color: var(--artdeco-fg-primary);
                    margin-right: var(--artdeco-spacing-2);
                }

                .change {
                    font-family: var(--artdeco-font-mono);
                    font-size: var(--artdeco-text-base);
                    font-weight: 600;

                    &.rise {
                        color: var(--artdeco-up);
                    }

                    &.fall {
                        color: var(--artdeco-down);
                    }
                }
            }

            .card-indicators {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: var(--artdeco-spacing-2);
                margin-bottom: var(--artdeco-spacing-3);

                .indicator-row {
                    text-align: center;

                    .label {
                        font-family: var(--artdeco-font-body);
                        font-size: var(--artdeco-text-xs);
                        color: var(--artdeco-fg-muted);
                        display: block;
                    }

                    .value {
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
            }

            .card-tags {
                display: flex;
                flex-wrap: wrap;
                gap: var(--artdeco-spacing-1);
            }
        }

        .card-actions {
            display: flex;
            gap: var(--artdeco-spacing-2);
            padding: var(--artdeco-spacing-3);
            background: var(--artdeco-bg-base);
            border-top: 1px solid rgba(212, 175, 55, 0.1);

            .card-action-btn {
                flex: 1;
                padding: var(--artdeco-spacing-2);
                background: transparent;
                border: 1px solid rgba(212, 175, 55, 0.3);
                color: var(--artdeco-gold-primary);
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-xs);
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
                cursor: pointer;
                transition: all var(--artdeco-transition-base);

                &:hover {
                    background: var(--artdeco-gold-primary);
                    color: var(--artdeco-bg-global);
                }
            }
        }
    }

    .cards-list {
        .list-card-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: var(--artdeco-spacing-4);
            background: var(--artdeco-bg-card);
            border: 1px solid rgba(212, 175, 55, 0.1);
            margin-bottom: var(--artdeco-spacing-2);
            cursor: pointer;
            transition: all var(--artdeco-transition-base);

            &:hover {
                border-color: var(--artdeco-gold-primary);
            }

            .row-main {
                flex: 1;

                .stock-identity {
                    margin-bottom: var(--artdeco-spacing-2);

                    .stock-name {
                        font-family: var(--artdeco-font-display);
                        font-size: var(--artdeco-text-base);
                        font-weight: 600;
                        color: var(--artdeco-fg-primary);
                    }

                    .stock-code {
                        font-family: var(--artdeco-font-mono);
                        font-size: var(--artdeco-text-sm);
                        color: var(--artdeco-fg-muted);
                        margin-left: var(--artdeco-spacing-2);
                    }
                }

                .stock-price-info {
                    margin-bottom: var(--artdeco-spacing-2);

                    .price {
                        font-family: var(--artdeco-font-mono);
                        font-size: var(--artdeco-text-lg);
                        font-weight: 700;
                        color: var(--artdeco-fg-primary);
                        margin-right: var(--artdeco-spacing-2);
                    }

                    .change {
                        font-family: var(--artdeco-font-mono);
                        font-size: var(--artdeco-text-sm);
                        font-weight: 600;

                        &.rise {
                            color: var(--artdeco-up);
                        }

                        &.fall {
                            color: var(--artdeco-down);
                        }
                    }
                }

                .stock-indicators-list {
                    display: flex;
                    gap: var(--artdeco-spacing-4);

                    .indi {
                        font-family: var(--artdeco-font-mono);
                        font-size: var(--artdeco-text-xs);
                        color: var(--artdeco-fg-muted);
                    }
                }

                .stock-tags {
                    margin-top: var(--artdeco-spacing-2);
                    display: flex;
                    gap: var(--artdeco-spacing-1);
                }
            }

            .row-actions {
                display: flex;
                gap: var(--artdeco-spacing-2);

                .row-action-btn {
                    padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
                    background: transparent;
                    border: 1px solid rgba(212, 175, 55, 0.3);
                    color: var(--artdeco-gold-primary);
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-text-xs);
                    text-transform: uppercase;
                    cursor: pointer;
                    transition: all var(--artdeco-transition-base);

                    &:hover {
                        background: var(--artdeco-gold-primary);
                        color: var(--artdeco-bg-global);
                    }
                }
            }
        }
    }

    // ==================== DIALOGS ====================

    .dialog-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }

    .dialog {
        @include artdeco-stepped-corners(8px);

        background: var(--artdeco-bg-card);
        border: 1px solid var(--artdeco-gold-primary);
        width: 90%;
        max-width: 500px;
        max-height: 80vh;
        overflow: hidden;

        .dialog-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: var(--artdeco-spacing-4);
            border-bottom: 1px solid rgba(212, 175, 55, 0.2);

            h3 {
                font-family: var(--artdeco-font-display);
                font-size: var(--artdeco-text-lg);
                color: var(--artdeco-gold-primary);
                margin: 0;
            }

            .close-btn {
                background: transparent;
                border: none;
                font-size: 24px;
                color: var(--artdeco-fg-muted);
                cursor: pointer;

                &:hover {
                    color: var(--artdeco-gold-primary);
                }
            }
        }

        .dialog-body {
            padding: var(--artdeco-spacing-4);
            max-height: 60vh;
            overflow-y: auto;

            .search-results {
                margin-top: var(--artdeco-spacing-4);

                .search-result-item {
                    display: flex;
                    justify-content: space-between;
                    padding: var(--artdeco-spacing-3);
                    background: var(--artdeco-bg-base);
                    border: 1px solid rgba(212, 175, 55, 0.1);
                    margin-bottom: var(--artdeco-spacing-2);
                    cursor: pointer;
                    transition: all var(--artdeco-transition-base);

                    &:hover {
                        border-color: var(--artdeco-gold-primary);
                    }

                    .stock-name {
                        font-family: var(--artdeco-font-body);
                        color: var(--artdeco-fg-primary);
                    }

                    .stock-code {
                        font-family: var(--artdeco-font-mono);
                        color: var(--artdeco-fg-muted);
                    }
                }
            }

            .import-options {
                display: flex;
                gap: var(--artdeco-spacing-6);
                margin-bottom: var(--artdeco-spacing-4);

                .import-option {
                    display: flex;
                    align-items: center;
                    gap: var(--artdeco-spacing-2);
                    cursor: pointer;

                    input {
                        accent-color: var(--artdeco-gold-primary);
                    }
                }
            }

            .text-import {
                textarea {
                    width: 100%;
                    padding: var(--artdeco-spacing-3);
                    background: var(--artdeco-bg-base);
                    border: 1px solid rgba(212, 175, 55, 0.2);
                    color: var(--artdeco-fg-primary);
                    font-family: var(--artdeco-font-mono);
                    font-size: var(--artdeco-text-sm);
                    resize: vertical;

                    &:focus {
                        outline: none;
                        border-color: var(--artdeco-gold-primary);
                    }
                }
            }

            .dialog-actions {
                display: flex;
                justify-content: flex-end;
                gap: var(--artdeco-spacing-3);
                margin-top: var(--artdeco-spacing-6);
            }
        }
    }

    // ============================================
    //   DESIGN NOTE - 设计说明
    //   本项目仅支持桌面端，不包含移动端响应式代码
    // ============================================
</style>
