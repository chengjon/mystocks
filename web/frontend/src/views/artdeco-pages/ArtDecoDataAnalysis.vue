<template>
    <div class="artdeco-data-analysis">
        <!-- Page Header -->
        <div class="page-header">
            <div class="header-content">
                <h1 class="page-title">数据分析中心</h1>
                <p class="page-subtitle">技术指标分析 · 智能选股 · 自定义指标</p>
            </div>
            <div class="header-actions">
                <ArtDecoButton variant="outline" size="sm" @click="refreshData">刷新数据</ArtDecoButton>
                <ArtDecoButton variant="solid" @click="runScreening">执行筛选</ArtDecoButton>
            </div>
        </div>

        <!-- Stats Overview -->
        <div class="stats-overview">
            <ArtDecoStatCard
                label="可用指标"
                :value="stats.availableIndicators"
                change="0"
                change-percent
                variant="gold"
            />
            <ArtDecoStatCard
                label="自定义指标"
                :value="stats.customIndicators"
                change="3"
                change-percent
                variant="gold"
            />
            <ArtDecoStatCard
                label="筛选股票数"
                :value="stats.screenedStocks"
                change="15"
                change-percent
                variant="rise"
            />
            <ArtDecoStatCard
                label="今日筛选次数"
                :value="stats.screeningTimes"
                change="5"
                change-percent
                variant="gold"
            />
            <ArtDecoStatCard
                label="符合条件"
                :value="stats.qualifiedStocks"
                :change="stats.qualifiedChange"
                change-percent
                :variant="stats.qualifiedChange >= 0 ? 'rise' : 'fall'"
            />
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
            <!-- Technical Indicator Library -->
            <div v-if="activeTab === 'indicators'" class="tab-panel">
                <div class="indicators-layout">
                    <!-- Category Sidebar -->
                    <ArtDecoCard title="指标分类" hoverable class="category-card">
                        <div class="category-list">
                            <button
                                v-for="category in indicatorCategories"
                                :key="category.key"
                                class="category-item"
                                :class="{ active: activeCategory === category.key }"
                                @click="activeCategory = category.key"
                            >
                                <span class="category-icon">{{ category.icon }}</span>
                                <span class="category-name">{{ category.label }}</span>
                                <span class="category-count">{{ getCategoryCount(category.key) }}</span>
                            </button>
                        </div>
                    </ArtDecoCard>

                    <!-- Indicators Grid -->
                    <div class="indicators-grid">
                        <ArtDecoCard
                            v-for="indicator in filteredIndicators"
                            :key="indicator.id"
                            :title="indicator.name"
                            hoverable
                            class="indicator-card"
                            @click="selectIndicator(indicator)"
                        >
                            <div class="indicator-content">
                                <div class="indicator-header">
                                    <ArtDecoBadge :text="indicator.categoryLabel" variant="gold" size="sm" />
                                    <span class="indicator-type">{{ indicator.type }}</span>
                                </div>
                                <p class="indicator-description">{{ indicator.description }}</p>
                                <div class="indicator-params">
                                    <span class="params-label">参数:</span>
                                    <span
                                        v-for="param in indicator.params.slice(0, 2)"
                                        :key="param.name"
                                        class="param-tag"
                                    >
                                        {{ param.name }}:{{ param.default }}
                                    </span>
                                </div>
                                <div class="indicator-preview">
                                    <span class="preview-label">示例值:</span>
                                    <span class="preview-value" :class="getValueClass(indicator.example)">
                                        {{ formatValue(indicator.example) }}
                                    </span>
                                </div>
                            </div>
                        </ArtDecoCard>
                    </div>
                </div>

                <!-- Indicator Detail Modal -->
                <div v-if="selectedIndicator" class="indicator-modal-overlay" @click.self="selectedIndicator = null">
                    <div class="indicator-modal">
                        <div class="modal-header">
                            <h2>{{ selectedIndicator.name }}</h2>
                            <button class="close-btn" @click="selectedIndicator = null">×</button>
                        </div>
                        <div class="modal-body">
                            <div class="modal-section">
                                <h3>指标说明</h3>
                                <p>{{ selectedIndicator.description }}</p>
                            </div>
                            <div class="modal-section">
                                <h3>参数配置</h3>
                                <div class="params-config">
                                    <div
                                        v-for="param in selectedIndicator.params"
                                        :key="param.name"
                                        class="param-config-item"
                                    >
                                        <label>{{ param.name }}</label>
                                        <ArtDecoInput
                                            v-model.number="param.value"
                                            :type="param.type === 'integer' ? 'number' : 'number'"
                                            :min="param.min"
                                            :max="param.max"
                                            :step="param.step || 1"
                                        />
                                        <span class="param-range">({{ param.min }}-{{ param.max }})</span>
                                        <span class="param-desc">{{ param.desc }}</span>
                                    </div>
                                </div>
                            </div>
                            <div class="modal-section">
                                <h3>计算公式</h3>
                                <div class="formula-display">
                                    <code>{{ selectedIndicator.formula }}</code>
                                </div>
                            </div>
                            <div class="modal-section">
                                <h3>计算预览</h3>
                                <div class="preview-display">
                                    <div class="preview-chart">
                                        <svg width="100%" height="120" viewBox="0 0 300 120">
                                            <path
                                                d="M0,100 Q50,80 100,70 T200,50 T300,30"
                                                fill="none"
                                                stroke="#D4AF37"
                                                stroke-width="2"
                                            />
                                            <path
                                                d="M0,110 Q50,100 100,95 T200,80 T300,60"
                                                fill="none"
                                                stroke="#FF5252"
                                                stroke-width="1.5"
                                                stroke-dasharray="5,3"
                                            />
                                        </svg>
                                    </div>
                                    <div class="preview-stats">
                                        <div class="preview-stat">
                                            <span class="stat-label">当前值</span>
                                            <span class="stat-value">{{ selectedIndicator.example }}</span>
                                        </div>
                                        <div class="preview-stat">
                                            <span class="stat-label">历史最高</span>
                                            <span class="stat-value">{{ selectedIndicator.historyHigh }}</span>
                                        </div>
                                        <div class="preview-stat">
                                            <span class="stat-label">历史最低</span>
                                            <span class="stat-value">{{ selectedIndicator.historyLow }}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <ArtDecoButton variant="outline" @click="addToCustom(selectedIndicator)">
                                添加到自定义
                            </ArtDecoButton>
                            <ArtDecoButton variant="solid" @click="calculateIndicator(selectedIndicator)">
                                应用到图表
                            </ArtDecoButton>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Custom Indicator Editor -->
            <div v-if="activeTab === 'editor'" class="tab-panel">
                <div class="editor-layout">
                    <!-- Indicator Template Library -->
                    <ArtDecoCard title="指标模板" hoverable class="template-card">
                        <div class="template-list">
                            <div
                                v-for="template in indicatorTemplates"
                                :key="template.id"
                                class="template-item"
                                @click="loadTemplate(template)"
                            >
                                <div class="template-icon">{{ template.icon }}</div>
                                <div class="template-info">
                                    <div class="template-name">{{ template.name }}</div>
                                    <div class="template-desc">{{ template.description }}</div>
                                </div>
                            </div>
                        </div>
                    </ArtDecoCard>

                    <!-- Code Editor -->
                    <ArtDecoCard title="自定义指标编辑器" hoverable class="code-card">
                        <div class="editor-controls">
                            <div class="control-row">
                                <label>指标名称</label>
                                <ArtDecoInput v-model="customIndicator.name" placeholder="输入指标名称" />
                            </div>
                            <div class="control-row">
                                <label>显示类型</label>
                                <ArtDecoSelect
                                    v-model="customIndicator.displayType"
                                    :options="displayTypes"
                                    placeholder="选择显示类型"
                                />
                            </div>
                            <div class="control-row">
                                <label>线条颜色</label>
                                <div class="color-picker">
                                    <button
                                        v-for="color in colorOptions"
                                        :key="color.value"
                                        class="color-btn"
                                        :class="{ active: customIndicator.color === color.value }"
                                        :style="{ background: color.value }"
                                        @click="customIndicator.color = color.value"
                                    ></button>
                                </div>
                            </div>
                        </div>

                        <div class="code-editor">
                            <div class="editor-tabs">
                                <button
                                    v-for="file in editorFiles"
                                    :key="file.key"
                                    class="editor-tab"
                                    :class="{ active: activeFile === file.key }"
                                    @click="activeFile = file.key"
                                >
                                    {{ file.name }}
                                </button>
                            </div>
                            <div class="code-area">
                                <ArtDecoCodeEditor v-model="customIndicator.code" title="PYTHON" language="PYTHON" />
                            </div>
                        </div>

                        <div class="editor-actions">
                            <ArtDecoButton variant="outline" size="sm" @click="validateCode">语法检查</ArtDecoButton>
                            <ArtDecoButton variant="outline" size="sm" @click="saveIndicator">保存指标</ArtDecoButton>
                            <ArtDecoButton variant="solid" size="sm" @click="applyIndicator">应用到图表</ArtDecoButton>
                        </div>
                    </ArtDecoCard>

                    <!-- Parameter Definition -->
                    <ArtDecoCard title="参数定义" hoverable class="params-card">
                        <div class="params-definition">
                            <div class="param-header">
                                <ArtDecoButton variant="outline" size="sm" @click="addParameter">
                                    添加参数
                                </ArtDecoButton>
                            </div>
                            <div class="param-list">
                                <div
                                    v-for="(param, index) in customIndicator.parameters"
                                    :key="index"
                                    class="param-item"
                                >
                                    <div class="param-row">
                                        <ArtDecoInput
                                            v-model="param.name"
                                            placeholder="参数名"
                                            class="param-name-input"
                                        />
                                        <ArtDecoSelect
                                            v-model="param.type"
                                            :options="paramTypes"
                                            class="param-type-select"
                                        />
                                        <ArtDecoInput
                                            v-model.number="param.default"
                                            type="number"
                                            placeholder="默认值"
                                            class="param-default-input"
                                        />
                                        <ArtDecoInput
                                            v-model.number="param.min"
                                            type="number"
                                            placeholder="最小值"
                                            class="param-range-input"
                                        />
                                        <ArtDecoInput
                                            v-model.number="param.max"
                                            type="number"
                                            placeholder="最大值"
                                            class="param-range-input"
                                        />
                                        <button class="remove-param-btn" @click="removeParameter(index)">×</button>
                                    </div>
                                    <ArtDecoInput
                                        v-model="param.description"
                                        placeholder="参数描述"
                                        class="param-desc-input"
                                    />
                                </div>
                            </div>
                        </div>
                    </ArtDecoCard>
                </div>
            </div>

            <!-- Stock Screener -->
            <div v-if="activeTab === 'screener'" class="tab-panel">
                <div class="screener-layout">
                    <!-- Filter Panel -->
                    <ArtDecoCard title="筛选条件" hoverable class="filter-card">
                        <div class="filter-sections">
                            <!-- Price Filters -->
                            <div class="filter-section">
                                <h4>价格条件</h4>
                                <div class="filter-row">
                                    <label>价格范围</label>
                                    <div class="range-inputs">
                                        <ArtDecoInput
                                            v-model.number="screeningFilters.priceMin"
                                            type="number"
                                            placeholder="最低价"
                                        />
                                        <span class="range-separator">-</span>
                                        <ArtDecoInput
                                            v-model.number="screeningFilters.priceMax"
                                            type="number"
                                            placeholder="最高价"
                                        />
                                    </div>
                                </div>
                                <div class="filter-row">
                                    <label>涨跌幅</label>
                                    <div class="range-inputs">
                                        <ArtDecoInput
                                            v-model.number="screeningFilters.changeMin"
                                            type="number"
                                            placeholder="最小涨幅%"
                                        />
                                        <span class="range-separator">-</span>
                                        <ArtDecoInput
                                            v-model.number="screeningFilters.changeMax"
                                            type="number"
                                            placeholder="最大涨幅%"
                                        />
                                    </div>
                                </div>
                            </div>

                            <!-- Volume Filters -->
                            <div class="filter-section">
                                <h4>成交量条件</h4>
                                <div class="filter-row">
                                    <label>成交量(手)</label>
                                    <div class="range-inputs">
                                        <ArtDecoInput
                                            v-model.number="screeningFilters.volumeMin"
                                            type="number"
                                            placeholder="最小量"
                                        />
                                        <span class="range-separator">-</span>
                                        <ArtDecoInput
                                            v-model.number="screeningFilters.volumeMax"
                                            type="number"
                                            placeholder="最大量"
                                        />
                                    </div>
                                </div>
                                <div class="filter-row">
                                    <label>换手率</label>
                                    <div class="range-inputs">
                                        <ArtDecoInput
                                            v-model.number="screeningFilters.turnoverMin"
                                            type="number"
                                            step="0.1"
                                            placeholder="最小%"
                                        />
                                        <span class="range-separator">-</span>
                                        <ArtDecoInput
                                            v-model.number="screeningFilters.turnoverMax"
                                            type="number"
                                            step="0.1"
                                            placeholder="最大%"
                                        />
                                    </div>
                                </div>
                            </div>

                            <!-- Technical Indicator Filters -->
                            <div class="filter-section">
                                <h4>技术指标条件</h4>
                                <div class="indicator-filters">
                                    <div
                                        v-for="(filter, index) in screeningFilters.indicators"
                                        :key="index"
                                        class="indicator-filter-row"
                                    >
                                        <ArtDecoSelect
                                            v-model="filter.indicator"
                                            :options="availableIndicatorsForFilter"
                                            placeholder="选择指标"
                                            class="indicator-select"
                                        />
                                        <ArtDecoSelect
                                            v-model="filter.operator"
                                            :options="operatorOptions"
                                            class="operator-select"
                                        />
                                        <ArtDecoInput
                                            v-model.number="filter.value"
                                            type="number"
                                            step="0.01"
                                            placeholder="阈值"
                                            class="value-input"
                                        />
                                        <button class="remove-filter-btn" @click="removeIndicatorFilter(index)">
                                            ×
                                        </button>
                                    </div>
                                </div>
                                <ArtDecoButton variant="outline" size="sm" @click="addIndicatorFilter">
                                    添加指标条件
                                </ArtDecoButton>
                            </div>

                            <!-- Market Cap Filters -->
                            <div class="filter-section">
                                <h4>基本面条件</h4>
                                <div class="filter-row">
                                    <label>市值(亿)</label>
                                    <div class="range-inputs">
                                        <ArtDecoInput
                                            v-model.number="screeningFilters.marketCapMin"
                                            type="number"
                                            placeholder="最小"
                                        />
                                        <span class="range-separator">-</span>
                                        <ArtDecoInput
                                            v-model.number="screeningFilters.marketCapMax"
                                            type="number"
                                            placeholder="最大"
                                        />
                                    </div>
                                </div>
                                <div class="filter-row">
                                    <label>PE(市盈率)</label>
                                    <div class="range-inputs">
                                        <ArtDecoInput
                                            v-model.number="screeningFilters.peMin"
                                            type="number"
                                            placeholder="最小"
                                        />
                                        <span class="range-separator">-</span>
                                        <ArtDecoInput
                                            v-model.number="screeningFilters.peMax"
                                            type="number"
                                            placeholder="最大"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="filter-actions">
                            <ArtDecoButton variant="outline" @click="resetFilters">重置条件</ArtDecoButton>
                            <ArtDecoButton variant="solid" @click="runScreening">执行筛选</ArtDecoButton>
                        </div>
                    </ArtDecoCard>

                    <!-- Filter Templates -->
                    <ArtDecoCard title="筛选模板" hoverable class="templates-card">
                        <div class="template-grid">
                            <div
                                v-for="template in screeningTemplates"
                                :key="template.id"
                                class="template-item"
                                :class="{ active: selectedTemplate === template.id }"
                                @click="loadScreeningTemplate(template)"
                            >
                                <div class="template-icon">{{ template.icon }}</div>
                                <div class="template-name">{{ template.name }}</div>
                                <div class="template-stats">{{ template.stockCount }}只股票</div>
                            </div>
                        </div>
                    </ArtDecoCard>
                </div>
            </div>

            <!-- Results Visualization -->
            <div v-if="activeTab === 'results'" class="tab-panel">
                <div class="results-layout">
                    <!-- Results Table -->
                    <ArtDecoCard title="筛选结果" hoverable class="results-card">
                        <template #header>
                            <div class="results-header">
                                <div class="results-info">
                                    <span class="results-count">共 {{ screeningResults.length }} 只股票</span>
                                    <span class="results-time">更新时间: {{ lastUpdateTime }}</span>
                                </div>
                                <div class="results-actions">
                                    <ArtDecoButton variant="outline" size="sm" @click="exportResults('csv')">
                                        导出CSV
                                    </ArtDecoButton>
                                    <ArtDecoButton variant="outline" size="sm" @click="exportResults('excel')">
                                        导出Excel
                                    </ArtDecoButton>
                                    <ArtDecoButton variant="outline" size="sm" @click="saveAsTemplate">
                                        保存为模板
                                    </ArtDecoButton>
                                </div>
                            </div>
                        </template>

                        <ArtDecoTable
                            :columns="resultColumns"
                            :data="screeningResults"
                            :pagination="true"
                            :loading="loading"
                            row-key="symbol"
                            @row-click="handleRowClick"
                        >
                            <template #actions="{ row }">
                                <ArtDecoButton variant="outline" size="sm" @click="viewChart(row)">图表</ArtDecoButton>
                                <ArtDecoButton variant="solid" size="sm" @click="addToWatchlist(row)">
                                    关注
                                </ArtDecoButton>
                            </template>
                        </ArtDecoTable>
                    </ArtDecoCard>

                    <!-- Performance Metrics -->
                    <ArtDecoCard title="筛选结果统计" hoverable class="metrics-card">
                        <div class="metrics-grid">
                            <div class="metric-section">
                                <h4>涨跌幅分布</h4>
                                <div class="distribution-chart">
                                    <div class="distribution-bars">
                                        <div class="dist-bar rise">
                                            <div
                                                class="bar-fill"
                                                :style="{ height: metrics.riseDistribution + '%' }"
                                            ></div>
                                            <span class="bar-label">上涨</span>
                                            <span class="bar-value">{{ metrics.riseCount }}只</span>
                                        </div>
                                        <div class="dist-bar flat">
                                            <div
                                                class="bar-fill"
                                                :style="{ height: metrics.flatDistribution + '%' }"
                                            ></div>
                                            <span class="bar-label">持平</span>
                                            <span class="bar-value">{{ metrics.flatCount }}只</span>
                                        </div>
                                        <div class="dist-bar fall">
                                            <div
                                                class="bar-fill"
                                                :style="{ height: metrics.fallDistribution + '%' }"
                                            ></div>
                                            <span class="bar-label">下跌</span>
                                            <span class="bar-value">{{ metrics.fallCount }}只</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="metric-section">
                                <h4>行业分布</h4>
                                <div class="industry-list">
                                    <div
                                        v-for="(item, index) in metrics.industryDistribution.slice(0, 5)"
                                        :key="index"
                                        class="industry-item"
                                    >
                                        <span class="industry-name">{{ item.name }}</span>
                                        <div class="industry-bar">
                                            <div class="bar-fill" :style="{ width: item.percentage + '%' }"></div>
                                        </div>
                                        <span class="industry-count">{{ item.count }}只</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="metrics-summary">
                            <ArtDecoStatCard
                                label="平均涨幅"
                                :value="metrics.avgChange + '%'"
                                :change="metrics.avgChange"
                                change-percent
                                :variant="metrics.avgChange >= 0 ? 'rise' : 'fall'"
                            />
                            <ArtDecoStatCard
                                label="平均换手"
                                :value="metrics.avgTurnover + '%'"
                                change="0"
                                change-percent
                                variant="gold"
                            />
                            <ArtDecoStatCard
                                label="平均市值"
                                :value="metrics.avgMarketCap + '亿'"
                                change="0"
                                change-percent
                                variant="gold"
                            />
                            <ArtDecoStatCard
                                label="涨停数"
                                :value="metrics.limitUpCount"
                                change="0"
                                change-percent
                                :variant="metrics.limitUpCount > 0 ? 'rise' : 'gold'"
                            />
                        </div>
                    </ArtDecoCard>

                    <!-- Stock Detail Chart -->
                    <ArtDecoCard
                        v-if="selectedStock"
                        :title="selectedStock.name + ' - ' + selectedStock.symbol"
                        hoverable
                        class="chart-card"
                    >
                        <div class="stock-detail-header">
                            <div class="stock-info">
                                <span class="stock-price" :class="selectedStock.change >= 0 ? 'rise' : 'fall'">
                                    {{ selectedStock.price }}
                                </span>
                                <span class="stock-change" :class="selectedStock.change >= 0 ? 'rise' : 'fall'">
                                    {{ selectedStock.change >= 0 ? '+' : '' }}{{ selectedStock.change }}%
                                </span>
                            </div>
                            <div class="stock-indicators">
                                <span
                                    v-for="ind in selectedStock.indicatorValues"
                                    :key="ind.name"
                                    class="indicator-tag"
                                >
                                    {{ ind.name }}: {{ ind.value }}
                                </span>
                            </div>
                        </div>
                        <div class="stock-chart">
                            <svg width="100%" height="250" viewBox="0 0 600 250">
                                <g class="grid-lines">
                                    <line
                                        v-for="i in 5"
                                        :key="i"
                                        x1="0"
                                        :y1="i * 50"
                                        x2="600"
                                        :y2="i * 50"
                                        stroke="rgba(212,175,55,0.1)"
                                    />
                                </g>
                                <path
                                    d="M0,200 L50,180 L100,190 L150,160 L200,170 L250,150 L300,140 L350,160 L400,130 L450,140 L500,120 L550,100 L600,110"
                                    fill="none"
                                    stroke="#D4AF37"
                                    stroke-width="2"
                                />
                                <g class="volume-bars">
                                    <rect
                                        v-for="i in 20"
                                        :key="i"
                                        :x="(i - 1) * 30 + 10"
                                        y="220"
                                        width="20"
                                        :height="Math.random() * 30"
                                        fill="rgba(212,175,55,0.3)"
                                    />
                                </g>
                            </svg>
                        </div>
                    </ArtDecoCard>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref, computed, onMounted } from 'vue'
    import {
        ArtDecoStatCard,
        ArtDecoCard,
        ArtDecoButton,
        ArtDecoInput,
        ArtDecoSelect,
        ArtDecoBadge,
        ArtDecoTable,
        ArtDecoCodeEditor
    } from '@/components/artdeco'

    const activeTab = ref('indicators')
    const activeCategory = ref('trend')
    const activeFile = ref('main')
    const selectedIndicator = ref(null)
    const selectedStock = ref(null)
    const selectedTemplate = ref(null)
    const loading = ref(false)
    const lastUpdateTime = ref('')

    const stats = ref({
        availableIndicators: 26,
        customIndicators: 5,
        screenedStocks: 1248,
        screeningTimes: 18,
        qualifiedStocks: 156,
        qualifiedChange: 12
    })

    const mainTabs = [
        { key: 'indicators', label: '指标库', icon: '📊' },
        { key: 'editor', label: '指标编辑器', icon: '✏️' },
        { key: 'screener', label: '智能选股', icon: '🔍' },
        { key: 'results', label: '筛选结果', icon: '📈' }
    ]

    const indicatorCategories = [
        { key: 'trend', label: '趋势指标', icon: '📈' },
        { key: 'momentum', label: '动量指标', icon: '⚡' },
        { key: 'volatility', label: '波动指标', icon: '🌊' },
        { key: 'volume', label: '成交量指标', icon: '📊' }
    ]

    const indicators = ref([
        {
            id: 1,
            name: '简单移动平均线',
            key: 'sma',
            category: 'trend',
            categoryLabel: '趋势',
            type: '主图',
            description: '计算指定周期的收盘价算术平均值',
            params: [{ name: '周期', default: 5, min: 2, max: 200, type: 'integer', desc: '计算周期' }],
            formula: 'SMA = (C1 + C2 + ... + Cn) / n',
            example: 15.68,
            historyHigh: 28.5,
            historyLow: 8.2
        },
        {
            id: 2,
            name: '指数移动平均线',
            key: 'ema',
            category: 'trend',
            categoryLabel: '趋势',
            type: '主图',
            description: '对近期数据赋予更大权重的移动平均',
            params: [{ name: '周期', default: 12, min: 2, max: 200, type: 'integer', desc: '计算周期' }],
            formula: 'EMA = alpha * Close + (1-alpha) * EMA_prev',
            example: 15.72,
            historyHigh: 29.1,
            historyLow: 8.5
        },
        {
            id: 3,
            name: 'MACD',
            key: 'macd',
            category: 'trend',
            categoryLabel: '趋势',
            type: '副图',
            description: '指数平滑异同移动平均线',
            params: [
                { name: '快线', default: 12, min: 2, max: 50, type: 'integer', desc: '快速EMA周期' },
                { name: '慢线', default: 26, min: 5, max: 100, type: 'integer', desc: '慢速EMA周期' },
                { name: '信号线', default: 9, min: 2, max: 50, type: 'integer', desc: '信号线周期' }
            ],
            formula: 'MACD = EMA12 - EMA26, Signal = EMA9 of MACD',
            example: 0.45,
            historyHigh: 3.2,
            historyLow: -2.8
        },
        {
            id: 4,
            name: '布林带',
            key: 'boll',
            category: 'trend',
            categoryLabel: '趋势',
            type: '主图',
            description: '基于标准差的通道型指标',
            params: [
                { name: '周期', default: 20, min: 5, max: 50, type: 'integer', desc: '中轨周期' },
                { name: '倍数', default: 2, min: 1, max: 5, step: 0.1, type: 'float', desc: '标准差倍数' }
            ],
            formula: 'Upper = MA + K * Std, Lower = MA - K * Std',
            example: 16.2,
            historyHigh: 22.5,
            historyLow: 10.1
        },
        {
            id: 5,
            name: '抛物线转向指标',
            key: 'sar',
            category: 'trend',
            categoryLabel: '趋势',
            type: '主图',
            description: '判断趋势反转的止损指标',
            params: [
                { name: '步长', default: 0.02, min: 0.01, max: 0.1, step: 0.01, type: 'float', desc: '加速因子' },
                { name: '极限', default: 0.2, min: 0.1, max: 0.5, step: 0.01, type: 'float', desc: '最大值' }
            ],
            formula: 'SAR = SAR_prev + AF * (EP - SAR_prev)',
            example: 15.8,
            historyHigh: 18.2,
            historyLow: 12.5
        },
        {
            id: 6,
            name: '趋势线',
            key: 'trendline',
            category: 'trend',
            categoryLabel: '趋势',
            type: '主图',
            description: '连接价格高点的趋势线',
            params: [{ name: '周期', default: 20, min: 5, max: 100, type: 'integer', desc: '回溯周期' }],
            formula: '线性回归拟合',
            example: '上升',
            historyHigh: '-',
            historyLow: '-'
        },
        {
            id: 7,
            name: '自适应移动平均',
            key: 'kama',
            category: 'trend',
            categoryLabel: '趋势',
            type: '主图',
            description: '根据市场波动性自动调整的MA',
            params: [
                { name: '快速', default: 2, min: 2, max: 10, type: 'integer', desc: '快速ER周期' },
                { name: '慢速', default: 30, min: 10, max: 100, type: 'integer', desc: '慢速ER周期' }
            ],
            formula: 'KAMA = MA * SC + KAMA_prev * (1-SC)',
            example: 15.65,
            historyHigh: 27.8,
            historyLow: 8.9
        },
        {
            id: 8,
            name: '相对强弱指标',
            key: 'rsi',
            category: 'momentum',
            categoryLabel: '动量',
            type: '副图',
            description: '衡量价格变动的速度和幅度',
            params: [{ name: '周期', default: 14, min: 2, max: 50, type: 'integer', desc: '计算周期' }],
            formula: 'RSI = 100 - 100 / (1 + RS)',
            example: 62.5,
            historyHigh: 85.2,
            historyLow: 15.8
        },
        {
            id: 9,
            name: '随机指标',
            key: 'kdj',
            category: 'momentum',
            categoryLabel: '动量',
            type: '副图',
            description: '随机振荡指标，判断超买超卖',
            params: [
                { name: 'N', default: 9, min: 3, max: 30, type: 'integer', desc: 'RSV周期' },
                { name: 'M1', default: 3, min: 2, max: 10, type: 'integer', desc: 'K线平滑' },
                { name: 'M2', default: 3, min: 2, max: 10, type: 'integer', desc: 'D线平滑' }
            ],
            formula: 'RSV = (Close - Ln) / (Hn - Ln) * 100',
            example: 'K:72 D:68 J:80',
            historyHigh: '95/90/98',
            historyLow: '5/8/2'
        },
        {
            id: 10,
            name: '威廉指标',
            key: 'wr',
            category: 'momentum',
            categoryLabel: '动量',
            type: '副图',
            description: '与RSI类似但方向相反的超买超卖指标',
            params: [{ name: '周期', default: 14, min: 2, max: 50, type: 'integer', desc: '计算周期' }],
            formula: 'WR = (Hn - C) / (Hn - Ln) * 100',
            example: -28.5,
            historyHigh: -5,
            historyLow: -95
        },
        {
            id: 11,
            name: '动量指标',
            key: 'mom',
            category: 'momentum',
            categoryLabel: '动量',
            type: '副图',
            description: '衡量价格变动的速度',
            params: [{ name: '周期', default: 10, min: 2, max: 50, type: 'integer', desc: '计算周期' }],
            formula: 'MOM = Close - Close_n',
            example: 1.25,
            historyHigh: 8.5,
            historyLow: -6.2
        },
        {
            id: 12,
            name: '变动率指标',
            key: 'roc',
            category: 'momentum',
            categoryLabel: '动量',
            type: '副图',
            description: '价格变动率百分比',
            params: [{ name: '周期', default: 12, min: 2, max: 50, type: 'integer', desc: '计算周期' }],
            formula: 'ROC = (Close - Close_n) / Close_n * 100',
            example: 3.2,
            historyHigh: 25.5,
            historyLow: -18.3
        },
        {
            id: 13,
            name: '顺势指标',
            key: 'cci',
            category: 'momentum',
            categoryLabel: '动量',
            type: '副图',
            description: '商品通道指数，衡量价格偏离程度',
            params: [{ name: '周期', default: 14, min: 5, max: 50, type: 'integer', desc: '计算周期' }],
            formula: 'CCI = (TP - MA) / (0.015 * MD)',
            example: 45.2,
            historyHigh: 180,
            historyLow: -165
        },
        {
            id: 14,
            name: '阿隆指标',
            key: 'aroon',
            category: 'momentum',
            categoryLabel: '动量',
            type: '副图',
            description: '判断趋势起始和结束',
            params: [{ name: '周期', default: 25, min: 5, max: 50, type: 'integer', desc: '计算周期' }],
            formula: 'AroonUp = (n - n_high) / n * 100',
            example: 'Up:72 Down:28',
            historyHigh: '100',
            historyLow: '0'
        },
        {
            id: 15,
            name: '平均真实波幅',
            key: 'atr',
            category: 'volatility',
            categoryLabel: '波动',
            type: '副图',
            description: '衡量市场波动性的指标',
            params: [{ name: '周期', default: 14, min: 5, max: 50, type: 'integer', desc: '计算周期' }],
            formula: 'ATR = EMA of True Range',
            example: 0.85,
            historyHigh: 3.2,
            historyLow: 0.15
        },
        {
            id: 16,
            name: '真实波动幅度',
            key: 'tr',
            category: 'volatility',
            categoryLabel: '波动',
            type: '副图',
            description: '当日最高价、最低价和昨收的最大差值',
            params: [],
            formula: 'TR = max(|High-Low|, |High-Close_prev|, |Low-Close_prev|)',
            example: 1.12,
            historyHigh: 5.8,
            historyLow: 0.1
        },
        {
            id: 17,
            name: '布林带宽度',
            key: 'boll_width',
            category: 'volatility',
            categoryLabel: '波动',
            type: '副图',
            description: '布林带上轨与下轨的差值',
            params: [
                { name: '周期', default: 20, min: 5, max: 50, type: 'integer', desc: 'BOLL周期' },
                { name: '倍数', default: 2, min: 1, max: 4, step: 0.1, type: 'float', desc: '标准差倍数' }
            ],
            formula: 'Boll_Width = Upper - Lower',
            example: 2.5,
            historyHigh: 8.2,
            historyLow: 0.8
        },
        {
            id: 18,
            name: '肯特纳通道',
            key: 'kc',
            category: 'volatility',
            categoryLabel: '波动',
            type: '主图',
            description: '基于ATR的通道指标',
            params: [
                { name: '周期', default: 20, min: 5, max: 50, type: 'integer', desc: '中轨周期' },
                { name: '倍数', default: 2, min: 0.5, max: 4, step: 0.1, type: 'float', desc: 'ATR倍数' }
            ],
            formula: 'KC = MA +/- K * ATR',
            example: '15.5-17.8',
            historyHigh: '-',
            historyLow: '-'
        },
        {
            id: 19,
            name: '波动率指标',
            key: 'volatility',
            category: 'volatility',
            categoryLabel: '波动',
            type: '副图',
            description: '价格波动率的百分比',
            params: [{ name: '周期', default: 20, min: 5, max: 100, type: 'integer', desc: '计算周期' }],
            formula: 'Volatility = Std(returns) * sqrt(252)',
            example: 25.5,
            historyHigh: 85.2,
            historyLow: 8.5
        },
        {
            id: 20,
            name: '成交量',
            key: 'volume',
            category: 'volume',
            categoryLabel: '成交量',
            type: '副图',
            description: '指定周期内的成交总量',
            params: [{ name: '周期', default: 20, min: 5, max: 100, type: 'integer', desc: '计算周期' }],
            formula: 'Volume = Sum(VOL)',
            example: 1250000,
            historyHigh: 85000000,
            historyLow: 50000
        },
        {
            id: 21,
            name: '成交量移动平均',
            key: 'vma',
            category: 'volume',
            categoryLabel: '成交量',
            type: '副图',
            description: '成交量的移动平均线',
            params: [{ name: '周期', default: 20, min: 5, max: 100, type: 'integer', desc: '计算周期' }],
            formula: 'VMA = MA(Volume)',
            example: 2500000,
            historyHigh: 45000000,
            historyLow: 800000
        },
        {
            id: 22,
            name: '能量潮',
            key: 'obv',
            category: 'volume',
            categoryLabel: '成交量',
            type: '副图',
            description: '积累量指标，衡量资金流向',
            params: [],
            formula: 'OBV = OBV_prev + Volume * sign(Close-Close_prev)',
            example: 125000000,
            historyHigh: 580000000,
            historyLow: -120000000
        },
        {
            id: 23,
            name: '成交量变化率',
            key: 'vroc',
            category: 'volume',
            categoryLabel: '成交量',
            type: '副图',
            description: '成交量变化的百分比',
            params: [{ name: '周期', default: 12, min: 2, max: 50, type: 'integer', desc: '计算周期' }],
            formula: 'VROC = (Volume - Volume_n) / Volume_n * 100',
            example: 15.5,
            historyHigh: 280,
            historyLow: -85
        },
        {
            id: 24,
            name: '资金流量指标',
            key: 'mfi',
            category: 'volume',
            categoryLabel: '成交量',
            type: '副图',
            description: '将成交量与价格结合的资金指标',
            params: [{ name: '周期', default: 14, min: 2, max: 50, type: 'integer', desc: '计算周期' }],
            formula: 'MFI = 100 - 100 / (1 + MR)',
            example: 65.5,
            historyHigh: 92,
            historyLow: 15
        },
        {
            id: 25,
            name: '累积/派发线',
            key: 'ad',
            category: 'volume',
            categoryLabel: '成交量',
            type: '副图',
            description: '资金进出指标',
            params: [],
            formula: 'AD = AD_prev + (Close-Low) - (High-Close) / (High-Low) * Volume',
            example: 2500000,
            historyHigh: 15000000,
            historyLow: -8000000
        },
        {
            id: 26,
            name: '价量趋势',
            key: 'pvt',
            category: 'volume',
            categoryLabel: '成交量',
            type: '副图',
            description: '价格与成交量的综合指标',
            params: [],
            formula: 'PVT = PVT_prev + Volume * (Close-Close_prev) / Close_prev',
            example: 850000,
            historyHigh: 4500000,
            historyLow: -2200000
        }
    ])

    const filteredIndicators = computed(() => {
        return indicators.value.filter(ind => ind.category === activeCategory.value)
    })

    function getCategoryCount(categoryKey) {
        return indicators.value.filter(ind => ind.category === categoryKey).length
    }

    function selectIndicator(indicator) {
        selectedIndicator.value = indicator
        indicator.params.forEach(param => {
            param.value = param.default
        })
    }

    function formatValue(value) {
        if (typeof value === 'number') {
            return value.toFixed(2)
        }
        return value
    }

    function getValueClass(value) {
        if (typeof value === 'number') {
            return value >= 0 ? 'rise' : 'fall'
        }
        return ''
    }

    const customIndicator = ref({
        name: '',
        displayType: 'line',
        color: '#D4AF37',
        code: `# 自定义指标模板
import pandas as pd
import numpy as np

def calculate_indicator(df, params):
    close = df['close']
    short_period = params.get('short_period', 5)
    long_period = params.get('long_period', 20)
    short_ma = close.rolling(short_period).mean()
    long_ma = close.rolling(long_period).mean()
    diff = short_ma - long_ma
    return {'short_ma': short_ma, 'long_ma': long_ma, 'diff': diff}

def generate_signals(indicator_data):
    diff = indicator_data['diff']
    signals = pd.Series(0, index=diff.index)
    crossover = (diff > 0) & (diff.shift(1) <= 0)
    signals[crossover] = 1
    crossunder = (diff < 0) & (diff.shift(1) >= 0)
    signals[crossunder] = -1
    return signals
`,
        parameters: [
            { name: 'short_period', type: 'integer', default: 5, min: 2, max: 50, description: '短期周期' },
            { name: 'long_period', type: 'integer', default: 20, min: 5, max: 200, description: '长期周期' }
        ]
    })

    const editorFiles = [
        { key: 'main', name: 'indicator.py' },
        { key: 'config', name: 'params.json' },
        { key: 'signals', name: 'signals.py' }
    ]

    const displayTypes = [
        { label: '折线图', value: 'line' },
        { label: '柱状图', value: 'bar' },
        { label: '填充线', value: 'area' },
        { label: '点图', value: 'dot' }
    ]

    const colorOptions = [
        { label: '金色', value: '#D4AF37' },
        { label: '红色', value: '#FF5252' },
        { label: '绿色', value: '#00E676' },
        { label: '蓝色', value: '#4FC3F7' },
        { label: '紫色', value: '#BB86FC' },
        { label: '橙色', value: '#FF9800' }
    ]

    const paramTypes = [
        { label: '整数', value: 'integer' },
        { label: '浮点数', value: 'float' }
    ]

    const indicatorTemplates = [
        { id: 1, icon: '📈', name: '双均线金叉', description: '短期均线上穿长期均线买入' },
        { id: 2, icon: '⚡', name: 'RSI超卖', description: 'RSI低于30时买入' },
        { id: 3, icon: '🌊', name: '波动率突破', description: 'ATR突破时入场' },
        { id: 4, icon: '📊', name: '量价齐升', description: '量能放大配合价格上涨' },
        { id: 5, icon: '🎯', name: 'MACD背离', description: '价格创新低但MACD不创新低' }
    ]

    const screeningFilters = ref({
        priceMin: null,
        priceMax: null,
        changeMin: null,
        changeMax: null,
        volumeMin: null,
        volumeMax: null,
        turnoverMin: null,
        turnoverMax: null,
        marketCapMin: null,
        marketCapMax: null,
        peMin: null,
        peMax: null,
        indicators: []
    })

    const availableIndicatorsForFilter = computed(() => {
        return indicators.value.map(ind => ({ label: ind.name, value: ind.key }))
    })

    const operatorOptions = [
        { label: '大于', value: '>' },
        { label: '小于', value: '<' },
        { label: '等于', value: '=' },
        { label: '区间', value: 'between' },
        { label: '金叉', value: 'golden_cross' },
        { label: '死叉', value: 'death_cross' }
    ]

    const screeningTemplates = [
        { id: 1, icon: '🔥', name: '强势股回调', stockCount: 45, filters: { changeMin: 3, turnoverMin: 3 } },
        { id: 2, icon: '💎', name: '低估值价值', stockCount: 128, filters: { peMin: 0, peMax: 15 } },
        { id: 3, icon: '📈', name: '放量突破', stockCount: 32, filters: { vrocMin: 50, changeMin: 2 } },
        { id: 4, icon: '🎯', name: '技术金叉', stockCount: 67, filters: {} },
        { id: 5, icon: '🏆', name: '创历史新高', stockCount: 18, filters: { changeMin: 5 } },
        { id: 6, icon: '💰', name: '高股息率', stockCount: 85, filters: {} }
    ]

    const screeningResults = ref([
        {
            symbol: '600519',
            name: '贵州茅台',
            price: 1680.5,
            change: 2.35,
            volume: 520000,
            turnover: 1.25,
            pe: 28.5,
            marketCap: 21000,
            indicatorValues: [
                { name: 'MA5', value: 1650 },
                { name: 'RSI', value: 68 }
            ]
        },
        {
            symbol: '000001',
            name: '平安银行',
            price: 12.35,
            change: 1.25,
            volume: 4500000,
            turnover: 2.85,
            pe: 6.2,
            marketCap: 1200,
            indicatorValues: [
                { name: 'MA5', value: 12.1 },
                { name: 'RSI', value: 62 }
            ]
        },
        {
            symbol: '600000',
            name: '浦发银行',
            price: 8.92,
            change: 0.85,
            volume: 3200000,
            turnover: 1.52,
            pe: 5.8,
            marketCap: 1850,
            indicatorValues: [
                { name: 'MA5', value: 8.85 },
                { name: 'RSI', value: 58 }
            ]
        },
        {
            symbol: '300750',
            name: '宁德时代',
            price: 385.2,
            change: 3.15,
            volume: 1800000,
            turnover: 2.15,
            pe: 35.2,
            marketCap: 9500,
            indicatorValues: [
                { name: 'MA5', value: 378 },
                { name: 'RSI', value: 72 }
            ]
        },
        {
            symbol: '601398',
            name: '工商银行',
            price: 5.85,
            change: 0.52,
            volume: 2800000,
            turnover: 0.85,
            pe: 5.2,
            marketCap: 15800,
            indicatorValues: [
                { name: 'MA5', value: 5.82 },
                { name: 'RSI', value: 55 }
            ]
        },
        {
            symbol: '600036',
            name: '招商银行',
            price: 42.5,
            change: 1.85,
            volume: 1500000,
            turnover: 1.45,
            pe: 8.5,
            marketCap: 5200,
            indicatorValues: [
                { name: 'MA5', value: 41.8 },
                { name: 'RSI', value: 65 }
            ]
        },
        {
            symbol: '000651',
            name: '格力电器',
            price: 38.25,
            change: -0.65,
            volume: 2200000,
            turnover: 1.82,
            pe: 12.5,
            marketCap: 2100,
            indicatorValues: [
                { name: 'MA5', value: 38.5 },
                { name: 'RSI', value: 48 }
            ]
        },
        {
            symbol: '002594',
            name: '比亚迪',
            price: 248.8,
            change: 2.45,
            volume: 980000,
            turnover: 2.35,
            pe: 42.5,
            marketCap: 6800,
            indicatorValues: [
                { name: 'MA5', value: 245 },
                { name: 'RSI', value: 70 }
            ]
        }
    ])

    const resultColumns = [
        { key: 'symbol', label: '代码', sortable: true },
        { key: 'name', label: '名称', sortable: true },
        { key: 'price', label: '最新价', sortable: true, format: v => v.toFixed(2) },
        {
            key: 'change',
            label: '涨跌幅',
            sortable: true,
            format: v => v.toFixed(2) + '%',
            class: row => (row.change >= 0 ? 'data-rise' : 'data-fall')
        },
        { key: 'volume', label: '成交量', sortable: true, format: v => (v / 10000).toFixed(0) + '万' },
        { key: 'turnover', label: '换手率', sortable: true, format: v => v.toFixed(2) + '%' },
        { key: 'pe', label: 'PE', sortable: true, format: v => v.toFixed(1) },
        { key: 'marketCap', label: '市值(亿)', sortable: true, format: v => v.toFixed(0) }
    ]

    const metrics = ref({
        riseCount: 5,
        flatCount: 0,
        fallCount: 3,
        riseDistribution: 62,
        flatDistribution: 0,
        fallDistribution: 38,
        avgChange: 1.58,
        avgTurnover: 1.78,
        avgMarketCap: 2850,
        limitUpCount: 1,
        industryDistribution: [
            { name: '银行', count: 3, percentage: 37.5 },
            { name: '酿酒', count: 1, percentage: 12.5 },
            { name: '新能源', count: 2, percentage: 25 },
            { name: '医药', count: 1, percentage: 12.5 },
            { name: '家电', count: 1, percentage: 12.5 }
        ]
    })

    function switchTab(tabKey) {
        activeTab.value = tabKey
    }

    function refreshData() {
        loading.value = true
        setTimeout(() => {
            loading.value = false
            lastUpdateTime.value = new Date().toLocaleString('zh-CN')
        }, 1000)
    }

    function runScreening() {
        loading.value = true
        activeTab.value = 'results'
        setTimeout(() => {
            loading.value = false
            lastUpdateTime.value = new Date().toLocaleString('zh-CN')
        }, 1500)
    }

    function addToCustom(indicator) {
        customIndicator.value.name = indicator.name
        customIndicator.value.code = `# 基于 ${indicator.name} 的自定义指标\n\n` + customIndicator.value.code
        activeTab.value = 'editor'
    }

    function calculateIndicator(indicator) {
        console.log('Calculating indicator:', indicator.name)
    }

    function loadTemplate(template) {
        console.log('Loading template:', template.name)
    }

    function validateCode() {
        console.log('Validating code...')
    }

    function saveIndicator() {
        console.log('Saving indicator...')
    }

    function applyIndicator() {
        console.log('Applying indicator...')
    }

    function addParameter() {
        customIndicator.value.parameters.push({
            name: 'new_param',
            type: 'integer',
            default: 10,
            min: 1,
            max: 100,
            description: ''
        })
    }

    function removeParameter(index) {
        customIndicator.value.parameters.splice(index, 1)
    }

    function addIndicatorFilter() {
        screeningFilters.value.indicators.push({ indicator: '', operator: '>', value: 0 })
    }

    function removeIndicatorFilter(index) {
        screeningFilters.value.indicators.splice(index, 1)
    }

    function resetFilters() {
        screeningFilters.value = {
            priceMin: null,
            priceMax: null,
            changeMin: null,
            changeMax: null,
            volumeMin: null,
            volumeMax: null,
            turnoverMin: null,
            turnoverMax: null,
            marketCapMin: null,
            marketCapMax: null,
            peMin: null,
            peMax: null,
            indicators: []
        }
    }

    function loadScreeningTemplate(template) {
        selectedTemplate.value = template.id
        screeningFilters.value = { ...screeningFilters.value, ...template.filters }
    }

    function handleRowClick(row) {
        selectedStock.value = row
    }

    function viewChart(row) {
        selectedStock.value = row
    }

    function addToWatchlist(row) {
        console.log('Adding to watchlist:', row.symbol)
    }

    function exportResults(format) {
        console.log('Exporting results as:', format)
    }

    function saveAsTemplate() {
        console.log('Saving as template...')
    }

    onMounted(() => {
        lastUpdateTime.value = new Date().toLocaleString('zh-CN')
    })
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-data-analysis {
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
        gap: var(--artdeco-spacing-3);
    }

    .stats-overview {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: var(--artdeco-spacing-4);
        margin-bottom: var(--artdeco-spacing-6);
    }

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

    .tab-content .tab-panel {
        animation: fadeIn 0.5s ease-out;
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

    .indicators-layout {
        display: grid;
        grid-template-columns: 280px 1fr;
        gap: var(--artdeco-spacing-4);
    }

    .category-card .category-list {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-2);
    }

    .category-item {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-3);
        padding: var(--artdeco-spacing-3);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);
        color: var(--artdeco-fg-primary);
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-sm);
        cursor: pointer;
        transition: all var(--artdeco-transition-base);
        &:hover {
            border-color: var(--artdeco-gold-primary);
            background: rgba(212, 175, 55, 0.05);
        }
        &.active {
            background: rgba(212, 175, 55, 0.1);
            border-color: var(--artdeco-gold-primary);
            color: var(--artdeco-gold-primary);
        }
        .category-icon {
            font-size: var(--artdeco-text-lg);
        }
        .category-name {
            flex: 1;
            text-align: left;
        }
        .category-count {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-xs);
            color: var(--artdeco-gold-primary);
            background: rgba(212, 175, 55, 0.1);
            padding: 2px 8px;
            border-radius: var(--artdeco-radius-none);
        }
    }

    .indicators-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    .indicator-card {
        cursor: pointer;
        .indicator-content {
            .indicator-header {
                display: flex;
                align-items: center;
                gap: var(--artdeco-spacing-2);
                margin-bottom: var(--artdeco-spacing-2);
            }
            .indicator-type {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-xs);
                color: var(--artdeco-fg-muted);
            }
            .indicator-description {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-muted);
                margin-bottom: var(--artdeco-spacing-3);
                line-height: 1.5;
            }
            .indicator-params {
                display: flex;
                align-items: center;
                gap: var(--artdeco-spacing-2);
                margin-bottom: var(--artdeco-spacing-2);
                .params-label {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-text-xs);
                    color: var(--artdeco-fg-muted);
                }
                .param-tag {
                    font-family: var(--artdeco-font-mono);
                    font-size: var(--artdeco-text-xs);
                    color: var(--artdeco-gold-primary);
                    background: rgba(212, 175, 55, 0.1);
                    padding: 2px 6px;
                    border-radius: var(--artdeco-radius-none);
                }
            }
            .indicator-preview {
                display: flex;
                align-items: center;
                gap: var(--artdeco-spacing-2);
                .preview-label {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-text-xs);
                    color: var(--artdeco-fg-muted);
                }
                .preview-value {
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
        }
    }

    .indicator-modal-overlay {
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

    .indicator-modal {
        width: 90%;
        max-width: 900px;
        max-height: 90vh;
        background: var(--artdeco-bg-card);
        border: 1px solid var(--artdeco-gold-primary);
        border-radius: var(--artdeco-radius-none);
        overflow: hidden;
        display: flex;
        flex-direction: column;
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: var(--artdeco-spacing-4);
            border-bottom: 1px solid rgba(212, 175, 55, 0.2);
            h2 {
                font-family: var(--artdeco-font-display);
                font-size: var(--artdeco-text-2xl);
                color: var(--artdeco-gold-primary);
                margin: 0;
            }
            .close-btn {
                width: 36px;
                height: 36px;
                background: transparent;
                border: 1px solid rgba(212, 175, 55, 0.3);
                border-radius: var(--artdeco-radius-none);
                color: var(--artdeco-fg-primary);
                font-size: 24px;
                cursor: pointer;
                transition: all var(--artdeco-transition-base);
                &:hover {
                    background: rgba(212, 175, 55, 0.1);
                    border-color: var(--artdeco-gold-primary);
                }
            }
        }
        .modal-body {
            flex: 1;
            overflow-y: auto;
            padding: var(--artdeco-spacing-4);
        }
        .modal-section {
            margin-bottom: var(--artdeco-spacing-5);
            h3 {
                font-family: var(--artdeco-font-display);
                font-size: var(--artdeco-text-lg);
                color: var(--artdeco-gold-primary);
                margin: 0 0 var(--artdeco-spacing-3) 0;
                padding-bottom: var(--artdeco-spacing-2);
                border-bottom: 1px solid rgba(212, 175, 55, 0.1);
            }
            p {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-secondary);
                line-height: 1.6;
            }
        }
        .params-config {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: var(--artdeco-spacing-3);
        }
        .param-config-item {
            display: grid;
            grid-template-columns: 80px 1fr 60px 1fr;
            gap: var(--artdeco-spacing-2);
            align-items: center;
            label {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-sm);
                font-weight: 600;
                color: var(--artdeco-gold-primary);
            }
            .param-range {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-xs);
                color: var(--artdeco-fg-muted);
            }
            .param-desc {
                grid-column: 1 / -1;
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-xs);
                color: var(--artdeco-fg-muted);
            }
        }
        .formula-display {
            background: var(--artdeco-bg-global);
            padding: var(--artdeco-spacing-3);
            border: 1px solid rgba(212, 175, 55, 0.2);
            border-radius: var(--artdeco-radius-none);
            code {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-gold-primary);
            }
        }
        .preview-display {
            .preview-chart {
                background: var(--artdeco-bg-global);
                border: 1px solid rgba(212, 175, 55, 0.2);
                border-radius: var(--artdeco-radius-none);
                padding: var(--artdeco-spacing-3);
                margin-bottom: var(--artdeco-spacing-3);
            }
            .preview-stats {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: var(--artdeco-spacing-3);
            }
            .preview-stat {
                text-align: center;
                padding: var(--artdeco-spacing-3);
                background: var(--artdeco-bg-card);
                border: 1px solid rgba(212, 175, 55, 0.1);
                border-radius: var(--artdeco-radius-none);
                .stat-label {
                    display: block;
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-text-sm);
                    color: var(--artdeco-fg-muted);
                    margin-bottom: var(--artdeco-spacing-1);
                }
                .stat-value {
                    font-family: var(--artdeco-font-mono);
                    font-size: var(--artdeco-text-lg);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                }
            }
        }
        .modal-footer {
            display: flex;
            justify-content: flex-end;
            gap: var(--artdeco-spacing-3);
            padding: var(--artdeco-spacing-4);
            border-top: 1px solid rgba(212, 175, 55, 0.2);
        }
    }

    .editor-layout {
        display: grid;
        grid-template-columns: 280px 1fr;
        gap: var(--artdeco-spacing-4);
    }

    .template-card .template-list {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-2);
    }

    .template-item {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-3);
        padding: var(--artdeco-spacing-3);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);
        cursor: pointer;
        transition: all var(--artdeco-transition-base);
        &:hover {
            border-color: var(--artdeco-gold-primary);
            background: rgba(212, 175, 55, 0.05);
        }
        .template-icon {
            font-size: var(--artdeco-text-xl);
        }
        .template-info {
            .template-name {
                font-family: var(--artdeco-font-body);
                font-weight: 600;
                color: var(--artdeco-fg-primary);
                font-size: var(--artdeco-text-sm);
            }
            .template-desc {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-xs);
                color: var(--artdeco-fg-muted);
            }
        }
    }

    .code-card {
        .editor-controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--artdeco-spacing-4);
            margin-bottom: var(--artdeco-spacing-4);
        }
        .control-row {
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
        .color-picker {
            display: flex;
            gap: var(--artdeco-spacing-2);
            .color-btn {
                width: 28px;
                height: 28px;
                border: 2px solid transparent;
                border-radius: var(--artdeco-radius-none);
                cursor: pointer;
                transition: all var(--artdeco-transition-base);
                &:hover {
                    transform: scale(1.1);
                }
                &.active {
                    border-color: var(--artdeco-gold-primary);
                    box-shadow: 0 0 8px rgba(212, 175, 55, 0.5);
                }
            }
        }
        .code-editor {
            border: 1px solid rgba(212, 175, 55, 0.2);
            border-radius: var(--artdeco-radius-none);
            overflow: hidden;
            margin-bottom: var(--artdeco-spacing-3);
            .editor-tabs {
                display: flex;
                background: var(--artdeco-bg-card);
                border-bottom: 1px solid rgba(212, 175, 55, 0.1);
            }
            .editor-tab {
                padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
                background: transparent;
                border: none;
                color: var(--artdeco-fg-muted);
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-sm);
                cursor: pointer;
                transition: all var(--artdeco-transition-base);
                &:hover {
                    color: var(--artdeco-gold-primary);
                }
                &.active {
                    color: var(--artdeco-gold-primary);
                    background: rgba(212, 175, 55, 0.05);
                }
            }
            .code-area {
                min-height: 400px;
            }
            .editor-actions {
                display: flex;
                justify-content: flex-end;
                gap: var(--artdeco-spacing-2);
                padding: var(--artdeco-spacing-3);
                background: var(--artdeco-bg-card);
                border-top: 1px solid rgba(212, 175, 55, 0.1);
            }
        }
    }

    .params-card .params-definition {
        .param-header {
            margin-bottom: var(--artdeco-spacing-3);
        }
        .param-list {
            display: flex;
            flex-direction: column;
            gap: var(--artdeco-spacing-3);
        }
        .param-item {
            padding: var(--artdeco-spacing-3);
            background: var(--artdeco-bg-global);
            border: 1px solid rgba(212, 175, 55, 0.1);
            border-radius: var(--artdeco-radius-none);
        }
        .param-row {
            display: grid;
            grid-template-columns: 100px 100px 80px 70px 70px 30px;
            gap: var(--artdeco-spacing-2);
            margin-bottom: var(--artdeco-spacing-2);
        }
        .param-name-input,
        .param-type-select,
        .param-default-input,
        .param-range-input {
            font-size: var(--artdeco-text-sm);
        }
        .remove-param-btn {
            width: 24px;
            height: 24px;
            background: transparent;
            border: 1px solid rgba(255, 82, 82, 0.3);
            border-radius: var(--artdeco-radius-none);
            color: var(--artdeco-down);
            font-size: 16px;
            cursor: pointer;
            &:hover {
                background: rgba(255, 82, 82, 0.1);
                border-color: var(--artdeco-down);
            }
        }
        .param-desc-input {
            font-size: var(--artdeco-text-sm);
        }
    }

    .screener-layout {
        display: grid;
        grid-template-columns: 1fr 300px;
        gap: var(--artdeco-spacing-4);
    }

    .filter-card {
        .filter-sections {
            display: flex;
            flex-direction: column;
            gap: var(--artdeco-spacing-5);
        }
        .filter-section h4 {
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-base);
            color: var(--artdeco-gold-primary);
            margin: 0 0 var(--artdeco-spacing-3) 0;
            padding-bottom: var(--artdeco-spacing-2);
            border-bottom: 1px solid rgba(212, 175, 55, 0.1);
        }
        .filter-row {
            display: flex;
            flex-direction: column;
            gap: var(--artdeco-spacing-2);
            margin-bottom: var(--artdeco-spacing-3);
            label {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-sm);
                font-weight: 600;
                color: var(--artdeco-fg-secondary);
            }
        }
        .range-inputs {
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-2);
            .range-separator {
                color: var(--artdeco-fg-muted);
                font-weight: 600;
            }
        }
        .indicator-filters {
            display: flex;
            flex-direction: column;
            gap: var(--artdeco-spacing-2);
            margin-bottom: var(--artdeco-spacing-3);
        }
        .indicator-filter-row {
            display: grid;
            grid-template-columns: 1fr 80px 80px 30px;
            gap: var(--artdeco-spacing-2);
            align-items: center;
            .indicator-select,
            .operator-select,
            .value-input {
                font-size: var(--artdeco-text-sm);
            }
            .remove-filter-btn {
                width: 24px;
                height: 24px;
                background: transparent;
                border: 1px solid rgba(255, 82, 82, 0.3);
                border-radius: var(--artdeco-radius-none);
                color: var(--artdeco-down);
                font-size: 16px;
                cursor: pointer;
                &:hover {
                    background: rgba(255, 82, 82, 0.1);
                }
            }
        }
        .filter-actions {
            display: flex;
            justify-content: flex-end;
            gap: var(--artdeco-spacing-3);
            margin-top: var(--artdeco-spacing-4);
            padding-top: var(--artdeco-spacing-4);
            border-top: 1px solid rgba(212, 175, 55, 0.1);
        }
    }

    .templates-card .template-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--artdeco-spacing-3);
    }

    .template-item {
        padding: var(--artdeco-spacing-3);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);
        cursor: pointer;
        transition: all var(--artdeco-transition-base);
        text-align: center;
        &:hover {
            border-color: var(--artdeco-gold-primary);
            background: rgba(212, 175, 55, 0.05);
        }
        &.active {
            border-color: var(--artdeco-gold-primary);
            background: rgba(212, 175, 55, 0.1);
        }
        .template-icon {
            font-size: var(--artdeco-text-2xl);
            margin-bottom: var(--artdeco-spacing-2);
        }
        .template-name {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            font-weight: 600;
            color: var(--artdeco-fg-primary);
            margin-bottom: var(--artdeco-spacing-1);
        }
        .template-stats {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-xs);
            color: var(--artdeco-gold-primary);
        }
    }

    .results-layout {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-4);
    }

    .results-card {
        .results-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
        }
        .results-info {
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-4);
            .results-count {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-base);
                font-weight: 600;
                color: var(--artdeco-gold-primary);
            }
            .results-time {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-muted);
            }
        }
        .results-actions {
            display: flex;
            gap: var(--artdeco-spacing-2);
        }
    }

    .metrics-card {
        .metrics-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: var(--artdeco-spacing-6);
            margin-bottom: var(--artdeco-spacing-5);
        }
        .metric-section h4 {
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-base);
            color: var(--artdeco-gold-primary);
            margin: 0 0 var(--artdeco-spacing-3) 0;
        }
        .distribution-chart .distribution-bars {
            display: flex;
            justify-content: space-around;
            align-items: flex-end;
            height: 150px;
            padding: var(--artdeco-spacing-3);
            background: var(--artdeco-bg-global);
            border: 1px solid rgba(212, 175, 55, 0.1);
            border-radius: var(--artdeco-radius-none);
        }
        .dist-bar {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: var(--artdeco-spacing-1);
            .bar-fill {
                width: 50px;
                background: linear-gradient(180deg, var(--artdeco-gold-primary), rgba(212, 175, 55, 0.3));
                border-radius: var(--artdeco-radius-none) var(--artdeco-radius-none) 0 0;
                transition: height var(--artdeco-transition-base);
            }
            &.rise .bar-fill {
                background: linear-gradient(180deg, var(--artdeco-up), rgba(255, 82, 82, 0.3));
            }
            &.fall .bar-fill {
                background: linear-gradient(180deg, var(--artdeco-down), rgba(0, 230, 118, 0.3));
            }
            .bar-label {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-secondary);
            }
            .bar-value {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-xs);
                color: var(--artdeco-gold-primary);
            }
        }
        .industry-list {
            display: flex;
            flex-direction: column;
            gap: var(--artdeco-spacing-3);
        }
        .industry-item {
            display: grid;
            grid-template-columns: 80px 1fr 50px;
            gap: var(--artdeco-spacing-2);
            align-items: center;
            .industry-name {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-secondary);
            }
            .industry-bar {
                height: 8px;
                background: var(--artdeco-bg-global);
                border-radius: var(--artdeco-radius-none);
                overflow: hidden;
                .bar-fill {
                    height: 100%;
                    background: linear-gradient(90deg, var(--artdeco-gold-primary), var(--artdeco-gold-hover));
                    border-radius: var(--artdeco-radius-none);
                }
            }
            .industry-count {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-xs);
                color: var(--artdeco-fg-muted);
                text-align: right;
            }
        }
        .metrics-summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: var(--artdeco-spacing-3);
        }
    }

    .chart-card {
        .stock-detail-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-4);
            padding-bottom: var(--artdeco-spacing-3);
            border-bottom: 1px solid rgba(212, 175, 55, 0.1);
        }
        .stock-info {
            display: flex;
            align-items: baseline;
            gap: var(--artdeco-spacing-3);
            .stock-price {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-2xl);
                font-weight: 600;
                &.rise {
                    color: var(--artdeco-up);
                }
                &.fall {
                    color: var(--artdeco-down);
                }
            }
            .stock-change {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-lg);
                font-weight: 600;
                &.rise {
                    color: var(--artdeco-up);
                }
                &.fall {
                    color: var(--artdeco-down);
                }
            }
        }
        .stock-indicators {
            display: flex;
            gap: var(--artdeco-spacing-2);
            .indicator-tag {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-xs);
                color: var(--artdeco-gold-primary);
                background: rgba(212, 175, 55, 0.1);
                padding: 4px 8px;
                border-radius: var(--artdeco-radius-none);
            }
        }
        .stock-chart {
            background: var(--artdeco-bg-global);
            border: 1px solid rgba(212, 175, 55, 0.2);
            border-radius: var(--artdeco-radius-none);
            padding: var(--artdeco-spacing-3);
        }
    }

    @media (max-width: 1400px) {
        .indicators-layout,
        .editor-layout,
        .screener-layout {
            grid-template-columns: 1fr;
        }
        .category-card,
        .template-card {
            display: none;
        }
    }
</style>
