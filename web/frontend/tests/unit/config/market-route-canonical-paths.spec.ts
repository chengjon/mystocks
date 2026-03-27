import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const routerSource = readFileSync(resolve(process.cwd(), 'src/router/index.ts'), 'utf8')

describe('market route canonical component paths', () => {
  it('uses the canonical market realtime component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/market/Realtime.vue')")
  })

  it('uses the canonical market technical component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/market/Technical.vue')")
  })

  it('uses the canonical market lhb component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/market/LHB.vue')")
  })
})
