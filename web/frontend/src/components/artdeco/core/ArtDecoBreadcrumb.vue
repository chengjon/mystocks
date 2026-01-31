<template>
    <nav class="artdeco-breadcrumb" aria-label="Breadcrumb">
        <!-- 几何装饰 - 左侧 -->
        <div class="breadcrumb-decoration breadcrumb-decoration--left"></div>

        <!-- 几何装饰 - 右侧 -->
        <div class="breadcrumb-decoration breadcrumb-decoration--right"></div>

        <!-- 金色分隔线 -->
        <div class="breadcrumb-separator-line"></div>

        <ol class="breadcrumb-list">
            <li v-for="(item, index) in breadcrumbs" :key="item.path" class="breadcrumb-item">
                <!-- 链接 -->
                <component
                    :is="index < breadcrumbs.length - 1 ? 'router-link' : 'span'"
                    :to="index < breadcrumbs.length - 1 ? { path: item.path } : null"
                    class="breadcrumb-link"
                    :class="{ 'breadcrumb-link--active': index === breadcrumbs.length - 1 }"
                >
                    <!-- 图标 -->
                    <span v-if="item.icon && showIcon" class="breadcrumb-icon">
                        <ArtDecoIcon :name="item.icon" size="xs" />
                    </span>

                    <!-- 文本 -->
                    <span class="breadcrumb-text">{{ item.title }}</span>
                </component>

                <!-- 分隔符（最后一项不显示） -->
                <span v-if="index < breadcrumbs.length - 1" class="breadcrumb-divider" aria-hidden="true">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path
                            d="M9 18L15 12L9 6"
                            stroke="currentColor"
                            stroke-width="2"
                            stroke-linecap="square"
                            stroke-linejoin="miter"
                        />
                    </svg>
                </span>
            </li>
        </ol>

        <!-- 右侧装饰 -->
        <div class="breadcrumb-corner-decoration">
            <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="0" y="0" width="100" height="100" fill="none" />
                <path d="M0 0 H30 V2 H2 V30 H0 V0 Z" fill="var(--artdeco-gold-primary)" />
            </svg>
        </div>
    </nav>
</template>

