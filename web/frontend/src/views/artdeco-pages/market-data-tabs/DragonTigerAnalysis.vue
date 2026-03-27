<script setup lang="ts">
import { useAttrs } from 'vue'
import MarketLhbPage from '@/views/market/LHB.vue'

const attrs = useAttrs()
</script>

<template>
  <MarketLhbPage v-bind="attrs" />
</template>
