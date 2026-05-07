import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const routerSource = readFileSync(resolve(process.cwd(), 'src/router/index.ts'), 'utf8')

describe('ai route canonical component paths', () => {
  it('uses the canonical ai sentiment component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/ai/Sentiment.vue')")
  })

  it('registers the ai sentiment route name', () => {
    expect(routerSource).toContain("name: 'ai-sentiment'")
  })
})
