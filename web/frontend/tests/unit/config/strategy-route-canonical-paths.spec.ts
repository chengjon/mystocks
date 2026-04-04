import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const routerSource = readFileSync(resolve(process.cwd(), 'src/router/index.ts'), 'utf8')

describe('strategy route canonical component paths', () => {
  it('uses the canonical strategy list component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/strategy/List.vue')")
  })

  it('uses the canonical strategy parameters component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/strategy/Parameters.vue')")
  })

  it('uses the canonical strategy backtest component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/strategy/Backtest.vue')")
  })

  it('uses the canonical strategy optimization component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/strategy/Optimization.vue')")
  })
})
