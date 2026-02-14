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
 * 导出类型定义
 */
export type { AriaProps }

