import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const appSource = readFileSync(resolve(process.cwd(), 'src/App.vue'), 'utf8')
const authStoreSource = readFileSync(resolve(process.cwd(), 'src/stores/auth.ts'), 'utf8')
const loginSource = readFileSync(resolve(process.cwd(), 'src/views/Login.vue'), 'utf8')
const notFoundSource = readFileSync(resolve(process.cwd(), 'src/views/NotFound.vue'), 'utf8')

describe('shell route runtime guardrails', () => {
  it('gives Blank layout routes a dedicated runtime shell branch', () => {
    expect(appSource).toContain("route.meta.layout === 'Blank'")
    expect(appSource).toContain("app-shell--blank")
    expect(appSource).toContain(":data-layout=\"isBlankLayout ? 'blank' : 'default'\"")
  })

  it('keeps login page status feedback inside the page shell', () => {
    expect(loginSource).toContain("role=\"status\"")
    expect(loginSource).toContain("aria-live=\"polite\"")
    expect(loginSource).toContain("status-message--error")
    expect(loginSource).toContain("status-message--success")
  })

  it('bridges login loading state through the shared auth store', () => {
    expect(authStoreSource).toContain('const loginPending = ref(false)')
    expect(authStoreSource).toContain('const isLoading = computed(() => loginPending.value || loginStore.isLoading)')
    expect(authStoreSource).toContain('loginPending.value = true')
    expect(authStoreSource).toContain('loginPending.value = false')
    expect(loginSource).toContain('const loading = computed(() => authStore.isLoading)')
  })

  it('hides seeded test-account hints outside explicit dev flags', () => {
    expect(loginSource).toContain("import.meta.env.DEV || import.meta.env.VITE_SHOW_TEST_ACCOUNTS === '1'")
    expect(loginSource).toContain('v-if="showTestAccounts"')
  })

  it('keeps the 404 shell on ArtDeco runtime tokens', () => {
    expect(notFoundSource).toContain('var(--artdeco-bg-global)')
    expect(notFoundSource).toContain('var(--artdeco-gold-primary)')
    expect(notFoundSource).toContain('var(--artdeco-fg-primary)')

    expect(notFoundSource).not.toContain('var(--bg-primary)')
    expect(notFoundSource).not.toContain('var(--gold-primary)')
    expect(notFoundSource).not.toContain('var(--text-primary)')
  })

  it('routes the 404 recovery action through canonical home-route truth', () => {
    expect(notFoundSource).toContain("import { HOME_ROUTE_PATH } from '@/router/homeRoute'")
    expect(notFoundSource).toContain('router.push(HOME_ROUTE_PATH)')
    expect(notFoundSource).not.toContain("router.push('/')")
  })

  it('keeps blank-layout shells free of shared request and stats chrome', () => {
    expect(loginSource).not.toContain('REQ_ID')
    expect(loginSource).not.toContain('TRACE_ID')
    expect(loginSource).not.toContain('ArtDecoStatCard')

    expect(notFoundSource).not.toContain('REQ_ID')
    expect(notFoundSource).not.toContain('TRACE_ID')
    expect(notFoundSource).not.toContain('ArtDecoStatCard')
  })
})
