<script setup lang="ts">
import { useAttrs } from 'vue'
import TradeHistoryCanonicalPage from '@/views/trade/History.vue'

const attrs = useAttrs()
</script>

<template>
  <TradeHistoryCanonicalPage v-bind="attrs" :history="[]" />
</template>
