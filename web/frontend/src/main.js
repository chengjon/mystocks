import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

import App from './App.vue'
import router from './router'
import './styles/index.scss'

// SECURITY FIX 1.2: 导入CSRF初始化函数
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

// SECURITY FIX 1.2: 启用CSRF保护
// 应用启动时初始化CSRF token，然后挂载应用
initializeSecurity().then(() => {
  console.log('✅ Security initialization complete')
}).catch(err => {
  console.warn('⚠️ Security initialization failed:', err)
  // 继续挂载应用，即使CSRF初始化失败
}).finally(() => {
  app.mount('#app')
})
