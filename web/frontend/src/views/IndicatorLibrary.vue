<template>
  <div class="indicator-library">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>技术指标库</h1>
      <p class="subtitle">共161个TA-Lib技术指标，涵盖趋势、动量、波动率、成交量和K线形态5大类</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-card shadow="hover" class="stat-card">
        <div class="stat-content">
          <el-icon class="stat-icon" color="#409eff"><DataLine /></el-icon>
          <div class="stat-info">
            <div class="stat-value">{{ registry?.total_count || 0 }}</div>
            <div class="stat-label">总指标数</div>
          </div>
        </div>
      </el-card>

      <el-card
        v-for="(count, category) in registry?.categories"
        :key="category"
        shadow="hover"
        class="stat-card"
      >
        <div class="stat-content">
          <el-icon class="stat-icon" :color="getCategoryColor(category)">
            <component :is="getCategoryIcon(category)" />
          </el-icon>
          <div class="stat-info">
            <div class="stat-value">{{ count }}</div>
            <div class="stat-label">{{ getCategoryLabel(category) }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-input
            v-model="searchQuery"
            placeholder="搜索指标名称、缩写或描述..."
            :prefix-icon="Search"
            clearable
            size="large"
          />
        </el-col>
        <el-col :span="12">
          <el-select
            v-model="selectedCategory"
            placeholder="选择分类"
            clearable
            size="large"
            style="width: 100%"
          >
            <el-option label="全部分类" value="" />
            <el-option label="趋势指标" value="trend" />
            <el-option label="动量指标" value="momentum" />
            <el-option label="波动率指标" value="volatility" />
            <el-option label="成交量指标" value="volume" />
            <el-option label="K线形态" value="candlestick" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <!-- 指标列表 -->
    <div v-loading="loading" class="indicators-container">
      <el-card
        v-for="indicator in filteredIndicators"
        :key="indicator.abbreviation"
        class="indicator-detail-card"
        shadow="hover"
      >
        <template #header>
          <div class="indicator-header">
            <div class="indicator-title-group">
              <span class="indicator-abbr">{{ indicator.abbreviation }}</span>
              <el-tag :type="getCategoryTagType(indicator.category)" size="small">
                {{ getCategoryLabel(indicator.category) }}
              </el-tag>
              <el-tag :type="getPanelTagType(indicator.panel_type)" size="small">
                {{ getPanelLabel(indicator.panel_type) }}
              </el-tag>
            </div>
          </div>
        </template>

        <div class="indicator-content">
          <!-- 基本信息 -->
          <div class="info-section">
            <h3>{{ indicator.full_name }}</h3>
            <h4>{{ indicator.chinese_name }}</h4>
            <p class="description">{{ indicator.description }}</p>
          </div>

          <!-- 参数说明 -->
          <div v-if="indicator.parameters && indicator.parameters.length > 0" class="params-section">
            <h4 class="section-title">
              <el-icon><Setting /></el-icon>
              参数配置
            </h4>
            <el-table :data="indicator.parameters" size="small" border>
              <el-table-column prop="display_name" label="参数名" width="120" />
              <el-table-column prop="type" label="类型" width="80" />
              <el-table-column prop="default" label="默认值" width="80" />
              <el-table-column label="范围" width="100">
                <template #default="{ row }">
                  {{ row.min !== undefined ? `[${row.min}, ${row.max}]` : '-' }}
                </template>
              </el-table-column>
              <el-table-column prop="description" label="说明" />
            </el-table>
          </div>

          <!-- 输出说明 -->
          <div class="outputs-section">
            <h4 class="section-title">
              <el-icon><TrendCharts /></el-icon>
              输出字段
            </h4>
            <el-descriptions :column="2" size="small" border>
              <el-descriptions-item
                v-for="(output, idx) in indicator.outputs"
                :key="idx"
                :label="output.name"
              >
                {{ output.description }}
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 参考线 -->
          <div v-if="indicator.reference_lines && indicator.reference_lines.length > 0" class="reference-section">
            <h4 class="section-title">
              <el-icon><Position /></el-icon>
              参考线
            </h4>
            <el-space wrap>
              <el-tag
                v-for="(line, idx) in indicator.reference_lines"
                :key="idx"
                type="info"
                effect="plain"
              >
                {{ line }}
              </el-tag>
            </el-space>
          </div>

          <!-- 最小数据点 -->
          <div class="min-data-section">
            <el-text size="small" type="info">
              <el-icon><InfoFilled /></el-icon>
              最小数据点: {{ indicator.min_data_points_formula }}
            </el-text>
          </div>
        </div>
      </el-card>

      <!-- 无结果提示 -->
      <el-empty v-if="filteredIndicators.length === 0 && !loading" description="未找到匹配的指标" />
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck

import { ref, computed, onMounted, type Ref, type ComputedRef } from 'vue'
import { ElMessage } from 'element-plus'
import type { Component } from 'vue'
import {
  Search,
  DataLine,
  TrendCharts,
  Setting,
  Position,
  InfoFilled,
  Histogram,
  Connection,
  Timer,
  PieChart
} from '@element-plus/icons-vue'
import { indicatorService } from '@/services/indicatorService'

// ============================================
// 类型定义
// ============================================

/**
 * 指标元数据
 */
interface IndicatorMetadata {
  abbreviation: string
  full_name: string
  chinese_name: string
  category: string
  description: string
  panel_type: 'overlay' | 'separate'
  parameters?: any[]
}

/**
 * 指标注册表
 */
interface IndicatorRegistry {
  indicators: IndicatorMetadata[]
  total_count: number
}

/**
 * 分类类型
 */
type CategoryType = 'trend' | 'momentum' | 'volatility' | 'volume' | 'candlestick'

/**
 * 面板类型
 */
type PanelType = 'overlay' | 'separate'

/**
 * Element Plus 标签类型
 */
type TagType = 'primary' | 'success' | 'warning' | 'info' | 'danger' | ''

// ============================================
// 状态管理
// ============================================

const loading: Ref<boolean> = ref(false)
const registry: Ref<IndicatorRegistry | null> = ref(null)
const searchQuery: Ref<string> = ref('')
const selectedCategory: Ref<string> = ref('')

// ============================================
// 生命周期与方法
// ============================================

/**
 * 组件挂载时获取指标注册表
 */
onMounted(async (): Promise<void> => {
  await fetchIndicatorRegistry()
})

/**
 * 获取指标注册表
 */
const fetchIndicatorRegistry = async (): Promise<void> => {
  loading.value = true
  try {
    registry.value = await indicatorService.getRegistry()
  } catch (error: any) {
    console.error('Failed to fetch indicator registry:', error)
    ElMessage.error('加载指标库失败')
  } finally {
    loading.value = false
  }
}

/**
 * 过滤指标
 */
const filteredIndicators: ComputedRef<IndicatorMetadata[]> = computed(() => {
  if (!registry.value?.indicators) return []

  let indicators = registry.value.indicators

  // 分类过滤
  if (selectedCategory.value) {
    indicators = indicators.filter(ind => ind.category === selectedCategory.value)
  }

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    indicators = indicators.filter(ind => {
      return (
        ind.abbreviation.toLowerCase().includes(query) ||
        ind.full_name.toLowerCase().includes(query) ||
        ind.chinese_name.includes(query) ||
        ind.description.toLowerCase().includes(query)
      )
    })
  }

  return indicators
})

