<template>
  <div class="portfolio-overview">
    <div class="stats-grid">
      <BloombergStatCard
        label="TOTAL ASSETS"
        :value="portfolio.total_assets"
        icon="wallet"
        format="currency"
      />

      <BloombergStatCard
        label="AVAILABLE CASH"
        :value="portfolio.available_cash"
        icon="coin"
        trend="down"
        format="currency"
      />

      <BloombergStatCard
        label="POSITION VALUE"
        :value="portfolio.position_value"
        icon="chart"
        trend="neutral"
        format="currency"
      />

      <BloombergStatCard
        label="TOTAL PROFIT"
        :value="portfolio.total_profit"
        :change="portfolio.profit_rate"
        :icon="portfolio.total_profit >= 0 ? 'trending-up' : 'trending-down'"
        :trend="portfolio.total_profit >= 0 ? 'up' : 'down'"
        format="currency"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import BloombergStatCard from '@/components/BloombergStatCard.vue'

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

defineExpose({
  setPortfolio: (data: Portfolio) => {
    Object.assign(portfolio, data)
  }
})
</script>

<style scoped lang="scss">
// ============================================
//   Bloomberg Terminal Style Portfolio Overview
// ============================================

.portfolio-overview {
  width: 100%;
  margin-bottom: 8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;

  @media (max-width: 1440px) {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
