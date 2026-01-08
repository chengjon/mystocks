import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { visualizer } from 'rollup-plugin-visualizer'

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
          // 手动分块策略
          manualChunks: {
            // Vue核心库
            'vue-vendor': ['vue', 'vue-router', 'pinia'],

            // Element Plus UI库
            'element-plus': ['element-plus', '@element-plus/icons-vue'],

            // ECharts图表库
            'echarts': ['echarts'],

            // K线图表库
            'klinecharts': ['klinecharts'],

            // 网格布局库
            'vue-grid-layout': ['vue-grid-layout']
          },
          // 分块文件命名
          chunkFileNames: 'assets/js/[name]-[hash].js',
          entryFileNames: 'assets/js/[name]-[hash].js',
          assetFileNames: 'assets/[ext]/[name]-[hash].[ext]'
        }
      },
      // 启用源码映射（生产环境建议关闭）
      sourcemap: false,
      // 压缩配置
      minify: 'terser',
      terserOptions: {
        compress: {
          // 移除console.log
          drop_console: true,
          drop_debugger: true
        }
      },
      // 分块大小警告阈值（KB）
      chunkSizeWarningLimit: 1000
    },
    // 优化依赖预构建
    optimizeDeps: {
      include: [
        'vue',
        'vue-router',
        'pinia',
        'element-plus',
        // ⚠️ 不预构建echarts，使用按需引入版本
        // 'echarts',
        'klinecharts'
      ]
    }
  };
})
