<script setup lang="ts">
import { computed, useAttrs } from 'vue'

import ArtDecoRouteHeader from '@/components/artdeco/route-shell/ArtDecoRouteHeader.vue'

defineOptions({
  inheritAttrs: false,
})

defineProps<{
  eyebrow: string
  title: string
  subtitle: string
  requestId: string
  statusText: string
  statusType: 'info' | 'success' | 'warning'
}>()

defineEmits<{
  refresh: []
}>()

const attrs = useAttrs()
const routeHeaderTestId = computed(() => {
  const value = attrs['data-testid']
  return typeof value === 'string' ? value : ''
})
const forwardedAttrs = computed(() => {
  const { ['data-testid']: _dataTestId, ...rest } = attrs
  return rest
})
</script>

<template>
  <ArtDecoRouteHeader
    v-bind="forwardedAttrs"
    :title="title"
    :subtitle="subtitle"
    :eyebrow="eyebrow"
    :show-status="true"
    :status-text="statusText"
    :status-type="statusType"
    :test-id="routeHeaderTestId"
  >
    <template #meta>
      <span>REQ_ID: {{ requestId }}</span>
      <span>DOMAIN: AI</span>
      <span>ENTRY: sentiment</span>
    </template>

    <template #actions>
      <slot name="actions" />
    </template>
  </ArtDecoRouteHeader>
</template>
