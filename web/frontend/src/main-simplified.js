// ============================================
//   SIMPLIFIED MAIN.JS - For Debugging
//   Minimal imports to isolate the issue
// ============================================

console.log('🔍 Step 1: main.js started')

import { createApp } from 'vue'
console.log('✅ Step 2: Vue imported')

import { createPinia } from 'pinia'
console.log('✅ Step 3: Pinia imported')

import App from './App.vue'
console.log('✅ Step 4: App.vue imported')

import router from './router/index.ts'
console.log('✅ Step 5: Router imported')

// ArtDeco tokens only (minimal CSS)
import './styles/artdeco-tokens.scss'
console.log('✅ Step 6: ArtDeco tokens loaded')

console.log('🔍 Step 7: Creating Vue app instance...')

const app = createApp(App)
const pinia = createPinia()

console.log('🔍 Step 8: Registering Pinia...')

try {
  app.use(pinia)
  console.log('✅ Step 9: Pinia registered')
} catch (error) {
  console.error('❌ FAILED to register Pinia:', error)
}

console.log('🔍 Step 10: Registering Router...')

try {
  app.use(router)
  console.log('✅ Step 11: Router registered')
} catch (error) {
  console.error('❌ FAILED to register Router:', error)
  console.error('Error details:', error.stack)
}

console.log('🔍 Step 12: Mounting Vue app to #app...')

try {
  const mountedApp = app.mount('#app')
  console.log('✅✅✅ SUCCESS: Vue app mounted!')
  console.log('Mounted app:', mountedApp)

  // Verify router is working
  setTimeout(() => {
    console.log('Current route:', window.location.hash)
    console.log('Router is ready:', router.isReady())
  }, 100)

} catch (error) {
  console.error('❌❌❌ CRITICAL: Failed to mount Vue app!')
  console.error('Error:', error.message)
  console.error('Stack:', error.stack)

  // Show error in the DOM for visibility
  const appDiv = document.getElementById('app')
  if (appDiv) {
    appDiv.innerHTML = `
      <div style="padding: 40px; font-family: monospace; background: #1a1a1a; color: #f0f0f0;">
        <h1 style="color: #ff5252;">❌ VUE MOUNT FAILED</h1>
        <h2>Error Details:</h2>
        <pre style="background: #2a2a2a; padding: 20px; overflow: auto;">${error.message}\n\n${error.stack}</pre>
        <h3>Troubleshooting:</h3>
        <ul>
          <li>Check browser DevTools Console for errors</li>
          <li>Check Network tab for failed imports</li>
          <li>Try refreshing the page</li>
        </ul>
      </div>
    `
  }
}

console.log('🔍 Step 13: main.js completed')
