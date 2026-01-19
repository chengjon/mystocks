<template>
  <span :class="['artdeco-badge', `artdeco-badge--${type}`]">
    <slot>{{ text }}</slot>
  </span>
</template>

<script setup lang="ts">
/**
 * ArtDecoBadge - ArtDeco风格的徽章组件
 * 用于显示状态、数量或简短提示
 *
 * @example
 * <ArtDecoBadge text="New" type="primary" />
 * <ArtDecoBadge type="danger">API Error</ArtDecoBadge>
 */
interface Props {
  /** 徽章文本 */
  text?: string
  /** 徽章类型，决定颜色和样式 */
  type?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info'
}

withDefaults(defineProps<Props>(), {
  text: '',
  type: 'primary'
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.artdeco-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.2em 0.6em;
  border-radius: var(--artdeco-radius-sm);
  font-size: var(--artdeco-text-xs);
  font-weight: var(--artdeco-font-semibold);
  line-height: 1;
  white-space: nowrap;
  vertical-align: middle;
  transition: all var(--artdeco-transition-fast) ease;

  // 默认样式 - Primary (金色)
  &--primary {
    background: var(--artdeco-gold-primary);
    color: var(--artdeco-bg-global);
  }

  // Secondary (柔和的金色边框)
  &--secondary {
    background: var(--artdeco-bg-elevated);
    color: var(--artdeco-gold-primary);
    border: 1px solid var(--artdeco-gold-dim);
  }

  // Success (绿色)
  &--success {
    background: var(--artdeco-success);
    color: var(--artdeco-bg-global);
  }

  // Warning (黄色)
  &--warning {
    background: var(--artdeco-warning);
    color: var(--artdeco-bg-global);
  }

  // Danger (红色)
  &--danger {
    background: var(--artdeco-error);
    color: var(--artdeco-bg-global);
  }

  // Info (蓝色)
  &--info {
    background: var(--artdeco-info);
    color: var(--artdeco-bg-global);
  }
}
</style>
