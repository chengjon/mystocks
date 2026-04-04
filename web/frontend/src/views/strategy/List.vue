<script setup lang="ts">
import { useAttrs } from 'vue'
import StrategyListPage from '@/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue'

const attrs = useAttrs()
</script>

<template>
  <StrategyListPage v-bind="attrs" />
</template>
