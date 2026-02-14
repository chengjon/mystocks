import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router/index.ts'

console.log('🏁 Diagnostic Boot Started');

try {
    const app = createApp(App)
    const pinia = createPinia()
    
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
