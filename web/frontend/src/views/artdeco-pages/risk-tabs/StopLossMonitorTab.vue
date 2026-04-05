<script setup lang="ts">
import { useAttrs } from 'vue'
import RiskStopLossCanonicalPage from '@/views/risk/StopLoss.vue'

const attrs = useAttrs()
</script>

<template>
  <RiskStopLossCanonicalPage v-bind="attrs" />
</template>
