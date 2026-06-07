<script setup lang="ts">
import { useAttrs } from 'vue'
import TradePositionsCanonicalPage from '@/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue'

const attrs = useAttrs()
</script>

<template>
  <TradePositionsCanonicalPage v-bind="attrs" />
</template>
