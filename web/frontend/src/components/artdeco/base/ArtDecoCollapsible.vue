<template>
    <div class="artdeco-collapsible" :class="{ 'is-expanded': isOpen }">
        <!-- 折叠头部 -->
        <div
            class="artdeco-collapsible-header"
            @click="toggle"
            @keydown.enter="toggle"
            @keydown.space.prevent="toggle"
            tabindex="0"
            role="button"
            :aria-expanded="isOpen"
            :aria-controls="contentId"
        >
            <!-- 标题插槽 -->
            <div class="artdeco-collapsible-title">
                <slot name="title">{{ title }}</slot>
            </div>

            <!-- 展开/折叠图标 -->
            <div class="artdeco-collapsible-icon" aria-hidden="true">
                <span v-if="isOpen" class="collapse-icon">▼</span>
                <span v-else class="expand-icon">▶</span>
            </div>

            <!-- 几何装饰 -->
            <div class="artdeco-collapsible-decoration artdeco-collapsible-decoration--left"></div>
            <div class="artdeco-collapsible-decoration artdeco-collapsible-decoration--right"></div>
        </div>

        <!-- 可折叠内容区域 -->
        <transition
            name="artdeco-collapse"
            @before-enter="beforeEnter"
            @enter="enter"
            @after-enter="afterEnter"
            @before-leave="beforeLeave"
            @leave="leave"
            @after-leave="afterLeave"
        >
            <div
                v-show="isOpen"
                :id="contentId"
                class="artdeco-collapsible-content"
                role="region"
                :aria-labelledby="headerId"
            >
                <div class="artdeco-collapsible-inner">
                    <slot />
                </div>
            </div>
        </transition>
    </div>
</template>

