import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { visualizer } from 'rollup-plugin-visualizer'
import Components from 'unplugin-vue-components/vite'
import AutoImport from 'unplugin-auto-import/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

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
    availablePort = await findAvailablePort(3020, 3029);
    console.log(`🚀 Using available port: ${availablePort}`);
  } catch (error) {
    console.error(`❌ ${(error as Error).message}`);
    process.exit(1);
  }

  return {
    plugins: [
      vue(),
      // ⚡ Element Plus 自动导入（按需引入，减少Bundle）
      AutoImport({
        resolvers: [ElementPlusResolver()],
      }),
      Components({
        resolvers: [ElementPlusResolver()],
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
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
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
            // Vue核心库
            if (id.includes('vue') || id.includes('pinia') || id.includes('vue-router')) {
              return 'vue-vendor'
            }

            // Element Plus UI库（自动导入，分块优化）
            if (id.includes('element-plus') || id.includes('@element-plus')) {
              return 'element-plus'
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
        'klinecharts'
      ],
      // 排除不需要预构建的包（按需引入）
      exclude: [
        'element-plus',
        'echarts'
      ]
    },
    // 实验性功能 - Phase 1.3.3 (并行构建)
    experimental: {
      renderBuiltUrl(filename, hostType) {
        return { runtime: `/${filename}` }
      }
    }
  };
})
