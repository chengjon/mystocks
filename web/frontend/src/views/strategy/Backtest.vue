<script setup lang="ts">
import { useAttrs } from 'vue'
import StrategyBacktestPage from '@/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue'

const attrs = useAttrs()
</script>

<template>
  <StrategyBacktestPage v-bind="attrs" />
</template>
