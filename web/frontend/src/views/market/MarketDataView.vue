<template>
  <div class="market-data-view">
    <!-- 页面头部 -->
    <el-page-header class="page-header" @back="goBack">
      <template #content>
        <div class="header-content">
          <el-icon class="header-icon">
            <DataLine />
          </el-icon>
          <span class="header-title">市场数据</span>
        </div>
      </template>
      <template #extra>
        <el-space>
          <el-tag type="success">实时数据</el-tag>
          <el-text type="info">{{ currentTime }}</el-text>
        </el-space>
      </template>
    </el-page-header>

    <!-- Tab选项卡 -->
    <el-card class="main-card" shadow="never">
      <el-tabs v-model="activeTab" type="border-card" class="market-tabs">
        <el-tab-pane label="资金流向" name="fund-flow">
          <template #label>
            <span class="tab-label">
              <el-icon><Money /></el-icon>
              资金流向
            </span>
          </template>
          <FundFlowPanel />
        </el-tab-pane>

        <el-tab-pane label="ETF行情" name="etf-data">
          <template #label>
            <span class="tab-label">
              <el-icon><TrendCharts /></el-icon>
              ETF行情
            </span>
          </template>
          <ETFDataTable />
        </el-tab-pane>

        <el-tab-pane label="竞价抢筹" name="chip-race">
          <template #label>
            <span class="tab-label">
              <el-icon><ShoppingCart /></el-icon>
              竞价抢筹
            </span>
          </template>
          <ChipRaceTable />
        </el-tab-pane>

        <el-tab-pane label="龙虎榜" name="longhubang">
          <template #label>
            <span class="tab-label">
              <el-icon><Flag /></el-icon>
              龙虎榜
            </span>
          </template>
          <LongHuBangTable />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import {
  DataLine,
  Money,
  TrendCharts,
  ShoppingCart,
  Flag
} from '@element-plus/icons-vue'

// 导入组件
import FundFlowPanel from '@/components/market/FundFlowPanel.vue'
import ETFDataTable from '@/components/market/ETFDataTable.vue'
import ChipRaceTable from '@/components/market/ChipRaceTable.vue'
import LongHuBangTable from '@/components/market/LongHuBangTable.vue'

// 路由
const router = useRouter()

// 响应式数据
const activeTab = ref('fund-flow')
const currentTime = ref('')

// 返回上一页
const goBack = () => {
  router.back()
}

// 更新当前时间
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 定时器
let timeInterval = null

// 组件挂载
onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
})

// 组件卸载
onBeforeUnmount(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
.market-data-view {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  font-size: 24px;
  color: #409eff;
}

.header-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.main-card {
  border-radius: 8px;
}

.market-tabs {
  border: none;
  box-shadow: none;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

:deep(.el-tabs__header) {
  background: white;
  border-bottom: 2px solid #e4e7ed;
  margin-bottom: 0;
}

:deep(.el-tabs__item) {
  height: 50px;
  line-height: 50px;
  font-size: 15px;
  font-weight: 500;
}

:deep(.el-tabs__item:hover) {
  color: #409eff;
}

:deep(.el-tabs__item.is-active) {
  color: #409eff;
  font-weight: 600;
}

:deep(.el-tabs__content) {
  padding: 0;
}
</style>
