import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const routerSource = readFileSync(resolve(process.cwd(), 'src/router/index.ts'), 'utf8')

describe('data route canonical component paths', () => {
  it('uses the canonical data industry component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/data/Industry.vue')")
  })

  it('uses the canonical data concept component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/data/Concepts.vue')")
  })

  it('uses the canonical data fund flow component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/data/FundFlow.vue')")
  })

  it('uses the canonical data advanced analysis component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/data/Advanced.vue')")
  })
})
