<script setup lang="ts">
import { useAttrs } from 'vue'
import SystemHealthPage from '@/views/artdeco-pages/system-tabs/SystemHealthTab.vue'

const attrs = useAttrs()
</script>

<template>
  <SystemHealthPage v-bind="attrs" />
</template>
