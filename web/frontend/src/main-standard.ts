import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router/index.ts'

// ============================================
//   STYLE IMPORTS (Vital for UI)
// ============================================
// Element Plus 基础样式 (现在通过按需引入，但覆盖样式需要手动引入)
import './styles/index.scss'

// ArtDeco 核心设计系统
import './styles/artdeco-global.scss'
import './styles/artdeco-financial.scss'
import './styles/fintech-design-system.scss'

// UI 覆盖与优化
import './styles/element-plus-override.scss'
import './styles/visual-optimization.scss'
import './styles/pro-fintech-optimization.scss'

// 性能优化: ECharts按需引入
import './utils/echarts.ts'

// 全局注册核心卡片
import ArtDecoCardCompact from '@/components/artdeco/base/ArtDecoCardCompact.vue'

console.log('🏁 Standard Boot Started (With Styles)');

try {
    const app = createApp(App)
    const pinia = createPinia()
    
    app.component('ArtDecoCardCompact', ArtDecoCardCompact)

    console.log('📦 Pinia Created');
    app.use(pinia)
    
    console.log('🗺️ Router Linking');
    app.use(router)
    
    console.log('🚀 Attempting Mount...');
    app.mount('#app')
    console.log('✅ Mount Signal Sent');
} catch (e) {
    console.error('🔥 FATAL BOOT ERROR:', e);
}
