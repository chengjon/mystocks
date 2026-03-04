import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { visualizer } from 'rollup-plugin-visualizer'
import Components from 'unplugin-vue-components/vite'
import AutoImport from 'unplugin-auto-import/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import commonjs from 'vite-plugin-commonjs'
// import { VitePWA } from 'vite-plugin-pwa' // PWA 禁用

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const frontendPortRaw = env.FRONTEND_PORT || process.env.FRONTEND_PORT || process.env.PORT
  if (!frontendPortRaw) {
    throw new Error("[port-config] Missing FRONTEND_PORT in .env")
  }

  const devPort = Number.parseInt(frontendPortRaw, 10)
  if (!Number.isInteger(devPort) || devPort <= 0) {
    throw new Error(`[port-config] Invalid FRONTEND_PORT: ${frontendPortRaw}`)
  }

  const backendPort = env.BACKEND_PORT || process.env.BACKEND_PORT
  if (!backendPort) {
    throw new Error("[port-config] Missing BACKEND_PORT in .env")
  }
  const backendUrl = `http://localhost:${backendPort}`

  return {
    define: {
      'import.meta.env.VITE_USE_MOCK_DATA': JSON.stringify(env.VITE_USE_MOCK_DATA === 'true'),
      'import.meta.env.VITE_API_BASE_URL': JSON.stringify(env.VITE_API_BASE_URL || '/api')
    },
  plugins: [
      vue(),
      // CJS转ESM：解决dayjs等CJS模块兼容问题
      commonjs({
        include: [/dayjs/, /node_modules/]
      }),
      // 重新启用Element Plus自动导入（按需导入模式）
      AutoImport({
        resolvers: [ElementPlusResolver()],
      }),
      Components({
        // 重新启用Element Plus Resolver（按需导入模式）
        resolvers: [ElementPlusResolver()],
        dirs: ['src/components/artdeco'],
        dts: 'src/components.d.ts',
      }),
      // Bundle分析插件 - 生成可视化报告
      visualizer({
        filename: 'dist/stats.html',
        gzipSize: true,
        brotliSize: true,
        open: false
      })
      
      // PWA 插件已禁用以解决 Node 24 兼容性问题
    ],
    resolve: {
      mainFields: ['module', 'main'],  // 优先使用ESM版本
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
        'axios': 'axios/dist/browser/axios.cjs'
      }
    },
    css: {
      preprocessorOptions: {
        scss: {
          api: 'modern-compiler',  // 使用现代 Sass API，消除 legacy 警告
          silenceDeprecations: ['legacy-js-api', 'import']  // 静默弃用警告
        }
      }
    },
    server: {
      host: '0.0.0.0',
      port: devPort,
      strictPort: true,
      proxy: {
        '/api': {
          target: backendUrl,
          changeOrigin: true
        }
      }
    },
    preview: {
      host: '0.0.0.0',
      port: devPort,
      strictPort: true,
      proxy: {
        '/api': {
          target: backendUrl,
          changeOrigin: true
        }
      }
    },
    publicDir: 'public',
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      // 代码分割优化 - 首屏体积↓60%
      rollupOptions: {
        output: {
          // 手动分块策略 - 修复循环依赖问题
          manualChunks(id) {
            // Vue 核心框架（vue + vue-router + pinia）
            if (id.includes('node_modules/vue/') || id.includes('node_modules/@vue/') ||
                id.includes('node_modules/vue-router/') || id.includes('node_modules/pinia/')) {
              return 'vue-core'
            }

            // Element Plus 独立分包（UI 组件库）
            if (id.includes('element-plus') || id.includes('@element-plus')) {
              return 'element-plus'
            }

            // ECharts图表库（按需引入）
            if (id.includes('echarts')) {
              return 'echarts'
            }

            // K线图表库
            if (id.includes('klinecharts')) {
              return 'klinecharts'
            }

            // 网格布局库
            if (id.includes('vue-grid-layout')) {
              return 'vue-grid-layout'
            }

            // 其他node_modules包
            if (id.includes('node_modules')) {
              return 'vendor'
            }
          },
          // 分块文件命名
          chunkFileNames: 'assets/js/[name]-[hash].js',
          entryFileNames: 'assets/js/[name]-[hash].js',
          assetFileNames: 'assets/[ext]/[name]-[hash].[ext]'
        }
      },
      // 启用源码映射（开发环境启用，生产环境关闭）
      sourcemap: process.env.NODE_ENV === 'development',
      // 压缩配置
      minify: 'terser',
      terserOptions: {
        compress: {
          // 移除console.log（生产环境）
          drop_console: process.env.NODE_ENV === 'production',
          drop_debugger: true
        }
      },
      // 分块大小警告阈值（KB） - Phase 1.3.4
      chunkSizeWarningLimit: 1000,
      // CSS代码分割 - Phase 1.3.1
      cssCodeSplit: true,
      // 目标浏览器支持 - Phase 1.3.3
      target: ['es2020', 'edge88', 'firefox78', 'chrome87', 'safari14'],
      // 优化依赖预构建 - Phase 1.3.3 (增量构建)
      optimizeDeps: {
        include: [
          'vue',
          'vue-router',
          'pinia',
          'klinecharts',
          'axios'  // 🔧 修复apiClient.ts加载问题 - 预构建axios
        ],
        // 排除不需要预构建的包（按需引入）
        exclude: [
          'echarts'
          // 移除dayjs排除，让Vite预构建dayjs及其插件
          // 移除了element-plus排除，现在使用按需导入
        ]
      }
    }

  }
})
