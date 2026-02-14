import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router/index.ts' // 使用重构后的真实路由
import axios from 'axios'

// 引入核心样式
import './styles/artdeco-global.scss'

// API LOGGING: 开启请求追踪
axios.interceptors.request.use(config => {
    console.log(`🚀 [API Request] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
});
axios.interceptors.response.use(
    res => { console.log(`✅ [API Success] ${res.config.url}`); return res; },
    err => { console.error(`❌ [API Error] ${err.config?.url}: ${err.message}`); return Promise.reject(err); }
);

// AUTH INJECTION: 注入测试 Token，确保 API 请求能发出
if (typeof localStorage !== 'undefined') {
    localStorage.setItem('auth_token', 'e2e-test-token-2026');
    console.log('🔑 Auth Token Injected');
}

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

app.mount('#app')
console.log('✅ ArtDeco App Mounted (Debug Entry)')
