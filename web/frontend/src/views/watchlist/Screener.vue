<script setup lang="ts">
import { useAttrs } from 'vue'
import WatchlistScreenerPage from '@/views/stocks/Screener.vue'

const attrs = useAttrs()
</script>

<template>
  <WatchlistScreenerPage v-bind="attrs" />
</template>
