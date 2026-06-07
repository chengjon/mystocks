<script setup lang="ts">
import { useAttrs } from 'vue'
import ArtDecoTradingManagementPage from '@/views/artdeco-pages/ArtDecoTradingManagement.vue'

const attrs = useAttrs()
</script>

<template>
  <ArtDecoTradingManagementPage v-bind="attrs" />
</template>
