/**
 * MyStocks ARIA Accessibility Enhancement Composable
 * MyStocks ARIA 无障碍性增强 Composable
 *
 * Purpose: 提供统一的ARIA标签管理，简化组件无障碍性实现
 *          Provide unified ARIA label management for component accessibility
 *
 * Version: 1.0
 * Created: 2026-01-13
 * Priority: P1 - Accessibility Enhancement
 *
 * WCAG Compliance:
 * - 1.1.1 Text Alternatives (Level A)
 * - 1.3.1 Info and Relationships (Level A)
 * - 1.3.2 Meaningful Sequence (Level A)
 * - 2.4.4 Link Purpose (Level A)
 * - 4.1.2 Name, Role, Value (Level A)
 *
 * Usage:
 * import { useAria } from '@/composables/useAria'
 *
 * // 按钮
 * const buttonAria = useAria().button('执行交易', { disabled: false })
 * <ArtDecoButton v-bind="buttonAria">执行交易</ArtDecoButton>
 *
 * // 实时数据卡片
 * const statAria = useAria().liveRegion('上证指数', 'polite')
 * <ArtDecoStatCard v-bind="statAria" ... />
 *
 * // 表单输入
 * const inputAria = useAria().input('股票代码', {
 *   required: true,
 *   describedBy: 'stock-code-hint'
 * })
 */

import { computed, type ComputedRef } from 'vue'

/**
 * ARIA标签管理接口（不包含HTML属性如tabindex）
 */
interface AriaProps {
    'aria-label'?: string
    'aria-labelledby'?: string
    'aria-describedby'?: string
    'aria-hidden'?: boolean | 'true' | 'false'
    'aria-live'?: 'polite' | 'assertive' | 'off'
    'aria-atomic'?: boolean | 'true' | 'false'
    'aria-busy'?: boolean | 'true' | 'false'
    'aria-controls'?: string
    'aria-current'?: 'page' | 'step' | 'location' | 'date' | 'time' | 'true' | 'false'
    'aria-disabled'?: boolean | 'true' | 'false'
    'aria-expanded'?: boolean | 'true' | 'false'
    'aria-haspopup'?: boolean | 'true' | 'false' | 'menu' | 'listbox' | 'tree' | 'grid' | 'dialog'
    'aria-pressed'?: boolean | 'true' | 'false' | 'mixed'
    'aria-selected'?: boolean | 'true' | 'false'
    'aria-checked'?: boolean | 'true' | 'false' | 'mixed'
    'aria-required'?: boolean | 'true' | 'false'
    'aria-invalid'?: boolean | 'true' | 'false'
    'aria-errormessage'?: string
    'aria-modal'?: boolean | 'true' | 'false'
    'aria-orientation'?: 'horizontal' | 'vertical'
    'aria-valuemin'?: number
    'aria-valuemax'?: number
    'aria-valuenow'?: number
    'aria-valuetext'?: string
    role?: string
}

/**
 * HTML属性接口（包含tabindex等非ARIA属性）
 */
interface HtmlProps {
    tabindex?: number | string
    [key: string]: any
}

/**
 * useAria Composable
 * 提供各种UI元素的ARIA标签生成器
 */
