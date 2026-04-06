<script setup lang="ts">
import { useAttrs } from 'vue'
import SystemSettingsCanonicalPage from '@/views/system/Settings.vue'

const attrs = useAttrs()
</script>

<template>
  <SystemSettingsCanonicalPage v-bind="attrs" />
</template>
