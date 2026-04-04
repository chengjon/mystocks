<script setup lang="ts">
import { useAttrs } from 'vue'
import TradeHistoryPage from '@/views/artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue'

const attrs = useAttrs()
</script>

<template>
  <TradeHistoryPage v-bind="attrs" />
</template>
