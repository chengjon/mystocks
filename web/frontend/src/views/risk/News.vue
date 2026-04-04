<script setup lang="ts">
import { useAttrs } from 'vue'
import RiskNewsPage from '@/views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue'

const attrs = useAttrs()
</script>

<template>
  <RiskNewsPage v-bind="attrs" />
</template>
