<script setup lang="ts">
import { useAttrs } from 'vue'
import SystemApiPage from '@/views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue'

const attrs = useAttrs()
</script>

<template>
  <SystemApiPage v-bind="attrs" />
</template>