/**
 * 获取分类标签类型
 */
const getCategoryTagType = (category: string): TagType => {
  const typeMap: Record<string, TagType> = {
    trend: 'primary',
    momentum: 'success',
    volatility: 'warning',
    volume: 'info',
    candlestick: 'danger'
  }
  return typeMap[category] || 'info'
}

/**
 * 获取面板类型标签
 */
const getPanelTagType = (panelType: PanelType): TagType => {
  return panelType === 'overlay' ? '' : 'warning'
}

/**
 * 获取面板类型标签文本
 */
const getPanelLabel = (panelType: PanelType): string => {
  return panelType === 'overlay' ? '主图叠加' : '独立面板'
}

/**
 * 获取分类标签文本
 */
const getCategoryLabel = (category: string): string => {
  const labelMap: Record<string, string> = {
    trend: '趋势',
    momentum: '动量',
    volatility: '波动率',
    volume: '成交量',
    candlestick: 'K线形态'
  }
  return labelMap[category] || category
}

/**
 * 获取分类颜色
 */
const getCategoryColor = (category: string): string => {
  const colorMap: Record<string, string> = {
    trend: '#409eff',
    momentum: '#67c23a',
    volatility: '#e6a23c',
    volume: '#909399',
    candlestick: '#f56c6c'
  }
  return colorMap[category] || '#909399'
}

/**
 * 获取分类图标
 */
const getCategoryIcon = (category: string): Component => {
  const iconMap: Record<string, Component> = {
    trend: TrendCharts,
    momentum: Connection,
    volatility: Histogram,
    volume: PieChart,
    candlestick: Timer
  }
  return iconMap[category] || DataLine
}
</script>

<style scoped lang="scss">
.indicator-library {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;

  .page-header {
    margin-bottom: 24px;

    h1 {
      margin: 0 0 8px 0;
      font-size: 28px;
      font-weight: 700;
      color: #303133;
    }

    .subtitle {
      margin: 0;
      font-size: 14px;
      color: #909399;
    }
  }

  .stats-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 24px;

    .stat-card {
      .stat-content {
        display: flex;
        align-items: center;
        gap: 16px;

        .stat-icon {
          font-size: 48px;
        }

        .stat-info {
          flex: 1;

          .stat-value {
            font-size: 32px;
            font-weight: 700;
            color: #303133;
            line-height: 1.2;
          }

          .stat-label {
            margin-top: 4px;
            font-size: 14px;
            color: #909399;
          }
        }
      }
    }
  }

  .search-card {
    margin-bottom: 24px;
  }

  .indicators-container {
    display: grid;
    gap: 20px;

    .indicator-detail-card {
      .indicator-header {
        .indicator-title-group {
          display: flex;
          align-items: center;
          gap: 12px;

          .indicator-abbr {
            font-size: 20px;
            font-weight: 700;
            color: #409eff;
          }
        }
      }

      .indicator-content {
        display: flex;
        flex-direction: column;
        gap: 20px;

        .info-section {
          h3 {
            margin: 0 0 4px 0;
            font-size: 18px;
            font-weight: 600;
            color: #303133;
          }

          h4 {
            margin: 0 0 12px 0;
            font-size: 16px;
            font-weight: 500;
            color: #606266;
          }

          .description {
            margin: 0;
            font-size: 14px;
            color: #909399;
            line-height: 1.8;
          }
        }

        .section-title {
          display: flex;
          align-items: center;
          gap: 8px;
          margin: 0 0 12px 0;
          font-size: 16px;
          font-weight: 600;
          color: #303133;

          .el-icon {
            color: #409eff;
          }
        }

        .min-data-section {
          padding: 12px;
          background: #f5f7fa;
          border-radius: 4px;

          .el-text {
            display: flex;
            align-items: center;
            gap: 4px;
          }
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .indicator-library {
    padding: 16px;

    .page-header {
      h1 {
        font-size: 24px;
      }
    }

    .stats-cards {
      grid-template-columns: 1fr;
    }
  }
}
</style>
