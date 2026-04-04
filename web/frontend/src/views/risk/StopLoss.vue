<script setup lang="ts">
import { useAttrs } from 'vue'
import RiskStopLossPage from '@/views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue'

const attrs = useAttrs()
</script>

<template>
  <RiskStopLossPage v-bind="attrs" />
</template>
