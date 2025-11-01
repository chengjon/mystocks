<template>
  <div class="market-data-view">
    <el-tabs v-model="activeTab" class="market-tabs">
      <!-- 资金流向 -->
      <el-tab-pane label="资金流向" name="fund-flow">
        <FundFlowPanel />
      </el-tab-pane>

      <!-- ETF数据 -->
      <el-tab-pane label="ETF行情" name="etf">
        <ETFDataPanel />
      </el-tab-pane>

      <!-- 竞价抢筹 -->
      <el-tab-pane label="竞价抢筹" name="chip-race">
        <ChipRacePanel />
      </el-tab-pane>

      <!-- 龙虎榜 -->
      <el-tab-pane label="龙虎榜" name="lhb">
        <LongHuBangPanel />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import FundFlowPanel from '@/components/market/FundFlowPanel.vue'
import ETFDataPanel from '@/components/market/ETFDataPanel.vue'
import ChipRacePanel from '@/components/market/ChipRacePanel.vue'
import LongHuBangPanel from '@/components/market/LongHuBangPanel.vue'

const activeTab = ref('fund-flow')
</script>

<style scoped lang="scss">
.market-data-view {
  padding: 20px;
  height: calc(100vh - 100px);

  .market-tabs {
    height: 100%;

    :deep(.el-tabs__content) {
      height: calc(100% - 55px);
      overflow-y: auto;
    }
  }
}
</style>
