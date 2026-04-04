<script setup lang="ts">
import { useAttrs } from 'vue'
import StrategyParametersPage from '@/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue'

const attrs = useAttrs()
</script>

<template>
  <StrategyParametersPage v-bind="attrs" />
</template>
