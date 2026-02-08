// web/frontend/src/main.ts (Enhanced)

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import i18n from './i18n'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import './styles/artdeco-main.css'

// 1. Create App
const app = createApp(App)

// 2. Global State (Pinia)
const pinia = createPinia()
app.use(pinia)

// 3. Routing
app.use(router)

// 4. Internationalization
app.use(i18n)

// 5. Global Icons (Element Plus)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 6. Global Error Boundary (Example)
app.config.errorHandler = (err, vm, info) => {
  console.error('[Vue Error]', err, info)
  // Optional: Sentry or other error reporting
}

// 7. Mount
app.mount('#app')
