import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const routerSource = readFileSync(resolve(process.cwd(), 'src/router/index.ts'), 'utf8')

describe('risk route canonical component paths', () => {
  it('uses the canonical risk center component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/risk/Center.vue')")
  })

  it('uses the canonical risk overview component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/risk/Overview.vue')")
  })

  it('uses the canonical risk stop-loss component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/risk/StopLoss.vue')")
  })

  it('uses the canonical risk alerts component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/risk/Alerts.vue')")
  })

  it('uses the canonical risk news component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/risk/News.vue')")
  })
})
