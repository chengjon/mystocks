import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const routerSource = readFileSync(resolve(process.cwd(), 'src/router/index.ts'), 'utf8')
const menuSource = readFileSync(resolve(process.cwd(), 'src/config/menu.config.js'), 'utf8')

describe('ai route canonical component paths', () => {
  it('uses the canonical ai sentiment component path', () => {
    expect(routerSource).toContain("component: () => import('@/views/ai/Sentiment.vue')")
  })

  it('registers the ai sentiment route name', () => {
    expect(routerSource).toContain("name: 'ai-sentiment'")
  })

  it('uses the canonical ai ml workbench component path', () => {
    expect(routerSource).toContain("path: 'ml'")
    expect(routerSource).toContain("name: 'ai-ml'")
    expect(routerSource).toContain("component: () => import('@/views/ai/MlWorkbench.vue')")
  })

  it('surfaces the ai ml workbench from ai navigation', () => {
    expect(menuSource).toContain("id: 'ai-ml'")
    expect(menuSource).toContain("title: '模型训练 / 预测'")
    expect(menuSource).toContain("path: '/ai/ml'")
  })

  it('uses the canonical ai batch analysis component path', () => {
    expect(routerSource).toContain("path: 'batch'")
    expect(routerSource).toContain("name: 'ai-batch'")
    expect(routerSource).toContain("component: () => import('@/views/ai/BatchAnalysis.vue')")
  })

  it('surfaces the ai batch analysis workbench from ai navigation', () => {
    expect(menuSource).toContain("id: 'ai-batch'")
    expect(menuSource).toContain("title: '批量分析'")
    expect(menuSource).toContain("path: '/ai/batch'")
  })
})
