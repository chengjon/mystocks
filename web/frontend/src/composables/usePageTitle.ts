/**
 * 页面标题管理 Composable
 *
 * 为Vue组件提供便捷的页面标题和Meta标签管理功能
 */

import { ref, computed, watch, onMounted, onUnmounted, readonly } from 'vue'
import { useRoute } from 'vue-router'
import { titleManager } from '@/services/titleManager'
import { titleGenerator, TitleGenerator } from '@/services/titleGenerator'
import { useAuthStore } from '@/stores/auth'
import type { TitleConfig, MetaConfig } from '@/services/titleManager'
import type { TitleContext, ConditionalTitleRule } from '@/services/titleGenerator'

export function usePageTitle() {
    const route = useRoute()
    const authStore = useAuthStore()

    // 响应式状态
    const currentTitle = ref('')
    const isDynamic = ref(false)

    // 计算属性
    const hasCustomTitle = computed(() => currentTitle.value !== '')
    const titleContext = computed(
        (): TitleContext => ({
            user: {
                username: authStore.user?.username,
                role: authStore.user?.roles?.[0] || authStore.user?.role,
                id: authStore.user?.id
            },
            route: {
                params: route.params as Record<string, string>,
                query: route.query as Record<string, string>,
                name: route.name as string,
                path: route.path
            },
            app: {
                name: 'MyStocks',
                version: import.meta.env.VITE_APP_VERSION || '1.0.0',
                environment: import.meta.env.MODE
            }
        })
    )

    // 设置页面标题
    const setTitle = (config: Partial<TitleConfig> | string) => {
        titleManager.setTitle(config)
        currentTitle.value = typeof config === 'string' ? config : config.title || ''
        isDynamic.value = typeof config === 'object' && config.dynamic === true
    }

    // 设置Meta标签
    const setMeta = (config: MetaConfig) => {
        titleManager.setMeta(config)
    }

    // 生成动态标题
    const generateTitle = (template: string, context?: TitleContext) => {
        return titleGenerator.generate(template, context || titleContext.value)
    }

    // 生成高级标题（支持条件表达式）
    const generateAdvancedTitle = (template: string, context?: TitleContext) => {
        return titleGenerator.generateAdvanced(template, context || titleContext.value)
    }

    // 基于数据更新标题
    const updateTitleFromData = (data: unknown, template: string, dataKey: string = 'name', fallbackTitle?: string) => {
        if (!data) {
            if (fallbackTitle) setTitle(fallbackTitle)
            return
        }

        const context: TitleContext = {
            ...titleContext.value,
            data: { [dataKey]: (data as Record<string, unknown>)[dataKey] || data }
        }

        const title = generateTitle(template, context)
        setTitle({ title, dynamic: true })
    }

    // 监听数据变化自动更新标题
    const watchDataForTitle = (
        dataRef: unknown,
        template: string,
        options: {
            dataKey?: string
            fallbackTitle?: string
            immediate?: boolean
        } = {}
    ) => {
        const { dataKey = 'name', fallbackTitle, immediate = true } = options

        const stopWatcher = watch(
            dataRef as object,
            newData => {
                updateTitleFromData(newData, template, dataKey, fallbackTitle)
            },
            { immediate }
        )

        // 返回停止函数，允许组件手动停止监听
        return stopWatcher
    }

    // 使用预定义模板
    const useTemplate = (templateName: keyof typeof TitleGenerator.TEMPLATES) => {
        const template = TitleGenerator.TEMPLATES[templateName]
        const title = generateTitle(template)
        setTitle({ title, dynamic: true })
    }

    // 使用条件规则
    const useConditionalRules = (ruleName: keyof typeof TitleGenerator.CONDITIONAL_RULES) => {
        const rules = [...TitleGenerator.CONDITIONAL_RULES[ruleName]] as ConditionalTitleRule[]
        const title = titleGenerator.generateConditional(rules, titleContext.value)
        setTitle({ title, dynamic: true })
    }

    // SEO优化设置
    const setSEOOptimized = (config: {
        title: string
        description: string
        keywords?: string[]
        image?: string
        url?: string
        type?: 'website' | 'article'
    }) => {
        titleManager.setSEOOptimized(config)
        currentTitle.value = config.title
        isDynamic.value = true
    }

    // 重置标题
    const resetTitle = () => {
        titleManager.reset()
        currentTitle.value = ''
        isDynamic.value = false
    }

    // 获取当前标题信息
    const getTitleInfo = () => ({
        title: titleManager.getCurrentTitle(),
        meta: titleManager.getCurrentMeta(),
        isDynamic: isDynamic.value,
        context: titleContext.value
    })

    // 批量更新
    const updatePage = (config: { title?: Partial<TitleConfig> | string; meta?: MetaConfig }) => {
        titleManager.updatePage(config)
        if (config.title) {
            currentTitle.value = typeof config.title === 'string' ? config.title : config.title.title || ''
            isDynamic.value = typeof config.title === 'object' && config.title.dynamic === true
        }
    }

    // 生命周期管理
    onMounted(() => {
        // 组件挂载时可以执行一些初始化逻辑
        if (import.meta.env.DEV) {
            console.log('📄 PageTitle composable mounted for route:', route.name)
        }
    })

    onUnmounted(() => {
        // 组件卸载时可以清理状态
        if (isDynamic.value && import.meta.env.DEV) {
            console.log('📄 PageTitle composable unmounted, title was dynamic')
        }
    })

    return {
        // 状态
        currentTitle: readonly(currentTitle),
        isDynamic: readonly(isDynamic),
        hasCustomTitle,
        titleContext,

        // 基本方法
        setTitle,
        setMeta,
        resetTitle,

        // 动态标题方法
        generateTitle,
        generateAdvancedTitle,
        updateTitleFromData,
        watchDataForTitle,

        // 预定义方法
        useTemplate,
        useConditionalRules,

        // SEO方法
        setSEOOptimized,

        // 高级方法
        updatePage,
        getTitleInfo
    }
}
