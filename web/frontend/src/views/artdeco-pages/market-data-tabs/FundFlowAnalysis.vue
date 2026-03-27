<script setup lang="ts">
import { useAttrs } from 'vue'
import DataFundFlowPage from '@/views/data/FundFlow.vue'

const attrs = useAttrs()
</script>

<template>
  <DataFundFlowPage v-bind="attrs" />
</template>
