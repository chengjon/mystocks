<script setup lang="ts">
import { useAttrs } from 'vue'
import RiskAlertsCanonicalPage from '@/views/risk/Alerts.vue'

interface Props {
  functionKey?: string
  userPermissions?: string[]
  systemConfig?: unknown
}

const props = defineProps<Props>()

const attrs = useAttrs()
</script>

<template>
  <RiskAlertsCanonicalPage v-bind="attrs" v-bind="props" />
</template>
