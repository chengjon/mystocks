<template>
    <!-- 页面头部 -->
    <PageHeader
      title="行业概念分析"
      subtitle="INDUSTRY CONCEPT ANALYSIS"
    />

    <!-- 主卡片 -->
    <div class="card main-card">
      <div class="card-header">
        <div class="header-title">
          <div class="title-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <line x1="8" y1="6" x2="21" y2="6"></line>
              <line x1="8" y1="12" x2="21" y2="12"></line>
              <line x1="8" y1="18" x2="21" y2="18"></line>
              <line x1="3" y1="6" x2="3.01" y2="6"></line>
              <line x1="3" y1="12" x2="3.01" y2="12"></line>
              <line x1="3" y1="18" x2="3.01" y2="18"></line>
            </svg>
          </div>
          <span class="title-text">分析面板</span>
          <span class="title-sub">ANALYSIS PANEL</span>
        </div>
        <button class="button button-primary" @click="refreshData" :class="{ loading: loading }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6"></path>
            <path d="M1 20v-6h6"></path>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
          </svg>
          刷新数据
        </button>
      </div>

      <div class="card-body">
        <!-- 筛选区域 -->
        <div class="filter-section">
          <div class="tabs">
            <button
              :class="['tab-button', { active: activeTab === 'industry' }]"
              @click="handleTabChange('industry')"
            >
              <span class="tab-icon">🏭</span>
              <span class="tab-text">行业分析</span>
            </button>
            <button
              :class="['tab-button', { active: activeTab === 'concept' }]"
              @click="handleTabChange('concept')"
            >
              <span class="tab-icon">💡</span>
              <span class="tab-text">概念分析</span>
            </button>
          </div>

          <div class="filter-controls">
            <select v-if="activeTab === 'industry'" v-model="selectedIndustry" class="select" @change="(e: Event) => handleIndustryChange((e.target as HTMLSelectElement).value)">
              <option value="">请选择行业</option>
              <option v-for="item in industryList" :key="item.industry_code" :value="item.industry_code">
                {{ item.industry_name }}
              </option>
            </select>

            <select v-if="activeTab === 'concept'" v-model="selectedConcept" class="select" @change="(e: Event) => handleConceptChange((e.target as HTMLSelectElement).value)">
              <option value="">请选择概念</option>
              <option v-for="item in conceptList" :key="item.concept_code" :value="item.concept_code">
                {{ item.concept_name }}
              </option>
            </select>

            <button class="button button-info" @click="resetFilters">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-9.75 9 9 9 0 0 0 9.75-9.75 0 0 0-9.75-9 9 0 0 0-9.75z"></path>
              </svg>
              重置筛选
            </button>
          </div>
        </div>

        <!-- 统计卡片 -->
        <div class="stats-section" v-if="currentCategory">
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-label">{{ stats[0]?.title || 'N/A' }}</div>
              <div class="stat-value" :style="{ color: stats[0]?.color || '#D4AF37' }">{{ stats[0]?.value || '-' }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">{{ stats[1]?.title || 'N/A' }}</div>
              <div class="stat-value" :style="{ color: stats[1]?.color || '#D4AF37' }">{{ stats[1]?.value || '-' }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">{{ stats[2]?.title || 'N/A' }}</div>
              <div class="stat-value" :style="{ color: stats[2]?.color || '#D4AF37' }">{{ stats[2]?.value || '-' }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">{{ stats[3]?.title || 'N/A' }}</div>
              <div class="stat-value" :style="{ color: stats[3]?.color || '#D4AF37' }">{{ stats[3]?.value || '-' }}</div>
            </div>
          </div>

          <!-- 图表区域 -->
          <div class="chart-section">
            <ChartContainer
              chart-type="pie"
              :data="pieChartData"
              :options="pieChartOptions"
              height="280px"
              :loading="stocksLoading"
            />
            <ChartContainer
              chart-type="bar"
              :data="barChartData"
              :options="barChartOptions"
              height="280px"
              :loading="stocksLoading"
            />
          </div>
        </div>

        <!-- 成分股列表 -->
        <div class="stocks-section" v-if="stocks.length > 0">
          <div class="card stocks-card">
            <div class="card-header">
              <div class="header-title">
                <span class="title-text">成分股列表</span>
              </div>
              <div class="stocks-header-actions">
                <input
                  v-model="searchKeyword"
                  placeholder="搜索股票代码或名称"
                  class="input"
                />
                <button class="button button-primary" @click="exportStocks">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                  </svg>
                  导出数据
                </button>
              </div>
            </div>
            <div class="card-body">
              <StockListTable
                :columns="tableColumns"
                :data="paginatedStocks"
                :loading="stocksLoading"
                :row-clickable="false"
              />

              <!-- 分页 -->
              <PaginationBar
                v-model:page="currentPage"
                v-model:page-size="pageSize"
                :total="stocks.length"
                :page-sizes="[10, 20, 50, 100]"
                @page-change="handleCurrentChange"
                @size-change="handleSizeChange"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import type { TableColumn } from '@/components/shared'
import { useIndustryConceptAnalysis } from './composables/useIndustryConceptAnalysis'

const {
  activeTab,
  loading,
  stocksLoading,
  industryList,
  conceptList,
  selectedIndustry,
  selectedConcept,
  currentCategory,
  stocks,
  searchKeyword,
  currentPage,
  pageSize,
  stats,
  pieChartData,
  pieChartOptions,
  barChartData,
  barChartOptions,
  tableColumns,
  paginatedStocks,
  formatPercent,
  formatPrice,
  formatVolume,
  formatAmount,
  getChangeColor,
  getChangeColorClass,
  refreshData,
  loadIndustryList,
  loadConceptList,
  loadIndustryStocks,
  loadConceptStocks,
  handleTabChange,
  handleIndustryChange,
  handleConceptChange,
  resetFilters,
  handleSizeChange,
  handleCurrentChange,
  exportStocks
} = useIndustryConceptAnalysis()
</script>

<style scoped lang="scss">
@import "./styles/IndustryConceptAnalysis";
</style>
