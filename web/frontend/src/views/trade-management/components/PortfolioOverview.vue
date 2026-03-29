<template>
  <div class="portfolio-overview">
    <div class="stats-grid">
      <ArtDecoStatCard
        label="TOTAL ASSETS"
        :value="formatCurrency(portfolio.total_assets)"
        variant="gold"
        :show-change="false"
      >
        <template #icon>
          <el-icon><Wallet /></el-icon>
        </template>
      </ArtDecoStatCard>

      <ArtDecoStatCard
        label="AVAILABLE CASH"
        :value="formatCurrency(portfolio.available_cash)"
        variant="gold"
        :show-change="false"
      >
        <template #icon>
          <el-icon><Coin /></el-icon>
        </template>
      </ArtDecoStatCard>

      <ArtDecoStatCard
        label="POSITION VALUE"
        :value="formatCurrency(portfolio.position_value)"
        variant="gold"
        :show-change="false"
      >
        <template #icon>
          <el-icon><DataLine /></el-icon>
        </template>
      </ArtDecoStatCard>

      <ArtDecoStatCard
        label="TOTAL PROFIT"
        :value="formatCurrency(portfolio.total_profit)"
        :change="portfolio.profit_rate"
        :variant="portfolio.total_profit >= 0 ? 'rise' : 'fall'"
      >
        <template #icon>
          <el-icon>
            <TrendCharts v-if="portfolio.total_profit >= 0" />
            <DataAnalysis v-else />
          </el-icon>
        </template>
      </ArtDecoStatCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { Coin, DataAnalysis, DataLine, TrendCharts, Wallet } from '@element-plus/icons-vue'
import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'

interface Portfolio {
  total_assets: number
  available_cash: number
  position_value: number
  total_profit: number
  profit_rate: number
}

const portfolio = reactive<Portfolio>({
  total_assets: 1000000,
  available_cash: 500000,
  position_value: 500000,
  total_profit: 50000,
  profit_rate: 5.0
})

const formatCurrency = (value: number) =>
  `¥${value.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })}`

defineExpose({
  setPortfolio: (data: Portfolio) => {
    Object.assign(portfolio, data)
  }
})
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.portfolio-overview {
  width: 100%;
  margin-bottom: var(--artdeco-spacing-2);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--artdeco-spacing-5);

  @media (width <= 90rem) {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
