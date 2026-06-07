<script setup lang="ts">
import { useAttrs } from 'vue'
import TradePortfolioCanonicalPage from '@/views/trade/Portfolio.vue'

const attrs = useAttrs()
</script>

<template>
  <TradePortfolioCanonicalPage v-bind="attrs" />
</template>
