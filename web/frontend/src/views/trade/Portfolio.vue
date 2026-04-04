<script setup lang="ts">
import { useAttrs } from 'vue'
import TradePortfolioPage from '@/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue'

const attrs = useAttrs()
</script>

<template>
  <TradePortfolioPage v-bind="attrs" />
</template>
