<script setup lang="ts">
import { useAttrs } from 'vue'
import RiskCenterPage from '@/views/artdeco-pages/ArtDecoRiskManagement.vue'

const attrs = useAttrs()
</script>

<template>
  <RiskCenterPage v-bind="attrs" />
</template>
