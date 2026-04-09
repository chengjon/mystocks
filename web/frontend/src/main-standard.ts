import { createApp } from 'vue'
import { createPinia } from 'pinia'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router/index.ts'
import ArtDecoCardCompact from '@/components/artdeco/base/ArtDecoCardCompact.vue'

// --- Style imports (ordered: base → theme → overrides → optimization) ---
import './styles/index.scss'
import './styles/artdeco-global.scss'
import './styles/artdeco-financial.scss'
import './styles/fintech-design-system.scss'
import './styles/element-plus-override.scss'
import './styles/visual-optimization.scss'
import './styles/pro-fintech-optimization.scss'

// --- Services (async init after mount) ---
import { initializeSecurity } from './services/httpClient.js'
import { ContractValidationError } from './api/unifiedApiClient.ts'
import { showVersionNotifications } from './services/versionNegotiator.ts'

// --- Performance: ECharts tree-shaking ---
import './utils/echarts.ts'

// ============================================================
//  App initialization
// ============================================================

const app = createApp(App)
const pinia = createPinia()

// Global component registrations
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
app.component('ArtDecoCardCompact', ArtDecoCardCompact)

app.use(pinia)
app.use(router)

// Global error handler — contract validation drift detection
app.config.errorHandler = (err, _instance, info) => {
  if (err instanceof ContractValidationError) {
    if (import.meta.env.DEV) {
      console.error(`API Contract Drift: ${err.message}`)
    } else {
      console.error('Contract validation failed:', err.message)
    }
    return
  }
  console.error('Global error:', err, info)
}

// Synchronous mount — UI renders immediately
app.mount('#app')

if (import.meta.env.DEV) {
  console.log('[MyStocks] App mounted')
}

// ============================================================
//  Async initialization (non-blocking, after mount)
// ============================================================

// PWA: Service Worker registration (post-load, non-blocking)
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing
          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                console.log('[MyStocks] New content available — refresh to update')
              }
            })
          }
        })
        navigator.serviceWorker.addEventListener('controllerchange', () => {
          window.location.reload()
        })
      })
      .catch((error) => {
        console.warn('[MyStocks] SW registration failed:', error)
      })
  })
}

// Security init with 2-second timeout race (non-blocking)
const initPromise = Promise.race([
  initializeSecurity().catch((err) => {
    console.warn('[MyStocks] Security init failed:', err)
    return null
  }),
  new Promise<null>((resolve) =>
    setTimeout(() => {
      console.warn('[MyStocks] Security init timed out (non-blocking)')
      resolve(null)
    }, 2000)
  )
])

initPromise
  .then(() => {
    // API version negotiation (after security completes)
    try {
      showVersionNotifications()
    } catch (err) {
      console.warn('[MyStocks] Version notification failed:', err)
    }

    // Session restore (dynamic import, non-blocking)
    import('./utils/sessionRestore.js')
      .then(({ restoreSession }) => {
        restoreSession().catch((err) => {
          console.warn('[MyStocks] Session restore failed:', err)
        })
      })
      .catch((err) => {
        console.warn('[MyStocks] Session restore import failed:', err)
      })
  })
  .catch((err) => {
    console.warn('[MyStocks] Init chain error:', err)
  })

// Browser debugging access
// eslint-disable-next-line @typescript-eslint/no-explicit-any
if (typeof window !== 'undefined') {
  (window as any).$vue = app
}
