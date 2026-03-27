<script setup lang="ts">
import { useAttrs } from 'vue'
import MarketRealtimePage from '@/views/market/Realtime.vue'

const attrs = useAttrs()
</script>

<template>
  <MarketRealtimePage v-bind="attrs" />
</template>
