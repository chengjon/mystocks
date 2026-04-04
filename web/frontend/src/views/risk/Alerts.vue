<script setup lang="ts">
import { useAttrs } from 'vue'
import RiskAlertsPage from '@/views/artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue'

const attrs = useAttrs()
</script>

<template>
  <RiskAlertsPage v-bind="attrs" />
</template>
