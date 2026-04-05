<script setup lang="ts">
import { useAttrs } from 'vue'
import TradeSignalsCanonicalPage from '@/views/trade/Signals.vue'

const attrs = useAttrs()
</script>

<template>
  <TradeSignalsCanonicalPage v-bind="attrs" />
</template>
