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

/**
 * 导出类型定义
 */
export interface AriaProps {
    'aria-label'?: string
    'aria-labelledby'?: string
    'aria-describedby'?: string
    'aria-live'?: 'off' | 'polite' | 'assertive'
    'aria-atomic'?: boolean | 'false' | 'true'
    'aria-relevant'?: 'additions' | 'removals' | 'text' | 'all'
    'aria-disabled'?: boolean | 'false' | 'true'
    'aria-hidden'?: boolean | 'false' | 'true'
    'aria-expanded'?: boolean | 'false' | 'true'
    'aria-controls'?: string
    'aria-haspopup'?: boolean | 'false' | 'true' | 'menu' | 'listbox' | 'tree' | 'grid' | 'dialog'
    'aria-pressed'?: boolean | 'false' | 'true' | 'mixed'
    'aria-current'?: boolean | 'false' | 'true' | 'page' | 'step' | 'location' | 'date' | 'time'
    'aria-required'?: boolean | 'false' | 'true'
    'aria-invalid'?: boolean | 'false' | 'true' | 'grammar' | 'spelling'
    'aria-readonly'?: boolean | 'false' | 'true'
    'aria-checked'?: boolean | 'false' | 'true' | 'mixed'
    'aria-selected'?: boolean | 'false' | 'true'
    'aria-activedescendant'?: string
    'aria-owns'?: string
    'aria-errormessage'?: string
    'aria-modal'?: boolean | 'false' | 'true'
    'aria-orientation'?: 'horizontal' | 'vertical'
    'aria-valuenow'?: number
    'aria-valuetext'?: string
    'aria-valuemin'?: number
    'aria-valuemax'?: number
    'aria-sort'?: 'ascending' | 'descending' | 'none' | 'other'
    'aria-colcount'?: number
    'aria-rowcount'?: number
    'aria-colindex'?: number
    'aria-rowindex'?: number
    'aria-colspan'?: number
    'aria-rowspan'?: number
    'aria-setsize'?: number
    'aria-posinset'?: number
    'aria-level'?: number
    'aria-multiselectable'?: boolean | 'false' | 'true'
    'aria-dropeffect'?: 'copy' | 'move' | 'link' | 'execute' | 'popup' | 'none'
    'aria-grabbed'?: boolean | 'false' | 'true'
    'aria-autocomplete'?: 'inline' | 'list' | 'both' | 'none'
    'aria-busy'?: boolean | 'false' | 'true'
    role?: string
    tabindex?: number | string
    [key: `aria-${string}`]: unknown
}

export interface HtmlProps {
    id?: string
    class?: string | Record<string, boolean> | Array<string | Record<string, boolean>>
    style?: string | Record<string, string>
    title?: string
    lang?: string
    dir?: 'ltr' | 'rtl' | 'auto'
    hidden?: boolean | 'hidden' | 'until-found'
}
