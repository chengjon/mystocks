import { createApp } from 'vue'
import { createPinia } from 'pinia'
// ✅ Element Plus自动导入配置（通过vite.config.mts插件处理）
// Element Plus核心功能现在通过unplugin-vue-components自动导入
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import _zhCn from 'element-plus/dist/locale/zh-cn.mjs'

import App from './App.vue'
import router from './router/index.ts'
import './styles/index.scss'

// ⚡ 性能优化: ECharts按需引入（减少80%体积）
import './utils/echarts.ts'

// 🎨 ArtDeco设计令牌（核心CSS变量定义）
import './styles/artdeco-tokens.scss'

// 🎨 金融数据终端设计系统 v2.0（统一所有样式）
import './styles/fintech-design-system.scss'

// ELEMENT PLUS OVERRIDE: Bloomberg Terminal主题（使用Design Tokens）
import './styles/element-plus-override.scss'

// VISUAL OPTIMIZATION v2.0: 视觉优化规范（解决按钮对齐、卡片比例、组件间距问题）
import './styles/visual-optimization.scss'

// PRO FINTECH OPTIMIZATION: 专业金融终端优化（Bloomberg级别）
import './styles/pro-fintech-optimization.scss'

// BLOOMBERG TERMINAL OVERRIDE: 强制应用专业金融终端样式（!important 规则）
import './styles/bloomberg-terminal-override.scss'

// SECURITY FIX 1.2: 导入CSRF初始化函数
import { initializeSecurity } from './services/httpClient.js'

// API版本协商服务
import { _versionNegotiator, showVersionNotifications } from './services/versionNegotiator.ts'

const app = createApp(App)
const pinia = createPinia()

// 注册所有 Element Plus 图标（保留，因为图标不包含在自动导入中）
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)

// 移除Element Plus全局导入，改用按需导入
// import ElementPlus from 'element-plus'
// import 'element-plus/dist/index.css'
// app.use(ElementPlus, { locale: zhCn })

// 🔧 修复方案1: 确保Vue应用一定会挂载，不被异步阻塞
// 立即挂载应用，然后异步执行安全初始化
app.mount('#app')

console.log('✅ Vue应用已挂载到#app')

// SECURITY FIX 1.2: 启用CSRF保护（异步执行，不阻塞挂载）
// 应用启动时初始化CSRF token，但不阻塞应用挂载
const initPromise = Promise.race([
  initializeSecurity().catch(err => {
    console.warn('⚠️ Security initialization failed:', err)
    return null
  }),
  new Promise((resolve) => setTimeout(() => {
    console.warn('⚠️ Security initialization timed out (non-blocking)')
    resolve(null)
  }, 2000))
])

// 异步初始化，不阻塞Vue应用
initPromise.then(() => {
  console.log('✅ Security initialization complete (or timed out)')
}).catch(err => {
  console.warn('⚠️ Security initialization error:', err)
}).finally(() => {
  // 初始化API版本协商服务（异步，不阻塞）
  try {
    showVersionNotifications()
  } catch (err) {
    console.warn('⚠️ Version notification failed:', err)
  }

  // Task 2.1.2: 应用启动时验证并恢复session
  import('./utils/sessionRestore.js').then(({ restoreSession }) => {
    restoreSession().catch(err => {
      console.warn('⚠️ Session restore failed:', err)
    })
  }).catch(err => {
    console.warn('⚠️ Session restore import failed:', err)
  })
})

// 暴露全局Vue实例，方便浏览器调试
if (typeof window !== 'undefined') {
  window.$vue = app
}
