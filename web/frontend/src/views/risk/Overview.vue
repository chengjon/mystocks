<script setup lang="ts">
import { useAttrs } from 'vue'
import RiskOverviewPage from '@/views/artdeco-pages/risk-tabs/RiskOverviewTab.vue'

const attrs = useAttrs()
</script>

<template>
  <RiskOverviewPage v-bind="attrs" />
</template>
