import { computed, type ComputedRef } from 'vue'

import type { AriaProps } from './unknown'

export const createDecorativeAria = (): ComputedRef<AriaProps> =>
  computed(() => ({
    'aria-hidden': true,
    role: 'presentation',
  }))

export const createNavigationAria = (label: string): ComputedRef<AriaProps> =>
  computed(() => ({
    role: 'navigation',
    'aria-label': label,
  }))

export const createMainAria = (label: string): ComputedRef<AriaProps> =>
  computed(() => ({
    role: 'main',
    'aria-label': label,
  }))

export const createSearchAria = (label = '搜索'): ComputedRef<AriaProps> =>
  computed(() => ({
    role: 'search',
    'aria-label': label,
  }))

export const createHintId = (
  fieldName: string,
  hintType: 'hint' | 'error' | 'description' = 'hint'
): string => `${fieldName}-${hintType}`
