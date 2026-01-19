import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { visualizer } from 'rollup-plugin-visualizer'
import Components from 'unplugin-vue-components/vite'
import AutoImport from 'unplugin-auto-import/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import commonjs from 'vite-plugin-commonjs'

// 查找可用端口的函数
async function findAvailablePort(startPort: number, endPort: number): Promise<number> {
  const net = await import('net');

  return new Promise((resolve, reject) => {
    function checkPort(port: number) {
      if (port > endPort) {
        reject(new Error(`No available port found in range ${startPort}-${endPort}`));
        return;
      }

      const server = net.createServer();

      server.listen(port, '0.0.0.0', () => {
        server.once('close', () => {
          resolve(port);
        });
        server.close();
      });

      server.on('error', () => {
        checkPort(port + 1);
      });
    }

    checkPort(startPort);
  });
}

// https://vitejs.dev/config/
export default defineConfig(async () => {
  let availablePort = 3000; // 默认端口

  try {
    availablePort = await findAvailablePort(3001, 3009);
    console.log(`🚀 Using available port: ${availablePort}`);
  } catch (error) {
    console.error(`❌ ${(error as Error).message}`);
    process.exit(1);
  }

  return {
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
      host: '0.0.0.0',  // 监听所有网卡，允许外部访问
      port: availablePort,
      proxy: {
        '/api': {
          target: 'http://localhost:8000', // 后端运行端口
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
          // 手动分块策略 - Phase 1.3.1
          manualChunks(id) {
            // Vue核心库 + Element Plus (合并以避免循环依赖)
            if (id.includes('vue') || id.includes('pinia') || id.includes('vue-router') ||
                id.includes('element-plus') || id.includes('@element-plus')) {
              return 'vue-vendor'
            }

            // ECharts图表库（按需引入） - Phase 1.3.2
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

            // Node_modules包
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
      target: ['es2020', 'edge88', 'firefox78', 'chrome87', 'safari14']
    },
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
  };
})
