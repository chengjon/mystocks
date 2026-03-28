<template>
  <div class="backtest-wizard layout-compact">
    <!-- ArtDeco Header -->
    <div class="wizard-header">
      <h1 class="page-title">STRATEGY BACKTESTING WIZARD</h1>
      <p class="page-subtitle">向导式策略回测流程</p>
    </div>

    <!-- Progress Indicator -->
    <div class="wizard-progress">
      <div
        v-for="(step, index) in wizardSteps"
        :key="step.id"
        :class="['step-item', { active: currentStep === index, completed: currentStep > index }]"
      >
        <div class="step-number">{{ index + 1 }}</div>
        <div class="step-label">{{ step.label }}</div>
      </div>
    </div>

    <!-- Step Content -->
    <div class="wizard-content">
        <!-- Step 1: Select Strategy Template -->
      <div v-if="currentStep === 0" class="step-content">
        <ArtDecoCardCompact>
          <template #header>
            <h3>选择策略模板</h3>
          </template>
          <div class="strategy-selection-container">
            <!-- Quick Templates -->
            <div class="quick-templates-section">
              <h4 class="section-title">快速模板</h4>
              <div class="strategy-grid">
                <div
                  v-for="(template, _idx) in quickTemplates"
                  :key="template.id"
                  :class="['strategy-card', { selected: selectedStrategy === template.id }]"
                  @click="selectStrategy(template.id)"
                >
                  <div class="strategy-icon">
                    <el-icon size="32"><TrendCharts /></el-icon>
                  </div>
                  <div class="strategy-info">
                    <div class="strategy-name">{{ template.name }}</div>
                    <div class="strategy-desc">{{ template.description }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- My Templates -->
            <div v-if="customTemplates.length > 0" class="my-templates-section">
              <h4 class="section-title">历史模板</h4>
              <div class="strategy-grid">
                <div
                  v-for="(template, _idx) in customTemplates"
                  :key="template.id"
                  :class="['strategy-card', { selected: selectedStrategy === template.id }]"
                  @click="selectStrategy(template.id)"
                >
                  <div class="strategy-icon">
                    <el-icon size="32"><FolderOpened /></el-icon>
                  </div>
                  <div class="strategy-info">
                    <div class="strategy-name">{{ template.name }}</div>
                    <div class="strategy-desc">{{ template.description }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Save Template Button -->
            <el-button @click="showSaveTemplateDialog = true" class="artdeco-gold-cta">
              <el-icon><Plus /></el-icon> 保存模板
            </el-button>
          </div>
        </ArtDecoCardCompact>
      </div>
    </div>

    <!-- Step 2.5: Compare Parameters -->
    <div v-if="currentStep === 2.5" class="step-content">
      <ArtDecoCardCompact>
        <template #header>
          <h3>参数对比与选择</h3>
        </template>
        <div class="compare-selection">
          <div class="selection-item">
            <label>选择回测1：</label>
            <el-select v-model="selectedBacktest1" placeholder="请选择回测1" filterable>
              <el-option
                v-for="(bt, _idx) in backtestHistory"
                :key="bt.id"
                :label="bt.name"
                :value="bt.id"
              >
                {{ bt.name }}
              </el-option>
            </el-select>
          </div>
          <div class="selection-item">
            <label>选择回测2：</label>
            <el-select v-model="selectedBacktest2" placeholder="请选择回测2" filterable>
              <el-option
                v-for="(bt, _idx) in backtestHistory"
                :key="bt.id"
                :label="bt.name"
                :value="bt.id"
              >
                {{ bt.name }}
              </el-option>
            </el-select>
          </div>
        </div>

        <!-- Comparison Table -->
        <div class="comparison-table-container">
          <el-table :data="comparisonData?.diffData || []" border stripe>
            <el-table-column prop="param" label="参数" width="180" />
            <el-table-column prop="backtest1Value" label="回测1" width="120" />
            <el-table-column prop="backtest2Value" label="回测2" width="120" />
            <el-table-column prop="difference" label="差异" width="100">
              <template #default="{ row }">
                <span :class="['diff-value', { 'diff-better': row.highlight && row.difference > 0, 'diff-worse': row.difference < 0 }]">
                  {{ row.difference }}
                </span>
              </template>
          </el-table-column>
        </el-table>
      </div>
      </ArtDecoCardCompact>
    </div>

    <!-- Step 3: Review and Run -->
    <div v-if="currentStep === 2" class="step-content">
      <ArtDecoCardCompact>
        <template #header>
          <h3>确认回测配置</h3>
        </template>
        <div class="review-content">
          <div class="review-item">
            <span class="review-label">策略模板：</span>
            <span class="review-value">{{ getSelectedStrategyName() }}</span>
          </div>
          <div class="review-item">
            <span class="review-label">短期MA周期：</span>
            <span class="review-value">{{ backtestParams.shortMA }}</span>
          </div>
          <div class="review-item">
            <span class="review-label">长期MA周期：</span>
            <span class="review-value">{{ backtestParams.longMA }}</span>
          </div>
          <div class="review-item">
            <span class="review-label">开始日期：</span>
            <span class="review-value">{{ formatDate(backtestParams.startDate) }}</span>
          </div>
          <div class="review-item">
            <span class="review-label">结束日期：</span>
            <span class="review-value">{{ formatDate(backtestParams.endDate) }}</span>
          </div>
          <div class="review-item">
            <span class="review-label">股票代码：</span>
            <span class="review-value">{{ backtestParams.symbols }}</span>
          </div>
        </div>
      </ArtDecoCardCompact>
    </div>

    <!-- Step 4: Results -->
    <div v-if="currentStep === 3" class="step-content">
      <ArtDecoCardCompact>
        <template #header>
          <h3>回测结果</h3>
        </template>
        <div class="results-content">
          <!-- Metrics -->
          <div class="results-metrics">
            <div class="metric-card">
              <div class="metric-label">总收益率</div>
              <div class="metric-value change-up">{{ backtestResults.totalReturn }}%</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">夏普比率</div>
              <div class="metric-value">{{ backtestResults.sharpeRatio }}</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">最大回撤</div>
              <div class="metric-value change-down">{{ backtestResults.maxDrawdown }}%</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">胜率</div>
              <div class="metric-value">{{ backtestResults.winRate }}%</div>
            </div>
          </div>

          <!-- Chart -->
          <div ref="backtestChartRef" class="backtest-chart"></div>
        </div>
      </ArtDecoCardCompact>
    </div>

    <!-- Navigation Buttons -->
    <div class="wizard-navigation">
      <el-button
        v-if="currentStep > 0"
        @click="prevStep"
        class="artdeco-gold-cta"
        plain
      >
        上一步
      </el-button>
      <el-button
        v-if="currentStep < 4"
        @click="nextStep"
        class="artdeco-gold-cta"
        :disabled="!canProceed"
      >
        {{ currentStep === 2.5 ? '开始对比' : '下一步' }}
      </el-button>
      <el-button
        v-if="currentStep === 3"
        @click="resetWizard"
        class="artdeco-gold-cta"
        plain
      >
        重新开始
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import ArtDecoCardCompact from '@/components/artdeco/base/ArtDecoCardCompact.vue'
import { useBacktestWizard } from './composables/useBacktestWizard'

const {
  wizardSteps,
  currentStep,
  selectedStrategy,
  quickTemplates,
  customTemplates,
  showSaveTemplateDialog,
  backtestParams,
  backtestResults,
  backtestHistory,
  selectedBacktest1,
  selectedBacktest2,
  comparisonData,
  backtestChartRef,
  canProceed,
  selectStrategy,
  nextStep,
  prevStep,
  resetWizard,
  getSelectedStrategyName,
  formatDate
} = useBacktestWizard()
</script>

<style scoped lang="scss">
@use "./styles/BacktestWizard.scss" as *;
</style>
