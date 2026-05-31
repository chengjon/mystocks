<template>
  <section
    v-bind="$attrs"
    :class="sectionClasses"
    :data-test="legacyTest || undefined"
    :data-testid="testId || undefined"
  >
    <div v-if="eyebrow || $slots.meta" class="hero-rail">
      <div class="hero-copy">
        <span v-if="eyebrow" class="hero-eyebrow">{{ eyebrow }}</span>
        <div v-if="$slots.meta" class="hero-meta">
          <slot name="meta" />
        </div>
      </div>
    </div>

    <ArtDecoHeader
      :title="title"
      :subtitle="subtitle"
      :show-status="showStatus"
      :status-text="statusText"
      :status-type="statusType"
    >
      <template v-if="$slots.actions" #actions>
        <slot name="actions" />
      </template>
    </ArtDecoHeader>

    <slot />
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import ArtDecoHeader from '../core/ArtDecoHeader.vue'

defineOptions({
  inheritAttrs: false,
})

type ArtDecoRouteHeaderStatusType = 'success' | 'warning' | 'danger' | 'error' | 'info'

const props = withDefaults(
  defineProps<{
    title: string
    subtitle?: string
    eyebrow?: string
    showStatus?: boolean
    statusText?: string
    statusType?: ArtDecoRouteHeaderStatusType
    testId?: string
    legacyTest?: string
    shellClass?: string
  }>(),
  {
    subtitle: '',
    eyebrow: '',
    showStatus: false,
    statusText: '',
    statusType: undefined,
    testId: '',
    legacyTest: '',
    shellClass: 'hero-shell artdeco-card-shell',
  },
)

const sectionClasses = computed(() => ['artdeco-route-header', props.shellClass])
</script>