<script setup lang="ts">
    import { ref, computed, watch } from 'vue'

    /**
     * ArtDecoCollapsible - 可折叠面板组件
     *
     * 用途: 减少页面认知负荷，支持渐进式信息披露
     *       Progressive Disclosure for reduced cognitive load
     *
     * 特性:
     * - ArtDeco风格（金色装饰，几何角落）
     * - 平滑动画过渡
     * - 键盘可访问（Enter/Space切换）
     * - ARIA无障碍标签
     * - 可受控（v-model）或非受控模式
     *
     * 示例:
     * <ArtDecoCollapsible title="技术指标" v-model="expanded">
     *   <div>指标内容...</div>
     * </ArtDecoCollapsible>
     */

    interface Props {
        /** 面板标题 */
        title?: string
        /** 初始展开状态（非受控模式） */
        defaultExpanded?: boolean
        /** 受控模式：展开状态 */
        expanded?: boolean
        /** 是否禁用 */
        disabled?: boolean
        /** 动画持续时间（ms） */
        duration?: number
    }

    const props = withDefaults(defineProps<Props>(), {
        title: '',
        defaultExpanded: false,
        disabled: false,
        duration: 300
    })

    const emit = defineEmits<{
        (e: 'update:expanded', value: boolean): void
        (e: 'toggle', value: boolean): void
        (e: 'expand'): void
        (e: 'collapse'): void
    }>()

    // 内部状态（非受控模式）
    const internalExpanded = ref(props.defaultExpanded)

    // 受控/非受控模式切换
    const isOpen = computed({
        get() {
            return props.expanded !== undefined ? props.expanded : internalExpanded.value
        },
        set(value: boolean) {
            if (props.expanded === undefined) {
                internalExpanded.value = value
            }
            emit('update:expanded', value)
            emit('toggle', value)
            if (value) {
                emit('expand')
            } else {
                emit('collapse')
            }
        }
    })

    // 生成唯一ID
    const contentId = computed(() => `collapsible-content-${Math.random().toString(36).substr(2, 9)}`)
    const headerId = computed(() => `collapsible-header-${Math.random().toString(36).substr(2, 9)}`)

    // 切换展开/折叠
    const toggle = () => {
        if (!props.disabled) {
            isOpen.value = !isOpen.value
        }
    }

    // 过渡动画hook
    const beforeEnter = (el: HTMLElement) => {
        el.style.height = '0'
        el.style.opacity = '0'
    }

    const enter = (el: HTMLElement) => {
        el.style.transition = `height ${props.duration}ms ease-in-out, opacity ${props.duration}ms ease-in-out`
        // 强制重排以触发transition
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                el.style.height = el.scrollHeight + 'px'
                el.style.opacity = '1'
            })
        })
    }

    const afterEnter = (el: HTMLElement) => {
        el.style.height = ''
        el.style.opacity = ''
    }

    const beforeLeave = (el: HTMLElement) => {
        el.style.height = el.scrollHeight + 'px'
        el.style.opacity = '1'
    }

    const leave = (el: HTMLElement) => {
        el.style.transition = `height ${props.duration}ms ease-in-out, opacity ${props.duration}ms ease-in-out`
        // 强制重排
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                el.style.height = '0'
                el.style.opacity = '0'
            })
        })
    }

    const afterLeave = (el: HTMLElement) => {
        el.style.height = ''
        el.style.opacity = ''
    }

    // 监听外部expanded变化（受控模式）
    watch(
        () => props.expanded,
        newValue => {
            if (newValue !== undefined) {
                internalExpanded.value = newValue
            }
        }
    )
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-collapsible {
        position: relative;
        border: 1px solid var(--artdeco-border-color);
        background: var(--artdeco-bg-elevated);
        margin-bottom: var(--artdeco-spacing-4);
        transition: all var(--artdeco-transition-base);

        // 几何角落装饰
        @include artdeco-geometric-corners;

        &:hover {
            border-color: var(--artdeco-border-hover);
            box-shadow: 0 4px 12px rgba(212, 175, 55, 0.1);
        }

        &.is-expanded {
            .artdeco-collapsible-header {
                border-bottom: 1px solid var(--artdeco-border-color);
            }

            .artdeco-collapsible-icon {
                transform: rotate(0deg);
            }
        }
    }

    .artdeco-collapsible-header {
        position: relative;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
        cursor: pointer;
        user-select: none;
        transition: all var(--artdeco-transition-base);

        // 焦点状态（键盘导航）
        &:focus-visible {
            outline: 2px solid var(--artdeco-gold-primary);
            outline-offset: 2px;
            box-shadow:
                0 0 0 2px var(--artdeco-bg-global),
                0 0 0 4px var(--artdeco-gold-primary),
                0 0 12px rgba(212, 175, 55, 0.4);
        }

        // 悬停状态
        &:hover {
            background: rgba(212, 175, 55, 0.05);

            .artdeco-collapsible-title {
                color: var(--artdeco-gold-primary);
            }
        }
    }

    .artdeco-collapsible-title {
        font-family: var(--artdeco-font-heading);
        font-size: var(--artdeco-font-size-md);
        font-weight: 600;
        color: var(--artdeco-fg-primary);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
        transition: color var(--artdeco-transition-base);
    }

    .artdeco-collapsible-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        font-size: 12px;
        color: var(--artdeco-gold-primary);
        transition: transform var(--artdeco-transition-slow);

        .expand-icon {
            transform: rotate(0deg);
            transition: transform var(--artdeco-transition-slow);
        }

        .collapse-icon {
            transform: rotate(180deg);
            transition: transform var(--artdeco-transition-slow);
        }
    }

    // 几何装饰
    .artdeco-collapsible-decoration {
        position: absolute;
        width: 8px;
        height: 8px;
        border: 2px solid var(--artdeco-gold-dim);
        opacity: 0.6;
        transition: all var(--artdeco-transition-base);

        &--left {
            top: 8px;
            left: 8px;
            border-right: none;
            border-bottom: none;
        }

        &--right {
            top: 8px;
            right: 8px;
            border-left: none;
            border-bottom: none;
        }

        .artdeco-collapsible:hover &,
        .artdeco-collapsible.is-expanded & {
            opacity: 1;
            border-color: var(--artdeco-gold-primary);
        }
    }

    .artdeco-collapsible-content {
        overflow: hidden;
        background: rgba(10, 10, 10, 0.5);
    }

    .artdeco-collapsible-inner {
        padding: var(--artdeco-spacing-4);
    }

    // 过渡动画
    .artdeco-collapse-enter-active,
    .artdeco-collapse-leave-active {
        transition: all var(--artdeco-transition-base);
        will-change: height, opacity;
    }

    // 无障碍性：隐藏折叠内容
    .artdeco-collapsible[aria-expanded='false'] {
        .artdeco-collapsible-content {
            visibility: hidden;
        }
    }

    // 禁用状态
    .artdeco-collapsible[aria-disabled='true'] {
        opacity: 0.6;
        cursor: not-allowed;
        pointer-events: none;
    }

    // 减少动画支持（无障碍性）
    @media (prefers-reduced-motion: reduce) {
        .artdeco-collapsible-header,
        .artdeco-collapsible-icon,
        .artdeco-collapse-enter-active,
        .artdeco-collapse-leave-active {
            transition: none !important;
        }
    }
</style>
