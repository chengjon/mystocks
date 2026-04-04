<script setup lang="ts">
import { useAttrs } from 'vue'
import TradeCenterPage from '@/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue'

const attrs = useAttrs()
</script>

<template>
  <TradeCenterPage v-bind="attrs" />
</template>
