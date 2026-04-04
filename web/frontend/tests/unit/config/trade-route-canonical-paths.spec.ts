import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const routerSource = readFileSync(resolve(process.cwd(), 'src/router/index.ts'), 'utf8')

describe('trade route canonical component paths', () => {
  it('uses the canonical trade center component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/trade/Center.vue')")
  })

  it('uses the canonical trade signals component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/trade/Signals.vue')")
  })

  it('uses the canonical trade portfolio component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/trade/Portfolio.vue')")
  })

  it('uses the canonical trade history component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/trade/History.vue')")
  })
})
