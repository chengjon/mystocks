<script setup lang="ts">
import { ArtDecoHeader } from '@/components/artdeco'

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
</script>

<template>
  <section class="hero-shell artdeco-card-shell">
    <div class="hero-rail">
      <div class="hero-copy">
        <span class="hero-eyebrow">{{ eyebrow }}</span>
        <div class="hero-meta">
          <span>REQ_ID: {{ requestId }}</span>
          <span>DOMAIN: AI</span>
          <span>ENTRY: sentiment</span>
        </div>
      </div>
    </div>

    <ArtDecoHeader
      :title="title"
      :subtitle="subtitle"
      :show-status="true"
      :status-text="statusText"
      :status-type="statusType"
    >
      <template #actions>
        <slot name="actions" />
      </template>
    </ArtDecoHeader>
  </section>
</template>
