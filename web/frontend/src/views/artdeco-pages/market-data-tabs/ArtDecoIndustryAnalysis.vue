<script setup lang="ts">
import { useAttrs } from 'vue'
import DataIndustryPage from '@/views/data/Industry.vue'

const attrs = useAttrs()
</script>

<template>
  <DataIndustryPage v-bind="attrs" />
</template>
