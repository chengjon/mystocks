<script setup lang="ts">
import { useAttrs } from 'vue'
import RiskOverviewCanonicalPage from '@/views/risk/Overview.vue'

const attrs = useAttrs()
</script>

<template>
  <RiskOverviewCanonicalPage v-bind="attrs" />
</template>
