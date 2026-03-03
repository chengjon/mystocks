import { describe, expect, it } from 'vitest'
import { ARTDECO_MENU_ITEMS } from '@/layouts/MenuConfig'

describe('ARTDECO_MENU_ITEMS strategy domain', () => {
  it('includes strategy parameters and signals menu entries', () => {
    const strategyDomain = ARTDECO_MENU_ITEMS.find(item => item.path === '/strategy')
    const childPaths = strategyDomain?.children?.map(item => item.path) ?? []

    expect(childPaths).toContain('/strategy/parameters')
    expect(childPaths).toContain('/strategy/signals')
  })
})
