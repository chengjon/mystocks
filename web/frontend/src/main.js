import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

import App from './App.vue'
import router from './router'
import './styles/index.scss'

// SECURITY FIX 1.2: Import CSRF initialization
import { initializeSecurity } from './services/httpClient.js'

const app = createApp(App)
const pinia = createPinia()

// 注册所有 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus, {
  locale: zhCn,
})

// SECURITY FIX 1.2: Initialize CSRF protection before mounting
;(async () => {
  try {
    // 初始化CSRF token
    await initializeSecurity()
    console.log('✅ Security initialization completed')

    // 挂载应用
    app.mount('#app')
  } catch (error) {
    console.error('❌ Failed to initialize security:', error)
    // 即使CSRF初始化失败，仍然挂载应用（优雅降级）
    app.mount('#app')
  }
})()

