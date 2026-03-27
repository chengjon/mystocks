<script setup lang="ts">
import { useAttrs } from 'vue'
import DataConceptsPage from '@/views/data/Concepts.vue'

const attrs = useAttrs()
</script>

<template>
  <DataConceptsPage v-bind="attrs" />
</template>
