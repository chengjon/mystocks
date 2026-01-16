<template>
    <div :class="groupClasses" :style="groupStyle">
        <slot />
    </div>
</template>

<script setup lang="ts">
    import { computed } from 'vue'

    // ============================================
    //   COMPONENT: ArtDecoButtonGroup
    //   Art Deco 风格按钮组组件
    //
    //   Design Philosophy:
    //   - 统一按钮间距（12px 组内 / 16px 组外）
    //   - 确保按钮垂直对齐
    //   - 支持垂直布局
    //   - 表单内自动增加上边距
    //
    //   Usage:
    //   <ArtDecoButtonGroup>
    //     <ArtDecoButton>Cancel</ArtDecoButton>
    //     <ArtDecoButton variant="solid">Submit</ArtDecoButton>
    //   </ArtDecoButtonGroup>
    // ============================================

    interface Props {
        /// 按钮排列方向
        direction?: 'horizontal' | 'vertical'

        /// 按钮间距（px，默认12px）
        gap?: number

        /// 是否在表单内（自动增加上边距）
        inForm?: boolean

        /// 对齐方式（仅水平布局）
        align?: 'left' | 'center' | 'right'

        /// 额外的CSS类
        class?: string
    }

    const props = withDefaults(defineProps<Props>(), {
        direction: 'horizontal',
        gap: 12, // 12px - 按钮组内统一间距
        inForm: false,
        align: 'left',
        class: ''
    })

    const groupClasses = computed(() => [
        'artdeco-btn-group',
        `artdeco-btn-group--${props.direction}`,
        `artdeco-btn-group--${props.align}`,
        {
            'artdeco-btn-group--in-form': props.inForm
        },
        props.class
    ])

    const groupStyle = computed(() => ({
        gap: `${props.gap}px`
    }))
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    // ============================================
    //   BUTTON GROUP BASE STYLES - 按钮组基础样式
    //   ✅ 优化: 统一按钮间距，确保垂直对齐
    // ============================================

    .artdeco-btn-group {
        display: flex;
        flex-wrap: wrap;

        // 确保按钮垂直对齐
        align-items: center;

        // 移除按钮的默认margin，使用gap统一间距
        .artdeco-button {
            margin: 0; // ✅ 移除默认margin
        }
    }

    // ============================================
    //   DIRECTION: HORIZONTAL - 水平布局（默认）
    // ============================================

    .artdeco-btn-group--horizontal {
        flex-direction: row;

        &.artdeco-btn-group--left {
            justify-content: flex-start;
        }

        &.artdeco-btn-group--center {
            justify-content: center;
        }

        &.artdeco-btn-group--right {
            justify-content: flex-end;
        }
    }

    // ============================================
    //   DIRECTION: VERTICAL - 垂直布局
    // ============================================

    .artdeco-btn-group--vertical {
        flex-direction: column;
        width: 100%;

        .artdeco-button {
            width: 100%; // 垂直布局时按钮占满宽度
        }
    }

    // ============================================
    //   IN FORM VARIANT - 表单内按钮组
    //   自动增加与表单字段的间距
    // ============================================

    .artdeco-btn-group--in-form {
        margin-top: var(--artdeco-spacing-4); // 32px - 与表单字段间距
        padding-top: var(--artdeco-spacing-3); // 24px - 上内边距
        border-top: 1px solid rgba(212, 175, 55, 0.2); // 可选：分隔线
    }

    // ============================================
    //   DESIGN NOTE - 设计说明
    //   本项目仅支持桌面端，不包含移动端响应式代码
    // ============================================
</style>
