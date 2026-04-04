<script setup lang="ts">
import { useAttrs } from 'vue'
import TradeSignalsPage from '@/views/artdeco-pages/trading-tabs/ArtDecoSignalsView.vue'

const attrs = useAttrs()
</script>

<template>
  <TradeSignalsPage v-bind="attrs" />
</template>
