<template>
    <ArtDecoCard :hoverable="hoverable" class="artdeco-info-card">
        <div class="artdeco-info-header" v-if="title || $slots.header">
            <slot name="header">
                <h3 class="artdeco-info-title">{{ title }}</h3>
            </slot>
        </div>

        <div class="artdeco-info-content">
            <div class="artdeco-info-label">{{ label }}</div>
            <div class="artdeco-info-value" :class="valueClass">
                <slot>{{ displayValue }}</slot>
            </div>
        </div>

        <div v-if="description || $slots.footer" class="artdeco-info-footer">
            <slot name="footer">
                <p class="artdeco-info-description">{{ description }}</p>
            </slot>
        </div>

        <div v-if="metadata" class="artdeco-info-metadata">
            <div v-for="(value, key) in metadata" :key="key" class="artdeco-info-meta-item">
                <span class="artdeco-info-meta-label">{{ key }}:</span>
                <span class="artdeco-info-meta-value">{{ value }}</span>
            </div>
        </div>
    </ArtDecoCard>
</template>

<script setup lang="ts">
    import { computed } from 'vue'
    import ArtDecoCard from '../base/ArtDecoCard.vue'

    interface Props {
        title?: string
        label: string
        value?: string | number
        description?: string
        valueClass?: string
        hoverable?: boolean
        metadata?: Record<string, string | number>
    }

    const props = withDefaults(defineProps<Props>(), {
        title: '',
        value: '',
        description: '',
        valueClass: '',
        hoverable: true,
        metadata: undefined
    })

    const displayValue = computed(() => {
        if (typeof props.value === 'number') {
            return props.value.toLocaleString('zh-CN', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })
        }
        return props.value
    })
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-info-card {
      padding: var(--artdeco-spacing-4);
      text-align: center;
      transition: all var(--artdeco-transition-base);
    }

    .artdeco-info-header {
      margin-bottom: var(--artdeco-spacing-3);
    }

    .artdeco-info-title {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-base); // 14px - Compact v3.1
      font-weight: 600;
      color: var(--artdeco-accent-gold);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
      margin: 0;
    }

    .artdeco-info-content {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-2);
      margin-bottom: var(--artdeco-spacing-3);
    }

    .artdeco-info-label {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-sm); // 12px - Compact v3.1
      font-weight: 600;
      color: var(--artdeco-fg-muted);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
    }

    .artdeco-info-value {
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-font-size-lg); // 24px - Compact v3.1
      font-weight: 600;
      color: var(--artdeco-accent-gold);
      line-height: 1;
      word-break: break-word;
    }

    .artdeco-info-footer {
      margin-top: var(--artdeco-spacing-3);
      padding-top: var(--artdeco-spacing-3);
      border-top: 1px solid rgba(212, 175, 55, 0.2);
    }

    .artdeco-info-description {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-base); // 14px - Compact v3.1
      color: var(--artdeco-silver-dim);
      line-height: 1.4;
      margin: 0;
    }

    .artdeco-info-metadata {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-1);
      margin-top: var(--artdeco-spacing-3);
      padding: var(--artdeco-spacing-2);
      background: var(--artdeco-bg-header);
      border: 1px solid rgba(212, 175, 55, 0.2);
      border-radius: var(--artdeco-radius-none);
    }

    .artdeco-info-meta-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: var(--artdeco-font-size-sm); // 12px - Compact v3.1
    }

    .artdeco-info-meta-label {
      font-family: var(--artdeco-font-body);
      font-weight: 600;
      color: var(--artdeco-fg-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .artdeco-info-meta-value {
      font-family: var(--artdeco-font-mono);
      font-weight: 500;
      color: var(--artdeco-fg-secondary);
    }

    /* Hover Effect */
    .artdeco-info-card:hover .artdeco-info-value {
      transform: scale(1.05);
      text-shadow: var(--artdeco-glow-subtle);
    }

    /* Value Color Variants */
    .artdeco-info-value.data-rise {
      color: var(--artdeco-rise);
    }

    .artdeco-info-value.data-fall {
      color: var(--artdeco-fall);
    }

    .artdeco-info-value.data-flat {
      color: var(--artdeco-fg-secondary);
    }

    // ============================================
    //   DESIGN NOTE - 设计说明
    //   本项目仅支持桌面端，不包含移动端响应式代码
    // ============================================
</style>
