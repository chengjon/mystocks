<script setup lang="ts">
import { useAttrs } from 'vue'
import DataAdvancedPage from '@/views/data/Advanced.vue'

const attrs = useAttrs()
</script>

<template>
  <DataAdvancedPage v-bind="attrs" />
</template>
