<template>
    <a href="#main-content" class="skip-link" @click="handleSkip">
        <slot>{{ skipText }}</slot>
        <span class="skip-link-icon">→</span>
    </a>
</template>

<script setup lang="ts">
    /**
     * ArtDeco Skip to Content Link
     *
     * 可访问性组件 - 允许键盘用户跳过导航直接到达主要内容
     *
     * 特性:
     * - 仅在获得焦点时可见（屏幕阅读器始终可访问）
     * - 符合WCAG 2.1 AA标准
     * - ArtDeco风格设计（金色 + 深黑背景）
     * - 平滑滚动到主要内容
     * - 自动设置焦点到目标元素
     * - 支持国际化 (i18n)
     *
     * 使用方法:
     * 1. 在布局文件顶部添加此组件
     * 2. 在主内容区域添加 id="main-content"
     * 3. 组件会在Tab键首次按下时显示
     *
     * @example
     * <ArtDecoSkipLink />
     *
     * <!-- 在主要内容处添加ID -->
     * <main id="main-content" tabindex="-1">
     *   <h1>页面标题</h1>
     *   ...
     * </main>
     */

    import { computed } from 'vue'
    import { useI18n } from '@/composables/useI18n'

    // Composables
    const { t } = useI18n()

    // Computed
    const skipText = computed(() => t('accessibility.skipToContent'))

    const handleSkip = (event: MouseEvent) => {
        event.preventDefault()

        // 获取目标元素
        const target = document.getElementById('main-content')
        if (!target) {
            console.warn('Skip link target #main-content not found')
            return
        }

        // 平滑滚动到目标
        target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        })

        // 设置焦点到目标元素（使其可被键盘访问）
        target.setAttribute('tabindex', '-1')
        target.focus({
            preventScroll: true // 已经滚动，不再重复
        })

        // 可选：在焦点后移除tabindex，避免在tab顺序中停留
        // setTimeout(() => {
        //   target.removeAttribute('tabindex')
        // }, 1000)
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .skip-link {
        --skip-link-bg: var(--artdeco-gold-primary);
        --skip-link-text: var(--artdeco-bg-global);
        --skip-link-border: var(--artdeco-gold-hover);
        --skip-link-focus: var(--artdeco-gold-hover);

        position: absolute;
        top: -100px; // 默认隐藏在屏幕上方
        left: 50%;
        transform: translateX(-50%);
        z-index: 9999;

        display: inline-flex;
        align-items: center;
        gap: var(--artdeco-spacing-sm);

        padding: var(--artdeco-spacing-sm) var(--artdeco-spacing-lg);
        font-family: var(--artdeco-font-heading);
        font-size: var(--artdeco-font-size-sm);
        font-weight: var(--artdeco-font-weight-bold);
        text-transform: uppercase;
        letter-spacing: 0.15em;

        color: var(--skip-link-text);
        background: var(--skip-link-bg);
        border: 2px solid var(--skip-link-border);
        border-radius: 0; // ArtDeco风格：直角
        text-decoration: none;
        white-space: nowrap;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);

        transition: all var(--artdeco-transition-normal) var(--artdeco-ease-out);

        // 焦点时显示（键盘导航）
        &:focus {
            top: var(--artdeco-spacing-md); // 从顶部滑入
            outline: none;
            box-shadow: 0 0 0 4px rgba(212, 175, 55, 0.3);
        }

        // 悬停效果
        &:hover {
            background: var(--skip-link-focus);
            transform: translateX(-50%) translateY(-2px);
            box-shadow: 0 6px 16px rgba(212, 175, 55, 0.4);
        }

        // 激活状态
        &:active {
            transform: translateX(-50%) translateY(0);
        }

        // 图标样式
        .skip-link-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: var(--artdeco-font-size-lg);
            font-weight: var(--artdeco-font-weight-bold);
            transition: transform var(--artdeco-transition-fast) var(--artdeco-ease-out);
        }

        &:hover .skip-link-icon {
            transform: translateX(2px);
        }
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .skip-link {
            left: var(--artdeco-spacing-md);
            transform: none;
            padding: var(--artdeco-spacing-xs) var(--artdeco-spacing-md);
            font-size: var(--artdeco-font-size-xs);

            &:focus {
                left: var(--artdeco-spacing-md);
                transform: none;
            }

            &:hover {
                transform: translateY(-2px);
            }
        }
    }

    /* 高对比度模式 */
    @media (prefers-contrast: high) {
        .skip-link {
            border-width: 3px;
            font-weight: 900;
        }
    }

    /* 减少动画模式 */
    @media (prefers-reduced-motion: reduce) {
        .skip-link {
            transition: none;

            &:focus {
                top: 0; // 直接显示，不使用动画
            }
        }

        .skip-link-icon {
            transition: none;
        }
    }

    /* 打印样式 */
    @media print {
        .skip-link {
            display: none;
        }
    }
</style>
