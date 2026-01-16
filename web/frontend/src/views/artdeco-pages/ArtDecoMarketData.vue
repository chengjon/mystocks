<template>
    <div class="artdeco-market-data">
        <!-- Page Header -->
        <div class="page-header">
            <div class="header-content">
                <h1 class="page-title">市场数据分析中心</h1>
                <p class="page-subtitle">深度分析市场资金动向，挖掘投资机会</p>
            </div>
            <div class="header-actions">
                <div class="time-display">
                    <span class="time-label">数据更新</span>
                    <span class="time-value">{{ lastUpdate }}</span>
                </div>
                <ArtDecoButton variant="outline" size="sm" @click="refreshData">刷新数据</ArtDecoButton>
            </div>
        </div>

        <!-- Main Navigation Tabs -->
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
            <!-- 资金流向分析 -->
            <div v-if="activeTab === 'fund-flow'" class="tab-panel">
                <div class="fund-overview">
                    <ArtDecoStatCard
                        label="沪股通净流入"
                        :value="fundData.shanghai.amount"
                        :change="fundData.shanghai.change"
                        change-percent
                        variant="gold"
                    />
                    <ArtDecoStatCard
                        label="深股通净流入"
                        :value="fundData.shenzhen.amount"
                        :change="fundData.shenzhen.change"
                        change-percent
                        variant="gold"
                    />
                    <ArtDecoStatCard
                        label="北向资金总额"
                        :value="fundData.north.amount"
                        :change="fundData.north.change"
                        change-percent
                        :variant="fundData.north.change > 0 ? 'rise' : 'fall'"
                    />
                    <ArtDecoStatCard
                        label="主力净流入"
                        :value="fundData.main.amount"
                        :change="fundData.main.change"
                        change-percent
                        variant="gold"
                    />
                </div>

                <ArtDecoCard title="近30日资金流向趋势" hoverable class="fund-chart-card">
                    <div class="chart-placeholder">
                        <div class="chart-title">资金流向趋势图</div>
                        <div class="chart-area">
                            <svg width="100%" height="200" viewBox="0 0 800 200" preserveAspectRatio="none">
                                <defs>
                                    <linearGradient id="fundPositive" x1="0%" y1="0%" x2="0%" y2="100%">
                                        <stop offset="0%" style="stop-color: #e74c3c; stop-opacity: 0.6" />
                                        <stop offset="100%" style="stop-color: #e74c3c; stop-opacity: 0.1" />
                                    </linearGradient>
                                    <linearGradient id="fundNegative" x1="0%" y1="0%" x2="0%" y2="100%">
                                        <stop offset="0%" style="stop-color: #27ae60; stop-opacity: 0.6" />
                                        <stop offset="100%" style="stop-color: #27ae60; stop-opacity: 0.1" />
                                    </linearGradient>
                                </defs>
                                <!-- 模拟资金流向柱状图 -->
                                <rect
                                    x="20"
                                    y="60"
                                    width="25"
                                    height="80"
                                    fill="url(#fundPositive)"
                                    stroke="#E74C3C"
                                    stroke-width="1"
                                />
                                <rect
                                    x="55"
                                    y="40"
                                    width="25"
                                    height="100"
                                    fill="url(#fundPositive)"
                                    stroke="#E74C3C"
                                    stroke-width="1"
                                />
                                <rect
                                    x="90"
                                    y="80"
                                    width="25"
                                    height="60"
                                    fill="url(#fundPositive)"
                                    stroke="#E74C3C"
                                    stroke-width="1"
                                />
                                <rect
                                    x="125"
                                    y="30"
                                    width="25"
                                    height="110"
                                    fill="url(#fundPositive)"
                                    stroke="#E74C3C"
                                    stroke-width="1"
                                />
                                <rect
                                    x="160"
                                    y="70"
                                    width="25"
                                    height="70"
                                    fill="url(#fundPositive)"
                                    stroke="#E74C3C"
                                    stroke-width="1"
                                />
                                <!-- 更多柱状图数据... -->
                            </svg>
                        </div>
                    </div>
                </ArtDecoCard>

                <ArtDecoCard title="个股资金流向排行" hoverable class="fund-ranking-card">
                    <div class="ranking-controls">
                        <div class="time-filters">
                            <button
                                v-for="filter in timeFilters"
                                :key="filter.key"
                                class="filter-btn"
                                :class="{ active: activeTimeFilter === filter.key }"
                                @click="activeTimeFilter = filter.key"
                            >
                                {{ filter.label }}
                            </button>
                        </div>
                        <ArtDecoSelect
                            v-model="rankingType"
                            :options="rankingOptions"
                            placeholder="选择排序方式"
                            class="ranking-select"
                        />
                    </div>

                    <div class="ranking-table">
                        <div class="table-header">
                            <div class="col-rank">排名</div>
                            <div class="col-stock">股票信息</div>
                            <div class="col-price">最新价</div>
                            <div class="col-change">涨跌幅</div>
                            <div class="col-flow">资金流入</div>
                            <div class="col-main">主力净额</div>
                        </div>
                        <div class="table-body">
                            <div class="table-row" v-for="(stock, index) in stockRanking" :key="stock.code">
                                <div class="col-rank">{{ index + 1 }}</div>
                                <div class="col-stock">
                                    <div class="stock-name">{{ stock.name }}</div>
                                    <div class="stock-code">{{ stock.code }}</div>
                                </div>
                                <div class="col-price">¥{{ stock.price }}</div>
                                <div class="col-change" :class="stock.change >= 0 ? 'rise' : 'fall'">
                                    {{ stock.change >= 0 ? '+' : '' }}{{ stock.change }}%
                                </div>
                                <div class="col-flow rise">+{{ stock.inflow }}亿</div>
                                <div class="col-main rise">+{{ stock.mainForce }}亿</div>
                            </div>
                        </div>
                    </div>
                </ArtDecoCard>
            </div>

            <!-- ETF分析 -->
            <div v-if="activeTab === 'etf'" class="tab-panel">
                <div class="etf-overview">
                    <ArtDecoStatCard label="ETF总成交额" value="2,345亿" change="18.5" change-percent variant="gold" />
                    <ArtDecoStatCard label="杠杆ETF成交" value="856亿" change="25.3" change-percent variant="rise" />
                    <ArtDecoStatCard label="沪深300ETF" value="4.25%" change="1.2" change-percent :variant="'rise'" />
                    <ArtDecoStatCard label="创业板ETF" value="-2.1%" change="-0.8" change-percent variant="fall" />
                </div>

                <ArtDecoCard title="热门ETF排行" hoverable class="etf-ranking-card">
                    <div class="etf-list">
                        <div class="etf-item" v-for="etf in etfRanking" :key="etf.code">
                            <div class="etf-info">
                                <div class="etf-name">{{ etf.name }}</div>
                                <div class="etf-code">{{ etf.code }}</div>
                                <div class="etf-type">{{ etf.type }}</div>
                            </div>
                            <div class="etf-performance">
                                <div class="etf-price">¥{{ etf.price }}</div>
                                <div class="etf-change" :class="etf.change >= 0 ? 'rise' : 'fall'">
                                    {{ etf.change >= 0 ? '+' : '' }}{{ etf.change }}%
                                </div>
                                <div class="etf-volume">{{ etf.volume }}亿</div>
                            </div>
                        </div>
                    </div>
                </ArtDecoCard>
            </div>

            <!-- 概念板块 -->
            <div v-if="activeTab === 'concepts'" class="tab-panel">
                <ArtDecoCard title="概念板块热度排行" hoverable class="concepts-card">
                    <div class="concepts-heat-map">
                        <div class="concept-item" v-for="concept in conceptRanking" :key="concept.name">
                            <div class="concept-info">
                                <div class="concept-name">{{ concept.name }}</div>
                                <div class="concept-stocks">{{ concept.stockCount }}只成分股</div>
                            </div>
                            <div class="concept-performance">
                                <div class="concept-change" :class="concept.change >= 0 ? 'rise' : 'fall'">
                                    {{ concept.change >= 0 ? '+' : '' }}{{ concept.change }}%
                                </div>
                                <div class="concept-heat">
                                    <div class="heat-bar">
                                        <div class="heat-fill" :style="{ width: concept.heat + '%' }"></div>
                                    </div>
                                    <div class="heat-value">{{ concept.heat }}°</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </ArtDecoCard>

                <ArtDecoCard title="热门概念详情" hoverable class="concept-detail-card">
                    <div class="concept-detail" v-if="selectedConcept">
                        <div class="detail-header">
                            <h3>{{ selectedConcept.name }}</h3>
                            <div class="detail-stats">
                                <span>成分股: {{ selectedConcept.stockCount }}只</span>
                                <span>
                                    平均涨跌幅:
                                    <span :class="selectedConcept.avgChange >= 0 ? 'rise' : 'fall'">
                                        {{ selectedConcept.avgChange >= 0 ? '+' : '' }}{{ selectedConcept.avgChange }}%
                                    </span>
                                </span>
                            </div>
                        </div>
                        <div class="top-stocks">
                            <h4>涨幅前五</h4>
                            <div class="stock-list">
                                <div class="stock-item" v-for="stock in selectedConcept.topStocks" :key="stock.code">
                                    <div class="stock-name">{{ stock.name }}</div>
                                    <div class="stock-code">{{ stock.code }}</div>
                                    <div class="stock-change rise">+{{ stock.change }}%</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div v-else class="no-selection">
                        <p>选择左侧概念板块查看详情</p>
                    </div>
                </ArtDecoCard>
            </div>

            <!-- 龙虎榜 -->
            <div v-if="activeTab === 'lhb'" class="tab-panel">
                <ArtDecoCard title="龙虎榜数据" hoverable class="lhb-card">
                    <div class="lhb-controls">
                        <ArtDecoSelect v-model="lhbDate" :options="dateOptions" placeholder="选择日期" />
                        <div class="lhb-filters">
                            <button class="filter-btn active">买入榜</button>
                            <button class="filter-btn">卖出榜</button>
                            <button class="filter-btn">机构榜</button>
                        </div>
                    </div>

                    <div class="lhb-table">
                        <div class="table-header">
                            <div class="col-rank">排名</div>
                            <div class="col-stock">股票信息</div>
                            <div class="col-price">收盘价</div>
                            <div class="col-change">涨跌幅</div>
                            <div class="col-buy">买入金额</div>
                            <div class="col-sell">卖出金额</div>
                            <div class="col-net">净买入</div>
                        </div>
                        <div class="table-body">
                            <div class="table-row" v-for="(item, index) in lhbData" :key="item.code">
                                <div class="col-rank">{{ index + 1 }}</div>
                                <div class="col-stock">
                                    <div class="stock-name">{{ item.name }}</div>
                                    <div class="stock-code">{{ item.code }}</div>
                                </div>
                                <div class="col-price">¥{{ item.price }}</div>
                                <div class="col-change rise">+{{ item.change }}%</div>
                                <div class="col-buy">{{ item.buyAmount }}亿</div>
                                <div class="col-sell">{{ item.sellAmount }}亿</div>
                                <div class="col-net rise">{{ item.netBuy }}亿</div>
                            </div>
                        </div>
                    </div>
                </ArtDecoCard>
            </div>

            <!-- 竞价抢筹 -->
            <!-- 数据质量监控 -->
            <div v-if="activeTab === 'data-quality'" class="tab-panel">
                <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                    <div class="quality-overview">
                        <ArtDecoStatCard
                            label="数据完整性"
                            :value="qualityData.integrity + '%'"
                            change="0.2"
                            change-percent
                            variant="gold"
                        />
                        <ArtDecoStatCard
                            label="数据准确性"
                            :value="qualityData.accuracy + '%'"
                            change="-0.1"
                            change-percent
                            variant="gold"
                        />
                        <ArtDecoStatCard
                            label="更新及时性"
                            :value="qualityData.timeliness + '%'"
                            change="1.5"
                            change-percent
                            :variant="'rise'"
                        />
                        <ArtDecoStatCard
                            label="数据一致性"
                            :value="qualityData.consistency + '%'"
                            change="0.8"
                            change-percent
                            variant="gold"
                        />
                    </div>

                    <div class="quality-details">
                        <div class="quality-section">
                            <h4>数据源健康状态</h4>
                            <div class="data-sources">
                                <div class="source-item" v-for="source in dataSources" :key="source.name">
                                    <div class="source-info">
                                        <div class="source-name">{{ source.name }}</div>
                                        <div class="source-type">{{ source.type }}</div>
                                    </div>
                                    <div class="source-status" :class="source.status">
                                        {{ source.statusText }}
                                    </div>
                                    <div class="source-quality">{{ source.quality }}%</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </ArtDecoCard>
            </div>
            <div v-if="activeTab === 'auction'" class="tab-panel">
                <!-- 数据质量监控 -->
                <div v-if="activeTab === 'data-quality'" class="tab-panel">
                    <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                        <div class="quality-overview">
                            <ArtDecoStatCard
                                label="数据完整性"
                                :value="qualityData.integrity + '%'"
                                change="0.2"
                                change-percent
                                variant="gold"
                            />
                            <ArtDecoStatCard
                                label="数据准确性"
                                :value="qualityData.accuracy + '%'"
                                change="-0.1"
                                change-percent
                                variant="gold"
                            />
                            <ArtDecoStatCard
                                label="更新及时性"
                                :value="qualityData.timeliness + '%'"
                                change="1.5"
                                change-percent
                                :variant="'rise'"
                            />
                            <ArtDecoStatCard
                                label="数据一致性"
                                :value="qualityData.consistency + '%'"
                                change="0.8"
                                change-percent
                                variant="gold"
                            />
                        </div>

                        <div class="quality-details">
                            <div class="quality-section">
                                <h4>数据源健康状态</h4>
                                <div class="data-sources">
                                    <div class="source-item" v-for="source in dataSources" :key="source.name">
                                        <div class="source-info">
                                            <div class="source-name">{{ source.name }}</div>
                                            <div class="source-type">{{ source.type }}</div>
                                        </div>
                                        <div class="source-status" :class="source.status">
                                            {{ source.statusText }}
                                        </div>
                                        <div class="source-quality">{{ source.quality }}%</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </ArtDecoCard>
                </div>
                <ArtDecoCard title="竞价抢筹分析" hoverable class="auction-card">
                    <!-- 数据质量监控 -->
                    <div v-if="activeTab === 'data-quality'" class="tab-panel">
                        <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                            <div class="quality-overview">
                                <ArtDecoStatCard
                                    label="数据完整性"
                                    :value="qualityData.integrity + '%'"
                                    change="0.2"
                                    change-percent
                                    variant="gold"
                                />
                                <ArtDecoStatCard
                                    label="数据准确性"
                                    :value="qualityData.accuracy + '%'"
                                    change="-0.1"
                                    change-percent
                                    variant="gold"
                                />
                                <ArtDecoStatCard
                                    label="更新及时性"
                                    :value="qualityData.timeliness + '%'"
                                    change="1.5"
                                    change-percent
                                    :variant="'rise'"
                                />
                                <ArtDecoStatCard
                                    label="数据一致性"
                                    :value="qualityData.consistency + '%'"
                                    change="0.8"
                                    change-percent
                                    variant="gold"
                                />
                            </div>

                            <div class="quality-details">
                                <div class="quality-section">
                                    <h4>数据源健康状态</h4>
                                    <div class="data-sources">
                                        <div class="source-item" v-for="source in dataSources" :key="source.name">
                                            <div class="source-info">
                                                <div class="source-name">{{ source.name }}</div>
                                                <div class="source-type">{{ source.type }}</div>
                                            </div>
                                            <div class="source-status" :class="source.status">
                                                {{ source.statusText }}
                                            </div>
                                            <div class="source-quality">{{ source.quality }}%</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </ArtDecoCard>
                    </div>
                    <div class="auction-overview">
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        label="竞价成交金额"
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        value="1,256亿"
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        change="12.3"
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        change-percent
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        variant="gold"
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        />
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        label="涨停家数"
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        value="68家"
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        change="15"
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        change-percent
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        variant="rise"
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        />
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        label="炸板率"
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        value="23.5%"
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        change="-5.2"
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        change-percent
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        variant="fall"
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        />
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        label="平均涨幅"
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        value="8.7%"
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        change="2.1"
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        change-percent
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        variant="gold"
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                        />
                        <!-- 数据质量监控 -->
                        <div v-if="activeTab === 'data-quality'" class="tab-panel">
                            <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                                <div class="quality-overview">
                                    <ArtDecoStatCard
                                        label="数据完整性"
                                        :value="qualityData.integrity + '%'"
                                        change="0.2"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="数据准确性"
                                        :value="qualityData.accuracy + '%'"
                                        change="-0.1"
                                        change-percent
                                        variant="gold"
                                    />
                                    <ArtDecoStatCard
                                        label="更新及时性"
                                        :value="qualityData.timeliness + '%'"
                                        change="1.5"
                                        change-percent
                                        :variant="'rise'"
                                    />
                                    <ArtDecoStatCard
                                        label="数据一致性"
                                        :value="qualityData.consistency + '%'"
                                        change="0.8"
                                        change-percent
                                        variant="gold"
                                    />
                                </div>

                                <div class="quality-details">
                                    <div class="quality-section">
                                        <h4>数据源健康状态</h4>
                                        <div class="data-sources">
                                            <div class="source-item" v-for="source in dataSources" :key="source.name">
                                                <div class="source-info">
                                                    <div class="source-name">{{ source.name }}</div>
                                                    <div class="source-type">{{ source.type }}</div>
                                                </div>
                                                <div class="source-status" :class="source.status">
                                                    {{ source.statusText }}
                                                </div>
                                                <div class="source-quality">{{ source.quality }}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </ArtDecoCard>
                        </div>
                    </div>
                    <!-- 数据质量监控 -->
                    <div v-if="activeTab === 'data-quality'" class="tab-panel">
                        <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
                            <div class="quality-overview">
                                <ArtDecoStatCard
                                    label="数据完整性"
                                    :value="qualityData.integrity + '%'"
                                    change="0.2"
                                    change-percent
                                    variant="gold"
                                />
                                <ArtDecoStatCard
                                    label="数据准确性"
                                    :value="qualityData.accuracy + '%'"
                                    change="-0.1"
                                    change-percent
                                    variant="gold"
                                />
                                <ArtDecoStatCard
                                    label="更新及时性"
                                    :value="qualityData.timeliness + '%'"
                                    change="1.5"
                                    change-percent
                                    :variant="'rise'"
                                />
                                <ArtDecoStatCard
                                    label="数据一致性"
                                    :value="qualityData.consistency + '%'"
                                    change="0.8"
                                    change-percent
                                    variant="gold"
                                />
                            </div>

                            <div class="quality-details">
                                <div class="quality-section">
                                    <h4>数据源健康状态</h4>
                                    <div class="data-sources">
                                        <div class="source-item" v-for="source in dataSources" :key="source.name">
                                            <div class="source-info">
                                                <div class="source-name">{{ source.name }}</div>
                                                <div class="source-type">{{ source.type }}</div>
                                            </div>
                                            <div class="source-status" :class="source.status">
                                                {{ source.statusText }}
                                            </div>
                                            <div class="source-quality">{{ source.quality }}%</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </ArtDecoCard>
                    </div>

                    <div class="auction-table">
                        <div class="table-header">
                            <div class="col-rank">排名</div>
                            <div class="col-stock">股票信息</div>
                            <div class="col-price">最新价</div>
                            <div class="col-change">涨跌幅</div>
                            <div class="col-volume">成交量</div>
                            <div class="col-amount">成交额</div>
                            <div class="col-rob">抢筹度</div>
                        </div>
                        <div class="table-body">
                            <div class="table-row" v-for="(stock, index) in auctionData" :key="stock.code">
                                <div class="col-rank">{{ index + 1 }}</div>
                                <div class="col-stock">
                                    <div class="stock-name">{{ stock.name }}</div>
                                    <div class="stock-code">{{ stock.code }}</div>
                                </div>
                                <div class="col-price">¥{{ stock.price }}</div>
                                <div class="col-change" :class="stock.change >= 10 ? 'rise' : 'normal'">
                                    +{{ stock.change }}%
                                </div>
                                <div class="col-volume">{{ stock.volume }}万</div>
                                <div class="col-amount">{{ stock.amount }}亿</div>
                                <div class="col-rob">
                                    <div class="rob-bar">
                                        <div class="rob-fill" :style="{ width: stock.robRate + '%' }"></div>
                                    </div>
                                    <span class="rob-text">{{ stock.robRate }}%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </ArtDecoCard>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref, onMounted } from 'vue'
    import { ArtDecoStatCard, ArtDecoCard, ArtDecoButton, ArtDecoSelect } from '@/components/artdeco'

    // 响应式数据
    const activeTab = ref('fund-flow')
    const activeTimeFilter = ref('1day')
    const rankingType = ref('amount')
    const lhbDate = ref('today')
    const selectedConcept = ref(null)
    const lastUpdate = ref('')

    // 主标签页
    const mainTabs = [
        { key: 'data-quality', label: '数据质量', icon: '🛡️' },
        { key: 'fund-flow', label: '资金流向', icon: '💰' },
        { key: 'etf', label: 'ETF分析', icon: '🏷️' },
        { key: 'concepts', label: '概念板块', icon: '💡' },
        { key: 'lhb', label: '龙虎榜', icon: '🏆' },
        { key: 'auction', label: '竞价抢筹', icon: '⏰' }
    ]

    // 时间筛选器
    const timeFilters = [
        { key: '1day', label: '1日' },
        { key: '3day', label: '3日' },
        { key: '5day', label: '5日' },
        { key: '10day', label: '10日' }
    ]

    // 排序选项
    const rankingOptions = [
        { label: '按流入金额', value: 'amount' },
        { label: '按涨跌幅', value: 'change' },
        { label: '按主力净额', value: 'main' }
    ]

    // 日期选项
    const dateOptions = [
        { label: '今日', value: 'today' },
        { label: '昨日', value: 'yesterday' },
        { label: '前日', value: 'dayBefore' }
    ]

    // 资金流向数据
    const fundData = ref({
        shanghai: { amount: '28.6亿', change: 5.2 },
        shenzhen: { amount: '30.2亿', change: 8.9 },
        north: { amount: '58.8亿', change: 15.6 },
        main: { amount: '126.5亿', change: 68.0 }
    })

    // 个股资金流向排行
    const stockRanking = ref([
        { name: '贵州茅台', code: '600519', price: '1850.00', change: 2.1, inflow: '12.5', mainForce: '8.9' },
        { name: '宁德时代', code: '300750', price: '245.60', change: 3.5, inflow: '8.9', mainForce: '6.7' },
        { name: '中国石化', code: '600028', price: '4.85', change: -1.8, inflow: '-5.2', mainForce: '-3.1' },
        { name: '招商银行', code: '600036', price: '38.45', change: 1.2, inflow: '6.7', mainForce: '4.5' },
        { name: '万科A', code: '000002', price: '18.90', change: -0.9, inflow: '-3.1', mainForce: '-2.2' }
    ])

    // ETF排行
    const etfRanking = ref([
        { name: '沪深300ETF', code: '159919', type: '宽基指数', price: '3.456', change: 1.2, volume: '45.6' },
        { name: '创业板ETF', code: '159915', type: '行业主题', price: '2.189', change: -0.8, volume: '32.1' },
        { name: '半导体ETF', code: '159941', type: '行业主题', price: '0.856', change: 4.5, volume: '28.9' },
        { name: '新能源ETF', code: '159941', type: '行业主题', price: '0.723', change: 3.2, volume: '25.6' }
    ])

    // 概念板块排行
    const conceptRanking = ref([
        { name: '人工智能', stockCount: 156, change: 3.2, heat: 85 },
        { name: '新能源汽车', stockCount: 98, change: 2.8, heat: 78 },
        { name: '半导体', stockCount: 87, change: -1.5, heat: 65 },
        { name: '医疗器械', stockCount: 134, change: 1.9, heat: 72 },
        { name: '云计算', stockCount: 76, change: 4.1, heat: 88 }
    ])

    // 龙虎榜数据
    const lhbData = ref([
        {
            name: 'N迈为股份',
            code: '300751',
            price: '456.78',
            change: 44.0,
            buyAmount: '8.9',
            sellAmount: '2.1',
            netBuy: '6.8'
        },
        {
            name: 'N爱德曼',
            code: '300751',
            price: '123.45',
            change: 123.0,
            buyAmount: '5.6',
            sellAmount: '1.2',
            netBuy: '4.4'
        },
        {
            name: 'N科创板',
            code: '300751',
            price: '89.12',
            change: 89.0,
            buyAmount: '4.3',
            sellAmount: '0.9',
            netBuy: '3.4'
        }
    ])

    // 竞价抢筹数据
    const auctionData = ref([
        {
            name: 'N迈为股份',
            code: '300751',
            price: '456.78',
            change: 44.0,
            volume: '1234',
            amount: '5.6',
            robRate: 95
        },
        { name: 'N爱德曼', code: '300751', price: '123.45', change: 123.0, volume: '987', amount: '3.2', robRate: 88 },
        { name: 'N科创板', code: '300751', price: '89.12', change: 89.0, volume: '756', amount: '2.8', robRate: 82 }
    ])

    // 方法
    const switchTab = tabKey => {
        activeTab.value = tabKey
    }

    const refreshData = () => {
        // 模拟数据刷新
        lastUpdate.value = new Date().toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        })
    }

    const selectConcept = concept => {
        selectedConcept.value = concept
    }

    // 初始化
    onMounted(() => {
        refreshData()
        // 默认选择第一个概念
        selectedConcept.value = conceptRanking.value[0]
    })
