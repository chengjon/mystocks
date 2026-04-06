<script setup lang="ts">
import { useAttrs } from 'vue'
import RiskNewsCanonicalPage from '@/views/risk/News.vue'

interface Props {
  functionKey?: string
  userPermissions?: string[]
  systemConfig?: unknown
}

const props = defineProps<Props>()
const attrs = useAttrs()
</script>

<template>
  <RiskNewsCanonicalPage v-bind="attrs" v-bind="props" />
</template>
