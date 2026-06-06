<script setup lang="ts">
import { useAttrs } from 'vue'
import RiskCenterCanonicalPage from '@/views/risk/Center.vue'

const attrs = useAttrs()
</script>

<template>
  <RiskCenterCanonicalPage v-bind="attrs" />
</template>