</script>

<style scoped lang="scss">
    .artdeco-market-data {
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

    // 资金流向概览
    .fund-overview {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: var(--artdeco-spacing-4);
        margin-bottom: var(--artdeco-spacing-6);
    }

    // 图表占位符
    .chart-placeholder {
        .chart-title {
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-lg);
            font-weight: 600;
            color: var(--artdeco-gold-primary);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
            margin-bottom: var(--artdeco-spacing-4);
            text-align: center;
        }

        .chart-area {
            width: 100%;
            height: 200px;
            background: var(--artdeco-bg-card);
            border: 1px solid rgba(212, 175, 55, 0.1);
            border-radius: var(--artdeco-radius-none);
            display: flex;
            align-items: center;
            justify-content: center;

            svg {
                width: 100%;
                height: 100%;
            }
        }
    }

    // 排行表
    .ranking-controls {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--artdeco-spacing-4);
        gap: var(--artdeco-spacing-4);

        .time-filters {
            display: flex;
            gap: var(--artdeco-spacing-2);
        }

        .filter-btn {
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

        .ranking-select {
            width: 200px;
        }
    }

    .ranking-table,
    .lhb-table,
    .auction-table {
        .table-header,
        .table-row {
            display: grid;
            grid-template-columns: 60px 2fr 1fr 1fr 1fr 1fr;
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
            }
        }

        .table-row {
            border-bottom: 1px solid rgba(212, 175, 55, 0.1);
            transition: all var(--artdeco-transition-base);

            &:hover {
                background: rgba(212, 175, 55, 0.02);
            }

            .col-rank {
                font-family: var(--artdeco-font-display);
                font-weight: 700;
                color: var(--artdeco-gold-primary);
                text-align: center;
            }

            .col-stock {
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

                &.normal {
                    color: var(--artdeco-fg-primary);
                }
            }

            .col-flow,
            .col-main,
            .col-buy,
            .col-sell,
            .col-net {
                font-family: var(--artdeco-font-mono);
                font-weight: 600;
                text-align: right;

                &.rise {
                    color: var(--artdeco-up);
                }

                &.fall {
                    color: var(--artdeco-down);
                }
            }

            .col-volume,
            .col-amount {
                font-family: var(--artdeco-font-mono);
                color: var(--artdeco-fg-primary);
                text-align: right;
            }

            .col-rob {
                display: flex;
                align-items: center;
                gap: var(--artdeco-spacing-2);

                .rob-bar {
                    flex: 1;
                    height: 8px;
                    background: var(--artdeco-bg-base);
                    border-radius: var(--artdeco-radius-sm);
                    overflow: hidden;

                    .rob-fill {
                        height: 100%;
                        background: linear-gradient(90deg, var(--artdeco-up), var(--artdeco-gold-primary));
                        border-radius: var(--artdeco-radius-sm);
                        transition: width var(--artdeco-transition-base);
                    }
                }

                .rob-text {
                    font-family: var(--artdeco-font-mono);
                    font-size: var(--artdeco-text-sm);
                    font-weight: 600;
                    color: var(--artdeco-up);
                    min-width: 40px;
                    text-align: right;
                }
            }
        }
    }

    // ETF列表
    .etf-list {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-3);
    }

    .etf-item {
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

        .etf-info {
            .etf-name {
                font-family: var(--artdeco-font-body);
                font-weight: 600;
                color: var(--artdeco-fg-primary);
                margin-bottom: 2px;
            }

            .etf-code {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-muted);
                margin-bottom: 2px;
            }

            .etf-type {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-xs);
                color: var(--artdeco-gold-primary);
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
            }
        }

        .etf-performance {
            text-align: right;

            .etf-price {
                font-family: var(--artdeco-font-mono);
                font-weight: 600;
                color: var(--artdeco-fg-primary);
                margin-bottom: 2px;
            }

            .etf-change {
                font-family: var(--artdeco-font-mono);
                font-weight: 700;
                font-size: var(--artdeco-text-sm);
                margin-bottom: 2px;

                &.rise {
                    color: var(--artdeco-up);
                }

                &.fall {
                    color: var(--artdeco-down);
                }
            }

            .etf-volume {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-muted);
            }
        }
    }

    // 概念板块
    .concepts-heat-map {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-4);
    }

    .concept-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--artdeco-spacing-4);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);
        transition: all var(--artdeco-transition-base);
        cursor: pointer;

        &:hover {
            border-color: var(--artdeco-gold-primary);
            box-shadow: var(--artdeco-glow-subtle);
        }

        .concept-info {
            .concept-name {
                font-family: var(--artdeco-font-body);
                font-weight: 600;
                color: var(--artdeco-fg-primary);
                margin-bottom: 2px;
            }

            .concept-stocks {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-muted);
            }
        }

        .concept-performance {
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-4);

            .concept-change {
                font-family: var(--artdeco-font-mono);
                font-weight: 700;
                min-width: 60px;
                text-align: right;

                &.rise {
                    color: var(--artdeco-up);
                }

                &.fall {
                    color: var(--artdeco-down);
                }
            }

            .concept-heat {
                display: flex;
                align-items: center;
                gap: var(--artdeco-spacing-2);

                .heat-bar {
                    width: 80px;
                    height: 6px;
                    background: var(--artdeco-bg-base);
                    border-radius: var(--artdeco-radius-sm);
                    overflow: hidden;

                    .heat-fill {
                        height: 100%;
                        background: linear-gradient(90deg, var(--artdeco-gold-primary), var(--artdeco-up));
                        border-radius: var(--artdeco-radius-sm);
                    }
                }

                .heat-value {
                    font-family: var(--artdeco-font-mono);
                    font-size: var(--artdeco-text-sm);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    min-width: 35px;
                    text-align: right;
                }
            }
        }
    }

    // 龙虎榜控制
    .lhb-controls {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--artdeco-spacing-4);
        gap: var(--artdeco-spacing-4);

        .lhb-filters {
            display: flex;
            gap: var(--artdeco-spacing-2);
        }
    }

    // 竞价抢筹概览
    .auction-overview {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: var(--artdeco-spacing-4);
        margin-bottom: var(--artdeco-spacing-6);
    }

    // 概念详情
    .concept-detail {
        .detail-header {
            margin-bottom: var(--artdeco-spacing-6);

            h3 {
                font-family: var(--artdeco-font-display);
                font-size: var(--artdeco-text-xl);
                font-weight: 700;
                color: var(--artdeco-gold-primary);
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
                margin: 0 0 var(--artdeco-spacing-3) 0;
            }

            .detail-stats {
                display: flex;
                gap: var(--artdeco-spacing-6);

                span {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-text-sm);
                    color: var(--artdeco-fg-muted);

                    .rise {
                        color: var(--artdeco-up);
                        font-weight: 600;
                    }

                    .fall {
                        color: var(--artdeco-down);
                        font-weight: 600;
                    }
                }
            }
        }

        .top-stocks {
            h4 {
                font-family: var(--artdeco-font-display);
                font-size: var(--artdeco-text-lg);
                font-weight: 600;
                color: var(--artdeco-gold-primary);
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
                margin-bottom: var(--artdeco-spacing-4);
            }

            .stock-list {
                display: flex;
                flex-direction: column;
                gap: var(--artdeco-spacing-2);
            }

            .stock-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
                background: var(--artdeco-bg-card);
                border: 1px solid rgba(212, 175, 55, 0.1);
                border-radius: var(--artdeco-radius-none);

                .stock-name {
                    font-family: var(--artdeco-font-body);
                    font-weight: 600;
                    color: var(--artdeco-fg-primary);
                }

                .stock-code {
                    font-family: var(--artdeco-font-mono);
                    font-size: var(--artdeco-text-sm);
                    color: var(--artdeco-fg-muted);
                }

                .stock-change {
                    font-family: var(--artdeco-font-mono);
                    font-weight: 700;
                    color: var(--artdeco-up);
                }
            }
        }
    }

    .no-selection {
        text-align: center;
        padding: var(--artdeco-spacing-8);
        color: var(--artdeco-fg-muted);

        p {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-base);
            margin: 0;
        }
    }

    // 响应式设计
    @media (max-width: 1200px) {
        .ranking-table,
        .lhb-table,
        .auction-table {
            .table-header,
            .table-row {
                grid-template-columns: 50px 1.5fr 1fr 1fr 1fr 1fr;
                font-size: var(--artdeco-text-sm);
            }
        }
    }

    @media (max-width: 768px) {
        .main-tabs {
            flex-wrap: wrap;
        }

        .fund-overview,
        .auction-overview {
            grid-template-columns: 1fr;
        }

        .ranking-controls,
        .lhb-controls {
            flex-direction: column;
            align-items: stretch;
            gap: var(--artdeco-spacing-3);
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
// 数据质量监控 .quality-overview { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap:
var(--artdeco-spacing-4); margin-bottom: var(--artdeco-spacing-6); } .quality-details { .quality-section { h4 {
font-family: var(--artdeco-font-display); font-size: var(--artdeco-text-lg); font-weight: 600; color:
var(--artdeco-gold-primary); text-transform: uppercase; letter-spacing: var(--artdeco-tracking-wide); margin: 0 0
var(--artdeco-spacing-4) 0; } } } .data-sources { display: flex; flex-direction: column; gap: var(--artdeco-spacing-3);
} .source-item { display: flex; justify-content: space-between; align-items: center; padding: var(--artdeco-spacing-4);
background: var(--artdeco-bg-card); border: 1px solid rgba(212, 175, 55, 0.1); border-radius:
var(--artdeco-radius-none); transition: all var(--artdeco-transition-base); &:hover { border-color:
var(--artdeco-gold-primary); box-shadow: var(--artdeco-glow-subtle); } .source-info { flex: 1; .source-name {
font-family: var(--artdeco-font-body); font-weight: 600; color: var(--artdeco-fg-primary); margin-bottom: 2px; }
.source-type { font-family: var(--artdeco-font-body); font-size: var(--artdeco-text-sm); color: var(--artdeco-fg-muted);
} } .source-status { padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2); border-radius:
var(--artdeco-radius-none); font-family: var(--artdeco-font-body); font-size: var(--artdeco-text-xs); font-weight: 600;
text-transform: uppercase; letter-spacing: var(--artdeco-tracking-wide); margin-right: var(--artdeco-spacing-3);
&.healthy { background: rgba(0, 230, 118, 0.1); color: var(--artdeco-up); } &.warning { background: rgba(212, 175, 55,
0.1); color: var(--artdeco-gold-primary); } } .source-quality { font-family: var(--artdeco-font-mono); font-weight: 600;
color: var(--artdeco-fg-primary); min-width: 50px; text-align: right; } }
