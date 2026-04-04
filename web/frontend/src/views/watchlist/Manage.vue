<script setup lang="ts">
import { useAttrs } from 'vue'
import WatchlistManagePage from '@/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue'

const attrs = useAttrs()
</script>

<template>
  <WatchlistManagePage v-bind="attrs" />
</template>
