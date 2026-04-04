<script setup lang="ts">
import { useAttrs } from 'vue'
import WatchlistSignalsPage from '@/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue'

const attrs = useAttrs()
</script>

<template>
  <WatchlistSignalsPage v-bind="attrs" />
</template>