export function useAria() {
    /**
     * 按钮ARIA标签
     * Button ARIA labels
     *
     * @param label - 按钮描述（如果按钮文字不够描述性）
     * @param options - 选项
     */
    const button = (
        label?: string,
        options: {
            disabled?: boolean
            pressed?: boolean
            expanded?: boolean
            hasPopup?: boolean | 'menu' | 'listbox' | 'tree' | 'grid' | 'dialog'
            controls?: string
        } = {}
    ): ComputedRef<AriaProps> => {
        return computed(() => {
            const aria: AriaProps = {}

            if (label) {
                aria['aria-label'] = label
            }

            if (options.disabled !== undefined) {
                aria['aria-disabled'] = options.disabled
            }

            if (options.pressed !== undefined) {
                aria['aria-pressed'] = options.pressed
            }

            if (options.expanded !== undefined) {
                aria['aria-expanded'] = options.expanded
            }

            if (options.hasPopup !== undefined) {
                aria['aria-haspopup'] = options.hasPopup
            }

            if (options.controls) {
                aria['aria-controls'] = options.controls
            }

            return aria
        })
    }

    /**
     * 链接ARIA标签
     * Link ARIA labels
     *
     * @param label - 链接描述（如果链接文字不够描述性）
     * @param current - 是否为当前页面
     */
    const link = (
        label?: string,
        options: {
            current?: boolean
            describedBy?: string
        } = {}
    ): ComputedRef<AriaProps> => {
        return computed(() => {
            const aria: AriaProps = {}

            if (label) {
                aria['aria-label'] = label
            }

            if (options.current) {
                aria['aria-current'] = 'page'
            }

            if (options.describedBy) {
                aria['aria-describedby'] = options.describedBy
            }

            return aria
        })
    }

    /**
     * 输入框ARIA标签
     * Input field ARIA labels
     *
     * @param label - 输入框标签
     * @param options - 选项
     */
    const input = (
        label: string,
        options: {
            required?: boolean
            invalid?: boolean
            errorMessage?: string
            describedBy?: string
            placeholder?: string
        } = {}
    ): ComputedRef<AriaProps> => {
        return computed(() => {
            const aria: AriaProps = {
                'aria-label': label
            }

            if (options.required) {
                aria['aria-required'] = true
            }

            if (options.invalid !== undefined) {
                aria['aria-invalid'] = options.invalid
            }

            if (options.errorMessage) {
                aria['aria-errormessage'] = options.errorMessage
            }

            if (options.describedBy) {
                aria['aria-describedby'] = options.describedBy
            }

            return aria
        })
    }

    /**
     * 实时数据区域ARIA标签
     * Live region ARIA labels (for dynamic content)
     *
     * @param label - 区域标签
     * @param politeness - 礼貌级别（polite/assertive）
     */
    const liveRegion = (label: string, politeness: 'polite' | 'assertive' = 'polite'): ComputedRef<AriaProps> => {
        return computed(() => ({
            'aria-label': label,
            'aria-live': politeness,
            'aria-atomic': true
        }))
    }

    /**
     * 模态框ARIA标签
     * Modal/Dialog ARIA labels
     *
     * @param label - 模态框标签
     * @param options - 选项
     */
    const modal = (
        label: string,
        options: {
            describedBy?: string
            labelledBy?: string
        } = {}
    ): ComputedRef<AriaProps> => {
        return computed(() => {
            const aria: AriaProps = {
                role: 'dialog',
                'aria-modal': true,
                'aria-label': label
            }

            if (options.describedBy) {
                aria['aria-describedby'] = options.describedBy
            }

            if (options.labelledBy) {
                aria['aria-labelledby'] = options.labelledBy
                delete aria['aria-label'] // 使用 labelledBy 时不需要 aria-label
            }

            return aria
        })
    }

    /**
     * 卡片ARIA标签（可点击卡片）
     * Card ARIA labels (clickable cards)
     *
     * @param label - 卡片描述
     * @param options - 选项
     */
    const card = (
        label: string,
        options: {
            selected?: boolean
            expanded?: boolean
            hasPopup?: boolean
        } = {}
    ): ComputedRef<AriaProps & HtmlProps> => {
        return computed(() => {
            const aria: AriaProps & HtmlProps = {
                role: 'button',
                'aria-label': label,
                tabindex: 0
            }

            if (options.selected !== undefined) {
                aria['aria-selected'] = options.selected
            }

            if (options.expanded !== undefined) {
                aria['aria-expanded'] = options.expanded
            }

            if (options.hasPopup) {
                aria['aria-haspopup'] = options.hasPopup
            }

            return aria
        })
    }

    /**
     * 选择器ARIA标签（Radio/Checkbox/Select）
     * Selection ARIA labels
     *
     * @param label - 选择器标签
     * @param options - 选项
     */
    const selection = (
        label: string,
        options: {
            checked?: boolean | 'mixed'
            required?: boolean
            invalid?: boolean
            describedBy?: string
        } = {}
    ): ComputedRef<AriaProps> => {
        return computed(() => {
            const aria: AriaProps = {
                'aria-label': label
            }

            if (options.checked !== undefined) {
                aria['aria-checked'] = options.checked
            }

            if (options.required) {
                aria['aria-required'] = true
            }

            if (options.invalid !== undefined) {
                aria['aria-invalid'] = options.invalid
            }

            if (options.describedBy) {
                aria['aria-describedby'] = options.describedBy
            }

            return aria
        })
    }

    /**
     * 标签页ARIA标签
     * Tab ARIA labels
     *
     * @param label - 标签页标签
     * @param options - 选项
     */
    const tab = (
        label: string,
        options: {
            selected?: boolean
            controls?: string
            panelId?: string
        } = {}
    ): ComputedRef<AriaProps> => {
        return computed(() => {
            const aria: AriaProps = {
                role: 'tab',
                'aria-label': label
            }

            if (options.selected !== undefined) {
                aria['aria-selected'] = options.selected
            }

            if (options.controls) {
                aria['aria-controls'] = options.controls
            }

            return aria
        })
    }

    /**
     * 列表ARIA标签
     * List ARIA labels
     *
     * @param label - 列表标签
     * @param options - 选项
     */
    const list = (
        label: string,
        options: {
            orientation?: 'horizontal' | 'vertical'
        } = {}
    ): ComputedRef<AriaProps> => {
        return computed(() => {
            const aria: AriaProps = {
                role: 'list',
                'aria-label': label
            }

            if (options.orientation) {
                aria['aria-orientation'] = options.orientation
            }

            return aria
        })
    }

    /**
     * 进度条/滑块ARIA标签
     * Progress/Slider ARIA labels
     *
     * @param label - 标签
     * @param options - 选项
     */
    const progress = (
        label: string,
        options: {
            valueNow?: number
            min?: number
            max?: number
            valueText?: string
            busy?: boolean
        } = {}
    ): ComputedRef<AriaProps> => {
        return computed(() => {
            const aria: AriaProps = {
                role: 'progressbar',
                'aria-label': label
            }

            if (options.valueNow !== undefined) {
                aria['aria-valuenow'] = options.valueNow
            }

            if (options.min !== undefined) {
                aria['aria-valuemin'] = options.min
            }

            if (options.max !== undefined) {
                aria['aria-valuemax'] = options.max
            }

            if (options.valueText) {
                aria['aria-valuetext'] = options.valueText
            }

            if (options.busy !== undefined) {
                aria['aria-busy'] = options.busy
            }

            return aria
        })
    }

    /**
     * 工具提示ARIA标签
     * Tooltip ARIA labels
     *
     * @param label - 工具提示内容
     * @param describedBy - 关联的元素ID
     */
    const tooltip = (label: string, describedBy?: string): ComputedRef<AriaProps> => {
        return computed(() => {
            const aria: AriaProps = {
                'aria-label': label
            }

            if (describedBy) {
                aria['aria-describedby'] = describedBy
            }

            return aria
        })
    }

    /**
     * 隐藏装饰性元素
     * Hide decorative elements from screen readers
     */
    const decorative = (): ComputedRef<AriaProps> => {
        return computed(() => ({
            'aria-hidden': true,
            role: 'presentation'
        }))
    }

    /**
     * 导航ARIA标签
     * Navigation ARIA labels
     *
     * @param label - 导航区域标签
     */
    const navigation = (label: string): ComputedRef<AriaProps> => {
        return computed(() => ({
            role: 'navigation',
            'aria-label': label
        }))
    }

    /**
     * 主要内容ARIA标签
     * Main content ARIA labels
     *
     * @param label - 主要内容标签
     */
    const main = (label: string): ComputedRef<AriaProps> => {
        return computed(() => ({
            role: 'main',
            'aria-label': label
        }))
    }

    /**
     * 搜索ARIA标签
     * Search ARIA labels
     *
     * @param label - 搜索框标签
     */
    const search = (label: string = '搜索'): ComputedRef<AriaProps> => {
        return computed(() => ({
            role: 'search',
            'aria-label': label
        }))
    }

    /**
     * 辅助技术提示文本ID生成器
     * Generate hint text ID for assistive technologies
     *
     * @param fieldName - 字段名
     * @param hintType - 提示类型（hint/error/description）
     */
    const hintId = (fieldName: string, hintType: 'hint' | 'error' | 'description' = 'hint'): string => {
        return `${fieldName}-${hintType}`
    }

    return {
        button,
        link,
        input,
        liveRegion,
        modal,
        card,
        selection,
        tab,
        list,
        progress,
        tooltip,
        decorative,
        navigation,
        main,
        search,
        hintId
    }
}

/**
 * 导出类型定义
 */
export type { AriaProps }
