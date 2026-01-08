import { createApp } from 'vue'
import { createPinia } from 'pinia'
// ⚡ 性能优化: 移除Element Plus全量导入，使用unplugin-vue-components自动导入
// import ElementPlus from 'element-plus'  // ❌ 已移除
// import 'element-plus/dist/index.css'  // ❌ 已移除（使用按需导入）
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

import App from './App.vue'
import router from './router'
import './styles/index.scss'

// ⚡ 性能优化: ECharts按需引入（减少80%体积）
import './utils/echarts'

// 🎨 金融数据终端设计系统 v2.0（统一所有样式）
import './styles/fintech-design-system.scss'

// ELEMENT PLUS COMPACT THEME: 紧凑主题（数据密集型量化系统）
import './styles/element-plus-compact.scss'

// VISUAL OPTIMIZATION v2.0: 视觉优化规范（解决按钮对齐、卡片比例、组件间距问题）
import './styles/visual-optimization.scss'

// PRO FINTECH OPTIMIZATION: 专业金融终端优化（Bloomberg级别）
import './styles/pro-fintech-optimization.scss'

// BLOOMBERG TERMINAL OVERRIDE: 强制应用专业金融终端样式（!important 规则）
import './styles/bloomberg-terminal-override.scss'

// SECURITY FIX 1.2: 导入CSRF初始化函数
import { initializeSecurity } from './services/httpClient.js'

const app = createApp(App)
const pinia = createPinia()

// 注册所有 Element Plus 图标（保留，因为图标不包含在自动导入中）
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)

// ⚡ 性能优化: 移除Element Plus全局注册，使用自动导入
// app.use(ElementPlus, { locale: zhCn })  // ❌ 已移除

// SECURITY FIX 1.2: 启用CSRF保护
// 应用启动时初始化CSRF token，然后挂载应用
initializeSecurity().then(() => {
  console.log('✅ Security initialization complete')
}).catch(err => {
  console.warn('⚠️ Security initialization failed:', err)
  // 继续挂载应用，即使CSRF初始化失败
}).finally(() => {
  // 初始化Pinia后挂载应用
  app.mount('#app')

  // Task 2.1.2: 应用启动时验证并恢复session
  import('./utils/sessionRestore.js').then(({ restoreSession }) => {
    restoreSession().catch(err => {
      console.warn('⚠️ Session restore failed:', err)
    })
  })
})
