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

// 🎨 ArtDeco全局真值入口（字体/重置/基础排版/背景）
import './styles/artdeco-global.scss'

// 🎨 ArtDeco金融语义真值层（技术指标、风险等级、数据质量等）
import './styles/artdeco-financial.scss'

// 🎨 ArtDeco核心 token 真值已由 artdeco-global.scss 导入
// import './styles/artdeco-tokens.scss' // ⚠️ 已通过artdeco-global.scss导入

// ⚙️ 历史 Fintech 兼容层（仍在主运行链路中，非新 ArtDeco 真值）
import './styles/fintech-design-system.scss'

// ⚙️ Element Plus 兼容映射层（第三方组件对齐）
import './styles/element-plus-override.scss'

// ⚙️ 历史视觉兼容层（按钮/卡片/间距旧覆盖）
import './styles/visual-optimization.scss'

// ⚙️ 历史专业终端兼容层（旧 Fintech/Bloomberg 风格增强）
import './styles/pro-fintech-optimization.scss'

// ⚙️ Bloomberg 兼容硬覆盖层（旧终端链路，非新 ArtDeco 真值）
import './styles/bloomberg-terminal-override.scss'

// SECURITY FIX 1.2: 导入CSRF初始化函数
import { initializeSecurity } from './services/httpClient.js'

// API版本协商服务
import { showVersionNotifications } from './services/versionNegotiator.ts'

// 契约验证错误处理
import { ContractValidationError } from './api/unifiedApiClient.ts'

const app = createApp(App)
const pinia = createPinia()

// 注册所有 Element Plus 图标（保留，因为图标不包含在自动导入中）
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)

// 全局错误处理器 - 处理契约验证错误
app.config.errorHandler = (err, instance, info) => {
  // 处理契约验证错误
  if (err instanceof ContractValidationError) {
    console.error('Contract validation error:', err)

    // 在开发环境下显示详细错误
    if (import.meta.env.DEV) {
      // 可以通过全局事件总线或store通知用户
      console.error(`API Contract Drift: ${err.message}`)
      console.error('Contract:', err.contractName)
      console.error('Endpoint:', err.endpoint)
      console.error('Expected:', err.expectedSchema)
      console.error('Actual:', err.actualData)
    } else {
      // 在生产环境下记录错误但不显示给用户
      console.error('Contract validation failed:', err.message)
    }

    // 可以选择不抛出错误，让应用继续运行
    return
  }

  // 处理其他错误
  console.error('Global error:', err, info)
}

// 移除Element Plus全局导入，改用按需导入
// import ElementPlus from 'element-plus'
// import 'element-plus/dist/index.css'
// app.use(ElementPlus, { locale: zhCn })

// ✅ 全局注册 ArtDeco 紧凑卡片组件
import ArtDecoCardCompact from '@/components/artdeco/base/ArtDecoCardCompact.vue'
app.component('ArtDecoCardCompact', ArtDecoCardCompact)

// 🔧 修复方案1: 确保Vue应用一定会挂载，不被异步阻塞
// 立即挂载应用，然后异步执行安全初始化
app.mount('#app')

console.log('✅ Vue应用已挂载到#app')

// PWA: Service Worker Registration (非阻塞，不影响应用启动)
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('✅ Service Worker registered successfully:', registration.scope)

        // Listen for updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing
          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                // New content is available, notify user
                console.log('🔄 New content available, please refresh')
                // In a real app, you might show a toast notification here
              }
            })
          }
        })

        // Handle controller change (when SW takes control)
        navigator.serviceWorker.addEventListener('controllerchange', () => {
          console.log('🔄 Service Worker controller changed, reloading...')
          window.location.reload()
        })
      })
      .catch((error) => {
        console.error('❌ Service Worker registration failed:', error)
      })
  })
} else {
  console.warn('⚠️ Service Worker not supported in this browser')
}

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

  // Initialize WebSocket connections for real-time data (Phase 3)
  // TODO: Re-enable when realtimeIntegration.js is implemented
  // import('./utils/realtimeIntegration.js').then(({ initializeWebSocketConnections, setupRealtimeDataIntegration }) => {
  //   initializeWebSocketConnections()
  //   setupRealtimeDataIntegration()
  //   console.log('✅ WebSocket connections initialized for real-time data')
  // }).catch(err => {
  //   console.warn('⚠️ WebSocket initialization failed:', err)
  // })
  console.warn('⚠️ WebSocket integration暂时禁用 - realtimeIntegration.js 未实现')
})

// 暴露全局Vue实例，方便浏览器调试
if (typeof window !== 'undefined') {
  window.$vue = app
}
