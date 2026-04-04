<script setup lang="ts">
import { useAttrs } from 'vue'
import SystemSettingsPage from '@/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue'

const attrs = useAttrs()
</script>

<template>
  <SystemSettingsPage v-bind="attrs" />
</template>
