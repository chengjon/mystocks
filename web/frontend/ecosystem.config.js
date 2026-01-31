/**
 * MyStocks Frontend - PM2 Ecosystem Configuration
 * Phase 3: Bloomberg Terminal Style Verification Environment
 * Production-ready PM2 configuration for MyStocks Vue 3 frontend
 * with comprehensive logging and monitoring
 */

module.exports = {
  apps: [
    {
      // 前端服务：Vite开发服务器
      name: 'mystocks-frontend',
      script: 'npm',
      args: 'run dev',
      cwd: '/opt/claude/mystocks_spec/web/frontend',
      
      // Environment configuration
      env: {
        NODE_ENV: 'development',
        PORT: 3020,  // Vite会查找3000-3009范围可用端口，实际可能使用3002
        HOST: '0.0.0.0',
      },
      
      // Instance configuration
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      max_restarts: 5,
      min_uptime: '30s',  // ✅ 增加到30秒，给Vite更多启动时间
      max_memory_restart: '2G',  // 限制内存重启次数
      restart_delay: 10000,  // 10秒重启延迟
      
      // 🆕 Logging configuration - 专门为前端服务配置
      log_file: './logs/frontend-frontend-error.log',
      error_file: './logs/frontend-frontend-error.log',
      out_file: './logs/frontend-frontend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      source_map_support: true,
      
      // Process management
      kill_timeout: 5000,
      listen_timeout: 10000,
      shutdown_with_message: true,
      
      // Instance variables
      node_args: '--max-old-space-size=1024',
      
      // Monitoring
      monitor_command: 'pm2 monit mystocks-frontend',
      
      // 🔧 稳定性优化
      wait_ready: true,
      listen_timeout: 10000,
      exp_backoff_restart_delay: 2000,
    },
    
    {
      // 前端服务：静态资源服务（生产环境）
      name: 'mystocks-frontend-static',
      script: 'npm',
      args: 'run preview --port 8081',
      cwd: '/opt/claude/mystocks_spec/web/frontend',
      disabled: true,  // 开发环境先不启用
      instances: 1,
      exec_mode: 'fork',
      
      env: {
        NODE_ENV: 'production',
        PORT: 3020,
        HOST: '0.0.0.0',
      },
      
      // 静态资源服务配置
      log_file: './logs/frontend-frontend-static-error.log',
      error_file: './logs/frontend-frontend-static-error.log',
      out_file: './logs/frontend-frontend-static-out.log',
      
      // Instance configuration
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      max_restarts: 5,
      min_uptime: '30s',
    },
  ],
  
  /**
   * Deployment configuration (optional, for future CI/CD integration)
   */
  deploy: {
    production: {
      user: 'root',
      host: 'localhost',
      ref: 'origin/main',
      repo: 'git@github.com:your-org/mystocks.git',
      path: '/opt/laude/mystocks_spec/web/frontend',
      'post-deploy': 'npm install && npm run build && pm2 reload ecosystem.config.js --env production',
    }
  },
}