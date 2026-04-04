<script setup lang="ts">
import { useAttrs } from 'vue'
import SystemDataSourcePage from '@/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue'

const attrs = useAttrs()
</script>

<template>
  <SystemDataSourcePage v-bind="attrs" />
</template>
