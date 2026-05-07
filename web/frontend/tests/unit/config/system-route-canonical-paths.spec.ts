import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const routerSource = readFileSync(resolve(process.cwd(), 'src/router/index.ts'), 'utf8')

describe('system route canonical component paths', () => {
  it('uses the canonical system settings component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/system/Settings.vue')")
  })

  it('uses the canonical system health component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/system/Health.vue')")
  })

  it('uses the canonical system API component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/system/API.vue')")
  })

  it('uses the canonical system resources component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/system/Resources.vue')")
  })

  it('uses the canonical system data-source component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/system/DataSource.vue')")
  })
})