<script setup lang="ts">
    import { computed } from 'vue'
    import { useRoute } from 'vue-router'
    import type { RouteLocationNormalized } from 'vue-router'
    import ArtDecoIcon from './ArtDecoIcon.vue'

    /**
     * ArtDeco Breadcrumb Component
     *
     * ArtDeco风格面包屑导航组件
     *
     * 特性:
     * - 自动从路由meta生成面包屑
     * - 支持自定义面包屑文本
     * - 完全符合ArtDeco设计规范（深黑背景 + 金色强调）
     * - 几何装饰元素
     * - 大写文本 + 增加字母间距
     * - WCAG AA可访问性标准
     * - 响应式设计
     *
     * @example
     * <ArtDecoBreadcrumb
     *   :show-icon="true"
     *   home-title="DASHBOARD"
     *   home-path="/dashboard"
     * />
     */

    interface BreadcrumbItem {
        path: string
        title: string
        icon?: string
    }

    // Props
    interface Props {
        // 首页标题（自动大写）
        homeTitle?: string
        // 首页路径
        homePath?: string
        // 是否显示图标
        showIcon?: boolean
        // 自定义面包屑映射
        customBreadcrumb?: Record<string, Partial<BreadcrumbItem>>
    }

    const props = withDefaults(defineProps<Props>(), {
        homeTitle: 'DASHBOARD',
        homePath: '/dashboard',
        showIcon: true,
        customBreadcrumb: () => ({})
    })

    // 当前路由
    const route = useRoute()

    // 生成面包屑数据
    const breadcrumbs = computed<BreadcrumbItem[]>(() => {
        const matched = route.matched.filter(item => item.meta && item.meta.title)
        const breadcrumbList: BreadcrumbItem[] = []

        // 添加首页（如果当前不在首页）
        if (route.path !== props.homePath) {
            breadcrumbList.push({
                path: props.homePath,
                title: props.homeTitle.toUpperCase(),
                icon: 'Home'
            })
        }

        // 添加路由匹配的面包屑
        matched.forEach(item => {
            // 跳过重定向路由
            if (item.redirect) return

            const meta = item.meta || {}
            const path = item.path || ''
            const customConfig = props.customBreadcrumb[path] || {}

            const breadcrumbItem: BreadcrumbItem = {
                path,
                title: (
                    customConfig.title ||
                    meta.title ||
                    (typeof item.name === 'string' ? item.name : 'UNNAMED')
                ).toUpperCase(),
                icon: customConfig.icon || meta.icon || undefined
            }

            // 避免重复的首页
            if (breadcrumbItem.path !== props.homePath) {
                breadcrumbList.push(breadcrumbItem)
            }
        })

        return breadcrumbList
    })
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-breadcrumb {
        --artdeco-breadcrumb-bg: var(--artdeco-bg-base);
        --artdeco-breadcrumb-text: var(--artdeco-fg-muted);
        --artdeco-breadcrumb-text-active: var(--artdeco-gold-primary);
        --artdeco-breadcrumb-text-hover: var(--artdeco-gold-hover);

        position: relative;
        display: flex;
        align-items: center;
        height: var(--artdeco-spacing-xl);
        padding: 0 var(--artdeco-spacing-lg);
        background: var(--artdeco-breadcrumb-bg);
        border-bottom: 1px solid var(--artdeco-border-color);
        overflow: hidden;

        // 几何装饰
        .breadcrumb-decoration {
            position: absolute;
            width: 1px;
            height: 40%;
            background: linear-gradient(to bottom, transparent, var(--artdeco-gold-primary), transparent);
            opacity: 0.3;

            &--left {
                left: var(--artdeco-spacing-md);
            }

            &--right {
                right: var(--artdeco-spacing-md);
            }
        }

        // 金色分隔线
        .breadcrumb-separator-line {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 1px;
            background: linear-gradient(90deg, transparent 0%, var(--artdeco-gold-primary) 50%, transparent 100%);
            opacity: 0.2;
        }

        // 右侧角落装饰
        .breadcrumb-corner-decoration {
            position: absolute;
            top: 0;
            right: 0;
            width: 20px;
            height: 20px;
            opacity: 0.15;
            z-index: 1;

            svg {
                width: 100%;
                height: 100%;
            }
        }
    }

    .breadcrumb-list {
        position: relative;
        z-index: 2;
        display: flex;
        align-items: center;
        list-style: none;
        margin: 0;
        padding: 0;
        gap: 0;
    }

    .breadcrumb-item {
        display: flex;
        align-items: center;
    }

    .breadcrumb-link {
        display: inline-flex;
        align-items: center;
        gap: var(--artdeco-spacing-xs);
        font-family: var(--artdeco-font-heading);
        font-size: var(--artdeco-font-size-sm);
        font-weight: var(--artdeco-font-weight-semibold);
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: var(--artdeco-breadcrumb-text);
        text-decoration: none;
        transition: all var(--artdeco-transition-normal) var(--artdeco-ease-out);
        cursor: pointer;

        &:hover {
            color: var(--artdeco-breadcrumb-text-hover);
            text-shadow: 0 0 10px rgba(212, 175, 55, 0.3);
        }

        &--active {
            color: var(--artdeco-breadcrumb-text-active);
            font-weight: var(--artdeco-font-weight-bold);
            cursor: default;
            text-shadow: 0 0 15px rgba(212, 175, 55, 0.4);
        }
    }

    .breadcrumb-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: var(--artdeco-font-size-base);
        color: inherit;
        opacity: 0.7;
        transition: all var(--artdeco-transition-normal) var(--artdeco-ease-out);
    }

    .breadcrumb-text {
        display: inline-block;
    }

    .breadcrumb-divider {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        margin: 0 var(--artdeco-spacing-sm);
        color: var(--artdeco-gold-primary);
        opacity: 0.4;

        svg {
            width: 100%;
            height: 100%;
            stroke-width: 2;
        }
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .artdeco-breadcrumb {
            height: var(--artdeco-spacing-lg);
            padding: 0 var(--artdeco-spacing-md);

            .breadcrumb-decoration {
                height: 30%;
            }

            .breadcrumb-corner-decoration {
                width: 15px;
                height: 15px;
            }
        }

        .breadcrumb-link {
            font-size: var(--artdeco-font-size-xs);
            letter-spacing: 0.1em;
        }

        .breadcrumb-divider {
            width: 16px;
            height: 16px;
            margin: 0 var(--artdeco-spacing-xs);
        }
    }

    @media (max-width: 480px) {
        // 移动端：隐藏中间面包屑，只显示首页和当前页
        .breadcrumb-item:not(:first-child):not(:last-child) {
            display: none;
        }

        .breadcrumb-item:last-child .breadcrumb-link::before {
            content: '...';
            margin-right: var(--artdeco-spacing-xs);
            color: var(--artdeco-gold-primary);
        }
    }

    /* 大屏幕优化 */
    @media (min-width: 1440px) {
        .artdeco-breadcrumb {
            padding: 0 var(--artdeco-spacing-xl);
        }

        .breadcrumb-link {
            font-size: var(--artdeco-font-size-base);
        }
    }

    /* 打印样式 */
    @media print {
        .artdeco-breadcrumb {
            background: white;
            border-bottom: 1px solid #000;

            .breadcrumb-decoration,
            .breadcrumb-separator-line,
            .breadcrumb-corner-decoration {
                display: none;
            }
        }

        .breadcrumb-link {
            color: #000;
        }
    }

    /* 可访问性增强 */
    @media (prefers-reduced-motion: reduce) {
        .breadcrumb-link {
            transition: none;
        }
    }

    /* 高对比度模式 */
    @media (prefers-contrast: high) {
        .artdeco-breadcrumb {
            border-bottom: 2px solid var(--artdeco-gold-primary);
        }

        .breadcrumb-link {
            text-decoration: underline;
            text-underline-offset: 2px;
        }

        .breadcrumb-link--active {
            text-decoration: none;
        }
    }
</style>
