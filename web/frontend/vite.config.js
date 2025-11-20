import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// 查找可用端口的函数
async function findAvailablePort(startPort, endPort) {
  const net = await import('net');
  
  return new Promise((resolve, reject) => {
    function checkPort(port) {
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
        // 端口被占用，尝试下一个端口
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
    availablePort = await findAvailablePort(3000, 3010);
    console.log(`🚀 Using available port: ${availablePort}`);
  } catch (error) {
    console.error(`❌ ${error.message}`);
    process.exit(1);
  }
  
  return {
    plugins: [vue()],
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
          target: 'http://localhost:8000', // 修改为当前后端运行端口
          changeOrigin: true
        }
      }
    }
  };
})
