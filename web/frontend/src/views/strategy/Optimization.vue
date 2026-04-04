<script setup lang="ts">
import { useAttrs } from 'vue'
import StrategyOptimizationPage from '@/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue'

const attrs = useAttrs()
</script>

<template>
  <StrategyOptimizationPage v-bind="attrs" />
</template>
