<template>
    <ArtDecoCard :hoverable="hoverable" :class="statClass" v-bind="ariaProps">
        <div class="artdeco-stat-header">
            <div class="artdeco-stat-label">{{ label }}</div>
            <div v-if="icon" class="artdeco-stat-icon" aria-hidden="true">
                <slot name="icon">{{ icon }}</slot>
            </div>
        </div>

        <!-- 实时数据更新区域 -->
        <div
            class="artdeco-stat-value"
            :class="valueClass"
            :aria-label="`${label}: ${displayValue}`"
            role="status"
            aria-live="polite"
        >
            <slot name="value">{{ displayValue }}</slot>
        </div>

        <div
            v-if="change || showChange"
            class="artdeco-stat-change"
            :class="changeClass"
            :aria-label="`变化: ${displayChange}`"
        >
            <span v-if="change > 0" class="artdeco-stat-arrow" aria-hidden="true">▲</span>
            <span v-else-if="change < 0" class="artdeco-stat-arrow" aria-hidden="true">▼</span>
            <span v-else class="artdeco-stat-arrow" aria-hidden="true">●</span>
            <span class="artdeco-stat-change-text">{{ displayChange }}</span>
        </div>

        <div v-if="description" class="artdeco-stat-description" role="note">
            {{ description }}
        </div>
    </ArtDecoCard>
</template>

<script setup lang="ts">
    import { computed } from 'vue'
    import ArtDecoCard from './ArtDecoCard.vue'
    import { useAria } from '@/composables/useAria'

    interface Props {
        label: string
        value: string | number
        change?: number
        changePercent?: boolean
        description?: string
        icon?: string
        hoverable?: boolean
        showChange?: boolean
        variant?: 'gold' | 'rise' | 'fall' | 'default'
    }

    const props = withDefaults(defineProps<Props>(), {
        change: 0,
        changePercent: true,
        description: '',
        icon: '',
        hoverable: true,
        showChange: true,
        variant: 'default'
    })

    // ♿ ARIA标签增强
    const ariaProps = computed(() => {
        const { liveRegion } = useAria()
        return liveRegion(props.label, 'polite').value
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

    const displayChange = computed(() => {
        if (props.changePercent) {
            return `${props.change >= 0 ? '+' : ''}${props.change}%`
        }
        return `${props.change >= 0 ? '+' : ''}${props.change}`
    })

    const valueClass = computed(() => {
        if (props.variant !== 'default') {
            return `artdeco-stat-value-${props.variant}`
        }
        if (props.change > 0) return 'artdeco-stat-value-rise'
        if (props.change < 0) return 'artdeco-stat-value-fall'
        return ''
    })

    const changeClass = computed(() => {
        if (props.change > 0) return 'artdeco-stat-change-rise'
        if (props.change < 0) return 'artdeco-stat-change-fall'
        return 'artdeco-stat-change-flat'
    })

    const statClass = computed(() => {
        return `artdeco-stat-card-${props.variant}`
    })
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens';

    .artdeco-stat-card {
      padding: var(--artdeco-spacing-4);
      text-align: center;

      // 添加几何角落装饰
      @include artdeco-geometric-corners;

      // 添加增强的悬停提升效果
      @include artdeco-hover-lift;
    }

    .artdeco-stat-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: var(--artdeco-spacing-3);
    }

    .artdeco-stat-label {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-sm);
      font-weight: 600;
      color: var(--artdeco-fg-muted);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
    }

    .artdeco-stat-icon {
      font-size: var(--artdeco-font-size-md);
      color: var(--artdeco-gold-opacity-20);
    }

    .artdeco-stat-value {
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-font-size-xl);
      font-weight: 600;
      line-height: 1;
      margin-bottom: var(--artdeco-spacing-2);
      transition: all var(--artdeco-transition-base);
    }

    /* Value Colors - A股标准色 */
    .artdeco-stat-value-gold {
      color: var(--artdeco-gold-primary);
    }

    .artdeco-stat-value-rise {
      color: var(--artdeco-up);
    }

    .artdeco-stat-value-fall {
      color: var(--artdeco-down);
    }

    .artdeco-stat-change {
      display: inline-flex;
      align-items: center;
      gap: var(--artdeco-spacing-1);
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-font-size-base);
      font-weight: 600;
      padding: var(--artdeco-spacing-1) var(--artdeco-spacing-3);
      border-radius: var(--artdeco-radius-none);
      transition: all var(--artdeco-transition-base);
    }

    .artdeco-stat-arrow {
      font-size: var(--artdeco-font-size-sm);
    }

    .artdeco-stat-change-rise {
      color: var(--artdeco-up);
      background: color-mix(in srgb, var(--artdeco-up) 10%, transparent);
    }

    .artdeco-stat-change-fall {
      color: var(--artdeco-down);
      background: color-mix(in srgb, var(--artdeco-down) 10%, transparent);
    }

    .artdeco-stat-change-flat {
      color: var(--artdeco-fg-muted);
      background: color-mix(in srgb, var(--artdeco-fg-muted) 10%, transparent);
    }

    .artdeco-stat-description {
      margin-top: var(--artdeco-spacing-3);
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-sm);
      color: var(--artdeco-silver-dim);
      line-height: 1.4;
    }

    /* Hover Effects - 增强戏剧化 */
    .artdeco-stat-card:hover {
      .artdeco-stat-value {
        transform: scale(1.05);
        text-shadow: var(--artdeco-glow-intense);
      }
    }

    .artdeco-stat-card-gold:hover .artdeco-stat-value {
      color: var(--artdeco-gold-light);
      text-shadow: 0 0 calc(var(--artdeco-spacing-5) - var(--artdeco-spacing-5) / 4) var(--artdeco-gold-opacity-50);
    }

    .artdeco-stat-card-rise:hover .artdeco-stat-value {
      color: var(--artdeco-up);
      text-shadow: 0 0 calc(var(--artdeco-spacing-5) - var(--artdeco-spacing-5) / 4) color-mix(in srgb, var(--artdeco-up) 50%, transparent);
    }

    .artdeco-stat-card-fall:hover .artdeco-stat-value {
      color: var(--artdeco-down);
      text-shadow: 0 0 calc(var(--artdeco-spacing-5) - var(--artdeco-spacing-5) / 4) color-mix(in srgb, var(--artdeco-down) 50%, transparent);
    }

    // ============================================
    //   DESIGN NOTE - 设计说明
    //   本项目仅支持桌面端，不包含移动端响应式代码
    // ============================================
</style>
