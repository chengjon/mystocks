<template>
  <div class="strategy-management">
    <div class="page-header">
      <h1>📈 股票策略管理</h1>
      <p class="subtitle">基于InStock经典策略的智能选股系统，支持10个经典策略</p>
    </div>

    <!-- 功能导航标签 -->
    <el-tabs v-model="activeTab" type="border-card" class="strategy-tabs">
      <!-- 1. 策略列表 -->
      <el-tab-pane name="list" label="策略列表">
        <template #label>
          <span><el-icon><List /></el-icon> 策略列表</span>
        </template>
        <StrategyList @run-strategy="handleRunStrategy" />
      </el-tab-pane>

      <!-- 2. 单只运行 -->
      <el-tab-pane name="single" label="单只运行">
        <template #label>
          <span><el-icon><Search /></el-icon> 单只运行</span>
        </template>
        <SingleRun :initial-strategy="selectedStrategy" />
      </el-tab-pane>

      <!-- 3. 批量扫描 -->
      <el-tab-pane name="batch" label="批量扫描">
        <template #label>
          <span><el-icon><Operation /></el-icon> 批量扫描</span>
        </template>
        <BatchScan />
      </el-tab-pane>

      <!-- 4. 结果查询 -->
      <el-tab-pane name="results" label="结果查询">
        <template #label>
          <span><el-icon><Document /></el-icon> 结果查询</span>
        </template>
        <ResultsQuery />
      </el-tab-pane>

      <!-- 5. 统计分析 -->
      <el-tab-pane name="stats" label="统计分析">
        <template #label>
          <span><el-icon><DataAnalysis /></el-icon> 统计分析</span>
        </template>
        <StatsAnalysis />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { List, Search, Operation, Document, DataAnalysis } from '@element-plus/icons-vue'
import StrategyList from './strategy/StrategyList.vue'
import SingleRun from './strategy/SingleRun.vue'
import BatchScan from './strategy/BatchScan.vue'
import ResultsQuery from './strategy/ResultsQuery.vue'
import StatsAnalysis from './strategy/StatsAnalysis.vue'

// 当前激活的标签页
const activeTab = ref('list')

// 选中的策略（用于从策略列表跳转到单只运行）
const selectedStrategy = ref(null)

// 处理从策略列表运行策略的事件
const handleRunStrategy = (strategy) => {
  selectedStrategy.value = strategy
  activeTab.value = 'single'
}
</script>

<style scoped lang="scss">
.strategy-management {
  padding: 20px;

  .page-header {
    margin-bottom: 20px;

    h1 {
      font-size: 28px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 8px 0;
    }

    .subtitle {
      font-size: 14px;
      color: #909399;
      margin: 0;
    }
  }

  .strategy-tabs {
    background: #fff;
    border-radius: 8px;

    :deep(.el-tabs__header) {
      margin: 0;
    }

    :deep(.el-tabs__item) {
      font-size: 15px;
      padding: 0 20px;

      .el-icon {
        margin-right: 5px;
      }
    }
  }
}
</style>
