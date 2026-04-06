<script setup lang="ts">
import { useAttrs } from 'vue'
import SystemHealthCanonicalPage from '@/views/system/Health.vue'

const attrs = useAttrs()
</script>

<template>
  <SystemHealthCanonicalPage v-bind="attrs" />
</template>
