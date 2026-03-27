<script setup lang="ts">
import { useAttrs } from 'vue'
import MarketTechnicalPage from '@/views/market/Technical.vue'

const attrs = useAttrs()
</script>

<template>
  <MarketTechnicalPage v-bind="attrs" />
</template>
