<script setup lang="ts">
import { useAttrs } from 'vue'
import SystemApiCanonicalPage from '@/views/system/API.vue'

const attrs = useAttrs()
</script>

<template>
  <SystemApiCanonicalPage v-bind="attrs" />
</template>
