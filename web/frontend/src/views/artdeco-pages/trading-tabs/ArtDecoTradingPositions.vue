<script setup lang="ts">
import { useAttrs } from 'vue'
import TradeCenterCanonicalPage from '@/views/trade/Center.vue'

const attrs = useAttrs()
</script>

<template>
  <TradeCenterCanonicalPage v-bind="attrs" />
</template>
